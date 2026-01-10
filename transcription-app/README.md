# AI Transcription Studio

A modern Windows desktop application for transcribing audio to text using NVIDIA's Parakeet TDT (Transducer-based Automatic Speech Recognition) model. This application runs entirely locally on your PC, leveraging NVIDIA GPU acceleration for fast, accurate transcription.

## Features

- **Live Transcription**: Real-time transcription from your microphone
- **File Transcription**: Transcribe recorded audio files (WAV, MP3, FLAC, OGG, M4A)
- **GPU Accelerated**: Uses NVIDIA CUDA for fast processing
- **Modern UI**: Clean, dark-themed interface built with PyQt6
- **Local Processing**: Everything runs on your PC - no cloud services required
- **High Accuracy**: Powered by NVIDIA's state-of-the-art Parakeet TDT model

## Screenshots

The application features:
- Dark, modern interface optimized for extended use
- Tabbed interface for Live and File transcription modes
- Real-time device information display
- Progress indicators for model loading and transcription
- Support for multiple audio input devices

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 8 GB minimum, 16 GB recommended
- **Storage**: 5 GB free space for model and dependencies
- **Python**: Python 3.9 or higher

### For GPU Acceleration (Recommended)
- **GPU**: NVIDIA GPU with 4GB+ VRAM
- **CUDA**: CUDA 11.8 or higher
- **cuDNN**: Compatible version with CUDA

### For CPU-Only Mode
The application will work on CPU, but transcription will be significantly slower.

## Installation

### Step 1: Install Python
Download and install Python 3.9 or higher from [python.org](https://www.python.org/downloads/)

Make sure to check "Add Python to PATH" during installation.

### Step 2: Install NVIDIA CUDA Toolkit (For GPU Support)

1. Download CUDA Toolkit 11.8 or higher from [NVIDIA Developer](https://developer.nvidia.com/cuda-downloads)
2. Install following the installation wizard
3. Verify installation by opening Command Prompt and running:
   ```bash
   nvcc --version
   ```

### Step 3: Install PyAudio Dependencies

PyAudio requires portaudio. On Windows:

1. Download the appropriate PyAudio wheel file from [unofficial Windows binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
2. Or install via conda if you use Anaconda:
   ```bash
   conda install pyaudio
   ```

### Step 4: Clone or Download This Repository

```bash
git clone <repository-url>
cd transcription-app
```

### Step 5: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- PyQt6 (GUI framework)
- NVIDIA NeMo Toolkit (ASR models)
- PyTorch (Deep learning framework)
- Audio processing libraries
- GPU utilities

**Note**: The first run will download the Parakeet TDT model (~1-2 GB), which may take several minutes depending on your internet connection.

## Usage

### Running the Application

Navigate to the transcription-app directory and run:

```bash
python main.py
```

### Live Transcription

1. Select the **Live Transcription** tab
2. Choose your microphone from the dropdown menu
3. Click **Start Recording** button
4. Speak into your microphone
5. Watch as your speech is transcribed in real-time
6. Click **Stop Recording** when finished
7. Use **Clear Text** to reset the transcription

### File Transcription

1. Select the **File Transcription** tab
2. Click **Select Audio File** and choose your audio file
3. Click **Transcribe File**
4. Wait for the transcription to complete
5. The transcribed text will appear in the text area
6. Use **Clear Text** to reset the transcription

### Supported Audio Formats

- WAV (recommended for best quality)
- MP3
- FLAC
- OGG
- M4A

## Performance Tips

### For Best Performance

1. **Use GPU**: Ensure you have NVIDIA CUDA installed for GPU acceleration
2. **Audio Quality**: Use clear audio with minimal background noise
3. **Microphone**: Use a good quality microphone for live transcription
4. **File Format**: WAV files at 16kHz sample rate work best
5. **Close Other Applications**: Free up GPU memory for better performance

### Troubleshooting

#### Model Loading Issues
- Ensure you have enough disk space (5GB+)
- Check your internet connection for first-time model download
- Verify CUDA installation with `nvidia-smi` command

#### Audio Device Issues
- Make sure your microphone is connected and enabled
- Check Windows sound settings
- Try selecting a different audio device from the dropdown

#### GPU Not Detected
- Verify CUDA installation: `nvcc --version`
- Check NVIDIA driver: `nvidia-smi`
- Ensure PyTorch was installed with CUDA support

#### Out of Memory Errors
- Close other GPU-intensive applications
- Try shorter audio files
- Consider using CPU mode (automatic fallback)

## Technical Details

### Architecture

The application consists of three main components:

1. **TranscriptionEngine** (`src/transcription_engine.py`)
   - Loads and manages the NVIDIA Parakeet TDT model
   - Handles GPU/CPU device selection
   - Performs transcription inference

2. **AudioRecorder** (`src/audio_recorder.py`)
   - Captures live audio from microphone using PyAudio
   - Processes audio in chunks for real-time transcription
   - Supports multiple audio input devices

3. **MainWindow** (`src/main_window.py`)
   - PyQt6-based modern GUI
   - Threading for non-blocking operations
   - Real-time progress updates

### NVIDIA Parakeet TDT Model

Parakeet TDT is a state-of-the-art speech recognition model developed by NVIDIA:
- Based on Transducer architecture (RNN-T)
- Optimized for streaming and batch transcription
- Excellent accuracy across various accents and domains
- Efficient inference with CUDA acceleration

## Development

### Project Structure

```
transcription-app/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/
│   ├── __init__.py
│   ├── main_window.py     # Main GUI window
│   ├── transcription_engine.py  # AI model handler
│   └── audio_recorder.py  # Audio capture
├── models/                # Model cache (created on first run)
└── assets/                # Application assets
```

### Adding Features

The application is designed to be extensible:
- Add new transcription models in `transcription_engine.py`
- Customize the UI in `main_window.py`
- Add audio preprocessing in `audio_recorder.py`

## License

This project uses the following open-source components:
- NVIDIA NeMo Toolkit (Apache 2.0)
- PyQt6 (GPL/Commercial)
- PyTorch (BSD-style)

## Credits

- **NVIDIA** for the Parakeet TDT model and NeMo toolkit
- **PyQt** for the GUI framework
- **PyTorch** for the deep learning framework

## Support

For issues and questions:
1. Check the Troubleshooting section above
2. Review NVIDIA NeMo documentation
3. Check PyQt6 documentation for UI-related issues

## Future Enhancements

Potential features for future versions:
- Export transcriptions to various formats (TXT, SRT, VTT)
- Speaker diarization (who spoke when)
- Multiple language support
- Custom model fine-tuning
- Batch processing of multiple files
- Transcription editing and correction tools
- Timestamp annotations
- Audio playback synchronized with transcription

## Version History

### Version 1.0.0
- Initial release
- Live microphone transcription
- Audio file transcription
- GPU acceleration support
- Modern dark-themed UI
