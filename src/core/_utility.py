"""Utility functions for file validation and processing.

This module provides core utility functions for file system operations and
validation related to video file processing. Functions are used throughout
the application for file type checking, format validation, and batch
operations.

Key Functions:
- Video file detection based on MIME type
- Filename normalization format validation
- Year validation against acceptable ranges
- Video extension retrieval
- Folder scanning for video files (non-recursive)
- Duplicate filename detection

Note: All functions are pure utilities with no side effects or UI dependencies.
"""

import os
import mimetypes
import re
from datetime import datetime

from ..models import (
    FileContentType,
    FILE_CONTENT_TYPES,
    FILE_CONTENT_TYPE_SERIES,
    FILE_CONTENT_TYPE_FILM,
    MIN_VALID_YEAR,
    MAX_VALID_YEAR,
    SERIES_NORMALIZED_PATTERN,
    FILM_NORMALIZED_PATTERN,
    VIDEO_EXTENSIONS,
)


def is_video_file(file_path: str) -> bool:
    """Check if a file is a video file based on MIME type.

    Uses Python's mimetypes module to detect if the file has a video MIME
    type. This is a heuristic check based on file extension.

    Args:
        file_path: Path to the file to check

    Returns:
        bool: True if file has a video MIME type, False otherwise
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type is not None and mime_type.startswith('video')


def is_normalized(file_name: str, media_type: FileContentType) -> bool:
    """Check if a filename is already in the normalized format.

    Validates that a filename matches the standardized naming pattern for
    its media type. This helps identify files that are already properly named
    and don't require renaming.

    Expected Formats:
    - Series: "Title (Year) - S##E## [- Remaining].ext"
    - Film: "Title (Year) [- Remaining].ext"

    The check is case-insensitive for series filenames and ignores the file
    extension when matching patterns.

    Args:
        file_name: Name of the file to check (with or without extension)
        media_type: Content type ('series' or 'film') from FileContentType enum

    Returns:
        bool: True if the file matches its media type's normalized pattern,
              False otherwise
    """
    # Remove the file extension for checking
    base_name = re.sub(r'\.[^.]+$', '', file_name)

    if media_type == FILE_CONTENT_TYPE_SERIES:
        # Pattern for series: "title (year) - S##E## - remaining"
        return re.match(SERIES_NORMALIZED_PATTERN, base_name, re.IGNORECASE) is not None

    elif media_type == FILE_CONTENT_TYPE_FILM:
        # Pattern for film: "title (year) - remaining" or "title (year)"
        return re.match(FILM_NORMALIZED_PATTERN, base_name) is not None

    return False


def validate_year(year_str: str) -> bool:
    """Validate if a string represents a valid year.

    Checks that the string contains only digits and falls within the
    acceptable year range (MIN_VALID_YEAR to MAX_VALID_YEAR). Used when
    validating user input or extracted year values.

    Args:
        year_str: String to validate as a year value

    Returns:
        bool: True if string is a valid year in acceptable range, False otherwise
    """
    if not year_str.isdigit():
        return False

    year = int(year_str)
    current_year = MAX_VALID_YEAR

    return MIN_VALID_YEAR <= year <= current_year


def get_video_extensions() -> list[str]:
    """Get list of supported video file extensions.

    Returns all configured video file extensions that the application
    recognizes and processes.

    Returns:
        list[str]: List of video extensions, each starting with a dot
                  (e.g., ['.mkv', '.mp4', '.avi'])
    """
    return VIDEO_EXTENSIONS


def scan_folder_for_videos(folder_path: str) -> list[str]:
    """Scan a folder for video files (flat only, no recursion).

    Searches the specified folder for video files without descending into
    subdirectories. Gracefully handles permission errors and missing paths
    by catching OSError and returning results found before the error.

    Args:
        folder_path: Path to folder to scan for video files

    Returns:
        list[str]: Sorted list of full file paths to video files found.
                  Empty list if folder is empty, inaccessible, or contains no videos
    """
    video_files = []

    try:
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)

            # Skip directories (no recursion)
            if os.path.isdir(item_path):
                continue

            # Check if it's a video file
            if is_video_file(item_path):
                video_files.append(item_path)

    except OSError:
        # Handle permission errors, non-existent paths, etc.
        pass

    return sorted(video_files)


def check_for_duplicate_names(new_names: list[str]) -> dict[str, list[int]]:
    """Check for duplicate names in a list.

    Identifies all filenames that appear more than once in the input list
    and returns their indices. Useful for detecting rename conflicts before
    executing file operations.

    Args:
        new_names: List of proposed new filenames (with or without extensions)

    Returns:
        dict: Mapping of duplicate name to list of indices where it appears.
              Only includes names that appear more than once.
              Example: {'Movie (2023).mkv': [0, 3]} indicates indices 0 and 3
                      both have the same proposed name
    """
    name_indices: dict[str, list[int]] = {}

    for idx, name in enumerate(new_names):
        if name in name_indices:
            name_indices[name].append(idx)
        else:
            name_indices[name] = [idx]

    # Return only duplicates (names that appear more than once)
    return {name: indices for name, indices in name_indices.items() if len(indices) > 1}
