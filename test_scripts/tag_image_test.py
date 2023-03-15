import os
import sys

import cv2
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.pipeline.tag_pipeline import ApriltagPipeline
from core.output_processor.robot_output_processor import RobotOutputProcessor
from core.output_processor.visual_output_processor import VisualOutputProcessor

rop = RobotOutputProcessor(4)
vop = VisualOutputProcessor(rop)

tag_pipeline = ApriltagPipeline(0, "test", vop, rop)

# frame, timestamp, cam_id, areas_of_interest
frame = cv2.imread("calibration/tag/0/img_2_14661608824203.jpg")

frames = (
    (frame, 0, 0, (((0, 0), (frame.shape[1], frame.shape[0])),)),
    (frame, 0, 1, (((0, 0), (10, 10)),)),
    (frame, 0, 2, (((0, 0), (10, 10)),)),
    (frame, 0, 3, (((0, 0), (10, 10)),))
)

tag_pipeline.daemon = True
tag_pipeline.add_frames(frames)

tag_pipeline.start()
input()