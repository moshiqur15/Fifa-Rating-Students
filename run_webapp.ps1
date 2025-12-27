# PowerShell Startup script for Student Rating System Web Application

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Student Rating System - Web App" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if streamlit is installed
try {
    python -c "import streamlit" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Streamlit not found"
    }
    Write-Host "✓ Streamlit is installed" -ForegroundColor Green
} catch {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    pip install -r requirements_webapp.txt
    Write-Host ""
}

# Create necessary directories
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "✓ Created logs directory" -ForegroundColor Green
}

if (-not (Test-Path "models")) {
    New-Item -ItemType Directory -Path "models" | Out-Null
    Write-Host "✓ Created models directory" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting web application..." -ForegroundColor Green
Write-Host ""
Write-Host "The app will open in your browser at http://localhost:8501" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start streamlit app
streamlit run webapp.py
