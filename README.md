# File Renamer - Media File Normalization Tool

A PySide6-based desktop application for standardizing video file names for movies and TV series.

## Features

### 🎬 Movie Renaming

- Batch process multiple movie files
- Auto-extract year from filename
- Standardized format: `Movie Title (Year) - extras.mkv`
- Support for various video formats

### 📺 Series Renaming

- Process entire season folders
- Normalize episode numbering (S##E## format)
- Single year prompt for all episodes
- Format: `Show Title (Year) - S01E01 - Episode Name.mkv`

### ✨ Key Capabilities

- **Inline Editing** - Fix problematic files directly in preview
- **Real-time Validation** - Instant feedback on edits
- **Duplicate Detection** - Prevents naming conflicts
- **File Conflict Protection** - Checks before overwriting
- **Smart Year Detection** - Auto-extracts from 1895 to present
- **Status Feedback** - Clear visual indicators for all files

## Installation

PlexRenamer is available in two formats: **Installer** (recommended) and **Portable** version.

### Option 1: Windows Installer (Recommended)

1. Download `PlexRenamer_Setup_v0.9.0.exe` from the releases
2. Run the installer and follow the setup wizard
3. Choose installation directory (default: `C:\Program Files\PlexRenamer`)
4. Optionally create desktop shortcut
5. Launch PlexRenamer from Start Menu or desktop

**Features:**
- Automatic installation and uninstallation
- Start Menu integration
- Desktop shortcut option
- Automatic cleanup of configuration files on uninstall (optional)

### Option 2: Portable Version

1. Download `PlexRenamer_Portable_v0.9.0.zip` from the releases
2. Extract the ZIP file to your preferred location
3. Run `PlexRenamer.exe` from the extracted folder

**Features:**
- No installation required
- Can run from USB drive
- Completely self-contained
- Perfect for testing or temporary use

### Option 3: Run from Source (Developers)

**Requirements:**
- Python 3.9+
- PySide6 >= 6.9.3

**Setup:**

```bash
# Clone or download the project
cd "path/to/Renamer V 2.0"

# Install dependencies
pip install -r requirements.txt

# Run the application (Method 1 - Direct)
python src/main.py

# Run the application (Method 2 - Launcher)
python run.py
```

### Building from Source

To create your own executables and installer:

```bash
# Build executable and installer
python scripts/build.py

# Output:
# - dist/PlexRenamer/PlexRenamer.exe (portable)
# - installer/PlexRenamer_Setup_v0.9.0.exe (installer)
```

**Requirements for building:**
- Python 3.9+
- PyInstaller >= 6.16.0
- Inno Setup 6 (for Windows installer)

## Usage

### Movie Workflow

1. Click **"Add Movie 🎬"**
2. Select one or more video files
3. Review the preview (double-click to edit if needed)
4. Click **"Apply Changes"** to rename
5. Click **"Start Over"** for next batch

### Series Workflow

1. Click **"Add Series 📺"**
2. Select season folder (e.g., "Season 1")
3. If year is missing, enter it when prompted
4. Review the preview
5. Click **"Apply Changes"** to rename
6. Click **"Start Over"** for next season

## Supported Formats

### Video Files

`.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v`, `.mpg`, `.mpeg`

### Episode Patterns

- `S01E01`, `s01e01` (standard format)
- `1x01`, `3x9` (alternative format)

## File Status Indicators

| Icon | Status | Description |
|------|--------|-------------|
| ✅ | Ready | File ready to rename |
| ⚠️ | Needs Year | Missing year, requires input |
| ❌ | Invalid | Invalid format, cannot process |
| ⏭️ | Already Normalized | File already in correct format |
| ⚠️ | Duplicate | Duplicate filename detected |

## Project Structure

```
src/
├── core/              # Business logic
│   ├── file_analyzer.py    # File name parsing and formatting
│   ├── media_info.py       # File metadata extraction
│   └── _utility.py         # Helper functions
├── gui/               # User interface
│   ├── main_window.py      # Main application window
│   ├── file_table.py       # Preview table with editing
│   ├── status_bar.py       # Status display widget
│   ├── buttons.py          # Custom button components
│   └── dialogs.py          # User input dialogs
├── models/            # Data structures
│   ├── media_types.py      # Media type definitions
│   └── gui_models.py       # GUI data models
└── main.py            # Application entry point

tests/
├── test_real_world_data.py  # FileAnalyzer tests
├── test_gui_components.py   # Component tests
└── test_main_window.py      # Integration tests
```

## Interface Guidelines

The application follows comprehensive interface guidelines to ensure a consistent and professional user experience:

- **Windows-standard button styles** with custom classes for different action types
- **Themed appearance** with support for default, dark, and light themes
- **Consistent color scheme** with semantic colors for different statuses
- **Proper spacing and alignment** following UI best practices
- **Clear separation** between structural properties (padding, fonts) and themeable properties (colors)


## Design Principles

### Validation Pipeline

1. **is_video_file()** - Verify file is a video
2. **is_normalized()** - Check if already correct
3. **FileAnalyzer** - Process and format name

### Safety Features

- Pre-rename conflict detection
- Duplicate name prevention
- User confirmation before changes
- No mixing movies and series in one session

### User Experience

- Color-coded status feedback
- Inline editing with live validation
- Batch year input for series
- Clear error messages

## Development

### Running Tests

```bash
# Test core components
python tests/test_gui_components.py

# Test FileAnalyzer with real data
python tests/test_real_world_data.py

# Test button components
python tests/test_buttons.py
```

### Code Quality

- Full type hints throughout
- Comprehensive docstrings
- Modular, reusable components
- Clean separation of concerns

## Configuration

### Year Range

- Minimum: 1895 (first commercial film)
- Maximum: Current year
- Defined in: `src/models/gui_models.py::MIN_VALID_YEAR`

### Supported Episode Formats

Defined in: `src/core/file_analyzer.py::_extract_episode()`

## Known Limitations

- Flat folder scanning only (no recursive subfolder processing)
- No undo functionality (yet)
- Session-based (can't mix movies and series)

## Future Enhancements

- [ ] Undo/Redo functionality
- [ ] Settings/preferences panel
- [ ] Batch statistics
- [ ] Theme customization
- [ ] Rename history log
- [ ] File preview pane
- [ ] Advanced filtering options
- [ ] Recursive folder processing

## License

This project is for educational and personal use.

## Credits

Built with PySide6 (Qt for Python)

---

**Version:** 0.9.0
**Status:** Beta - Settings Pending ⚙️
