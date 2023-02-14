from queue import Queue, Full
from threading import Event, Thread


class VisionPipeline(Thread):
    def __init__(self, pipeline_name: str):
        super().__init__()
        self.isBusyEvent: Event = Event()
        self.inputQueue: Queue = Queue(10)
        self.pipelineName = pipeline_name

    def is_busy(self):
        return self.isBusyEvent.is_set()
    
    def set_busy(self, busy):
        if busy:
            self.isBusyEvent.set()
        else:
            self.isBusyEvent.clear()

    def add_frames(self, frames):
        if not self.is_busy():
            try:
                self.inputQueue.put_nowait(frames)
            except Full:
                print(f"Error adding frame to {self.pipelineName} vision pipeline, pipeline queue full.")
            self.set_busy(True)