#!/usr/bin/env python3
"""
Main Application Module
Main application window for WinPick
"""

import os
import sys
import ctypes
import webbrowser
import tkinter as tk
import shutil
from tkinter import ttk, messagebox, PanedWindow

from src.ui.ui_components import (
    AppStyle, ConsoleView, CategoryView, 
    ScriptView, MenuBar, ScriptActionDialog
)
from src.controllers import (
    ScriptController, CategoryController, GitHubController
)
from src.utils.admin_utils import is_admin, request_admin_elevation
from src.utils.script_metadata import parse_script_metadata
from src.utils.message_handler import MessageHandler
from src.utils.github_auth import GitHubAuthHandler
from src.utils.rating_system import RatingSystem


class ScriptExplorer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("WinPick - Unlock the Potential of Windows")
        self.geometry("1200x900")  # Increased window size
        self.minsize(900, 600)
        
        # Set up styling
        self.style_manager = AppStyle()
        self.style = self.style_manager.apply_style(self)
        
        # Get color scheme for reuse
        self.primary_color = self.style_manager.primary_color
        self.secondary_color = self.style_manager.secondary_color
        self.accent_color = self.style_manager.accent_color
        self.text_color = self.style_manager.text_color
        self.bg_dark = self.style_manager.bg_dark
        self.bg_light = self.style_manager.bg_light
        
        # Define script categories
        self.categories = [
            "UI Customizations",
            "Performance Tweaks",
            "Privacy Settings",
            "Bloatware Removal",
            "Security Enhancements",
            "System Maintenance",
            "Boot Options",
            "Network Optimizations",
            "Power Management",
            "Default Apps"
        ]
        
        # Define script file extensions
        self.script_extensions = ['.ps1', '.py', '.bat', '.cmd', '.exe']
        
        # Setup base directory
        try:
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                base_dir = os.path.dirname(os.path.dirname(script_dir))
            except NameError:
                base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            self.base_dir = os.path.join(base_dir, "WindowsScripts")
            print(f"Using base directory: {self.base_dir}")
        except Exception as e:
            MessageHandler.error(f"Error setting up base directory: {str(e)}", "Directory Error")
        
        # Initialize controllers
        self.script_controller = ScriptController(self)
        self.category_controller = CategoryController(self)
        self.github_controller = GitHubController(self, self.base_dir)
        
        # Initialize GitHub authentication and rating system
        self.github_auth = GitHubAuthHandler(self)
        self.rating_system = RatingSystem(self.github_auth)
        
        # Create the main layout
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Menu Bar
        self.setup_menu()
        
        # Create Header
        self.create_header_frame()
        
        # Create Content Frame
        self.create_content_frame()
        
        # Initialize components with data
        self.initialize_components()
        
        # Update the admin button based on current privileges
        self.update_admin_indicator()
        
        # Update GitHub auth status
        self.update_github_auth_status()
    
    def setup_menu(self):
        """Set up the menu bar"""
        self.menu_bar = MenuBar(self)
        
        # File menu
        self.menu_bar.setup_file_menu(
            new_script_callback=self.create_new_script,
            new_category_callback=lambda: self.category_view.add_new_category(),
            open_scripts_folder_callback=lambda: self.category_controller.open_scripts_folder(self.base_dir),
            import_script_callback=self.import_script,
            export_script_callback=self.export_script,
            github_logout_callback=self.github_logout,
            clear_ratings_cache_callback=self.clear_ratings_cache,
            exit_callback=self.quit
        )
        
        # Tools menu
        self.menu_bar.setup_tools_menu(
            check_dirs_callback=self.check_and_create_directories,
            download_github_callback=lambda: self.github_controller.show_download_dialog(),
            clear_console_callback=lambda: self.console_view.clear_console(),
            refresh_view_callback=self.refresh_view,
            focus_command_callback=lambda: self.console_view.focus_command_input(),
            github_auth_callback=self.toggle_github_auth
        )
        
        # Help menu
        self.menu_bar.setup_help_menu(
            about_callback=self.show_about,
            patreon_callback=self.open_patreon
        )
        
    def github_logout(self):
        """Log out from GitHub by clearing the token cache"""
        if not self.github_auth.is_authenticated():
            MessageHandler.info("You are not currently logged in to GitHub.", "GitHub Logout", console_only=False)
            return
            
        if MessageHandler.confirm("Are you sure you want to log out of GitHub?", "Confirm Logout"):
            if self.github_auth.logout():
                MessageHandler.info("You have been logged out of GitHub.", "Logout Successful", console_only=False)
                # Update UI to reflect logged out state
                self.update_github_auth_status()
                # Refresh the script view to remove ratings
                self.refresh_view()
            else:
                MessageHandler.error("Failed to log out from GitHub.", "Logout Failed", console_only=False)

    def clear_ratings_cache(self):
        """Clear the ratings cache"""
        if MessageHandler.confirm(
            "This will clear the local ratings cache, forcing a refresh of ratings data on next interaction.\n\n"
            "Do you want to continue?",
            "Clear Ratings Cache"
        ):
            # Define the ratings cache file path
            ratings_cache_file = os.path.join(os.path.expanduser("~"), ".winpick", "script_ratings.json")
            
            try:
                # Check if the file exists
                if os.path.exists(ratings_cache_file):
                    # Create a backup directory
                    backup_dir = os.path.join(os.path.expanduser("~"), ".winpick", "cache_backup")
                    os.makedirs(backup_dir, exist_ok=True)
                    
                    # Copy to backup before deleting
                    backup_path = os.path.join(backup_dir, "script_ratings_backup.json")
                    shutil.copy2(ratings_cache_file, backup_path)
                    
                    # Remove the ratings cache file
                    os.remove(ratings_cache_file)
                    
                    # Reset the rating system's cache
                    if self.rating_system:
                        self.rating_system.ratings_cache = {}
                        self.rating_system.ratings_cache_time = {}
                    
                    MessageHandler.info(
                        "Ratings cache cleared successfully!\n"
                        f"A backup was created at: {backup_path}", 
                        "Cache Cleared", 
                        console_only=False
                    )
                    
                    # Refresh the UI to reflect the changes
                    self.refresh_view()
                else:
                    MessageHandler.info("No ratings cache file found.", "Cache Clear", console_only=False)
            except Exception as e:
                MessageHandler.error(f"Error clearing ratings cache: {str(e)}", "Cache Clear Error", console_only=False)
        
    def create_header_frame(self):
        """Create the header frame with logo and controls"""
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))
        
        # Left side - App title and logo
        self.title_frame = ttk.Frame(self.header_frame)
        self.title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.app_title = ttk.Label(self.title_frame, 
                                  text="WinPick", 
                                  font=("Segoe UI", 20, "bold"),
                                  foreground=self.primary_color)
        self.app_title.pack(side=tk.LEFT, padx=5)
        
        self.app_subtitle = ttk.Label(self.title_frame,
                                     text="Unlock the Potential of Windows",
                                     font=("Segoe UI", 12))
        self.app_subtitle.pack(side=tk.LEFT, padx=5)
        
        # Right side - Button controls
        self.controls_frame = ttk.Frame(self.header_frame)
        self.controls_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Heart icon for Patreon
        try:
            # Create a heart icon (can be replaced with a proper image file)
            heart_canvas = tk.Canvas(self.controls_frame, width=30, height=30, 
                                    bg=self.secondary_color, highlightthickness=0)
            heart_canvas.pack(side=tk.RIGHT, padx=5)
            
            # Draw a heart shape on the canvas
            heart_canvas.create_polygon(15, 7, 10, 3, 5, 7, 3, 12, 5, 17, 15, 25, 25, 17, 
                                      27, 12, 25, 7, 20, 3, 15, 7, 
                                      fill=self.accent_color, outline="")
            heart_canvas.bind("<Button-1>", lambda e: self.open_patreon())
            
            # Add tooltip to the heart icon
            from src.ui.tooltip import ToolTip
            heart_tooltip = ToolTip(heart_canvas)
            heart_canvas.bind("<Enter>", lambda e: heart_tooltip.showtip("Support on Patreon"))
            heart_canvas.bind("<Leave>", lambda e: heart_tooltip.hidetip())
        except Exception as e:
            print(f"Error creating heart icon: {e}")
        
        # Admin button
        self.admin_button = ttk.Button(self.controls_frame, text="", 
                                      command=self.request_admin_elevation)
        self.admin_button.pack(side=tk.RIGHT, padx=5)
        
        # Check Directories button
        self.check_dirs_btn = ttk.Button(self.controls_frame, 
                                        text="Check Directories", 
                                        command=self.check_and_create_directories)
        self.check_dirs_btn.pack(side=tk.RIGHT, padx=5)
        
        # GitHub Download button
        self.github_btn = ttk.Button(self.controls_frame, 
                                  text="Download Scripts from GitHub", 
                                  command=lambda: self.github_controller.show_download_dialog())
        self.github_btn.pack(side=tk.RIGHT, padx=5)
        
        # New Script button
        self.new_script_btn = ttk.Button(self.controls_frame, 
                                        text="New Script", 
                                        command=self.create_new_script)
        self.new_script_btn.pack(side=tk.RIGHT, padx=5)

    def create_content_frame(self):
        """Create the main content with paned windows"""
        self.content_pane = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.content_pane.pack(fill=tk.BOTH, expand=True)
        
        # Left pane - Categories
        self.left_pane = ttk.Frame(self.content_pane, width=250)
        self.content_pane.add(self.left_pane, weight=1)
        
        # Right side with scripts list and console output
        self.right_pane = ttk.PanedWindow(self.content_pane, orient=tk.VERTICAL)
        self.content_pane.add(self.right_pane, weight=3)
        
        # Category view component
        self.category_view = CategoryView(self.left_pane, self.base_dir, 
                                     primary_color=self.primary_color,
                                     secondary_color=self.secondary_color)
        self.category_view.frame.pack(fill=tk.BOTH, expand=True)
        
        # Set category selection callback
        self.category_view.set_selection_callback(self.on_category_select)
        
        # Scripts view component
        self.scripts_frame = ttk.Frame(self.right_pane)
        self.right_pane.add(self.scripts_frame, weight=2)
        
        self.script_view = ScriptView(self.scripts_frame, primary_color=self.primary_color, rating_system=self.rating_system)
        self.script_view.frame.pack(fill=tk.BOTH, expand=True)
        
        # Connect the search functionality
        self.script_view.search_var.trace_add("write", lambda *args: self.on_search_changed())
        self.script_view.filter_scripts = self.filter_scripts
        
        # Set script callbacks
        self.script_view.set_callbacks(
            double_click_callback=self.on_script_double_click,
            right_click_callback=self.on_script_right_click
        )
        
        # Console view component
        self.console_frame = ttk.Frame(self.right_pane)
        self.right_pane.add(self.console_frame, weight=1)
        
        self.console_view = ConsoleView(self.console_frame, 
                                    primary_color=self.primary_color,
                                    bg_dark=self.bg_dark)
        self.console_view.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create command input and connect to controller
        self.command_entry = self.console_view.create_command_input(self.execute_command)
        
    def initialize_components(self):
        """Initialize components with data"""
        # Create directories if needed
        self.category_controller.check_and_create_directories(self.base_dir, self.categories)
        
        # Initialize categories
        self.category_view.initialize_categories(self.categories)
        
        # Initialize script view with rating system
        self.script_view.set_rating_system(self.rating_system)
        
        # Redirect console output
        self.console_view.redirect_output()

    def on_search_changed(self):
        """Callback for when search text changes"""
        search_text = self.script_view.search_var.get().strip()
        # Only filter if we have at least 2 characters or search is being cleared
        if len(search_text) >= 2 or not search_text:
            self.filter_scripts()

    def filter_scripts(self, event=None):
        """Filter scripts based on search text"""
        search_text = self.script_view.search_var.get().lower()
        
        # Clear the tree
        for item in self.script_view.scripts_tree.get_children():
            self.script_view.scripts_tree.delete(item)
        
        # If no search text, reload scripts
        if not search_text:
            category_path, category_name = self.category_view.get_selected_category()
            if category_path and category_name:
                self.script_view.load_scripts(category_path, category_name)
            return
        
        # Search across all categories
        found_scripts = []
        
        for category in self.categories:
            category_path = os.path.join(self.base_dir, category)
            if not os.path.exists(category_path):
                continue
                
            for file in os.listdir(category_path):
                file_path = os.path.join(category_path, file)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file)
                    if ext.lower() in self.script_extensions:
                        script_type = ext.lstrip(".").upper()
                        friendly_name, description, undoable, undo_desc, developer, link = parse_script_metadata(file_path)
                        
                        # Get rating if rating system is available
                        rating_text = ""
                        rating_value = None
                        if self.rating_system:
                            avg_rating = self.rating_system.get_average_rating(file_path, friendly_name)
                            if avg_rating:
                                rating_text = f"{avg_rating}/5"
                                rating_value = avg_rating
                        
                        # Check if search text matches any field
                        if (search_text in friendly_name.lower() or 
                            search_text in description.lower() or 
                            search_text in developer.lower()):
                            
                            found_scripts.append((
                                script_type, 
                                friendly_name, 
                                developer, 
                                description, 
                                rating_text,  # Add rating
                                "Yes" if undoable else "No", 
                                undo_desc, 
                                file_path,
                                link,
                                rating_value  # Add rating value for sorting
                            ))
        
        # Update tree with results
        for script_type, friendly_name, developer, description, rating_text, undoable, undo_desc, script_path, link, rating_value in sorted(found_scripts, key=lambda x: x[1].lower()):
            # Add link to tags if available
            tags = [script_path, undo_desc]
            if link:
                tags.append(link)
                tags.append("has_link")
            
            # Add rating to tags if available
            if rating_value:
                tags.append(f"rating_{rating_value}")
                tags.append("has_rating")
                
            self.script_view.scripts_tree.insert("", tk.END, 
                values=(script_type, friendly_name, developer, description, rating_text, undoable), 
                tags=tags
            )
        
        self.script_view.scripts_label.config(text=f"Search Results: {len(found_scripts)} scripts")
        print(f"Found {len(found_scripts)} scripts matching '{search_text}'")

    # Event Handlers
    def on_category_select(self, event):
        """Handle category selection - immediately show selected category
        and load scripts asynchronously"""
        # Immediately get the selected category for responsiveness
        category_path, category_name = self.category_view.get_selected_category()
        if not category_path or not category_name:
            return
            
        # Start loading scripts (this is now asynchronous and will return immediately)
        self.script_view.load_scripts(category_path, category_name)
        
        # Log that we've started loading (actual script count will be logged when loading completes)
        print(f"Loading scripts from category: {category_name}")
        
    def on_script_double_click(self, event):
        """Handle script double-click event"""
        script_info = self.script_view.get_selected_script()
        if not script_info:
            return
            
        if script_info['undoable']:
            # Show action dialog for undoable scripts
            dialog = ScriptActionDialog(
                self, 
                script_info, 
                primary_color=self.primary_color,
                secondary_color=self.secondary_color
            )
            dialog.show()
            
            if dialog.result == 'run':
                self.script_controller.run_script(script_info['path'])
            elif dialog.result == 'undo':
                self.script_controller.run_script(script_info['path'], undo=True)
        else:
            # Run non-undoable scripts directly
            self.script_controller.run_script(script_info['path'])
    
    def on_script_right_click(self, event):
        """Handle script right-click event (context menu)"""
        item = self.script_view.scripts_tree.identify_row(event.y)
        if item:
            self.script_view.scripts_tree.selection_set(item)
            script_info = self.script_view.get_selected_script()
            if not script_info:
                return
                
            script_path = script_info['path']
            script_type = script_info['type'].lower()
            undoable = script_info['undoable']
            
            popup_menu = tk.Menu(self, tearoff=0)
            
            # Modern styling for popup menu
            popup_menu.configure(bg=self.bg_light, fg=self.text_color, 
                               activebackground=self.primary_color, 
                               activeforeground="white", font=("Segoe UI", 9))
            
            popup_menu.add_command(label="▶  Run", 
                                  command=lambda: self.script_controller.run_script(script_path))
            if undoable:
                popup_menu.add_command(label="↩  Undo", 
                                      command=lambda: self.script_controller.run_script(script_path, undo=True))
            popup_menu.add_separator()
            popup_menu.add_command(label="🔒  Run as Administrator", 
                                  command=lambda: self.script_controller.run_script_as_admin(script_path))
            if undoable:
                popup_menu.add_command(label="🔒  Undo as Administrator", 
                                      command=lambda: self.script_controller.run_script_as_admin(script_path, undo=True))
            popup_menu.add_separator()
            
            # Add Rate Script option
            popup_menu.add_command(label="⭐  Rate Script", 
                                 command=lambda: self.rating_system.show_rating_dialog(self, script_info))
            popup_menu.add_separator()
            
            if script_type != "exe":
                popup_menu.add_command(label="✏️  Edit Script", 
                                      command=lambda: self.script_controller.edit_script(script_path))
            popup_menu.add_command(label="🗑️  Delete Script", 
                                  command=lambda: self.delete_script(script_path))
            popup_menu.add_separator()
            popup_menu.add_command(label="📦  Install Dependencies", 
                                  command=lambda: self.script_controller.install_dependencies(script_path))
            popup_menu.add_separator()
            popup_menu.add_command(label="📂  Open Containing Folder", 
                                  command=lambda: self.script_controller.open_containing_folder(script_path))
            
            try:
                popup_menu.tk_popup(event.x_root, event.y_root, 0)
            finally:
                popup_menu.grab_release()
    
    # Action Handler Methods
    def create_new_script(self):
        """Show the new script creation dialog"""
        from src.ui.script_creator import create_new_script_dialog
        
        category_path, category_name = self.category_view.get_selected_category()
        if not category_path or not category_name:
            MessageHandler.info("Please select a category first.", "Select Category", console_only=False)
            return
            
        create_new_script_dialog(self, category_name, category_path, self.on_category_select)
        
    def import_script(self):
        """Import a script from file system"""
        category_path, category_name = self.category_view.get_selected_category()
        if not category_path or not category_name:
            MessageHandler.info("Please select a category first.", "Select Category", console_only=False)
            return
            
        imported_script = self.script_controller.import_script(category_path)
        if imported_script:
            # Refresh the script list
            self.script_view.load_scripts(category_path, category_name)
    
    def export_script(self):
        """Export selected script to file system"""
        script_info = self.script_view.get_selected_script()
        if not script_info:
            MessageHandler.info("Please select a script to export.", "Select Script", console_only=False)
            return
            
        self.script_controller.export_script(script_info['path'])
    
    def delete_script(self, script_path):
        """Delete a script with confirmation and refresh view"""
        if self.script_controller.delete_script(script_path):
            # Refresh the script list
            category_path, category_name = self.category_view.get_selected_category()
            if category_path and category_name:
                self.script_view.load_scripts(category_path, category_name)
    
    def execute_command(self, event=None):
        """Execute a command from the command input"""
        command = self.command_entry.get().strip()
        if command:
            self.script_controller.execute_command(command)
            self.command_entry.delete(0, tk.END)
    
    def toggle_github_auth(self):
        """Toggle GitHub authentication state"""
        if self.github_auth.is_authenticated():
            if MessageHandler.confirm("Are you sure you want to log out of GitHub?", "Confirm Logout"):
                if self.github_auth.logout():
                    MessageHandler.info("You have been logged out of GitHub.", "Logout Successful", console_only=False)
                    # Update UI to reflect logged out state
                    self.update_github_auth_status()
                    # Refresh the script view to remove ratings
                    self.refresh_view()
        else:
            if self.github_auth.authenticate():
                # Check if authentication was successful
                if self.github_auth.is_authenticated():
                    MessageHandler.info(
                        f"Successfully authenticated as {self.github_auth.user_info['login']}",
                        "Authentication Successful",
                        console_only=False
                    )
                    # Update UI to reflect logged in state
                    self.update_github_auth_status()
                    # Refresh the script view to show ratings
                    self.refresh_view()
                else:
                    MessageHandler.info(
                        "GitHub authentication is pending. Please complete the process in your browser.",
                        "Authentication Pending",
                        console_only=False
                    )

    def update_github_auth_status(self):
        """Update the UI to reflect GitHub authentication status"""
        try:
            if self.github_auth.is_authenticated():
                self.menu_bar.update_github_auth_label(f"Sign Out ({self.github_auth.user_info['login']})")
            else:
                self.menu_bar.update_github_auth_label("Sign In with GitHub")
        except Exception as e:
            print(f"Error updating GitHub auth status: {str(e)}")
    
    def check_and_create_directories(self):
        """Check and create required directories"""
        if self.category_controller.check_and_create_directories(self.base_dir, self.categories):
            # Refresh category view
            self.refresh_view()
    
    def refresh_view(self):
        """Refresh all views"""
        try:
            # Remember current selection
            current_category = None
            category_path, category_name = self.category_view.get_selected_category()
            if category_name:
                current_category = category_name
                
            # Re-initialize categories
            self.category_view.initialize_categories(self.categories)
            
            # Restore selection or select first item
            if current_category:
                if not self.category_view.select_category_by_name(current_category):
                    # If couldn't select the previous category, select the first item
                    if self.category_view.category_tree.get_children():
                        first_item = self.category_view.category_tree.get_children()[0]
                        self.category_view.category_tree.selection_set(first_item)
                        self.category_view.category_tree.see(first_item)
                        self.category_view.category_tree.event_generate("<<TreeviewSelect>>")
            elif self.category_view.category_tree.get_children():
                # If no previous selection, select the first item
                first_item = self.category_view.category_tree.get_children()[0]
                self.category_view.category_tree.selection_set(first_item)
                self.category_view.category_tree.see(first_item)
                self.category_view.category_tree.event_generate("<<TreeviewSelect>>")
                
            MessageHandler.info("View refreshed")
        except Exception as e:
            error_msg = f"Error refreshing view: {str(e)}"
            MessageHandler.error(error_msg)
    
    def open_patreon(self):
        """Open the Patreon page in a web browser"""
        url = "https://www.patreon.com/c/mikethetech"
        if MessageHandler.confirm_url_open(url, "Open Patreon"):
            webbrowser.open(url)
            print("Opening Patreon page...")
    
    def request_admin_elevation(self):
        """Request elevation to administrator privileges"""
        request_admin_elevation(self)
    
    def update_admin_indicator(self):
        """Update the admin button text based on current privileges"""
        try:
            if is_admin():
                self.admin_button.config(text="Administrator Mode", style="TButton")
            else:
                self.admin_button.config(text="Request Admin Rights", style="Admin.TButton")
                print("WARNING: Application is not running with administrative privileges."
                     " Click the 'Request Admin Rights' button to enable admin privileges.")
        except Exception as e:
            error_msg = f"Error checking admin status: {str(e)}"
            MessageHandler.error(error_msg)
    
    def show_about(self):
        """Show the about dialog with scrollable content"""
        about_window = tk.Toplevel(self)
        about_window.title("About WinPick")
        about_window.geometry("600x500")
        about_window.transient(self)
        about_window.grab_set()
        about_window.configure(bg=self.secondary_color)
        
        # Center on parent window
        x = self.winfo_x() + (self.winfo_width() // 2) - (600 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (500 // 2)
        about_window.geometry(f"+{x}+{y}")
        
        # Create a main canvas with scrollbar for the entire dialog
        main_canvas = tk.Canvas(about_window, bg=self.secondary_color)
        main_scrollbar = ttk.Scrollbar(about_window, orient=tk.VERTICAL, command=main_canvas.yview)
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
        
        about_window.bind("<Configure>", on_window_configure)
        
        # Logo and title
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create a simple logo using a canvas
        logo_canvas = tk.Canvas(header_frame, width=64, height=64, 
                               bg=self.secondary_color, highlightthickness=0)
        logo_canvas.pack(side=tk.LEFT)
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, padx=15)
        
        ttk.Label(title_frame, 
                text="WinPick", 
                font=("Segoe UI", 24, "bold"),
                foreground=self.primary_color).pack(anchor=tk.W)
        
        ttk.Label(title_frame, 
                text="Windows Script Manager",
                font=("Segoe UI", 12)).pack(anchor=tk.W)
        
        # Version and build info
        version_frame = ttk.Frame(frame)
        version_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(version_frame, 
                text="Version 25.4.12", # Updated version number
                font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        
        ttk.Label(version_frame,
                text="Built with ♥ for Windows 11 users",
                foreground=self.accent_color).pack(side=tk.RIGHT)
        
        # About text in a scrolled text widget
        from tkinter import scrolledtext
        
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        text = scrolledtext.ScrolledText(content_frame, 
                                        wrap=tk.WORD, 
                                        bg=self.bg_light, 
                                        font=("Segoe UI", 10),
                                        padx=10, pady=10,
                                        height=12)
        text.pack(fill=tk.BOTH, expand=True)
        
        about_text = """This application helps you manage and run Windows scripts.

Features:
- Organize scripts by category
- Run scripts with or without admin rights
- Undo script actions when supported
- Advanced console output display
- Modern user interface
- Rate scripts and share feedback
- Asynchronous loading for improved responsiveness

Developed by MikeTheTech
Support me on Patreon: https://www.patreon.com/c/mikethetech
"""
        text.insert(tk.END, about_text)
        text.config(state=tk.DISABLED)
        
        # Bottom buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=(20, 0))
        
        ttk.Button(button_frame, 
                text="Support on Patreon", 
                width=20,
                command=self.open_patreon).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, 
                text="OK", 
                width=15,
                command=about_window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Make sure we initialize the scroll region
        frame.update_idletasks()
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        # Remove mousewheel binding when the window is closed
        def on_close():
            main_canvas.unbind_all("<MouseWheel>")
            about_window.destroy()
            
        about_window.protocol("WM_DELETE_WINDOW", on_close)
    
    def __del__(self):
        """Cleanup when the app is being destroyed"""
        try:
            self.console_view.restore_output()
        except:
            pass