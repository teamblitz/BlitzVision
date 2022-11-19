import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R
from pupil_apriltags import Detection


def solve(detection: list[Detection], tag_groups: dict[str], camera_matrix, dist_coeffs):
    solutions = []
    
    for tag_group in tag_groups:

        object_points = np.empty((len(detection) * 4, 3))
        image_points = np.empty((len(detection) * 4, 2))
        
        i = 0
        for tag in detection:
            for object_corner, image_corner in zip(tag_group["tags"][tag.tag_family + " " + str(tag.tag_id)]["corners"], tag.corners):
                object_points[i] = object_corner
                image_points[i] = image_corner
                i += 1
        rVec = None
        tVec = None
        cv2.solvePnP(object_points, image_points, camera_matrix, dist_coeffs, rVec, tVec)
        solutions.append((rVec, tVec))
    return solutions


def compute_tag_corers(tag: dict[str, float]) -> list[float]:

    size = tag["size"] # Extract tag size in meters

    rotated_tag = [] # Empty list for the new corners.

    # The wpi cordinate system is left is positive y.
    # Corner 0 is the lower left corner with roll 0. with 1 though 3 counter clockwise around the tag.
    # Compute a flat tag at the origin. This tag is facing X- and we will need to rotate it to face X+
    flat_tag = np.array(
        [
            np.array([0, size/2, -size/2]), # Lower left corner
            np.array([0, -size/2, -size/2]), # Lower right corner
            np.array([0, -size/2, size/2]), # Upper right corner
            np.array([0, size/2, size/2]), # Upper left corner
        ]
    )
    for corner in flat_tag:
        # First we must rotate the tag 180 degrees around the z axis. 
        # This is because when we are describing rotations, the X+ axis comes out of the face of the tag, 
        # however currently the x+ axis comes out of the back of the tag.
        corner = R.from_euler("Z", 180, degrees=True).apply(corner)
        
        # Next we rotate the tag by the supplyed Yaw (CCW+ looking down from z axis) Pitch(Down positive from front) and roll(clockwise from front)
        # All rotations are insentric
        corner = R.from_euler("ZYX", [tag["yaw"], tag["pitch"], tag["roll"]], degrees=True).apply(corner)

        rotated_tag.append(corner)
    
    return rotated_tag



