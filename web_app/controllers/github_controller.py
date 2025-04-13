#!/usr/bin/env python3
"""
GitHub Controller for Web App
Handles GitHub repository operations for web interface
"""

import os
import sys
import re
import tempfile
import shutil
import requests
import zipfile
import traceback

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.message_handler import MessageHandler

class GitHubDownloaderWeb:
    """Web-friendly version of GitHubDownloader without Tkinter dependencies"""
    
    def __init__(self):
        """Initialize the GitHub downloader for web"""
        pass
        
    def download_repository(self, repo_url, output_dir, progress_callback=None, branch="main"):
        """
        Download a directory from a GitHub repository
        
        Args:
            repo_url: GitHub repository URL (e.g., "https://github.com/username/repo")
            output_dir: Directory to save downloaded files
            progress_callback: Optional callback for progress updates
            branch: Branch to download from
            
        Returns:
            bool: Success status
        """
        try:
            # Extract username and repository name from the URL
            parts = repo_url.rstrip('/').split('/')
            if 'github.com' not in parts:
                if progress_callback:
                    progress_callback("Invalid GitHub URL. It should be in the format: https://github.com/username/repository")
                return False
            
            username_idx = parts.index('github.com') + 1
            if username_idx >= len(parts):
                if progress_callback:
                    progress_callback("Invalid GitHub URL. Username not found.")
                return False
            
            repo_idx = username_idx + 1
            if repo_idx >= len(parts):
                if progress_callback:
                    progress_callback("Invalid GitHub URL. Repository name not found.")
                return False
            
            username = parts[username_idx]
            repository = parts[repo_idx]
            
            # Check if repository path contains a branch and subdirectory specification
            # Example: https://github.com/username/repo/tree/branch/folder
            subdirectory = None
            if '/tree/' in repo_url:
                tree_parts = repo_url.split('/tree/', 1)[1].split('/')
                if len(tree_parts) > 1:  # Contains both branch and subdirectory
                    branch = tree_parts[0]
                    subdirectory = '/'.join(tree_parts[1:])
                    if progress_callback:
                        progress_callback(f"Detected subdirectory: {subdirectory}")
                elif len(tree_parts) == 1:  # Only contains branch
                    branch = tree_parts[0]
            
            # Construct the API URL to get the content
            api_url = f"https://api.github.com/repos/{username}/{repository}/zipball/{branch}"
            
            if progress_callback:
                progress_callback(f"Downloading from GitHub: {repo_url}, branch: {branch}")
            
            # Download the repository zip file
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "repo.zip")
            
            if progress_callback:
                progress_callback(f"Downloading repository to temporary file")
            
            response = requests.get(api_url, stream=True)
            
            if response.status_code != 200:
                error_msg = f"Failed to download from GitHub. Status code: {response.status_code}"
                if progress_callback:
                    progress_callback(error_msg)
                return False
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            last_progress = 0
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Report download progress every 10%
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            if progress >= last_progress + 10:
                                last_progress = progress
                                if progress_callback:
                                    progress_callback(f"Downloaded {progress}% ({downloaded_size/1024:.1f} KB / {total_size/1024:.1f} KB)")
            
            if progress_callback:
                progress_callback("Download completed, extracting files...")
            
            # Extract the zip file
            extract_dir = os.path.join(temp_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find the extracted folder (it will have a name like username-repository-hash)
            extracted_items = os.listdir(extract_dir)
            if not extracted_items:
                if progress_callback:
                    progress_callback("Extraction failed: No files found in the downloaded repository.")
                return False
            
            # The first item should be the repository folder
            repo_folder = os.path.join(extract_dir, extracted_items[0])
            
            # If a subdirectory was specified, use that
            if subdirectory:
                sub_path = os.path.join(repo_folder, subdirectory)
                if os.path.exists(sub_path) and os.path.isdir(sub_path):
                    repo_folder = sub_path
                    if progress_callback:
                        progress_callback(f"Using subdirectory: {subdirectory}")
                else:
                    if progress_callback:
                        progress_callback(f"Warning: Specified subdirectory '{subdirectory}' not found, using repository root")
            
            if progress_callback:
                progress_callback(f"Copying files to output directory: {output_dir}")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Copy all files to output directory
            file_count = 0
            script_extensions = ['.ps1', '.py', '.bat', '.cmd', '.exe']
            
            for root, dirs, files in os.walk(repo_folder):
                # Get the relative path from the repo_folder
                rel_path = os.path.relpath(root, repo_folder)
                
                for file in files:
                    # Check if it's a script file
                    _, ext = os.path.splitext(file)
                    if ext.lower() in script_extensions:
                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(output_dir, file if rel_path == '.' else os.path.join(rel_path, file))
                        
                        # Create destination directory if needed
                        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                        
                        # Copy the file
                        shutil.copy2(src_file, dest_file)
                        file_count += 1
                        if progress_callback:
                            progress_callback(f"Copied script: {os.path.relpath(dest_file, output_dir)}")
            
            if progress_callback:
                progress_callback(f"Successfully copied {file_count} script files")
            
            # Clean up temp files
            try:
                shutil.rmtree(temp_dir)
                if progress_callback:
                    progress_callback("Cleaned up temporary files")
            except Exception as e:
                if progress_callback:
                    progress_callback(f"Warning: Failed to clean up temporary files: {str(e)}")
            
            return True
            
        except Exception as e:
            error_msg = f"Error downloading from GitHub: {str(e)}"
            if progress_callback:
                progress_callback(f"ERROR: {error_msg}")
            return False

class GitHubController:
    """Controller for GitHub operations"""
    
    def __init__(self, parent=None, base_dir=None):
        self.parent = parent
        self.base_dir = base_dir
        self.downloader = GitHubDownloaderWeb()
    
    def download_scripts_from_repo_web(self, repo_url, output_dir, output_callback=None, branch="main", preserve_structure=True):
        """
        Download scripts from a GitHub repository for web interface
        
        Args:
            repo_url: GitHub repository URL
            output_dir: Base directory to save scripts
            output_callback: Optional callback for logging
            branch: Repository branch to download from
            preserve_structure: Whether to preserve the repository folder structure
            
        Returns:
            dict: Result information with success status and message
        """
        if not repo_url:
            return {'success': False, 'message': "Repository URL is required"}
        
        # Validate URL format
        valid_url_pattern = r'^https?://github\.com/[\w-]+/[\w.-]+(/tree/[\w.-]+(/[\w.-]+)*)?$'
        if not re.match(valid_url_pattern, repo_url):
            return {'success': False, 'message': "Invalid GitHub repository URL"}
        
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            if output_callback:
                output_callback(f"\n{'='*50}")
                output_callback(f"Downloading from: {repo_url}")
                output_callback(f"Branch: {branch}")
                output_callback(f"To: {output_dir}")
                output_callback(f"Preserving folder structure: {preserve_structure}")
                output_callback(f"{'='*50}\n")
            
            # Create a temporary directory for downloads
            with tempfile.TemporaryDirectory() as temp_dir:
                if output_callback:
                    output_callback(f"Created temporary directory for download")
                
                # Extract username and repository name
                try:
                    parts = repo_url.rstrip('/').split('/')
                    username_idx = parts.index('github.com') + 1
                    repo_idx = username_idx + 1
                    
                    if username_idx < len(parts) and repo_idx < len(parts):
                        username = parts[username_idx]
                        repository = parts[repo_idx]
                        # Only add prefix if it's not the default WinPick-Scripts repo
                        default_repo = "itsmikethetech/WinPick-Scripts"
                        repo_key = f"{username}/{repository}"
                        is_default_repo = repo_key.lower() == default_repo.lower()
                        repo_prefix = "" if is_default_repo else f"{username.lower()}-{repository.lower()}-"
                    else:
                        is_default_repo = False
                        repo_prefix = ""
                except Exception:
                    is_default_repo = False
                    repo_prefix = ""
                
                # Download repository content
                try:
                    if output_callback:
                        output_callback("Downloading repository content...")
                    
                    # Download to temp directory
                    download_success = self.downloader.download_repository(
                        repo_url, 
                        temp_dir,
                        branch=branch,
                        progress_callback=lambda msg: output_callback(msg) if output_callback else None
                    )
                    
                    if not download_success:
                        return {'success': False, 'message': "Failed to download repository content"}
                        
                    if output_callback:
                        output_callback("Download completed successfully")
                    
                    # Copy the files with proper structure
                    if preserve_structure:
                        # For the default repo or when preserving structure is enabled, copy with structure
                        copied_files = self._copy_with_structure(
                            temp_dir, 
                            output_dir, 
                            output_callback,
                            repo_prefix=repo_prefix if not is_default_repo else "",
                            is_default_repo=is_default_repo
                        )
                    else:
                        # When not preserving structure, copy to flat directory
                        copied_files = self._copy_scripts_to_category(
                            temp_dir, 
                            output_dir, 
                            output_callback, 
                            repo_prefix
                        )
                    
                    return {
                        'success': True, 
                        'message': f"Successfully downloaded {copied_files} scripts from {repo_url}",
                        'files_count': copied_files
                    }
                    
                except Exception as e:
                    error_msg = f"Error downloading repository: {str(e)}"
                    if output_callback:
                        output_callback(f"ERROR: {error_msg}")
                    return {'success': False, 'message': error_msg}
        
        except Exception as e:
            error_msg = f"Error in download process: {str(e)}"
            if output_callback:
                output_callback(f"ERROR: {error_msg}")
            return {'success': False, 'message': error_msg}
    
    def _copy_scripts_to_category(self, source_dir, category_path, output_callback=None, repo_prefix=""):
        """Copy script files from temp directory to category directory (flat structure)"""
        script_extensions = ['.ps1', '.py', '.bat', '.cmd', '.exe']
        copied_files = 0
        
        try:
            if output_callback:
                output_callback("Copying scripts to category directory...")
            
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    _, ext = os.path.splitext(file)
                    if ext.lower() in script_extensions:
                        source_file = os.path.join(root, file)
                        
                        # Add repo prefix to filename for non-default repos if specified
                        if repo_prefix:
                            base_name, file_ext = os.path.splitext(file)
                            dest_filename = f"{repo_prefix}{base_name}{file_ext}"
                        else:
                            dest_filename = file
                            
                        dest_file = os.path.join(category_path, dest_filename)
                        
                        # Check if destination file already exists
                        if os.path.exists(dest_file):
                            if output_callback:
                                output_callback(f"Overwriting existing file: {dest_filename}")
                        else:
                            if output_callback:
                                output_callback(f"Copying new file: {dest_filename}")
                                
                        # Copy the file
                        shutil.copy2(source_file, dest_file)
                        copied_files += 1
            
            if output_callback:
                output_callback(f"Successfully copied {copied_files} script files")
                
            return copied_files
                
        except Exception as e:
            error_msg = f"Error copying scripts: {str(e)}"
            if output_callback:
                output_callback(f"ERROR: {error_msg}")
            return 0
            
    def _copy_with_structure(self, source_dir, output_dir, output_callback=None, repo_prefix="", is_default_repo=False):
        """Copy files from temp directory to output directory preserving folder structure"""
        script_extensions = ['.ps1', '.py', '.bat', '.cmd', '.exe']
        copied_files = 0
        
        try:
            if output_callback:
                output_callback("Copying repository contents with folder structure...")
            
            # Find the root of the extracted repository (typically has a username-repo-hash format)
            extract_items = os.listdir(source_dir)
            if not extract_items:
                if output_callback:
                    output_callback("Error: No files found in the downloaded repository")
                return 0
                
            # Extract root is the first item (which should be a folder)
            extract_root = os.path.join(source_dir, extract_items[0])
            if not os.path.isdir(extract_root):
                extract_root = source_dir
            
            if output_callback:
                output_callback(f"Processing repository contents from: {os.path.basename(extract_root)}")
            
            # Walk through the extracted repository
            for root, dirs, files in os.walk(extract_root):
                # Get the path relative to the extract root
                rel_path = os.path.relpath(root, extract_root)
                
                # Create the corresponding directory in the output
                if rel_path != '.':
                    target_dir = os.path.join(output_dir, rel_path)
                    os.makedirs(target_dir, exist_ok=True)
                else:
                    target_dir = output_dir
                
                # Copy each file
                for file in files:
                    _, ext = os.path.splitext(file)
                    # Only copy script files
                    if ext.lower() in script_extensions:
                        source_file = os.path.join(root, file)
                        
                        # If not the default repo and a prefix is specified, add prefix to filename
                        if repo_prefix and not is_default_repo:
                            base_name, file_ext = os.path.splitext(file)
                            dest_filename = f"{repo_prefix}{base_name}{file_ext}"
                        else:
                            dest_filename = file
                            
                        dest_file = os.path.join(target_dir, dest_filename)
                        
                        # Check if destination file already exists
                        if os.path.exists(dest_file):
                            if output_callback:
                                rel_dest = os.path.relpath(dest_file, output_dir)
                                output_callback(f"Overwriting existing file: {rel_dest}")
                        else:
                            if output_callback:
                                rel_dest = os.path.relpath(dest_file, output_dir)
                                output_callback(f"Copying new file: {rel_dest}")
                        
                        # Create parent directory if it doesn't exist
                        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                        
                        # Copy the file
                        shutil.copy2(source_file, dest_file)
                        copied_files += 1
            
            if output_callback:
                output_callback(f"Successfully copied {copied_files} script files with folder structure")
                
            return copied_files
                
        except Exception as e:
            error_msg = f"Error copying scripts with structure: {str(e)}"
            if output_callback:
                output_callback(f"ERROR: {error_msg}")
            return 0