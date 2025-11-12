"""Debug test for edit mode - run this and check console output."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QTimer
from src.gui.file_table import FileTable
from src.models import FileProcessingData, FileStatus, FILE_CONTENT_TYPE_FILM


def test_edit_with_debug():
    """Test edit mode with debug output."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    print('\\n=== Creating table ===')
    table = FileTable()
    table.set_mode(FILE_CONTENT_TYPE_FILM)

    print('\\n=== Adding test data ===')
    test_data = [
        FileProcessingData(
            path='/test/pippo.mkv',
            original_name='pippo.mkv',
            new_name='pippo.mkv',
            status=FileStatus.NEEDS_YEAR,
        )
    ]
    table.set_file_data(test_data)

    table.show()
    table.resize(800, 200)

    print('\\n=== Getting item ===')
    item = table.item(0, table.COL_NEW)
    print(f'Item: {item}')
    print(f'Item text: {item.text() if item else "None"}')
    print(
        f'Item editable: {bool(item.flags() & Qt.ItemFlag.ItemIsEditable) if item else "None"}'
    )

    print('\\n=== Simulating double-click ===')
    table._on_item_double_clicked(item)

    # Wait for QTimer to fire
    print('\\n=== Waiting for QTimer (100ms) ===')
    QTest.qWait(100)
    app.processEvents()

    print('\\n=== Checking state after double-click ===')
    print(f'Is editing: {table.is_editing()}')
    print(f'Editing row: {table._editing_row}')
    print(f'Current editor widget: {table.cellWidget(0, table.COL_NEW)}')
    print(f'Item text after: {item.text() if item else "None"}')

    # Keep window open for manual testing
    print('\\n=== Window is open - try double-clicking manually ===')
    print('Press Ctrl+C to exit')

    app.exec()


if __name__ == '__main__':
    test_edit_with_debug()
