import cv2
from cv2 import aruco
import sys
import matplotlib.pyplot as plt
from datetime import datetime

import argparse

aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)

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
            print("Detected id {} at frame {} time {}".format(id, frame_number, getCurrentTime()))
        if writer is not None:
            frame_markers = aruco.drawDetectedMarkers(image.copy(), corners, ids)
            writer.write(frame_markers.astype('uint8'))
    elif writer is not None:
        writer.write(image.copy().astype('uint8'))

    return corners, ids, rejectedImgPoints


def get_time_from_video(filename):
    cap = cv2.VideoCapture(filename)
    ret,frame = cap.read()

    height, width, channels = frame.shape 

    new_file = filename.split(".")[0] + "_marked.avi"
    writer = cv2.VideoWriter(new_file, cv2.VideoWriter_fourcc('M','J','P','G'), 24, (width, height))

    print("Writing to {}".format(new_file))

    count = 0
    while cap.isOpened():
        ret,frame = cap.read()
        if cv2.waitKey(10) & 0xFF == ord('q') or frame is None:
            break
        cv2.imshow('window-name', frame)
        look_for_marker(frame, count, writer=writer)
        count = count + 1

    writer.release()
    cap.release()
    cv2.destroyAllWindows() # destroy all opened windows


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
