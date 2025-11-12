"""Core-level constants and models for file analysis and processing."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.file_analyzer import FileAnalyzer

# =============================================================================
# PLACEHOLDER CONSTANTS
# =============================================================================

# Year placeholder used when year is missing or invalid
DEFAULT_YEAR_PLACEHOLDER = 'Set the correct year'
DEFAULT_YEAR_POS_PLACEHOLDER = 0
DEFAULT_EPISODE_PLACEHOLDER = ''

# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================

# Year validation range (shared with gui_models.py for consistency)
MIN_VALID_YEAR = 1895  # First commercial film exhibition
MAX_VALID_YEAR = datetime.now().year  # Current year

# =============================================================================
# FILENAME PARSING CONSTANTS
# =============================================================================

# Character separators used in filename parsing
FILENAME_SEPARATORS = ' .-_'  # space, dot, minus, underscore

# Potential artifacts to clean from title and remainder parts
# Used to remove residual characters after year/episode extraction
# Example: "Title (2024)" → when extracting year, "(" remains in title, ")" in remainder
POTENTIAL_ARTIFACTS = '.[]<>()-_ '

# Replacement patterns for filename cleaning
SEPARATOR_REPLACEMENTS = {
    '.': ' ',
    '_': ' ',
}

# =============================================================================
# REGEX PATTERNS - Centralized pattern definitions
# =============================================================================

# -----------------------------------------------------------------------------
# EPISODE DETECTION PATTERNS
# Used in: FileAnalyzer._extract_episode()
# Purpose: Extract season and episode numbers from filenames
# -----------------------------------------------------------------------------

# Matches S01E01, s01e01, S1E1, etc.
EPISODE_PATTERN_SE = r'[Ss](\d+)[Ee](\d+)'

# Matches 1x01, 3x9, etc. (alternative format)
EPISODE_PATTERN_X = r'(\d+)[Xx](\d+)'

# Combined pattern for matching either S##E## or ##x## format
# Used in: FileProcessor._check_episode_not_modified()
# Captures: group(1) or group(2) for S##E##, group(3) or group(4) for ##x##
EPISODE_PATTERN_COMBINED = r'[Ss](\d+)[Ee](\d+)|(\d+)[Xx](\d+)'

# Pattern for splitting filename on episode marker (S##E## or ##x##)
# Used in: FileProcessor._extract_title_from_series_edit()
# Purpose: Split to get the part before the episode
EPISODE_SPLIT_PATTERN = r'[Ss]\d+[Ee]\d+|\d+[Xx]\d+'

# Standardized output format for episodes
EPISODE_FORMAT = 'S{:02d}E{:02d}'  # e.g., S01E01

# -----------------------------------------------------------------------------
# YEAR DETECTION PATTERN
# Used in: FileAnalyzer._extract_year()
# Purpose: Extract 4-digit year from filename
# -----------------------------------------------------------------------------

# Matches any 4-digit number (word boundary ensures it's standalone)
YEAR_PATTERN = r'\b\d{4}\b'

# -----------------------------------------------------------------------------
# TITLE + YEAR EXTRACTION PATTERN
# Used in: FileProcessor.propagate_series_edit()
# Purpose: Extract title and year from normalized series name
# -----------------------------------------------------------------------------

# Matches "Title (YYYY)" at the start of a string
# Captures: group(1) = title, group(2) = year
# Used to extract base info before applying to all episodes
TITLE_YEAR_PATTERN = r'^(.+?) \((\d{4})\)'

# -----------------------------------------------------------------------------
# SERIES PARSING PATTERN (FULL)
# Used in: FileProcessor.propagate_series_edit()
# Purpose: Parse complete normalized series filename
# -----------------------------------------------------------------------------

# Matches complete series format: "Title (YYYY) - S##E## - EpisodeTitle"
# Captures: group(1) = title, group(2) = year, group(3) = optional episode title
# Example: "Breaking Bad (2008) - S01E01 - Pilot"
SERIES_FULL_PATTERN = r'^(.+?) \((\d{4})\) - S\d+E\d+( - .+)?$'

# -----------------------------------------------------------------------------
# NORMALIZATION VALIDATION PATTERNS
# Used in: _utility.is_normalized()
# Purpose: Check if filename is already in correct format
# -----------------------------------------------------------------------------

# Pattern for normalized series: "Title (YYYY) - S##E## - EpisodeTitle"
# Must match complete filename structure
SERIES_NORMALIZED_PATTERN = r'^[^(]+ \(\d{4}\) - S\d+E\d+( - .+)?$'

# Pattern for normalized film: "Title (YYYY)" or "Title (YYYY) - Remainder"
# Must match complete filename structure
FILM_NORMALIZED_PATTERN = r'^[^(]+ \(\d{4}\)( - .+)?$'

# =============================================================================
# FILENAME FORMAT TEMPLATES
# =============================================================================

# -----------------------------------------------------------------------------
# Film format templates
# Used in: FileAnalyzer.formatter_media_name()
# -----------------------------------------------------------------------------

# Film with remainder: "Title (YYYY) - Remainder.ext"
FILM_FORMAT_WITH_REMAINDER = '{title} ({year}) - {remainder}{ext}'

# Film without remainder: "Title (YYYY).ext"
FILM_FORMAT_NO_REMAINDER = '{title} ({year}){ext}'

# -----------------------------------------------------------------------------
# Series format templates
# Used in: FileAnalyzer.formatter_media_name()
# -----------------------------------------------------------------------------

# Series full format: "Title (YYYY) - S##E## - EpisodeTitle.ext"
SERIES_FORMAT_FULL = '{title} ({year}) - {episode} - {remainder}{ext}'

# =============================================================================
# SUPPORTED FILE EXTENSIONS
# =============================================================================

# Video file extensions supported by the application
VIDEO_EXTENSIONS = [
    '.mp4',
    '.mkv',
    '.avi',
    '.mov',
    '.wmv',
    '.flv',
    '.webm',
    '.m4v',
    '.mpg',
    '.mpeg',
]

# =============================================================================
# DOMAIN MODELS - Business entities and states
# =============================================================================


class FileStatus(Enum):
    """Status of a file in the processing workflow.

    These are business states, not UI states.
    The GUI displays these states but doesn't define them.
    """

    READY = 'ready'  # ✅ Ready to rename
    NEEDS_YEAR = 'needs_year'  # ⚠️ Missing year, needs user input
    INVALID = 'invalid'  # ❌ Invalid format, cannot normalize
    ALREADY_NORMALIZED = 'already_normalized'  # ⭐ Already in correct format
    DUPLICATE = 'duplicate'  # ⚠️ Duplicate name detected
    NOT_VIDEO = 'not_video'  # ❌ Not a video file


@dataclass
class FileProcessingData:
    """Data Transfer Object for file processing workflow.

    Represents a file being processed for renaming with all its metadata.
    This is a domain model, not a GUI model.
    """

    path: str  # Full file path
    original_name: str  # Original filename (basename)
    new_name: str  # Proposed new filename
    status: FileStatus  # Current processing status
    analyzer: 'FileAnalyzer | None' = None  # FileAnalyzer instance if applicable
    error_message: str | None = None  # Error message if status is ERROR/INVALID
