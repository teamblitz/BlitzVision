from queue import Queue, LifoQueue
from threading import Lock, Thread
import time
import logging

logger = logging.getLogger(__name__)

class MultiThreadProvider:

    def __init__(self, supplier, name):
        '''A multi-thread provider built to provide camera feed to multiple threads. 

        @param supplier - needs a blocking function, ie a camera, that reflects external state, 
        and cannot simpily be called multiple times from different threads to achieve the same state.
        
        @param name - name for debuging purposes'''
        # A list containing all of the output queues
        self.output_queues: list[Queue] = []
        self.lock = Lock()
        self.supplier = supplier
        self.name = name

        thread = Thread(target=self.run(), name=f"MultiThreadProvider {name}")
        thread.start()


    
    def register_output_queue(self, queue):
        '''Register a new output queue. Images are added to the queue as availible. It is the responsibility of the thread using the queue to keep it not full. If the queue fills up then new frames will no longer be added to the queue.'''
        with self.lock: # This is likely unnecessary but it is here as a redundancy
            self.output_queues.append(queue) # .append() is thread safe per https://docs.python.org/3/faq/library.html#what-kinds-of-global-value-mutation-are-thread-safe

    def run(self):
        while True:
            output = self.supplier()  # Read the method (generaly a camera frame).
            timestamp = time.perf_counter()
        
            for queue in self.output_queues:
                try:
                    with self.lock:
                        while not queue.empty():
                            queue.get_nowait()
                        queue.put_nowait((output, timestamp))
                except:
                    logger.critical(f"Error occurred while adding outputs to queue of type {type(queue)} on MultiThreadProvider {self.name}. Faital, This may lead to threads hanging. This most likly occured because a different queue implementation then the built in python Queue was used. ", exc_info=1)
                    self.output_queues.remove(queue) # Remove the queue to prevent spam.

