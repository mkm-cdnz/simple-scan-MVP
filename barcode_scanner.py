#!/usr/bin/env python3
"""Simple barcode scanner for Windows 11 with webcam + clipboard support."""
from __future__ import annotations

import datetime as dt
import sys
import threading
import time
from dataclasses import dataclass
from typing import List, Optional

try:
    import winsound
except ImportError:  # pragma: no cover - non-Windows fallback
    winsound = None  # type: ignore[assignment]

import cv2
import pyperclip
from PIL import Image, ImageTk
from pyzbar import pyzbar
import tkinter as tk
from tkinter import ttk


@dataclass
class CameraOption:
    index: int
    label: str


class BarcodeScannerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Barcode Scanner")
        self.root.geometry("1200x720")

        self.video_label = ttk.Label(self.root)
        self.video_label.grid(row=0, column=0, rowspan=6, sticky="nsew", padx=8, pady=8)

        self.status_var = tk.StringVar(value="Initializing camera...")
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 12))
        self.status_label.grid(row=0, column=1, sticky="w", padx=8, pady=(8, 4))

        self.type_var = tk.StringVar(value="Type: --")
        self.type_label = ttk.Label(self.root, textvariable=self.type_var)
        self.type_label.grid(row=1, column=1, sticky="w", padx=8)

        self.cooldown_var = tk.IntVar(value=2)
        self.cooldown_label = ttk.Label(self.root, text="Cooldown (seconds)")
        self.cooldown_label.grid(row=2, column=1, sticky="w", padx=8, pady=(8, 0))
        self.cooldown_spin = ttk.Spinbox(self.root, from_=0, to=10, textvariable=self.cooldown_var, width=5)
        self.cooldown_spin.grid(row=2, column=1, sticky="w", padx=160, pady=(8, 0))

        self.camera_var = tk.StringVar()
        self.camera_label = ttk.Label(self.root, text="Camera")
        self.camera_label.grid(row=3, column=1, sticky="w", padx=8, pady=(8, 0))
        self.camera_menu = ttk.OptionMenu(self.root, self.camera_var, None)
        self.camera_menu.grid(row=3, column=1, sticky="w", padx=80, pady=(8, 0))
        self.refresh_button = ttk.Button(self.root, text="Refresh Cameras", command=self.refresh_cameras)
        self.refresh_button.grid(row=3, column=1, sticky="w", padx=260, pady=(8, 0))

        self.start_button = ttk.Button(self.root, text="Start", command=self.start_camera)
        self.start_button.grid(row=4, column=1, sticky="w", padx=8, pady=(8, 0))
        self.stop_button = ttk.Button(self.root, text="Stop", command=self.stop_camera, state="disabled")
        self.stop_button.grid(row=4, column=1, sticky="w", padx=80, pady=(8, 0))

        self.copy_button = ttk.Button(self.root, text="Copy Selected", command=self.copy_selected)
        self.copy_button.grid(row=5, column=1, sticky="w", padx=8, pady=(8, 0))

        self.history = ttk.Treeview(self.root, columns=("time", "type", "data"), show="headings", height=16)
        self.history.heading("time", text="Timestamp")
        self.history.heading("type", text="Type")
        self.history.heading("data", text="Data")
        self.history.column("time", width=150)
        self.history.column("type", width=120)
        self.history.column("data", width=360)
        self.history.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)

        self.history_scroll = ttk.Scrollbar(self.root, orient="vertical", command=self.history.yview)
        self.history.configure(yscrollcommand=self.history_scroll.set)
        self.history_scroll.grid(row=6, column=2, sticky="ns", pady=8)

        self.root.grid_rowconfigure(6, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.capture: Optional[cv2.VideoCapture] = None
        self.frame_after_id: Optional[str] = None
        self.last_scan_time: float = 0.0

        self.refresh_cameras()
        if self.camera_var.get():
            self.start_camera()

    def refresh_cameras(self) -> None:
        cameras = self.detect_cameras()
        menu = self.camera_menu["menu"]
        menu.delete(0, "end")
        for option in cameras:
            menu.add_command(label=option.label, command=lambda value=option.label: self.camera_var.set(value))
        if cameras:
            self.camera_var.set(cameras[0].label)
        else:
            self.camera_var.set("")
            self.status_var.set("No cameras detected.")

    def detect_cameras(self) -> List[CameraOption]:
        options: List[CameraOption] = []
        for idx in range(10):
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cap is None or not cap.isOpened():
                continue
            ret, _ = cap.read()
            cap.release()
            if ret:
                options.append(CameraOption(index=idx, label=f"Camera {idx}"))
        return options

    def start_camera(self) -> None:
        camera_label = self.camera_var.get()
        if not camera_label:
            self.status_var.set("No camera selected.")
            return
        index = int(camera_label.split()[-1])
        if self.capture:
            self.stop_camera()
        self.capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if not self.capture.isOpened():
            self.status_var.set("Unable to open camera.")
            return
        self.status_var.set("Scanning...")
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.schedule_frame()

    def stop_camera(self) -> None:
        if self.frame_after_id:
            self.root.after_cancel(self.frame_after_id)
            self.frame_after_id = None
        if self.capture:
            self.capture.release()
            self.capture = None
        self.video_label.configure(image="")
        self.status_var.set("Stopped.")
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def schedule_frame(self) -> None:
        self.frame_after_id = self.root.after(10, self.update_frame)

    def update_frame(self) -> None:
        if not self.capture:
            return
        ret, frame = self.capture.read()
        if not ret:
            self.status_var.set("Failed to read frame.")
            self.schedule_frame()
            return

        decoded = pyzbar.decode(frame)
        now = time.time()
        cooldown = max(0, self.cooldown_var.get())

        if decoded:
            for barcode in decoded:
                x, y, w, h = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                barcode_data = barcode.data.decode("utf-8", errors="replace")
                barcode_type = barcode.type
                if now - self.last_scan_time >= cooldown:
                    self.last_scan_time = now
                    self.handle_scan(barcode_data, barcode_type)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        image = image.resize((800, 450))
        photo = ImageTk.PhotoImage(image)
        self.video_label.configure(image=photo)
        self.video_label.image = photo
        self.schedule_frame()

    def handle_scan(self, data: str, barcode_type: str) -> None:
        timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.insert("", "end", values=(timestamp, barcode_type, data))
        self.history.see(self.history.get_children()[-1])
        self.status_var.set(f"Copied: {data}")
        self.type_var.set(f"Type: {barcode_type}")
        print(f"[{timestamp}] {barcode_type}: {data}")
        pyperclip.copy(data)
        self.play_beep()

    def copy_selected(self) -> None:
        selected = self.history.selection()
        if not selected:
            self.status_var.set("No selection to copy.")
            return
        values = self.history.item(selected[-1], "values")
        if values:
            pyperclip.copy(values[2])
            self.status_var.set(f"Copied selection: {values[2]}")
            self.play_beep()

    def play_beep(self) -> None:
        if winsound:
            threading.Thread(target=lambda: winsound.MessageBeep(winsound.MB_OK), daemon=True).start()
        else:
            self.root.bell()


def main() -> int:
    root = tk.Tk()
    app = BarcodeScannerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_camera)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
