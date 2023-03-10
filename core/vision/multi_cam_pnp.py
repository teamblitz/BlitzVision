import cv2
import numpy as np
from scipy import linalg
from scipy.spatial.transform import Rotation as R


def calc_cam_to_general_transform(cam_pose):
    """
    cam pose: (translation vector, rotation matrix)

    returns: homogeneous transform matrix Tcg that transforms points from the camera, to general coordinate frame
    """

    transform = np.zeros((4, 4))
    transform[0:3, 0:3] = cam_pose[1]
    transform[0:3, 3] = cam_pose[0]
    transform[3, 3] = 1
    return transform


def calc(obj_points, img_points, cam_general_transforms, camera_matrices, dist_coeffs):
    """
        obj_points:
            an "array like" of length n representing object points in the real world
        img_points:
            same as obj points
        cam_general_transform:
            Tcg transformation matrix that brings points from the camera to the general coordinate frame.
            There should be 4 of these.
        returns:
            homogeneous matrix Tgw transformation form the general camera frame to the world camera frame.
            int of iterations taken to find the pose
    """
    print(img_points)
    line_versors = []
    line_origins = []
    object_points = []
    for i in range(0, 4):
        if len(img_points[i]) > 1:
            undistorted_points = cv2.undistortPoints(np.asarray(img_points[i]), camera_matrices[i], dist_coeffs[i])
            for j in range(len(undistorted_points)):
                # make the point a vector
                point = np.empty(3)
                # print("Undistorted Point")
                # print(undistorted_points[j])
                point[:2] = undistorted_points[j] # - [1280 / 2, 800 / 2]
                point[2] = 1
                
                # print("Shifted Point")
                # print(point)
                
                point = point * (1 / linalg.norm(point))
                # print("Normalized vector")
                # print(point)

                # orient and rotate axes
                point = cam_general_transforms[i][0:3, 0:3] @ (np.array(([0, 0, 1],
                                                                         [-1, 0, 0],
                                                                         [0, -1, 0])) @ point)
                
                # print("Rotated Point")
                # print(point)
                # normalize it to be a unit vector
                line_versors.append(point)

                # pull out the origin
                line_origins.append(cam_general_transforms[i][0:3, 3])
                # add the object points
                object_points.append(obj_points[i][j])
    line_versors_matrix = np.asarray(line_versors)
    line_origins_matrix = np.asarray(line_origins)
    object_points_matrix = np.asarray(object_points)

    # print("Line_versors")
    # print(line_versors_matrix)

    # print("Line origins")
    # print(line_origins_matrix)

    # print("Object points")
    # print(object_points_matrix)
    
    return gPPnP(line_versors_matrix, line_origins_matrix, object_points_matrix,
                 tol=(0.0001 ** 2) * np.prod(object_points_matrix.shape))


# function [R t, a] = gPPnP(P,O,S,tol,pz)
# from A. Fusiello, F. Crosilla, and F. Malapelle, “Procrustean point-line
# registration and the NPnP problem,” in 2015 International Conference on
# 3D Vision, Oct. 2015, pp. 250–255. doi: 10.1109/3DV.2015.35.
def gPPnP(P, O, S, tol, pz=True, unit_scale=True):
    """
    input
        P : matrix (nx3) of line versors
        O : matrix (nx3) of line origins
        S : matrix (nx3) 3D coordinates
        tol: exit tolerance
        pZ : positive Z flag
        unit_scale : whether or not to compute the scale factor
    output
        T: Euclidean transform from frame of P and O to frame of S
        iter: number of iterations to reach tolernce
    """
    n = P.shape[0]
    # print(P.shape, O.shape, S.shape)
    Z = np.diag(np.ones(n))  # Z is n x n
    II = np.identity(n) - np.full((n, n), 1.0 / n)  # II is n x n
    err = np.inf
    E_old = 1000 * np.ones((n, 3))  # E_old is n x 3
    D = linalg.khatri_rao(np.identity(n), P.T)  # D is 3n x n
    iter = 0
    while err > tol:
        iter += 1
        U, _, Vt = np.linalg.svd((Z @ P + O).T @ II @ S)  # (Z @ P + O).T @ II @ S is 3 x 3, U and Vt are 3 x 3
        R = U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt  # R is 3 x 3
        A = Z @ P + O  # A is n x 3
        AR = A @ R  # AR is n x 3
        if unit_scale:
            a = 1
        else:
            a = np.trace(A.T @ II @ A) / np.trace(AR.T @ II @ S)  # A.T @ II @ A is 3 x 3, AR.T @ II @ S is 3 x 3

        c = np.mean(a * S - AR, axis=0, keepdims=True).T  # c is 3 x 1
        X = a * S - O @ R - np.ones((n, 1)) @ c.T  # X is n x 3
        vecY = (R @ X.T).reshape((-1, 1), order="F")  # R @ X.T is 3 x n, vecY is 3n x 1
        v, _, _, _ = np.linalg.lstsq(D, vecY, rcond=None)  # v is n by 1
        if pz:
            v[v < 0] = 0

        # print("v shape is ", v.shape)
        Z = np.diag(v.reshape(-1))  # Z is n x n
        E = X - Z @ P @ R  # E is n x 3
        err = np.linalg.norm(E - E_old)
        E_old = E

    t = -R @ c

    return np.vstack((np.hstack((R.T, -R.T @ t)),
                      np.array([0, 0, 0, 1]))), iter


# function [R t, a] = gFiore(P,O,S)
def gFiore(P, O, S, unit_scale=True):
    """
    input
        P : matrix (nx3) of line versors
        O : matrix (nx3) of line origins
        S : matrix (nx3) 3D coordinates
        unit_scale : whether or not to compute the scale factor
    output
        T: Euclidean transform from frame of P and O to frame of S
    """
    n = P.shape[0]
    II = np.identity(n) - np.full((n, n), 1.0 / n)
    M = np.concatenate((S, np.ones((n, 1))), axis=1).T
    _, sv, Vt = np.linalg.svd(M)
    tol = sv.max() * max(M.shape) * np.finfo(M.dtype).eps
    rankM = (sv > tol).sum()
    # print("rank M is ", rankM)
    Vrt = Vt[rankM:, :]
    # print("shape of Vrt is ", Vrt.shape)
    D = (P @ P.T) * (Vrt.T @ Vrt)
    # print("D is ", D)
    b = -np.diag((Vrt.T @ Vrt @ O @ P.T))
    # print("b is ", b)
    v, _, _, _ = np.linalg.lstsq(D, b, rcond=None)
    # print("v is ", v)
    Z = np.diag(v.reshape(-1))
    U, _, Vt = np.linalg.svd((Z @ P + O).T @ II @ S)
    R = U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt
    A = Z @ P + O
    AR = A @ R
    if unit_scale:
        a = 1
    else:
        a = np.trace(A.T @ II @ A) / np.trace(AR.T @ II @ S)

    c = np.mean(a * S - AR, axis=0, keepdims=True).T
    t = -R @ c

    return np.vstack((np.hstack((R.T, -R.T @ t)),
                      np.array([0, 0, 0, 1])))
