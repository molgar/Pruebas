"""
Audio Recorder for Live Transcription
Handles real-time audio capture from microphone
"""

import pyaudio
import numpy as np
import threading
import queue
from typing import Optional, Callable
import wave


class AudioRecorder:
    """Manages live audio recording from microphone"""

    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_duration: float = 2.0,
        callback: Optional[Callable] = None
    ):
        """
        Initialize the audio recorder

        Args:
            sample_rate: Audio sample rate in Hz
            chunk_duration: Duration of each audio chunk in seconds
            callback: Callback function called with audio chunks
        """
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)
        self.callback = callback

        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.recording_thread = None

    def list_devices(self) -> list:
        """List all available audio input devices"""
        devices = []
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels'],
                    'sample_rate': int(device_info['defaultSampleRate'])
                })
        return devices

    def start_recording(self, device_index: Optional[int] = None):
        """
        Start recording audio from microphone

        Args:
            device_index: Index of the input device to use (None for default)
        """
        if self.is_recording:
            return

        self.is_recording = True

        # Open audio stream
        self.stream = self.audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024,
            stream_callback=self._audio_callback
        )

        self.stream.start_stream()

        # Start processing thread
        self.recording_thread = threading.Thread(target=self._process_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback for incoming audio data"""
        if self.is_recording:
            self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    def _process_audio(self):
        """Process audio chunks in a separate thread"""
        audio_buffer = []

        while self.is_recording:
            try:
                # Get audio data from queue
                data = self.audio_queue.get(timeout=0.1)

                # Convert to numpy array
                audio_chunk = np.frombuffer(data, dtype=np.float32)
                audio_buffer.extend(audio_chunk)

                # When we have enough data, process it
                if len(audio_buffer) >= self.chunk_size:
                    audio_data = np.array(audio_buffer[:self.chunk_size])
                    audio_buffer = audio_buffer[self.chunk_size:]

                    # Call the callback with the audio data
                    if self.callback:
                        self.callback(audio_data)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing audio: {e}")

    def stop_recording(self):
        """Stop recording audio"""
        if not self.is_recording:
            return

        self.is_recording = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if self.recording_thread:
            self.recording_thread.join(timeout=1.0)

    def save_recording(self, filename: str, audio_data: np.ndarray):
        """
        Save recorded audio to a WAV file

        Args:
            filename: Output filename
            audio_data: Audio data as numpy array
        """
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paFloat32))
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())

    def cleanup(self):
        """Clean up audio resources"""
        self.stop_recording()
        self.audio.terminate()
