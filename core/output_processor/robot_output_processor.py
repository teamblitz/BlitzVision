from threading import Lock
from typing import Iterable, Any

import cv2
import numpy as np
from scipy import linalg
from scipy.spatial.transform import Rotation as R
from networktables import NetworkTables

import utils.units as units
import vision.multi_cam_pnp as multi_cam_pnp

valid_ids = {"tag16h5": (1, 2, 3, 4, 5, 6, 7, 8), "tag25h9": (1, 2)}
valid_families = valid_ids.keys()


def valid_detection(family, tag_id):
    if family not in valid_families:
        return False
    if tag_id not in valid_ids[family]:
        return False

    return True


def compute_tag_transform(tag_xyz, tag_rot_matrix):
    output = np.zeros((4, 4))
    output[0:3, 0:3] = tag_rot_matrix
    output[0:3, 3] = tag_xyz
    output[3, 3] = 1
    return output


def compute_tag_corners(transform, size):
    corners = (  # Homogeneous corner coordinates
        [0, size / 2, -size / 2, 1],  # Lower left
        [0, -size / 2, -size / 2, 1],  # Lower right
        [0, -size / 2, size / 2, 1],  # Upper right
        [0, size / 2, size / 2, 1]  # Upper left
    )
    output_corners = []
    for corner in corners:
        output_corners.append((transform @ corner)[0:3])
    return output_corners


class RobotOutputProcessor:
    def __init__(self, num_cameras: int):
        self.last_detection_corners = [[] for _ in range(num_cameras)]
        self.quad_cam_ids = [0, 1, 2, 3]

        # Defined constants
        self.april_tag_transforms = {
            "tag16h5": {
                # Red side of the field
                1: compute_tag_transform([units.inches_to_meters(610.77),
                                          units.inches_to_meters(42.19),
                                          units.inches_to_meters(18.22)],
                                         np.identity(3)),
                2: compute_tag_transform([units.inches_to_meters(610.77),
                                          units.inches_to_meters(108.19),
                                          units.inches_to_meters(18.22)],
                                         np.identity(3)),
                3: compute_tag_transform([units.inches_to_meters(610.77),
                                          units.inches_to_meters(174.19),  # FIRST's diagram has a typo (it says 147.19)
                                          units.inches_to_meters(18.22)],
                                         np.identity(3)),
                4: compute_tag_transform([units.inches_to_meters(636.96),
                                          units.inches_to_meters(265.74),
                                          units.inches_to_meters(27.38)],
                                         np.identity(3)),
                # Blue side of the field
                5: compute_tag_transform([units.inches_to_meters(14.25),
                                          units.inches_to_meters(265.74),
                                          units.inches_to_meters(27.38)],
                                         R.from_euler("Z", np.pi).as_matrix()),
                6: compute_tag_transform([units.inches_to_meters(40.45),
                                          units.inches_to_meters(174.19),  # FIRST's diagram has a typo (it says 147.19)
                                          units.inches_to_meters(18.22)],
                                         R.from_euler("Z", np.pi).as_matrix()),
                7: compute_tag_transform([units.inches_to_meters(40.45),
                                          units.inches_to_meters(108.19),
                                          units.inches_to_meters(18.22)],
                                         R.from_euler("Z", np.pi).as_matrix()),
                8: compute_tag_transform([units.inches_to_meters(40.45),
                                          units.inches_to_meters(42.19),
                                          units.inches_to_meters(18.22)],
                                         R.from_euler("Z", np.pi).as_matrix())
            }
        }
        # The coordinates of the corners for all apriltags in order
        # Corner 0 is the lower left corner with roll 0. with 1 though 3 counterclockwise around the tag.
        # 0-3 is tag id-1 4-7 is id-2 etc.
        # points 0-31 are the field 16h5 tags
        # further points could be used for the drivers station tags
        size = units.inches_to_meters(6)
        self.april_tag_corners = {
            "tag16h5": {
                1: compute_tag_corners(self.april_tag_transforms["tag16h5"][1], size),
                2: compute_tag_corners(self.april_tag_transforms["tag16h5"][2], size),
                3: compute_tag_corners(self.april_tag_transforms["tag16h5"][3], size),
                4: compute_tag_corners(self.april_tag_transforms["tag16h5"][4], size),
                5: compute_tag_corners(self.april_tag_transforms["tag16h5"][5], size),
                6: compute_tag_corners(self.april_tag_transforms["tag16h5"][6], size),
                7: compute_tag_corners(self.april_tag_transforms["tag16h5"][7], size),
                8: compute_tag_corners(self.april_tag_transforms["tag16h5"][8], size)
            }
        }

        # The cameras are numbered 0 to 3.
        # 0 is front right
        # 1 is back right
        # 2 is front left
        # 3 is back left
        # units=meters
        between_mounts = units.inches_to_meters(12)
        front_to_edge = units.millimeters_to_meters(19.77)
        back_to_edge = units.millimeters_to_meters(18)
        # These angles
        self.camera_transforms = [
            multi_cam_pnp.calc_cam_to_general_transform(
                ([0.02, (between_mounts / 2 + front_to_edge), 0],
                 R.from_euler("ZYX", [37.5, 0, 0], degrees=True).as_matrix())),
            multi_cam_pnp.calc_cam_to_general_transform(
                ([-0.02, (between_mounts / 2 + front_to_edge), 0],
                 R.from_euler("ZYX", [154.39, 0, 0], degrees=True).as_matrix())),
            multi_cam_pnp.calc_cam_to_general_transform(
                ([0.02, -(between_mounts / 2 + front_to_edge), 0],
                 R.from_euler("ZYX", [-37.5, 0, 0], degrees=True).as_matrix())),
            multi_cam_pnp.calc_cam_to_general_transform(
                ([-0.02, -(between_mounts / 2 + back_to_edge), 0],
                 R.from_euler("ZYX", [-154.39, 0, 0], degrees=True).as_matrix()))
        ]
        # TODO: These are fake camera intrinsics from chatgpt, we will need to replace them with our own.
        K = np.array([[834.064, 0.0, 640],
                      [0.0, 834.064, 400],
                      [0.0, 0.0, 1.0]])
        D = np.array([0., 0., 0., 0., 0.])
        self.camera_matrices = [K, K, K, K]
        self.camera_dist_coeffs = [D, D, D, D]

        self.transform_general_to_robot = np.zeros((4, 4))
        self.transform_general_to_robot[0:3, 0:3] = np.identity(3)
        self.transform_general_to_robot[0:3, 3] = [units.inches_to_meters(7.0625), 0, units.inches_to_meters(21)]
        self.transform_general_to_robot[3, 3] = 1

        self.lock = Lock()

    def process_quad_cam(self, inputs):
        timestamp = -1
        quad_detections: Iterable[Iterable[Any] | None] = [None for _ in range(4)]
        # Quad cam cam ids are 0 - 3
        for (detections, cam_id, frame_timestamp) in inputs:
            if timestamp == -1:
                timestamp = frame_timestamp
            # elif timestamp != frame_timestamp:
            #     # print("Mismatched timestamps!")\
            #     pass
            quad_detections[cam_id] = detections

        valid_tags = 0

        img_points = [[] for _ in range(4)]
        obj_points = [[] for _ in range(4)]

        for i in range(0, 4):
            for detection in quad_detections[i]:
                tag_id, family, corners, center, _, cam_id = detection

                if not valid_detection(family, tag_id):
                    print("NOT VALID" + str(detection))
                    continue
                valid_tags += 1

                for img_point, obj_point in zip(corners, self.april_tag_corners[family][tag_id]):
                    img_points[i].append(img_point)
                    obj_points[i].append(obj_point)

        if valid_tags > 0:
            transform_general_to_world, _ = multi_cam_pnp.calc(obj_points, img_points, self.camera_transforms,
                                                               self.camera_matrices, self.camera_dist_coeffs)
            transform_robot_to_world = transform_general_to_world @ linalg.inv(self.transform_general_to_robot)

            print(transform_general_to_world)
            print(R.from_matrix(transform_general_to_world[0:3, 0:3]).as_euler("ZYX", degrees=True))

            NetworkTables.getEntry("/Jetson/pose/translation").setDoubleArray(list(transform_robot_to_world[0:3, 3]))
            NetworkTables.getEntry("/Jetson/pose/rotation").setDoubleArray(
                transform_robot_to_world[0:3, 0:3].reshape(9).tolist())
            NetworkTables.getEntry("/Jetson/pose/timestamp").setDouble(timestamp)
            NetworkTables.flush()
            print(transform_robot_to_world)
        # self.lock.acquire() for cam_id in self.quad_cam_ids: self.last_detection_corners[cam_id] = [detection[2]
        # for detection in detections[cam_id]] #Corners are the 3rd item in the tuple from tag detection pipeline.
        # self.lock.release()

    def calculate_areas_of_interest(self, cam_id: int):
        for corners in self.last_detection_corners[cam_id]:
            if len(corners) <= 0:
                print(
                    f"Corner length 0 when calculating areas of interest on cam id {cam_id} Last detection corners dump: {self.last_detection_corners}")
            # our min and max values can start at the first corner coordinates

        points, _ = cv2.projectPoints(self.april_tag_object_points, self.camera_poses_rt[cam_id][0],
                                      self.camera_poses_rt[cam_id][1], )
