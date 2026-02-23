"""
Flask Web Application for Dynamic SLAM
Real-time SLAM processing with web interface
"""
import os
import sys
import json
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from dynamic_slam import DynamicSLAM
from utils import get_image_list

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dynamic-slam-secret-key-2026'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# Global state for processing
processing_state = {
    'is_processing': False,
    'progress': 0,
    'current_frame': 0,
    'total_frames': 0,
    'status': 'idle',
    'message': '',
    'sequence': None,
    'results': None,
    'errors': []
}

processing_lock = threading.Lock()


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/sequences', methods=['GET'])
def get_sequences():
    """Get list of available sequences"""
    sequences = []
    sequences_dir = Config.SEQUENCES_DIR
    
    if os.path.exists(sequences_dir):
        for seq in sorted(os.listdir(sequences_dir)):
            seq_path = os.path.join(sequences_dir, seq)
            if os.path.isdir(seq_path):
                # Check if images exist
                img_path = os.path.join(seq_path, 'image_0')
                if os.path.exists(img_path):
                    images = get_image_list(img_path)
                    
                    # Check if ground truth exists
                    gt_path = os.path.join(Config.POSES_DIR, f"{seq}.txt")
                    has_gt = os.path.exists(gt_path)
                    
                    sequences.append({
                        'id': seq,
                        'name': f'Sequence {seq}',
                        'num_frames': len(images),
                        'has_ground_truth': has_gt
                    })
    
    return jsonify({'sequences': sequences})


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    config = {
        'feature_type': Config.FEATURE_TYPE,
        'max_features': Config.MAX_FEATURES,
        'yolo_confidence': Config.YOLO_CONF_THRESHOLD,
        'min_match_count': Config.MIN_MATCH_COUNT,
        'ransac_threshold': Config.RANSAC_REPROJ_THRESHOLD,
    }
    return jsonify(config)


@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    data = request.json
    
    if 'feature_type' in data:
        Config.FEATURE_TYPE = data['feature_type']
    if 'max_features' in data:
        Config.MAX_FEATURES = int(data['max_features'])
    if 'yolo_confidence' in data:
        Config.YOLO_CONF_THRESHOLD = float(data['yolo_confidence'])
    if 'min_match_count' in data:
        Config.MIN_MATCH_COUNT = int(data['min_match_count'])
    if 'ransac_threshold' in data:
        Config.RANSAC_REPROJ_THRESHOLD = float(data['ransac_threshold'])
    
    return jsonify({'status': 'success', 'message': 'Configuration updated'})


@app.route('/api/process', methods=['POST'])
def process_sequence():
    """Start processing a sequence"""
    global processing_state
    
    with processing_lock:
        if processing_state['is_processing']:
            return jsonify({'status': 'error', 'message': 'Already processing'}), 400
        
        data = request.json
        sequence = data.get('sequence', '00')
        start_frame = int(data.get('start_frame', 0))
        end_frame = data.get('end_frame')
        if end_frame:
            end_frame = int(end_frame)
        
        # Reset state
        processing_state = {
            'is_processing': True,
            'progress': 0,
            'current_frame': start_frame,
            'total_frames': 0,
            'status': 'starting',
            'message': 'Initializing SLAM system...',
            'sequence': sequence,
            'results': None,
            'errors': [],
            'start_time': time.time()
        }
        
        # Start processing in background thread
        thread = threading.Thread(
            target=run_slam_processing,
            args=(sequence, start_frame, end_frame)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'status': 'success', 'message': 'Processing started'})


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current processing status"""
    with processing_lock:
        return jsonify(processing_state)


@app.route('/api/stop', methods=['POST'])
def stop_processing():
    """Stop current processing"""
    global processing_state
    
    with processing_lock:
        if processing_state['is_processing']:
            processing_state['status'] = 'stopping'
            processing_state['message'] = 'Stopping...'
    
    return jsonify({'status': 'success', 'message': 'Stop signal sent'})


@app.route('/api/results/<sequence>', methods=['GET'])
def get_results(sequence):
    """Get results for a sequence"""
    results_dir = Config.RESULTS_DIR
    
    results = {
        'sequence': sequence,
        'files': []
    }
    
    # List result files
    if os.path.exists(results_dir):
        for filename in os.listdir(results_dir):
            if sequence in filename:
                filepath = os.path.join(results_dir, filename)
                results['files'].append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': os.path.getmtime(filepath)
                })
    
    # Load trajectory if exists
    traj_file = os.path.join(results_dir, f"trajectory_seq{sequence}.txt")
    if os.path.exists(traj_file):
        results['has_trajectory'] = True
    
    # Load statistics
    stats_file = os.path.join(results_dir, f"error_stats_seq{sequence}.txt")
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            results['statistics'] = f.read()
    
    return jsonify(results)


@app.route('/results/<path:filename>')
def serve_result(filename):
    """Serve result files"""
    return send_from_directory(Config.RESULTS_DIR, filename)


@app.route('/api/demo/<demo_type>', methods=['POST'])
def run_demo(demo_type):
    """Run demo functions"""
    try:
        if demo_type == 'features':
            from demo import demo_feature_extraction
            demo_feature_extraction()
            return jsonify({'status': 'success', 'message': 'Feature demo completed'})
        
        elif demo_type == 'matching':
            from demo import demo_feature_matching
            demo_feature_matching()
            return jsonify({'status': 'success', 'message': 'Matching demo completed'})
        
        else:
            return jsonify({'status': 'error', 'message': 'Unknown demo type'}), 400
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def run_slam_processing(sequence, start_frame, end_frame):
    """Background task to run SLAM processing"""
    global processing_state
    
    try:
        # Update status
        with processing_lock:
            processing_state['status'] = 'initializing'
            processing_state['message'] = 'Loading SLAM system...'
        
        # Create SLAM system
        slam = DynamicSLAM(sequence=sequence)
        
        # Get total frames
        from utils import get_image_list
        img_path = Config.get_sequence_path(sequence)
        images = get_image_list(img_path)
        
        if end_frame is None:
            end_frame = len(images)
        
        total = end_frame - start_frame
        
        with processing_lock:
            processing_state['total_frames'] = total
            processing_state['status'] = 'processing'
            processing_state['message'] = 'Processing frames...'
        
        # Monkey-patch SLAM to update progress
        original_process = slam.process_sequence
        
        def process_with_progress(start, end):
            # Set up progress callback
            from tqdm import tqdm
            
            img_files = get_image_list(Config.get_sequence_path(sequence))
            
            # Initialize
            slam.estimated_poses = [slam.pose_estimator.get_pose()]
            prev_image = None
            prev_keypoints = None
            prev_descriptors = None
            
            for i in tqdm(range(start, end), desc="Processing"):
                # Update progress
                with processing_lock:
                    processing_state['current_frame'] = i
                    processing_state['progress'] = int((i - start) / total * 100)
                
                # Check if stopped
                if processing_state['status'] == 'stopping':
                    break
                
                # Process frame (simplified version)
                import cv2
                img = cv2.imread(img_files[i])
                
                dynamic_mask = slam.detector.detect(img)
                keypoints, descriptors = slam.feature_extractor.extract_features(
                    img, dynamic_mask, return_static_only=True
                )
                
                if prev_image is not None and prev_descriptors is not None:
                    matches = slam.feature_matcher.match(prev_descriptors, descriptors)
                    
                    if len(matches) >= Config.MIN_MATCH_COUNT:
                        pts1, pts2 = slam.feature_matcher.get_matched_points(
                            prev_keypoints, keypoints, matches
                        )
                        R, t, inlier_mask = slam.pose_estimator.estimate_pose_essential(pts1, pts2)
                        
                        if R is not None and t is not None:
                            scale = 1.0
                            if slam.gt_poses and i < len(slam.gt_poses):
                                gt_t = slam.gt_poses[i][:3, 3] - slam.gt_poses[i-1][:3, 3]
                                slam.scale_estimator.add_measurement(t, gt_t)
                                scale = slam.scale_estimator.get_scale()
                            
                            current_pose = slam.pose_estimator.update_pose(R, t, scale)
                            slam.estimated_poses.append(current_pose.copy())
                        else:
                            slam.estimated_poses.append(slam.estimated_poses[-1].copy())
                    else:
                        slam.estimated_poses.append(slam.estimated_poses[-1].copy())
                
                prev_image = img
                prev_keypoints = keypoints
                prev_descriptors = descriptors
        
        # Process
        process_with_progress(start_frame, end_frame)
        
        # Generate results
        with processing_lock:
            processing_state['status'] = 'generating_results'
            processing_state['message'] = 'Generating visualizations...'
        
        slam._generate_results()
        
        # Complete
        elapsed = time.time() - processing_state['start_time']
        
        with processing_lock:
            processing_state['is_processing'] = False
            processing_state['status'] = 'completed'
            processing_state['progress'] = 100
            processing_state['message'] = f'Completed in {elapsed:.1f}s'
            processing_state['results'] = {
                'num_poses': len(slam.estimated_poses),
                'elapsed_time': elapsed
            }
    
    except Exception as e:
        with processing_lock:
            processing_state['is_processing'] = False
            processing_state['status'] = 'error'
            processing_state['message'] = str(e)
            processing_state['errors'].append(str(e))
        
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(Config.RESULTS_DIR, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    print("\n" + "=" * 70)
    print("DYNAMIC SLAM WEB APPLICATION")
    print("=" * 70)
    print(f"\n🌐 Starting web server...")
    print(f"📁 Dataset: {Config.DATASET_ROOT}")
    print(f"📊 Results: {Config.RESULTS_DIR}")
    print("\n" + "=" * 70)
    print("🚀 Open your browser and navigate to:")
    print("   http://localhost:5000")
    print("=" * 70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
