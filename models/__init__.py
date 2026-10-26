"""Models package for Organizer MCP Server."""

from models.result import (
    ToolResult,
    ErrorInfo,
    FileReadInfo,
    FileRenameInfo,
    DuplicateGroup,
    DuplicatesResult,
    FilenameSuggestion,
    OrganizationChange,
    OrganizationResult,
    JunkFolderResult,
    FileTypeStats,
    FolderScanResult,
)
from models.organizer_models import (
    ReadFileIn,
    RenameFileIn,
    OrganizeIn,
    FindDuplicatesIn,
    SuggestNamesIn,
    CreateJunkFolderIn,
)

__all__ = [
    "ToolResult",
    "ErrorInfo",
    "FileReadInfo",
    "FileRenameInfo",
    "DuplicateGroup",
    "DuplicatesResult",
    "FilenameSuggestion",
    "OrganizationChange",
    "OrganizationResult",
    "JunkFolderResult",
    "FileTypeStats",
    "FolderScanResult",
    "ReadFileIn",
    "RenameFileIn",
    "OrganizeIn",
    "FindDuplicatesIn",
    "SuggestNamesIn",
    "CreateJunkFolderIn",
]
