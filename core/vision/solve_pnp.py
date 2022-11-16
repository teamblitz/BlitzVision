import cv2
import numpy as np
from pupil_apriltags import Detection


def solve(detection, tag_groups):
    for tag_group in tag_groups:

        object_points = np.empty((len(detection) * 4, 3))
        image_points = np.empty((len(detection) * 4, 2))

        for tag in detection:
            tag.