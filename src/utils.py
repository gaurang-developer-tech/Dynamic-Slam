"""
Utility functions for Dynamic SLAM
"""
import numpy as np
import cv2
import os
from glob import glob


def load_kitti_calibration(calib_path):
    """
    Load KITTI calibration file
    
    Args:
        calib_path: Path to calib.txt
        
    Returns:
        dict: Calibration matrices (P0, P1, P2, P3)
    """
    calib = {}
    with open(calib_path, 'r') as f:
        for line in f.readlines():
            key, value = line.split(':', 1)
            calib[key] = np.array([float(x) for x in value.split()])
    
    # Reshape projection matrices
    for key in ['P0', 'P1', 'P2', 'P3']:
        if key in calib:
            calib[key] = calib[key].reshape(3, 4)
    
    return calib


def get_camera_intrinsics(calib_dict, camera_id=0):
    """
    Extract camera intrinsic matrix from calibration
    
    Args:
        calib_dict: Calibration dictionary
        camera_id: Camera ID (0 for left camera)
        
    Returns:
        K: 3x3 intrinsic matrix
    """
    P = calib_dict[f'P{camera_id}']
    K = P[:3, :3]
    return K


def load_ground_truth_poses(poses_path):
    """
    Load ground truth poses from KITTI format
    
    Args:
        poses_path: Path to poses file
        
    Returns:
        list: List of 4x4 transformation matrices
    """
    poses = []
    with open(poses_path, 'r') as f:
        for line in f.readlines():
            T = np.fromstring(line, dtype=np.float64, sep=' ')
            T = T.reshape(3, 4)
            T = np.vstack((T, [0, 0, 0, 1]))
            poses.append(T)
    return poses


def get_image_list(sequence_path):
    """
    Get sorted list of images in sequence
    
    Args:
        sequence_path: Path to image directory
        
    Returns:
        list: Sorted list of image paths
    """
    image_files = sorted(glob(os.path.join(sequence_path, "*.png")))
    if len(image_files) == 0:
        image_files = sorted(glob(os.path.join(sequence_path, "*.jpg")))
    return image_files


def pose_to_transformation_matrix(R, t):
    """
    Convert rotation and translation to 4x4 transformation matrix
    
    Args:
        R: 3x3 rotation matrix
        t: 3x1 translation vector
        
    Returns:
        T: 4x4 transformation matrix
    """
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t.flatten()
    return T


def transformation_matrix_to_pose(T):
    """
    Extract rotation and translation from 4x4 transformation matrix
    
    Args:
        T: 4x4 transformation matrix
        
    Returns:
        R: 3x3 rotation matrix
        t: 3x1 translation vector
    """
    R = T[:3, :3]
    t = T[:3, 3].reshape(3, 1)
    return R, t


def euler_angles_from_rotation_matrix(R):
    """
    Calculate euler angles from rotation matrix
    
    Args:
        R: 3x3 rotation matrix
        
    Returns:
        roll, pitch, yaw in degrees
    """
    sy = np.sqrt(R[0, 0]**2 + R[1, 0]**2)
    
    singular = sy < 1e-6
    
    if not singular:
        roll = np.arctan2(R[2, 1], R[2, 2])
        pitch = np.arctan2(-R[2, 0], sy)
        yaw = np.arctan2(R[1, 0], R[0, 0])
    else:
        roll = np.arctan2(-R[1, 2], R[1, 1])
        pitch = np.arctan2(-R[2, 0], sy)
        yaw = 0
    
    return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)


def compute_trajectory_length(poses):
    """
    Compute total trajectory length
    
    Args:
        poses: List of 4x4 transformation matrices
        
    Returns:
        float: Total distance traveled
    """
    total_distance = 0
    for i in range(len(poses) - 1):
        t1 = poses[i][:3, 3]
        t2 = poses[i+1][:3, 3]
        total_distance += np.linalg.norm(t2 - t1)
    return total_distance


def scale_trajectory(estimated_poses, gt_poses):
    """
    Scale estimated trajectory to match ground truth scale
    (For monocular SLAM which has scale ambiguity)
    
    Args:
        estimated_poses: List of estimated 4x4 transformation matrices
        gt_poses: List of ground truth 4x4 transformation matrices
        
    Returns:
        list: Scaled estimated poses
    """
    est_length = compute_trajectory_length(estimated_poses)
    gt_length = compute_trajectory_length(gt_poses)
    
    if est_length == 0:
        return estimated_poses
    
    scale = gt_length / est_length
    
    scaled_poses = []
    for pose in estimated_poses:
        scaled_pose = pose.copy()
        scaled_pose[:3, 3] *= scale
        scaled_poses.append(scaled_pose)
    
    return scaled_poses
