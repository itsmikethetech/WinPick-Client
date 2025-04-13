#!/usr/bin/env python3
"""
WinPick Web App Runner
Starts the Flask web server for the WinPick Web App
"""

import os
import sys
import webbrowser
import time
from threading import Timer

def open_browser():
    """Open web browser after short delay"""
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    print("Starting WinPick Web App...")
    print("="*50)
    print("WinPick Web Interface is running at: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    print("="*50)
    
    # Add web_app directory to Python path
    web_app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web_app')
    if web_app_dir not in sys.path:
        sys.path.append(web_app_dir)
    
    # Start browser opener timer
    Timer(1, open_browser).start()
    
    # Import and run Flask app
    from web_app.app import app
    
    # Disable Flask's default logging output
    import logging
    log = logging.getLogger('werkzeug')
    log.disabled = True
    
    app.run(debug=False, host='127.0.0.1', port=5000)