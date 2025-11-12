"""Theme system for the application.

This module defines the theming system for the Renamer application, providing
a centralized way to manage colors and visual styling across all UI components.

Key Features:
- Theme dataclass: Defines all color properties organized by UI component
- Multiple themes: Support for switching between different color schemes
- Stylesheet generation: Applies theme colors to Qt widgets via stylesheets
- Separation of concerns: Theme handles colors only, structural styles are
  in button style definitions

Theme Properties:
- Buttons: LoadButton, ServiceButton, CriticalButton, ExitButton (each with
  normal, hover, pressed, and disabled states)
- Table: Background, text, headers, gridlines, and scrollbars
- Status bar: Background, border, and text colors for different message types
- File status: Text colors for different file validation states

Usage:
    theme = get_theme('default')
    apply_theme_to_app(app, theme)

Note: Some color properties (file_*_text) are currently hardcoded in
FileTable.NEW_NAME_TEXT_COLORS and could be refactored to use theme colors.
"""

from PySide6.QtWidgets import QApplication
from dataclasses import dataclass
from typing import NamedTuple


@dataclass
class Theme:
    """Theme configuration for the application.

    A dataclass that stores all color properties needed to theme the Renamer
    application. Properties are organized by UI component and state to make
    theme creation and management straightforward.

    Color Properties Organization:
    1. ACTIVELY USED IN STYLESHEET - Colors applied via apply_theme_to_app():
       - Window and general text colors
       - Button colors (LoadButton, ServiceButton, CriticalButton, ExitButton)
       - Table colors (background, text, headers, gridlines, scrollbars)
       - Status bar colors and text states
    2. AVAILABLE BUT UNUSED - Hardcoded in components:
       - File status text colors (in FileTable.NEW_NAME_TEXT_COLORS)
       - These can be refactored to use theme properties

    Each button type supports four states:
    - Normal (base color)
    - Hover (mouse over)
    - Pressed (clicked)
    - Disabled (inactive)

    Each state includes background, text, and border colors.
    """

    name: str

    # ===== ACTIVELY USED IN STYLESHEET =====
    # Window colors
    window_bg: str
    text_color: str

    # LoadButton colors (Add Movie, Add Series)
    load_button_bg: str
    load_button_hover_bg: str
    load_button_pressed_bg: str
    load_button_disabled_bg: str
    load_button_text: str
    load_button_hover_text: str
    load_button_disabled_text: str
    load_button_border: str
    load_button_hover_border: str
    load_button_pressed_border: str
    load_button_disabled_border: str

    # ServiceButton colors (Apply Changes)
    service_button_bg: str
    service_button_hover_bg: str
    service_button_pressed_bg: str
    service_button_disabled_bg: str
    service_button_text: str
    service_button_hover_text: str
    service_button_disabled_text: str
    service_button_border: str
    service_button_hover_border: str
    service_button_pressed_border: str
    service_button_disabled_border: str

    # CriticalButton colors (Remove, Force Edit - destructive actions)
    remove_button_bg: str
    remove_button_hover_bg: str
    remove_button_pressed_bg: str
    remove_button_disabled_bg: str
    remove_button_text: str
    remove_button_hover_text: str
    remove_button_disabled_text: str
    remove_button_border: str
    remove_button_hover_border: str
    remove_button_pressed_border: str
    remove_button_disabled_border: str

    # ExitButton colors (Quit, Start Over)
    exit_button_bg: str
    exit_button_hover_bg: str
    exit_button_pressed_bg: str
    exit_button_disabled_bg: str
    exit_button_text: str
    exit_button_hover_text: str
    exit_button_disabled_text: str
    exit_button_border: str
    exit_button_hover_border: str
    exit_button_pressed_border: str
    exit_button_disabled_border: str

    # Table colors
    table_bg: str
    table_text: str
    table_header_bg: str
    table_header_text: str
    table_header_border: (
        str  # Border/gridline color for horizontal lines and status column separator
    )
    table_vertical_line: str
    table_horizontal_line: str
    table_selection_bg: str  # Selected row background (also used for toggle buttons)

    # Scrollbar colors
    scrollbar_bg: str  # Background track
    scrollbar_handle: str  # Scrollbar handle/thumb
    scrollbar_handle_hover: str  # Handle on hover

    # Status bar colors
    status_bar_bg: str
    status_bar_border: str
    status_info_text: str
    status_warning_text: str
    status_error_text: str
    status_success_text: str
    status_processing_text: str

    # Media Info Panel colors
    panel_bg: str
    panel_border: str
    panel_text: str

    # ===== AVAILABLE BUT CURRENTLY UNUSED =====
    # These are hardcoded in FileTable.NEW_NAME_TEXT_COLORS - could be refactored to use theme
    file_ready_text: str
    file_needs_year_text: str
    file_invalid_text: str
    file_normalized_text: str
    file_duplicate_text: str
    file_not_video_text: str


# Define available themes
THEMES: dict[str, Theme] = {
    'default': Theme(
        name='Default',
        # Dark theme base - you can adjust these
        window_bg='#1e1e1e',
        text_color='#d4d4d4',
        # LoadButton -  neutral gray
        load_button_bg='#3e3e42',
        load_button_hover_bg='#505056',
        load_button_pressed_bg='#2d2d30',
        load_button_disabled_bg='#2d2d30',
        load_button_text='#cccccc',
        load_button_hover_text='#ffffff',
        load_button_disabled_text='#656565',
        load_button_border='#3e3e42',
        load_button_hover_border='#505056',
        load_button_pressed_border='#2d2d30',
        load_button_disabled_border='#2d2d30',
        # ServiceButton - bright blue for primary actions
        service_button_bg='#0e639c',
        service_button_hover_bg='#1177bb',
        service_button_pressed_bg='#0d5a8f',
        service_button_disabled_bg='#3e3e42',
        service_button_text='#ffffff',
        service_button_hover_text='#ffffff',
        service_button_disabled_text='#858585',
        service_button_border='#0e639c',
        service_button_hover_border='#1177bb',
        service_button_pressed_border='#0d5a8f',
        service_button_disabled_border='#3e3e42',
        # CriticalButton - red for destructive/critical actions
        remove_button_bg='#c72e2e',
        remove_button_hover_bg='#e03e3e',
        remove_button_pressed_bg='#a52222',
        remove_button_disabled_bg='#3e3e42',
        remove_button_text='#ffffff',
        remove_button_hover_text='#ffffff',
        remove_button_disabled_text='#858585',
        remove_button_border='#c72e2e',
        remove_button_hover_border='#e03e3e',
        remove_button_pressed_border='#a52222',
        remove_button_disabled_border='#3e3e42',
        # ExitButton - neutral gray
        exit_button_bg='#3e3e42',
        exit_button_hover_bg='#505056',
        exit_button_pressed_bg='#2d2d30',
        exit_button_disabled_bg='#2d2d30',
        exit_button_text='#cccccc',
        exit_button_hover_text='#ffffff',
        exit_button_disabled_text='#656565',
        exit_button_border='#3e3e42',
        exit_button_hover_border='#505056',
        exit_button_pressed_border='#2d2d30',
        exit_button_disabled_border='#2d2d30',
        # Table colors
        table_bg='#252526',
        table_text='#d4d4d4',
        table_header_bg='#2d2d30',
        table_header_text='#cccccc',
        table_header_border='#1e1e1e',
        table_vertical_line='#555555',
        table_horizontal_line='#161616',
        table_selection_bg='#094771',  # Blue selection background
        # Scrollbar colors
        scrollbar_bg='#1e1e1e',  # Matches window background
        scrollbar_handle='#424242',  # Subtle gray handle
        scrollbar_handle_hover='#4e4e4e',  # Slightly lighter on hover
        # Status bar colors
        status_bar_bg='#2d2d2d',
        status_bar_border='#555555',
        status_info_text='#5fa4ea',
        status_warning_text='#f39c12',
        status_error_text='#dc3545',
        status_success_text='#00720f',
        status_processing_text='#3498db',
        # Media Info Panel colors
        panel_bg='#1e1e1e',
        panel_border='#3e3e42',
        panel_text='#d4d4d4',
        # File status text colors
        file_ready_text='#66bb6a',
        file_needs_year_text='#ffb74d',
        file_invalid_text='#f44336',
        file_normalized_text='#9e9e9e',
        file_duplicate_text='#ff9800',
        file_not_video_text='#f44336',
    ),
    # 'dark': Theme(
    #     name='Dark',
    #     # Classic dark theme with blue-gray tones
    #     window_bg='#2b2b2b',
    #     text_color='#e8e8e8',
    #     # LoadButton - vibrant blue
    #     load_button_bg='#2196f3',
    #     load_button_hover_bg='#42a5f5',
    #     load_button_pressed_bg='#1976d2',
    #     load_button_disabled_bg='#424242',
    #     load_button_text='#ffffff',
    #     load_button_hover_text='#ffffff',
    #     load_button_disabled_text='#757575',
    #     load_button_border='#2196f3',
    #     load_button_hover_border='#42a5f5',
    #     load_button_pressed_border='#1976d2',
    #     load_button_disabled_border='#424242',
    #     # ServiceButton - dark gray
    #     service_button_bg='#424242',
    #     service_button_hover_bg='#4f4f4f',
    #     service_button_pressed_bg='#353535',
    #     service_button_disabled_bg='#353535',
    #     service_button_text='#e0e0e0',
    #     service_button_hover_text='#ffffff',
    #     service_button_disabled_text='#616161',
    #     service_button_border='#555555',
    #     service_button_hover_border='#666666',
    #     service_button_pressed_border='#444444',
    #     service_button_disabled_border='#353535',
    #     # ExitButton - red
    #     exit_button_bg='#d32f2f',
    #     exit_button_hover_bg='#e53935',
    #     exit_button_pressed_bg='#c62828',
    #     exit_button_disabled_bg='#424242',
    #     exit_button_text='#ffffff',
    #     exit_button_hover_text='#ffffff',
    #     exit_button_disabled_text='#757575',
    #     exit_button_border='#d32f2f',
    #     exit_button_hover_border='#e53935',
    #     exit_button_pressed_border='#c62828',
    #     exit_button_disabled_border='#424242',
    #     # Table colors
    #     table_header_bg='#1e1e1e',
    #     table_header_text='#e8e8e8',
    #     table_alt_row_bg='#323232',
    #     # Status bar text colors
    #     status_info_text='#64b5f6',
    #     status_warning_text='#ffa726',
    #     status_error_text='#ef5350',
    #     status_success_text='#66bb6a',
    #     status_processing_text='#42a5f5',
    #     # File status text colors
    #     file_ready_text='#66bb6a',
    #     file_needs_year_text='#ffa726',
    #     file_invalid_text='#ef5350',
    #     file_normalized_text='#9e9e9e',
    #     file_duplicate_text='#ff9800',
    #     file_not_video_text='#ef5350',
    # ),
    # 'light': Theme(
    #     name='Light',
    #     # Clean light theme with blue accents
    #     window_bg='#f5f5f5',
    #     text_color='#212121',
    #     # LoadButton - blue primary
    #     load_button_bg='#1976d2',
    #     load_button_hover_bg='#2196f3',
    #     load_button_pressed_bg='#1565c0',
    #     load_button_disabled_bg='#e0e0e0',
    #     load_button_text='#ffffff',
    #     load_button_hover_text='#ffffff',
    #     load_button_disabled_text='#9e9e9e',
    #     load_button_border='#1976d2',
    #     load_button_hover_border='#2196f3',
    #     load_button_pressed_border='#1565c0',
    #     load_button_disabled_border='#e0e0e0',
    #     # ServiceButton - light gray
    #     service_button_bg='#ffffff',
    #     service_button_hover_bg='#e3f2fd',
    #     service_button_pressed_bg='#bbdefb',
    #     service_button_disabled_bg='#fafafa',
    #     service_button_text='#424242',
    #     service_button_hover_text='#212121',
    #     service_button_disabled_text='#bdbdbd',
    #     service_button_border='#bdbdbd',
    #     service_button_hover_border='#1976d2',
    #     service_button_pressed_border='#1565c0',
    #     service_button_disabled_border='#e0e0e0',
    #     # ExitButton - red
    #     exit_button_bg='#d32f2f',
    #     exit_button_hover_bg='#e53935',
    #     exit_button_pressed_bg='#c62828',
    #     exit_button_disabled_bg='#e0e0e0',
    #     exit_button_text='#ffffff',
    #     exit_button_hover_text='#ffffff',
    #     exit_button_disabled_text='#9e9e9e',
    #     exit_button_border='#d32f2f',
    #     exit_button_hover_border='#e53935',
    #     exit_button_pressed_border='#c62828',
    #     exit_button_disabled_border='#e0e0e0',
    #     # Table colors
    #     table_header_bg='#1976d2',
    #     table_header_text='#ffffff',
    #     table_alt_row_bg='#fafafa',
    #     # Status bar text colors
    #     status_info_text='#1976d2',
    #     status_warning_text='#f57c00',
    #     status_error_text='#d32f2f',
    #     status_success_text='#388e3c',
    #     status_processing_text='#1976d2',
    #     # File status text colors
    #     file_ready_text='#2e7d32',
    #     file_needs_year_text='#f57c00',
    #     file_invalid_text='#c62828',
    #     file_normalized_text='#757575',
    #     file_duplicate_text='#e65100',
    #     file_not_video_text='#c62828',
    # ),
}


def get_theme(theme_name: str) -> Theme:
    """Get theme by name.

    Retrieves a theme from the THEMES dictionary by name. If the theme
    does not exist, returns the default theme.

    Args:
        theme_name: Name of the theme to retrieve (e.g., 'default')

    Returns:
        Theme object with the requested name, or default theme if not found
    """
    return THEMES.get(theme_name, THEMES['default'])


def get_theme_names() -> list[str]:
    """Get list of available theme names.

    Returns all currently available theme names that can be passed to
    get_theme(). Useful for populating theme selection UI or validation.

    Returns:
        List of theme name strings (e.g., ['default', 'dark', 'light'])
    """
    return list(THEMES.keys())


def apply_theme_to_app(app: QApplication, theme: Theme) -> None:
    """Apply theme to QApplication.

    Generates and applies a Qt stylesheet to the application based on the
    provided Theme object. The stylesheet includes:
    - Main window and widget background/text colors
    - Button styles for all button types and states (hover, pressed, disabled)
    - Table widget styling including headers, gridlines, and scrollbars
    - Status bar styling with colors for different message types

    Design Note:
    - Only color properties are included in the stylesheet
    - Structural properties (font, padding, dimensions) are defined separately
      in ButtonStyle classes to maintain separation of concerns
    - Most styling (except colors) is handled by button style definitions

    Args:
        app: QApplication instance to apply the theme to
        theme: Theme object containing all color definitions
    """
    # Create stylesheet - ONLY colors, not structural properties
    # Structural styles (font, padding, dimensions) are in ButtonStyle definitions
    stylesheet = f'''
        QMainWindow {{
            background-color: {theme.window_bg};
            color: {theme.text_color};
        }}
        
        QWidget {{
            background-color: {theme.window_bg};
            color: {theme.text_color};
        }}
        
        /* LoadButton - COLORS ONLY */
        QPushButton#LoadButton {{
            background-color: {theme.load_button_bg};
            color: {theme.load_button_text};
            border-color: {theme.load_button_border};
        }}
        
        QPushButton#LoadButton:hover {{
            background-color: {theme.load_button_hover_bg};
            color: {theme.load_button_hover_text};
            border-color: {theme.load_button_hover_border};
        }}
        
        QPushButton#LoadButton:pressed {{
            background-color: {theme.load_button_pressed_bg};
            border-color: {theme.load_button_pressed_border};
        }}
        
        QPushButton#LoadButton:disabled {{
            background-color: {theme.load_button_disabled_bg};
            color: {theme.load_button_disabled_text};
            border-color: {theme.load_button_disabled_border};
        }}
        
        /* ServiceButton - COLORS ONLY */
        QPushButton#ServiceButton {{
            background-color: {theme.service_button_bg};
            color: {theme.service_button_text};
            border-color: {theme.service_button_border};
        }}
        
        QPushButton#ServiceButton:hover {{
            background-color: {theme.service_button_hover_bg};
            color: {theme.service_button_hover_text};
            border-color: {theme.service_button_hover_border};
        }}
        
        QPushButton#ServiceButton:pressed {{
            background-color: {theme.service_button_pressed_bg};
            border-color: {theme.service_button_pressed_border};
        }}
        
        QPushButton#ServiceButton:disabled {{
            background-color: {theme.service_button_disabled_bg};
            color: {theme.service_button_disabled_text};
            border-color: {theme.service_button_disabled_border};
        }}
        
        /* ExitButton - COLORS ONLY */
        QPushButton#ExitButton {{
            background-color: {theme.exit_button_bg};
            color: {theme.exit_button_text};
            border-color: {theme.exit_button_border};
        }}
        
        QPushButton#ExitButton:hover {{
            background-color: {theme.exit_button_hover_bg};
            color: {theme.exit_button_hover_text};
            border-color: {theme.exit_button_hover_border};
        }}
        
        QPushButton#ExitButton:pressed {{
            background-color: {theme.exit_button_pressed_bg};
            border-color: {theme.exit_button_pressed_border};
        }}
        
        QPushButton#ExitButton:disabled {{
            background-color: {theme.exit_button_disabled_bg};
            color: {theme.exit_button_disabled_text};
            border-color: {theme.exit_button_disabled_border};
        }}
        
        /* CriticalButton - COLORS ONLY (used for Remove, Force Edit, etc.) */
        QPushButton#CriticalButton {{
            background-color: {theme.remove_button_bg};
            color: {theme.remove_button_text};
            border-color: {theme.remove_button_border};
        }}

        QPushButton#CriticalButton:hover {{
            background-color: {theme.remove_button_hover_bg};
            color: {theme.remove_button_hover_text};
            border-color: {theme.remove_button_hover_border};
        }}

        QPushButton#CriticalButton:pressed {{
            background-color: {theme.remove_button_pressed_bg};
            border-color: {theme.remove_button_pressed_border};
        }}

        QPushButton#CriticalButton:disabled {{
            background-color: {theme.remove_button_disabled_bg};
            color: {theme.remove_button_disabled_text};
            border-color: {theme.remove_button_disabled_border};
        }}

        /* ToggleIconButton - COLORS ONLY (Info and Settings buttons) */
        QPushButton#ToggleIconButton {{
            background-color: transparent;
        }}

        QPushButton#ToggleIconButton:hover {{
            background-color: {theme.table_selection_bg};
        }}

        QPushButton#ToggleIconButton:checked {{
            background-color: {theme.table_selection_bg};
        }}

        QPushButton#ToggleIconButton:disabled {{
            opacity: 0.4;
        }}

        /* StatefulIconButton - COLORS ONLY (Always clickable, uses enabled state for icon color) */
        QPushButton#StatefulIconButton {{
            background-color: transparent;
        }}

        QPushButton#StatefulIconButton:hover {{
            background-color: {theme.table_selection_bg};
        }}

        QPushButton#StatefulIconButton:disabled {{
            opacity: 0.4;
        }}

        /* Table - COLORS ONLY */
        QTableWidget {{
            background-color: {theme.table_bg};
            color: {theme.table_text};
            border: none;
            gridline-color: transparent;  
        }}
        
        QTableWidget::item {{
            padding: 5px;
            border-bottom: 1px solid {theme.table_horizontal_line};  /* Horizontal lines - darker than background */
            border-right: none;  /* No vertical lines by default */
        }}
        
        QTableWidget::item:first {{  /* Status column only */
            border-right: 1px solid {theme.table_vertical_line};  /* Vertical line after status column */
        }}
        
        QHeaderView::section {{
            background-color: {theme.table_header_bg};
            color: {theme.table_header_text};
            padding: 5px;
            border: none;
            border-bottom: 1px solid {theme.table_horizontal_line};  /* Horizontal line under header */
            font-weight: bold;
        }}
        
        QHeaderView::section:first {{  /* Status column header */
            border-right: 1px solid {theme.table_header_border};  /* Vertical line after status header */
        }}
        
        /* Modern flat scrollbar - VS Code style */
        QScrollBar:vertical {{
            background-color: {theme.scrollbar_bg};
            width: 14px;
            margin: 0px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {theme.scrollbar_handle};
            min-height: 30px;
            border-radius: 7px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {theme.scrollbar_handle_hover};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;  /* Remove arrow buttons */
        }}
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;  /* Remove page step area styling */
        }}
        
        QScrollBar:horizontal {{
            background-color: {theme.scrollbar_bg};
            height: 14px;
            margin: 0px;
            border: none;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {theme.scrollbar_handle};
            min-width: 30px;
            border-radius: 7px;
            margin: 2px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {theme.scrollbar_handle_hover};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;  /* Remove arrow buttons */
        }}
        
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;  /* Remove page step area styling */
        }}

        /* MediaInfoPanel - COLORS ONLY */
        QWidget#MediaInfoPanel {{
            background-color: {theme.panel_bg};
            border: 1px solid {theme.panel_border};
            color: {theme.panel_text};
        }}

        QWidget#MediaInfoPanel QLabel {{
            color: {theme.panel_text};
            background-color: transparent;
        }}

        /* Section titles - bold and slightly larger */
        QLabel#SectionTitle {{
            color: {theme.panel_text};
            font-weight: bold;
            font-size: 10pt;
            padding: 2px 0px 3px 0px;
        }}

        /* Field labels - left column */
        QLabel#FieldLabel {{
            color: {theme.panel_text};
            font-weight: normal;
            padding-right: 10px;
        }}

        /* Field values - right column, selectable */
        QLabel#FieldValue {{
            color: {theme.panel_text};
            font-weight: normal;
        }}

        /* Track headers for audio/subtitle lists */
        QLabel#TrackHeader {{
            color: {theme.panel_text};
            font-weight: bold;
            font-size: 9pt;
            padding-top: 4px;
            padding-bottom: 1px;
        }}

        /* No selection message in media info panel */
        QLabel#NoSelectionMessage {{
            color: {theme.panel_text};
            font-size: 14pt;
            font-style: italic;
            padding: 40px;
        }}

        /* Vertical separators in media info panel */
        QFrame#VerticalSeparator {{
            color: {theme.panel_border};
            max-width: 1px;
        }}

        /* Status Bar */
        QFrame#StatusBar {{
            background-color: {theme.status_bar_bg};
            border: 1px solid {theme.status_bar_border};
            border-radius: 8px;
        }}
        
        QFrame#StatusBar QLabel {{
            background-color: transparent;
        }}
        
        QFrame#StatusBar QLabel#InfoText {{
            color: {theme.status_info_text};
        }}
        
        QFrame#StatusBar QLabel#WarningText {{
            color: {theme.status_warning_text};
        }}
        
        QFrame#StatusBar QLabel#ErrorText {{
            color: {theme.status_error_text};
        }}
        
        QFrame#StatusBar QLabel#SuccessText {{
            color: {theme.status_success_text};
        }}
        
        QFrame#StatusBar QLabel#ProcessingText {{
            color: {theme.status_processing_text};
        }}
        
    '''

    app.setStyleSheet(stylesheet)
