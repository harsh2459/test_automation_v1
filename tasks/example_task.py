import json
import glob
import os
from fingerprint_manager import FingerprintManager
from core.browser_engine import BrowserEngine
import time
import random

def example_navigation():
    print("Starting example navigation task...")
    
    # Get a random user agent
    user_agent = FingerprintManager.get_random_user_agent()
    
    # Initialize browser engine with no proxy
    browser_engine = BrowserEngine(
        headless=True,
        proxy=None,  # Explicitly set to None
        user_agent=user_agent
    )
    
    try:
        # Launch browser
        page = browser_engine.launch_browser()
        
        # Navigate to a simple site
        page.goto("https://httpbin.org/user-agent")
        
        # Get the displayed user agent
        content = page.text_content("pre")
        print(f"Displayed User Agent: {content}")
        
        # Take a screenshot
        screenshot_path = browser_engine.save_screenshot("example_task")
        print(f"Task completed. Screenshot saved at {screenshot_path}")
        
    except Exception as e:
        print(f"Error during task: {e}")
        # Save screenshot on error too
        if browser_engine.page:
            browser_engine.save_screenshot("error")
        
    finally:
        browser_engine.close()

def manage_screenshots(action="list", filter_session=None):
    """Manage screenshot files and metadata"""
    if not os.path.exists("screenshots"):
        print("No screenshots directory found")
        return
    
    if action == "list":
        json_files = glob.glob("screenshots/*.json")
        if not json_files:
            print("No screenshot metadata found")
            return
            
        print("Available screenshots with metadata:")
        for json_file in json_files:
            with open(json_file, 'r') as f:
                metadata = json.load(f)
                session_id = metadata.get('session_id', 'unknown')
                timestamp = metadata.get('timestamp', 'unknown')
                filename = metadata.get('filename', 'unknown')
                
                if filter_session and filter_session != session_id:
                    continue
                    
                print(f"Session: {session_id} | Time: {timestamp} | File: {filename}")
    
    elif action == "clean":
        # Remove files based on session ID or all
        if filter_session:
            pattern = f"screenshots/*{filter_session}*"
        else:
            pattern = "screenshots/*"
            
        files_to_remove = glob.glob(pattern)
        for file_path in files_to_remove:
            os.remove(file_path)
            print(f"Removed: {file_path}")
            
        print(f"Removed {len(files_to_remove)} files")