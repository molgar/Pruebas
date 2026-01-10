@echo off
echo Starting AI Transcription Studio...
python main.py
if %errorlevel% neq 0 (
    echo.
    echo Error: Application failed to start
    echo Please make sure you have run setup.bat first
    pause
)
