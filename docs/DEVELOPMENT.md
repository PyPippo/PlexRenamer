# PlexRenamer - Developer Documentation

This document provides technical information for developers who want to contribute to PlexRenamer or understand its architecture.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Architecture Overview](#architecture-overview)
- [Design Principles](#design-principles)
- [Development Workflow](#development-workflow)
- [Building & Packaging](#building--packaging)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Contributing](#contributing)

---

## Getting Started

### Prerequisites

- **Python:** 3.9 or higher
- **Git:** For version control
- **IDE:** VS Code recommended (with Python extension)
- **PyInstaller:** For building executables (optional)
- **Inno Setup 6:** For creating Windows installers (optional)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/username/plexrenamer.git
cd plexrenamer

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
# or
python src/main.py
```

### Dependencies

**Runtime:**
- **PySide6 >= 6.9.3** - Qt for Python GUI framework
- **pymediainfo >= 6.1.0** - Media file metadata extraction

**Build Tools:**
- **pyinstaller >= 6.16.0** - Executable packaging
- **Inno Setup 6** - Windows installer creation

---

## Project Structure

```
PlexRenamer/
├── src/                          # Source code
│   ├── __init__.py
│   ├── main.py                   # Application entry point
│   ├── config.py                 # Configuration constants
│   │
│   ├── core/                     # Business logic
│   │   ├── __init__.py
│   │   ├── file_analyzer.py     # File name parsing and formatting
│   │   ├── file_processor.py    # File renaming operations
│   │   ├── session_manager.py   # Session state management
│   │   └── _utility.py          # Helper functions
│   │
│   ├── gui/                      # User interface
│   │   ├── __init__.py
│   │   ├── main_window.py       # Main application window
│   │   ├── file_table.py        # Editable preview table
│   │   ├── status_bar.py        # Status display widget
│   │   ├── buttons.py           # Custom button components
│   │   ├── dialogs.py           # User input dialogs
│   │   ├── themes.py            # Theme and styling
│   │   └── media_info_panel.py  # Media info display
│   │
│   ├── models/                   # Data structures
│   │   ├── __init__.py
│   │   ├── media_types.py       # Media type enums
│   │   ├── gui_models.py        # GUI data models
│   │   ├── core_models.py       # Core business models
│   │   └── app_models.py        # Application metadata
│   │
│   ├── media_info/               # Media metadata
│   │   ├── __init__.py
│   │   ├── media_info.py        # MediaInfo integration
│   │   └── media_metadata.py    # Metadata models
│   │
│   ├── presenters/               # MVP pattern (in development)
│   │   ├── __init__.py
│   │   └── app_presenter.py
│   │
│   ├── utils/                    # Utilities
│   │   ├── __init__.py
│   │   └── logging_config.py    # Logging configuration
│   │
│   └── assets/                   # Resources
│       ├── icons/               # Application icons (.ico)
│       └── screenshots/         # UI screenshots (.png)
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_real_world_data.py  # FileAnalyzer tests
│   ├── test_gui_components.py   # Component tests
│   ├── test_main_window.py      # Integration tests
│   ├── test_integration.py      # E2E tests
│   └── report/
│       └── TESTING_REPORT.md    # Test results
│
├── scripts/                      # Build and utility scripts
│   └── build.py                 # Build script (PyInstaller + Inno Setup)
│
├── docs/                         # Documentation (ignored by git)
│   ├── DEVELOPMENT.md           # This file
│   ├── USER_GUIDE.md            # User manual
│   └── plexrenamer_v0.9.0.md    # Release notes
│
├── config/                       # User configuration (ignored by git)
├── data_set/                     # Test data (ignored by git)
├── dist/                         # Build output (ignored by git)
├── build/                        # Build temp files (ignored by git)
├── installer/                    # Installer output (ignored by git)
│
├── .gitignore                    # Git ignore rules
├── .vscode/                      # VS Code settings
├── README.md                     # Main documentation
├── requirements.txt              # Python dependencies
├── run.py                        # Application launcher
└── PlexRenamer.spec              # PyInstaller spec (auto-generated)
```

---

## Architecture Overview

PlexRenamer follows a layered architecture with clear separation of concerns:

### Layers

1. **GUI Layer** (`src/gui/`)
   - PySide6-based user interface
   - Handles user input and display
   - Emits signals for user actions

2. **Core Layer** (`src/core/`)
   - Business logic implementation
   - File analysis and renaming
   - Session state management

3. **Models Layer** (`src/models/`)
   - Data structures and enums
   - Application metadata
   - Type definitions

4. **Media Info Layer** (`src/media_info/`)
   - Media file metadata extraction
   - Integration with pymediainfo

5. **Presenters Layer** (`src/presenters/`)
   - MVP pattern implementation (in development)
   - Mediates between GUI and Core

### Key Components

#### FileAnalyzer (`src/core/file_analyzer.py`)

Responsible for parsing and normalizing file names.

**Key Methods:**
- `analyze_movie(filename)` - Parse movie file names
- `analyze_series(filename, year)` - Parse TV series file names
- `_extract_year(filename)` - Extract year from filename
- `_extract_episode(filename)` - Extract episode information

**Output Format:**
- Movies: `Movie Title (Year) - extras.ext`
- Series: `Show Title (Year) - S01E01 - Episode Name.ext`

#### SessionManager (`src/core/session_manager.py`)

Manages application session state.

**Responsibilities:**
- Track loaded files
- Maintain media type (movie/series)
- Prevent mixing media types in one session
- Duplicate detection

#### FileTable (`src/gui/file_table.py`)

Editable table widget for file preview.

**Features:**
- Inline editing with validation
- Real-time duplicate detection
- Status color coding
- Double-click to edit

---

## Design Principles

### 1. Validation Pipeline

Every file goes through a multi-step validation process:

```python
1. is_video_file(path) → Verify file extension
2. is_normalized(filename) → Check if already correct format
3. FileAnalyzer.analyze() → Parse and format name
4. Duplicate detection → Check for conflicts
5. File conflict check → Verify target doesn't exist
```

### 2. Safety Features

- **Pre-rename validation** - All checks before any file operations
- **Duplicate prevention** - Cannot create files with same name
- **User confirmation** - Explicit "Apply Changes" required
- **Session isolation** - Cannot mix movies and series

### 3. User Experience

- **Color-coded feedback** - Visual status indicators
- **Inline editing** - Fix issues without re-loading
- **Live validation** - Instant feedback on edits
- **Clear error messages** - Actionable user guidance

### 4. Code Quality

- **Type hints** - Full type annotations throughout
- **Docstrings** - Google-style docstrings on all public functions
- **Modular design** - Reusable, testable components
- **Clean separation** - GUI, logic, and data layers

---

## Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow existing code style
   - Add type hints
   - Write docstrings
   - Update tests if needed

3. **Test your changes**
   ```bash
   python tests/test_gui_components.py
   python tests/test_real_world_data.py
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: Add feature description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention

Follow conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `style:` - Code style changes (formatting, etc.)
- `chore:` - Build, dependencies, etc.

---

## Building & Packaging

### Build Configuration

Version and app name are centralized in `src/models/app_models.py`:

```python
APP_NAME = 'PlexRenamer'
APP_VERSION = '0.9.0'
```

The build script (`scripts/build.py`) automatically imports these values.

### Build Process

```bash
# Build both installer and portable version
python scripts/build.py
```

**Output:**
- `dist/PlexRenamer/PlexRenamer.exe` - Portable executable
- `installer/PlexRenamer_Setup_v0.9.0.exe` - Windows installer
- `PlexRenamer.spec` - PyInstaller spec file (auto-generated)

### Build Steps

1. **Clean** - Remove previous build artifacts
2. **PyInstaller** - Create standalone executable
   - Collects all dependencies
   - Includes PySide6 libraries
   - Embeds icons and resources
3. **Inno Setup** - Create Windows installer
   - Auto-generates `.iss` script
   - Includes Start Menu shortcuts
   - Optional desktop shortcut
   - Uninstaller with config cleanup

### Manual PyInstaller

```bash
# Generate spec file
pyinstaller --name PlexRenamer --windowed --onedir \
  --collect-all PySide6 \
  --icon src/assets/icons/app_icon.ico \
  src/main.py

# Build from spec
pyinstaller PlexRenamer.spec
```

---

## Testing

### Test Structure

- `test_real_world_data.py` - FileAnalyzer with real file names
- `test_gui_components.py` - GUI component unit tests
- `test_main_window.py` - Integration tests
- `test_integration.py` - End-to-end tests

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_gui_components.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Visual Testing

```bash
# Launch visual test
python tests/visual_test.py
```

---

## Code Quality

### Type Hints

Full type annotations are required:

```python
def analyze_movie(self, filename: str) -> tuple[str, bool]:
    """Analyze movie filename."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def analyze_series(self, filename: str, year: int | None) -> tuple[str, bool]:
    """Analyze TV series filename.

    Args:
        filename: Original filename to analyze
        year: Year to use if not found in filename

    Returns:
        Tuple of (normalized_name, success_flag)

    Raises:
        ValueError: If year is invalid
    """
    ...
```

### Code Style

- Follow PEP 8
- Use meaningful variable names
- Keep functions focused and small
- Add comments for complex logic

---

## Configuration

### Year Range

Configurable in `src/models/gui_models.py`:

```python
MIN_VALID_YEAR = 1895  # First commercial film
# MAX_VALID_YEAR = Current year (auto-detected)
```

### Supported Formats

Video extensions in `src/core/_utility.py`:

```python
VIDEO_EXTENSIONS = {
    '.mp4', '.mkv', '.avi', '.mov', '.wmv',
    '.flv', '.webm', '.m4v', '.mpg', '.mpeg'
}
```

### Episode Patterns

Regex patterns in `src/core/file_analyzer.py`:

```python
# Standard: S01E01
EPISODE_PATTERN_1 = r'[Ss](\d{1,2})[Ee](\d{1,2})'

# Alternative: 1x01
EPISODE_PATTERN_2 = r'(\d{1,2})x(\d{1,2})'
```

---

## Contributing

We welcome contributions! Here's how to get started:

### 1. Fork & Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/yourusername/plexrenamer.git
```

### 2. Set Up Development Environment

```bash
cd plexrenamer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create Feature Branch

```bash
git checkout -b feature/amazing-feature
```

### 4. Make Changes

- Follow the code quality guidelines
- Add tests for new features
- Update documentation

### 5. Test

```bash
python -m pytest tests/
```

### 6. Commit & Push

```bash
git commit -m "feat: Add amazing feature"
git push origin feature/amazing-feature
```

### 7. Create Pull Request

Open a PR on GitHub with:
- Clear description of changes
- Screenshots if UI changes
- Link to related issues

---

## Known Issues & Limitations

### Current Limitations

- **No Undo** - File renames are permanent
- **Flat Folders Only** - No recursive subfolder processing
- **Session-based** - Cannot mix movies and series
- **No Settings Panel** - Planned for v1.0

### Planned Improvements

See [Roadmap](../README.md#roadmap) in main README.

---

## Additional Resources

- **[PySide6 Documentation](https://doc.qt.io/qtforpython-6/)**
- **[PyInstaller Manual](https://pyinstaller.org/en/stable/)**
- **[Inno Setup Documentation](https://jrsoftware.org/ishelp/)**
- **[Python Type Hints](https://docs.python.org/3/library/typing.html)**

---

## Contact & Support

- **GitHub Issues:** [https://github.com/username/plexrenamer/issues](https://github.com/username/plexrenamer/issues)
- **Developer:** Qoder Project

---

**Last Updated:** 2025-11-12
**Version:** 0.9.0
