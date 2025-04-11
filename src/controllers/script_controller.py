#!/usr/bin/env python3
"""
Script Controller
Handles script operations (run, edit, delete, etc.)
"""

import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, filedialog

from src.utils.script_metadata import parse_script_metadata
from src.utils.message_handler import MessageHandler


class ScriptController:
    def __init__(self, parent=None):
        self.parent = parent
    
    def run_script(self, script_path, undo=False):
        """Run a script with the appropriate interpreter"""
        from src.utils.script_runner import run_script
        script_name = os.path.basename(script_path)
        try:
            process = run_script(script_path, undo)
            self.create_process_output_thread(process, script_name, undo)
            action_text = "Undoing" if undo else "Running"
            print(f"{action_text} {script_name}")
            return True
        except Exception as e:
            error_msg = f"Failed to {'undo' if undo else 'run'} the script: {str(e)}"
            MessageHandler.error(error_msg, "Script Error")
            return False
    
    def run_script_as_admin(self, script_path, undo=False):
        """Run a script with administrator privileges"""
        from src.utils.script_runner import run_script_as_admin
        script_name = os.path.basename(script_path)
        try:
            success = run_script_as_admin(script_path, undo)
            if success:
                action_text = "Undoing" if undo else "Running"
                print(f"{action_text} {script_name} as Administrator")
                print(f"\n=== Attempting to {action_text.lower()} as Administrator: {script_name} ===")
                print("Note: Output will appear in a separate console window when running as Administrator")
                return True
            return False
        except Exception as e:
            action_text = "Undoing" if undo else "Running"
            error_msg = f"Failed to {action_text.lower()} the script as Administrator: {str(e)}"
            MessageHandler.error(error_msg, "Admin Script Error")
            return False
    
    def create_process_output_thread(self, process, script_name, undo=False):
        """Create a thread to read and display the script's output"""
        action_type = "UNDO" if undo else "RUN"
        def read_output():
            try:
                print(f"\n=== {action_type}: {script_name} ===\n")
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        print(output.strip())
                return_code = process.poll()
                if return_code == 0:
                    print(f"\n=== Script {action_type.lower()} completed successfully: {script_name} ===\n")
                else:
                    print(f"\n=== Script {action_type.lower()} returned error code {return_code}: {script_name} ===\n")
            except Exception as e:
                print(f"\nError reading script output: {str(e)}\n")
        output_thread = threading.Thread(target=read_output)
        output_thread.daemon = True
        output_thread.start()
    
    def edit_script(self, script_path):
        """Open the script in the default editor"""
        try:
            os.startfile(script_path)
            print(f"Opened {os.path.basename(script_path)} for editing")
            return True
        except Exception as e:
            error_msg = f"Failed to open the script for editing: {str(e)}"
            MessageHandler.error(error_msg, "Edit Error")
            return False
    
    def delete_script(self, script_path):
        """Delete a script file with confirmation"""
        script_name = os.path.basename(script_path)
        
        if self.parent:
            # Confirm with the user
            if not MessageHandler.confirm(
                f"Are you sure you want to delete '{script_name}'?\n\nThis action cannot be undone.",
                "Confirm Deletion"
            ):
                return False
        
        try:
            os.remove(script_path)
            print(f"Deleted script: {script_name}")
            return True
        except Exception as e:
            error_msg = f"Failed to delete script: {str(e)}"
            MessageHandler.error(error_msg, "Deletion Error")
            return False
    
    def import_script(self, category_path):
        """Import a script from another location"""
        if not self.parent:
            print("Cannot import script without UI")
            return None
            
        file_types = [
            ("All Script Files", "*.ps1;*.py;*.bat;*.cmd;*.exe"),
            ("PowerShell Scripts", "*.ps1"),
            ("Python Scripts", "*.py"),
            ("Batch Files", "*.bat;*.cmd"),
            ("Executable Files", "*.exe"),
            ("All Files", "*.*")
        ]
        script_path = filedialog.askopenfilename(
            title="Import Script",
            filetypes=file_types
        )
        if not script_path:
            return None
            
        try:
            import shutil
            script_name = os.path.basename(script_path)
            destination = os.path.join(category_path, script_name)
            
            if os.path.exists(destination):
                if not MessageHandler.confirm(f"{script_name} already exists. Overwrite?", "File Exists"):
                    return None
                    
            shutil.copy2(script_path, destination)
            print(f"Imported {script_name}")
            return destination
            
        except Exception as e:
            error_msg = f"Error importing script: {str(e)}"
            MessageHandler.error(error_msg, "Import Error")
            return None
    
    def export_script(self, script_path):
        """Export a script to another location"""
        if not self.parent:
            print("Cannot export script without UI")
            return False
            
        if not script_path:
            MessageHandler.info("Please select a script to export.", "Select Script", console_only=False)
            return False
            
        script_name = os.path.basename(script_path)
        destination = filedialog.asksaveasfilename(
            title="Export Script",
            initialfile=script_name,
            defaultextension=os.path.splitext(script_name)[1]
        )
        if not destination:
            return False
            
        try:
            import shutil
            shutil.copy2(script_path, destination)
            print(f"Exported {script_name} to {destination}")
            return True
            
        except Exception as e:
            error_msg = f"Error exporting script: {str(e)}"
            MessageHandler.error(error_msg, "Export Error")
            return False
    
    def open_containing_folder(self, script_path):
        """Open the folder containing the script"""
        folder_path = os.path.dirname(script_path)
        try:
            os.startfile(folder_path)
            print(f"Opened folder: {folder_path}")
            return True
        except Exception as e:
            error_msg = f"Error opening folder: {str(e)}"
            MessageHandler.error(error_msg, "Folder Error")
            return False
    
    def install_dependencies(self, script_path):
        """Install dependencies for the script"""
        from src.utils.dependency_manager import DependencyManager
        
        try:
            dependency_manager = DependencyManager(self.parent)
            dependency_manager.install_dependencies(script_path)
            return True
        except Exception as e:
            error_msg = f"Error installing dependencies: {str(e)}"
            MessageHandler.error(error_msg, "Dependency Error")
            return False
    
    def execute_command(self, command):
        """Execute a system command"""
        if not command:
            return False
            
        try:
            print(f"\n=== Executing command: {command} ===\n")
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            threading.Thread(
                target=self.capture_command_output,
                args=(process, command),
                daemon=True
            ).start()
            
            return True
            
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            print(f"\nERROR: {error_msg}\n")
            return False
    
    def capture_command_output(self, process, command):
        """Capture and display command output"""
        try:
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
                    
            return_code = process.poll()
            if return_code == 0:
                print(f"\n=== Command completed successfully ===\n")
            else:
                print(f"\n=== Command returned error code {return_code} ===\n")
                
        except Exception as e:
            print(f"\nError reading command output: {str(e)}\n")
