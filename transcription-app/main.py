#!/usr/bin/env python3
"""
AI Transcription Studio
Main entry point for the application
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from main_window import main

if __name__ == "__main__":
    main()
