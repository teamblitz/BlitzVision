from queue import Queue, Full
from threading import Event, Thread


class VisionPipeline(Thread):
    def __init__(self, pipeline_name: str):
        super().__init__()
        self.isBusyEvent: Event = Event()
        self.inputQueue: Queue = Queue()
        self.pipelineName = pipeline_name

    def is_busy(self):
        return self.isBusyEvent.is_set()
    
    def set_busy(self, busy):
        if busy:
            self.isBusyEvent.set()
        else:
            self.isBusyEvent.clear()

    def add_frames(self, frames):
        for frame in frames:
            try:
                self.inputQueue.put_nowait(frame)
            except Full:
                print(f"Error adding frame to {self.pipelineName} vision pipeline, pipeline queue full.")