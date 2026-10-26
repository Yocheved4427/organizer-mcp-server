"""Validation utilities."""

from pathlib import Path
from utils.errors import FolderAccessError, FileAccessError, ValidationError
import os

# System directories that are always blocked (defense-in-depth fallback)
_BLOCKED_SYSTEM_PATHS = [
    Path("C:/Windows"),
    Path("C:/Program Files"),
    Path("C:/Program Files (x86)"),
    Path("/etc"),
    Path("/usr"),
    Path("/bin"),
    Path("/sbin"),
    Path("/sys"),
    Path("/proc"),
    Path("/boot"),
]


def _get_allowed_paths() -> list:
    """Read ORGANIZER_ALLOWED_PATHS from env, return list of resolved Path objects."""
    raw = os.environ.get("ORGANIZER_ALLOWED_PATHS", "").strip()
    if not raw:
        return []
    return [Path(p.strip()).expanduser().resolve() for p in raw.split(",") if p.strip()]


def _is_subpath(path: Path, base: Path) -> bool:
    """Return True if path is equal to or under base."""
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def _validate_path_is_allowed(path: Path) -> None:
    """
    Enforce the path allow-list.

    If ORGANIZER_ALLOWED_PATHS is set, the path must be under one of those roots.
    If not set, block known OS system directories as a hard-coded fallback.

    Raises:
        ValidationError: If the path is outside the allowed scope.
    """
    resolved = path.resolve()
    allowed = _get_allowed_paths()

    if allowed:
        if not any(_is_subpath(resolved, base) for base in allowed):
            raise ValidationError(
                f"Access denied: '{path}' is outside the configured allowed paths. "
                "Set ORGANIZER_ALLOWED_PATHS in .env to the directories this server may access."
            )
    else:
        # No allow-list configured — block known system directories as a safety net
        for sys_path in _BLOCKED_SYSTEM_PATHS:
            if _is_subpath(resolved, sys_path.resolve()):
                raise ValidationError(
                    f"Access denied: '{path}' is a protected system directory. "
                    "Set ORGANIZER_ALLOWED_PATHS in .env to restrict access to specific folders."
                )


def validate_folder_path(folder_path: str) -> Path:
    """
    Validate that a folder path is accessible and is a directory.
    
    Args:
        folder_path: Path to validate
        
    Returns:
        Path object
        
    Raises:
        FolderAccessError: If path is invalid or not a directory
        ValidationError: If path is outside the allowed scope
    """
    path = Path(folder_path).expanduser().absolute()

    _validate_path_is_allowed(path)

    if not path.exists():
        raise FolderAccessError(f"Folder does not exist: {folder_path}")

    if not path.is_dir():
        raise FolderAccessError(f"Path is not a directory: {folder_path}")

    # Check if readable
    if not os.access(path, os.R_OK):
        raise FolderAccessError(f"Folder is not readable: {folder_path}")

    return path


def validate_file_path(file_path: str) -> Path:
    """
    Validate that a file path exists and is a file.
    
    Args:
        file_path: Path to validate
        
    Returns:
        Path object
        
    Raises:
        FileAccessError: If path is invalid or not a file
        ValidationError: If path is outside the allowed scope
    """
    path = Path(file_path).expanduser().absolute()

    _validate_path_is_allowed(path)

    if not path.exists():
        raise FileAccessError(f"File does not exist: {file_path}")

    if not path.is_file():
        raise FileAccessError(f"Path is not a file: {file_path}")

    return path


def validate_filename(filename: str) -> str:
    """
    Validate that a filename is safe.
    
    Args:
        filename: Filename to validate
        
    Returns:
        Validated filename
        
    Raises:
        ValidationError: If filename is invalid
    """
    if not filename or len(filename) == 0:
        raise ValidationError("Filename cannot be empty")

    # Check for path separators
    if "/" in filename or "\\" in filename or ".." in filename:
        raise ValidationError("Filename cannot contain path separators")

    # Check for invalid characters (Windows)
    invalid_chars = '<>:"|?*'
    if any(char in filename for char in invalid_chars):
        raise ValidationError(f"Filename contains invalid characters: {invalid_chars}")

    # Check length
    if len(filename) > 255:
        raise ValidationError("Filename is too long (max 255 characters)")

    return filename
