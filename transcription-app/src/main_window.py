"""
Main Application Window
Modern UI for the transcription application with export and multi-language support
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QComboBox, QTabWidget,
    QFileDialog, QProgressBar, QGroupBox, QStatusBar, QMessageBox, QCheckBox,
    QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon
import numpy as np
from pathlib import Path
from typing import List

from transcription_engine import TranscriptionEngine
from audio_recorder import AudioRecorder
from export_handler import TranscriptionSegment, ExportHandler
from model_manager import ModelManager, ModelInfo


class ModelDownloadThread(QThread):
    """Thread for downloading models in the background"""
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(bool, str)  # success, model_id

    def __init__(self, engine, model_id):
        super().__init__()
        self.engine = engine
        self.model_id = model_id

    def run(self):
        try:
            # Load the model (NeMo automatically downloads it)
            self.progress.emit(f"Downloading {self.model_id}...", 0)
            success = self.engine.load_model(self.model_id, 'en')

            if success:
                # Mark as downloaded in model manager
                self.engine.model_manager.mark_model_downloaded(self.model_id)
                self.progress.emit(f"Downloaded {self.model_id}", 100)
                self.finished.emit(True, self.model_id)
            else:
                self.progress.emit(f"Failed to download {self.model_id}", -1)
                self.finished.emit(False, self.model_id)
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}", -1)
            self.finished.emit(False, self.model_id)


class ModelLoaderThread(QThread):
    """Thread for loading the model without freezing the UI"""
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(bool)

    def __init__(self, engine, model_name, language='en'):
        super().__init__()
        self.engine = engine
        self.model_name = model_name
        self.language = language

    def run(self):
        success = self.engine.load_model(self.model_name, self.language)
        self.finished.emit(success)


class TranscriptionThread(QThread):
    """Thread for transcribing audio files with timestamps"""
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(list)  # Now returns list of segments
    error = pyqtSignal(str)

    def __init__(self, engine, audio_path):
        super().__init__()
        self.engine = engine
        self.audio_path = audio_path

    def run(self):
        try:
            # Use the new method that returns segments with timestamps
            segments = self.engine.transcribe_file_with_timestamps(self.audio_path)
            self.finished.emit(segments)
        except Exception as e:
            self.error.emit(str(e))


class ModelSelectorDialog(QDialog):
    """Dialog for selecting and downloading ASR models"""

    def __init__(self, model_manager: ModelManager, engine: TranscriptionEngine, parent=None):
        super().__init__(parent)
        self.model_manager = model_manager
        self.engine = engine
        self.selected_model_id = None
        self.download_thread = None

        self.setWindowTitle("Model Manager")
        self.setMinimumSize(900, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize the model selector UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Header
        header = QLabel("Available ASR Models")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #0d7377; margin-bottom: 10px;")
        layout.addWidget(header)

        # Cache info
        cache_info = self.model_manager.get_model_summary()
        info_text = (
            f"Downloaded: {cache_info['downloaded']}/{cache_info['total_models']} models  |  "
            f"Cache Size: {cache_info['cache_size_mb']} MB  |  "
            f"Cache Location: {cache_info['cache_dir']}"
        )
        cache_label = QLabel(info_text)
        cache_label.setStyleSheet("font-size: 11px; color: #888888; margin-bottom: 10px;")
        layout.addWidget(cache_label)

        # Models table
        self.models_table = QTableWidget()
        self.models_table.setColumnCount(6)
        self.models_table.setHorizontalHeaderLabels([
            "Model Name", "Languages", "Size (MB)", "Category", "Status", "Actions"
        ])

        # Set table properties
        self.models_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.models_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.models_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.models_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.models_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.models_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.models_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.models_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Style the table
        self.models_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #404040;
                gridline-color: #404040;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #0d7377;
            }
            QHeaderView::section {
                background-color: #252525;
                color: #e0e0e0;
                padding: 8px;
                border: 1px solid #404040;
                font-weight: bold;
            }
        """)

        # Populate table
        self.populate_table()

        layout.addWidget(self.models_table)

        # Progress bar for downloads
        self.download_progress = QProgressBar()
        self.download_progress.setVisible(False)
        layout.addWidget(self.download_progress)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(self.status_label)

        # Button box
        button_box = QDialogButtonBox()

        # Clear cache button
        self.clear_cache_btn = QPushButton("🗑️ Clear Cache")
        self.clear_cache_btn.clicked.connect(self.clear_cache)
        button_box.addButton(self.clear_cache_btn, QDialogButtonBox.ButtonRole.ActionRole)

        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_table)
        button_box.addButton(self.refresh_btn, QDialogButtonBox.ButtonRole.ActionRole)

        # Close button
        close_btn = button_box.addButton(QDialogButtonBox.StandardButton.Close)
        close_btn.clicked.connect(self.accept)

        layout.addWidget(button_box)

    def populate_table(self):
        """Populate the models table"""
        all_models = self.model_manager.get_all_models()
        self.models_table.setRowCount(len(all_models))

        row = 0
        for model_key, model_info in all_models.items():
            # Model name
            name_item = QTableWidgetItem(model_info.name)
            self.models_table.setItem(row, 0, name_item)

            # Languages
            languages_str = ", ".join(model_info.languages)
            languages_item = QTableWidgetItem(languages_str)
            self.models_table.setItem(row, 1, languages_item)

            # Size
            size_item = QTableWidgetItem(f"{model_info.size_mb}")
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.models_table.setItem(row, 2, size_item)

            # Category
            category_item = QTableWidgetItem(model_info.category.title())
            self.models_table.setItem(row, 3, category_item)

            # Status
            status_text = "✅ Downloaded" if model_info.is_downloaded else "⬇️ Not Downloaded"
            status_item = QTableWidgetItem(status_text)
            if model_info.is_downloaded:
                status_item.setForeground(Qt.GlobalColor.green)
            self.models_table.setItem(row, 4, status_item)

            # Actions button
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 4, 4, 4)
            action_layout.setSpacing(4)

            if model_info.is_downloaded:
                # Use button
                use_btn = QPushButton("Use")
                use_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0d7377;
                        color: white;
                        padding: 4px 12px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #14a085;
                    }
                """)
                use_btn.clicked.connect(lambda checked, m=model_info: self.use_model(m))
                action_layout.addWidget(use_btn)

                # Delete button
                delete_btn = QPushButton("Delete")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #d32f2f;
                        color: white;
                        padding: 4px 12px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #f44336;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, m=model_info: self.delete_model(m))
                action_layout.addWidget(delete_btn)
            else:
                # Download button
                download_btn = QPushButton("Download")
                download_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1976d2;
                        color: white;
                        padding: 4px 12px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #2196f3;
                    }
                """)
                download_btn.clicked.connect(lambda checked, m=model_info: self.download_model(m))
                action_layout.addWidget(download_btn)

            self.models_table.setCellWidget(row, 5, action_widget)
            row += 1

    def download_model(self, model_info: ModelInfo):
        """Download a model"""
        reply = QMessageBox.question(
            self,
            "Download Model",
            f"Download {model_info.name}?\n\n"
            f"Size: {model_info.size_mb} MB\n"
            f"Languages: {', '.join(model_info.languages)}\n\n"
            f"This may take several minutes depending on your internet connection.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.status_label.setText(f"Downloading {model_info.name}...")
            self.download_progress.setVisible(True)
            self.download_progress.setRange(0, 0)  # Indeterminate

            # Start download in thread
            self.download_thread = ModelDownloadThread(self.engine, model_info.model_id)
            self.download_thread.progress.connect(self.on_download_progress)
            self.download_thread.finished.connect(self.on_download_finished)
            self.download_thread.start()

    def on_download_progress(self, message: str, progress: int):
        """Handle download progress updates"""
        self.status_label.setText(message)
        if progress >= 0:
            if self.download_progress.maximum() == 0:
                self.download_progress.setRange(0, 100)
            self.download_progress.setValue(progress)

    def on_download_finished(self, success: bool, model_id: str):
        """Handle download completion"""
        self.download_progress.setVisible(False)

        if success:
            self.status_label.setText(f"Successfully downloaded {model_id}")
            QMessageBox.information(
                self,
                "Download Complete",
                f"Model {model_id} has been downloaded successfully!\n\n"
                f"You can now use this model for transcription."
            )
            self.refresh_table()
        else:
            self.status_label.setText(f"Failed to download {model_id}")
            QMessageBox.critical(
                self,
                "Download Failed",
                f"Failed to download {model_id}. Please check your internet connection and try again."
            )

    def use_model(self, model_info: ModelInfo):
        """Use a downloaded model"""
        reply = QMessageBox.question(
            self,
            "Switch Model",
            f"Switch to {model_info.name}?\n\n"
            f"The current model will be unloaded and this model will be loaded.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.selected_model_id = model_info.model_id
            self.status_label.setText(f"Switching to {model_info.name}...")
            self.accept()  # Close dialog and return to main window

    def delete_model(self, model_info: ModelInfo):
        """Delete a downloaded model"""
        reply = QMessageBox.question(
            self,
            "Delete Model",
            f"Delete {model_info.name}?\n\n"
            f"This will free up {model_info.size_mb} MB of disk space.\n"
            f"You can re-download it later if needed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.model_manager.clear_cache(model_info.model_id)
            self.status_label.setText(f"Deleted {model_info.name}")
            self.refresh_table()

    def clear_cache(self):
        """Clear all model cache"""
        reply = QMessageBox.question(
            self,
            "Clear All Cache",
            "Clear all downloaded models?\n\n"
            "This will delete all downloaded models and free up disk space.\n"
            "You can re-download them later if needed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            cache_size = self.model_manager.get_cache_size()
            self.model_manager.clear_cache()
            self.status_label.setText(f"Cleared {cache_size} MB of cache")
            self.refresh_table()
            QMessageBox.information(
                self,
                "Cache Cleared",
                f"Successfully cleared {cache_size} MB of model cache."
            )

    def refresh_table(self):
        """Refresh the models table"""
        self.models_table.clearContents()
        self.populate_table()


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.engine = None
        self.recorder = None
        self.is_recording = False
        self.live_audio_buffer = []
        self.current_time = 0.0  # For live transcription timestamps

        # Store segments for export
        self.live_segments: List[TranscriptionSegment] = []
        self.file_segments: List[TranscriptionSegment] = []

        self.init_ui()
        self.init_engine()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("AI Transcription Studio - Parakeet TDT")
        self.setMinimumSize(1200, 800)

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
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #e0e0e0;
                selection-background-color: #0d7377;
            }
            QCheckBox {
                color: #e0e0e0;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid #404040;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #0d7377;
                border-color: #0d7377;
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

        # Settings row
        settings_layout = QHBoxLayout()

        # Device info
        self.device_label = QLabel("Device: Initializing...")
        self.device_label.setStyleSheet("color: #888888; font-size: 12px;")
        settings_layout.addWidget(self.device_label)

        settings_layout.addStretch()

        # Model manager button
        self.model_manager_btn = QPushButton("📦 Model Manager")
        self.model_manager_btn.clicked.connect(self.open_model_manager)
        self.model_manager_btn.setEnabled(False)
        settings_layout.addWidget(self.model_manager_btn)

        # Language selector
        lang_label = QLabel("Language:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Spanish (Español)", "es")
        self.lang_combo.addItem("French (Français)", "fr")
        self.lang_combo.addItem("Multilingual (Auto)", "multilingual")
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        self.lang_combo.setEnabled(False)

        settings_layout.addWidget(lang_label)
        settings_layout.addWidget(self.lang_combo)

        # Speaker diarization toggle
        self.diarization_checkbox = QCheckBox("Enable Speaker Detection")
        self.diarization_checkbox.setEnabled(False)
        self.diarization_checkbox.stateChanged.connect(self.on_diarization_toggled)
        settings_layout.addWidget(self.diarization_checkbox)

        main_layout.addLayout(settings_layout)

        # Tab widget for different modes
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Live transcription tab
        self.live_tab = self.create_live_tab()
        self.tab_widget.addTab(self.live_tab, "🎙️ Live Transcription")

        # File transcription tab
        self.file_tab = self.create_file_tab()
        self.tab_widget.addTab(self.file_tab, "📁 File Transcription")

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

        # Export buttons for live transcription
        export_layout = QHBoxLayout()
        export_label = QLabel("Export:")
        export_layout.addWidget(export_label)

        self.live_export_txt_btn = QPushButton("💾 TXT")
        self.live_export_txt_btn.clicked.connect(lambda: self.export_transcription('live', 'txt'))

        self.live_export_srt_btn = QPushButton("💾 SRT")
        self.live_export_srt_btn.clicked.connect(lambda: self.export_transcription('live', 'srt'))

        self.live_export_vtt_btn = QPushButton("💾 VTT")
        self.live_export_vtt_btn.clicked.connect(lambda: self.export_transcription('live', 'vtt'))

        export_layout.addWidget(self.live_export_txt_btn)
        export_layout.addWidget(self.live_export_srt_btn)
        export_layout.addWidget(self.live_export_vtt_btn)
        export_layout.addStretch()

        layout.addLayout(export_layout)

        # Transcription output
        output_label = QLabel("Live Transcription:")
        output_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(output_label)

        self.live_text_edit = QTextEdit()
        self.live_text_edit.setPlaceholderText(
            "Transcribed text will appear here in real-time...\n\n"
            "Speaker labels will appear if Speaker Detection is enabled."
        )
        self.live_text_edit.setMinimumHeight(350)
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

        # Export buttons for file transcription
        export_layout = QHBoxLayout()
        export_label = QLabel("Export:")
        export_layout.addWidget(export_label)

        self.file_export_txt_btn = QPushButton("💾 TXT")
        self.file_export_txt_btn.clicked.connect(lambda: self.export_transcription('file', 'txt'))

        self.file_export_srt_btn = QPushButton("💾 SRT")
        self.file_export_srt_btn.clicked.connect(lambda: self.export_transcription('file', 'srt'))

        self.file_export_vtt_btn = QPushButton("💾 VTT")
        self.file_export_vtt_btn.clicked.connect(lambda: self.export_transcription('file', 'vtt'))

        self.file_export_json_btn = QPushButton("💾 JSON")
        self.file_export_json_btn.clicked.connect(lambda: self.export_transcription('file', 'json'))

        export_layout.addWidget(self.file_export_txt_btn)
        export_layout.addWidget(self.file_export_srt_btn)
        export_layout.addWidget(self.file_export_vtt_btn)
        export_layout.addWidget(self.file_export_json_btn)
        export_layout.addStretch()

        layout.addLayout(export_layout)

        # Transcription output
        output_label = QLabel("Transcription Result:")
        output_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(output_label)

        self.file_text_edit = QTextEdit()
        self.file_text_edit.setPlaceholderText(
            "Transcribed text from the audio file will appear here...\n\n"
            "Speaker labels and timestamps will be included if available."
        )
        self.file_text_edit.setMinimumHeight(350)
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
        self.model_loader = ModelLoaderThread(self.engine, "nvidia/parakeet-tdt-1.1b", 'en')
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
            self.lang_combo.setEnabled(True)
            self.diarization_checkbox.setEnabled(True)
            self.model_manager_btn.setEnabled(True)

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

    def on_language_changed(self, index):
        """Handle language change"""
        language_code = self.lang_combo.currentData()

        if self.engine and self.engine.is_loaded:
            reply = QMessageBox.question(
                self,
                "Change Language",
                "Changing language will reload the model. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.status_bar.showMessage(f"Switching to {self.lang_combo.currentText()}...")
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)

                # Reload with new language
                self.model_loader = ModelLoaderThread(
                    self.engine,
                    "nvidia/parakeet-tdt-1.1b",
                    language_code
                )
                self.model_loader.finished.connect(self.on_model_loaded)
                self.model_loader.start()

    def on_diarization_toggled(self, state):
        """Handle speaker diarization toggle"""
        if state == Qt.CheckState.Checked.value:
            self.engine.enable_speaker_diarization()
            self.status_bar.showMessage("Speaker detection enabled")
        else:
            self.engine.disable_speaker_diarization()
            self.status_bar.showMessage("Speaker detection disabled")

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
            self.current_time = 0.0
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
            # Transcribe with timestamps
            segment = self.engine.transcribe_audio_data_with_timestamps(
                audio_data,
                16000,
                self.current_time
            )

            # Add to segments list
            if segment.text.strip():
                self.live_segments.append(segment)

                # Display in text edit
                current_text = self.live_text_edit.toPlainText()

                # Format with speaker if available
                if segment.speaker:
                    display_text = f"[{segment.speaker}] {segment.text}"
                else:
                    display_text = segment.text

                if current_text:
                    self.live_text_edit.setPlainText(current_text + " " + display_text)
                else:
                    self.live_text_edit.setPlainText(display_text)

                # Auto-scroll to bottom
                cursor = self.live_text_edit.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                self.live_text_edit.setTextCursor(cursor)

                # Update current time
                self.current_time = segment.end_time

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

    def on_transcription_finished(self, segments: List[TranscriptionSegment]):
        """Handle completed file transcription"""
        self.progress_bar.setVisible(False)
        self.transcribe_btn.setEnabled(True)
        self.status_bar.showMessage("Transcription complete")

        # Store segments
        self.file_segments = segments

        # Display in text edit
        display_text = ""
        for segment in segments:
            timestamp = f"[{self.format_time(segment.start_time)} --> {self.format_time(segment.end_time)}]"
            speaker = f"[{segment.speaker}] " if segment.speaker else ""
            display_text += f"{timestamp} {speaker}{segment.text}\n\n"

        self.file_text_edit.setPlainText(display_text.strip())

    def on_transcription_error(self, error: str):
        """Handle transcription error"""
        self.progress_bar.setVisible(False)
        self.transcribe_btn.setEnabled(True)
        self.status_bar.showMessage("Transcription failed")
        QMessageBox.critical(self, "Transcription Error", error)

    def format_time(self, seconds: float) -> str:
        """Format seconds to MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    def export_transcription(self, source: str, format: str):
        """Export transcription to specified format"""
        # Get segments based on source
        segments = self.live_segments if source == 'live' else self.file_segments

        if not segments:
            QMessageBox.warning(
                self,
                "No Transcription",
                "There is no transcription to export. Please transcribe audio first."
            )
            return

        # File dialog for save location
        extensions = {
            'txt': 'Text Files (*.txt)',
            'srt': 'SRT Subtitles (*.srt)',
            'vtt': 'WebVTT Subtitles (*.vtt)',
            'json': 'JSON Files (*.json)'
        }

        default_name = f"transcription.{format}"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export as {format.upper()}",
            default_name,
            extensions[format]
        )

        if file_path:
            try:
                # Include speakers if diarization is enabled
                include_speakers = self.engine.diarization_enabled

                success = ExportHandler.export(
                    segments,
                    file_path,
                    format,
                    include_speakers
                )

                if success:
                    self.status_bar.showMessage(f"Exported to {Path(file_path).name}")
                    QMessageBox.information(
                        self,
                        "Export Successful",
                        f"Transcription exported successfully to:\n{file_path}"
                    )
                else:
                    raise Exception("Export failed")

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export transcription:\n{str(e)}"
                )

    def clear_live_transcription(self):
        """Clear the live transcription text"""
        self.live_text_edit.clear()
        self.live_segments = []
        self.current_time = 0.0

    def clear_file_transcription(self):
        """Clear the file transcription text"""
        self.file_text_edit.clear()
        self.file_segments = []

    def open_model_manager(self):
        """Open the model manager dialog"""
        if not self.engine or not hasattr(self.engine, 'model_manager'):
            QMessageBox.warning(
                self,
                "Model Manager Not Available",
                "The model manager is not available. Please wait for initialization to complete."
            )
            return

        # Open model selector dialog
        dialog = ModelSelectorDialog(self.engine.model_manager, self.engine, self)
        result = dialog.exec()

        # If a model was selected, switch to it
        if result == QDialog.DialogCode.Accepted and dialog.selected_model_id:
            self.switch_model(dialog.selected_model_id)

    def switch_model(self, model_id: str):
        """Switch to a different model"""
        # Get current language
        current_language = self.lang_combo.currentData()

        # Show loading indicator
        self.status_bar.showMessage(f"Loading model {model_id}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        # Disable controls during loading
        self.record_btn.setEnabled(False)
        self.select_file_btn.setEnabled(False)
        self.lang_combo.setEnabled(False)
        self.diarization_checkbox.setEnabled(False)
        self.model_manager_btn.setEnabled(False)

        # Unload current model
        self.engine.unload_model()

        # Load new model in thread
        self.model_loader = ModelLoaderThread(self.engine, model_id, current_language)
        self.model_loader.progress.connect(self.on_engine_progress)
        self.model_loader.finished.connect(self.on_model_switched)
        self.model_loader.start()

    def on_model_switched(self, success: bool):
        """Handle model switching completion"""
        self.progress_bar.setVisible(False)

        if success:
            self.status_bar.showMessage("Model switched successfully")

            # Re-enable controls
            self.record_btn.setEnabled(True)
            self.select_file_btn.setEnabled(True)
            self.lang_combo.setEnabled(True)
            self.diarization_checkbox.setEnabled(True)
            self.model_manager_btn.setEnabled(True)

            QMessageBox.information(
                self,
                "Model Switched",
                "The model has been switched successfully!\n\nYou can now continue transcribing with the new model."
            )
        else:
            self.status_bar.showMessage("Failed to switch model")
            QMessageBox.critical(
                self,
                "Error",
                "Failed to switch to the selected model. The previous model may still be loaded."
            )

            # Try to re-enable controls
            self.model_manager_btn.setEnabled(True)

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
