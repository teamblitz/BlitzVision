import glob

import cv2
import numpy as np

from camera_calibration import CameraCalibration

for i in range(4):
    path = f"calibration/images/{i}/*.jpg"
    calib = CameraCalibration(7, 10)
    successful = 0
    unsuccessful = 0
    for file in glob.glob(path):
        img = cv2.imread(file)
        ret = calib.add_to_calibration(img)
        if not ret:
            unsuccessful += 1
        else:
            successful += 1

    ret, cameraMatrix, distCoeffs, rvecs, tvecs = calib.finish_calibration()
    print(f"Calibration for camera {i} {'Successful' if ret else 'Unsuccessful'}" +
          f"\n {calib.get_frame_count()} successful, {unsuccessful} unsuccessful" +
          f"\n {cameraMatrix}"
          f"\n {distCoeffs}")

    if ret:
        np.savez(f"calibration/store/{i}.npz", ret=ret, cameraMatrix=cameraMatrix, distCoeffs=distCoeffs)
        print("Saved")

    print("\n\n")

print("Done")
