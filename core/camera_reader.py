from threading import Thread
from typing import Callable, Tuple
import cv2

ListenerFunction = Callable[[Tuple[cv2.Mat, ...]], None]

## Abstract camera reader class
class CameraReader(Thread):
    def __init__(self, listener: ListenerFunction):
        self.listener = listener