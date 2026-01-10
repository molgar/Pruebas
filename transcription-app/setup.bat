@echo off
echo ========================================
echo AI Transcription Studio - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not installed
    echo Please reinstall Python with pip enabled
    pause
    exit /b 1
)

echo Installing dependencies...
echo This may take several minutes...
echo.

REM Upgrade pip
python -m pip install --upgrade pip

REM Install PyTorch with CUDA support (for NVIDIA GPUs)
echo Installing PyTorch with CUDA support...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

REM Install other dependencies
echo Installing other dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo You can now run the application using:
echo     run.bat
echo.
echo Or manually with:
echo     python main.py
echo.
pause
