#!/usr/bin/env python3
"""
GitHub Authentication Handler for Web App
A web-friendly version of the GitHubAuthHandler without Tkinter dependencies
"""

import os
import sys
import json
import requests
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class GitHubAuthHandlerWeb:
    """Handles GitHub Device Flow authentication for web interface"""
    
    def __init__(self, client_id="Ov23lir6NAb4i8wrTseJ", scope="public_repo"):
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
    
    def get_username(self):
        """Get the GitHub username of the authenticated user"""
        if self.user_info:
            return self.user_info.get('login')
        
        user_info = self.get_user_info()
        if user_info:
            return user_info.get('login')
            
        return None
    
    def is_authenticated(self):
        """Check if the user is authenticated with GitHub"""
        return self.token is not None and self.get_user_info() is not None
    
    def authenticate(self):
        """
        Start the GitHub Device Flow authentication
        For web app, this will return device flow information for the front-end to handle
        """
        if self.is_authenticated():
            # Already authenticated
            return True
        
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
                return False
            
            device_flow_data = response.json()
            device_code = device_flow_data.get('device_code')
            
            # Start polling for the token in the current thread for simplicity in web app
            result = self._poll_for_token(
                device_code, 
                int(device_flow_data.get('interval', 5)),
                int(device_flow_data.get('expires_in', 900))
            )
            
            return result
            
        except Exception as e:
            print(f"Error starting authentication flow: {str(e)}")
            return False
    
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
                    
                    return True
                    
                if 'error' in response_data:
                    error = response_data.get('error')
                    
                    if error == 'authorization_pending':
                        # Expected error, user hasn't authorized yet
                        pass
                    elif error == 'slow_down':
                        # GitHub is telling us to slow down our polling
                        interval += 5
                    elif error == 'expired_token':
                        # Token has expired
                        print("Device code expired. Please try again.")
                        return False
                    elif error == 'access_denied':
                        # User declined the authorization
                        print("Authorization denied by user.")
                        return False
                    else:
                        # Other error
                        print(f"Error during polling: {error}")
                        return False
            
            except Exception as e:
                print(f"Error during token polling: {str(e)}")
            
            # Wait for the specified interval before polling again
            time.sleep(interval)
        
        # If we get here, we've exceeded the expiration time
        print("Authentication timed out.")
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