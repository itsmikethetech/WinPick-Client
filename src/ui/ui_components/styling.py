#!/usr/bin/env python3
"""
UI Styling Module
Handles theming and styling for the application
"""

import tkinter as tk
from tkinter import ttk
import sys


class AppStyle:
    def __init__(self):
        # Define modern color scheme
        self.primary_color = "#3F51B5"       # Material Indigo primary
        self.primary_light = "#7986CB"       # Lighter primary for hover states
        self.primary_dark = "#303F9F"        # Darker primary for pressed states
        self.secondary_color = "#F5F5F5"     # Light gray background
        self.accent_color = "#FF4081"        # Pink accent
        self.text_color = "#212121"          # Near-black text
        self.text_secondary = "#757575"      # Secondary text
        self.bg_dark = "#2D3142"             # Dark background for console
        self.bg_light = "#FFFFFF"            # White background for content areas
        self.card_bg = "#FFFFFF"             # Card background
        self.border_color = "#E0E0E0"        # Border color
        self.success_color = "#4CAF50"       # Success green
        self.warning_color = "#FF9800"       # Warning orange
        self.error_color = "#F44336"         # Error red
        
        # Font configuration
        self.font_family = self._get_system_font()
        self.font_size_small = 9
        self.font_size_normal = 10
        self.font_size_large = 12
        self.font_size_xlarge = 14
        
    def _get_system_font(self):
        """Return the best font for the operating system"""
        if sys.platform == "win32":
            return "Segoe UI"
        elif sys.platform == "darwin":
            return "San Francisco"
        else:
            return "Roboto"
        
    def apply_style(self, root):
        """Apply styles to the application"""
        # Set up theming with modern colors
        root.configure(bg=self.secondary_color)
        style = ttk.Style()
        
        # Use clam theme as base
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
            
        # Configure global styles
        style.configure(".", font=(self.font_family, self.font_size_normal))
        
        # Frame styles
        style.configure("TFrame", background=self.secondary_color)
        
        # Card frame style - for content areas that need elevation
        style.configure("Card.TFrame", 
                       background=self.card_bg,
                       relief="flat")
        
        # Label styles
        style.configure("TLabel", 
                      background=self.secondary_color, 
                      foreground=self.text_color,
                      font=(self.font_family, self.font_size_normal))
        
        # Heading label style
        style.configure("Heading.TLabel", 
                      font=(self.font_family, self.font_size_large, "bold"),
                      foreground=self.primary_color)
        
        # Subheading label style
        style.configure("Subheading.TLabel", 
                      font=(self.font_family, self.font_size_normal, "bold"),
                      foreground=self.text_color)
        
        # Button styles - modern flat design
        style.configure("TButton", 
                      background=self.primary_color, 
                      foreground="white",
                      borderwidth=0,
                      focusthickness=0,
                      font=(self.font_family, self.font_size_normal),
                      padding=[12, 6])
        
        style.map("TButton", 
                background=[('active', self.primary_light), ('pressed', self.primary_dark)],
                foreground=[('active', 'white'), ('pressed', 'white')])
        
        # Secondary button style
        style.configure("Secondary.TButton", 
                      background=self.secondary_color,
                      foreground=self.primary_color,
                      borderwidth=1,
                      relief="solid")
        
        style.map("Secondary.TButton",
                background=[('active', self.card_bg), ('pressed', self.card_bg)],
                foreground=[('active', self.primary_dark), ('pressed', self.primary_dark)])
        
        # Admin button style - danger button
        style.configure("Admin.TButton", 
                      background=self.accent_color, 
                      foreground="white")
        
        style.map("Admin.TButton",
                background=[('active', '#FF5B99'), ('pressed', '#E03771')])
        
        # Icon button style - for toolbar buttons with icons
        style.configure("Icon.TButton", 
                      background=self.secondary_color,
                      foreground=self.primary_color,
                      borderwidth=0,
                      focusthickness=0,
                      padding=4)
        
        style.map("Icon.TButton",
                background=[('active', self.card_bg), ('pressed', self.card_bg)])
        
        # Success button style
        style.configure("Success.TButton", 
                      background=self.success_color, 
                      foreground="white")
        
        style.map("Success.TButton",
                background=[('active', '#5DBE61'), ('pressed', '#43A047')])
        
        # Category treeview style - smoother with more padding
        style.configure("Category.Treeview", 
                       background=self.bg_light, 
                       foreground=self.text_color,
                       rowheight=36,
                       borderwidth=0,
                       font=(self.font_family, self.font_size_normal))
        
        style.map("Category.Treeview",
                background=[('selected', self.primary_color)],
                foreground=[('selected', 'white')])
        
        # Style the treeview heading
        style.configure("Category.Treeview.Heading", 
                      font=(self.font_family, self.font_size_normal, "bold"),
                      background=self.secondary_color,
                      foreground=self.text_color)
        
        # Scripts treeview style
        style.configure("Scripts.Treeview", 
                       background=self.bg_light,
                       foreground=self.text_color,
                       rowheight=36,
                       borderwidth=0,
                       font=(self.font_family, self.font_size_normal))
        
        style.map("Scripts.Treeview",
                background=[('selected', self.primary_color)],
                foreground=[('selected', 'white')])
        
        # Style the treeview heading
        style.configure("Scripts.Treeview.Heading", 
                      font=(self.font_family, self.font_size_normal, "bold"),
                      background=self.secondary_color,
                      relief="flat",
                      borderwidth=0,
                      foreground=self.text_color)
        
        # Entry style - modern flat input with animation on focus
        style.configure("TEntry", 
                      fieldbackground=self.bg_light, 
                      foreground=self.text_color,
                      borderwidth=1,
                      focusthickness=0,
                      font=(self.font_family, self.font_size_normal))
        
        style.map("TEntry",
                fieldbackground=[('focus', self.bg_light)],
                bordercolor=[('focus', self.primary_color)])
        
        # Search entry style
        style.configure("Search.TEntry", 
                      padding=[6, 4])
        
        # Notebook (tab) styles
        style.configure("TNotebook", 
                      background=self.secondary_color,
                      borderwidth=0)
        
        style.configure("TNotebook.Tab", 
                      background=self.secondary_color,
                      foreground=self.text_secondary,
                      padding=[14, 8],
                      font=(self.font_family, self.font_size_normal),
                      borderwidth=0,
                      focusthickness=0)
        
        style.map("TNotebook.Tab",
                background=[('selected', self.bg_light)],
                foreground=[('selected', self.primary_color)],
                expand=[('selected', [1, 1, 1, 0])])
        
        # Scrollbar style - thinner and modern
        style.configure("TScrollbar", 
                      arrowsize=13,
                      background=self.secondary_color,
                      borderwidth=0,
                      troughcolor=self.secondary_color)
        
        style.map("TScrollbar",
                background=[('active', self.primary_light), ('pressed', self.primary_color)],
                arrowcolor=[('active', self.primary_color), ('pressed', 'white')])
        
        # Separator style
        style.configure("TSeparator", 
                      background=self.border_color)
        
        # Progressbar style
        style.configure("TProgressbar", 
                      background=self.primary_color,
                      troughcolor=self.secondary_color,
                      borderwidth=0,
                      thickness=6)
        
        return style
