"""
System Verification Script
Check if all dependencies and data are properly configured
"""
import os
import sys


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor} (need 3.8+)")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    
    dependencies = {
        'numpy': 'NumPy',
        'cv2': 'OpenCV',
        'torch': 'PyTorch',
        'ultralytics': 'YOLOv8',
        'matplotlib': 'Matplotlib',
        'tqdm': 'tqdm'
    }
    
    optional = {
        'evo': 'EVO (trajectory evaluation)'
    }
    
    all_ok = True
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - NOT INSTALLED")
            all_ok = False
    
    print("\nOptional dependencies:")
    for module, name in optional.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ⚠ {name} - not installed (optional)")
    
    return all_ok


def check_cuda():
    """Check CUDA availability"""
    print("\nChecking CUDA...")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"  ✓ CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"    CUDA version: {torch.version.cuda}")
        else:
            print("  ⚠ CUDA not available (will use CPU)")
    except Exception as e:
        print(f"  ✗ Error checking CUDA: {e}")


def check_yolo_model():
    """Check if YOLO model exists"""
    print("\nChecking YOLO model...")
    
    model_path = r"D:\DYNAMIC_SLAM\yolov8n-seg.pt"
    
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"  ✓ Model found: {model_path}")
        print(f"    Size: {size_mb:.1f} MB")
        return True
    else:
        print(f"  ✗ Model not found: {model_path}")
        print("    Download from: https://github.com/ultralytics/assets/releases")
        return False


def check_dataset():
    """Check if KITTI dataset is present"""
    print("\nChecking dataset...")
    
    dataset_root = r"D:\DYNAMIC_SLAM\data\dataset"
    sequences_dir = os.path.join(dataset_root, "sequences")
    poses_dir = os.path.join(dataset_root, "poses")
    
    if not os.path.exists(dataset_root):
        print(f"  ✗ Dataset root not found: {dataset_root}")
        return False
    
    print(f"  ✓ Dataset root exists")
    
    # Check sequence 00
    seq_path = os.path.join(sequences_dir, "00")
    if os.path.exists(seq_path):
        # Check for images
        img_path = os.path.join(seq_path, "image_0")
        if os.path.exists(img_path):
            import glob
            images = glob.glob(os.path.join(img_path, "*.png"))
            print(f"  ✓ Sequence 00 found: {len(images)} images")
        else:
            print(f"  ✗ Images not found in {img_path}")
            return False
        
        # Check calibration
        calib_path = os.path.join(seq_path, "calib.txt")
        if os.path.exists(calib_path):
            print(f"  ✓ Calibration file found")
        else:
            print(f"  ✗ Calibration file not found")
            return False
    else:
        print(f"  ✗ Sequence 00 not found: {seq_path}")
        return False
    
    # Check ground truth
    gt_path = os.path.join(poses_dir, "00.txt")
    if os.path.exists(gt_path):
        with open(gt_path, 'r') as f:
            num_poses = len(f.readlines())
        print(f"  ✓ Ground truth found: {num_poses} poses")
    else:
        print(f"  ⚠ Ground truth not found (optional)")
    
    return True


def check_output_dir():
    """Check/create output directory"""
    print("\nChecking output directory...")
    
    results_dir = r"D:\DYNAMIC_SLAM\results"
    
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print(f"  ✓ Created: {results_dir}")
    else:
        print(f"  ✓ Exists: {results_dir}")
    
    return True


def test_imports():
    """Test importing project modules"""
    print("\nTesting project imports...")
    
    sys.path.insert(0, r"D:\DYNAMIC_SLAM\src")
    
    modules = [
        'config',
        'utils',
        'dynamic_detector',
        'feature_extraction',
        'pose_estimation',
        'visualization',
        'dynamic_slam'
    ]
    
    all_ok = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except Exception as e:
            print(f"  ✗ {module}: {e}")
            all_ok = False
    
    return all_ok


def test_yolo_inference():
    """Test YOLO model loading and inference"""
    print("\nTesting YOLO inference...")
    
    try:
        from ultralytics import YOLO
        import numpy as np
        
        model = YOLO(r"D:\DYNAMIC_SLAM\yolov8n-seg.pt")
        print("  ✓ Model loaded")
        
        # Create dummy image
        dummy_img = np.zeros((480, 640, 3), dtype=np.uint8)
        results = model.predict(dummy_img, verbose=False)
        print("  ✓ Inference successful")
        
        return True
    except Exception as e:
        print(f"  ✗ YOLO test failed: {e}")
        return False


def main():
    """Run all checks"""
    print("=" * 70)
    print("DYNAMIC SLAM - SYSTEM VERIFICATION")
    print("=" * 70)
    
    checks = []
    
    # Run checks
    checks.append(("Python Version", check_python_version()))
    checks.append(("Dependencies", check_dependencies()))
    check_cuda()  # Informational only
    checks.append(("YOLO Model", check_yolo_model()))
    checks.append(("Dataset", check_dataset()))
    checks.append(("Output Directory", check_output_dir()))
    checks.append(("Project Imports", test_imports()))
    checks.append(("YOLO Inference", test_yolo_inference()))
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    for name, status in checks:
        symbol = "✓" if status else "✗"
        print(f"  {symbol} {name}")
    
    all_passed = all(status for _, status in checks)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL CHECKS PASSED!")
        print("\nYou're ready to run Dynamic SLAM!")
        print("\nQuick start:")
        print("  python run.py --demo")
    else:
        print("✗ SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running.")
        print("\nRefer to README.md or QUICKSTART.md for setup instructions.")
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
