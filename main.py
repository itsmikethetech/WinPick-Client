#!/usr/bin/env python3
"""
WinPick - Windows Scripts Manager
Main entry point for the application
"""

import os
import sys
import ctypes
import traceback
from tkinter import messagebox

from src.utils.message_handler import MessageHandler

# Check for administrator rights and display a message
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def main():
    try:
        # Import the app module
        from src.ui.app import ScriptExplorer
        
        # Create and run the application
        app = ScriptExplorer()
        app.mainloop()
    except Exception as e:
        error_msg = f"Error starting application: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        MessageHandler.error(error_msg, "Application Error")
        
if __name__ == "__main__":
    main()
