#!/usr/bin/env python3
"""
GitHub Authentication Module
Handles GitHub Device Flow authentication for the rating system
"""

import os
import json
import webbrowser
import requests
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

class GitHubAuthHandler:
    """Handles GitHub Device Flow authentication"""
    
    def __init__(self, parent=None, client_id="Ov23lir6NAb4i8wrTseJ", 
                 scope="public_repo"):
        self.parent = parent
        self.client_id = client_id
        self.scope = scope
        self.token = None
        self.user_info = None
        
        # Device flow URLs
        self.device_code_url = "https://github.com/login/device/code"
        self.token_url = "https://github.com/login/oauth/access_token"
        
        # Token cache path
        self.token_cache_path = os.path.join(os.path.expanduser("~"), ".winpick", "github_token.json")
        self.load_cached_token()
        
    def load_cached_token(self):
        """Load the cached GitHub token if available"""
        try:
            if not os.path.exists(os.path.dirname(self.token_cache_path)):
                os.makedirs(os.path.dirname(self.token_cache_path), exist_ok=True)
                return False
                
            if not os.path.exists(self.token_cache_path):
                return False
                
            with open(self.token_cache_path, 'r') as f:
                data = json.load(f)
                self.token = data.get('token')
                
                # Check if token is valid by fetching user info
                if self.token and self.get_user_info():
                    print("Loaded cached GitHub token")
                    return True
                else:
                    # Invalid token
                    self.token = None
                    return False
        except Exception as e:
            print(f"Error loading cached token: {str(e)}")
            self.token = None
            return False
    
    def save_token_to_cache(self):
        """Save the GitHub token to cache"""
        if not self.token:
            return
            
        try:
            if not os.path.exists(os.path.dirname(self.token_cache_path)):
                os.makedirs(os.path.dirname(self.token_cache_path), exist_ok=True)
                
            with open(self.token_cache_path, 'w') as f:
                json.dump({'token': self.token}, f)
                print("Saved GitHub token to cache")
        except Exception as e:
            print(f"Error saving token to cache: {str(e)}")
    
    def get_user_info(self):
        """Get user information using the GitHub token"""
        if not self.token:
            return None
            
        try:
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            response = requests.get('https://api.github.com/user', headers=headers)
            
            if response.status_code == 200:
                self.user_info = response.json()
                return self.user_info
            else:
                print(f"Error fetching user info: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error getting user info: {str(e)}")
            return None
    
    def is_authenticated(self):
        """Check if the user is authenticated with GitHub"""
        return self.token is not None and self.get_user_info() is not None
    
    def authenticate(self):
        """Start the GitHub Device Flow authentication"""
        if self.is_authenticated():
            # Already authenticated
            return True
        
        # Show a dialog to inform the user about the authentication process
        if self.parent:
            result = messagebox.askyesno(
                "GitHub Authentication",
                f"You need to authenticate with GitHub to use this feature.\n\n"
                f"This will show you a code that you will need to enter on GitHub's website.\n\n"
                f"Would you like to proceed?"
            )
            if not result:
                return False
        
        try:
            # Step 1: Request device and user verification codes
            headers = {
                'Accept': 'application/json'
            }
            data = {
                'client_id': self.client_id,
                'scope': self.scope
            }
            
            response = requests.post(self.device_code_url, headers=headers, data=data)
            
            if response.status_code != 200:
                print(f"Error requesting device code: {response.status_code}, {response.text}")
                if self.parent:
                    messagebox.showerror(
                        "Authentication Error",
                        f"Failed to start the authentication process.\n\n"
                        f"GitHub API response: {response.text}\n\n"
                        f"Please try again later."
                    )
                return False
            
            device_flow_data = response.json()
            device_code = device_flow_data.get('device_code')
            user_code = device_flow_data.get('user_code')
            verification_uri = device_flow_data.get('verification_uri')
            expires_in = int(device_flow_data.get('expires_in', 900))  # Default 15 minutes
            interval = int(device_flow_data.get('interval', 5))  # Default polling interval of 5 seconds
            
            # Display the user code and verification URL to the user
            if self.parent:
                self.show_device_code_dialog(user_code, verification_uri)
                
                # Start polling for the token in a separate thread
                thread = threading.Thread(
                    target=self._poll_for_token,
                    args=(device_code, interval, expires_in)
                )
                thread.daemon = True
                thread.start()
            else:
                # If no parent UI, give instructions in console
                print("\n=== GitHub Device Authentication ===")
                print(f"Open: {verification_uri}")
                print(f"Enter code: {user_code}")
                print("Waiting for you to complete the authentication...")
                
                # Poll for token directly
                result = self._poll_for_token(device_code, interval, expires_in)
                return result
                
            return True
        except Exception as e:
            print(f"Error starting authentication flow: {str(e)}")
            if self.parent:
                messagebox.showerror(
                    "Authentication Error",
                    f"Failed to start the authentication process: {str(e)}\n\n"
                    f"Please try again later."
                )
            return False
    
    def show_device_code_dialog(self, user_code, verification_uri):
        """Show a dialog with the device code and instructions"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("GitHub Authentication")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.resizable(False, False)
        
        # Make the window take priority
        dialog.lift()  # Raise it above other windows
        dialog.focus_force()  # Force focus to this window
        
        # Configure the dialog
        dialog.columnconfigure(0, weight=1)
        
        # Add instructions
        ttk.Label(dialog, text="GitHub Authentication Required", font=("", 14, "bold")).grid(
            row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        instruction_text = (
            "1. Go to the following URL in your browser:\n"
            f"{verification_uri}\n\n"
            "2. Enter the code below when prompted:\n"
        )
        ttk.Label(dialog, text=instruction_text, justify="left").grid(
            row=1, column=0, padx=20, pady=0, sticky="w")
        
        # Add the user code in a prominent display
        code_frame = ttk.Frame(dialog)
        code_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        code_frame.columnconfigure(0, weight=1)
        
        code_label = ttk.Label(
            code_frame, 
            text=user_code, 
            font=("Courier", 18, "bold"),
            background="#f0f0f0",
            padding=10
        )
        code_label.grid(sticky="ew")
        
        # Add a copy button
        def copy_code():
            dialog.clipboard_clear()
            dialog.clipboard_append(user_code)
            copy_btn.config(text="Copied!")
            dialog.after(2000, lambda: copy_btn.config(text="Copy Code"))
            
        copy_btn = ttk.Button(dialog, text="Copy Code", command=copy_code)
        copy_btn.grid(row=3, column=0, padx=20, pady=5)
        
        # Add a browser button
        def open_browser():
            webbrowser.open(verification_uri)
            
        browser_btn = ttk.Button(
            dialog, 
            text="Open Browser", 
            command=open_browser
        )
        browser_btn.grid(row=4, column=0, padx=20, pady=5)
        
        # Add status text
        self.status_var = tk.StringVar(value="Waiting for authentication...")
        status_label = ttk.Label(
            dialog, 
            textvariable=self.status_var,
            foreground="#666666",
            justify="center"
        )
        status_label.grid(row=5, column=0, padx=20, pady=(15, 20), sticky="ew")
        
        # Store reference to the dialog
        self.auth_dialog = dialog
        self.auth_success = False
        
        # Make the dialog stay on top initially to capture attention
        dialog.attributes('-topmost', True)
        # But allow it to go behind other windows if the user wants to
        dialog.after(3000, lambda: dialog.attributes('-topmost', False))
        
        # Auto-open browser
        dialog.after(500, open_browser)
    
    def _poll_for_token(self, device_code, interval, expires_in):
        """Poll for token using the device code"""
        headers = {
            'Accept': 'application/json'
        }
        data = {
            'client_id': self.client_id,
            'device_code': device_code,
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
        }
        
        start_time = time.time()
        
        while time.time() - start_time < expires_in:
            try:
                response = requests.post(self.token_url, headers=headers, data=data)
                response_data = response.json()
                
                if 'access_token' in response_data:
                    # Successfully got the token
                    self.token = response_data['access_token']
                    self.save_token_to_cache()
                    
                    # Get user info
                    user_info = self.get_user_info()
                    if user_info:
                        username = user_info.get('login', 'User')
                        print(f"Authenticated as: {username}")
                        
                        if hasattr(self, 'auth_dialog') and self.auth_dialog.winfo_exists():
                            self.status_var.set(f"Authentication successful! Welcome, {username}.")
                            self.auth_success = True
                            self.parent.after(2000, self.auth_dialog.destroy)
                    
                    return True
                    
                if 'error' in response_data:
                    error = response_data.get('error')
                    
                    if error == 'authorization_pending':
                        # Expected error, user hasn't authorized yet
                        if hasattr(self, 'status_var'):
                            self.status_var.set("Waiting for you to authorize in the browser...")
                    elif error == 'slow_down':
                        # GitHub is telling us to slow down our polling
                        interval += 5
                        if hasattr(self, 'status_var'):
                            self.status_var.set("Polling slowed down, please wait...")
                    elif error == 'expired_token':
                        # Token has expired
                        print("Device code expired. Please try again.")
                        if hasattr(self, 'status_var'):
                            self.status_var.set("Code expired. Please try again.")
                        if hasattr(self, 'auth_dialog') and self.auth_dialog.winfo_exists():
                            self.parent.after(2000, self.auth_dialog.destroy)
                        return False
                    elif error == 'access_denied':
                        # User declined the authorization
                        print("Authorization denied by user.")
                        if hasattr(self, 'status_var'):
                            self.status_var.set("Authorization denied. Please try again.")
                        if hasattr(self, 'auth_dialog') and self.auth_dialog.winfo_exists():
                            self.parent.after(2000, self.auth_dialog.destroy)
                        return False
                    else:
                        # Other error
                        print(f"Error during polling: {error}")
                        if hasattr(self, 'status_var'):
                            self.status_var.set(f"Error: {error}")
                        if hasattr(self, 'auth_dialog') and self.auth_dialog.winfo_exists():
                            self.parent.after(2000, self.auth_dialog.destroy)
                        return False
            
            except Exception as e:
                print(f"Error during token polling: {str(e)}")
                if hasattr(self, 'status_var'):
                    self.status_var.set(f"Connection error, retrying...")
            
            # Wait for the specified interval before polling again
            time.sleep(interval)
        
        # If we get here, we've exceeded the expiration time
        print("Authentication timed out.")
        if hasattr(self, 'status_var'):
            self.status_var.set("Authentication timed out. Please try again.")
        if hasattr(self, 'auth_dialog') and self.auth_dialog.winfo_exists():
            self.parent.after(2000, self.auth_dialog.destroy)
        return False
    
    def logout(self):
        """Log out the user by clearing the token"""
        self.token = None
        self.user_info = None
        
        # Remove the token cache file
        try:
            if os.path.exists(self.token_cache_path):
                os.remove(self.token_cache_path)
                print("Removed GitHub token cache")
        except Exception as e:
            print(f"Error removing token cache: {str(e)}")
        
        return True