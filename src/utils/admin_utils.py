#!/usr/bin/env python3
"""
Admin Utilities
Functions related to admin privileges and elevation
"""

import os
import sys
import ctypes
import subprocess
import tkinter as tk
from tkinter import messagebox


def is_admin():
    """Check if the current process has admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        print(f"Error checking admin status: {str(e)}")
        return False


def request_admin_elevation(parent=None):
    """
    Request elevation to admin privileges
    Returns True if already admin, False otherwise
    """
    try:
        if is_admin():
            if parent:
                messagebox.showinfo("Administrator", "Application is already running as Administrator.")
            print("Application is already running as Administrator.")
            return True
        else:
            if parent and messagebox.askyesno("Administrator Rights", 
                                   "This will restart the application with administrator privileges. Continue?"):
                print("Requesting administrator privileges... Relaunching as admin.")
                params = " ".join([f'"{arg}"' for arg in sys.argv])
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
                if parent:
                    parent.quit()
                return False
            elif not parent:
                # If no parent window is provided, just try to elevate
                params = " ".join([f'"{arg}"' for arg in sys.argv])
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
                return False
    except Exception as e:
        print(f"Failed to request admin elevation: {e}")
        return False
    return False


def run_as_admin(command, wait=True):
    """Run a command with admin privileges"""
    try:
        if isinstance(command, list):
            cmd = " ".join([f'"{c}"' for c in command])
        else:
            cmd = command
            
        print(f"Running as admin: {cmd}")
        return ctypes.windll.shell32.ShellExecuteW(None, "runas", cmd, None, None, 
                                               1 if wait else 0)
    except Exception as e:
        print(f"Error running command as admin: {str(e)}")
        return None
