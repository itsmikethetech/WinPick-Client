#!/usr/bin/env python3
"""
Clear Ratings Cache Utility

This script clears the locally cached ratings data, forcing the application
to fetch fresh ratings data from GitHub on the next run.
"""

import os
import json
import sys
import shutil
from pathlib import Path

def clear_ratings_cache():
    """Clear the local ratings cache files."""
    # Define the cache directory path
    cache_dir = os.path.join(os.path.expanduser("~"), ".winpick", "cache")
    ratings_cache_file = os.path.join(os.path.expanduser("~"), ".winpick", "script_ratings.json")
    
    try:
        # Check if the ratings cache file exists
        if os.path.exists(ratings_cache_file):
            # Create a backup directory
            backup_dir = os.path.join(os.path.expanduser("~"), ".winpick", "cache_backup")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copy to backup before deleting
            backup_path = os.path.join(backup_dir, "script_ratings_backup.json")
            shutil.copy2(ratings_cache_file, backup_path)
            
            # Remove the ratings cache file
            os.remove(ratings_cache_file)
            print(f"Cleared ratings cache file (backup created at {backup_path})")
            
            return True
        else:
            print("No ratings cache file found.")
            return False
    except Exception as e:
        print(f"Error clearing ratings cache: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== WinPick Ratings Cache Cleaner ===\n")
    
    confirmation = input("This will clear the local ratings cache, forcing a refresh on next app start. Continue? (y/n): ")
    
    if confirmation.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)
    
    success = clear_ratings_cache()
    
    if success:
        print("\nOperation completed successfully.")
    else:
        print("\nOperation completed with issues.")