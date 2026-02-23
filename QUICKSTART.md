# Dynamic SLAM - Quick Start Guide

## ⚡ Quick Setup (5 minutes)

### 1. Clone/Download Project
```bash
cd D:\DYNAMIC_SLAM
```

### 2. Create Environment
```bash
conda env create -f environment.yml
conda activate dynamic_slam
```

### 3. Download YOLO Weights (if not present)
```bash
# The yolov8n-seg.pt should already be in the project root
# If not, download it:
# wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-seg.pt
```

### 4. Verify Dataset Structure
Ensure your dataset is in this structure:
```
data/dataset/
├── sequences/
│   └── 00/
│       ├── image_0/
│       │   ├── 000000.png
│       │   ├── 000001.png
│       │   └── ...
│       ├── calib.txt
│       └── times.txt
└── poses/
    └── 00.txt
```

## 🚀 Running the System

### Option 1: Quick Demo (Recommended for first run)
```bash
python run.py --demo
```
This processes first 50 frames and creates visualizations.

### Option 2: Full Sequence
```bash
python run.py --sequence 00
```

### Option 3: Custom Range
```bash
python run.py --sequence 00 --start 0 --end 200
```

### Option 4: With Evaluation
```bash
python run.py --sequence 00 --evaluate
```

## 📊 Check Results

After running, check the `results/` folder:

### Key Files:
- **`trajectory_2d_seq00.png`** - Bird's eye view of path
- **`trajectory_3d_seq00.png`** - 3D visualization
- **`errors_seq00.png`** - Error analysis
- **`error_stats_seq00.txt`** - Numerical statistics

### If evaluation was run:
- **`evo_results_seq00.txt`** - EVO metrics (APE, RPE)
- **`evo_trajectory_seq00.png`** - Comparison with ground truth
- **`evo_ape_seq00.png`** - Absolute pose error
- **`evo_rpe_seq00.png`** - Relative pose error

## 🎯 What to Expect

### Good Results (Sequence 00):
- Translation Error: < 5m (for full sequence)
- Features per frame: 500-2000
- Matches per frame: 200-800

### If Results are Poor:
1. Check if YOLO is detecting dynamic objects properly
2. Try different feature types (SIFT instead of ORB)
3. Adjust parameters in `src/config.py`

## ⚙️ Configuration

Edit `src/config.py` for quick changes:

```python
# Try SIFT instead of ORB (more accurate but slower)
FEATURE_TYPE = "SIFT"

# Increase features for better tracking
MAX_FEATURES = 5000

# Adjust YOLO confidence
YOLO_CONF_THRESHOLD = 0.25  # Lower = more detections
```

## 🐛 Common Issues

### No images found
```
ERROR: No images found in D:\DYNAMIC_SLAM\data\dataset\sequences\00\image_0
```
**Fix**: Extract KITTI dataset properly

### YOLO model not found
```
ERROR: Model file not found: yolov8n-seg.pt
```
**Fix**: Download weights or check path in config

### Not enough matches
```
Warning: Not enough matches (found: 20, need: 50)
```
**Fix**: Lower `MIN_MATCH_COUNT` in config or use SIFT

## 📈 Performance Tips

### For Speed:
- Use ORB features
- Reduce MAX_FEATURES to 1000
- Process fewer frames

### For Accuracy:
- Use SIFT features
- Increase MAX_FEATURES to 5000
- Tune RANSAC parameters

## 🎓 Next Steps

1. ✅ Run demo and check visualizations
2. ✅ Process full sequence 00
3. ✅ Compare with ground truth
4. 📚 Try different sequences (00-10 have ground truth)
5. 🔧 Experiment with parameters
6. 🚀 Implement improvements:
   - Loop closure detection
   - Local mapping
   - Better scale estimation
   - Bundle adjustment

## 💡 Tips

- **Start with short sequences**: Test on 50-100 frames first
- **Check visualizations**: Look at `frame_*_matches.jpg` to see if matching works
- **Monitor feature counts**: Should be consistent across frames
- **Use ground truth for debugging**: Compare estimated vs GT poses

## 📞 Need Help?

1. Check `README.md` for detailed documentation
2. Review error messages in console
3. Verify dataset and paths
4. Check configuration parameters

---

**Ready to run? Execute:**
```bash
python run.py --demo
```

🎉 **Enjoy your Dynamic SLAM system!**
