# AGENTS.md - WinGetGUI Project Guide

This document provides guidance for AI coding agents working in this repository.

## Project Overview

WinGetGUI is a graphical user interface for Windows Package Manager (winget) built with PySide6. It provides an AppStore-like experience for managing software packages on Windows.

**Key Technologies:**
- Python 3.7+
- PySide6 (Qt for Python) - GUI framework
- setuptools - Build and packaging tool
- pytest - Testing framework

## Project Structure

```
WinGetGUI/
├── wingetgui/                    # Main package directory
│   ├── __init__.py              # Package init with version
│   ├── __main__.py              # Entry point (python -m wingetgui)
│   ├── app.py                   # Main application (WinGetGUI class)
│   └── resources/               # Icons and resources
├── tests/                        # Test files
│   ├── test_app.py
│   └── wingetgui.py
├── pyproject.toml               # PyPI configuration
├── MANIFEST.in                  # Package manifest
├── upload_pypi.bat              # Windows upload script
├── upload_pypi.sh               # Linux/Mac upload script
├── requirements.txt             # Dependencies
├── README.md                    # Documentation
├── README_CN.md                 # Chinese documentation
└── LICENSE                      # GPLv3 license
```

## Build/Lint/Test Commands

### Prerequisites
```bash
pip install -r requirements.txt
pip install pytest
```

### Running the Application
```bash
python -m wingetgui
```

### Testing
```bash
pytest

pytest -v

pytest tests/test_app.py

pytest tests/test_app.py::test_first

pytest --cov=wingetgui
```

### Building and Publishing
```bash
pip install build twine

python -m build

twine check dist/*

twine upload dist/*
```

### Quick Upload Scripts
```bash
upload_pypi.sh    # Linux/Mac: auto bump version, build, upload

upload_pypi.bat   # Windows: auto bump version, build, upload
```

### Linting/Type Checking
```bash
pip install ruff mypy
ruff check wingetgui/
mypy wingetgui/
```

## Version Management

Version is defined in `wingetgui/__init__.py`:
```python
__version__ = "0.0.1"
```

Upload scripts automatically bump patch version before uploading.

## Code Style Guidelines

### Imports
```python
import sys
import subprocess
import json
import threading

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QPixmap, QIcon
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `WinGetGUI`, `PackageModel`, `Worker`)
- **Functions/Methods**: snake_case (e.g., `search_packages`, `on_package_selected`)
- **Variables**: snake_case (e.g., `current_package`, `installed_table`)
- **Qt Signals**: snake_case (e.g., `finished`, `error`, `result`)

### Formatting
- Use 4 spaces for indentation (no tabs)
- Maximum line length: ~100-120 characters
- Use f-strings for string formatting

### Docstrings
Chinese docstrings are acceptable. Keep them concise.
```python
def search_packages(self):
    """搜索软件包"""
```

### Error Handling
```python
try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
except subprocess.TimeoutExpired:
    return "操作超时"
except Exception as e:
    return f"发生错误: {str(e)}"
```

### Qt/PySide6 Conventions
```python
class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)
    result = Signal(object)

class Worker(QRunnable):
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()
```

## Code Patterns

### Threading Pattern
1. Create `Worker(QRunnable)` with function to execute
2. Define `WorkerSignals(QObject)` with result/error/finished signals
3. Start with `self.threadpool.start(worker)`
4. Connect signals to callbacks

### Package Data Model
```python
{
    "Name": "Package Name",
    "Id": "Publisher.PackageId",
    "Version": "1.0.0",
    "Publisher": "Publisher Name",
    "Description": "Package description"
}
```

## Important Notes

- **Windows-specific** application wrapping `winget` CLI
- GUI uses Chinese text for labels/messages
- Checks for `winget` availability on startup
- Timeout: 30s for queries, 300s for install/uninstall/update
- License: GPLv3+