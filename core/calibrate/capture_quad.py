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

    captured_frames = [[] for _ in range(4)]

    while True:
        frames = [None for _ in range(0, 4)]
        for (frame, timestamp, cam_id) in frames_queue.get():
            cv2.imshow(str(cam_id), resize(frame, 640))
            frames[cam_id] = frame

        key = cv2.waitKey(1)

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
                    cv2.imwrite(f"calibration\\images\\{str(i)}\\img_{str(j)}.jpg")
            print("saved")
            break

        if to_capture == -1:
            continue

        captured_frames[to_capture].append(frames[to_capture])

        print(
            f"Successfully added calibration frame for cam {to_capture}\n Count:{len(captured_frames[to_capture])}")

        global busy
        busy = False


if __name__ == "__main__":
    main()
