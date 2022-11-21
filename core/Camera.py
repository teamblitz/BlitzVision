from queue import Queue, LifoQueue
from threading import Lock
import time

class Camera:

    def __init__(self, read_func=None):
        '''Read func is a blocking function that returns a boolean if successful, and a frame.'''
        # A list containing all of the output queues
        self.output_queues: list[Queue] = []
        self.lock = Lock()
        self.read = read_func


    
    def register_output_queue(self, queue):
        '''Register a new output queue. Images are added to the queue as availible. It is the responsibility of the thread using the queue to keep it not full. If the queue fills up then new frames will no longer be added to the queue.'''
        with self.lock: # This is likely unnecessary but it is here as a redundancy
            self.output_queues.append(queue) # .append() is thread safe per https://docs.python.org/3/faq/library.html#what-kinds-of-global-value-mutation-are-thread-safe

    def run(self):
        while True:
            ret, frame = self.read()  # read the camera frame
            timestamp = time.perf_counter()
            if not ret:
                continue
            for queue in self.output_queues:
                with self.lock:
                    if not queue.full(): # We are in lock so this is safe.
                        queue.put_nowait((frame, timestamp))
                        

                    
             

    # Meant to be overriden by subclasses. Meant to be a blocking call.
    # Should return a boolean indicating whether or not successful, and the frame
    def read(self):
        pass
        

    
