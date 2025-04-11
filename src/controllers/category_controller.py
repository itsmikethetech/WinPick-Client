#!/usr/bin/env python3
"""
Category Controller
Handles category operations and directory management
"""

import os
import traceback
import tkinter as tk
from tkinter import messagebox

from src.utils.message_handler import MessageHandler


class CategoryController:
    def __init__(self, parent=None):
        self.parent = parent
        
    def check_and_create_directories(self, base_dir, categories):
        """Check if directories exist and create them if needed"""
        try:
            if not os.path.exists(base_dir):
                print(f"Base directory does not exist. Creating: {base_dir}")
                os.makedirs(base_dir, exist_ok=True)
                print(f"Created base directory: {base_dir}")
                MessageHandler.info(f"Created base directory: {base_dir}")
            else:
                print(f"Base directory already exists: {base_dir}")
                
            missing_dirs = []
            for category in categories:
                category_dir = os.path.join(base_dir, category)
                if not os.path.exists(category_dir):
                    missing_dirs.append(category)
                    
            if missing_dirs:
                print(f"Creating {len(missing_dirs)} missing directories...")
                for category in missing_dirs:
                    category_dir = os.path.join(base_dir, category)
                    try:
                        os.makedirs(category_dir, exist_ok=True)
                        print(f"Created directory: {category_dir}")
                    except Exception as e:
                        error_msg = f"Error creating {category_dir}: {str(e)}"
                        MessageHandler.error(error_msg, "Directory Creation Error")
                        
                MessageHandler.info(f"Created {len(missing_dirs)} missing directories: {', '.join(missing_dirs)}")
            else:
                print("All category directories exist")
                MessageHandler.info("All script directories already exist.")
                    
            return True
            
        except Exception as e:
            error_msg = f"Error checking/creating directories: {str(e)}\n{traceback.format_exc()}"
            MessageHandler.error(error_msg, "Directory Check Error")
            return False
            
    def open_scripts_folder(self, base_dir):
        """Open the scripts base directory"""
        try:
            os.makedirs(base_dir, exist_ok=True)
            os.startfile(base_dir)
            print(f"Opened scripts folder: {base_dir}")
            return True
        except Exception as e:
            error_msg = f"Error opening scripts folder: {str(e)}"
            MessageHandler.error(error_msg, "Folder Error")
            return False
    
    def add_category(self, base_dir, category_name):
        """Add a new category directory"""
        if not category_name:
            if self.parent:
                MessageHandler.error("Please enter a category name.", "Error", console_only=False)
            return None
            
        category_path = os.path.join(base_dir, category_name)
        
        try:
            os.makedirs(category_path, exist_ok=True)
            print(f"Created new category: {category_name}")
            return category_path
        except Exception as e:
            error_msg = f"Error creating category: {str(e)}"
            MessageHandler.error(error_msg, "Category Creation Error")
            return None
