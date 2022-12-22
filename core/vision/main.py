from concurrent.futures import ThreadPoolExecutor

import cv2

from core.multithread_provider import MultiThreadProvider



cameras: list[dict[str, MultiThreadProvider | int]] = []

def main():

    # Here populate the camera list
    webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    cameras.append({"Provider": MultiThreadProvider(webcam.read)})


    with ThreadPoolExecutor(threads=True) as executor:
        while True:
            executor.shutdown

