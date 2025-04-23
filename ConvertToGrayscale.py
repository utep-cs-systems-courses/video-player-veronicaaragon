#!/usr/bin/env python3

import cv2

# globals
outputDir    = 'frames'

# initialize frame count
count = 0

# get the next frame file name
inFileName = f'{outputDir}/frame_{count:04d}.bmp'


# load the next file
inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)

while inputFrame is not None and count < 72:
    print(f'Converting frame {count}')

    # convert the image to grayscale
    grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)
    
    # generate output file name
    outFileName = f'{outputDir}/grayscale_{count:04d}.bmp'

    # write output file
    cv2.imwrite(outFileName, grayscaleFrame)

    count += 1

    # generate input file name for the next frame
    inFileName = f'{outputDir}/frame_{count:04d}.bmp'
    
    # load the next frame
    inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)


    
    
