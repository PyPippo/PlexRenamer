"""Core business logic for file analysis and utilities."""

from ._utility import (
    is_video_file,
    is_normalized,
    validate_year,
    get_video_extensions,
    scan_folder_for_videos,
    check_for_duplicate_names,
)
from .file_analyzer import FileAnalyzer as FileAnalyzer

__all__ = [
    'is_video_file',
    'is_normalized',
    'validate_year',
    'get_video_extensions',
    'scan_folder_for_videos',
    'check_for_duplicate_names',
    'FileAnalyzer',
]
