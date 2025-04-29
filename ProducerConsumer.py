#!/usr/bin/env python3
import threading
import cv2
import os
import time
from threading import Semaphore

# Global variables
outputDir = 'frames'
clipFileName = 'clip.mp4'
maxFrames = 72  # Maximum number of frames to process

# Semaphores for producer-consumer coordination
# Semaphores for Queue 1 (Extract -> Grayscale)
empty1 = Semaphore(10)  # Initially 10 empty slots
full1 = Semaphore(0)    # Initially 0 full slots
mutex1 = Semaphore(1)   # Mutex for queue access

# Semaphores for Queue 2 (Grayscale -> Display)
empty2 = Semaphore(10)  # Initially 10 empty slots
full2 = Semaphore(0)    # Initially 0 full slots
mutex2 = Semaphore(1)   # Mutex for queue access

# Shared buffers
extractionQueue = []  # Queue between extraction and grayscale conversion
displayQueue = []     # Queue between grayscale conversion and display

# Create output directory if it doesn't exist
if not os.path.exists(outputDir):
    print(f"Output directory {outputDir} didn't exist, creating")
    os.makedirs(outputDir)

def extractFrames():
    """Extract frames from the video file and add them to the extraction queue"""
    print("Starting frame extraction thread")
    count = 0
    
    # Open video file
    vidcap = cv2.VideoCapture(clipFileName)
    
    # Read first frame
    success, frame = vidcap.read()
    
    while success and count < maxFrames:
        print(f'Extracting frame {count}')
        
        # Wait for an empty slot in the queue
        empty1.acquire()
        
        # Get exclusive access to the queue
        mutex1.acquire()
        
        # Add the frame to the queue
        extractionQueue.append((count, frame))
        
        # Release the mutex
        mutex1.release()
        
        # Signal that a frame is available
        full1.release()
        
        # Read the next frame
        success, frame = vidcap.read()
        count += 1
    
    print('Frame extraction complete')

def convertToGrayscale():
    """Take frames from the extraction queue, convert to grayscale, and add to display queue"""
    print("Starting grayscale conversion thread")
    count = 0
    
    while count < maxFrames:
        # Wait for a frame to be available
        full1.acquire()
        
        # Get exclusive access to the extraction queue
        mutex1.acquire()
        
        # Get a frame from the queue
        frame_count, frame = extractionQueue.pop(0)
        
        # Release the mutex
        mutex1.release()
        
        # Signal that there's an empty slot in the queue
        empty1.release()
        
        print(f'Converting frame {frame_count} to grayscale')
        
        # Convert frame to grayscale
        grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Wait for an empty slot in the display queue
        empty2.acquire()
        
        # Get exclusive access to the display queue
        mutex2.acquire()
        
        # Add the grayscale frame to the display queue
        displayQueue.append((frame_count, grayscaleFrame))
        
        # Release the mutex
        mutex2.release()
        
        # Signal that a grayscale frame is available
        full2.release()
        
        count += 1
    
    print('Grayscale conversion complete')

def displayFrames():
    """Take grayscale frames from the display queue and display them"""
    print("Starting frame display thread")
    count = 0
    frameDelay = 42  # 42ms delay between frames (approximately 24fps)
    
    while count < maxFrames:
        # Wait for a grayscale frame to be available
        full2.acquire()
        
        # Get exclusive access to the display queue
        mutex2.acquire()
        
        # Get a frame from the queue
        frame_count, frame = displayQueue.pop(0)
        
        # Release the mutex
        mutex2.release()
        
        # Signal that there's an empty slot in the queue
        empty2.release()
        
        print(f'Displaying frame {frame_count}')
        
        # Display the frame
        cv2.imshow('Video', frame)
        
        # Wait for the specified delay and check if the user wants to quit
        if cv2.waitKey(frameDelay) and 0xFF == ord("q"):
            break
        
        count += 1
    
    print('Frame display complete')
    # Cleanup the windows
    cv2.destroyAllWindows()

def main():
    """Main function to create and start the threads"""
    # Create the threads
    extractThread = threading.Thread(target=extractFrames)
    grayscaleThread = threading.Thread(target=convertToGrayscale)
    displayThread = threading.Thread(target=displayFrames)
    
    # Start the threads
    extractThread.start()
    grayscaleThread.start()
    displayThread.start()
    
    # Wait for all threads to complete
    extractThread.join()
    grayscaleThread.join()
    displayThread.join()
    
    print("All processing complete")

if __name__ == "__main__":
    main()