"""Main organizer service for analyzing and organizing files."""

import shutil
from pathlib import Path
from typing import Dict, Optional, List
from collections import defaultdict

from models.result import (
    ToolResult, DuplicateGroup, DuplicatesResult, FilenameSuggestion,
    OrganizationResult, OrganizationChange, FolderScanResult, FileTypeStats,
    ErrorInfo
)
from utils import (
    validate_folder_path, validate_file_path, is_text_file, read_text_file,
    calculate_file_hash, calculate_quick_hash, is_generic_filename, get_all_files,
    extract_keywords_from_content, sanitize_filename, is_hidden_file
)
from utils.file_utils import TEXT_EXTENSIONS
from utils.errors import FolderAccessError
import logging

logger = logging.getLogger(__name__)


class OrganizerService:
    """Service for analyzing and organizing files and folders."""

    def find_duplicates(
        self,
        folder_path: str,
        include_hidden: bool = False,
        min_size: int = 1024
    ) -> ToolResult:
        """
        Find duplicate files in a folder.

        Args:
            folder_path: Path to the folder to scan
            include_hidden: Whether to include hidden files
            min_size: Minimum file size to check (bytes)

        Returns:
            ToolResult with DuplicatesResult data
        """
        try:
            folder = validate_folder_path(folder_path)
            result = DuplicatesResult(folder_path=str(folder), total_files=0)

            # Phase 1: group by (size, quick_hash) to avoid full hashing every file
            size_map: Dict[int, List[Path]] = defaultdict(list)

            for file_path in get_all_files(folder, exclude_hidden=not include_hidden):
                try:
                    result.total_files += 1

                    if not include_hidden and is_hidden_file(file_path):
                        continue

                    file_size = file_path.stat().st_size
                    if file_size < min_size:
                        continue

                    size_map[file_size].append(file_path)

                except Exception as e:
                    logger.warning(f"Error accessing {file_path}: {e}")
                    continue

            # Phase 2: full hash only for files that share the same size
            hash_map: Dict[str, List[Path]] = defaultdict(list)
            for files_same_size in size_map.values():
                if len(files_same_size) < 2:
                    continue
                for file_path in files_same_size:
                    try:
                        file_hash = calculate_file_hash(file_path)
                        if file_hash:
                            hash_map[file_hash].append(file_path)
                    except Exception as e:
                        logger.warning(f"Error hashing {file_path}: {e}")
                        continue

            # Extract duplicate groups
            for file_hash, files in hash_map.items():
                if len(files) > 1:
                    dup_group = DuplicateGroup(
                        file_hash=file_hash,
                        file_size=files[0].stat().st_size,
                        file_count=len(files),
                        file_paths=[str(f) for f in files]
                    )
                    result.duplicate_groups.append(dup_group)
                    result.total_duplicate_files += len(files) - 1  # -1 for original
                    result.total_wasted_space += dup_group.file_size * (len(files) - 1)

            return ToolResult(ok=True, data={"duplicates": result.model_dump()})

        except FolderAccessError as e:
            return ToolResult(
                ok=False,
                error=ErrorInfo(code="folder_access_error", message=str(e))
            )
        except Exception as e:
            logger.exception(f"Error finding duplicates: {e}")
            return ToolResult(
                ok=False,
                error=ErrorInfo(code="duplicate_error", message=str(e))
            )

    def suggest_filename(
        self,
        file_path: str,
        max_content_size: int = 10000
    ) -> ToolResult:
        """
        Suggest meaningful filenames based on file content analysis.

        Args:
            file_path: Path to the file
            max_content_size: Maximum bytes of content to analyze

        Returns:
            ToolResult with FilenameSuggestion data
        """
        try:
            path = validate_file_path(file_path)

            suggestions = []
            analysis = ""
            keywords = []  # Initialize keywords for all file types

            if is_text_file(path):
                try:
                    content = read_text_file(path, max_size=max_content_size)
                    
                    # Extract first line as potential name
                    first_line = content.split('\n')[0].strip()
                    if first_line and len(first_line) < 50:
                        suggestions.append(sanitize_filename(first_line[:40]) + path.suffix)

                    # Extract keywords
                    keywords = extract_keywords_from_content(content, max_keywords=3)
                    if keywords:
                        keyword_name = "_".join(keywords) + path.suffix
                        suggestions.append(sanitize_filename(keyword_name))

                    analysis = f"Content-based suggestion from first line and keywords"

                except Exception as e:
                    logger.warning(f"Error analyzing content: {e}")
                    analysis = "Could not analyze content"
            else:
                # For binary files, suggest based on type
                ext = path.suffix.lower()
                type_name = {
                    '.pdf': 'document',
                    '.jpg': 'image', '.jpeg': 'image', '.png': 'image',
                    '.mp3': 'audio', '.wav': 'audio',
                    '.mp4': 'video', '.avi': 'video',
                    '.zip': 'archive', '.tar': 'archive'
                }.get(ext, 'file')
                suggestions.append(f"{type_name}{ext}")
                analysis = f"Type-based suggestion for {ext} files"

            # If no suggestions, use a default
            if not suggestions:
                suggestions.append(sanitize_filename(path.stem) + path.suffix)

            # Remove duplicates while preserving order
            suggestions = list(dict.fromkeys(suggestions))

            suggestion = FilenameSuggestion(
                current_name=path.name,
                suggested_names=suggestions[:5],  # Top 5 suggestions
                analysis=analysis,
                confidence=min(0.9, 0.5 + len(keywords) * 0.1) if keywords else 0.5
            )

            return ToolResult(ok=True, data={"suggestion": suggestion.model_dump()})

        except Exception as e:
            logger.exception(f"Error suggesting filename: {e}")
            return ToolResult(
                ok=False,
                error=ErrorInfo(code="suggest_error", message=str(e))
            )

    def organize_files(
        self,
        folder_path: str,
        organization_map: Optional[Dict[str, str]] = None,
        create_categories: bool = True
    ) -> ToolResult:
        """
        Organize files in a folder based on an organization map.

        Args:
            folder_path: Path to the root folder
            organization_map: Dict mapping file paths to category folder names
            create_categories: Whether to create category folders

        Returns:
            ToolResult with OrganizationResult data
        """
        try:
            folder = validate_folder_path(folder_path)
            result = OrganizationResult(folder_path=str(folder))

            if not organization_map:
                organization_map = {}

            for file_path_str, category in organization_map.items():
                try:
                    file_path = Path(file_path_str)

                    if not file_path.exists():
                        result.changes.append(
                            OrganizationChange(
                                file_path=file_path_str,
                                new_location=category,
                                status="skipped",
                                message="File does not exist"
                            )
                        )
                        continue

                    # Create category folder
                    category_folder = folder / sanitize_filename(category)
                    category_folder.mkdir(parents=True, exist_ok=True)
                    result.folders_created += 1

                    # Move file
                    new_path = category_folder / file_path.name
                    
                    # Handle duplicates
                    counter = 1
                    while new_path.exists():
                        stem = file_path.stem
                        suffix = file_path.suffix
                        new_path = category_folder / f"{stem}_{counter}{suffix}"
                        counter += 1

                    shutil.move(str(file_path), str(new_path))
                    result.files_moved += 1

                    result.changes.append(
                        OrganizationChange(
                            file_path=file_path_str,
                            new_location=category,
                            status="moved",
                            message=f"Moved to {category}/"
                        )
                    )

                except Exception as e:
                    logger.error(f"Error moving {file_path_str}: {e}")
                    result.changes.append(
                        OrganizationChange(
                            file_path=file_path_str,
                            new_location=category,
                            status="error",
                            message=str(e)
                        )
                    )

            result.redirect_file_path = str(folder / "REDIRECT.txt")
            self._create_redirect_file(folder, result)
            result.summary = f"Organized {result.files_moved} files into {result.folders_created} categories"

            return ToolResult(ok=True, data={"organization": result.model_dump()})

        except FolderAccessError as e:
            return ToolResult(
                ok=False,
                error=ErrorInfo(code="folder_access_error", message=str(e))
            )
        except Exception as e:
            logger.exception(f"Error organizing folder: {e}")
            return ToolResult(
                ok=False,
                error=ErrorInfo(code="organize_error", message=str(e))
            )

    def scan_folder(
        self,
        folder_path: str,
        include_hidden: bool = False
    ) -> ToolResult:
        """
        Scan and analyze a folder structure.

        Args:
            folder_path: Path to the folder to scan
            include_hidden: Whether to include hidden files

        Returns:
            ToolResult with FolderScanResult data
        """
        try:
            folder = validate_folder_path(folder_path)
            result = FolderScanResult(
                folder_path=str(folder),
                total_files=0,
                total_folders=0,
                total_size=0
            )

            # Collect file type statistics in a single pass (no byte I/O per file)
            type_stats: Dict[str, FileTypeStats] = {}
            seen_dirs: set = set()

            for file_path in get_all_files(folder, exclude_hidden=not include_hidden):
                try:
                    # Count unique parent directories as a proxy for subfolder count
                    parent = str(file_path.parent)
                    if parent != str(folder):
                        seen_dirs.add(parent)

                    result.total_files += 1
                    file_size = file_path.stat().st_size
                    result.total_size += file_size

                    # Check file type by extension only (no disk reads)
                    ext = file_path.suffix.lower() or "(no extension)"

                    if ext not in type_stats:
                        type_stats[ext] = FileTypeStats(
                            extension=ext,
                            count=0,
                            total_size=0
                        )

                    type_stats[ext].count += 1
                    type_stats[ext].total_size += file_size

                    # Use extension-only text detection (no byte reading)
                    if ext in TEXT_EXTENSIONS:
                        result.text_files += 1
                    else:
                        result.binary_files += 1

                    # Track all file paths
                    result.files.append(str(file_path))

                    # Check for generic names
                    if is_generic_filename(file_path.name):
                        result.files_with_generic_names += 1
                        result.generic_name_files.append(str(file_path))

                    # Check for hidden files
                    if is_hidden_file(file_path):
                        result.hidden_files += 1

                except Exception as e:
                    logger.warning(f"Error scanning {file_path}: {e}")
                    continue

            result.total_folders = len(seen_dirs)
            result.file_types = list(type_stats.values())
            result.file_types.sort(key=lambda x: x.count, reverse=True)

            return ToolResult(ok=True, data={"scan": result.model_dump()})

        except FolderAccessError as e:
            return ToolResult(
                ok=False,
                error=ErrorInfo(code="folder_access_error", message=str(e))
            )
        except Exception as e:
            logger.exception(f"Error scanning folder: {e}")
            return ToolResult(
                ok=False,
                error=ErrorInfo(code="scan_error", message=str(e))
            )

    @staticmethod
    def _create_redirect_file(folder: Path, result: OrganizationResult) -> None:
        """Create a REDIRECT.txt file documenting all changes."""
        try:
            redirect_path = folder / "REDIRECT.txt"
            
            lines = [
                "=" * 80,
                "FILE ORGANIZATION REDIRECT MAP",
                "=" * 80,
                f"Generated: {folder}",
                f"Total files moved: {result.files_moved}",
                f"Total folders created: {result.folders_created}",
                "",
                "CHANGES LOG:",
                "-" * 80,
            ]

            for change in result.changes:
                status_marker = "✓" if change.status == "moved" else "✗" if change.status == "error" else "→"
                lines.append(f"{status_marker} {Path(change.file_path).name}")
                lines.append(f"  From: {change.file_path}")
                lines.append(f"  To:   {change.new_location}/")
                if change.message:
                    lines.append(f"  Note: {change.message}")
                lines.append("")

            lines.extend([
                "=" * 80,
                "END OF REDIRECT MAP",
                "=" * 80,
            ])

            with open(redirect_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            logger.info(f"Created redirect file: {redirect_path}")

        except Exception as e:
            logger.error(f"Error creating redirect file: {e}")
