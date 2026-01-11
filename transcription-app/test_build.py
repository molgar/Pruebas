#!/usr/bin/env python3
"""
Basic build validation test
Tests core functionality without requiring GUI or heavy dependencies
"""

import sys
import os
sys.path.insert(0, 'src')

def test_model_manager():
    """Test ModelManager without NeMo"""
    print("Testing ModelManager...")
    try:
        from model_manager import ModelManager, ModelInfo

        # Initialize manager
        manager = ModelManager()

        # Test getting all models
        models = manager.get_all_models()
        assert len(models) > 0, "No models found"
        print(f"  ✓ Found {len(models)} models in catalog")

        # Test filtering by language
        en_models = manager.get_models_by_language('en')
        print(f"  ✓ Found {len(en_models)} English models")

        # Test model info structure
        first_model = list(models.values())[0]
        assert hasattr(first_model, 'name'), "ModelInfo missing name"
        assert hasattr(first_model, 'model_id'), "ModelInfo missing model_id"
        assert hasattr(first_model, 'languages'), "ModelInfo missing languages"
        print(f"  ✓ ModelInfo structure valid")

        # Test cache directory creation
        cache_dir = manager.get_cache_dir()
        print(f"  ✓ Cache directory: {cache_dir}")

        # Test summary
        summary = manager.get_model_summary()
        assert 'total_models' in summary, "Summary missing total_models"
        assert 'downloaded' in summary, "Summary missing downloaded count"
        print(f"  ✓ Summary: {summary['downloaded']}/{summary['total_models']} models downloaded")

        print("✓ ModelManager tests passed\n")
        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False

def test_export_handler():
    """Test ExportHandler with mock data"""
    print("Testing ExportHandler...")
    try:
        from export_handler import ExportHandler, TranscriptionSegment

        # Create mock segments
        segments = [
            TranscriptionSegment("Hello, how are you?", 0.0, 3.5, "Speaker 1"),
            TranscriptionSegment("I'm doing great, thanks!", 3.5, 6.2, "Speaker 2"),
            TranscriptionSegment("That's wonderful to hear.", 6.2, 9.1, "Speaker 1"),
        ]

        print(f"  ✓ Created {len(segments)} test segments")

        # Test segment properties
        assert segments[0].text == "Hello, how are you?"
        assert segments[0].start_time == 0.0
        assert segments[0].end_time == 3.5
        assert segments[0].speaker == "Speaker 1"
        print(f"  ✓ TranscriptionSegment structure valid")

        # Test export to temp file (TXT)
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            txt_path = f.name

        success = ExportHandler.export(segments, txt_path, 'txt', include_speakers=True)
        assert success, "TXT export failed"

        # Verify file was created
        assert os.path.exists(txt_path), "TXT file not created"
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Speaker 1" in content, "Speaker label missing"
            assert "Hello, how are you?" in content, "Text missing"
        os.unlink(txt_path)
        print(f"  ✓ TXT export works")

        # Test SRT export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False) as f:
            srt_path = f.name

        success = ExportHandler.export(segments, srt_path, 'srt', include_speakers=True)
        assert success, "SRT export failed"

        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "00:00:00,000 --> 00:00:03,500" in content, "Timestamp missing"
        os.unlink(srt_path)
        print(f"  ✓ SRT export works")

        # Test JSON export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = f.name

        success = ExportHandler.export(segments, json_path, 'json', include_speakers=True)
        assert success, "JSON export failed"

        with open(json_path, 'r', encoding='utf-8') as f:
            import json
            data = json.load(f)
            assert 'segments' in data, "JSON missing segments"
            assert len(data['segments']) == 3, "JSON segment count wrong"
        os.unlink(json_path)
        print(f"  ✓ JSON export works")

        print("✓ ExportHandler tests passed\n")
        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    modules = [
        'model_manager',
        'export_handler',
        'audio_recorder',
    ]

    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module} imports successfully")
        except ImportError as e:
            # Expected for modules with heavy dependencies
            if 'pyaudio' in str(e).lower() or 'nemo' in str(e).lower() or 'torch' in str(e).lower():
                print(f"  ⚠ {module} requires external dependencies (expected)")
            else:
                print(f"  ✗ {module} import failed: {e}")
                failed.append(module)

    if failed:
        print(f"✗ Some imports failed unexpectedly: {failed}\n")
        return False
    else:
        print("✓ All module imports successful (or expected dependencies missing)\n")
        return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("AI Transcription Studio - Build Validation")
    print("=" * 60)
    print()

    results = []

    # Test 1: Module imports
    results.append(("Imports", test_imports()))

    # Test 2: ModelManager
    results.append(("ModelManager", test_model_manager()))

    # Test 3: ExportHandler
    results.append(("ExportHandler", test_export_handler()))

    # Summary
    print("=" * 60)
    print("Test Summary:")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20} {status}")

    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ BUILD VALIDATION SUCCESSFUL")
        print("The application structure is valid and core components work correctly.")
        print("\nNote: Full functionality requires installing dependencies:")
        print("  pip install -r requirements.txt")
        return 0
    else:
        print("\n✗ BUILD VALIDATION FAILED")
        print("Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
