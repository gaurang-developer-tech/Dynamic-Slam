"""
Visualization utilities for Dynamic SLAM
"""
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from config import Config


class Visualizer:
    """Visualize SLAM results"""
    
    def __init__(self, save_path=None):
        """
        Initialize visualizer
        
        Args:
            save_path: Directory to save visualizations
        """
        self.save_path = save_path or Config.RESULTS_DIR
        self.trajectory_plot = None
        self.fig = None
        self.ax = None
        
    def draw_matches(self, img1, kp1, img2, kp2, matches, mask=None):
        """
        Draw feature matches between two images
        
        Args:
            img1: First image
            kp1: Keypoints from first image
            img2: Second image
            kp2: Keypoints from second image
            matches: List of cv2.DMatch objects
            mask: Optional mask for inlier/outlier visualization
            
        Returns:
            result: Image with drawn matches
        """
        if mask is not None:
            # Draw only inliers
            matches_to_draw = [m for i, m in enumerate(matches) if mask[i]]
        else:
            matches_to_draw = matches
        
        # Draw matches
        result = cv2.drawMatches(
            img1, kp1, img2, kp2, matches_to_draw, None,
            matchColor=(0, 255, 0),
            singlePointColor=(255, 0, 0),
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
        )
        
        return result
    
    def draw_keypoints(self, image, keypoints, color=(0, 255, 0)):
        """
        Draw keypoints on image
        
        Args:
            image: Input image
            keypoints: List of cv2.KeyPoint objects
            color: Color for drawing (BGR)
            
        Returns:
            result: Image with drawn keypoints
        """
        result = cv2.drawKeypoints(
            image, keypoints, None,
            color=color,
            flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
        )
        return result
    
    def create_side_by_side(self, img1, img2, title1="Image 1", title2="Image 2"):
        """
        Create side-by-side visualization
        
        Args:
            img1: First image
            img2: Second image
            title1: Title for first image
            title2: Title for second image
            
        Returns:
            result: Combined image
        """
        # Resize if different sizes
        if img1.shape != img2.shape:
            h = max(img1.shape[0], img2.shape[0])
            w = max(img1.shape[1], img2.shape[1])
            
            img1_resized = cv2.resize(img1, (w, h))
            img2_resized = cv2.resize(img2, (w, h))
        else:
            img1_resized = img1
            img2_resized = img2
        
        # Combine horizontally
        result = np.hstack((img1_resized, img2_resized))
        
        # Add titles
        cv2.putText(
            result, title1, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
        )
        cv2.putText(
            result, title2, (img1_resized.shape[1] + 10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
        )
        
        return result
    
    def plot_trajectory_2d(self, estimated_poses, gt_poses=None, save_name=None):
        """
        Plot 2D bird's eye view of trajectory
        
        Args:
            estimated_poses: List of estimated 4x4 transformation matrices
            gt_poses: Optional list of ground truth poses
            save_name: Filename to save plot
        """
        plt.figure(figsize=(12, 12))
        
        # Extract x, z coordinates (bird's eye view)
        est_x = [pose[0, 3] for pose in estimated_poses]
        est_z = [pose[2, 3] for pose in estimated_poses]
        
        plt.plot(est_x, est_z, 'b-', label='Estimated', linewidth=2)
        plt.plot(est_x[0], est_z[0], 'go', markersize=10, label='Start')
        plt.plot(est_x[-1], est_z[-1], 'ro', markersize=10, label='End')
        
        if gt_poses is not None:
            gt_x = [pose[0, 3] for pose in gt_poses]
            gt_z = [pose[2, 3] for pose in gt_poses]
            plt.plot(gt_x, gt_z, 'r--', label='Ground Truth', linewidth=2, alpha=0.7)
        
        plt.xlabel('X (meters)', fontsize=12)
        plt.ylabel('Z (meters)', fontsize=12)
        plt.title('Camera Trajectory (Bird\'s Eye View)', fontsize=14)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        
        if save_name:
            save_path = Config.get_results_path(save_name)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Trajectory plot saved to {save_path}")
        
        plt.close()
    
    def plot_trajectory_3d(self, estimated_poses, gt_poses=None, save_name=None):
        """
        Plot 3D trajectory
        
        Args:
            estimated_poses: List of estimated 4x4 transformation matrices
            gt_poses: Optional list of ground truth poses
            save_name: Filename to save plot
        """
        from mpl_toolkits.mplot3d import Axes3D
        
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Extract x, y, z coordinates
        est_x = [pose[0, 3] for pose in estimated_poses]
        est_y = [pose[1, 3] for pose in estimated_poses]
        est_z = [pose[2, 3] for pose in estimated_poses]
        
        ax.plot(est_x, est_z, est_y, 'b-', label='Estimated', linewidth=2)
        ax.scatter(est_x[0], est_z[0], est_y[0], c='g', s=100, label='Start')
        ax.scatter(est_x[-1], est_z[-1], est_y[-1], c='r', s=100, label='End')
        
        if gt_poses is not None:
            gt_x = [pose[0, 3] for pose in gt_poses]
            gt_y = [pose[1, 3] for pose in gt_poses]
            gt_z = [pose[2, 3] for pose in gt_poses]
            ax.plot(gt_x, gt_z, gt_y, 'r--', label='Ground Truth', linewidth=2, alpha=0.7)
        
        ax.set_xlabel('X (meters)', fontsize=12)
        ax.set_ylabel('Z (meters)', fontsize=12)
        ax.set_zlabel('Y (meters)', fontsize=12)
        ax.set_title('Camera Trajectory (3D)', fontsize=14)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        if save_name:
            save_path = Config.get_results_path(save_name)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"3D trajectory plot saved to {save_path}")
        
        plt.close()
    
    def create_info_panel(self, frame_id, num_features, num_matches, num_inliers,
                         translation_norm, num_dynamic_objects):
        """
        Create information panel image
        
        Args:
            frame_id: Current frame number
            num_features: Number of extracted features
            num_matches: Number of feature matches
            num_inliers: Number of inlier matches
            translation_norm: Magnitude of translation
            num_dynamic_objects: Number of detected dynamic objects
            
        Returns:
            panel: Image with information overlay
        """
        panel = np.zeros((200, 400, 3), dtype=np.uint8)
        
        # Add text
        y_offset = 30
        line_height = 30
        
        info_lines = [
            f"Frame: {frame_id}",
            f"Features: {num_features}",
            f"Matches: {num_matches}",
            f"Inliers: {num_inliers}",
            f"Translation: {translation_norm:.3f}m",
            f"Dynamic Objects: {num_dynamic_objects}"
        ]
        
        for i, line in enumerate(info_lines):
            y = y_offset + i * line_height
            cv2.putText(
                panel, line, (10, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
            )
        
        return panel
    
    def save_image(self, image, filename):
        """
        Save image to results directory
        
        Args:
            image: Image to save
            filename: Filename
        """
        save_path = Config.get_results_path(filename)
        cv2.imwrite(save_path, image)
        return save_path


def plot_errors(errors_dict, save_name="errors.png"):
    """
    Plot trajectory errors over time
    
    Args:
        errors_dict: Dictionary with error metrics
        save_name: Filename to save plot
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # Plot translation errors
    if 'trans_errors' in errors_dict:
        axes[0].plot(errors_dict['trans_errors'], 'b-', linewidth=1)
        axes[0].set_ylabel('Translation Error (m)', fontsize=12)
        axes[0].set_title('Translation Error per Frame', fontsize=14)
        axes[0].grid(True, alpha=0.3)
    
    # Plot rotation errors
    if 'rot_errors' in errors_dict:
        axes[1].plot(errors_dict['rot_errors'], 'r-', linewidth=1)
        axes[1].set_ylabel('Rotation Error (deg)', fontsize=12)
        axes[1].set_xlabel('Frame Number', fontsize=12)
        axes[1].set_title('Rotation Error per Frame', fontsize=14)
        axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    save_path = Config.get_results_path(save_name)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Error plot saved to {save_path}")
    plt.close()
