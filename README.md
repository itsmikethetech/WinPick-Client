WinPick (Client): Unlock the Full Potential of Windows

Welcome to WinPick, your key to unlocking the full potential of Microsoft Windows. The name WinPick is a play on words for “Windows Lockpick”, symbolizing its ability to unlock hidden and underutilized features in Windows.

<img src="https://github.com/itsmikethetech/WinPick/assets/25166211/208e288c-e338-4880-9e15-00512f8784c0" width="100">

# Overview

WinPick is a powerful application that brings together a vast collection of community scripts designed to enhance your Windows experience. It serves as a one-stop solution for customizing, optimizing, and tweaking Windows to suit your needs and preferences.

# Windows Scripts Collection

## Categories

- **Bloatware Removal** - Scripts to remove unnecessary pre-installed software
- **Boot Options** - Scripts to optimize and configure Windows boot settings
- **Default Apps** - Scripts to manage and set default application associations
- **Network Optimizations** - Scripts to enhance network performance and settings
- **Performance Tweaks** - Scripts to improve overall system performance
- **Power Management** - Scripts to optimize power settings and battery life
- **Privacy Settings** - Scripts to enhance and manage Windows privacy settings
- **Security Enhancements** - Scripts to improve system security
- **System Maintenance** - Scripts for routine system maintenance tasks
- **UI Customizations** - Scripts to customize the Windows user interface

## Installation

### Prerequisites

- Windows 10/11
- Python 3.6 or higher
- PowerShell 5.0 or higher (for PowerShell scripts)
- Administrative privileges (for most scripts)

### Setup

1. Clone this repository or download it to your computer
2. Install dependencies (if any):
   ```
   pip install -r requirements.txt
   ```
3. Run the main application:
   ```
   python main.py
   ```

## Usage

### Application Interface

The WinPick application provides a graphical interface for browsing, running, and managing Windows scripts:

1. **Browse Categories**: Select a category from the left panel to view available scripts
2. **Run Scripts**: Double-click on a script to run it, or right-click for additional options
3. **Create Scripts**: Click the "New Script" button to create a new script from a template
4. **Console Output**: View script execution output in the console panel

### Manual Usage

Each script can also be run directly from PowerShell, Command Prompt, or Explorer:

- PowerShell scripts (.ps1): `powershell -ExecutionPolicy Bypass -File script_name.ps1`
- Python scripts (.py): `python script_name.py`
- Batch scripts (.bat/.cmd): Double-click or run in Command Prompt

Most scripts include undo functionality, which can be triggered with:
- PowerShell: `-Undo` parameter
- Python: `--undo` flag
- Batch: `undo` parameter

## Project Structure

```
├── main.py                 # Application entry point
├── README.md               # This file
├── setup.py                # Installation script
├── src/                    # Source code
│   ├── ui/                 # User interface components
│   └── utils/              # Utility functions
└── WindowsScripts/         # Script collection
    ├── Bloatware Removal/  # Scripts for removing bloatware
    ├── Boot Options/       # Boot configuration scripts
    ├── ...
    └── Script Templates/   # Templates for creating new scripts
```

## Contributing

Feel free to contribute by adding new scripts or improving existing ones. Please follow the template in the Script Templates directory when adding new scripts.

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Add your scripts or make changes
4. Commit your changes (`git commit -m 'Add some feature'`)
5. Push to the branch (`git push origin feature-branch`)
6. Open a Pull Request


## Contributing

Feel free to contribute by adding new scripts or improving existing ones. Please follow the template in the Script Templates directory when adding new scripts.
