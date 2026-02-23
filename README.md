# Dynamic SLAM - Visual Odometry Made Easy

A beginner-friendly monocular visual SLAM (Simultaneous Localization and Mapping) system with **interactive web interface**, dynamic object detection, and robust camera pose estimation.

> 🌟 **NEW**: Interactive web interface - perfect for beginners! No coding required!

## 🎯 Project Overview

This project implements a complete visual odometry pipeline that:
- **🌐 Interactive Web Interface** - Easy-to-use interface for everyone!
- **🤖 Detects dynamic objects** using YOLOv8 AI segmentation
- **🔍 Extracts and matches features** only from static regions
- **📊 Estimates camera pose** using Essential Matrix decomposition
- **✅ Evaluates trajectory** against ground truth (KITTI dataset)

### 🆕 What's New - Beginner-Friendly Web Interface!

No programming knowledge required! Our new web interface features:
- ✨ **Step-by-step visual guide** - Always know what to do next
- 🎓 **Interactive tutorial** - Learn in 2 minutes
- 💡 **Helpful tooltips** - Hover over any setting for explanation
- 🚀 **Quick Demo mode** - See results in 1 minute!
- 📱 **Modern design** - Beautiful gradients, smooth animations
- 📖 **Built-in help** - Comprehensive guide always accessible

👉 **First time? Jump to [Web Interface Quick Start](#-web-interface-quick-start)**

## 📁 Project Structure

```
DYNAMIC_SLAM/
├── src/
│   ├── config.py                 # Configuration parameters
│   ├── utils.py                  # Utility functions (data loading, etc.)
│   ├── dynamic_detector.py       # YOLO-based dynamic object detection
│   ├── feature_extraction.py     # Feature extraction and matching
│   ├── pose_estimation.py        # Camera pose estimation
│   ├── visualization.py          # Visualization utilities
│   ├── dynamic_slam.py           # Main SLAM pipeline
│   ├── evaluate_trajectory.py    # Trajectory evaluation with EVO
│   ├── demo.py                   # Demo scripts
│   ├── run_batch.py             # Batch processing script
│   └── test_mask.py             # Initial YOLO test script
├── data/
│   └── dataset/                  # KITTI dataset
│       ├── sequences/            # Image sequences
│       │   ├── 00/
│       │   │   ├── image_0/     # Left camera images
│       │   │   ├── calib.txt    # Calibration parameters
│       │   │   └── times.txt    # Timestamps
│       │   └── ...
│       └── poses/                # Ground truth poses
│           ├── 00.txt
│           └── ...
├── results/                      # Output directory
├── environment.yml               # Conda environment
├── yolov8n-seg.pt               # YOLO model weights
└── README.md                     # This file
```

## 🚀 Web Interface Quick Start

### For Complete Beginners (Recommended!)

1. **Start the web interface:**
   ```bash
   # Double-click this file in Windows Explorer:
   launch_web.bat
   
   # OR run in terminal:
   .\start_web.bat
   ```

2. **Your browser opens automatically** to `http://localhost:5000`

3. **Follow the on-screen instructions:**
   - Click "Start Tutorial" for a 2-minute guided tour
   - OR select a sequence and click "Quick Demo" to see it in action!

4. **That's it!** Results appear automatically below.

### What You'll See:
- 📹 **Video Selector** - Choose which driving footage to analyze
- ⚙️ **Settings** (Optional) - Keep defaults for best results
- 🚀 **Quick Demo** - Process 50 frames in ~1 minute
- 📊 **Live Progress** - Watch the analysis happen in real-time
- 🖼️ **Results Gallery** - Beautiful visualizations of camera path

### Need Help?
- Click the **Help (❓)** button in the interface
- Read [USER_GUIDE.md](USER_GUIDE.md) - Complete beginner's guide
- See [WEB_ENHANCEMENT_SUMMARY.md](WEB_ENHANCEMENT_SUMMARY.md) - Feature overview

---

## 🚀 Quick Start (Advanced Users)

### 1. Environment Setup

Create conda environment:
```bash
conda env create -f environment.yml
conda activate dynamic_slam
```

### 2. Choose Your Interface

**Option A: Web Interface (Recommended for beginners)** 🌐
```bash
# Windows
start_web.bat

# Linux/Mac
./start_web.sh

# Then open browser: http://localhost:5000
```

**Option B: Command Line**
```bash
cd src
python demo.py --demo all --frames 50
```

### 3. Run Demo

**Web Interface:**
- Open http://localhost:5000
- Click "Quick Run (50 frames)"
- View results in browser

**Command Line:**
```bash
cd src
python demo.py --demo all --frames 50
```

This4. Full SLAM Processing

**Web Interface:**
- Select sequence from dropdown
- Click "Start Processing"
- Monitor progress in real-time
- View/download results when complete

**Command Line:**
```bash
cd src
python dynamic_slam.py
```

By default, this processes sequence "00". Modify `Config.SEQUENCE` in [src/config.py](src/config.py) to change the sequence.

### 5n dynamic_slam.py
```

By default, this processes sequence "00". Modify `Config.SEQUENCE` in [src/config.py](src/config.py) to change the sequence.

### 4. Evaluate Results

Evaluate trajectory using EVO:
```bash
cd src
python evaluate_trajectory.py --sequence 00
```

## 📊 Configuration

Edit [src/config.py](src/config.py) to customize:

### Dataset Configuration
```python
SEQUENCE = "00"              # Sequence to process
START_FRAME = 0              # Start frame
END_FRAME = None             # End frame (None = all)
```

### Feature Extraction
```python
FEATURE_TYPE = "ORB"         # ORB, SIFT, or AKAZE
MAX_FEATURES = 3000          # Maximum features per frame
```

### Dynamic Object Detection
```python
YOLO_CONF_THRESHOLD = 0.3    # Confidence threshold
DYNAMIC_CLASSES = [0, 1, 2, 5, 7]  # person, bicycle, car, bus, truck
```

### Pose Estimation
```python
RANSAC_REPROJ_THRESHOLD = 1.0    # RANSAC reprojection threshold
MIN_MATCH_COUNT = 50              # Minimum matches for pose estimation
```

## 🔧 Advanced Usage

### Web Interface 🌐

The project includes a modern web interface for easy testing and visualization:

**Features:**
- 📊 Real-time processing status
- 🎛️ Interactive parameter tuning
- 📈 Live result visualization
- 🚀 One-click demos and quick runs
- 📱 Responsive design

**Start the web server:**
```bash
# Windows
start_web.bat

# Linux/Mac  
./start_web.sh

# Manual
python web_app.py
```

Then open **http://localhost:5000** in your browser.

See [WEB_INTERFACE.md](WEB_INTERFACE.md) for complete documentation.

### Process Multiple Sequences
```bash
cd src
python run_batch.py --sequences 00 01 02 --start 0 --end 500
```

### Custom Sequence Range
```python
from dynamic_slam import DynamicSLAM

slam = DynamicSLAM(sequence="00")
slam.process_sequence(start_frame=0, end_frame=100)
```

### Use Different Features
Modify in [src/config.py](src/config.py):
```python
FEATURE_TYPE = "SIFT"  # or "ORB", "AKAZE"
```

## 📈 Output Files

After running, check the `results/` folder:

### Trajectory Files
- `trajectory_seq00.txt` - Estimated camera poses (KITTI format)
- `trajectory_2d_seq00.png` - 2D trajectory plot
- `trajectory_3d_seq00.png` - 3D trajectory visualization

### Evaluation Results
- `error_stats_seq00.txt` - Translation and rotation error statistics
- `errors_seq00.png` - Error plots over time
- `evo_results_seq00.txt` - EVO evaluation metrics (APE, RPE)
- `evo_trajectory_seq00.png` - EVO trajectory comparison
- `evo_ape_seq00.png` - Absolute Pose Error plot
- `evo_rpe_seq00.png` - Relative Pose Error plot

### Intermediate Visualizations
- `frame_XXXXXX_matches.jpg` - Feature matches (saved every 10 frames)
- `demo_features.jpg` - Demo: feature extraction
- `demo_matches.jpg` - Demo: feature matching

## 🧪 System Pipeline

```
Input Image
    ↓
┌─────────────────────────┐
│ YOLO Dynamic Detection  │ → Dynamic Object Mask
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Feature Extraction      │ → Keypoints + Descriptors
│ (Static Regions Only)   │    (Dynamic regions filtered)
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Feature Matching        │ → Matched Feature Pairs
│ (with Lowe's Ratio)     │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Pose Estimation         │ → R, t (Rotation, Translation)
│ (Essential Matrix)      │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Scale Estimation        │ → Scaled Relative Pose
│ (using Ground Truth)    │
└─────────────────────────┘
    ↓
Camera Trajectory
```

## 📚 Key Components

### 1. Dynamic Object Detection (`dynamic_detector.py`)
- Uses YOLOv8 segmentation to detect dynamic objects
- Creates binary mask: 255 = dynamic, 0 = static
- Filters out people, vehicles, bicycles

### 2. Feature Extraction (`feature_extraction.py`)
- Supports ORB, SIFT, AKAZE features
- Filters features in dynamic regions
- Robust feature matching with ratio test

### 3. Pose Estimation (`pose_estimation.py`)
- Essential Matrix decomposition for relative pose
- RANSAC for outlier rejection
- Scale estimation using ground truth (monocular scale ambiguity)

### 4. Visualization (`visualization.py`)
- 2D/3D trajectory plots
- Feature matching visualization
- Error analysis plots

## 📊 Evaluation Metrics

### Absolute Pose Error (APE)
Measures global consistency of the trajectory:
- **Mean/Median**: Average error
- **RMSE**: Root mean square error
- **Std**: Error variation

### Relative Pose Error (RPE)
Measures local accuracy (drift):
- Computed over consecutive frames
- Better indicator of smoothness

## 🐛 Troubleshooting

### "No images found"
- Ensure KITTI dataset is properly extracted in `data/dataset/sequences/`
- Check that sequence folders contain `image_0/` directory with PNG files

### "YOLO model not found"
- Ensure `yolov8n-seg.pt` is in the project root
- Download from: `https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-seg.pt`

### "Not enough matches"
- Reduce `MIN_MATCH_COUNT` in config
- Try different feature types (SIFT is more robust than ORB)
- Increase `MAX_FEATURES`

### Low accuracy
- Tune RANSAC parameters
- Adjust feature detection thresholds
- Check if dynamic object detection is working properly

## 🔬 Experimental Features

### Different Pose Estimation Methods
Modify `pose_estimation.py` to use:
- PnP (when 3D points are available)
- Fundamental Matrix (uncalibrated)
- Direct methods (photometric error)

### Loop Closure Detection
Add place recognition for loop closure (not yet implemented)

### Local Mapping
Maintain local 3D map of static points (not yet implemented)

## 📝 Citation

If you use this code, please cite the KITTI dataset:
```
@INPROCEEDINGS{Geiger2012CVPR,
  author = {Andreas Geiger and Philip Lenz and Raquel Urtasun},
  title = {Are we ready for Autonomous Driving? The KITTI Vision Benchmark Suite},
  booktitle = {CVPR},
  year = {2012}
}
```

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest improvements
- Add new features
- Improve documentation

## 📄 License

This project is for educational purposes. Please respect the licenses of:
- KITTI Dataset
- YOLOv8 (Ultralytics)
- OpenCV
- EVO library

## 🎓 Learning Resources

- **SLAM**: "Multiple View Geometry in Computer Vision" by Hartley & Zisserman
- **Visual Odometry**: [Tutorial by Davide Scaramuzza](http://rpg.ifi.uzh.ch/docs/VO_Part_I_Scaramuzza.pdf)
- **KITTI Dataset**: [Official Website](http://www.cvlibs.net/datasets/kitti/)
- **YOLOv8**: [Ultralytics Documentation](https://docs.ultralytics.com/)

## 📞 Support

For questions or issues:
1. Check existing documentation
2. Review error messages carefully
3. Verify dataset and environment setup
4. Check configuration parameters

---

**Happy SLAMming! 🚗💨**
