"""
Transcription Engine using NVIDIA Parakeet TDT Model
Handles model loading, GPU management, and transcription
"""

import torch
import nemo.collections.asr as nemo_asr
from typing import Optional, Callable
import numpy as np
import soundfile as sf
from pathlib import Path


class TranscriptionEngine:
    """Manages the Parakeet TDT model and transcription operations"""

    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        Initialize the transcription engine

        Args:
            progress_callback: Optional callback function for progress updates
        """
        self.model = None
        self.device = self._get_device()
        self.progress_callback = progress_callback
        self.is_loaded = False

    def _get_device(self) -> str:
        """Detect and return the best available device"""
        if torch.cuda.is_available():
            return 'cuda'
        else:
            return 'cpu'

    def load_model(self, model_name: str = "nvidia/parakeet-tdt-1.1b") -> bool:
        """
        Load the Parakeet TDT model

        Args:
            model_name: HuggingFace model identifier or local path

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.progress_callback:
                self.progress_callback("Loading model...", 0)

            # Load pre-trained Parakeet TDT model
            self.model = nemo_asr.models.EncDecRNNTBPEModel.from_pretrained(
                model_name=model_name
            )

            # Move model to appropriate device
            self.model = self.model.to(self.device)
            self.model.eval()

            if self.progress_callback:
                self.progress_callback("Model loaded successfully", 100)

            self.is_loaded = True
            return True

        except Exception as e:
            if self.progress_callback:
                self.progress_callback(f"Error loading model: {str(e)}", -1)
            return False

    def transcribe_file(self, audio_path: str) -> str:
        """
        Transcribe an audio file

        Args:
            audio_path: Path to the audio file

        Returns:
            Transcribed text
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        try:
            if self.progress_callback:
                self.progress_callback("Transcribing audio file...", 0)

            # Transcribe using NeMo
            transcription = self.model.transcribe([audio_path])[0]

            if self.progress_callback:
                self.progress_callback("Transcription complete", 100)

            return transcription

        except Exception as e:
            error_msg = f"Error during transcription: {str(e)}"
            if self.progress_callback:
                self.progress_callback(error_msg, -1)
            raise RuntimeError(error_msg)

    def transcribe_audio_data(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Transcribe raw audio data (for live transcription)

        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate of the audio

        Returns:
            Transcribed text
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        try:
            # Save temporary audio file
            temp_path = Path("temp_audio.wav")
            sf.write(temp_path, audio_data, sample_rate)

            # Transcribe
            transcription = self.model.transcribe([str(temp_path)])[0]

            # Clean up
            temp_path.unlink(missing_ok=True)

            return transcription

        except Exception as e:
            error_msg = f"Error during transcription: {str(e)}"
            if self.progress_callback:
                self.progress_callback(error_msg, -1)
            raise RuntimeError(error_msg)

    def get_device_info(self) -> dict:
        """Get information about the computing device being used"""
        info = {
            'device': self.device,
            'device_name': 'CPU'
        }

        if self.device == 'cuda':
            info['device_name'] = torch.cuda.get_device_name(0)
            info['cuda_version'] = torch.version.cuda
            info['gpu_memory_total'] = torch.cuda.get_device_properties(0).total_memory / 1e9
            info['gpu_memory_allocated'] = torch.cuda.memory_allocated(0) / 1e9

        return info

    def unload_model(self):
        """Unload the model and free up resources"""
        if self.model is not None:
            del self.model
            self.model = None

        if self.device == 'cuda':
            torch.cuda.empty_cache()

        self.is_loaded = False
