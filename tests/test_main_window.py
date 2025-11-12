#!/usr/bin/env python3
"""Test main window functionality (non-interactive)."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")

    try:
        from src.gui.main_window import MainWindow
        from src.gui.status_bar import StatusBar
        from src.gui.file_table import FileTable
        from src.gui import dialogs
        from src.models import FileStatus, FileProcessingData, MessageType

        print("✅ All imports successful")
        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_component_initialization():
    """Test that components can be initialized."""
    print("\nTesting component initialization...")

    try:
        # These shouldn't require QApplication for basic import/definition
        from src.models import FileStatus, FileProcessingData

        # Create a sample FileProcessingData
        data = FileProcessingData(
            path="/test/path.mkv",
            original_name="test.mkv",
            new_name="Test (2023).mkv",
            status=FileStatus.READY,
        )

        assert data.path == "/test/path.mkv"
        print("✅ Component initialization successful")
        return True

    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("MAIN WINDOW TEST SUITE (Non-Interactive)")
    print("=" * 60)

    tests = [test_imports, test_component_initialization]

    all_passed = True
    for test in tests:
        if not test():
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nNote: To test the GUI interactively, run:")
        print("  python src/main.py")
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
