# PS MultiInjector

![version](https://img.shields.io/badge/version-1.1.0-blue)

[View changelog](./CHANGELOG.md)

READMEs by language: [Español](../README.md), [English](./README_en.md), [Português](./README_pt.md), [中文](./README_zh.md), [한국어](./README_ko.md)

Cross-platform payload injector for PS4/PS5 in Python with a graphical interface based on the original idea from MaNu(TheWizWikii) https://github.com/TheWizWikii/PS5-PS4-Payload-injector-Pro

## Features
- Cross-platform GUI (PySide6/Qt)
- Download and select payloads from GitHub
- Send payloads via TCP or Socat
- Multi-language (dynamic language switcher with flags)
- Socat auto-resolution with cache, system PATH, and optional URL overrides
- Configuration with pydantic-settings

## New in 1.1.0
- Refreshed styling pipeline using QSS for a more consistent cross-platform UI.
- Test setup improvements for headless Qt execution (`QT_QPA_PLATFORM=offscreen`).

## Installation

1. Clone the repository and enter the folder:
   ```sh
   git clone <repo-url>
   cd PS_MultiInjector/PS_MultiInjector
   ```
2. Install dependencies (requires Python 3.8+). You can use `uv` (faster) or `pip`:
   
   With uv (recommended):
   ```sh
   uv pip install -r requirements.txt
   ```
   Or with pip:
   ```sh
   pip install -r requirements.txt
   ```
   Optional profiles:
   ```sh
   # Testing (runtime + pytest)
   uv pip install -r requirements-test.txt

   # Development (runtime + test + flake8 + watchdog)
   uv pip install -r requirements-dev.txt
   ```
3. Run the application:
   ```sh
   python src/main.py
   ```

## Project structure
- `src/` — Main source code
- `tests/` — Unit and mocked integration tests
- `requirements.txt` — Runtime dependencies for publication/executable
- `requirements-test.txt` — Runtime + test dependencies
- `requirements-dev.txt` — Runtime + test + development tooling
- `README_en.md` — This file

## Tests

The test suite lives in `tests/`.

- Activate your virtual environment and install dependencies:
   ```sh
   source .venv/bin/activate
   pip install -r requirements-test.txt
   ```
- Run the tests:
   ```sh
   pytest tests
   ```

The suite uses package imports (`src.*`). `tests/conftest.py` adds the project root to the import path during `pytest` collection, so no `PYTHONPATH` export is required.

## Logs & Debugging

When the application crashes (especially in the built `.app`/`.exe`), a log file is written automatically:

| Platform | Log location |
|---|---|
| **macOS** | `~/Library/Logs/PS_MultiInjector/app.log` |
| **Windows** | `%APPDATA%\PS_MultiInjector\Logs\app.log` |
| **Linux** | `~/.local/share/PS_MultiInjector/logs/app.log` |

Read the log after a crash:

```bash
# macOS / Linux
cat ~/Library/Logs/PS_MultiInjector/app.log      # macOS
cat ~/.local/share/PS_MultiInjector/logs/app.log  # Linux

# Windows (PowerShell)
type "$env:APPDATA\PS_MultiInjector\Logs\app.log"
```

When running as a frozen bundle (`PyInstaller`), `stdout` and `stderr` are also redirected to this file, so any unhandled exception will appear there. In development (`uv run src/main.py`) the log is still written but errors are also visible in the terminal.

## Dependencies

### Runtime Dependencies
- **Python 3.8+** (required)
- **PySide6** (Qt GUI framework for the desktop interface)
- **socat** (optional but recommended for PS4/PS5 payload injection)
  - Without socat: Only TCP method available for payload injection
  - With socat: Both TCP and Socat methods available for PS4/PS5 console communication

### Installing Socat

Socat is an optional but recommended dependency for advanced PS4/PS5 payload injection. The app will auto-detect its availability and disable the Socat checkbox if not found.

**macOS (Intel & Apple Silicon)**
```bash
brew install socat
```

**Linux (Ubuntu/Debian)**
```bash
sudo apt install socat
```

**Linux (Fedora/RHEL)**
```bash
sudo dnf install socat
```

**Linux (Arch)**
```bash
sudo pacman -S socat
```

**Windows**
Three options:
1. **WSL (Recommended)** — Install Windows Subsystem for Linux, then use Linux commands above
2. **MSYS2/Cygwin** — Install via package manager
3. **scoop** — `scoop install socat`
4. **Manual binary** — See [SOCAT_MANUAL_SETUP.md](SOCAT_MANUAL_SETUP.md) for detailed OS-specific instructions

### Manual Binary Installation

To manually place the socat binary in the app's directory, see [SOCAT_MANUAL_SETUP.md](SOCAT_MANUAL_SETUP.md) for detailed step-by-step instructions for each operating system.

**Quick paths:**
- **macOS:** `~/Library/Application Support/PS_MultiInjector/socat/`
- **Windows:** `%APPDATA%\PS_MultiInjector\socat\`
- **Linux:** `~/.local/share/PS_MultiInjector/socat/`

If socat is not found, the app will:
- Display a message explaining how to install it
- Disable the "Enable SOCAT" checkbox
- Still allow TCP-based payload injection

## Socat Usage for PS4/PS5

Socat provides an alternative method to TCP for injecting payloads into PS4/PS5 consoles. It offers:
- Better reliability for certain network configurations
- Support for complex routing scenarios
- Advanced socket manipulation capabilities

The app detects socat availability automatically:
- If found: "Enable SOCAT" checkbox is active
- If not found: Checkbox is disabled with installation instructions shown

## Socat Resolution (Technical)

Socat resolution order is:
1. Cached binary in the user data directory.
2. System binary found in `PATH`.
3. Download from configured URL (only when a valid source is available/configured).

Current validated sources and behavior:

| Platform | Architecture | Default behavior |
|---|---|---|
| macOS | arm64 / x86_64 | Use system `socat` from Homebrew (`brew install socat`) |
| Linux | x86_64 | Auto-download is supported (default URL), or use system `socat` |
| Linux | arm64 | Use distro package (`apt`, `dnf`, `pacman`) |
| Windows | x86_64 | Use system `socat` (MSYS2/Cygwin), or set `SOCAT_WIN_URL` in `.env` |
| Windows | arm64 | Use system/package-manager binary or a custom internal URL |

Notes:
- The old public static-binaries URLs for macOS and Windows are not reliable anymore, so they are not used as defaults.
- You can override URLs via `.env` settings when you control a trusted binary source.
- Cached Socat binaries are stored in the user data folder (not inside the app bundle).
- Socat operations have a configurable timeout (default: 30 seconds) for PS4/PS5 payload injection.

## Notes
- The language selector uses real Unicode flags thanks to the `open_flags` package (no local images required).
- You can add more languages by creating JSON files in `src/lang`.
- Internet connection is required to download the payload list and any externally fetched Socat binary.
- Before sending, the app validates IP format and port range (1-65535). Both initial payload loading and payload sending run asynchronously to keep the UI responsive.

## How to add a new language

The language selector auto-discovers `*.json` files in `src/lang`, so you do not need to hardcode language lists when adding a new translation.

Recommended steps:

1. Create a new translation file using a lowercase locale code, for example:
   - `src/lang/fr-fr.json`
   - `src/lang/ja-jp.json`
2. Copy all keys from `src/lang/en-us.json` (or `src/lang/es-es.json`) and translate only the values.
3. Keep every key in `snake_case` and do not remove keys.
4. Run tests to validate key parity:
   ```sh
   python -m pytest tests/test_config_and_lang.py -v
   ```
5. Restart the app: the new language will appear automatically in the selector.

Notes:
- The file name defines the locale (`en-us`, `es-es`, etc.).
- The selector flag is resolved from the locale country code (`us`, `es`, `jp`, etc.).
- Language configuration uses full locale codes (`xx-yy`). Base-code aliases (`en`, `es`, etc.) are not maintained.

## Using `uv` and `watchdog` for development

For a modern and fast development workflow, you can use `uv` to install dependencies and run the app, and `watchdog` (with `watchmedo`) to autoreload the application when saving Python files.

1. Install dependencies with uv:
   ```sh
   uv pip install -r requirements-dev.txt
   ```
2. Run the app normally:
   ```sh
   uv run src/main.py
   ```
3. For development with autoreload (auto-restart on save):
   ```sh
   watchmedo auto-restart --pattern="*.py" --recursive -- uv run src/main.py
   ```

This will restart the app every time you modify any `.py` file in the project.

## Building native executables

You can generate a native executable for your operating system locally using the scripts in `ci-cd/`:

- **Linux or macOS (Intel or ARM):**
  ```sh
  bash ci-cd/build_local.sh
  ```
- **Windows:**
  Run in CMD or PowerShell:
  ```bat
  ci-cd\build_local.bat
  ```

This will generate an executable in the `dist/` folder with the name and version for your architecture and OS. You must run the script on each platform to get the native binary for that architecture (no universal binaries are generated).

## Acknowledgements

- [MaNu (TheWizWikii)](https://github.com/TheWizWikii)
