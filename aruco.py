import sys
import threading as th
from datetime import datetime
import logging
import argparse

import matplotlib.pyplot as plt
import cv2
from cv2 import aruco

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
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
        logging.info("Press enter to terminate capture")
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

def read_marker(image_file):
    frame  =  cv2.imread(image_file)
    corners, ids, rejectedImgPoints = look_for_marker(frame)
    frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)

    plt.figure()
    plt.imshow(frame_markers)
    for i in range(len(ids)):
        c = corners[i][0]
        plt.plot([c[:, 0].mean()], [c[:, 1].mean()], "o", label = "id={0}".format(ids[i]))
    plt.legend()
    plt.show()

def look_for_marker(image, frame_number=0, writer=None):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    parameters =  aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if ids is not None:
        for id in ids:
            logging.info("Detected id {} at frame {} time {}".format(id, frame_number, getCurrentTime()))
        if writer:
            image = aruco.drawDetectedMarkers(image.copy(), corners, ids)
    
    if writer:
        writer.write(image.copy().astype('uint8'))

    return corners, ids, rejectedImgPoints

def get_time_from_video(filename=None, annotated_file=None, data_file=None):
    cap = cv2.VideoCapture(filename)
    streaming = False
    if filename is None:
        logging.info("No filename selected, attempting to stream webcam")
        cap = cv2.VideoCapture(0)
        stream = True

    if annotated_file is not None:
        ret,frame = cap.read()
        height, width, channels = frame.shape
        writer = cv2.VideoWriter(annotated_file, cv2.VideoWriter_fourcc('M','J','P','G'), 24, (width, height))
        logging.info("Writing to {}".format(annotated_file))
    count = 0
    capture_loop = InteruptableCapture(loop = lambda cap, writer, count : capture_next_frame(cap, writer, count))
    capture_loop.capture(cap, writer, count)
    logging.info("Cleaning up writer and capture")
    writer.release()
    cap.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Track your pets.')
    parser.add_argument('--generate', help='sum the integers (default: find the max)')
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
