#!/usr/bin/env python3
"""Visual test to verify button styles are applied in the UI."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel
from src.gui.buttons import LoadButton, ServiceButton, ExitButton
from src.gui.themes import get_theme, apply_theme_to_app


def visual_test():
    """Test that button styles are visually applied."""
    app = QApplication(sys.argv)

    # Apply theme
    theme = get_theme('default')
    apply_theme_to_app(app, theme)

    # Create a test window
    window = QWidget()
    window.setWindowTitle('Button Style Visual Test')
    layout = QVBoxLayout()

    # Add a label
    layout.addWidget(QLabel('Check the font size and weight of each button:'))

    # Test LoadButton (should have 15pt bold font)
    load_btn = LoadButton('Load Button (15pt bold)')
    layout.addWidget(load_btn)

    # Test ServiceButton (should have 9pt normal font)
    service_btn = ServiceButton('Service Button (9pt normal)')
    layout.addWidget(service_btn)

    # Test ExitButton (should have 9pt normal font)
    exit_btn = ExitButton('Exit Button (9pt normal)')
    layout.addWidget(exit_btn)

    window.setLayout(layout)
    window.show()

    print("Visual test running. Check the window to see the button styles.")
    print("LoadButton should have 15pt bold font, others should have 9pt normal font.")
    print("Close the window to exit.")

    # Run the application
    sys.exit(app.exec())


if __name__ == '__main__':
    visual_test()
