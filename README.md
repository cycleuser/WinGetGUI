# WinGetGUI

![License](https://img.shields.io/github/license/EasyCam/WinGetGUI)
![Platform](https://img.shields.io/badge/platform-windows-blue)
![Version](https://img.shields.io/github/v/release/EasyCam/WinGetGUI)

A graphical user interface for Windows Package Manager (winget) built with PySide6. This tool provides an AppStore-like experience for managing software packages on Windows.

## Features

- **Search Packages**: Easily search for software packages available in the winget repository
- **Install Packages**: Install software with a single click
- **View Installed Packages**: See all installed packages in a tabular format
- **Uninstall Packages**: Remove installed software through the GUI
- **Update Packages**: Update software to the latest versions
- **Package Details**: View detailed information about each package


## Requirements

- Windows 10/11
- Windows Package Manager (winget) installed
- Python 3.7 or higher
- PySide6

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/EasyCam/WinGetGUI.git
   cd WinGetGUI
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   cd wingetgui
   briefcase run
   ```

## Usage

1. Launch the application
2. Use the "搜索" (Search) tab to find software packages
3. Select a package to view its details
4. Click "安装" (Install) to install the selected package
5. Use the "已安装" (Installed) tab to manage installed packages
6. Refresh the installed packages list to see updates


## Screenshots

### Installed Packages View
![Installed Packages](./images/1-installed.png)

### Search Packages View
![Search Packages](./images/2-search.png)

### Package Information View
![Package Information](./images/3-info.png)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- This project was generated using [Briefcase](https://github.com/beeware/briefcase) - part of [The BeeWare Project](https://beeware.org/)
- Built with [PySide6](https://wiki.qt.io/Qt_for_Python)
