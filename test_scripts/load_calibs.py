import numpy as np

camera_matrices = []
camera_dist_coeffs = []

for i in range(4):
    file = np.load(f"calibration/store/{i}.npz")
    camera_matrices.append(file["cameraMatrix"])
    camera_dist_coeffs.append(file["distCoeffs"])

print(camera_matrices)
print(camera_dist_coeffs)