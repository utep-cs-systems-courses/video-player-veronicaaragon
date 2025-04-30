# BoundedBuffer.py
from threading import Semaphore, Lock

class BoundedBuffer:
    def __init__(self, size):
        self.buffer = []
        self.size = size
        self.empty = Semaphore(size)
        self.full = Semaphore(0)
        self.lock = Lock()

    def put(self, item):
        self.empty.acquire()
        with self.lock:
            self.buffer.append(item)
        self.full.release()

    def get(self):
        self.full.acquire()
        with self.lock:
            item = self.buffer.pop(0)
        self.empty.release()
        return item
