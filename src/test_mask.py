import cv2
import numpy as np
from ultralytics import YOLO
import os

def test_yolo_masking():
    image_path = r"D:\DYNAMIC_SLAM\data\dataset\sequences\00\image_0\000000.png"
    save_path = r"D:\DYNAMIC_SLAM\results\mask_test.jpg"

    if not os.path.exists(image_path):
        print(f"WAIT! File not found at: {image_path}")
        print("Did you unzip the Kaggle folder correctly?")
        return

    print("Loading YOLOv8-Seg model...")
    model = YOLO("yolov8n-seg.pt") 

    img = cv2.imread(image_path)
    print(f"Loaded image shape: {img.shape}")

    results = model.predict(img, classes=[0, 1, 2, 5, 7], verbose=False)

    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    
    if results[0].masks is not None:
        for seg in results[0].masks.data:
            m = seg.cpu().numpy().astype(np.uint8)
            m_resized = cv2.resize(m, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)
            mask = np.maximum(mask, m_resized * 255)
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    combined = np.hstack((img, mask_bgr))
    
    cv2.imwrite(save_path, combined)
    print(f"Success! Test result saved to: {save_path}")

if __name__ == "__main__":
    test_yolo_masking()