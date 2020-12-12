import sys
import threading as th
from datetime import datetime
import log
import argparse

import matplotlib.pyplot as plt
import cv2
import cv_utils as utils
from cv2 import aruco

aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)

class InteruptableCapture:
    def __init__(self, loop, interupt_key='enter'):
        self.keep_going = True
        self.loop = loop
        self.interupt_key = interupt_key

    def key_capture_thread(self):
         while self.keep_going:
            key = input()
            self.keep_going = False   

    def capture(self, cap, writer, count):
        th.Thread(target=self.key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
        log.info("Press enter to terminate capture")
        while self.keep_going:
            if not cap.isOpened():
                return False
            ret,frame = cap.read()
            if frame is None:
                return False
            look_for_marker(frame, count, writer=writer)
            count = count + 1

def getCurrentTime():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")

def gen_marker(filename="marker", id=0):
    fig = plt.figure()
    output = "_markers/{}_{}.jpg".format(filename, id)
    img = aruco.drawMarker(aruco_dict, id, 4*4*10)
    cv2.imwrite(output, img)

def read_marker(image_file, display_duration=5000):
    frame  =  cv2.imread(image_file)
    corners, ids, rejectedImgPoints = look_for_marker(frame)
    image = frame.copy()
    image = utils.draw_markers(image.copy(), corners, ids)
    plt.imshow(image)
    cv2.imwrite(image_file.split(".")[0]+'marked.jpg', image)
    cv2.imshow("image", image)
    cv2.waitKey(display_duration)

def look_for_marker(image, frame_number=0, writer=None):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    parameters =  aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if ids is not None:
        for id in ids:
            log.info("Detected id {} at frame {} time {}".format(id, frame_number, getCurrentTime()))
        if writer:
            image = utils.draw_markers(image.copy(), corners, ids)
    
    if writer:
        writer.write(image.copy().astype('uint8'))

    return corners, ids, rejectedImgPoints

def get_time_from_video(filename=None, annotated_file=None, data_file=None):
    cap = cv2.VideoCapture(filename)
    streaming = False
    if filename is None:
        log.info("No filename selected, attempting to stream webcam")
        cap = cv2.VideoCapture(0)
        stream = True

    if annotated_file is not None:
        ret,frame = cap.read()
        height, width, channels = frame.shape
        writer = cv2.VideoWriter(annotated_file, cv2.VideoWriter_fourcc('M','J','P','G'), 24, (width, height))
        log.info("Writing to {}".format(annotated_file))
    count = 0
    capture_loop = InteruptableCapture(loop = lambda cap, writer, count : capture_next_frame(cap, writer, count))
    capture_loop.capture(cap, writer, count)
    log.info("Cleaning up writer and capture")
    writer.release()
    cap.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Track your pets.')
    parser.add_argument('--generate')
    parser.add_argument('--type', help = "Track from video")
    parser.add_argument('-f', help = "Filename to track")
    args = parser.parse_args()

    if args.generate is not None:
        for i in range(0,15):
            gen_marker(id=i)
    elif args.type == 'v':
        get_time_from_video(args.f)
    else:
        read_marker(args.f)
