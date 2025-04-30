# pipeline_player.py
import cv2
import os
import threading
from BoundedBuffer import BoundedBuffer
import time

input_file = 'clip.mp4'
NUM_FRAMES = 72
FPS = 24

frame_buffer = BoundedBuffer(10)
gray_buffer = BoundedBuffer(10)

def extract_frames():
    cap = cv2.VideoCapture(input_file)
    count = 0
    success, frame = cap.read()
    while success and count < NUM_FRAMES:
        frame_buffer.put((count, frame))
        success, frame = cap.read()
        count += 1
    frame_buffer.put(None)  # Sentinel

def convert_to_grayscale():
    while True:
        item = frame_buffer.get()
        if item is None:
            gray_buffer.put(None)
            break
        count, frame = item
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_buffer.put((count, gray))

# Main logic
if __name__ == "__main__":
    t1 = threading.Thread(target=extract_frames)
    t2 = threading.Thread(target=convert_to_grayscale)

    t1.start()
    t2.start()

    # Display on main thread
    while True:
        item = gray_buffer.get()
        if item is None:
            break
        count, gray = item
        cv2.imshow('Frame', gray)
        if cv2.waitKey(int(1000 / FPS)) & 0xFF == ord('q'):
            break

    t1.join()
    t2.join()
    cv2.destroyAllWindows()