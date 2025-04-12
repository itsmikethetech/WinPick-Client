#!/usr/bin/env python3
"""
GitHub Logout Utility

This script removes the GitHub authentication token,
effectively logging the user out from GitHub.
"""

import os
import sys

def logout_from_github():
    """Remove the GitHub token cache file."""
    # Define the token cache path
    token_cache_path = os.path.join(os.path.expanduser("~"), ".winpick", "github_token.json")
    
    try:
        if os.path.exists(token_cache_path):
            os.remove(token_cache_path)
            print("GitHub authentication token removed successfully.")
            return True
        else:
            print("No GitHub authentication token found. You are already logged out.")
            return False
    except Exception as e:
        print(f"Error logging out from GitHub: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== WinPick GitHub Logout Utility ===\n")
    
    confirmation = input("This will log you out from GitHub. Continue? (y/n): ")
    
    if confirmation.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)
    
    success = logout_from_github()
    
    if success:
        print("\nYou have been successfully logged out from GitHub.")
    else:
        print("\nOperation completed with issues.")