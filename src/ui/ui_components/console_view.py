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
        """Create a modern console output view with syntax highlighting and clean design"""
        # Console header with better spacing and styling
        self.console_header = ttk.Frame(self.frame)
        self.console_header.pack(fill=tk.X, expand=False, pady=(0, 8))
        
        # Get parent app's font info if available
        try:
            parent_app = self.parent
            while parent_app and not hasattr(parent_app, 'font_family'):
                if hasattr(parent_app, 'master'):
                    parent_app = parent_app.master
                else:
                    parent_app = None
                    
            if parent_app and hasattr(parent_app, 'font_family'):
                self.font_family = parent_app.font_family
                self.font_size_large = parent_app.font_size_large
                self.font_size_normal = parent_app.font_size_normal
            else:
                self.font_family = "Segoe UI"
                self.font_size_large = 12
                self.font_size_normal = 10
        except:
            self.font_family = "Segoe UI"
            self.font_size_large = 12
            self.font_size_normal = 10
        
        # Console title with icon and modern styling
        ttk.Label(self.console_header, 
                text="🖥️ Console Output", 
                font=(self.font_family, self.font_size_large, "bold"),
                foreground=self.primary_color).pack(side=tk.LEFT, anchor=tk.W, pady=(0, 5), padx=(0, 10))
        
        # Control buttons in separate container for better organization
        self.console_controls = ttk.Frame(self.console_header)
        self.console_controls.pack(side=tk.RIGHT)
        
        # Clear console button with icon
        self.clear_console_btn = ttk.Button(self.console_controls, 
                                        text="🧹 Clear", 
                                        command=self.clear_console)
        self.clear_console_btn.pack(side=tk.RIGHT, padx=5)
        
        # Copy button to copy console contents
        self.copy_console_btn = ttk.Button(self.console_controls,
                                        text="📋 Copy",
                                        command=self.copy_console_contents)
        self.copy_console_btn.pack(side=tk.RIGHT, padx=5)
        
        # Filter dropdown for console output
        self.filter_var = tk.StringVar(value="All")
        self.filter_frame = ttk.Frame(self.console_controls)
        self.filter_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Label(self.filter_frame, text="Filter:").pack(side=tk.LEFT)
        
        self.filter_combo = ttk.Combobox(self.filter_frame, 
                                      textvariable=self.filter_var,
                                      state="readonly",
                                      values=["All", "Errors", "Warnings", "Info"],
                                      width=8)
        self.filter_combo.pack(side=tk.LEFT, padx=5)
        self.filter_combo.bind("<<ComboboxSelected>>", self.apply_console_filter)
        
        # Modern console with syntax highlighting and rounded corners using a frame wrapper
        console_frame = ttk.Frame(self.frame, padding=2)
        console_frame.pack(fill=tk.BOTH, expand=True)
        
        # Console with enhanced styling and monospace font for better code display
        self.console = scrolledtext.ScrolledText(
            console_frame, 
            wrap=tk.WORD, 
            bg=self.bg_dark, 
            fg="#ffffff", 
            insertbackground="#ffffff",
            selectbackground=self.primary_color,
            highlightthickness=0,
            borderwidth=0,
            padx=10,
            pady=10,
            font=("Cascadia Code", 10) if self.is_font_available("Cascadia Code") else ("Consolas", 10))
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Add additional syntax highlighting tags
        self.console.tag_config("error", foreground="#FF5252")
        self.console.tag_config("warning", foreground="#FFC107")
        self.console.tag_config("success", foreground="#4CAF50")
        self.console.tag_config("info", foreground="#2196F3")
        self.console.tag_config("cmd", foreground="#9C27B0")
        self.console.tag_config("path", foreground="#00BCD4")
        self.console.tag_config("header", foreground=self.primary_color, font=("Consolas", 10, "bold"))
    
    def is_font_available(self, font_name):
        """Check if a font is available on the system"""
        try:
            from tkinter import font
            return font_name in font.families()
        except:
            return False
            
    def copy_console_contents(self):
        """Copy console contents to clipboard"""
        try:
            text = self.console.get(1.0, tk.END)
            self.parent.clipboard_clear()
            self.parent.clipboard_append(text)
            self.parent.update()
            print("Console contents copied to clipboard")
        except Exception as e:
            print(f"Error copying console contents: {str(e)}")
            
    def apply_console_filter(self, event=None):
        """Apply filter to console output"""
        filter_value = self.filter_var.get()
        
        # Save current content
        current_content = self.console.get(1.0, tk.END)
        
        # Clear console
        self.console.delete(1.0, tk.END)
        
        # Reapply filtered content
        if filter_value == "All":
            self.console.insert(tk.END, current_content)
        else:
            lines = current_content.split("\n")
            for line in lines:
                should_show = False
                
                if filter_value == "Errors" and ("ERROR:" in line or "Error:" in line):
                    should_show = True
                elif filter_value == "Warnings" and ("WARNING:" in line or "Warning:" in line):
                    should_show = True
                elif filter_value == "Info" and not any(x in line for x in ["ERROR:", "Error:", "WARNING:", "Warning:"]):
                    should_show = True
                    
                if should_show:
                    self.console.insert(tk.END, line + "\n")
                    
        # Reapply syntax highlighting
        self._apply_syntax_highlighting()
    
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
    
    def _apply_syntax_highlighting(self):
        """Apply syntax highlighting to the entire console content"""
        content = self.console.get(1.0, tk.END)
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_start = f"{i+1}.0"
            line_end = f"{i+1}.end"
            
            # Apply highlighting based on content
            if "ERROR:" in line or "Error:" in line:
                self.console.tag_add("error", line_start, line_end)
            elif "WARNING:" in line or "Warning:" in line:
                self.console.tag_add("warning", line_start, line_end)
            elif "SUCCESS:" in line or "Success:" in line:
                self.console.tag_add("success", line_start, line_end)
            elif "INFO:" in line or "Info:" in line:
                self.console.tag_add("info", line_start, line_end)
            elif line.startswith(">") or line.startswith("$"):
                self.console.tag_add("cmd", line_start, line_end)
            elif "===" in line:
                self.console.tag_add("header", line_start, line_end)
            
            # Highlight file paths
            path_patterns = [r'[A-Za-z]:\\[\w\\.-]+', r'/[\w/.-]+']
            for pattern in path_patterns:
                import re
                for match in re.finditer(pattern, line):
                    start, end = match.span()
                    self.console.tag_add("path", f"{i+1}.{start}", f"{i+1}.{end}")

    def update_console(self):
        """Update the console with queued output and apply enhanced syntax highlighting"""
        try:
            while not self.console_queue.empty():
                text = self.console_queue.get_nowait()
                
                # Insert text at the end of the console
                text_start = self.console.index(tk.END)
                self.console.insert(tk.END, text)
                text_end = self.console.index(tk.END)
                
                # Apply syntax highlighting
                if "ERROR:" in text or "Error:" in text:
                    start_pos = self.console.search("ERROR:", text_start, text_end, backwards=False)
                    if not start_pos:
                        start_pos = self.console.search("Error:", text_start, text_end, backwards=False)
                    if start_pos:
                        line_end = self.console.search("\n", start_pos, text_end)
                        if not line_end:
                            line_end = text_end
                        self.console.tag_add("error", start_pos, line_end)
                
                elif "WARNING:" in text or "Warning:" in text:
                    start_pos = self.console.search("WARNING:", text_start, text_end, backwards=False)
                    if not start_pos:
                        start_pos = self.console.search("Warning:", text_start, text_end, backwards=False)
                    if start_pos:
                        line_end = self.console.search("\n", start_pos, text_end)
                        if not line_end:
                            line_end = text_end
                        self.console.tag_add("warning", start_pos, line_end)
                
                elif "SUCCESS:" in text or "Success:" in text:
                    start_pos = self.console.search("SUCCESS:", text_start, text_end, backwards=False)
                    if not start_pos:
                        start_pos = self.console.search("Success:", text_start, text_end, backwards=False)
                    if start_pos:
                        line_end = self.console.search("\n", start_pos, text_end)
                        if not line_end:
                            line_end = text_end
                        self.console.tag_add("success", start_pos, line_end)
                
                elif "===" in text:
                    start_pos = self.console.search("===", text_start, text_end, backwards=False)
                    if start_pos:
                        line_end = self.console.search("\n", start_pos, text_end)
                        if not line_end:
                            line_end = text_end
                        self.console.tag_add("header", start_pos, line_end)
                        
                # Highlight command prompts
                if text.startswith(">") or text.startswith("$"):
                    self.console.tag_add("cmd", text_start, text_start + "+1c lineend")
                
                # Highlight file paths
                try:
                    import re
                    path_patterns = [r'[A-Za-z]:\\[\w\\.-]+', r'/[\w/.-]+']
                    for pattern in path_patterns:
                        for match in re.finditer(pattern, text):
                            start, end = match.span()
                            start_idx = f"{text_start} + {start}c"
                            end_idx = f"{text_start} + {end}c"
                            self.console.tag_add("path", start_idx, end_idx)
                except Exception as e:
                    self.old_stdout.write(f"Error applying path highlighting: {str(e)}\n")
                
                # Auto-scroll to bottom
                self.console.see(tk.END)
                self.console.update_idletasks()
                
        except Exception as e:
            self.old_stdout.write(f"Error updating console: {str(e)}\n")
        
        # Schedule the next update
        self.parent.after(100, self.update_console)
    
    def clear_console(self):
        """Clear the console output"""
        self.console.delete(1.0, tk.END)
        print("Console cleared.")

    def create_command_input(self, command_callback):
        """Create a modern command input field at the bottom of the console"""
        # Command frame with rounded corners and elevation effect
        self.command_frame = ttk.Frame(self.parent, style="Card.TFrame", padding=(10, 10, 10, 10))
        self.command_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=8)
        
        # Command label with icon and modern font
        ttk.Label(self.command_frame, 
                 text="📟 Command:", 
                 font=(self.font_family, self.font_size_normal, "bold"),
                 background=self.card_bg if hasattr(self, 'card_bg') else "#ffffff").pack(side=tk.LEFT, padx=5)
        
        # Command history button 
        self.history_frame = ttk.Frame(self.command_frame, style="Card.TFrame")
        self.history_frame.pack(side=tk.RIGHT)
        
        self.history_btn = ttk.Button(self.history_frame,
                                   text="⏱️ History",
                                   width=10,
                                   command=self.show_command_history)
        self.history_btn.pack(side=tk.RIGHT, padx=5)
        
        # Modern execute button with icon
        self.execute_btn = ttk.Button(self.command_frame, 
                                   text="▶️ Execute", 
                                   width=12,
                                   style="TButton",
                                   command=lambda: command_callback(None))
        self.execute_btn.pack(side=tk.RIGHT, padx=5)
        
        # Command input container
        self.input_container = ttk.Frame(self.command_frame, style="Card.TFrame")
        self.input_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Command input with enhanced styling and monospace font
        prefer_fonts = ["Cascadia Code", "Consolas", "Courier New"]
        font_family = "Consolas"  # Default fallback
        
        # Try to find a good monospace font
        if hasattr(self, 'is_font_available'):
            for font in prefer_fonts:
                if self.is_font_available(font):
                    font_family = font
                    break
        
        # Command entry with modern styling
        self.command_entry = ttk.Entry(self.input_container, 
                                    font=(font_family, 10),
                                    style="Search.TEntry")
        self.command_entry.pack(fill=tk.X, expand=True, pady=4)
        self.command_entry.bind("<Return>", command_callback)
        
        # Command history storage
        self.command_history = []
        self.history_position = -1
        
        # Add up/down arrow navigation for command history
        self.command_entry.bind("<Up>", self.history_prev)
        self.command_entry.bind("<Down>", self.history_next)
        
        return self.command_entry
    
    def show_command_history(self):
        """Show command history in a popup window"""
        if not self.command_history:
            print("No command history available")
            return
            
        history_window = tk.Toplevel(self.parent)
        history_window.title("Command History")
        history_window.geometry("600x400")
        history_window.transient(self.parent)
        history_window.grab_set()
        
        # Center on parent
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (600 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (400 // 2)
        history_window.geometry(f"+{x}+{y}")
        
        # Create scrollable list
        frame = ttk.Frame(history_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, 
                text="Command History", 
                font=(self.font_family, self.font_size_large, "bold")).pack(pady=(0, 10))
        
        # Create scrollable listbox
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(frame, 
                           yscrollcommand=scrollbar.set,
                           font=("Consolas", 10),
                           selectbackground=self.primary_color,
                           borderwidth=1,
                           highlightthickness=0)
        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Add commands in reverse order (newest first)
        for cmd in reversed(self.command_history):
            listbox.insert(tk.END, cmd)
        
        # Add double-click behavior to use a command
        def on_double_click(event):
            selection = listbox.curselection()
            if selection:
                selected_cmd = listbox.get(selection[0])
                self.command_entry.delete(0, tk.END)
                self.command_entry.insert(0, selected_cmd)
                history_window.destroy()
                self.command_entry.focus_set()
                
        listbox.bind("<Double-1>", on_double_click)
        
        # Add button frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Add clear button
        def clear_history():
            self.command_history = []
            history_window.destroy()
            print("Command history cleared")
            
        ttk.Button(button_frame,
                 text="Clear History",
                 command=clear_history).pack(side=tk.LEFT, padx=5)
        
        # Add close button
        ttk.Button(button_frame,
                 text="Close",
                 command=history_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Add use selection button
        def use_selected():
            selection = listbox.curselection()
            if selection:
                selected_cmd = listbox.get(selection[0])
                self.command_entry.delete(0, tk.END)
                self.command_entry.insert(0, selected_cmd)
                history_window.destroy()
                self.command_entry.focus_set()
                
        ttk.Button(button_frame,
                 text="Use Selected",
                 command=use_selected).pack(side=tk.RIGHT, padx=5)
        
        # Focus the listbox initially
        listbox.focus_set()
        
    def history_prev(self, event):
        """Navigate to previous command in history"""
        if not self.command_history:
            return "break"
            
        if self.history_position < len(self.command_history) - 1:
            self.history_position += 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[-(self.history_position+1)])
            self.command_entry.icursor(tk.END)  # Move cursor to end
            
        return "break"  # Prevent default behavior
        
    def history_next(self, event):
        """Navigate to next command in history"""
        if self.history_position > 0:
            self.history_position -= 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[-(self.history_position+1)])
            self.command_entry.icursor(tk.END)  # Move cursor to end
        elif self.history_position == 0:
            # At the bottom of history, clear the input
            self.history_position = -1
            self.command_entry.delete(0, tk.END)
            
        return "break"  # Prevent default behavior
    
    def focus_command_input(self):
        """Set focus to the command input field"""
        if hasattr(self, 'command_entry'):
            self.command_entry.focus_set()
