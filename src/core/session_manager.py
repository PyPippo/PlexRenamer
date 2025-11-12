"""Session Manager - Centralized application state management.

This module contains the SessionManager class which manages all application
state including editing mode, selection, UI state, and session lifecycle.

Main responsibilities:
- Track application state (IDLE, FILES_LOADED, EDITING)
- Manage editing mode transitions
- Maintain selection state
- Control UI state and button availability
- Validate state transitions

The SessionManager is the single source of truth for application state,
ensuring consistency across the View and Model layers.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum, auto

logger = logging.getLogger(__name__)


class AppState(Enum):
    """Application state enumeration.

    Represents the top-level application state determining what operations
    are available to the user.

    States:
        IDLE: No files loaded, initial state
        FILES_LOADED: Files loaded, not currently editing
        EDITING: In edit mode for a file
    """

    IDLE = auto()  # Nessun file caricato
    FILES_LOADED = auto()  # File caricati, non in editing
    EDITING = auto()  # In modalità editing


@dataclass
class EditingState:
    """Current editing session state.

    Tracks which file is being edited and preserves original values
    for rollback functionality.
    """

    is_active: bool = False
    row: Optional[int] = None
    original_value: str = ''
    original_extension: str = ''

    def reset(self) -> None:
        """Reset editing state to inactive with no file selected."""
        self.is_active = False
        self.row = None
        self.original_value = ''
        self.original_extension = ''


@dataclass
class SelectionState:
    """Current table selection state.

    Tracks which row (if any) is currently selected in the file table.
    """

    selected_row: Optional[int] = None

    def has_selection(self) -> bool:
        """Check if a row is currently selected.

        Returns:
            True if a row is selected, False otherwise
        """
        return self.selected_row is not None

    def clear(self) -> None:
        """Clear the current selection."""
        self.selected_row = None


@dataclass
class ModeState:
    """Processing mode and lock state.

    Tracks whether the application is in film or series mode, and whether
    mode changes are currently allowed (locked when files are loaded).
    """

    current_mode: Optional[str] = None  # 'film' o 'series'
    is_locked: bool = False  # True quando ci sono file caricati

    def lock(self) -> None:
        """Lock the mode to prevent switching.

        Called when files are loaded to prevent user from changing between
        film and series modes mid-session.
        """
        self.is_locked = True

    def unlock(self) -> None:
        """Unlock the mode and reset to None.

        Allows mode switching again after session reset.
        """
        self.is_locked = False
        self.current_mode = None


@dataclass
class UIState:
    """UI component state and visibility.

    Tracks button enabled/disabled states and status bar message.
    Used to synchronize View button states with application state.
    """

    # Button states
    add_movie_enabled: bool = True
    add_series_enabled: bool = True
    apply_enabled: bool = False
    remove_enabled: bool = False
    save_enabled: bool = False
    discard_enabled: bool = False
    start_over_enabled: bool = False

    # Status bar
    status_message: str = 'Ready to process files'
    status_type: str = 'INFO'  # INFO, WARNING, ERROR, SUCCESS, PROCESSING

    def enable_mode_selection(self) -> None:
        """Enable Add Movie and Add Series buttons."""
        self.add_movie_enabled = True
        self.add_series_enabled = True

    def disable_mode_selection(self) -> None:
        """Disable Add Movie and Add Series buttons."""
        self.add_movie_enabled = False
        self.add_series_enabled = False

    def enable_editing_mode(self) -> None:
        """Enable Save and Discard buttons, disable Apply and Remove."""
        self.save_enabled = True
        self.discard_enabled = True
        self.apply_enabled = False
        self.remove_enabled = False

    def disable_editing_mode(self) -> None:
        """Disable Save and Discard buttons."""
        self.save_enabled = False
        self.discard_enabled = False


@dataclass
class SessionData:
    """Complete session state snapshot.

    Single source of truth containing all application state information.
    Used by SessionManager to track and validate state changes.
    """

    app_state: AppState = AppState.IDLE
    mode: ModeState = field(default_factory=ModeState)
    editing: EditingState = field(default_factory=EditingState)
    selection: SelectionState = field(default_factory=SelectionState)
    ui: UIState = field(default_factory=UIState)

    # Metadata
    file_count: int = 0
    last_action: str = 'initialized'

    def to_dict(self) -> dict[str, Any]:
        """Export session state as dictionary for debugging and logging.

        Returns:
            Dictionary representation of current session state
        """
        return {
            'app_state': self.app_state.name,
            'mode': self.mode.current_mode,
            'is_editing': self.editing.is_active,
            'selected_row': self.selection.selected_row,
            'file_count': self.file_count,
            'last_action': self.last_action,
        }


class SessionManager:
    """Manages application session state and transitions.

    Central authority for all application state, ensuring consistency and
    validating state transitions. Provides query methods for checking state
    and methods for transitioning between states.

    Responsibilities:
    - Maintain current application state (IDLE, FILES_LOADED, EDITING)
    - Manage editing mode with enter/exit validation
    - Maintain selection state
    - Control UI state and button availability
    - Validate state transitions
    - Maintain state history for debugging

    Does NOT handle:
    - File processing business logic
    - GUI operations and dialogs
    - File data processing
    """

    def __init__(self) -> None:
        """Initialize the session manager with IDLE state."""
        self.session = SessionData()
        self._state_history: list[AppState] = [AppState.IDLE]

    # ========================================================================
    # LIFECYCLE METHODS - Gestione ciclo di vita sessione
    # ========================================================================

    def start_session(self, mode: str, file_count: int) -> None:
        """Start a new session with loaded files.

        Transitions from IDLE to FILES_LOADED state, locks the mode,
        and updates UI state accordingly.

        Args:
            mode: Processing mode - 'film' or 'series'
            file_count: Number of files loaded
        """
        self.session.mode.current_mode = mode
        self.session.mode.lock()
        self.session.file_count = file_count
        self.session.app_state = AppState.FILES_LOADED
        self.session.last_action = f"loaded_{file_count}_files"

        # Update UI state
        self.session.ui.disable_mode_selection()
        self.session.ui.start_over_enabled = True

        self._add_to_history(AppState.FILES_LOADED)

    def reset_session(self) -> None:
        """Perform complete session reset to IDLE state.

        Clears all state including editing, selection, and mode.
        Returns to initial state.
        """
        self.session = SessionData()
        self._state_history = [AppState.IDLE]
        self.session.last_action = 'reset'

    def update_file_count(self, count: int) -> None:
        """Update file count and auto-reset if no files remain.

        Automatically triggers session reset if count reaches zero.

        Args:
            count: New file count (after removals or renames)
        """
        self.session.file_count = count

        # Se non ci sono più file, reset automatico
        if count == 0:
            self.reset_session()

    # ========================================================================
    # EDITING STATE MANAGEMENT
    # ========================================================================

    def start_editing(
        self, row: int, original_value: str, original_extension: str
    ) -> None:
        """Start editing a file row.

        Transitions to EDITING state and stores original values for rollback.
        Updates UI state to enable Save/Discard and disable other operations.

        Args:
            row: Row index of file being edited
            original_value: Original filename for rollback if edit cancelled
            original_extension: Original file extension

        Raises:
            RuntimeError: If already in editing mode
        """
        logger.debug(
            'Starting editing session: row=%d, original_value=\'%s\', extension=\'%s\'',
            row,
            original_value,
            original_extension,
        )
        logger.debug(
            'Editing state before: is_active=%s, row=%s',
            self.session.editing.is_active,
            self.session.editing.row,
        )

        if self.session.editing.is_active:
            logger.error('Already in editing mode')
            raise RuntimeError('Already in editing mode')

        self.session.editing.is_active = True
        self.session.editing.row = row
        self.session.editing.original_value = original_value
        self.session.editing.original_extension = original_extension
        logger.debug('Editing row set to: %d', row)

        self.session.app_state = AppState.EDITING
        self.session.last_action = f"start_edit_row_{row}"
        logger.debug('App state changed to: EDITING')

        # Update UI state
        self.session.ui.enable_editing_mode()

        self._add_to_history(AppState.EDITING)
        logger.debug(
            'Editing state after: is_active=%s, row=%s',
            self.session.editing.is_active,
            self.session.editing.row,
        )

    def complete_editing(self, saved: bool = True) -> None:
        """Complete the current editing session.

        Transitions from EDITING to FILES_LOADED state. Resets editing state
        and updates UI accordingly.

        Args:
            saved: True if edit was saved, False if cancelled
        """
        logger.debug('Completing editing: saved=%s', saved)
        logger.debug(
            'Editing state before: is_active=%s, row=%s',
            self.session.editing.is_active,
            self.session.editing.row,
        )

        if not self.session.editing.is_active:
            logger.warning('Not in editing mode, returning')
            return

        row = self.session.editing.row
        action = 'saved' if saved else 'discarded'
        logger.debug('Editing row %d will be %s', row, action)

        self.session.editing.reset()
        logger.debug('Editing state reset')

        self.session.app_state = AppState.FILES_LOADED
        self.session.last_action = f"edit_{action}_row_{row}"

        # Update UI state
        self.session.ui.disable_editing_mode()

        self._add_to_history(AppState.FILES_LOADED)
        logger.debug('Editing completed')

    def get_editing_info(self) -> tuple[int | None, str, str]:
        """Get information about current editing session.

        Returns:
            Tuple of (row, original_value, original_extension) or
            (None, '', '') if not currently editing
        """
        return (
            self.session.editing.row,
            self.session.editing.original_value,
            self.session.editing.original_extension,
        )

    # ========================================================================
    # SELECTION STATE MANAGEMENT
    # ========================================================================

    def set_selection(self, row: int | None) -> None:
        """Set the current table selection.

        Args:
            row: Row index to select, or None to deselect
        """
        self.session.selection.selected_row = row
        self.session.last_action = (
            f"selected_row_{row}' if row is not None else 'deselected"
        )

    def clear_selection(self) -> None:
        """Clear the current selection."""
        self.session.selection.clear()
        self.session.last_action = 'selection_cleared'

    def get_selected_row(self) -> int | None:
        """Get the currently selected row.

        Returns:
            Row index if a row is selected, None otherwise
        """
        return self.session.selection.selected_row

    def has_selection(self) -> bool:
        """Check if a row is currently selected.

        Returns:
            True if a row is selected, False otherwise
        """
        return self.session.selection.has_selection()

    # ========================================================================
    # UI STATE MANAGEMENT
    # ========================================================================

    def update_ui_state(
        self,
        apply_enabled: bool | None = None,
        remove_enabled: bool | None = None,
        status_message: str | None = None,
        status_type: str | None = None,
    ) -> None:
        """Update UI state (button availability and status messages).

        Only provided parameters are updated; others remain unchanged.

        Args:
            apply_enabled: Enable/disable Apply Changes button
            remove_enabled: Enable/disable Remove button
            status_message: Status bar message text
            status_type: Status message type (INFO, WARNING, ERROR, SUCCESS, PROCESSING)
        """
        if apply_enabled is not None:
            self.session.ui.apply_enabled = apply_enabled

        if remove_enabled is not None:
            self.session.ui.remove_enabled = remove_enabled

        if status_message is not None:
            self.session.ui.status_message = status_message

        if status_type is not None:
            self.session.ui.status_type = status_type

    def get_ui_state(self) -> UIState:
        """Get the current UI state.

        Returns:
            Current UIState object with all button and message states
        """
        return self.session.ui

    # ========================================================================
    # QUERY METHODS - Interrogazione stato
    # ========================================================================

    def is_idle(self) -> bool:
        """Check if application is in IDLE state.

        Returns:
            True if state is IDLE, False otherwise
        """
        return self.session.app_state == AppState.IDLE

    def has_files_loaded(self) -> bool:
        """Check if files are loaded in the current session.

        Returns:
            True if in FILES_LOADED or EDITING state, False otherwise
        """
        return self.session.app_state in [AppState.FILES_LOADED, AppState.EDITING]

    def is_editing(self) -> bool:
        """Check if currently in editing mode.

        Returns:
            True if in EDITING state, False otherwise
        """
        result = self.session.editing.is_active
        logger.debug('is_editing() = %s', result)
        return result

    def get_editing_row(self) -> int | None:
        """Get the row currently being edited.

        Returns:
            Row index if editing, None otherwise
        """
        return self.session.editing.row

    def is_mode_locked(self) -> bool:
        """Check if mode switching is locked.

        Returns:
            True if mode is locked (files loaded), False if can switch
        """
        return self.session.mode.is_locked

    def get_current_mode(self) -> str | None:
        """Get the current processing mode.

        Returns:
            'film' or 'series' if mode set, None if in IDLE state
        """
        return self.session.mode.current_mode

    def get_file_count(self) -> int:
        """Get the number of files in current session.

        Returns:
            File count (0 if no session)
        """
        return self.session.file_count

    def get_app_state(self) -> AppState:
        """Get the current application state.

        Returns:
            Current AppState (IDLE, FILES_LOADED, or EDITING)
        """
        return self.session.app_state

    def get_last_action(self) -> str:
        """Get the last action performed for debugging.

        Returns:
            Description of the last state change
        """
        return self.session.last_action

    # ========================================================================
    # VALIDATION METHODS
    # ========================================================================

    def can_start_editing(self) -> bool:
        """Check if editing can be started in current state.

        Editing is allowed only in FILES_LOADED state when not already editing.

        Returns:
            True if can start editing, False otherwise
        """
        result = (
            self.session.app_state == AppState.FILES_LOADED
            and not self.session.editing.is_active
        )
        logger.debug(
            'can_start_editing() = %s (app_state=%s)',
            result,
            self.session.app_state.name,
        )
        return result

    def can_apply_changes(self) -> bool:
        """Check if rename changes can be applied in current state.

        Apply is allowed only when files are loaded and not editing.

        Returns:
            True if can apply changes, False otherwise
        """
        return (
            self.session.app_state == AppState.FILES_LOADED
            and self.session.file_count > 0
            and not self.session.editing.is_active
        )

    def can_remove_file(self) -> bool:
        """Check if a file can be removed in current state.

        File removal requires a selection and not being in edit mode.

        Returns:
            True if a file can be removed, False otherwise
        """
        return (
            self.session.app_state == AppState.FILES_LOADED
            and self.session.selection.has_selection()
            and not self.session.editing.is_active
        )

    def can_change_mode(self) -> bool:
        """Check if processing mode can be changed.

        Mode changes are only allowed when not locked (IDLE state).

        Returns:
            True if mode can be changed, False if locked
        """
        return not self.session.mode.is_locked

    # ========================================================================
    # HISTORY MANAGEMENT (opzionale, per future undo/redo)
    # ========================================================================

    def _add_to_history(self, state: AppState) -> None:
        """Add a state to the history for debugging.

        Maintains a rolling history limited to 50 states.

        Args:
            state: AppState to add to history
        """
        self._state_history.append(state)
        # Limita history a 50 elementi
        if len(self._state_history) > 50:
            self._state_history.pop(0)

    def get_state_history(self) -> list[AppState]:
        """Get the history of state transitions.

        Returns:
            Copy of state history list (maximum 50 entries)
        """
        return self._state_history.copy()

    # ========================================================================
    # DEBUG & LOGGING
    # ========================================================================

    def print_state(self) -> None:
        """Print current session state to stdout for debugging."""
        print('\n=== SESSION STATE ===')
        state_dict = self.session.to_dict()
        for key, value in state_dict.items():
            print(f"{key:20s}: {value}")
        print('====================\n')

    def export_state(self) -> dict[str, Any]:
        """Export complete session state as dictionary.

        Returns:
            Dictionary representation of current session state
        """
        return self.session.to_dict()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    # Example of how to use SessionManager

    manager = SessionManager()

    # 1. Initial state
    print('Initial state:')
    manager.print_state()
    assert manager.is_idle()
    assert manager.can_change_mode()

    # 2. Load files
    manager.start_session('film', 5)
    print('After loading files:')
    manager.print_state()
    assert manager.has_files_loaded()
    assert manager.is_mode_locked()
    assert not manager.can_change_mode()

    # 3. Selection
    manager.set_selection(2)
    assert manager.has_selection()
    assert manager.get_selected_row() == 2

    # 4. Start editing
    if manager.can_start_editing():
        manager.start_editing(2, 'Movie (2024).mkv', '.mkv')
        print('During editing:')
        manager.print_state()
        assert manager.is_editing()
        assert not manager.can_apply_changes()

    # 5. Complete editing
    manager.complete_editing(saved=True)
    print('After editing:')
    manager.print_state()
    assert not manager.is_editing()
    assert manager.can_apply_changes()

    # 6. Reset
    manager.reset_session()
    print('After reset:')
    manager.print_state()
    assert manager.is_idle()
