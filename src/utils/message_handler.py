#!/usr/bin/env python3
"""
Message Handler Module
Handles displaying messages to the user, either in console or as dialog
"""

import tkinter as tk
from tkinter import messagebox


class MessageHandler:
    """Class to handle message display logic"""
    
    @staticmethod
    def info(message, title="Information", console_only=True):
        """
        Display informational messages
        
        Args:
            message: The message to display
            title: The dialog title
            console_only: If True, only print to console without showing dialog
        """
        print(f"INFO: {message}")
        
        if not console_only:
            messagebox.showinfo(title, message)
    
    @staticmethod
    def error(message, title="Error", console_only=False):
        """
        Display error messages
        
        Args:
            message: The error message to display
            title: The dialog title
            console_only: If True, only print to console without showing dialog
        """
        print(f"ERROR: {message}")
        
        if not console_only:
            messagebox.showerror(title, message)
    
    @staticmethod
    def warning(message, title="Warning", console_only=False):
        """
        Display warning messages
        
        Args:
            message: The warning message to display
            title: The dialog title
            console_only: If True, only print to console without showing dialog
        """
        print(f"WARNING: {message}")
        
        if not console_only:
            messagebox.showwarning(title, message)
    
    @staticmethod
    def confirm(message, title="Confirm"):
        """
        Display confirmation dialog
        
        Args:
            message: The confirmation message
            title: The dialog title
            
        Returns:
            bool: True if confirmed, False otherwise
        """
        print(f"CONFIRM: {message}")
        return messagebox.askyesno(title, message)
        
    @staticmethod
    def confirm_url_open(url, title="Open URL", message=None):
        """
        Display confirmation dialog for opening a URL
        
        Args:
            url: The URL to open
            title: The dialog title
            message: Optional custom message (default uses the URL)
            
        Returns:
            bool: True if confirmed, False otherwise
        """
        if message is None:
            message = f"You are about to open this URL in your web browser:\n\n{url}\n\nWould you like to proceed?"
            
        print(f"URL CONFIRMATION: {url}")
        return messagebox.askyesno(title, message)
