"""
Demo script for Dynamic SLAM
Run quick tests on a few frames
"""
import cv2
import os
from config import Config
from dynamic_slam import DynamicSLAM


def demo_feature_extraction():
    """Demo: Feature extraction with dynamic masking"""
    from utils import get_image_list
    from dynamic_detector import DynamicObjectDetector
    from feature_extraction import FeatureExtractor
    from visualization import Visualizer
    
    print("\n" + "=" * 60)
    print("DEMO: Feature Extraction with Dynamic Object Filtering")
    print("=" * 60)
    
    # Get first image
    sequence_path = Config.get_sequence_path("00")
    image_files = get_image_list(sequence_path)
    
    if len(image_files) == 0:
        print("ERROR: No images found!")
        return
    
    img = cv2.imread(image_files[0])
    
    # Detect dynamic objects
    detector = DynamicObjectDetector()
    dynamic_mask = detector.detect(img)
    
    # Extract features (all features)
    extractor = FeatureExtractor()
    kp_all, _ = extractor.extract_features(img, None, return_static_only=False)
    
    # Extract features (static only)
    kp_static, _ = extractor.extract_features(img, dynamic_mask, return_static_only=True)
    
    print(f"\nTotal features detected: {len(kp_all)}")
    print(f"Static features only: {len(kp_static)}")
    print(f"Dynamic features filtered: {len(kp_all) - len(kp_static)}")
    
    # Visualize
    visualizer = Visualizer()
    
    # Draw all features
    img_all = visualizer.draw_keypoints(img, kp_all, color=(0, 255, 0))
    
    # Draw static features
    img_static = visualizer.draw_keypoints(img, kp_static, color=(0, 0, 255))
    
    # Combine
    result = visualizer.create_side_by_side(
        img_all, img_static,
        "All Features", "Static Features Only"
    )
    
    # Save
    save_path = Config.get_results_path("demo_features.jpg")
    cv2.imwrite(save_path, result)
    print(f"\nVisualization saved to: {save_path}")


def demo_feature_matching():
    """Demo: Feature matching between consecutive frames"""
    from utils import get_image_list
    from dynamic_detector import DynamicObjectDetector
    from feature_extraction import FeatureExtractor, FeatureMatcher
    from visualization import Visualizer
    
    print("\n" + "=" * 60)
    print("DEMO: Feature Matching with Dynamic Filtering")
    print("=" * 60)
    
    # Get first two images
    sequence_path = Config.get_sequence_path("00")
    image_files = get_image_list(sequence_path)
    
    if len(image_files) < 2:
        print("ERROR: Need at least 2 images!")
        return
    
    img1 = cv2.imread(image_files[0])
    img2 = cv2.imread(image_files[1])
    
    # Detect dynamic objects
    detector = DynamicObjectDetector()
    mask1 = detector.detect(img1)
    mask2 = detector.detect(img2)
    
    # Extract features
    extractor = FeatureExtractor()
    kp1, desc1 = extractor.extract_features(img1, mask1, return_static_only=True)
    kp2, desc2 = extractor.extract_features(img2, mask2, return_static_only=True)
    
    # Match features
    matcher = FeatureMatcher()
    matches = matcher.match(desc1, desc2)
    
    print(f"\nFrame 1 features: {len(kp1)}")
    print(f"Frame 2 features: {len(kp2)}")
    print(f"Matches found: {len(matches)}")
    
    # Visualize
    visualizer = Visualizer()
    matches_img = visualizer.draw_matches(img1, kp1, img2, kp2, matches)
    
    # Save
    save_path = Config.get_results_path("demo_matches.jpg")
    cv2.imwrite(save_path, matches_img)
    print(f"\nVisualization saved to: {save_path}")


def demo_quick_slam(num_frames=50):
    """Demo: Run SLAM on first N frames"""
    print("\n" + "=" * 60)
    print(f"DEMO: Quick SLAM Run ({num_frames} frames)")
    print("=" * 60)
    
    # Create SLAM system
    slam = DynamicSLAM(sequence="00")
    
    # Process limited frames
    slam.process_sequence(start_frame=0, end_frame=num_frames)
    
    print(f"\nDemo complete! Check results in: {Config.RESULTS_DIR}")


def main():
    """Run all demos"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Dynamic SLAM Demo')
    parser.add_argument('--demo', type=str, default='all',
                       choices=['features', 'matching', 'slam', 'all'],
                       help='Which demo to run')
    parser.add_argument('--frames', type=int, default=50,
                       help='Number of frames for SLAM demo')
    
    args = parser.parse_args()
    
    if args.demo == 'features' or args.demo == 'all':
        demo_feature_extraction()
    
    if args.demo == 'matching' or args.demo == 'all':
        demo_feature_matching()
    
    if args.demo == 'slam' or args.demo == 'all':
        demo_quick_slam(args.frames)


if __name__ == "__main__":
    main()
