# Accident Reconstruction Tool - Professional Edition

**Version 2.0.0** - Complete Windows Application with Auto-Update

Professional accident reconstruction software for creating detailed accident diagrams.

---

## ðŸ“¥ Quick Start

### Installation

```bash
# Install required packages
pip install pillow reportlab

# Run the application
python AccidentReconstructor.py
```

---

## ðŸŽ¨ Features

### ðŸš— Vehicles (4 Types)
- **Sedan** - Standard passenger car
- **Pickup Truck** - Light truck
- **18-Wheeler** - Semi-truck/tractor-trailer
- **Motorcycle** - Two-wheeled vehicle

### ðŸ›£ï¸ Roads (6 Types)
**Road Type Selector:**
- 2-Lane Road
- 4-Lane Road
- 4-Lane Highway
- Intersection

**Road Styles:**
- Straight Road
- Curved Road (adjustable curve)

### âž¡ï¸ Arrows (5 Types)
- Straight Arrow
- Left Turn Arrow
- Right Turn Arrow
- Left Curve Arrow (adjustable)
- Right Curve Arrow (adjustable)

### ðŸ“ Symbols (4 Types)
- ðŸŒ³ **Tree** - Fixed obstacles
- ðŸš¶ **Pedestrian** - People
- ðŸ“ **Text Label** - Custom annotations
- ðŸ§­ **Compass** - Orientation indicator

### ðŸŽ® Controls (8-10 Buttons per Object)
- **â†» â†º** Rotate clockwise/counter-clockwise
- **+ âˆ’** Scale up/down
- **â†”** Width adjustment
- **â†•** Height adjustment
- **âŒ’ âŒ£** Curve adjustment (curved objects only)

### âŒ¨ï¸ Keyboard Shortcuts
- **R** - Rotate clockwise 15Â°
- **Shift+R** - Rotate counter-clockwise 15Â°
- **Delete** - Delete selected object
- **Right-click** - Rotate object 15Â°
- **Drag** - Move object

### ðŸ“„ Export
- Professional PDF export
- Monochrome design (print-ready)
- Timestamped filenames

### ðŸ”„ Auto-Update
- Automatic update checking on startup
- Manual update check via Help menu
- One-click installation
- Automatic restart after update

---

## ðŸ”§ Setup Auto-Update (Optional)

### 1. Create GitHub Repository

1. Go to [github.com](https://github.com)
2. Click **"New repository"**
3. Name: `accident-reconstructor`
4. Make it **Public**
5. Click **"Create repository"**

### 2. Upload Files

Upload these files to your repository:
- `AccidentReconstructor.py`
- `version.json`
- `README.md` (optional)

### 3. Configure GitHub Username

The application is already configured for username: **omerta7z**

If you need to change it:
1. Open `AccidentReconstructor.py`
2. Find line ~35:
   ```python
   GITHUB_USER = "omerta7z"
   ```
3. Replace with your GitHub username
4. Save the file

### 4. Release Updates

When you want to release a new version:

1. **Update version.json:**
   ```json
   {
     "version": "2.1.0",
     "changelog": "Version 2.1.0\n\nâ€¢ New feature 1\nâ€¢ Bug fix 2"
   }
   ```

2. **Update AccidentReconstructor.py:**
   ```python
   CURRENT_VERSION = "2.1.0"
   ```

3. **Upload to GitHub**

4. **Users get notified automatically!**

---

## ðŸ“– How to Use

### Creating a Diagram

1. **Select a tool** from the left panel
2. **Click on canvas** to place the object
3. **Drag** to move the object
4. **Use control buttons** to adjust:
   - Rotation
   - Size
   - Width/Height
   - Curve (for curved objects)

### Road Types

1. **Select road type** from dropdown:
   - 2-Lane Road
   - 4-Lane Road
   - 4-Lane Highway
   - Intersection

2. **Click road button:**
   - Straight Road
   - Curved Road

3. **Place on canvas**

4. **Adjust curve** (curved roads only):
   - Use âŒ’ âŒ£ buttons

### Exporting

1. Click **"ðŸ“„ Export to PDF"**
2. Choose save location
3. PDF is created with timestamp

---

## ðŸŽ¯ UI Layout

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Accident Reconstruction    â”‚
â”‚   Professional Edition      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  ðŸš— VEHICLES                â”‚
â”‚  â€¢ Sedan                    â”‚
â”‚  â€¢ Pickup Truck             â”‚
â”‚  â€¢ 18-Wheeler               â”‚
â”‚  â€¢ Motorcycle               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  ðŸ›£ï¸ ROADS                   â”‚
â”‚  Road Type: [Selector â–¼]    â”‚
â”‚  â€¢ Straight Road            â”‚
â”‚  â€¢ Curved Road              â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  âž¡ï¸ ARROWS                  â”‚
â”‚  â€¢ Straight Arrow           â”‚
â”‚  â€¢ Left Turn Arrow          â”‚
â”‚  â€¢ Right Turn Arrow         â”‚
â”‚  â€¢ Left Curve Arrow         â”‚
â”‚  â€¢ Right Curve Arrow        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  ðŸ“ SYMBOLS                 â”‚
â”‚  â€¢ ðŸŒ³ Tree                  â”‚
â”‚  â€¢ ðŸš¶ Pedestrian            â”‚
â”‚  â€¢ ðŸ“ Text Label            â”‚
â”‚  â€¢ ðŸ§­ Compass               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  âš™ï¸ ACTIONS                 â”‚
â”‚  â€¢ ðŸ—‘ï¸ Delete Selected       â”‚
â”‚  â€¢ ðŸ”„ Clear All             â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  ðŸ“„ EXPORT                  â”‚
â”‚  â€¢ ðŸ“„ Export to PDF         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## ðŸ’¡ Tips

- **Right-click** on any object to rotate it quickly
- Use **keyboard shortcuts** for faster workflow
- **Curved roads** can be adjusted with âŒ’ âŒ£ buttons
- **Text labels** can be customized when placing
- **Compass** rotates to show different orientations
- **PDF export** includes timestamp for organization

---

## ðŸ› Troubleshooting

### Application won't start
```bash
# Make sure dependencies are installed
pip install pillow reportlab
```

### Update check fails
- Check internet connection
- Verify GitHub repository is public
- Confirm version.json is uploaded

### PDF export fails
```bash
# Reinstall reportlab
pip uninstall reportlab
pip install reportlab
```

---

## ðŸ“‹ System Requirements

- **Python:** 3.7 or higher
- **Operating System:** Windows, macOS, Linux
- **Dependencies:**
  - tkinter (included with Python)
  - Pillow (PIL)
  - ReportLab

---

## ðŸ”„ Version History

### Version 2.0.0 (Current)
- Complete UI redesign
- All 6 road types
- All 5 arrow types
- Improved symbols
- Auto-update functionality
- Professional color scheme
- Scrollable tool panel

---

## ðŸ“ž Support

For issues or questions:
1. Check this README
2. Review the troubleshooting section
3. Check for updates via Help menu

---

## ðŸ“„ License

Created by Galaxy AI
Professional Edition

---

## ðŸŽŠ Credits

**Author:** Galaxy AI  
**Version:** 2.0.0  
**Date:** February 2026

---

**Enjoy creating professional accident reconstruction diagrams!**
