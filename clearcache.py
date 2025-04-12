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
    
    if not os.path.exists(cache_dir):
        print("No cache directory found. Nothing to clear.")
        return False
    
    try:
        # Find all JSON files in the cache directory
        cache_files = list(Path(cache_dir).glob("*.json"))
        
        if not cache_files:
            print("No cache files found in the cache directory.")
            return False
        
        # Create a backup directory
        backup_dir = os.path.join(os.path.expanduser("~"), ".winpick", "cache_backup")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Move files to backup instead of deleting them
        for file_path in cache_files:
            # Skip any non-ratings related files
            if "ratings" in file_path.name or "stars" in file_path.name:
                backup_path = os.path.join(backup_dir, file_path.name)
                shutil.copy2(file_path, backup_path)
                os.remove(file_path)
                print(f"Cleared cache file: {file_path.name} (backup created)")
        
        print("\nRatings cache cleared successfully!")
        print(f"Backup created in: {backup_dir}")
        print("\nThe application will fetch fresh ratings data on next run.")
        return True
        
    except Exception as e:
        print(f"Error clearing cache: {str(e)}")
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