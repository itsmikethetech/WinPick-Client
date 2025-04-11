"""
Script Runner
Functions for running scripts with or without administrator privileges
"""

import os
import sys
import subprocess
import ctypes

def run_script(script_path, undo=False):
    """Run the script and return the process object"""
    # Get the script extension
    _, ext = os.path.splitext(script_path)
    ext = ext.lower()
    
    # Different handling based on script type
    if ext == '.ps1':
        if undo:
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path, "-Undo"]
        else:
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path]
    elif ext == '.py':
        if undo:
            cmd = [sys.executable, script_path, "--undo"]
        else:
            cmd = [sys.executable, script_path]
    elif ext in ['.bat', '.cmd']:
        if undo:
            cmd = [script_path, "undo"]
        else:
            cmd = [script_path]
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    elif ext == '.exe':
        # For EXE files, simply execute them directly
        if undo:
            print("\nWARNING: Undo operation not supported for EXE files\n")
            raise ValueError("Undo operation not supported for EXE files")
        cmd = [script_path]
    else:
        raise ValueError(f"Unsupported script type: {ext}")
    
    # Create and return the process
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

def run_script_as_admin(script_path, undo=False):
    """Run the script with administrator privileges"""
    # Get the script extension
    _, ext = os.path.splitext(script_path)
    ext = ext.lower()
    
    try:
        print(f"\n=== Attempting to {'undo' if undo else 'run'} as Administrator: {os.path.basename(script_path)} ===")
        print("Note: Output will appear in a separate console window when running as Administrator")
        
        if ext == '.ps1':
            if undo:
                args = f"-ExecutionPolicy Bypass -File \"{script_path}\" -Undo"
            else:
                args = f"-ExecutionPolicy Bypass -File \"{script_path}\""
            
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", "powershell", args, None, 1
            )
        elif ext == '.py':
            if undo:
                args = f"\"{script_path}\" --undo"
            else:
                args = f"\"{script_path}\""
            
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, args, None, 1
            )
        elif ext in ['.bat', '.cmd']:
            if undo:
                args = "undo"
            else:
                args = None
            
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", script_path, args, None, 1
            )
        elif ext == '.exe':
            if undo:
                print("\nWARNING: Undo operation not supported for EXE files\n")
                return False
            
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", script_path, None, None, 1
            )
        else:
            raise ValueError(f"Unsupported script type: {ext}")
        
        return True
    except Exception as e:
        print(f"\nERROR: Failed to run script as Administrator: {str(e)}\n")
        return False
