@echo off
REM Dynamic SLAM Web Application Launcher for Windows

echo ====================================
echo Dynamic SLAM Web Application
echo ====================================
echo.

REM Check if conda environment is activated
python -c "import sys; sys.exit(0 if 'dynamic_slam' in sys.prefix else 1)" 2>nul
if %errorlevel% neq 0 (
    echo Warning: Conda environment 'dynamic_slam' not detected
    echo Please activate it first:
    echo   conda activate dynamic_slam
    echo.
    echo Attempting to continue anyway...
    echo.
)

REM Check if Flask is installed
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo Flask not found. Installing...
    pip install flask
    echo.
)

REM Create necessary directories
if not exist "results" mkdir results
if not exist "uploads" mkdir uploads
if not exist "templates" mkdir templates
if not exist "static" mkdir static

echo Starting web server...
echo.
echo ====================================
echo Open your browser and go to:
echo   http://localhost:5000
echo ====================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the web application
python web_app.py

pause
