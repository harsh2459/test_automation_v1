from fingerprint_manager import FingerprintManager
from core.browser_engine import BrowserEngine
import time
import random

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
        print(f"Using fingerprint: {fingerprint['session_id']}")
        
        # Navigate to the wallpaper site with proper parameters
        site_url = "http://localhost:5000"
        params = {
            "session_id": browser_engine.session_id,
            "fingerprint": fingerprint.get('session_id', 'unknown')
        }
        
        # Build URL with parameters
        from urllib.parse import urlencode
        url_with_params = f"{site_url}?{urlencode(params)}"
        
        print(f"Navigating to: {url_with_params}")
        page.goto(url_with_params)
        
        # Simulate human reading time
        reading_time = random.uniform(3, 8)
        print(f"Simulating reading time: {reading_time:.2f} seconds")
        time.sleep(reading_time)
        
        # Enhanced ad clicking simulation
        self._simulate_ad_interaction(page)
        
        # Enhanced wallpaper interaction
        self._simulate_wallpaper_interaction(page)
        
        # Take a screenshot
        screenshot_path = browser_engine.save_screenshot("wallpaper_visit", include_fingerprint=True)
        print(f"Screenshot saved: {screenshot_path}")
        
        print("Wallpaper site visit completed successfully")
        
    except Exception as e:
        print(f"Error during wallpaper site visit: {e}")
        
    finally:
        browser_engine.close()

def _simulate_ad_interaction(self, page):
    """Simulate ad interactions with higher success rate"""
    # Try to find and click ads with 50% probability
    if random.random() < 0.5:
        print("Looking for ads to click...")
        
        # Wait for ads to load
        page.wait_for_timeout(2000)
        
        # Try to find ad elements
        ad_selectors = [".ad", "[class*='ad']", "[id*='ad']", "button", "a"]
        
        for selector in ad_selectors:
            ads = page.query_selector_all(selector)
            if ads:
                # Click a random ad
                ad = random.choice(ads)
                try:
                    ad.click()
                    print("Clicked on an ad")
                    page.wait_for_timeout(random.randint(2000, 5000))
                    break
                except:
                    continue

def _simulate_wallpaper_interaction(self, page):
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
                
                break
            except:
                continue

def run_multiple_visits(num_visits=5, delay_between=30):
    """Run multiple visits to the wallpaper site"""
    for i in range(num_visits):
        print(f"Starting visit {i+1}/{num_visits}")
        wallpaper_site_visit()
        
        if i < num_visits - 1:
            wait_time = random.randint(delay_between // 2, delay_between * 2)
            print(f"Waiting {wait_time} seconds before next visit...")
            time.sleep(wait_time)