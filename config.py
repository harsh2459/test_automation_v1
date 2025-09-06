import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_file="config/config.json"):
        self.config_file = config_file
        self.default_config = {
            "browser": {
                "headless": False,
                "viewport_width": 1366,
                "viewport_height": 768,
                "user_agents": [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62",
                ]
            },
            "proxy": {
                "enabled": True,
                "max_proxies": 100,
                "cache_expiry_hours": 6,
                "sources": [
                    "https://www.proxy-list.download/api/v1/get?type=http",
                    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
                    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
                    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
                    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
                ]
            },
            "behavior": {
                "min_read_time": 15,
                "max_read_time": 120,
                "scroll_variation": 0.3,
                "mouse_movement_intensity": 0.7
            },
            "stealth": {
                "webgl_vendor": "Google Inc.",
                "webgl_renderer": "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)",
                "hardware_concurrency": 8,
                "device_memory": 8
            }
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}. Using default configuration.")
        
        return self.default_config
    
    def save_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key_path, default=None):
        keys = key_path.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

# Global config instance
config = ConfigManager()