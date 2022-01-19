import sys
import argparse
from types import prepare_class
import auto_logger
import log
import cv2
import cv_utils as utils
from cv2 import aruco
from utils import getCurrentTime

from capture.interuptable import InteruptableCapture
from capture.roi import ROI

aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)

class TagDetector:
    def __init__(self, input_file=None, annotated_file=None, data_file=None, stream=False, preview=False, videoSource=False, roi=False):
        self.count = 0
        self.input_file = input_file
        self.annotated_file = annotated_file
        self.stream = stream
        self.image_writer = None
        self.preview = preview
        self.videoSource = videoSource
        self.roi = roi
        self.roi_list = []
        self.frame_rate = 1
        self.auto_logger = None
        if self.preview:
            cv2.namedWindow('preview',cv2.WINDOW_AUTOSIZE)
        
        self.data_logger = auto_logger.AutoLogger(custom_data_file=data_file)
        
        if videoSource:
            self._init_video_capture_source()
        if roi:
            self._set_roi()
    
    def _set_roi(self):
        key = "Y"
        id = 0
        img = self.get_next_frame()
        new_rois = cv2.selectROIs("selectRoi", img)
        cv2.destroyWindow('selectRoi')
        for new_roi in new_rois:
            roi = ROI(new_roi, id)
            self.roi_list.append(roi)
            id+=1

    def _get_roi_detection_index(self, midpoint):
        # to judge a point(x0,y0) is in the rectangle, just to check if a < x0 < a+c and b < y0 < b + d
        # ROI is top left coordinate, and width and height
        for roi in self.roi_list:
            if roi.check_if_coords_in_region(midpoint):
                return roi.id
        return -1

    def read_marker(self, display_duration=5000):
        frame  =  cv2.imread(self.input_file)
        corners, ids, rejectedImgPoints = self.look_for_marker(frame)
        image = utils.draw_markers(frame, corners, ids)
        cv2.imwrite(self.input_file.split(".")[0]+'marked.jpg', image)
        cv2.imshow("image", image)
        cv2.waitKey(display_duration)
        cv2.destroyWindow('image')

    def get_next_frame(self):
        if not self.videoSource:
            return cv2.imread(self.input_file)

        if not self.cap.isOpened():
            return None

        ret,frame = self.cap.read()
        return frame

    def process_detected_markers(self, image, corners, ids, rejectedImgPoints):
        self.data_file = self.data_logger.get_log_file()
        
        if not self.data_file:
            log.error("No output file found")

        if ids is None:
            self.prepare_no_detections_output(image)
            return
  
        for idx, id in enumerate(ids):
            midpoint = utils.get_midpoint_from_corners(corners[idx][0])
            roi_idx = self._get_roi_detection_index(midpoint)
            if len(self.roi_list) == 0 or roi_idx >=0:
                timestamp = 0
                if self.stream:
                    timestamp = getCurrentTime()
                else: 
                    timestamp = "{:.2f}".format(float(self.count / self.frame_rate))

                log.info("Detected id {} at frame {} time {} x {} y {} roi {} ".format(id, self.count, timestamp, midpoint[0], midpoint[1], roi_idx))
                self.data_file.write("{},{},{},{},{},{}\n".format(id, self.count, timestamp, midpoint[0], midpoint[1], roi_idx))

        self.prepare_detections_output(image, corners, ids)

    def _draw_roi(self, image):
        for roi in self.roi_list:
            red = (255,255,0)
            cv2.rectangle(image, roi.top_left, roi.bottom_right, red)     
        return image

    def prepare_detections_output(self, image, corners, ids):
        if self.image_writer:    
            #draw markers
            if corners:
                for idx, corner in enumerate(corners):
                    image = utils.draw_marker(image.copy(), corner, ids[idx])                
            image = self._draw_roi(image)
            self.image_writer.write(image.copy().astype('uint8'))

        if self.preview:
            cv2.imshow("preview", image)
            cv2.waitKey(10)

    def prepare_no_detections_output(self, image):
        image = self._draw_roi(image)
        if self.image_writer:
            self.image_writer.write(image.copy().astype('uint8'))
        if self.preview:
            cv2.imshow("preview", image)
            cv2.waitKey(10)

    def look_for_marker(self, image):
        #30 fps * 60 (to minutes) * 60 (to hours)  * 24 (to days) == frames per day
        if self.count > 30 * 60 * 60 * 24:
            #Reset count to 0 for videos longer than 1 day
            self.count = 0
        self.count += 1
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        parameters =  aruco.DetectorParameters_create()
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        self.process_detected_markers(image, corners, ids, rejectedImgPoints)
        return corners, ids, rejectedImgPoints

    def _init_annotated_video_writer(self):
        if self.annotated_file and self.image_writer is None:
            log.info("Init video output")
            ret,frame = self.cap.read()
            height, width, channels = frame.shape
            log.info("Video file has height: {} width: {}".format(height, width))
            log.info("Writing to {}".format(self.annotated_file))
            self.image_writer = cv2.VideoWriter(self.annotated_file, cv2.VideoWriter_fourcc('M','J','P','G'), 24, (width, height))

    def _init_video_capture_source(self):
        log.info("Initializing video capture source")
        if self.input_file:
            filename = self.input_file
            log.info("Streaming from input file: " + filename)
            self.cap = cv2.VideoCapture(filename)
        elif self.stream:
            log.info("Streaming from webcam")
            self.cap = cv2.VideoCapture(0)

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            #warm up the camera for 30 frames to let lighting adjust
            for i in range(0,30):
                self.get_next_frame()

        self.frame_rate = int(self.cap.get(cv2.CAP_PROP_FPS))
        print("The frame rate is: " + str(self.frame_rate ))

    def record_detections(self):
        self._init_annotated_video_writer()
        capture_loop = InteruptableCapture()

        #Blocking call to capture, returns on exit
        capture_loop.capture(self)

        log.info(" Capture ended -cleaning up writer and capture")
        if self.image_writer:
            self.image_writer.release()
        self.cap.release()
        self.data_file.close()
        cv2.destroyAllWindows()
