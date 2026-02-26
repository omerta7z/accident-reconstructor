#!/usr/bin/env python3
"""
Accident Reconstruction Diagram Tool v2.4.0
Professional Edition with Fixed Auto-Update & North Arrow
Author: Galaxy AI
Date: February 26, 2026
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import math
from PIL import Image, ImageDraw, ImageTk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime
import urllib.request
import json
import tempfile
import shutil
import sys
import subprocess
import io
import os

# ============================================================================
# AUTO-UPDATE FUNCTIONALITY - FIXED
# ============================================================================

class AutoUpdater:
    GITHUB_USER = "omerta7z"
    GITHUB_REPO = "accident-reconstructor"
    CURRENT_VERSION = "2.4.0"

    @classmethod
    def get_version_url(cls):
        return f"https://raw.githubusercontent.com/{cls.GITHUB_USER}/{cls.GITHUB_REPO}/main/version.json"

    @classmethod
    def get_download_url(cls):
        return f"https://raw.githubusercontent.com/{cls.GITHUB_USER}/{cls.GITHUB_REPO}/main/accident_reconstructor.py"

    @classmethod
    def check_for_updates(cls):
        """Check GitHub for newer version"""
        try:
            version_url = cls.get_version_url()
            print(f"Checking for updates at: {version_url}")

            # Add headers to avoid GitHub rate limiting
            req = urllib.request.Request(version_url)
            req.add_header('User-Agent', 'AccidentReconstructor/2.4.0')

            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode('utf-8')
                version_data = json.loads(data)

            latest_version = version_data.get("version", "0.0.0")
            changelog = version_data.get("changelog", "")

            print(f"Current version: {cls.CURRENT_VERSION}")
            print(f"Latest version: {latest_version}")

            # Compare versions
            current = tuple(map(int, cls.CURRENT_VERSION.split(".")))
            latest = tuple(map(int, latest_version.split(".")))

            if latest > current:
                print("Update available!")
                return True, latest_version, changelog
            else:
                print("Already up to date")
                return False, cls.CURRENT_VERSION, ""

        except Exception as e:
            print(f"Update check failed: {e}")
            return False, cls.CURRENT_VERSION, ""

    @classmethod
    def download_update(cls, progress_callback=None):
        """Download new version from GitHub"""
        try:
            download_url = cls.get_download_url()
            print(f"Downloading from: {download_url}")

            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.py')
            temp_path = temp_file.name
            temp_file.close()

            # Download with progress
            def report_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(100, (downloaded / total_size) * 100)
                    progress_callback(percent)

            # Add headers
            req = urllib.request.Request(download_url)
            req.add_header('User-Agent', 'AccidentReconstructor/2.4.0')

            # Download file
            urllib.request.urlretrieve(download_url, temp_path, reporthook=report_progress)

            print(f"Downloaded to: {temp_path}")
            return temp_path

        except Exception as e:
            print(f"Download failed: {e}")
            return None

    @classmethod
    def apply_update(cls, new_file_path):
        """Apply the downloaded update"""
        try:
            # Get current file path
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                current_file = sys.executable
            else:
                # Running as script
                current_file = os.path.abspath(sys.argv[0])

            print(f"Current file: {current_file}")
            print(f"New file: {new_file_path}")

            # Create backup
            backup_file = current_file + ".backup"
            if os.path.exists(current_file):
                shutil.copy2(current_file, backup_file)
                print(f"Backup created: {backup_file}")

            # Replace current file with new version
            shutil.copy2(new_file_path, current_file)
            print("File replaced successfully")

            # Clean up temp file
            try:
                os.remove(new_file_path)
            except:
                pass

            return True

        except Exception as e:
            print(f"Update failed: {e}")
            return False

class UpdateDialog:
    def __init__(self, parent, version, changelog):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Update Available")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        header = tk.Frame(self.dialog, bg="#27ae60", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="Update Available", font=("Arial", 16, "bold"),
                bg="#27ae60", fg="white").pack(pady=20)

        content = tk.Frame(self.dialog, bg="white")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        tk.Label(content, text=f"Version {version} is available!",
                font=("Arial", 12, "bold"), bg="white").pack(pady=10)
        tk.Label(content, text=f"Current: {AutoUpdater.CURRENT_VERSION}",
                font=("Arial", 10), bg="white", fg="#7f8c8d").pack()

        tk.Label(content, text="What's New:", font=("Arial", 10, "bold"),
                bg="white").pack(pady=(20, 5))

        changelog_frame = tk.Frame(content, bg="white")
        changelog_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        scrollbar = tk.Scrollbar(changelog_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        changelog_text = tk.Text(changelog_frame, wrap=tk.WORD, height=10,
                                yscrollcommand=scrollbar.set, font=("Arial", 9))
        changelog_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=changelog_text.yview)
        changelog_text.insert("1.0", changelog if changelog else "Bug fixes and improvements")
        changelog_text.config(state=tk.DISABLED)

        self.progress_frame = tk.Frame(content, bg="white")
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var,
                                           maximum=100, length=400)
        self.progress_label = tk.Label(self.progress_frame, text="", font=("Arial", 9), bg="white")

        button_frame = tk.Frame(self.dialog, bg="#ecf0f1")
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        tk.Button(button_frame, text="Update Now", command=self.update_now,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Later", command=self.update_later,
                 bg="#95a5a6", fg="white", font=("Arial", 10, "bold"),
                 width=15, height=2).pack(side=tk.RIGHT, padx=5)

        self.dialog.protocol("WM_DELETE_WINDOW", self.update_later)

    def update_progress(self, percent):
        self.progress_var.set(percent)
        self.progress_label.config(text=f"Downloading... {percent:.0f}%")
        self.dialog.update()

    def update_now(self):
        self.progress_frame.pack(fill=tk.X, pady=10)
        self.progress_bar.pack(fill=tk.X)
        self.progress_label.pack(pady=5)

        new_file = AutoUpdater.download_update(progress_callback=self.update_progress)
        if new_file:
            self.progress_label.config(text="Installing update...")
            self.dialog.update()
            if AutoUpdater.apply_update(new_file):
                messagebox.showinfo("Update Complete", "Update installed successfully!\n\nPlease restart the application.",
                                   parent=self.dialog)
                self.dialog.destroy()
                sys.exit(0)
            else:
                messagebox.showerror("Update Failed", "Failed to install update. Please try again later.", parent=self.dialog)
                self.dialog.destroy()
        else:
            messagebox.showerror("Download Failed", "Failed to download update. Please check your internet connection.", parent=self.dialog)
            self.dialog.destroy()

    def update_later(self):
        self.dialog.destroy()

def check_for_updates_on_startup(root):
    try:
        has_update, version, changelog = AutoUpdater.check_for_updates()
        if has_update:
            UpdateDialog(root, version, changelog)
    except Exception as e:
        print(f"Startup update check failed: {e}")

def manual_update_check(root):
    try:
        has_update, version, changelog = AutoUpdater.check_for_updates()
        if has_update:
            UpdateDialog(root, version, changelog)
        else:
            messagebox.showinfo("No Updates",
                               f"You have the latest version ({AutoUpdater.CURRENT_VERSION}).",
                               parent=root)
    except Exception as e:
        messagebox.showerror("Update Check Failed", f"Failed to check for updates: {str(e)}", parent=root)

# ============================================================================
# COLLAPSIBLE SECTION
# ============================================================================

class CollapsibleSection(tk.Frame):
    def __init__(self, parent, title, bg_color="#ecf0f1"):
        super().__init__(parent, bg=bg_color)
        self.bg_color = bg_color
        self.is_expanded = True

        self.header = tk.Frame(self, bg="#34495e", cursor="hand2", height=35)
        self.header.pack(fill=tk.X, pady=(0, 2))
        self.header.pack_propagate(False)

        self.arrow_label = tk.Label(self.header, text="â–¼", bg="#34495e", fg="white",
                                    font=("Arial", 10, "bold"), width=2)
        self.arrow_label.pack(side=tk.LEFT, padx=8)

        self.title_label = tk.Label(self.header, text=title, bg="#34495e", fg="white",
                                    font=("Arial", 10, "bold"), anchor="w")
        self.title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8)

        self.content = tk.Frame(self, bg=bg_color)
        self.content.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.header.bind("<Button-1>", self.toggle)
        self.arrow_label.bind("<Button-1>", self.toggle)
        self.title_label.bind("<Button-1>", self.toggle)

    def toggle(self, event=None):
        if self.is_expanded:
            self.content.pack_forget()
            self.arrow_label.config(text="â–¶")
            self.is_expanded = False
        else:
            self.content.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
            self.arrow_label.config(text="â–¼")
            self.is_expanded = True

    def get_content_frame(self):
        return self.content

# ============================================================================
# DIAGRAM OBJECTS
# ============================================================================

class DiagramObject:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.rotation, self.scale = 0, 1.0
        self.width_scale, self.height_scale = 1.0, 1.0
        self.curve_amount, self.selected = 0.0, False

    def draw(self, canvas):
        pass

    def draw_to_pil(self, draw, offset_x=0, offset_y=0):
        """Draw object to PIL ImageDraw for PDF export"""
        pass

    def contains(self, x, y):
        return False
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
    def rotate(self, angle=15):
        self.rotation = (self.rotation + angle) % 360
    def scale_up(self):
        self.scale = min(self.scale * 1.2, 3.0)
    def scale_down(self):
        self.scale = max(self.scale / 1.2, 0.3)
    def width_up(self):
        self.width_scale = min(self.width_scale * 1.2, 3.0)
    def width_down(self):
        self.width_scale = max(self.width_scale / 1.2, 0.3)
    def height_up(self):
        self.height_scale = min(self.height_scale * 1.2, 3.0)
    def height_down(self):
        self.height_scale = max(self.height_scale / 1.2, 0.3)
    def curve_up(self):
        self.curve_amount = min(self.curve_amount + 0.2, 2.0)
    def curve_down(self):
        self.curve_amount = max(self.curve_amount - 0.2, -2.0)
    def get_bounds(self):
        return (self.x - 50, self.y - 50, self.x + 50, self.y + 50)

class Vehicle(DiagramObject):
    """Realistic top-down vehicle view"""
    def __init__(self, x, y, vehicle_type="car"):
        super().__init__(x, y)
        self.vehicle_type = vehicle_type
        sizes = {"car": (55, 100), "truck": (75, 130), "semi": (80, 200), "motorcycle": (30, 65)}
        self.base_width, self.base_height = sizes.get(vehicle_type, (55, 100))

    def draw(self, canvas):
        """Draw vehicle on tkinter canvas"""
        w = self.base_width * self.scale * self.width_scale
        h = self.base_height * self.scale * self.height_scale
        angle = math.radians(self.rotation)
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        def rp(px, py):
            return (px * cos_a - py * sin_a + self.x, px * sin_a + py * cos_a + self.y)

        hw, hh, s = w/2, h/2, self.scale
        outline = "#000000"
        lw = int(3 * s) if self.selected else int(2 * s)

        # Shadow
        shadow = [rp(-hw+3*s, -hh+3*s), rp(hw+3*s, -hh+3*s),
                 rp(hw+3*s, hh+3*s), rp(-hw+3*s, hh+3*s)]
        canvas.create_polygon(shadow, fill="#d0d0d0", outline="", tags="object")

        if self.vehicle_type == "motorcycle":
            self._draw_motorcycle_topdown(canvas, rp, hw, hh, s, outline, lw)
        elif self.vehicle_type == "semi":
            self._draw_semi_topdown(canvas, rp, hw, hh, s, outline, lw)
        elif self.vehicle_type == "truck":
            self._draw_truck_topdown(canvas, rp, hw, hh, s, outline, lw)
        else:  # car
            self._draw_car_topdown(canvas, rp, hw, hh, s, outline, lw)

    def _draw_car_topdown(self, canvas, rp, hw, hh, s, outline, lw):
        """Draw sedan from top-down view"""
        # Main body
        body = [rp(-hw*0.9, -hh*0.85), rp(hw*0.9, -hh*0.85),
               rp(hw*0.9, hh*0.85), rp(-hw*0.9, hh*0.85)]
        canvas.create_polygon(body, fill="#3498db", outline=outline, width=lw, tags="object")

        # Hood (front)
        hood = [rp(-hw*0.85, -hh*0.85), rp(hw*0.85, -hh*0.85),
               rp(hw*0.85, -hh*0.5), rp(-hw*0.85, -hh*0.5)]
        canvas.create_polygon(hood, fill="#2980b9", outline=outline, width=int(lw*0.7), tags="object")

        # Windshield
        windshield = [rp(-hw*0.7, -hh*0.5), rp(hw*0.7, -hh*0.5),
                     rp(hw*0.7, -hh*0.2), rp(-hw*0.7, -hh*0.2)]
        canvas.create_polygon(windshield, fill="#85c1e9", outline=outline, width=int(lw*0.5), tags="object")

        # Roof
        roof = [rp(-hw*0.75, -hh*0.2), rp(hw*0.75, -hh*0.2),
               rp(hw*0.75, hh*0.3), rp(-hw*0.75, hh*0.3)]
        canvas.create_polygon(roof, fill="#5dade2", outline=outline, width=int(lw*0.5), tags="object")

        # Rear window
        rear_window = [rp(-hw*0.7, hh*0.3), rp(hw*0.7, hh*0.3),
                      rp(hw*0.7, hh*0.5), rp(-hw*0.7, hh*0.5)]
        canvas.create_polygon(rear_window, fill="#85c1e9", outline=outline, width=int(lw*0.5), tags="object")

        # Trunk
        trunk = [rp(-hw*0.85, hh*0.5), rp(hw*0.85, hh*0.5),
                rp(hw*0.85, hh*0.85), rp(-hw*0.85, hh*0.85)]
        canvas.create_polygon(trunk, fill="#2980b9", outline=outline, width=int(lw*0.7), tags="object")

        # Wheels (black circles)
        wr = 8 * s
        wheel_positions = [(-hw*0.75, -hh*0.6), (hw*0.75, -hh*0.6),
                          (-hw*0.75, hh*0.6), (hw*0.75, hh*0.6)]
        for wx, wy in wheel_positions:
            wheel_x, wheel_y = rp(wx, wy)
            canvas.create_oval(wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr,
                             fill="#000000", outline=outline, width=int(lw*0.6), tags="object")

    def _draw_truck_topdown(self, canvas, rp, hw, hh, s, outline, lw):
        """Draw pickup truck from top-down view"""
        # Cab
        cab = [rp(-hw*0.9, -hh*0.85), rp(hw*0.9, -hh*0.85),
              rp(hw*0.9, -hh*0.2), rp(-hw*0.9, -hh*0.2)]
        canvas.create_polygon(cab, fill="#e74c3c", outline=outline, width=lw, tags="object")

        # Windshield
        windshield = [rp(-hw*0.7, -hh*0.6), rp(hw*0.7, -hh*0.6),
                     rp(hw*0.7, -hh*0.35), rp(-hw*0.7, -hh*0.35)]
        canvas.create_polygon(windshield, fill="#f1948a", outline=outline, width=int(lw*0.5), tags="object")

        # Bed
        bed = [rp(-hw*0.9, -hh*0.15), rp(hw*0.9, -hh*0.15),
              rp(hw*0.9, hh*0.85), rp(-hw*0.9, hh*0.85)]
        canvas.create_polygon(bed, fill="#c0392b", outline=outline, width=lw, tags="object")

        # Bed rails
        canvas.create_line(rp(-hw*0.9, -hh*0.15)[0], rp(-hw*0.9, -hh*0.15)[1],
                          rp(-hw*0.9, hh*0.85)[0], rp(-hw*0.9, hh*0.85)[1],
                          fill=outline, width=int(lw*1.2), tags="object")
        canvas.create_line(rp(hw*0.9, -hh*0.15)[0], rp(hw*0.9, -hh*0.15)[1],
                          rp(hw*0.9, hh*0.85)[0], rp(hw*0.9, hh*0.85)[1],
                          fill=outline, width=int(lw*1.2), tags="object")

        # Wheels
        wr = 9 * s
        wheel_positions = [(-hw*0.75, -hh*0.7), (hw*0.75, -hh*0.7),
                          (-hw*0.75, hh*0.65), (hw*0.75, hh*0.65)]
        for wx, wy in wheel_positions:
            wheel_x, wheel_y = rp(wx, wy)
            canvas.create_oval(wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr,
                             fill="#000000", outline=outline, width=int(lw*0.6), tags="object")

    def _draw_semi_topdown(self, canvas, rp, hw, hh, s, outline, lw):
        """Draw 18-wheeler from top-down view"""
        # Cab
        cab_h = hh * 0.25
        cab = [rp(-hw*0.9, -hh*0.85), rp(hw*0.9, -hh*0.85),
              rp(hw*0.9, -hh*0.85+cab_h*2), rp(-hw*0.9, -hh*0.85+cab_h*2)]
        canvas.create_polygon(cab, fill="#f39c12", outline=outline, width=lw, tags="object")

        # Windshield
        windshield = [rp(-hw*0.7, -hh*0.75), rp(hw*0.7, -hh*0.75),
                     rp(hw*0.7, -hh*0.55), rp(-hw*0.7, -hh*0.55)]
        canvas.create_polygon(windshield, fill="#f8c471", outline=outline, width=int(lw*0.5), tags="object")

        # Trailer
        trailer = [rp(-hw*0.95, -hh*0.85+cab_h*2+5*s), rp(hw*0.95, -hh*0.85+cab_h*2+5*s),
                  rp(hw*0.95, hh*0.85), rp(-hw*0.95, hh*0.85)]
        canvas.create_polygon(trailer, fill="#d68910", outline=outline, width=lw, tags="object")

        # Trailer details (vertical lines)
        for i in range(3):
            y_pos = -hh*0.3 + i * hh*0.35
            canvas.create_line(rp(-hw*0.95, y_pos)[0], rp(-hw*0.95, y_pos)[1],
                              rp(hw*0.95, y_pos)[0], rp(hw*0.95, y_pos)[1],
                              fill=outline, width=int(lw*0.4), tags="object")

        # Wheels (6 wheels for semi)
        wr = 7 * s
        wheel_positions = [
            (-hw*0.75, -hh*0.85+cab_h*2), (hw*0.75, -hh*0.85+cab_h*2),  # Cab wheels
            (-hw*0.85, hh*0.5), (hw*0.85, hh*0.5),  # Rear wheels 1
            (-hw*0.85, hh*0.7), (hw*0.85, hh*0.7)   # Rear wheels 2
        ]
        for wx, wy in wheel_positions:
            wheel_x, wheel_y = rp(wx, wy)
            canvas.create_oval(wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr,
                             fill="#000000", outline=outline, width=int(lw*0.6), tags="object")

    def _draw_motorcycle_topdown(self, canvas, rp, hw, hh, s, outline, lw):
        """Draw motorcycle from top-down view"""
        # Main body (narrow)
        body = [rp(-hw*0.4, -hh*0.7), rp(hw*0.4, -hh*0.7),
               rp(hw*0.4, hh*0.7), rp(-hw*0.4, hh*0.7)]
        canvas.create_polygon(body, fill="#7f8c8d", outline=outline, width=lw, tags="object")

        # Handlebars (front)
        handlebar_y = -hh*0.75
        canvas.create_line(rp(-hw*0.8, handlebar_y)[0], rp(-hw*0.8, handlebar_y)[1],
                          rp(hw*0.8, handlebar_y)[0], rp(hw*0.8, handlebar_y)[1],
                          fill=outline, width=int(lw*1.5), tags="object")

        # Seat area
        seat = [rp(-hw*0.5, -hh*0.2), rp(hw*0.5, -hh*0.2),
               rp(hw*0.5, hh*0.3), rp(-hw*0.5, hh*0.3)]
        canvas.create_polygon(seat, fill="#95a5a6", outline=outline, width=int(lw*0.7), tags="object")

        # Wheels (2 wheels)
        wr = 10 * s
        wheel_positions = [(0, -hh*0.7), (0, hh*0.7)]
        for wx, wy in wheel_positions:
            wheel_x, wheel_y = rp(wx, wy)
            canvas.create_oval(wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr,
                             fill="#000000", outline=outline, width=int(lw*0.8), tags="object")

    def draw_to_pil(self, draw, offset_x=0, offset_y=0):
        """Draw vehicle to PIL ImageDraw for PDF export"""
        w = self.base_width * self.scale * self.width_scale
        h = self.base_height * self.scale * self.height_scale
        angle = math.radians(self.rotation)
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        def rp(px, py):
            rx = px * cos_a - py * sin_a + self.x + offset_x
            ry = px * sin_a + py * cos_a + self.y + offset_y
            return (int(rx), int(ry))

        hw, hh, s = w/2, h/2, self.scale
        lw = int(3 * s) if self.selected else int(2 * s)

        # Shadow
        shadow = [rp(-hw+3*s, -hh+3*s), rp(hw+3*s, -hh+3*s),
                 rp(hw+3*s, hh+3*s), rp(-hw+3*s, hh+3*s)]
        draw.polygon(shadow, fill="#d0d0d0", outline=None)

        if self.vehicle_type == "motorcycle":
            self._draw_motorcycle_pil(draw, rp, hw, hh, s, lw)
        elif self.vehicle_type == "semi":
            self._draw_semi_pil(draw, rp, hw, hh, s, lw)
        elif self.vehicle_type == "truck":
            self._draw_truck_pil(draw, rp, hw, hh, s, lw)
        else:
            self._draw_car_pil(draw, rp, hw, hh, s, lw)

    def _draw_car_pil(self, draw, rp, hw, hh, s, lw):
        """Draw sedan to PIL"""
        body = [rp(-hw*0.9, -hh*0.85), rp(hw*0.9, -hh*0.85),
               rp(hw*0.9, hh*0.85), rp(-hw*0.9, hh*0.85)]
        draw.polygon(body, fill="#3498db", outline="#000000")

        hood = [rp(-hw*0.85, -hh*0.85), rp(hw*0.85, -hh*0.85),
               rp(hw*0.85, -hh*0.5), rp(-hw*0.85, -hh*0.5)]
        draw.polygon(hood, fill="#2980b9", outline="#000000")

        windshield = [rp(-hw*0.7, -hh*0.5), rp(hw*0.7, -hh*0.5),
                     rp(hw*0.7, -hh*0.2), rp(-hw*0.7, -hh*0.2)]
        draw.polygon(windshield, fill="#85c1e9", outline="#000000")

        roof = [rp(-hw*0.75, -hh*0.2), rp(hw*0.75, -hh*0.2),
               rp(hw*0.75, hh*0.3), rp(-hw*0.75, hh*0.3)]
        draw.polygon(roof, fill="#5dade2", outline="#000000")

        rear_window = [rp(-hw*0.7, hh*0.3), rp(hw*0.7, hh*0.3),
                      rp(hw*0.7, hh*0.5), rp(-hw*0.7, hh*0.5)]
        draw.polygon(rear_window, fill="#85c1e9", outline="#000000")

        trunk = [rp(-hw*0.85, hh*0.5), rp(hw*0.85, hh*0.5),
                rp(hw*0.85, hh*0.85), rp(-hw*0.85, hh*0.85)]
        draw.polygon(trunk, fill="#2980b9", outline="#000000")

        wr = int(8 * s)
        wheel_positions = [(-hw*0.75, -hh*0.6), (hw*0.75, -hh*0.6),
                          (-hw*0.75, hh*0.6), (hw*0.75, hh*0.6)]
        for wx, wy in wheel_positions:
            wheel_x, wheel_y = rp(wx, wy)
            draw.ellipse([wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr],
                        fill="#000000", outline="#000000")

    def _draw_truck_pil(self, draw, rp, hw, hh, s, lw):
        """Draw pickup to PIL"""
        cab = [rp(-hw*0.9, -hh*0.85), rp(hw*0.9, -hh*0.85),
              rp(hw*0.9, -hh*0.2), rp(-hw*0.9, -hh*0.2)]
        draw.polygon(cab, fill="#e74c3c", outline="#000000")

        windshield = [rp(-hw*0.7, -hh*0.6), rp(hw*0.7, -hh*0.6),
                     rp(hw*0.7, -hh*0.35), rp(-hw*0.7, -hh*0.35)]
        draw.polygon(windshield, fill="#f1948a", outline="#000000")

        bed = [rp(-hw*0.9, -hh*0.15), rp(hw*0.9, -hh*0.15),
              rp(hw*0.9, hh*0.85), rp(-hw*0.9, hh*0.85)]
        draw.polygon(bed, fill="#c0392b", outline="#000000")

        wr = int(9 * s)
        wheel_positions = [(-hw*0.75, -hh*0.7), (hw*0.75, -hh*0.7),
                          (-hw*0.75, hh*0.65), (hw*0.75, hh*0.65)]
        for wx, wy in wheel_positions:
            wheel_x, wheel_y = rp(wx, wy)
            draw.ellipse([wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr],
                        fill="#000000", outline="#000000")

    def _draw_semi_pil(self, draw, rp, hw, hh, s, lw):
        """Draw semi to PIL"""
        cab_h = hh * 0.25
        cab = [rp(-hw*0.9, -hh*0.85), rp(hw*0.9, -hh*0.85),
              rp(hw*0.9, -hh*0.85+cab_h*2), rp(-hw*0.9, -hh*0.85+cab_h*2)]
        draw.polygon(cab, fill="#f39c12", outline="#000000")

        windshield = [rp(-hw*0.7, -hh*0.75), rp(hw*0.7, -hh*0.75),
                     rp(hw*0.7, -hh*0.55), rp(-hw*0.7, -hh*0.55)]
        draw.polygon(windshield, fill="#f8c471", outline="#000000")

        trailer = [rp(-hw*0.95, -hh*0.85+cab_h*2+5*s), rp(hw*0.95, -hh*0.85+cab_h*2+5*s),
                  rp(hw*0.95, hh*0.85), rp(-hw*0.95, hh*0.85)]
        draw.polygon(trailer, fill="#d68910", outline="#000000")

        wr = int(7 * s)
        wheel_positions = [
            (-hw*0.75, -hh*0.85+cab_h*2), (hw*0.75, -hh*0.85+cab_h*2),
            (-hw*0.85, hh*0.5), (hw*0.85, hh*0.5),
            (-hw*0.85, hh*0.7), (hw*0.85, hh*0.7)
        ]
        for wx, wy in wheel_positions:
            wheel_x, wheel_y = rp(wx, wy)
            draw.ellipse([wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr],
                        fill="#000000", outline="#000000")

    def _draw_motorcycle_pil(self, draw, rp, hw, hh, s, lw):
        """Draw motorcycle to PIL"""
        body = [rp(-hw*0.4, -hh*0.7), rp(hw*0.4, -hh*0.7),
               rp(hw*0.4, hh*0.7), rp(-hw*0.4, hh*0.7)]
        draw.polygon(body, fill="#7f8c8d", outline="#000000")

        handlebar_y = -hh*0.75
        draw.line([rp(-hw*0.8, handlebar_y), rp(hw*0.8, handlebar_y)],
                 fill="#000000", width=int(lw*1.5))

        seat = [rp(-hw*0.5, -hh*0.2), rp(hw*0.5, -hh*0.2),
               rp(hw*0.5, hh*0.3), rp(-hw*0.5, hh*0.3)]
        draw.polygon(seat, fill="#95a5a6", outline="#000000")

        wr = int(10 * s)
        wheel_positions = [(0, -hh*0.7), (0, hh*0.7)]
        for wx, wy in wheel_positions:
            wheel_x, wheel_y = rp(wx, wy)
            draw.ellipse([wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr],
                        fill="#000000", outline="#000000")

    def contains(self, x, y):
        dx, dy = x - self.x, y - self.y
        angle = math.radians(-self.rotation)
        lx = dx * math.cos(angle) - dy * math.sin(angle)
        ly = dx * math.sin(angle) + dy * math.cos(angle)
        hw = (self.base_width * self.scale * self.width_scale) / 2
        hh = (self.base_height * self.scale * self.height_scale) / 2
        return abs(lx) < hw and abs(ly) < hh

    def get_bounds(self):
        hw = (self.base_width * self.scale * self.width_scale) / 2
        hh = (self.base_height * self.scale * self.height_scale) / 2
        return (self.x-hw-30, self.y-hh-30, self.x+hw+30, self.y+hh+30

class Road(DiagramObject):
    def __init__(self, x, y, road_type="2-Lane Road"):
        super().__init__(x, y)
        self.road_type = road_type

    def draw(self, canvas):
        s = self.scale
        w_s = self.width_scale
        h_s = self.height_scale

        angle_rad = math.radians(self.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        def rp(px, py):
            rx = px * cos_a - py * sin_a + self.x
            ry = px * sin_a + py * cos_a + self.y
            return (rx, ry)

        outline = "#000000"
        width = int(3 * s) if self.selected else int(2 * s)

        length = 200 * s * w_s
        road_width = 25 * s * h_s
        if "4-Lane" in self.road_type:
            road_width = 40 * s * h_s

        corners = [(-length, -road_width/2), (length, -road_width/2),
                  (length, road_width/2), (-length, road_width/2)]
        rotated = [rp(cx, cy) for cx, cy in corners]
        canvas.create_polygon(rotated, fill="#808080", outline=outline, width=width, tags="object")

        p1 = rp(-length, 0)
        p2 = rp(length, 0)
        canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="#ffffff",
                          width=int(2*s), dash=(10, 5), tags="object")

    def draw_to_pil(self, draw, offset_x=0, offset_y=0):
        s = self.scale
        w_s = self.width_scale
        h_s = self.height_scale

        angle_rad = math.radians(self.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        def rp(px, py):
            rx = px * cos_a - py * sin_a + self.x + offset_x
            ry = px * sin_a + py * cos_a + self.y + offset_y
            return (int(rx), int(ry))

        length = 200 * s * w_s
        road_width = 25 * s * h_s
        if "4-Lane" in self.road_type:
            road_width = 40 * s * h_s

        corners = [(-length, -road_width/2), (length, -road_width/2),
                  (length, road_width/2), (-length, road_width/2)]
        rotated = [rp(cx, cy) for cx, cy in corners]
        draw.polygon(rotated, fill="#808080", outline="#000000")

        p1 = rp(-length, 0)
        p2 = rp(length, 0)
        draw.line([p1, p2], fill="#ffffff", width=int(2*s))

    def contains(self, x, y):
        dx = x - self.x
        dy = y - self.y
        angle_rad = math.radians(-self.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        local_x = dx * cos_a - dy * sin_a
        local_y = dx * sin_a + dy * cos_a

        length = 200 * self.scale * self.width_scale
        width = 40 * self.scale * self.height_scale if "4-Lane" in self.road_type else 25 * self.scale * self.height_scale
        return abs(local_x) < length and abs(local_y) < width

    def get_bounds(self):
        length = 200 * self.scale * self.width_scale
        width = 40 * self.scale * self.height_scale if "4-Lane" in self.road_type else 25 * self.scale * self.height_scale
        margin = 30
        return (self.x - length - margin, self.y - width - margin,
                self.x + length + margin, self.y + width + margin)

class CurvedRoad(DiagramObject):
    def __init__(self, x, y, road_type="2-Lane Road"):
        super().__init__(x, y)
        self.road_type = road_type
        self.curve_amount = 0.5

    def draw(self, canvas):
        s = self.scale
        w_s = self.width_scale
        h_s = self.height_scale
        curve = self.curve_amount

        angle_rad = math.radians(self.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        def rp(px, py):
            rx = px * cos_a - py * sin_a + self.x
            ry = px * sin_a + py * cos_a + self.y
            return (rx, ry)

        outline = "#000000"
        width = int(3 * s) if self.selected else int(2 * s)

        length = 200 * s * w_s
        road_width = 25 * s * h_s
        if "4-Lane" in self.road_type:
            road_width = 40 * s * h_s

        segments = 20
        points_top = []
        points_bottom = []

        for i in range(segments + 1):
            t = i / segments
            x_pos = -length + 2 * length * t
            y_curve = curve * 100 * s * (t * (1 - t) * 4)

            pt_top = rp(x_pos, -road_width/2 + y_curve)
            points_top.append(pt_top)

            pt_bottom = rp(x_pos, road_width/2 + y_curve)
            points_bottom.append(pt_bottom)

        all_points = points_top + list(reversed(points_bottom))
        canvas.create_polygon(all_points, fill="#808080", outline=outline, width=width, tags="object")

        center_points = []
        for i in range(segments + 1):
            t = i / segments
            x_pos = -length + 2 * length * t
            y_curve = curve * 100 * s * (t * (1 - t) * 4)
            pt = rp(x_pos, y_curve)
            center_points.append(pt)

        for i in range(len(center_points) - 1):
            if i % 2 == 0:
                canvas.create_line(center_points[i][0], center_points[i][1],
                                 center_points[i+1][0], center_points[i+1][1],
                                 fill="#ffffff", width=int(2*s), tags="object")

    def draw_to_pil(self, draw, offset_x=0, offset_y=0):
        s = self.scale
        w_s = self.width_scale
        h_s = self.height_scale
        curve = self.curve_amount

        angle_rad = math.radians(self.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        def rp(px, py):
            rx = px * cos_a - py * sin_a + self.x + offset_x
            ry = px * sin_a + py * cos_a + self.y + offset_y
            return (int(rx), int(ry))

        length = 200 * s * w_s
        road_width = 25 * s * h_s
        if "4-Lane" in self.road_type:
            road_width = 40 * s * h_s

        segments = 20
        points_top = []
        points_bottom = []

        for i in range(segments + 1):
            t = i / segments
            x_pos = -length + 2 * length * t
            y_curve = curve * 100 * s * (t * (1 - t) * 4)

            pt_top = rp(x_pos, -road_width/2 + y_curve)
            points_top.append(pt_top)

            pt_bottom = rp(x_pos, road_width/2 + y_curve)
            points_bottom.append(pt_bottom)

        all_points = points_top + list(reversed(points_bottom))
        draw.polygon(all_points, fill="#808080", outline="#000000")

    def contains(self, x, y):
        length = 200 * self.scale * self.width_scale
        width = 40 * self.scale * self.height_scale
        dx = abs(x - self.x)
        dy = abs(y - self.y)
        return dx < length and dy < width + abs(self.curve_amount * 50)

    def get_bounds(self):
        length = 200 * self.scale * self.width_scale
        width = 40 * self.scale * self.height_scale
        curve_offset = abs(self.curve_amount * 50)
        margin = 30
        return (self.x - length - margin, self.y - width - curve_offset - margin,
                self.x + length + margin, self.y + width + curve_offset + margin)

class Arrow(DiagramObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.base_length = 80

    def draw(self, canvas):
        length = self.base_length * self.scale * self.width_scale
        angle_rad = math.radians(self.rotation)

        x2 = self.x + length * math.cos(angle_rad)
        y2 = self.y + length * math.sin(angle_rad)

        outline = "#000000"
        width = int(5 * self.scale * self.height_scale)
        arrow_size = int(16 * self.scale)

        canvas.create_line(self.x, self.y, x2, y2, fill=outline, width=width,
                          arrow=tk.LAST, arrowshape=(arrow_size, arrow_size+4, arrow_size//2),
                          tags="object")

    def draw_to_pil(self, draw, offset_x=0, offset_y=0):
        length = self.base_length * self.scale * self.width_scale
        angle_rad = math.radians(self.rotation)

        x1 = self.x + offset_x
        y1 = self.y + offset_y
        x2 = x1 + length * math.cos(angle_rad)
        y2 = y1 + length * math.sin(angle_rad)

        width = int(5 * self.scale * self.height_scale)
        draw.line([(x1, y1), (x2, y2)], fill="#000000", width=width)

        # Draw arrowhead
        arrow_size = 16 * self.scale
        angle1 = angle_rad + math.pi * 0.85
        angle2 = angle_rad - math.pi * 0.85

        p1 = (int(x2), int(y2))
        p2 = (int(x2 + arrow_size * math.cos(angle1)), int(y2 + arrow_size * math.sin(angle1)))
        p3 = (int(x2 + arrow_size * math.cos(angle2)), int(y2 + arrow_size * math.sin(angle2)))

        draw.polygon([p1, p2, p3], fill="#000000", outline="#000000")

    def contains(self, x, y):
        length = self.base_length * self.scale * self.width_scale
        dx = x - self.x
        dy = y - self.y
        return abs(dx) < length and abs(dy) < 20 * self.scale

    def get_bounds(self):
        length = self.base_length * self.scale * self.width_scale
        margin = 30
        return (self.x - margin, self.y - 20 * self.scale - margin,
                self.x + length + margin, self.y + 20 * self.scale + margin)

class TurnArrow(DiagramObject):
    def __init__(self, x, y, direction="left"):
        super().__init__(x, y)
        self.direction = direction
        self.base_size = 60

    def draw(self, canvas):
        size = self.base_size * self.scale
        angle_rad = math.radians(self.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        def rp(px, py):
            rx = px * cos_a - py * sin_a + self.x
            ry = px * sin_a + py * cos_a + self.y
            return (rx, ry)

        outline = "#000000"
        width = int(5 * self.scale)

        p1 = rp(0, size/2)
        p2 = rp(0, -size/4)
        canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=outline, width=width, tags="object")

        if self.direction == "left":
            p3 = rp(-size/2, -size/4)
        else:
            p3 = rp(size/2, -size/4)

        canvas.create_line(p2[0], p2[1], p3[0], p3[1], fill=outline, width=width, tags="object")

        arrow_size = int(12 * self.scale)
        if self.direction == "left":
            ah = [rp(-size/2, -size/4), rp(-size/2 + arrow_size, -size/4 - arrow_size/2),
                  rp(-size/2 + arrow_size, -size/4 + arrow_size/2)]
        else:
            ah = [rp(size/2, -size/4), rp(size/2 - arrow_size, -size/4 - arrow_size/2),
                  rp(size/2 - arrow_size, -size/4 + arrow_size/2)]

        canvas.create_polygon(ah, fill=outline, outline=outline, tags="object")

    def draw_to_pil(self, draw, offset_x=0, offset_y=0):
        size = self.base_size * self.scale
        angle_rad = math.radians(self.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        def rp(px, py):
            rx = px * cos_a - py * sin_a + self.x + offset_x
            ry = px * sin_a + py * cos_a + self.y + offset_y
            return (int(rx), int(ry))

        width = int(5 * self.scale)

        p1 = rp(0, size/2)
        p2 = rp(0, -size/4)
        draw.line([p1, p2], fill="#000000", width=width)

        if self.direction == "left":
            p3 = rp(-size/2, -size/4)
        else:
            p3 = rp(size/2, -size/4)

        draw.line([p2, p3], fill="#000000", width=width)

        arrow_size = int(12 * self.scale)
        if self.direction == "left":
            ah = [rp(-size/2, -size/4), rp(-size/2 + arrow_size, -size/4 - arrow_size/2),
                  rp(-size/2 + arrow_size, -size/4 + arrow_size/2)]
        else:
            ah = [rp(size/2, -size/4), rp(size/2 - arrow_size, -size/4 - arrow_size/2),
                  rp(size/2 - arrow_size, -size/4 + arrow_size/2)]

        draw.polygon(ah, fill="#000000", outline="#000000")

    def contains(self, x, y):
        size = self.base_size * self.scale
        dx = abs(x - self.x)
        dy = abs(y - self.y)
        return dx < size and dy < size

    def get_bounds(self):
        size = self.base_size * self.scale
        margin = 20
        return (self.x - size - margin, self.y - size - margin,
                self.x + size + margin, self.y + size + margin)

class CurveArrow(DiagramObject):
    def __init__(self, x, y, direction="left"):
        super().__init__(x, y)
        self.direction = direction
        self.base_radius = 50
        self.curve_amount = 1.0

    def draw(self, canvas):
        radius = self.base_radius * self.scale * self.width_scale

        outline = "#000000"
        width = int(5 * self.scale)

        segments = 20
        points = []

        for i in range(segments + 1):
            t = i / segments
            if self.direction == "left":
                angle = math.radians(270 + 90 * t + self.rotation)
            else:
                angle = math.radians(180 + 90 * t + self.rotation)

            px = self.x + radius * math.cos(angle) * abs(self.curve_amount)
            py = self.y + radius * math.sin(angle) * abs(self.curve_amount)
            points.append((px, py))

        for i in range(len(points) - 1):
            canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1],
                             fill=outline, width=width, tags="object")

        arrow_size = 12 * self.scale
        end_point = points[-1]

        if self.direction == "left":
            ah_angle = math.radians(45 + self.rotation)
        else:
            ah_angle = math.radians(-45 + self.rotation)

        ah1 = end_point
        ah2 = (end_point[0] + arrow_size * math.cos(ah_angle + math.pi/6),
               end_point[1] + arrow_size * math.sin(ah_angle + math.pi/6))
        ah3 = (end_point[0] + arrow_size * math.cos(ah_angle - math.pi/6),
               end_point[1] + arrow_size * math.sin(ah_angle - math.pi/6))

        canvas.create_polygon([ah1, ah2, ah3], fill=outline, outline=outline, tags="object")

    def draw_to_pil(self, draw, offset_x=0, offset_y=0):
        radius = self.base_radius * self.scale * self.width_scale
        width = int(5 * self.scale)

        segments = 20
        points = []

        for i in range(segments + 1):
            t = i / segments
            if self.direction == "left":
                angle = math.radians(270 + 90 * t + self.rotation)
            else:
                angle = math.radians(180 + 90 * t + self.rotation)

            px = int(self.x + offset_x + radius * math.cos(angle) * abs(self.curve_amount))
            py = int(self.y + offset_y + radius * math.sin(angle) * abs(self.curve_amount))
            points.append((px, py))

        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill="#000000", width=width)

        arrow_size = 12 * self.scale
        end_point = points[-1]

        if self.direction == "left":
            ah_angle = math.radians(45 + self.rotation)
        else:
            ah_angle = math.radians(-45 + self.rotation)

        ah1 = end_point
        ah2 = (int(end_point[0] + arrow_size * math.cos(ah_angle + math.pi/6)),
               int(end_point[1] + arrow_size * math.sin(ah_angle + math.pi/6)))
        ah3 = (int(end_point[0] + arrow_size * math.cos(ah_angle - math.pi/6)),
               int(end_point[1] + arrow_size * math.sin(ah_angle - math.pi/6)))

        draw.polygon([ah1, ah2, ah3], fill="#000000", outline="#000000")

    def contains(self, x, y):
        radius = self.base_radius * self.scale
        dx = abs(x - self.x)
        dy = abs(y - self.y)
        return dx < radius * 1.5 and dy < radius * 1.5

    def get_bounds(self):
        radius = self.base_radius * self.scale * self.width_scale * abs(self.curve_amount)
        margin = 20
        return (self.x - radius - margin, self.y - radius - margin,
                self.x + radius + margin, self.y + radius + margin)

class Tree(DiagramObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.base_width, self.base_height = 40, 60

    def draw(self, canvas):
        s = self.scale
        trunk_w, trunk_h = 8*s*self.width_scale, 25*s*self.height_scale
        canvas.create_rectangle(self.x-trunk_w/2, self.y-trunk_h/2, self.x+trunk_w/2, self.y+trunk_h/2,
                               fill="#a0a0a0", outline="#000000", tags="object")
        crown_r = 20 * s
        crown_y = self.y - trunk_h/2 - crown_r*0.7
        for oy in [0, -crown_r*0.3, crown_r*0.2]:
            for ox in [0, -crown_r*0.2, crown_r*0.2]:
                canvas.create_oval(self.x+ox-crown_r, crown_y+oy-crown_r,
                                 self.x+ox+crown_r, crown_y+oy+crown_r,
                                 fill="#d0d0d0", outline="#000000", tags="object")

    def draw_to_pil(self, draw, offset_x=0, offset_y=0):
        s = self.scale
        trunk_w, trunk_h = 8*s*self.width_scale, 25*s*self.height_scale
        x, y = self.x + offset_x, self.y + offset_y
        draw.rectangle([x-trunk_w/2, y-trunk_h/2, x+trunk_w/2, y+trunk_h/2],
                      fill="#a0a0a0", outline="#000000")
        crown_r = 20 * s
        crown_y = y - trunk_h/2 - crown_r*0.7
        for oy in [0, -crown_r*0.3, crown_r*0.2]:
            for ox in [0, -crown_r*0.2, crown_r*0.2]:
                draw.ellipse([x+ox-crown_r, crown_y+oy-crown_r,
                             x+ox+crown_r, crown_y+oy+crown_r],
                            fill="#d0d0d0", outline="#000000")

    def contains(self, x, y):
        return abs(x - self.x) < 25*self.scale and abs(y - self.y) < 25*self.scale

    def get_bounds(self):
        r = 30 * self.scale
        return (self.x-r-20, self.y-r-20, self.x+r+20, self.y+r+20)

class Pedestrian(DiagramObject):
    def draw(self, canvas):
        s = self.scale
        outline = "#000000"
        width = int(3 * s) if self.selected else int(2 * s)

        angle_rad = math.radians(self.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        def rp(px, py):
            rx = px * cos_a - py * sin_a + self.x
            ry = px * sin_a + py * cos_a + self.y
            return (rx, ry)

        head_x, head_y = rp(0, -20 * s)
        head_r = 8 * s
        canvas.create_oval(head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r,
                          fill="white", outline=outline, width=width, tags="object")

        body_start = rp(0, -12 * s)
        body_end = rp(0, 10 * s)
        canvas.create_line(body_start[0], body_start[1], body_end[0], body_end[1],
                          fill=outline, width=width, tags="object")

        arm_start = rp(0, -5 * s)
        left_arm = rp(-12 * s, 5 * s)
        right_arm = rp(12 * s, 5 * s)
        canvas.create_line(arm_start[0], arm_start[1], left_arm[0], left_arm[1],
                          fill=outline, width=width, tags="object")
        canvas.create_line(arm_start[0], arm_start[1], right_arm[0], right_arm[1],
                          fill=outline, width=width, tags="object")

        leg_start = rp(0, 10 * s)
        left_leg = rp(-8 * s, 30 * s)
        right_leg = rp(8 * s, 30 * s)
        canvas.create_line(leg_start[0], leg_start[1], left_leg[0], left_leg[1],
                          fill=outline, width=width, tags="object")
        canvas.create_line(leg_start[0], leg_start[1], right_leg[0], right_leg[1],
                          fill=outline, width=width, tags="object")

    def draw_to_pil(self, draw, offset_x=0, offset_y=0):
        s = self.scale
        width = int(3 * s) if self.selected else int(2 * s)

        angle_rad = math.radians(self.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        def rp(px, py):
            rx = px * cos_a - py * sin_a + self.x + offset_x
            ry = px * sin_a + py * cos_a + self.y + offset_y
            return (int(rx), int(ry))

        head_x, head_y = rp(0, -20 * s)
        head_r = int(8 * s)
        draw.ellipse([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r],
                    fill="white", outline="#000000")

        body_start = rp(0, -12 * s)
        body_end = rp(0, 10 * s)
        draw.line([body_start, body_end], fill="#000000", width=width)

        arm_start = rp(0, -5 * s)
        left_arm = rp(-12 * s, 5 * s)
        right_arm = rp(12 * s, 5 * s)
        draw.line([arm_start, left_arm], fill="#000000", width=width)
        draw.line([arm_start, right_arm], fill="#000000", width=width)

        leg_start = rp(0, 10 * s)
        left_leg = rp(-8 * s, 30 * s)
        right_leg = rp(8 * s, 30 * s)
        draw.line([leg_start, left_leg], fill="#000000", width=width)
        draw.line([leg_start, right_leg], fill="#000000", width=width)

    def contains(self, x, y):
        return abs(x - self.x) < 20*self.scale and abs(y - self.y) < 35*self.scale

    def get_bounds(self):
        return (self.x-50, self.y-65, self.x+50, self.y+65)

class TextLabel(DiagramObject):
    def __init__(self, x, y, text="Label"):
        super().__init__(x, y)
        self.text = text

    def draw(self, canvas):
        canvas.create_text(self.x, self.y, text=self.text,
                          font=("Arial", int(12*self.scale), "bold"),
                          fill="#000000", tags="object")

    def draw_to_pil(self, draw, offset_x=0, offset_y=0):
        from PIL import ImageFont
        try:
            font = ImageFont.truetype("arial.ttf", int(12*self.scale))
        except:
            font = ImageFont.load_default()

        x, y = self.x + offset_x, self.y + offset_y
        draw.text((x, y), self.text, fill="#000000", font=font, anchor="mm")

    def contains(self, x, y):
        return abs(x-self.x) < len(self.text)*7*self.scale and abs(y-self.y) < 15*self.scale

    def get_bounds(self):
        w, h = len(self.text)*7*self.scale, 15*self.scale
        return (self.x-w-30, self.y-h-30, self.x+w+30, self.y+h+30)

class NorthArrow(DiagramObject):
    """Simple North Arrow - just an arrow pointing up with 'N' label"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.base_size = 50

    def draw(self, canvas):
        size = self.base_size * self.scale
        outline = "#000000"
        lw = int(3 * self.scale) if self.selected else int(2 * self.scale)

        # Calculate rotation
        angle_rad = math.radians(self.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        def rp(px, py):
            rx = px * cos_a - py * sin_a + self.x
            ry = px * sin_a + py * cos_a + self.y
            return (rx, ry)

        # Arrow shaft (vertical line)
        p1 = rp(0, size/2)
        p2 = rp(0, -size/2)
        canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=outline, width=lw, tags="object")

        # Arrowhead (triangle pointing up)
        arrow_size = size * 0.4
        ah1 = rp(0, -size/2)
        ah2 = rp(-arrow_size/2, -size/2 + arrow_size)
        ah3 = rp(arrow_size/2, -size/2 + arrow_size)
        canvas.create_polygon([ah1, ah2, ah3], fill=outline, outline=outline, tags="object")

        # 'N' label above arrow
        label_y = rp(0, -size/2 - 20*self.scale)
        canvas.create_text(label_y[0], label_y[1], text="N",
                          font=("Arial", int(16*self.scale), "bold"),
                          fill=outline, tags="object")

    def draw_to_pil(self, draw, offset_x=0, offset_y=0):
        size = self.base_size * self.scale

        # Calculate rotation
        angle_rad = math.radians(self.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        def rp(px, py):
            rx = px * cos_a - py * sin_a + self.x + offset_x
            ry = px * sin_a + py * cos_a + self.y + offset_y
            return (int(rx), int(ry))

        lw = int(3 * self.scale) if self.selected else int(2 * self.scale)

        # Arrow shaft
        p1 = rp(0, size/2)
        p2 = rp(0, -size/2)
        draw.line([p1, p2], fill="#000000", width=lw)

        # Arrowhead
        arrow_size = size * 0.4
        ah1 = rp(0, -size/2)
        ah2 = rp(-arrow_size/2, -size/2 + arrow_size)
        ah3 = rp(arrow_size/2, -size/2 + arrow_size)
        draw.polygon([ah1, ah2, ah3], fill="#000000", outline="#000000")

        # 'N' label
        from PIL import ImageFont
        try:
            font = ImageFont.truetype("arial.ttf", int(16*self.scale))
        except:
            font = ImageFont.load_default()

        label_pos = rp(0, -size/2 - 20*self.scale)
        draw.text(label_pos, "N", fill="#000000", font=font, anchor="mm")

    def contains(self, x, y):
        return math.sqrt((x-self.x)**2 + (y-self.y)**2) < 40*self.scale

    def get_bounds(self):
        s = 50 * self.scale
        return (self.x-s-30, self.y-s-30, self.x+s+30, self.y+s+30)

class ControlButton:
    def __init__(self, x, y, button_type, size=28):
        self.x, self.y, self.button_type, self.size = x, y, button_type, size
        self.canvas_items = []

    def draw(self, canvas):
        for item in self.canvas_items:
            canvas.delete(item)
        self.canvas_items = []

        colors = {"rotate_cw": "#3498db", "rotate_ccw": "#3498db", "scale_up": "#27ae60",
                 "scale_down": "#e67e22", "width_up": "#16a085", "width_down": "#d35400",
                 "height_up": "#8e44ad", "height_down": "#c0392b", "curve_up": "#f39c12",
                 "curve_down": "#e74c3c"}
        bg = colors.get(self.button_type, "#95a5a6")

        item = canvas.create_oval(self.x-self.size/2, self.y-self.size/2,
                                 self.x+self.size/2, self.y+self.size/2,
                                 fill=bg, outline="white", width=2, tags="control")
        self.canvas_items.append(item)

        labels = {
            "rotate_cw": "R+",
            "rotate_ccw": "R-", 
            "scale_up": "+",
            "scale_down": "-",
            "width_up": "W+",
            "width_down": "W-",
            "height_up": "H+",
            "height_down": "H-",
            "curve_up": "C+",
            "curve_down": "C-"
        }

        item = canvas.create_text(self.x, self.y, text=labels.get(self.button_type, "?"),
                                 font=("Arial", 10, "bold"), fill="white", tags="control")
        self.canvas_items.append(item)

    def contains(self, x, y):
        return math.sqrt((x-self.x)**2 + (y-self.y)**2) < self.size/2


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class AccidentReconstructorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Accident Reconstruction Tool v{AutoUpdater.CURRENT_VERSION}")
        self.root.geometry("1400x900")
        self.objects, self.selected_object, self.control_buttons = [], None, []
        self.current_tool, self.drag_start = None, None
        self.setup_ui()

    def setup_ui(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Check for Updates", command=lambda: manual_update_check(self.root))
        help_menu.add_separator()
        help_menu.add_command(label=f"About (v{AutoUpdater.CURRENT_VERSION})", command=self.show_about)

        # SCROLLABLE TOOLBOX
        tool_frame = tk.Frame(self.root, width=280, bg="#ecf0f1", relief=tk.RAISED, bd=2)
        tool_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        tool_frame.pack_propagate(False)

        canvas_tools = tk.Canvas(tool_frame, bg="#ecf0f1", highlightthickness=0)
        scrollbar = ttk.Scrollbar(tool_frame, orient="vertical", command=canvas_tools.yview)
        scrollable_frame = tk.Frame(canvas_tools, bg="#ecf0f1")

        scrollable_frame.bind("<Configure>",
            lambda e: canvas_tools.configure(scrollregion=canvas_tools.bbox("all")))

        canvas_tools.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_tools.configure(yscrollcommand=scrollbar.set)

        canvas_tools.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def on_mousewheel(event):
            canvas_tools.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas_tools.bind_all("<MouseWheel>", on_mousewheel)

        # Header
        header_frame = tk.Frame(scrollable_frame, bg="#2c3e50", height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        tk.Label(header_frame, text="Accident Reconstruction", bg="#2c3e50", fg="white",
                font=("Arial", 13, "bold")).pack(pady=(15, 2))
        tk.Label(header_frame, text="Professional Edition v2.4", bg="#2c3e50", fg="#ecf0f1",
                font=("Arial", 9)).pack()

        # VEHICLES
        vehicles_section = CollapsibleSection(scrollable_frame, "VEHICLES")
        vehicles_section.pack(fill=tk.X, pady=5, padx=5)
        vehicles_content = vehicles_section.get_content_frame()

        for text, tool, color in [("Sedan", "car", "#34495e"), ("Pickup Truck", "truck", "#34495e"),
                                  ("18-Wheeler", "semi", "#2c3e50"), ("Motorcycle", "motorcycle", "#7f8c8d")]:
            tk.Button(vehicles_content, text=text, command=lambda t=tool: self.set_tool(t),
                     width=28, height=2, bg=color, fg="white", font=("Arial", 9, "bold"),
                     relief=tk.FLAT, bd=0, activebackground="#1abc9c", activeforeground="white",
                     cursor="hand2").pack(pady=4, padx=8, fill=tk.X)

        # ROADS
        roads_section = CollapsibleSection(scrollable_frame, "ROADS")
        roads_section.pack(fill=tk.X, pady=5, padx=5)
        roads_content = roads_section.get_content_frame()

        tk.Label(roads_content, text="Road Type:", bg="#ecf0f1", font=("Arial", 9, "bold")).pack(pady=(5, 3))
        self.road_combo = ttk.Combobox(roads_content, values=["2-Lane Road", "4-Lane Road",
                                       "4-Lane Highway", "Intersection"], state="readonly", width=26, font=("Arial", 9))
        self.road_combo.set("2-Lane Road")
        self.road_combo.pack(pady=5, padx=8)

        for text, tool, color in [("Straight Road", "road", "#5d6d7e"), ("Curved Road", "curved_road", "#34495e")]:
            tk.Button(roads_content, text=text, command=lambda t=tool: self.set_tool(t),
                     width=28, height=2, bg=color, fg="white", font=("Arial", 9, "bold"),
                     relief=tk.FLAT, bd=0, activebackground="#1abc9c", activeforeground="white",
                     cursor="hand2").pack(pady=4, padx=8, fill=tk.X)

        # ARROWS
        arrows_section = CollapsibleSection(scrollable_frame, "ARROWS")
        arrows_section.pack(fill=tk.X, pady=5, padx=5)
        arrows_content = arrows_section.get_content_frame()

        for text, tool, color in [("Straight Arrow", "arrow", "#2c3e50"), ("Left Turn Arrow", "turn_left", "#34495e"),
                                  ("Right Turn Arrow", "turn_right", "#34495e"), ("Left Curve Arrow", "curve_left", "#5d6d7e"),
                                  ("Right Curve Arrow", "curve_right", "#5d6d7e")]:
            tk.Button(arrows_content, text=text, command=lambda t=tool: self.set_tool(t),
                     width=28, height=2, bg=color, fg="white", font=("Arial", 9, "bold"),
                     relief=tk.FLAT, bd=0, activebackground="#1abc9c", activeforeground="white",
                     cursor="hand2").pack(pady=4, padx=8, fill=tk.X)

        # SYMBOLS
        symbols_section = CollapsibleSection(scrollable_frame, "SYMBOLS")
        symbols_section.pack(fill=tk.X, pady=5, padx=5)
        symbols_content = symbols_section.get_content_frame()

        for text, tool, color in [("Tree", "tree", "#27ae60"), ("Pedestrian", "pedestrian", "#95a5a6"),
                                  ("Text Label", "text", "#8e44ad"), ("North Arrow", "north", "#16a085")]:
            tk.Button(symbols_content, text=text, command=lambda t=tool: self.set_tool(t),
                     width=28, height=2, bg=color, fg="white", font=("Arial", 9, "bold"),
                     relief=tk.FLAT, bd=0, activebackground="#1abc9c", activeforeground="white",
                     cursor="hand2").pack(pady=4, padx=8, fill=tk.X)

        # ACTIONS
        actions_section = CollapsibleSection(scrollable_frame, "ACTIONS")
        actions_section.pack(fill=tk.X, pady=5, padx=5)
        actions_content = actions_section.get_content_frame()

        for text, command, color in [("Delete Selected", self.delete_selected, "#c0392b"), ("Clear All", self.clear_all, "#e74c3c")]:
            tk.Button(actions_content, text=text, command=command, width=28, height=2, bg=color, fg="white",
                     font=("Arial", 9, "bold"), relief=tk.FLAT, bd=0, activebackground="#e74c3c",
                     activeforeground="white", cursor="hand2").pack(pady=4, padx=8, fill=tk.X)

        # EXPORT
        export_section = CollapsibleSection(scrollable_frame, "EXPORT")
        export_section.pack(fill=tk.X, pady=5, padx=5)
        export_content = export_section.get_content_frame()

        tk.Button(export_content, text="Export to PDF", command=self.export_pdf, width=28, height=2,
                 bg="#27ae60", fg="white", font=("Arial", 9, "bold"), relief=tk.FLAT, bd=0,
                 activebackground="#229954", activeforeground="white", cursor="hand2").pack(pady=4, padx=8, fill=tk.X)

        tk.Label(scrollable_frame, text="", bg="#ecf0f1", height=2).pack()

        # CANVAS
        canvas_frame = tk.Frame(self.root, bg="#bdc3c7", relief=tk.SUNKEN, bd=2)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.root.bind("<Delete>", lambda e: self.delete_selected())
        self.root.bind("<r>", lambda e: self.rotate_selected())
        self.root.bind("<R>", lambda e: self.rotate_selected(-15))

        # Status bar
        status_frame = tk.Frame(self.root, bg="#34495e", height=35)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(status_frame, text="Ready | Select a tool and click on canvas to place objects",
                                     bd=0, anchor=tk.W, bg="#ecf0f1", fg="#2c3e50", font=("Arial", 9), padx=10)
        self.status_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)

        legend_text = "Controls: R+ Rotate | + Size | W+ Width | H+ Height | C+ Curve | [R] Key | [Del] Delete"
        tk.Label(status_frame, text=legend_text, bg="#34495e", fg="white",
                font=("Arial", 8), padx=15).pack(side=tk.RIGHT, pady=2)

    def set_tool(self, tool):
        self.current_tool = tool
        tool_names = {"car": "Sedan", "truck": "Pickup Truck", "semi": "18-Wheeler", "motorcycle": "Motorcycle",
                     "pedestrian": "Pedestrian", "tree": "Tree", "road": "Straight Road", "curved_road": "Curved Road",
                     "arrow": "Straight Arrow", "turn_left": "Left Turn Arrow", "turn_right": "Right Turn Arrow",
                     "curve_left": "Left Curve Arrow", "curve_right": "Right Curve Arrow", "text": "Text Label", 
                     "north": "North Arrow"}
        self.status_label.config(text=f"Tool: {tool_names.get(tool, tool)} - Click canvas to place")

    def create_control_buttons(self):
        self.control_buttons = []
        if not self.selected_object:
            return
        x1, y1, x2, y2 = self.selected_object.get_bounds()
        cx, cy = (x1+x2)/2, (y1+y2)/2
        has_curve = isinstance(self.selected_object, (CurvedRoad, CurveArrow))

        if has_curve:
            self.control_buttons = [
                ControlButton(cx, y1-20, "rotate_ccw"), ControlButton(x2+20, cy-25, "width_up"),
                ControlButton(x2+20, cy, "scale_up"), ControlButton(x2+20, cy+25, "curve_up"),
                ControlButton(cx+15, y2+20, "height_up"), ControlButton(cx-15, y2+20, "rotate_cw"),
                ControlButton(x1-20, cy+25, "curve_down"), ControlButton(x1-20, cy, "scale_down"),
                ControlButton(x1-20, cy-25, "width_down"), ControlButton(cx, y1-50, "height_down")
            ]
        else:
            self.control_buttons = [
                ControlButton(cx, y1-20, "rotate_ccw"), ControlButton(x2+20, cy-15, "width_up"),
                ControlButton(x2+20, cy+15, "scale_up"), ControlButton(cx+15, y2+20, "height_up"),
                ControlButton(cx-15, y2+20, "rotate_cw"), ControlButton(x1-20, cy+15, "scale_down"),
                ControlButton(x1-20, cy-15, "width_down"), ControlButton(cx, y1-50, "height_down")
            ]

    def draw_control_buttons(self):
        for button in self.control_buttons:
            button.draw(self.canvas)

    def on_canvas_click(self, event):
        for button in self.control_buttons:
            if button.contains(event.x, event.y):
                self.handle_control_button(button.button_type)
                return
        clicked_obj = None
        for obj in reversed(self.objects):
            if obj.contains(event.x, event.y):
                clicked_obj = obj
                break
        if clicked_obj:
            if self.selected_object:
                self.selected_object.selected = False
            self.selected_object = clicked_obj
            self.selected_object.selected = True
            self.drag_start = (event.x, event.y)
            self.create_control_buttons()
            self.redraw()
            self.update_status()
        elif self.current_tool:
            self.add_object(event.x, event.y)
            self.current_tool = None
            self.status_label.config(text="Ready")
        else:
            if self.selected_object:
                self.selected_object.selected = False
                self.selected_object = None
                self.control_buttons = []
                self.redraw()
                self.status_label.config(text="Ready")

    def handle_control_button(self, button_type):
        if not self.selected_object:
            return
        actions = {
            "rotate_cw": lambda: self.selected_object.rotate(15), "rotate_ccw": lambda: self.selected_object.rotate(-15),
            "scale_up": lambda: self.selected_object.scale_up(), "scale_down": lambda: self.selected_object.scale_down(),
            "width_up": lambda: self.selected_object.width_up(), "width_down": lambda: self.selected_object.width_down(),
            "height_up": lambda: self.selected_object.height_up(), "height_down": lambda: self.selected_object.height_down(),
            "curve_up": lambda: self.selected_object.curve_up(), "curve_down": lambda: self.selected_object.curve_down()
        }
        if button_type in actions:
            actions[button_type]()
            self.create_control_buttons()
            self.redraw()
            self.update_status()

    def on_canvas_drag(self, event):
        if self.selected_object and self.drag_start:
            dx, dy = event.x - self.drag_start[0], event.y - self.drag_start[1]
            self.selected_object.move(dx, dy)
            self.drag_start = (event.x, event.y)
            self.create_control_buttons()
            self.redraw()

    def on_canvas_release(self, event):
        self.drag_start = None

    def on_right_click(self, event):
        if self.selected_object:
            self.selected_object.rotate(15)
            self.create_control_buttons()
            self.redraw()
            self.update_status()

    def rotate_selected(self, angle=15):
        if self.selected_object:
            self.selected_object.rotate(angle)
            self.create_control_buttons()
            self.redraw()
            self.update_status()

    def update_status(self):
        if self.selected_object:
            obj_type = type(self.selected_object).__name__
            status_text = f"{obj_type} | Rot: {self.selected_object.rotation:.0f}Â° | Scale: {self.selected_object.scale:.2f}x"
            if hasattr(self.selected_object, 'curve_amount') and isinstance(self.selected_object, (CurvedRoad, CurveArrow)):
                status_text += f" | Curve: {self.selected_object.curve_amount:.1f}"
            self.status_label.config(text=status_text)

    def add_object(self, x, y):
        obj = None
        if self.current_tool in ["car", "truck", "semi", "motorcycle"]:
            obj = Vehicle(x, y, self.current_tool)
        elif self.current_tool == "tree":
            obj = Tree(x, y)
        elif self.current_tool == "pedestrian":
            obj = Pedestrian(x, y)
        elif self.current_tool == "road":
            obj = Road(x, y, self.road_combo.get())
        elif self.current_tool == "curved_road":
            obj = CurvedRoad(x, y, self.road_combo.get())
        elif self.current_tool == "arrow":
            obj = Arrow(x, y)
        elif self.current_tool == "turn_left":
            obj = TurnArrow(x, y, "left")
        elif self.current_tool == "turn_right":
            obj = TurnArrow(x, y, "right")
        elif self.current_tool == "curve_left":
            obj = CurveArrow(x, y, "left")
        elif self.current_tool == "curve_right":
            obj = CurveArrow(x, y, "right")
        elif self.current_tool == "text":
            text = simpledialog.askstring("Text Label", "Enter text:")
            if text:
                obj = TextLabel(x, y, text)
        elif self.current_tool == "north":
            obj = NorthArrow(x, y)

        if obj:
            self.objects.append(obj)
            if self.selected_object:
                self.selected_object.selected = False
            self.selected_object = obj
            obj.selected = True
            self.create_control_buttons()
            self.redraw()
            self.update_status()

    def delete_selected(self):
        if self.selected_object:
            self.objects.remove(self.selected_object)
            self.selected_object = None
            self.control_buttons = []
            self.redraw()
            self.status_label.config(text="Object deleted")

    def clear_all(self):
        if messagebox.askyesno("Clear All", "Clear all objects from the diagram?"):
            self.objects.clear()
            self.selected_object = None
            self.control_buttons = []
            self.redraw()
            self.status_label.config(text="Diagram cleared")

    def redraw(self):
        self.canvas.delete("object")
        self.canvas.delete("control")
        for obj in self.objects:
            obj.draw(self.canvas)
        self.draw_control_buttons()

    def export_pdf(self):
        """Export diagram to PDF with actual canvas content"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"AccidentDiagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        if not filename:
            return

        try:
            # Get canvas dimensions
            self.canvas.update()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Find bounding box of all objects
            if self.objects:
                min_x = min(obj.get_bounds()[0] for obj in self.objects)
                min_y = min(obj.get_bounds()[1] for obj in self.objects)
                max_x = max(obj.get_bounds()[2] for obj in self.objects)
                max_y = max(obj.get_bounds()[3] for obj in self.objects)

                # Add margin
                margin = 50
                min_x = max(0, min_x - margin)
                min_y = max(0, min_y - margin)
                max_x = min(canvas_width, max_x + margin)
                max_y = min(canvas_height, max_y + margin)

                diagram_width = int(max_x - min_x)
                diagram_height = int(max_y - min_y)
            else:
                min_x, min_y = 0, 0
                diagram_width, diagram_height = canvas_width, canvas_height

            # Create PIL image of diagram
            img = Image.new('RGB', (diagram_width, diagram_height), 'white')
            draw = ImageDraw.Draw(img)

            # Draw all objects to PIL image
            for obj in self.objects:
                obj.draw_to_pil(draw, offset_x=-min_x, offset_y=-min_y)

            # Save image to temporary file
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_img_path = temp_img.name
            temp_img.close()
            img.save(temp_img_path, 'PNG')

            # Create PDF
            c = pdf_canvas.Canvas(filename, pagesize=letter)
            page_width, page_height = letter

            # Title
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, page_height - 50, "Accident Reconstruction Diagram")

            # Metadata
            c.setFont("Helvetica", 10)
            c.drawString(50, page_height - 70, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(50, page_height - 85, f"Created with: Accident Reconstruction Tool v{AutoUpdater.CURRENT_VERSION}")

            # Line separator
            c.setStrokeColorRGB(0.5, 0.5, 0.5)
            c.setLineWidth(1)
            c.line(50, page_height - 95, page_width - 50, page_height - 95)

            # Calculate scaling to fit diagram on page
            max_img_width = page_width - 100
            max_img_height = page_height - 200

            scale = min(max_img_width / diagram_width, max_img_height / diagram_height, 1.0)

            scaled_width = diagram_width * scale
            scaled_height = diagram_height * scale

            # Center the image
            x_pos = (page_width - scaled_width) / 2
            y_pos = page_height - 150 - scaled_height

            # Add diagram image to PDF
            c.drawImage(temp_img_path, x_pos, y_pos, width=scaled_width, height=scaled_height)

            # Footer
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(50, 30, f"Accident Reconstruction Tool v{AutoUpdater.CURRENT_VERSION} | Galaxy AI")

            c.save()

            # Clean up temp file
            try:
                os.remove(temp_img_path)
            except:
                pass

            messagebox.showinfo("Success", f"PDF exported successfully!\n\nSaved to: {filename}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export PDF:\n{str(e)}")

    def show_about(self):
        about = f"""Accident Reconstruction Tool
Professional Edition

Version: {AutoUpdater.CURRENT_VERSION}
Author: Galaxy AI

Features:
â€¢ 4 Realistic Top-Down Vehicles
â€¢ 6 Road Types
â€¢ 5 Arrow Types
â€¢ Symbols & Labels
â€¢ Simple North Arrow (N)
â€¢ Auto-Update (Fixed)
â€¢ Collapsible Sections
â€¢ Professional UI
â€¢ Full PDF Export with Diagram"""
        messagebox.showinfo("About", about, parent=self.root)

def main():
    root = tk.Tk()
    app = AccidentReconstructorApp(root)
    root.after(1000, lambda: check_for_updates_on_startup(root))
    root.mainloop()

if __name__ == "__main__":
    main()
