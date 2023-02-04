from threading import Thread, Event
from queue import Queue
from typing import Tuple, Union, Any
import cv2

from pupil_apriltags import Detection
from core.pipeline.vision_pipeline import VisionPipeline

from vision.apriltag_detector import ApriltagDetector

class ApriltagPipeline(VisionPipeline):

    max_error: int = 0

    def __init__(self, id: int, name: str):
        super().__init__(f"tag{id}{name}")

        self.detector = ApriltagDetector()
    
    def run(self):
        while True:
            for frame, timestamp, cam_id in self.inputQueue.get():
                detections: list[Detection] = self.detector.detect(frame)
                outputs = []
                for detection in detections:
                    if detection.hamming > self.max_error:
                        outputs.append((detection.tag_id, detection.tag_family, detection.corners, detection.center,  timestamp, cam_id))
                        