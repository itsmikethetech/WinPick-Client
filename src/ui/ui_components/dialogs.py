#!/usr/bin/env python3
"""
Dialog Module
Modern responsive dialogs for the application
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox


class ScriptActionDialog:
    """Modern dialog for script actions (run or undo)"""
    def __init__(self, parent, script_info, primary_color="#3F51B5", accent_color="#FF4081"):
        self.parent = parent
        self.script_info = script_info
        self.primary_color = primary_color
        self.accent_color = accent_color
        self.result = None
        
        # Try to get styling from parent app
        try:
            # Find the parent app object
            parent_app = parent
            while parent_app and not hasattr(parent_app, 'card_bg'):
                if hasattr(parent_app, 'master'):
                    parent_app = parent_app.master
                else:
                    parent_app = None
                    
            if parent_app:
                # Get style properties
                self.primary_color = parent_app.primary_color
                self.primary_light = parent_app.primary_light
                self.primary_dark = parent_app.primary_dark
                self.accent_color = parent_app.accent_color
                self.secondary_color = parent_app.secondary_color
                self.text_color = parent_app.text_color
                self.text_secondary = parent_app.text_secondary
                self.card_bg = parent_app.card_bg
                self.success_color = parent_app.success_color
                self.warning_color = parent_app.warning_color
                self.error_color = parent_app.error_color
                self.font_family = parent_app.font_family
                self.font_size_small = parent_app.font_size_small
                self.font_size_normal = parent_app.font_size_normal
                self.font_size_large = parent_app.font_size_large
                self.font_size_xlarge = parent_app.font_size_xlarge
            else:
                # Default values if parent app not found
                self.secondary_color = "#F5F5F5"
                self.text_color = "#212121"
                self.text_secondary = "#757575"
                self.card_bg = "#FFFFFF"
                self.success_color = "#4CAF50"
                self.warning_color = "#FF9800"
                self.error_color = "#F44336"
                self.font_family = self._get_system_font()
                self.font_size_small = 9
                self.font_size_normal = 10
                self.font_size_large = 12
                self.font_size_xlarge = 14
        except:
            # Fallback values if anything fails
            self.secondary_color = "#F5F5F5"
            self.text_color = "#212121"
            self.text_secondary = "#757575"
            self.card_bg = "#FFFFFF"
            self.success_color = "#4CAF50"
            self.warning_color = "#FF9800"
            self.error_color = "#F44336"
            self.font_family = self._get_system_font()
            self.font_size_small = 9
            self.font_size_normal = 10
            self.font_size_large = 12
            self.font_size_xlarge = 14
    
    def _get_system_font(self):
        """Get the best font for the current system"""
        import sys
        if sys.platform == "win32":
            return "Segoe UI"
        elif sys.platform == "darwin":
            return "San Francisco"
        else:
            return "Roboto"
    
    def show(self):
        """Show the dialog with a modern card-like design and return the action result"""
        # Create modern styled dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Script: {self.script_info['name']}")
        dialog.geometry("520x560")
        dialog.minsize(400, 450)  # Set minimum size for better UX
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.configure(bg=self.secondary_color)
        
        # Make dialog appear centered on parent window
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (520 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (560 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Create main container with padding
        main_container = ttk.Frame(dialog, padding=16, style="Card.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # Create scrollable canvas for the dialog content
        main_canvas = tk.Canvas(main_container, 
                              bg=self.card_bg, 
                              highlightthickness=0, 
                              borderwidth=0)
        main_scrollbar = ttk.Scrollbar(main_container, 
                                     orient=tk.VERTICAL, 
                                     command=main_canvas.yview)
        main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # Create a frame inside the canvas that will be scrollable
        content_frame = ttk.Frame(main_canvas, style="Card.TFrame", padding=16)
        frame_window = main_canvas.create_window((0, 0), 
                                             window=content_frame, 
                                             anchor=tk.NW, 
                                             tags="content")
        
        # Configure the scrolling behavior
        def configure_scroll_region(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        content_frame.bind("<Configure>", configure_scroll_region)
        
        # Bind mouse wheel to scrolling
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Adjust the canvas size when the window is resized
        def on_window_configure(event):
            canvas_width = event.width - 2  # Account for borders
            main_canvas.itemconfig(frame_window, width=canvas_width)
        
        dialog.bind("<Configure>", on_window_configure)
        
        # Script header with card-like styling
        header_container = ttk.Frame(content_frame, style="Card.TFrame")
        header_container.pack(fill=tk.X, pady=(0, 20))
        
        # Get script type and icon
        script_type = self.script_info['type'].lower()
        script_icon = "📄"  # Default icon
        if script_type == "ps1":
            script_icon = "⚙️"
        elif script_type == "py":
            script_icon = "🐍"
        elif script_type == "bat" or script_type == "cmd":
            script_icon = "🖥️"
        elif script_type == "exe":
            script_icon = "🚀"
        
        # Script title with icon and larger font
        title_label = ttk.Label(header_container, 
                             text=f"{script_icon} {self.script_info['name']}", 
                             font=(self.font_family, self.font_size_xlarge, "bold"),
                             foreground=self.primary_color,
                             background=self.card_bg)
        title_label.pack(anchor=tk.CENTER, pady=(0, 10))
        
        # Script description with cleaner wrapping
        if self.script_info['description']:
            desc_container = ttk.Frame(header_container, style="Card.TFrame")
            desc_container.pack(fill=tk.X, pady=(0, 10))
            
            desc_label = ttk.Label(desc_container, 
                                 text=self.script_info['description'],
                                 wraplength=450,
                                 justify=tk.CENTER,
                                 font=(self.font_family, self.font_size_normal),
                                 foreground=self.text_secondary,
                                 background=self.card_bg)
            desc_label.pack(fill=tk.X)
        
        # Script metadata in card-like container
        details_card = ttk.Frame(content_frame, style="Card.TFrame", padding=16)
        details_card.pack(fill=tk.X, pady=10)
        
        # Card header
        ttk.Label(details_card,
                text="Script Details",
                font=(self.font_family, self.font_size_large, "bold"),
                foreground=self.text_color,
                background=self.card_bg).pack(anchor=tk.W, pady=(0, 10))
        
        # Script info grid with improved layout
        info_grid = ttk.Frame(details_card, style="Card.TFrame")
        info_grid.pack(fill=tk.X, pady=(0, 10))
        
        # Script details with clear labels and values
        # Type
        type_row = ttk.Frame(info_grid, style="Card.TFrame")
        type_row.pack(fill=tk.X, pady=4)
        
        ttk.Label(type_row, 
                text="Type:", 
                width=12,
                font=(self.font_family, self.font_size_normal, "bold"),
                foreground=self.text_color,
                background=self.card_bg).pack(side=tk.LEFT, anchor=tk.W)
                
        type_value = ttk.Label(type_row, 
                            text=self.script_info['type'],
                            foreground=self.text_secondary,
                            background=self.card_bg)
        type_value.pack(side=tk.LEFT, anchor=tk.W, padx=10)
        
        # Developer
        dev_row = ttk.Frame(info_grid, style="Card.TFrame")
        dev_row.pack(fill=tk.X, pady=4)
        
        ttk.Label(dev_row, 
                text="Developer:", 
                width=12,
                font=(self.font_family, self.font_size_normal, "bold"),
                foreground=self.text_color,
                background=self.card_bg).pack(side=tk.LEFT, anchor=tk.W)
                
        dev_value = ttk.Label(dev_row, 
                           text=self.script_info['developer'],
                           foreground=self.text_secondary,
                           background=self.card_bg)
        dev_value.pack(side=tk.LEFT, anchor=tk.W, padx=10)
        
        # Rating if available
        if 'rating_value' in self.script_info and self.script_info['rating_value']:
            rating_row = ttk.Frame(info_grid, style="Card.TFrame")
            rating_row.pack(fill=tk.X, pady=4)
            
            ttk.Label(rating_row, 
                    text="Rating:", 
                    width=12,
                    font=(self.font_family, self.font_size_normal, "bold"),
                    foreground=self.text_color,
                    background=self.card_bg).pack(side=tk.LEFT, anchor=tk.W)
            
            # Create star rating display
            stars = "★" * int(self.script_info['rating_value'])
            if self.script_info['rating_value'] % 1 >= 0.5:  # Add half star
                stars += "½"
            stars += "☆" * (5 - len(stars))
            
            rating_value = ttk.Label(rating_row, 
                                  text=f"{stars} ({self.script_info['rating_value']}/5)",
                                  foreground=self.warning_color,
                                  background=self.card_bg)
            rating_value.pack(side=tk.LEFT, anchor=tk.W, padx=10)
        
        # Undo information if available
        if self.script_info['undoable'] and self.script_info['undo_desc']:
            # Create a separate card for undo info
            undo_card = ttk.Frame(content_frame, style="Card.TFrame", padding=16)
            undo_card.pack(fill=tk.X, pady=10)
            
            # Card header with warning icon
            ttk.Label(undo_card,
                    text="↩️ Undo Information",
                    font=(self.font_family, self.font_size_large, "bold"),
                    foreground=self.warning_color,
                    background=self.card_bg).pack(anchor=tk.W, pady=(0, 10))
            
            # Undo description
            undo_desc = ttk.Label(undo_card, 
                              text=self.script_info['undo_desc'],
                              wraplength=450,
                              justify=tk.LEFT,
                              foreground=self.text_color,
                              background=self.card_bg)
            undo_desc.pack(fill=tk.X, pady=4)
            
            # Add note about undoing
            ttk.Label(undo_card,
                    text="Note: You can undo this script's actions by clicking the 'Undo' button below.",
                    wraplength=450,
                    foreground=self.text_secondary,
                    font=(self.font_family, self.font_size_small, "italic"),
                    background=self.card_bg).pack(fill=tk.X, pady=(10, 0))
        
        # Warning for non-undoable scripts
        elif not self.script_info['undoable']:
            warning_card = ttk.Frame(content_frame, style="Card.TFrame", padding=16)
            warning_card.pack(fill=tk.X, pady=10)
            
            # Card header with warning icon
            ttk.Label(warning_card,
                    text="⚠️ Warning",
                    font=(self.font_family, self.font_size_large, "bold"),
                    foreground=self.error_color,
                    background=self.card_bg).pack(anchor=tk.W, pady=(0, 10))
            
            # Warning message
            warning_msg = ttk.Label(warning_card, 
                                 text="This script does not support undo functionality. Any changes made by this script cannot be automatically reverted.",
                                 wraplength=450,
                                 justify=tk.LEFT,
                                 foreground=self.text_color,
                                 background=self.card_bg)
            warning_msg.pack(fill=tk.X, pady=4)
        
        # Action buttons in a card-like container
        button_card = ttk.Frame(content_frame, style="Card.TFrame", padding=16)
        button_card.pack(fill=tk.X, pady=(20, 0))
        
        button_container = ttk.Frame(button_card, style="Card.TFrame")
        button_container.pack(fill=tk.X)
        
        def on_run():
            self.result = 'run'
            on_close()
            
        def on_undo():
            self.result = 'undo'
            on_close()
            
        def on_close():
            main_canvas.unbind_all("<MouseWheel>")
            dialog.destroy()
        
        # Cancel button - left side
        ttk.Button(button_container, 
                  text="Cancel", 
                  width=12,
                  style="Secondary.TButton",
                  command=on_close).pack(side=tk.LEFT, padx=5)
        
        # Action buttons - right side
        action_buttons = ttk.Frame(button_container, style="Card.TFrame")
        action_buttons.pack(side=tk.RIGHT)
        
        # Undo button with icon
        if self.script_info['undoable']:
            undo_btn = ttk.Button(action_buttons, 
                               text="↩️ Undo Script", 
                               width=15,
                               style="TButton",
                               command=on_undo)
            undo_btn.pack(side=tk.RIGHT, padx=5)
        
        # Run button with icon - success color
        run_btn = ttk.Button(action_buttons, 
                          text="▶️ Run Script", 
                          width=15,
                          style="Success.TButton",
                          command=on_run)
        run_btn.pack(side=tk.RIGHT, padx=5)
        
        # Make sure we initialize the scroll region
        content_frame.update_idletasks()
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        # Set up close handler
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        
        # Make dialog modal and set focus to run button
        run_btn.focus_set()
        self.parent.wait_window(dialog)
        
        return self
