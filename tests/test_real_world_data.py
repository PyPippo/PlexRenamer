#!/usr/bin/env python3
"""
Test FileAnalyzer with real-world data from data_set folders
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.file_analyzer import FileAnalyzer
from src.models import FILE_CONTENT_TYPE_SERIES


def test_series_folder(folder_path: Path, series_name: str, user_year: str = "2023"):
    """Test all files in a series folder"""
    print(f"\n{'='*80}")
    print(f"Testing: {series_name}")
    print(f"{'='*80}")

    files = sorted([f for f in os.listdir(folder_path) if f.endswith('.mkv')])

    if not files:
        print(f"⚠️  No .mkv files found in {folder_path}")
        return

    print(f"Found {len(files)} files\n")

    results: dict[str, list[tuple[str, str]]] = {
        'success': [],
        'failed': [],
        'anomalies': [],
    }

    for i, filename in enumerate(files[:5], 1):  # Test first 5 files
        file_path = folder_path / filename

        print(f"\n--- File {i}/{min(5, len(files))} ---")
        print(f"Original: {filename}")

        try:
            # Create analyzer
            analyzer = FileAnalyzer(str(file_path), FILE_CONTENT_TYPE_SERIES)  # type: ignore
            analyzer.actual_title = filename
            analyzer.set_media_year(user_year)

            # Format the name
            result = analyzer.formatter_media_name()

            if result:
                print(f"Formatted: {result}")
                results['success'].append((filename, result))

                # Check for anomalies
                if not any(ep in result.upper() for ep in ['S', 'E', 'X']):
                    results['anomalies'].append((filename, "No episode marker found"))
                    print("⚠️  ANOMALY: No episode marker in result")
                else:
                    print("✅ SUCCESS")
            else:
                print("❌ FAILED: formatter returned None")
                results['failed'].append((filename, "Returned None"))

        except Exception as e:
            print(f"❌ ERROR: {e}")
            results['failed'].append((filename, str(e)))

    # Summary
    print(f"\n{'-'*80}")
    print(f"Summary for {series_name}:")
    print(f"  ✅ Successful: {len(results['success'])}")
    print(f"  ❌ Failed: {len(results['failed'])}")
    print(f"  ⚠️  Anomalies: {len(results['anomalies'])}")

    if results['failed']:
        print(f"\nFailed files:")
        for fname, error in results['failed']:
            print(f"  - {fname}: {error}")

    if results['anomalies']:
        print(f"\nAnomalies detected:")
        for fname, issue in results['anomalies']:
            print(f"  - {fname}: {issue}")

    return results


def main():
    print("=" * 80)
    print("REAL-WORLD DATA TEST SUITE")
    print("=" * 80)

    data_set_path = Path("data_set")

    if not data_set_path.exists():
        print("❌ data_set folder not found!")
        return

    # Test each series
    test_cases = [
        ("Futurama", "1999"),
        ("Babylon 5", "1994"),
        ("Russian Doll", "2019"),
    ]

    all_results = {}

    for series_name, year in test_cases:
        series_path = data_set_path / series_name
        if series_path.exists():
            all_results[series_name] = test_series_folder(
                series_path, series_name, year
            )
        else:
            print(f"\n⚠️  Folder not found: {series_path}")

    # Overall summary
    print(f"\n{'='*80}")
    print("OVERALL SUMMARY")
    print(f"{'='*80}")

    total_success = sum(len(r['success']) for r in all_results.values())
    total_failed = sum(len(r['failed']) for r in all_results.values())
    total_anomalies = sum(len(r['anomalies']) for r in all_results.values())

    print(f"Total files tested: {total_success + total_failed}")
    print(f"  ✅ Successful: {total_success}")
    print(f"  ❌ Failed: {total_failed}")
    print(f"  ⚠️  Anomalies: {total_anomalies}")

    if total_failed == 0 and total_anomalies == 0:
        print("\n🎉 ALL TESTS PASSED PERFECTLY!")
    elif total_failed == 0:
        print("\n⚠️  All tests completed but with some anomalies to review")
    else:
        print("\n❌ Some tests failed - review needed")


if __name__ == "__main__":
    main()
