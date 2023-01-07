from queue import Queue
import numpy as np
from typing import Callable
import pupil_apriltags
import cv2

from core.vision.apriltag_detector import ApriltagDetector



def run(input: Queue[cv2.Mat], output: Queue, should_stream_func: Callable[[], bool], stream: Queue[cv2.Mat], should_exit_func: Callable[[], bool], detector: ApriltagDetector, config: dict[str, any]):
    while True:
        image: cv2.Mat = input.get()
        # TODO: Check if the image needs to be resized, anf if so do so.
        # if config["resize"]:
        #       cv2.resize(image, config["resize-factor"])
        

        result: list[pupil_apriltags.Detection] = detector.detect(input.get())

        for tag in result:
            if tag.hamming < 1:
                continue


        # check if should stream
        # if so stream.
