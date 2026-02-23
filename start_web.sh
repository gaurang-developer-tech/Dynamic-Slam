#!/bin/bash
# Dynamic SLAM Web Application Launcher for Linux/Mac

echo "===================================="
echo "Dynamic SLAM Web Application"
echo "===================================="
echo ""

# Check if conda environment is activated
if [[ "$CONDA_DEFAULT_ENV" != "dynamic_slam" ]]; then
    echo "Warning: Conda environment 'dynamic_slam' not active"
    echo "Please activate it first:"
    echo "  conda activate dynamic_slam"
    echo ""
    echo "Attempting to continue anyway..."
    echo ""
fi

# Check if Flask is installed
python -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Flask not found. Installing..."
    pip install flask
    echo ""
fi

# Create necessary directories
mkdir -p results uploads templates static

echo "Starting web server..."
echo ""
echo "===================================="
echo "Open your browser and go to:"
echo "  http://localhost:5000"
echo "===================================="
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the web application
python web_app.py
