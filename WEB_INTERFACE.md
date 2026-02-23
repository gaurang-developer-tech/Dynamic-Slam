# 🌐 Dynamic SLAM Web Interface

## Overview

The Dynamic SLAM Web Interface provides an easy-to-use browser-based interface for running and visualizing SLAM results without using the command line.

## ✨ Features

- **📊 Real-time Progress Tracking**: Watch processing status live
- **🎛️ Interactive Configuration**: Adjust parameters on the fly
- **📈 Live Visualization**: View results immediately after processing
- **🚀 Quick Actions**: Run demos and quick tests with one click
- **📱 Responsive Design**: Works on desktop and mobile devices
- **🎨 Modern UI**: Clean, intuitive Bootstrap 5 interface

## 🚀 Quick Start

### 1. Install Flask (if not already installed)
```bash
pip install flask werkzeug
```

Or update your conda environment:
```bash
conda env update -f environment.yml
```

### 2. Start the Web Server

**Windows:**
```bash
start_web.bat
```

**Linux/Mac:**
```bash
chmod +x start_web.sh
./start_web.sh
```

**Or manually:**
```bash
python web_app.py
```

### 3. Open Your Browser
Navigate to: **http://localhost:5000**

## 📋 User Interface Guide

### Left Panel - Controls

#### 1. Sequence Selection
- **Select Sequence**: Choose from available KITTI sequences
- **Start Frame**: Beginning frame number (default: 0)
- **End Frame**: Ending frame number (leave empty for all frames)
- ✓ Sequences with ground truth are marked with "GT"

#### 2. Configuration
- **Feature Type**: Choose ORB (fast), SIFT (accurate), or AKAZE
- **Max Features**: Slider to adjust feature count (500-10000)
- **YOLO Confidence**: Detection confidence threshold (0.1-0.9)
- Click **Update Configuration** to apply changes

#### 3. Quick Actions
- **Demo: Feature Extraction**: Test feature detection
- **Demo: Feature Matching**: Test feature matching between frames
- **Quick Run (50 frames)**: Fast test on first 50 frames

#### 4. Control Buttons
- **Start Processing**: Begin SLAM processing
- **Stop**: Halt current processing

### Right Panel - Status and Results

#### 1. Processing Status
- **Status Badge**: Current processing state
  - 🔵 IDLE: Ready
  - 🔵 PROCESSING: Running
  - 🟡 GENERATING_RESULTS: Creating visualizations
  - 🟢 COMPLETED: Finished
  - 🔴 ERROR: Failed
- **Progress Bar**: Real-time progress indicator
- **Frame Counter**: Current frame / Total frames
- **Message Box**: Status messages and information

#### 2. Statistics (after completion)
- **Total Poses**: Number of estimated camera poses
- **Processing Time**: Time taken in seconds
- **FPS**: Frames processed per second

#### 3. Results Gallery
- **Visualizations**: 2D/3D trajectory plots, error graphs
- **Click images** to view full size
- **Download button** on each result

## 🔧 API Endpoints

The web application exposes these REST API endpoints:

### GET /api/sequences
List available sequences
```json
{
  "sequences": [
    {
      "id": "00",
      "name": "Sequence 00",
      "num_frames": 4540,
      "has_ground_truth": true
    }
  ]
}
```

### GET /api/config
Get current configuration
```json
{
  "feature_type": "ORB",
  "max_features": 3000,
  "yolo_confidence": 0.3
}
```

### POST /api/config
Update configuration
```json
{
  "feature_type": "SIFT",
  "max_features": 5000,
  "yolo_confidence": 0.25
}
```

### POST /api/process
Start processing
```json
{
  "sequence": "00",
  "start_frame": 0,
  "end_frame": 100
}
```

### GET /api/status
Get processing status
```json
{
  "is_processing": true,
  "progress": 45,
  "current_frame": 45,
  "total_frames": 100,
  "status": "processing",
  "message": "Processing frames..."
}
```

### POST /api/stop
Stop processing
```json
{
  "status": "success",
  "message": "Stop signal sent"
}
```

### GET /api/results/{sequence}
Get results for a sequence
```json
{
  "sequence": "00",
  "files": [...],
  "has_trajectory": true,
  "statistics": "..."
}
```

### POST /api/demo/{demo_type}
Run demo (features or matching)

## 📱 Usage Examples

### Example 1: Quick Test
1. Select **Sequence 00**
2. Click **Quick Run (50 frames)**
3. Watch progress bar
4. View results when complete

### Example 2: Full Processing
1. Select sequence
2. Leave frames empty (process all)
3. Click **Start Processing**
4. Monitor status
5. Download results

### Example 3: Custom Configuration
1. Change **Feature Type** to SIFT
2. Increase **Max Features** to 5000
3. Lower **YOLO Confidence** to 0.25
4. Click **Update Configuration**
5. Start processing

### Example 4: Run Demos
1. Click **Demo: Feature Extraction**
2. Wait for completion
3. Check results folder for `demo_features.jpg`
4. Click **Demo: Feature Matching**
5. Check results for `demo_matches.jpg`

## 🎨 Screenshots

### Main Interface
```
┌─────────────────────────────────────────────────────────┐
│ Dynamic SLAM                    Monocular Visual Odom   │
├─────────────────┬───────────────────────────────────────┤
│ Sequence:       │ Status: PROCESSING                    │
│ [Seq 00   ▼]    │ ████████████░░░░░░░░░ 60%            │
│                 │ Frame 600 / 1000                      │
│ Start: [0    ]  │                                       │
│ End:   [1000 ]  │ Statistics:                           │
│                 │ • Poses: 600                          │
│ Feature: [ORB▼] │ • Time: 45.3s                        │
│ Max Feat: 3000  │ • FPS: 13.2                          │
│ YOLO: 0.30      │                                       │
│                 │ Results:                              │
│ [Update Config] │ [trajectory_2d] [trajectory_3d]      │
│                 │ [errors_plot]   [evo_results]        │
│ Quick Actions:  │                                       │
│ [Demo Features] │                                       │
│ [Demo Matching] │                                       │
│ [Quick Run 50]  │                                       │
│                 │                                       │
│ [▶ START]       │                                       │
│ [■ STOP]        │                                       │
└─────────────────┴───────────────────────────────────────┘
```

## 🔐 Security Notes

⚠️ **Important**: This web interface is intended for **local development and testing only**.

- Default configuration listens on `0.0.0.0:5000` (all interfaces)
- No authentication or authorization
- No HTTPS/SSL
- Not suitable for production deployment

For production use:
- Add authentication (Flask-Login, JWT)
- Use HTTPS with SSL certificates
- Run behind reverse proxy (nginx, Apache)
- Implement rate limiting
- Add CSRF protection

## 🐛 Troubleshooting

### "Address already in use"
Port 5000 is occupied. Change port in `web_app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### "Flask not found"
Install Flask:
```bash
pip install flask werkzeug
```

### Results not showing
- Check browser console for errors
- Verify results directory exists
- Refresh page after processing completes

### Processing hangs
- Check terminal for error messages
- Verify dataset is properly loaded
- Try stopping and restarting

### Slow processing
- Reduce number of frames
- Use ORB instead of SIFT
- Lower max features count

## 💡 Tips

1. **Use Quick Run first**: Test with 50 frames before full processing
2. **Monitor terminal**: Detailed logs appear in terminal
3. **Run demos**: Verify system works before full processing
4. **Save config**: Note good parameter combinations
5. **Multiple sequences**: Process one at a time
6. **Check results folder**: Files saved immediately

## 📊 Result Files

After processing, these files appear in results gallery:

| File | Description |
|------|-------------|
| `trajectory_2d_seq00.png` | Bird's eye view trajectory |
| `trajectory_3d_seq00.png` | 3D trajectory visualization |
| `errors_seq00.png` | Translation/rotation errors |
| `error_stats_seq00.txt` | Error statistics (text) |
| `evo_trajectory_seq00.png` | EVO comparison plot |
| `evo_ape_seq00.png` | Absolute Pose Error |
| `evo_rpe_seq00.png` | Relative Pose Error |
| `demo_features.jpg` | Feature extraction demo |
| `demo_matches.jpg` | Feature matching demo |

## 🚀 Advanced Usage

### Custom Integration
Use the API programmatically:

```python
import requests

# Start processing
response = requests.post('http://localhost:5000/api/process', json={
    'sequence': '00',
    'start_frame': 0,
    'end_frame': 100
})

# Poll status
while True:
    status = requests.get('http://localhost:5000/api/status').json()
    print(f"Progress: {status['progress']}%")
    if not status['is_processing']:
        break
    time.sleep(1)

# Get results
results = requests.get('http://localhost:5000/api/results/00').json()
```

### JavaScript Integration
```javascript
// Start processing
fetch('/api/process', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        sequence: '00',
        start_frame: 0,
        end_frame: 100
    })
});

// Poll status
setInterval(async () => {
    const status = await fetch('/api/status').then(r => r.json());
    console.log('Progress:', status.progress);
}, 1000);
```

## 📚 Architecture

```
Web Browser
    ↓ (HTTP requests)
Flask Server (web_app.py)
    ↓ (API calls)
Dynamic SLAM System
    ↓ (Processing)
Results → Served to Browser
```

### Files Structure
```
DYNAMIC_SLAM/
├── web_app.py              # Flask application
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── app.js            # Frontend JavaScript
│   └── style.css         # Custom CSS
├── start_web.bat         # Windows launcher
├── start_web.sh          # Linux/Mac launcher
└── results/              # Output files (served)
```

## 🎯 Future Enhancements

Potential improvements:
- [ ] Real-time video streaming
- [ ] WebSocket for live updates
- [ ] User authentication
- [ ] Multiple concurrent sessions
- [ ] Result comparison tool
- [ ] Parameter optimization wizard
- [ ] Export to different formats
- [ ] Cloud deployment support

---

## 📞 Support

For issues or questions:
1. Check terminal output for errors
2. Verify Flask installation
3. Check dataset paths in config
4. Review browser console logs

**Enjoy the web interface! 🎉**
