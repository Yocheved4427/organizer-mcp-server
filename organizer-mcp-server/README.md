# Organizer MCP Server

An MCP server that gives Claude the ability to intelligently organize your files — reading content, detecting duplicates, suggesting meaningful names, and moving files into logical folders.

## 🎬 Demo

[Watch the demo](mcp-orgenizer.mp4)

## Tools

| Tool | Description |
|------|-------------|
| `scan_folder` | Get file statistics, types, and detect generic filenames |
| `find_duplicates` | Find identical files by content hash |
| `create_junk_folder` | Move unwanted files to a quarantine folder |
| `read_file` | Read file content for AI analysis |
| `suggest_filename` | Suggest meaningful names from file content |
| `rename_file` | Apply a new name to a file |
| `organize_folder` | Move files into AI-created category folders |

## Setup

### 1. Install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

### 2. Add to Claude Desktop

Edit your Claude Desktop config file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "organizer": {
      "command": "python",
      "args": ["C:/absolute/path/to/organizer-mcp-server/main.py"]
    }
  }
}
```

Restart Claude Desktop. A hammer icon (🔨) will confirm the tools are loaded.

## How It Works

1. **Scan** — Claude uses `scan_folder` to understand what's in your folder
2. **Read** — Claude reads files with generic names to understand their content
3. **Plan** — Claude decides on category names based on actual file content
4. **Execute** — Claude calls `organize_folder` with a file → category map
5. **Verify** — A `REDIRECT.txt` log is created showing every change made

No templates. No hardcoded rules. Folders are created based on what Claude understands about your files.

## Example

```
Before:
  Downloads/
    Document1.pdf      ← Claude reads: "Q4 Sales Report"
    File2.xlsx         ← Claude reads: "Revenue Analysis"
    Untitled.doc       ← Claude reads: "Product Requirements"
    IMG_001.jpg
    IMG_002.jpg

After:
  Downloads/
    Financial_Reports/
      Document1.pdf
      File2.xlsx
    Product_Documentation/
      Untitled.doc
    Photos/
      IMG_001.jpg
      IMG_002.jpg
    REDIRECT.txt
```

## Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python main.py
```

Opens a web UI at `http://localhost:5173` where you can call every tool manually.

## 📄 License

This project is licensed under the [MIT License](LICENSE).
