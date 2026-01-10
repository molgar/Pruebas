# Quick Start Guide

Get up and running with AI Transcription Studio in just a few steps!

## Prerequisites Checklist

Before you begin, make sure you have:

- [ ] Windows 10 or 11 (64-bit)
- [ ] Python 3.9 or higher installed
- [ ] NVIDIA GPU with updated drivers (optional, but recommended for speed)
- [ ] At least 8 GB RAM
- [ ] 5 GB free disk space
- [ ] Working microphone (for live transcription)

## Installation (5 minutes)

### Option 1: Automated Setup (Recommended)

1. **Download/Clone the project**
   ```bash
   git clone <repository-url>
   cd transcription-app
   ```

2. **Run the setup script**
   - Double-click `setup.bat`
   - Wait for all dependencies to install (5-10 minutes)

3. **Launch the application**
   - Double-click `run.bat`

### Option 2: Manual Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   python main.py
   ```

## First Run

When you first launch the application:

1. **Model Download**: The app will download the NVIDIA Parakeet TDT model (~1-2 GB)
   - This only happens once
   - Takes 5-15 minutes depending on internet speed
   - Be patient!

2. **GPU Detection**: The app will automatically detect if you have an NVIDIA GPU
   - GPU: Shows "Device: NVIDIA GeForce RTX..." or similar
   - CPU: Shows "Device: CPU"

3. **Ready to Use**: Once you see "Ready to transcribe" in the status bar

## Using the App

### Selecting Language

1. Use the **Language** dropdown in the top bar
2. Choose from:
   - English
   - Spanish (Español)
   - French (Français)
   - Multilingual (Auto-detect)
3. The model will reload with your selected language

### Enabling Speaker Detection

1. Check the **"Enable Speaker Detection"** box in the top bar
2. Different speakers will be automatically labeled in transcriptions
3. Speaker labels appear as [Speaker 1], [Speaker 2], etc.

### Live Transcription (Real-time)

1. Click the **"Live Transcription"** tab
2. Select your microphone from the dropdown
3. (Optional) Enable speaker detection for conversations
4. Click **"Start Recording"** 🎙️
5. Speak clearly into your microphone
6. Watch the transcription appear in real-time with speaker labels!
7. Click **"Stop Recording"** ⏹️ when done
8. Export using **💾 TXT**, **💾 SRT**, or **💾 VTT** buttons

**Tips for Best Results:**
- Speak clearly at a normal pace
- Use a good quality microphone
- Minimize background noise
- Ensure proper microphone levels

### File Transcription (Pre-recorded Audio)

1. Click the **"File Transcription"** tab
2. Click **"Select Audio File"** 📁
3. Choose your audio file (WAV, MP3, FLAC, OGG, M4A)
4. (Optional) Enable speaker detection to identify different speakers
5. Click **"Transcribe File"** ▶️
6. Wait for processing to complete
7. View the transcription with timestamps and speaker labels
8. Export using **💾 TXT**, **💾 SRT**, **💾 VTT**, or **💾 JSON** buttons

**Supported Formats:**
- WAV (best quality)
- MP3
- FLAC
- OGG
- M4A

### Exporting Transcriptions

After transcribing, you can export in multiple formats:

- **TXT**: Plain text with speaker labels
- **SRT**: Subtitle format for video players
- **VTT**: Web video subtitle format
- **JSON**: Complete data with timestamps and metadata

Simply click the export button for your desired format and choose where to save!

## Common Issues

### "Failed to load model"
- **Solution**: Check your internet connection and try again
- Make sure you have enough disk space (5GB+)

### "No microphone detected"
- **Solution**: Check Windows sound settings
- Make sure your microphone is plugged in and enabled
- Try restarting the application

### Slow transcription
- **Solution**: Install CUDA for GPU acceleration
- Close other GPU-intensive applications
- Try shorter audio clips

### "Python not found"
- **Solution**: Install Python from python.org
- Make sure to check "Add Python to PATH" during installation

## Performance Expectations

### With NVIDIA GPU (Recommended)
- **Live transcription**: Near real-time
- **File transcription**: ~30 seconds per minute of audio

### With CPU Only
- **Live transcription**: 2-5 second delay
- **File transcription**: 2-5 minutes per minute of audio

## Next Steps

Now that you're up and running:

1. Try both live and file transcription modes
2. Experiment with different audio qualities
3. Check the full README.md for advanced features
4. Adjust your microphone settings for optimal quality

## Need Help?

- Read the full [README.md](README.md) for detailed documentation
- Check the Troubleshooting section
- Review system requirements

## Keyboard Shortcuts

(Future feature - currently all controls via GUI)

## Tips for Best Accuracy

1. **Audio Quality**: Use high-quality audio files (WAV at 16kHz or higher)
2. **Clear Speech**: Speak clearly and at a moderate pace
3. **Quiet Environment**: Minimize background noise
4. **Good Microphone**: Use a quality microphone positioned correctly
5. **GPU Acceleration**: Use NVIDIA GPU for faster, more responsive transcription

Enjoy transcribing! 🎙️📝
