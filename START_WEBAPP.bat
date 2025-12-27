@echo off
echo ============================================================
echo   STUDENT RATING SYSTEM - WEB APPLICATION LAUNCHER
echo ============================================================
echo.
echo Starting web application...
echo.

cd /d "%~dp0"

call venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

echo Virtual environment activated
echo Starting server...
echo.
echo The browser will open automatically at http://127.0.0.1:8000
echo Press CTRL+C to stop the server
echo.
echo ============================================================
echo.

python run_webapp.py

pause
