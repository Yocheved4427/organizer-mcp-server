"""
Organizer MCP Server - Intelligent file organization using Model Context Protocol.

This MCP server provides tools for analyzing and organizing computer files and folders.
It can scan directory trees, identify duplicates, suggest meaningful filenames,
and automatically organize files into logical folders based on content analysis.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional, Dict, List
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from services.organizer_service import OrganizerService
from services.file_operations_service import FileOperationsService
from models.organizer_models import (
    OrganizeIn, ReadFileIn, RenameFileIn, FindDuplicatesIn,
    SuggestNamesIn, CreateJunkFolderIn, ScanFolderIn
)
from models.result import ToolResult, ErrorInfo
from utils import errors
from utils.validate import validate_folder_path, validate_file_path

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("organizer-mcp-server")

# Initialize services
organizer_service = OrganizerService()
file_ops_service = FileOperationsService()


@mcp.tool(description="""
Scan a folder and get complete analysis: file statistics, types, duplicates, and generic filenames.
""")
async def scan_folder(folder_path: str, include_hidden: bool = False) -> dict:
    """Scan and analyze a folder structure."""
    try:
        _ = ScanFolderIn(folder_path=folder_path, include_hidden=include_hidden)
        res = await asyncio.to_thread(
            organizer_service.scan_folder,
            folder_path,
            include_hidden
        )
        return res.model_dump()
    except Exception as e:
        return ToolResult(
            ok=False,
            error=ErrorInfo(code="scan_error", message=str(e))
        ).model_dump()


@mcp.tool(description="""
Find duplicate files based on content hash. Returns groups of identical files with paths and sizes.
""")
async def find_duplicates(
    folder_path: str,
    include_hidden: bool = False,
    min_size: int = 1024
) -> dict:
    """Find duplicate files in a folder."""
    try:
        _ = FindDuplicatesIn(folder_path=folder_path, include_hidden=include_hidden)
        res = await asyncio.to_thread(
            organizer_service.find_duplicates,
            folder_path,
            include_hidden,
            min_size
        )
        return res.model_dump()
    except Exception as e:
        return ToolResult(
            ok=False,
            error=ErrorInfo(code="duplicate_error", message=str(e))
        ).model_dump()


@mcp.tool(description="""
Create a junk folder and move unwanted files into it for safe quarantine before deletion.
""")
async def create_junk_folder(
    folder_path: str,
    files_to_move: List[str],
    folder_name: str = "_junk"
) -> dict:
    """Create a junk folder and move files into it."""
    try:
        _ = CreateJunkFolderIn(folder_path=folder_path, files_to_move=files_to_move)
        res = await asyncio.to_thread(
            file_ops_service.create_junk_folder,
            folder_path,
            files_to_move,
            folder_name
        )
        return res.model_dump()
    except Exception as e:
        return ToolResult(
            ok=False,
            error=ErrorInfo(code="junk_error", message=str(e))
        ).model_dump()


@mcp.tool(description="""
Read and analyze file content and metadata. Returns file name, path, content, size, and type.
""")
async def read_file(file_path: str, max_size: int = 50000) -> dict:
    """Read a file and return its metadata and content."""
    try:
        _ = ReadFileIn(file_path=file_path, max_size=max_size)
        res = await asyncio.to_thread(file_ops_service.read_file, file_path, max_size)
        return res.model_dump()
    except Exception as e:
        return ToolResult(
            ok=False,
            error=ErrorInfo(code="read_error", message=str(e))
        ).model_dump()


@mcp.tool(description="""
Suggest meaningful filenames based on content analysis. Returns multiple name options.
""")
async def suggest_filename(file_path: str, max_content_size: int = 10000) -> dict:
    """Suggest meaningful filenames based on content analysis."""
    try:
        _ = SuggestNamesIn(file_path=file_path)
        res = await asyncio.to_thread(
            organizer_service.suggest_filename,
            file_path,
            max_content_size
        )
        return res.model_dump()
    except Exception as e:
        return ToolResult(
            ok=False,
            error=ErrorInfo(code="suggest_error", message=str(e))
        ).model_dump()


@mcp.tool(description="""
Rename a file to a more meaningful name. Returns old and new paths.
""")
async def rename_file(file_path: str, new_name: str) -> dict:
    """Rename a file to a new name."""
    try:
        _ = RenameFileIn(file_path=file_path, new_name=new_name)
        res = await asyncio.to_thread(file_ops_service.rename_file, file_path, new_name)
        return res.model_dump()
    except Exception as e:
        return ToolResult(
            ok=False,
            error=ErrorInfo(code="rename_error", message=str(e))
        ).model_dump()


@mcp.tool(description="""
Organize files into categories based on organization_map. Creates folders and moves files. Generates REDIRECT.txt log.
""")
async def organize_folder(
    folder_path: str,
    organization_map: Optional[Dict[str, str]] = None,
    create_categories: bool = True
) -> dict:
    """Organize files in a folder based on provided organization map."""
    try:
        _ = OrganizeIn(folder_path=folder_path)
        res = await asyncio.to_thread(
            organizer_service.organize_files,
            folder_path,
            organization_map,
            create_categories
        )
        return res.model_dump()
    except Exception as e:
        return ToolResult(
            ok=False,
            error=ErrorInfo(code="organize_error", message=str(e))
        ).model_dump()


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
