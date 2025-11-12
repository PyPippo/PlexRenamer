"""Test for edit mode double-click fix."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QTimer
from src.gui.file_table import FileTable
from src.models import FileProcessingData, FileStatus, FILE_CONTENT_TYPE_FILM


def test_double_click_edit_mode():
    """Test that double-clicking a row enters edit mode without crashing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create table
    table = FileTable()
    table.set_mode(FILE_CONTENT_TYPE_FILM)

    # Add test data
    test_data = [
        FileProcessingData(
            path='/test/pippo.mkv',
            original_name='pippo.mkv',
            new_name='pippo.mkv',
            status=FileStatus.NEEDS_YEAR,
        )
    ]
    table.set_file_data(test_data)

    # Show table
    table.show()

    # Get the item
    item = table.item(0, table.COL_NEW)
    assert item is not None, 'Item should exist'

    # Track if editing started
    editing_started = []
    table.editing_started.connect(lambda row: editing_started.append(row))

    # Simulate double-click
    table._on_item_double_clicked(item)

    # Process events to allow QTimer.singleShot to fire
    QTest.qWait(100)
    app.processEvents()

    # Verify editing started
    assert (
        len(editing_started) == 1
    ), f'Editing should have started, got {editing_started}'
    assert editing_started[0] == 0, 'Should be editing row 0'
    assert table.is_editing(), 'Table should be in editing mode'
    assert table._editing_row == 0, 'Should be editing row 0'

    # Verify text was changed to basename only
    current_text = item.text()
    assert current_text == 'pippo', f'Expected "pippo", got "{current_text}"'

    print('✅ Test passed: Double-click edit mode works without crashes')

    # Cleanup
    table.close()

    return True


if __name__ == '__main__':
    try:
        result = test_double_click_edit_mode()
        if result:
            print('\\n✅ All tests passed!')
            sys.exit(0)
        else:
            print('\\n❌ Tests failed!')
            sys.exit(1)
    except Exception as e:
        print(f'\\n❌ Test failed with error: {e}')
        import traceback

        traceback.print_exc()
        sys.exit(1)
