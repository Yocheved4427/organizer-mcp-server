# Usage Instructions — Organizer MCP Server

> For setup and overview, see [README.md](README.md).

## Step-by-Step Workflow

Follow this workflow to organize any folder intelligently:

### Step 1: Scan the Folder
**Goal**: Get an overview of what you're working with

```bash
# Use scan_folder to understand the folder structure
Tool: scan_folder
Parameters:
  - folder_path: "G:/my_downloads"
  - include_hidden: false

# Returns:
# - Total files: 150
# - File types: PDF, JPEG, XLSX, etc.
# - Files with generic names: 23
# - Duplicate groups: 3
```

**What to do:**
- Check how many files need attention
- Look for generic filenames (Document1, Untitled, etc.)
- Note duplicate groups to clean up

### Step 2: Find Duplicates (Optional)
**Goal**: Identify wasted space from duplicate files

```bash
Tool: find_duplicates
Parameters:
  - folder_path: "G:/my_downloads"
  - include_hidden: false
  - min_size: 1024

# Returns duplicate groups with:
# - File hash (identical content)
# - File paths of duplicates
# - Total wasted space
```

**What to do:**
- Review duplicate groups
- Decide which copies to keep
- Use create_junk_folder to quarantine extras

### Step 3: Analyze Files with Generic Names
**Goal**: Understand what files need better names

```bash
Tool: read_file
Parameters:
  - file_path: "G:/my_downloads/Document1.pdf"
  - max_size: 50000

# Returns:
# - file_name: "Document1.pdf"
# - file_type: ".pdf"
# - content: (first 50000 bytes)
# - size: (file size)
```

**What to do:**
- Read files with generic names
- Understand their actual content
- Prepare to rename them meaningfully

### Step 4: Get Filename Suggestions
**Goal**: Generate better names based on content

```bash
Tool: suggest_filename
Parameters:
  - file_path: "G:/my_downloads/Document1.pdf"
  - max_content_size: 10000

# Returns:
# - current_name: "Document1.pdf"
# - suggested_names: [
#     "Q4_2024_Financial_Report.pdf",
#     "quarterly_report.pdf",
#     "report.pdf"
#   ]
# - analysis: "Content suggests Q4 financial report"
```

**What to do:**
- Review suggestions
- Choose the best option or use a custom name

### Step 5: Rename Files (Optional)
**Goal**: Give files meaningful names before organizing

```bash
Tool: rename_file
Parameters:
  - file_path: "G:/my_downloads/Document1.pdf"
  - new_name: "Q4_2024_Financial_Report.pdf"

# Returns:
# - old_path: "G:/my_downloads/Document1.pdf"
# - new_path: "G:/my_downloads/Q4_2024_Financial_Report.pdf"
```

**What to do:**
- Rename files one by one or in batches
- Use suggestions or custom names
- Verify each rename was successful

### Step 6: Build Organization Map
**Goal**: Create a plan for how to organize files

```
This is where YOU tell the AI what folders to create.

Example organization_map:
{
  "G:/my_downloads/Q4_Financial_Report.pdf": "Finance/2024_Reports",
  "G:/my_downloads/Revenue_Analysis.xlsx": "Finance/2024_Reports",
  "G:/my_downloads/Vacation_Photo1.jpg": "Personal/Photos/2024_Vacation",
  "G:/my_downloads/Invoice_123.pdf": "Finance/Invoices",
  "G:/my_downloads/Project_Brief.docx": "Projects/Project_Alpha"
}

Format: { "full_file_path": "destination_folder" }
```

**What to do:**
- Use insights from steps 1-5
- Map each file to a logical folder
- Create a clear folder hierarchy

### Step 7: Execute Organization
**Goal**: Move files to their new locations

```bash
Tool: organize_folder
Parameters:
  - folder_path: "G:/my_downloads"
  - organization_map: (from Step 6)
  - create_categories: true

# Returns:
# - files_moved: 45
# - folders_created: 8
# - redirect_file_path: "G:/my_downloads/REDIRECT.txt"
```

**What to do:**
- Execute the organization plan
- Check the REDIRECT.txt file for a complete log
- Verify all files moved to correct locations

### Step 8: Clean Up Duplicates (Optional)
**Goal**: Move duplicate files to junk folder for review

```bash
Tool: create_junk_folder
Parameters:
  - folder_path: "G:/my_downloads"
  - files_to_move: [
      "G:/my_downloads/duplicate_photo1.jpg",
      "G:/my_downloads/duplicate_photo2.jpg"
    ]
  - folder_name: "_junk"

# Returns:
# - junk_folder_path: "G:/my_downloads/_junk"
# - files_moved: 2
# - total_size_moved: 52428800
```

**What to do:**
- Move identified duplicates to _junk folder
- Review before permanent deletion
- Delete junk folder contents when confident

### Step 9: Verify Results
**Goal**: Confirm organization was successful

```bash
Tool: scan_folder (again)
Parameters:
  - folder_path: "G:/my_downloads"

# Compare with original scan:
# - Total files: same (not counting _junk)
# - Files with generic names: should be lower
# - Folder structure: should be organized
```

**What to do:**
- Run scan_folder again
- Verify file count (minus moved duplicates)
- Check new folder structure is as expected
- Look for any remaining generic filenames

## 📚 Available Tools

### `scan_folder`
Get complete analysis of a folder structure.

**Parameters:**
- `folder_path` (string): Folder to analyze
- `include_hidden` (boolean, default: false): Include hidden files

**Returns:**
```python
{
  "total_files": 250,
  "total_folders": 45,
  "total_size": 1073741824,
  "file_types": [
    {"extension": ".pdf", "count": 45, "total_size": 524288000},
    {"extension": ".jpg", "count": 120, "total_size": 314572800}
  ],
  "duplicate_groups": 3,
  "files_with_generic_names": 23,
  "text_files": 85,
  "binary_files": 165,
  "hidden_files": 2
}
```

### `find_duplicates`
Find duplicate files based on content hash.

**Parameters:**
- `folder_path` (string): Root folder to scan
- `include_hidden` (boolean, default: false): Include hidden files
- `min_size` (integer, default: 1024): Minimum file size in bytes

**Returns:**
```python
{
  "total_files": 150,
  "duplicate_groups": [
    {
      "file_hash": "a1b2c3d4...",
      "file_size": 1048576,
      "file_count": 3,
      "file_paths": ["/path/file1.jpg", "/path/file2.jpg", "/path/file3.jpg"]
    }
  ],
  "total_duplicate_files": 5,
  "total_wasted_space": 5242880
}
```

### `create_junk_folder`
Create a junk folder and move unwanted files into it.

**Parameters:**
- `folder_path` (string): Root folder where junk folder is created
- `files_to_move` (array): List of file paths to move
- `folder_name` (string, default: "_junk"): Junk folder name

**Returns:**
```python
{
  "junk_folder_path": "/path/_junk",
  "files_moved": 5,
  "total_size_moved": 52428800
}
```

### `read_file`
Read and analyze a file's content and metadata.

**Parameters:**
- `file_path` (string): Absolute path to the file
- `max_size` (integer, default: 50000): Maximum bytes to read

**Returns:**
```python
{
  "file_name": "document.pdf",
  "file_path": "/full/path/document.pdf",
  "size": 2048576,
  "is_text": false,
  "file_type": ".pdf",
  "content": "Binary file - cannot display content",
  "truncated": false
}
```

### `suggest_filename`
Generate intelligent filename suggestions based on content.

**Parameters:**
- `file_path` (string): Path to the file
- `max_content_size` (integer, default: 10000): Maximum bytes to analyze

**Returns:**
```python
{
  "current_name": "Untitled1.txt",
  "suggested_names": [
    "Project_Charter_2024.txt",
    "project_charter.txt",
    "charter.txt"
  ],
  "analysis": "Content-based suggestion from first line and keywords",
  "confidence": 0.75
}
```

### `rename_file`
Rename a file to a more meaningful name.

**Parameters:**
- `file_path` (string): Absolute path to the file
- `new_name` (string): New filename with extension

**Returns:**
```python
{
  "old_name": "Document1.pdf",
  "new_name": "Q4_Financial_Report.pdf",
  "old_path": "/path/Document1.pdf",
  "new_path": "/path/Q4_Financial_Report.pdf"
}
```

### `organize_folder`
Organize files into categories based on a provided map.

**Parameters:**
- `folder_path` (string): Root folder to organize
- `organization_map` (object): Mapping of file paths to category folders
- `create_categories` (boolean, default: true): Auto-create folders

**Example organization_map:**
```python
{
  "/path/file1.pdf": "Documents",
  "/path/file2.jpg": "Images",
  "/path/file3.mp3": "Music"
}
```

**Returns:**
```python
{
  "folder_path": "/path",
  "files_moved": 3,
  "folders_created": 3,
  "changes": [
    {
      "file_path": "/path/file1.pdf",
      "new_location": "Documents",
      "status": "moved",
      "message": "Moved to Documents/"
    }
  ],
  "redirect_file_path": "/path/REDIRECT.txt",
  "summary": "Organized 3 files into 3 categories"
}
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root (optional):

```env
# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Maximum file size to read (bytes)
MAX_FILE_READ_SIZE=50000

# Minimum file size for duplicate detection (bytes)
MIN_DUPLICATE_SIZE=1024

# File extensions to treat as text
TEXT_EXTENSIONS=.txt,.md,.py,.json,.yaml,.csv
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. -v
```

## 🔒 Security Considerations

### Safe Operations

- ✅ Files are never deleted, only moved to `_junk` folder
- ✅ Cannot navigate outside the root folder (path traversal protection)
- ✅ Invalid filenames are automatically sanitized
- ✅ Existing files are never overwritten (automatic renaming on conflicts)
- ✅ All operations are logged for audit trail

### Best Practices

1. **Always backup** before organizing large directories
2. **Review** the generated `REDIRECT.txt` before automation
3. **Start small** - test on a single folder first
4. **Check junk folder** before permanent deletion
5. **Monitor logs** for any issues

## Troubleshooting

### "Permission Denied" Errors

**Solution**: Run with appropriate permissions or use folders you own.

```bash
# On macOS/Linux
sudo chmod -R u+rw /path/to/folder

# On Windows
# Right-click folder → Properties → Security → Edit permissions
```

### "File Not Found" on Windows Paths

**Solution**: Use forward slashes or escape backslashes:
```python
# Good
"/Users/name/Downloads"
"C:/Users/name/Downloads"
"C:\\Users\\name\\Downloads"  # Escaped

# Bad
"C:\Users\name\Downloads"  # Unescaped
```

### MCP Not Showing in Claude Desktop

**Solution**: 
1. Verify the path in config is absolute
2. Test the server directly: `python main.py`
3. Check Claude logs in `~/Library/Logs/Claude/`
4. Restart Claude Desktop

### Encoding Errors When Reading Files

**Solution**: The server automatically tries UTF-8, Latin-1, and CP1252. Files with unusual encodings may need manual handling.

## Project Structure

```
organizer-mcp-server/
├── main.py                          # MCP server entry point
├── models/
│   ├── result.py                    # Response models
│   └── organizer_models.py          # Input validation models
├── services/
│   ├── organizer_service.py         # File analysis & organization
│   └── file_operations_service.py   # File operations
├── utils/
│   ├── file_utils.py                # File handling utilities
│   ├── errors.py                    # Error classes
│   └── validate.py                  # Input validation
└── tests/
```
