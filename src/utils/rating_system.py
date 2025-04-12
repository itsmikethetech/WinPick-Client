#!/usr/bin/env python3
"""
Rating System Module
Handles script ratings using GitHub Issues
"""

import json
import re
import requests
import tkinter as tk
from tkinter import ttk, messagebox
import os
import time
from datetime import datetime

class RatingSystem:
    """Manages script ratings using GitHub Issues"""
    
    def __init__(self, auth_handler, repo_owner="itsmikethetech", repo_name="WinPick-Feedback"):
        self.auth_handler = auth_handler
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.ratings_cache = {}
        self.ratings_cache_time = {}
        self.rating_cache_file = os.path.join(os.path.expanduser("~"), ".winpick", "script_ratings.json")
        
        # Create cache directory if it doesn't exist
        os.makedirs(os.path.dirname(self.rating_cache_file), exist_ok=True)
        
        # Load cached ratings
        self.load_cached_ratings()
    
    def load_cached_ratings(self):
        """Load cached ratings from file"""
        try:
            if os.path.exists(self.rating_cache_file):
                with open(self.rating_cache_file, 'r') as f:
                    cache_data = json.load(f)
                    self.ratings_cache = cache_data.get('ratings', {})
                    self.ratings_cache_time = cache_data.get('cache_time', {})
                    print(f"Loaded {len(self.ratings_cache)} cached ratings")
        except Exception as e:
            print(f"Error loading cached ratings: {str(e)}")
            self.ratings_cache = {}
            self.ratings_cache_time = {}
    
    def save_cached_ratings(self):
        """Save ratings cache to file"""
        try:
            with open(self.rating_cache_file, 'w') as f:
                json.dump({
                    'ratings': self.ratings_cache,
                    'cache_time': self.ratings_cache_time
                }, f)
                print(f"Saved {len(self.ratings_cache)} ratings to cache")
        except Exception as e:
            print(f"Error saving ratings cache: {str(e)}")
    
    def get_script_id(self, script_path, script_name):
        """Generate a unique ID for a script based on its path and name"""
        # Create a unique identifier for the script
        script_filename = os.path.basename(script_path)
        return f"{script_name}_{script_filename}"
    
    def get_rating(self, script_path, script_name, force_refresh=False):
        """
        Get the rating for a script
        
        Args:
            script_path: Path to the script file
            script_name: Name of the script
            force_refresh: Whether to force a refresh from the server
            
        Returns:
            dict: Rating information or None if no rating
        """
        script_id = self.get_script_id(script_path, script_name)
        
        # Check if we have a cached rating and it's less than 30 minutes old
        cache_time = self.ratings_cache_time.get(script_id, 0)
        if not force_refresh and script_id in self.ratings_cache and time.time() - cache_time < 1800:  # 30 minutes
            return self.ratings_cache[script_id]
        
        # If not authenticated, return cached rating if available, otherwise None
        if not self.auth_handler.is_authenticated():
            return self.ratings_cache.get(script_id)
        
        try:
            # Search for issues with the script ID in the title
            headers = {
                'Authorization': f'token {self.auth_handler.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Use the GitHub search API to find issues
            query = f'repo:{self.repo_owner}/{self.repo_name} in:title "{script_id}" type:issue'
            response = requests.get(
                f'https://api.github.com/search/issues?q={query}',
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"Error searching for ratings: {response.status_code}")
                return self.ratings_cache.get(script_id)
            
            data = response.json()
            issues = data.get('items', [])
            
            if not issues:
                # No ratings found
                self.ratings_cache[script_id] = None
                self.ratings_cache_time[script_id] = time.time()
                self.save_cached_ratings()
                return None
            
            # Parse the rating information from the most recent issue
            latest_issue = issues[0]
            for issue in issues:
                if issue['created_at'] > latest_issue['created_at']:
                    latest_issue = issue
            
            title = latest_issue['title']
            body = latest_issue['body']
            
            # Extract the rating value from the title
            # Format: "Script Rating: [ScriptID] - [RatingValue]/5"
            rating_match = re.search(r'(\d+)\/5', title)
            if not rating_match:
                return None
            
            rating_value = int(rating_match.group(1))
            
            # Parse the comment and user info
            rating_info = {
                'rating': rating_value,
                'comment': body,
                'user': latest_issue['user']['login'],
                'date': latest_issue['created_at'],
                'url': latest_issue['html_url'],
                'id': latest_issue['number']
            }
            
            # Cache the rating
            self.ratings_cache[script_id] = rating_info
            self.ratings_cache_time[script_id] = time.time()
            self.save_cached_ratings()
            
            return rating_info
            
        except Exception as e:
            print(f"Error getting rating: {str(e)}")
            return self.ratings_cache.get(script_id)
    
    def submit_rating(self, script_path, script_name, rating, comment=""):
        """
        Submit a rating for a script
        
        Args:
            script_path: Path to the script file
            script_name: Name of the script
            rating: Rating value (1-5)
            comment: Optional comment
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.auth_handler.is_authenticated():
            return False
        
        if rating < 1 or rating > 5:
            print("Invalid rating value. Must be between 1 and 5.")
            return False
        
        script_id = self.get_script_id(script_path, script_name)
        
        try:
            headers = {
                'Authorization': f'token {self.auth_handler.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Create issue title and body
            title = f"Script Rating: {script_id} - {rating}/5"
            
            # Add more information to the issue body
            body = comment if comment else "No comment provided."
            body += f"\n\n**Script Name:** {script_name}\n"
            body += f"**Script Path:** {os.path.basename(script_path)}\n"
            body += f"**Rating:** {rating}/5\n"
            body += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            # Create a new issue in the feedback repository
            response = requests.post(
                f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues',
                headers=headers,
                json={
                    'title': title,
                    'body': body,
                    'labels': ['script-rating']
                }
            )
            
            if response.status_code != 201:
                print(f"Error submitting rating: {response.status_code}")
                print(response.text)
                return False
            
            # Update the cache with the new rating
            issue_data = response.json()
            rating_info = {
                'rating': rating,
                'comment': comment,
                'user': self.auth_handler.user_info['login'],
                'date': issue_data['created_at'],
                'url': issue_data['html_url'],
                'id': issue_data['number']
            }
            
            self.ratings_cache[script_id] = rating_info
            self.ratings_cache_time[script_id] = time.time()
            self.save_cached_ratings()
            
            return True
            
        except Exception as e:
            print(f"Error submitting rating: {str(e)}")
            return False
    
    def get_average_rating(self, script_path, script_name):
        """Get the average rating for a script"""
        script_id = self.get_script_id(script_path, script_name)
        
        try:
            # If not authenticated, return None
            if not self.auth_handler.is_authenticated():
                # Return cached value if available
                if script_id in self.ratings_cache:
                    return self.ratings_cache[script_id]['rating']
                return None
            
            # Search for all issues with the script ID in the title
            headers = {
                'Authorization': f'token {self.auth_handler.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Use the GitHub search API to find issues
            query = f'repo:{self.repo_owner}/{self.repo_name} in:title "{script_id}" type:issue'
            response = requests.get(
                f'https://api.github.com/search/issues?q={query}',
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"Error searching for ratings: {response.status_code}")
                return None
            
            data = response.json()
            issues = data.get('items', [])
            
            if not issues:
                # No ratings found
                return None
            
            # Extract ratings from all issues
            all_ratings = []
            for issue in issues:
                title = issue['title']
                rating_match = re.search(r'(\d+)\/5', title)
                if rating_match:
                    rating_value = int(rating_match.group(1))
                    all_ratings.append(rating_value)
            
            if not all_ratings:
                return None
            
            # Calculate the average rating
            average_rating = sum(all_ratings) / len(all_ratings)
            return round(average_rating, 1)
            
        except Exception as e:
            print(f"Error calculating average rating: {str(e)}")
            return None
    
    def show_rating_dialog(self, parent, script_info):
        """
        Show a dialog to view and submit ratings
        
        Args:
            parent: Parent tkinter window
            script_info: Dictionary with script information
            
        Returns:
            None
        """
        if not script_info:
            return
        
        script_path = script_info['path']
        script_name = script_info['name']
        
        # Check if user is authenticated
        if not self.auth_handler.is_authenticated():
            if not self.auth_handler.authenticate():
                messagebox.showinfo(
                    "Authentication Required", 
                    "You need to authenticate with GitHub to view and submit ratings."
                )
                return
        
        # Get existing rating
        rating_info = self.get_rating(script_path, script_name)
        average_rating = self.get_average_rating(script_path, script_name)
        
        # Create the dialog
        dialog = tk.Toplevel(parent)
        dialog.title(f"Rate Script: {script_name}")
        dialog.geometry("550x400")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center on parent window
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (550 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (400 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Get theme colors from parent
        try:
            bg_color = parent.secondary_color
            primary_color = parent.primary_color
            text_color = parent.text_color
        except:
            bg_color = "#f0f0f0"
            primary_color = "#4a86e8"
            text_color = "#333333"
        
        dialog.configure(bg=bg_color)
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with script info
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            header_frame, 
            text=f"Rating for: {script_name}", 
            font=("Segoe UI", 14, "bold"),
            foreground=primary_color
        ).pack(anchor=tk.W)
        
        ttk.Label(
            header_frame,
            text=f"Script Type: {script_info['type']} | Developer: {script_info['developer']}",
            font=("Segoe UI", 10)
        ).pack(anchor=tk.W, pady=(5, 0))
        
        # Display average rating if available
        if average_rating is not None:
            avg_frame = ttk.Frame(main_frame)
            avg_frame.pack(fill=tk.X, pady=(0, 15))
            
            ttk.Label(
                avg_frame,
                text="Average Rating:",
                font=("Segoe UI", 12, "bold")
            ).grid(row=0, column=0, sticky=tk.W)
            
            # Create star display for average rating
            stars_frame = ttk.Frame(avg_frame)
            stars_frame.grid(row=0, column=1, padx=(10, 0))
            
            # Display star characters based on rating (★ for filled, ☆ for empty)
            full_stars = int(average_rating)
            half_star = average_rating - full_stars >= 0.5
            empty_stars = 5 - full_stars - (1 if half_star else 0)
            
            star_text = "★" * full_stars
            if half_star:
                star_text += "½"
            star_text += "☆" * empty_stars
            
            ttk.Label(
                stars_frame,
                text=star_text,
                font=("Segoe UI", 14),
                foreground="#FFD700"  # Gold color for stars
            ).pack(side=tk.LEFT)
            
            ttk.Label(
                stars_frame,
                text=f" ({average_rating}/5)",
                font=("Segoe UI", 12)
            ).pack(side=tk.LEFT)
        
        # Separator
        ttk.Separator(main_frame).pack(fill=tk.X, pady=10)
        
        # User rating section
        rating_frame = ttk.Frame(main_frame)
        rating_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(
            rating_frame,
            text="Your Rating:",
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=0, sticky=tk.W)
        
        # Rating variable
        current_rating = tk.IntVar(value=rating_info['rating'] if rating_info else 0)
        
        # Star buttons for rating
        stars_frame = ttk.Frame(rating_frame)
        stars_frame.grid(row=0, column=1, padx=(10, 0))
        
        def create_star_button(value):
            def on_click():
                current_rating.set(value)
                update_star_buttons()
            
            button = ttk.Button(
                stars_frame,
                text="☆",
                width=3,
                command=on_click
            )
            button.pack(side=tk.LEFT, padx=2)
            return button
        
        star_buttons = [create_star_button(i+1) for i in range(5)]
        
        def update_star_buttons():
            rating_value = current_rating.get()
            for i, button in enumerate(star_buttons):
                if i < rating_value:
                    button.configure(text="★")
                else:
                    button.configure(text="☆")
        
        # Initial update
        update_star_buttons()
        
        # Comment field
        comment_frame = ttk.Frame(main_frame)
        comment_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(
            comment_frame,
            text="Comment:",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor=tk.W)
        
        comment_text = tk.Text(comment_frame, height=5, width=50, wrap=tk.WORD)
        comment_text.pack(fill=tk.X, pady=(5, 0))
        
        # Set existing comment if available
        if rating_info and rating_info.get('comment'):
            comment_text.insert('1.0', rating_info['comment'])
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(15, 0))
        
        def submit_rating():
            rating_value = current_rating.get()
            if rating_value < 1:
                messagebox.showwarning("Invalid Rating", "Please select a rating (1-5 stars).")
                return
            
            comment = comment_text.get('1.0', tk.END).strip()
            
            # Submit the rating
            if self.submit_rating(script_path, script_name, rating_value, comment):
                messagebox.showinfo("Success", "Your rating has been submitted!")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to submit rating. Please try again.")
        
        submit_btn = ttk.Button(
            buttons_frame,
            text="Submit Rating",
            command=submit_rating
        )
        submit_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = ttk.Button(
            buttons_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
