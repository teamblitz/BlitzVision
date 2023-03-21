from threading import Thread, Event
from queue import Queue
from typing import Tuple, Union, Any
import cv2
import time

from pupil_apriltags import Detection
from pipeline.vision_pipeline import VisionPipeline

from vision.apriltag_detector import ApriltagDetector


class ApriltagPipeline(VisionPipeline):
    max_error: int = 0

    def __init__(self, _id: int, name: str, visual_output_processor, robot_output_processor):
        super().__init__(f"tag{_id}{name}")

        self.visual_output_processor = visual_output_processor
        self.robot_output_processor = robot_output_processor
        self.detector = ApriltagDetector()

    def run(self):
        while True:
            outputs = []
            for cam_in in self.inputQueue.get():
                frame, timestamp, cam_id, areas_of_interest = cam_in

                output = []
                self.visual_output_processor.clear_tag_detections(cam_id)
                # Area of interest is a tuple ((x1,y1),(x2,y2))
                for area_of_interest in areas_of_interest:
                    (x1, y1), (x2, y2) = area_of_interest
                    processing_frame = frame[y1:y2, x1:x2, :]
                    pretime = time.perf_counter()
                    detections: list[Detection] = self.detector.detect(processing_frame)
                    print(time.perf_counter() - pretime)
                    for detection in detections:
                        if detection.hamming <= self.max_error:
                            translated_corners = [translate_translate_coordinates(x, y, area_of_interest[0]) for x, y in
                                                  detection.corners]
                            translated_center = translate_translate_coordinates(detection.center[0],
                                                                                detection.center[1],
                                                                                area_of_interest[0])
                            output.append(
                                (detection.tag_id, detection.tag_family.decode(), translated_corners, translated_center,
                                 timestamp, cam_id))

                outputs.append((output, cam_id, timestamp))

                self.visual_output_processor.add_tag_detections(cam_id, output)

            if len(outputs) == 4:
                self.robot_output_processor.process_quad_cam(outputs)
            else:
                print("SOMTHING IS WRONG, 4 frames expected for camera pnp!")

            if self.inputQueue.empty():
                self.set_busy(False)


def translate_translate_coordinates(x, y, crop_start):
    return x + crop_start[0], y + crop_start[1]
