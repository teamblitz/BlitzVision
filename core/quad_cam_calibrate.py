import numpy as np

from quad_camera_reader import QuadCameraReader
from vision.camera_calibration import CameraCalibration
from queue import Queue
from threading import Lock
import cv2

frames_queue = Queue(1)

lock = Lock()

busy = False

def listener(frames):
    global busy
    if not busy:
        while not frames_queue.empty():
            frames_queue.get()
        frames_queue.put(frames)
        busy = True

def resize(frame, dst_width):
    width = frame.shape[1]
    height = frame.shape[0]
    scale = dst_width * 1.0 / width
    return cv2.resize(frame, (int(scale * width), int(scale * height)))


def main():

    reader: QuadCameraReader = QuadCameraReader(listener)
    reader.start()

    calibrators = [CameraCalibration(7, 10) for _ in range(0, 4)]

    while True:
        print("hI")
        print(frames_queue.qsize())
        frames = [None for _ in range(0, 4)]
        for (frame, timestamp, cam_id) in frames_queue.get():
            cv2.imshow(str(cam_id), resize(calibrators[cam_id].show_pattern(frame)[1], 640))
            frames[cam_id] = frame
        
        print(frames_queue.qsize())
        global busy
        busy = False

        continue

        to_calib = -1
        key = cv2.waitKey(1)

        if key == ord("c"):
            camraMatrices = []
            distCoeffsList = []
            for i in range(0, 4):
                ret, cameraMatrix, distCoeffs, rvecs, tvecs = calibrators[i].finish_calibration()
                if not ret:
                    print(f"Failed to calibrate camera {i}")

                camraMatrices.append(cameraMatrix)
                distCoeffsList.append(distCoeffs)
            np.savez("camera_calibrations.npz", cameraMatrices=camraMatrices, distCoeffs=distCoeffsList)
            print("saved")

            break

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

        print(
            f"{'Successfully added' if ret else 'Failed to add'} calibration frame for cam {to_calib}\n Count:{calibrators[to_calib].get_frame_count()}")

        # global busy
        # busy = False


if __name__ == "__main__":
    main()