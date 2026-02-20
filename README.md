# Key Repeat Tool

A simple Python utility with a GUI that rapidly repeats a key while it is physically held down — much faster than the default OS key repeat. Great for games like Enshrouded!

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-informational)

## Features

- **Toggle ON/OFF** with a single click
- **Configurable target key** — click "Change Key…" and press any key
- **Adjustable repeat speed** — slider from 5 ms (~200 reps/sec) to 200 ms (~5 reps/sec)
- Lightweight tkinter GUI, no heavy dependencies

## Requirements

- Python 3.7+
- [`keyboard`](https://pypi.org/project/keyboard/) library

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python key_repeat.py
```

> **Note:** On Windows you may need to run your terminal **as Administrator** so the `keyboard` library can install global key hooks.

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
