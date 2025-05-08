# BoundedBuffer.py
from threading import Semaphore, Lock

class Buffer:
    def __init__(self, size):
        self.buffer = [] # Initialize an empty buffer
        self.size = size # Maximum size of the buffer
        self.empty = Semaphore(size) # Semaphore to track empty slots
        self.full = Semaphore(0) # track full slots
        self.lock = Lock() # Ensures one thread at a time can append or pop

    # insert an item into the buffer
    def put(self, item):
        self.empty.acquire() # Wait for an empty slot
        with self.lock:
            self.buffer.append(item) # add item to buffer
        self.full.release() # Signal that new item is available

    # remove an item from the buffer
    def get(self):
        self.full.acquire() # Wait until at least one item is available
        with self.lock:
            item = self.buffer.pop(0) #Removes and retrieves oldest item from buffer
        self.empty.release() # Signal that new slot is available
        return item # Returns item to consumer thread