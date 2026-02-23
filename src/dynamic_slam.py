"""
Main Dynamic SLAM Pipeline
Integrates all components: feature extraction, dynamic detection, and pose estimation
"""
import cv2
import numpy as np
import os
from tqdm import tqdm

from config import Config
from utils import (
    load_kitti_calibration, get_camera_intrinsics,
    load_ground_truth_poses, get_image_list,
    pose_to_transformation_matrix
)
from dynamic_detector import DynamicObjectDetector
from feature_extraction import FeatureExtractor, FeatureMatcher
from pose_estimation import PoseEstimator, ScaleEstimator
from visualization import Visualizer, plot_errors


class DynamicSLAM:
    """Main Dynamic SLAM system"""
    
    def __init__(self, sequence=None):
        """
        Initialize Dynamic SLAM system
        
        Args:
            sequence: Sequence ID (e.g., "00", "01")
        """
        self.sequence = sequence or Config.SEQUENCE
        
        # Load calibration
        calib_path = Config.get_calib_path(self.sequence)
        self.calib = load_kitti_calibration(calib_path)
        self.K = get_camera_intrinsics(self.calib, camera_id=0)
        
        # Initialize modules
        print("Initializing Dynamic SLAM components...")
        self.detector = DynamicObjectDetector()
        self.feature_extractor = FeatureExtractor()
        self.feature_matcher = FeatureMatcher()
        self.pose_estimator = PoseEstimator(self.K)
        self.scale_estimator = ScaleEstimator()
        self.visualizer = Visualizer()
        
        # Load ground truth if available
        self.gt_poses = None
        gt_path = Config.get_poses_path(self.sequence)
        if os.path.exists(gt_path):
            self.gt_poses = load_ground_truth_poses(gt_path)
            print(f"Loaded {len(self.gt_poses)} ground truth poses")
        
        # Storage
        self.estimated_poses = []
        self.frame_data = []
        
        print("Dynamic SLAM initialized successfully!")
    
    def process_sequence(self, start_frame=None, end_frame=None):
        """
        Process entire sequence
        
        Args:
            start_frame: Start frame index
            end_frame: End frame index (None = process all)
        """
        # Get image list
        sequence_path = Config.get_sequence_path(self.sequence)
        image_files = get_image_list(sequence_path)
        
        if len(image_files) == 0:
            print(f"ERROR: No images found in {sequence_path}")
            return
        
        # Determine frame range
        start = start_frame or Config.START_FRAME
        end = end_frame or Config.END_FRAME or len(image_files)
        end = min(end, len(image_files))
        
        print(f"\nProcessing sequence {self.sequence}")
        print(f"Frames: {start} to {end} (Total: {end - start})")
        print(f"Image size: {cv2.imread(image_files[0]).shape}")
        print("-" * 60)
        
        # Initialize with first frame
        self.estimated_poses = [np.eye(4)]  # Start at origin
        
        # Previous frame data
        prev_image = None
        prev_keypoints = None
        prev_descriptors = None
        prev_points_3d = None
        
        # Process frames
        for i in tqdm(range(start, end), desc="Processing frames"):
            # Load image
            img = cv2.imread(image_files[i])
            
            # Detect dynamic objects
            dynamic_mask = self.detector.detect(img)
            
            # Extract features (static regions only)
            keypoints, descriptors = self.feature_extractor.extract_features(
                img, dynamic_mask, return_static_only=True
            )
            
            # Get detection info
            _, yolo_result = self.detector.detect(img, return_results=True)
            det_info = self.detector.get_detection_info(yolo_result)
            
            # Store frame data
            frame_info = {
                'frame_id': i,
                'num_features': len(keypoints),
                'num_dynamic_objects': det_info['num_objects'],
                'dynamic_classes': det_info['classes']
            }
            
            # Process if we have previous frame
            if prev_image is not None and prev_descriptors is not None:
                # Match features
                matches = self.feature_matcher.match(prev_descriptors, descriptors)
                
                if len(matches) >= Config.MIN_MATCH_COUNT:
                    # Get matched points
                    pts1, pts2 = self.feature_matcher.get_matched_points(
                        prev_keypoints, keypoints, matches
                    )
                    
                    # Estimate pose
                    R, t, inlier_mask = self.pose_estimator.estimate_pose_essential(pts1, pts2)
                    
                    if R is not None and t is not None:
                        num_inliers = np.sum(inlier_mask)
                        
                        # Scale estimation using ground truth (if available)
                        scale = 1.0
                        if self.gt_poses is not None and i < len(self.gt_poses):
                            gt_t = self.gt_poses[i][:3, 3] - self.gt_poses[i-1][:3, 3]
                            self.scale_estimator.add_measurement(t, gt_t)
                            scale = self.scale_estimator.get_scale()
                        
                        # Update pose
                        current_pose = self.pose_estimator.update_pose(R, t, scale)
                        self.estimated_poses.append(current_pose.copy())
                        
                        # Update frame info
                        frame_info['num_matches'] = len(matches)
                        frame_info['num_inliers'] = num_inliers
                        frame_info['translation_norm'] = np.linalg.norm(t * scale)
                        
                        # Save visualization if enabled
                        if Config.SAVE_INTERMEDIATE_RESULTS and i % 10 == 0:
                            self._save_frame_visualization(
                                prev_image, img, prev_keypoints, keypoints,
                                matches, inlier_mask, dynamic_mask, frame_info
                            )
                    else:
                        # Failed to estimate pose, repeat last pose
                        self.estimated_poses.append(self.estimated_poses[-1].copy())
                        frame_info['num_matches'] = len(matches)
                        frame_info['num_inliers'] = 0
                else:
                    # Not enough matches, repeat last pose
                    self.estimated_poses.append(self.estimated_poses[-1].copy())
                    frame_info['num_matches'] = len(matches) if matches else 0
                    frame_info['num_inliers'] = 0
            
            # Store frame data
            self.frame_data.append(frame_info)
            
            # Update previous frame
            prev_image = img
            prev_keypoints = keypoints
            prev_descriptors = descriptors
        
        print("\n" + "=" * 60)
        print("Processing complete!")
        print(f"Estimated {len(self.estimated_poses)} poses")
        
        # Generate results
        self._generate_results()
    
    def _save_frame_visualization(self, img1, img2, kp1, kp2, matches, 
                                  inlier_mask, dynamic_mask, frame_info):
        """Save visualization for a frame"""
        # Draw matches
        matches_img = self.visualizer.draw_matches(
            img1, kp1, img2, kp2, matches, inlier_mask
        )
        
        # Resize for display
        scale = Config.DISPLAY_SCALE
        h, w = matches_img.shape[:2]
        matches_img = cv2.resize(matches_img, (int(w * scale), int(h * scale)))
        
        # Save
        filename = f"frame_{frame_info['frame_id']:06d}_matches.jpg"
        self.visualizer.save_image(matches_img, filename)
    
    def _generate_results(self):
        """Generate and save results"""
        print("\nGenerating results...")
        
        # Save trajectory plots
        if len(self.estimated_poses) > 1:
            self.visualizer.plot_trajectory_2d(
                self.estimated_poses,
                self.gt_poses,
                save_name=f"trajectory_2d_seq{self.sequence}.png"
            )
            
            self.visualizer.plot_trajectory_3d(
                self.estimated_poses,
                self.gt_poses,
                save_name=f"trajectory_3d_seq{self.sequence}.png"
            )
        
        # Save trajectory to file
        self._save_trajectory()
        
        # Compute errors if ground truth available
        if self.gt_poses is not None:
            self._compute_errors()
        
        # Print statistics
        self._print_statistics()
    
    def _save_trajectory(self):
        """Save estimated trajectory to file"""
        filename = Config.get_results_path(f"trajectory_seq{self.sequence}.txt")
        
        with open(filename, 'w') as f:
            for pose in self.estimated_poses:
                # Save as KITTI format (3x4 matrix)
                row = pose[:3, :].flatten()
                f.write(' '.join([f'{x:.6e}' for x in row]) + '\n')
        
        print(f"Trajectory saved to {filename}")
    
    def _compute_errors(self):
        """Compute trajectory errors against ground truth"""
        trans_errors = []
        rot_errors = []
        
        n = min(len(self.estimated_poses), len(self.gt_poses))
        
        for i in range(n):
            est_pose = self.estimated_poses[i]
            gt_pose = self.gt_poses[i]
            
            # Translation error
            trans_error = np.linalg.norm(est_pose[:3, 3] - gt_pose[:3, 3])
            trans_errors.append(trans_error)
            
            # Rotation error
            R_est = est_pose[:3, :3]
            R_gt = gt_pose[:3, :3]
            R_error = R_est.T @ R_gt
            angle_error = np.arccos(np.clip((np.trace(R_error) - 1) / 2, -1, 1))
            rot_errors.append(np.degrees(angle_error))
        
        # Plot errors
        plot_errors(
            {'trans_errors': trans_errors, 'rot_errors': rot_errors},
            save_name=f"errors_seq{self.sequence}.png"
        )
        
        # Save error statistics
        stats_file = Config.get_results_path(f"error_stats_seq{self.sequence}.txt")
        with open(stats_file, 'w') as f:
            f.write(f"Translation Error (m):\n")
            f.write(f"  Mean: {np.mean(trans_errors):.4f}\n")
            f.write(f"  Median: {np.median(trans_errors):.4f}\n")
            f.write(f"  Std: {np.std(trans_errors):.4f}\n")
            f.write(f"  Max: {np.max(trans_errors):.4f}\n")
            f.write(f"\nRotation Error (deg):\n")
            f.write(f"  Mean: {np.mean(rot_errors):.4f}\n")
            f.write(f"  Median: {np.median(rot_errors):.4f}\n")
            f.write(f"  Std: {np.std(rot_errors):.4f}\n")
            f.write(f"  Max: {np.max(rot_errors):.4f}\n")
        
        print(f"Error statistics saved to {stats_file}")
    
    def _print_statistics(self):
        """Print processing statistics"""
        print("\n" + "=" * 60)
        print("STATISTICS")
        print("=" * 60)
        
        total_frames = len(self.frame_data)
        
        # Feature statistics
        avg_features = np.mean([f['num_features'] for f in self.frame_data])
        avg_matches = np.mean([f.get('num_matches', 0) for f in self.frame_data[1:]])
        avg_inliers = np.mean([f.get('num_inliers', 0) for f in self.frame_data[1:]])
        
        # Dynamic object statistics
        avg_dynamic = np.mean([f['num_dynamic_objects'] for f in self.frame_data])
        frames_with_dynamic = sum([1 for f in self.frame_data if f['num_dynamic_objects'] > 0])
        
        print(f"Total Frames Processed: {total_frames}")
        print(f"Average Features per Frame: {avg_features:.1f}")
        print(f"Average Matches per Frame: {avg_matches:.1f}")
        print(f"Average Inliers per Frame: {avg_inliers:.1f}")
        print(f"Average Dynamic Objects: {avg_dynamic:.2f}")
        print(f"Frames with Dynamic Objects: {frames_with_dynamic} ({frames_with_dynamic/total_frames*100:.1f}%)")
        print("=" * 60)


def main():
    """Main entry point"""
    # Parse arguments or use defaults
    sequence = Config.SEQUENCE
    
    # Create and run SLAM
    slam = DynamicSLAM(sequence=sequence)
    slam.process_sequence()
    
    print("\nDynamic SLAM completed successfully!")
    print(f"Results saved to: {Config.RESULTS_DIR}")


if __name__ == "__main__":
    main()
