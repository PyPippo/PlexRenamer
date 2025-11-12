"""Media file information extraction and metadata handling.

This module provides the MediaInfo class for extracting and managing file
metadata including type classification, size, modification date, and more.
Supports various file types with automatic MIME type detection and fallback
to extension-based classification.

Key Features:
- Automatic file type detection (video, audio, image, document, etc.)
- File size in human-readable format (B, KB, MB, GB, etc.)
- File metadata extraction (size, modification date, extension)
- Unicode icon generation for visual file type representation
- Fallback extension-based detection when MIME type unavailable

Usage:
    media = MediaInfo('Breaking.Bad.S01E01.mkv')
    file_type = media.get_file_type()  # 'Video'
    size = media.get_file_size()  # '2.35 GB'
"""

import os
import math
import mimetypes
from datetime import datetime


class MediaInfo:
    """Extracts and manages media file metadata and properties.

    This class provides a comprehensive interface for accessing file metadata
    including type classification, size information, modification date, and
    visual representation through icons.

    File type detection uses a two-stage approach:
    1. MIME type detection (primary)
    2. Extension-based fallback (secondary)

    Attributes:
        file_path: Full path to the media file
        file_name: Base filename (with extension)
        file_size: File size in bytes
        file_extension: File extension in lowercase
        file_type: Human-readable file type classification
        file_last_modified: DateTime of last modification

    Supported Types: Video, Audio, Image, Text, PDF, Office Document,
    Archive, Executable, Application, Unknown
    """

    def __init__(self, file_path: str):
        """Initialize media info extractor.

        Extracts and caches file metadata immediately upon instantiation.
        Retrieves file name, size, extension, type, and last modified date
        from the file system.

        Args:
            file_path: Full path to the media file to extract information from
        """
        # file attributes
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.file_size = os.path.getsize(file_path)
        self.file_extension = self.get_file_extension()
        self.file_type = self.get_file_type()
        self.file_last_modified = self.get_file_last_modified()

    def get_file_type(self) -> str:
        """Determine the file type based on file extension and MIME type.

        Uses a two-stage detection process:
        1. Primary: MIME type detection via mimetypes module
        2. Fallback: Extension-based detection if MIME type unavailable

        Supports common file types: Video, Audio, Image, Text, PDF, Document,
        Archive, Executable, and Unknown.

        Returns:
            str: Human-readable file type name (e.g., 'Video', 'Image', 'Unknown')
        """
        # First try to get MIME type
        mime_type, _ = mimetypes.guess_type(self.file_path)

        if mime_type:
            # Extract general category from MIME type
            main_type = mime_type.split('/')[0]
            if main_type == 'image':
                return 'Image'
            elif main_type == 'video':
                return 'Video'
            elif main_type == 'audio':
                return 'Audio'
            elif main_type == 'text':
                return 'Text'
            elif main_type == 'application':
                sub_type = mime_type.split('/')[1]
                if 'pdf' in sub_type:
                    return 'PDF'
                elif any(
                    office in sub_type
                    for office in ['word', 'excel', 'powerpoint', 'msword']
                ):
                    return 'Office Document'
                elif 'zip' in sub_type or 'compressed' in sub_type:
                    return 'Archive'
                else:
                    return 'Application'

        # Fallback to extension-based detection
        ext = self.file_extension
        if ext in [
            '.txt',
            '.md',
            '.py',
            '.js',
            '.html',
            '.css',
            '.json',
            '.xml',
            '.csv',
        ]:
            return 'Text'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']:
            return 'Image'
        elif ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
            return 'Video'
        elif ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
            return 'Audio'
        elif ext in ['.pdf']:
            return 'PDF'
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            return 'Archive'
        elif ext in ['.exe', '.msi', '.dmg', '.deb', '.rpm']:
            return 'Executable'
        else:
            return 'Unknown'

    def get_file_type_icon(self) -> str:
        """Get the Unicode icon associated with the file type.

        Returns a visual emoji representation of the file type for use in
        UI displays. Each file type has a corresponding icon.

        Returns:
            str: Unicode emoji character representing the file type
                 (e.g., '🎬' for video, '📄' for text, '?' for unknown)
        """
        file_type = self.get_file_type()
        if file_type == 'Image':
            return '🖼️'
        elif file_type == 'Video':
            return '🎬'
        elif file_type == 'Audio':
            return '🎧'
        elif file_type == 'Text':
            return '📄'
        elif file_type == 'PDF':
            return '📊'
        elif file_type == 'Archive':
            return '📦'
        elif file_type == 'Executable':
            return '💻'
        else:
            return '?'

    def get_file_name(self) -> str:
        """Get the file name without extension.

        Extracts just the base filename without the file extension.

        Returns:
            str: Filename without extension (e.g., 'Breaking Bad S01E01')
        """
        return os.path.splitext(self.file_name)[0]

    def get_file_path(self) -> str:
        """Get the full file path.

        Returns:
            str: Full path to the media file
        """
        return self.file_path

    def get_file_last_modified(self) -> datetime:
        """Get the last modified date of the file.

        Retrieves the file's modification timestamp from the file system
        and converts it to a Python datetime object.

        Returns:
            datetime: Date and time of last modification
        """
        timestamp = os.path.getmtime(self.file_path)
        return datetime.fromtimestamp(timestamp)

    def get_file_extension(self) -> str:
        """Get the file extension from the file path.

        Extracts the extension (e.g., '.mkv', '.mp4') and returns it in
        lowercase for consistent comparison.

        Returns:
            str: File extension including the dot, in lowercase
                 (e.g., '.mkv'), or empty string if no extension
        """
        _, extension = os.path.splitext(self.file_path)
        return extension.lower()

    def get_file_size(self) -> str:
        """Get the file size in human-readable format.

        Converts the file size in bytes to a human-readable format using
        binary prefixes (B, KB, MB, GB, TB, PB, EB, ZB, YB). Returns size
        rounded to 2 decimal places.

        Returns:
            str: File size with unit (e.g., '2.35 GB', '150.5 MB', '0B')
        """
        size_bytes = self.file_size
        if size_bytes == 0:
            return '0B'
        size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f'{s} {size_name[i]}'
