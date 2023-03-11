import numpy as np
import sys
import os
import time

# print(
#     os.path.abspath(
#         os.path.dirname(os.path.dirname((os.path.dirname(__file__)))
#     )
# )
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

    captured_frames = [[] for _ in range(4)]

    while True:
        frames = [None for _ in range(0, 4)]
        for (frame, timestamp, cam_id) in frames_queue.get():
            cv2.imshow(str(cam_id), resize(frame, 640))
            frames[cam_id] = frame

        key = cv2.waitKey(1)
        to_capture = -1

        global busy
        busy = False

        if key == ord("q"):
            break
        if key == ord("0"):
            to_capture = 0
        if key == ord("1"):
            to_capture = 1
        if key == ord("2"):
            to_capture = 2
        if key == ord("3"):
            to_capture = 3

        if (key == ord("s")):
            for i, images in enumerate(captured_frames):
                for j, img in enumerate(images):
                    name = f"calibration/tag/{str(i)}/img_{str(j)}_{time.monotonic_ns()}.jpg"
                    # name = f"test_{i}_{j}.jpg"
                    print(name)
                    print(cv2.imwrite(name, img))
            print("saved")

        if to_capture == -1:
            continue

        captured_frames[to_capture].append(frames[to_capture])

        print(
            f"Successfully added calibration frame for cam {to_capture}\n Count:{len(captured_frames[to_capture])}")
        
    cv2.destroyAllWindows()



if __name__ == "__main__":
    main()
