// Dynamic SLAM - Enhanced Interactive Frontend

// State
let currentSequence = null;
let sequences = [];
let tutorialStep = 1;
let welcomeShown = localStorage.getItem('welcomeShown') === 'true';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadSequences();
    loadConfiguration();
    setupEventListeners();
    startStatusPolling();
    initializeTooltips();
    showWelcome();
});

// Initialize app
function initializeApp() {
    console.log('🚀 Dynamic SLAM - Interactive UI Loaded');
    updateStepIndicator(1);
}

// Show welcome banner for first-time users
function showWelcome() {
    if (!welcomeShown) {
        document.getElementById('welcomeBanner').style.display = 'block';
        localStorage.setItem('welcomeShown', 'true');
    }
}

// Initialize tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Update step indicator
function updateStepIndicator(step) {
    document.querySelectorAll('.step').forEach((el, index) => {
        el.classList.remove('step-active', 'step-complete');
        const stepNum = index + 1;
        if (stepNum < step) {
            el.classList.add('step-complete');
        } else if (stepNum === step) {
            el.classList.add('step-active');
        }
    });
}

// Setup event listeners
function setupEventListeners() {
    // Buttons
    document.getElementById('startBtn').addEventListener('click', startProcessing);
    document.getElementById('stopBtn').addEventListener('click', stopProcessing);
    document.getElementById('updateConfigBtn').addEventListener('click', updateConfiguration);
    document.getElementById('quickDemoBtn').addEventListener('click', quickRun);
    document.getElementById('demoFeaturesBtn').addEventListener('click', () => runDemo('features'));
    document.getElementById('demoMatchingBtn').addEventListener('click', () => runDemo('matching'));
    document.getElementById('tutorialBtn').addEventListener('click', showTutorial);
    
    // Inline tutorial button
    const inlineBtn = document.getElementById('tutorialBtnInline');
    if (inlineBtn) {
        inlineBtn.addEventListener('click', showTutorial);
    }
    
    // Help button
    document.getElementById('helpBtn').addEventListener('click', () => {
        new bootstrap.Modal(document.getElementById('helpModal')).show();
    });
    
    // Sequence selection
    document.getElementById('sequenceSelect').addEventListener('change', onSequenceChange);
    
    // Range sliders with live update
    document.getElementById('maxFeatures').addEventListener('input', function() {
        document.getElementById('maxFeaturesValue').textContent = this.value;
    });
    
    document.getElementById('yoloConf').addEventListener('input', function() {
        document.getElementById('yoloConfValue').textContent = parseFloat(this.value).toFixed(2);
    });
}

// Load sequences
async function loadSequences() {
    try {
        const response = await fetch('/api/sequences');
        const data = await response.json();
        sequences = data.sequences;
        
        const select = document.getElementById('sequenceSelect');
        select.innerHTML = '';
        
        if (sequences.length === 0) {
            select.innerHTML = '<option value="">No sequences found</option>';
            showMessage('No sequences found in dataset', 'warning');
            return;
        }
        
        sequences.forEach(seq => {
            const option = document.createElement('option');
            option.value = seq.id;
            const gtLabel = seq.has_ground_truth ? ' ✓ GT' : '';
            option.textContent = `${seq.name} (${seq.num_frames} frames)${gtLabel}`;
            select.appendChild(option);
        });
        
        if (sequences.length > 0) {
            select.value = sequences[0].id;
            onSequenceChange();
        }
        
    } catch (error) {
        console.error('Error loading sequences:', error);
        showMessage('Error loading sequences. Please check the server.', 'danger');
    }
}

// Handle sequence change
function onSequenceChange() {
    const select = document.getElementById('sequenceSelect');
    const seqId = select.value;
    
    currentSequence = sequences.find(s => s.id === seqId);
    
    if (currentSequence) {
        const frames = currentSequence.num_frames;
        const gt = currentSequence.has_ground_truth ? 'Ground truth available for accuracy comparison' : 'No ground truth available';
        
        document.getElementById('sequenceInfoText').textContent = `${frames} frames • ${gt}`;
        document.getElementById('endFrame').max = frames;
        document.getElementById('endFrame').placeholder = `Max: ${frames}`;
        
        // Estimate processing time
        const estimatedMinutes = Math.ceil(frames / 150); // Rough estimate
        document.getElementById('estimatedTime').textContent = `~${estimatedMinutes} min`;
        
        // Load existing results
        loadResults(seqId);
        
        // Move to step 2
        updateStepIndicator(2);
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
    const btn = document.getElementById('updateConfigBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="bi bi-hourglass-split spin"></i> Saving...';
    
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
        
        if (response.ok) {
            showMessage('✓ Settings saved successfully!', 'success');
            btn.innerHTML = '<i class="bi bi-check-circle"></i> Saved!';
            setTimeout(() => {
                btn.innerHTML = '<i class="bi bi-check-circle"></i> Save Settings';
                btn.disabled = false;
            }, 2000);
        }
        
    } catch (error) {
        console.error('Error updating configuration:', error);
        showMessage('Error saving settings', 'danger');
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-check-circle"></i> Save Settings';
    }
}

// Start processing
async function startProcessing() {
    const seqId = document.getElementById('sequenceSelect').value;
    if (!seqId) {
        showMessage('⚠️ Please select a video sequence first!', 'warning');
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
            showMessage('🚀 Processing started! Watch the progress below...', 'info');
            updateStepIndicator(3);
        } else {
            showMessage(`❌ ${result.message}`, 'danger');
        }
        
    } catch (error) {
        console.error('Error starting processing:', error);
        showMessage('Error starting processing. Check server connection.', 'danger');
    }
}

// Stop processing
async function stopProcessing() {
    try {
        const response = await fetch('/api/stop', {method: 'POST'});
        await response.json();
        showMessage('⏸️ Stopping processing...', 'warning');
        
    } catch (error) {
        console.error('Error stopping processing:', error);
    }
}

// Quick run
function quickRun() {
    const seqId = document.getElementById('sequenceSelect').value;
    if (!seqId) {
        showMessage('⚠️ Please select a video sequence first!', 'warning');
        return;
    }
    
    document.getElementById('startFrame').value = 0;
    document.getElementById('endFrame').value = 50;
    
    // Show encouraging message for first-time users
    showMessage('🌟 Great! Running Quick Demo with 50 frames. This will take about 1 minute...', 'info');
    
    startProcessing();
}

// Run demo
async function runDemo(demoType) {
    const btn = event.target.closest('button');
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="bi bi-hourglass-split spin"></i> Running...';
    
    try {
        showMessage(`🎨 Running ${demoType} demo...`, 'info');
        
        const response = await fetch(`/api/demo/${demoType}`, {method: 'POST'});
        const data = await response.json();
        
        if (response.ok) {
            showMessage(`✓ ${demoType.charAt(0).toUpperCase() + demoType.slice(1)} demo completed! Check results below.`, 'success');
            
            // Reload results after delay
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
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    }
}

// Poll status
function startStatusPolling() {
    setInterval(updateStatus, 1000);
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
        
        const statusLabels = {
            'idle': '⚙️ Ready',
            'starting': '🚀 Starting',
            'initializing': '📋 Initializing',
            'processing': '⚡ Processing',
            'generating_results': '📊 Generating Results',
            'completed': '✓ Complete',
            'error': '❌ Error',
            'stopping': '⏸️ Stopping'
        };
        
        statusText.className = `badge ${badges[status.status] || 'bg-secondary'}`;
        statusText.textContent = statusLabels[status.status] || status.status.toUpperCase();
        
        // Update sequence
        document.getElementById('currentSequence').textContent = status.sequence || '-';
        
        // Update progress
        const progress = status.progress || 0;
        const progressBar = document.getElementById('progressBar');
        const progressPercent = document.getElementById('progressPercent');
        progressBar.style.width = `${progress}%`;
        progressPercent.textContent = `${progress}%`;
        
        if (status.current_frame !== undefined && status.total_frames !== undefined) {
            document.getElementById('progressText').textContent = 
                `Frame ${status.current_frame} / ${status.total_frames}`;
        } else {
            document.getElementById('progressText').textContent = status.status === 'idle' ? 
                'Waiting to start...' : 'Processing...';
        }
        
        // Update message
        if (status.message) {
            const friendlyMessages = {
                'Ready to process': '👍 Ready! Select a sequence and click Quick Demo to start.',
                'Processing started': '🚀 Processing started! Sit back and watch the progress.',
                'Processing completed': '🎉 All done! Check out your results below.'
            };
            
            const msg = friendlyMessages[status.message] || status.message;
            document.getElementById('messageText').textContent = msg;
        }
        
        // Update buttons
        if (status.is_processing) {
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            updateStepIndicator(3);
        } else {
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        }
        
        // Show statistics if completed
        if (status.status === 'completed' && status.results) {
            showStatistics(status.results);
            updateStepIndicator(4);
            
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
    const statsCard = document.getElementById('statsCard');
    statsCard.style.display = 'block';
    statsCard.style.animation = 'fadeInUp 0.5s ease-out';
    
    document.getElementById('statPoses').textContent = results.num_poses || '-';
    document.getElementById('statTime').textContent = results.elapsed_time ? 
        `${results.elapsed_time.toFixed(1)}s` : '-';
    
    if (results.elapsed_time && results.num_poses) {
        const fps = results.num_poses / results.elapsed_time;
        document.getElementById('statFPS').textContent = fps.toFixed(1);
    }
}

// Load results
async function loadResults(sequence) {
    try {
        const response = await fetch(`/api/results/${sequence}`);
        const data = await response.json();
        
        const gallery = document.getElementById('resultsGallery');
        const noResults = document.getElementById('noResults');
        const resultsInfo = document.getElementById('resultsInfo');
        const resultsCard = document.getElementById('resultsCard');
        
        if (data.files && data.files.length > 0) {
            resultsCard.style.display = 'block';
            gallery.innerHTML = '';
            noResults.style.display = 'none';
            resultsInfo.style.display = 'block';
            
            // Filter image files
            const imageFiles = data.files.filter(f => 
                f.name.endsWith('.png') || f.name.endsWith('.jpg')
            );
            
            imageFiles.forEach(file => {
                const col = document.createElement('div');
                col.className = 'col-md-6 mb-3';
                
                const card = document.createElement('div');
                card.className = 'card';
                card.style.animation = 'fadeInUp 0.5s ease-out';
                
                const img = document.createElement('img');
                img.src = `/results/${file.name}`;
                img.className = 'card-img-top';
                img.alt = file.name;
                img.onclick = () => showImageModal(file.name, `/results/${file.name}`);
                
                const body = document.createElement('div');
                body.className = 'card-body';
                
                const title = document.createElement('h6');
                title.className = 'card-title';
                const cleanName = file.name
                    .replace(`_seq${sequence}`, '')
                    .replace(/\.[^/.]+$/, '')
                    .replace(/_/g, ' ');
                title.textContent = cleanName.charAt(0).toUpperCase() + cleanName.slice(1);
                
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
            resultsInfo.style.display = 'none';
        }
        
    } catch (error) {
        console.error('Error loading results:', error);
    }
}

// Show image modal
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
    messageBox.style.animation = 'slideDown 0.3s ease-out';
    
    const icon = {
        'info': 'info-circle',
        'success': 'check-circle',
        'warning': 'exclamation-triangle',
        'danger': 'x-circle'
    };
    
    const iconHtml = `<i class="bi bi-${icon[type] || 'info-circle'} fs-4 me-3"></i>`;
    const contentHtml = `<div><div class="fw-bold">${type === 'success' ? 'Success!' : type === 'danger' ? 'Error' : type === 'warning' ? 'Attention' : 'Info'}</div><div id="messageText">${message}</div></div>`;
    
    messageBox.innerHTML = `<div class="d-flex align-items-start">${iconHtml}${contentHtml}</div>`;
}

// Show tutorial
function showTutorial() {
    const tutorialContent = document.getElementById('tutorialContent');
    
    tutorialContent.innerHTML = `
        <div class="tutorial-step">
            <h4><i class="bi bi-stars"></i> Welcome to Dynamic SLAM!</h4>
            <p class="lead">Let's get you started in 3 easy steps:</p>
            
            <div class="card mb-3">
                <div class="card-body">
                    <h6 class="fw-bold"><i class="bi bi-1-circle text-primary"></i> Choose a Video Sequence</h6>
                    <p>At the top left, select any sequence from the dropdown. Each sequence is a video split into frames.</p>
                    <p class="small text-muted">💡 Tip: Sequences with "✓ GT" have ground truth data for accuracy comparison.</p>
                </div>
            </div>
            
            <div class="card mb-3">
                <div class="card-body">
                    <h6 class="fw-bold"><i class="bi bi-2-circle text-success"></i> Run Quick Demo</h6>
                    <p>Click the <strong>"Quick Demo"</strong> button. It processes 50 frames in about 1 minute.</p>
                    <p class="small text-muted">💡 Tip: Keep default settings - they work great!</p>
                </div>
            </div>
            
            <div class="card mb-3">
                <div class="card-body">
                    <h6 class="fw-bold"><i class="bi bi-3-circle text-info"></i> View Results</h6>
                    <p>Results appear below automatically. Click any image to view it larger!</p>
                    <p class="small text-muted">💡 Tip: You'll see trajectory maps, feature matches, and error plots.</p>
                </div>
            </div>
            
            <div class="alert alert-success">
                <strong><i class="bi bi-check-circle"></i> That's it!</strong> Close this and try the Quick Demo now.
            </div>
            
            <button class="btn btn-primary btn-lg w-100" data-bs-dismiss="modal">
                <i class="bi bi-rocket"></i> Start Using Dynamic SLAM
            </button>
        </div>
    `;
    
    const modal = new bootstrap.Modal(document.getElementById('tutorialModal'));
    modal.show();
}

// Tutorial navigation (if needed)
function nextTutorialStep(step) {
    tutorialStep = step;
    showTutorial();
}
