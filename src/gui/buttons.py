"""Custom button widgets for the application that follow Windows standard styles."""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from ..models.gui_models import (
    LOAD_BUTTON_STYLE,
    SERVICE_BUTTON_STYLE,
    EXIT_BUTTON_STYLE,
    REMOVE_BUTTON_STYLE,
    ButtonStyle,
)


class StyledButton(QPushButton):
    """Base class for buttons with custom styles.

    This class should not be instantiated directly.
    Use LoadButton, ServiceButton, or ExitButton instead.
    """

    def __init__(self, style: ButtonStyle, text: str = '', parent=None):
        """Initialize the styled button.

        Args:
            style: ButtonStyle configuration (required)
            text: Button text
            parent: Parent widget
        """
        super().__init__(text, parent)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)

        self.button_style = style
        self.apply_structural_styles()

    def apply_structural_styles(self):
        """Apply structural styles to the button (theme-independent).

        Can be overridden by subclasses to customize styling.
        Subclasses should call super().apply_structural_styles() first.
        """
        s = self.button_style

        # Base structural CSS (common to all buttons)
        structural_css = f'''
            QPushButton {{
                font-family: '{s.font_family}';
                font-size: {s.font_size};
                font-weight: {s.font_weight};
                
                padding: {s.padding};
                min-height: {s.min_height};
                min-width: {s.min_width};
               
                border-radius: {s.border_radius};
                border-width: {s.border_width};
                border-style: {s.border_style};

            }}
        '''

        # Set icon size as widget property
        self.setIconSize(QSize(s.icon_size, s.icon_size))

        # Apply the stylesheet to the button
        self.setStyleSheet(structural_css)


class LoadButton(StyledButton):
    """Load button for adding content (Add Movie, Add Series)."""

    def __init__(self, text: str = '', parent=None):
        """Initialize the load button.

        Args:
            text: Button text
            parent: Parent widget
        """
        super().__init__(LOAD_BUTTON_STYLE, text, parent)
        self.setObjectName('LoadButton')


class ServiceButton(StyledButton):
    """Service button for file operations (Remove, Apply Changes)."""

    def __init__(self, text: str = '', parent=None):
        """Initialize the service button.

        Args:
            text: Button text
            parent: Parent widget
        """
        super().__init__(SERVICE_BUTTON_STYLE, text, parent)
        self.setObjectName('ServiceButton')


class CriticalButton(StyledButton):
    """Critical/destructive action button (Remove, Force Edit, etc.).

    Used for actions that modify or remove data, requiring user attention.
    Uses a distinct visual style to indicate the critical nature of the action.
    """

    def __init__(self, text: str = '', parent=None):
        """Initialize the critical button.

        Args:
            text: Button text
            parent: Parent widget
        """
        super().__init__(REMOVE_BUTTON_STYLE, text, parent)
        self.setObjectName('CriticalButton')


class ExitButton(StyledButton):
    """Exit button for application controls (Quit, Start Over)."""

    def __init__(self, text: str = '', parent=None):
        """Initialize the exit button.

        Args:
            text: Button text
            parent: Parent widget
        """
        super().__init__(EXIT_BUTTON_STYLE, text, parent)
        self.setObjectName('ExitButton')


class ToggleIconButton(QPushButton):
    """Toggle button with icon only, for Info and Settings panels.

    Features:
    - Flat style with icon only (no text)
    - Toggle state: normal (enabled/disabled) and active (pressed)
    - Visual feedback on hover and active state
    - Checkable to maintain pressed state
    """

    def __init__(self, icon_path: str, tooltip: str = '', parent=None):
        """Initialize the toggle icon button.

        Args:
            icon_path: Path to the icon file
            tooltip: Tooltip text to show on hover
            parent: Parent widget
        """
        super().__init__(parent)

        # Set icon
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(24, 24))

        # Set tooltip
        if tooltip:
            self.setToolTip(tooltip)

        # Make it checkable (toggle behavior)
        self.setCheckable(True)

        # Flat style
        self.setFlat(True)

        # Fixed size for icon button
        self.setFixedSize(32, 32)

        # Set focus policy
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Apply base styles
        self.setObjectName('ToggleIconButton')
        self._apply_styles()

    def _apply_styles(self):
        """Apply CSS styles for the toggle button."""
        # Base structural CSS only - colors will be applied by theme
        self.setStyleSheet('''
            QPushButton#ToggleIconButton {
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
        ''')


class StatefulIconButton(QPushButton):
    """Icon button that is always clickable but uses enabled/disabled for visual state.

    This button uses Qt's automatic icon greyscale conversion when disabled,
    but remains clickable at all times by intercepting mouse events.

    Visual states:
    - Active (enabled=True): Colored icon
    - Inactive (enabled=False): Greyscale icon (automatic Qt behavior)

    Usage:
        button = StatefulIconButton(QIcon('icon.png'))
        button.clicked.connect(on_click)

        # Toggle visual state programmatically
        button.set_active(True)  # Colored icon
        button.set_active(False)  # Greyscale icon
    """

    def __init__(self, icon: QIcon, parent=None):
        """Initialize stateful icon button.

        Args:
            icon: Icon to display
            parent: Parent widget
        """
        super().__init__(parent)

        # Internal state (independent from enabled property)
        self._is_active = False

        # Set icon
        self.setIcon(icon)
        self.setIconSize(QSize(24, 24))

        # Flat style
        self.setFlat(True)

        # Fixed size for icon button
        self.setFixedSize(32, 32)

        # Set focus policy
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Apply base styles
        self.setObjectName('StatefulIconButton')
        self._apply_styles()

        # Start in inactive state (greyscale)
        self.setEnabled(False)

        # Install event filter on self to intercept clicks even when disabled
        self.installEventFilter(self)

    def _apply_styles(self):
        """Apply CSS styles for the button."""
        # Base structural CSS only - colors will be applied by theme
        self.setStyleSheet('''
            QPushButton#StatefulIconButton {
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
        ''')

    def eventFilter(self, obj, event):
        """Intercept mouse clicks even when button is disabled.

        Args:
            obj: Object that received the event
            event: Event to filter

        Returns:
            bool: True if event was handled, False otherwise
        """
        if obj == self:
            # Intercept mouse press on disabled button
            if event.type() == event.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    # Toggle active state
                    self.set_active(not self._is_active)
                    # Emit clicked signal manually
                    self.clicked.emit()
                    return True

        return super().eventFilter(obj, event)

    def set_active(self, active: bool):
        """Set button visual state (active=colored, inactive=greyscale).

        Args:
            active: True for colored icon, False for greyscale icon
        """
        self._is_active = active
        self.setEnabled(active)

    def is_active(self) -> bool:
        """Check if button is in active state.

        Returns:
            True if active (colored), False if inactive (greyscale)
        """
        return self._is_active
