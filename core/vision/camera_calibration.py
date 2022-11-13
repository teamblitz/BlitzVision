import cv2
import numpy as np

# https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_calib3d/py_calibration/py_calibration.html
class CameraCalibration:

    # Define the chess board rows and columns
    rows: int
    columns: int

    # Set the termination criteria for the corner sub-pixel algorithm
    criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 0.001)

    # Create the arrays to store the object points and the image points
    objectPointsArray = []
    imgPointsArray = []

    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns

        # Prepare the object points: (0,0,0), (1,0,0), (2,0,0), ..., (6,5,0). They are the same for all images
        self.objectPoints = np.zeros((rows * columns, 3), np.float32)
        self.objectPoints[:, :2] = np.mgrid[0:rows, 0:columns].T.reshape(-1, 2)*21.757

    def show_pattern(self, img):
        '''Draw calibration grid on the image and return true if detected.'''
        # Convert to gray scale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (self.rows, self.columns), None)

        # Make sure the chess board pattern was found in the image
        if ret:
            # Refine the corner position
            corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), self.criteria)

            # Draw the corners on the image
            cv2.drawChessboardCorners(img, (self.rows, self.columns), corners, ret)

        return (ret, img)
    
    def add_to_calibration(self, img):

        # Convert to gray scale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (self.rows, self.columns), None)

        # Make sure the chess board pattern was found in the image
        if ret:
            # Refine the corner position
            corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), self.criteria)
            
            # Add the object points and the image points to the arrays
            self.objectPointsArray.append(self.objectPoints)
            self.imgPointsArray.append(corners)

            # Draw the corners on the image
            cv2.drawChessboardCorners(img, (self.rows, self.columns), corners, ret)

        # Should return true if adding to calibration was successful.
        return ret

    def finish_calibration(self, imageSize):
        return cv2.calibrateCamera(self.objectPointsArray, self.imgPointsArray, imageSize, None, None)

def get_image_size(img):
    return img.shape[::-1]