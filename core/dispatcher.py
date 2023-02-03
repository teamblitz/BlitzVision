from quad_camera_reader import QuadCameraReader

from typing import List, Dict, Any, Union
from threading import Event
from queue import Queue


class Dispatcher:



    def __init__(self):
        self.quadCamera = QuadCameraReader((lambda x: self.listener(0, x)))


        self.cameraPipelines: List[Dict[str, Any, Union[Event, Queue]]] = [
            {
                "tagQueue": Queue(),
                "tagBusyEvent": Event(),
                "tagSettings": [
                    1
                ],
                "yoloQueue": None,
                "yoloBusyEvent": None
            }
        ]

    def listener(self, id, frames):
        if not self.cameraPipelines[id]["tagBusyEvent"].is_set():
            # Give it the frame/frames
            self.cameraPipelines[id]["tagQueue"].put(frames)
            # Mark as busy
            self.cameraPipelines[id]["tagBusyEvent"].set()