#!/usr/bin/env python3
"""
Accident Reconstruction Diagram Tool v2.5.0
Complete Edition with Intersections, Animal, and ATV
Author: Galaxy AI
Date: February 26, 2026
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import math
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
from datetime import datetime
import urllib.request
import json
import tempfile
import shutil
import sys
import os

# ============================================================================
# AUTO-UPDATE SYSTEM
# ============================================================================

class AutoUpdater:
    GITHUB_USER = "omerta7z"
    GITHUB_REPO = "accident-reconstructor"
    CURRENT_VERSION = "2.5.0"

    @classmethod
    def get_version_url(cls):
        return f"https://raw.githubusercontent.com/{cls.GITHUB_USER}/{cls.GITHUB_REPO}/main/version.json"

    @classmethod
    def get_download_url(cls):
        return f"https://raw.githubusercontent.com/{cls.GITHUB_USER}/{cls.GITHUB_REPO}/main/accident_reconstructor.py"

    @classmethod
    def check_for_updates(cls):
        try:
            req = urllib.request.Request(cls.get_version_url())
            req.add_header('User-Agent', 'AccidentReconstructor/2.5.0')
            with urllib.request.urlopen(req, timeout=10) as response:
                version_data = json.loads(response.read().decode('utf-8'))
            latest_version = version_data.get("version", "0.0.0")
            current = tuple(map(int, cls.CURRENT_VERSION.split(".")))
            latest = tuple(map(int, latest_version.split(".")))
            if latest > current:
                return True, latest_version, version_data.get("changelog", "")
            return False, cls.CURRENT_VERSION, ""
        except:
            return False, cls.CURRENT_VERSION, ""

    @classmethod
    def download_update(cls, progress_callback=None):
        try:
            temp_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.py')
            temp_path = temp_file.name
            temp_file.close()

            def report_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    percent = min(100, (block_num * block_size / total_size) * 100)
                    progress_callback(percent)

            req = urllib.request.Request(cls.get_download_url())
            req.add_header('User-Agent', 'AccidentReconstructor/2.6.0')
            urllib.request.urlretrieve(cls.get_download_url(), temp_path, reporthook=report_progress)
            return temp_path
        except:
            return None

    @classmethod
    def apply_update(cls, new_file_path):
        try:
            current_file = os.path.abspath(sys.argv[0]) if not getattr(sys, 'frozen', False) else sys.executable
            backup_file = current_file + ".backup"
            if os.path.exists(current_file):
                shutil.copy2(current_file, backup_file)
            shutil.copy2(new_file_path, current_file)
            try:
                os.remove(new_file_path)
            except:
                pass
            return True
        except:
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
        tk.Label(content, text=f"Version {version} available!",
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
        changelog_text.insert("1.0", changelog if changelog else "Updates")
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
            self.progress_label.config(text="Installing...")
            self.dialog.update()
            if AutoUpdater.apply_update(new_file):
                messagebox.showinfo("Complete", "Installed! Restart app.", parent=self.dialog)
                self.dialog.destroy()
                sys.exit(0)
            else:
                messagebox.showerror("Failed", "Install failed.", parent=self.dialog)
                self.dialog.destroy()
        else:
            messagebox.showerror("Failed", "Download failed.", parent=self.dialog)
            self.dialog.destroy()

    def update_later(self):
        self.dialog.destroy()

def check_for_updates_on_startup(root):
    try:
        has_update, version, changelog = AutoUpdater.check_for_updates()
        if has_update:
            UpdateDialog(root, version, changelog)
    except:
        pass

def manual_update_check(root):
    try:
        has_update, version, changelog = AutoUpdater.check_for_updates()
        if has_update:
            UpdateDialog(root, version, changelog)
        else:
            messagebox.showinfo("No Updates", f"Latest: {AutoUpdater.CURRENT_VERSION}", parent=root)
    except Exception as e:
        messagebox.showerror("Failed", f"Error: {e}", parent=root)

# ============================================================================
# UI COMPONENTS
# ============================================================================

class CollapsibleSection(tk.Frame):
    def __init__(self, parent, title, bg_color="#ecf0f1"):
        super().__init__(parent, bg=bg_color)
        self.bg_color, self.is_expanded = bg_color, True

        self.header = tk.Frame(self, bg="#34495e", cursor="hand2", height=35)
        self.header.pack(fill=tk.X, pady=(0, 2))
        self.header.pack_propagate(False)

        self.arrow_label = tk.Label(self.header, text="▼", bg="#34495e", fg="white",
                                    font=("Arial", 10, "bold"), width=2)
        self.arrow_label.pack(side=tk.LEFT, padx=8)

        self.title_label = tk.Label(self.header, text=title, bg="#34495e", fg="white",
                                    font=("Arial", 10, "bold"), anchor="w")
        self.title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8)

        self.content = tk.Frame(self, bg=bg_color)
        self.content.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        for widget in [self.header, self.arrow_label, self.title_label]:
            widget.bind("<Button-1>", self.toggle)

    def toggle(self, event=None):
        if self.is_expanded:
            self.content.pack_forget()
            self.arrow_label.config(text="▶")
            self.is_expanded = False
        else:
            self.content.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
            self.arrow_label.config(text="▼")
            self.is_expanded = True

    def get_content_frame(self):
        return self.content

# ============================================================================
# DIAGRAM OBJECTS BASE CLASS
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

# ============================================================================
# VEHICLE CLASSES (5 TYPES: Car, Truck, Semi, Motorcycle, ATV)
# ============================================================================

class Vehicle(DiagramObject):
    """All vehicle types with realistic top-down views"""
    def __init__(self, x, y, vehicle_type="car"):
        super().__init__(x, y)
        self.vehicle_type = vehicle_type
        sizes = {
            "car": (55, 100),
            "truck": (75, 130),
            "semi": (80, 200),
            "motorcycle": (30, 65),
            "atv": (50, 70)  # NEW in v2.5.0
        }
        self.base_width, self.base_height = sizes.get(vehicle_type, (55, 100))

    def draw(self, canvas):
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

        # Draw specific vehicle type
        if self.vehicle_type == "atv":
            self._draw_atv(canvas, rp, hw, hh, s, outline, lw)
        elif self.vehicle_type == "motorcycle":
            self._draw_motorcycle(canvas, rp, hw, hh, s, outline, lw)
        elif self.vehicle_type == "semi":
            self._draw_semi(canvas, rp, hw, hh, s, outline, lw)
        elif self.vehicle_type == "truck":
            self._draw_truck(canvas, rp, hw, hh, s, outline, lw)
        else:
            self._draw_car(canvas, rp, hw, hh, s, outline, lw)

    def _draw_atv(self, canvas, rp, hw, hh, s, outline, lw):
        """NEW: ATV with 4 wheels, brown color"""
        # Body
        body = [rp(-hw*0.7, -hh*0.7), rp(hw*0.7, -hh*0.7),
               rp(hw*0.7, hh*0.7), rp(-hw*0.7, hh*0.7)]
        canvas.create_polygon(body, fill="#8b4513", outline=outline, width=lw, tags="object")

        # Handlebars
        handlebar_y = -hh*0.75
        canvas.create_line(rp(-hw*0.9, handlebar_y)[0], rp(-hw*0.9, handlebar_y)[1],
                          rp(hw*0.9, handlebar_y)[0], rp(hw*0.9, handlebar_y)[1],
                          fill=outline, width=int(lw*1.5), tags="object")

        # Seat
        seat = [rp(-hw*0.6, -hh*0.2), rp(hw*0.6, -hh*0.2),
               rp(hw*0.6, hh*0.4), rp(-hw*0.6, hh*0.4)]
        canvas.create_polygon(seat, fill="#654321", outline=outline, width=int(lw*0.7), tags="object")

        # 4 Wheels
        wr = 9 * s
        for wx, wy in [(-hw*0.85, -hh*0.65), (hw*0.85, -hh*0.65),
                      (-hw*0.85, hh*0.65), (hw*0.85, hh*0.65)]:
            wheel_x, wheel_y = rp(wx, wy)
            canvas.create_oval(wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr,
                             fill="#000000", outline=outline, width=int(lw*0.8), tags="object")

    def _draw_car(self, canvas, rp, hw, hh, s, outline, lw):
        """Sedan"""
        body = [rp(-hw*0.9, -hh*0.85), rp(hw*0.9, -hh*0.85),
               rp(hw*0.9, hh*0.85), rp(-hw*0.9, hh*0.85)]
        canvas.create_polygon(body, fill="#3498db", outline=outline, width=lw, tags="object")
        hood = [rp(-hw*0.85, -hh*0.85), rp(hw*0.85, -hh*0.85),
               rp(hw*0.85, -hh*0.5), rp(-hw*0.85, -hh*0.5)]
        canvas.create_polygon(hood, fill="#2980b9", outline=outline, width=int(lw*0.7), tags="object")
        windshield = [rp(-hw*0.7, -hh*0.5), rp(hw*0.7, -hh*0.5),
                     rp(hw*0.7, -hh*0.2), rp(-hw*0.7, -hh*0.2)]
        canvas.create_polygon(windshield, fill="#85c1e9", outline=outline, width=int(lw*0.5), tags="object")
        roof = [rp(-hw*0.75, -hh*0.2), rp(hw*0.75, -hh*0.2),
               rp(hw*0.75, hh*0.3), rp(-hw*0.75, hh*0.3)]
        canvas.create_polygon(roof, fill="#5dade2", outline=outline, width=int(lw*0.5), tags="object")
        rear_window = [rp(-hw*0.7, hh*0.3), rp(hw*0.7, hh*0.3),
                      rp(hw*0.7, hh*0.5), rp(-hw*0.7, hh*0.5)]
        canvas.create_polygon(rear_window, fill="#85c1e9", outline=outline, width=int(lw*0.5), tags="object")
        trunk = [rp(-hw*0.85, hh*0.5), rp(hw*0.85, hh*0.5),
                rp(hw*0.85, hh*0.85), rp(-hw*0.85, hh*0.85)]
        canvas.create_polygon(trunk, fill="#2980b9", outline=outline, width=int(lw*0.7), tags="object")
        wr = 8 * s
        for wx, wy in [(-hw*0.75, -hh*0.6), (hw*0.75, -hh*0.6),
                      (-hw*0.75, hh*0.6), (hw*0.75, hh*0.6)]:
            wheel_x, wheel_y = rp(wx, wy)
            canvas.create_oval(wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr,
                             fill="#000000", outline=outline, width=int(lw*0.6), tags="object")

    def _draw_truck(self, canvas, rp, hw, hh, s, outline, lw):
        """Pickup truck"""
        cab = [rp(-hw*0.9, -hh*0.85), rp(hw*0.9, -hh*0.85),
              rp(hw*0.9, -hh*0.2), rp(-hw*0.9, -hh*0.2)]
        canvas.create_polygon(cab, fill="#e74c3c", outline=outline, width=lw, tags="object")
        windshield = [rp(-hw*0.7, -hh*0.6), rp(hw*0.7, -hh*0.6),
                     rp(hw*0.7, -hh*0.35), rp(-hw*0.7, -hh*0.35)]
        canvas.create_polygon(windshield, fill="#f1948a", outline=outline, width=int(lw*0.5), tags="object")
        bed = [rp(-hw*0.9, -hh*0.15), rp(hw*0.9, -hh*0.15),
              rp(hw*0.9, hh*0.85), rp(-hw*0.9, hh*0.85)]
        canvas.create_polygon(bed, fill="#c0392b", outline=outline, width=lw, tags="object")
        wr = 9 * s
        for wx, wy in [(-hw*0.75, -hh*0.7), (hw*0.75, -hh*0.7),
                      (-hw*0.75, hh*0.65), (hw*0.75, hh*0.65)]:
            wheel_x, wheel_y = rp(wx, wy)
            canvas.create_oval(wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr,
                             fill="#000000", outline=outline, width=int(lw*0.6), tags="object")

    def _draw_semi(self, canvas, rp, hw, hh, s, outline, lw):
        """18-wheeler"""
        cab_h = hh * 0.25
        cab = [rp(-hw*0.9, -hh*0.85), rp(hw*0.9, -hh*0.85),
              rp(hw*0.9, -hh*0.85+cab_h*2), rp(-hw*0.9, -hh*0.85+cab_h*2)]
        canvas.create_polygon(cab, fill="#f39c12", outline=outline, width=lw, tags="object")
        windshield = [rp(-hw*0.7, -hh*0.75), rp(hw*0.7, -hh*0.75),
                     rp(hw*0.7, -hh*0.55), rp(-hw*0.7, -hh*0.55)]
        canvas.create_polygon(windshield, fill="#f8c471", outline=outline, width=int(lw*0.5), tags="object")
        trailer = [rp(-hw*0.95, -hh*0.85+cab_h*2+5*s), rp(hw*0.95, -hh*0.85+cab_h*2+5*s),
                  rp(hw*0.95, hh*0.85), rp(-hw*0.95, hh*0.85)]
        canvas.create_polygon(trailer, fill="#d68910", outline=outline, width=lw, tags="object")
        wr = 7 * s
        for wx, wy in [(-hw*0.75, -hh*0.85+cab_h*2), (hw*0.75, -hh*0.85+cab_h*2),
                      (-hw*0.85, hh*0.5), (hw*0.85, hh*0.5),
                      (-hw*0.85, hh*0.7), (hw*0.85, hh*0.7)]:
            wheel_x, wheel_y = rp(wx, wy)
            canvas.create_oval(wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr,
                             fill="#000000", outline=outline, width=int(lw*0.6), tags="object")

    def _draw_motorcycle(self, canvas, rp, hw, hh, s, outline, lw):
        """Motorcycle"""
        body = [rp(-hw*0.4, -hh*0.7), rp(hw*0.4, -hh*0.7),
               rp(hw*0.4, hh*0.7), rp(-hw*0.4, hh*0.7)]
        canvas.create_polygon(body, fill="#7f8c8d", outline=outline, width=lw, tags="object")
        handlebar_y = -hh*0.75
        canvas.create_line(rp(-hw*0.8, handlebar_y)[0], rp(-hw*0.8, handlebar_y)[1],
                          rp(hw*0.8, handlebar_y)[0], rp(hw*0.8, handlebar_y)[1],
                          fill=outline, width=int(lw*1.5), tags="object")
        seat = [rp(-hw*0.5, -hh*0.2), rp(hw*0.5, -hh*0.2),
               rp(hw*0.5, hh*0.3), rp(-hw*0.5, hh*0.3)]
        canvas.create_polygon(seat, fill="#95a5a6", outline=outline, width=int(lw*0.7), tags="object")
        wr = 10 * s
        for wx, wy in [(0, -hh*0.7), (0, hh*0.7)]:
            wheel_x, wheel_y = rp(wx, wy)
            canvas.create_oval(wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr,
                             fill="#000000", outline=outline, width=int(lw*0.8), tags="object")

    def draw_to_pil(self, draw, offset_x=0, offset_y=0):
        """Draw to PIL for PDF export"""
        w = self.base_width * self.scale * self.width_scale
        h = self.base_height * self.scale * self.height_scale
        angle = math.radians(self.rotation)
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        def rp(px, py):
            return (int(px * cos_a - py * sin_a + self.x + offset_x),
                   int(px * sin_a + py * cos_a + self.y + offset_y))

        hw, hh, s = w/2, h/2, self.scale
        shadow = [rp(-hw+3*s, -hh+3*s), rp(hw+3*s, -hh+3*s),
                 rp(hw+3*s, hh+3*s), rp(-hw+3*s, hh+3*s)]
        draw.polygon(shadow, fill="#d0d0d0")

        if self.vehicle_type == "atv":
            body = [rp(-hw*0.7, -hh*0.7), rp(hw*0.7, -hh*0.7),
                   rp(hw*0.7, hh*0.7), rp(-hw*0.7, hh*0.7)]
            draw.polygon(body, fill="#8b4513", outline="#000000")
            seat = [rp(-hw*0.6, -hh*0.2), rp(hw*0.6, -hh*0.2),
                   rp(hw*0.6, hh*0.4), rp(-hw*0.6, hh*0.4)]
            draw.polygon(seat, fill="#654321", outline="#000000")
            wr = int(9 * s)
            for wx, wy in [(-hw*0.85, -hh*0.65), (hw*0.85, -hh*0.65),
                          (-hw*0.85, hh*0.65), (hw*0.85, hh*0.65)]:
                wheel_x, wheel_y = rp(wx, wy)
                draw.ellipse([wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr], fill="#000000")
        elif self.vehicle_type == "motorcycle":
            body = [rp(-hw*0.4, -hh*0.7), rp(hw*0.4, -hh*0.7),
                   rp(hw*0.4, hh*0.7), rp(-hw*0.4, hh*0.7)]
            draw.polygon(body, fill="#7f8c8d", outline="#000000")
            wr = int(10 * s)
            for wx, wy in [(0, -hh*0.7), (0, hh*0.7)]:
                wheel_x, wheel_y = rp(wx, wy)
                draw.ellipse([wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr], fill="#000000")
        elif self.vehicle_type == "semi":
            cab_h = hh * 0.25
            cab = [rp(-hw*0.9, -hh*0.85), rp(hw*0.9, -hh*0.85),
                  rp(hw*0.9, -hh*0.85+cab_h*2), rp(-hw*0.9, -hh*0.85+cab_h*2)]
            draw.polygon(cab, fill="#f39c12", outline="#000000")
            trailer = [rp(-hw*0.95, -hh*0.85+cab_h*2+5*s), rp(hw*0.95, -hh*0.85+cab_h*2+5*s),
                      rp(hw*0.95, hh*0.85), rp(-hw*0.95, hh*0.85)]
            draw.polygon(trailer, fill="#d68910", outline="#000000")
            wr = int(7 * s)
            for wx, wy in [(-hw*0.75, -hh*0.85+cab_h*2), (hw*0.75, -hh*0.85+cab_h*2),
                          (-hw*0.85, hh*0.5), (hw*0.85, hh*0.5),
                          (-hw*0.85, hh*0.7), (hw*0.85, hh*0.7)]:
                wheel_x, wheel_y = rp(wx, wy)
                draw.ellipse([wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr], fill="#000000")
        elif self.vehicle_type == "truck":
            cab = [rp(-hw*0.9, -hh*0.85), rp(hw*0.9, -hh*0.85),
                  rp(hw*0.9, -hh*0.2), rp(-hw*0.9, -hh*0.2)]
            draw.polygon(cab, fill="#e74c3c", outline="#000000")
            bed = [rp(-hw*0.9, -hh*0.15), rp(hw*0.9, -hh*0.15),
                  rp(hw*0.9, hh*0.85), rp(-hw*0.9, hh*0.85)]
            draw.polygon(bed, fill="#c0392b", outline="#000000")
            wr = int(9 * s)
            for wx, wy in [(-hw*0.75, -hh*0.7), (hw*0.75, -hh*0.7),
                          (-hw*0.75, hh*0.65), (hw*0.75, hh*0.65)]:
                wheel_x, wheel_y = rp(wx, wy)
                draw.ellipse([wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr], fill="#000000")
        else:  # car
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
            trunk = [rp(-hw*0.85, hh*0.5), rp(hw*0.85, hh*0.5),
                    rp(hw*0.85, hh*0.85), rp(-hw*0.85, hh*0.85)]
            draw.polygon(trunk, fill="#2980b9", outline="#000000")
            wr = int(8 * s)
            for wx, wy in [(-hw*0.75, -hh*0.6), (hw*0.75, -hh*0.6),
                          (-hw*0.75, hh*0.6), (hw*0.75, hh*0.6)]:
                wheel_x, wheel_y = rp(wx, wy)
                draw.ellipse([wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr], fill="#000000")

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
        return (self.x-hw-30, self.y-hh-30, self.x+hw+30, self.y+hh+30)

class LegacyRoad(DiagramObject):
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


# ============================================================================
# ROAD CLASSES (8 TYPES: 4 Basic + 4 NEW Intersections)
# ============================================================================


class Road(DiagramObject):
    """Road segments: 2-lane / 4-lane, straight / curved.

    Tool palette uses ids like:
      - 2lane_straight, 2lane_curved
      - 4lane_straight, 4lane_curved
    """

    def __init__(self, x, y, road_type="2lane_straight"):
        super().__init__(x, y)
        self.road_type = road_type
        self.base_width = 80 if "2lane" in road_type else 160
        self.base_height = 200

    def draw(self, canvas):
        w = self.base_width * self.scale * self.width_scale
        h = self.base_height * self.scale * self.height_scale
        angle = math.radians(self.rotation)
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        def rp(px, py):
            return (px * cos_a - py * sin_a + self.x, px * sin_a + py * cos_a + self.y)

        hw, hh = w / 2, h / 2
        lw = 3 if self.selected else 2

        if "curved" in self.road_type:
            self._draw_curved(canvas, rp, hw, hh, lw)
        else:
            self._draw_straight(canvas, rp, hw, hh, lw)

    def _draw_straight(self, canvas, rp, hw, hh, lw):
        road = [rp(-hw, -hh), rp(hw, -hh), rp(hw, hh), rp(-hw, hh)]
        canvas.create_polygon(road, fill="#4a4a4a", outline="#000000", width=lw, tags="object")

        if "4lane" in self.road_type:
            # lane separators
            canvas.create_line(*rp(-hw / 2, -hh), *rp(-hw / 2, hh), fill="#ffff00", width=int(lw * 1.5), tags="object")
            canvas.create_line(*rp(hw / 2, -hh), *rp(hw / 2, hh), fill="#ffff00", width=int(lw * 1.5), tags="object")
            # median double yellow
            canvas.create_line(*rp(-2, -hh), *rp(-2, hh), fill="#ffff00", width=int(lw * 2), tags="object")
            canvas.create_line(*rp(2, -hh), *rp(2, hh), fill="#ffff00", width=int(lw * 2), tags="object")
        else:
            for i in range(-5, 6):
                y1, y2 = i * hh / 5 - hh / 10, i * hh / 5 + hh / 10
                canvas.create_line(*rp(0, y1), *rp(0, y2), fill="#ffff00", width=int(lw * 1.2), tags="object")

        canvas.create_line(*rp(-hw, -hh), *rp(-hw, hh), fill="#ffffff", width=lw, tags="object")
        canvas.create_line(*rp(hw, -hh), *rp(hw, hh), fill="#ffffff", width=lw, tags="object")

    def _draw_curved(self, canvas, rp, hw, hh, lw):
        curve = self.curve_amount
        num_points = 30
        left_points = []
        right_points = []

        for i in range(num_points + 1):
            t = i / num_points
            y = (t - 0.5) * hh * 2
            # quadratic bezier bump, peak at t=0.5
            x_offset = curve * hw * 4 * t * (1 - t)
            left_points.append(rp(-hw + x_offset, y))
            right_points.append(rp(hw + x_offset, y))

        all_points = left_points + list(reversed(right_points))
        canvas.create_polygon(all_points, fill="#4a4a4a", outline="#000000", width=lw, tags="object")

        if "4lane" in self.road_type:
            center_points = []
            for i in range(num_points + 1):
                t = i / num_points
                y = (t - 0.5) * hh * 2
                x_offset = curve * hw * 4 * t * (1 - t)
                center_points.append(rp(x_offset, y))
            for i in range(len(center_points) - 1):
                canvas.create_line(center_points[i][0], center_points[i][1],
                                   center_points[i + 1][0], center_points[i + 1][1],
                                   fill="#ffff00", width=int(lw * 1.5), tags="object")
        else:
            for i in range(0, num_points, 3):
                if i + 1 >= num_points:
                    continue
                t1 = i / num_points
                t2 = (i + 1) / num_points
                y1 = (t1 - 0.5) * hh * 2
                y2 = (t2 - 0.5) * hh * 2
                x1 = curve * hw * 4 * t1 * (1 - t1)
                x2 = curve * hw * 4 * t2 * (1 - t2)
                canvas.create_line(*rp(x1, y1), *rp(x2, y2), fill="#ffff00", width=int(lw * 1.2), tags="object")

    def draw_to_pil(self, draw, offset_x=0, offset_y=0):
        w = self.base_width * self.scale * self.width_scale
        h = self.base_height * self.scale * self.height_scale
        angle = math.radians(self.rotation)
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        def rp(px, py):
            return (
                int(px * cos_a - py * sin_a + self.x + offset_x),
                int(px * sin_a + py * cos_a + self.y + offset_y),
            )

        hw, hh = w / 2, h / 2

        if "curved" in self.road_type:
            curve = self.curve_amount
            num_points = 30
            left_points = []
            right_points = []
            for i in range(num_points + 1):
                t = i / num_points
                y = (t - 0.5) * hh * 2
                x_offset = curve * hw * 4 * t * (1 - t)
                left_points.append(rp(-hw + x_offset, y))
                right_points.append(rp(hw + x_offset, y))
            draw.polygon(left_points + list(reversed(right_points)), fill="#4a4a4a", outline="#000000")

            if "4lane" in self.road_type:
                center_points = []
                for i in range(num_points + 1):
                    t = i / num_points
                    y = (t - 0.5) * hh * 2
                    x_offset = curve * hw * 4 * t * (1 - t)
                    center_points.append(rp(x_offset, y))
                for i in range(len(center_points) - 1):
                    draw.line([center_points[i], center_points[i + 1]], fill="#ffff00", width=2)
            else:
                for i in range(0, num_points, 3):
                    if i + 1 >= num_points:
                        continue
                    t1 = i / num_points
                    t2 = (i + 1) / num_points
                    y1 = (t1 - 0.5) * hh * 2
                    y2 = (t2 - 0.5) * hh * 2
                    x1 = curve * hw * 4 * t1 * (1 - t1)
                    x2 = curve * hw * 4 * t2 * (1 - t2)
                    draw.line([rp(x1, y1), rp(x2, y2)], fill="#ffff00", width=2)
        else:
            road = [rp(-hw, -hh), rp(hw, -hh), rp(hw, hh), rp(-hw, hh)]
            draw.polygon(road, fill="#4a4a4a", outline="#000000")
            if "4lane" in self.road_type:
                draw.line([rp(-hw / 2, -hh), rp(-hw / 2, hh)], fill="#ffff00", width=2)
                draw.line([rp(hw / 2, -hh), rp(hw / 2, hh)], fill="#ffff00", width=2)
                draw.line([rp(-2, -hh), rp(-2, hh)], fill="#ffff00", width=3)
                draw.line([rp(2, -hh), rp(2, hh)], fill="#ffff00", width=3)
            else:
                for i in range(-5, 6):
                    y1, y2 = i * hh / 5 - hh / 10, i * hh / 5 + hh / 10
                    draw.line([rp(0, y1), rp(0, y2)], fill="#ffff00", width=2)

        # edge lines (always)
        draw.line([rp(-hw, -hh), rp(-hw, hh)], fill="#ffffff", width=2)
        draw.line([rp(hw, -hh), rp(hw, hh)], fill="#ffffff", width=2)

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
        return (self.x - hw - 20, self.y - hh - 20, self.x + hw + 20, self.y + hh + 20)



class Intersection(DiagramObject):
    """Intersection types: t_2lane, t_4lane, 4way_2lane, 4way_4lane."""

    def __init__(self, x, y, intersection_type="t_2lane"):
        super().__init__(x, y)
        self.intersection_type = intersection_type
        self.base_size = 100 if "2lane" in intersection_type else 200

    def draw(self, canvas):
        size = self.base_size * self.scale
        angle = math.radians(self.rotation)
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        def rp(px, py):
            return (px * cos_a - py * sin_a + self.x, px * sin_a + py * cos_a + self.y)

        lw = 3 if self.selected else 2
        if self.intersection_type.startswith("t_"):
            self._draw_t_intersection(canvas, rp, size, lw)
        else:
            self._draw_4way_intersection(canvas, rp, size, lw)

    def _draw_t_intersection(self, canvas, rp, size, lw):
        is_4lane = "4lane" in self.intersection_type
        road_width = size if is_4lane else size / 2

        vert = [rp(-road_width / 2, -size), rp(road_width / 2, -size),
                rp(road_width / 2, size), rp(-road_width / 2, size)]
        canvas.create_polygon(vert, fill="#4a4a4a", outline="#000000", width=lw, tags="object")

        horiz = [rp(0, -road_width / 2), rp(size, -road_width / 2),
                 rp(size, road_width / 2), rp(0, road_width / 2)]
        canvas.create_polygon(horiz, fill="#4a4a4a", outline="#000000", width=lw, tags="object")

        if is_4lane:
            canvas.create_line(*rp(0, -size), *rp(0, size), fill="#ffff00", width=int(lw * 1.5), tags="object")
            canvas.create_line(*rp(0, 0), *rp(size, 0), fill="#ffff00", width=int(lw * 1.5), tags="object")
        else:
            for i in range(-4, 5):
                y1, y2 = i * size / 8 - size / 16, i * size / 8 + size / 16
                if abs(y1) < size:
                    canvas.create_line(*rp(0, y1), *rp(0, y2),
                                       fill="#ffff00", width=int(lw * 1.2), tags="object")
            for i in range(0, 4):
                x1, x2 = i * size / 8, i * size / 8 + size / 16
                canvas.create_line(*rp(x1, 0), *rp(x2, 0),
                                   fill="#ffff00", width=int(lw * 1.2), tags="object")

    def _draw_4way_intersection(self, canvas, rp, size, lw):
        is_4lane = "4lane" in self.intersection_type
        road_width = size if is_4lane else size / 2

        vert = [rp(-road_width / 2, -size), rp(road_width / 2, -size),
                rp(road_width / 2, size), rp(-road_width / 2, size)]
        canvas.create_polygon(vert, fill="#4a4a4a", outline="#000000", width=lw, tags="object")

        horiz = [rp(-size, -road_width / 2), rp(size, -road_width / 2),
                 rp(size, road_width / 2), rp(-size, road_width / 2)]
        canvas.create_polygon(horiz, fill="#4a4a4a", outline="#000000", width=lw, tags="object")

        if is_4lane:
            canvas.create_line(*rp(-road_width / 4, -size), *rp(-road_width / 4, size),
                               fill="#ffff00", width=int(lw * 1.5), tags="object")
            canvas.create_line(*rp(road_width / 4, -size), *rp(road_width / 4, size),
                               fill="#ffff00", width=int(lw * 1.5), tags="object")
            canvas.create_line(*rp(-size, -road_width / 4), *rp(size, -road_width / 4),
                               fill="#ffff00", width=int(lw * 1.5), tags="object")
            canvas.create_line(*rp(-size, road_width / 4), *rp(size, road_width / 4),
                               fill="#ffff00", width=int(lw * 1.5), tags="object")
        else:
            for i in range(-4, 5):
                y1, y2 = i * size / 8 - size / 16, i * size / 8 + size / 16
                if abs(y1) < size:
                    canvas.create_line(*rp(0, y1), *rp(0, y2),
                                       fill="#ffff00", width=int(lw * 1.2), tags="object")
            for i in range(-4, 5):
                x1, x2 = i * size / 8 - size / 16, i * size / 8 + size / 16
                if abs(x1) < size:
                    canvas.create_line(*rp(x1, 0), *rp(x2, 0),
                                       fill="#ffff00", width=int(lw * 1.2), tags="object")

    def draw_to_pil(self, draw, offset_x=0, offset_y=0):
        size = self.base_size * self.scale
        angle = math.radians(self.rotation)
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        def rp(px, py):
            return (
                int(px * cos_a - py * sin_a + self.x + offset_x),
                int(px * sin_a + py * cos_a + self.y + offset_y),
            )

        is_4lane = "4lane" in self.intersection_type
        road_width = size if is_4lane else size / 2

        vert = [rp(-road_width / 2, -size), rp(road_width / 2, -size),
                rp(road_width / 2, size), rp(-road_width / 2, size)]
        draw.polygon(vert, fill="#4a4a4a", outline="#000000")

        if self.intersection_type.startswith("t_"):
            horiz = [rp(0, -road_width / 2), rp(size, -road_width / 2),
                     rp(size, road_width / 2), rp(0, road_width / 2)]
        else:
            horiz = [rp(-size, -road_width / 2), rp(size, -road_width / 2),
                     rp(size, road_width / 2), rp(-size, road_width / 2)]
        draw.polygon(horiz, fill="#4a4a4a", outline="#000000")

        if is_4lane:
            draw.line([rp(0, -size), rp(0, size)], fill="#ffff00", width=2)
            if self.intersection_type.startswith("t_"):
                draw.line([rp(0, 0), rp(size, 0)], fill="#ffff00", width=2)
            else:
                draw.line([rp(-size, 0), rp(size, 0)], fill="#ffff00", width=2)

    def contains(self, x, y):
        dx, dy = x - self.x, y - self.y
        size = self.base_size * self.scale
        return abs(dx) < size and abs(dy) < size

    def get_bounds(self):
        size = self.base_size * self.scale
        return (self.x - size - 20, self.y - size - 20, self.x + size + 20, self.y + size + 20)


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
    """North Arrow - FIXED to be scalable and rotatable"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.base_size = 60

    def draw(self, canvas):
        size = self.base_size * self.scale
        angle = math.radians(self.rotation)
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        def rp(px, py):
            return (px * cos_a - py * sin_a + self.x, px * sin_a + py * cos_a + self.y)

        lw = 3 if self.selected else 2

        # Arrow shaft
        canvas.create_line(rp(0, size/2)[0], rp(0, size/2)[1],
                         rp(0, -size/2)[0], rp(0, -size/2)[1],
                         fill="#000000", width=int(lw*2), tags="object")

        # Arrow head
        arrow_head = [rp(0, -size/2), rp(-size/6, -size/3), rp(size/6, -size/3)]
        canvas.create_polygon(arrow_head, fill="#000000", outline="#000000", tags="object")

        # "N" label above arrow
        n_x, n_y = rp(0, -size/2 - 20)
        canvas.create_text(n_x, n_y, text="N", font=("Arial", int(16*self.scale), "bold"),
                         fill="#000000", tags="object")

    def draw_to_pil(self, draw, offset_x=0, offset_y=0):
        size = self.base_size * self.scale
        x, y = self.x + offset_x, self.y + offset_y

        # Arrow shaft
        draw.line([x, y+size/2, x, y-size/2], fill="#000000", width=3)

        # Arrow head
        draw.polygon([x, y-size/2, x-size/6, y-size/3, x+size/6, y-size/3], fill="#000000")

        # "N" label
        draw.text((x-5, y-size/2-25), "N", fill="#000000")

    def contains(self, x, y):
        size = self.base_size * self.scale
        return abs(x - self.x) < size/2 and abs(y - self.y) < size/2

    def get_bounds(self):
        size = self.base_size * self.scale
        return (self.x-size/2-10, self.y-size/2-30, self.x+size/2+10, self.y+size/2+10)
        
class Animal(DiagramObject):
    """Animal (Deer) symbol - FIXED to appear on diagram"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.base_width = 60
        self.base_height = 70

    def draw(self, canvas):
        w = self.base_width * self.scale * self.width_scale
        h = self.base_height * self.scale * self.height_scale
        angle = math.radians(self.rotation)
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        def rp(px, py):
            return (px * cos_a - py * sin_a + self.x, px * sin_a + py * cos_a + self.y)

        lw = 3 if self.selected else 2

        # Body (oval)
        body_points = []
        for i in range(20):
            angle_i = i * math.pi * 2 / 20
            px = math.cos(angle_i) * w/2 * 0.6
            py = math.sin(angle_i) * h/2 * 0.4
            body_points.append(rp(px, py))
        canvas.create_polygon(body_points, fill="#8b4513", outline="#000000", width=lw, tags="object")

        # Head (circle)
        head_x, head_y = rp(0, -h/3)
        canvas.create_oval(head_x-w/6, head_y-w/6, head_x+w/6, head_y+w/6,
                         fill="#8b4513", outline="#000000", width=lw, tags="object")

        # Antlers (V shapes)
        canvas.create_line(rp(-w/8, -h/3)[0], rp(-w/8, -h/3)[1],
                         rp(-w/4, -h/2)[0], rp(-w/4, -h/2)[1],
                         fill="#654321", width=int(lw*1.2), tags="object")
        canvas.create_line(rp(w/8, -h/3)[0], rp(w/8, -h/3)[1],
                         rp(w/4, -h/2)[0], rp(w/4, -h/2)[1],
                         fill="#654321", width=int(lw*1.2), tags="object")

        # Legs (4 lines)
        for leg_x in [-w/4, -w/6, w/6, w/4]:
            canvas.create_line(rp(leg_x, h/4)[0], rp(leg_x, h/4)[1],
                             rp(leg_x, h/2)[0], rp(leg_x, h/2)[1],
                             fill="#654321", width=int(lw*1.2), tags="object")

        # Tail
        canvas.create_line(rp(w/3, 0)[0], rp(w/3, 0)[1],
                         rp(w/2, -h/6)[0], rp(w/2, -h/6)[1],
                         fill="#654321", width=int(lw*1.2), tags="object")

    def draw_to_pil(self, draw, offset_x=0, offset_y=0):
        w = self.base_width * self.scale * self.width_scale
        h = self.base_height * self.scale * self.height_scale
        x, y = self.x + offset_x, self.y + offset_y

        # Body
        draw.ellipse([x-w/3, y-h/5, x+w/3, y+h/5], fill="#8b4513", outline="#000000")

        # Head
        draw.ellipse([x-w/6, y-h/3-w/6, x+w/6, y-h/3+w/6], fill="#8b4513", outline="#000000")

        # Antlers
        draw.line([x-w/8, y-h/3, x-w/4, y-h/2], fill="#654321", width=2)
        draw.line([x+w/8, y-h/3, x+w/4, y-h/2], fill="#654321", width=2)

        # Legs
        for leg_x in [-w/4, -w/6, w/6, w/4]:
            draw.line([x+leg_x, y+h/4, x+leg_x, y+h/2], fill="#654321", width=2)

    def contains(self, x, y):
        w = self.base_width * self.scale * self.width_scale
        h = self.base_height * self.scale * self.height_scale
        return abs(x - self.x) < w/2 and abs(y - self.y) < h/2

    def get_bounds(self):
        w = self.base_width * self.scale * self.width_scale
        h = self.base_height * self.scale * self.height_scale
        return (self.x-w/2-10, self.y-h/2-10, self.x+w/2+10, self.y+h/2+10)


# ============================================================================
# ARROWS / IMPACT / MEASUREMENT / SKID MARKS
# ============================================================================

class Arrow(DiagramObject):
    """Multi-purpose annotation symbol.

    Supported arrow_type values:
      - "straight": Single-direction arrow
      - "curved": Curved arrow (uses curve_amount)
      - "skid": Skid marks (uses curve_amount)
      - "impact": Impact point marker
      - "measure": Measurement line (double arrow)
    """

    def __init__(self, x: float, y: float, arrow_type: str = "straight"):
        super().__init__(x, y)
        self.arrow_type = arrow_type

    @property
    def supports_curve(self) -> bool:
        return self.arrow_type in {"curved", "skid"}

    def draw(self, canvas: tk.Canvas):
        lw = 3 if self.selected else 2
        if self.arrow_type == "impact":
            self._draw_impact_tk(canvas, lw)
        elif self.arrow_type == "measure":
            self._draw_measure_tk(canvas, lw)
        elif self.arrow_type == "skid":
            self._draw_skid_tk(canvas, lw)
        elif self.arrow_type == "curved":
            self._draw_curved_tk(canvas, lw)
        else:
            self._draw_straight_tk(canvas, lw)

    def draw_to_pil(self, draw: ImageDraw.ImageDraw, offset_x: float = 0, offset_y: float = 0):
        lw = 3
        if self.arrow_type == "impact":
            self._draw_impact_pil(draw, offset_x, offset_y, lw)
        elif self.arrow_type == "measure":
            self._draw_measure_pil(draw, offset_x, offset_y, lw)
        elif self.arrow_type == "skid":
            self._draw_skid_pil(draw, offset_x, offset_y, lw)
        elif self.arrow_type == "curved":
            self._draw_curved_pil(draw, offset_x, offset_y, lw)
        else:
            self._draw_straight_pil(draw, offset_x, offset_y, lw)

    # ---------------- Geometry ----------------

    def _poly_bounds(self, pts: list[tuple[float, float]]) -> tuple[float, float, float, float]:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return (min(xs), min(ys), max(xs), max(ys))

    def get_bounds(self):
        if self.arrow_type == "impact":
            r = 18 * self.scale * max(self.width_scale, self.height_scale)
            return (self.x - r, self.y - r, self.x + r, self.y + r)

        pts = self._path_points()
        minx, miny, maxx, maxy = self._poly_bounds(pts)
        pad = 14 * self.scale
        return (minx - pad, miny - pad, maxx + pad, maxy + pad)

    def contains(self, x, y):
        minx, miny, maxx, maxy = self.get_bounds()
        if not (minx <= x <= maxx and miny <= y <= maxy):
            return False
        # coarse hit-test: near polyline or inside impact circle
        if self.arrow_type == "impact":
            r = 18 * self.scale * max(self.width_scale, self.height_scale)
            return (x - self.x) ** 2 + (y - self.y) ** 2 <= r ** 2
        pts = self._path_points()
        return self._near_polyline(x, y, pts, tol=10 * self.scale)

    def _near_polyline(self, x: float, y: float, pts: list[tuple[float, float]], tol: float) -> bool:
        tol2 = tol * tol
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            if self._dist2_point_segment(x, y, x1, y1, x2, y2) <= tol2:
                return True
        return False

    @staticmethod
    def _dist2_point_segment(px, py, x1, y1, x2, y2):
        vx, vy = x2 - x1, y2 - y1
        wx, wy = px - x1, py - y1
        c1 = vx * wx + vy * wy
        if c1 <= 0:
            return (px - x1) ** 2 + (py - y1) ** 2
        c2 = vx * vx + vy * vy
        if c2 <= c1:
            return (px - x2) ** 2 + (py - y2) ** 2
        b = c1 / c2
        bx, by = x1 + b * vx, y1 + b * vy
        return (px - bx) ** 2 + (py - by) ** 2

    def _path_points(self) -> list[tuple[float, float]]:
        """Return world points for the primary path polyline."""
        L = 140.0
        if self.arrow_type == "measure":
            # measurement: straight line
            local = [(-L / 2, 0), (L / 2, 0)]
        else:
            # vertical by default
            if self.arrow_type in {"curved", "skid"}:
                local = []
                n = 32
                bend = self.curve_amount * (L * 0.18)
                for i in range(n + 1):
                    t = i / n
                    y = -L / 2 + t * L
                    x = bend * 4 * t * (1 - t)
                    local.append((x, y))
            else:
                local = [(0, -L / 2), (0, L / 2)]
        return [self._tp(lx, ly) for lx, ly in local]

    def _arrow_head(self, tip: tuple[float, float], prev: tuple[float, float], size: float) -> list[tuple[float, float]]:
        tx, ty = tip
        px, py = prev
        ang = math.atan2(ty - py, tx - px)
        a1 = ang + math.radians(150)
        a2 = ang - math.radians(150)
        return [(tx, ty), (tx + math.cos(a1) * size, ty + math.sin(a1) * size), (tx + math.cos(a2) * size, ty + math.sin(a2) * size)]

    # ---------------- Draw: straight ----------------

    def _draw_straight_tk(self, canvas: tk.Canvas, lw: int):
        pts = self._path_points()
        canvas.create_line(*pts[0], *pts[-1], fill="#2c3e50", width=lw, tags="object")
        head = self._arrow_head(pts[-1], pts[-2], size=18 * self.scale)
        canvas.create_polygon(head, fill="#2c3e50", outline="#2c3e50", tags="object")

    def _draw_straight_pil(self, draw: ImageDraw.ImageDraw, ox: float, oy: float, lw: int):
        pts = self._path_points()
        p0 = (pts[0][0] - ox, pts[0][1] - oy)
        p1 = (pts[-1][0] - ox, pts[-1][1] - oy)
        draw.line([p0, p1], fill=(44, 62, 80), width=lw)
        head = self._arrow_head(pts[-1], pts[-2], size=18 * self.scale)
        head2 = [(x - ox, y - oy) for x, y in head]
        draw.polygon(head2, fill=(44, 62, 80), outline=(44, 62, 80))

    # ---------------- Draw: curved ----------------

    def _draw_curved_tk(self, canvas: tk.Canvas, lw: int):
        pts = self._path_points()
        for i in range(len(pts) - 1):
            canvas.create_line(*pts[i], *pts[i + 1], fill="#2c3e50", width=lw, smooth=True, tags="object")
        head = self._arrow_head(pts[-1], pts[-2], size=18 * self.scale)
        canvas.create_polygon(head, fill="#2c3e50", outline="#2c3e50", tags="object")

    def _draw_curved_pil(self, draw: ImageDraw.ImageDraw, ox: float, oy: float, lw: int):
        pts = self._path_points()
        pts2 = [(x - ox, y - oy) for x, y in pts]
        draw.line(pts2, fill=(44, 62, 80), width=lw, joint="curve")
        head = self._arrow_head(pts[-1], pts[-2], size=18 * self.scale)
        head2 = [(x - ox, y - oy) for x, y in head]
        draw.polygon(head2, fill=(44, 62, 80), outline=(44, 62, 80))

    # ---------------- Draw: skid ----------------

    def _draw_skid_tk(self, canvas: tk.Canvas, lw: int):
        pts = self._path_points()
        # two parallel tracks in local-x, implemented by offsetting in world using local normal
        offset = 10 * self.scale * self.width_scale
        # approximate normal using last segment orientation
        for side in (-1, 1):
            track = []
            for i in range(len(pts)):
                if i == 0:
                    dx, dy = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
                else:
                    dx, dy = pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
                l = math.hypot(dx, dy) or 1.0
                nx, ny = -dy / l, dx / l
                track.append((pts[i][0] + nx * offset * side, pts[i][1] + ny * offset * side))
            # dashed effect: draw short segments
            for i in range(0, len(track) - 1, 2):
                canvas.create_line(*track[i], *track[i + 1], fill="#1f1f1f", width=max(1, lw - 1), tags="object")

    def _draw_skid_pil(self, draw: ImageDraw.ImageDraw, ox: float, oy: float, lw: int):
        pts = self._path_points()
        offset = 10 * self.scale * self.width_scale
        for side in (-1, 1):
            track = []
            for i in range(len(pts)):
                if i == 0:
                    dx, dy = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
                else:
                    dx, dy = pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
                l = math.hypot(dx, dy) or 1.0
                nx, ny = -dy / l, dx / l
                track.append((pts[i][0] + nx * offset * side, pts[i][1] + ny * offset * side))
            for i in range(0, len(track) - 1, 2):
                p0 = (track[i][0] - ox, track[i][1] - oy)
                p1 = (track[i + 1][0] - ox, track[i + 1][1] - oy)
                draw.line([p0, p1], fill=(31, 31, 31), width=max(1, lw - 1))

    # ---------------- Draw: impact ----------------

    def _draw_impact_tk(self, canvas: tk.Canvas, lw: int):
        r = 18 * self.scale * max(self.width_scale, self.height_scale)
        p1 = self._tp(-r, -r)
        p2 = self._tp(r, r)
        p3 = self._tp(-r, r)
        p4 = self._tp(r, -r)
        canvas.create_oval(self.x - r, self.y - r, self.x + r, self.y + r, outline="#c0392b", width=lw, tags="object")
        canvas.create_line(*p1, *p2, fill="#c0392b", width=lw, tags="object")
        canvas.create_line(*p3, *p4, fill="#c0392b", width=lw, tags="object")

    def _draw_impact_pil(self, draw: ImageDraw.ImageDraw, ox: float, oy: float, lw: int):
        r = 18 * self.scale * max(self.width_scale, self.height_scale)
        draw.ellipse([self.x - r - ox, self.y - r - oy, self.x + r - ox, self.y + r - oy], outline=(192, 57, 43), width=lw)
        p1 = self._tp(-r, -r)
        p2 = self._tp(r, r)
        p3 = self._tp(-r, r)
        p4 = self._tp(r, -r)
        draw.line([(p1[0]-ox, p1[1]-oy), (p2[0]-ox, p2[1]-oy)], fill=(192, 57, 43), width=lw)
        draw.line([(p3[0]-ox, p3[1]-oy), (p4[0]-ox, p4[1]-oy)], fill=(192, 57, 43), width=lw)

    # ---------------- Draw: measurement ----------------

    def _draw_measure_tk(self, canvas: tk.Canvas, lw: int):
        pts = self._path_points()
        canvas.create_line(*pts[0], *pts[1], fill="#16a085", width=lw, tags="object")
        head1 = self._arrow_head(pts[0], pts[1], size=14 * self.scale)
        head2 = self._arrow_head(pts[1], pts[0], size=14 * self.scale)
        canvas.create_polygon(head1, fill="#16a085", outline="#16a085", tags="object")
        canvas.create_polygon(head2, fill="#16a085", outline="#16a085", tags="object")

    def _draw_measure_pil(self, draw: ImageDraw.ImageDraw, ox: float, oy: float, lw: int):
        pts = self._path_points()
        p0 = (pts[0][0] - ox, pts[0][1] - oy)
        p1 = (pts[1][0] - ox, pts[1][1] - oy)
        draw.line([p0, p1], fill=(22, 160, 133), width=lw)
        head1 = [(x - ox, y - oy) for x, y in self._arrow_head(pts[0], pts[1], size=14 * self.scale)]
        head2 = [(x - ox, y - oy) for x, y in self._arrow_head(pts[1], pts[0], size=14 * self.scale)]
        draw.polygon(head1, fill=(22, 160, 133), outline=(22, 160, 133))
        draw.polygon(head2, fill=(22, 160, 133), outline=(22, 160, 133))


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

class AccidentReconstructionApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Accident Reconstruction Tool v{AutoUpdater.CURRENT_VERSION}")
        self.root.geometry("1400x900")

        self.objects = []
        self.selected_object = None
        self.drag_data = {"x": 0, "y": 0, "item": None}

        self.setup_ui()
        self.setup_canvas()
        self.setup_bindings()

        # Check for updates on startup
        self.root.after(1000, lambda: check_for_updates_on_startup(self.root))

    def setup_ui(self):
        """Setup the user interface"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_diagram)
        file_menu.add_command(label="Export PDF", command=self.export_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Check for Updates", command=lambda: manual_update_check(self.root))
        help_menu.add_command(label="About", command=self.show_about)

        # Main container
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left panel (tools)
        left_panel = tk.Frame(main_container, width=300, bg="#ecf0f1")
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)

        # Scrollable tool panel
        canvas_scroll = tk.Canvas(left_panel, bg="#ecf0f1", highlightthickness=0)
        scrollbar = tk.Scrollbar(left_panel, orient="vertical", command=canvas_scroll.yview)
        scrollable_frame = tk.Frame(canvas_scroll, bg="#ecf0f1")

        scrollable_frame.bind("<Configure>",
                             lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))

        canvas_scroll.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)

        canvas_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tool sections
        self.create_tool_sections(scrollable_frame)

        # Right panel (canvas)
        right_panel = tk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Canvas frame
        self.canvas_frame = tk.Frame(right_panel)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_tool_sections(self, parent):
        # Vehicles - NO EMOJI
        vehicles_section = CollapsibleSection(parent, "Vehicles (5)")
        vehicles_section.pack(fill=tk.X, padx=5, pady=2)
        vehicles_frame = vehicles_section.get_content_frame()

        tk.Button(vehicles_frame, text="Sedan", command=lambda: self.add_object("car"),
                bg="#3498db", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, padx=5, pady=2)
        tk.Button(vehicles_frame, text="Pickup Truck", command=lambda: self.add_object("truck"),
                bg="#e74c3c", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, padx=5, pady=2)
        tk.Button(vehicles_frame, text="18-Wheeler", command=lambda: self.add_object("semi"),
                bg="#f39c12", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, padx=5, pady=2)
        tk.Button(vehicles_frame, text="Motorcycle", command=lambda: self.add_object("motorcycle"),
                bg="#7f8c8d", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, padx=5, pady=2)
        tk.Button(vehicles_frame, text="ATV (NEW)", command=lambda: self.add_object("atv"),
                bg="#8b4513", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, padx=5, pady=2)

        # Roads & Intersections - NO EMOJI
        roads_section = CollapsibleSection(parent, "Roads & Intersections (8)")
        roads_section.pack(fill=tk.X, padx=5, pady=2)
        roads_frame = roads_section.get_content_frame()

        tk.Label(roads_frame, text="Basic Roads:", bg="#ecf0f1", font=("Arial", 9, "bold")).pack(pady=2)
        tk.Button(roads_frame, text="2-Lane Straight", command=lambda: self.add_object("2lane_straight"),
                bg="#4a4a4a", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)
        tk.Button(roads_frame, text="2-Lane Curved", command=lambda: self.add_object("2lane_curved"),
                bg="#4a4a4a", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)
        tk.Button(roads_frame, text="4-Lane Straight", command=lambda: self.add_object("4lane_straight"),
                bg="#4a4a4a", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)
        tk.Button(roads_frame, text="4-Lane Curved", command=lambda: self.add_object("4lane_curved"),
                bg="#4a4a4a", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)

        tk.Label(roads_frame, text="Intersections (NEW):", bg="#ecf0f1", font=("Arial", 9, "bold")).pack(pady=2)
        tk.Button(roads_frame, text="T-Intersection 2-Lane", command=lambda: self.add_object("t_2lane"),
                bg="#2c3e50", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)
        tk.Button(roads_frame, text="T-Intersection 4-Lane", command=lambda: self.add_object("t_4lane"),
                bg="#2c3e50", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)
        tk.Button(roads_frame, text="4-Way 2-Lane", command=lambda: self.add_object("4way_2lane"),
                bg="#2c3e50", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)
        tk.Button(roads_frame, text="4-Way 4-Lane", command=lambda: self.add_object("4way_4lane"),
                bg="#2c3e50", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)

        # Arrows - NO EMOJI
        arrows_section = CollapsibleSection(parent, "Arrows (5)")
        arrows_section.pack(fill=tk.X, padx=5, pady=2)
        arrows_frame = arrows_section.get_content_frame()

        tk.Button(arrows_frame, text="Straight Arrow", command=lambda: self.add_object("arrow_straight"),
                bg="#c0392b", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)
        tk.Button(arrows_frame, text="Left Turn", command=lambda: self.add_object("arrow_left"),
                bg="#c0392b", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)
        tk.Button(arrows_frame, text="Right Turn", command=lambda: self.add_object("arrow_right"),
                bg="#c0392b", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)
        tk.Button(arrows_frame, text="Left Curve", command=lambda: self.add_object("arrow_left_curve"),
                bg="#c0392b", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)
        tk.Button(arrows_frame, text="Right Curve", command=lambda: self.add_object("arrow_right_curve"),
                bg="#c0392b", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)

        # Symbols - NO EMOJI
        symbols_section = CollapsibleSection(parent, "Symbols (5)")
        symbols_section.pack(fill=tk.X, padx=5, pady=2)
        symbols_frame = symbols_section.get_content_frame()

        tk.Button(symbols_frame, text="Tree", command=lambda: self.add_object("tree"),
                bg="#27ae60", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)
        tk.Button(symbols_frame, text="Pedestrian", command=lambda: self.add_object("pedestrian"),
                bg="#f39c12", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)
        tk.Button(symbols_frame, text="Text Label", command=lambda: self.add_object("text"),
                bg="#34495e", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)
        tk.Button(symbols_frame, text="North Arrow (NEW)", command=lambda: self.add_object("north_arrow"),
                bg="#2980b9", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)
        tk.Button(symbols_frame, text="Animal Deer (NEW)", command=lambda: self.add_object("animal"),
                bg="#8b4513", fg="white", font=("Arial", 9)).pack(fill=tk.X, padx=5, pady=1)

        # Controls - NO EMOJI
        controls_section = CollapsibleSection(parent, "Controls")
        controls_section.pack(fill=tk.X, padx=5, pady=2)
        controls_frame = controls_section.get_content_frame()

        tk.Button(controls_frame, text="Delete Selected", command=self.delete_selected,
                bg="#e74c3c", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, padx=5, pady=2)
        tk.Button(controls_frame, text="Clear All", command=self.clear_all,
                bg="#c0392b", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, padx=5, pady=2)

    def setup_canvas(self):
        """Setup the drawing canvas"""
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Grid
        for i in range(0, 2000, 50):
            self.canvas.create_line(i, 0, i, 2000, fill="#e0e0e0", tags="grid")
            self.canvas.create_line(0, i, 2000, i, fill="#e0e0e0", tags="grid")

    def setup_bindings(self):
        """Setup event bindings"""
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.root.bind("<Delete>", lambda e: self.delete_selected())
        self.root.bind("<r>", lambda e: self.rotate_selected())
        self.root.bind("<R>", lambda e: self.rotate_selected(-15))
        self.root.bind("<plus>", lambda e: self.scale_selected_up())
        self.root.bind("<minus>", lambda e: self.scale_selected_down())

    def add_object(self, obj_type):
        """Add object to canvas"""
        x, y = 400, 400

        if obj_type in ["car", "truck", "semi", "motorcycle", "atv"]:
            obj = Vehicle(x, y, obj_type)
        elif obj_type.startswith("2lane") or obj_type.startswith("4lane"):
            obj = Road(x, y, obj_type)
        elif obj_type.startswith("t_") or obj_type.startswith("4way_"):
            obj = Intersection(x, y, obj_type)
        elif obj_type.startswith("arrow_"):
            arrow_type = obj_type.replace("arrow_", "")
            obj = Arrow(x, y, arrow_type)
        elif obj_type == "tree":
            obj = Tree(x, y)
        elif obj_type == "pedestrian":
            obj = Pedestrian(x, y)
        elif obj_type == "text":
            text = simpledialog.askstring("Text Label", "Enter text:", parent=self.root)
            if not text:
                return
            obj = TextLabel(x, y, text)
        elif obj_type == "north_arrow":
            obj = NorthArrow(x, y)
        elif obj_type == "animal":  # CRITICAL: Add this case
            obj = Animal(x, y)
        else:
            return

        self.objects.append(obj)
        self.redraw()


    def on_canvas_click(self, event):
        """Handle canvas click"""
        x, y = event.x, event.y

        # Deselect all
        for obj in self.objects:
            obj.selected = False

        # Find clicked object
        for obj in reversed(self.objects):
            if obj.contains(x, y):
                obj.selected = True
                self.selected_object = obj
                self.drag_data = {"x": x, "y": y, "item": obj}
                self.redraw()
                return

        self.selected_object = None
        self.redraw()

    def on_canvas_drag(self, event):
        """Handle canvas drag"""
        if self.drag_data["item"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.drag_data["item"].move(dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.redraw()

    def on_canvas_release(self, event):
        """Handle canvas release"""
        self.drag_data = {"x": 0, "y": 0, "item": None}

    def rotate_selected(self, angle=15):
        """Rotate selected object"""
        if self.selected_object:
            self.selected_object.rotate(angle)
            self.redraw()

    def scale_selected_up(self):
        """Scale up selected object"""
        if self.selected_object:
            self.selected_object.scale_up()
            self.redraw()

    def scale_selected_down(self):
        """Scale down selected object"""
        if self.selected_object:
            self.selected_object.scale_down()
            self.redraw()

    def delete_selected(self):
        """Delete selected object"""
        if self.selected_object:
            self.objects.remove(self.selected_object)
            self.selected_object = None
            self.redraw()

    def clear_all(self):
        """Clear all objects"""
        if messagebox.askyesno("Clear All", "Delete all objects?", parent=self.root):
            self.objects = []
            self.selected_object = None
            self.redraw()

    def new_diagram(self):
        """New diagram"""
        if messagebox.askyesno("New Diagram", "Clear current diagram?", parent=self.root):
            self.clear_all()

    def redraw(self):
        """Redraw canvas"""
        self.canvas.delete("object")
        for obj in self.objects:
            obj.draw(self.canvas)

    def export_pdf(self):
        """Export to PDF"""
        filename = filedialog.asksaveasfilename(defaultextension=".pdf",
                                               filetypes=[("PDF files", "*.pdf")],
                                               parent=self.root)
        if not filename:
            return

        try:
            # Create PDF
            c = pdf_canvas.Canvas(filename, pagesize=letter)
            width, height = letter

            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Accident Reconstruction Diagram")
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 70, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(50, height - 85, f"Version: {AutoUpdater.CURRENT_VERSION}")

            # Draw objects to PIL image
            img = Image.new('RGB', (800, 600), 'white')
            draw = ImageDraw.Draw(img)

            # Find bounds
            if self.objects:
                min_x = min(obj.x for obj in self.objects) - 100
                min_y = min(obj.y for obj in self.objects) - 100
                max_x = max(obj.x for obj in self.objects) + 100
                max_y = max(obj.y for obj in self.objects) + 100

                # Scale to fit
                scale_x = 700 / (max_x - min_x) if max_x > min_x else 1
                scale_y = 500 / (max_y - min_y) if max_y > min_y else 1
                scale = min(scale_x, scale_y, 1.0)

                offset_x = 50 - min_x * scale
                offset_y = 50 - min_y * scale

                # Draw objects
                for obj in self.objects:
                    obj.draw_to_pil(draw, offset_x, offset_y)

            # Add image to PDF
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            c.drawImage(ImageReader(img_buffer), 50, height - 700, width=700, height=500)

            c.save()
            messagebox.showinfo("Success", f"PDF saved: {filename}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}", parent=self.root)

    def show_about(self):
        """Show about dialog"""
        about_text = f"""Accident Reconstruction Tool
Version {AutoUpdater.CURRENT_VERSION}

Professional accident reconstruction software

Features:
â€¢ 5 Vehicle Types (Car, Truck, Semi, Motorcycle, ATV)
â€¢ 8 Road Types (4 Basic + 4 Intersections)
â€¢ 5 Arrow Types
â€¢ 5 Symbol Types (Tree, Pedestrian, Text, North Arrow, Animal)
â€¢ PDF Export
â€¢ Auto-Update

Author: Galaxy AI
Date: February 2026"""
        messagebox.showinfo("About", about_text, parent=self.root)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = AccidentReconstructionApp(root)
    root.mainloop()
