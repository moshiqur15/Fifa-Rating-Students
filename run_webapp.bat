@echo off
REM Startup script for Student Rating System Web Application

echo ====================================
echo Student Rating System - Web App
echo ====================================
echo.

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements_webapp.txt
    echo.
)

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "models" mkdir models

echo Starting web application...
echo.
echo The app will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start streamlit app
streamlit run webapp.py

pause
