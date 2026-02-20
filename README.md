# Key Repeat Tool

> **Hold a key, and it repeats — blazing fast.** No more finger fatigue from mashing the same button over and over.

A lightweight Windows utility with a simple GUI that rapidly repeats any key while it's physically held down — much faster than the default OS key repeat. Useful for gaming, accessibility, productivity, or anywhere you need rapid key repeats.

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-informational)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

- **Toggle ON/OFF** with a single click
- **Configurable target key** — click "Change Key…" and press any key (default: **E**)
- **Adjustable repeat speed** — slider from 5 ms (~200 reps/sec) to 200 ms (~5 reps/sec)
- Lightweight tkinter GUI, no heavy dependencies
- Standalone `.exe` available — no Python needed

## Use cases

- **Gaming** — spam interact/gather keys (e.g. gathering plants in Enshrouded, fishing in MMOs, rapid-fire actions)
- **Accessibility** — help users who have difficulty pressing keys repeatedly
- **Productivity** — rapid scrolling, text deletion, or any repetitive key action

## Download

Grab the latest **KeyRepeatTool.exe** from the [Releases page](https://github.com/AlejandroIzuel/key-repeat/releases) — no Python installation needed. Just download and run!

> You may need to right-click → **Run as Administrator** for the keyboard hooks to work.

> **Windows SmartScreen warning:** Since the `.exe` is not code-signed, Windows may show an "Unknown publisher" warning. This is normal for open-source tools. Click **"More info"** → **"Run anyway"** to proceed.

---

## Run from source

### Requirements

- Python 3.12+
- [`keyboard`](https://pypi.org/project/keyboard/) library

### Installation

```bash
pip install -r requirements.txt
```

### Usage

```bash
python key_repeat.py
```

> **Note:** On Windows you may need to run your terminal **as Administrator** so the `keyboard` library can install global key hooks.

### Build .exe locally

```bash
pip install pyinstaller
pyinstaller KeyRepeatTool.spec
```

The executable will be in the `dist/` folder.

### Quick start

1. Launch the program.
2. (Optional) Click **Change Key…** and press the key you want to repeat (default is **E**).
3. Adjust the repeat interval with the slider if needed.
4. Click **ON** to activate.
5. Hold down the target key — it will repeat rapidly until you release it.
6. Click **OFF** (or close the window) to deactivate.

## How it works

The program uses the `keyboard` library to install a global hook on the configured key. When a key-down event is detected, a background thread starts sending rapid key-press events at the configured interval. When the key is released, the thread stops. A `_simulating` flag prevents the hook from reacting to the synthetic events it generates.

## License

MIT
