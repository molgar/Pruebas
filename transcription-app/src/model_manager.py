"""
Model Manager for ASR Models
Handles model discovery, downloading, caching, and management
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Callable
import json


class ModelInfo:
    """Information about an ASR model"""

    def __init__(
        self,
        name: str,
        model_id: str,
        languages: List[str],
        size_mb: int,
        description: str,
        category: str = "general"
    ):
        self.name = name
        self.model_id = model_id
        self.languages = languages
        self.size_mb = size_mb
        self.description = description
        self.category = category
        self.is_downloaded = False
        self.local_path = None

    def __repr__(self):
        return f"<ModelInfo {self.name} ({', '.join(self.languages)}) - {self.size_mb}MB>"


class ModelManager:
    """Manages ASR model discovery, downloading, and caching"""

    # Available models catalog
    AVAILABLE_MODELS = {
        'parakeet-tdt-1.1b': ModelInfo(
            name='Parakeet TDT 1.1B',
            model_id='nvidia/parakeet-tdt-1.1b',
            languages=['en', 'es', 'fr', 'multilingual'],
            size_mb=1200,
            description='High-accuracy multilingual model with 1.1B parameters. Best for general use.',
            category='multilingual'
        ),
        'parakeet-tdt-0.6b': ModelInfo(
            name='Parakeet TDT 0.6B',
            model_id='nvidia/parakeet-tdt-0.6b',
            languages=['en', 'es', 'fr', 'multilingual'],
            size_mb=650,
            description='Smaller, faster multilingual model. Good balance of speed and accuracy.',
            category='multilingual'
        ),
        'stt-en-conformer-ctc-large': ModelInfo(
            name='Conformer CTC Large (English)',
            model_id='nvidia/stt_en_conformer_ctc_large',
            languages=['en'],
            size_mb=450,
            description='English-only model with excellent accuracy.',
            category='english'
        ),
        'stt-en-conformer-ctc-medium': ModelInfo(
            name='Conformer CTC Medium (English)',
            model_id='nvidia/stt_en_conformer_ctc_medium',
            languages=['en'],
            size_mb=200,
            description='Balanced English model for good speed and accuracy.',
            category='english'
        ),
        'stt-es-conformer-ctc-large': ModelInfo(
            name='Conformer CTC Large (Spanish)',
            model_id='nvidia/stt_es_conformer_ctc_large',
            languages=['es'],
            size_mb=450,
            description='Spanish-only model with high accuracy.',
            category='spanish'
        ),
        'quartznet-15x5-en': ModelInfo(
            name='QuartzNet 15x5 (English)',
            model_id='nvidia/QuartzNet15x5Base-En',
            languages=['en'],
            size_mb=75,
            description='Very lightweight English model. Fast but lower accuracy.',
            category='english'
        ),
    }

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the model manager

        Args:
            cache_dir: Directory to cache downloaded models (default: user cache)
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Use user cache directory (no admin rights needed)
            if os.name == 'nt':  # Windows
                cache_base = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
            else:
                cache_base = Path.home() / '.cache'

            self.cache_dir = cache_base / 'ai-transcription-studio' / 'models'

        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Model cache metadata file
        self.cache_metadata_file = self.cache_dir / 'models.json'

        # Load cached model information
        self._load_cache_metadata()

        # Update download status for all models
        self._update_download_status()

    def _load_cache_metadata(self):
        """Load cached model metadata from disk"""
        if self.cache_metadata_file.exists():
            try:
                with open(self.cache_metadata_file, 'r') as f:
                    self.cache_metadata = json.load(f)
            except:
                self.cache_metadata = {}
        else:
            self.cache_metadata = {}

    def _save_cache_metadata(self):
        """Save cache metadata to disk"""
        try:
            with open(self.cache_metadata_file, 'w') as f:
                json.dump(self.cache_metadata, f, indent=2)
        except Exception as e:
            print(f"Failed to save cache metadata: {e}")

    def _update_download_status(self):
        """Update download status for all models based on NeMo cache"""
        for model_key, model_info in self.AVAILABLE_MODELS.items():
            # Check if model exists in cache metadata
            if model_info.model_id in self.cache_metadata:
                model_info.is_downloaded = True
                model_info.local_path = self.cache_metadata[model_info.model_id].get('path')
            else:
                model_info.is_downloaded = False
                model_info.local_path = None

    def get_all_models(self) -> Dict[str, ModelInfo]:
        """Get all available models"""
        return self.AVAILABLE_MODELS

    def get_models_by_language(self, language: str) -> List[ModelInfo]:
        """
        Get models that support a specific language

        Args:
            language: Language code (e.g., 'en', 'es', 'fr')

        Returns:
            List of ModelInfo objects
        """
        return [
            model for model in self.AVAILABLE_MODELS.values()
            if language in model.languages or 'multilingual' in model.languages
        ]

    def get_models_by_category(self, category: str) -> List[ModelInfo]:
        """
        Get models in a specific category

        Args:
            category: Category name ('multilingual', 'english', 'spanish', etc.)

        Returns:
            List of ModelInfo objects
        """
        return [
            model for model in self.AVAILABLE_MODELS.values()
            if model.category == category
        ]

    def get_downloaded_models(self) -> List[ModelInfo]:
        """Get list of downloaded models"""
        return [
            model for model in self.AVAILABLE_MODELS.values()
            if model.is_downloaded
        ]

    def get_model_by_id(self, model_id: str) -> Optional[ModelInfo]:
        """
        Get model information by model ID

        Args:
            model_id: Model identifier (e.g., 'nvidia/parakeet-tdt-1.1b')

        Returns:
            ModelInfo object or None
        """
        for model in self.AVAILABLE_MODELS.values():
            if model.model_id == model_id:
                return model
        return None

    def is_model_downloaded(self, model_id: str) -> bool:
        """
        Check if a model is already downloaded

        Args:
            model_id: Model identifier

        Returns:
            True if downloaded, False otherwise
        """
        model = self.get_model_by_id(model_id)
        return model.is_downloaded if model else False

    def mark_model_downloaded(self, model_id: str, local_path: Optional[str] = None):
        """
        Mark a model as downloaded

        Args:
            model_id: Model identifier
            local_path: Optional local path to the model
        """
        model = self.get_model_by_id(model_id)
        if model:
            model.is_downloaded = True
            model.local_path = local_path

            # Update cache metadata
            self.cache_metadata[model_id] = {
                'path': local_path,
                'downloaded': True
            }
            self._save_cache_metadata()

    def get_cache_size(self) -> int:
        """
        Get total size of cached models in MB

        Returns:
            Total cache size in megabytes
        """
        total_size = 0
        try:
            for item in self.cache_dir.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
        except:
            pass

        return total_size // (1024 * 1024)  # Convert to MB

    def clear_cache(self, model_id: Optional[str] = None):
        """
        Clear model cache

        Args:
            model_id: Specific model to remove, or None to clear all
        """
        if model_id:
            # Remove specific model
            model = self.get_model_by_id(model_id)
            if model and model.local_path:
                try:
                    if os.path.exists(model.local_path):
                        import shutil
                        shutil.rmtree(model.local_path)

                    model.is_downloaded = False
                    model.local_path = None

                    if model_id in self.cache_metadata:
                        del self.cache_metadata[model_id]
                        self._save_cache_metadata()
                except Exception as e:
                    print(f"Failed to remove model cache: {e}")
        else:
            # Clear all cache
            try:
                import shutil
                if self.cache_dir.exists():
                    shutil.rmtree(self.cache_dir)
                    self.cache_dir.mkdir(parents=True, exist_ok=True)

                # Reset all models
                for model in self.AVAILABLE_MODELS.values():
                    model.is_downloaded = False
                    model.local_path = None

                self.cache_metadata = {}
                self._save_cache_metadata()
            except Exception as e:
                print(f"Failed to clear cache: {e}")

    def get_recommended_model(
        self,
        language: str = 'en',
        prefer_size: str = 'balanced'  # 'small', 'balanced', 'large'
    ) -> Optional[ModelInfo]:
        """
        Get recommended model based on criteria

        Args:
            language: Target language
            prefer_size: Size preference ('small', 'balanced', 'large')

        Returns:
            Recommended ModelInfo or None
        """
        # Get models for language
        models = self.get_models_by_language(language)

        if not models:
            return None

        # Sort by size
        if prefer_size == 'small':
            # Smallest model
            return min(models, key=lambda m: m.size_mb)
        elif prefer_size == 'large':
            # Largest model (usually best quality)
            return max(models, key=lambda m: m.size_mb)
        else:
            # Balanced - medium size
            models_sorted = sorted(models, key=lambda m: m.size_mb)
            return models_sorted[len(models_sorted) // 2]

    def get_cache_dir(self) -> str:
        """
        Get the cache directory path

        Returns:
            String path to cache directory
        """
        return str(self.cache_dir)

    def get_model_summary(self) -> Dict:
        """
        Get summary of model cache status

        Returns:
            Dictionary with cache statistics
        """
        all_models = list(self.AVAILABLE_MODELS.values())
        downloaded_models = self.get_downloaded_models()

        return {
            'total_models': len(all_models),
            'downloaded': len(downloaded_models),
            'available': len(all_models) - len(downloaded_models),
            'cache_size_mb': self.get_cache_size(),
            'cache_dir': str(self.cache_dir)
        }
