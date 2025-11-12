"""Status bar widget for displaying colored messages to the user.

This module provides the StatusBar widget, a custom QFrame that displays
status messages with appropriate styling based on message type. Used throughout
the application to provide feedback to users about file processing progress,
errors, and other important events.

Features:
- Type-based styling (Info, Warning, Error, Success, Processing)
- Unicode emoji icons for visual feedback
- Word wrapping for long messages
- CSS-based theming support with object name targeting
- Clear method to reset to default state

Message Types:
- INFO: Informational messages (blue text)
- WARNING: Warning messages (yellow text)
- ERROR: Error messages (red text)
- SUCCESS: Success messages (green text)
- PROCESSING: Processing messages (cyan text)
"""

from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ..models import MessageType


class StatusBar(QFrame):
    """Custom status bar widget for displaying colored messages with icons.

    A simple but effective status display that shows application state and
    feedback messages. Each message type has distinct styling to provide visual
    cues to the user about the message importance and context.

    The widget consists of a QLabel inside a QFrame with CSS-based styling.
    Message type is communicated via object name to allow CSS selectors like
    '#StatusBar #SuccessText' to apply appropriate colors.

    Attributes:
        message_label: QLabel displaying the current message with icon
    """

    def __init__(self, parent=None):
        """Initialize the status bar widget.

        Sets up the label, layout, and applies default styling. The status bar
        displays with word wrapping enabled and an initial ready message.

        Args:
            parent: Parent widget for proper widget hierarchy (optional).
                   Defaults to None.
        """
        super().__init__(parent)
        self.setObjectName('StatusBar')  # For CSS targeting
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize the UI components.

        Configures the QFrame and QLabel with:
        - No frame shape/shadow to work with CSS borders
        - Message label with word wrapping and margins
        - Font size set to 9 points
        - Layout with zero margins to align border with content
        - Default message type set to INFO
        """
        # Remove default frame to avoid double border with CSS border
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.setLineWidth(0)
        self.setMidLineWidth(0)

        # Create label for message text
        self.message_label = QLabel('Ready to process files')
        self.message_label.setWordWrap(True)
        self.message_label.setMargin(10)

        # Set font
        font = QFont()
        font.setPointSize(9)
        self.message_label.setFont(font)

        # Add label to frame with zero margins to prevent gap between border and content
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.message_label)

        # Set default style
        self.set_message('Ready to process files', MessageType.INFO)

    def set_message(
        self, message: str, message_type: MessageType = MessageType.INFO
    ) -> None:
        """Set the status message with appropriate styling.

        Updates the displayed message and applies visual styling based on the
        message type. Each type has:
        - A Unicode emoji icon (ℹ️, ⚠️, ❌, ✅, 🔄)
        - A distinct text color applied via CSS object name targeting
        - An object name for CSS theming (InfoText, WarningText, etc.)

        The message is displayed with the icon prepended.

        Args:
            message: Message text to display (can contain newlines for multi-line)
            message_type: Type of message from MessageType enum, determines
                         styling. Defaults to MessageType.INFO
        """
        # Icon mapping
        icons = {
            MessageType.INFO: 'ℹ️',
            MessageType.WARNING: '⚠️',
            MessageType.ERROR: '❌',
            MessageType.SUCCESS: '✅',
            MessageType.PROCESSING: '🔄',
        }

        # Object name mapping for CSS targeting
        object_names = {
            MessageType.INFO: 'InfoText',
            MessageType.WARNING: 'WarningText',
            MessageType.ERROR: 'ErrorText',
            MessageType.SUCCESS: 'SuccessText',
            MessageType.PROCESSING: 'ProcessingText',
        }

        icon = icons.get(message_type, '')
        object_name = object_names.get(message_type, 'InfoText')

        # Set message with icon
        self.message_label.setText(f'{icon} {message}')

        # Set object name for CSS targeting
        self.message_label.setObjectName(object_name)

    def clear(self) -> None:
        """Clear the status message.

        Resets the status bar to its default ready state with an informational
        message. Used when returning to the ready state after processing.
        """
        self.set_message('Ready to process files', MessageType.INFO)
