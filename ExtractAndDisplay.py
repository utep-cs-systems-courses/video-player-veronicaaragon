#!/usr/bin/env python3

import threading
import cv2
import numpy as np
import base64
import queue

def extractFrames(fileName, outputBuffer, maxFramesToLoad=9999):
    # Initialize frame count 
    count = 0

    # open video file
    vidcap = cv2.VideoCapture(fileName)

    # read first image
    success,image = vidcap.read()
    
    print(f'Reading frame {count} {success}')
    while success and count < maxFramesToLoad:
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)

        #encode the frame as base 64 to make debugging easier
        jpgAsText = base64.b64encode(jpgImage)

        # add the frame to the buffer
        outputBuffer.put(image)
       
        success,image = vidcap.read()
        print(f'Reading frame {count} {success}')
        count += 1

    print('Frame extraction complete')


def displayFrames(inputBuffer):
    # initialize frame count
    count = 0

    # go through each frame in the buffer until the buffer is empty
    while not inputBuffer.empty():
        # get the next frame
        frame = inputBuffer.get()

        print(f'Displaying frame {count}')        

        # display the image in a window called "video" and wait 42ms
        # before displaying the next frame
        cv2.imshow('Video', frame)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

        count += 1

    print('Finished displaying all frames')
    # cleanup the windows
    cv2.destroyAllWindows()

# filename of clip to load
filename = 'clip.mp4'

# shared queue  
extractionQueue = queue.Queue()

# extract the frames
extractFrames(filename,extractionQueue, 72)

# display the frames
displayFrames(extractionQueue)

