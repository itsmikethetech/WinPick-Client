#!/usr/bin/env python3
"""
Dependency Manager
Handles detection and installation of script dependencies
"""

import os
import sys
import re
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


class DependencyManager:
    def __init__(self, parent=None, primary_color="#4a86e8", secondary_color="#f0f0f0", 
                 accent_color="#ff5252", text_color="#333333", bg_light="#ffffff"):
        self.parent = parent
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.accent_color = accent_color
        self.text_color = text_color
        self.bg_light = bg_light

    def detect_python_dependencies(self, script_path):
        """
        Detect Python dependencies in a script file
        Returns a list of missing dependencies
        """
        if not script_path.lower().endswith(".py"):
            return []

        try:
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
        except Exception as e:
            print(f"Error reading script: {str(e)}")
            return []

        # Find modules using regex patterns
        imports = re.findall(r'^\s*import\s+([a-zA-Z0-9_.,\s]+)', source, re.MULTILINE)
        from_imports = re.findall(r'^\s*from\s+([a-zA-Z0-9_.]+)\s+import', source, re.MULTILINE)
        
        # Process regular imports (may have multiple modules per line)
        modules = set()
        for match in imports:
            mod_list = [m.strip() for m in match.split(',')]
            for module in mod_list:
                # Extract the base module name (before any "as" keyword)
                base_module = module.split(' as ')[0].strip()
                # Get just the top-level package name
                top_module = base_module.split('.')[0]
                modules.add(top_module)
        
        # Process from imports
        for match in from_imports:
            # Get just the top-level package name
            top_module = match.split('.')[0]
            modules.add(top_module)
        
        # Filter out built-in modules and check if modules can be imported
        missing_modules = []
        for mod in modules:
            # Skip common built-ins
            if mod in ['os', 'sys', 'io', 're', 'time', 'datetime', 'math', 
                      'json', 'random', 'threading', 'queue', 'tkinter', 'ctypes',
                      'argparse', 'subprocess', 'traceback']:
                continue
                
            try:
                __import__(mod)
            except ImportError:
                missing_modules.append(mod)
                
        return missing_modules

    def detect_powershell_dependencies(self, script_path):
        """
        Detect PowerShell module dependencies in a script file
        Returns a list of PowerShell modules
        """
        if not script_path.lower().endswith(".ps1"):
            return []

        try:
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
        except Exception as e:
            print(f"Error reading script: {str(e)}")
            return []

        # Find import-module statements
        module_matches = re.findall(r'Import-Module\s+([a-zA-Z0-9_.-]+)', source, re.IGNORECASE)
        return [module.strip() for module in module_matches]

    def install_dependencies(self, script_path):
        """Show dialog to install missing dependencies"""
        # Only process Python scripts for now
        if not script_path.lower().endswith(".py"):
            messagebox.showinfo("Unsupported", "Dependency installation is only available for Python scripts.")
            return

        missing_modules = self.detect_python_dependencies(script_path)
        
        if not missing_modules:
            messagebox.showinfo("Dependencies", "All Python module dependencies appear to be satisfied.")
            print("All dependencies are installed.")
            return
        
        print("Missing modules:", missing_modules)
        
        # Create a modern dependency installation dialog
        dep_window = tk.Toplevel(self.parent)
        dep_window.title("Install Dependencies")
        dep_window.geometry("500x350")
        dep_window.transient(self.parent)
        dep_window.grab_set()
        dep_window.configure(bg=self.secondary_color)
        
        # Center on parent window
        if self.parent:
            x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (500 // 2)
            y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (350 // 2)
            dep_window.geometry(f"+{x}+{y}")
            
        frame = ttk.Frame(dep_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(frame, 
                 text="Python Dependencies", 
                 font=("Segoe UI", 14, "bold"),
                 foreground=self.primary_color).pack(anchor=tk.CENTER, pady=(0, 10))
        
        script_name = os.path.basename(script_path)
        ttk.Label(frame, 
                 text=f"Script: {script_name}",
                 font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Missing modules list frame
        module_frame = ttk.Frame(frame)
        module_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(module_frame, 
                 text="Missing modules:", 
                 font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        
        modules_list = ttk.Frame(module_frame)
        modules_list.pack(fill=tk.X, pady=5, padx=10)
        
        for i, module in enumerate(missing_modules):
            ttk.Label(modules_list, 
                     text=f"• {module}",
                     font=("Consolas", 10)).pack(anchor=tk.W, pady=1)
        
        # Installation options
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill=tk.X, pady=10)
        
        # Checkboxes for options
        upgrade_pip_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, 
                       text="Upgrade pip to latest version first",
                       variable=upgrade_pip_var).pack(anchor=tk.W, pady=2)
        
        # Status message area
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        status_var = tk.StringVar(value="Ready to install missing dependencies")
        status_label = ttk.Label(status_frame, textvariable=status_var)
        status_label.pack(fill=tk.X, pady=5)
        
        # Progress bar
        progress_var = tk.DoubleVar(value=0.0)
        progress_bar = ttk.Progressbar(status_frame, variable=progress_var, mode="determinate")
        progress_bar.pack(fill=tk.X, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def install():
            # Disable buttons during installation
            install_btn.config(state="disabled")
            cancel_btn.config(state="disabled")
            
            # Update status
            status_var.set("Checking pip installation...")
            progress_var.set(10)
            dep_window.update_idletasks()
            
            # Run installation in a separate thread to keep UI responsive
            def install_thread():
                try:
                    # Check pip
                    try:
                        pip_output = subprocess.check_output([sys.executable, "-m", "pip", "--version"])
                        pip_installed = True
                        print("Pip is installed:", pip_output.decode().strip())
                        status_var.set("Pip is already installed")
                        progress_var.set(20)
                        dep_window.update_idletasks()
                    except Exception as e:
                        pip_installed = False
                        print("Pip is not installed, trying to install it.")
                        status_var.set("Installing pip...")
                        try:
                            import ensurepip
                            ensurepip.bootstrap()
                            pip_installed = True
                            print("Pip installed successfully.")
                            status_var.set("Pip installed successfully")
                            progress_var.set(20)
                            dep_window.update_idletasks()
                        except Exception as e:
                            status_var.set(f"Failed to install pip: {str(e)}")
                            progress_var.set(0)
                            dep_window.update_idletasks()
                            # Re-enable buttons
                            install_btn.config(state="normal")
                            cancel_btn.config(state="normal")
                            return
                    
                    # Upgrade pip if requested
                    if upgrade_pip_var.get():
                        status_var.set("Upgrading pip to latest version...")
                        progress_var.set(30)
                        dep_window.update_idletasks()
                        try:
                            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
                            print("Pip upgraded successfully.")
                            status_var.set("Pip upgraded successfully")
                            progress_var.set(40)
                            dep_window.update_idletasks()
                        except Exception as e:
                            print(f"Failed to upgrade pip: {str(e)}")
                            status_var.set(f"Warning: Failed to upgrade pip, continuing with installation")
                            progress_var.set(40)
                            dep_window.update_idletasks()
                    
                    # Install missing modules
                    status_var.set(f"Installing {len(missing_modules)} missing modules...")
                    progress_var.set(50)
                    dep_window.update_idletasks()
                    
                    try:
                        command = [sys.executable, "-m", "pip", "install"] + missing_modules
                        print("Running command:", " ".join(command))
                        
                        process = subprocess.Popen(
                            command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        
                        # Read output line by line
                        while True:
                            line = process.stdout.readline()
                            if not line and process.poll() is not None:
                                break
                            if line:
                                line = line.strip()
                                print(line)
                                status_var.set(line)
                                # Update progress bar gradually
                                current_progress = progress_var.get()
                                if current_progress < 90:
                                    progress_var.set(current_progress + 1)
                                dep_window.update_idletasks()
                        
                        if process.returncode == 0:
                            status_var.set("All dependencies installed successfully!")
                            progress_var.set(100)
                            dep_window.update_idletasks()
                            
                            # Show success message and close dialog
                            dep_window.after(1000, lambda: [
                                messagebox.showinfo("Success", 
                                                   "Missing dependencies have been installed successfully."),
                                dep_window.destroy()
                            ])
                        else:
                            status_var.set(f"Installation failed with code {process.returncode}")
                            progress_var.set(0)
                            dep_window.update_idletasks()
                            # Re-enable buttons
                            install_btn.config(state="normal")
                            cancel_btn.config(state="normal")
                    except Exception as e:
                        status_var.set(f"Error: {str(e)}")
                        progress_var.set(0)
                        print(f"ERROR: Failed to install dependencies: {str(e)}")
                        # Re-enable buttons
                        install_btn.config(state="normal")
                        cancel_btn.config(state="normal")
                except Exception as e:
                    status_var.set(f"Error: {str(e)}")
                    progress_var.set(0)
                    print(f"ERROR: Installation process failed: {str(e)}")
                    # Re-enable buttons
                    install_btn.config(state="normal")
                    cancel_btn.config(state="normal")
            
            # Start installation thread
            threading.Thread(target=install_thread, daemon=True).start()
        
        cancel_btn = ttk.Button(button_frame, 
                              text="Cancel", 
                              width=15,
                              command=dep_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        install_btn = ttk.Button(button_frame, 
                               text="Install", 
                               width=15,
                               command=install)
        install_btn.pack(side=tk.RIGHT, padx=5)
