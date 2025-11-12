"""File processing business logic without GUI dependencies.

This module contains the FileProcessor class which handles all file processing
business logic independently. It can be used standalone or integrated with the
GUI application through signal-based events.

Main responsibilities:
- Process files through FileAnalyzer
- Validate formats and names
- Manage duplicate detection
- Execute physical file renames
- Provide processing statistics

Note: This module does not handle UI dialogs, user confirmations, or application
state management. Those concerns are delegated to AppPresenter.
"""

import logging
import os
import re

from ..models import (
    FileProcessingData,
    FileStatus,
    FileContentType,
    FILE_CONTENT_TYPE_SERIES,
    FILE_CONTENT_TYPE_FILM,
    DEFAULT_YEAR_PLACEHOLDER,
    EPISODE_PATTERN_COMBINED,
    EPISODE_SPLIT_PATTERN,
    SERIES_FULL_PATTERN,
    TITLE_YEAR_PATTERN,
    FILENAME_SEPARATORS,
    SEPARATOR_REPLACEMENTS,
)
from .file_analyzer import FileAnalyzer
from ._utility import is_video_file, is_normalized, check_for_duplicate_names

logger = logging.getLogger(__name__)


class FileProcessor:
    """Manages pure file processing business logic.

    Handles all file processing operations including analysis, validation,
    duplicate checking, and physical file renaming. Operates independently
    of the GUI layer through a clean API.

    Responsibilities:
    - Process files through FileAnalyzer
    - Validate formats and names
    - Manage duplicate detection
    - Execute physical file renames
    - Provide processing statistics

    Does NOT handle:
    - GUI interactions and dialogs
    - User confirmations
    - Application state (editing, selection, etc.)
    """

    def __init__(self) -> None:
        """Initialize the file processor with empty state."""
        self.current_mode: FileContentType | None = None
        self.file_data: list[FileProcessingData] = []

    # ========================================================================
    # PUBLIC API - Metodi principali
    # ========================================================================

    def set_mode(self, mode: FileContentType) -> None:
        """Set the processing mode (film or series).

        Args:
            mode: Processing mode - 'film' or 'series'
        """
        self.current_mode = mode

    def process_files(self, file_paths: list[str]) -> list[FileProcessingData]:
        """Process a list of files through the complete pipeline.

        Pipeline:
        1. Process each file individually through validation
        2. Check for duplicates among results
        3. Return processed list with status assignments

        Args:
            file_paths: List of file paths to process

        Returns:
            List of FileProcessingData with assigned statuses
        """
        self.file_data.clear()

        for file_path in file_paths:
            processed = self._process_single_file(file_path)
            self.file_data.append(processed)

        # Check duplicates dopo aver processato tutti i file
        self._update_duplicate_status()

        return self.file_data

    def reprocess_edited_file(self, row: int, new_filename: str) -> FileProcessingData:
        """Reprocess a file after user editing and validation.

        Validates the edited filename, runs it through FileAnalyzer, and updates
        the FileProcessingData with new formatting and status. Automatically
        detects if placeholder year is needed.

        Args:
            row: Index of the file in the internal list
            new_filename: New filename including extension

        Returns:
            Updated FileProcessingData with new name, status, and analyzer

        Raises:
            IndexError: If row index is out of range
            RuntimeError: If current_mode is not set before calling
        """
        if row >= len(self.file_data):
            raise IndexError(f"Row {row} out of range")

        if self.current_mode is None:
            raise RuntimeError('Cannot reprocess file: current_mode is not set')

        file_item = self.file_data[row]

        # Step 1: Video file check
        if not is_video_file(new_filename):
            file_item.new_name = '(not a video file)'
            file_item.status = FileStatus.NOT_VIDEO
            file_item.error_message = 'Not a valid video extension'
            return file_item

        # Step 2: FileAnalyzer processing
        # IMPORTANTE: Non fare check is_normalized qui
        # Tratta ogni edit come se fosse un nuovo caricamento
        try:
            folder = os.path.dirname(file_item.path)
            temp_path = os.path.join(folder, new_filename)

            analyzer = FileAnalyzer(temp_path, self.current_mode)
            base_name = os.path.splitext(new_filename)[0]
            analyzer.actual_title = base_name

            formatted_name = analyzer.formatter_media_name()

            # Determina status in base al risultato di FileAnalyzer
            # USA SEMPRE il formatted_name che ritorna FileAnalyzer
            if DEFAULT_YEAR_PLACEHOLDER in formatted_name:
                status = FileStatus.NEEDS_YEAR
                # NON sovrascrivere formatted_name!
                # Mostra il placeholder all'utente
            else:
                status = FileStatus.READY

            # Aggiorna file_item con il risultato di FileAnalyzer
            file_item.new_name = formatted_name  # ← USA SEMPRE questo
            file_item.status = status
            file_item.analyzer = analyzer
            file_item.error_message = None

        except ValueError as e:
            file_item.new_name = '(invalid format)'
            file_item.status = FileStatus.INVALID
            file_item.error_message = str(e)
        except Exception as e:
            file_item.new_name = f'(error: {str(e)})'
            file_item.status = FileStatus.INVALID
            file_item.error_message = str(e)

        return file_item

    def apply_series_year(self, year: str) -> int:
        """Apply a year to all series files that need it.

        Updates all files with NEEDS_YEAR status by setting their analyzer's
        media_year and reformatting. Updates duplicate status after applying.

        Args:
            year: Year string to apply (e.g., "2024")

        Returns:
            Number of files successfully updated with the year
        """
        updated_count = 0

        for item in self.file_data:
            if item.status == FileStatus.NEEDS_YEAR and item.analyzer:
                item.analyzer.set_media_year(year)
                try:
                    formatted_name = item.analyzer.formatter_media_name()
                    item.new_name = formatted_name
                    item.status = FileStatus.READY
                    updated_count += 1
                except Exception as e:
                    item.error_message = str(e)

        # Ricalcola duplicati dopo l'update
        self._update_duplicate_status()

        return updated_count

    def propagate_series_edit(self, edited_row: int, new_base_name: str) -> list[int]:
        """Propagate title and year changes to all series episodes.

        When editing any episode in a series, propagates the title and year
        to all other episodes while preserving each episode's original season/episode
        number and episode title.

        Propagation Logic:
        1. Extract title and year from the edited episode name
        2. Iterate all episodes (except the edited one)
        3. For each episode, construct new name with:
           - Extracted title and year
           - Original S##E## and episode title
        4. Update status and re-check duplicates

        Preconditions:
        - The edited file must already be reprocessed and normalized
        - Year must be validated
        - Episode number (E##) must not have been modified

        Args:
            edited_row: Index of the episode being edited
            new_base_name: New normalized name format: "Title (Year) - S##E## - EpTitle"

        Returns:
            List of row indices that were modified (excludes edited_row)

        Examples:
            >>> # Edit any episode in the series
            >>> processor.propagate_series_edit(2, "Breaking Bad (2008) - S01E03 - Pilot")
            >>> # Other episodes updated: "Breaking Bad (2008) - S01E01...", etc.
            [0, 1, 3, 4, ...]
        """
        # Propaga SEMPRE se siamo in modalità series
        if self.current_mode != FILE_CONTENT_TYPE_SERIES:
            return []

        logger.debug(f"propagate_series_edit: new_base_name='{new_base_name}'")

        # Estrai title, year E SEASON dal nome editato usando pattern centralizzato
        match = re.match(SERIES_FULL_PATTERN, new_base_name, re.IGNORECASE)

        if not match:
            logger.debug('Episode doesn\'t match series pattern')
            return []

        title = match.group(1).strip()
        year = match.group(2)

        logger.debug(f"Extracted from edited file: title='{title}', year={year}")

        # CRITICAL: Estrai anche la STAGIONE dal nome editato (non dall'originale!)
        # Cerca S##E## nel new_base_name
        season_match = re.search(r'[Ss](\d{1,2})[Ee]\d{1,2}', new_base_name)
        edited_season = None
        if season_match:
            edited_season = int(season_match.group(1))
            logger.info(
                f"Propagating series edit from row {edited_row}: "
                f"title='{title}', year={year}, season={edited_season:02d}"
            )
        else:
            logger.warning(f"Could not extract season from edited name: {new_base_name}")
            # Fallback: estrai solo title e year
            logger.info(
                f"Propagating series edit from row {edited_row}: "
                f"title='{title}', year={year} (no season change)"
            )

        modified_rows = []

        # Applica a tutti gli altri episodi (TRANNE l'episodio editato)
        for row in range(len(self.file_data)):
            # Skip l'episodio che è stato editato
            if row == edited_row:
                continue

            file_item = self.file_data[row]

            # Propaga su tutti i file modificabili (READY, NEEDS_YEAR, INVALID, DUPLICATE)
            # Skip SOLO: NOT_VIDEO, ALREADY_NORMALIZED
            if file_item.status in [
                FileStatus.NOT_VIDEO,
                FileStatus.ALREADY_NORMALIZED,
            ]:
                logger.debug(f"Row {row}: Skipping (status={file_item.status})")
                continue

            if not file_item.analyzer:
                continue

            try:
                # Estrai episode da nome originale usando pattern centralizzato
                base_name = os.path.splitext(file_item.original_name)[0]
                extension = os.path.splitext(file_item.original_name)[1]

                # Usa pattern combinato centralizzato (EPISODE_PATTERN_COMBINED)
                ep_match = re.search(EPISODE_PATTERN_COMBINED, base_name)

                if not ep_match:
                    logger.debug(f"Row {row}: No episode pattern found")
                    continue

                # Estrai season/episode dal nome ORIGINALE
                if ep_match.group(1):  # S##E## format
                    original_season = int(ep_match.group(1))
                    episode = int(ep_match.group(2))
                else:  # ##x## format
                    original_season = int(ep_match.group(3))
                    episode = int(ep_match.group(4))

                # CRITICAL FIX: Usa la stagione editata se disponibile, altrimenti quella originale
                season = edited_season if edited_season is not None else original_season

                logger.debug(f"Row {row}: original_season={original_season:02d}, edited_season={edited_season}, using season={season:02d}, episode={episode:02d}")

                season_ep = f"S{season:02d}E{episode:02d}"

                # Estrai remainder (episode title) dopo episode number
                # Usa pattern split centralizzato (EPISODE_SPLIT_PATTERN)
                parts = re.split(EPISODE_SPLIT_PATTERN, base_name, maxsplit=1)

                remainder = ''
                if len(parts) > 1 and parts[-1]:
                    # Pulisci remainder usando costanti centralizzate
                    remainder = parts[-1].strip(FILENAME_SEPARATORS)
                    # Applica replacements
                    for old_sep, new_sep in SEPARATOR_REPLACEMENTS.items():
                        remainder = remainder.replace(old_sep, new_sep)

                # Costruisci nuovo nome
                if remainder:
                    new_name = (
                        f"{title} ({year}) - {season_ep} - {remainder}{extension}"
                    )
                else:
                    new_name = f"{title} ({year}) - {season_ep}{extension}"

                # Update file_item
                file_item.new_name = new_name
                file_item.status = FileStatus.READY
                file_item.error_message = None

                # Update analyzer per consistenza
                if file_item.analyzer:
                    file_item.analyzer.set_media_year(year)
                    file_item.analyzer.actual_title = base_name

                modified_rows.append(row)
                logger.debug(f"Row {row}: Updated to {new_name}")

            except Exception as e:
                logger.error(f"Row {row}: Error propagating edit: {e}")
                continue

        # Ricalcola duplicati dopo le modifiche
        if modified_rows:
            self._update_duplicate_status()

        logger.info(f"Propagation complete: {len(modified_rows)} episodes updated")
        return modified_rows

    def force_edit_file(self, row: int) -> list[int]:
        """Force edit an ALREADY_NORMALIZED file by changing its status to READY.

        This allows editing of files that are already in the correct format.
        For series: changes ALL episodes to READY status.
        For movies: changes only the selected file.

        Args:
            row: Index of the file to force edit

        Returns:
            List of row indices that were modified

        Examples:
            >>> # Movie mode - single file
            >>> processor.force_edit_file(0)
            [0]

            >>> # Series mode - all episodes
            >>> processor.force_edit_file(2)
            [0, 1, 2, 3, 4, ...]
        """
        if row < 0 or row >= len(self.file_data):
            logger.warning(f"force_edit_file: Invalid row {row}")
            return []

        modified_rows = []

        # MOVIE MODE: Change only the selected file
        if self.current_mode == FILE_CONTENT_TYPE_FILM:
            file_item = self.file_data[row]

            if file_item.status == FileStatus.ALREADY_NORMALIZED:
                # Reprocess file to calculate new_name from current filename
                self._reprocess_normalized_file(file_item)
                modified_rows.append(row)
                logger.info(f"Force edit movie: row {row} changed to READY")
            else:
                logger.warning(f"force_edit_file: File at row {row} is not ALREADY_NORMALIZED (status={file_item.status})")

        # SERIES MODE: Change ALL ALREADY_NORMALIZED files
        elif self.current_mode == FILE_CONTENT_TYPE_SERIES:
            logger.info(f"Force edit series: changing all ALREADY_NORMALIZED files to READY")

            for idx in range(len(self.file_data)):
                file_item = self.file_data[idx]

                if file_item.status == FileStatus.ALREADY_NORMALIZED:
                    # Reprocess file to calculate new_name from current filename
                    self._reprocess_normalized_file(file_item)
                    modified_rows.append(idx)

            logger.info(f"Force edit complete: {len(modified_rows)} files changed to READY")

        # Update duplicates after status changes
        if modified_rows:
            self._update_duplicate_status()

        return modified_rows

    # ========================================================================
    # RENAME OPERATIONS - Operazioni di rinominazione
    # ========================================================================

    # ========================================================================
    # FILE OPERATIONS - Operazioni sui file
    # ========================================================================

    def remove_file(self, row: int) -> bool:
        """Remove a file from the processing list.

        Removes the file at the given index and updates duplicate status for
        remaining files.

        Args:
            row: Index of the file to remove

        Returns:
            True if successfully removed, False if index is invalid
        """
        if 0 <= row < len(self.file_data):
            del self.file_data[row]
            self._update_duplicate_status()
            logger.info(f"Removed file at row {row}")
            return True
        logger.warning(f"Cannot remove file: invalid row {row}")
        return False

    # ========================================================================
    # RENAME OPERATIONS - Operazioni di rinominazione
    # ========================================================================

    def execute_renames(self) -> tuple[int, int, list[str]]:
        """Alias for apply_renames() for backward compatibility.

        Returns:
            Tuple of (successes, total, errors) - see apply_renames()
        """
        return self.apply_renames()

    def apply_renames(self) -> tuple[int, int, list[str]]:
        """Execute physical file renames for all READY files.

        Iterates through files with READY status and performs actual filesystem
        renames. Successfully renamed files are removed from the internal list.
        OSError exceptions are caught and converted to error messages.

        Returns:
            Tuple of (success_count, total_count, errors)
            - success_count: Number of files successfully renamed
            - total_count: Total number of files that had READY status
            - errors: List of error messages (empty if all succeeded)
        """
        ready_files = [
            item for item in self.file_data if item.status == FileStatus.READY
        ]

        success_count = 0
        errors = []
        renamed_items = []

        for item in ready_files:
            try:
                folder = os.path.dirname(item.path)
                target_path = os.path.join(folder, item.new_name)

                os.rename(item.path, target_path)

                success_count += 1
                renamed_items.append(item)
            except OSError as e:
                error_msg = f"Error renaming {item.original_name}: {e}"
                errors.append(error_msg)

        # Rimuovi solo i file rinominati con successo
        self.file_data = [item for item in self.file_data if item not in renamed_items]

        return success_count, len(ready_files), errors

    def check_target_conflicts(self) -> list[str]:
        """Check for filename conflicts in target directory.

        A conflict occurs when the target filename already exists in the same
        directory and is a different file from the source.

        Returns:
            List of conflicting filenames (empty if no conflicts)
        """
        conflicts = []
        ready_files = [
            item for item in self.file_data if item.status == FileStatus.READY
        ]

        for item in ready_files:
            folder = os.path.dirname(item.path)
            target_path = os.path.join(folder, item.new_name)

            # Conflitto se esiste E non è lo stesso file
            if os.path.exists(target_path) and os.path.abspath(
                target_path
            ) != os.path.abspath(item.path):
                conflicts.append(item.new_name)

        return conflicts

    # ========================================================================
    # QUERY METHODS - Interrogazione stato
    # ========================================================================

    def get_statistics(self) -> dict[FileStatus, int]:
        """Get file count statistics by processing status.

        Returns:
            Dictionary mapping FileStatus to count of files with that status.
            Example: {FileStatus.READY: 5, FileStatus.INVALID: 2, ...}
        """
        counts: dict[FileStatus, int] = {}
        for item in self.file_data:
            counts[item.status] = counts.get(item.status, 0) + 1
        return counts

    def has_ready_files(self) -> bool:
        """Check if there are any files with READY status.

        Returns:
            True if at least one file has READY status, False otherwise
        """
        return any(item.status == FileStatus.READY for item in self.file_data)

    def has_blocking_issues(self) -> bool:
        """Check for blocking issues that prevent rename application.

        DEPRECATED: This method is maintained for backward compatibility but
        should not be used. Invalid and Not Video files do not block the apply
        operation - they are simply skipped during rename execution.

        Use has_ready_files() instead to determine if apply is possible.

        Returns:
            Always returns False (no files block the apply operation)
        """
        # Sempre False - nessun file "blocca" l'apply
        return False

    def needs_year_input(self) -> bool:
        """Check if year input is needed for any series files.

        Returns:
            True if any file has NEEDS_YEAR status, False otherwise
        """
        return any(item.status == FileStatus.NEEDS_YEAR for item in self.file_data)

    def get_file_data(self) -> list[FileProcessingData]:
        """Get the complete list of processed files.

        Returns:
            List of all FileProcessingData objects
        """
        return self.file_data

    def get_file_at(self, row: int) -> FileProcessingData | None:
        """Get a specific file by index.

        Args:
            row: Index of the file to retrieve

        Returns:
            FileProcessingData at the index, or None if index is out of range
        """
        if 0 <= row < len(self.file_data):
            return self.file_data[row]
        return None

    def is_empty(self) -> bool:
        """Check if the processor has no files.

        Returns:
            True if file list is empty, False otherwise
        """
        return len(self.file_data) == 0

    def clear(self) -> None:
        """Clear all files and reset the processor state."""
        self.file_data.clear()
        self.current_mode = None

    # ========================================================================
    # PRIVATE METHODS - Logica interna
    # ========================================================================

    def _reprocess_normalized_file(self, file_item: FileProcessingData) -> None:
        """Reprocess an ALREADY_NORMALIZED file to calculate new_name.

        Used when forcing edit on already normalized files. Takes the current
        filename and reprocesses it through FileAnalyzer to generate the
        proper new_name format.

        Args:
            file_item: FileProcessingData to reprocess (modified in place)
        """
        try:
            # Use current filename (without extension) as base
            current_filename = file_item.original_name

            # Create analyzer with current file
            analyzer = FileAnalyzer(file_item.path, self.current_mode)
            base_name = os.path.splitext(current_filename)[0]
            analyzer.actual_title = base_name

            # Get formatted name
            formatted_name = analyzer.formatter_media_name()

            # Update file_item
            file_item.new_name = formatted_name
            file_item.status = FileStatus.READY
            file_item.analyzer = analyzer
            file_item.error_message = None

            logger.debug(f"Reprocessed normalized file: {current_filename} -> {formatted_name}")

        except Exception as e:
            logger.error(f"Error reprocessing normalized file {file_item.original_name}: {e}")
            file_item.new_name = f'(error: {str(e)})'
            file_item.status = FileStatus.INVALID
            file_item.error_message = str(e)

    def _process_single_file(self, file_path: str) -> FileProcessingData:
        """Process a single file through the validation pipeline.

        Pipeline stages:
        1. Check if file is a video file (by MIME type)
        2. Check if file is already normalized
        3. Run through FileAnalyzer for format detection and normalization

        Args:
            file_path: Full path to the file to process

        Returns:
            FileProcessingData with assigned status and formatted name

        Raises:
            RuntimeError: If current_mode is not set
        """
        # AGGIUNGERE QUESTO CHECK
        if self.current_mode is None:
            raise RuntimeError('Cannot process file: current_mode is not set')

        filename = os.path.basename(file_path)

        # Step 1: Video file check
        if not is_video_file(file_path):
            return FileProcessingData(
                path=file_path,
                original_name=filename,
                new_name='(not a video file)',
                status=FileStatus.NOT_VIDEO,
                error_message='Not a valid video file',
            )

        # Step 2: Already normalized check
        if is_normalized(filename, self.current_mode):
            return FileProcessingData(
                path=file_path,
                original_name=filename,
                new_name='(already normalized)',
                status=FileStatus.ALREADY_NORMALIZED,
            )

        # Step 3: FileAnalyzer processing
        try:
            analyzer = FileAnalyzer(file_path, self.current_mode)
            analyzer.actual_title = filename
            formatted_name = analyzer.formatter_media_name()

            # Determina status in base a presenza placeholder year
            status = (
                FileStatus.NEEDS_YEAR
                if DEFAULT_YEAR_PLACEHOLDER in formatted_name
                else FileStatus.READY
            )

            return FileProcessingData(
                path=file_path,
                original_name=filename,
                new_name=formatted_name,
                status=status,
                analyzer=analyzer,
            )

        except ValueError as e:
            return FileProcessingData(
                path=file_path,
                original_name=filename,
                new_name='(invalid format)',
                status=FileStatus.INVALID,
                error_message=str(e),
            )
        except Exception as e:
            return FileProcessingData(
                path=file_path,
                original_name=filename,
                new_name=f"(error: {str(e)})",
                status=FileStatus.INVALID,
                error_message=str(e),
            )

    def _update_duplicate_status(self) -> None:
        """Update duplicate status for all files.

        Algorithm:
        1. Reset all DUPLICATE files to their original status
        2. Find new duplicates among processable files (READY, NEEDS_YEAR)
        3. Mark newly detected duplicates

        This is called after processing, year application, and edits to ensure
        duplicate detection stays synchronized with current names.
        """
        # Step 1: Reset DUPLICATE files al loro status originale
        for item in self.file_data:
            if item.status == FileStatus.DUPLICATE:
                # Determina status originale
                if DEFAULT_YEAR_PLACEHOLDER in item.new_name:
                    item.status = FileStatus.NEEDS_YEAR
                elif item.new_name and item.new_name != '(invalid format)':
                    item.status = FileStatus.READY
                else:
                    item.status = FileStatus.INVALID

        # Step 2: Trova duplicati attuali tra file processabili
        processable_items = [
            item
            for item in self.file_data
            if item.status in [FileStatus.READY, FileStatus.NEEDS_YEAR]
        ]

        new_names = [item.new_name for item in processable_items]
        duplicates = check_for_duplicate_names(new_names)

        # Step 3: Marca i duplicati trovati
        if duplicates:
            for dup_name, indices in duplicates.items():
                for idx in indices:
                    if idx < len(processable_items):
                        processable_items[idx].status = FileStatus.DUPLICATE
