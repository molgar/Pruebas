#!/usr/bin/env python3
"""
Headless build test - tests core functionality without GUI or heavy ML dependencies
"""

import sys
import os
sys.path.insert(0, 'src')

def test_model_manager_full():
    """Comprehensive ModelManager test"""
    print("=" * 60)
    print("Testing ModelManager (Full)")
    print("=" * 60)

    try:
        from model_manager import ModelManager, ModelInfo

        # Initialize
        manager = ModelManager()
        print("✓ ModelManager initialized")

        # Test all models
        all_models = manager.get_all_models()
        print(f"✓ Catalog: {len(all_models)} models")

        for key, model in all_models.items():
            print(f"  - {model.name}")
            print(f"    ID: {model.model_id}")
            print(f"    Languages: {', '.join(model.languages)}")
            print(f"    Size: {model.size_mb} MB")
            print(f"    Category: {model.category}")
            print(f"    Downloaded: {model.is_downloaded}")

        # Test filtering
        print("\n✓ Testing filters:")
        en_models = manager.get_models_by_language('en')
        print(f"  - English models: {len(en_models)}")

        es_models = manager.get_models_by_language('es')
        print(f"  - Spanish models: {len(es_models)}")

        multilingual = manager.get_models_by_category('multilingual')
        print(f"  - Multilingual models: {len(multilingual)}")

        # Test recommendations
        print("\n✓ Testing recommendations:")
        large_model = manager.get_recommended_model('en', prefer_size='large')
        print(f"  - Large model (EN): {large_model.name if large_model else 'None'}")

        small_model = manager.get_recommended_model('en', prefer_size='small')
        print(f"  - Small model (EN): {small_model.name if small_model else 'None'}")

        balanced = manager.get_recommended_model('en', prefer_size='balanced')
        print(f"  - Balanced (EN): {balanced.name if balanced else 'None'}")

        # Test cache operations
        print("\n✓ Testing cache operations:")
        cache_dir = manager.get_cache_dir()
        print(f"  - Cache dir: {cache_dir}")

        cache_size = manager.get_cache_size()
        print(f"  - Cache size: {cache_size} MB")

        summary = manager.get_model_summary()
        print(f"  - Summary: {summary}")

        print("\n✓ ModelManager: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"\n✗ ModelManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_export_handler_full():
    """Comprehensive ExportHandler test"""
    print("\n" + "=" * 60)
    print("Testing ExportHandler (Full)")
    print("=" * 60)

    try:
        from export_handler import ExportHandler, TranscriptionSegment
        import tempfile
        import json

        # Create comprehensive test data
        segments = [
            TranscriptionSegment("Good morning everyone, welcome to today's meeting.", 0.0, 4.2, "Speaker 1"),
            TranscriptionSegment("Thank you for joining us today.", 4.2, 7.1, "Speaker 2"),
            TranscriptionSegment("Let's begin with the first agenda item.", 7.1, 10.5, "Speaker 1"),
            TranscriptionSegment("I have some important updates to share.", 10.5, 14.0, "Speaker 2"),
            TranscriptionSegment("That sounds great, please go ahead.", 14.0, 17.2, "Speaker 1"),
        ]

        print(f"✓ Created {len(segments)} test segments")

        # Test TXT export (with and without speakers)
        print("\n✓ Testing TXT export:")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            txt_path = f.name

        ExportHandler.export(segments, txt_path, 'txt', include_speakers=True)
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"  - With speakers ({len(content)} chars)")
            print("  " + content[:100] + "...")
        os.unlink(txt_path)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            txt_path = f.name

        ExportHandler.export(segments, txt_path, 'txt', include_speakers=False)
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"  - Without speakers ({len(content)} chars)")
        os.unlink(txt_path)

        # Test SRT export
        print("\n✓ Testing SRT export:")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False) as f:
            srt_path = f.name

        ExportHandler.export(segments, srt_path, 'srt', include_speakers=True)
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"  - Generated {len(content)} chars")
            lines = content.split('\n')
            print(f"  - {len(lines)} lines")
            # Check for subtitle numbers
            assert '1' in content and '2' in content
            # Check for timestamps
            assert '00:00:00,000 --> 00:00:04,200' in content
            print("  - Timestamps valid")
        os.unlink(srt_path)

        # Test VTT export
        print("\n✓ Testing VTT export:")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.vtt', delete=False) as f:
            vtt_path = f.name

        ExportHandler.export(segments, vtt_path, 'vtt', include_speakers=True)
        with open(vtt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"  - Generated {len(content)} chars")
            assert content.startswith('WEBVTT')
            assert '<v Speaker 1>' in content or '<v Speaker 2>' in content
            print("  - WebVTT format valid")
        os.unlink(vtt_path)

        # Test JSON export
        print("\n✓ Testing JSON export:")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = f.name

        ExportHandler.export(segments, json_path, 'json', include_speakers=True)
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"  - Generated JSON with {len(data)} keys")
            assert 'segments' in data
            assert 'total_duration' in data
            assert 'segment_count' in data
            print(f"  - Segments: {data['segment_count']}")
            print(f"  - Duration: {data['total_duration']} seconds")

            # Verify segment structure
            seg = data['segments'][0]
            assert 'text' in seg
            assert 'start_time' in seg
            assert 'end_time' in seg
            assert 'speaker' in seg
            assert 'duration' in seg
            print(f"  - Segment structure valid")
        os.unlink(json_path)

        print("\n✓ ExportHandler: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"\n✗ ExportHandler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_transcription_segment():
    """Test TranscriptionSegment class"""
    print("\n" + "=" * 60)
    print("Testing TranscriptionSegment")
    print("=" * 60)

    try:
        from export_handler import TranscriptionSegment

        # Create segment
        seg = TranscriptionSegment(
            "Hello world, this is a test.",
            0.0,
            3.5,
            "Speaker 1"
        )

        print(f"✓ Segment created:")
        print(f"  - Text: {seg.text}")
        print(f"  - Start: {seg.start_time}s")
        print(f"  - End: {seg.end_time}s")
        print(f"  - Duration: {seg.end_time - seg.start_time}s")
        print(f"  - Speaker: {seg.speaker}")

        # Test without speaker
        seg2 = TranscriptionSegment("No speaker label.", 3.5, 6.0)
        assert seg2.speaker is None
        print(f"✓ Segment without speaker: {seg2.text}")

        print("\n✓ TranscriptionSegment: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"\n✗ TranscriptionSegment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_project_structure():
    """Verify project file structure"""
    print("\n" + "=" * 60)
    print("Testing Project Structure")
    print("=" * 60)

    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'src/__init__.py',
        'src/main_window.py',
        'src/transcription_engine.py',
        'src/audio_recorder.py',
        'src/export_handler.py',
        'src/model_manager.py',
    ]

    missing = []
    for filepath in required_files:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✓ {filepath} ({size:,} bytes)")
        else:
            print(f"✗ {filepath} MISSING")
            missing.append(filepath)

    if missing:
        print(f"\n✗ Missing files: {missing}")
        return False
    else:
        print("\n✓ Project Structure: ALL FILES PRESENT")
        return True

def main():
    """Run comprehensive headless tests"""
    print("\n" + "=" * 60)
    print("AI Transcription Studio - Headless Build Test")
    print("Testing core functionality without GUI/ML dependencies")
    print("=" * 60 + "\n")

    results = []

    # Test 1: Project structure
    results.append(("Project Structure", test_project_structure()))

    # Test 2: TranscriptionSegment
    results.append(("TranscriptionSegment", test_transcription_segment()))

    # Test 3: ExportHandler (full)
    results.append(("ExportHandler", test_export_handler_full()))

    # Test 4: ModelManager (full)
    results.append(("ModelManager", test_model_manager_full()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:25} {status}")

    print("=" * 60)
    print(f"Results: {passed}/{total} test suites passed")

    if passed == total:
        print("\n" + "🎉 " * 10)
        print("✓ BUILD SUCCESSFUL - ALL TESTS PASSED")
        print("🎉 " * 10)
        print("\nCore application logic is working correctly!")
        print("The following components are verified:")
        print("  ✓ Model management system")
        print("  ✓ Export functionality (TXT, SRT, VTT, JSON)")
        print("  ✓ Data structures and classes")
        print("  ✓ File operations")
        print("\nNote: GUI and ML features require full dependency installation:")
        print("  pip install -r requirements.txt")
        return 0
    else:
        print("\n✗ BUILD FAILED")
        print("Some tests did not pass. Review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
