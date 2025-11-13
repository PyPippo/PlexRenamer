# PlexRenamer - User Guide

**Version:** 0.9.0
**Last Updated:** 2025-11-12

---

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Working with Movies](#working-with-movies)
- [Working with TV Series](#working-with-tv-series)
- [Inline Editing](#inline-editing)
- [Understanding Status Indicators](#understanding-status-indicators)
- [Common Scenarios](#common-scenarios)
- [Tips & Best Practices](#tips--best-practices)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## Introduction

PlexRenamer is a desktop application designed to automatically normalize video file names for Plex Media Server. It ensures your movie and TV series files follow Plex's naming conventions, making them easier to organize and identify.

### What PlexRenamer Does

- **Normalizes movie files** to format: `Movie Title (Year) - extras.mkv`
- **Normalizes TV series** to format: `Show Title (Year) - S01E01 - Episode Name.mkv`
- **Validates** file names in real-time
- **Detects duplicates** before renaming
- **Prevents conflicts** by checking if target files already exist

### What PlexRenamer Doesn't Do

- Does **not** move files between folders
- Does **not** fetch metadata from online databases
- Does **not** create copies (renames in place)
- Does **not** have undo functionality (yet)

---

## Installation

### Windows Installer (Recommended)

1. Download `PlexRenamer_Setup_v0.9.0.exe` from the [Releases page](https://github.com/username/plexrenamer/releases)
2. Double-click the installer
3. Follow the setup wizard:
   - Choose installation directory (default: `C:\Program Files\PlexRenamer`)
   - Optionally create desktop shortcut
   - Click Install
4. Launch PlexRenamer from:
   - Start Menu → PlexRenamer
   - Desktop shortcut (if created)

### Portable Version

1. Download `PlexRenamer_Portable_v0.9.0.zip` from the [Releases page](https://github.com/username/plexrenamer/releases)
2. Extract the ZIP file to any folder (e.g., `C:\Tools\PlexRenamer`)
3. Double-click `PlexRenamer.exe` inside the extracted folder

### System Requirements

- **OS:** Windows 10 or 11 (64-bit)
- **Disk Space:** ~150 MB
- **RAM:** 256 MB minimum
- No additional software needed

---

## Getting Started

### First Launch

When you launch PlexRenamer for the first time, you'll see:

1. **Main Window** with two large buttons:
   - **Add Movie 🎬** - For renaming movie files
   - **Add Series 📺** - For renaming TV series episodes

2. **File Preview Table** (initially empty)

3. **Status Bar** at the bottom showing:
   - Total files loaded
   - Files ready to rename
   - Files with issues

4. **Action Buttons** (initially disabled):
   - **Apply Changes** - Executes the rename operation
   - **Start Over** - Clears the session and starts fresh

### Important Concepts

**Session-based Operation:**
- Each session is for either movies OR series (not both)
- Click "Start Over" to begin a new session
- Cannot mix movies and series in one session

**Preview-First Approach:**
- Always review the preview before applying changes
- Edit any problematic files inline
- Check for duplicates or conflicts

---

## Working with Movies

### Basic Movie Workflow

1. **Click "Add Movie 🎬"**
   - Opens file browser

2. **Select Movie Files**
   - Navigate to your movie folder
   - Select one or more video files
   - Click Open

3. **Review the Preview**
   - PlexRenamer shows original and new names
   - Status icon indicates if file is ready
   - Year is automatically extracted (if present in filename)

4. **Apply Changes**
   - Click **Apply Changes** button
   - Confirm the operation
   - Wait for completion

5. **Start Over** (Optional)
   - Click **Start Over** to rename more movies
   - Previous session is cleared

### Movie Naming Format

PlexRenamer follows this format:

```
Movie Title (Year) - extras.ext
```

**Examples:**

| Original Filename | Renamed To |
|-------------------|------------|
| `The.Matrix.1999.1080p.mkv` | `The Matrix (1999).mkv` |
| `Inception_2010_BluRay.mp4` | `Inception (2010).mp4` |
| `Godfather.Part.II.1974.mkv` | `Godfather Part II (1974).mkv` |
| `Avatar.2009.EXTENDED.mkv` | `Avatar (2009) - EXTENDED.mkv` |

### Year Detection

PlexRenamer automatically extracts years from filenames:

- **Valid range:** 1895 (first commercial film) to current year
- **Common patterns recognized:**
  - `Movie.Title.2024.mkv`
  - `Movie_Title_[2024].mp4`
  - `Movie.Title.(2024).avi`

**If year is missing:**
- You'll be prompted to enter it manually
- Enter a 4-digit year (e.g., `2024`)
- Click OK

---

## Working with TV Series

### Basic Series Workflow

1. **Click "Add Series 📺"**
   - Opens folder browser

2. **Select Season Folder**
   - Navigate to series folder
   - Select the **season folder** (e.g., "Season 1", "S01")
   - Click Select Folder

3. **Enter Year** (if prompted)
   - If year is not in filenames, you'll be asked to enter it
   - Enter the year the series started (e.g., `2024`)
   - This applies to ALL episodes in the season

4. **Review the Preview**
   - Check episode numbering
   - Verify episode names
   - Look for any issues

5. **Apply Changes**
   - Click **Apply Changes**
   - Confirm the operation
   - Wait for completion

6. **Repeat for Other Seasons**
   - Click **Start Over**
   - Select next season folder
   - Repeat process

### Series Naming Format

PlexRenamer follows this format:

```
Show Title (Year) - S##E## - Episode Name.ext
```

**Examples:**

| Original Filename | Renamed To |
|-------------------|------------|
| `Breaking.Bad.S01E01.Pilot.mkv` | `Breaking Bad (2008) - S01E01 - Pilot.mkv` |
| `The.Office.1x01.pilot.mp4` | `The Office (2005) - S01E01 - Pilot.mp4` |
| `Stranger.Things.S02E05.mkv` | `Stranger Things (2016) - S02E05.mkv` |

### Episode Pattern Recognition

PlexRenamer recognizes these patterns:

**Standard Format:**
- `S01E01` - Season 1, Episode 1
- `s02e15` - Season 2, Episode 15
- `S03E09` - Season 3, Episode 9

**Alternative Format:**
- `1x01` - Season 1, Episode 1
- `2x15` - Season 2, Episode 15
- `3x9` - Season 3, Episode 9 (single-digit episode)

---

## Inline Editing

Sometimes PlexRenamer's automatic parsing needs correction. You can edit file names directly in the preview table.

### How to Edit

1. **Double-click** any cell in the "New Name" column
2. **Edit the text** directly
3. **Press Enter** or click outside to confirm
4. The file is **validated immediately**:
   - ✅ Green background = Valid
   - ❌ Red background = Invalid (duplicate or format error)

### What You Can Edit

- **Movie titles** - Fix typos or formatting
- **Years** - Change or add years
- **Episode names** - Correct episode titles
- **Extras info** - Add or modify extra tags (e.g., "EXTENDED")

### Validation Rules

**Movies:**
- Must include title and year: `Title (Year).ext`
- Year must be 4 digits between 1895 and current year
- Extension must match original file

**Series:**
- Must include show title, year, and episode: `Show (Year) - S##E##.ext`
- Year must be 4 digits
- Season/Episode must be in S##E## format
- Extension must match original file

### Editing Tips

- Press **Escape** to cancel editing
- **Tab** to move to next editable cell
- Edit multiple files before applying changes
- Check for red backgrounds (duplicates/errors)

---

## Understanding Status Indicators

Each file in the preview table has a status icon indicating its state:

| Icon | Status | Meaning | Action Needed |
|------|--------|---------|---------------|
| ✅ | **Ready** | File ready to rename | None - good to go! |
| ⚠️ | **Needs Year** | Year missing from filename | Edit to add year |
| ❌ | **Invalid** | Format invalid or parse failed | Edit filename or check format |
| ⏭️ | **Already Normalized** | File already in correct format | None - already correct |
| ⚠️ | **Duplicate** | Another file will have same name | Edit one of the duplicates |

### Status Colors

The "New Name" column uses background colors:

- **Green** - Valid, ready to rename
- **Red** - Problem (duplicate or invalid)
- **White** - Already normalized (no rename needed)

### Counter in Status Bar

The bottom status bar shows:

```
Total: 10 | Ready: 8 | Issues: 2
```

- **Total** - Total files loaded
- **Ready** - Files ready to rename (✅)
- **Issues** - Files with problems (⚠️ or ❌)

---

## Common Scenarios

### Scenario 1: Renaming Downloaded Movies

**Situation:** You downloaded several movies with messy filenames:
- `the.matrix.1999.1080p.BluRay.x264-GROUP.mkv`
- `inception_2010_720p.mkv`
- `avatar.2009.extended.edition.mkv`

**Steps:**
1. Click "Add Movie 🎬"
2. Select all three files
3. Review preview - should all be ✅ Ready
4. Click "Apply Changes"
5. Done! Files renamed to:
   - `The Matrix (1999).mkv`
   - `Inception (2010).mkv`
   - `Avatar (2009) - EXTENDED EDITION.mkv`

### Scenario 2: Series with Missing Year

**Situation:** Season folder has episodes without year:
- `Breaking.Bad.S01E01.Pilot.mkv`
- `Breaking.Bad.S01E02.Cats.in.the.Bag.mkv`
- etc.

**Steps:**
1. Click "Add Series 📺"
2. Select season folder
3. Dialog appears: "Enter year for Breaking Bad"
4. Enter `2008`
5. All episodes now show with year: `Breaking Bad (2008) - S##E##...`
6. Click "Apply Changes"

### Scenario 3: Fixing Duplicate Names

**Situation:** Two files would get the same name:
- `Inception.2010.mkv` → `Inception (2010).mkv` ⚠️ Duplicate
- `Inception.2010.IMAX.mkv` → `Inception (2010).mkv` ⚠️ Duplicate

**Steps:**
1. Notice both files are marked ⚠️ Duplicate (red background)
2. Double-click second file's "New Name"
3. Edit to: `Inception (2010) - IMAX.mkv`
4. Press Enter
5. Both now show ✅ Ready (green background)
6. Click "Apply Changes"

### Scenario 4: Multiple Seasons

**Situation:** TV series with 3 seasons to rename

**Steps:**
1. Click "Add Series 📺" → Select "Season 1" folder
2. Review and Apply Changes
3. Click "Start Over"
4. Click "Add Series 📺" → Select "Season 2" folder
5. Review and Apply Changes
6. Click "Start Over"
7. Click "Add Series 📺" → Select "Season 3" folder
8. Review and Apply Changes
9. All done!

---

## Tips & Best Practices

### Before You Start

1. **Make a backup** of your files (especially important - no undo!)
2. **Test with a few files first** before processing entire library
3. **Ensure files are in correct folders** (season folders for series)
4. **Close Plex** if files are being scanned/used

### While Using PlexRenamer

1. **Always review the preview** carefully before applying
2. **Check for red backgrounds** (duplicates or errors)
3. **Use inline editing** to fix problematic files
4. **Don't mix movies and series** - use separate sessions
5. **Rename one season at a time** for TV series

### After Renaming

1. **Verify files in File Explorer** to confirm renames
2. **Run Plex library scan** to update metadata
3. **Check Plex** to ensure files are properly identified

### Organizing Your Library

**Recommended Folder Structure:**

```
Movies/
├── The Matrix (1999).mkv
├── Inception (2010).mkv
└── Avatar (2009).mkv

TV Shows/
├── Breaking Bad/
│   ├── Season 1/
│   │   ├── Breaking Bad (2008) - S01E01 - Pilot.mkv
│   │   └── Breaking Bad (2008) - S01E02 - Cat's in the Bag.mkv
│   └── Season 2/
│       └── Breaking Bad (2008) - S02E01 - Seven Thirty-Seven.mkv
└── The Office/
    └── Season 1/
        └── The Office (2005) - S01E01 - Pilot.mkv
```

---

## Troubleshooting

### Problem: Files Not Showing Up

**Possible Causes:**
- Selected wrong folder
- No video files in folder
- Files are in subfolders (PlexRenamer doesn't scan recursively)

**Solutions:**
- Verify folder contains video files (`.mkv`, `.mp4`, etc.)
- Select the correct folder with video files
- Move files to a single folder (no nested folders)

### Problem: Year Not Detected

**Possible Causes:**
- Year not in filename
- Year in unexpected format
- Year out of valid range (1895 - current year)

**Solutions:**
- Enter year manually when prompted
- Use inline editing to add year
- Check filename for year in format like `2024` or `(2024)`

### Problem: Episode Not Detected

**Possible Causes:**
- Episode pattern not recognized
- Non-standard numbering
- Multiple episode indicators confusing parser

**Solutions:**
- Check filename has `S##E##` or `#x##` pattern
- Use inline editing to fix episode number
- Rename files manually to include proper episode pattern

### Problem: Duplicate Warning

**Possible Causes:**
- Two files would result in same name
- File already exists with target name

**Solutions:**
- Use inline editing to differentiate files
- Add extra info like `- EXTENDED`, `- DC`, `- Part 1`
- Check if target file already exists in folder

### Problem: Apply Changes Doesn't Work

**Possible Causes:**
- Files have issues (red background)
- Duplicates not resolved
- Files in use by another program

**Solutions:**
- Fix all files showing red backgrounds
- Resolve duplicate names
- Close programs using the files (Plex, media players)
- Check file permissions (not read-only)

---

## FAQ

### Can I undo renames?

**No**, there is currently no undo functionality. PlexRenamer renames files in place permanently. Always review the preview carefully and consider backing up your files first. Undo/Redo is planned for v1.0.

### Can I rename files in subfolders?

**No**, PlexRenamer only scans the selected folder, not subfolders. This is a current limitation. Recursive folder processing is planned for a future release.

### Can I mix movies and TV series?

**No**, each session is either for movies OR TV series, not both. This prevents confusion and ensures correct naming conventions. Use "Start Over" to switch between types.

### What video formats are supported?

PlexRenamer supports all common video formats:
`.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v`, `.mpg`, `.mpeg`

### What happens to my original files?

Files are **renamed in place** - no copies are made. The original filename is lost (no undo). The file content is unchanged, only the filename changes.

### Can PlexRenamer fetch metadata from IMDB/TMDB?

**No**, PlexRenamer does not connect to online databases. It only parses and formats filenames based on existing information in the filename.

### Does PlexRenamer work with Plex automatically?

PlexRenamer prepares files for Plex by using the correct naming format, but it doesn't directly interact with Plex. After renaming, refresh your Plex library to see the changes.

### Can I customize the naming format?

**Not yet**. PlexRenamer uses the standard Plex naming conventions. Custom formatting options are planned for v1.0 (Settings panel).

### What if files already have correct names?

Files already in the correct format are marked with ⏭️ "Already Normalized" and are skipped during renaming. No changes are made to these files.

### Can I run PlexRenamer from a USB drive?

**Yes!** Use the Portable version. Extract the ZIP to your USB drive and run `PlexRenamer.exe` directly. No installation needed.

---

## Support & Feedback

### Getting Help

- **User Guide:** You're reading it!
- **GitHub Issues:** [Report bugs or request features](https://github.com/username/plexrenamer/issues)
- **README:** Check the [main README](../README.md) for quick reference

### Reporting Bugs

When reporting a bug, please include:

1. **PlexRenamer version** (shown at bottom of window)
2. **Windows version** (10 or 11)
3. **Steps to reproduce** the issue
4. **Screenshot** (if applicable)
5. **Example filenames** that cause the problem (if privacy allows)

### Feature Requests

We welcome feature requests! Please:

1. Check [existing issues](https://github.com/username/plexrenamer/issues) first
2. Describe the feature clearly
3. Explain the use case / why it's needed
4. Provide examples if applicable

---

## Appendix: Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Double-click** | Edit cell in preview table |
| **Enter** | Confirm edit |
| **Escape** | Cancel edit |
| **Tab** | Move to next editable cell |

---

**Version:** 0.9.0
**Last Updated:** 2025-11-12
**Need more help?** Check the [Developer Documentation](DEVELOPMENT.md) or [open an issue](https://github.com/username/plexrenamer/issues)
