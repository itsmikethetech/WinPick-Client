#!/usr/bin/env python3
"""
Console View Module
Handles the console output display and redirection
"""

import sys
import tkinter as tk
from tkinter import ttk, scrolledtext
import queue
import threading
from src.utils.console_redirector import ConsoleRedirector


class ConsoleView:
    def __init__(self, parent, primary_color="#4a86e8", bg_dark="#2d2d2d"):
        self.parent = parent
        self.primary_color = primary_color
        self.bg_dark = bg_dark
        
        # Setup console output queue and redirector
        self.console_queue = queue.Queue()
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        
        # Create console frame
        self.frame = ttk.Frame(parent)
        self.create_console_view()
        
        # Start the console update timer
        self.parent.after(100, self.update_console)
        
    def create_console_view(self):
        """Create the console output view"""
        self.console_header = ttk.Frame(self.frame)
        self.console_header.pack(fill=tk.X, expand=False)
        
        ttk.Label(self.console_header, 
                 text="Console Output", 
                 font=("Segoe UI", 12, "bold"),
                 foreground=self.primary_color).pack(side=tk.LEFT, anchor=tk.W, pady=(0, 5))
        
        self.clear_console_btn = ttk.Button(self.console_header, 
                                          text="Clear Console", 
                                          command=self.clear_console)
        self.clear_console_btn.pack(side=tk.RIGHT, padx=5)
        
        # Console with syntax highlighting
        self.console = scrolledtext.ScrolledText(
            self.frame, 
            wrap=tk.WORD, 
            bg=self.bg_dark, 
            fg="#ffffff", 
            insertbackground="#ffffff",
            selectbackground=self.primary_color,
            font=("Consolas", 10))
        self.console.pack(fill=tk.BOTH, expand=True)
    
    def redirect_output(self):
        """Redirect stdout and stderr to the console"""
        sys.stdout = ConsoleRedirector(self.console_queue)
        sys.stderr = ConsoleRedirector(self.console_queue)
        
        print("================== WinPick Console ==================")
        print("Console output will appear here.")
        print("Scripts will display their output in this console.")
        print("=====================================================")
    
    def restore_output(self):
        """Restore original stdout and stderr"""
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
    
    def update_console(self):
        """Update the console with queued output"""
        try:
            while not self.console_queue.empty():
                text = self.console_queue.get_nowait()
                self.console.insert(tk.END, text)
                self.console.see(tk.END)
                self.console.update_idletasks()
                
                # Apply some basic syntax highlighting
                if "ERROR:" in text or "Error:" in text:
                    start_pos = self.console.search("ERROR:", tk.END+"-50c linestart", tk.END, backwards=True)
                    if not start_pos:
                        start_pos = self.console.search("Error:", tk.END+"-50c linestart", tk.END, backwards=True)
                    if start_pos:
                        line_end = self.console.search("\n", start_pos, tk.END)
                        if not line_end:
                            line_end = tk.END
                        self.console.tag_add("error", start_pos, line_end)
                        self.console.tag_config("error", foreground="#ff5252")
                
                elif "WARNING:" in text or "Warning:" in text:
                    start_pos = self.console.search("WARNING:", tk.END+"-50c linestart", tk.END, backwards=True)
                    if not start_pos:
                        start_pos = self.console.search("Warning:", tk.END+"-50c linestart", tk.END, backwards=True)
                    if start_pos:
                        line_end = self.console.search("\n", start_pos, tk.END)
                        if not line_end:
                            line_end = tk.END
                        self.console.tag_add("warning", start_pos, line_end)
                        self.console.tag_config("warning", foreground="#ffc107")
                
                elif "===" in text:
                    start_pos = self.console.search("===", tk.END+"-50c linestart", tk.END, backwards=True)
                    if start_pos:
                        line_end = self.console.search("\n", start_pos, tk.END)
                        if not line_end:
                            line_end = tk.END
                        self.console.tag_add("header", start_pos, line_end)
                        self.console.tag_config("header", foreground="#4a86e8", font=("Consolas", 10, "bold"))
                
        except Exception as e:
            self.old_stdout.write(f"Error updating console: {str(e)}\n")
        
        # Schedule the next update
        self.parent.after(100, self.update_console)
    
    def clear_console(self):
        """Clear the console output"""
        self.console.delete(1.0, tk.END)
        print("Console cleared.")

    def create_command_input(self, command_callback):
        """Create a command input field at the bottom of the console"""
        self.command_frame = ttk.Frame(self.parent, padding=(10, 10))
        self.command_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Label(self.command_frame, 
                 text="Command:", 
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Command input with modern styling
        self.command_entry = ttk.Entry(self.command_frame, width=50, font=("Consolas", 10))
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
        self.command_entry.bind("<Return>", command_callback)
        
        # Modern execute button
        self.execute_btn = ttk.Button(self.command_frame, 
                                    text="Execute", 
                                    width=15,
                                    command=lambda: command_callback(None))
        self.execute_btn.pack(side=tk.RIGHT, padx=5)
        
        return self.command_entry
    
    def focus_command_input(self):
        """Set focus to the command input field"""
        if hasattr(self, 'command_entry'):
            self.command_entry.focus_set()
