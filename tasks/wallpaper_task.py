from fingerprint_manager import FingerprintManager
from core.browser_engine import BrowserEngine
from human_behavior import AdvancedBehaviorSimulator
import time
import random
from urllib.parse import urlencode
from utils.session_manager import SessionManager
from utils.proxy_manager import AdvancedProxyManager
from datetime import datetime
from config import config
from utils.monitoring import monitor

def _simulate_ad_interaction(page, session_id, behavior_simulator):
    """Simulate ad interactions with multiple approaches"""
    interaction_methods = [
        _click_ad_via_api,
        _click_ad_via_element,
        _click_ad_via_javascript
    ]
    
    # Try different methods with weighted probability
    methods = random.choices(
        interaction_methods,
        weights=[0.4, 0.4, 0.2],
        k=random.randint(1, 3)
    )
    
    for method in methods:
        try:
            if method(page, session_id, behavior_simulator):
                return True
        except Exception as e:
            print(f"Ad interaction method failed: {e}")
            continue
    
    return False

def _click_ad_via_api(page, session_id, behavior_simulator):
    """Click ad via direct API call"""
    if random.random() < 0.6:
        ad_id = random.randint(1, 2)
        print(f"Directly calling ad click API for ad {ad_id}")
        
        # Make a direct API call to simulate ad click
        api_url = f"http://localhost:5000/ad-click?ad_id={ad_id}&session_id={session_id}"
        page.evaluate(f"""() => {{
            fetch('{api_url}', {{ method: 'GET' }})
                .then(response => response.json())
                .then(data => console.log('Ad click recorded via API:', data));
        }}""")
        
        page.wait_for_timeout(random.randint(1000, 3000))
        return True
    return False

def _click_ad_via_element(page, session_id, behavior_simulator):
    """Click ad by finding and interacting with elements"""
    if random.random() < 0.7:
        print("Looking for ad elements to click...")
        
        # Wait for page to load completely
        page.wait_for_timeout(2000)
        
        # Try different selectors with priority
        ad_selectors = [
            ".btn", "button", "a", "[class*='ad']", "[id*='ad']",
            "[class*='promo']", "[class*='offer']", "[class*='premium']"
        ]
        
        for selector in ad_selectors:
            ads = page.query_selector_all(selector)
            if ads:
                # Filter to only visible ads
                visible_ads = [ad for ad in ads if ad.is_visible()]
                if visible_ads:
                    ad = random.choice(visible_ads)
                    try:
                        print(f"Clicking ad element with selector: {selector}")
                        
                        # Use behavior simulator for human-like interaction
                        behavior_simulator.simulate_element_interaction(page, selector, "click")
                        
                        page.wait_for_timeout(random.randint(2000, 5000))
                        return True
                    except Exception as e:
                        print(f"Failed to click ad element: {e}")
                        continue
        return False

def _click_ad_via_javascript(page, session_id, behavior_simulator):
    """Click ad by executing JavaScript directly"""
    if random.random() < 0.3:
        try:
            ad_id = random.randint(1, 2)
            print(f"Executing trackAdClick function for ad {ad_id}")
            
            # Execute the trackAdClick function directly
            page.evaluate(f"trackAdClick({ad_id})")
            page.wait_for_timeout(2000)
            return True
        except:
            print("trackAdClick function not found or failed")
            return False
    return False

def _simulate_wallpaper_interaction(page, behavior_simulator):
    """Simulate interaction with wallpaper elements"""
    interaction_types = ["click", "hover", "scroll"]
    
    for _ in range(random.randint(1, 3)):
        try:
            # Try different selectors
            selectors = [".wallpaper-card", ".download-btn", "img", "[class*='image']"]
            
            for selector in selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    element = random.choice(elements)
                    if element.is_visible():
                        action = random.choice(interaction_types)
                        
                        if action == "click" and behavior_simulator.simulate_element_interaction(page, selector, "click"):
                            print(f"Clicked on {selector}")
                            return True
                        elif action == "hover":
                            element.hover()
                            page.wait_for_timeout(random.randint(500, 1500))
                            print(f"Hovered on {selector}")
                            return True
                        elif action == "scroll":
                            # Scroll to element
                            element.scroll_into_view_if_needed()
                            page.wait_for_timeout(random.randint(500, 1500))
                            print(f"Scrolled to {selector}")
                            return True
        except Exception as e:
            print(f"Wallpaper interaction failed: {e}")
            continue
    
    return False

def wallpaper_site_visit(use_proxy=True, session_id=None):
    print("Starting wallpaper site visit task...")
    monitor.start_timer("wallpaper_visit")
    
    # Initialize session manager
    session_manager = SessionManager()
    
    # Generate fingerprint
    fp_manager = FingerprintManager()
    fingerprint = fp_manager.get_comprehensive_fingerprint()
    user_agent = fingerprint["user_agent"]
    
    # Define site URL early to check if it's localhost
    site_url = "http://localhost:5000"
    
    # Initialize proxy manager if needed - but skip for localhost
    proxy_manager = None
    proxy = None
    
    # Don't use proxy for localhost connections
    if use_proxy and "localhost" not in site_url:
        try:
            proxy_manager = AdvancedProxyManager()
            # Use configured max proxies
            max_proxies = config.get("proxy.max_proxies", 100)
            proxy_manager.load_proxies(max_proxies=max_proxies)
            proxy = proxy_manager.get_proxy_for_session(session_id or fingerprint['session_id'])
            
            # If no valid proxy found, fall back to direct connection
            if not proxy or not proxy.get("server"):
                print("No valid proxies found, falling back to direct connection")
                proxy = None
                
        except Exception as e:
            print(f"Proxy setup failed: {e}, falling back to direct connection")
            proxy = None
    else:
        print("Localhost detected, disabling proxy usage")
    
    # Initialize browser engine
    browser_engine = BrowserEngine(
        headless=config.get("browser.headless", False),
        proxy=proxy,
        user_agent=user_agent,
        fingerprint=fingerprint,
        session_id=session_id or fingerprint['session_id'],  # Use provided session_id or generate new
        target_url=site_url  # Pass the target URL for localhost detection
    )
    
    # Initialize behavior simulator
    behavior_simulator = AdvancedBehaviorSimulator()
    behavior_pattern = behavior_simulator.get_random_pattern()
    print(f"Using behavior pattern: {behavior_pattern}")
    
    try:
        # Launch browser
        page = browser_engine.launch_browser()
        session_id = browser_engine.session_id
        print(f"Using session ID: {session_id}")
        print(f"Using fingerprint: {fingerprint['session_id']}")
        if proxy:
            print(f"Using proxy: {proxy.get('server', 'Unknown')}")
        else:
            print("Using direct connection (no proxy)")
        
        # Navigate to the wallpaper site with proper parameters
        params = {
            "session_id": session_id,
            "fingerprint": fingerprint.get('session_id', 'unknown')
        }
        
        # Build URL with parameters
        url_with_params = f"{site_url}?{urlencode(params)}"
        
        # Use the new natural browsing method
        behavior_simulator.simulate_natural_browsing(page, url_with_params, session_id)
        
        # Enhanced ad clicking simulation
        ad_clicked = _simulate_ad_interaction(page, session_id, behavior_simulator)
        if ad_clicked:
            print("Successfully simulated ad interaction")
        else:
            print("No ad interaction simulated")
        
        # Enhanced wallpaper interaction
        wallpaper_interacted = _simulate_wallpaper_interaction(page, behavior_simulator)
        if wallpaper_interacted:
            print("Successfully interacted with wallpaper content")
        
        # Take a screenshot
        screenshot_path = browser_engine.save_screenshot("wallpaper_visit", include_fingerprint=True)
        print(f"Screenshot saved: {screenshot_path}")
        
        # Save session data
        session_data = {
            "session_id": session_id,
            "fingerprint": fingerprint,
            "user_agent": user_agent,
            "proxy": proxy,
            "last_activity": datetime.now().isoformat(),
            "visit_count": 1  # Will be incremented on subsequent visits
        }
        session_manager.save_session_data(session_id, session_data)
        
        duration = monitor.end_timer("wallpaper_visit")
        monitor.log_event("wallpaper_visit_completed", {
            "session_id": session_id,
            "duration": duration,
            "ad_clicked": ad_clicked,
            "wallpaper_interacted": wallpaper_interacted,
            "screenshot_path": screenshot_path
        })
        
        print("Wallpaper site visit completed successfully")
        return session_id
        
    except Exception as e:
        duration = monitor.end_timer("wallpaper_visit")
        monitor.log_event("wallpaper_visit_failed", {
            "session_id": session_id,
            "duration": duration,
            "error": str(e)
        }, level="ERROR")
        print(f"Error during wallpaper site visit: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        browser_engine.close()

def run_multiple_visits(num_visits=5, delay_between=30, use_proxy=True):
    """Run multiple visits to the wallpaper site with session persistence"""
    session_manager = SessionManager()
    session_id = None
    
    for i in range(num_visits):
        print(f"Starting visit {i+1}/{num_visits}")
        start_time = time.time()
        
        # Load previous session data if exists
        session_data = {}
        if session_id:
            session_data = session_manager.load_session_data(session_id)
            if session_data:
                session_data["visit_count"] = session_data.get("visit_count", 0) + 1
                print(f"Resuming session {session_id}, visit count: {session_data['visit_count']}")
        
        # Run the visit
        session_id = wallpaper_site_visit(use_proxy=use_proxy, session_id=session_id)
        
        visit_duration = time.time() - start_time
        print(f"Visit completed in {visit_duration:.2f} seconds")
        
        if i < num_visits - 1:
            # Vary delay based on visit duration and random factor
            base_delay = max(delay_between, visit_duration * 1.5)
            wait_time = random.randint(int(base_delay * 0.7), int(base_delay * 1.3))
            print(f"Waiting {wait_time} seconds before next visit...")
            time.sleep(wait_time)
    
    # Save performance report after all visits
    monitor.save_report()