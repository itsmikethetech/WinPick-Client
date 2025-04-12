#!/usr/bin/env python3
"""
Menu Module
Handles the application menu bar
"""

import tkinter as tk
from tkinter import ttk


class MenuBar:
    def __init__(self, parent):
        self.parent = parent
        self.menu_bar = tk.Menu(parent)
        
        # Initialize the menu structure
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        
        # Add menus to the menu bar
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Tools", menu=self.tools_menu)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        
        # Apply the menu bar to the parent window
        parent.config(menu=self.menu_bar)
        
        # Keep track of the GitHub auth menu item
        self.github_auth_item = None
        
    def setup_file_menu(self, new_script_callback, new_category_callback, 
                       open_scripts_folder_callback, import_script_callback, 
                       export_script_callback, exit_callback):
        """Setup the File menu with callbacks"""
        self.file_menu.add_command(label="New Script", command=new_script_callback)
        self.file_menu.add_command(label="New Category", command=new_category_callback)
        self.file_menu.add_command(label="Open Scripts Folder", command=open_scripts_folder_callback)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Import Script", command=import_script_callback)
        self.file_menu.add_command(label="Export Selected Script", command=export_script_callback)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=exit_callback)
        
    def setup_tools_menu(self, check_dirs_callback, download_github_callback, 
                        clear_console_callback, refresh_view_callback, 
                        focus_command_callback, github_auth_callback=None):
        """Setup the Tools menu with callbacks"""
        self.tools_menu.add_command(label="Check/Create Directories", command=check_dirs_callback)
        self.tools_menu.add_command(label="Download Scripts from GitHub", command=download_github_callback)
        self.tools_menu.add_command(label="Clear Console", command=clear_console_callback)
        self.tools_menu.add_command(label="Refresh View", command=refresh_view_callback)
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="Run Command", command=focus_command_callback)
        
        # Add GitHub authentication option if callback provided
        if github_auth_callback:
            self.tools_menu.add_separator()
            # Default label, will be updated later
            self.github_auth_item = self.tools_menu.add_command(
                label="Sign In with GitHub", 
                command=github_auth_callback
            )
        
    def setup_help_menu(self, about_callback, patreon_callback):
        """Setup the Help menu with callbacks"""
        self.help_menu.add_command(label="About", command=about_callback)
        self.help_menu.add_command(label="Support on Patreon", command=patreon_callback)
    
    def update_github_auth_label(self, label):
        """Update the GitHub auth menu item label"""
        if self.github_auth_item is not None:
            self.tools_menu.entryconfigure(self.github_auth_item, label=label)