#!/usr/bin/env python3
"""Test GUI components functionality."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.models import (
    FileStatus,
    FileProcessingData,
    MessageType,
    FILE_CONTENT_TYPE_FILM,
    FILE_CONTENT_TYPE_SERIES,
)
from src.core import FileAnalyzer


def test_file_processing_data():
    """Test FileProcessingData dataclass."""
    print("Testing FileProcessingData...")

    data = FileProcessingData(
        path="/path/to/movie.2023.mkv",
        original_name="movie.2023.mkv",
        new_name="Movie (2023).mkv",
        status=FileStatus.READY,
    )

    assert data.path == "/path/to/movie.2023.mkv"
    assert data.original_name == "movie.2023.mkv"
    assert data.new_name == "Movie (2023).mkv"
    assert data.status == FileStatus.READY
    assert data.analyzer is None
    assert data.error_message is None

    print("✅ FileProcessingData works correctly")


def test_file_status_enum():
    """Test FileStatus enum."""
    print("\nTesting FileStatus enum...")

    assert FileStatus.READY.value == "ready"
    assert FileStatus.NEEDS_YEAR.value == "needs_year"
    assert FileStatus.INVALID.value == "invalid"
    assert FileStatus.ALREADY_NORMALIZED.value == "already_normalized"
    assert FileStatus.DUPLICATE.value == "duplicate"
    assert FileStatus.NOT_VIDEO.value == "not_video"

    print("✅ FileStatus enum works correctly")


def test_message_type_enum():
    """Test MessageType enum."""
    print("\nTesting MessageType enum...")

    assert MessageType.INFO.value == "info"
    assert MessageType.WARNING.value == "warning"
    assert MessageType.ERROR.value == "error"
    assert MessageType.SUCCESS.value == "success"
    assert MessageType.PROCESSING.value == "processing"

    print("✅ MessageType enum works correctly")


def test_file_analyzer_integration():
    """Test FileAnalyzer with FileProcessingData."""
    print("\nTesting FileAnalyzer integration...")

    # Test with a movie file
    file_path = "The.Matrix.1999.1080p.mkv"
    analyzer = FileAnalyzer(file_path, FILE_CONTENT_TYPE_FILM)
    analyzer.actual_title = file_path

    formatted = analyzer.formatter_media_name()
    print(f"  Input:  {file_path}")
    print(f"  Output: {formatted}")

    data = FileProcessingData(
        path=file_path,
        original_name=file_path,
        new_name=formatted,
        status=FileStatus.READY,
        analyzer=analyzer,
    )

    # FileAnalyzer includes "1080p" in the output as remainder
    assert "The Matrix (1999)" in data.new_name
    assert "1080p" in data.new_name
    assert data.analyzer is not None

    # Test with a series file
    series_file = "breaking.bad.s01e01.pilot.mkv"
    series_analyzer = FileAnalyzer(series_file, FILE_CONTENT_TYPE_SERIES)
    series_analyzer.actual_title = series_file
    series_analyzer.set_media_year("2008")

    formatted_series = series_analyzer.formatter_media_name()
    print(f"\n  Input:  {series_file}")
    print(f"  Output: {formatted_series}")

    assert "S01E01" in formatted_series
    assert "2008" in formatted_series

    print("✅ FileAnalyzer integration works correctly")


def test_status_icon_mapping():
    """Test that all status types have corresponding icons."""
    print("\nTesting status icon coverage...")

    try:
        from src.gui.file_table import FileTable

        # Ensure all FileStatus values have icons
        for status in FileStatus:
            icon = FileTable.STATUS_ICONS.get(status)
            assert icon is not None, f"Missing icon for status: {status}"
            print(f"  {status.value:20} → {icon}")

        print("✅ All statuses have icons")
    except ImportError:
        print("⏭️  Skipping (PySide6 not available in this environment)")


def test_duplicate_detection():
    """Test duplicate name detection."""
    print("\nTesting duplicate detection...")

    from src.core import check_for_duplicate_names

    # Test with duplicates
    names = [
        "Movie (2023).mkv",
        "Film (2020).mkv",
        "Movie (2023).mkv",
        "Show (2021).mkv",
    ]
    duplicates = check_for_duplicate_names(names)

    assert "Movie (2023).mkv" in duplicates
    assert duplicates["Movie (2023).mkv"] == [0, 2]

    print(f"  Detected duplicates: {duplicates}")

    # Test without duplicates
    unique_names = ["Movie1 (2023).mkv", "Movie2 (2020).mkv", "Movie3 (2021).mkv"]
    no_duplicates = check_for_duplicate_names(unique_names)

    assert len(no_duplicates) == 0

    print("✅ Duplicate detection works correctly")


def main():
    """Run all tests."""
    print("=" * 60)
    print("GUI COMPONENTS TEST SUITE")
    print("=" * 60)

    try:
        test_file_processing_data()
        test_file_status_enum()
        test_message_type_enum()
        test_file_analyzer_integration()
        test_status_icon_mapping()
        test_duplicate_detection()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
