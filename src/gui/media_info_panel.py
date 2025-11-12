"""Media Info Panel - Collapsible panel for displaying media file metadata."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QScrollArea,
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve

from ..models import (
    MEDIA_INFO_PANEL_HEIGHT_RATIO,
    MEDIA_INFO_PANEL_MIN_HEIGHT,
    MEDIA_INFO_PANEL_MAX_HEIGHT,
    MEDIA_INFO_PANEL_MARGIN,
    MEDIA_INFO_PANEL_SPACING,
    MEDIA_INFO_CONTENT_SPACING,
    MEDIA_INFO_SECTIONS_SPACING,
    MEDIA_INFO_SECTIONS_LEFT_PADDING,
    MEDIA_INFO_SECTION_TITLE_SPACING,
    MEDIA_INFO_GRID_LEFT_MARGIN,
    MEDIA_INFO_GRID_HORIZONTAL_SPACING,
    MEDIA_INFO_GRID_VERTICAL_SPACING,
    MEDIA_INFO_ANIMATION_DURATION,
)


# =============================================================================
# FIELD MAPPINGS - Declarative field definitions for metadata sections
# =============================================================================

# General section fields (keys only - labels auto-generated from key names)
GENERAL_FIELDS = ['filename', 'format', 'duration', 'file_size', 'overall_bitrate']

# Video section fields (keys only - labels auto-generated from key names)
VIDEO_FIELDS = ['codec', 'codec_profile', 'resolution', 'aspect_ratio', 'frame_rate', 'bitrate', 'bit_depth']

# Audio track fields (keys only - labels auto-generated from key names)
AUDIO_FIELDS = ['codec', 'channels', 'channel_layout', 'sample_rate', 'bitrate', 'language', 'title', 'default', 'forced']

# Subtitle track fields (keys only - labels auto-generated from key names)
SUBTITLE_FIELDS = ['codec', 'language', 'title', 'default', 'forced']


class SectionWidget(QWidget):
    """Widget representing a section with title and content grid."""

    def __init__(self, title: str, parent=None):
        """Initialize section widget.

        Args:
            title: Section title
            parent: Parent widget
        """
        super().__init__(parent)

        # Main layout for the section
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(MEDIA_INFO_SECTION_TITLE_SPACING)

        # Section title
        title_label = QLabel(title)
        title_label.setObjectName('SectionTitle')
        main_layout.addWidget(title_label)

        # Content container with its own grid
        content_container = QWidget()
        self.content_grid = QGridLayout(content_container)
        self.content_grid.setContentsMargins(MEDIA_INFO_GRID_LEFT_MARGIN, 0, 0, 0)
        self.content_grid.setHorizontalSpacing(MEDIA_INFO_GRID_HORIZONTAL_SPACING)
        self.content_grid.setVerticalSpacing(MEDIA_INFO_GRID_VERTICAL_SPACING)
        self.content_grid.setColumnStretch(0, 0)  # Label column: fixed width
        self.content_grid.setColumnStretch(1, 1)  # Value column: expandable

        main_layout.addWidget(content_container)
        main_layout.addStretch()  # Push content to top


class MediaInfoPanel(QWidget):
    """Collapsible panel that displays media file information.

    Features:
    - Initially hidden (height = 0)
    - Smooth expand/collapse animation
    - Shows metadata for selected file
    - Updates automatically when selection changes
    """

    def __init__(self, parent=None):
        """Initialize the media info panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Initial state: collapsed
        self._is_expanded = False

        # Setup UI
        self._setup_ui()

        # Start collapsed (height = 0, hidden)
        self.setMaximumHeight(0)
        self.setVisible(False)

    def _setup_ui(self):
        """Setup the panel user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            MEDIA_INFO_PANEL_MARGIN,
            MEDIA_INFO_PANEL_MARGIN,
            MEDIA_INFO_PANEL_MARGIN,
            MEDIA_INFO_PANEL_MARGIN
        )
        main_layout.setSpacing(MEDIA_INFO_PANEL_SPACING)

        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Content widget inside scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(MEDIA_INFO_CONTENT_SPACING)

        # Create sections
        self._general_section = self._create_section('General')
        self._video_section = self._create_section('Video')
        self._audio_section = self._create_section('Audio Tracks')
        self._subtitle_section = self._create_section('Subtitle Tracks')

        # Single row: General | Video | Audio | Subtitles (4 columns)
        row = QHBoxLayout()
        row.setSpacing(MEDIA_INFO_SECTIONS_SPACING)
        row.setContentsMargins(MEDIA_INFO_SECTIONS_LEFT_PADDING, 0, 0, 0)

        # General section
        row.addWidget(self._general_section, 1)

        # Vertical separator
        self._separator1 = self._create_vertical_separator()
        row.addWidget(self._separator1)

        # Video section
        row.addWidget(self._video_section, 1)

        # Vertical separator
        self._separator2 = self._create_vertical_separator()
        row.addWidget(self._separator2)

        # Audio section
        row.addWidget(self._audio_section, 1)

        # Vertical separator
        self._separator3 = self._create_vertical_separator()
        row.addWidget(self._separator3)

        # Subtitle section
        row.addWidget(self._subtitle_section, 1)

        content_layout.addLayout(row)

        # Create "No selection" message widget (initially hidden)
        self._no_selection_widget = QLabel('No media file selected')
        self._no_selection_widget.setObjectName('NoSelectionMessage')
        self._no_selection_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._no_selection_widget.setVisible(False)
        content_layout.addWidget(self._no_selection_widget)

        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Set object name for theme styling
        self.setObjectName('MediaInfoPanel')

    def _create_section(self, title: str) -> SectionWidget:
        """Create a section widget with title and content area.

        Args:
            title: Section title

        Returns:
            SectionWidget containing the section
        """
        return SectionWidget(title)

    def _create_vertical_separator(self) -> QFrame:
        """Create a vertical separator line.

        Returns:
            QFrame configured as vertical separator
        """
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setObjectName('VerticalSeparator')
        return separator

    def _add_field(self, grid: QGridLayout, row: int, label_text: str, value_text: str):
        """Add a label-value pair to a grid layout.

        Args:
            grid: Grid layout to add to
            row: Row number
            label_text: Label text (field name)
            value_text: Value text (field value)
        """
        label = QLabel(f'{label_text}:')
        label.setObjectName('FieldLabel')
        value = QLabel(value_text)
        value.setObjectName('FieldValue')
        value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        grid.addWidget(label, row, 0, Qt.AlignmentFlag.AlignTop)
        grid.addWidget(value, row, 1, Qt.AlignmentFlag.AlignTop)

    def _populate_fields(
        self,
        grid: QGridLayout,
        data: dict,
        fields: list[str],
        start_row: int = 0,
        indent: str = '',
    ) -> int:
        """Populate grid with fields from data dict using field mappings.

        Args:
            grid: Grid layout to populate
            data: Dictionary containing field values
            fields: List of field keys to display (labels auto-generated from keys)
            start_row: Starting row number (default: 0)
            indent: Indentation prefix for labels (default: '')

        Returns:
            int: Next available row number after population

        Example:
            row = self._populate_fields(grid, video_data, VIDEO_FIELDS)
        """
        row = start_row
        for key in fields:
            value = data.get(key)
            if value is not None:
                # Special handling for boolean fields ('default' and 'forced')
                if key in ('default', 'forced'):
                    value = 'Yes' if value else 'No'
                # Auto-generate label: replace underscores with spaces and capitalize
                label = key.replace('_', ' ').title()
                self._add_field(grid, row, f'{indent}{label}', str(value))
                row += 1
        return row

    def toggle(self):
        """Toggle panel visibility with animation."""
        if self._is_expanded:
            self.collapse()
        else:
            self.expand()

    def _calculate_target_height(self) -> int:
        """Calculate target height for expanded panel based on main window size.

        The panel height is dynamically calculated as a percentage of the main
        window height, with minimum and maximum bounds for usability.

        Calculation logic:
        1. Get current main window height
        2. Calculate panel height as MEDIA_INFO_PANEL_HEIGHT_RATIO of window height
        3. Clamp result between MEDIA_INFO_PANEL_MIN_HEIGHT and MEDIA_INFO_PANEL_MAX_HEIGHT

        Returns:
            int: Target height in pixels for the expanded panel

        Examples:
            - Window 400px high → 150px panel (80px would be too small, use minimum)
            - Window 800px high → 160px panel (20% of 800)
            - Window 1600px high → 320px panel (20% of 1600)
            - Window 3000px high → 600px panel (600px would be too large, use maximum)
        """
        # Get main window instance
        main_window = self.window()

        # If we can't get window height, use a safe default
        if not main_window or not hasattr(main_window, 'height'):
            return MEDIA_INFO_PANEL_MIN_HEIGHT

        # Get current window height
        window_height = main_window.height()

        # Calculate panel height as percentage of window height
        calculated_height = int(window_height * MEDIA_INFO_PANEL_HEIGHT_RATIO)

        # Apply min/max bounds
        target_height = max(
            MEDIA_INFO_PANEL_MIN_HEIGHT,
            min(MEDIA_INFO_PANEL_MAX_HEIGHT, calculated_height)
        )

        return target_height

    def expand(self):
        """Expand the panel with smooth animation."""
        if self._is_expanded:
            return

        self._is_expanded = True
        self.setVisible(True)

        # Calculate target height based on current window size
        target_height = self._calculate_target_height()

        # Stop any existing animation
        if hasattr(self, 'animation') and self.animation:
            self.animation.stop()
            try:
                self.animation.finished.disconnect()
            except:
                pass

        # Set fixed height for smooth animation (no layout recalculations)
        self.setMinimumHeight(0)
        self.setMaximumHeight(0)

        # Animate both minimum and maximum height together
        self.animation = QPropertyAnimation(self, b"minimumHeight")
        self.animation.setDuration(MEDIA_INFO_ANIMATION_DURATION)
        self.animation.setStartValue(0)
        self.animation.setEndValue(target_height)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Update maximum height during animation to match minimum
        self.animation.valueChanged.connect(lambda val: self.setMaximumHeight(val))
        self.animation.start()

    def collapse(self):
        """Collapse the panel with smooth animation."""
        if not self._is_expanded:
            return

        self._is_expanded = False

        # Stop any existing animation
        if hasattr(self, 'animation') and self.animation:
            self.animation.stop()
            try:
                self.animation.finished.disconnect()
                self.animation.valueChanged.disconnect()
            except:
                pass

        # Get current height for smooth animation
        current_height = self.height()

        # Animate both minimum and maximum height together
        self.animation = QPropertyAnimation(self, b"minimumHeight")
        self.animation.setDuration(MEDIA_INFO_ANIMATION_DURATION)
        self.animation.setStartValue(current_height)
        self.animation.setEndValue(0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Update maximum height during animation to match minimum
        self.animation.valueChanged.connect(lambda val: self.setMaximumHeight(val))

        # Hide panel when animation completes
        self.animation.finished.connect(lambda: self.setVisible(False))
        self.animation.start()

    def is_expanded(self) -> bool:
        """Check if panel is currently expanded.

        Returns:
            True if expanded, False if collapsed
        """
        return self._is_expanded

    def show_no_selection(self):
        """Display 'No media file selected' message in panel.

        Hides all section titles and separators, shows centered message.
        """
        # Hide all sections and separators
        self._general_section.setVisible(False)
        self._video_section.setVisible(False)
        self._audio_section.setVisible(False)
        self._subtitle_section.setVisible(False)
        self._separator1.setVisible(False)
        self._separator2.setVisible(False)
        self._separator3.setVisible(False)

        # Show "No selection" message
        self._no_selection_widget.setVisible(True)

    def update_info(self, metadata: dict):
        """Update panel content with file metadata.

        Args:
            metadata: Dictionary containing metadata from MediaMetadataExtractor
                     Expected keys: 'general', 'video', 'audio', 'subtitles'
        """
        # Hide "No selection" message
        self._no_selection_widget.setVisible(False)

        # Show all sections and separators
        self._general_section.setVisible(True)
        self._video_section.setVisible(True)
        self._audio_section.setVisible(True)
        self._subtitle_section.setVisible(True)
        self._separator1.setVisible(True)
        self._separator2.setVisible(True)
        self._separator3.setVisible(True)

        # Clear all sections
        self._clear_section(self._general_section)
        self._clear_section(self._video_section)
        self._clear_section(self._audio_section)
        self._clear_section(self._subtitle_section)

        # Populate general section
        general = metadata.get('general', {})
        if general:
            grid = self._general_section.content_grid
            self._populate_fields(grid, general, GENERAL_FIELDS)

        # Populate video section
        video = metadata.get('video')
        if video:
            grid = self._video_section.content_grid
            self._populate_fields(grid, video, VIDEO_FIELDS)
        else:
            # No video track
            grid = self._video_section.content_grid
            self._add_field(grid, 0, 'Status', 'No video track found')

        # Populate audio section
        audio_tracks = metadata.get('audio', [])
        if audio_tracks:
            grid = self._audio_section.content_grid
            row = 0
            for i, audio in enumerate(audio_tracks, 1):
                # Track header
                track_label = QLabel(f'Track {i}')
                track_label.setObjectName('TrackHeader')
                grid.addWidget(track_label, row, 0, 1, 2)
                row += 1

                # Track details using field mappings
                row = self._populate_fields(grid, audio, AUDIO_FIELDS, row, '  ')

                # Add spacing between tracks
                if i < len(audio_tracks):
                    row += 1
        else:
            # No audio tracks
            grid = self._audio_section.content_grid
            self._add_field(grid, 0, 'Status', 'No audio tracks found')

        # Populate subtitle section
        subtitle_tracks = metadata.get('subtitles', [])
        if subtitle_tracks:
            grid = self._subtitle_section.content_grid
            row = 0
            for i, subtitle in enumerate(subtitle_tracks, 1):
                # Track header
                track_label = QLabel(f'Track {i}')
                track_label.setObjectName('TrackHeader')
                grid.addWidget(track_label, row, 0, 1, 2)
                row += 1

                # Track details using field mappings
                row = self._populate_fields(grid, subtitle, SUBTITLE_FIELDS, row, '  ')

                # Add spacing between tracks
                if i < len(subtitle_tracks):
                    row += 1
        else:
            # No subtitle tracks
            grid = self._subtitle_section.content_grid
            self._add_field(grid, 0, 'Status', 'No subtitle tracks found')

    def _clear_section(self, section: SectionWidget):
        """Clear all content from a section.

        Args:
            section: Section widget to clear
        """
        grid = section.content_grid
        # Remove all widgets from grid
        while grid.count():
            item = grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
