#!/usr/bin/env python3
"""Test button components functionality."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel
from src.gui.buttons import LoadButton, ServiceButton, ExitButton


def test_buttons():
    """Test that all button types can be created and displayed."""
    print('Testing button components...')

    app = QApplication(sys.argv)

    # Create a test window
    window = QWidget()
    window.setWindowTitle('Button Test')
    layout = QVBoxLayout()

    # Add a label
    layout.addWidget(QLabel('Button Style Test'))

    # Test LoadButton
    load_btn = LoadButton('Load Button')
    layout.addWidget(load_btn)

    # Test ServiceButton
    service_btn = ServiceButton('Service Button')
    layout.addWidget(service_btn)

    # Test ExitButton
    exit_btn = ExitButton('Exit Button')
    layout.addWidget(exit_btn)

    # Test disabled buttons
    disabled_load = LoadButton('Disabled Load')
    disabled_load.setEnabled(False)
    layout.addWidget(disabled_load)

    disabled_service = ServiceButton('Disabled Service')
    disabled_service.setEnabled(False)
    layout.addWidget(disabled_service)

    disabled_exit = ExitButton('Disabled Exit')
    disabled_exit.setEnabled(False)
    layout.addWidget(disabled_exit)

    window.setLayout(layout)
    window.show()

    print('✅ Button components created successfully')
    print('✅ Window displayed - check visual appearance')
    print('Close the window to continue...')

    # Run the application
    sys.exit(app.exec())


if __name__ == '__main__':
    test_buttons()
