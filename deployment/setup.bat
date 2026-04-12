@echo off
REM ================================================
REM GramAI - Windows Setup Script
REM Offline AI Assistant for Rural India
REM ================================================
REM Usage: Right-click > Run as Administrator
REM ================================================

echo ==============================================
echo 🌾 GramAI - Windows Setup Script
echo 🌾 ग्रामAI - विंडोज सेटअप
echo ==============================================

set PROJECT_DIR=%~dp0..

REM ---- Step 1: Check Python ----
echo.
echo [1/5] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)
echo ✅ Python found

REM ---- Step 2: Create Virtual Environment ----
echo.
echo [2/5] Creating Python virtual environment...
cd /d "%PROJECT_DIR%"
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate
pip install --upgrade pip
pip install -r backend\requirements.txt
echo ✅ Dependencies installed

REM ---- Step 3: Install Ollama ----
echo.
echo [3/5] Checking Ollama...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Ollama not found!
    echo 📥 Download from: https://ollama.ai/download
    echo After installing, run: ollama pull mistral
    echo Press any key to continue anyway...
    pause
) else (
    echo ✅ Ollama found
    echo Pulling Mistral model...
    ollama pull mistral
)

REM ---- Step 4: Create Directories ----
echo.
echo [4/5] Setting up directories...
if not exist "backend\audio_cache" mkdir backend\audio_cache
if not exist "backend\models" mkdir backend\models
if not exist "backend\chroma_db" mkdir backend\chroma_db
echo ✅ Directories created

REM ---- Step 5: Create Start Script ----
echo.
echo [5/5] Creating start script...
(
    echo @echo off
    echo echo Starting GramAI...
    echo cd /d "%PROJECT_DIR%"
    echo call venv\Scripts\activate
    echo start "" ollama serve
    echo timeout /t 3 /nobreak
    echo cd backend
    echo python -m uvicorn main:app --host 0.0.0.0 --port 8000
) > "%PROJECT_DIR%\start-gramai.bat"

echo.
echo ==============================================
echo ✅ GramAI सेटअप पूरा हुआ!
echo ✅ GramAI Setup Complete!
echo.
echo 🚀 To start: Double-click start-gramai.bat
echo 🌐 Then open: http://localhost:8000
echo ==============================================
pause
