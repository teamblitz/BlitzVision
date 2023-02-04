from threading import Thread
from typing import Callable, Tuple, Any
import cv2
import numpy as np

# The version of python on the jetson does not have cv2.Mat
Cv2Mat = np.ndarray[int, np.dtype[np.generic]]

ListenerFunction = Callable[[Tuple[Cv2Mat, ...]], None]

## Abstract camera reader class
class CameraReader(Thread):
    def __init__(self, listener: ListenerFunction):
        super().__init__()
        self.listener = listener