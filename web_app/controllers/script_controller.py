#!/usr/bin/env python3
"""
Script Controller for Web App
Handles script operations for the web interface
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.script_metadata import parse_script_metadata
from src.utils.message_handler import MessageHandler

class ScriptController:
    """Controller for script operations"""
    
    def get_scripts_for_web(self, category_path, rating_system=None):
        """Get list of scripts in a category for web display"""
        scripts = []
        script_extensions = ['.ps1', '.py', '.bat', '.cmd', '.exe']
        
        os.makedirs(category_path, exist_ok=True)
        
        try:
            for file in os.listdir(category_path):
                file_path = os.path.join(category_path, file)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file)
                    if ext.lower() in script_extensions:
                        script_type = ext.lstrip(".").upper()
                        friendly_name, description, undoable, undo_desc, developer, link = parse_script_metadata(file_path)
                        
                        # Get rating if rating system is available
                        rating = None
                        if rating_system:
                            rating = rating_system.get_average_rating(file_path, friendly_name)
                        
                        scripts.append({
                            'file_name': file,
                            'file_path': file_path,
                            'type': script_type,
                            'name': friendly_name,
                            'developer': developer,
                            'description': description,
                            'rating': rating,
                            'undoable': undoable,
                            'undo_desc': undo_desc,
                            'link': link
                        })
        except Exception as e:
            MessageHandler.error(f"Error reading scripts: {str(e)}")
        
        # Sort scripts by name
        return sorted(scripts, key=lambda x: x['name'].lower())
    
    def run_script_web(self, script_path, undo=False, admin=False, output_callback=None):
        """Run a script and return web-friendly result"""
        if not os.path.exists(script_path):
            if output_callback:
                output_callback(f"ERROR: Script not found: {script_path}")
            return {'success': False, 'message': f"Script not found: {script_path}"}
        
        try:
            script_type = os.path.splitext(script_path)[1].lower()
            friendly_name, description, undoable, undo_desc, developer, link = parse_script_metadata(script_path)
            
            # Check if trying to undo a non-undoable script
            if undo and not undoable:
                msg = f"Script '{friendly_name}' does not support undo functionality"
                if output_callback:
                    output_callback(f"ERROR: {msg}")
                return {'success': False, 'message': msg}
            
            # Log execution
            action = "Undoing" if undo else "Running"
            if output_callback:
                output_callback(f"\n{'='*50}")
                output_callback(f"{action} script: {friendly_name}")
                output_callback(f"Type: {script_type}")
                output_callback(f"Path: {script_path}")
                output_callback(f"{'='*50}\n")
            
            # Prepare command based on script type
            cmd = None
            if script_type == '.py':
                cmd = [sys.executable, script_path]
                if undo:
                    cmd.append('--undo')
            elif script_type == '.ps1':
                cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path]
                if undo:
                    cmd.append('-Undo')
            elif script_type in ['.bat', '.cmd']:
                cmd = [script_path]
                if undo:
                    cmd.append('undo')
            elif script_type == '.exe':
                cmd = [script_path]
                if undo:
                    cmd.append('/undo')
            else:
                msg = f"Unsupported script type: {script_type}"
                if output_callback:
                    output_callback(f"ERROR: {msg}")
                return {'success': False, 'message': msg}
            
            # Execute the script
            if output_callback:
                output_callback(f"Executing command: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                shell=(os.name == 'nt')  # Use shell on Windows
            )
            
            # Stream and capture output
            output = []
            for line in process.stdout:
                line = line.strip()
                if output_callback:
                    output_callback(line)
                output.append(line)
            
            # Wait for process to complete
            return_code = process.wait()
            
            if return_code == 0:
                msg = f"Script executed successfully"
                if output_callback:
                    output_callback(f"SUCCESS: {msg}")
                return {'success': True, 'message': msg, 'output': output}
            else:
                msg = f"Script failed with return code: {return_code}"
                if output_callback:
                    output_callback(f"ERROR: {msg}")
                return {'success': False, 'message': msg, 'output': output}
                
        except Exception as e:
            msg = f"Error executing script: {str(e)}"
            if output_callback:
                output_callback(f"ERROR: {msg}")
            return {'success': False, 'message': msg}
    
    def get_script_template(self, script_type, name, developer, link, description, undoable, undo_desc):
        """Get template for a new script"""
        if script_type == ".py":
            return f"""# NAME: {name}
# DEVELOPER: {developer}
# LINK: {link}
# DESCRIPTION: {description}
# UNDOABLE: {"Yes" if undoable else "No"}
# UNDO_DESC: {undo_desc}
#
# This is a Python script template with undo capability

import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='{description}')
    parser.add_argument('--undo', action='store_true', help='Undo the changes made by this script')
    args = parser.parse_args()
    
    if args.undo:
        perform_undo()
    else:
        perform_action()

def perform_action():
    print("Performing main action...")
    # Your main code here
    
def perform_undo():
    print("Performing undo action...")
    # Your undo code here

if __name__ == "__main__":
    main()
"""
        elif script_type == ".ps1":
            return f"""# NAME: {name}
# DEVELOPER: {developer}
# LINK: {link}
# DESCRIPTION: {description}
# UNDOABLE: {"Yes" if undoable else "No"}
# UNDO_DESC: {undo_desc}
#
# This is a PowerShell script template with undo capability

param (
    [switch]$Undo
)

function Perform-Action {{
    Write-Host "Performing main action..."
    # Your main code here
}}

function Perform-Undo {{
    Write-Host "Performing undo action..."
    # Your undo code here
}}

if ($Undo) {{
    Perform-Undo
}} else {{
    Perform-Action
}}
"""
        elif script_type in [".bat", ".cmd"]:
            return f""":: NAME: {name}
:: DEVELOPER: {developer}
:: LINK: {link}
:: DESCRIPTION: {description}
:: UNDOABLE: {"Yes" if undoable else "No"}
:: UNDO_DESC: {undo_desc}
::
:: This is a Batch script template with undo capability

@echo off

if "%1"=="undo" goto :undo

:main
echo Performing main action...
:: Your main code here
goto :end

:undo
echo Performing undo action...
:: Your undo code here
goto :end

:end
pause
"""
        else:
            return "Unsupported script type"