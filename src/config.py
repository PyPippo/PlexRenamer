"""Application configuration management.

This module handles persistent application settings using JSON serialization.
It manages:
- Window state (size, position, maximized state)
- Last used directories for movies and series
- UI theme (currently supported: 'default', future extensions possible)

Configuration is stored in 'config/settings.json' and automatically loaded/saved
on application startup/shutdown. If the file is missing or corrupted, default values are used.

The AppConfig class provides methods to:
- Load configuration from file
- Save configuration to file
- Initialize with default values
- Ensure the config directory exists

All configuration values are stored in a structured, type-safe way using dataclasses,
making the code maintainable and easy to extend.
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Any
from .models.app_models import APP_NAME

@dataclass
class WindowConfig:
    """Window state configuration."""

    width: int = 900
    height: int = 500
    x: int | None = None
    y: int | None = None
    maximized: bool = False


@dataclass
class AppConfig:
    """Application configuration."""

    window: WindowConfig
    last_movie_directory: str = ''
    last_series_directory: str = ''
    theme: str = 'default'  # for future theme support

    def __init__(
        self,
        window: WindowConfig | None = None,
        last_movie_directory: str = '',
        last_series_directory: str = '',
        theme: str = 'default',
    ):
        """Initialize application configuration.

        Args:
            window: Window configuration
            last_movie_directory: Last used directory for movie selection
            last_series_directory: Last used directory for series selection
            theme: Application theme name
        """
        self.window = window or WindowConfig()
        self.last_movie_directory = last_movie_directory
        self.last_series_directory = last_series_directory
        self.theme = theme

    @classmethod
    def load(cls, config_file: Path) -> 'AppConfig':
        """Load configuration from file.

        Args:
            config_file: Path to configuration file

        Returns:
            AppConfig: Loaded configuration or default if file doesn't exist
        """
        if not config_file.exists():
            return cls()

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Parse window config
            window_data = data.get('window', {})
            window = WindowConfig(
                width=window_data.get('width', 900),
                height=window_data.get('height', 500),
                x=window_data.get('x'),
                y=window_data.get('y'),
                maximized=window_data.get('maximized', False),
            )

            return cls(
                window=window,
                last_movie_directory=data.get('last_movie_directory', ''),
                last_series_directory=data.get('last_series_directory', ''),
                theme=data.get('theme', 'default'),
            )

        except (json.JSONDecodeError, KeyError, ValueError):
            # If config is corrupted, return default
            return cls()

    def save(self, config_file: Path) -> None:
        """Save configuration to file.

        Args:
            config_file: Path to configuration file
        """
        # Ensure config directory exists
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict
        data = {
            'window': asdict(self.window),
            'last_movie_directory': self.last_movie_directory,
            'last_series_directory': self.last_series_directory,
            'theme': self.theme,
        }

        # Write to file
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)


def get_config_file() -> Path:
    """Get path to configuration file.

    Returns:
        Path: Path to settings.json in config directory

    Note:
        When running from source, uses project_root/config/settings.json
        When running as installed executable, uses AppData/APP_NAME/config/settings.json
    """
    import sys
    
    # Check if running as PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - use AppData
        if sys.platform == 'win32':
            # Windows: use %APPDATA%
            appdata = Path.home() / 'AppData' / 'Roaming' / APP_NAME
        elif sys.platform == 'darwin':
            # macOS: use ~/Library/Application Support
            appdata = Path.home() / 'Library' / 'Application Support' / APP_NAME
        else:
            # Linux: use ~/.config
            appdata = Path.home() / '.config' / APP_NAME

        return appdata / 'config' / 'settings.json'
    else:
        # Running from source - use project directory
        project_root = Path(__file__).parent.parent
        return project_root / 'config' / 'settings.json'
