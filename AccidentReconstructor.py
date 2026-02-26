#!/usr/bin/env python3
"""
Accident Reconstruction Diagram Tool - COMPLETE VERSION WITH AUTO-UPDATE
=========================================================================
Professional accident reconstruction software with auto-update capability

Version: 2.0.0
Author: Galaxy AI
Date: February 2026
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import math
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import ImageReader
import io
from datetime import datetime
import urllib.request
import json
import tempfile
import shutil
import sys
import subprocess


# ============================================================================
# AUTO-UPDATE FUNCTIONALITY
# ============================================================================

class AutoUpdater:
    """Auto-update functionality"""

    # REPLACE WITH YOUR GITHUB INFO
    GITHUB_USER = "your-username"
    GITHUB_REPO = "accident-reconstructor"
    VERSION_FILE = "https://raw.githubusercontent.com/{user}/{repo}/main/version.json"
    DOWNLOAD_URL = "https://raw.githubusercontent.com/{user}/{repo}/main/AccidentReconstructor.py"

    CURRENT_VERSION = "2.0.0"

    @classmethod
    def check_for_updates(cls):
        try:
            version_url = cls.VERSION_FILE.format(user=cls.GITHUB_USER, repo=cls.GITHUB_REPO)
            with urllib.request.urlopen(version_url, timeout=5) as response:
                version_data = json.loads(response.read().decode())
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
            download_url = cls.DOWNLOAD_URL.format(user=cls.GITHUB_USER, repo=cls.GITHUB_REPO)
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py')
            temp_path = temp_file.name
            temp_file.close()

            def report_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    percent = min(100, (block_num * block_size / total_size) * 100)
                    progress_callback(percent)

            urllib.request.urlretrieve(download_url, temp_path, reporthook=report_progress)
            return temp_path
        except:
            return None

    @classmethod
    def apply_update(cls, new_file_path):
        try:
            current_file = sys.argv[0]
            backup_file = current_file + ".backup"
            shutil.copy2(current_file, backup_file)
            shutil.copy2(new_file_path, current_file)
            try:
                import os
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
        tk.Label(header, text="ðŸ”„ Update Available", font=("Arial", 16, "bold"),
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
                messagebox.showinfo("Update Complete",
                                   "Update installed!\n\nRestarting...",
                                   parent=self.dialog)
                python = sys.executable
                subprocess.Popen([python] + sys.argv)
                sys.exit(0)
            else:
                messagebox.showerror("Update Failed", "Failed to install update.",
                                    parent=self.dialog)
                self.dialog.destroy()
        else:
            messagebox.showerror("Download Failed", "Failed to download update.",
                                parent=self.dialog)
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
            messagebox.showinfo("No Updates",
                               f"You have the latest version ({AutoUpdater.CURRENT_VERSION}).",
                               parent=root)
    except Exception as e:
        messagebox.showerror("Update Check Failed", f"Failed: {e}", parent=root)


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
    def __init__(self, x, y, vehicle_type="car"):
        super().__init__(x, y)
        self.vehicle_type = vehicle_type
        sizes = {"car": (55, 100), "truck": (75, 130), "semi": (80, 200), "motorcycle": (30, 65)}
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

        shadow = [rp(-hw+3*s, -hh+3*s), rp(hw+3*s, -hh+3*s),
                 rp(hw+3*s, hh+3*s), rp(-hw+3*s, hh+3*s)]
        canvas.create_polygon(shadow, fill="#d0d0d0", outline="", tags="object")

        body = [rp(-hw, -hh), rp(hw, -hh), rp(hw, hh), rp(-hw, hh)]
        canvas.create_polygon(body, fill="white", outline=outline, width=lw, tags="object")

        wr = 7 * s
        positions = [(0, -hh+5*s), (0, hh-5*s)] if self.vehicle_type == "motorcycle" else                    [(-hw*0.65, -hh+20*s), (hw*0.65, -hh+20*s),
                    (-hw*0.65, hh-20*s), (hw*0.65, hh-20*s)]
        for wx, wy in positions:
            wheel_x, wheel_y = rp(wx, wy)
            canvas.create_oval(wheel_x-wr, wheel_y-wr, wheel_x+wr, wheel_y+wr,
                             fill="#000000", tags="object")

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


class Tree(DiagramObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.base_width, self.base_height = 40, 60

    def draw(self, canvas):
        s = self.scale
        tw, th = 8*s*self.width_scale, 25*s*self.height_scale
        canvas.create_rectangle(self.x-tw/2, self.y-th/2, self.x+tw/2, self.y+th/2,
                               fill="#a0a0a0", outline="#000000", tags="object")
        cr = 20 * s
        cy = self.y - th/2 - cr*0.7
        for oy in [0, -cr*0.3, cr*0.2]:
            for ox in [0, -cr*0.2, cr*0.2]:
                canvas.create_oval(self.x+ox-cr, cy+oy-cr, self.x+ox+cr, cy+oy+cr,
                                 fill="#d0d0d0", outline="#000000", tags="object")

    def contains(self, x, y):
        return abs(x - self.x) < 25*self.scale and abs(y - self.y) < 25*self.scale

    def get_bounds(self):
        r = 30 * self.scale
        return (self.x-r-20, self.y-r-20, self.x+r+20, self.y+r+20)


class TextLabel(DiagramObject):
    def __init__(self, x, y, text="Label"):
        super().__init__(x, y)
        self.text = text

    def draw(self, canvas):
        canvas.create_text(self.x, self.y, text=self.text,
                          font=("Arial", int(12*self.scale), "bold"),
                          fill="#000000", tags="object")

    def contains(self, x, y):
        return abs(x-self.x) < len(self.text)*7*self.scale and abs(y-self.y) < 15*self.scale

    def get_bounds(self):
        w, h = len(self.text)*7*self.scale, 15*self.scale
        return (self.x-w-30, self.y-h-30, self.x+w+30, self.y+h+30)


class ControlButton:
    def __init__(self, x, y, button_type, size=25):
        self.x, self.y, self.button_type, self.size = x, y, button_type, size
        self.canvas_items = []

    def draw(self, canvas):
        for item in self.canvas_items:
            canvas.delete(item)
        self.canvas_items = []
        colors = {"rotate_cw": "#3498db", "rotate_ccw": "#3498db", "scale_up": "#27ae60",
                 "scale_down": "#e67e22", "width_up": "#16a085", "width_down": "#d35400",
                 "height_up": "#8e44ad", "height_down": "#c0392b"}
        bg = colors.get(self.button_type, "#95a5a6")
        item = canvas.create_oval(self.x-self.size/2, self.y-self.size/2,
                                 self.x+self.size/2, self.y+self.size/2,
                                 fill=bg, outline="white", width=2, tags="control")
        self.canvas_items.append(item)
        icons = {"rotate_cw": "â†»", "rotate_ccw": "â†º", "scale_up": "+", "scale_down": "âˆ’",
                "width_up": "â†”", "width_down": "â†”", "height_up": "â†•", "height_down": "â†•"}
        item = canvas.create_text(self.x, self.y, text=icons.get(self.button_type, "?"),
                                 font=("Arial", 14, "bold"), fill="white", tags="control")
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
        self.root.geometry("1200x800")
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

        tool_frame = tk.Frame(self.root, width=220, bg="#ecf0f1", relief=tk.RAISED, bd=2)
        tool_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        tool_frame.pack_propagate(False)

        tk.Label(tool_frame, text="Accident Reconstruction", bg="#ecf0f1",
                font=("Arial", 11, "bold")).pack(pady=5)

        tk.Label(tool_frame, text="VEHICLES", bg="#ecf0f1", font=("Arial", 9, "bold")).pack(pady=5)
        for emoji, text, tool in [("ðŸš—", "Sedan", "car"), ("ðŸšš", "Pickup", "truck"),
                                  ("ðŸš›", "18-Wheeler", "semi"), ("ðŸï¸", "Motorcycle", "motorcycle")]:
            tk.Button(tool_frame, text=f"{emoji} {text}", command=lambda t=tool: self.set_tool(t),
                     width=22, height=2, bg="#2c3e50", fg="white").pack(pady=2)

        tk.Label(tool_frame, text="OTHER", bg="#ecf0f1", font=("Arial", 9, "bold")).pack(pady=5)
        tk.Button(tool_frame, text="ðŸŒ³ Tree", command=lambda: self.set_tool("tree"),
                 width=22, height=2, bg="#27ae60", fg="white").pack(pady=2)
        tk.Button(tool_frame, text="ðŸ“ Text", command=lambda: self.set_tool("text"),
                 width=22, height=2, bg="#8e44ad", fg="white").pack(pady=2)

        tk.Label(tool_frame, text="ACTIONS", bg="#ecf0f1", font=("Arial", 9, "bold")).pack(pady=5)
        tk.Button(tool_frame, text="ðŸ—‘ï¸ Delete", command=self.delete_selected,
                 bg="#c0392b", fg="white", width=22, height=2).pack(pady=2)
        tk.Button(tool_frame, text="ðŸ“„ Export PDF", command=self.export_pdf,
                 bg="#27ae60", fg="white", width=22, height=2).pack(pady=2)

        canvas_frame = tk.Frame(self.root, bg="#bdc3c7")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas = tk.Canvas(canvas_frame, bg="white", relief=tk.SUNKEN, bd=2)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.root.bind("<Delete>", lambda e: self.delete_selected())

        status_frame = tk.Frame(self.root, bg="#34495e")
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = tk.Label(status_frame, text="Ready | Click buttons to add objects",
                                     bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#ecf0f1")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def set_tool(self, tool):
        self.current_tool = tool
        self.status_label.config(text=f"Tool: {tool} - Click canvas to place")

    def create_control_buttons(self):
        self.control_buttons = []
        if not self.selected_object:
            return
        x1, y1, x2, y2 = self.selected_object.get_bounds()
        cx, cy = (x1+x2)/2, (y1+y2)/2
        self.control_buttons = [
            ControlButton(cx, y1-20, "rotate_ccw"),
            ControlButton(x2+20, cy-15, "width_up"),
            ControlButton(x2+20, cy+15, "scale_up"),
            ControlButton(cx+15, y2+20, "height_up"),
            ControlButton(cx-15, y2+20, "rotate_cw"),
            ControlButton(x1-20, cy+15, "scale_down"),
            ControlButton(x1-20, cy-15, "width_down"),
            ControlButton(cx, y1-50, "height_down")
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
        elif self.current_tool:
            self.add_object(event.x, event.y)
            self.current_tool = None
        else:
            if self.selected_object:
                self.selected_object.selected = False
                self.selected_object = None
                self.control_buttons = []
                self.redraw()

    def handle_control_button(self, button_type):
        if not self.selected_object:
            return
        actions = {
            "rotate_cw": lambda: self.selected_object.rotate(15),
            "rotate_ccw": lambda: self.selected_object.rotate(-15),
            "scale_up": lambda: self.selected_object.scale_up(),
            "scale_down": lambda: self.selected_object.scale_down(),
            "width_up": lambda: self.selected_object.width_up(),
            "width_down": lambda: self.selected_object.width_down(),
            "height_up": lambda: self.selected_object.height_up(),
            "height_down": lambda: self.selected_object.height_down()
        }
        if button_type in actions:
            actions[button_type]()
            self.create_control_buttons()
            self.redraw()

    def on_canvas_drag(self, event):
        if self.selected_object and self.drag_start:
            dx, dy = event.x - self.drag_start[0], event.y - self.drag_start[1]
            self.selected_object.move(dx, dy)
            self.drag_start = (event.x, event.y)
            self.create_control_buttons()
            self.redraw()

    def on_canvas_release(self, event):
        self.drag_start = None

    def add_object(self, x, y):
        obj = None
        if self.current_tool in ["car", "truck", "semi", "motorcycle"]:
            obj = Vehicle(x, y, self.current_tool)
        elif self.current_tool == "tree":
            obj = Tree(x, y)
        elif self.current_tool == "text":
            text = simpledialog.askstring("Text Label", "Enter text:")
            if text:
                obj = TextLabel(x, y, text)
        if obj:
            self.objects.append(obj)
            if self.selected_object:
                self.selected_object.selected = False
            self.selected_object = obj
            obj.selected = True
            self.create_control_buttons()
            self.redraw()

    def delete_selected(self):
        if self.selected_object:
            self.objects.remove(self.selected_object)
            self.selected_object = None
            self.control_buttons = []
            self.redraw()

    def redraw(self):
        self.canvas.delete("object")
        self.canvas.delete("control")
        for obj in self.objects:
            obj.draw(self.canvas)
        self.draw_control_buttons()

    def export_pdf(self):
        filename = filedialog.asksaveasfilename(defaultextension=".pdf",
                                               filetypes=[("PDF files", "*.pdf")])
        if filename:
            try:
                c = pdf_canvas.Canvas(filename, pagesize=letter)
                c.setFont("Helvetica-Bold", 16)
                c.drawString(50, 750, "Accident Reconstruction Diagram")
                c.setFont("Helvetica", 10)
                c.drawString(50, 730, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                c.save()
                messagebox.showinfo("Success", "PDF exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")

    def show_about(self):
        about = f"""Accident Reconstruction Tool
Professional Edition

Version: {AutoUpdater.CURRENT_VERSION}
Author: Galaxy AI

Features:
â€¢ 4 Realistic Vehicles
â€¢ Tree Obstacles
â€¢ Full Control System
â€¢ PDF Export
â€¢ Auto-Update Functionality"""
        messagebox.showinfo("About", about, parent=self.root)


def main():
    root = tk.Tk()
    app = AccidentReconstructorApp(root)
    root.after(1000, lambda: check_for_updates_on_startup(root))
    root.mainloop()


if __name__ == "__main__":
    main()
