#!/usr/bin/env python3
"""
Script View Module
Handles the script list display and interactions
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

from src.ui.tooltip import ToolTip
from src.utils.script_metadata import parse_script_metadata
from src.utils.message_handler import MessageHandler


class ScriptView:
    def __init__(self, parent, primary_color="#4a86e8", rating_system=None):
        self.parent = parent
        self.primary_color = primary_color
        self.script_extensions = ['.ps1', '.py', '.bat', '.cmd', '.exe']
        self.rating_system = rating_system
        
        # Create UI components
        self.frame = ttk.Frame(parent)
        self.create_script_view()
        
    def create_script_view(self):
        """Create the script list view UI"""
        scripts_header = ttk.Frame(self.frame)
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
        self.tree_frame = ttk.Frame(self.frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.scrollbar = ttk.Scrollbar(self.tree_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add Rating column to the tree
        self.scripts_tree = ttk.Treeview(
            self.tree_frame, 
            columns=("Type", "Name", "Developer", "Description", "Rating", "Undoable"), 
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
        self.scripts_tree.heading("Rating", text="Rating")
        self.scripts_tree.heading("Undoable", text="Undoable")
        self.scripts_tree.column("Type", width=60, anchor=tk.W)
        self.scripts_tree.column("Name", width=180, anchor=tk.W)
        self.scripts_tree.column("Developer", width=150, anchor=tk.W)
        self.scripts_tree.column("Description", width=250, anchor=tk.W)
        self.scripts_tree.column("Rating", width=80, anchor=tk.CENTER)
        self.scripts_tree.column("Undoable", width=80, anchor=tk.CENTER)
        
        # Create tooltip for the tree
        self.tooltip = ToolTip(self.scripts_tree)
        self.scripts_tree.bind("<Motion>", self.show_tooltip)
        
        # Set up event bindings - these will be connected to callbacks later
        self.scripts_tree.bind("<Double-1>", lambda e: print("Double-click event"))
        self.scripts_tree.bind("<Button-3>", lambda e: print("Right-click event"))
        self.scripts_tree.bind("<Button-1>", self.on_script_click)
        
    def set_callbacks(self, double_click_callback, right_click_callback):
        """Set callbacks for tree item interactions"""
        self.scripts_tree.bind("<Double-1>", double_click_callback)
        self.scripts_tree.bind("<Button-3>", right_click_callback)
        
    def set_rating_system(self, rating_system):
        """Set the rating system for the script view"""
        self.rating_system = rating_system
        
    def load_scripts(self, category_path, category_name):
        """Load scripts from the specified category path"""
        self.scripts_label.config(text=f"Scripts - {category_name}")
        
        # Clear existing items
        for item in self.scripts_tree.get_children():
            self.scripts_tree.delete(item)
            
        # Ensure directory exists
        os.makedirs(category_path, exist_ok=True)
        
        # Load and sort scripts
        scripts = []
        try:
            for file in os.listdir(category_path):
                file_path = os.path.join(category_path, file)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file)
                    if ext.lower() in self.script_extensions:
                        script_type = ext.lstrip(".").upper()
                        friendly_name, description, undoable, undo_desc, developer, link = parse_script_metadata(file_path)
                        
                        # Get rating if rating system is available
                        rating_text = ""
                        rating_value = None
                        if self.rating_system:
                            avg_rating = self.rating_system.get_average_rating(file_path, friendly_name)
                            if avg_rating:
                                rating_text = f"{avg_rating}/5"
                                rating_value = avg_rating
                        
                        scripts.append((
                            script_type, 
                            friendly_name, 
                            developer, 
                            description, 
                            rating_text,  # Add rating text
                            undoable, 
                            undo_desc, 
                            file_path, 
                            link,
                            rating_value  # Add rating value for sorting
                        ))
        except Exception as e:
            print(f"Error reading scripts: {str(e)}")
            
        # Add scripts to tree
        for script_type, friendly_name, developer, description, rating_text, undoable, undo_desc, script_path, link, rating_value in sorted(scripts, key=lambda x: x[1].lower()):
            # Add link to tags if available
            tags = [script_path, undo_desc]
            if link:
                tags.append(link)
                tags.append("has_link")
            
            # Add rating to tags if available
            if rating_value:
                tags.append(f"rating_{rating_value}")
                tags.append("has_rating")
            
            self.scripts_tree.insert("", tk.END, 
                values=(script_type, friendly_name, developer, description, rating_text, "Yes" if undoable else "No"), 
                tags=tags
            )
        
        print(f"Found {len(scripts)} scripts in {category_name}")
        return len(scripts)
        
    def filter_scripts(self, event=None):
        """Filter scripts based on search text"""
        pass  # This will be implemented in the app class since it needs access to all categories
        
    def show_tooltip(self, event):
        """Show tooltips for tree items"""
        item = self.scripts_tree.identify_row(event.y)
        if item:
            column = self.scripts_tree.identify_column(event.x)
            if column == "#4":  # Description column
                values = self.scripts_tree.item(item, 'values')
                if len(values) >= 4:
                    description = values[3]
                    self.tooltip.showtip(description)
                    return
            elif column == "#5":  # Rating column
                tags = self.scripts_tree.item(item, 'tags')
                if "has_rating" in tags:
                    self.tooltip.showtip("Click to rate this script")
                    return
                else:
                    self.tooltip.showtip("No ratings yet. Click to rate this script.")
                    return
            elif column == "#6":  # Undoable column
                values = self.scripts_tree.item(item, 'values')
                tags = self.scripts_tree.item(item, 'tags')
                if len(values) >= 6 and len(tags) >= 2:
                    undoable = values[5]
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
        """Handle clicks on script items, particularly for developer column links"""
        item = self.scripts_tree.identify_row(event.y)
        if not item:
            return
            
        column = self.scripts_tree.identify_column(event.x)
        
        if column == "#3":  # Developer column
            tags = self.scripts_tree.item(item, 'tags')
            # Check if this item has a link (should be the third tag if present)
            if len(tags) >= 3 and "has_link" in tags:
                for tag in tags:
                    # Check if the tag looks like a URL
                    if tag.startswith(("http://", "https://", "www.")):
                        try:
                            # Open the URL in the default browser with confirmation
                            url = tag
                            if url.startswith("www."):
                                url = "http://" + url
                            
                            developer = self.scripts_tree.item(item, 'values')[2]
                            if MessageHandler.confirm_url_open(
                                    url, 
                                    "Open Developer Link",
                                    f"You are about to open this developer link for {developer}:\n\n{url}\n\nWould you like to proceed?"
                                ):
                                print(f"Opening developer link: {url}")
                                webbrowser.open(url)
                            break
                        except Exception as e:
                            print(f"Error opening link: {str(e)}")
                            MessageHandler.error(f"Failed to open the developer link: {str(e)}", "Link Error")
        
        elif column == "#5":  # Rating column
            # Handle rating click - show rating dialog
            if self.rating_system:
                script_info = self.get_selected_script()
                if script_info:
                    self.rating_system.show_rating_dialog(self.parent, script_info)
    
    def get_selected_script(self):
        """Get the currently selected script"""
        selected_items = self.scripts_tree.selection()
        if not selected_items:
            return None
            
        item_id = selected_items[0]
        values = self.scripts_tree.item(item_id, 'values')
        tags = self.scripts_tree.item(item_id, 'tags')
        
        if len(tags) >= 1:
            script_path = tags[0]
            undo_desc = tags[1] if len(tags) > 1 else ""
            link = None
            rating = None
            
            for tag in tags:
                if tag.startswith(("http://", "https://", "www.")):
                    link = tag
                elif tag.startswith("rating_"):
                    try:
                        rating = float(tag.split('_')[1])
                    except:
                        pass
                    
            return {
                'item_id': item_id,
                'type': values[0],
                'name': values[1],
                'developer': values[2],
                'description': values[3],
                'rating': values[4] if len(values) > 4 else "",
                'undoable': values[5] == "Yes" if len(values) > 5 else False,
                'undo_desc': undo_desc,
                'path': script_path,
                'link': link,
                'rating_value': rating
            }
            
        return None
