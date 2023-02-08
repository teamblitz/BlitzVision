from pipeline.tag_pipeline import ApriltagPipeline
from pipeline.vision_pipeline import VisionPipeline
from quad_camera_reader import QuadCameraReader
from output_processor.visual_output_processor import VisualOutputProcessor

from typing import List, Dict, Any, Union, Tuple
from threading import Event
from queue import Queue


class Dispatcher:

    def __init__(self):
        self.quadCamera = QuadCameraReader((lambda x: self.listener(0, x)))
        self.quadCamera.start()
        self.vop = VisualOutputProcessor()

        self.cameraPipelines: List[Dict[str, VisionPipeline]] = [
            {
                "tag": ApriltagPipeline(0, "QuadCamera", self.vop)
            }
        ]

        self.cameraPipelines[0]["tag"].start()

    def listener(self, pipeline_id, frames):
        if "tag" in self.cameraPipelines[pipeline_id].keys() and not self.cameraPipelines[pipeline_id]["tag"].is_busy():
            self.cameraPipelines[pipeline_id]["tag"].add_frames(frames)
        
        for frame in frames:
            frame, _, cam_id = frame
            self.vop.display_frame(frame, cam_id)


if __name__ == "__main__":
    dispatcher = Dispatcher()
