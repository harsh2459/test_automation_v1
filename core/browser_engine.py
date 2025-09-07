from playwright.sync_api import sync_playwright
import random
import time
import os
import json
import hashlib
from datetime import datetime
import re
from utils.session_manager import SessionManager
from utils.monitoring import monitor
from config import config

try:
    from playwright_stealth import stealth_sync
    HAVE_STEALTH = True
except ImportError:
    HAVE_STEALTH = False

def retry_on_failure(max_retries=3, delay=1, backoff=2, exceptions=(Exception,)):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries, current_delay = max_retries, delay
            while retries > 0:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries -= 1
                    if retries == 0:
                        print(f"Function {func.__name__} failed after {max_retries} attempts: {e}")
                        raise
                    print(f"Function {func.__name__} failed: {e}. Retrying in {current_delay} seconds...")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator

class BrowserEngine:
    def __init__(self, headless=None, proxy=None, user_agent=None, fingerprint=None, session_id=None, target_url=None):
        self.headless = headless if headless is not None else config.get("browser.headless", False)
        self.proxy = proxy
        self.user_agent = user_agent or self.get_random_user_agent()
        self.fingerprint = fingerprint or {}
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.session_id = session_id or hashlib.md5(str(time.time()).encode()).hexdigest()[:12]
        self.proxy_manager = None
        self.geolocation = self._generate_geolocation()
        self.session_manager = SessionManager()
        self.target_url = target_url

    def _generate_geolocation(self):
        """Generate realistic geolocation data"""
        cities = {
            "US": [
                {"city": "New York", "lat": 40.7128, "lon": -74.0060, "timezone": "America/New_York"},
                {"city": "Los Angeles", "lat": 34.0522, "lon": -118.2437, "timezone": "America/Los_Angeles"},
                {"city": "Chicago", "lat": 41.8781, "lon": -87.6298, "timezone": "America/Chicago"}
            ],
            "UK": [
                {"city": "London", "lat": 51.5074, "lon": -0.1278, "timezone": "Europe/London"}
            ],
            "DE": [
                {"city": "Berlin", "lat": 52.5200, "lon": 13.4050, "timezone": "Europe/Berlin"}
            ]
        }
        
        country = random.choice(list(cities.keys()))
        location = random.choice(cities[country])
        
        return {
            "latitude": location["lat"],
            "longitude": location["lon"],
            "accuracy": random.uniform(10, 100),
            "country": country,
            "city": location["city"],
            "timezone": location["timezone"]
        }
    
    def get_random_user_agent(self):
        """Get a user agent from config or use default list"""
        user_agents = config.get("browser.user_agents", [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62",
        ])
        return random.choice(user_agents)
    
    @retry_on_failure(max_retries=3, delay=2, backoff=2)
    def launch_browser(self, retry_count=3):
        """Launch browser with advanced stealth and proxy rotation"""
        # Check if we're in an async environment (moved outside the loop)
        try:
          import asyncio
         if asyncio.get_event_loop().is_running():
              print("Warning: Running in async environment, this may cause issues with sync Playwright")
     except:
         pass
    
     for attempt in range(retry_count):
            try:
                # Check if we're accessing localhost and disable proxy if so
                if self.target_url and any(domain in self.target_url for domain in ['localhost', '127.0.0.1']):
                     print("Localhost detected, disabling proxy usage")
                    self.proxy = None
            
              # Rotate proxy if we have a proxy manager
            if self.proxy_manager and not self.proxy:
                self.proxy = self.proxy_manager.get_proxy_for_session(self.session_id)
                if not self.proxy:
                    print("No proxies available, proceeding without proxy")
            
            self.playwright = sync_playwright().start()
            
            # Extract browser version from user agent for more realistic args
            chrome_version = self._extract_chrome_version(self.user_agent)
            
            launch_options = {
                "headless": self.headless,
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    f"--user-agent={self.user_agent}",
                    f"--lang={self._get_language_from_ua()}",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--disable-notifications",
                    "--disable-popup-blocking",
                    "--metrics-recording-only",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-default-apps",
                    "--disable-translate",
                    f"--window-size={random.randint(1200, 1920)},{random.randint(800, 1080)}",
                ]
            }
            
            if self.proxy and self.proxy.get("server"):
                launch_options["proxy"] = self.proxy
            
            self.browser = self.playwright.chromium.launch(**launch_options)
            
            # Set up context with randomized settings
            context_options = {
                "viewport": {
                    "width": config.get("browser.viewport_width", random.randint(1000, 1920)),
                    "height": config.get("browser.viewport_height", random.randint(600, 1080))
                },
                "user_agent": self.user_agent,
                "locale": self._get_language_from_ua(),
                "timezone_id": self.geolocation["timezone"],
                "geolocation": {
                    "latitude": self.geolocation["latitude"],
                    "longitude": self.geolocation["longitude"],
                    "accuracy": self.geolocation["accuracy"]
                },
                "permissions": ["geolocation"]
            }
            
            storage_state_path = self.session_manager.get_storage_state_path(self.session_id)
            if os.path.exists(storage_state_path):
                context_options["storage_state"] = storage_state_path
            
            # Set HTTP headers for more realism
            context_options["extra_http_headers"] = self._generate_http_headers()
            
            self.context = self.browser.new_context(**context_options)
            self.page = self.context.new_page()
            
            # Apply advanced stealth if available
            if HAVE_STEALTH:
                stealth_sync(self.page)
            else:
                self._apply_advanced_stealth()
            
            # Apply fingerprint overrides
            self._apply_fingerprint_overrides()
            
            # Simulate network conditions (updated to avoid deprecated method)
            self._simulate_network_conditions()
            
            print(f"Browser launched successfully with session ID: {self.session_id}")
            if self.proxy:
                print(f"Using proxy: {self.proxy.get('server', 'Unknown')}")
            
            # Log the browser launch
            monitor.log_event("browser_launched", {
                "session_id": self.session_id,
                "user_agent": self.user_agent,
                "proxy": self.proxy,
                "geolocation": self.geolocation
            })
            
            return self.page
            
        except Exception as e:
            print(f"Error launching browser (attempt {attempt + 1}/{retry_count}): {e}")
            
            # Update proxy performance if we have a proxy manager
            if self.proxy_manager and self.proxy:
                self.proxy_manager.update_proxy_performance(self.proxy, success=False)
            
            # Make sure close method exists before calling it
            if hasattr(self, 'close'):
                self.close()
            else:
                # Basic cleanup if close method doesn't exist yet
                try:
                    if hasattr(self, 'context') and self.context:
                        self.context.close()
                    if hasattr(self, 'browser') and self.browser:
                        self.browser.close()
                    if hasattr(self, 'playwright') and self.playwright:
                        self.playwright.stop()
                except Exception as cleanup_error:
                    print(f"Cleanup error: {cleanup_error}")
            
            # Wait before retry with exponential backoff
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"Waiting {wait_time:.2f} seconds before retry...")
            time.sleep(wait_time)
    else:
        raise Exception(f"Failed to launch browser after {retry_count} attempts")  
    
    def _extract_chrome_version(self, user_agent):
        """Extract Chrome version from user agent"""
        match = re.search(r'Chrome/(\d+\.\d+\.\d+\.\d+)', user_agent)
        return match.group(1) if match else None
    
    def _get_language_from_ua(self):
        """Extract language from user agent or use fingerprint"""
        if self.fingerprint.get('language'):
            return self.fingerprint['language']
        
        # Default to English variants based on common user agents
        languages = ["en-US", "en-GB", "en-CA", "en-AU"]
        return random.choice(languages)
    
    def _generate_http_headers(self):
        """Generate realistic HTTP headers"""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': f'{self._get_language_from_ua()},en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': str(random.randint(0, 1)),
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Randomly add Sec-Fetch headers (not all browsers have them)
        if random.random() < 0.7:
            headers.update({
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            })
        
        return headers
    
    def _apply_advanced_stealth(self):
        """Apply advanced stealth techniques to avoid detection"""
        # Get stealth configuration
        webgl_vendor = config.get("stealth.webgl_vendor", "Google Inc.")
        webgl_renderer = config.get("stealth.webgl_renderer", "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)")
        hardware_concurrency = config.get("stealth.hardware_concurrency", 8)
        device_memory = config.get("stealth.device_memory", 8)
        
        stealth_script = f"""
        // Override navigator properties
        Object.defineProperty(navigator, 'webdriver', {{
            get: () => false,
        }});
        
        // Override plugins with more realistic data
        Object.defineProperty(navigator, 'plugins', {{
            get: () => {json.dumps(self._generate_plugins_list())},
        }});
        
        // Override hardware properties
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {hardware_concurrency},
        }});
        
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {device_memory},
        }});
        
        // Mock WebGL properties
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{
                return '{webgl_vendor}';
            }}
            if (parameter === 37446) {{
                return '{webgl_renderer}';
            }}
            return getParameter.call(this, parameter);
        }};
        
        // Mock performance metrics
        const originalGetEntries = performance.getEntriesByType;
        performance.getEntriesByType = function(type) {{
            if (type === 'navigation') {{
                const navEntries = originalGetEntries.call(this, type);
                if (navEntries.length > 0) {{
                    // Add some randomness to timing metrics
                    navEntries[0].domContentLoadedEventEnd += Math.random() * 100;
                    navEntries[0].loadEventEnd += Math.random() * 200;
                }}
                return navEntries;
            }}
            return originalGetEntries.call(this, type);
        }};
        
        // Mock timezone
        Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {{
            get: () => function() {{
                const options = Reflect.apply(Intl.DateTimeFormat.prototype.resolvedOptions, this, arguments);
                options.timeZone = '{self.fingerprint.get('timezone', 'America/New_York')}';
                return options;
            }}
        }});
        
        // Mock media devices with more variability
        Object.defineProperty(navigator, 'mediaDevices', {{
            get: () => ({{
                enumerateDevices: () => Promise.resolve({json.dumps(self._generate_media_devices())}),
                getUserMedia: () => Promise.resolve({{}}),
            }}),
        }});
        """
        
        self.page.add_init_script(stealth_script)
    
    def _generate_plugins_list(self):
        """Generate a realistic plugins list based on browser fingerprint"""
        plugins = [
            {"name": "Chrome PDF Plugin", "filename": "internal-pdf-viewer", "description": "Portable Document Format"},
            {"name": "Chrome PDF Viewer", "filename": "mhjfbmdgcfjbbpaeojofohoefgiehjai", "description": ""},
            {"name": "Native Client", "filename": "internal-nacl-plugin", "description": ""},
        ]
        
        # Add some randomness
        if random.random() < 0.3:
            plugins.append({
                "name": "Widevine Content Decryption Module",
                "filename": "widevinecdmadapter.plugin",
                "description": "Widevine Content Decryption Module"
            })
        
        return plugins
    
    def _generate_media_devices(self):
        """Generate realistic media devices"""
        devices = [
            {"kind": "audioinput", "deviceId": "default", "label": "", "groupId": "default-group"},
            {"kind": "videoinput", "deviceId": "default", "label": "", "groupId": "default-group"},
        ]
        
        # Sometimes add additional devices
        if random.random() < 0.4:
            devices.append({
                "kind": "audiooutput", 
                "deviceId": "default", 
                "label": "", 
                "groupId": "default-group"
            })
        
        return devices
    
    def _apply_fingerprint_overrides(self):
        """Apply JavaScript overrides to mask automation and spoof fingerprint"""
        if not self.fingerprint:
            return
            
        fingerprint_script = f"""
        // Override navigator properties
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {self.fingerprint.get('hardwareConcurrency', random.randint(4, 16))}
        }});
        
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {self.fingerprint.get('deviceMemory', random.choice([4, 8, 16]))}
        }});
        
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{self.fingerprint.get('platform', random.choice(["Win32", "MacIntel", "Linux x86_64"]))}'
        }});
        
        // Screen properties
        Object.defineProperty(screen, 'width', {{
            get: () => {self.fingerprint.get('screenWidth', random.randint(1200, 1920))}
        }});
        
        Object.defineProperty(screen, 'height', {{
            get: () => {self.fingerprint.get('screenHeight', random.randint(800, 1080))}
        }});
        
        Object.defineProperty(screen, 'colorDepth', {{
            get: () => {self.fingerprint.get('colorDepth', random.choice([24, 30, 32]))}
        }});
        
        Object.defineProperty(screen, 'pixelDepth', {{
            get: () => {self.fingerprint.get('pixelDepth', random.choice([24, 30, 32]))}
        }});
        
        // Timezone
        Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {{
            get: () => function() {{
                const options = Reflect.apply(Intl.DateTimeFormat.prototype.resolvedOptions, this, arguments);
                options.timeZone = '{self.fingerprint.get('timezone', 'America/New_York')}';
                return options;
            }}
        }});
        """
        
        self.page.add_init_script(fingerprint_script)
    
def _simulate_network_conditions(self):
    """Network condition simulation - placeholder for future implementation"""
    # This method is temporarily empty since emulate_network_conditions was deprecated
    if not self.headless:
        print("Network simulation would run here (API changed in Playwright)")
    pass

def close(self):
    """Properly close browser and cleanup resources"""
    try:
        if hasattr(self, 'context') and self.context:
            # Save session state before closing
            try:
                storage_state_path = self.session_manager.get_storage_state_path(self.session_id)
                self.context.storage_state(path=storage_state_path)
            except Exception as e:
                print(f"Error saving storage state: {e}")
            self.context.close()
        if hasattr(self, 'browser') and self.browser:
            self.browser.close()
        if hasattr(self, 'playwright') and self.playwright:
            self.playwright.stop()
    except Exception as e:
        print(f"Error during browser cleanup: {e}")
    finally:
        # Ensure we clear references
        self.context = None
        self.browser = None
        self.playwright = None
    
    def _randomize_geolocation(self):
        """Randomize geolocation for each session"""
        # Override the initial geolocation with more randomness
        self.geolocation = {
            "latitude": random.uniform(-90, 90),
            "longitude": random.uniform(-180, 180),
            "accuracy": random.uniform(10, 5000),  # Wider accuracy range
            "country": random.choice(["US", "UK", "DE", "FR", "CA", "AU", "JP"]),
            "city": random.choice(["New York", "London", "Berlin", "Paris", "Toronto", "Sydney", "Tokyo"]),
            "timezone": random.choice([
                "America/New_York", "Europe/London", "Europe/Berlin", 
                "Europe/Paris", "America/Toronto", "Australia/Sydney", "Asia/Tokyo"
            ])
        }
    
    def save_screenshot(self, name="screenshot", include_fingerprint=True):
        """Save screenshot with optional fingerprint metadata"""
        if not self.page:
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("screenshots", exist_ok=True)
        
        filename = f"screenshots/{name}_{self.session_id}_{timestamp}.png"
        self.page.screenshot(path=filename)
        
        # Save fingerprint metadata if requested
        if include_fingerprint:
            metadata = {
                "timestamp": timestamp,
                "session_id": self.session_id,
                "user_agent": self.user_agent,
                "fingerprint": self.fingerprint,
                "proxy": self.proxy,
                "filename": filename
            }
            
            metadata_path = f"screenshots/{name}_{self.session_id}_{timestamp}.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        return filename
    
def close(self):
    """Properly close browser and cleanup resources"""
    try:
        if hasattr(self, 'context') and self.context:
            # Save session state before closing
            try:
                storage_state_path = self.session_manager.get_storage_state_path(self.session_id)
                self.context.storage_state(path=storage_state_path)
            except Exception as e:
                print(f"Error saving storage state: {e}")
            self.context.close()
        if hasattr(self, 'browser') and self.browser:
            self.browser.close()
        if hasattr(self, 'playwright') and self.playwright:
            self.playwright.stop()
    except Exception as e:
        print(f"Error during browser cleanup: {e}")
    finally:
        # Ensure we clear references
        self.context = None
        self.browser = None
        self.playwright = None
    
    def simulate_human_behavior(self, page=None):
        """Simulate human-like behavior on the page"""
        target_page = page or self.page
        if not target_page:
            return
            
        # Random mouse movements
        for _ in range(random.randint(3, 8)):
            x = random.randint(0, target_page.viewport_size["width"])
            y = random.randint(0, target_page.viewport_size["height"])
            target_page.mouse.move(x, y)
            time.sleep(random.uniform(0.1, 0.7))
        
        # Random scrolling
        scroll_actions = random.randint(2, 6)
        for _ in range(scroll_actions):
            scroll_direction = random.choice([-1, 1])
            scroll_amount = random.randint(200, 800) * scroll_direction
            target_page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            time.sleep(random.uniform(0.5, 2.0))
            
            # Occasionally scroll back a bit (human-like behavior)
            if random.random() < 0.3:
                target_page.evaluate(f"window.scrollBy(0, {-scroll_amount//3})")
                time.sleep(random.uniform(0.2, 0.8))
        
        # Random keyboard actions
        if random.random() < 0.5:
            key_actions = random.randint(1, 4)
            for _ in range(key_actions):
                key = random.choice(["PageDown", "PageUp", "ArrowDown", "ArrowUp"])
                target_page.keyboard.press(key)
                time.sleep(random.uniform(0.3, 1.2))
                
def _simulate_hardware_level_behavior(self):
    """Simulate hardware-level characteristics"""
    hardware_script = """
    // Advanced hardware simulation
    const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        // GPU fingerprint spoofing
        if (parameter === 37445) return 'Google Inc. (Apple GPU)';
        if (parameter === 37446) return 'Apple Metal Renderer';
        return originalGetParameter.call(this, parameter);
    };
    
    // AudioContext fingerprint randomization
    const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
    AudioContext.prototype.createAnalyser = function() {
        const analyser = originalCreateAnalyser.apply(this, arguments);
        // Add slight variations to audio processing
        analyser.frequencyBinCount = 1024;
        return analyser;
    };
    """
    self.page.add_init_script(hardware_script)

def _simulate_network_imperfections(self):
    """Add network-level imperfections"""
    network_script = """
    // Simulate real network conditions
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        // Randomly delay requests (10-200ms)
        const delay = Math.random() * 190 + 10;
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve(originalFetch.apply(this, args));
            }, delay);
        });
    };
    """
    self.page.add_init_script(network_script)