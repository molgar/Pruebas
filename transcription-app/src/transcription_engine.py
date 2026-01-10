"""
Transcription Engine using NVIDIA Parakeet TDT Model
Handles model loading, GPU management, transcription, and speaker diarization
"""

import torch
import nemo.collections.asr as nemo_asr
from typing import Optional, Callable, List, Dict, Tuple
import numpy as np
import soundfile as sf
from pathlib import Path
from export_handler import TranscriptionSegment


class TranscriptionEngine:
    """Manages the Parakeet TDT model and transcription operations"""

    # Available language models
    LANGUAGE_MODELS = {
        'en': 'nvidia/parakeet-tdt-1.1b',  # English
        'es': 'nvidia/parakeet-tdt-1.1b',  # Spanish (multilingual model)
        'fr': 'nvidia/parakeet-tdt-1.1b',  # French (multilingual model)
        'multilingual': 'nvidia/parakeet-tdt-1.1b'
    }

    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        Initialize the transcription engine

        Args:
            progress_callback: Optional callback function for progress updates
        """
        self.model = None
        self.diarization_model = None
        self.device = self._get_device()
        self.progress_callback = progress_callback
        self.is_loaded = False
        self.diarization_enabled = False
        self.current_language = 'en'

    def _get_device(self) -> str:
        """Detect and return the best available device"""
        if torch.cuda.is_available():
            return 'cuda'
        else:
            return 'cpu'

    def load_model(self, model_name: str = "nvidia/parakeet-tdt-1.1b", language: str = 'en') -> bool:
        """
        Load the Parakeet TDT model

        Args:
            model_name: HuggingFace model identifier or local path
            language: Language code ('en', 'es', 'fr', 'multilingual')

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.progress_callback:
                self.progress_callback("Loading model...", 0)

            # Set current language
            self.current_language = language

            # Use language-specific model if available
            if language in self.LANGUAGE_MODELS:
                model_name = self.LANGUAGE_MODELS[language]

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

    def enable_speaker_diarization(self) -> bool:
        """
        Enable speaker diarization (identifies different speakers)

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.progress_callback:
                self.progress_callback("Loading speaker diarization model...", 0)

            # Note: Using a lightweight approach with voice activity detection
            # For production, consider using pyannote.audio or NeMo MSDD model
            self.diarization_enabled = True

            if self.progress_callback:
                self.progress_callback("Speaker diarization enabled", 100)

            return True

        except Exception as e:
            if self.progress_callback:
                self.progress_callback(f"Error enabling diarization: {str(e)}", -1)
            return False

    def disable_speaker_diarization(self):
        """Disable speaker diarization"""
        self.diarization_enabled = False
        if self.diarization_model is not None:
            del self.diarization_model
            self.diarization_model = None

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

    def transcribe_file_with_timestamps(
        self,
        audio_path: str,
        return_hypotheses: bool = True
    ) -> List[TranscriptionSegment]:
        """
        Transcribe an audio file with detailed timestamps and speaker info

        Args:
            audio_path: Path to the audio file
            return_hypotheses: Whether to get detailed word-level timestamps

        Returns:
            List of TranscriptionSegment objects
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        try:
            if self.progress_callback:
                self.progress_callback("Transcribing with timestamps...", 0)

            # Load audio file
            audio, sample_rate = sf.read(audio_path)

            # Get detailed transcription with timestamps
            # NeMo's transcribe method with return_hypotheses gives word-level details
            hypotheses = self.model.transcribe(
                [audio_path],
                batch_size=1,
                return_hypotheses=True
            )

            segments = []
            current_time = 0.0

            if hypotheses and len(hypotheses) > 0:
                hypothesis = hypotheses[0]

                # Get text and timing information
                if hasattr(hypothesis, 'text'):
                    text = hypothesis.text
                    # Estimate timing based on audio duration
                    audio_duration = len(audio) / sample_rate

                    # Split into sentences for better segmentation
                    import re
                    sentences = re.split(r'[.!?]\s+', text)
                    sentences = [s.strip() for s in sentences if s.strip()]

                    time_per_segment = audio_duration / max(len(sentences), 1)

                    for i, sentence in enumerate(sentences):
                        start_time = i * time_per_segment
                        end_time = (i + 1) * time_per_segment

                        # Perform speaker diarization if enabled
                        speaker = self._detect_speaker(audio_path, start_time, end_time) if self.diarization_enabled else None

                        segment = TranscriptionSegment(
                            text=sentence,
                            start_time=start_time,
                            end_time=end_time,
                            speaker=speaker
                        )
                        segments.append(segment)

            if self.progress_callback:
                self.progress_callback("Transcription complete", 100)

            return segments

        except Exception as e:
            error_msg = f"Error during transcription: {str(e)}"
            if self.progress_callback:
                self.progress_callback(error_msg, -1)
            raise RuntimeError(error_msg)

    def _detect_speaker(self, audio_path: str, start_time: float, end_time: float) -> str:
        """
        Detect speaker for a specific time segment

        Args:
            audio_path: Path to audio file
            start_time: Start time in seconds
            end_time: End time in seconds

        Returns:
            Speaker label
        """
        # Simplified speaker detection using audio characteristics
        # In production, use pyannote.audio or NeMo's speaker diarization
        try:
            import librosa

            # Load audio segment
            audio, sr = librosa.load(audio_path, sr=16000, offset=start_time, duration=end_time-start_time)

            # Simple speaker detection based on pitch
            # Higher pitch = Speaker A, Lower pitch = Speaker B
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
            pitch_mean = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 150

            # Simple classification (this is a placeholder - use real models in production)
            if pitch_mean > 180:
                return "Speaker 1"
            else:
                return "Speaker 2"

        except Exception as e:
            print(f"Speaker detection error: {e}")
            return "Unknown"

    def transcribe_audio_data_with_timestamps(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000,
        start_time: float = 0.0
    ) -> TranscriptionSegment:
        """
        Transcribe raw audio data with timestamps (for live transcription)

        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate of the audio
            start_time: Starting timestamp for this chunk

        Returns:
            TranscriptionSegment object
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        try:
            # Save temporary audio file
            temp_path = Path("temp_audio.wav")
            sf.write(temp_path, audio_data, sample_rate)

            # Transcribe
            transcription = self.model.transcribe([str(temp_path)])[0]

            # Calculate duration
            duration = len(audio_data) / sample_rate
            end_time = start_time + duration

            # Detect speaker if diarization is enabled
            speaker = None
            if self.diarization_enabled:
                speaker = self._detect_speaker(str(temp_path), 0, duration)

            # Clean up
            temp_path.unlink(missing_ok=True)

            return TranscriptionSegment(
                text=transcription,
                start_time=start_time,
                end_time=end_time,
                speaker=speaker
            )

        except Exception as e:
            error_msg = f"Error during transcription: {str(e)}"
            if self.progress_callback:
                self.progress_callback(error_msg, -1)
            raise RuntimeError(error_msg)

    def set_language(self, language: str) -> bool:
        """
        Change the transcription language

        Args:
            language: Language code ('en', 'es', 'fr', 'multilingual')

        Returns:
            True if successful
        """
        if language not in self.LANGUAGE_MODELS:
            return False

        # If model is already loaded and language is different, reload
        if self.is_loaded and language != self.current_language:
            self.unload_model()
            return self.load_model(language=language)

        self.current_language = language
        return True

    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get list of supported languages

        Returns:
            Dictionary of language codes and names
        """
        return {
            'en': 'English',
            'es': 'Spanish (Español)',
            'fr': 'French (Français)',
            'multilingual': 'Multilingual (Auto-detect)'
        }

    def unload_model(self):
        """Unload the model and free up resources"""
        if self.model is not None:
            del self.model
            self.model = None

        if self.diarization_model is not None:
            del self.diarization_model
            self.diarization_model = None

        if self.device == 'cuda':
            torch.cuda.empty_cache()

        self.is_loaded = False
        self.diarization_enabled = False
