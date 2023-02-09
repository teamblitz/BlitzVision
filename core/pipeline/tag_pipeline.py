from threading import Thread, Event
from queue import Queue
from typing import Tuple, Union, Any
import cv2

from pupil_apriltags import Detection
from pipeline.vision_pipeline import VisionPipeline

from vision.apriltag_detector import ApriltagDetector


class ApriltagPipeline(VisionPipeline):
    max_error: int = 0

    def __init__(self, _id: int, name: str, output_processor):
        super().__init__(f"tag{_id}{name}")

        self.detector = ApriltagDetector()
        self.output_processor = output_processor

    def run(self):
        while True:
            things = self.inputQueue.get()
            frame, timestamp, cam_id = things
            detections: list[Detection] = self.detector.detect(frame)
            outputs = []
            for detection in detections:
                if detection.hamming <= self.max_error:
                    outputs.append((detection.tag_id, detection.tag_family, detection.corners, detection.center,
                                    timestamp, cam_id))
                    if detection.tag_id != 7:
                        print(detection)
            #TODO: We can't do this once we add tag tracking and will need to be smarter
            self.output_processor.clear_tag_detections(cam_id)
            self.output_processor.add_tag_detections(cam_id, outputs)
            if self.inputQueue.empty():
                self.set_busy(False)
