"""Data models for Organizer MCP Server responses."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ErrorInfo(BaseModel):
    """Error information in a tool result."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Additional error details")


class ToolResult(BaseModel):
    """Standard result format for all tools."""
    ok: bool = Field(..., description="Whether the operation succeeded")
    data: Optional[Dict[str, Any]] = Field(None, description="Result data if successful")
    error: Optional[ErrorInfo] = Field(None, description="Error info if failed")


class FileReadInfo(BaseModel):
    """Information returned when reading a file."""
    file_name: str = Field(..., description="Name of the file")
    file_path: str = Field(..., description="Absolute path to the file")
    size: int = Field(..., description="File size in bytes")
    is_text: bool = Field(..., description="Whether the file is text-based")
    file_type: str = Field(..., description="File extension/type")
    content: Optional[str] = Field(None, description="File content (if text file)")
    truncated: bool = Field(False, description="Whether content was truncated")


class FileRenameInfo(BaseModel):
    """Information returned when renaming a file."""
    old_name: str = Field(..., description="Original filename")
    new_name: str = Field(..., description="New filename")
    old_path: str = Field(..., description="Original absolute path")
    new_path: str = Field(..., description="New absolute path")


class DuplicateGroup(BaseModel):
    """A group of duplicate files."""
    file_hash: str = Field(..., description="Content hash of the files")
    file_size: int = Field(..., description="File size in bytes")
    file_count: int = Field(..., description="Number of duplicates")
    file_paths: List[str] = Field(..., description="Paths to all duplicate files")


class DuplicatesResult(BaseModel):
    """Result of finding duplicates."""
    folder_path: str = Field(..., description="Root folder analyzed")
    total_files: int = Field(..., description="Total files scanned")
    duplicate_groups: List[DuplicateGroup] = Field(default_factory=list)
    total_duplicate_files: int = Field(default=0)
    total_wasted_space: int = Field(default=0, description="Total space used by duplicates in bytes")


class FilenameSuggestion(BaseModel):
    """Suggested filename based on content analysis."""
    current_name: str = Field(..., description="Current filename")
    suggested_names: List[str] = Field(..., description="List of suggested filenames")
    analysis: str = Field(..., description="Analysis of file content")
    confidence: float = Field(default=0.5, description="Confidence score 0-1")


class OrganizationChange(BaseModel):
    """Record of a file being organized."""
    file_path: str = Field(..., description="Original file path")
    new_location: str = Field(..., description="New folder/location")
    status: str = Field(..., description="Status: moved, error, skipped")
    message: Optional[str] = Field(None, description="Additional info")


class OrganizationResult(BaseModel):
    """Result of organizing a folder."""
    folder_path: str = Field(..., description="Root folder organized")
    files_moved: int = Field(default=0)
    folders_created: int = Field(default=0)
    changes: List[OrganizationChange] = Field(default_factory=list)
    redirect_file_path: Optional[str] = Field(None, description="Path to Redirect.txt mapping file")
    summary: str = Field(default="")


class JunkFolderResult(BaseModel):
    """Result of creating junk folder and moving files."""
    junk_folder_path: str = Field(..., description="Path to created junk folder")
    files_moved: int = Field(..., description="Number of files moved")
    total_size_moved: int = Field(..., description="Total size of moved files in bytes")


class FileTypeStats(BaseModel):
    """Statistics about files of a particular type."""
    extension: str = Field(..., description="File extension")
    count: int = Field(..., description="Number of files")
    total_size: int = Field(..., description="Total size in bytes")


class FolderScanResult(BaseModel):
    """Result of scanning a folder for analysis."""
    folder_path: str = Field(..., description="Root folder analyzed")
    total_files: int = Field(..., description="Total files found")
    total_folders: int = Field(..., description="Total folders found")
    total_size: int = Field(..., description="Total size in bytes")
    file_types: List[FileTypeStats] = Field(default_factory=list)
    duplicate_groups: int = Field(default=0, description="Number of duplicate groups found")
    files_with_generic_names: int = Field(default=0)
    text_files: int = Field(default=0)
    binary_files: int = Field(default=0)
    hidden_files: int = Field(default=0)
    files: List[str] = Field(default_factory=list, description="Absolute paths of all files found")
    generic_name_files: List[str] = Field(default_factory=list, description="Absolute paths of files with generic names")
