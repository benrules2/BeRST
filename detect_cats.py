#!/usr/local/bin/python3

import aruco as cv
import argparse
import log
import sys
import os

def get_output_filename(args, extension='.csv', annotated='_marked.avi', annotated_img='.jpg'):
    image_extension = annotated
    output_csv = None

    if args.i:
        #if image input exists, use image extension, otherwise use video
        image_extension = annotated_img
    
    filename = None
    if args.o:
        filename = os.path.basename(args.o)
        log.info("Filename {}".format(filename))
        output_csv = filename.split(".")[0] + extension
    
    annoted_video_output = None
    if args.annotate:
        if filename:
            filename = filename.split(".")
            annoted_video_output = filename[0] + image_extension
        else:
            annoted_video_output = "annotated_output" + image_extension
  
    return output_csv, annoted_video_output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Track your pets.')
    parser.add_argument('-v', action='store_true', help="Expect video", default=False)
    parser.add_argument('-i', action='store_true', help="Expect images", default=False)
    parser.add_argument('--stream', help = "Stream from your webcam", action='store_true', default=False)
    parser.add_argument('--preview', help = "Watch results in preview window", action='store_true',default=False)
    parser.add_argument('-f', help = "Filename to track", default=None)
    parser.add_argument('-o', help = "Output csv file", default=None)
    parser.add_argument('--annotate', help = "Draw detections onto input and save",  action='store_true',  default=False)
    parser.add_argument('--roi', action='store_true', help="Set Regions of Interest for tracking", default=False)
    args = parser.parse_args()

    if not args.stream and (args.i or args.v) and args.f == None:
        log.error("Video or image mode selected (-i / -v) but no file provided. Please select a file '-f'")
        pass
    
    outfile_data, outfile_annotated = get_output_filename(args)   

    if args.annotate:
        log.info("Writting detections to {} and data to {}".format(outfile_annotated, outfile_data))
    else:
        log.info("No annotation selected (optimize speed). Writting data to {}".format(outfile_data))

    detector = cv.TagDetector(
        input_file=args.f, 
        annotated_file=outfile_annotated, 
        data_file=outfile_data, 
        stream=args.stream,
        preview=args.preview,
        videoSource=args.v,
        roi=args.roi
        )

    if args.i:
        log.info("Image mode selected. Looking for markers in {}".format(args.f))
        detector.read_marker()

    elif args.v:
        if not args.stream:
            log.info("Video mode selected. Looking for markers in {}".format(args.f))
        else:
            log.info("Streaming mode selected, using computer webcam.")
        detector.record_detections()
