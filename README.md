# Accident Reconstruction Tool v2.4.0

Professional accident reconstruction software with FIXED auto-update and simple north arrow.

## What's New in v2.4.0

### Fixed Auto-Update System
- Completely rewritten update mechanism
- Better error handling and logging
- Proper file path detection (works with scripts and executables)
- User-Agent headers to avoid GitHub rate limiting
- Improved download progress tracking
- User must manually restart after update (more reliable)
- Creates backup before updating

### Simple North Arrow
- Replaced full compass with simple north arrow
- Just an arrow pointing up with "N" label
- Cleaner, simpler design
- Rotates with object controls

## Features

### Top-Down Realistic Vehicles
- **Sedan** - Blue car with hood, windshield, roof, rear window, trunk, 4 wheels
- **Pickup Truck** - Red truck with detailed cab, windshield, separate bed, 4 wheels
- **18-Wheeler** - Orange semi with cab, windshield, long trailer, 6 wheels
- **Motorcycle** - Gray bike with handlebars, narrow body, 2 wheels

### Complete PDF Export
- Captures actual diagram from canvas
- Renders all objects using PIL
- Professional layout with title and metadata
- Scales diagram to fit page
- Centers diagram on page

### Roads, Arrows, Symbols
- 6 Road Types (2-Lane, 4-Lane, Highway, Intersection - straight/curved)
- 5 Arrow Types (Straight, Turn Left/Right, Curve Left/Right)
- 4 Symbols (Tree, Pedestrian, Text Label, North Arrow)

### Professional UI
- Collapsible sections
- Working scrollbar with mouse wheel
- No emojis - clean text only
- Maximized canvas
- Descriptive control labels

### Auto-Update
- Automatic checking on startup
- Manual check via Help menu
- One-click download and installation
- Progress tracking
- Backup creation

## Installation

```bash
pip install pillow reportlab
python AccidentReconstructor.py
```

## GitHub Setup

Upload these files to your repository:
- `AccidentReconstructor.py`
- `version.json`
- `README.md`

Repository: `https://github.com/omerta7z/accident-reconstructor`

## Version

2.4.0 - February 26, 2026

## Author

Galaxy AI
