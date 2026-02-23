// Dynamic SLAM Web Application - Frontend JavaScript

// State
let currentSequence = null;
let processingInterval = null;
let sequences = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadSequences();
    loadConfiguration();
    setupEventListeners();
    startStatusPolling();
});

// Setup event listeners
function setupEventListeners() {
    // Buttons
    document.getElementById('startBtn').addEventListener('click', startProcessing);
    document.getElementById('stopBtn').addEventListener('click', stopProcessing);
    document.getElementById('updateConfigBtn').addEventListener('click', updateConfiguration);
    document.getElementById('quickRunBtn').addEventListener('click', quickRun);
    document.getElementById('demoFeaturesBtn').addEventListener('click', () => runDemo('features'));
    document.getElementById('demoMatchingBtn').addEventListener('click', () => runDemo('matching'));
    
    // Sequence selection
    document.getElementById('sequenceSelect').addEventListener('change', onSequenceChange);
    
    // Range sliders
    document.getElementById('maxFeatures').addEventListener('input', function() {
        document.getElementById('maxFeaturesValue').textContent = this.value;
    });
    
    document.getElementById('yoloConf').addEventListener('input', function() {
        document.getElementById('yoloConfValue').textContent = parseFloat(this.value).toFixed(2);
    });
}

// Load available sequences
async function loadSequences() {
    try {
        const response = await fetch('/api/sequences');
        const data = await response.json();
        sequences = data.sequences;
        
        const select = document.getElementById('sequenceSelect');
        select.innerHTML = '';
        
        if (sequences.length === 0) {
            select.innerHTML = '<option value="">No sequences found</option>';
            return;
        }
        
        sequences.forEach(seq => {
            const option = document.createElement('option');
            option.value = seq.id;
            option.textContent = `${seq.name} (${seq.num_frames} frames)${seq.has_ground_truth ? ' ✓ GT' : ''}`;
            select.appendChild(option);
        });
        
        // Select first sequence
        if (sequences.length > 0) {
            select.value = sequences[0].id;
            onSequenceChange();
        }
        
    } catch (error) {
        console.error('Error loading sequences:', error);
        showMessage('Error loading sequences', 'danger');
    }
}

// Handle sequence selection change
function onSequenceChange() {
    const select = document.getElementById('sequenceSelect');
    const seqId = select.value;
    
    currentSequence = sequences.find(s => s.id === seqId);
    
    if (currentSequence) {
        const info = `${currentSequence.num_frames} frames${currentSequence.has_ground_truth ? ', Ground Truth available' : ''}`;
        document.getElementById('sequenceInfo').textContent = info;
        document.getElementById('endFrame').max = currentSequence.num_frames;
        document.getElementById('endFrame').placeholder = `Max: ${currentSequence.num_frames}`;
        
        // Load results if available
        loadResults(seqId);
    }
}

// Load configuration
async function loadConfiguration() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        document.getElementById('featureType').value = config.feature_type;
        document.getElementById('maxFeatures').value = config.max_features;
        document.getElementById('maxFeaturesValue').textContent = config.max_features;
        document.getElementById('yoloConf').value = config.yolo_confidence;
        document.getElementById('yoloConfValue').textContent = config.yolo_confidence.toFixed(2);
        
    } catch (error) {
        console.error('Error loading configuration:', error);
    }
}

// Update configuration
async function updateConfiguration() {
    const config = {
        feature_type: document.getElementById('featureType').value,
        max_features: parseInt(document.getElementById('maxFeatures').value),
        yolo_confidence: parseFloat(document.getElementById('yoloConf').value)
    };
    
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(config)
        });
        
        const data = await response.json();
        showMessage('Configuration updated successfully', 'success');
        
    } catch (error) {
        console.error('Error updating configuration:', error);
        showMessage('Error updating configuration', 'danger');
    }
}

// Start processing
async function startProcessing() {
    const seqId = document.getElementById('sequenceSelect').value;
    if (!seqId) {
        showMessage('Please select a sequence', 'warning');
        return;
    }
    
    const startFrame = parseInt(document.getElementById('startFrame').value) || 0;
    const endFrameInput = document.getElementById('endFrame').value;
    const endFrame = endFrameInput ? parseInt(endFrameInput) : null;
    
    const data = {
        sequence: seqId,
        start_frame: startFrame,
        end_frame: endFrame
    };
    
    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            showMessage('Processing started...', 'info');
        } else {
            showMessage(result.message, 'danger');
        }
        
    } catch (error) {
        console.error('Error starting processing:', error);
        showMessage('Error starting processing', 'danger');
    }
}

// Stop processing
async function stopProcessing() {
    try {
        const response = await fetch('/api/stop', {method: 'POST'});
        const data = await response.json();
        showMessage('Stopping...', 'warning');
        
    } catch (error) {
        console.error('Error stopping processing:', error);
    }
}

// Quick run (50 frames)
function quickRun() {
    document.getElementById('startFrame').value = 0;
    document.getElementById('endFrame').value = 50;
    startProcessing();
}

// Run demo
async function runDemo(demoType) {
    try {
        showMessage(`Running ${demoType} demo...`, 'info');
        
        const response = await fetch(`/api/demo/${demoType}`, {method: 'POST'});
        const data = await response.json();
        
        if (response.ok) {
            showMessage(`${demoType} demo completed!`, 'success');
            // Reload results after a delay
            setTimeout(() => {
                const seqId = document.getElementById('sequenceSelect').value;
                if (seqId) loadResults(seqId);
            }, 1000);
        } else {
            showMessage(`Demo failed: ${data.message}`, 'danger');
        }
        
    } catch (error) {
        console.error('Error running demo:', error);
        showMessage('Error running demo', 'danger');
    }
}

// Poll processing status
function startStatusPolling() {
    setInterval(updateStatus, 1000); // Poll every second
}

// Update status
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        
        // Update status badge
        const statusText = document.getElementById('statusText');
        const badges = {
            'idle': 'bg-secondary',
            'starting': 'bg-info',
            'initializing': 'bg-info',
            'processing': 'bg-primary',
            'generating_results': 'bg-warning',
            'completed': 'bg-success',
            'error': 'bg-danger',
            'stopping': 'bg-warning'
        };
        
        statusText.className = `badge ${badges[status.status] || 'bg-secondary'}`;
        statusText.textContent = status.status.replace('_', ' ').toUpperCase();
        
        // Update current sequence
        document.getElementById('currentSequence').textContent = status.sequence || '-';
        
        // Update progress
        const progress = status.progress || 0;
        const progressBar = document.getElementById('progressBar');
        progressBar.style.width = `${progress}%`;
        progressBar.textContent = `${progress}%`;
        
        if (status.current_frame !== undefined && status.total_frames !== undefined) {
            document.getElementById('progressText').textContent = 
                `Frame ${status.current_frame} / ${status.total_frames}`;
        }
        
        // Update message
        if (status.message) {
            document.getElementById('messageText').textContent = status.message;
        }
        
        // Update buttons
        if (status.is_processing) {
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
        } else {
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        }
        
        // Show statistics if completed
        if (status.status === 'completed' && status.results) {
            showStatistics(status.results);
            // Load results
            if (status.sequence) {
                loadResults(status.sequence);
            }
        }
        
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

// Show statistics
function showStatistics(results) {
    document.getElementById('statsCard').style.display = 'block';
    document.getElementById('statPoses').textContent = results.num_poses || '-';
    document.getElementById('statTime').textContent = results.elapsed_time ? 
        `${results.elapsed_time.toFixed(1)}s` : '-';
    
    if (results.elapsed_time && results.num_poses) {
        const fps = results.num_poses / results.elapsed_time;
        document.getElementById('statFPS').textContent = fps.toFixed(2);
    }
}

// Load results
async function loadResults(sequence) {
    try {
        const response = await fetch(`/api/results/${sequence}`);
        const data = await response.json();
        
        const gallery = document.getElementById('resultsGallery');
        const noResults = document.getElementById('noResults');
        
        if (data.files && data.files.length > 0) {
            document.getElementById('resultsCard').style.display = 'block';
            gallery.innerHTML = '';
            noResults.style.display = 'none';
            
            // Filter for image files
            const imageFiles = data.files.filter(f => 
                f.name.endsWith('.png') || f.name.endsWith('.jpg')
            );
            
            imageFiles.forEach(file => {
                const col = document.createElement('div');
                col.className = 'col-md-6 mb-3';
                
                const card = document.createElement('div');
                card.className = 'card';
                
                const img = document.createElement('img');
                img.src = `/results/${file.name}`;
                img.className = 'card-img-top';
                img.alt = file.name;
                img.style.cursor = 'pointer';
                img.onclick = () => showImageModal(file.name, `/results/${file.name}`);
                
                const body = document.createElement('div');
                body.className = 'card-body';
                
                const title = document.createElement('h6');
                title.className = 'card-title';
                title.textContent = file.name.replace(`_seq${sequence}`, '').replace(/\.[^/.]+$/, '');
                
                const downloadBtn = document.createElement('a');
                downloadBtn.href = `/results/${file.name}`;
                downloadBtn.download = file.name;
                downloadBtn.className = 'btn btn-sm btn-outline-primary';
                downloadBtn.innerHTML = '<i class="bi bi-download"></i> Download';
                
                body.appendChild(title);
                body.appendChild(downloadBtn);
                card.appendChild(img);
                card.appendChild(body);
                col.appendChild(card);
                gallery.appendChild(col);
            });
            
        } else {
            noResults.style.display = 'block';
        }
        
    } catch (error) {
        console.error('Error loading results:', error);
    }
}

// Show image in modal
function showImageModal(title, src) {
    document.getElementById('imageModalTitle').textContent = title;
    document.getElementById('modalImage').src = src;
    const modal = new bootstrap.Modal(document.getElementById('imageModal'));
    modal.show();
}

// Show message
function showMessage(message, type) {
    const messageBox = document.getElementById('messageBox');
    const classList = {
        'info': 'alert-info',
        'success': 'alert-success',
        'warning': 'alert-warning',
        'danger': 'alert-danger'
    };
    
    messageBox.className = `alert ${classList[type] || 'alert-info'} mb-0`;
    
    const icon = {
        'info': 'info-circle',
        'success': 'check-circle',
        'warning': 'exclamation-triangle',
        'danger': 'x-circle'
    };
    
    document.getElementById('messageText').innerHTML = 
        `<i class="bi bi-${icon[type] || 'info-circle'}"></i> ${message}`;
}
