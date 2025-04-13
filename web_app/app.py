#!/usr/bin/env python3
"""
WinPick Web App - Flask-based web interface for WinPick
"""

import os
import sys
import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import web app controllers
from web_app.controllers.category_controller import CategoryController
from web_app.controllers.script_controller import ScriptController
from web_app.controllers.github_controller import GitHubController

# Import original utility functions
from web_app.controllers.github_auth_web import GitHubAuthHandlerWeb
from web_app.controllers.rating_system_web import RatingSystemWeb
from src.utils.script_metadata import parse_script_metadata
from src.utils.message_handler import MessageHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        # Only log errors and warnings to console
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set Werkzeug logger to only show warnings
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Initialize Flask app
app = Flask(__name__, 
          static_folder='static',
          template_folder='templates')
app.secret_key = os.urandom(24)  # For flash messages and session

# Setup base directory for scripts
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    scripts_dir = os.path.join(base_dir, "WindowsScripts")
    os.makedirs(scripts_dir, exist_ok=True)
    logger.info(f"Using scripts directory: {scripts_dir}")
except Exception as e:
    logger.error(f"Error setting up base directory: {str(e)}")
    scripts_dir = os.path.join(os.path.expanduser("~"), "WindowsScripts")
    os.makedirs(scripts_dir, exist_ok=True)

# Define script categories
CATEGORIES = [
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

# Initialize controllers
category_controller = CategoryController()
script_controller = ScriptController()
github_auth = GitHubAuthHandlerWeb()
rating_system = RatingSystemWeb(github_auth)  # Use web-friendly rating system
github_controller = GitHubController(None, scripts_dir)

# Initialize categories on startup
category_controller.check_and_create_directories(scripts_dir, CATEGORIES)

# Custom console output capture for web display
console_output = []

def capture_output(message):
    """Capture console output for web display"""
    # Add timestamp to message
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    console_output.append(f"[{timestamp}] {message}")
    while len(console_output) > 500:  # Limit buffer size but keep a larger history
        console_output.pop(0)
    # Only log important messages to Python console
    if "ERROR" in message or "WARNING" in message:
        logger.info(message)

# Override MessageHandler's methods to use web flash messages
MessageHandler.info = lambda msg, title=None, console_only=True: (capture_output(f"INFO: {msg}"), flash(msg, "info") if not console_only else None)
MessageHandler.error = lambda msg, title=None, console_only=True: (capture_output(f"ERROR: {msg}"), flash(msg, "error") if not console_only else None)
MessageHandler.warning = lambda msg, title=None, console_only=True: (capture_output(f"WARNING: {msg}"), flash(msg, "warning") if not console_only else None)

@app.route('/')
def index():
    """Main page"""
    # Get categories and create if needed
    category_dirs = category_controller.check_and_create_directories(scripts_dir, CATEGORIES)
    custom_categories = category_controller.detect_custom_categories(scripts_dir, CATEGORIES)
    
    # Default to first category if none selected
    selected_category = request.args.get('category', CATEGORIES[0] if CATEGORIES else None)
    
    # Get scripts for selected category
    scripts = []
    if selected_category:
        category_path = os.path.join(scripts_dir, selected_category)
        os.makedirs(category_path, exist_ok=True)
        scripts = script_controller.get_scripts_for_web(category_path, rating_system)
    
    # Get GitHub authentication status
    github_status = {
        'authenticated': github_auth.is_authenticated(),
        'username': github_auth.get_username() if github_auth.is_authenticated() else None
    }
    
    return render_template('index.html', 
                         categories=CATEGORIES + custom_categories,
                         selected_category=selected_category,
                         scripts=scripts,
                         console_output=console_output,
                         github_status=github_status,
                         now=datetime.datetime.now())

@app.route('/script/<category>/<filename>')
def view_script(category, filename):
    """View script details"""
    category_path = os.path.join(scripts_dir, category)
    script_path = os.path.join(category_path, filename)
    
    if not os.path.exists(script_path):
        flash("Script not found.", "error")
        return redirect(url_for('index'))
    
    # Get script content and metadata
    script_content = ""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
    except Exception as e:
        logger.error(f"Failed to read script: {str(e)}")
        script_content = f"Error reading script: {str(e)}"
    
    friendly_name, description, undoable, undo_desc, developer, link = parse_script_metadata(script_path)
    
    # Get rating if available
    rating = None
    if rating_system:
        rating = rating_system.get_average_rating(script_path, friendly_name)
    
    script_info = {
        'name': friendly_name,
        'filename': filename,
        'path': script_path,
        'content': script_content,
        'type': os.path.splitext(filename)[1],
        'description': description,
        'developer': developer,
        'link': link,
        'undoable': undoable,
        'undo_desc': undo_desc,
        'rating': rating
    }
    
    # Get GitHub authentication status
    github_status = {
        'authenticated': github_auth.is_authenticated(),
        'username': github_auth.get_username() if github_auth.is_authenticated() else None
    }
    
    return render_template('script_detail.html', 
                         script=script_info,
                         category=category,
                         categories=CATEGORIES,
                         github_status=github_status,
                         now=datetime.datetime.now())

@app.route('/run_script', methods=['POST'])
def run_script():
    """Run a script"""
    script_path = request.form.get('script_path')
    undo = request.form.get('undo') == 'true'
    
    if not script_path or not os.path.exists(script_path):
        return jsonify({'success': False, 'message': 'Script not found'})
    
    result = script_controller.run_script_web(script_path, undo=undo, output_callback=capture_output)
    
    return jsonify({
        'success': result['success'],
        'message': result['message'],
        'console_output': console_output[-10:]  # Last 10 lines
    })

@app.route('/create_script', methods=['GET', 'POST'])
def create_script():
    """Create new script form/handler"""
    if request.method == 'POST':
        category = request.form.get('category')
        script_name = request.form.get('name')
        script_type = request.form.get('type')
        developer = request.form.get('developer')
        link = request.form.get('link')
        description = request.form.get('description')
        undoable = request.form.get('undoable') == 'true'
        undo_desc = request.form.get('undo_desc', '')
        content = request.form.get('content')
        
        if not script_name or not category or not script_type:
            flash("Missing required fields.", "error")
            return redirect(url_for('create_script'))
        
        category_path = os.path.join(scripts_dir, category)
        os.makedirs(category_path, exist_ok=True)
        
        file_name = f"{script_name}{script_type}" if not script_name.endswith(script_type) else script_name
        script_path = os.path.join(category_path, file_name)
        
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created new script: {file_name} in {category}")
            flash(f"Script '{script_name}' created successfully!", "success")
            return redirect(url_for('index', category=category))
        except Exception as e:
            error_msg = f"Failed to create script: {str(e)}"
            logger.error(error_msg)
            flash(error_msg, "error")
            return redirect(url_for('create_script'))
    
    # GET request - display form
    categories = CATEGORIES + category_controller.detect_custom_categories(scripts_dir, CATEGORIES)
    selected_category = request.args.get('category', categories[0] if categories else None)
    
    # Get GitHub authentication status
    github_status = {
        'authenticated': github_auth.is_authenticated(),
        'username': github_auth.get_username() if github_auth.is_authenticated() else None
    }
    
    return render_template('create_script.html', 
                         categories=categories,
                         selected_category=selected_category,
                         github_status=github_status,
                         now=datetime.datetime.now())

@app.route('/github_auth', methods=['GET'])
def github_auth_handler():
    """Handle GitHub authentication"""
    if github_auth.is_authenticated():
        # Log out
        if github_auth.logout():
            flash("Successfully logged out from GitHub.", "success")
        else:
            flash("Failed to log out from GitHub.", "error")
    else:
        # Log in
        if github_auth.authenticate():
            username = github_auth.get_username()
            if username:
                flash(f"Successfully logged in as {username}.", "success")
            else:
                flash("Authentication in progress. Please check browser for GitHub login.", "info")
        else:
            flash("Failed to authenticate with GitHub.", "error")
    
    return redirect(url_for('index'))

@app.route('/rate_script', methods=['POST'])
def rate_script():
    """Rate a script"""
    if not github_auth.is_authenticated():
        return jsonify({'success': False, 'message': 'You must be logged in to GitHub to rate scripts'})
    
    script_path = request.form.get('script_path')
    script_name = request.form.get('script_name')
    rating_value = request.form.get('rating')
    
    try:
        rating_value = float(rating_value)
        if rating_value < 1 or rating_value > 5:
            raise ValueError("Rating must be between 1 and 5")
            
        success = rating_system.submit_rating(script_path, script_name, rating_value)
        
        if success:
            new_avg = rating_system.get_average_rating(script_path, script_name)
            return jsonify({
                'success': True, 
                'message': 'Rating submitted successfully!',
                'new_rating': new_avg
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to submit rating'})
    except Exception as e:
        logger.error(f"Error submitting rating: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/github_download', methods=['GET', 'POST'])
def github_download():
    """GitHub script download page/handler"""
    if request.method == 'POST':
        repo_url = request.form.get('repo_url')
        branch = request.form.get('branch', 'main')
        
        if not repo_url:
            flash("Repository URL is required.", "error")
            return redirect(url_for('github_download'))
        
        # Log only the URL to Python console, not all output
        print(f"Downloading from {repo_url}, branch: {branch}")
        
        # Ensure scripts_dir exists
        os.makedirs(scripts_dir, exist_ok=True)
        
        # Download scripts to the main scripts directory
        result = github_controller.download_scripts_from_repo_web(
            repo_url, 
            scripts_dir,  # Download directly to main scripts directory
            branch=branch,
            output_callback=capture_output,
            preserve_structure=True  # Preserve the repository folder structure
        )
        
        if result['success']:
            flash(f"Successfully downloaded scripts from {repo_url}!", "success")
        else:
            flash(f"Failed to download scripts: {result['message']}", "error")
            
        return redirect(url_for('index'))
    
    # GET request - display form
    categories = CATEGORIES + category_controller.detect_custom_categories(scripts_dir, CATEGORIES)
    
    # Get GitHub authentication status
    github_status = {
        'authenticated': github_auth.is_authenticated(),
        'username': github_auth.get_username() if github_auth.is_authenticated() else None
    }
    
    return render_template('github_download.html', 
                         categories=categories, 
                         github_status=github_status,
                         now=datetime.datetime.now())

@app.route('/console_output', methods=['GET'])
def get_console_output():
    """AJAX endpoint to get console output"""
    return jsonify({
        'output': console_output
    })

@app.route('/clear_console', methods=['POST'])
def clear_console():
    """Clear the console output"""
    global console_output
    console_output = []
    capture_output("Console cleared.")
    return jsonify({'success': True})

@app.route('/activity_log')
def activity_log():
    """View activity log page"""
    # Get GitHub authentication status
    github_status = {
        'authenticated': github_auth.is_authenticated(),
        'username': github_auth.get_username() if github_auth.is_authenticated() else None
    }
    
    return render_template('activity_log.html', 
                         console_output=console_output,
                         github_status=github_status,
                         now=datetime.datetime.now())

if __name__ == '__main__':
    # Run web server
    app.run(debug=True, host='127.0.0.1', port=5000)