"""Key Repeat Tool.

A simple Windows utility with a GUI that rapidly repeats a configured key
while it is physically held down — much faster than the default OS key repeat.

Requirements:
    Python 3.12+, keyboard

Usage:
    python key_repeat.py

Note:
    On Windows you may need to run the terminal as Administrator
    so the keyboard library can install global key hooks.
"""

from __future__ import annotations

import sys
import threading
import time
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any

try:
    import keyboard
except ImportError:
    print("ERROR: 'keyboard' package not found.\nInstall it with:  pip install keyboard")
    sys.exit(1)

if TYPE_CHECKING:
    from keyboard import KeyboardEvent

# ── Constants ────────────────────────────────────────────────────────────
DEFAULT_KEY: str = "e"
DEFAULT_INTERVAL_MS: float = 30.0
MIN_INTERVAL_MS: int = 5
MAX_INTERVAL_MS: int = 200
FALLBACK_INTERVAL_S: float = 0.030

WINDOW_TITLE: str = "Key Repeat Tool"
WINDOW_SIZE: str = "400x340"

COLOR_ON: str = "#339933"
COLOR_ON_ACTIVE: str = "#227722"
COLOR_OFF: str = "#cc3333"
COLOR_OFF_ACTIVE: str = "#aa2222"
COLOR_KEY: str = "#0066cc"

FONT_FAMILY: str = "Segoe UI"


class KeyRepeatApp:
    """GUI application that rapidly repeats a target key while it is held.

    Attributes:
        root: The tkinter root window.
        enabled: Whether the repeat feature is currently active.
        target_key: The key name to hook and repeat.
    """

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)

        self.enabled: bool = False
        self.key_physically_held: bool = False
        self.capturing_key: bool = False
        self.target_key: str = DEFAULT_KEY
        self.repeat_interval_ms = tk.DoubleVar(value=DEFAULT_INTERVAL_MS)
        self._simulating: bool = False
        self._hook: Any = None
        self._lock = threading.Lock()

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        """Construct all UI widgets."""
        style = ttk.Style()
        style.configure("Header.TLabel", font=(FONT_FAMILY, 16, "bold"))
        style.configure("Info.TLabel", font=(FONT_FAMILY, 10))
        style.configure("Small.TLabel", font=(FONT_FAMILY, 9), foreground="gray")

        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text=WINDOW_TITLE, style="Header.TLabel").pack(pady=(0, 15))

        self.toggle_btn = tk.Button(
            main,
            text="OFF",
            width=18,
            height=2,
            bg=COLOR_OFF,
            fg="white",
            activebackground=COLOR_OFF_ACTIVE,
            activeforeground="white",
            font=(FONT_FAMILY, 12, "bold"),
            relief="flat",
            cursor="hand2",
            command=self._toggle,
        )
        self.toggle_btn.pack(pady=(0, 15))

        key_frame = ttk.Frame(main)
        key_frame.pack(fill="x", pady=(0, 12))

        ttk.Label(key_frame, text="Target key:", style="Info.TLabel").pack(side="left")
        self.key_display = ttk.Label(
            key_frame,
            text=self.target_key.upper(),
            font=(FONT_FAMILY, 11, "bold"),
            foreground=COLOR_KEY,
        )
        self.key_display.pack(side="left", padx=(8, 12))

        self.change_key_btn = ttk.Button(
            key_frame, text="Change Key…", command=self._start_key_capture
        )
        self.change_key_btn.pack(side="left")

        speed_frame = ttk.Frame(main)
        speed_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(speed_frame, text="Repeat interval:", style="Info.TLabel").pack(anchor="w")

        slider_row = ttk.Frame(speed_frame)
        slider_row.pack(fill="x")
        ttk.Label(slider_row, text="5 ms").pack(side="left")
        self.speed_slider = ttk.Scale(
            slider_row,
            from_=MIN_INTERVAL_MS,
            to=MAX_INTERVAL_MS,
            variable=self.repeat_interval_ms,
            orient="horizontal",
        )
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Label(slider_row, text="200 ms").pack(side="left")

        self.speed_info = ttk.Label(speed_frame, text="", style="Small.TLabel")
        self.speed_info.pack(anchor="w", pady=(2, 0))
        self._update_speed_info()
        self.repeat_interval_ms.trace_add("write", lambda *_: self._update_speed_info())

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main, textvariable=self.status_var, style="Small.TLabel").pack(
            side="bottom", pady=(10, 0)
        )

    def _update_speed_info(self) -> None:
        """Refresh the speed label text from the current slider value."""
        try:
            ms = max(1, int(self.repeat_interval_ms.get()))
        except (tk.TclError, ValueError):
            return
        rps = 1000 // ms
        self.speed_info.config(text=f"{ms} ms  (~{rps} repeats/sec)")

    def _toggle(self) -> None:
        """Toggle the key-repeat feature on or off."""
        if self.capturing_key:
            return
        self.enabled = not self.enabled
        if self.enabled:
            self._install_hook()
            self.toggle_btn.config(text="ON", bg=COLOR_ON, activebackground=COLOR_ON_ACTIVE)
            self.status_var.set(f"Active  —  hold [{self.target_key.upper()}] for rapid repeat")
        else:
            self._uninstall_hook()
            self.key_physically_held = False
            self.toggle_btn.config(text="OFF", bg=COLOR_OFF, activebackground=COLOR_OFF_ACTIVE)
            self.status_var.set("Disabled")

    def _install_hook(self) -> None:
        """Register a global keyboard hook for the target key."""
        self._uninstall_hook()
        self._hook = keyboard.hook_key(self.target_key, self._on_key_event)

    def _uninstall_hook(self) -> None:
        """Remove the active keyboard hook if one exists."""
        if self._hook is not None:
            keyboard.unhook(self._hook)
            self._hook = None

    def _start_key_capture(self) -> None:
        """Enter 'listening' mode: the next key pressed becomes the target."""
        if self.enabled:
            self._toggle()
        self.capturing_key = True
        self.key_display.config(text="press a key…")
        self.status_var.set("Press any key to set as target…")
        self.change_key_btn.config(state="disabled")
        keyboard.hook(self._capture_callback, suppress=False)

    def _capture_callback(self, event: KeyboardEvent) -> None:
        """Handle the first KEY_DOWN during key capture and set it as target."""
        if event.event_type != keyboard.KEY_DOWN:
            return
        keyboard.unhook(self._capture_callback)
        self.target_key = event.name or DEFAULT_KEY
        self.key_display.config(text=self.target_key.upper())
        self.capturing_key = False
        self.change_key_btn.config(state="normal")
        self.status_var.set(f"Target key set to [{self.target_key.upper()}]")

    def _on_key_event(self, event: KeyboardEvent) -> None:
        """Handle keyboard hook events for the target key.

        Starts a repeat thread on KEY_DOWN and stops it on KEY_UP.
        Ignores synthetic events produced by ``_repeat_loop``.
        """
        if self._simulating:
            return

        if event.event_type == keyboard.KEY_DOWN:
            with self._lock:
                if not self.key_physically_held:
                    self.key_physically_held = True
                    threading.Thread(target=self._repeat_loop, daemon=True).start()

        elif event.event_type == keyboard.KEY_UP:
            self.key_physically_held = False

    def _repeat_loop(self) -> None:
        """Background thread: sends rapid key-press events until the key is released."""
        while self.key_physically_held and self.enabled:
            self._simulating = True
            try:
                keyboard.send(self.target_key)
            finally:
                self._simulating = False
            try:
                interval = self.repeat_interval_ms.get() / 1000.0
            except (tk.TclError, ValueError):
                interval = FALLBACK_INTERVAL_S
            time.sleep(interval)

    def _on_close(self) -> None:
        """Clean up hooks and destroy the window."""
        self.enabled = False
        self.key_physically_held = False
        self._uninstall_hook()
        self.root.destroy()

    def run(self) -> None:
        """Start the tkinter main loop."""
        self.root.mainloop()


if __name__ == "__main__":
    app = KeyRepeatApp()
    app.run()
