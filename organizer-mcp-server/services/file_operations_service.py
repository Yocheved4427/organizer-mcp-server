"""File operations service for MCP tools."""

import shutil
from pathlib import Path
from typing import Dict, Optional, List
from models.result import (
    ToolResult, FileReadInfo, FileRenameInfo, JunkFolderResult, ErrorInfo
)
from utils import (
    is_text_file, read_text_file, validate_folder_path, validate_file_path,
    validate_filename, sanitize_filename, get_all_files
)
from utils.errors import FileAccessError, FolderAccessError
import logging

logger = logging.getLogger(__name__)


class FileOperationsService:
    """Service for file reading, renaming, and junk folder operations."""

    def read_file(self, file_path: str, max_size: int = 50000) -> ToolResult:
        """
        Read a file and return its metadata and content.

        Args:
            file_path: Path to the file to read
            max_size: Maximum bytes to read

        Returns:
            ToolResult with FileReadInfo data
        """
        try:
            path = validate_file_path(file_path)
            
            file_size = path.stat().st_size
            is_text = is_text_file(path)
            
            content = None
            truncated = False

            if is_text:
                try:
                    content = read_text_file(path, max_size=max_size)
                    if file_size > max_size:
                        truncated = True
                except Exception as e:
                    content = f"[Error reading file: {str(e)}]"
                    logger.error(f"Error reading text file {path}: {e}")
            else:
                content = "[Binary file - cannot display content]"

            file_info = FileReadInfo(
                file_name=path.name,
                file_path=str(path),
                size=file_size,
                is_text=is_text,
                file_type=path.suffix or "no extension",
                content=content,
                truncated=truncated
            )

            return ToolResult(ok=True, data={"file_info": file_info.model_dump()})

        except FileAccessError as e:
            return ToolResult(
                ok=False,
                error=ErrorInfo(code="file_access_error", message=str(e))
            )
        except Exception as e:
            logger.exception(f"Error reading file: {e}")
            return ToolResult(
                ok=False,
                error=ErrorInfo(code="read_error", message=f"Error reading file: {str(e)}")
            )

    def rename_file(self, file_path: str, new_name: str) -> ToolResult:
        """
        Rename a file.

        Args:
            file_path: Path to the file to rename
            new_name: New filename (with extension)

        Returns:
            ToolResult with FileRenameInfo data
        """
        try:
            path = validate_file_path(file_path)
            validate_filename(new_name)
            
            new_name = sanitize_filename(new_name)
            new_path = path.parent / new_name

            if new_path.exists() and new_path != path:
                raise FileAccessError(f"File already exists: {new_name}")

            old_name = path.name
            path.rename(new_path)

            rename_info = FileRenameInfo(
                old_name=old_name,
                new_name=new_name,
                old_path=str(path),
                new_path=str(new_path)
            )

            logger.info(f"File renamed: {path} -> {new_path}")
            return ToolResult(ok=True, data={"rename_info": rename_info.model_dump()})

        except Exception as e:
            logger.error(f"Error renaming file: {e}")
            return ToolResult(
                ok=False,
                error=ErrorInfo(code="rename_error", message=str(e))
            )

    def create_junk_folder(
        self,
        folder_path: str,
        files_to_move: List[str],
        folder_name: str = "_junk"
    ) -> ToolResult:
        """
        Create a junk folder and move files into it.

        Args:
            folder_path: Root folder where to create junk folder
            files_to_move: List of file paths to move
            folder_name: Name of the junk folder

        Returns:
            ToolResult with JunkFolderResult data
        """
        try:
            root_path = validate_folder_path(folder_path)
            
            # Create junk folder
            junk_folder = root_path / folder_name
            junk_folder.mkdir(exist_ok=True)

            files_moved = 0
            total_size = 0
            errors = []

            for file_path in files_to_move:
                try:
                    path = validate_file_path(file_path)
                    file_size = path.stat().st_size

                    # Move file to junk folder
                    new_path = junk_folder / path.name
                    
                    # Handle name conflicts
                    counter = 1
                    original_stem = path.stem
                    original_suffix = path.suffix
                    while new_path.exists():
                        new_name = f"{original_stem}_{counter}{original_suffix}"
                        new_path = junk_folder / new_name
                        counter += 1

                    shutil.move(str(path), str(new_path))
                    files_moved += 1
                    total_size += file_size
                    logger.info(f"Moved to junk: {path} -> {new_path}")

                except Exception as e:
                    error_msg = f"Failed to move {file_path}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

            junk_result = JunkFolderResult(
                junk_folder_path=str(junk_folder),
                files_moved=files_moved,
                total_size_moved=total_size
            )

            return ToolResult(
                ok=True,
                data={
                    "junk_result": junk_result.model_dump(),
                    "errors": errors if errors else None
                }
            )

        except FolderAccessError as e:
            return ToolResult(
                ok=False,
                error=ErrorInfo(code="folder_access_error", message=str(e))
            )
        except Exception as e:
            logger.exception(f"Error creating junk folder: {e}")
            return ToolResult(
                ok=False,
                error=ErrorInfo(code="junk_error", message=str(e))
            )
