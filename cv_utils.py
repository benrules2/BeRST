import cv2
import log
import random

def get_midpoint_from_corners(corners):
    return (corners[:, 0].mean(), corners[:, 1].mean())

def draw_marker(image, corners, id, colour=(255,0,0), thickness=10):
    corners = corners[0]
    if len(corners) < 4:
        log.error("Not enough corners {}".format(len(corners)))
        log.info("Corners: {}".format(corners))
        return image

    cv2.line(image, tuple(corners[0]), tuple(corners[1]), colour, thickness)
    cv2.line(image, tuple(corners[1]), tuple(corners[2]), colour, thickness)
    cv2.line(image, tuple(corners[2]), tuple(corners[3]), colour, thickness)
    cv2.line(image, tuple(corners[3]), tuple(corners[0]), colour, thickness)

    label_loc = get_midpoint_from_corners(corners)

    cv2.putText(image,"id = {}".format(id), label_loc, cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 5, cv2.LINE_4)
    return image

def draw_markers(image, corners, ids, colour=(255,0,0), thickness=10):
    for id in range(0, len(ids)):
        r = random.randint(0,255)
        g = random.randint(0,r)
        b = random.randint(r,255)
        image = draw_marker(image, corners[id], id, colour=(r, g, b))
    return image


def gen_marker(filename="marker", id=0):
    output = "_markers/{}_{}.jpg".format(filename, id)
    img = aruco.drawMarker(aruco_dict, id, 4*4*10)
    cv2.imwrite(output, img)
