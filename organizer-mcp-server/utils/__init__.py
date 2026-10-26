"""Initialization of utils package."""

from utils.file_utils import (
    is_text_file,
    read_text_file,
    calculate_file_hash,
    calculate_quick_hash,
    is_generic_filename,
    extract_keywords_from_content,
    sanitize_filename,
    get_all_files,
    is_hidden_file,
)
from utils.errors import (
    OrganizerError,
    FileAccessError,
    FileReadError,
    FolderAccessError,
    ValidationError,
    OperationError,
)
from utils.validate import (
    validate_folder_path,
    validate_file_path,
    validate_filename,
)

__all__ = [
    "is_text_file",
    "read_text_file",
    "calculate_file_hash",
    "calculate_quick_hash",
    "is_generic_filename",
    "extract_keywords_from_content",
    "sanitize_filename",
    "get_all_files",
    "is_hidden_file",
    "OrganizerError",
    "FileAccessError",
    "FileReadError",
    "FolderAccessError",
    "ValidationError",
    "OperationError",
    "validate_folder_path",
    "validate_file_path",
    "validate_filename",
]
