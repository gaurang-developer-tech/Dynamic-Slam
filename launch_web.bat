@echo off
REM Dynamic SLAM Web Interface - Easy Launcher
REM This script starts the server and opens your browser automatically

echo.
echo ========================================
echo   Dynamic SLAM - Starting Web Interface
echo ========================================
echo.
echo Activating environment...
call conda activate dynamic_slam

echo.
echo Starting web server...
echo.
echo The web interface will open in your browser automatically.
echo.
echo If it doesn't open, navigate to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server when you're done.
echo.
echo ========================================
echo.

REM Start Python server in background
start /B python web_app.py

REM Wait a moment for server to start
timeout /t 3 /nobreak > nul

REM Open browser
start http://localhost:5000

REM Keep window open
echo Server is running...
echo.
pause
