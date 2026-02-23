"""
Feature extraction module for Dynamic SLAM
"""
import cv2
import numpy as np
from config import Config


class FeatureExtractor:
    """Extract and describe keypoints from images"""
    
    def __init__(self, feature_type=None, max_features=None):
        """
        Initialize feature extractor
        
        Args:
            feature_type: Type of features (ORB, SIFT, AKAZE)
            max_features: Maximum number of features to extract
        """
        self.feature_type = feature_type or Config.FEATURE_TYPE
        self.max_features = max_features or Config.MAX_FEATURES
        
        self.detector = self._create_detector()
        
    def _create_detector(self):
        """Create feature detector based on type"""
        if self.feature_type == "ORB":
            return cv2.ORB_create(
                nfeatures=Config.ORB_N_FEATURES,
                scaleFactor=Config.ORB_SCALE_FACTOR,
                nlevels=Config.ORB_N_LEVELS
            )
        elif self.feature_type == "SIFT":
            return cv2.SIFT_create(
                nfeatures=Config.SIFT_N_FEATURES,
                contrastThreshold=Config.SIFT_CONTRAST_THRESHOLD,
                edgeThreshold=Config.SIFT_EDGE_THRESHOLD
            )
        elif self.feature_type == "AKAZE":
            return cv2.AKAZE_create()
        else:
            raise ValueError(f"Unknown feature type: {self.feature_type}")
    
    def detect_and_compute(self, image, mask=None):
        """
        Detect keypoints and compute descriptors
        
        Args:
            image: Input image (grayscale or BGR)
            mask: Optional mask (255 = valid region, 0 = invalid)
            
        Returns:
            keypoints: List of cv2.KeyPoint objects
            descriptors: Numpy array of descriptors
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Detect and compute
        keypoints, descriptors = self.detector.detectAndCompute(gray, mask)
        
        return keypoints, descriptors
    
    def filter_keypoints_by_mask(self, keypoints, descriptors, mask):
        """
        Filter out keypoints that fall in masked regions
        
        Args:
            keypoints: List of cv2.KeyPoint objects
            descriptors: Numpy array of descriptors
            mask: Binary mask (0 = remove, 255 = keep)
            
        Returns:
            filtered_keypoints: List of filtered keypoints
            filtered_descriptors: Filtered descriptors
        """
        if mask is None or descriptors is None:
            return keypoints, descriptors
        
        filtered_kp = []
        filtered_desc = []
        
        for i, kp in enumerate(keypoints):
            x, y = int(kp.pt[0]), int(kp.pt[1])
            # Check bounds
            if 0 <= y < mask.shape[0] and 0 <= x < mask.shape[1]:
                # Keep keypoint only if in valid region (mask value > 0)
                if mask[y, x] > 0:
                    filtered_kp.append(kp)
                    filtered_desc.append(descriptors[i])
        
        if len(filtered_desc) > 0:
            filtered_desc = np.array(filtered_desc)
        else:
            filtered_desc = None
            
        return filtered_kp, filtered_desc
    
    def extract_features(self, image, dynamic_mask=None, return_static_only=True):
        """
        Extract features from image, optionally filtering dynamic regions
        
        Args:
            image: Input image
            dynamic_mask: Binary mask where 255 = dynamic object, 0 = static
            return_static_only: If True, return only features from static regions
            
        Returns:
            keypoints: List of cv2.KeyPoint objects
            descriptors: Numpy array of descriptors
        """
        # First detect all features
        keypoints, descriptors = self.detect_and_compute(image)
        
        # If we have a dynamic mask and want static features only
        if dynamic_mask is not None and return_static_only:
            # Create static mask (inverse of dynamic mask)
            static_mask = cv2.bitwise_not(dynamic_mask)
            keypoints, descriptors = self.filter_keypoints_by_mask(
                keypoints, descriptors, static_mask
            )
        
        return keypoints, descriptors


class FeatureMatcher:
    """Match features between images"""
    
    def __init__(self, feature_type=None, matcher_type=None):
        """
        Initialize feature matcher
        
        Args:
            feature_type: Type of features (ORB, SIFT, AKAZE)
            matcher_type: Type of matcher (BF, FLANN)
        """
        self.feature_type = feature_type or Config.FEATURE_TYPE
        self.matcher_type = matcher_type or Config.MATCHER_TYPE
        
        self.matcher = self._create_matcher()
    
    def _create_matcher(self):
        """Create matcher based on feature type"""
        if self.feature_type == "ORB" or self.feature_type == "AKAZE":
            # Binary descriptors - use Hamming distance
            if self.matcher_type == "BF":
                return cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            else:  # FLANN
                FLANN_INDEX_LSH = 6
                index_params = dict(
                    algorithm=FLANN_INDEX_LSH,
                    table_number=6,
                    key_size=12,
                    multi_probe_level=1
                )
                search_params = dict(checks=50)
                return cv2.FlannBasedMatcher(index_params, search_params)
        else:  # SIFT
            # Floating point descriptors - use L2 distance
            if self.matcher_type == "BF":
                return cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
            else:  # FLANN
                FLANN_INDEX_KDTREE = 1
                index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
                search_params = dict(checks=50)
                return cv2.FlannBasedMatcher(index_params, search_params)
    
    def match(self, desc1, desc2, ratio_threshold=None):
        """
        Match descriptors using ratio test
        
        Args:
            desc1: Descriptors from first image
            desc2: Descriptors from second image
            ratio_threshold: Lowe's ratio test threshold
            
        Returns:
            good_matches: List of cv2.DMatch objects
        """
        if desc1 is None or desc2 is None:
            return []
        
        if len(desc1) < 2 or len(desc2) < 2:
            return []
        
        ratio = ratio_threshold or Config.LOWE_RATIO_THRESHOLD
        
        # Find knn matches
        matches = self.matcher.knnMatch(desc1, desc2, k=2)
        
        # Apply ratio test
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < ratio * n.distance:
                    good_matches.append(m)
        
        return good_matches
    
    def get_matched_points(self, keypoints1, keypoints2, matches):
        """
        Extract matched point coordinates
        
        Args:
            keypoints1: Keypoints from first image
            keypoints2: Keypoints from second image
            matches: List of cv2.DMatch objects
            
        Returns:
            pts1: Nx2 array of points from image 1
            pts2: Nx2 array of points from image 2
        """
        pts1 = np.float32([keypoints1[m.queryIdx].pt for m in matches])
        pts2 = np.float32([keypoints2[m.trainIdx].pt for m in matches])
        
        return pts1, pts2
