"""
Main Application Window
Modern UI for the transcription application
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QComboBox, QTabWidget,
    QFileDialog, QProgressBar, QGroupBox, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon
import numpy as np
from pathlib import Path

from transcription_engine import TranscriptionEngine
from audio_recorder import AudioRecorder


class ModelLoaderThread(QThread):
    """Thread for loading the model without freezing the UI"""
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(bool)

    def __init__(self, engine, model_name):
        super().__init__()
        self.engine = engine
        self.model_name = model_name

    def run(self):
        success = self.engine.load_model(self.model_name)
        self.finished.emit(success)


class TranscriptionThread(QThread):
    """Thread for transcribing audio files without freezing the UI"""
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, engine, audio_path):
        super().__init__()
        self.engine = engine
        self.audio_path = audio_path

    def run(self):
        try:
            result = self.engine.transcribe_file(self.audio_path)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.engine = None
        self.recorder = None
        self.is_recording = False
        self.live_audio_buffer = []

        self.init_ui()
        self.init_engine()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("AI Transcription Studio - Parakeet TDT")
        self.setMinimumSize(1000, 700)

        # Set modern style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
            QPushButton:pressed {
                background-color: #0a5f62;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QTextEdit {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-radius: 5px;
                padding: 10px;
                font-size: 13px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 13px;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox:hover {
                border: 1px solid #0d7377;
            }
            QTabWidget::pane {
                border: 1px solid #404040;
                border-radius: 5px;
                background-color: #252525;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #e0e0e0;
                padding: 10px 20px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #0d7377;
            }
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 5px;
                text-align: center;
                background-color: #2d2d2d;
            }
            QProgressBar::chunk {
                background-color: #0d7377;
                border-radius: 5px;
            }
            QGroupBox {
                border: 1px solid #404040;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #0d7377;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QStatusBar {
                background-color: #252525;
                color: #e0e0e0;
                border-top: 1px solid #404040;
            }
        """)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("AI Transcription Studio")
        header_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        header.setFont(header_font)
        header.setStyleSheet("color: #0d7377; margin-bottom: 10px;")
        main_layout.addWidget(header)

        # Device info
        self.device_label = QLabel("Device: Initializing...")
        self.device_label.setStyleSheet("color: #888888; font-size: 12px;")
        main_layout.addWidget(self.device_label)

        # Tab widget for different modes
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Live transcription tab
        self.live_tab = self.create_live_tab()
        self.tab_widget.addTab(self.live_tab, "Live Transcription")

        # File transcription tab
        self.file_tab = self.create_file_tab()
        self.tab_widget.addTab(self.file_tab, "File Transcription")

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def create_live_tab(self):
        """Create the live transcription tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Microphone selection
        mic_group = QGroupBox("Microphone Settings")
        mic_layout = QHBoxLayout()

        mic_label = QLabel("Select Microphone:")
        self.mic_combo = QComboBox()
        mic_layout.addWidget(mic_label)
        mic_layout.addWidget(self.mic_combo, 1)

        mic_group.setLayout(mic_layout)
        layout.addWidget(mic_group)

        # Recording controls
        controls_layout = QHBoxLayout()

        self.record_btn = QPushButton("🎙️ Start Recording")
        self.record_btn.clicked.connect(self.toggle_recording)
        self.record_btn.setEnabled(False)

        self.clear_live_btn = QPushButton("Clear Text")
        self.clear_live_btn.clicked.connect(self.clear_live_transcription)

        controls_layout.addWidget(self.record_btn)
        controls_layout.addWidget(self.clear_live_btn)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Transcription output
        output_label = QLabel("Live Transcription:")
        output_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(output_label)

        self.live_text_edit = QTextEdit()
        self.live_text_edit.setPlaceholderText(
            "Transcribed text will appear here in real-time..."
        )
        self.live_text_edit.setMinimumHeight(300)
        layout.addWidget(self.live_text_edit)

        return tab

    def create_file_tab(self):
        """Create the file transcription tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # File selection
        file_group = QGroupBox("Audio File")
        file_layout = QVBoxLayout()

        file_btn_layout = QHBoxLayout()
        self.select_file_btn = QPushButton("📁 Select Audio File")
        self.select_file_btn.clicked.connect(self.select_audio_file)
        self.select_file_btn.setEnabled(False)

        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("color: #888888;")

        file_btn_layout.addWidget(self.select_file_btn)
        file_btn_layout.addWidget(self.file_path_label, 1)
        file_layout.addLayout(file_btn_layout)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Transcribe button
        btn_layout = QHBoxLayout()

        self.transcribe_btn = QPushButton("▶️ Transcribe File")
        self.transcribe_btn.clicked.connect(self.transcribe_file)
        self.transcribe_btn.setEnabled(False)

        self.clear_file_btn = QPushButton("Clear Text")
        self.clear_file_btn.clicked.connect(self.clear_file_transcription)

        btn_layout.addWidget(self.transcribe_btn)
        btn_layout.addWidget(self.clear_file_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # Transcription output
        output_label = QLabel("Transcription Result:")
        output_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(output_label)

        self.file_text_edit = QTextEdit()
        self.file_text_edit.setPlaceholderText(
            "Transcribed text from the audio file will appear here..."
        )
        self.file_text_edit.setMinimumHeight(300)
        layout.addWidget(self.file_text_edit)

        return tab

    def init_engine(self):
        """Initialize the transcription engine"""
        self.status_bar.showMessage("Loading AI model...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        # Create engine
        self.engine = TranscriptionEngine(progress_callback=self.on_engine_progress)

        # Load model in thread
        self.model_loader = ModelLoaderThread(self.engine, "nvidia/parakeet-tdt-1.1b")
        self.model_loader.progress.connect(self.on_engine_progress)
        self.model_loader.finished.connect(self.on_model_loaded)
        self.model_loader.start()

    def on_engine_progress(self, message: str, progress: int):
        """Handle progress updates from the engine"""
        self.status_bar.showMessage(message)

        if progress >= 0:
            if self.progress_bar.maximum() == 0:
                self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(progress)

    def on_model_loaded(self, success: bool):
        """Handle model loading completion"""
        self.progress_bar.setVisible(False)

        if success:
            self.status_bar.showMessage("Model loaded successfully - Ready to transcribe")

            # Update device info
            device_info = self.engine.get_device_info()
            device_text = f"Device: {device_info['device_name']}"
            if 'gpu_memory_total' in device_info:
                device_text += f" ({device_info['gpu_memory_total']:.1f} GB)"
            self.device_label.setText(device_text)

            # Enable controls
            self.record_btn.setEnabled(True)
            self.select_file_btn.setEnabled(True)

            # Initialize audio recorder
            self.init_audio_recorder()
        else:
            self.status_bar.showMessage("Failed to load model")
            QMessageBox.critical(
                self,
                "Error",
                "Failed to load the transcription model. Please check the logs."
            )

    def init_audio_recorder(self):
        """Initialize the audio recorder and populate device list"""
        self.recorder = AudioRecorder(
            sample_rate=16000,
            chunk_duration=3.0,
            callback=self.on_audio_chunk
        )

        # Get available devices
        devices = self.recorder.list_devices()
        for device in devices:
            self.mic_combo.addItem(device['name'], device['index'])

    def toggle_recording(self):
        """Toggle live recording on/off"""
        if not self.is_recording:
            # Start recording
            device_index = self.mic_combo.currentData()
            self.recorder.start_recording(device_index)
            self.is_recording = True
            self.record_btn.setText("⏹️ Stop Recording")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #d32f2f;
                }
                QPushButton:hover {
                    background-color: #f44336;
                }
            """)
            self.status_bar.showMessage("Recording...")
            self.live_audio_buffer = []
        else:
            # Stop recording
            self.recorder.stop_recording()
            self.is_recording = False
            self.record_btn.setText("🎙️ Start Recording")
            self.record_btn.setStyleSheet("")
            self.status_bar.showMessage("Recording stopped")

    def on_audio_chunk(self, audio_data: np.ndarray):
        """Handle incoming audio chunks during live recording"""
        try:
            # Transcribe the audio chunk
            transcription = self.engine.transcribe_audio_data(audio_data, 16000)

            # Append to text edit
            if transcription.strip():
                current_text = self.live_text_edit.toPlainText()
                if current_text:
                    self.live_text_edit.setPlainText(current_text + " " + transcription)
                else:
                    self.live_text_edit.setPlainText(transcription)

                # Auto-scroll to bottom
                cursor = self.live_text_edit.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                self.live_text_edit.setTextCursor(cursor)

        except Exception as e:
            print(f"Error transcribing audio chunk: {e}")

    def select_audio_file(self):
        """Open file dialog to select audio file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.wav *.mp3 *.flac *.ogg *.m4a);;All Files (*)"
        )

        if file_path:
            self.selected_file_path = file_path
            self.file_path_label.setText(Path(file_path).name)
            self.file_path_label.setStyleSheet("color: #0d7377; font-weight: bold;")
            self.transcribe_btn.setEnabled(True)

    def transcribe_file(self):
        """Transcribe the selected audio file"""
        if not hasattr(self, 'selected_file_path'):
            return

        self.transcribe_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_bar.showMessage("Transcribing file...")

        # Start transcription in thread
        self.transcription_thread = TranscriptionThread(
            self.engine,
            self.selected_file_path
        )
        self.transcription_thread.finished.connect(self.on_transcription_finished)
        self.transcription_thread.error.connect(self.on_transcription_error)
        self.transcription_thread.start()

    def on_transcription_finished(self, result: str):
        """Handle completed file transcription"""
        self.progress_bar.setVisible(False)
        self.transcribe_btn.setEnabled(True)
        self.status_bar.showMessage("Transcription complete")
        self.file_text_edit.setPlainText(result)

    def on_transcription_error(self, error: str):
        """Handle transcription error"""
        self.progress_bar.setVisible(False)
        self.transcribe_btn.setEnabled(True)
        self.status_bar.showMessage("Transcription failed")
        QMessageBox.critical(self, "Transcription Error", error)

    def clear_live_transcription(self):
        """Clear the live transcription text"""
        self.live_text_edit.clear()

    def clear_file_transcription(self):
        """Clear the file transcription text"""
        self.file_text_edit.clear()

    def closeEvent(self, event):
        """Handle application closing"""
        if self.recorder:
            self.recorder.cleanup()

        if self.engine:
            self.engine.unload_model()

        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
