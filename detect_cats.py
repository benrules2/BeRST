#!/usr/local/bin/python3

import aruco as cv
import argparse
import log
import sys

def get_output_filename(args, extension='.csv', annotated='_marked.avi', annotated_img='.jpg'):
    image_extention = annotated
    if(args.i):
        image_extention = annotated_img
    filename = args.f 
    if filename is None:
        filename = 'output'
    filename = filename.split(".")
    return filename[0] + extension, filename[0] + image_extention

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Track your pets.')
    parser.add_argument('-v', action='store_true', default=False)
    parser.add_argument('-i', action='store_true', default=False)
    parser.add_argument('--stream', action='store_true', default=True)
    parser.add_argument('-f', help = "Filename to track", default=None)
    parser.add_argument('-o', help = "Output csv file", default=None)
    parser.add_argument('--annotate', help = "Draw detections onto input and save", action='store_true',  default=False)

    args = parser.parse_args()

    if (args.i or args.v) and args.f == None:
        log.error("Video or image mode selected (-i / -v) but no file provided. Please select a file '-f'")
        pass
    
    outfile_data, outfile_annotated = get_output_filename(args)   

    if args.annotate:
        log.info("Writting detections to {} and data to {}".format(outfile_annotated, outfile_data))
    else:
        log.info("No annotation selected (optimize speed). Writting data to {}".format(outfile_data))

    if args.i:
        log.info("Image mode selected. Looking for markers in {}".format(args.f))
        cv.read_marker(args.f)

    elif args.v:
        log.info("Video mode selected. Looking for markers in {}".format(args.f))
        cv.get_time_from_video(filename=args.f, annotated_file=outfile_annotated, data_file=outfile_data)
        
    elif args.stream:
        log.info("Streaming mode selected, using computer webcam.")
        cv.get_time_from_video(filename=args.f, annotated_file=outfile_annotated, data_file=outfile_data)
