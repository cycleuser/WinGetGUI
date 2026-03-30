# WinGetGUI - Windows Package Manager GUI

A graphical user interface for Windows Package Manager (winget) built with [PySide6](https://wiki.qt.io/Qt_for_Python). Manage your Windows software packages with an AppStore-like experience -- search, install, uninstall, and update packages through a user-friendly interface.

![Installed Packages View](images/1-installed.png)

## Features

- **Search Packages** -- Search for software packages in the winget repository with real-time results display
- **Install Packages** -- Install software with a single click, with progress feedback and confirmation dialogs
- **View Installed Packages** -- Browse all installed packages in a sortable table view, showing package name, ID, installed version, and available updates
- **Uninstall Packages** -- Remove installed software through the GUI with safety confirmations
- **Update Packages** -- Update software to the latest versions with winget upgrade command integration
- **Package Details** -- View detailed information about each package including name, version, publisher, ID, and description
- **WinGet Availability Check** -- Automatic detection of winget installation on startup with helpful error messages
- **Chinese UI** -- Full Chinese language interface for native users
- **Threaded Operations** -- Background threading for all winget operations to keep the UI responsive
- **Timeout Protection** -- 30s timeout for queries, 300s timeout for install/uninstall/update operations

## Screenshots

| Installed Packages | Search Packages |
|:------------------:|:---------------:|
| ![Installed](images/1-installed.png) | ![Search](images/2-search.png) |

| Package Information | Update Packages |
|:-------------------:|:---------------:|
| ![Info](images/3-info.png) | ![Updated](images/4-updated.png) |

## Requirements

- Windows 10/11
- [Windows Package Manager (winget)](https://docs.microsoft.com/en-us/windows/package-manager/winget/) installed
- Python 3.7+

## Installation

### Method 1: Install from PyPI (Recommended)

```bash
pip install wingetgui
```

After installation, launch directly:

```bash
# Launch WinGetGUI
wingetgui

# Or use python -m
python -m wingetgui
```

### Method 2: Install from Source (Development)

```bash
# 1. Clone the repository
git clone https://github.com/cycleuser/WinGetGUI.git
cd WinGetGUI

# 2. (Optional) Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux/macOS

# 3. Install in editable mode with all dependencies
pip install -e .

# 4. Launch WinGetGUI
wingetgui
```

### WinGet Setup

Make sure winget is installed and available:

```powershell
# Check winget version
winget --version

# If winget is not installed, install it from:
# https://docs.microsoft.com/en-us/windows/package-manager/winget/
```

## Usage

1. Launch the application: `wingetgui`
2. Use the "Search" tab to find software packages
3. Select a package to view its details
4. Click "Install" to install the selected package
5. Use the "Installed" tab to manage installed packages
6. Click "Refresh" to update the installed packages list
7. Select an installed package to uninstall or update

## Project Structure

```
WinGetGUI/
├── pyproject.toml              # Package metadata & build config
├── MANIFEST.in                 # Source distribution manifest
├── LICENSE                     # GPL-3.0-or-later
├── README.md                   # English documentation
├── README_CN.md                # Chinese documentation
├── wingetgui/
│   ├── __init__.py             # Package version (__version__)
│   ├── __main__.py             # python -m wingetgui entry
│   ├── app.py                  # Main application (WinGetGUI class)
│   └── resources/              # Icons and resources
│       ├── wingetgui.ico       # Windows icon
│       ├── wingetgui.png       # PNG icon
│       └── wingetgui.icns      # macOS icon
├── tests/                      # Test suite
│   ├── test_app.py             # Basic tests
│   └── wingetgui.py            # Test helper
├── images/                     # Screenshots
├── upload_pypi.bat             # Windows PyPI upload script
├── upload_pypi.sh              # Linux/macOS PyPI upload script
└── requirements.txt            # Dependencies
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI (auto-bumps version)
# Windows:
upload_pypi.bat
# Linux/macOS:
./upload_pypi.sh
```

## Python API

```python
from wingetgui import WinGetGUI, main

# Launch the application programmatically
main()

# Or create the window instance
app = WinGetGUI()
```

## Version Management

Version is defined in `wingetgui/__init__.py`:

```python
__version__ = "0.0.1"
```

Upload scripts automatically bump the patch version before building and uploading.

## Technical Details

- **GUI Framework**: PySide6 (Qt for Python)
- **Threading**: QThreadPool + QRunnable for background operations
- **Signals**: Qt Signal/Slot mechanism for thread-safe communication
- **Timeouts**: 
  - Query operations: 30 seconds
  - Install/Uninstall/Update: 300 seconds (5 minutes)

## License

GPL-3.0-or-later. See [LICENSE](LICENSE) for details.