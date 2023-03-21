from networktables import NetworkTables

from output_processor.robot_output_processor import RobotOutputProcessor
from pipeline.tag_pipeline import ApriltagPipeline
from pipeline.vision_pipeline import VisionPipeline
from quad_camera_reader import QuadCameraReader
from robot_communicator import RobotCommunicator
from output_processor.visual_output_processor import VisualOutputProcessor

from typing import List, Dict, Any, Union, Tuple
from threading import Event
from queue import Queue


def calculate_areas_of_interest(cam_id: int, frame_size: Tuple[Any, Any]) -> Tuple[Tuple[int]]:
    """Frame size in width, height notation"""
    return (((0, 0), frame_size),)


class Dispatcher:

    def __init__(self):

        rc = RobotCommunicator()
        rc.start()

        NetworkTables.initialize(server='10.20.83.2')
        print("NT Client Established")

        self.quadCamera = QuadCameraReader((lambda x: self.listener(0, x)))
        self.quadCamera.start()
        self.rop = RobotOutputProcessor(4)
        self.vop = VisualOutputProcessor(self.rop)

        self.cameraPipelines: List[Dict[str, VisionPipeline]] = [
            {
                "tag": ApriltagPipeline(0, "QuadCamera", self.vop, self.rop)
            }
        ]

        self.cameraPipelines[0]["tag"].start()

    def listener(self, pipeline_id, frames):
        if hasattr(self, "cameraPipelines"):
            if "tag" in self.cameraPipelines[pipeline_id].keys() and not self.cameraPipelines[pipeline_id]["tag"].is_busy():
                self.cameraPipelines[pipeline_id]["tag"].add_frames(
                    [(frame, timestamp, cam_id, calculate_areas_of_interest(cam_id, (frame.shape[1], frame.shape[0]))) for
                    frame, timestamp, cam_id in frames]
                )

            for frame in frames:
                frame, _, cam_id = frame
                # self.vop.display_frame(frame, cam_id)
        else:
            print("cameraPipelines does not exist.")


if __name__ == "__main__":
    dispatcher = Dispatcher()
