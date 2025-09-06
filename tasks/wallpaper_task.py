from fingerprint_manager import FingerprintManager
from core.browser_engine import BrowserEngine
import time
import random
from urllib.parse import urlencode

def _simulate_ad_interaction(page, session_id):
    """Simulate ad interactions with direct API calls to ensure tracking"""
    # Try to find and click ads with 60% probability
    if random.random() < 0.6:
        print("Looking for ads to interact with...")
        
        # Wait for ads to load
        page.wait_for_timeout(2000)
        
        # Try different approaches to ensure ad clicks are tracked
        
        # 1. First try: Directly call the website's ad click API
        try:
            ad_id = random.randint(1, 2)
            print(f"Directly calling ad click API for ad {ad_id}")
            
            # Make a direct API call to simulate ad click
            api_url = f"http://localhost:5000/ad-click?ad_id={ad_id}&session_id={session_id}"
            page.evaluate(f"""() => {{
                fetch('{api_url}')
                    .then(response => response.json())
                    .then(data => console.log('Ad click recorded:', data));
            }}""")
            
            page.wait_for_timeout(1000)
            return True
        except Exception as e:
            print(f"Direct API call failed: {e}")
        
        # 2. Second try: Find and click actual ad elements
        try:
            ad_selectors = [".ad", "[class*='ad']", "[id*='ad']", "button", "a"]
            
            for selector in ad_selectors:
                ads = page.query_selector_all(selector)
                if ads:
                    # Click a random ad
                    ad = random.choice(ads)
                    try:
                        print(f"Clicking ad element with selector: {selector}")
                        ad.click()
                        page.wait_for_timeout(random.randint(2000, 5000))
                        return True
                    except:
                        continue
        except Exception as e:
            print(f"Element clicking failed: {e}")
        
        # 3. Third try: Execute the trackAdClick function directly
        try:
            ad_id = random.randint(1, 2)
            print(f"Executing trackAdClick function for ad {ad_id}")
            page.evaluate(f"trackAdClick({ad_id})")
            page.wait_for_timeout(2000)
            return True
        except:
            print("trackAdClick function not found or failed")
    
    return False

def _simulate_wallpaper_interaction(page):
    """Simulate interaction with wallpaper elements"""
    # Try to interact with wallpapers
    wallpaper_selectors = [".wallpaper", "img", "[class*='image']", "[class*='wall']"]
    
    for selector in wallpaper_selectors:
        wallpapers = page.query_selector_all(selector)
        if wallpapers:
            # Interact with a random wallpaper
            wallpaper = random.choice(wallpapers)
            try:
                # Hover over the wallpaper
                wallpaper.hover()
                page.wait_for_timeout(1000)
                
                # Maybe click on it (33% chance)
                if random.random() < 0.33:
                    wallpaper.click()
                    print("Interacted with a wallpaper")
                    page.wait_for_timeout(2000)
                
                return True
            except:
                continue
    
    return False

def wallpaper_site_visit():
    print("Starting wallpaper site visit task...")
    
    # Generate fingerprint
    fp_manager = FingerprintManager()
    fingerprint = fp_manager.get_comprehensive_fingerprint()
    user_agent = fingerprint["user_agent"]
    
    # Initialize browser engine
    browser_engine = BrowserEngine(
        headless=False,
        user_agent=user_agent,
        fingerprint=fingerprint
    )
    
    try:
        # Launch browser
        page = browser_engine.launch_browser()
        session_id = browser_engine.session_id
        print(f"Using session ID: {session_id}")
        print(f"Using fingerprint: {fingerprint['session_id']}")
        
        # Navigate to the wallpaper site with proper parameters
        site_url = "http://localhost:5000"
        params = {
            "session_id": session_id,
            "fingerprint": fingerprint.get('session_id', 'unknown')
        }
        
        # Build URL with parameters
        url_with_params = f"{site_url}?{urlencode(params)}"
        
        print(f"Navigating to: {url_with_params}")
        page.goto(url_with_params)
        
        # Simulate human reading time
        reading_time = random.uniform(3, 8)
        print(f"Simulating reading time: {reading_time:.2f} seconds")
        time.sleep(reading_time)
        
        # Enhanced ad clicking simulation
        ad_clicked = _simulate_ad_interaction(page, session_id)
        if ad_clicked:
            print("Successfully simulated ad interaction")
        else:
            print("No ad interaction simulated")
        
        # Enhanced wallpaper interaction
        _simulate_wallpaper_interaction(page)
        
        # Take a screenshot
        screenshot_path = browser_engine.save_screenshot("wallpaper_visit", include_fingerprint=True)
        print(f"Screenshot saved: {screenshot_path}")
        
        print("Wallpaper site visit completed successfully")
        
    except Exception as e:
        print(f"Error during wallpaper site visit: {e}")
        
    finally:
        browser_engine.close()

def run_multiple_visits(num_visits=5, delay_between=30):
    """Run multiple visits to the wallpaper site"""
    for i in range(num_visits):
        print(f"Starting visit {i+1}/{num_visits}")
        wallpaper_site_visit()
        
        if i < num_visits - 1:
            wait_time = random.randint(delay_between // 2, delay_between * 2)
            print(f"Waiting {wait_time} seconds before next visit...")
            time.sleep(wait_time)