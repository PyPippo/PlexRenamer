"""File preview table widget with inline editing and status visualization.

This module provides the FileTable widget, a custom QTableWidget specialized
for displaying file rename previews with inline editing capabilities. It
manages the visual representation of file processing results and handles user
interactions for editing filenames.

Key Responsibilities:
- Render file list with status icons, original names, and proposed new names
- Manage inline editing mode with proper state tracking
- Emit signals for editing actions (start, save, discard)
- Apply visual styling based on file status
- Handle keyboard and mouse interactions

Does NOT Handle:
- File validation logic (delegated to FileProcessor)
- Duplicate detection (delegated to FileProcessor)
- Series propagation logic (delegated to FileProcessor)
- Application state management (delegated to Presenter)

Note: This simplified implementation (STEP 5) removed validation methods,
propagation logic, and getter methods to reduce coupling and complexity.
All business logic is delegated to other components.
"""

import os
import logging
from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QAbstractItemDelegate,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QBrush

from ..models import FileStatus, FileProcessingData, STATUS_ICONS

logger = logging.getLogger(__name__)


class FileTable(QTableWidget):
    """Custom table widget for file rename preview - SIMPLIFIED.

    ✅ STEP 5 COMPLETE:
    - SUB-STEP 5.1: Removed validation methods
    - SUB-STEP 5.2: Removed _propagate_series_changes
    - SUB-STEP 5.3: Simplified editing methods
    - SUB-STEP 5.4: Removed getter methods
    - SUB-STEP 5.5: Cleanup (unused vars, imports, docs)

    Responsibilities:
    - Rendering file list
    - UI editing management
    - Emitting signals for UI events

    Does NOT handle:
    - File validation (→ FileProcessor)
    - Duplicate checking (→ FileProcessor)
    - Series propagation (→ FileProcessor)
    - Business logic (→ Presenter)
    """

    # Signals
    editing_started = Signal(int)
    save_requested = Signal(int, str)
    discard_requested = Signal(int)

    # Column indices
    COL_STATUS = 0
    COL_ORIGINAL = 1
    COL_ARROW = 2
    COL_NEW = 3

    # Text colors for "New Name" column based on status
    # NOTE: These remain here as they are Qt/UI-specific (QColor)
    NEW_NAME_TEXT_COLORS = {
        FileStatus.READY: QColor(0, 114, 15),
        FileStatus.NEEDS_YEAR: QColor(183, 149, 11),
        FileStatus.INVALID: QColor(220, 53, 69),
        FileStatus.ALREADY_NORMALIZED: QColor(108, 117, 125),
        FileStatus.DUPLICATE: QColor(255, 107, 0),
        FileStatus.NOT_VIDEO: QColor(220, 53, 69),
    }

    def __init__(self, parent=None):
        """Initialize the file table widget.

        Sets up the table structure, column configuration, and editing state
        tracking. Calls _setup_ui() to configure all UI elements and signal
        connections.

        Args:
            parent: Parent widget (optional). Defaults to None.
        """
        super().__init__(parent)
        self.file_data: list[FileProcessingData] = []
        # Editing state (minimal)
        self._is_editing = False
        self._editing_row: int | None = None
        self._original_value: str = ''
        self._original_extension: str = ''
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize the table UI.

        Configures the table structure:
        - Sets 4 columns: Status, Original Name, Arrow, New Name
        - Configures header resize modes (Status/Arrow: contents, Names: stretch)
        - Sets single row selection mode with no grid lines
        - Connects itemChanged and itemDoubleClicked signals
        - Installs event filter on viewport for click detection
        """
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Status", "Original Name", "→", "New Name"])

        # Configure headers
        header = self.horizontalHeader()
        header.setSectionResizeMode(
            self.COL_STATUS, QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(self.COL_ORIGINAL, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(
            self.COL_ARROW, QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(self.COL_NEW, QHeaderView.ResizeMode.Stretch)

        # Table properties
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(False)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.viewport().installEventFilter(self)

        # Connect signals
        self.itemChanged.connect(self._on_item_changed)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

    def set_file_data(self, file_data: list[FileProcessingData]) -> None:
        """Populate table with file data.

        Updates the table display with new file processing results. Protects
        against repopulation while an editor is open to prevent loss of user
        edits in progress.

        CRITICAL: This method blocks updates when _is_editing is True and
        an editor widget is visible on the New Name column.

        Args:
            file_data: List of FileProcessingData objects containing file
                information (original name, new name, status, etc.)
        """
        if self._is_editing and self._editing_row is not None:
            current_index = self.model().index(self._editing_row, self.COL_NEW)
            if self.indexWidget(current_index) is not None:
                logger.debug(f"set_file_data: BLOCKED - Editor open on row {self._editing_row}")
                return  # Editor open, block update

        logger.debug(f"set_file_data: Updating table with {len(file_data)} files (is_editing={self._is_editing})")
        self.file_data = file_data
        self._populate_table()

    def _populate_table(self) -> None:
        """Populate the table with current file data.

        Clears existing rows and adds new rows based on self.file_data.
        Blocks signals during population to prevent unnecessary updates.
        """
        self.blockSignals(True)
        self.setRowCount(0)
        for row_idx, file_item in enumerate(self.file_data):
            self._add_row(row_idx, file_item)
        self.blockSignals(False)

    def _add_row(self, row_idx: int, file_item: FileProcessingData) -> None:
        """Add a single row to the table.

        Creates a table row with four columns:
        1. Status icon (non-editable, centered)
        2. Original filename (non-editable)
        3. Arrow "→" separator (non-editable, centered)
        4. New filename (editable, colored based on status)

        Args:
            row_idx: Index of the row to insert
            file_item: FileProcessingData object containing file details
        """
        self.insertRow(row_idx)

        # Status icon
        status_item = QTableWidgetItem(STATUS_ICONS.get(file_item.status, ""))
        status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row_idx, self.COL_STATUS, status_item)

        # Original filename
        original_item = QTableWidgetItem(file_item.original_name)
        original_item.setFlags(original_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.setItem(row_idx, self.COL_ORIGINAL, original_item)

        # Arrow
        arrow_item = QTableWidgetItem("→")
        arrow_item.setFlags(arrow_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        arrow_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row_idx, self.COL_ARROW, arrow_item)

        # New filename (editable)
        new_item = QTableWidgetItem(file_item.new_name)
        new_item.setFlags(new_item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.setItem(row_idx, self.COL_NEW, new_item)

        self._apply_text_colors(row_idx, file_item.status)

    def _apply_text_colors(self, row_idx: int, status: FileStatus) -> None:
        """Apply text color to the New Name column based on status.

        Maps FileStatus values to specific colors for visual feedback:
        - READY: Green (ready for rename)
        - NEEDS_YEAR: Yellow (missing year information)
        - INVALID: Red (invalid format)
        - ALREADY_NORMALIZED: Gray (no changes needed)
        - DUPLICATE: Orange (duplicate name detected)
        - NOT_VIDEO: Red (not a video file)

        Args:
            row_idx: Index of the row to color
            status: FileStatus enum value determining the color
        """
        new_name_item = self.item(row_idx, self.COL_NEW)
        if new_name_item:
            text_color = self.NEW_NAME_TEXT_COLORS.get(status, QColor(0, 0, 0))
            try:
                self.itemChanged.disconnect(self._on_item_changed)
            except RuntimeError:
                pass
            new_name_item.setForeground(QBrush(text_color))
            self.itemChanged.connect(self._on_item_changed)

    def _on_item_double_clicked(self, item: QTableWidgetItem) -> None:
        """Handle double-click to enter edit mode.

        Only responds to double-clicks on the New Name column (COL_NEW).
        Other columns are ignored. Calls _enter_edit_mode() to start editing.

        Args:
            item: The clicked QTableWidgetItem
        """
        if item.column() != self.COL_NEW:
            return
        self._enter_edit_mode(item.row())

    def _enter_edit_mode(self, row: int) -> None:
        """Enter edit mode for a specific row.

        Prepares a filename for editing by:
        1. Validating row index and checking if already editing
        2. Storing original value and file extension
        3. Extracting base name (without extension) for editing
        4. Temporarily disconnecting itemChanged signal
        5. Deferring the actual editor activation to next event loop

        The deferred activation ensures proper focus handling and text selection.

        Args:
            row: Index of the row to edit
        """
        if row >= len(self.file_data) or self._is_editing:
            return

        file_item = self.file_data[row]
        new_item = self.item(row, self.COL_NEW)
        if not new_item:
            return

        # Store state
        self._is_editing = True
        self._editing_row = row
        self._original_value = file_item.new_name
        self._original_extension = os.path.splitext(file_item.original_name)[1]

        # Extract base name (without extension)
        base_name, _ = os.path.splitext(file_item.new_name)

        try:
            self.itemChanged.disconnect(self._on_item_changed)
        except RuntimeError:
            pass

        new_item.setText(base_name)
        new_item.setFlags(new_item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.itemChanged.connect(self._on_item_changed)

        # Defer editing to next event loop
        QTimer.singleShot(0, lambda: self._start_editing_item(row))

    def _start_editing_item(self, row: int) -> None:
        """Start editing (deferred).

        This method is called via QTimer.singleShot(0, ...) to defer the
        actual editor activation until the next event loop iteration. This
        ensures proper focus handling, text selection, and cursor positioning.

        Validates that the editing state matches the current row before
        proceeding.

        Args:
            row: Index of the row to edit
        """
        if not self._is_editing or self._editing_row != row:
            return
        new_item = self.item(row, self.COL_NEW)
        if new_item:
            self.editItem(new_item)
            self.editing_started.emit(row)

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        """Handle item changed (ENTER key or focus loss).

        Triggered when the user commits an edit via ENTER key or by
        defocusing the editor. Only responds to changes in the New Name
        column while in editing mode. Emits save_requested signal with
        the edited text (stripped of whitespace).

        Args:
            item: The QTableWidgetItem that was changed
        """
        if item.column() != self.COL_NEW:
            return
        if self._is_editing and item.row() == self._editing_row:
            edited_text = item.text().strip()
            self.save_requested.emit(item.row(), edited_text)

    def closeEditor(self, editor, hint) -> None:
        """Override closeEditor to handle ESC and clicks outside.

        Handles three editing termination scenarios:
        1. ESC pressed: Discard edits via RevertModelCache hint
        2. Click outside: Discard edits (critical fix from V1 bug)
        3. ENTER key: Already handled by _on_item_changed()

        ⚠️ CRITICAL FIX - DO NOT MODIFY:
        This implementation fixes a V1 bug where clicking outside the
        editor would not properly discard changes. The click-outside case
        is now explicitly handled by emitting discard_requested signal.

        Args:
            editor: The editor widget being closed
            hint: QAbstractItemDelegate.EndEditHint indicating how editor was closed
        """
        super().closeEditor(editor, hint)

        if not self._is_editing:
            return

        # ESC pressed - discard
        if hint == QAbstractItemDelegate.EndEditHint.RevertModelCache:
            if self._editing_row is not None:
                self.discard_requested.emit(self._editing_row)
                self._reset_editing_state()
            return

        # Click outside - discard (critical fix from V1)
        elif self._is_editing:
            if self._editing_row is not None:
                self.discard_requested.emit(self._editing_row)
                self._reset_editing_state()
            return

        # ENTER key handled by _on_item_changed

    def keyPressEvent(self, event) -> None:
        """Handle key press events.

        During editing mode, accepts ESC key presses to trigger editor
        closure (which then emits discard_requested). Other key presses
        are delegated to parent class.

        Args:
            event: QKeyEvent containing the pressed key information
        """
        from PySide6.QtCore import Qt as QtCore

        if self._is_editing and event.key() == QtCore.Key.Key_Escape:
            event.accept()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event) -> None:
        """Handle focus lost during editing.

        When focus is lost and editing is in progress, defers a check to
        determine if focus moved outside the table widget. If so, emits
        discard_requested and resets editing state.

        Uses a 50ms delay to allow Qt's focus system to complete before
        checking the new focus widget.

        Args:
            event: QFocusEvent indicating focus loss
        """
        if self._is_editing:
            from PySide6.QtWidgets import QApplication

            def check_focus_later():
                focus_widget = QApplication.focusWidget()
                if focus_widget is None or not self.isAncestorOf(focus_widget):
                    if self._is_editing and self._editing_row is not None:
                        self.discard_requested.emit(self._editing_row)
                        self._reset_editing_state()

            QTimer.singleShot(50, check_focus_later)
        super().focusOutEvent(event)

    def eventFilter(self, obj, event) -> bool:
        """Event filter to handle clicks on empty area.

        Installed on the viewport to detect mouse clicks on the table.
        When a click occurs on an empty (invalid) table area, clears the
        current selection. This provides feedback that the click was
        registered but doesn't select a row.

        Args:
            obj: The object that received the event (viewport)
            event: The QEvent being filtered

        Returns:
            True if event was handled (click on empty area), False otherwise
        """
        from PySide6.QtCore import QEvent
        from PySide6.QtGui import QMouseEvent

        if obj == self.viewport() and event.type() == QEvent.Type.MouseButtonPress:
            if isinstance(event, QMouseEvent):
                index = self.indexAt(event.pos())
                if not index.isValid():
                    self.clearSelection()
        return super().eventFilter(obj, event)

    def force_close_editor(self) -> None:
        """Force close the current editor widget.

        Forcefully closes any active editor using multiple strategies:
        1. Calls closePersistentEditor() on the item
        2. If still stuck, performs nuclear cleanup:
           - Hides and deletes all editor widgets
           - Resets edit triggers to NoEditTriggers
           - Resets table state to NoState
           - Re-applies NoEditTriggers after brief delay

        This method is used when normal editor closure fails, particularly
        during state resets or when editors become stuck.
        """
        if not self._is_editing or self._editing_row is None:
            return

        current_index = self.model().index(self._editing_row, self.COL_NEW)
        editor = self.indexWidget(current_index)

        if editor:
            item = self.item(self._editing_row, self.COL_NEW)
            if item is not None:
                self.closePersistentEditor(item)

        # Nuclear cleanup if still stuck
        if self.indexWidget(current_index) is not None:
            for row in range(self.rowCount()):
                for col in range(self.columnCount()):
                    index = self.model().index(row, col)
                    widget = self.indexWidget(index)
                    if widget:
                        widget.hide()
                        widget.deleteLater()
                        self.setIndexWidget(index, None)  # type: ignore[arg-type]
            self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.setState(QAbstractItemView.State.NoState)
            QTimer.singleShot(
                10,
                lambda: self.setEditTriggers(
                    QAbstractItemView.EditTrigger.NoEditTriggers
                ),
            )

    def complete_edit_save(self, row: int, new_name: str, status: FileStatus) -> None:
        """Complete editing with save.

        Commits the edited filename and updates the file status. Called
        by the Presenter after successful validation of the edited text.
        Updates all affected table cells and applies appropriate text colors.

        Steps:
        1. Force close any open editor
        2. CRITICAL: Reset editing state IMMEDIATELY to allow files_processed signal
        3. Update FileProcessingData with new name and status
        4. Update New Name cell with validated new_name
        5. Update Status icon
        6. Apply text colors based on new status
        7. Clear selection

        IMPORTANT: Editing state is reset BEFORE updating UI to ensure that
        the subsequent files_processed signal (which contains series propagation)
        is not blocked by the _is_editing flag in set_file_data().

        Args:
            row: Index of the row being edited
            new_name: The validated new filename (with extension)
            status: The new FileStatus after validation
        """
        logger.debug(f"complete_edit_save: row={row}, new_name='{new_name}', status={status}")
        logger.debug(f"complete_edit_save: Before - is_editing={self._is_editing}, editing_row={self._editing_row}")

        if row >= len(self.file_data):
            logger.warning(f"complete_edit_save: Row {row} out of range (total={len(self.file_data)})")
            return

        # Step 1: Force close editor
        self.force_close_editor()

        # Step 2: CRITICAL FIX - Reset editing state IMMEDIATELY
        # This ensures files_processed signal won't be blocked
        self._reset_editing_state()
        logger.debug(f"complete_edit_save: After reset - is_editing={self._is_editing}, editing_row={self._editing_row}")

        # Step 3: Update FileProcessingData
        file_item = self.file_data[row]
        file_item.new_name = new_name
        file_item.status = status

        # Step 4: Update New Name cell
        new_item = self.item(row, self.COL_NEW)
        if new_item:
            self.blockSignals(True)
            new_item.setText(new_name)
            self.blockSignals(False)

        # Step 5: Update Status icon
        status_item = self.item(row, self.COL_STATUS)
        if status_item:
            status_item.setText(STATUS_ICONS.get(status, ''))

        # Step 6: Apply text colors
        self._apply_text_colors(row, status)

        # Step 7: Clear selection
        self.clearSelection()
        logger.debug("complete_edit_save: Complete")

    def complete_edit_discard(self, row: int) -> None:
        """Complete editing with discard.

        Cancels the current edit and restores the original filename.
        Called by the Presenter when user cancels editing or validation fails.
        Restores _original_value that was saved when entering edit mode.

        Args:
            row: Index of the row being edited
        """
        if row >= len(self.file_data):
            return

        self.blockSignals(True)
        new_item = self.item(row, self.COL_NEW)
        if new_item:
            new_item.setText(self._original_value)
        self._reset_editing_state()
        self.clearSelection()
        self.viewport().update()
        self.blockSignals(False)

    def _reset_editing_state(self) -> None:
        """Reset all editing state variables.

        Clears all editing-related state flags and values:
        - _is_editing: Set to False
        - _editing_row: Set to None
        - _original_value: Set to empty string
        - _original_extension: Set to empty string
        """
        self._is_editing = False
        self._editing_row = None
        self._original_value = ""
        self._original_extension = ""

    def save_current_edit(self) -> None:
        """Trigger save of current edit (called by Save button).

        Called when the Save button is clicked. Extracts the current text
        from the editor widget (or item if widget unavailable), strips
        whitespace, and emits save_requested signal.

        Handles both cases:
        - If editor widget (QLineEdit) exists: use widget text
        - Otherwise: fall back to item text
        """
        if not self._is_editing or self._editing_row is None:
            return

        new_item = self.item(self._editing_row, self.COL_NEW)
        if new_item:
            current_index = self.model().index(self._editing_row, self.COL_NEW)
            editor_widget = self.indexWidget(current_index)

            if editor_widget is not None:
                from PySide6.QtWidgets import QLineEdit

                if isinstance(editor_widget, QLineEdit):
                    edited_text = editor_widget.text().strip()
                else:
                    edited_text = new_item.text().strip()
            else:
                edited_text = new_item.text().strip()

            self.save_requested.emit(self._editing_row, edited_text)

    def discard_current_edit(self) -> None:
        """Trigger discard of current edit (called by Discard button).

        Called when the Discard button is clicked. Force closes the current
        editor and emits discard_requested signal to notify the Presenter.
        """
        if not self._is_editing or self._editing_row is None:
            return

        row = self._editing_row
        self.force_close_editor()
        self.discard_requested.emit(row)
