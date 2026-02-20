"""
Key Repeat Tool
===============
A simple Windows utility with a GUI that rapidly repeats a configured key
while it is physically held down — much faster than the default OS key repeat.

Requirements:  Python 3.7+, keyboard
Usage:         python key_repeat.py
Note:          On Windows you may need to run the terminal as Administrator
               so the keyboard library can install global key hooks.
"""

import sys
import threading
import time
import tkinter as tk
from tkinter import ttk

try:
    import keyboard
except ImportError:
    print(
        "ERROR: 'keyboard' package not found.\n"
        "Install it with:  pip install keyboard"
    )
    sys.exit(1)


class KeyRepeatApp:
    """GUI application that rapidly repeats a target key while it is held."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Key Repeat Tool")
        self.root.geometry("400x340")
        self.root.resizable(False, False)

        # ── State ────────────────────────────────────────────────────
        self.enabled = False
        self.key_physically_held = False
        self.capturing_key = False
        self.target_key = "e"
        self.repeat_interval_ms = tk.DoubleVar(value=30.0)
        self._simulating = False
        self._hook = None

        # ── UI & window close handler ────────────────────────────────
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ================================================================ UI

    def _build_ui(self):
        style = ttk.Style()
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Info.TLabel", font=("Segoe UI", 10))
        style.configure("Small.TLabel", font=("Segoe UI", 9), foreground="gray")

        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)

        # Title
        ttk.Label(main, text="Key Repeat Tool", style="Header.TLabel").pack(
            pady=(0, 15)
        )

        # ── On / Off toggle button ──────────────────────────────────
        self.toggle_btn = tk.Button(
            main,
            text="OFF",
            width=18,
            height=2,
            bg="#cc3333",
            fg="white",
            activebackground="#aa2222",
            activeforeground="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            cursor="hand2",
            command=self._toggle,
        )
        self.toggle_btn.pack(pady=(0, 15))

        # ── Key selection row ───────────────────────────────────────
        key_frame = ttk.Frame(main)
        key_frame.pack(fill="x", pady=(0, 12))

        ttk.Label(key_frame, text="Target key:", style="Info.TLabel").pack(
            side="left"
        )
        self.key_display = ttk.Label(
            key_frame,
            text=self.target_key.upper(),
            font=("Segoe UI", 11, "bold"),
            foreground="#0066cc",
        )
        self.key_display.pack(side="left", padx=(8, 12))

        self.change_key_btn = ttk.Button(
            key_frame, text="Change Key…", command=self._start_key_capture
        )
        self.change_key_btn.pack(side="left")

        # ── Speed slider ────────────────────────────────────────────
        speed_frame = ttk.Frame(main)
        speed_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(speed_frame, text="Repeat interval:", style="Info.TLabel").pack(
            anchor="w"
        )

        slider_row = ttk.Frame(speed_frame)
        slider_row.pack(fill="x")
        ttk.Label(slider_row, text="5 ms").pack(side="left")
        self.speed_slider = ttk.Scale(
            slider_row,
            from_=5,
            to=200,
            variable=self.repeat_interval_ms,
            orient="horizontal",
        )
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Label(slider_row, text="200 ms").pack(side="left")

        self.speed_info = ttk.Label(speed_frame, text="", style="Small.TLabel")
        self.speed_info.pack(anchor="w", pady=(2, 0))
        self._update_speed_info()
        self.repeat_interval_ms.trace_add(
            "write", lambda *_: self._update_speed_info()
        )

        # ── Status bar ──────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main, textvariable=self.status_var, style="Small.TLabel").pack(
            side="bottom", pady=(10, 0)
        )

    def _update_speed_info(self):
        try:
            ms = max(1, int(self.repeat_interval_ms.get()))
        except (tk.TclError, ValueError):
            return
        rps = 1000 // ms
        self.speed_info.config(text=f"{ms} ms  (~{rps} repeats/sec)")

    # ============================================================ Toggle

    def _toggle(self):
        if self.capturing_key:
            return
        self.enabled = not self.enabled
        if self.enabled:
            self._install_hook()
            self.toggle_btn.config(text="ON", bg="#339933", activebackground="#227722")
            self.status_var.set(
                f"Active  —  hold [{self.target_key.upper()}] for rapid repeat"
            )
        else:
            self._uninstall_hook()
            self.key_physically_held = False
            self.toggle_btn.config(text="OFF", bg="#cc3333", activebackground="#aa2222")
            self.status_var.set("Disabled")

    # ============================================================ Hooks

    def _install_hook(self):
        self._uninstall_hook()
        self._hook = keyboard.hook_key(self.target_key, self._on_key_event)

    def _uninstall_hook(self):
        if self._hook is not None:
            keyboard.unhook(self._hook)
            self._hook = None

    # ====================================================== Key capture

    def _start_key_capture(self):
        """Enter 'listening' mode: the next key pressed becomes the target."""
        if self.enabled:
            self._toggle()  # turn off first
        self.capturing_key = True
        self.key_display.config(text="press a key…")
        self.status_var.set("Press any key to set as target…")
        self.change_key_btn.config(state="disabled")
        keyboard.hook(self._capture_callback, suppress=False)

    def _capture_callback(self, event):
        if event.event_type != keyboard.KEY_DOWN:
            return
        keyboard.unhook(self._capture_callback)
        self.target_key = event.name
        self.key_display.config(text=self.target_key.upper())
        self.capturing_key = False
        self.change_key_btn.config(state="normal")
        self.status_var.set(f"Target key set to [{self.target_key.upper()}]")

    # ================================================== Event handling

    def _on_key_event(self, event):
        """Called by the keyboard hook for every event on the target key."""
        if self._simulating:
            return  # ignore events we generated ourselves

        if event.event_type == keyboard.KEY_DOWN:
            if not self.key_physically_held:
                self.key_physically_held = True
                threading.Thread(target=self._repeat_loop, daemon=True).start()

        elif event.event_type == keyboard.KEY_UP:
            self.key_physically_held = False

    def _repeat_loop(self):
        """Background thread: sends rapid key-press events."""
        while self.key_physically_held and self.enabled:
            self._simulating = True
            try:
                keyboard.send(self.target_key)
            finally:
                self._simulating = False
            try:
                interval = self.repeat_interval_ms.get() / 1000.0
            except (tk.TclError, ValueError):
                interval = 0.030
            time.sleep(interval)

    # ============================================================= Exit

    def _on_close(self):
        self.enabled = False
        self.key_physically_held = False
        self._uninstall_hook()
        self.root.destroy()

    # ============================================================== Run

    def run(self):
        self.root.mainloop()


# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = KeyRepeatApp()
    app.run()
