"""App Presenter - MVP pattern coordinator.

This module contains the AppPresenter class which coordinates interactions
between View (GUI) and Model (Business Logic). It manages application state,
handles user events, and updates the view through signals.
"""

import re
import logging
from typing import Optional
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

from ..core.file_processor import FileProcessor
from ..core.session_manager import SessionManager, AppState
from ..core._utility import validate_year
from ..models import (
    FileContentType,
    FileProcessingData,
    FileStatus,
    MessageType,
    DEFAULT_YEAR_PLACEHOLDER,
    MIN_VALID_YEAR,
    MAX_VALID_YEAR,
    FILE_CONTENT_TYPE_SERIES,
    FILE_CONTENT_TYPE_FILM,
)


class AppPresenter(QObject):
    """MVP Presenter coordinating View and Model interactions.

    Central coordinator between View (MainWindow, FileTable) and Model
    (FileProcessor, SessionManager). Manages application state, handles user
    events, validates state transitions, and updates the view through signals.

    Responsibilities:
    - Coordinate interactions between View and Model
    - Manage application state transitions
    - Validate user actions before processing
    - Emit signals to update View when state changes
    - Handle complex business logic workflows

    Does NOT handle:
    - GUI rendering or widget creation
    - Direct file system operations
    - Low-level file processing

    See docs/dev/signal_flows.md for detailed signal flow diagrams.
    """

    # ========================================================================
    # SIGNALS - Comunicazione verso la View
    # ========================================================================

    # File processing signals
    # ────────────────────────

    files_processed = Signal(list)
    """List[FileProcessingData] - Emitted when files are processed and ready.
    
    Emitted by: handle_movie_selection(), handle_series_selection(),
                handle_apply_series_year(), handle_remove_file()
    Connected to: MainWindow._on_presenter_files_processed()
    """

    file_updated = Signal(int, str, object)
    """(row: int, new_name: str, status: FileStatus) - Single file updated.
    
    Emitted by: handle_save_edit()
    Connected to: MainWindow._on_presenter_file_updated()
    """

    files_cleared = Signal()
    """Emitted when all files are cleared.
    
    Emitted by: handle_reset_session()
    Connected to: MainWindow._on_presenter_files_cleared()
    """

    # UI update signals
    # ─────────────────

    mode_changed = Signal(str)
    """str - Processing mode changed ('film' or 'series').
    
    Emitted by: handle_movie_selection(), handle_series_selection()
    """

    button_states_changed = Signal(dict)
    """Dict[str, bool] - Button enabled/disabled states.
    
    Keys: 'add_movie', 'add_series', 'apply', 'remove', 'save', 'discard', 'start_over'
    Emitted by: All handle_*() methods, _update_button_states()
    Connected to: MainWindow._on_presenter_button_states_changed()
    """

    status_message_changed = Signal(str, object)
    """(message: str, msg_type: MessageType) - Status bar message.
    
    Emitted by: _emit_statistics_message(), handle_apply_renames(), others
    Connected to: MainWindow._on_presenter_status_message_changed()
    """

    # Session signals
    # ───────────────

    session_started = Signal(str, int)
    """(mode: str, file_count: int) - New session started.
    
    Emitted by: handle_movie_selection(), handle_apply_series_year()
    """

    session_reset = Signal()
    """Emitted when session is reset (Start Over).
    
    Emitted by: handle_reset_session()
    Connected to: MainWindow._on_presenter_session_reset()
    """

    # Editing signals
    # ───────────────

    editing_started = Signal(int)
    """int - Row index being edited.
    
    Emitted by: handle_editing_started()
    Connected to: MainWindow._on_presenter_editing_started()
    """

    editing_completed = Signal(int, bool)  # (row, saved)
    """bool - True if saved, False if discarded.
    
    Emitted by: handle_save_edit(), handle_discard_edit()
    Connected to: MainWindow._on_presenter_editing_completed()
    """

    # Action result signals
    # ─────────────────────

    rename_completed = Signal(int, int, list)
    """(success: int, total: int, errors: list[str]) - Rename results.
    
    Emitted by: handle_apply_renames()
    Connected to: MainWindow._on_presenter_rename_completed()
    """

    year_prompt_needed = Signal(str)
    """str - Folder name for year dialog.
    
    Emitted by: handle_series_selection()
    Connected to: MainWindow._on_year_prompt_needed()
    """

    conflicts_detected = Signal(list)
    """List[str] - Conflicting file names.
    
    Emitted by: handle_apply_renames()
    Connected to: MainWindow._on_presenter_conflicts_detected()
    """

    def __init__(self) -> None:
        """Initialize the presenter with FileProcessor and SessionManager."""
        super().__init__()

        # Model components
        self.file_processor = FileProcessor()
        self.session_manager = SessionManager()

    # ========================================================================
    # FILE SELECTION HANDLERS - Gestione selezione file
    # ========================================================================

    def handle_movie_selection(self, file_paths: list[str]) -> None:
        """Handle movie file selection and processing.

        Workflow:
        1. Set processor mode to 'film'
        2. Process all selected files through FileAnalyzer
        3. Start a new session
        4. Update View with processed files
        5. Update UI state (buttons, status message)

        Args:
            file_paths: List of file paths selected by user
        """
        # Set mode nel processor
        self.file_processor.set_mode('film')

        # Process files
        processed_data = self.file_processor.process_files(file_paths)

        # Start session
        self.session_manager.start_session('film', len(processed_data))

        # Notify View
        self.mode_changed.emit('film')
        self.files_processed.emit(processed_data)
        self.session_started.emit('film', len(processed_data))

        # Update UI state
        self._update_ui_after_file_load()

    def handle_series_selection(self, file_paths: list[str], folder_name: str) -> None:
        """Handle series folder selection and processing.

        Workflow:
        1. Set processor mode to 'series'
        2. Process all video files found in folder
        3. Start a new session
        4. Check if year input is needed for any files
        5. If needed, emit year_prompt_needed signal
        6. Update View and UI state

        Args:
            file_paths: List of video file paths found in folder
            folder_name: Name of the folder (for year dialog)
        """
        # Set mode nel processor
        self.file_processor.set_mode('series')

        # Process files
        processed_data = self.file_processor.process_files(file_paths)

        # Start session
        self.session_manager.start_session('series', len(processed_data))

        # Notify View
        self.mode_changed.emit('series')
        self.files_processed.emit(processed_data)
        self.session_started.emit('series', len(processed_data))

        # Check if year input is needed
        if self.file_processor.needs_year_input():
            # Emit signal - View mostrerà dialog
            self.year_prompt_needed.emit(folder_name)
        else:
            # Update UI state
            self._update_ui_after_file_load()

    # ========================================================================
    # EDITING HANDLERS - Gestione editing
    # ========================================================================

    def handle_editing_started(
        self, row: int, original_value: str, original_extension: str
    ) -> None:
        """Handle the start of file editing.

        Validates that editing can start in current state, updates SessionManager,
        and notifies View through signal.

        Args:
            row: Index of file being edited
            original_value: Original filename for rollback
            original_extension: Original file extension
        """
        logger.debug(
            'Editing started: row=%d, original_value=\'%s\', extension=\'%s\'',
            row,
            original_value,
            original_extension,
        )
        logger.debug(
            'Before: is_editing=%s, editing_row=%s',
            self.session_manager.is_editing(),
            self.session_manager.get_editing_row(),
        )

        can_start = self.session_manager.can_start_editing()
        logger.debug('can_start_editing() = %s', can_start)

        if not can_start:
            logger.warning('Cannot start editing, returning')
            return

        logger.debug('Starting editing session')
        # Update session state
        self.session_manager.start_editing(row, original_value, original_extension)
        logger.debug('Editing session started')

        logger.debug(
            'After: is_editing=%s, editing_row=%s',
            self.session_manager.is_editing(),
            self.session_manager.get_editing_row(),
        )

        logger.debug('Emitting editing_started signal')
        # Notify View
        self.editing_started.emit(row)
        logger.debug('Signal emitted')

        logger.debug('Updating button states')
        # Update UI state
        self._update_button_states()
        logger.debug('handle_editing_started finished')

    def handle_save_edit(self, row: int, edited_text: str) -> None:
        """Handle saving an edited filename.

        Comprehensive validation and processing workflow:
        1. Clean placeholder text from input
        2. Validate episode number wasn't changed (series only)
        3. Reconstruct filename with extension
        4. Reprocess through FileAnalyzer
        5. Validate title is not empty (series)
        6. Validate year format (series)
        7. Update duplicate detection
        8. Propagate changes to all episodes (series)
        9. Complete editing session
        10. Update View with results

        Automatic discards on validation failures with user-friendly error messages.

        Args:
            row: Index of file being edited
            edited_text: New filename text (without extension)
        """
        if not self.session_manager.is_editing():
            return

        # Get editing info from session
        editing_row, original_value, original_ext = (
            self.session_manager.get_editing_info()
        )

        # Clean placeholder text
        cleaned_text = self._clean_placeholder_text(edited_text)

        # NUOVO: Se siamo in modalità series, verifica che E## non sia stato modificato
        if self.file_processor.current_mode == FILE_CONTENT_TYPE_SERIES:
            # Estrai E## dal nome originale e da quello editato
            original_episode = self._extract_episode_number(original_value)
            edited_episode = self._extract_episode_number(cleaned_text)

            if original_episode != edited_episode:
                # E## è stato modificato → DISCARD automatico
                logger.warning(
                    f"Episode number changed from {original_episode} to {edited_episode}, discarding"
                )

                # IMPORTANTE: Ripristina new_name originale nel FileProcessor
                original_full_name = original_value + original_ext
                self.file_processor.file_data[row].new_name = original_full_name

                # Mostra messaggio
                self.status_message_changed.emit(
                    f"❌ Cannot change episode number (E##). Edit discarded.",
                    MessageType.ERROR,
                )

                # Complete editing come discard
                self.session_manager.complete_editing(saved=False)
                self.editing_completed.emit(row, False)
                self._update_button_states()
                return

        # Reconstruct filename with extension
        reconstructed_name = cleaned_text + original_ext

        # IMPORTANTE: Salva status originale PRIMA del reprocess
        # In caso di DISCARD automatico, dobbiamo ripristinarlo
        original_status = self.file_processor.file_data[row].status

        # Reprocess file
        try:
            updated_item = self.file_processor.reprocess_edited_file(
                row, reconstructed_name
            )

            # NUOVO: Verifica che il titolo non sia vuoto dopo normalizzazione
            if self.file_processor.current_mode == FILE_CONTENT_TYPE_SERIES:
                # Estrai la parte del titolo (prima di " - S##E##")
                # Formato: "Title (YYYY) - S##E## - Episode"
                title_match = re.match(
                    r'^(.+?)\s*-\s*[Ss]\d{1,2}[Ee]\d{1,2}', updated_item.new_name
                )
                if title_match:
                    title_part = title_match.group(1).strip()
                    # Rimuovi anno per vedere se rimane qualcosa
                    title_without_year = re.sub(r'\(\d{4}\)', '', title_part).strip()

                    if not title_without_year:
                        # Titolo vuoto (solo anno) → DISCARD
                        logger.warning(
                            "Empty title after normalization (only year), discarding edit"
                        )

                        # Ripristina new_name E status originali
                        original_full_name = original_value + original_ext
                        self.file_processor.file_data[row].new_name = original_full_name
                        self.file_processor.file_data[row].status = original_status

                        self.status_message_changed.emit(
                            "❌ Series title cannot be empty. Edit discarded.",
                            MessageType.ERROR,
                        )
                        self.session_manager.complete_editing(saved=False)
                        self.editing_completed.emit(row, False)
                        self._update_button_states()
                        return

            # NUOVO: Verifica che l'anno sia valido prima di procedere
            if self.file_processor.current_mode == FILE_CONTENT_TYPE_SERIES:
                # Estrai anno dal nome processato
                year_pattern = r'\((\d{4})\)'
                year_match = re.search(year_pattern, updated_item.new_name)

                if year_match:
                    year_str = year_match.group(1)
                    # Valida anno
                    if not validate_year(year_str):
                        # Anno invalido → DISCARD automatico
                        logger.warning(f"Invalid year {year_str} in edit, discarding")

                        # Ripristina new_name E status originali
                        original_full_name = original_value + original_ext
                        self.file_processor.file_data[row].new_name = original_full_name
                        self.file_processor.file_data[row].status = original_status

                        # Mostra messaggio all'utente
                        self.status_message_changed.emit(
                            f"❌ Invalid year '{year_str}'. Must be between {MIN_VALID_YEAR}-{MAX_VALID_YEAR}. Edit discarded.",
                            MessageType.ERROR,
                        )

                        # Complete editing come discard (NOT saved)
                        self.session_manager.complete_editing(saved=False)
                        self.editing_completed.emit(row, False)

                        # Update UI
                        self._update_button_states()
                        return
                else:
                    # Anno mancante → DISCARD automatico
                    logger.warning("Missing year in series title, discarding edit")

                    # Ripristina new_name E status originali
                    original_full_name = original_value + original_ext
                    self.file_processor.file_data[row].new_name = original_full_name
                    self.file_processor.file_data[row].status = original_status

                    self.status_message_changed.emit(
                        "❌ Series title must include a valid year (YYYY). Edit discarded.",
                        MessageType.ERROR,
                    )

                    self.session_manager.complete_editing(saved=False)
                    self.editing_completed.emit(row, False)
                    self._update_button_states()
                    return

            # Update duplicates
            self.file_processor._update_duplicate_status()

            # Propaga modifiche series (SEMPRE, non solo primo episodio)
            import os

            base_name = os.path.splitext(updated_item.new_name)[0]
            modified_rows = self.file_processor.propagate_series_edit(row, base_name)
            if modified_rows:
                logger.info(f"Series propagation updated {len(modified_rows)} episodes")

            # Complete editing in session
            self.session_manager.complete_editing(saved=True)

            # Notify View - update single file
            self.file_updated.emit(row, updated_item.new_name, updated_item.status)

            # IMPORTANTE: Update full list (duplicates + propagation)
            self.files_processed.emit(self.file_processor.file_data)

            self.editing_completed.emit(row, True)

            # Update UI state
            self._update_ui_after_edit()

        except Exception as e:
            logger.error(f"Error during save edit: {e}")
            # Discard on error
            self.session_manager.complete_editing(saved=False)
            self.editing_completed.emit(row, False)
            self.status_message_changed.emit(
                f"❌ Error processing edit: {e}", MessageType.ERROR
            )

    def handle_discard_edit(self, row: int) -> None:
        """Handle discarding an edit (ESC or click outside).

        Validates editing state, completes editing session, and notifies View
        to restore original filename.

        Args:
            row: Index of file whose edit is being discarded
        """
        logger.debug('Discard edit called: row=%d', row)
        logger.debug(
            'SessionManager state: is_editing=%s', self.session_manager.is_editing()
        )

        if not self.session_manager.is_editing():
            logger.debug('Not in editing mode (already completed), returning')
            return

        logger.debug('Getting editing info from session_manager')
        editing_row, original_value, original_ext = (
            self.session_manager.get_editing_info()
        )
        logger.debug(
            'editing_row=%d, original_value=\'%s\'', editing_row, original_value
        )

        if editing_row is None or editing_row != row:
            logger.warning('Row mismatch: editing_row=%d, row=%d', editing_row, row)
            return

        logger.debug('Completing editing (not saved)')
        # Complete editing in session (not saved)
        self.session_manager.complete_editing(saved=False)
        logger.debug('Editing completed')

        logger.debug('Emitting editing_completed signal')
        # Notify View - View ripristinerà valore originale
        self.editing_completed.emit(row, False)
        logger.debug('Signal emitted')

        logger.debug('Updating UI after edit')
        # Update UI state
        self._update_ui_after_edit()
        logger.debug('handle_discard_edit finished')

    # ========================================================================
    # SELECTION HANDLERS - Gestione selezione
    # ========================================================================

    def handle_selection_changed(self, row: int | None) -> None:
        """Handle table selection change.

        Updates session state, emits status message for selected file or
        general statistics if no selection, and updates button states.

        Args:
            row: Index of selected row, or None if deselected
        """
        # Update session
        self.session_manager.set_selection(row)

        # Update status message based on selection
        if row is not None:
            file_item = self.file_processor.get_file_at(row)
            if file_item:
                message, msg_type = self._get_status_for_file(file_item)
                self.status_message_changed.emit(message, msg_type)
        else:
            # No selection - show general statistics
            self._emit_statistics_message()

        # Update button states
        self._update_button_states()

    def get_selected_file_path(self) -> str | None:
        """Get path of currently selected file.

        Returns:
            str: File path if a file is selected, None otherwise
        """
        selected_row = self.session_manager.get_selected_row()
        if selected_row is not None:
            file_item = self.file_processor.get_file_at(selected_row)
            if file_item:
                return file_item.path
        return None

    def get_selected_file_metadata(self) -> dict | None:
        """Extract metadata for currently selected file.

        Returns:
            dict: Metadata dictionary with keys 'general', 'video', 'audio', 'subtitles',
                  or None if no file selected or extraction fails
        """
        from ..media_info import MediaMetadataExtractor

        file_path = self.get_selected_file_path()
        if not file_path:
            return None

        try:
            extractor = MediaMetadataExtractor(file_path)
            return extractor.extract_all()
        except Exception as e:
            # Log error but don't crash - return empty metadata
            print(f"Failed to extract metadata from {file_path}: {e}")
            return {
                'general': {},
                'video': None,
                'audio': [],
                'subtitles': [],
            }

    # ========================================================================
    # ACTION HANDLERS - Azioni utente
    # ========================================================================

    def handle_remove_file(self, row: int) -> None:
        """Handle file removal from the processing list.

        Validates removal is allowed, removes from processor, updates session,
        and triggers auto-reset if no files remain.

        Args:
            row: Index of file to remove
        """
        if not self.session_manager.can_remove_file():
            return

        # Remove from processor
        success = self.file_processor.remove_file(row)

        if success:
            # Update session
            new_count = len(self.file_processor.file_data)
            self.session_manager.update_file_count(new_count)

            if new_count == 0:
                # No more files - reset session
                self.handle_reset_session()
            else:
                # Update View with remaining files
                self.files_processed.emit(self.file_processor.file_data)
                self._update_ui_after_file_load()

    def get_force_edit_confirmation_message(self) -> str:
        """Get confirmation message for force edit operation.

        Returns appropriate warning message based on current mode (film/series).

        Returns:
            str: Confirmation message for the dialog
        """
        if self.file_processor.current_mode == FILE_CONTENT_TYPE_FILM:
            return (
                'Force edit will change the status of this file from\n'
                'ALREADY_NORMALIZED to READY, allowing you to edit it.\n\n'
                'This may create duplicate filenames.\n\n'
                'Are you sure you want to proceed?'
            )
        else:  # Series mode
            return (
                'Force edit will change the status of ALL ALREADY_NORMALIZED\n'
                'episodes in this series to READY, allowing you to edit them.\n\n'
                'This may create duplicate filenames.\n\n'
                'Are you sure you want to proceed?'
            )

    def handle_force_edit(self, row: int) -> None:
        """Handle force edit action for ALREADY_NORMALIZED files.

        Changes file status from ALREADY_NORMALIZED to READY to allow editing.
        For movies: changes only the selected file.
        For series: changes ALL ALREADY_NORMALIZED files.

        This is a potentially dangerous operation that requires confirmation.

        Args:
            row: Index of file to force edit
        """
        # Validate row
        if row < 0 or row >= len(self.file_processor.file_data):
            return

        # Force edit file(s) - change status from ALREADY_NORMALIZED to READY
        modified_rows = self.file_processor.force_edit_file(row)

        if modified_rows:
            # Update View
            self.files_processed.emit(self.file_processor.file_data)

            # Update UI state (statistics and button states)
            self._update_ui_after_file_load()

            # Update status message
            count = len(modified_rows)
            if self.file_processor.current_mode == FILE_CONTENT_TYPE_FILM:
                message = f"File status changed to READY - you can now edit it"
            else:  # Series mode
                message = f"{count} file(s) changed to READY - you can now edit them"

            self.status_message_changed.emit(message, 'info')

    def handle_apply_series_year(self, year: str) -> None:
        """Handle application of year to series files needing it.

        Updates all NEEDS_YEAR files with provided year, triggers reprocessing,
        and updates View.

        Args:
            year: Year string to apply (e.g., "2024")
        """
        # Apply year to processor
        updated_count = self.file_processor.apply_series_year(year)

        if updated_count > 0:
            # Update View
            self.files_processed.emit(self.file_processor.file_data)
            self._update_ui_after_file_load()

    def handle_cancel_series_load(self) -> None:
        """Handle cancellation of series load (user clicked Cancel in year dialog).

        Clears all data, resets session, updates View and UI state, and returns
        application to IDLE state.
        """
        logger.info('Cancelling series load')

        # Clear dei dati
        self.file_processor.clear()

        # Reset session
        self.session_manager.reset_session()

        # Notify View
        self.mode_changed.emit('idle')
        self.files_processed.emit([])  # Empty list → clear table

        # Update UI state
        self._update_button_states()

        # Status message
        self.status_message_changed.emit('Series load cancelled', MessageType.INFO)

    def handle_apply_renames(self) -> bool:
        """Handle application of file renames to disk.

        Comprehensive workflow:
        1. Validate that rename can be applied
        2. Check for target file conflicts
        3. If conflicts found, emit conflicts_detected signal
        4. Execute actual file renames
        5. Update View with results
        6. Auto-reset if all files successfully renamed

        Returns:
            True if renames were executed, False if blocked by conflicts
        """
        if not self.session_manager.can_apply_changes():
            return False

        # Check conflicts
        conflicts = self.file_processor.check_target_conflicts()
        if conflicts:
            # Emit signal - View mostrerà warning
            self.conflicts_detected.emit(conflicts)
            return False

        # Execute renames
        success_count, total_count, errors = self.file_processor.execute_renames()

        # Notify View
        self.rename_completed.emit(success_count, total_count, errors)

        # Update session
        new_count = len(self.file_processor.file_data)
        self.session_manager.update_file_count(new_count)

        if new_count == 0:
            # All files renamed - reset session
            self.handle_reset_session()
        else:
            # Update View with remaining files
            self.files_processed.emit(self.file_processor.file_data)
            self._update_ui_after_file_load()

        return True

    def handle_reset_session(self) -> None:
        """Handle complete session reset (Start Over button).

        Clears all data, resets session state, updates View, and returns
        application to IDLE state with all buttons reset.
        """
        # Clear processor
        self.file_processor.clear()

        # Reset session
        self.session_manager.reset_session()

        # Notify View
        self.session_reset.emit()
        self.files_cleared.emit()

        # Update UI state
        self._update_button_states_for_idle()

    # ========================================================================
    # QUERY METHODS - Interrogazione stato (per View)
    # ========================================================================

    def can_remove_file(self, row: int) -> bool:
        """Check if a file can be removed.

        A file can be removed if it's not in READY or ALREADY_NORMALIZED status.
        Only invalid, not video, needs year, and duplicate files can be removed.

        Args:
            row: Index of file to check

        Returns:
            True if file can be removed, False otherwise
        """
        if row is None or row < 0 or row >= len(self.file_processor.file_data):
            return False

        if not self.session_manager.can_remove_file():
            return False

        file_item = self.file_processor.file_data[row]

        # ⚠️ CRITICAL: Allow removing ALL non-READY files
        # This includes: INVALID, NOT_VIDEO, NEEDS_YEAR, DUPLICATE
        # Cannot remove: READY, ALREADY_NORMALIZED
        removable_statuses = [
            FileStatus.INVALID,
            FileStatus.NOT_VIDEO,
            FileStatus.NEEDS_YEAR,
            FileStatus.DUPLICATE,
        ]

        return file_item.status in removable_statuses

    def can_apply_renames(self) -> bool:
        """Check if rename application is allowed.

        Apply is allowed when:
        1. Not currently editing
        2. At least one file has READY status

        Invalid and Not Video files are ignored during apply.

        Returns:
            True if apply is possible, False otherwise
        """
        return (
            self.session_manager.can_apply_changes()
            and self.file_processor.has_ready_files()
        )

    def is_editing(self) -> bool:
        """Check if currently in editing mode.

        Returns:
            True if file is being edited, False otherwise
        """
        return self.session_manager.is_editing()

    def is_mode_locked(self) -> bool:
        """Check if mode switching is locked.

        Returns:
            True if mode is locked (files loaded), False otherwise
        """
        return self.session_manager.is_mode_locked()

    def get_file_count(self) -> int:
        """Get the number of files in current session.

        Returns:
            File count (0 if no session)
        """
        return self.session_manager.get_file_count()

    def can_force_edit(self, row: int) -> bool:
        """Check if a file can be force edited.

        Force edit is allowed for files with ALREADY_NORMALIZED status,
        enabling users to manually edit files that are already in the
        correct format.

        Args:
            row: Index of file to check

        Returns:
            True if file can be force edited, False otherwise
        """
        if row is None or row < 0 or row >= len(self.file_processor.file_data):
            return False

        # Can't force edit while in editing mode
        if self.session_manager.is_editing():
            return False

        file_item = self.file_processor.file_data[row]

        # Only ALREADY_NORMALIZED files can be force edited
        return file_item.status == FileStatus.ALREADY_NORMALIZED

    # ========================================================================
    # PRIVATE HELPERS - Logica interna
    # ========================================================================

    def _clean_placeholder_text(self, text: str) -> str:
        """Clean placeholder year text from user input.

        Removes year placeholder with/without parentheses and extra whitespace.

        Args:
            text: Text to clean

        Returns:
            Cleaned text without placeholder
        """
        # Remove placeholder with or without parentheses
        cleaned = text.replace(f'({DEFAULT_YEAR_PLACEHOLDER})', '').strip()
        cleaned = cleaned.replace(DEFAULT_YEAR_PLACEHOLDER, '').strip()

        # Clean up double spaces and trailing separators
        cleaned = re.sub(r'\s+', ' ', cleaned).strip(' .-_')

        return cleaned

    def _extract_episode_number(self, text: str) -> str | None:
        """Extract episode number from filename.

        Supports both S##E## and ##x## formats, normalizing to S##E## style.

        Args:
            text: Filename text (with or without extension)

        Returns:
            Episode number as 'E##' string (e.g., 'E03'), or None if not found

        Examples:
            >>> _extract_episode_number("Breaking Bad (2008) - S01E03 - Pilot")
            "E03"
            >>> _extract_episode_number("Breaking Bad - 1x03 - Pilot")
            "E03"
            >>> _extract_episode_number("Movie Title (2020)")
            None
        """
        # Pattern per S##E## o ##x##
        pattern = r'[Ss]\d+[Ee](\d+)|\d+[Xx](\d+)'
        match = re.search(pattern, text)

        if not match:
            return None

        # Estrai il numero episodio
        episode_num = match.group(1) if match.group(1) else match.group(2)
        return f"E{int(episode_num):02d}"

    def _get_status_for_file(
        self, file_item: FileProcessingData
    ) -> tuple[str, MessageType]:
        """Generate status message for a file.

        Creates appropriate message and message type based on file status.

        Args:
            file_item: FileProcessingData to generate message for

        Returns:
            Tuple of (message, MessageType)
        """
        if file_item.status == FileStatus.READY:
            return (f"✅ Ready to rename: {file_item.new_name}", MessageType.SUCCESS)
        elif file_item.status == FileStatus.NEEDS_YEAR:
            return (
                '⚠️ Missing year - Add a 4-digit year (e.g., 2025) to normalize',
                MessageType.WARNING,
            )
        elif file_item.status == FileStatus.DUPLICATE:
            return (
                '⚠️ Duplicate name - This filename conflicts with another file',
                MessageType.WARNING,
            )
        elif file_item.status == FileStatus.INVALID:
            error_msg = file_item.error_message or 'Invalid format'
            return (f"❌ {error_msg}", MessageType.ERROR)
        elif file_item.status == FileStatus.ALREADY_NORMALIZED:
            return (
                f"⭐️ Already normalized: {file_item.original_name} - Will be skipped",
                MessageType.INFO,
            )
        elif file_item.status == FileStatus.NOT_VIDEO:
            return (
                f"❌ Not a video file: {file_item.original_name}",
                MessageType.ERROR,
            )

        return ('', MessageType.INFO)

    def _emit_statistics_message(self) -> None:
        """Emit status message with file statistics.

        Uses UI_STATUS_DESCRIPTORS and build_status_message() to generate
        consistent status messages. Handles special cases:
        - Empty file list: "Ready to process files"
        - All normalized: "All files already normalized"
        - Normal case: Statistics breakdown by status
        """
        from ..models import build_status_message

        stats = self.file_processor.get_statistics()
        total = sum(stats.values())

        # Caso speciale: nessun file
        if total == 0:
            message = "Ready to process files"
            msg_type = MessageType.INFO
        # Caso speciale: tutti già normalizzati
        elif stats.get(FileStatus.ALREADY_NORMALIZED, 0) == total:
            message = "ℹ️ All files are already normalized. Nothing to do."
            msg_type = MessageType.INFO
        # Caso normale: usa helper per costruire messaggio
        else:
            message, msg_type = build_status_message(stats)

        self.status_message_changed.emit(message, msg_type)

    def _update_button_states(self) -> None:
        """Update all button availability states based on current state.

        Checks current application state, editing mode, selection, and file
        status to determine which buttons should be enabled/disabled.
        Emits button_states_changed signal.
        """
        logger.debug('Updating button states')

        is_editing = self.session_manager.is_editing()
        is_mode_locked = self.session_manager.is_mode_locked()
        has_selection = self.session_manager.has_selection()
        selected_row = self.session_manager.get_selected_row()

        logger.debug(
            'State: is_editing=%s, is_mode_locked=%s, has_selection=%s, selected_row=%s',
            is_editing,
            is_mode_locked,
            has_selection,
            selected_row,
        )

        can_apply = self.can_apply_renames()
        can_remove = (
            self.can_remove_file(selected_row) if selected_row is not None else False
        )
        can_force_edit = (
            self.can_force_edit(selected_row) if selected_row is not None else False
        )

        logger.debug('Permissions: can_apply=%s, can_remove=%s, can_force_edit=%s',
                     can_apply, can_remove, can_force_edit)

        states = {
            'add_movie': not is_mode_locked,
            'add_series': not is_mode_locked,
            'apply': not is_editing and can_apply,
            'remove': not is_editing
            and has_selection
            and selected_row is not None
            and can_remove,
            'force_edit': not is_editing
            and has_selection
            and selected_row is not None
            and can_force_edit,
            'save': is_editing,
            'discard': is_editing,
            'start_over': is_mode_locked,
            'info': has_selection and selected_row is not None,
        }

        logger.debug('Button states: %s', states)
        self.button_states_changed.emit(states)
        logger.debug('Button states updated')

    def _update_ui_after_file_load(self) -> None:
        """Update UI after files have been loaded.

        Emits statistics message and updates button states.
        """
        self._emit_statistics_message()
        self._update_button_states()

    def _update_ui_after_edit(self) -> None:
        """Update UI after editing is complete.

        Updates button states and emits statistics message.
        """
        logger.debug('Updating UI after edit')

        # Update button states based on current file processor state
        logger.debug('Updating button states')
        self._update_button_states()

        # Update status message
        logger.debug('Emitting statistics message')
        self._emit_statistics_message()

        logger.debug('UI update completed')

    def _update_button_states_for_idle(self) -> None:
        """Update button states for IDLE application state.

        Disables all action buttons and enables only Add Movie/Add Series.
        """
        states = {
            'add_movie': True,
            'add_series': True,
            'apply': False,
            'remove': False,
            'force_edit': False,
            'save': False,
            'discard': False,
            'start_over': False,
        }

        self.button_states_changed.emit(states)
        self.status_message_changed.emit('Ready to process files', MessageType.INFO)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    """Example of how View (MainWindow) interacts with Presenter."""

    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Create presenter
    presenter = AppPresenter()

    # Connect signals (View would do this)
    def on_files_processed(files):
        print(f"View: Received {len(files)} files to display")

    def on_button_states_changed(states):
        print(f"View: Update button states: {states}")

    def on_status_message(message, msg_type):
        print(f"View: Status [{msg_type}]: {message}")

    presenter.files_processed.connect(on_files_processed)
    presenter.button_states_changed.connect(on_button_states_changed)
    presenter.status_message_changed.connect(on_status_message)

    # Simulate user actions
    print('\n1. User selects movies:')
    presenter.handle_movie_selection(['/path/to/movie1.mkv', '/path/to/movie2.mp4'])

    print('\n2. User selects a row:')
    presenter.handle_selection_changed(0)

    print('\n3. User starts editing:')
    presenter.handle_editing_started(0, 'Movie (2024).mkv', '.mkv')

    print('\n4. User saves edit:')
    presenter.handle_save_edit(0, 'Better Movie Title 2024')

    sys.exit(0)

