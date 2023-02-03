from threading import Thread, Event
from queue import Queue

from vision.apriltag_detector import ApriltagDetector

class TagDetector(Thread):
    def __init__(self, inputQueue: Queue, isBusyEvent: Event):
        self.isBusyEvent: Event = isBusyEvent
        self.inputQueue: Queue = inputQueue
        super().__init__()

        self.detector = ApriltagDetector()
    
    def run(self):
        while True:
            for frame, timestamp, settings in self.inputQueue.get():
                continue