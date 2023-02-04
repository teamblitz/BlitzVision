from core.pipeline.tag_pipeline import ApriltagPipeline
from core.pipeline.vision_pipeline import VisionPipeline
from quad_camera_reader import QuadCameraReader

from typing import List, Dict, Any, Union, Tuple
from threading import Event
from queue import Queue


class Dispatcher:

    def __init__(self):
        self.quadCamera = QuadCameraReader((lambda x: self.listener(0, x)))


        self.cameraPipelines: List[Dict[str, VisionPipeline]] = [
            {
                "tag": ApriltagPipeline(0,"QuadCamera")
            }
        ]

    def listener(self, pipeline_id, frames):
        if "tag" in self.cameraPipelines[pipeline_id].keys() and not self.cameraPipelines[pipeline_id]["tag"].isBusy():
            self.cameraPipelines[pipeline_id]["tag"].addFrames(frames)
