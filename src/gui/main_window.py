"""Main window for the File Renamer application."""

import os
import logging
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QToolButton

from src.models.app_models import (
    APP_NAME,
    MAIN_WINDOW_ICON_PATH,
    BUTTON_FILMS_ICON_PATH,
    BUTTON_SERIES_ICON_PATH,
    BUTTON_MEDIA_INFO_ICON_PATH,
    BUTTON_SETTINGS_ICON_PATH,
)

from ..models import (
    MessageType,
    DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    LAYOUT_MARGIN,
    LAYOUT_SPACING,
    BUTTON_SPACING,
)
from ..core import scan_folder_for_videos, get_video_extensions
from ..presenters import AppPresenter
from ..config import AppConfig, get_config_file
from .status_bar import StatusBar
from .file_table import FileTable
from .media_info_panel import MediaInfoPanel
from .dialogs import prompt_series_year, show_info, show_warning, confirm_action, confirm_dangerous_action
from .themes import get_theme, apply_theme_to_app
from .buttons import LoadButton, CriticalButton, ServiceButton, ExitButton, StatefulIconButton

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window for the File Renamer.

    Displays file preview table, manages user interactions, and coordinates
    with AppPresenter through signal/slot connections. Handles window state
    persistence and theme management.

    Responsibilities:
    - Create and manage UI layout
    - Connect user actions to Presenter handlers
    - Display Presenter updates through signal handlers
    - Manage window geometry and state
    - Apply and manage application theme
    """

    def __init__(self, app: QApplication) -> None:
        """Initialize the main application window.

        Creates UI, connects Presenter signals, loads configuration,
        restores window state, and displays the window.

        Args:
            app: QApplication instance
        """
        super().__init__()
        self.app = app

        # Load configuration
        self.config = AppConfig.load(get_config_file())

        # Create Presenter (MVP pattern)
        self.presenter = AppPresenter()
        self._connect_presenter_signals()

        # Setup UI
        self._setup_window()
        self._setup_ui()

        # Restore window state
        self._restore_window_state()

        # Show window
        self.show()

    def _setup_window(self) -> None:
        """Configure main window properties (title, size, position)."""
        self.setWindowTitle(APP_NAME)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self._set_window_icon()
        self._center_window()

    def _get_resource_path(self, relative_path: str) -> Path:
        """Get the correct path for a resource file.

        Handles both frozen (PyInstaller) and source execution modes.

        Args:
            relative_path: Path relative to project root (e.g., 'src/assets/icons/app.png')

        Returns:
            Absolute path to the resource
        """
        if getattr(sys, 'frozen', False):
            # Running as compiled executable - resources bundled with PyInstaller
            base_path = Path(getattr(sys, '_MEIPASS', '.'))
        else:
            # Running from source - relative to project root
            base_path = Path(__file__).parent.parent.parent

        return base_path / relative_path

    def _set_window_icon(self) -> None:
        """Set the window icon from the configured path."""
        if MAIN_WINDOW_ICON_PATH:
            icon_path = self._get_resource_path(MAIN_WINDOW_ICON_PATH)

            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
                logger.debug(f"Window icon set: {icon_path}")
            else:
                logger.warning(f"Window icon not found: {icon_path}")

    def _load_button_icons(self) -> None:
        """Load and set icons for buttons."""
        # Film button icon
        if BUTTON_FILMS_ICON_PATH:
            icon_path = self._get_resource_path(BUTTON_FILMS_ICON_PATH)
            if icon_path.exists():
                self.add_movie_button.setIcon(QIcon(str(icon_path)))
                logger.debug(f"Film button icon set: {icon_path}")
            else:
                logger.warning(f"Film button icon not found: {icon_path}")

        # Series button icon
        if BUTTON_SERIES_ICON_PATH:
            icon_path = self._get_resource_path(BUTTON_SERIES_ICON_PATH)
            if icon_path.exists():
                self.add_series_button.setIcon(QIcon(str(icon_path)))
                logger.debug(f"Series button icon set: {icon_path}")
            else:
                logger.warning(f"Series button icon not found: {icon_path}")

    def _setup_ui(self) -> None:
        """Initialize the complete user interface.

        Creates and configures all UI components:
        1. Top buttons: Add Movie, Add Series + Info/Settings toggle buttons
        2. File preview table with selection handling
        3. Media Info Panel (collapsible, below table)
        4. Action buttons: Apply Changes, Save, Discard, Remove
        5. Status bar for messages
        6. Bottom buttons: Quit, Start Over
        7. Applies theme to all components
        """
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(
            LAYOUT_MARGIN,
            LAYOUT_MARGIN,
            LAYOUT_MARGIN,
            LAYOUT_MARGIN,
        )
        main_layout.setSpacing(LAYOUT_SPACING)

        # 1. Top buttons: Add Movie / Add Series + Toggle buttons (Info / Settings)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(BUTTON_SPACING)

        self.add_movie_button = LoadButton('  Add Movie')
        self.add_movie_button.clicked.connect(self._on_add_movie_clicked)
        button_layout.addWidget(self.add_movie_button)

        self.add_series_button = LoadButton('  Add Series')
        self.add_series_button.clicked.connect(self._on_add_series_clicked)
        button_layout.addWidget(self.add_series_button)

        button_layout.addStretch()

        # Stateful icon buttons on the right side (always clickable, visual state via enabled/disabled)
        self.info_button = StatefulIconButton(
            QIcon(str(self._get_resource_path(BUTTON_MEDIA_INFO_ICON_PATH)))
        )
        self.info_button.setToolTip('Show Media Info')
        self.info_button.clicked.connect(self._on_info_clicked)
        button_layout.addWidget(self.info_button)

        self.settings_button = StatefulIconButton(
            QIcon(str(self._get_resource_path(BUTTON_SETTINGS_ICON_PATH)))
        )
        self.settings_button.setToolTip('Settings')
        self.settings_button.clicked.connect(self._on_settings_clicked)
        button_layout.addWidget(self.settings_button)

        main_layout.addLayout(button_layout)

        # 2. File preview table
        self.file_table = FileTable()
        self.file_table.editing_started.connect(self._on_editing_started)
        self.file_table.save_requested.connect(self._on_save_requested)
        self.file_table.discard_requested.connect(self._on_discard_requested)
        self.file_table.itemSelectionChanged.connect(self._on_selection_changed)
        main_layout.addWidget(self.file_table, stretch=1)  # Stretch to fill available space

        # 3. Media Info Panel (collapsible, initially hidden)
        self.media_info_panel = MediaInfoPanel()
        main_layout.addWidget(self.media_info_panel, stretch=0)  # Fixed size when expanded

        # 4. Action buttons: Remove / Apply Changes
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.apply_button = ServiceButton('Apply Changes')
        self.apply_button.clicked.connect(self._on_apply_clicked)
        self.apply_button.setEnabled(False)
        action_layout.addWidget(self.apply_button)

        self.save_button = ServiceButton('Save Changes')
        self.save_button.clicked.connect(self._on_save_clicked)
        self.save_button.setEnabled(False)
        action_layout.addWidget(self.save_button)

        self.discard_button = ServiceButton('Discard Changes')
        self.discard_button.clicked.connect(self._on_discard_clicked)
        self.discard_button.setEnabled(False)
        action_layout.addWidget(self.discard_button)

        self.force_edit_button = CriticalButton('Force Edit')
        self.force_edit_button.clicked.connect(self._on_force_edit_clicked)
        self.force_edit_button.setEnabled(False)
        action_layout.addWidget(self.force_edit_button)

        self.remove_button = CriticalButton('Remove')
        self.remove_button.clicked.connect(self._on_remove_clicked)
        self.remove_button.setEnabled(False)
        action_layout.addWidget(self.remove_button)

        main_layout.addLayout(action_layout)

        # 5. Status bar
        self.status_bar = StatusBar()
        main_layout.addWidget(self.status_bar)

        # 6. Bottom buttons: Quit / Start Over
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.quit_button = ExitButton('Quit')
        self.quit_button.clicked.connect(self.close)
        bottom_layout.addWidget(self.quit_button)

        self.start_over_button = ExitButton('Start Over')
        self.start_over_button.clicked.connect(self._on_start_over_clicked)
        self.start_over_button.setEnabled(False)
        bottom_layout.addWidget(self.start_over_button)

        main_layout.addLayout(bottom_layout)

        # IMPORTANTE: Applica il tema DOPO aver creato tutti i widget
        self._apply_theme()

        # Load button icons AFTER theme application to prevent icons from being overwritten
        self._load_button_icons()

    def _center_window(self) -> None:
        """Center window on the primary screen."""
        screen = self.app.primaryScreen()
        size = screen.size()
        window_height = self.height()
        window_width = self.width()
        pos_h = (size.height() // 2) - (window_height // 2)
        pos_w = (size.width() // 2) - (window_width // 2)
        self.move(pos_w, pos_h)

    def _apply_theme(self) -> None:
        """Apply configured theme to application and refresh button styles.

        Gets theme from configuration, applies stylesheet to QApplication,
        and refreshes all button styles to reflect theme colors.
        """
        theme = get_theme(self.config.theme)
        apply_theme_to_app(self.app, theme)

        # Refresh button styles
        self.add_movie_button.style().unpolish(self.add_movie_button)
        self.add_movie_button.style().polish(self.add_movie_button)
        self.add_series_button.style().unpolish(self.add_series_button)
        self.add_series_button.style().polish(self.add_series_button)
        self.remove_button.style().unpolish(self.remove_button)
        self.remove_button.style().polish(self.remove_button)
        self.apply_button.style().unpolish(self.apply_button)
        self.apply_button.style().polish(self.apply_button)
        self.quit_button.style().unpolish(self.quit_button)
        self.quit_button.style().polish(self.quit_button)
        self.start_over_button.style().unpolish(self.start_over_button)
        self.start_over_button.style().polish(self.start_over_button)

    # ========================================================================
    # PRESENTER INTEGRATION (MVP Pattern)
    # ========================================================================

    def _connect_presenter_signals(self) -> None:
        """Connect all Presenter signals to View handler methods.

        Creates signal/slot connections for:
        - File processing signals (files_processed, file_updated, etc.)
        - UI update signals (button_states_changed, status_message_changed)
        - Session signals (session_reset, session_started)
        - Editing signals (editing_started, editing_completed)
        - Action result signals (rename_completed, conflicts_detected, etc.)
        """
        # File processing signals
        self.presenter.files_processed.connect(self._on_presenter_files_processed)
        self.presenter.file_updated.connect(self._on_presenter_file_updated)
        self.presenter.files_cleared.connect(self._on_presenter_files_cleared)

        # UI update signals
        self.presenter.button_states_changed.connect(
            self._on_presenter_button_states_changed
        )
        self.presenter.status_message_changed.connect(
            self._on_presenter_status_message_changed
        )

        # Session signals
        self.presenter.session_reset.connect(self._on_presenter_session_reset)

        # Editing signals
        self.presenter.editing_started.connect(self._on_presenter_editing_started)
        self.presenter.editing_completed.connect(self._on_presenter_editing_completed)

        # Action result signals
        self.presenter.rename_completed.connect(self._on_presenter_rename_completed)
        self.presenter.year_prompt_needed.connect(self._on_presenter_year_prompt_needed)
        self.presenter.conflicts_detected.connect(self._on_presenter_conflicts_detected)

    def _on_presenter_files_processed(self, file_data: list) -> None:
        """Handle files_processed signal from Presenter.

        Updates file table with newly processed file data.

        Args:
            file_data: List of FileProcessingData objects
        """
        logger.debug('_on_presenter_files_processed: count=%d', len(file_data))
        logger.debug('_on_presenter_files_processed: file_table._is_editing=%s', self.file_table._is_editing)
        # Update table with processed data
        self.file_table.set_file_data(file_data)

    def _on_presenter_file_updated(self, row: int, new_name: str, status) -> None:
        """Handle file_updated signal from Presenter.

        Updates table display after file edit is saved.

        Args:
            row: Index of updated file
            new_name: New filename
            status: Updated FileStatus
        """
        logger.debug(f"_on_presenter_file_updated: row={row}, new_name='{new_name}', status={status}")
        logger.debug(f"_on_presenter_file_updated: file_table._is_editing={self.file_table._is_editing}")
        # Update table with edited file
        self.file_table.complete_edit_save(row, new_name, status)

    def _on_presenter_files_cleared(self) -> None:
        """Handle files_cleared signal from Presenter.

        Clears table display and selection.
        """
        self.file_table.set_file_data([])
        self.file_table.clearSelection()

    def _on_presenter_button_states_changed(self, states: dict[str, bool]) -> None:
        """Handle button_states_changed signal from Presenter.

        Updates enabled/disabled state of all buttons based on application state.

        Args:
            states: Dictionary mapping button names to enabled state
        """
        self.add_movie_button.setEnabled(states.get('add_movie', True))
        self.add_series_button.setEnabled(states.get('add_series', True))
        self.apply_button.setEnabled(states.get('apply', False))
        self.remove_button.setEnabled(states.get('remove', False))
        self.force_edit_button.setEnabled(states.get('force_edit', False))
        self.save_button.setEnabled(states.get('save', False))
        self.discard_button.setEnabled(states.get('discard', False))
        self.start_over_button.setEnabled(states.get('start_over', False))
        # Note: info_button and settings_button are always clickable (StatefulIconButton)

    def _on_presenter_status_message_changed(self, message: str, msg_type) -> None:
        """Handle status_message_changed signal from Presenter.

        Updates status bar with new message and message type.

        Args:
            message: Status message text
            msg_type: MessageType (INFO, WARNING, ERROR, SUCCESS, PROCESSING)
        """
        self.status_bar.set_message(message, msg_type)

    def _on_presenter_session_reset(self) -> None:
        """Handle session_reset signal from Presenter.

        Clears table and selection when session is reset.
        """
        # Clear table and selection
        self.file_table.set_file_data([])
        self.file_table.clearSelection()

    def _on_presenter_editing_started(self, row: int) -> None:
        """Handle editing_started signal from Presenter.

        Placeholder for future editing UI updates if needed.

        Args:
            row: Index of file being edited
        """
        # Presenter ha già aggiornato SessionManager
        # Non serve fare nulla qui, i bottoni sono gestiti da button_states_changed
        pass

    def _on_presenter_editing_completed(self, row: int, saved: bool) -> None:
        """Handle editing_completed signal from Presenter.

        Restores table display if edit was discarded.

        Args:
            row: Index of file that was being edited
            saved: True if edit was saved, False if discarded
        """
        logger.debug('Presenter editing completed: row=%d, saved=%s', row, saved)
        if saved:
            logger.debug('Edit saved, table updated')
        else:
            logger.debug('Edit discarded, table restored')
            # IMPORTANTE: Informa FileTable del discard
            self.file_table.complete_edit_discard(row)

    def _on_presenter_rename_completed(
        self, success_count: int, total_count: int, errors: list
    ) -> None:
        """Handle rename_completed signal from Presenter.

        Displays result dialog showing number of successful renames and any errors.

        Args:
            success_count: Number of files successfully renamed
            total_count: Total number of files that had READY status
            errors: List of error messages
        """
        if errors:
            # Show errors
            error_msg = '\n'.join(errors[:5])
            if len(errors) > 5:
                error_msg += f"\n... and {len(errors) - 5} more errors"

            from .dialogs import show_error

            show_error(
                self,
                'Rename Errors',
                f"Renamed {success_count} out of {total_count} files.\n\n"
                f"Errors:\n{error_msg}",
            )
        else:
            # Show success
            show_info(
                self,
                'Renaming Complete',
                f"Successfully renamed {success_count} out of {total_count} file(s).",
            )

    def _on_presenter_year_prompt_needed(self, folder_name: str) -> None:
        """Handle year_prompt_needed signal from Presenter.

        Displays year input dialog for series, applies year if valid,
        or cancels series load if user cancels.

        Args:
            folder_name: Name of series folder for dialog display
        """
        year = prompt_series_year(self, folder_name)

        if year:
            # Apply year via Presenter
            self.presenter.handle_apply_series_year(year)
        else:
            # Utente ha cliccato Annulla → cleanup e torna in idle
            logger.info('User cancelled year input, clearing series')
            self.presenter.handle_cancel_series_load()

    def _on_presenter_conflicts_detected(self, conflicts: list[str]) -> None:
        """Handle conflicts_detected signal from Presenter.

        Displays warning dialog listing files that would overwrite existing files.

        Args:
            conflicts: List of conflicting filenames
        """
        conflict_list = '\n'.join(f"  - {name}" for name in conflicts[:10])
        if len(conflicts) > 10:
            conflict_list += f"\n  ... and {len(conflicts) - 10} more"

        show_warning(
            self,
            'File Conflicts Detected',
            f"The following files already exist in the target folder:\n\n"
            f"{conflict_list}\n\n"
            f"Cannot proceed with renaming to avoid overwriting.",
        )

    # ========================================================================
    # Event Handlers - File Selection
    # ========================================================================

    def _on_add_movie_clicked(self) -> None:
        """Handle Add Movie button click.

        Opens file dialog, saves selected directory, scans for video files,
        and delegates to Presenter for processing.
        """
        # Build filter string for video files
        extensions = get_video_extensions()
        filter_patterns = ' '.join(f"*{ext}" for ext in extensions)
        file_filter = f"Video files ({filter_patterns})"

        # Open file dialog
        start_dir = self.config.last_movie_directory
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 'Select Movie Files', start_dir, file_filter
        )

        if file_paths:
            # Save directory for next time
            self.config.last_movie_directory = os.path.dirname(file_paths[0])

            # Delegate to Presenter (NEW)
            self.presenter.handle_movie_selection(file_paths)

    def _on_add_series_clicked(self) -> None:
        """Handle Add Series button click.

        Opens folder dialog, saves selected directory, scans for video files,
        validates folder has videos, and delegates to Presenter for processing.
        """
        # Open dialog
        start_dir = self.config.last_series_directory
        folder_path = QFileDialog.getExistingDirectory(
            self, 'Select Series Folder', start_dir, QFileDialog.Option.ShowDirsOnly
        )

        if not folder_path:
            return

        # Save directory
        self.config.last_series_directory = folder_path

        # Show scanning message
        self.status_bar.set_message(
            '📄 Scanning folder for video files...', MessageType.PROCESSING
        )
        QApplication.processEvents()

        # Scan for video files
        video_files = scan_folder_for_videos(folder_path)

        if not video_files:
            show_warning(
                self,
                'No Video Files',
                f"The selected folder contains no video files.\n\n"
                f"Folder: {folder_path}\n"
                f"Supported formats: {', '.join(get_video_extensions())}",
            )
            self.status_bar.clear()
            return

        # Delegate to Presenter
        folder_name = os.path.basename(folder_path)
        self.presenter.handle_series_selection(video_files, folder_name)

    # ========================================================================
    # Event Handlers - Actions
    # ========================================================================

    def _on_editing_started(self, row: int) -> None:
        """Handle editing_started signal from FileTable.

        Delegates to Presenter to start editing session.

        Args:
            row: Index of file being edited
        """
        logger.debug(
            'Editing started event: row=%d, file_data_len=%d',
            row,
            len(self.file_table.file_data),
        )

        if row >= len(self.file_table.file_data):
            logger.warning(
                'Row %d >= file_data length %d, returning',
                row,
                len(self.file_table.file_data),
            )
            return

        # Get file info
        file_item = self.file_table.file_data[row]
        import os

        original_extension = os.path.splitext(file_item.original_name)[1]
        logger.debug(
            'File info: new_name=\'%s\', extension=\'%s\'',
            file_item.new_name,
            original_extension,
        )

        # Delegate to Presenter
        logger.debug('Delegating to presenter.handle_editing_started()')
        self.presenter.handle_editing_started(
            row, file_item.new_name, original_extension
        )
        logger.debug('Editing started handled')

    def _on_save_requested(self, row: int, edited_text: str) -> None:
        """Handle save_requested signal from FileTable.

        Delegates to Presenter to validate and save edit.

        Args:
            row: Index of file being edited
            edited_text: New filename text from user
        """
        # Delegate to Presenter
        self.presenter.handle_save_edit(row, edited_text)

    def _on_discard_requested(self, row: int) -> None:
        """Handle discard_requested signal from FileTable (ESC or click outside).

        Delegates to Presenter to discard edit and restore original filename.

        Args:
            row: Index of file whose edit is being discarded
        """
        logger.debug('Discard requested: row=%d', row)

        # Delegate to Presenter
        self.presenter.handle_discard_edit(row)
        logger.debug('Discard handled')

    def _on_selection_changed(self) -> None:
        """Handle table selection change.

        Prevents updates if in editing mode, otherwise delegates to Presenter.
        Updates media info panel if it's currently open.
        """
        # Don't update if in editing mode
        if self.presenter.session_manager.is_editing():
            return

        selected_row = self.file_table.currentRow()

        # Delegate to Presenter - it will update button states and status message
        self.presenter.handle_selection_changed(selected_row)

        # If media info panel is open, update it with new selection
        if self.media_info_panel.is_expanded():
            if selected_row >= 0:
                # Valid selection - update panel content
                metadata = self.presenter.get_selected_file_metadata()
                if metadata:
                    self.media_info_panel.update_info(metadata)
                else:
                    # Failed to get metadata - show no selection message
                    self.media_info_panel.show_no_selection()
            else:
                # No selection - show no selection message (don't close panel)
                self.media_info_panel.show_no_selection()

    # Button action function
    #
    # Button force edit
    def _on_force_edit_clicked(self) -> None:
        """Handle Force Edit button click.

        Shows confirmation dialog and delegates to Presenter to force edit
        ALREADY_NORMALIZED files by changing their status to READY.
        """
        selected_row = self.file_table.currentRow()

        if selected_row is None:
            show_info(self, 'No Selection', 'Please select a file to force edit.')
            return

        # Get confirmation message from Presenter
        message = self.presenter.get_force_edit_confirmation_message()

        # Confirm with user (using warning dialog for dangerous operation)
        if not confirm_dangerous_action(self, 'Confirm Force Edit', message):
            return

        # Delegate to Presenter
        self.presenter.handle_force_edit(selected_row)

    # Button remove
    def _on_remove_clicked(self) -> None:
        """Handle Remove button click.

        Validates selection, shows confirmation dialog, and delegates to Presenter.
        Closes media info panel if it was open for the removed file.
        """
        selected_row = self.file_table.currentRow()

        if selected_row is None:
            show_info(self, 'No Selection', 'Please select a file to remove.')
            return

        # Delegate to Presenter
        self.presenter.handle_remove_file(selected_row)

        # Close media info panel after file removal
        # (selection will be lost or changed, panel will update via selection change)

    # Button save
    def _on_save_clicked(self) -> None:
        """Handle Save button click.

        Triggers save of current edit in FileTable.
        """
        self.file_table.save_current_edit()

    # Button discard
    def _on_discard_clicked(self) -> None:
        """Handle Discard button click.

        Triggers discard of current edit in FileTable.
        """
        self.file_table.discard_current_edit()

    # Button Apply
    def _on_apply_clicked(self) -> None:
        """Handle Apply Changes button click.

        Shows confirmation dialog and delegates to Presenter to apply renames.
        Closes media info panel after successful rename operation.
        """
        # Confirm with user
        if not confirm_action(
            self,
            'Confirm Rename',
            'Are you sure you want to rename these files?\n\n'
            'This action will modify filenames on disk.',
        ):
            return

        # Delegate to Presenter
        self.presenter.handle_apply_renames()

        # Close media info panel after applying renames
        # (files will be removed from list, selection will be lost)
        if self.media_info_panel.is_expanded():
            self._close_media_info_panel()

    def _on_start_over_clicked(self) -> None:
        """Handle Start Over button click.

        Shows confirmation if files exist, then delegates to Presenter for reset.
        Closes media info panel since all files will be removed.
        """
        if self.presenter.get_file_count() > 0:
            if not confirm_action(
                self, 'Start Over', 'Discard current changes and start over?'
            ):
                return

        # Delegate to Presenter
        self.presenter.handle_reset_session()

        # Close media info panel after session reset
        if self.media_info_panel.is_expanded():
            self._close_media_info_panel()

    # Stateful icon button - Info
    def _on_info_clicked(self) -> None:
        """Handle Info button click.

        Button toggles its visual state automatically (via StatefulIconButton).
        Opens/closes media info panel based on button state.
        """
        if self.info_button.is_active():
            # Button is now active (colored) - open panel
            metadata = self.presenter.get_selected_file_metadata()
            if metadata:
                # File selected - show metadata
                self.media_info_panel.update_info(metadata)
            else:
                # No file selected - show message
                self.media_info_panel.show_no_selection()
            self.media_info_panel.expand()
        else:
            # Button is now inactive (greyscale) - close panel
            self.media_info_panel.collapse()

    def _close_media_info_panel(self) -> None:
        """Close media info panel and reset button state.

        This is called automatically when conditions require closing the panel
        (e.g., no selection, file removed, session reset).
        """
        self.media_info_panel.collapse()
        self.info_button.set_active(False)

    # Stateful icon button - Settings
    def _on_settings_clicked(self) -> None:
        """Handle Settings button click.

        Button toggles its visual state automatically (via StatefulIconButton).
        Opens/closes settings panel based on button state.
        """
        if self.settings_button.is_active():
            # Button is now active (colored) - open settings panel
            # TODO: Implement settings panel
            logger.debug('Settings panel opened')
        else:
            # Button is now inactive (greyscale) - close settings panel
            # TODO: Implement settings panel
            logger.debug('Settings panel closed')

    # ========================================================================
    # Window state management
    # ========================================================================

    def _restore_window_state(self) -> None:
        """Restore window geometry and state from configuration.

        Restores window size, position, and maximized state. Centers window
        if no saved position available.
        """
        # Restore size
        self.resize(self.config.window.width, self.config.window.height)

        # Restore position if available
        if self.config.window.x is not None and self.config.window.y is not None:
            self.move(self.config.window.x, self.config.window.y)
        else:
            # Center window if no saved position
            self._center_window()

        # Restore maximized state
        if self.config.window.maximized:
            self.showMaximized()

    def _save_window_state(self) -> None:
        """Save current window geometry and state to configuration.

        Saves window size, position, and maximized state for restoration
        on next application launch.
        """
        # Save window geometry
        self.config.window.width = self.width()
        self.config.window.height = self.height()
        self.config.window.x = self.x()
        self.config.window.y = self.y()
        self.config.window.maximized = self.isMaximized()

        # Save configuration to file
        self.config.save(get_config_file())

    # Close event override

    def closeEvent(self, event) -> None:
        """Handle window close event.

        Saves window state before closing and quits application.

        Args:
            event: QCloseEvent
        """
        # Save window state before closing
        self._save_window_state()
        self.app.quit()
