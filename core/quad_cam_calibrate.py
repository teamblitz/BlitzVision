from quad_camera_reader import QuadCameraReader
from camera_calibration import CameraCalibration
from queue import Queue
import cv2


frames_queue = Queue()

def listener(frames):
    frames_queue.put(frames)

def main():
    reader: QuadCameraReader = QuadCameraReader(listener)
    reader.start()

    calibrators = [CameraCalibration(10, 10) for _ in range(0, 4)]

    while True:
        frames = [None for _ in range(0,4)]
        for (frame, timestamp, cam_id) in frames_queue.get():
            cv2.imshow(cam_id, calibrators[cam_id].show_pattern(frame))
            frames[cam_id] = frame

        to_calib = -1
        key = cv2.waitKey(1)
        if key == ord("q"):
            break
        if key == ord("0"):
            to_calib = 0
        if key == ord("1"):
            to_calib = 1
        if key == ord("2"):
            to_calib = 2
        if key == ord("3"):
            to_calib = 3


        if to_calib == -1:
            continue

        ret = calibrators[to_calib].add_to_calibration(frames[to_calib])

        print(f"{'Successfully added' if ret else 'Failed to add'} calibration frame for cam {to_calib}")

        if key == ord("c"):
            for i in range(0, 4):
                calibrators[i].finish_calibration()

