from threading import Lock

import cv2


class RobotOutputProcessor:
    def __init__(self, num_cameras: int):
        self.last_detection = [[] for _ in range(num_cameras)]
        self.quad_cam_cam_ids = [0, 1, 2, 3]
        self.lock = Lock()

    def register_tag_detection(self, cam_id, outputs):
        # Registers the output, does not process yet
        self.lock.acquire()
        self.last_detection[cam_id] = outputs
        self.lock.release()

    def process_quad_cam(self, inputs):
        timestamp = -1
        detections = [None for _ in range(4)]
        # Quad cam cam ids are 0 - 3
        for (detection, cam_id, frame_timestamp) in inputs:
            if timestamp == -1:
                timestamp = frame_timestamp
            if timestamp != frame_timestamp:
                print("Mismatched timestamps!")
            detections[cam_id] = detection

        


        pass
