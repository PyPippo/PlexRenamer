"""File analyzer for parsing and formatting media filenames.

This module provides the FileAnalyzer class which handles extracting and
formatting media filenames according to standardized patterns. It supports
both films and TV series with automatic year and episode extraction.

Key Features:
- Extract year information from filenames with validation
- Extract and normalize episode information (S##E## format)
- Format filenames according to standardized patterns
- Support for both film and series content types
- Smart cleaning of formatting artifacts and separators

Usage:
    analyzer = FileAnalyzer('Breaking.Bad.S01E01.mkv', 'series')
    formatted = analyzer.formatter_media_name()
    # Returns: 'Breaking Bad (YEAR_NEEDED) - S01E01.mkv'

Note: Year and episode information can be extracted automatically or set
manually via setter methods when user input is required.
"""

import os
import re
from datetime import datetime

from ..models import (
    FileContentType,
    FILE_CONTENT_TYPES,
    FILE_CONTENT_TYPE_SERIES,
    FILE_CONTENT_TYPE_FILM,
    MIN_VALID_YEAR,
    MAX_VALID_YEAR,
    DEFAULT_YEAR_PLACEHOLDER,
    DEFAULT_YEAR_POS_PLACEHOLDER,
    DEFAULT_EPISODE_PLACEHOLDER,
    FILENAME_SEPARATORS,
    POTENTIAL_ARTIFACTS,
    SEPARATOR_REPLACEMENTS,
    EPISODE_PATTERN_SE,
    EPISODE_PATTERN_X,
    EPISODE_FORMAT,
    YEAR_PATTERN,
    FILM_FORMAT_WITH_REMAINDER,
    FILM_FORMAT_NO_REMAINDER,
    SERIES_FORMAT_FULL,
)


class FileAnalyzer:
    """Analyzes and formats media filenames according to standardized patterns.

    Supports both films and TV series with automatic year and episode extraction.
    """

    def __init__(self, file_path: str, media_type: FileContentType):
        """Initialize file analyzer.

        Sets up the analyzer with a file path and media type. Extracts and
        stores the file extension, initializes media attributes with default
        placeholders that can be updated via setter methods.

        Args:
            file_path: Full path to the media file to analyze
            media_type: Type of content ('film' or 'series'), from FileContentType enum
        """
        # file attributes
        self.file_path = file_path
        self.file_extension = self._get_file_extension()
        # media attributes
        self.media_year: str = DEFAULT_YEAR_PLACEHOLDER
        self.media_year_pos: int = DEFAULT_YEAR_POS_PLACEHOLDER
        self.media_episode: str = DEFAULT_EPISODE_PLACEHOLDER
        self.media_type: FileContentType = media_type
        self.actual_title: str = os.path.basename(file_path)

    # =========================================================================
    # PRIVATE METHODS - Internal helpers
    # =========================================================================

    def _get_file_extension(self) -> str:
        """Get the file extension from the file path.

        Extracts the extension (e.g., '.mkv', '.mp4') from the file path.
        Returns the extension in lowercase.

        Returns:
            str: File extension including the dot (e.g., '.mkv'), or empty string
                if no extension found
        """
        _, extension = os.path.splitext(self.file_path)
        return extension.lower()

    def _extract_year(self, name: str) -> tuple[None, None] | tuple[int, int]:
        """Extract the first valid year from a string.

        Searches for the first valid year in the input string using a year
        pattern regex. Years must fall within the valid range (MIN_VALID_YEAR
        to MAX_VALID_YEAR) to be considered valid. Returns both the year and
        its position in the string for further processing.

        Priority: Returns the leftmost (first) valid year found.

        Args:
            name: The filename or string to search for year information

        Returns:
            tuple: (year, position) if found and valid:
                - year: Extracted year as integer (e.g., 2008)
                - position: Start position of year in the string
            Or (None, None) if no valid year found
        """
        if not name:
            return None, None

        # Current year for the maximum range
        current_year = MAX_VALID_YEAR

        # Find all matches in the string
        matches = re.finditer(YEAR_PATTERN, name)

        # Check if matches is not None and iterate safely
        if matches:
            # Find the first valid (leftmost) year
            for match in matches:
                year = int(match.group())

                # Check if the year is in the valid range (using MIN_VALID_YEAR constant)
                if MIN_VALID_YEAR <= year <= current_year:
                    return year, match.start()

        return None, None

    def _extract_episode(
        self, name: str
    ) -> tuple[str, int, int] | tuple[None, None, None]:
        """Extract season and episode information from a string.

        Searches for and normalizes season/episode patterns to S##E## format.
        Supports multiple input formats and always returns normalized output.

        Supported Input Formats:
        - S01E01 or s01e01 (standard format with uppercase S and E)
        - 1x01 or 3x9 (alternative format with 'x' separator)
        - Both are normalized to S##E## format with zero-padding

        Search Priority:
        1. First searches for S##E## format
        2. If not found, searches for N×N format
        3. Returns None if neither format found

        Args:
            name: The filename or string to search for episode information

        Returns:
            tuple: (normalized_episode_str, position, original_length) if found:
                - normalized_episode_str: Always in S##E## format with zero-padding
                  (e.g., 'S01E01', 'S03E09')
                - position: Start position of the original match in the string
                - original_length: Length of the original matched string (for slicing)
            Or (None, None, None) if no valid episode format found
        """
        if not name:
            return None, None, None

        # Search for SxxExx format first
        match_se = re.search(EPISODE_PATTERN_SE, name)
        if match_se:
            season = int(match_se.group(1))
            episode = int(match_se.group(2))
            # Normalize to S##E## format with zero-padding
            normalized = EPISODE_FORMAT.format(season, episode)
            original_length = len(match_se.group())
            return normalized, match_se.start(), original_length

        # Otherwise look for NxN format
        match_x = re.search(EPISODE_PATTERN_X, name)
        if match_x:
            season = int(match_x.group(1))
            episode = int(match_x.group(2))
            # Normalize to S##E## format with zero-padding
            normalized = EPISODE_FORMAT.format(season, episode)
            original_length = len(match_x.group())
            return normalized, match_x.start(), original_length

        return None, None, None

    # =========================================================================
    # PUBLIC SETTERS - External configuration
    # =========================================================================

    def set_media_type(self, media_type: FileContentType) -> None:
        """Set media type.

        Updates the media type classification for this analyzer. Used when
        switching between film and series content types.

        Args:
            media_type: Target media type ('film' or 'series')
        """
        self.media_type = media_type

    def set_media_year(self, year: str) -> None:
        """Set the media year.

        Updates the media year value. Used when the year is provided by the
        user or when overriding auto-detected year.

        Args:
            year: Year string to set (e.g., '2008')
        """
        self.media_year = year

    def set_media_year_pos(self, year_pos: int) -> None:
        """Set the media year position.

        Updates the position of the year in the filename. Primarily used
        for internal state tracking during complex parsing scenarios.

        Args:
            year_pos: Position (index) of year in the filename string
        """
        self.media_year_pos = year_pos

    def set_media_episode(self, episode: str) -> None:
        """Set the media episode.

        Updates the episode information. Used when overriding auto-detected
        episode or when manually specifying the season/episode number.

        Args:
            episode: Episode string in S##E## format (e.g., 'S01E01')
        """
        self.media_episode = episode

    # =========================================================================
    # FORMATTER CORE METHODS
    # =========================================================================

    def formatter_media_name(self) -> str:
        """Format the file name according to media type and standardized patterns.

        Main formatter method that processes filenames and applies standardized
        naming conventions. Automatically extracts year and episode information,
        applies smart cleaning to remove artifacts, and formats the output.

        Processing Steps:
        1. Remove file extension from filename
        2. Extract year and validate it's in acceptable range
        3. Extract episode (for series only)
        4. Apply format-specific processing (film vs. series)
        5. Clean artifacts and normalize separators
        6. Generate formatted filename with extension

        Film Formatting:
        - Format: 'Title (Year) [- Remainder].ext'
        - Year is required or uses media_year placeholder
        - Remainder (after year in original) is optional

        Series Formatting:
        - Format: 'Title (Year) - S##E## [- Remainder].ext'
        - Episode information is extracted and normalized to S##E## format
        - Year is required or uses media_year placeholder
        - Remainder (after episode) is optional

        Smart Cleaning:
        - Removes parentheses artifacts from year extraction
        - Handles malformed inputs gracefully
        - Normalizes whitespace and special separators
        - Removes leading/trailing artifacts from extracted parts

        Returns:
            str: Formatted filename with file extension

        Raises:
            ValueError: If episode not found in series filename or unsupported media type
        """
        # Remove extension
        base_name = os.path.splitext(self.actual_title)[0]

        # Extract year and position from base_name (without extension)
        year, pos_year = self._extract_year(base_name)

        # =====================================================================
        # FILM FORMATTING
        # =====================================================================
        if self.media_type == FILE_CONTENT_TYPE_FILM:
            if year is not None:
                assert pos_year is not None

                # Extract raw title and remainder around the year
                raw_title = base_name[:pos_year]
                raw_remainder = base_name[pos_year + 4 :]

                # Smart cleaning: remove parentheses artifacts from year extraction
                # This handles:
                # - "title (year)" -> removes trailing "(" from title, leading ")" from remainder
                # - "title (year" -> removes trailing "(" from title (malformed but flexible)
                # - "title year)" -> removes leading ")" from remainder (malformed but flexible)
                # - "title year" -> no change (normal case)
                title = raw_title.strip(POTENTIAL_ARTIFACTS)
                remainder = raw_remainder.strip(POTENTIAL_ARTIFACTS)

                # Replace separators
                clean_title = title
                clean_remainder = remainder
                for old_sep, new_sep in SEPARATOR_REPLACEMENTS.items():
                    clean_title = clean_title.replace(old_sep, new_sep)
                    clean_remainder = clean_remainder.replace(old_sep, new_sep)

                # Return formatted name based on whether there's a remainder
                if (
                    clean_remainder.strip()
                ):  # Only add dash if there's content after year
                    return FILM_FORMAT_WITH_REMAINDER.format(
                        title=clean_title,
                        year=year,
                        remainder=clean_remainder,
                        ext=self.file_extension,
                    )
                else:
                    return FILM_FORMAT_NO_REMAINDER.format(
                        title=clean_title, year=year, ext=self.file_extension
                    )
            else:
                # No year found - Ask user, for now use media_year placeholder
                title = base_name.strip(FILENAME_SEPARATORS)
                clean_title = title
                for old_sep, new_sep in SEPARATOR_REPLACEMENTS.items():
                    clean_title = clean_title.replace(old_sep, new_sep)
                return FILM_FORMAT_NO_REMAINDER.format(
                    title=clean_title, year=self.media_year, ext=self.file_extension
                )

        # =====================================================================
        # SERIES FORMATTING
        # =====================================================================
        elif self.media_type == FILE_CONTENT_TYPE_SERIES:
            episode, pos_episode, original_len = self._extract_episode(base_name)

            # Needs better handling - if title is empty then discard
            # and show notification in status bar
            if episode is None:
                raise ValueError('No episode found in the title')

            assert pos_episode is not None
            assert original_len is not None

            # Extract raw title (before episode) and remainder (after episode)
            raw_title = base_name[:pos_episode]
            raw_remainder = base_name[pos_episode + original_len :]

            # --- CASE 1: Year found in title ---
            if year is not None:
                assert pos_year is not None

                # Check if year comes BEFORE episode (correct position)
                if pos_year < pos_episode:
                    # Extract title without year
                    raw_title_without_year = base_name[:pos_year]

                    # ✨ CRITICAL FIX: Smart cleaning for series
                    # Apply POTENTIAL_ARTIFACTS cleaning SYMMETRICALLY like films
                    # This fixes the double parenthesis bug: "((2025)" -> "(2025)"
                    #
                    # Split around year position:
                    # - Part before year gets artifacts stripped from the RIGHT
                    # - Part after year (remainder) gets artifacts stripped from LEFT
                    #
                    # Example: "Breaking Bad (2025) - S01E01 - Pilot"
                    #          raw_title_without_year = "Breaking Bad ("
                    #          after strip = "Breaking Bad"
                    title = raw_title_without_year.strip(POTENTIAL_ARTIFACTS)
                    remainder = raw_remainder.strip(POTENTIAL_ARTIFACTS)

                    # Replace separators
                    clean_title = title
                    clean_remainder = remainder
                    for old_sep, new_sep in SEPARATOR_REPLACEMENTS.items():
                        clean_title = clean_title.replace(old_sep, new_sep)
                        clean_remainder = clean_remainder.replace(old_sep, new_sep)

                    return SERIES_FORMAT_FULL.format(
                        title=clean_title,
                        year=year,
                        episode=episode,
                        remainder=clean_remainder,
                        ext=self.file_extension,
                    )
                else:
                    # Year comes AFTER episode - invalid position, treat as no year
                    # Apply smart cleaning to title and remainder
                    title = raw_title.strip(POTENTIAL_ARTIFACTS)
                    remainder = raw_remainder.strip(POTENTIAL_ARTIFACTS)

                    clean_title = title
                    clean_remainder = remainder
                    for old_sep, new_sep in SEPARATOR_REPLACEMENTS.items():
                        clean_title = clean_title.replace(old_sep, new_sep)
                        clean_remainder = clean_remainder.replace(old_sep, new_sep)

                    return SERIES_FORMAT_FULL.format(
                        title=clean_title,
                        year=self.media_year,
                        episode=episode,
                        remainder=clean_remainder,
                        ext=self.file_extension,
                    )

            # --- CASE 2: No year found - ask user ---
            else:
                # Apply smart cleaning to title and remainder
                title = raw_title.strip(POTENTIAL_ARTIFACTS)
                remainder = raw_remainder.strip(POTENTIAL_ARTIFACTS)

                clean_title = title
                clean_remainder = remainder
                for old_sep, new_sep in SEPARATOR_REPLACEMENTS.items():
                    clean_title = clean_title.replace(old_sep, new_sep)
                    clean_remainder = clean_remainder.replace(old_sep, new_sep)

                return SERIES_FORMAT_FULL.format(
                    title=clean_title,
                    year=self.media_year,
                    episode=episode,
                    remainder=clean_remainder,
                    ext=self.file_extension,
                )

        else:
            raise ValueError(f"Unsupported media type: {self.media_type}")
