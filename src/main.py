"""Entry point for the File Renamer application."""

import sys
import logging
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.utils.logging_config import setup_logging

# Setup logging BEFORE importing other modules
# For production: use WARNING level (quiet)
# For development: use DEBUG level (verbose)
setup_logging(level=logging.WARNING)  # Production mode (quiet)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the application."""
    logger.info('Application starting...')
    app = QApplication()
    main_window = MainWindow(app)
    # show window - run app

    app.exec()
    logger.info('Application closed.')


if __name__ == '__main__':
    main()
