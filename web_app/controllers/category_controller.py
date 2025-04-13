#!/usr/bin/env python3
"""
Category Controller for Web App
Handles category operations for the web interface
"""

import os
import sys
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

class CategoryController:
    """Controller for category operations"""
    
    def check_and_create_directories(self, base_dir, categories):
        """Check and create required directories for categories"""
        try:
            os.makedirs(base_dir, exist_ok=True)
            
            # Create directories for all categories
            for category in categories:
                category_path = os.path.join(base_dir, category)
                os.makedirs(category_path, exist_ok=True)
                
            logger.info(f"Checked and created directories in {base_dir}")
            return True
        except Exception as e:
            logger.error(f"Error checking/creating directories: {str(e)}")
            return False
    
    def detect_custom_categories(self, base_dir, default_categories):
        """Detect custom categories in the base directory"""
        custom_categories = []
        try:
            if not os.path.exists(base_dir):
                return custom_categories
                
            # Get all directories in the base directory
            for item in os.listdir(base_dir):
                item_path = os.path.join(base_dir, item)
                if os.path.isdir(item_path) and item not in default_categories:
                    custom_categories.append(item)
                    
            logger.info(f"Detected {len(custom_categories)} custom categories")
            return sorted(custom_categories)
        except Exception as e:
            logger.error(f"Error detecting custom categories: {str(e)}")
            return []
            
    def get_category_info(self, base_dir, categories):
        """Get information about categories, including script counts"""
        category_info = []
        
        try:
            # Process both default and custom categories
            for category in categories:
                category_path = os.path.join(base_dir, category)
                
                if not os.path.exists(category_path):
                    os.makedirs(category_path, exist_ok=True)
                    
                # Count scripts in the category
                script_count = 0
                script_extensions = ['.ps1', '.py', '.bat', '.cmd', '.exe']
                
                for file in os.listdir(category_path):
                    file_path = os.path.join(category_path, file)
                    if os.path.isfile(file_path):
                        _, ext = os.path.splitext(file)
                        if ext.lower() in script_extensions:
                            script_count += 1
                
                # Add category info
                category_info.append({
                    'name': category,
                    'path': category_path,
                    'script_count': script_count,
                    'is_custom': category not in categories
                })
                
            return sorted(category_info, key=lambda x: x['name'])
        except Exception as e:
            logger.error(f"Error getting category info: {str(e)}")
            return []
    
    def create_new_category(self, base_dir, category_name):
        """Create a new category directory"""
        try:
            # Sanitize category name
            sanitized_name = self._sanitize_category_name(category_name)
            
            if not sanitized_name:
                logger.warning("Invalid category name provided")
                return False, "Invalid category name"
                
            category_path = os.path.join(base_dir, sanitized_name)
            
            # Check if category already exists
            if os.path.exists(category_path):
                logger.warning(f"Category already exists: {sanitized_name}")
                return False, "Category already exists"
                
            # Create the category directory
            os.makedirs(category_path, exist_ok=True)
            
            logger.info(f"Created new category: {sanitized_name}")
            return True, sanitized_name
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            return False, str(e)
    
    def _sanitize_category_name(self, name):
        """Sanitize category name to ensure it's valid"""
        # Remove leading/trailing whitespace
        sanitized = name.strip()
        
        # Replace invalid characters
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_\-\s]', '', sanitized)
        
        return sanitized