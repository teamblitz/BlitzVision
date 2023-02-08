import cv2
import time
import os
import subprocess

from camera_reader import CameraReader, ListenerFunction, Cv2Mat
import time_manager


def resize(frame, dst_width):
    width = frame.shape[1]
    height = frame.shape[0]
    scale = dst_width * 1.0 / width
    return cv2.resize(frame, (int(scale * width), int(scale * height)))


class QuadCameraReader(CameraReader):

    def __init__(self, listener: ListenerFunction):
        super().__init__(listener)

        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

        # Set the pixel format for BA81
        self.cap.set(cv2.CAP_PROP_FOURCC, 825770306)

        # Disable rgb conversion as this makes the fps 15x slower when on.
        self.cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)

        # Size 5120x800
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 5120)

        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)

        # Set camera exposure, we need to fetch a frame first for it to work.
        self.cap.read()
        print(subprocess.run(["v4l2-ctl -c exposure=500"], shell=True))

    def run(self):
        frame_count = 0
        start = time.time()

        while True:
            self.cap.grab()
            timestamp = time.time()
            ret, frame = self.cap.retrieve()

            # We have to do this because convert rgb is off.
            w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            frame = frame.reshape(int(h), int(w))

            # Convert to rby
            frame = cv2.cvtColor(frame, cv2.COLOR_BAYER_BG2BGR)

            # Split the frame into the streams from each camera.
            height, width, _ = frame.shape

            step = int(width / 4)

            frames = [
                (frame[0:height, step * 0: step * 1].copy(), time_manager.get_instance().get_timestamp(), 0),
                (frame[0:height, step * 1: step * 2].copy(), time_manager.get_instance().get_timestamp(), 1),
                (frame[0:height, step * 2: step * 3].copy(), time_manager.get_instance().get_timestamp(), 2),
                (frame[0:height, step * 3: step * 4].copy(), time_manager.get_instance().get_timestamp(), 3)
            ]

            self.listener(frames)

            # resize for display TODO Remove later
            # frame = resize(frame, 1280.0)

            # cv2.imshow("Test", frame)
            # if cv2.waitKey(1) == ord('q'):
            #     break
            # frame_count +=1
            # if time.time() - start >= 1:
            #     print(f"FPS: {frame_count}")
            #     start = time.time()
            #     frame_count = 0 
        # self.cap.release()


if __name__ == "__main__":
    reader = QuadCameraReader(None)
    reader.run()
