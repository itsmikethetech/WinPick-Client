"""
GitHub Downloader
Functions for downloading scripts from GitHub repositories
"""

import os
import sys
import traceback
import tempfile
import shutil
import zipfile
import requests
import tkinter as tk
from tkinter import ttk, messagebox

class GitHubDownloader:
    def __init__(self, parent, base_dir):
        """
        Initialize the GitHub downloader
        
        Args:
            parent: The parent tkinter window
            base_dir: The base directory to download scripts to
        """
        self.parent = parent
        self.base_dir = base_dir
        self.primary_color = parent.primary_color
        self.secondary_color = parent.secondary_color
        self.accent_color = parent.accent_color
        self.text_color = parent.text_color
        self.bg_dark = parent.bg_dark
        self.bg_light = parent.bg_light
        self.style = parent.style
    
    def download_repository(self, repo_url, directory_path=None, branch="main"):
        """
        Download a directory from a GitHub repository
        
        Args:
            repo_url: GitHub repository URL (e.g., "https://github.com/username/repo")
            directory_path: Path to the directory within the repository to download (None for the whole repo)
            branch: Branch to download from
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Extract username and repository name from the URL
            parts = repo_url.rstrip('/').split('/')
            if 'github.com' not in parts:
                return False, "Invalid GitHub URL. It should be in the format: https://github.com/username/repository"
            
            username_idx = parts.index('github.com') + 1
            if username_idx >= len(parts):
                return False, "Invalid GitHub URL. Username not found."
            
            repo_idx = username_idx + 1
            if repo_idx >= len(parts):
                return False, "Invalid GitHub URL. Repository name not found."
            
            username = parts[username_idx]
            repository = parts[repo_idx]
            
            # Construct the API URL to get the content
            api_url = f"https://api.github.com/repos/{username}/{repository}/zipball/{branch}"
            
            print(f"Downloading from GitHub: {repo_url}, branch: {branch}")
            
            # Download the repository zip file
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "repo.zip")
            
            print(f"Downloading repository to: {zip_path}")
            response = requests.get(api_url, stream=True)
            
            if response.status_code != 200:
                return False, f"Failed to download from GitHub. Status code: {response.status_code}, Message: {response.text}"
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print("Download completed, extracting files...")
            
            # Extract the zip file
            extract_dir = os.path.join(temp_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find the extracted folder (it will have a name like username-repository-hash)
            extracted_items = os.listdir(extract_dir)
            if not extracted_items:
                return False, "Extraction failed: No files found in the downloaded repository."
            
            # The first item should be the repository folder
            repo_folder = os.path.join(extract_dir, extracted_items[0])
            
            if directory_path:
                # If a specific directory was requested, use that
                repo_folder = os.path.join(repo_folder, directory_path)
                if not os.path.exists(repo_folder):
                    return False, f"Directory '{directory_path}' not found in the repository."
            
            # Now, ask if the user wants to overwrite existing files
            overwrite_all = False
            skip_all = False
            file_count = 0
            
            # Recursively copy files, asking for overwrite confirmation as needed
            for root, dirs, files in os.walk(repo_folder):
                # Get the relative path from the repo_folder
                rel_path = os.path.relpath(root, repo_folder)
                # Create the destination directory
                dest_dir = os.path.join(self.base_dir, rel_path) if rel_path != '.' else self.base_dir
                os.makedirs(dest_dir, exist_ok=True)
                
                # Copy all files, asking for overwrite confirmation if needed
                for file in files:
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_dir, file)
                    
                    if os.path.exists(dest_file) and not overwrite_all and not skip_all:
                        # File already exists, ask for confirmation
                        result = self.show_overwrite_dialog(file, dest_file)
                        if result == "overwrite":
                            shutil.copy2(src_file, dest_file)
                            file_count += 1
                            print(f"Overwritten file: {dest_file}")
                        elif result == "overwrite_all":
                            overwrite_all = True
                            shutil.copy2(src_file, dest_file)
                            file_count += 1
                            print(f"Overwritten file: {dest_file}")
                        elif result == "skip":
                            print(f"Skipped file: {dest_file}")
                        elif result == "skip_all":
                            skip_all = True
                            print(f"Skipped file: {dest_file}")
                        elif result == "cancel":
                            print("Download cancelled by user.")
                            return False, "Download cancelled by user."
                    elif os.path.exists(dest_file) and overwrite_all:
                        # Overwrite all files
                        shutil.copy2(src_file, dest_file)
                        file_count += 1
                        print(f"Overwritten file: {dest_file}")
                    elif not os.path.exists(dest_file) or skip_all:
                        # File doesn't exist, just copy it
                        if not skip_all or not os.path.exists(dest_file):
                            shutil.copy2(src_file, dest_file)
                            file_count += 1
                            print(f"Copied file: {dest_file}")
            
            # Clean up temp files
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Warning: Failed to clean up temporary files: {str(e)}")
            
            return True, f"Successfully downloaded {file_count} files from GitHub."
            
        except Exception as e:
            error_msg = f"Error downloading from GitHub: {str(e)}\n{traceback.format_exc()}"
            print(f"ERROR: {error_msg}")
            return False, error_msg
    
    def show_overwrite_dialog(self, filename, filepath):
        """
        Show a dialog asking whether to overwrite an existing file
        
        Args:
            filename: The name of the file
            filepath: The full path to the file
            
        Returns:
            str: One of "overwrite", "overwrite_all", "skip", "skip_all", "cancel"
        """
        dialog = tk.Toplevel(self.parent)
        dialog.title("File Exists")
        dialog.geometry("450x250")
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.configure(bg=self.secondary_color)
        
        # Center dialog on parent window
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (450 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (250 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Make dialog modal
        dialog.focus_set()
        dialog.protocol("WM_DELETE_WINDOW", lambda: dialog.destroy())
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Warning icon and message
        warning_frame = ttk.Frame(frame)
        warning_frame.pack(fill=tk.X, pady=10)
        
        # Create a warning symbol
        warning_label = ttk.Label(warning_frame, 
                                 text="⚠️", 
                                 font=("Segoe UI", 24),
                                 foreground=self.accent_color)
        warning_label.pack(side=tk.LEFT, padx=(0, 10))
        
        message_frame = ttk.Frame(warning_frame)
        message_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(message_frame, 
                 text="File Already Exists", 
                 font=("Segoe UI", 12, "bold"),
                 foreground=self.text_color).pack(anchor=tk.W)
        
        ttk.Label(message_frame, 
                 text=f"The file {filename} already exists in the destination directory.",
                 wraplength=350).pack(anchor=tk.W, pady=5)
        
        ttk.Label(message_frame,
                 text=f"Path: {filepath}",
                 foreground=self.primary_color,
                 wraplength=350).pack(anchor=tk.W)
        
        # Result variable
        result = tk.StringVar(value="cancel")
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        cancel_btn = ttk.Button(button_frame, 
                              text="Cancel", 
                              width=15,
                              command=lambda: [result.set("cancel"), dialog.destroy()])
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        skip_all_btn = ttk.Button(button_frame, 
                                text="Skip All", 
                                width=15,
                                command=lambda: [result.set("skip_all"), dialog.destroy()])
        skip_all_btn.pack(side=tk.RIGHT, padx=5)
        
        skip_btn = ttk.Button(button_frame, 
                            text="Skip", 
                            width=15,
                            command=lambda: [result.set("skip"), dialog.destroy()])
        skip_btn.pack(side=tk.RIGHT, padx=5)
        
        overwrite_all_btn = ttk.Button(button_frame, 
                                     text="Overwrite All", 
                                     width=15,
                                     command=lambda: [result.set("overwrite_all"), dialog.destroy()])
        overwrite_all_btn.pack(side=tk.LEFT, padx=5)
        
        overwrite_btn = ttk.Button(button_frame, 
                                 text="Overwrite", 
                                 width=15,
                                 command=lambda: [result.set("overwrite"), dialog.destroy()])
        overwrite_btn.pack(side=tk.LEFT, padx=5)
        
        # Wait for the dialog to be closed
        dialog.wait_window()
        
        return result.get()
    
    def show_download_dialog(self):
        """Show a dialog to download scripts from GitHub"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Download Scripts from GitHub")
        dialog.geometry("550x400")
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.configure(bg=self.secondary_color)
        
        # Center dialog on parent window
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (550 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (400 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, 
                               text="Download Scripts from GitHub", 
                               font=("Segoe UI", 16, "bold"),
                               foreground=self.primary_color)
        title_label.pack(side=tk.LEFT)
        
        # GitHub icon
        github_label = ttk.Label(title_frame, 
                                text="⟳", 
                                font=("Segoe UI", 20))
        github_label.pack(side=tk.RIGHT)
        
        # Repository input
        repo_frame = ttk.Frame(frame)
        repo_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(repo_frame, 
                 text="Repository URL:", 
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        repo_var = tk.StringVar(value="https://github.com/itsmikethetech/WinPick-Scripts")
        repo_entry = ttk.Entry(repo_frame, textvariable=repo_var, width=50)
        repo_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Branch input
        ttk.Label(repo_frame, 
                 text="Branch:", 
                 font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        branch_var = tk.StringVar(value="main")
        branch_entry = ttk.Entry(repo_frame, textvariable=branch_var, width=20)
        branch_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Directory input
        ttk.Label(repo_frame, 
                 text="Directory to Download:", 
                 font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        dir_var = tk.StringVar(value="WindowsScripts")
        dir_entry = ttk.Entry(repo_frame, textvariable=dir_var, width=30)
        dir_entry.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Help text
        help_frame = ttk.Frame(frame)
        help_frame.pack(fill=tk.X, pady=10)
        
        help_text = ttk.Label(help_frame, 
                             text="This will download scripts from the specified GitHub repository and directory.\n\n"
                                  "The default URL and directory are set to download the WindowsScripts directory from\n"
                                  "the official WinPick-Scripts repository, which contains recommended scripts.",
                             wraplength=500,
                             justify=tk.LEFT)
        help_text.pack(anchor=tk.W)
        
        # Status display
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        status_var = tk.StringVar(value="Ready to download")
        status_label = ttk.Label(status_frame, textvariable=status_var)
        status_label.pack(fill=tk.X, pady=5)
        
        # Progress bar
        progress_var = tk.DoubleVar(value=0.0)
        progress_bar = ttk.Progressbar(status_frame, variable=progress_var, mode="indeterminate")
        progress_bar.pack(fill=tk.X, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def start_download():
            # Update status and disable buttons
            status_var.set("Downloading from GitHub...")
            progress_bar.start(10)
            download_btn.config(state="disabled")
            cancel_btn.config(state="disabled")
            
            # Start download in a separate thread
            import threading
            def download_thread():
                try:
                    # Get values from the entries
                    repo_url = repo_var.get().strip()
                    branch = branch_var.get().strip()
                    dir_path = dir_var.get().strip()
                    
                    # Validate inputs
                    if not repo_url:
                        status_var.set("Error: Repository URL is required.")
                        download_btn.config(state="normal")
                        cancel_btn.config(state="normal")
                        progress_bar.stop()
                        return
                    
                    if not branch:
                        branch = "main"
                    
                    # Perform the download
                    success, message = self.download_repository(repo_url, dir_path, branch)
                    
                    if success:
                        # Show success message
                        status_var.set("Download completed successfully!")
                        
                        # Schedule dialog closure after a delay
                        self.parent.after(2000, dialog.destroy)
                        
                        # Update the UI to refresh the script list
                        self.parent.refresh_view()
                        
                        # Show a success message
                        messagebox.showinfo("Download Complete", message)
                    else:
                        # Show error message
                        status_var.set(f"Error: {message}")
                        download_btn.config(state="normal")
                        cancel_btn.config(state="normal")
                
                except Exception as e:
                    error_msg = f"Error during download: {str(e)}\n{traceback.format_exc()}"
                    print(f"ERROR: {error_msg}")
                    status_var.set(f"Error: {str(e)}")
                    download_btn.config(state="normal")
                    cancel_btn.config(state="normal")
                
                finally:
                    # Stop the progress bar
                    progress_bar.stop()
            
            # Start the download thread
            download_thread = threading.Thread(target=download_thread)
            download_thread.daemon = True
            download_thread.start()
        
        cancel_btn = ttk.Button(button_frame, 
                              text="Cancel", 
                              width=15,
                              command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        download_btn = ttk.Button(button_frame, 
                                text="Download", 
                                width=15,
                                command=start_download)
        download_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set focus to the repository entry
        repo_entry.focus_set()
