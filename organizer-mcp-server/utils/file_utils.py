"""Utility functions for file operations."""

import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, Set, List
import logging

logger = logging.getLogger(__name__)

# Common text file extensions
TEXT_EXTENSIONS = {
    '.txt', '.md', '.py', '.js', '.ts', '.json', '.yaml', '.yml', '.xml',
    '.html', '.css', '.sql', '.sh', '.bat', '.csv', '.log', '.conf',
    '.cfg', '.ini', '.toml', '.rst', '.tex', '.cpp', '.c', '.h', '.java',
    '.rb', '.go', '.rs', '.php', '.swift', '.kt', '.scala', '.r',
    '.pl', '.lua', '.vim', '.elisp', '.clj', '.ex', '.erl', '.docx',
    '.doc', '.odt'
}

# Generic filename patterns
GENERIC_PATTERNS = {
    'document', 'file', 'new', 'untitled', 'unnamed', 'copy', 'temp',
    'test', 'sample', 'example', 'noname', 'archive', 'download',
    'screenshot', 'image', 'photo', 'video', 'audio', 'data',
}


def is_text_file(file_path: Path) -> bool:
    """Check if a file is a text file based on extension and content."""
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    # Check extension first
    if file_path.suffix.lower() in TEXT_EXTENSIONS:
        return True

    # Try to detect by mimetype
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type and mime_type.startswith('text'):
        return True

    # Try reading first few bytes
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(512)
            return is_likely_text(chunk)
    except Exception:
        return False


def is_likely_text(data: bytes) -> bool:
    """Check if bytes likely represent text."""
    if not data:
        return True
    
    # Check for null bytes (usually binary)
    if b'\x00' in data[:512]:
        return False
    
    try:
        data.decode('utf-8')
        return True
    except UnicodeDecodeError:
        pass
    
    try:
        data.decode('latin-1')
        # If mostly printable, likely text
        printable = sum(32 <= b < 127 or b in (9, 10, 13) for b in data[:512])
        return printable / len(data[:512]) > 0.75
    except Exception:
        return False


def read_text_file(file_path: Path, max_size: int = 50000, encoding: str = 'utf-8') -> str:
    """Read text file content, handling encoding issues."""
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    file_size = file_path.stat().st_size
    read_size = min(file_size, max_size)

    # Try different encodings
    encodings = [encoding, 'utf-8', 'latin-1', 'cp1252']

    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                content = f.read(read_size)
                return content
        except (UnicodeDecodeError, LookupError):
            continue

    # Last resort - read as binary and decode with errors='ignore'
    with open(file_path, 'rb') as f:
        data = f.read(read_size)
        return data.decode('utf-8', errors='ignore')


def calculate_file_hash(file_path: Path, algorithm: str = 'sha256') -> str:
    """Calculate hash of a file for duplicate detection."""
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    hasher = hashlib.new(algorithm)
    chunk_size = 65536

    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {file_path}: {e}")
        return ""


def calculate_quick_hash(file_path: Path) -> str:
    """Quick hash using only first and last chunk (for speed)."""
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    hasher = hashlib.sha256()
    chunk_size = 65536

    try:
        with open(file_path, 'rb') as f:
            # First chunk
            chunk = f.read(chunk_size)
            hasher.update(chunk)

            # Last chunk
            f.seek(max(0, f.seek(0, 2) - chunk_size))  # Go to end
            chunk = f.read(chunk_size)
            if chunk:
                hasher.update(chunk)

        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating quick hash for {file_path}: {e}")
        return ""


def is_generic_filename(filename: str) -> bool:
    """Check if a filename is generic/non-descriptive."""
    name_lower = filename.lower()

    # Check for generic patterns
    for pattern in GENERIC_PATTERNS:
        if pattern in name_lower:
            return True

    # Check for numbered files like Document1, File2, etc.
    if any(name_lower.endswith(str(i)) for i in range(10)):
        return True

    # Check if filename is just extension or very short
    if '.' not in filename or len(filename.split('.')[0]) < 3:
        return True

    return False


def extract_keywords_from_content(content: str, max_keywords: int = 5) -> List[str]:
    """Extract important keywords from text content."""
    if not content:
        return []

    # Simple keyword extraction - get first meaningful words
    words = content.split()[:100]  # First 100 words
    keywords = []

    for word in words:
        # Clean word
        clean_word = ''.join(c for c in word if c.isalnum())
        if len(clean_word) > 3:  # At least 3 characters
            keywords.append(clean_word.lower())
            if len(keywords) >= max_keywords:
                break

    return list(set(keywords))  # Remove duplicates


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to be filesystem-safe."""
    # Remove/replace invalid characters
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')

    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext

    return filename


def get_all_files(
    folder_path: Path,
    exclude_hidden: bool = True,
    max_files: int = 10000,
    max_depth: Optional[int] = None,
) -> List[Path]:
    """Recursively get all files in a folder."""
    if not isinstance(folder_path, Path):
        folder_path = Path(folder_path)

    files: List[Path] = []

    def _walk(directory: Path, depth: int) -> None:
        if max_depth is not None and depth > max_depth:
            return
        if len(files) >= max_files:
            return
        try:
            for entry in os.scandir(directory):
                if len(files) >= max_files:
                    return
                if exclude_hidden and entry.name.startswith('.'):
                    continue
                if entry.is_file(follow_symlinks=False):
                    files.append(Path(entry.path))
                elif entry.is_dir(follow_symlinks=False):
                    _walk(Path(entry.path), depth + 1)
        except PermissionError:
            logger.warning(f"Permission denied accessing {directory}")

    _walk(folder_path, 0)
    return files


def is_hidden_file(file_path: Path) -> bool:
    """Check if a file is hidden."""
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    return file_path.name.startswith('.')
