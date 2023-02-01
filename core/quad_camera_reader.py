import cv2

from camera_reader import CameraReader, ListenerFunction

class QuadCameraReader(CameraReader):

    def __init__(self, listener: ListenerFunction):
        super.__init__(listener)
        
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

        self.cap.set(cv2.CAP_PROP_FOURCC, None) # TODO: Set pixel format

    def run(self):
        while True:
            # Wait for frame
            # Seperate frames
            # Inform the listener
            break

