@echo off
REM ============================================================
REM GramAI - Windows Mobile Deployment Script
REM Deploys as PWA accessible from mobile devices
REM ============================================================

echo.
echo ==========================================
echo   GramAI Mobile Deployment (Windows)
echo ==========================================
echo.

set PROJECT_DIR=%~dp0..
cd /d "%PROJECT_DIR%"

REM ---- Step 1: Python Environment ----
echo [1/4] Setting up Python environment...
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r backend\requirements.txt --quiet 2>nul

REM ---- Step 2: Create .env ----
echo [2/4] Configuring environment...
if not exist ".env" (
    (
        echo HOST=0.0.0.0
        echo PORT=8000
        echo OLLAMA_BASE_URL=http://localhost:11434
        echo OLLAMA_MODEL=mistral
    ) > .env
    echo Created .env configuration file
)

REM ---- Step 3: Get IP Address ----
echo [3/4] Finding network address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "LOCAL_IP=%%a"
    goto :found_ip
)
:found_ip
set LOCAL_IP=%LOCAL_IP: =%

REM ---- Step 4: Start Server ----
echo [4/4] Starting GramAI server...
echo.
echo ==========================================
echo   GramAI is running!
echo.
echo   On your PC:    http://localhost:8000
echo   On mobile:     http://%LOCAL_IP%:8000
echo.
echo   To install on phone:
echo   1. Connect phone to same WiFi
echo   2. Open Chrome on phone
echo   3. Go to http://%LOCAL_IP%:8000
echo   4. Tap "Install" banner or menu "Add to Home Screen"
echo   5. App will work offline!
echo ==========================================
echo.
echo Press Ctrl+C to stop the server.
echo.

venv\Scripts\python.exe backend\main.py
