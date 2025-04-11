#!/usr/bin/env python3
"""
GitHub Controller
Handles GitHub integration for downloading scripts
"""

import os
import tkinter as tk
from tkinter import messagebox
from src.utils.github_downloader.github_downloader import GitHubDownloader
from src.utils.message_handler import MessageHandler


class GitHubController:
    def __init__(self, parent, base_dir):
        self.parent = parent
        self.base_dir = base_dir
        
    def show_download_dialog(self):
        """Open the GitHub download dialog"""
        try:
            # Initialize the GitHub downloader
            downloader = GitHubDownloader(self.parent, self.base_dir)
            
            # Show the download dialog
            downloader.show_download_dialog()
            return True
            
        except Exception as e:
            error_msg = f"Error opening GitHub download dialog: {str(e)}"
            MessageHandler.error(error_msg, "GitHub Download Error")
            return False
