# Desktop - PyQt5 Annotation Tool

## Overview

High-performance desktop application for video annotation:
- Smooth 1920×1080 video scrubbing
- YOLO bounding box annotation
- Protocol handler (`oceanml://`) for browser integration
- Automatic sync to Supabase

## Structure

```
desktop/
├── PYQT5_UI.py                # Main application entry
├── ui/
│   ├── main_window.py         # Main window layout
│   ├── video_player.py        # Video player widget
│   ├── annotation_canvas.py  # Drawing canvas overlay
│   └── toolbar.py             # Annotation tools
├── services/
│   ├── video_downloader.py   # Download with progress
│   ├── annotation_sync.py    # Upload annotations
│   └── protocol_handler.py   # Parse oceanml:// URLs
├── models/
│   └── annotation.py         # YOLO format annotation
├── requirements.txt
├── build_installer.py        # PyInstaller + NSIS build script
└── .env.example
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Supabase anon key
- `API_URL` - Backend API URL

### 3. Run Application

#### Development Mode

```bash
python PYQT5_UI.py
```

#### With Protocol Handler (Test)

```bash
python PYQT5_UI.py "oceanml://annotate?video=1&token=test"
```

## Building Installer

### Windows

```bash
python build_installer.py --platform windows
```

Creates: `dist/OceanML-Setup.exe`

### macOS

```bash
python build_installer.py --platform mac
```

Creates: `dist/OceanML.dmg`

## Features

### Video Player
- Frame-by-frame scrubbing
- Play/pause
- Speed control
- Timeline with annotations

### Annotation Tools
- **Draw:** Click and drag to create bounding box
- **Label:** Select species from dropdown
- **Edit:** Click existing box to modify
- **Delete:** Select and press Delete key

### Keyboard Shortcuts
- `←/→` - Previous/next frame
- `Space` - Play/pause
- `Ctrl+S` - Save annotations
- `Ctrl+Z` - Undo last annotation
- `Delete` - Delete selected box

## Protocol Handler

The app registers as handler for `oceanml://` URLs.

**Example:**
```
oceanml://annotate?video=123&token=eyJ...
```

When user clicks "Annotate" in web dashboard, browser opens this URL, which launches the desktop app with the video ID and auth token.

## Development

### Adding New Features

1. UI changes: Edit files in `ui/`
2. Business logic: Add services in `services/`
3. Data models: Update `models/`

### Testing

```bash
pytest tests/
```

## Packaging

The installer includes:
- Python interpreter
- All dependencies
- Protocol handler registration
- Desktop shortcut
- Auto-update checker

## Deployment

Built installers can be hosted on:
- Backend static files endpoint
- CDN (Cloudflare, AWS S3)
- GitHub Releases

Users download once and app auto-updates.
