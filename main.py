#!/usr/bin/env python3
"""
WinPick - Windows script management and automation tool
Main application entry point
"""

import tkinter as tk
from src.ui.script_explorer import ScriptExplorer

if __name__ == "__main__":
    app = ScriptExplorer()
    app.mainloop()
