#!/usr/bin/env python3
"""
Script Explorer UI component
Main application window for browsing and running Windows scripts
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
import ctypes
import traceback
import re
import threading
import queue
import webbrowser
from PIL import Image, ImageTk
import urllib.parse

from src.ui.tooltip import ToolTip
from src.utils.console_redirector import ConsoleRedirector
from src.utils.script_metadata import parse_script_metadata, get_exe_metadata

class ScriptExplorer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Create file menu
        self.create_menu_bar()
        
        self.title("WinPick - Unlock the Potential of Windows")
        self.geometry("1200x800")  # Increased window size
        self.minsize(900, 600)
        
        # Set up theming with modern colors
        self.configure(bg="#f0f0f0")
        self.style = ttk.Style()
        available_themes = self.style.theme_names()
        if 'clam' in available_themes:
            self.style.theme_use('clam')
        
        # Modern color scheme
        self.primary_color = "#4a86e8"       # Blue primary
        self.secondary_color = "#f0f0f0"     # Light gray background
        self.accent_color = "#ff5252"        # Red accent
        self.text_color = "#333333"          # Dark gray text
        self.bg_dark = "#2d2d2d"             # Dark background for console
        self.bg_light = "#ffffff"            # White background for content areas
        
        # Configure style with modern colors
        self.style.configure("TFrame", background=self.secondary_color)
        self.style.configure("TLabel", background=self.secondary_color, foreground=self.text_color)
        self.style.configure("TButton", background=self.primary_color, foreground="white", font=("Segoe UI", 9))
        self.style.map("TButton", 
                       background=[('active', '#3a76d8'), ('pressed', '#2a66c8')],
                       foreground=[('active', 'white')])
        
        # Define a custom style for admin mode button (red)
        self.style.configure("Admin.TButton", background=self.accent_color, foreground="white")
        self.style.map("Admin.TButton",
                      background=[('active', '#e04242'), ('pressed', '#d03232')])
        
        # Define a style for the category tree
        self.style.configure("Category.Treeview", 
                            background=self.bg_light, 
                            foreground=self.text_color,
                            rowheight=30,
                            font=("Segoe UI", 10))
        self.style.map("Category.Treeview",
                      background=[('selected', self.primary_color)],
                      foreground=[('selected', 'white')])
        
        # Define a style for scripts tree
        self.style.configure("Scripts.Treeview", 
                            background=self.bg_light,
                            foreground=self.text_color,
                            rowheight=30,
                            font=("Segoe UI", 10))
        self.style.map("Scripts.Treeview",
                      background=[('selected', self.primary_color)],
                      foreground=[('selected', 'white')])
        
        # Custom ttk.Entry style
        self.style.configure("TEntry", 
                            fieldbackground=self.bg_light, 
                            foreground=self.text_color,
                            borderwidth=1,
                            font=("Segoe UI", 10))
        
        # Custom ttk.Notebook style for tabs
        self.style.configure("TNotebook", background=self.secondary_color)
        self.style.configure("TNotebook.Tab", 
                            background=self.secondary_color,
                            foreground=self.text_color,
                            padding=[10, 5],
                            font=("Segoe UI", 10))
        self.style.map("TNotebook.Tab",
                      background=[('selected', self.bg_light)],
                      foreground=[('selected', self.primary_color)])
        
        self.categories = [
            "UI Customizations",
            "Performance Tweaks",
            "Privacy Settings",
            "Bloatware Removal",
            "Security Enhancements",
            "System Maintenance",
            "Boot Options",
            "Network Optimizations",
            "Power Management",
            "Default Apps"
        ]
        
        self.script_extensions = ['.ps1', '.py', '.bat', '.cmd', '.exe']
        
        # Setup console output queue and redirector
        self.console_queue = queue.Queue()
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        
        try:
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                base_dir = os.path.dirname(os.path.dirname(script_dir))
            except NameError:
                base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            self.base_dir = os.path.join(base_dir, "WindowsScripts")
            print(f"Creating base directory: {self.base_dir}")
            os.makedirs(self.base_dir, exist_ok=True)
            for category in self.categories:
                category_dir = os.path.join(self.base_dir, category)
                print(f"Creating category folder: {category}")
                os.makedirs(category_dir, exist_ok=True)
            print("All directories created successfully")
        except Exception as e:
            error_msg = f"Error creating directories: {str(e)}\n{traceback.format_exc()}"
            messagebox.showerror("Directory Creation Error", error_msg)
            print(error_msg)
        
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_header_frame()
        self.create_content_frame()
        
        self.tooltip = ToolTip(self.scripts_tree)
        self.scripts_tree.bind("<Motion>", self.show_tooltip)
        
        self._initialize_categories()
        if self.category_tree.get_children():
            first_item = self.category_tree.get_children()[0]
            self.category_tree.selection_set(first_item)
            self.on_category_select(None)
        
        self.redirect_output()
        self.after(100, self.update_console)
        print("Ready")
        self.create_command_input()

        # Update the admin button based on current privileges.
        self.update_admin_indicator()
    
    def create_header_frame(self):
        """Create the header frame with logo and controls"""
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))
        
        # Left side - App title and logo
        self.title_frame = ttk.Frame(self.header_frame)
        self.title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.app_title = ttk.Label(self.title_frame, 
                                  text="WinPick", 
                                  font=("Segoe UI", 20, "bold"),
                                  foreground=self.primary_color)
        self.app_title.pack(side=tk.LEFT, padx=5)
        
        self.app_subtitle = ttk.Label(self.title_frame,
                                     text="Unlock the Potential of Windows",
                                     font=("Segoe UI", 12))
        self.app_subtitle.pack(side=tk.LEFT, padx=5)
        
        # Right side - Button controls
        self.controls_frame = ttk.Frame(self.header_frame)
        self.controls_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Heart icon for Patreon
        try:
            # Create a heart icon (can be replaced with a proper image file)
            heart_canvas = tk.Canvas(self.controls_frame, width=30, height=30, 
                                    bg=self.secondary_color, highlightthickness=0)
            heart_canvas.pack(side=tk.RIGHT, padx=5)
            
            # Draw a heart shape on the canvas
            heart_canvas.create_polygon(15, 7, 10, 3, 5, 7, 3, 12, 5, 17, 15, 25, 25, 17, 
                                      27, 12, 25, 7, 20, 3, 15, 7, 
                                      fill=self.accent_color, outline="")
            heart_canvas.bind("<Button-1>", lambda e: self.open_patreon())
            
            # Add tooltip to the heart icon
            heart_tooltip = ToolTip(heart_canvas)
            heart_canvas.bind("<Enter>", lambda e: heart_tooltip.showtip("Support on Patreon"))
            heart_canvas.bind("<Leave>", lambda e: heart_tooltip.hidetip())
        except Exception as e:
            print(f"Error creating heart icon: {e}")
        
        # Admin button
        self.admin_button = ttk.Button(self.controls_frame, text="", 
                                      command=self.request_admin_elevation)
        self.admin_button.pack(side=tk.RIGHT, padx=5)
        
        # Check Directories button
        self.check_dirs_btn = ttk.Button(self.controls_frame, 
                                        text="Check Directories", 
                                        command=self.check_and_create_directories)
        self.check_dirs_btn.pack(side=tk.RIGHT, padx=5)
        
        # New Script button
        self.new_script_btn = ttk.Button(self.controls_frame, 
                                        text="New Script", 
                                        command=self.create_new_script)
        self.new_script_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_content_frame(self):
        """Create the main content with paned windows"""
        self.content_pane = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.content_pane.pack(fill=tk.BOTH, expand=True)
        
        # Left pane - Categories
        self.left_pane = ttk.Frame(self.content_pane, width=250)
        self.content_pane.add(self.left_pane, weight=1)
        
        # Category header with title and add button
        category_header = ttk.Frame(self.left_pane)
        category_header.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(category_header, 
                 text="Categories", 
                 font=("Segoe UI", 12, "bold"),
                 foreground=self.primary_color).pack(side=tk.LEFT)
        
        add_category_btn = ttk.Button(category_header, 
                                     text="+", 
                                     width=3, 
                                     command=self.add_new_category)
        add_category_btn.pack(side=tk.RIGHT)
        
        # Category tree
        self.category_frame = ttk.Frame(self.left_pane)
        self.category_frame.pack(fill=tk.BOTH, expand=True)
        
        self.category_scrollbar = ttk.Scrollbar(self.category_frame)
        self.category_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.category_tree = ttk.Treeview(self.category_frame, 
                                         show="tree", 
                                         selectmode="browse",
                                         style="Category.Treeview")
        self.category_tree.pack(fill=tk.BOTH, expand=True)
        self.category_scrollbar.config(command=self.category_tree.yview)
        self.category_tree.config(yscrollcommand=self.category_scrollbar.set)
        self.category_tree.bind("<<TreeviewSelect>>", self.on_category_select)
        
        # Right side with scripts list and console output
        self.right_pane = ttk.PanedWindow(self.content_pane, orient=tk.VERTICAL)
        self.content_pane.add(self.right_pane, weight=3)
        
        # Scripts frame
        self.scripts_frame = ttk.Frame(self.right_pane)
        self.right_pane.add(self.scripts_frame, weight=2)
        
        scripts_header = ttk.Frame(self.scripts_frame)
        scripts_header.pack(fill=tk.X, pady=(0, 5))
        
        self.scripts_label = ttk.Label(scripts_header, 
                                     text="Scripts", 
                                     font=("Segoe UI", 12, "bold"),
                                     foreground=self.primary_color)
        self.scripts_label.pack(side=tk.LEFT)
        
        # Add search box to scripts header
        ttk.Label(scripts_header, text="Search:").pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(scripts_header, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<Return>", self.filter_scripts)
        
        search_btn = ttk.Button(scripts_header, text="🔍", width=3, command=self.filter_scripts)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(scripts_header, text="✕", width=3, 
                              command=lambda: [self.search_var.set(""), self.filter_scripts()])
        clear_btn.pack(side=tk.LEFT)
        
        # Scripts tree
        self.tree_frame = ttk.Frame(self.scripts_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.scrollbar = ttk.Scrollbar(self.tree_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.scripts_tree = ttk.Treeview(
            self.tree_frame, 
            columns=("Type", "Name", "Developer", "Description", "Undoable"), 
            show="headings",
            style="Scripts.Treeview"
        )
        self.scripts_tree.pack(fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.scripts_tree.yview)
        self.scripts_tree.config(yscrollcommand=self.scrollbar.set)
        
        self.scripts_tree.heading("Type", text="Type")
        self.scripts_tree.heading("Name", text="Name")
        self.scripts_tree.heading("Developer", text="Developer")
        self.scripts_tree.heading("Description", text="Description")
        self.scripts_tree.heading("Undoable", text="Undoable")
        self.scripts_tree.column("Type", width=60, anchor=tk.W)
        self.scripts_tree.column("Name", width=180, anchor=tk.W)
        self.scripts_tree.column("Developer", width=150, anchor=tk.W)
        self.scripts_tree.column("Description", width=350, anchor=tk.W)
        self.scripts_tree.column("Undoable", width=80, anchor=tk.CENTER)
        
        self.scripts_tree.bind("<Double-1>", self.on_script_double_click)
        self.scripts_tree.bind("<Button-3>", self.on_script_right_click)
        self.scripts_tree.bind("<Button-1>", self.on_script_click)
        
        # Configure tag for items with a developer link
        # self.scripts_tree.tag_configure("has_link", foreground=self.primary_color)
        
        # Console frame
        self.console_frame = ttk.Frame(self.right_pane)
        self.right_pane.add(self.console_frame, weight=1)
        
        self.console_header = ttk.Frame(self.console_frame)
        self.console_header.pack(fill=tk.X, expand=False)
        
        ttk.Label(self.console_header, 
                 text="Console Output", 
                 font=("Segoe UI", 12, "bold"),
                 foreground=self.primary_color).pack(side=tk.LEFT, anchor=tk.W, pady=(0, 5))
        
        self.clear_console_btn = ttk.Button(self.console_header, 
                                          text="Clear Console", 
                                          command=self.clear_console)
        self.clear_console_btn.pack(side=tk.RIGHT, padx=5)
        
        # Console with syntax highlighting
        self.console = scrolledtext.ScrolledText(
            self.console_frame, 
            wrap=tk.WORD, 
            bg=self.bg_dark, 
            fg="#ffffff", 
            insertbackground="#ffffff",
            selectbackground=self.primary_color,
            font=("Consolas", 10))
        self.console.pack(fill=tk.BOTH, expand=True)

    def filter_scripts(self, event=None):
        """Filter scripts based on search text"""
        search_text = self.search_var.get().lower()
        
        # Clear the tree
        for item in self.scripts_tree.get_children():
            self.scripts_tree.delete(item)
        
        # If no search text, reload scripts
        if not search_text:
            selected_items = self.category_tree.selection()
            if selected_items:
                self.on_category_select(None)
            return
        
        # Search across all categories
        found_scripts = []
        
        for category in self.categories:
            category_path = os.path.join(self.base_dir, category)
            if not os.path.exists(category_path):
                continue
                
            for file in os.listdir(category_path):
                file_path = os.path.join(category_path, file)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file)
                    if ext.lower() in self.script_extensions:
                        script_type = ext.lstrip(".").upper()
                        friendly_name, description, undoable, undo_desc, developer, link = parse_script_metadata(file_path)
                        
                        # Check if search text matches any field
                        if (search_text in friendly_name.lower() or 
                            search_text in description.lower() or 
                            search_text in developer.lower()):
                            
                            found_scripts.append((
                                script_type, 
                                friendly_name, 
                                developer, 
                                description, 
                                undoable, 
                                undo_desc, 
                                file_path,
                                link
                            ))
        
        # Update tree with results
        for script_type, friendly_name, developer, description, undoable, undo_desc, script_path, link in sorted(found_scripts, key=lambda x: x[1].lower()):
            # Add link to tags if available
            tags = [script_path, undo_desc]
            if link:
                tags.append(link)
                tags.append("has_link")
                
            self.scripts_tree.insert("", tk.END, 
                values=(script_type, friendly_name, developer, description, undoable), 
                tags=tags
            )
        
        self.scripts_label.config(text=f"Search Results: {len(found_scripts)} scripts")
        print(f"Found {len(found_scripts)} scripts matching '{search_text}'")
            
    def redirect_output(self):
        sys.stdout = ConsoleRedirector(self.console_queue)
        sys.stderr = ConsoleRedirector(self.console_queue)
        print("=== WinPick Console ===")
        print("Console output will appear here.")
        print("Scripts will display their output in this console.")
        print("==========================================")
    
    def restore_output(self):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
    
    def update_console(self):
        try:
            while not self.console_queue.empty():
                text = self.console_queue.get_nowait()
                self.console.insert(tk.END, text)
                self.console.see(tk.END)
                self.console.update_idletasks()
                
                # Apply some basic syntax highlighting
                if "ERROR:" in text or "Error:" in text:
                    start_pos = self.console.search("ERROR:", tk.END+"-50c linestart", tk.END, backwards=True)
                    if not start_pos:
                        start_pos = self.console.search("Error:", tk.END+"-50c linestart", tk.END, backwards=True)
                    if start_pos:
                        line_end = self.console.search("\n", start_pos, tk.END)
                        if not line_end:
                            line_end = tk.END
                        self.console.tag_add("error", start_pos, line_end)
                        self.console.tag_config("error", foreground="#ff5252")
                
                elif "WARNING:" in text or "Warning:" in text:
                    start_pos = self.console.search("WARNING:", tk.END+"-50c linestart", tk.END, backwards=True)
                    if not start_pos:
                        start_pos = self.console.search("Warning:", tk.END+"-50c linestart", tk.END, backwards=True)
                    if start_pos:
                        line_end = self.console.search("\n", start_pos, tk.END)
                        if not line_end:
                            line_end = tk.END
                        self.console.tag_add("warning", start_pos, line_end)
                        self.console.tag_config("warning", foreground="#ffc107")
                
                elif "===" in text:
                    start_pos = self.console.search("===", tk.END+"-50c linestart", tk.END, backwards=True)
                    if start_pos:
                        line_end = self.console.search("\n", start_pos, tk.END)
                        if not line_end:
                            line_end = tk.END
                        self.console.tag_add("header", start_pos, line_end)
                        self.console.tag_config("header", foreground="#4a86e8", font=("Consolas", 10, "bold"))
                
        except Exception as e:
            self.old_stdout.write(f"Error updating console: {str(e)}\n")
        self.after(100, self.update_console)
    
    def open_patreon(self):
        """Open the Patreon page in a web browser"""
        webbrowser.open("https://www.patreon.com/c/mikethetech")
        print("Opening Patreon page...")
    
    def clear_console(self):
        self.console.delete(1.0, tk.END)
        print("Console cleared.")
    
    def on_category_select(self, event):
        selected_items = self.category_tree.selection()
        if not selected_items:
            return
        item_id = selected_items[0]
        category_path = self.category_tree.item(item_id, 'values')[0]
        category_name = self.category_tree.item(item_id, 'text')
        self.scripts_label.config(text=f"Scripts - {category_name}")
        for item in self.scripts_tree.get_children():
            self.scripts_tree.delete(item)
        os.makedirs(category_path, exist_ok=True)
        scripts = []
        try:
            for file in os.listdir(category_path):
                file_path = os.path.join(category_path, file)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file)
                    if ext.lower() in self.script_extensions:
                        script_type = ext.lstrip(".").upper()
                        friendly_name, description, undoable, undo_desc, developer, link = parse_script_metadata(file_path)
                        scripts.append((script_type, friendly_name, developer, description, undoable, undo_desc, file_path, link))
        except Exception as e:
            print(f"Error reading scripts: {str(e)}")
        for script_type, friendly_name, developer, description, undoable, undo_desc, script_path, link in sorted(scripts, key=lambda x: x[1].lower()):
            # Add link to tags if available
            tags = [script_path, undo_desc]
            if link:
                tags.append(link)
                tags.append("has_link")
            
            self.scripts_tree.insert("", tk.END, 
                values=(script_type, friendly_name, developer, description, undoable), 
                tags=tags
            )
        print(f"Found {len(scripts)} scripts in {category_name}")
    
    def show_tooltip(self, event):
        item = self.scripts_tree.identify_row(event.y)
        if item:
            column = self.scripts_tree.identify_column(event.x)
            if column == "#4":  # Description column
                values = self.scripts_tree.item(item, 'values')
                if len(values) >= 4:
                    description = values[3]
                    self.tooltip.showtip(description)
                    return
            elif column == "#5":  # Undoable column
                values = self.scripts_tree.item(item, 'values')
                tags = self.scripts_tree.item(item, 'tags')
                if len(values) >= 5 and len(tags) >= 2:
                    undoable = values[4]
                    undo_desc = tags[1]
                    if undoable == "Yes" and undo_desc:
                        self.tooltip.showtip(f"Undo will: {undo_desc}")
                        return
                    elif undoable == "No":
                        self.tooltip.showtip("This script cannot be undone")
                        return
            elif column == "#3":  # Developer column
                tags = self.scripts_tree.item(item, 'tags')
                if "has_link" in tags:
                    self.tooltip.showtip("Click to visit developer's link")
                    return
        self.tooltip.hidetip()
    
    def on_script_click(self, event):
        item = self.scripts_tree.identify_row(event.y)
        if not item:
            return
            
        column = self.scripts_tree.identify_column(event.x)
        if column != "#3":  # Developer column
            return
            
        tags = self.scripts_tree.item(item, 'tags')
        # Check if this item has a link (should be the third tag if present)
        if len(tags) >= 3 and "has_link" in tags:
            for tag in tags:
                # Check if the tag looks like a URL
                if tag.startswith(("http://", "https://", "www.")):
                    try:
                        # Open the URL in the default browser
                        url = tag
                        if url.startswith("www."):
                            url = "http://" + url
                        
                        print(f"Opening developer link: {url}")
                        webbrowser.open(url)
                        break
                    except Exception as e:
                        print(f"Error opening link: {str(e)}")
                        messagebox.showerror("Link Error", f"Failed to open the developer link: {str(e)}")
    
    def on_script_double_click(self, event):
        selected_items = self.scripts_tree.selection()
        if not selected_items:
            return
        item = selected_items[0]
        values = self.scripts_tree.item(item, 'values')
        if values[4] == "Yes":
            self.show_script_action_dialog(item)
        else:
            script_path = self.scripts_tree.item(item, "tags")[0]
            self.run_script(script_path)
    
    def show_script_action_dialog(self, item):
        values = self.scripts_tree.item(item, 'values')
        tags = self.scripts_tree.item(item, 'tags')
        script_path = tags[0]
        undo_desc = tags[1] if len(tags) > 1 else ""
        
        dialog = tk.Toplevel(self)
        dialog.title("Script Action")
        dialog.geometry("500x280")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=self.secondary_color)
        
        # Make dialog appear centered on parent window
        x = self.winfo_x() + (self.winfo_width() // 2) - (500 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (280 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Script title with icon for script type
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        script_type = values[0].lower()
        script_icon = "📄"  # Default icon
        if script_type == "ps1":
            script_icon = "⚙️"
        elif script_type == "py":
            script_icon = "🐍"
        elif script_type == "bat" or script_type == "cmd":
            script_icon = "🖥️"
        elif script_type == "exe":
            script_icon = "🚀"
            
        ttk.Label(title_frame, 
                 text=f"{script_icon} {values[1]}", 
                 font=("Segoe UI", 14, "bold"),
                 foreground=self.primary_color).pack(anchor=tk.CENTER)
        
        # Information frame
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        # Script details
        ttk.Label(info_frame, 
                 text="Type:", 
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=3)
        ttk.Label(info_frame, 
                 text=values[0]).grid(row=0, column=1, sticky=tk.W, pady=3, padx=10)
        ttk.Label(info_frame, 
                 text="Developer:", 
                 font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=3)
        ttk.Label(info_frame, 
                 text=values[2]).grid(row=1, column=1, sticky=tk.W, pady=3, padx=10)
        ttk.Label(info_frame, 
                 text="Description:", 
                 font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky=tk.NW, pady=3)
        desc_label = ttk.Label(info_frame, 
                             text=values[3],
                             wraplength=350)
        desc_label.grid(row=2, column=1, sticky=tk.W, pady=3, padx=10)
        
        if undo_desc:
            ttk.Label(info_frame, 
                     text="Undo Action:", 
                     font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky=tk.NW, pady=3)
            undo_label = ttk.Label(info_frame, 
                                 text=undo_desc,
                                 wraplength=350)
            undo_label.grid(row=3, column=1, sticky=tk.W, pady=3, padx=10)
        
        # Action buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=(15, 0))
        
        # Run button with icon
        run_btn = ttk.Button(button_frame, 
                           text="▶ Run Script", 
                           width=15,
                           command=lambda: [dialog.destroy(), self.run_script(script_path)])
        run_btn.pack(side=tk.LEFT, padx=5)
        
        # Undo button with icon
        undo_btn = ttk.Button(button_frame, 
                            text="↩ Undo Script", 
                            width=15,
                            command=lambda: [dialog.destroy(), self.run_script(script_path, undo=True)])
        undo_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        ttk.Button(button_frame, 
                  text="Cancel", 
                  width=15,
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def on_script_right_click(self, event):
        item = self.scripts_tree.identify_row(event.y)
        if item:
            self.scripts_tree.selection_set(item)
            values = self.scripts_tree.item(item, 'values')
            script_path = self.scripts_tree.item(item, "tags")[0]
            script_type = values[0].lower()
            popup_menu = tk.Menu(self, tearoff=0)
            
            # Modern styling for popup menu
            popup_menu.configure(bg=self.bg_light, fg=self.text_color, activebackground=self.primary_color, activeforeground="white", font=("Segoe UI", 9))
            
            popup_menu.add_command(label="▶  Run", command=lambda: self.run_script(script_path))
            if values[4] == "Yes":
                popup_menu.add_command(label="↩  Undo", command=lambda: self.run_script(script_path, undo=True))
            popup_menu.add_separator()
            popup_menu.add_command(label="🔒  Run as Administrator", command=lambda: self.run_script_as_admin(script_path))
            if values[4] == "Yes":
                popup_menu.add_command(label="🔒  Undo as Administrator", command=lambda: self.run_script_as_admin(script_path, undo=True))
            popup_menu.add_separator()
            if script_type != "exe":
                popup_menu.add_command(label="✏️  Edit Script", command=lambda: self.edit_script(script_path))
            popup_menu.add_command(label="🗑️  Delete Script", command=lambda: self.delete_script(script_path))
            popup_menu.add_separator()
            popup_menu.add_command(label="📦  Install Dependencies", command=lambda: self.install_dependencies(script_path))
            popup_menu.add_separator()
            popup_menu.add_command(label="📂  Open Containing Folder", command=lambda: self.open_containing_folder(script_path))
            try:
                popup_menu.tk_popup(event.x_root, event.y_root, 0)
            finally:
                popup_menu.grab_release()

    
    def edit_script(self, script_path):
        try:
            os.startfile(script_path)
            print(f"Opened {os.path.basename(script_path)} for editing")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open the script for editing: {str(e)}")
    
    def delete_script(self, script_path):
        script_name = os.path.basename(script_path)
        
        # Create a modern confirmation dialog
        confirm_dialog = tk.Toplevel(self)
        confirm_dialog.title("Confirm Deletion")
        confirm_dialog.geometry("400x180")
        confirm_dialog.transient(self)
        confirm_dialog.grab_set()
        confirm_dialog.configure(bg=self.secondary_color)
        
        # Center the dialog on the parent window
        x = self.winfo_x() + (self.winfo_width() // 2) - (400 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (180 // 2)
        confirm_dialog.geometry(f"+{x}+{y}")
        
        dialog_frame = ttk.Frame(confirm_dialog, padding=20)
        dialog_frame.pack(fill=tk.BOTH, expand=True)
        
        # Warning icon and message
        warning_frame = ttk.Frame(dialog_frame)
        warning_frame.pack(fill=tk.X, pady=10)
        
        # Create a warning symbol
        warning_label = ttk.Label(warning_frame, 
                                 text="⚠️", 
                                 font=("Segoe UI", 24),
                                 foreground=self.accent_color)
        warning_label.pack(side=tk.LEFT, padx=(0, 10))
        
        message_frame = ttk.Frame(warning_frame)
        message_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(message_frame, 
                 text="Delete Script?", 
                 font=("Segoe UI", 12, "bold"),
                 foreground=self.text_color).pack(anchor=tk.W)
        
        ttk.Label(message_frame, 
                 text=f"Are you sure you want to delete '{script_name}'?",
                 wraplength=300).pack(anchor=tk.W, pady=5)
        
        ttk.Label(message_frame,
                 text="This action cannot be undone.",
                 foreground=self.accent_color).pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(dialog_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def confirm_delete():
            confirm_dialog.destroy()
            try:
                os.remove(script_path)
                print(f"Deleted script: {script_name}")
                selection = self.category_tree.selection()
                if selection:
                    self.on_category_select(None)
            except Exception as e:
                error_msg = f"Failed to delete script: {str(e)}"
                messagebox.showerror("Deletion Error", error_msg)
                print(error_msg)
        
        ttk.Button(button_frame, 
                  text="Cancel", 
                  width=15,
                  command=confirm_dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        delete_btn = ttk.Button(button_frame, 
                              text="Delete", 
                              width=15,
                              style="Admin.TButton",
                              command=confirm_delete)
        delete_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_process_output_thread(self, process, script_name, undo=False):
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
    
    def run_script(self, script_path, undo=False):
        from src.utils.script_runner import run_script
        script_name = os.path.basename(script_path)
        try:
            process = run_script(script_path, undo)
            self.create_process_output_thread(process, script_name, undo)
            action_text = "Undoing" if undo else "Running"
            print(f"{action_text} {script_name}")
        except Exception as e:
            error_msg = f"Failed to {'undo' if undo else 'run'} the script: {str(e)}"
            messagebox.showerror("Error", error_msg)
            print(f"\nERROR: {error_msg}\n")
    
    def run_script_as_admin(self, script_path, undo=False):
        from src.utils.script_runner import run_script_as_admin
        script_name = os.path.basename(script_path)
        try:
            success = run_script_as_admin(script_path, undo)
            if success:
                action_text = "Undoing" if undo else "Running"
                print(f"{action_text} {script_name} as Administrator")
                print(f"\n=== Attempting to {action_text.lower()} as Administrator: {script_name} ===")
                print("Note: Output will appear in a separate console window when running as Administrator")
        except Exception as e:
            action_text = "Undoing" if undo else "Running"
            error_msg = f"Failed to {action_text.lower()} the script as Administrator: {str(e)}"
            messagebox.showerror("Error", error_msg)
            print(f"\nERROR: {error_msg}\n")
    
    def create_new_script(self):
        from src.ui.script_creator import create_new_script_dialog
        selected_items = self.category_tree.selection()
        if not selected_items:
            messagebox.showinfo("Select Category", "Please select a category first.")
            return
        item_id = selected_items[0]
        category_path = self.category_tree.item(item_id, 'values')[0]
        category_name = self.category_tree.item(item_id, 'text')
        create_new_script_dialog(self, category_name, category_path, self.on_category_select)
    
    def check_and_create_directories(self):
        try:
            if not os.path.exists(self.base_dir):
                print(f"Base directory does not exist. Creating: {self.base_dir}")
                os.mkdir(self.base_dir)
                print(f"Created base directory: {self.base_dir}")
                messagebox.showinfo("Directory Created", f"Created base directory: {self.base_dir}")
            else:
                print(f"Base directory already exists: {self.base_dir}")
            self.detect_custom_folders()
            missing_dirs = []
            for category in self.categories:
                category_dir = os.path.join(self.base_dir, category)
                if not os.path.exists(category_dir):
                    missing_dirs.append(category)
            if missing_dirs:
                print(f"Creating {len(missing_dirs)} missing directories...")
                for category in missing_dirs:
                    category_dir = os.path.join(self.base_dir, category)
                    try:
                        os.mkdir(category_dir)
                        print(f"Created directory: {category_dir}")
                    except Exception as e:
                        error_msg = f"Error creating {category_dir}: {str(e)}"
                        messagebox.showerror("Directory Creation Error", error_msg)
                        print(f"ERROR: {error_msg}")
                messagebox.showinfo("Directories Created", f"Created {len(missing_dirs)} missing directories: {', '.join(missing_dirs)}")
            else:
                print("All category directories exist")
                messagebox.showinfo("Directories Exist", "All script directories already exist.")
            self._initialize_categories()
            selected_items = self.category_tree.selection()
            if selected_items:
                self.on_category_select(None)
        except Exception as e:
            error_msg = f"Error checking/creating directories: {str(e)}\n{traceback.format_exc()}"
            messagebox.showerror("Directory Check Error", error_msg)
            print(f"ERROR: {error_msg}")
    
    def open_containing_folder(self, script_path):
        folder_path = os.path.dirname(script_path)
        os.startfile(folder_path)
        print(f"Opened folder: {folder_path}")
    
    def create_menu_bar(self):
        self.menu_bar = tk.Menu(self)
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New Script", command=self.create_new_script)
        self.file_menu.add_command(label="New Category", command=self.add_new_category)
        self.file_menu.add_command(label="Open Scripts Folder", command=self.open_scripts_folder)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Import Script", command=self.import_script)
        self.file_menu.add_command(label="Export Selected Script", command=self.export_script)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit)
        
        # Tools menu
        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.tools_menu.add_command(label="Check/Create Directories", command=self.check_and_create_directories)
        self.tools_menu.add_command(label="Clear Console", command=self.clear_console)
        self.tools_menu.add_command(label="Refresh View", command=self.refresh_view)
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="Run Command", command=self.focus_command_input)
        
        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.show_about)
        self.help_menu.add_command(label="Support on Patreon", command=self.open_patreon)
        
        # Add menus to menu bar
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Tools", menu=self.tools_menu)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        
        self.config(menu=self.menu_bar)
    
    def create_command_input(self):
        # Add command input frame with modern styling
        self.command_frame = ttk.Frame(self, padding=(10, 10))
        self.command_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Label(self.command_frame, 
                 text="Command:", 
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Command input with modern styling
        self.command_entry = ttk.Entry(self.command_frame, width=50, font=("Consolas", 10))
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
        self.command_entry.bind("<Return>", self.execute_command)
        
        # Modern execute button
        self.execute_btn = ttk.Button(self.command_frame, 
                                    text="Execute", 
                                    width=15,
                                    command=lambda: self.execute_command(None))
        self.execute_btn.pack(side=tk.RIGHT, padx=5)
    
    def focus_command_input(self):
        self.command_entry.focus_set()
    
    def execute_command(self, event=None):
        command = self.command_entry.get().strip()
        if not command:
            return
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
            self.command_entry.delete(0, tk.END)
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}\n{traceback.format_exc()}"
            print(f"\nERROR: {error_msg}\n")
    
    def capture_command_output(self, process, command):
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
    
    def import_script(self):
        selected_items = self.category_tree.selection()
        if not selected_items:
            messagebox.showinfo("Select Category", "Please select a category first.")
            return
        item_id = selected_items[0]
        category_path = self.category_tree.item(item_id, 'values')[0]
        category_name = self.category_tree.item(item_id, 'text')
        
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
            return
        try:
            import shutil
            script_name = os.path.basename(script_path)
            destination = os.path.join(category_path, script_name)
            if os.path.exists(destination):
                if not messagebox.askyesno("File Exists", f"{script_name} already exists. Overwrite?"):
                    return
            shutil.copy2(script_path, destination)
            print(f"Imported {script_name}")
            self.on_category_select(None)
        except Exception as e:
            error_msg = f"Error importing script: {str(e)}\n{traceback.format_exc()}"
            messagebox.showerror("Import Error", error_msg)
            print(f"ERROR: {error_msg}")
    
    def export_script(self):
        selected_items = self.scripts_tree.selection()
        if not selected_items:
            messagebox.showinfo("Select Script", "Please select a script to export.")
            return
        item = selected_items[0]
        script_path = self.scripts_tree.item(item, "tags")[0]
        script_name = os.path.basename(script_path)
        destination = filedialog.asksaveasfilename(
            title="Export Script",
            initialfile=script_name,
            defaultextension=os.path.splitext(script_name)[1]
        )
        if not destination:
            return
        try:
            import shutil
            shutil.copy2(script_path, destination)
            print(f"Exported {script_name} to {destination}")
        except Exception as e:
            error_msg = f"Error exporting script: {str(e)}\n{traceback.format_exc()}"
            messagebox.showerror("Export Error", error_msg)
            print(f"ERROR: {error_msg}")
    
    def open_scripts_folder(self):
        os.startfile(self.base_dir)
        print(f"Opened scripts folder: {self.base_dir}")
    
    def show_about(self):
        """Show the about dialog with enhanced dependency information"""
        # Create a modern About dialog
        about_window = tk.Toplevel(self)
        about_window.title("About WinPick")
        about_window.geometry("600x500")
        about_window.transient(self)
        about_window.grab_set()
        about_window.configure(bg=self.secondary_color)
        
        # Center on parent window
        x = self.winfo_x() + (self.winfo_width() // 2) - (600 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (500 // 2)
        about_window.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(about_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo and title
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create a simple logo using a canvas
        logo_canvas = tk.Canvas(header_frame, width=64, height=64, 
                            bg=self.secondary_color, highlightthickness=0)
        logo_canvas.pack(side=tk.LEFT)
        

        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, padx=15)
        
        ttk.Label(title_frame, 
                text="WinPick", 
                font=("Segoe UI", 24, "bold"),
                foreground=self.primary_color).pack(anchor=tk.W)
        
        ttk.Label(title_frame, 
                text="Windows Script Manager",
                font=("Segoe UI", 12)).pack(anchor=tk.W)
        
        # Version and build info
        version_frame = ttk.Frame(frame)
        version_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(version_frame, 
                text="Version 25.4.10",
                font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        
        ttk.Label(version_frame,
                text="Built with ♥ for Windows 11 users",
                foreground=self.accent_color).pack(side=tk.RIGHT)
        
        # Content in a scrolled text widget
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        text = scrolledtext.ScrolledText(content_frame, 
                                        wrap=tk.WORD, 
                                        bg=self.bg_light, 
                                        font=("Segoe UI", 10),
                                        padx=10, pady=10,
                                        height=12)
        text.pack(fill=tk.BOTH, expand=True)
        
        # Collect developer info
        developer_set = set()
        # New: Collect dependencies from all scripts
        import re
        dependency_set = set()
        
        if os.path.exists(self.base_dir):
            for category in os.listdir(self.base_dir):
                category_path = os.path.join(self.base_dir, category)
                if os.path.isdir(category_path):
                    for file in os.listdir(category_path):
                        file_path = os.path.join(category_path, file)
                        if os.path.isfile(file_path):
                            _, ext = os.path.splitext(file)
                            if ext.lower() in self.script_extensions:
                                # parse_script_metadata returns (friendly_name, description, undoable, undo_desc, developer, link)
                                _, _, _, _, developer, _ = parse_script_metadata(file_path)
                                if developer.strip():
                                    developer_set.add(developer.strip())
                                
                                # Scan for dependencies in Python scripts
                                if ext.lower() == '.py':
                                    try:
                                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                            content = f.read()
                                        
                                        # Find import statements
                                        import_matches = re.findall(r'^\s*import\s+([a-zA-Z0-9_.,\s]+)', content, re.MULTILINE)
                                        from_import_matches = re.findall(r'^\s*from\s+([a-zA-Z0-9_.]+)\s+import', content, re.MULTILINE)
                                        
                                        # Process regular imports (may have multiple modules per line)
                                        for match in import_matches:
                                            modules = [m.strip() for m in match.split(',')]
                                            for module in modules:
                                                # Extract the base module name (before any "as" keyword)
                                                base_module = module.split(' as ')[0].strip()
                                                # Get just the top-level package name
                                                top_module = base_module.split('.')[0]
                                                if top_module not in ['os', 'sys', 'io', 're', 'time', 'datetime', 'math', 
                                                                    'json', 'random', 'threading', 'queue', 'tkinter', 'ctypes',
                                                                    'argparse', 'subprocess', 'traceback']:  # Common built-ins
                                                    dependency_set.add(top_module)
                                        
                                        # Process from imports
                                        for match in from_import_matches:
                                            # Get just the top-level package name
                                            top_module = match.split('.')[0]
                                            if top_module not in ['os', 'sys', 'io', 're', 'time', 'datetime', 'math', 
                                                                'json', 'random', 'threading', 'queue', 'tkinter', 'ctypes',
                                                                'argparse', 'subprocess', 'traceback']:  # Common built-ins
                                                dependency_set.add(top_module)
                                                
                                    except Exception as e:
                                        print(f"Error scanning dependencies in {file_path}: {str(e)}")
                                    
                                # Scan for dependencies in PowerShell scripts
                                elif ext.lower() == '.ps1':
                                    try:
                                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                            content = f.read()
                                        
                                        # Find import-module statements
                                        module_matches = re.findall(r'Import-Module\s+([a-zA-Z0-9_.-]+)', content, re.IGNORECASE)
                                        for module in module_matches:
                                            dependency_set.add(f"PS:{module.strip()}")
                                    except Exception as e:
                                        print(f"Error scanning dependencies in {file_path}: {str(e)}")
        
        # Build the about text
        about_text = """This application helps you manage and run Windows scripts.

    Features:
    - Organize scripts by category
    - Run scripts with or without admin rights
    - Undo script actions when supported
    - Advanced console output display
    - Modern user interface
    """
        
        if developer_set:
            # Sort the developer names and build the credits text
            developers_str = ", ".join(sorted(developer_set))
            credits_text = "\n\nThanks/Credits to the following Script Developers:\n" + developers_str
            about_text += credits_text
        
        # Add dependency information
        if dependency_set:
            # Sort and format dependencies
            python_deps = sorted([dep for dep in dependency_set if not dep.startswith("PS:")])
            ps_deps = sorted([dep[3:] for dep in dependency_set if dep.startswith("PS:")])
            
            deps_text = "\n\nThe scripts in this package use the following dependencies. Thanks to all developers!\n\n"
            
            if python_deps:
                deps_text += "Python Dependencies:\n" + ", ".join(python_deps)
            
            if ps_deps and python_deps:
                deps_text += "\n\nPowerShell Dependencies:\n" + ", ".join(ps_deps)
            elif ps_deps:
                deps_text += "PowerShell Dependencies:\n" + ", ".join(ps_deps)
                
            about_text += deps_text
        
        # Append developer info and Patreon support link
        developer_info = """

    Developed by MikeTheTech
    Support me on Patreon: https://www.patreon.com/c/mikethetech
    """
        about_text += developer_info
        
        text.insert(tk.END, about_text)
        text.config(state=tk.DISABLED)
        
        # Bottom buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=(20, 0))
        
        ttk.Button(button_frame, 
                text="Support on Patreon", 
                width=20,
                command=self.open_patreon).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, 
                text="OK", 
                width=15,
                command=about_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def refresh_view(self):
        try:
            current_selection = None
            selected_items = self.category_tree.selection()
            if selected_items:
                current_selection = self.category_tree.item(selected_items[0], 'text')
            self._initialize_categories()
            if current_selection:
                for item_id in self.category_tree.get_children():
                    if self.category_tree.item(item_id, 'text') == current_selection:
                        self.category_tree.selection_set(item_id)
                        self.category_tree.see(item_id)
                        self.on_category_select(None)
                        break
            elif self.category_tree.get_children():
                first_item = self.category_tree.get_children()[0]
                self.category_tree.selection_set(first_item)
                self.on_category_select(None)
            print("View refreshed")
        except Exception as e:
            error_msg = f"Error refreshing view: {str(e)}\n{traceback.format_exc()}"
            print(f"ERROR: {error_msg}")
    
    def detect_custom_folders(self):
        try:
            base_dirs = [d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))]
            new_categories = []
            for dir_name in base_dirs:
                if dir_name not in self.categories:
                    category_path = os.path.join(self.base_dir, dir_name)
                    self.category_tree.insert('', 'end', text=dir_name, values=(category_path,), tags=('category',))
                    new_categories.append(dir_name)
                    self.categories.append(dir_name)
            if new_categories:
                print(f"Added {len(new_categories)} new categories: {', '.join(new_categories)}")
            for item_id in self.category_tree.get_children():
                category_path = self.category_tree.item(item_id, 'values')[0]
                self._add_subcategories(item_id, category_path)
            return True
        except Exception as e:
            error_msg = f"Error detecting custom folders: {str(e)}\n{traceback.format_exc()}"
            print(f"ERROR: {error_msg}")
            return False

    def install_dependencies(self, script_path):
        import re, sys, subprocess, os
        from tkinter import messagebox

        # Only process Python scripts
        if not script_path.lower().endswith(".py"):
            messagebox.showinfo("Unsupported", "Dependency installation is only available for Python scripts.")
            return

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read script: {str(e)}")
            return

        # Find modules using simple regex patterns
        imports = re.findall(r'^\s*import\s+([a-zA-Z0-9_]+)', source, re.MULTILINE)
        from_imports = re.findall(r'^\s*from\s+([a-zA-Z0-9_]+)\s+import', source, re.MULTILINE)
        modules = set(imports + from_imports)
        print("Identified potential dependencies:", modules)

        # Filter out built-in modules and check if modules can be imported
        import_types = sys.builtin_module_names
        missing_modules = []
        for mod in modules:
            if mod in import_types:
                continue
            try:
                __import__(mod)
            except ImportError:
                missing_modules.append(mod)
        if not missing_modules:
            messagebox.showinfo("Dependencies", "All Python module dependencies appear to be satisfied.")
            print("All dependencies are installed.")
            return
        print("Missing modules:", missing_modules)

        # Create a modern dependency installation dialog
        dep_window = tk.Toplevel(self)
        dep_window.title("Install Dependencies")
        dep_window.geometry("500x350")
        dep_window.transient(self)
        dep_window.grab_set()
        dep_window.configure(bg=self.secondary_color)
        
        # Center on parent window
        x = self.winfo_x() + (self.winfo_width() // 2) - (500 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (350 // 2)
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
    
    def _initialize_categories(self):
        try:
            for item in self.category_tree.get_children():
                self.category_tree.delete(item)
            os.makedirs(self.base_dir, exist_ok=True)
            for category in sorted(self.categories):
                category_path = os.path.join(self.base_dir, category)
                os.makedirs(category_path, exist_ok=True)
                self.category_tree.insert('', 'end', text=category, values=(category_path,), tags=('category',))
            self.detect_custom_folders()
        except Exception as e:
            error_msg = f"Error initializing categories: {str(e)}\n{traceback.format_exc()}"
            print(f"ERROR: {error_msg}")
    
    def _add_subcategories(self, parent_id, parent_path):
        try:
            subdirs = [d for d in os.listdir(parent_path) if os.path.isdir(os.path.join(parent_path, d))]
            for subdir in sorted(subdirs):
                subdir_path = os.path.join(parent_path, subdir)
                subcategory_id = self.category_tree.insert(parent_id, 'end', text=subdir, values=(subdir_path,), tags=('subcategory',))
                self._add_subcategories(subcategory_id, subdir_path)
        except Exception as e:
            print(f"Error adding subcategories for {parent_path}: {str(e)}")
    
    def add_new_category(self):
        # Create a modern category dialog
        dialog = tk.Toplevel(self)
        dialog.title("New Category")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=self.secondary_color)
        
        # Center the dialog
        x = self.winfo_x() + (self.winfo_width() // 2) - (400 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (200 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, 
                 text="Create New Category", 
                 font=("Segoe UI", 14, "bold"),
                 foreground=self.primary_color).pack(pady=(0, 20))
        
        ttk.Label(frame, 
                 text="Enter name for the new category:").pack(anchor=tk.W, pady=(0, 5))
        
        name_var = tk.StringVar()
        name_entry = ttk.Entry(frame, textvariable=name_var, width=40)
        name_entry.pack(fill=tk.X, pady=(0, 20))
        name_entry.focus_set()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        def create_category():
            new_category = name_var.get().strip()
            if not new_category:
                messagebox.showerror("Error", "Please enter a category name.")
                return
                
            clean_name = re.sub(r'[^a-zA-Z0-9_\-\s]', '', new_category)
            if not clean_name:
                messagebox.showerror("Invalid Name", "Please enter a valid category name.")
                return
                
            if clean_name in self.categories:
                messagebox.showerror("Category Exists", f"The category '{clean_name}' already exists.")
                return
                
            category_path = os.path.join(self.base_dir, clean_name)
            try:
                os.makedirs(category_path, exist_ok=True)
                self.categories.append(clean_name)
                self.detect_custom_folders()
                
                # Select the new category
                for item_id in self.category_tree.get_children():
                    if self.category_tree.item(item_id, 'text') == clean_name:
                        self.category_tree.selection_set(item_id)
                        self.category_tree.see(item_id)
                        self.on_category_select(None)
                        break
                        
                print(f"Created new category: {clean_name}")
                dialog.destroy()
            except Exception as e:
                error_msg = f"Error creating category: {str(e)}\n{traceback.format_exc()}"
                messagebox.showerror("Category Creation Error", error_msg)
                print(f"ERROR: {error_msg}")
        
        ttk.Button(button_frame, 
                  text="Cancel", 
                  width=15,
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame, 
                  text="Create", 
                  width=15,
                  command=create_category).pack(side=tk.RIGHT, padx=5)
    
    def update_admin_indicator(self):
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin:
                self.admin_button.config(text="Administrator Mode", style="TButton")
            else:
                self.admin_button.config(text="Request Admin Rights", style="Admin.TButton")
                print("WARNING: Application is not running with administrative privileges. Click the 'Request Admin Rights' button to enable admin privileges.")
        except Exception as e:
            print(f"Error checking admin status: {str(e)}")
    
    def request_admin_elevation(self, event=None):
        try:
            if ctypes.windll.shell32.IsUserAnAdmin():
                messagebox.showinfo("Administrator", "Application is already running as Administrator.")
                print("Application is already running as Administrator.")
            else:
                if messagebox.askyesno("Administrator Rights", 
                                     "This will restart the application with administrator privileges. Continue?"):
                    print("Requesting administrator privileges... Relaunching as admin.")
                    params = " ".join([f'"{arg}"' for arg in sys.argv])
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
                    self.quit()
        except Exception as e:
            print(f"Failed to request admin elevation: {e}")
    
    def __del__(self):
        try:
            self.restore_output()
        except:
            pass

if __name__ == "__main__":
    app = ScriptExplorer()
    app.mainloop()