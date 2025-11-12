"""Logging configuration for the application."""

import logging
import sys
from pathlib import Path


def setup_logging(level=logging.WARNING, log_file=None):
    """Setup application logging.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging to file

    Usage:
        # Development (verbose)
        setup_logging(level=logging.DEBUG)

        # Production (quiet)
        setup_logging(level=logging.WARNING)
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Suppress verbose Qt/PySide6 warnings
    logging.getLogger('PySide6').setLevel(logging.WARNING)
    logging.getLogger('qt').setLevel(logging.WARNING)

    return root_logger


def get_logger(name):
    """Get logger for specific module.

    Args:
        name: Module name (use __name__)

    Returns:
        Logger instance

    Usage:
        logger = get_logger(__name__)
        logger.debug("Debug message with %s", variable)
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
    """
    return logging.getLogger(name)
