# PlexRenamer - Release Notes v0.9.0

**Release Date:** 2025-11-12
**Status:** Beta - Feature Complete (Settings Pending)

**Language:** English | [Italiano](plexrenamer_v0.9.0.md)

---

## Release Summary

PlexRenamer v0.9.0 represents a fully functional beta release for normalizing video file names (movies and TV series) for Plex Media Server. The application is stable and ready to use, with all core features implemented. Only the Settings panel is missing to be considered release 1.0.

---

## Implemented Features

### Core Features

#### 1. Movie Renaming
- Batch processing of multiple files
- Automatic year extraction from filename
- Standardized format: `Movie Title (Year) - extras.mkv`
- Support for all major video formats

#### 2. TV Series Renaming
- Processing of entire season folders
- Episode numbering normalization (S##E## format)
- Single year prompt for all episodes
- Format: `Show Title (Year) - S01E01 - Episode Name.mkv`

#### 3. Inline Editing
- Direct editing in the preview table
- Real-time validation
- Immediate visual feedback on status
- Duplicate prevention during editing

#### 4. Validation System
- Automatic duplicate detection
- File conflict checking
- Real-time format validation
- Color-coded status indicators

### User Interface

#### GUI Components
- **MainWindow**: Main window with responsive layout
- **FileTable**: Editable table with inline validation
- **StatusBar**: Status bar with dynamic counters
- **CustomButtons**: Themed buttons with Windows-standard styles
- **Dialogs**: Dialogs for year input and user confirmations

#### Themes and Styling
- System theme support (light/dark)
- Semantic color palette for file states
- Consistent button styles following Windows guidelines
- Separation between structural and themeable properties

### Data Management

#### Models
- **MediaType**: Enum for media types (MOVIE, SERIES)
- **FileStatus**: File validation states
- **ProcessableFile**: Data model for processable files
- **SessionManager**: Application session management

#### Business Logic
- **FileAnalyzer**: File name parsing and formatting
- **MediaInfo**: File metadata extraction (duration, codec, resolution)
- **Utility Functions**: Helper functions for validation and checks

---

## Configuration File Changes

### 1. src/models/app_models.py

**Path:** `src/models/app_models.py`

**Changes Applied:**
```diff
  # App name and version
  APP_NAME = 'PlexRenamer'
- APP_VERSION = '2.0.0'
+ APP_VERSION = '0.9.0'
```

**Motivation:**
- Version update from 2.0.0 to 0.9.0 (Beta)
- This constant is used by `scripts/build.py` to:
  - Generate PyInstaller `.spec` file
  - Create installer with Inno Setup
  - Name output files (e.g., `PlexRenamer_Setup_v0.9.0.exe`)

**Usage:**
```python
# In scripts/build.py
from src.models.app_models import APP_NAME, APP_VERSION

# Used in:
# - Executable name: {APP_NAME}.exe
# - Installer name: {APP_NAME}_Setup_v{APP_VERSION}
# - Inno Setup script: AppVersion={APP_VERSION}
```

### 2. scripts/build.py

**Path:** `scripts/build.py`

**Status:** No changes needed - Configuration correct

**How it works:**
The `build.py` file is the main build script for the application. It automatically imports constants from `app_models.py`:

```python
from src.models.app_models import (
    APP_NAME,
    APP_VERSION,
    APP_ICON_PATH,
    INSTALLER_ICON_PATH,
    MAIN_WINDOW_ICON_PATH,
    BUTTON_FILMS_ICON_PATH,
    BUTTON_SERIES_ICON_PATH,
)
```

**Build Process:**

1. **Cleanup**: Removes `dist/`, `build/`, `installer/` folders and previous `*.spec` files
2. **PyInstaller**:
   - Generates `PlexRenamer.spec` with name and version from `app_models.py`
   - Creates `PlexRenamer.exe` executable in `dist/PlexRenamer/`
   - Includes all icons and PySide6 dependencies
3. **Inno Setup**:
   - Generates `.iss` script with current version
   - Creates installer `PlexRenamer_Setup_v0.9.0.exe` in `installer/`

**Generated Output:**
```
dist/PlexRenamer/PlexRenamer.exe          # Standalone executable
installer/PlexRenamer_Setup_v0.9.0.exe    # Windows installer
PlexRenamer.spec                           # PyInstaller spec (git ignored)
```

**Execution:**
```bash
python scripts/build.py
```

### 3. README.md

**Path:** `README.md`

**Changes Applied:**

1. **Version and status update:**
```diff
- **Version:** 1.0.0
- **Status:** Production Ready ✅
+ **Version:** 0.9.0
+ **Status:** Beta - Settings Pending ⚙️
```

2. **Complete restructuring oriented to end users:**
   - Added **Screenshots** section with 3 images (Series, Movie Editing, Results)
   - Prominent **Download** section with GitHub releases links
   - Expanded **Installation Options**:
     - Option 1: Windows Installer (recommended)
     - Option 2: Portable Version
     - Detailed System Requirements
   - New **Quick Start Guide** section (Movies and TV Series)
   - New **File Status Indicators** section (table)
   - New **FAQ & Support** section with common questions
   - Reduced **For Developers** section with link to DEVELOPMENT.md
   - Added **Roadmap** with future versions
   - Expanded **Credits** section with dependency links
   - **Technical documentation moved** to `docs/DEVELOPMENT.md`

**Motivation:**
- Version alignment with `app_models.py`
- Correct Beta status indication
- Transparency about missing functionality (Settings)
- **Complete installation options documentation for end users**
- **Clarity on how to obtain and use executables**
- **Distinction between end users and developers**

### 4. .gitignore

**Path:** `.gitignore`

**Changes Applied:**
```diff
- # Deprecated/Backup Files
- docs/development_steps/
+ # Documentation folder (excluded from repository)
+ docs/
```

**Motivation:**
- Complete exclusion of `docs/` folder from repository
- Simplified documentation management
- docs folder contains only development documentation not needed by end users

**Relevant .gitignore Sections:**

```gitignore
# test data
data_set/

# build and installer
dist/
installer/
build/
*.spec

# Documentation folder (excluded from repository)
docs/

# Application configuration (user-specific)
config/

# Python-specific ignores
__pycache__/
*.py[codz]
.venv/
venv/
*.egg-info/

# IDE
.vscode/
.idea/
```

### 5. requirements.txt

**Path:** `requirements.txt`

**Current Content:**
```
PySide6>=6.9.3
pyinstaller>=6.16.0
pymediainfo>=6.1.0
```

**Status:** No changes needed
- All dependencies are up to date
- Minimum versions correctly specified
- Production ready

### 6. PlexRenamer.spec

**Path:** `PlexRenamer.spec`

**Status:** No changes needed
- PyInstaller configuration correct
- All assets and icons included
- Console mode disabled (GUI app)
- Application icon configured

**Notes:**
- File automatically generated by PyInstaller
- Included in .gitignore (pattern `*.spec`)
- Absolute paths specific to development machine

---

## Project Structure

```
Renamer V 2.0/
├── .gitignore              ✅ Updated (excludes docs/)
├── .vscode/                # VS Code configuration
├── README.md               # Main documentation
├── requirements.txt        ✅ No changes
├── PlexRenamer.spec        # PyInstaller config (ignored)
├── run.py                  # Application launcher
│
├── src/                    # Source code
│   ├── __init__.py
│   ├── main.py            # Entry point
│   │
│   ├── core/              # Business logic
│   │   ├── file_analyzer.py
│   │   ├── session_manager.py
│   │   └── _utility.py
│   │
│   ├── gui/               # User interface
│   │   ├── main_window.py
│   │   ├── file_table.py
│   │   ├── status_bar.py
│   │   ├── buttons.py
│   │   └── dialogs.py
│   │
│   ├── models/            # Data models
│   │   ├── media_types.py
│   │   └── gui_models.py
│   │
│   ├── media_info/        # Metadata extraction
│   │   └── media_info.py
│   │
│   ├── presenters/        # Presentation layer (MVP pattern)
│   │   └── __init__.py
│   │
│   ├── utils/             # Utilities
│   │   └── logging_config.py
│   │
│   └── assets/            # Resources
│       ├── icons/         # Application icons
│       └── screenshots/   # UI screenshots
│
├── tests/                 # Test suite
│   ├── test_real_world_data.py
│   ├── test_gui_components.py
│   ├── test_main_window.py
│   └── test_integration.py
│
├── scripts/               # Utility scripts
│   └── build.py
│
├── config/                # User configuration (ignored)
├── data_set/              # Test dataset (ignored)
├── docs/                  # Documentation (ignored)
├── dist/                  # Build output (ignored)
├── build/                 # Build temp (ignored)
└── installer/             # Installer output (ignored)
```

---

## Supported File Formats

### Video
`.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v`, `.mpg`, `.mpeg`

### Episode Patterns
- `S01E01`, `s01e01` (standard format)
- `1x01`, `3x9` (alternative format)

### Valid Year Range
- Minimum: 1895 (first commercial film)
- Maximum: Current year
- Defined in: `src/models/gui_models.py::MIN_VALID_YEAR`

---

## Status Indicators

| Icon | Status | Description |
|------|--------|-------------|
| ✅ | Ready | File ready to rename |
| ⚠️ | Needs Year | Missing year, requires input |
| ❌ | Invalid | Invalid format, cannot process |
| ⏭️ | Already Normalized | File already in correct format |
| ⚠️ | Duplicate | Duplicate filename detected |

---

## Known Limitations

### Missing Features
- ❌ **Settings Panel** (planned for v1.0)
  - Year range configuration
  - Theme preferences
  - Formatting options
  - Path settings

### Technical Limitations
- Flat folder scanning only (no recursive subfolder processing)
- No Undo/Redo functionality
- Session-based (cannot mix movies and series)
- No media file preview

---

## Roadmap v1.0

### High Priority
- [ ] Implement Settings panel
- [ ] Customizable year range configuration
- [ ] Save/load user preferences

### Medium Priority
- [ ] Undo/Redo functionality
- [ ] Rename history
- [ ] Batch statistics

### Low Priority
- [ ] Media file preview
- [ ] Recursive folder scanning
- [ ] Advanced filters
- [ ] Theme customization

---

## Technical Notes

### Architecture
- **Pattern:** MVP (Model-View-Presenter) in transition
- **UI Framework:** PySide6 (Qt for Python)
- **Type Hints:** Complete throughout codebase
- **Docstrings:** Google-style on all public functions

### Best Practices Applied
- Separation of concerns (core/gui/models)
- Reusable and modular components
- Multi-level data validation
- Robust error handling
- Configurable logging

### Testing
- GUI component tests
- Integration tests
- Real data tests
- Visual testing available

---

## Installation and Usage

### Installation

```bash
# Clone repository
cd "path/to/Renamer V 2.0"

# Install dependencies
pip install -r requirements.txt

# Run application
python run.py
# or
python src/main.py
```

### Build Executable

```bash
# Build with PyInstaller
pyinstaller PlexRenamer.spec

# Output in dist/PlexRenamer/
```

---

## User Workflow

### Movies
1. Click **"Add Movie 🎬"**
2. Select one or more video files
3. Review preview (double-click to edit)
4. Click **"Apply Changes"** to rename
5. Click **"Start Over"** for new batch

### TV Series
1. Click **"Add Series 📺"**
2. Select season folder (e.g., "Season 1")
3. Enter year if prompted
4. Review preview (double-click to edit)
5. Click **"Apply Changes"** to rename
6. Click **"Start Over"** for new season

---

## Credits

**Development:** Qoder Project
**Framework:** PySide6 (Qt for Python)
**Media Info:** pymediainfo
**Build Tool:** PyInstaller

---

## License

Educational and Personal Use

---

## Release Summary

### Files Modified

1. **[src/models/app_models.py](src/models/app_models.py:13)**
   - `APP_VERSION`: `2.0.0` → `0.9.0`

2. **[README.md](README.md)**
   - `Version`: `1.0.0` → `0.9.0`
   - `Status`: `Production Ready ✅` → `Beta - Settings Pending ⚙️`
   - **Complete restructuring oriented to end users:**
     - New **Screenshots** section with 3 images (Series, Movie Editing, Results)
     - Prominent **Download** section with GitHub releases links
     - Expanded **Installation Options**:
       - Option 1: Windows Installer (recommended)
       - Option 2: Portable Version
       - Detailed System Requirements
     - New **Quick Start Guide** section (Movies and TV Series)
     - New **File Status Indicators** section (table)
     - New **FAQ & Support** section with common questions
     - Reduced **For Developers** section with link to DEVELOPMENT.md
     - Added **Roadmap** with future versions
     - Expanded **Credits** section with dependency links
   - **Technical documentation moved** to `docs/DEVELOPMENT.md`

3. **[.gitignore](.gitignore:10-11)**
   - Added complete `docs/` folder exclusion

### Files Created

1. **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)**
   - New complete technical documentation for developers
   - Contains all technical parts previously in README
   - Includes architecture, workflow, build, testing, contributing

### Files Verified (No Changes)

- **[scripts/build.py](scripts/build.py)**: Configuration correct, imports version from `app_models.py`
- **[requirements.txt](requirements.txt)**: Up-to-date dependencies
- **PlexRenamer.spec**: Automatically generated by `build.py` (git ignored)

### Next Steps

**To commit release 0.9.0:**

```bash
# 1. Initialize git repository (if not already done)
git init

# 2. Add all files (docs/ will be automatically excluded)
git add -A

# 3. Verify what will be committed
git status

# 4. Create release commit
git commit -m "Release 0.9.0 - PlexRenamer Beta

Initial release of PlexRenamer, a PySide6-based desktop application for
standardizing video file names for movies and TV series.

Features:
- Movie and TV series batch renaming
- Inline editing with real-time validation
- Duplicate detection and conflict prevention
- Smart year extraction and validation
- Status indicators and visual feedback
- Windows-standard themed UI

Configuration Changes:
- Updated app_models.py version to 0.9.0 (Beta status)
- Updated README.md version and status
- Updated .gitignore to exclude docs/ folder

Missing for v1.0:
- Settings panel implementation"

# 5. (Optional) Create release tag
git tag -a v0.9.0 -m "Release 0.9.0 - Beta"

# 6. (Optional) Push to remote repository
git remote add origin <repository-url>
git push -u origin main
git push --tags
```

---

**Release Status:** ✅ Beta - Fully Functional
**Next Milestone:** v1.0 - Settings Implementation
**Release Date:** 2025-11-12
