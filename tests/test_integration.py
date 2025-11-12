#!/usr/bin/env python3
"""Integration test - Test complete workflow with real files."""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.models import (
    FileStatus,
    FileProcessingData,
    FILE_CONTENT_TYPE_FILM,
    FILE_CONTENT_TYPE_SERIES,
)
from src.core import (
    FileAnalyzer,
    is_video_file,
    is_normalized,
    scan_folder_for_videos,
    check_for_duplicate_names,
)


def test_movie_processing():
    """Test movie file processing."""
    print("\n" + "=" * 60)
    print("TEST: Movie Processing")
    print("=" * 60)

    # Create a mock movie file path
    test_files = [
        "The.Matrix.1999.1080p.BluRay.mkv",
        "Inception.2010.720p.mkv",
        "Interstellar.2014.1080p.mkv",
        # Test case for bug fix: year already in parentheses
        "trial title (2011) remainder.mkv",
    ]

    expected_outputs = [
        "The Matrix (1999) - 1080p BluRay.mkv",
        "Inception (2010) - 720p.mkv",
        "Interstellar (2014) - 1080p.mkv",
        "trial title (2011) - remainder.mkv",  # Should NOT become ((2011) -)
    ]

    file_data = []

    for filename, expected in zip(test_files, expected_outputs):
        # Simulate processing
        try:
            analyzer = FileAnalyzer(filename, FILE_CONTENT_TYPE_FILM)
            analyzer.actual_title = filename
            formatted = analyzer.formatter_media_name()

            print(f"\nOriginal: {filename}")
            print(f"Formatted: {formatted}")
            print(f"Expected: {expected}")

            # Verify output matches expected
            if formatted != expected:
                print(f"❌ Output mismatch!")
                print(f"  Got:      {formatted}")
                print(f"  Expected: {expected}")
                return False

            # Check if normalized
            if is_normalized(formatted, FILE_CONTENT_TYPE_FILM):
                print("✅ Correctly normalized")
            else:
                print("❌ Not normalized correctly")
                return False

            file_data.append(
                FileProcessingData(
                    path=filename,
                    original_name=filename,
                    new_name=formatted,
                    status=FileStatus.READY,
                    analyzer=analyzer,
                )
            )

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            return False

    # Check for duplicates
    new_names = [item.new_name for item in file_data]
    duplicates = check_for_duplicate_names(new_names)

    if duplicates:
        print(f"\n❌ Duplicates detected: {duplicates}")
        return False
    else:
        print("\n✅ No duplicates detected")

    print("\n✅ Movie processing test passed")
    return True


def test_series_processing():
    """Test series file processing."""
    print("\n" + "=" * 60)
    print("TEST: Series Processing")
    print("=" * 60)

    # Create mock series file paths
    test_files = [
        "breaking.bad.s01e01.pilot.mkv",
        "breaking.bad.s01e02.cats.in.the.bag.mkv",
        "breaking.bad.s01e03.and.the.bags.in.the.river.mkv",
    ]

    file_data = []

    for filename in test_files:
        # Simulate processing
        try:
            analyzer = FileAnalyzer(filename, FILE_CONTENT_TYPE_SERIES)
            analyzer.actual_title = filename
            analyzer.set_media_year("2008")
            formatted = analyzer.formatter_media_name()

            print(f"\nOriginal: {filename}")
            print(f"Formatted: {formatted}")

            # Check if normalized
            if is_normalized(formatted, FILE_CONTENT_TYPE_SERIES):
                print("✅ Correctly normalized")
            else:
                print("❌ Not normalized correctly")
                return False

            file_data.append(
                FileProcessingData(
                    path=filename,
                    original_name=filename,
                    new_name=formatted,
                    status=FileStatus.READY,
                    analyzer=analyzer,
                )
            )

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            return False

    # Check for duplicates
    new_names = [item.new_name for item in file_data]
    duplicates = check_for_duplicate_names(new_names)

    if duplicates:
        print(f"\n❌ Duplicates detected: {duplicates}")
        return False
    else:
        print("\n✅ No duplicates detected")

    print("\n✅ Series processing test passed")
    return True


def test_folder_scanning():
    """Test folder scanning functionality."""
    print("\n" + "=" * 60)
    print("TEST: Folder Scanning")
    print("=" * 60)

    data_set_path = Path("data_set")

    if not data_set_path.exists():
        print("⏭️  Skipping - data_set folder not found")
        return True

    # Test scanning different series folders
    series_folders = [
        "Futurama",
        "Babylon 5",
        "Russian Doll",
    ]

    for series_name in series_folders:
        series_path = data_set_path / series_name

        if not series_path.exists():
            print(f"\n⏭️  Skipping {series_name} - folder not found")
            continue

        print(f"\n--- Testing {series_name} ---")
        video_files = scan_folder_for_videos(str(series_path))

        print(f"Found {len(video_files)} video files")

        if len(video_files) > 0:
            # Show first 3 files
            for i, file_path in enumerate(video_files[:3]):
                filename = os.path.basename(file_path)
                print(f"  {i + 1}. {filename}")

            # Verify all are video files
            all_videos = all(is_video_file(f) for f in video_files)
            if all_videos:
                print("✅ All files are valid video files")
            else:
                print("❌ Some files are not video files")
                return False
        else:
            print("⚠️  No video files found")

    print("\n✅ Folder scanning test passed")
    return True


def test_duplicate_detection():
    """Test duplicate name detection."""
    print("\n" + "=" * 60)
    print("TEST: Duplicate Detection")
    print("=" * 60)

    # Test case 1: No duplicates
    names1 = ["Movie1 (2020).mkv", "Movie2 (2021).mkv", "Movie3 (2022).mkv"]
    duplicates1 = check_for_duplicate_names(names1)

    print("\nTest Case 1: No duplicates")
    print(f"Names: {names1}")
    print(f"Duplicates: {duplicates1}")

    if len(duplicates1) == 0:
        print("✅ Correctly detected no duplicates")
    else:
        print("❌ False positive - detected duplicates where none exist")
        return False

    # Test case 2: With duplicates
    names2 = ["Movie (2020).mkv", "Film (2021).mkv", "Movie (2020).mkv"]
    duplicates2 = check_for_duplicate_names(names2)

    print("\nTest Case 2: With duplicates")
    print(f"Names: {names2}")
    print(f"Duplicates: {duplicates2}")

    if "Movie (2020).mkv" in duplicates2:
        print("✅ Correctly detected duplicates")
    else:
        print("❌ Failed to detect duplicates")
        return False

    print("\n✅ Duplicate detection test passed")
    return True


def test_invalid_files():
    """Test handling of invalid files."""
    print("\n" + "=" * 60)
    print("TEST: Invalid File Handling")
    print("=" * 60)

    # Test with series file that has no episode number
    invalid_series = "random.video.file.mkv"

    print(f"\nTesting: {invalid_series}")

    try:
        analyzer = FileAnalyzer(invalid_series, FILE_CONTENT_TYPE_SERIES)
        analyzer.actual_title = invalid_series
        analyzer.set_media_year("2020")
        formatted = analyzer.formatter_media_name()
        print(f"❌ Should have raised ValueError, got: {formatted}")
        return False
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")

    print("\n✅ Invalid file handling test passed")
    return True


def test_year_extraction():
    """Test year extraction from various filename patterns."""
    print("\n" + "=" * 60)
    print("TEST: Year Extraction")
    print("=" * 60)

    test_cases = [
        ("Movie.2001.1080p.mkv", 2001),
        ("Film.Name.1999.BluRay.mkv", 1999),
        ("Show.2023.S01E01.mkv", 2023),
        ("Ancient.Film.1920.mkv", 1920),
    ]

    for filename, expected_year in test_cases:
        analyzer = FileAnalyzer(filename, FILE_CONTENT_TYPE_FILM)
        analyzer.actual_title = filename
        year, pos = analyzer._extract_year(filename)

        print(f"\nFile: {filename}")
        print(f"Expected: {expected_year}, Got: {year}")

        if year == expected_year:
            print("✅ Correct")
        else:
            print("❌ Incorrect")
            return False

    print("\n✅ Year extraction test passed")
    return True


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("INTEGRATION TEST SUITE")
    print("=" * 60)

    tests = [
        test_movie_processing,
        test_series_processing,
        test_folder_scanning,
        test_duplicate_detection,
        test_invalid_files,
        test_year_extraction,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ Test {test.__name__} crashed: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")

    if failed == 0:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
