from playwright.sync_api import sync_playwright
import random
import time
import os
import json
import hashlib
from datetime import datetime
import re

try:
    from playwright_stealth import stealth_sync
    HAVE_STEALTH = True
except ImportError:
    HAVE_STEALTH = False

class BrowserEngine:
    def __init__(self, headless=False, proxy=None, user_agent=None, fingerprint=None):
        self.headless = headless
        self.proxy = proxy
        self.user_agent = user_agent or self.get_random_user_agent()
        self.fingerprint = fingerprint or {}
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:12]
        self.proxy_manager = None
        self.geolocation = self._generate_geolocation()
        
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
        """Get a more diverse set of user agents"""
        user_agents = [
            # Chrome Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
            
            # Chrome macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
            
            # Firefox Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
            
            # Firefox macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0",
            
            # Safari
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
            
            # Edge
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62",
        ]
        return random.choice(user_agents)
    
    def launch_browser(self, retry_count=3):
        """Launch browser with advanced stealth and proxy rotation"""
        for attempt in range(retry_count):
            try:
                # Rotate proxy if we have a proxy manager
                if self.proxy_manager:
                    self.proxy = self.proxy_manager.get_proxy()
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
                        "width": random.randint(1200, 1920),
                        "height": random.randint(800, 1080)
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
                
                print(f"Browser launched successfully with session ID: {self.session_id}")
                if self.proxy:
                    print(f"Using proxy: {self.proxy.get('server', 'Unknown')}")
                
                return self.page
                
            except Exception as e:
                print(f"Error launching browser (attempt {attempt + 1}/{retry_count}): {e}")
                
                # Update proxy performance if we have a proxy manager
                if self.proxy_manager and self.proxy:
                    self.proxy_manager.update_proxy_performance(self.proxy, success=False)
                
                self.close()
                
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
        stealth_script = """
        // Override navigator properties
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
        
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );

        // Override plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [{
                name: 'Chrome PDF Plugin',
                filename: 'internal-pdf-viewer',
                description: 'Portable Document Format'
            }, {
                name: 'Chrome PDF Viewer',
                filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                description: ''
            }, {
                name: 'Native Client',
                filename: 'internal-nacl-plugin',
                description: ''
            }],
        });

        // Override languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['%s'],
        });
        
        // Override chrome object
        window.chrome = {
            app: {
                isInstalled: false,
            },
            webstore: {
                onInstallStageChanged: {},
                onDownloadProgress: {},
            },
            runtime: {
                PlatformOs: {
                    MAC: 'mac',
                    WIN: 'win',
                    ANDROID: 'android',
                    CROS: 'cros',
                    LINUX: 'linux',
                    OPENBSD: 'openbsd',
                },
                PlatformArch: {
                    ARM: 'arm',
                    X86_32: 'x86-32',
                    X86_64: 'x86-64',
                },
                PlatformNaclArch: {
                    ARM: 'arm',
                    X86_32: 'x86-32',
                    X86_64: 'x86-64',
                },
                RequestUpdateCheckStatus: {
                    THROTTLED: 'throttled',
                    NO_UPDATE: 'no_update',
                    UPDATE_AVAILABLE: 'update_available',
                },
                OnInstalledReason: {
                    INSTALL: 'install',
                    UPDATE: 'update',
                    CHROME_UPDATE: 'chrome_update',
                    SHARED_MODULE_UPDATE: 'shared_module_update',
                },
                OnRestartRequiredReason: {
                    APP_UPDATE: 'app_update',
                    OS_UPDATE: 'os_update',
                    PERIODIC: 'periodic',
                },
            },
        };
        
        // Mock media devices
        Object.defineProperty(navigator, 'mediaDevices', {
            get: () => ({
                enumerateDevices: () => Promise.resolve([
                    { kind: 'audioinput', deviceId: 'default', label: '', groupId: '' },
                    { kind: 'videoinput', deviceId: 'default', label: '', groupId: '' },
                ]),
                getUserMedia: () => Promise.resolve({}),
            }),
        });
        
        // Mock battery API
        Object.defineProperty(navigator, 'getBattery', {
            get: () => () => Promise.resolve({
                level: 0.%d,
                charging: %s,
                chargingTime: %d,
                dischargingTime: Infinity,
            }),
        });
        
        // Mock connection API
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                downlink: %d,
                effectiveType: '%s',
                rtt: %d,
                saveData: false,
            }),
        });
        """ % (
            self._get_language_from_ua(),
            random.randint(10, 99),
            str(random.random() < 0.3).lower(),
            random.randint(1800, 3600),
            random.uniform(1, 100),
            random.choice(['4g', '3g', '2g']),
            random.randint(50, 200)
        )
        
        self.page.add_init_script(stealth_script)
    
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
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except:
            pass
    
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