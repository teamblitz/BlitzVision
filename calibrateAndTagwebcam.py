'''
 Based on the following tutorial:
   http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_calib3d/py_calibration/py_calibration.html
'''

from ctypes import resize
import time
import numpy as np
import cv2
import glob
import pupil_apriltags
import math

from scipy.spatial.transform import Rotation as R

# ref https://stackoverflow.com/questions/59044973/how-do-i-draw-a-line-indicating-the-orientation-of-an-apriltag
def draw_pose(self,overlay, camera_params, tag_size, pose, z_sign=1):
    opoints = np.array([
        -2, -2, 0,
        2, -2, 0,
        2, 2, 0,
        2, -2, -4 * z_sign,
    ]).reshape(-1, 1, 3) * 0.5 * tag_size

    fx, fy, cx, cy = camera_params

    K = np.array([fx, 0, cx, 0, fy, cy, 0, 0, 1]).reshape(3, 3)

    rvec, _ = cv2.Rodrigues(pose[:3, :3])
    tvec = pose[:3, 3]

    dcoeffs = np.zeros(5)

    ipoints, _ = cv2.projectPoints(opoints, rvec, tvec, K, dcoeffs)

    ipoints = np.round(ipoints).astype(int)

    ipoints = [tuple(pt) for pt in ipoints.reshape(-1, 2)]

    cv2.line(overlay, ipoints[0], ipoints[1], (0,0,255), 2)
    cv2.line(overlay, ipoints[1], ipoints[2], (0,255,0), 2)
    cv2.line(overlay, ipoints[1], ipoints[3], (255,0,0), 2)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(overlay, 'X', ipoints[0], font, 0.5, (0,0,255), 2, cv2.LINE_AA)
    cv2.putText(overlay, 'Y', ipoints[2], font, 0.5, (0,255,0), 2, cv2.LINE_AA)
    cv2.putText(overlay, 'Z', ipoints[3], font, 0.5, (255,0,0), 2, cv2.LINE_AA)

def _draw_cube(self,overlay, camera_params, tag_size, pose,centroid, z_sign=1):

    opoints = np.array([
        -10, -8, 0,
        10, -8, 0,
        10, 8, 0,
        -10, 8, 0,
        -10, -8, 2 * z_sign,
        10, -8, 2 * z_sign,
        10, 8, 2 * z_sign,
        -10, 8, 2 * z_sign,
    ]).reshape(-1, 1, 3) * 0.5 * tag_size

    edges = np.array([
        0, 1,
        1, 2,
        2, 3,
        3, 0,
        0, 4,
        1, 5,
        2, 6,
        3, 7,
        4, 5,
        5, 6,
        6, 7,
        7, 4
    ]).reshape(-1, 2)

    fx, fy, cx, cy = camera_params

    K = np.array([fx, 0, cx, 0, fy, cy, 0, 0, 1]).reshape(3, 3)

    rvec, _ = cv2.Rodrigues(pose[:3, :3])
    tvec = pose[:3, 3]

    dcoeffs = np.zeros(5)

    ipoints, _ = cv2.projectPoints(opoints, rvec, tvec, K, dcoeffs)

    ipoints = np.round(ipoints).astype(int)

    ipoints = [tuple(pt) for pt in ipoints.reshape(-1, 2)]

    for i, j in edges:
        cv2.line(overlay, ipoints[i], ipoints[j], (0, 255, 0), 1, 16)


apriltag_size = 0.209 # 11" 16h5 is 0.209, FRC 8.125" is .163
font = cv2.FONT_HERSHEY_SIMPLEX

# used to record the time when we processed last frame
prev_frame_time = 0
 
# used to record the time at which we processed current frame
new_frame_time = 0

cam = cv2.VideoCapture(1) # this is the magic!

cv2.namedWindow("apriltag")
img_counter = 0


# Define the chess board rows and columns
rows = 9
cols = 6

# Set the termination criteria for the corner sub-pixel algorithm
criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 0.001)

# Prepare the object points: (0,0,0), (1,0,0), (2,0,0), ..., (6,5,0). They are the same for all images
objectPoints = np.zeros((rows * cols, 3), np.float32)
objectPoints[:, :2] = np.mgrid[0:rows, 0:cols].T.reshape(-1, 2)*21.757

# Create the arrays to store the object points and the image points
objectPointsArray = []
imgPointsArray = []

# Loop over the image files
# for path in glob.glob('C:/Users/noahb/Documents/tags/opencv_frame_*.png'):
#     # Load the image and convert it to gray scale
#     img = cv2.imread(path)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     # Find the chess board corners
#     ret, corners = cv2.findChessboardCorners(gray, (rows, cols), None)

#     # Make sure the chess board pattern was found in the image
#     if ret:
#         # Refine the corner position
#         corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        
#         # Add the object points and the image points to the arrays
#         objectPointsArray.append(objectPoints)
#         imgPointsArray.append(corners)

#         # Draw the corners on the image
#         cv2.drawChessboardCorners(img, (rows, cols), corners, ret)
    
#     # Display the image
#     #cv2.imshow('chess board', img)
#     #cv2.waitKey(50)

# # Calibrate the camera and save the results
# ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objectPointsArray, imgPointsArray, gray.shape[::-1], None, None)
# # np.savez('new_calibration_arrays.npz', mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)

# fx = mtx[0][0]
# fy = mtx[1][1]
# cx = mtx[0][2]
# cy = mtx[1][2]

#aprilimg = cv2.imread('TENVISHD1080pApriltag\opencv_frame_4.png', cv2.IMREAD_GRAYSCALE)
#aprilimgclr = cv2.cvtColor(aprilimg,cv2.COLOR_GRAY2BGR)
#cv2.imshow('apriltag', aprilimgclr)

detector = pupil_apriltags.Detector(families='tag36h11',
                       nthreads=1,
                       quad_decimate=2.0,
                       quad_sigma=0.0,
                       refine_edges=1,
                       decode_sharpening=0.25,
                       debug=0
                    #    searchpath=["/usr/local/lib"]
                       )

while True:
    ret, aprilimgclr = cam.read()
    if not ret:
        print("failed to grab frame")
        break

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "opencv_frame_{}.png".format(img_counter)
        cv2.imwrite(img_name, aprilimgclr)
        print("{} written!".format(img_name))
        img_counter += 1


    aprilimg = cv2.cvtColor(aprilimgclr,cv2.COLOR_BGR2GRAY)
    #camera_params= ([fx, fy, cx, cy]), 
    result = detector.detect(aprilimg) #, estimate_tag_pose=False, tag_size=apriltag_size)

    #print (result)

    if (len(result) > 0):
        print("tags!")
        for tagnum in range (0, len(result)):
            tag = result[tagnum]
            
            if(tag.hamming < 1):
            
                #print (tag)
                x1 = int(tag.corners[0][0])
                y1 = int(tag.corners[0][1])
                x2 = int(tag.corners[1][0])
                y2 = int(tag.corners[1][1])
                cv2.line(aprilimgclr, (x1, y1), (x2, y2), (0, 0, 255), 2)

                x1 = int(tag.corners[1][0])
                y1 = int(tag.corners[1][1])
                x2 = int(tag.corners[2][0])
                y2 = int(tag.corners[2][1])
                cv2.line(aprilimgclr, (x1, y1), (x2, y2), (0, 255, 255), 2)

                x1 = int(tag.corners[2][0])
                y1 = int(tag.corners[2][1])
                x2 = int(tag.corners[3][0])
                y2 = int(tag.corners[3][1])
                cv2.line(aprilimgclr, (x1, y1), (x2, y2), (0, 255, 0), 2)

                x1 = int(tag.corners[3][0])
                y1 = int(tag.corners[3][1])
                x2 = int(tag.corners[0][0])
                y2 = int(tag.corners[0][1])
                cv2.line(aprilimgclr, (x1, y1), (x2, y2), (255, 128, 64), 2)
                
                np.set_printoptions(precision=3)
                
                pose_mat = tag.pose_R
                pose_t = [0,0,0]

                pose_t[0] = tag.pose_t[0]
                pose_t[1] = tag.pose_t[1]
                pose_t[2] = tag.pose_t[2]

                # xlabelstring = "X:" + str(pose_t[0])
                # ylabelstring = "Y:" + str(pose_t[1])
                # zlabelstring = "Z:" + str(pose_t[2])

                
                #ref https://gitlab.eecs.umich.edu/njanne/opencv-apriltag/-/blob/7a8530981fbc71bf7eb620ee1ea0ac11e82383bd/apriltag_pose_lcm.py#L74
                rot_matrix = R.from_matrix(pose_mat)
                pose_raw = rot_matrix.apply(np.resize(np.asarray(pose_t), 3), True)
                eulers = rot_matrix.as_euler('yxz', degrees=True) #Y=H, 
                # print(eulers) 

                xlabelstring = "Y:" + str(np.around(eulers[0], 2))
                ylabelstring = "P:" + str(np.around(eulers[1], 2))
                zlabelstring = "R:" + str(np.around(eulers[2], 2))

                pose_relative = [0,0,0]
                pose_relative[0] = pose_raw[1]
                pose_relative[1] = -pose_raw[2]
                pose_relative[2] = pose_raw[0]

                # xlabelstring = "X:" + str(pose_relative[0])
                # ylabelstring = "Y:" + str(pose_relative[1])
                # zlabelstring = "Z:" + str(pose_relative[2])
                
                textSize, baseline = cv2.getTextSize(xlabelstring, font, 1, 2)
                textyheight = textSize[1] + baseline
                cv2.rectangle(aprilimgclr, (int(tag.center[0]), int(tag.center[1] - textyheight)), (int(tag.center[0] + textSize[0]), int(tag.center[1]) + textyheight * 2), (255, 255, 255), -1)
                cv2.putText(aprilimgclr, xlabelstring, (int(tag.center[0]), int(tag.center[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 128, 128), 2)
                cv2.putText(aprilimgclr, ylabelstring, (int(tag.center[0]), int(tag.center[1]) + textyheight), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 128, 128), 2)
                cv2.putText(aprilimgclr, zlabelstring, (int(tag.center[0]), int(tag.center[1]) + textyheight * 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 128, 128), 2)

                # cv2.putText(aprilimgclr, '0', (int(tag.corners[0][0]), int(tag.corners[0][1]) + textyheight), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 128, 128), 2)
                # cv2.putText(aprilimgclr, '1', (int(tag.corners[1][0]), int(tag.corners[1][1]) + textyheight), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 128, 128), 2)
                # cv2.putText(aprilimgclr, '2', (int(tag.corners[2][0]), int(tag.corners[2][1]) + textyheight), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 128, 128), 2)
                # cv2.putText(aprilimgclr, '3', (int(tag.corners[3][0]), int(tag.corners[3][1]) + textyheight), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 128, 128), 2)
                
                
                #draw_pose(self,overlay, camera_params, tag_size, pose, z_sign=1):
                
                
                
    # time when we finish processing for this frame
    new_frame_time = time.time()
    delta_time = new_frame_time-prev_frame_time
    fps = 0
    if(delta_time > 0):
        fps = 1/delta_time
    prev_frame_time = new_frame_time
 
    # converting the fps into integer
    fps = int(fps)
 
    # converting the fps to string so that we can display it on frame
    # by using putText function
    fps = str(fps)
    # putting the FPS count on the frame
    cv2.putText(aprilimgclr, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)

    cv2.imshow('apriltag', aprilimgclr)

cv2.waitKey(1)

cam.release()

cv2.destroyAllWindows()


