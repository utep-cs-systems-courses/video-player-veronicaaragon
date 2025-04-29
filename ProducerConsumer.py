#!/usr/bin/env python3

import threading
import cv2
import os
import time
import queue

class BoundedBuffer:
    """
    A bounded buffer implementation using semaphores and a mutex.
    """
    def __init__(self, capacity=10):
        self.buffer = []
        self.capacity = capacity
        # Binary semaphore (mutex) to protect the buffer
        self.mutex = threading.Semaphore(1)
        # Counting semaphore to track empty slots
        self.empty_slots = threading.Semaphore(capacity)
        # Counting semaphore to track filled slots
        self.filled_slots = threading.Semaphore(0)
    
    def deposit(self, item):
        """Add an item to the buffer (producer operation)"""
        # Wait for an empty slot
        self.empty_slots.acquire()
        # Get exclusive access to the buffer
        self.mutex.acquire()
        try:
            # Add the item to the buffer
            self.buffer.append(item)
        finally:
            # Release the mutex
            self.mutex.release()
        # Signal that a slot has been filled
        self.filled_slots.release()
    
    def extract(self):
        """Remove an item from the buffer (consumer operation)"""
        # Wait for a filled slot
        self.filled_slots.acquire()
        # Get exclusive access to the buffer
        self.mutex.acquire()
        try:
            # Remove the item from the buffer
            item = self.buffer.pop(0)
        finally:
            # Release the mutex
            self.mutex.release()
        # Signal that a slot has been emptied
        self.empty_slots.release()
        return item

    def size(self):
        """Get the current size of the buffer"""
        self.mutex.acquire()
        try:
            size = len(self.buffer)
        finally:
            self.mutex.release()
        return size

    def is_empty(self):
        """Check if the buffer is empty"""
        self.mutex.acquire()
        try:
            is_empty = len(self.buffer) == 0
        finally:
            self.mutex.release()
        return is_empty

def extract_frames(video_filename, output_buffer, max_frames=72):
    """
    Extract frames from the video file and deposit them in the output buffer.
    """
    print(f"Starting frame extraction from {video_filename}")
    count = 0
    
    # Open the video clip
    vidcap = cv2.VideoCapture(video_filename)
    
    # Read one frame
    success, frame = vidcap.read()
    
    while success and count < max_frames:
        print(f'Extracted frame {count}')
        
        # Put the frame in the output buffer
        output_buffer.deposit(frame)
        
        # Read the next frame
        success, frame = vidcap.read()
        count += 1
    
    # Signal that extraction is complete by depositing None
    output_buffer.deposit(None)
    print('Frame extraction complete')

def convert_to_grayscale(input_buffer, output_buffer):
    """
    Convert frames from the input buffer to grayscale and deposit them in the output buffer.
    """
    print("Starting grayscale conversion")
    count = 0
    
    # Process frames until None is received (end signal)
    frame = input_buffer.extract()
    
    while frame is not None:
        print(f'Converting frame {count} to grayscale')
        
        try:
            # Convert the frame to grayscale
            grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Put the grayscale frame in the output buffer
            output_buffer.deposit(grayscale_frame)
            
            # Increment counter
            count += 1
        except Exception as e:
            print(f"Error converting frame {count}: {e}")
        
        # Get the next frame
        frame = input_buffer.extract()
    
    # Signal that conversion is complete by depositing None
    output_buffer.deposit(None)
    print('Grayscale conversion complete')

def display_frames(input_buffer, frame_delay=42):
    """
    Display frames from the input buffer with the specified delay.
    """
    print("Starting frame display")
    count = 0
    
    # Process frames until None is received (end signal)
    frame = input_buffer.extract()
    
    while frame is not None:
        print(f'Displaying frame {count}')
        
        try:
            # Display the frame
            # Make sure frame is properly formatted for display
            if len(frame.shape) == 2:  # If grayscale
                # Convert to 3-channel for display
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            else:
                frame_display = frame
                
            # Instead of cv2.imshow
            cv2.imwrite(f"debug_frame_{count:04d}.jpg", frame)
            
            # Wait for frame_delay ms and check if the user wants to quit
            key = cv2.waitKey(frame_delay)
            if key & 0xFF == ord("q"):
                break
        except Exception as e:
            print(f"Error displaying frame {count}: {e}")
            break
        
        # Get the next frame
        frame = input_buffer.extract()
        count += 1
    
    print('Frame display complete')
    cv2.destroyAllWindows()

def main():
    # Video file to process
    video_filename = 'clip.mp4'
    
    # Check if the video file exists
    if not os.path.exists(video_filename):
        print(f"Error: Video file '{video_filename}' not found.")
        print("Please make sure the video file is in the current directory.")
        return
    
    # Create the bounded buffers with a capacity of 10 frames
    extraction_to_conversion_buffer = BoundedBuffer(10)
    conversion_to_display_buffer = BoundedBuffer(10)
    
    # Create the threads
    extractor_thread = threading.Thread(
        target=extract_frames,
        args=(video_filename, extraction_to_conversion_buffer)
    )
    
    converter_thread = threading.Thread(
        target=convert_to_grayscale,
        args=(extraction_to_conversion_buffer, conversion_to_display_buffer)
    )
    
    display_thread = threading.Thread(
        target=display_frames,
        args=(conversion_to_display_buffer,)
    )
    
    # Start the threads
    print("Starting all threads...")
    extractor_thread.start()
    converter_thread.start()
    display_thread.start()
    
    # Wait for all threads to complete
    extractor_thread.join()
    converter_thread.join()
    display_thread.join()
    
    print("All threads have completed. Program finished.")

if __name__ == "__main__":
    main()