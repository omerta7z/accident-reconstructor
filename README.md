# Accident Reconstruction Tool

Professional accident reconstruction software with auto-update capability.

## Features
- 4 Realistic Vehicles (Sedan, Pickup, 18-Wheeler, Motorcycle)
- Tree Obstacles
- Full Control System (8 buttons per object)
- PDF Export
- Auto-Update Functionality

## Installation
```bash
pip install pillow reportlab
python AccidentReconstructor.py
```

## Setup Auto-Update
1. Create GitHub repository named "accident-reconstructor"
2. Upload AccidentReconstructor.py and version.json
3. Edit AccidentReconstructor.py:
   - Replace `GITHUB_USER = "your-username"` with your GitHub username
4. When releasing updates:
   - Update version.json with new version number
   - Add changelog
   - Upload new AccidentReconstructor.py
   - Users will be notified automatically!

## Version
2.0.0
