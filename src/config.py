"""
Configuration file for Dynamic SLAM system
"""
import os

class Config:
    """Configuration parameters for Dynamic SLAM"""
    
    # Dataset paths
    DATASET_ROOT = r"D:\DYNAMIC_SLAM\data\dataset"
    SEQUENCES_DIR = os.path.join(DATASET_ROOT, "sequences")
    POSES_DIR = os.path.join(DATASET_ROOT, "poses")
    RESULTS_DIR = r"D:\DYNAMIC_SLAM\results"
    
    # Default sequence to process
    SEQUENCE = "00"
    
    # YOLO Model
    YOLO_MODEL_PATH = r"D:\DYNAMIC_SLAM\yolov8n-seg.pt"
    DYNAMIC_CLASSES = [0, 1, 2, 5, 7]  # person, bicycle, car, bus, truck
    YOLO_CONF_THRESHOLD = 0.3
    
    # Feature Extraction
    FEATURE_TYPE = "ORB"  # Options: ORB, SIFT, AKAZE
    MAX_FEATURES = 3000
    
    # ORB Parameters
    ORB_N_FEATURES = 3000
    ORB_SCALE_FACTOR = 1.2
    ORB_N_LEVELS = 8
    
    # SIFT Parameters
    SIFT_N_FEATURES = 3000
    SIFT_CONTRAST_THRESHOLD = 0.04
    SIFT_EDGE_THRESHOLD = 10
    
    # Feature Matching
    MATCHER_TYPE = "BF"  # BF or FLANN
    LOWE_RATIO_THRESHOLD = 0.7
    MIN_MATCH_COUNT = 50
    
    # RANSAC Parameters
    RANSAC_REPROJ_THRESHOLD = 1.0
    RANSAC_CONFIDENCE = 0.999
    RANSAC_MAX_ITERS = 2000
    
    # Pose Estimation
    MIN_DEPTH = 0.1
    MAX_DEPTH = 100.0
    
    # Visualization
    DRAW_MATCHES = True
    DRAW_TRAJECTORY = True
    SAVE_INTERMEDIATE_RESULTS = True
    DISPLAY_SCALE = 0.5
    
    # Processing
    START_FRAME = 0
    END_FRAME = None  # None = process all frames
    SKIP_FRAMES = 0  # Process every Nth frame (0 = process all)
    
    @classmethod
    def get_sequence_path(cls, sequence=None):
        """Get path to sequence images"""
        seq = sequence or cls.SEQUENCE
        return os.path.join(cls.SEQUENCES_DIR, seq, "image_0")
    
    @classmethod
    def get_calib_path(cls, sequence=None):
        """Get path to calibration file"""
        seq = sequence or cls.SEQUENCE
        return os.path.join(cls.SEQUENCES_DIR, seq, "calib.txt")
    
    @classmethod
    def get_poses_path(cls, sequence=None):
        """Get path to ground truth poses"""
        seq = sequence or cls.SEQUENCE
        return os.path.join(cls.POSES_DIR, f"{seq}.txt")
    
    @classmethod
    def get_results_path(cls, filename):
        """Get path for results file"""
        os.makedirs(cls.RESULTS_DIR, exist_ok=True)
        return os.path.join(cls.RESULTS_DIR, filename)
