"""Media metadata extraction using pymediainfo library.

This module provides detailed metadata extraction for video and audio files,
including format information, codecs, bitrates, resolution, and track details.

Key Features:
- Extract general file information (format, duration, file size)
- Video track metadata (codec, resolution, frame rate, bitrate)
- Audio track metadata (codec, channels, sample rate, bitrate, language)
- Subtitle track metadata (codec, language)
- Support for multiple audio and subtitle tracks

Dependencies:
    pymediainfo>=6.1.0

Usage:
    extractor = MediaMetadataExtractor('Breaking.Bad.S01E01.mkv')
    metadata = extractor.extract_all()

    # Access general info
    print(metadata['general']['format'])
    print(metadata['general']['duration'])

    # Access video track
    print(metadata['video']['codec'])
    print(metadata['video']['resolution'])

    # Access audio tracks (list)
    for audio in metadata['audio']:
        print(f"{audio['language']}: {audio['codec']}")
"""

from typing import Any, Protocol, cast
from pathlib import Path
from pymediainfo import MediaInfo as PyMediaInfo


# =============================================================================
# TYPE PROTOCOLS - Define interfaces for pymediainfo objects
# =============================================================================

class MediaTrack(Protocol):
    """Protocol defining the interface for pymediainfo Track objects.

    This protocol defines only the attributes we actually use,
    providing type hints without depending on pymediainfo's internal types.
    """
    track_type: str
    format: str | None
    codec_id: str | None
    file_extension: str | None

    # General track attributes
    duration: int | None
    other_file_size: list[str] | None
    other_overall_bit_rate: list[str] | None

    # Video track attributes
    width: int | None
    height: int | None
    format_profile: str | None
    other_display_aspect_ratio: list[str] | None
    other_frame_rate: list[str] | None
    other_bit_rate: list[str] | None
    other_bit_depth: list[str] | None

    # Audio track attributes
    channel_layout: str | None
    channel_s: int | None
    other_sampling_rate: list[str] | None
    language: str | None
    title: str | None
    default: str | None

    # Subtitle track attributes
    forced: str | None


# =============================================================================
# CONFIGURATION - Adjust these values to change behavior
# =============================================================================

# Maximum filename length to display (longer names will be truncated with '...')
MAX_FILENAME_LENGTH = 45


# =============================================================================
# AUDIO CHANNEL MAPPING
# =============================================================================

# Map channel count to standard layout names
# Common audio channel configurations for media files
CHANNEL_COUNT_TO_LAYOUT = {
    1: 'Mono',          # Single channel
    2: 'Stereo',        # Left + Right
    3: '2.1',           # Stereo + LFE (subwoofer)
    4: 'Quad',          # Front L/R + Rear L/R OR 3.1
    5: '4.1',           # Quad + LFE (subwoofer)
    6: '5.1',           # Front L/C/R + Rear L/R + LFE (most common surround)
    7: '6.1',           # 5.1 + Rear Center
    8: '7.1',           # Front L/C/R + Side L/R + Rear L/R + LFE
    10: '7.1.2',        # 7.1 + 2 height channels (Dolby Atmos)
    12: '7.1.4',        # 7.1 + 4 height channels (Dolby Atmos)
    16: '9.1.6',        # 9.1 + 6 height channels (advanced Atmos)
}


class MediaMetadataExtractor:
    """Extracts detailed metadata from media files using pymediainfo.

    This class provides a structured interface for extracting comprehensive
    metadata from video and audio files, organizing information by track type
    (general, video, audio, subtitles).

    Attributes:
        file_path: Path to the media file
        media_info: Parsed MediaInfo object from pymediainfo
    """

    def __init__(self, file_path: str):
        """Initialize metadata extractor.

        Args:
            file_path: Path to the media file

        Raises:
            FileNotFoundError: If the file does not exist
            RuntimeError: If pymediainfo cannot parse the file
        """
        self.file_path = Path(file_path)

        if not self.file_path.exists():
            raise FileNotFoundError(f'File not found: {file_path}')

        try:
            self.media_info: PyMediaInfo = PyMediaInfo.parse(str(self.file_path))
        except Exception as e:
            raise RuntimeError(f'Failed to parse media file: {e}')

    def extract_all(self) -> dict[str, Any]:
        """Extract all available metadata.

        Returns a dictionary containing:
        - general: General file information
        - video: Video track metadata (if available)
        - audio: List of audio track metadata
        - subtitles: List of subtitle track metadata

        Returns:
            dict containing all metadata organized by track type
        """
        return {
            'general': self.extract_general(),
            'video': self.extract_video(),
            'audio': self.extract_audio_tracks(),
            'subtitles': self.extract_subtitle_tracks(),
        }

    def extract_general(self) -> dict[str, str | None]:
        """Extract general file information.

        Returns:
            dict with keys:
            - filename: File name without path (e.g., 'movie.mkv'), truncated if too long
            - format: Container format (e.g., 'Matroska', 'MPEG-4')
            - duration: Duration in human-readable format (e.g., '42min 30s')
            - file_size: File size in human-readable format (e.g., '2.35 GiB')
            - overall_bitrate: Overall bitrate (e.g., '8 500 kb/s')
        """

        # Truncate filename if too long (always needed)
        filename = self._truncate_filename(self.file_path.name)

        for track in self.media_info.tracks:
            general_track = cast(MediaTrack, track)
            if general_track.track_type != 'General':
                continue
                
            # Format duration from milliseconds to readable format
            duration = None
            if general_track.duration:
                duration_ms = int(general_track.duration)
                duration = self._format_duration(duration_ms)

            return {
                'filename': filename,
                'format': general_track.format or general_track.file_extension,
                'duration': duration,
                'file_size': general_track.other_file_size[0] if general_track.other_file_size else None,
                'overall_bitrate': general_track.other_overall_bit_rate[0] if general_track.other_overall_bit_rate else None,
            }

        # No General track found
        return {
            'filename': filename,
            'format': None,
            'duration': None,
            'file_size': None,
            'overall_bitrate': None,
        }

    def extract_video(self) -> dict[str, str | None] | None:
        """Extract video track metadata.

        Returns:
            dict with keys:
            - codec: Video codec name (e.g., 'AVC', 'HEVC', 'VP9')
            - codec_profile: Codec profile (e.g., 'High@L4.1')
            - resolution: Resolution (e.g., '1920x1080')
            - aspect_ratio: Display aspect ratio (e.g., '16:9')
            - frame_rate: Frame rate (e.g., '23.976 fps')
            - bitrate: Video bitrate (e.g., '8 000 kb/s')
            - bit_depth: Bit depth (e.g., '8 bits', '10 bits')

            Returns None if no video track found
        """

        for track in self.media_info.tracks:
            video_track = cast(MediaTrack, track)
            if video_track.track_type != 'Video':
                continue

            # Build resolution string
            resolution = None
            if video_track.width and video_track.height:
                resolution = f"{video_track.width}x{video_track.height}"

            # Get codec profile
            codec_profile = None
            if video_track.format_profile:
                codec_profile = video_track.format_profile
            elif video_track.codec_id:
                codec_profile = video_track.codec_id

            return {
                'codec': video_track.format or video_track.codec_id,
                'codec_profile': codec_profile,
                'resolution': resolution,
                'aspect_ratio': video_track.other_display_aspect_ratio[0] if video_track.other_display_aspect_ratio else None,
                'frame_rate': video_track.other_frame_rate[0] if video_track.other_frame_rate else None,
                'bitrate': video_track.other_bit_rate[0] if video_track.other_bit_rate else None,
                'bit_depth': video_track.other_bit_depth[0] if video_track.other_bit_depth else None,
            }

        # No video track found
        return None

    def extract_audio_tracks(self) -> list[dict[str, str | int | bool | None]]:
        """Extract metadata for all audio tracks.

        Returns:
            list of dicts, each containing:
            - track_number: Track number (1-based)
            - codec: Audio codec (e.g., 'AAC', 'AC-3', 'DTS', 'FLAC')
            - channels: Channel configuration (e.g., '6 channels', '2 channels')
            - channel_layout: Channel layout (e.g., '5.1', 'Stereo')
            - sample_rate: Sample rate (e.g., '48.0 kHz')
            - bitrate: Audio bitrate (e.g., '384 kb/s')
            - language: Language code (e.g., 'en', 'it', 'ja')
            - title: Track title if available
            - default: Whether track is default (Yes/No)
            - forced: Whether track is forced (Yes/No)
        """
        audio_tracks: list[dict[str, str | int | bool | None]] = []
        track_number = 0

        for track in self.media_info.tracks:
            audio_track: MediaTrack = cast(MediaTrack, track)
            if audio_track.track_type != 'Audio':
                continue

            track_number += 1

            # Get channel layout
            channel_layout = None
            if audio_track.channel_layout:
                channel_layout = audio_track.channel_layout
            elif audio_track.channel_s:
                # Map channel count to standard layout using dict lookup
                channel_layout = CHANNEL_COUNT_TO_LAYOUT.get(audio_track.channel_s)

            # Check if default
            is_default = getattr(audio_track, 'default', None) == 'Yes'

            # Check if forced
            is_forced = getattr(audio_track, 'forced', None) == 'Yes'

            audio_tracks.append({
                'track_number': track_number,
                'codec': audio_track.format or audio_track.codec_id,
                'channels': f'{audio_track.channel_s} channels' if audio_track.channel_s else None,
                'channel_layout': channel_layout,
                'sample_rate': audio_track.other_sampling_rate[0] if audio_track.other_sampling_rate else None,
                'bitrate': audio_track.other_bit_rate[0] if audio_track.other_bit_rate else None,
                'language': audio_track.language,
                'title': audio_track.title,
                'default': is_default,
                'forced': is_forced,
            })

        return audio_tracks

    def extract_subtitle_tracks(self) -> list[dict[str, str | int | bool | None]]:
        """Extract metadata for all subtitle tracks.

        Returns:
            list of dicts, each containing:
            - track_number: Track number (1-based)
            - codec: Subtitle format (e.g., 'UTF-8', 'ASS', 'SRT')
            - language: Language code (e.g., 'en', 'it', 'ja')
            - title: Track title if available
            - default: Whether track is default (Yes/No)
            - forced: Whether track is forced subtitles
        """
        subtitle_tracks: list[dict[str, str | int | bool | None]] = []
        track_number = 0

        for track in self.media_info.tracks:
            subtitle_track: MediaTrack = cast(MediaTrack, track)
            if subtitle_track.track_type != 'Text':
                continue

            track_number += 1

            # Check if default
            is_default = getattr(subtitle_track, 'default', None) == 'Yes'

            # Check if forced
            is_forced = getattr(subtitle_track, 'forced', None) == 'Yes'

            subtitle_tracks.append({
                'track_number': track_number,
                'codec': subtitle_track.format or subtitle_track.codec_id,
                'language': subtitle_track.language,
                'title': subtitle_track.title,
                'default': is_default,
                'forced': is_forced,
            })

        return subtitle_tracks

    @staticmethod
    def _truncate_filename(filename: str) -> str:
        """Truncate filename if it exceeds MAX_FILENAME_LENGTH.

        Args:
            filename: Original filename

        Returns:
            Truncated filename with '...' if too long, otherwise original filename
        """
        if len(filename) <= MAX_FILENAME_LENGTH:
            return filename
        return filename[:MAX_FILENAME_LENGTH - 3] + '...'

    @staticmethod
    def _format_duration(duration_ms: int) -> str:
        """Format duration from milliseconds to human-readable format.

        Args:
            duration_ms: Duration in milliseconds

        Returns:
            Formatted duration string (e.g., '1h 42min 30s', '42min 30s', '30s')
        """
        seconds = duration_ms // 1000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}min")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")

        return ' '.join(parts)
