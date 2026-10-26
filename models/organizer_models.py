"""Input validation models for Organizer MCP Server."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
import os


class ReadFileIn(BaseModel):
    """Input for read_file tool."""
    file_path: str = Field(..., description="Absolute path to file")
    max_size: int = Field(default=50000, description="Max bytes to read")

    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """Validate file path exists."""
        path = os.path.expanduser(v)
        if not os.path.exists(path):
            raise ValueError(f"File does not exist: {v}")
        if not os.path.isfile(path):
            raise ValueError(f"Path is not a file: {v}")
        return v


class RenameFileIn(BaseModel):
    """Input for rename_file tool."""
    file_path: str = Field(..., description="Absolute path to file")
    new_name: str = Field(..., description="New filename")

    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """Validate file path exists."""
        path = os.path.expanduser(v)
        if not os.path.exists(path):
            raise ValueError(f"File does not exist: {v}")
        return v

    @field_validator('new_name')
    @classmethod
    def validate_new_name(cls, v: str) -> str:
        """Validate new filename."""
        if not v or len(v) == 0:
            raise ValueError("New name cannot be empty")
        if "/" in v or "\\" in v or ".." in v:
            raise ValueError("Filename cannot contain path separators")
        return v


class OrganizeIn(BaseModel):
    """Input for organize_folder tool."""
    folder_path: str = Field(..., description="Absolute path to folder")
    organization_map: Optional[Dict[str, str]] = Field(None)
    create_categories: bool = Field(default=True)

    @field_validator('folder_path')
    @classmethod
    def validate_folder_path(cls, v: str) -> str:
        """Validate folder path exists."""
        path = os.path.expanduser(v)
        if not os.path.exists(path):
            raise ValueError(f"Folder does not exist: {v}")
        if not os.path.isdir(path):
            raise ValueError(f"Path is not a directory: {v}")
        return v


class FindDuplicatesIn(BaseModel):
    """Input for find_duplicates tool."""
    folder_path: str = Field(..., description="Absolute path to folder")
    include_hidden: bool = Field(default=False)
    min_size: int = Field(default=1024, description="Minimum file size in bytes")

    @field_validator('folder_path')
    @classmethod
    def validate_folder_path(cls, v: str) -> str:
        """Validate folder path exists."""
        path = os.path.expanduser(v)
        if not os.path.exists(path):
            raise ValueError(f"Folder does not exist: {v}")
        if not os.path.isdir(path):
            raise ValueError(f"Path is not a directory: {v}")
        return v


class SuggestNamesIn(BaseModel):
    """Input for suggest_filename tool."""
    file_path: str = Field(..., description="Absolute path to file")
    max_content_size: int = Field(default=10000)

    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """Validate file path exists."""
        path = os.path.expanduser(v)
        if not os.path.exists(path):
            raise ValueError(f"File does not exist: {v}")
        if not os.path.isfile(path):
            raise ValueError(f"Path is not a file: {v}")
        return v


class ScanFolderIn(BaseModel):
    """Input for scan_folder tool."""
    folder_path: str = Field(..., description="Absolute path to folder")
    include_hidden: bool = Field(default=False)

    @field_validator('folder_path')
    @classmethod
    def validate_folder_path(cls, v: str) -> str:
        """Validate folder path exists."""
        path = os.path.expanduser(v)
        if not os.path.exists(path):
            raise ValueError(f"Folder does not exist: {v}")
        if not os.path.isdir(path):
            raise ValueError(f"Path is not a directory: {v}")
        return v


class CreateJunkFolderIn(BaseModel):
    """Input for create_junk_folder tool."""
    folder_path: str = Field(..., description="Absolute path to folder")
    files_to_move: List[str] = Field(..., description="List of file paths to move")
    folder_name: str = Field(default="_junk")

    @field_validator('folder_path')
    @classmethod
    def validate_folder_path(cls, v: str) -> str:
        """Validate folder path exists."""
        path = os.path.expanduser(v)
        if not os.path.exists(path):
            raise ValueError(f"Folder does not exist: {v}")
        if not os.path.isdir(path):
            raise ValueError(f"Path is not a directory: {v}")
        return v
