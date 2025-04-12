#!/usr/bin/env python3
"""    
Category View Module
Handles the category tree display and interactions
"""

import os
import re
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from src.utils.message_handler import MessageHandler


class CategoryView:
    def __init__(self, parent, base_dir, primary_color="#4a86e8", secondary_color="#f0f0f0"):
        self.parent = parent
        self.base_dir = base_dir
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.categories = []
        
        # Create the UI components
        self.frame = ttk.Frame(parent, width=250)
        self.create_category_view()
        
    def create_category_view(self):
        """Create the category tree view UI"""
        # Category header with title and add button
        self.category_header = ttk.Frame(self.frame)
        self.category_header.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.category_header, 
                 text="Categories", 
                 font=("Segoe UI", 12, "bold"),
                 foreground=self.primary_color).pack(side=tk.LEFT)
        
        add_category_btn = ttk.Button(self.category_header, 
                                     text="+", 
                                     width=3, 
                                     command=self.add_new_category)
        add_category_btn.pack(side=tk.RIGHT)
        
        # Category tree
        self.category_frame = ttk.Frame(self.frame)
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
        
    def set_selection_callback(self, callback):
        """Set the callback function for tree selection events"""
        self.category_tree.bind("<<TreeviewSelect>>", callback)
        
    def initialize_categories(self, categories_list):
        """Initialize the category tree with the provided list of categories"""
        self.categories = categories_list.copy()
        
        try:
            # Clear the tree first for immediate visual feedback
            for item in self.category_tree.get_children():
                self.category_tree.delete(item)
                
            os.makedirs(self.base_dir, exist_ok=True)
            
            # Start loading categories asynchronously
            threading.Thread(target=self._load_categories_async, 
                            args=(sorted(self.categories),), 
                            daemon=True).start()
            
            return True
                
        except Exception as e:
            error_msg = f"Error initializing categories: {str(e)}"
            print(f"ERROR: {error_msg}")
            MessageHandler.error(error_msg, "Category Error")
            
        return None
        
    def _load_categories_async(self, sorted_categories):
        """Load categories asynchronously"""
        try:
            # First add all main categories
            for category in sorted_categories:
                category_path = os.path.join(self.base_dir, category)
                os.makedirs(category_path, exist_ok=True)
                
                # Use after() to update UI from a background thread
                self.parent.after(0, lambda c=category, p=category_path: 
                                self.category_tree.insert('', 'end', text=c, values=(p,), tags=('category',)))
            
            # Then detect custom folders
            self.parent.after(100, self.detect_custom_folders)
            
            # Select first item if available after a short delay
            def select_first():
                if self.category_tree.get_children():
                    first_item = self.category_tree.get_children()[0]
                    self.category_tree.selection_set(first_item)
                    self.category_tree.focus(first_item)
                    self.category_tree.event_generate("<<TreeviewSelect>>")
            
            self.parent.after(200, select_first)
            
        except Exception as e:
            error_msg = f"Error in async category loading: {str(e)}"
            print(f"ERROR: {error_msg}")
            # Use after to safely display error from background thread
            self.parent.after(0, lambda: MessageHandler.error(error_msg, "Category Loading Error"))
    
    def detect_custom_folders(self):
        """Detect any custom folders in the base directory"""
        try:
            if not os.path.exists(self.base_dir):
                return False
            
            # Start custom folder detection in a background thread
            threading.Thread(target=self._detect_custom_folders_async, daemon=True).start()
            return True
        except Exception as e:
            error_msg = f"Error detecting custom folders: {str(e)}"
            print(f"ERROR: {error_msg}")
            return False
    
    def _detect_custom_folders_async(self):
        """Detect custom folders asynchronously"""
        try:
            base_dirs = [d for d in os.listdir(self.base_dir) 
                        if os.path.isdir(os.path.join(self.base_dir, d))]
            new_categories = []
            
            for dir_name in base_dirs:
                if dir_name not in self.categories:
                    category_path = os.path.join(self.base_dir, dir_name)
                    
                    # Use after() to safely update UI from background thread
                    self.parent.after(0, lambda d=dir_name, p=category_path: 
                                    self.category_tree.insert('', 'end', text=d, 
                                                            values=(p,), tags=('category',)))
                    new_categories.append(dir_name)
                    self.categories.append(dir_name)
            
            if new_categories:
                print(f"Added {len(new_categories)} new categories: {', '.join(new_categories)}")
            
            # Process subcategories
            def process_subcategories():
                for item_id in self.category_tree.get_children():
                    try:
                        category_path = self.category_tree.item(item_id, 'values')[0]
                        # Start a separate thread for each category to avoid blocking UI
                        threading.Thread(target=lambda p=category_path, i=item_id: 
                                        self._add_subcategories_async(i, p), 
                                        daemon=True).start()
                    except Exception as e:
                        print(f"Error processing subcategory: {str(e)}")
            
            # Schedule subcategory processing after a short delay
            self.parent.after(300, process_subcategories)
            
        except Exception as e:
            error_msg = f"Error in async custom folder detection: {str(e)}"
            print(f"ERROR: {error_msg}")
    
    def _add_subcategories(self, parent_id, parent_path):
        """Add subcategories to the tree view recursively (synchronous version)"""
        try:
            if not os.path.exists(parent_path):
                return
                
            subdirs = [d for d in os.listdir(parent_path) 
                      if os.path.isdir(os.path.join(parent_path, d))]
                      
            for subdir in sorted(subdirs):
                subdir_path = os.path.join(parent_path, subdir)
                subcategory_id = self.category_tree.insert(parent_id, 'end', text=subdir, 
                                                         values=(subdir_path,), tags=('subcategory',))
                self._add_subcategories(subcategory_id, subdir_path)
                
        except Exception as e:
            print(f"Error adding subcategories for {parent_path}: {str(e)}")
            
    def _add_subcategories_async(self, parent_id, parent_path):
        """Add subcategories to the tree view recursively (asynchronous version)"""
        try:
            if not os.path.exists(parent_path):
                return
                
            subdirs = [d for d in os.listdir(parent_path) 
                      if os.path.isdir(os.path.join(parent_path, d))]
                      
            for subdir in sorted(subdirs):
                subdir_path = os.path.join(parent_path, subdir)
                
                # Use after() to safely update UI from background thread
                def add_subdir(p_id, s_dir, s_path):
                    try:
                        subcategory_id = self.category_tree.insert(p_id, 'end', text=s_dir, 
                                                               values=(s_path,), tags=('subcategory',))
                        # Schedule recursive call with a slight delay to prevent UI freezing
                        self.parent.after(10, lambda: self._add_subcategories_async(subcategory_id, s_path))
                    except Exception as e:
                        print(f"Error in async subcategory addition: {str(e)}")
                
                self.parent.after(0, lambda p=parent_id, s=subdir, sp=subdir_path: add_subdir(p, s, sp))
                
        except Exception as e:
            print(f"Error adding subcategories async for {parent_path}: {str(e)}")
    
    def add_new_category(self):
        """Show dialog to add a new category"""
        # Create a modern category dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("New Category")
        dialog.geometry("400x200")
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.configure(bg=self.secondary_color)
        
        # Center the dialog
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (400 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (200 // 2)
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
                MessageHandler.error("Please enter a category name.", "Error", console_only=False)
                return
                
            clean_name = re.sub(r'[^a-zA-Z0-9_\-\s]', '', new_category)
            if not clean_name:
                MessageHandler.error("Please enter a valid category name.", "Invalid Name", console_only=False)
                return
                
            if clean_name in self.categories:
                MessageHandler.error(f"The category '{clean_name}' already exists.", "Category Exists", console_only=False)
                return
                
            category_path = os.path.join(self.base_dir, clean_name)
            try:
                os.makedirs(category_path, exist_ok=True)
                self.categories.append(clean_name)
                new_item = self.category_tree.insert('', 'end', text=clean_name, 
                                                   values=(category_path,), tags=('category',))
                
                # Select the new category
                self.category_tree.selection_set(new_item)
                self.category_tree.see(new_item)
                self.category_tree.event_generate("<<TreeviewSelect>>")
                
                print(f"Created new category: {clean_name}")
                dialog.destroy()
            except Exception as e:
                error_msg = f"Error creating category: {str(e)}"
                MessageHandler.error(error_msg, "Category Creation Error")
        
        ttk.Button(button_frame, 
                  text="Cancel", 
                  width=15,
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame, 
                  text="Create", 
                  width=15,
                  command=create_category).pack(side=tk.RIGHT, padx=5)
    
    def get_selected_category(self):
        """Get the currently selected category path and name"""
        selected_items = self.category_tree.selection()
        if not selected_items:
            return None, None
            
        item_id = selected_items[0]
        category_path = self.category_tree.item(item_id, 'values')[0]
        category_name = self.category_tree.item(item_id, 'text')
        
        return category_path, category_name
    
    def select_category_by_name(self, category_name):
        """Select a category by its name"""
        for item_id in self.category_tree.get_children():
            if self.category_tree.item(item_id, 'text') == category_name:
                self.category_tree.selection_set(item_id)
                self.category_tree.see(item_id)
                self.category_tree.event_generate("<<TreeviewSelect>>")
                return True
        return False
