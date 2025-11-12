"""Dialog windows for user input and confirmations.

This module provides utility functions for displaying dialog boxes to the user,
including input dialogs, message dialogs (info, warning, error), and
confirmation dialogs. All dialogs are modal and block execution until the
user responds.

Functions:
- prompt_series_year: Request year input with validation loop
- show_error: Display error message dialog
- show_warning: Display warning message dialog
- show_info: Display informational message dialog
- confirm_action: Display confirmation dialog with Yes/No options
- confirm_dangerous_action: Display warning confirmation for dangerous operations

Note: This module does not handle dialog triggering logic, which is managed
by AppPresenter based on file processing results and user actions.
"""

from PySide6.QtWidgets import QInputDialog, QMessageBox
from datetime import datetime

from ..core import validate_year
from ..models import MIN_VALID_YEAR, MAX_VALID_YEAR


def prompt_series_year(parent, folder_name: str) -> str | None:
    """Prompt user for series year when not detected in filenames.

    Displays an input dialog requesting the release year for a series.
    Validates the entered year against acceptable range and loops until
    a valid year is entered or the user cancels.

    Validation Loop:
    1. Show input dialog with suggested current year
    2. If cancelled: return None
    3. If invalid: show warning and loop back to step 1
    4. If valid: return the year string

    Args:
        parent: Parent widget for dialog modality
        folder_name: Name of the folder/series being processed (shown in prompt)

    Returns:
        str: Valid year string (e.g., '2008') if confirmed, or None if cancelled
    """
    current_year_str = str(MAX_VALID_YEAR)

    # Loop finché anno valido o cancel
    while True:
        year, ok = QInputDialog.getText(
            parent,
            'Series Year Required',
            f"No year detected for series in folder:\n{folder_name}\n\n"
            f"Enter release year ({MIN_VALID_YEAR}-{MAX_VALID_YEAR}):",
            text=current_year_str,
        )

        # User cancelled
        if not ok:
            return None

        # Validate year
        if validate_year(year):
            return year

        # Invalid year - show warning and loop
        QMessageBox.warning(
            parent,
            'Invalid Year',
            f"The year '{year}' is not valid.\n\n"
            f"Please enter a year between {MIN_VALID_YEAR} and {MAX_VALID_YEAR}.\n\n"
            f"Or click Cancel to abort series import.",
        )
        # Loop continues - prompts again


def show_error(parent, title: str, message: str) -> None:
    """Show error dialog.

    Displays a critical error message dialog with a red stop icon.
    Blocks until user acknowledges the error.

    Args:
        parent: Parent widget for dialog modality
        title: Dialog window title
        message: Error message text (can include newlines)
    """
    QMessageBox.critical(parent, title, message)


def show_warning(parent, title: str, message: str) -> None:
    """Show warning dialog.

    Displays a warning message dialog with a yellow exclamation icon.
    Blocks until user acknowledges the warning.

    Args:
        parent: Parent widget for dialog modality
        title: Dialog window title
        message: Warning message text (can include newlines)
    """
    QMessageBox.warning(parent, title, message)


def show_info(parent, title: str, message: str) -> None:
    """Show information dialog.

    Displays an informational message dialog with a blue information icon.
    Blocks until user acknowledges the information.

    Args:
        parent: Parent widget for dialog modality
        title: Dialog window title
        message: Informational message text (can include newlines)
    """
    QMessageBox.information(parent, title, message)


def confirm_action(parent, title: str, message: str) -> bool:
    """Show confirmation dialog.

    Displays a confirmation dialog with Yes and No buttons. The No button
    is set as the default to prevent accidental confirmations. Blocks until
    user responds.

    Args:
        parent: Parent widget for dialog modality
        title: Dialog window title
        message: Confirmation message text (can include newlines)

    Returns:
        bool: True if user clicked Yes, False if user clicked No or closed dialog
    """
    reply = QMessageBox.question(
        parent,
        title,
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )

    return reply == QMessageBox.StandardButton.Yes


def confirm_dangerous_action(parent, title: str, message: str) -> bool:
    """Show warning confirmation dialog for dangerous operations.

    Displays a warning confirmation dialog with Yes and No buttons and a
    yellow warning icon. The No button is set as the default to prevent
    accidental confirmations of dangerous operations. Blocks until user responds.

    Args:
        parent: Parent widget for dialog modality
        title: Dialog window title
        message: Warning message text (can include newlines)

    Returns:
        bool: True if user clicked Yes, False if user clicked No or closed dialog
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg_box.setDefaultButton(QMessageBox.StandardButton.No)

    reply = msg_box.exec()
    return reply == QMessageBox.StandardButton.Yes
