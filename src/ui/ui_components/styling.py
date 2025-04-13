#!/usr/bin/env python3
"""
UI Styling Module
Handles theming and styling for the application
"""

import tkinter as tk
from tkinter import ttk


class AppStyle:
    def __init__(self):
        # Define color scheme
        self.primary_color = "#4a86e8"       # Blue primary
        self.secondary_color = "#f0f0f0"     # Light gray background
        self.accent_color = "#ff5252"        # Red accent
        self.text_color = "#333333"          # Dark gray text
        self.bg_dark = "#2d2d2d"             # Dark background for console
        self.bg_light = "#ffffff"            # White background for content areas
        
    def apply_style(self, root):
        """Apply styles to the application"""
        # Set up theming with modern colors
        root.configure(bg=self.secondary_color)
        style = ttk.Style()
        
        # Use clam theme if available
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
            
        # Configure style with modern colors
        style.configure("TFrame", background=self.secondary_color)
        style.configure("TLabel", background=self.secondary_color, foreground=self.text_color)
        style.configure("TButton", background=self.primary_color, foreground="white", font=("Segoe UI", 9))
        style.map("TButton", 
                background=[('active', '#3a76d8'), ('pressed', '#2a66c8')],
                foreground=[('active', 'white')])
        
        # Define a custom style for admin mode button (red)
        style.configure("Admin.TButton", background=self.accent_color, foreground="white")
        style.map("Admin.TButton",
                 background=[('active', '#e04242'), ('pressed', '#d03232')])
        
        # Define a style for the category tree
        style.configure("Category.Treeview", 
                       background=self.bg_light, 
                       foreground=self.text_color,
                       rowheight=30,
                       font=("Segoe UI", 10))
        style.map("Category.Treeview",
                 background=[('selected', self.primary_color)],
                 foreground=[('selected', 'white')])
        
        # Define a style for scripts tree
        style.configure("Scripts.Treeview", 
                       background=self.bg_light,
                       foreground=self.text_color,
                       rowheight=30,
                       font=("Segoe UI", 10))
        style.map("Scripts.Treeview",
                 background=[('selected', self.primary_color)],
                 foreground=[('selected', 'white')])
        
        # Custom ttk.Entry style
        style.configure("TEntry", 
                       fieldbackground=self.bg_light, 
                       foreground=self.text_color,
                       borderwidth=1,
                       font=("Segoe UI", 10))
        
        # Custom ttk.Notebook style for tabs
        style.configure("TNotebook", background=self.secondary_color)
        style.configure("TNotebook.Tab", 
                       background=self.secondary_color,
                       foreground=self.text_color,
                       padding=[10, 5],
                       font=("Segoe UI", 10))
        style.map("TNotebook.Tab",
                 background=[('selected', self.bg_light)],
                 foreground=[('selected', self.primary_color)])
                 
        return style
