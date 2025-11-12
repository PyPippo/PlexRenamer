"""Media file information extraction and metadata handling.

This module provides classes for extracting and managing file metadata:
- MediaInfo: Basic file information (type, size, modification date)
- MediaMetadataExtractor: Detailed media metadata (codecs, tracks, etc.)
"""

from .media_info import MediaInfo as MediaInfo
from .media_metadata import MediaMetadataExtractor as MediaMetadataExtractor

__all__ = [
    'MediaInfo',
    'MediaMetadataExtractor',
]
