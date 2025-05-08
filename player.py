#!/usr/bin/env python3
import cv2
import threading
from Buffer import Buffer

input_file = 'clip.mp4'
NUM_FRAMES = 72 # to process
FPS = 24
FRAME_DELAY = 42 

frame_buffer = Buffer(10) # color frames extracted from the video
gray_buffer = Buffer(10) # holds grayscale frames
display_buffer = Buffer(10) # shares final grayscale frames

def extract_frames(): # Extract frames from video
    cap = cv2.VideoCapture(input_file) # Open video
    count = 0 # Frame counter
    success, frame = cap.read() # Read first frame
    while success and count < NUM_FRAMES: 
        print(f"Extracting frame {count}")
        frame_buffer.put((count, frame)) # store frame & # in buffer
        success, frame = cap.read() # Read next frame
        count += 1
    frame_buffer.put(None)  # trigger termination of the thread
    print("Extraction complete")

def convert_to_grayscale(): # Convert frames to grayscale
    while True:
        item = frame_buffer.get() 
        if item is None:
            display_buffer.put(None)
            break
        count, frame = item
        print(f"Converting frame {count} to grayscale")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        display_buffer.put((count, gray))
    print("Conversion complete")

def display_frames(): # this function will run in a separate thread
    while True:
        item = display_buffer.get()
        if item is None:
            break
        count, gray = item
        print(f"Displaying frame {count}")
        gray_buffer.put((count, gray))
    gray_buffer.put(None) # 
    print("Display thread finished")

if __name__ == "__main__":
    t1 = threading.Thread(target=extract_frames) # thread for extracting frames
    t2 = threading.Thread(target=convert_to_grayscale) # thread for converting frames to grayscale
    t3 = threading.Thread(target=display_frames) # thread for displaying frames
    
    t1.start() # Start threads
    t2.start()
    t3.start()

    while True:
        item = gray_buffer.get() # Grabs grayscale frames
        if item is None:
            break
        count, gray = item 
        
        cv2.imshow('Frame', gray) # Display the frame
        
        if cv2.waitKey(FRAME_DELAY) & 0xFF == ord('q'):
            break

    t1.join() # Wait for threads to finish
    t2.join()
    t3.join()
    cv2.destroyAllWindows() # Close all OpenCV windows
    print("Processing complete")