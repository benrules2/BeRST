import sys
import threading as th
import log
import argparse
import auto_logger
import cv2
import cv_utils as utils
from cv2 import aruco
from utils import getCurrentTime

aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)

class InteruptableCapture:
    def __init__(self):
        self.keep_going = True

    def key_capture_thread(self):
         while self.keep_going:
            key = input()
            self.keep_going = False   

    def capture(self, tag_detector):
        th.Thread(target=self.key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
        log.info("Press enter to terminate capture")
        while self.keep_going:
            next_frame = tag_detector.get_next_frame()
            if next_frame is None:
                break
            else:
                tag_detector.look_for_marker(next_frame)

class TagDetector:
    def __init__(self, input_file=None, annotated_file=None, data_file=None, stream=False, preview=False, videoSource=False, roi=False):
        self.count = 0
        self.input_file = input_file
        self.annotated_file = annotated_file
        self.stream = stream
        self.writer = None
        self.preview = preview
        self.videoSource = videoSource
        self.roi = roi
        self.roi_list = []
        self.frame_rate = 1
        self.auto_logger = None
        if self.preview:
            cv2.namedWindow('preview',cv2.WINDOW_AUTOSIZE)
        if data_file == "auto.csv":
            self.auto_logger = auto_logger.AutoLogger()
            self.data_file = self.auto_logger.get_log_file()
        elif data_file:        
            self.data_file = open(data_file, "w")
            log.info("Writing csv to {}".format(data_file))
            self.data_file.write("#id,frame_idx,timestamp\n".format(id, self.count, getCurrentTime()))
        
        if videoSource:
            self._set_video_capture_source()
        if roi:
            self._set_roi()
    
    def _set_roi(self):
        img = self.get_next_frame()
        print(img.shape)
        new_roi = cv2.selectROI("selectRoi", img)
        cv2.destroyWindow('selectRoi')
        self.roi_list.append(new_roi)
        print(self.roi_list[0][3])

    def _check_marker_in_roi(self, midpoint):
        # to judge a point(x0,y0) is in the rectangle, just to check if a < x0 < a+c and b < y0 < b + d
        # ROI is top left coordinate, and width and height
        for roi in self.roi_list:
            x_inside = midpoint[0] >= roi[0] and midpoint[0] <= roi[0] + roi[2]
            y_inside = midpoint[1] >= roi[1] and midpoint[1] <= roi[0] + roi[3]

            if x_inside and y_inside:
                return True

        return False

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

    def _record_positive_matches(self, image, corners, ids, rejectedImgPoints):
        if self.data_file and self.auto_logger:
            self.data_file = self.auto_logger.get_log_file()

        if ids is not None and self.data_file:
            for idx, id in enumerate(ids):
                midpoint = utils.get_corner_midpoint(corners[idx])
                if len(self.roi_list) == 0 or self._check_marker_in_roi(midpoint):
                    timestamp = "{:.2f}".format(float(self.count / self.frame_rate))
                    if self.stream:
                        timestamp = getCurrentTime()
                    log.info("Detected id {} at frame {} time {} x {} y {} ".format(id, self.count, timestamp, midpoint[0], midpoint[1]))
                    self.data_file.write("{},{},{},{},{}\n".format(id, self.count, timestamp, midpoint[0], midpoint[1]))
                    if self.writer:
                        image = utils.draw_markers(image.copy(), corners, ids)
        
        if self.writer:
            if len(self.roi_list) > 0:
                for roi in self.roi_list:
                    red = (int(255),int(0),int(0))
                    cv2.rectangle(image, roi, red)
            self.writer.write(image.copy().astype('uint8'))

        if self.preview:
            cv2.imshow("preview", image)
            cv2.waitKey(10)

    def look_for_marker(self, image):
        self.count += 1
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        parameters =  aruco.DetectorParameters_create()
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        self._record_positive_matches(image, corners, ids, rejectedImgPoints)
        return corners, ids, rejectedImgPoints

    def init_writer(self):
        if self.annotated_file and self.writer is None:
            ret,frame = self.cap.read()
            height, width, channels = frame.shape
            log.info("Video file has height: {} width: {}".format(height, width))
            log.info("Writing to {}".format(self.annotated_file))
            self.writer = cv2.VideoWriter(self.annotated_file, cv2.VideoWriter_fourcc('M','J','P','G'), 24, (width, height))

    def _set_video_capture_source(self):
        filename = self.input_file
        self.cap = cv2.VideoCapture(filename)
        if self.stream:
            log.info("Streaming from computer video capture")
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
        self.frame_rate = int(self.cap.get(cv2.CAP_PROP_FPS))
        print("The frame rate is: " + str(self.frame_rate ))

    def get_time_from_video(self):
        self.init_writer()
        capture_loop = InteruptableCapture()
        capture_loop.capture(self)
        log.info("Cleaning up writer and capture")
        if self.writer:
            self.writer.release()
        self.cap.release()
        self.data_file.close()
        cv2.destroyAllWindows()

def gen_marker(filename="marker", id=0):
    output = "_markers/{}_{}.jpg".format(filename, id)
    img = aruco.drawMarker(aruco_dict, id, 4*4*10)
    cv2.imwrite(output, img)
