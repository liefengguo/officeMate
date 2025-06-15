# OfficeMate

OfficeMate is a cross-platform document snapshot and diff tool built with **PyQt5**. It allows you to capture versions of your documents and visually inspect differences between them. The application works on **macOS**, **Windows** and **Linux**.

## Features

- Manage projects containing `.txt` and `.docx` files
- Take snapshots and store version history automatically
- Compare any two snapshots with rich text highlighting
- Preview snapshot contents in a separate window
- Dashboard with recent documents
- Light, dark and auto themes with OS detection
- Multilingual user interface:
  - 中文
  - English
  - Español
  - Português
  - 日本語
  - Deutsch
  - Français
  - Русский
  - 한국어

## Getting Started

Run the application with:

```bash
python main.py
```

Snapshot data is stored per user in the following locations:

- **macOS**: `~/Library/Application Support/DocSnap`
- **Windows**: `%APPDATA%\DocSnap`
- **Linux**: `~/.local/share/DocSnap`

Qt makes the UI consistent across platforms. Ensure Python and PyQt5 are installed before launching.
