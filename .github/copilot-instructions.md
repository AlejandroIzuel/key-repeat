# Copilot Instructions for Key Repeat Tool

## Project Overview

This is a lightweight Windows desktop utility (Python + tkinter) that rapidly
repeats a configurable keyboard key while it is physically held down.

## Tech Stack

- **Language:** Python 3.12+
- **GUI:** tkinter (stdlib)
- **Key hooking:** `keyboard` library
- **Packaging:** PyInstaller (single-file `.exe`)
- **Linting/Formatting:** Ruff
- **Type checking:** mypy
- **Git hooks:** pre-commit

## Code Style & Conventions

- Follow **PEP 8** and let **Ruff** enforce formatting (`ruff format`) and linting (`ruff check`).
- Use **type hints** on all function signatures (`from __future__ import annotations`).
- Use **`from __future__ import annotations`** at the top of every module for modern annotation syntax.
- Place third-party type imports behind `if TYPE_CHECKING:` to avoid runtime import costs.
- Extract **magic numbers and strings** into module-level constants (e.g. `DEFAULT_KEY`, `COLOR_ON`), with explicit type annotations.
- Use **docstrings** (Google style) on all public classes and methods.
- **Comments explain *why*, not *what*.** Do not add comments that merely restate the code. Only add a comment when the reasoning or intent is non-obvious.
- Avoid section-separator comments (e.g. `# === Hooks ===`). Let docstrings and clear naming guide the reader.
- Prefix private methods/attributes with a single underscore `_`.
- Keep the codebase in a **single `key_repeat.py` file** unless complexity demands splitting.

## Architecture

- `KeyRepeatApp` — single class containing all GUI, state, and keyboard logic.
- A global `keyboard` hook detects physical key-down/key-up events.
- On key-down, a **daemon thread** fires rapid `keyboard.send()` calls at the configured interval.
- A `_simulating` flag prevents the hook from reacting to its own synthetic events.
- A `threading.Lock` guards the key-down → thread-start transition to avoid race conditions.
- The app cleans up hooks on window close via `WM_DELETE_WINDOW` protocol.

## Development Workflow

1. Install dev dependencies: `pip install -r requirements.txt && pip install ruff mypy pre-commit`
2. Install git hooks: `pre-commit install`
3. Run linter: `ruff check .`
4. Run formatter: `ruff format .`
5. Run type checker: `mypy key_repeat.py`
6. Run all checks: `pre-commit run --all-files`

## CI/CD

- GitHub Actions workflow at `.github/workflows/build-release.yml`.
- Triggers on version tags (`v*`).
- Builds a Windows `.exe` via PyInstaller and attaches it to a GitHub Release.

## Important Notes

- The `keyboard` library requires **Administrator privileges** on Windows for global hooks.
- This tool is **Windows-only** in practice (Linux requires root + X11/uinput, macOS needs accessibility permissions).
- tkinter variables (`DoubleVar`, `StringVar`) are **not thread-safe** — access from background threads is wrapped in try/except.
- Keep the UI responsive — never block the main thread with long-running operations.
