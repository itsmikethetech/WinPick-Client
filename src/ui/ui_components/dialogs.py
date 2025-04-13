#!/usr/bin/env python3
"""
Dialog Module
Common dialogs used in the application
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox


class ScriptActionDialog:
    """Dialog for script actions (run or undo)"""
    def __init__(self, parent, script_info, primary_color="#4a86e8", secondary_color="#f0f0f0"):
        self.parent = parent
        self.script_info = script_info
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.result = None
        
    def show(self):
        """Show the dialog and return the action result"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Script Action")
        dialog.geometry("500x500")
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.configure(bg=self.secondary_color)
        
        # Make dialog appear centered on parent window
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (500 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (280 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Create scrollable canvas for the dialog content
        main_canvas = tk.Canvas(dialog, bg=self.secondary_color)
        main_scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=main_canvas.yview)
        main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # Create a frame inside the canvas that will be scrollable
        frame = ttk.Frame(main_canvas, padding=20)
        frame_window = main_canvas.create_window((0, 0), window=frame, anchor=tk.NW, tags="frame")
        
        # Configure the scrolling behavior
        def configure_scroll_region(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        frame.bind("<Configure>", configure_scroll_region)
        
        # Bind mouse wheel to scrolling
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Adjust the canvas size when the window is resized
        def on_window_configure(event):
            # Update the width of the canvas window
            main_canvas.itemconfig(frame_window, width=event.width-20)
        
        dialog.bind("<Configure>", on_window_configure)
        
        # Script title with icon for script type
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
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
            
        ttk.Label(title_frame, 
                 text=f"{script_icon} {self.script_info['name']}", 
                 font=("Segoe UI", 14, "bold"),
                 foreground=self.primary_color).pack(anchor=tk.CENTER)
        
        # Information frame
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        # Script details
        ttk.Label(info_frame, 
                 text="Type:", 
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=3)
        ttk.Label(info_frame, 
                 text=self.script_info['type']).grid(row=0, column=1, sticky=tk.W, pady=3, padx=10)
                 
        ttk.Label(info_frame, 
                 text="Developer:", 
                 font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=3)
        ttk.Label(info_frame, 
                 text=self.script_info['developer']).grid(row=1, column=1, sticky=tk.W, pady=3, padx=10)
                 
        ttk.Label(info_frame, 
                 text="Description:", 
                 font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky=tk.NW, pady=3)
        desc_label = ttk.Label(info_frame, 
                             text=self.script_info['description'],
                             wraplength=350)
        desc_label.grid(row=2, column=1, sticky=tk.W, pady=3, padx=10)
        
        if self.script_info['undo_desc']:
            ttk.Label(info_frame, 
                     text="Undo Action:", 
                     font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky=tk.NW, pady=3)
            undo_label = ttk.Label(info_frame, 
                                 text=self.script_info['undo_desc'],
                                 wraplength=350)
            undo_label.grid(row=3, column=1, sticky=tk.W, pady=3, padx=10)
        
        # Action buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=(15, 0))
        
        def on_run():
            self.result = 'run'
            on_close()
            
        def on_undo():
            self.result = 'undo'
            on_close()
            
        def on_close():
            main_canvas.unbind_all("<MouseWheel>")
            dialog.destroy()
        
        # Run button with icon
        run_btn = ttk.Button(button_frame, 
                           text="▶ Run Script", 
                           width=15,
                           command=on_run)
        run_btn.pack(side=tk.LEFT, padx=5)
        
        # Undo button with icon
        if self.script_info['undoable']:
            undo_btn = ttk.Button(button_frame, 
                                text="↩ Undo Script", 
                                width=15,
                                command=on_undo)
            undo_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        ttk.Button(button_frame, 
                  text="Cancel", 
                  width=15,
                  command=on_close).pack(side=tk.LEFT, padx=5)
        
        # Make sure we initialize the scroll region
        frame.update_idletasks()
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        # Set up close handler
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        
        # Make dialog modal
        dialog.focus_set()
        self.parent.wait_window(dialog)
        
        return self
