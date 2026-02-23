"""
Dynamic object detection module using YOLO
"""
import cv2
import numpy as np
from ultralytics import YOLO
from config import Config


class DynamicObjectDetector:
    """Detect and segment dynamic objects in images"""
    
    def __init__(self, model_path=None, confidence_threshold=None):
        """
        Initialize YOLO detector
        
        Args:
            model_path: Path to YOLO model weights
            confidence_threshold: Confidence threshold for detections
        """
        self.model_path = model_path or Config.YOLO_MODEL_PATH
        self.conf_threshold = confidence_threshold or Config.YOLO_CONF_THRESHOLD
        
        print(f"Loading YOLO model from {self.model_path}...")
        self.model = YOLO(self.model_path)
        print("YOLO model loaded successfully!")
        
    def detect(self, image, return_results=False):
        """
        Detect dynamic objects in image
        
        Args:
            image: Input image (BGR)
            return_results: If True, return full YOLO results
            
        Returns:
            mask: Binary mask (255 = dynamic, 0 = static)
            results: YOLO results object (if return_results=True)
        """
        # Run inference
        results = self.model.predict(
            image,
            classes=Config.DYNAMIC_CLASSES,
            conf=self.conf_threshold,
            verbose=False
        )
        
        # Create binary mask
        mask = self._create_mask(image, results[0])
        
        if return_results:
            return mask, results[0]
        return mask
    
    def _create_mask(self, image, result):
        """
        Create binary mask from YOLO segmentation results
        
        Args:
            image: Input image
            result: YOLO result object
            
        Returns:
            mask: Binary mask (255 = dynamic, 0 = static)
        """
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        
        if result.masks is not None:
            for seg in result.masks.data:
                # Convert PyTorch tensor to numpy
                m = seg.cpu().numpy().astype(np.uint8)
                
                # Resize to match image dimensions
                m_resized = cv2.resize(
                    m,
                    (image.shape[1], image.shape[0]),
                    interpolation=cv2.INTER_NEAREST
                )
                
                # Combine masks (keep maximum)
                mask = np.maximum(mask, m_resized * 255)
        
        return mask
    
    def get_detection_info(self, result):
        """
        Extract detection information
        
        Args:
            result: YOLO result object
            
        Returns:
            dict: Detection statistics
        """
        info = {
            'num_objects': 0,
            'classes': [],
            'confidences': [],
            'boxes': []
        }
        
        if result.boxes is not None:
            info['num_objects'] = len(result.boxes)
            info['classes'] = result.boxes.cls.cpu().numpy().astype(int).tolist()
            info['confidences'] = result.boxes.conf.cpu().numpy().tolist()
            info['boxes'] = result.boxes.xyxy.cpu().numpy().tolist()
        
        return info
    
    def visualize_detections(self, image, result):
        """
        Draw detection results on image
        
        Args:
            image: Input image
            result: YOLO result object
            
        Returns:
            annotated_image: Image with drawn detections
        """
        annotated = image.copy()
        
        if result.boxes is not None:
            for i, box in enumerate(result.boxes.xyxy.cpu().numpy()):
                x1, y1, x2, y2 = box.astype(int)
                conf = result.boxes.conf[i].item()
                cls = int(result.boxes.cls[i].item())
                
                # Class names
                class_names = {
                    0: 'person', 1: 'bicycle', 2: 'car',
                    5: 'bus', 7: 'truck'
                }
                label = f"{class_names.get(cls, 'object')} {conf:.2f}"
                
                # Draw box
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw label
                cv2.putText(
                    annotated, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
                )
        
        # Draw masks
        if result.masks is not None:
            for seg in result.masks.data:
                m = seg.cpu().numpy().astype(np.uint8)
                m_resized = cv2.resize(
                    m,
                    (image.shape[1], image.shape[0]),
                    interpolation=cv2.INTER_NEAREST
                )
                
                # Create colored overlay
                overlay = annotated.copy()
                overlay[m_resized > 0] = [0, 255, 255]  # Yellow
                
                # Blend
                annotated = cv2.addWeighted(annotated, 0.7, overlay, 0.3, 0)
        
        return annotated
    
    def dilate_mask(self, mask, kernel_size=5):
        """
        Dilate mask to create safety margin around dynamic objects
        
        Args:
            mask: Binary mask
            kernel_size: Size of dilation kernel
            
        Returns:
            dilated_mask: Dilated binary mask
        """
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        dilated = cv2.dilate(mask, kernel, iterations=1)
        return dilated
