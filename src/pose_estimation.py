"""
Pose estimation module for Dynamic SLAM
"""
import cv2
import numpy as np
from config import Config


class PoseEstimator:
    """Estimate camera pose from feature matches"""
    
    def __init__(self, camera_matrix):
        """
        Initialize pose estimator
        
        Args:
            camera_matrix: 3x3 camera intrinsic matrix K
        """
        self.K = camera_matrix
        self.last_pose = np.eye(4)  # Initialize at origin
        
    def estimate_pose_essential(self, pts1, pts2):
        """
        Estimate relative pose using Essential Matrix
        
        Args:
            pts1: Nx2 array of points from first image
            pts2: Nx2 array of points from second image
            
        Returns:
            R: 3x3 rotation matrix
            t: 3x1 translation vector
            inlier_mask: Boolean mask of inliers
        """
        if len(pts1) < Config.MIN_MATCH_COUNT:
            return None, None, None
        
        # Compute Essential Matrix with RANSAC
        E, mask = cv2.findEssentialMat(
            pts1, pts2, self.K,
            method=cv2.RANSAC,
            prob=Config.RANSAC_CONFIDENCE,
            threshold=Config.RANSAC_REPROJ_THRESHOLD
        )
        
        if E is None:
            return None, None, None
        
        # Recover pose from Essential Matrix
        _, R, t, pose_mask = cv2.recoverPose(E, pts1, pts2, self.K, mask=mask)
        
        # Combine masks
        inlier_mask = (mask.ravel() == 1) & (pose_mask.ravel() > 0)
        
        return R, t, inlier_mask
    
    def estimate_pose_pnp(self, pts_2d, pts_3d):
        """
        Estimate absolute pose using PnP (when 3D points are available)
        
        Args:
            pts_2d: Nx2 array of 2D image points
            pts_3d: Nx3 array of 3D world points
            
        Returns:
            R: 3x3 rotation matrix
            t: 3x1 translation vector
            inlier_mask: Boolean mask of inliers
        """
        if len(pts_2d) < Config.MIN_MATCH_COUNT:
            return None, None, None
        
        # Use RANSAC-based PnP
        success, rvec, tvec, inliers = cv2.solvePnPRansac(
            pts_3d, pts_2d, self.K, None,
            reprojectionError=Config.RANSAC_REPROJ_THRESHOLD,
            confidence=Config.RANSAC_CONFIDENCE,
            iterationsCount=Config.RANSAC_MAX_ITERS
        )
        
        if not success:
            return None, None, None
        
        # Convert rotation vector to matrix
        R, _ = cv2.Rodrigues(rvec)
        t = tvec
        
        # Create inlier mask
        inlier_mask = np.zeros(len(pts_2d), dtype=bool)
        if inliers is not None:
            inlier_mask[inliers.ravel()] = True
        
        return R, t, inlier_mask
    
    def triangulate_points(self, pts1, pts2, T1, T2):
        """
        Triangulate 3D points from two views
        
        Args:
            pts1: Nx2 array of points from first image
            pts2: Nx2 array of points from second image
            T1: 4x4 transformation matrix of first camera
            T2: 4x4 transformation matrix of second camera
            
        Returns:
            points_3d: Nx3 array of 3D points in world coordinates
        """
        # Projection matrices
        P1 = self.K @ T1[:3, :]
        P2 = self.K @ T2[:3, :]
        
        # Triangulate
        pts1_norm = pts1.T
        pts2_norm = pts2.T
        
        points_4d = cv2.triangulatePoints(P1, P2, pts1_norm, pts2_norm)
        
        # Convert from homogeneous to 3D
        points_3d = points_4d[:3, :] / points_4d[3, :]
        points_3d = points_3d.T
        
        return points_3d
    
    def filter_triangulated_points(self, points_3d, min_depth=None, max_depth=None):
        """
        Filter triangulated points based on depth
        
        Args:
            points_3d: Nx3 array of 3D points
            min_depth: Minimum depth threshold
            max_depth: Maximum depth threshold
            
        Returns:
            valid_mask: Boolean mask of valid points
        """
        min_d = min_depth or Config.MIN_DEPTH
        max_d = max_depth or Config.MAX_DEPTH
        
        # Calculate depth (Z coordinate)
        depths = points_3d[:, 2]
        
        # Filter by depth range
        valid_mask = (depths > min_d) & (depths < max_d)
        
        return valid_mask
    
    def update_pose(self, R, t, scale=1.0):
        """
        Update absolute camera pose
        
        Args:
            R: 3x3 relative rotation matrix
            t: 3x1 relative translation vector
            scale: Scale factor for translation
            
        Returns:
            T: 4x4 updated absolute transformation matrix
        """
        # Create relative transformation
        T_rel = np.eye(4)
        T_rel[:3, :3] = R
        T_rel[:3, 3] = (t * scale).flatten()
        
        # Update absolute pose
        self.last_pose = self.last_pose @ T_rel
        
        return self.last_pose.copy()
    
    def set_pose(self, T):
        """
        Set absolute camera pose
        
        Args:
            T: 4x4 transformation matrix
        """
        self.last_pose = T.copy()
    
    def get_pose(self):
        """
        Get current camera pose
        
        Returns:
            T: 4x4 transformation matrix
        """
        return self.last_pose.copy()


class ScaleEstimator:
    """Estimate scale for monocular SLAM"""
    
    def __init__(self, window_size=10):
        """
        Initialize scale estimator
        
        Args:
            window_size: Number of frames to use for scale estimation
        """
        self.window_size = window_size
        self.estimated_translations = []
        self.gt_translations = []
        
    def add_measurement(self, estimated_t, gt_t):
        """
        Add translation measurement
        
        Args:
            estimated_t: Estimated translation vector
            gt_t: Ground truth translation vector
        """
        est_norm = np.linalg.norm(estimated_t)
        gt_norm = np.linalg.norm(gt_t)
        
        if est_norm > 1e-6:  # Avoid division by zero
            self.estimated_translations.append(est_norm)
            self.gt_translations.append(gt_norm)
            
            # Keep only recent measurements
            if len(self.estimated_translations) > self.window_size:
                self.estimated_translations.pop(0)
                self.gt_translations.pop(0)
    
    def get_scale(self):
        """
        Compute scale factor
        
        Returns:
            float: Scale factor
        """
        if len(self.estimated_translations) == 0:
            return 1.0
        
        # Compute scale as ratio of sums
        est_sum = sum(self.estimated_translations)
        gt_sum = sum(self.gt_translations)
        
        if est_sum > 1e-6:
            return gt_sum / est_sum
        return 1.0
