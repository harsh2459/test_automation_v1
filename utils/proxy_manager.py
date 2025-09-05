from utils.proxy_validator import ProxyValidator
import random
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
class AdvancedProxyManager:
    def __init__(self, proxy_sources: List[str] = None):
    self.proxy_sources = proxy_sources or [
        "https://www.proxy-list.download/api/v1/get?type=http",
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt"
    ]
    self.proxies = []
    self.proxy_stats = {}
    self.last_refresh = datetime.now()
    self.validator = ProxyValidator()
    self.load_proxies()

# Update the load_proxies method to validate proxies
def load_proxies(self):
    """Load and validate proxies from multiple sources"""
    self.proxies = []
    raw_proxies = []
    
    for source in self.proxy_sources:
        try:
            response = requests.get(source, timeout=15)
            if response.status_code == 200:
                proxies_from_source = response.text.strip().split('\n')
                raw_proxies.extend([p.strip() for p in proxies_from_source if p.strip()])
                print(f"Loaded {len(proxies_from_source)} proxies from {source}")
        except Exception as e:
            print(f"Error loading proxies from {source}: {e}")
            continue
    
    # Remove duplicates
    raw_proxies = list(set(raw_proxies))
    print(f"Total raw proxies: {len(raw_proxies)}")
    
    # Convert to proxy format
    proxy_objects = []
    for proxy_str in raw_proxies:
        proxy_parts = proxy_str.split(':')
        if len(proxy_parts) == 2:
            proxy_objects.append({"server": f"http://{proxy_str}"})
        elif len(proxy_parts) == 4:
            proxy_objects.append({
                "server": f"http://{proxy_parts[0]}:{proxy_parts[1]}",
                "username": proxy_parts[2],
                "password": proxy_parts[3]
            })
    
    # Validate proxies
    print("Validating proxies...")
    self.proxies = self.validator.validate_proxies_batch(proxy_objects)
    print(f"Valid proxies: {len(self.proxies)}")
    
    # Initialize statistics
    for proxy in self.proxies:
        proxy_str = proxy["server"].replace("http://", "").replace("https://", "")
        if proxy_str not in self.proxy_stats:
            self.proxy_stats[proxy_str] = {
                "success_count": 0,
                "fail_count": 0,
                "last_used": None,
                "cooldown_until": None,
                "speed": random.uniform(0.5, 2.0),
                "ban_count": 0
            }
    
    def get_proxy(self, proxy_type: Optional[str] = None, 
                 min_success_rate: float = 0.7,
                 cooldown_hours: int = 2,
                 max_ban_count: int = 3) -> Optional[Dict]:
        """Get a proxy based on performance and cooldown"""
        now = datetime.now()
        
        # Refresh proxies if it's been more than 6 hours or we're running low
        if (now - self.last_refresh) > timedelta(hours=6) or len(self.proxies) < 10:
            self.load_proxies()
            self.last_refresh = now
        
        # Filter available proxies
        available = []
        for proxy, stats in self.proxy_stats.items():
            # Skip if banned too many times
            if stats["ban_count"] >= max_ban_count:
                continue
                
            # Check cooldown
            if stats["cooldown_until"] and now < stats["cooldown_until"]:
                continue
            
            # Check success rate
            total_attempts = stats["success_count"] + stats["fail_count"]
            if total_attempts > 0:
                success_rate = stats["success_count"] / total_attempts
                if success_rate < min_success_rate:
                    continue
            
            available.append((proxy, stats))
        
        if not available:
            print("No available proxies meeting criteria")
            return None
        
        # Weight by performance and recency
        weights = []
        for proxy, stats in available:
            # Higher weight for better success rate and faster speed
            total_attempts = stats["success_count"] + stats["fail_count"]
            success_rate = stats["success_count"] / total_attempts if total_attempts > 0 else 0.5
            weight = success_rate * (1 / stats["speed"])
            
            # Reduce weight for recently used proxies
            if stats["last_used"]:
                hours_since_use = (now - stats["last_used"]).total_seconds() / 3600
                weight *= min(1.0, hours_since_use / 24)
            
            # Reduce weight for proxies with bans
            weight *= (1 - (stats["ban_count"] / (max_ban_count + 1)))
            
            weights.append(weight)
        
        # Select proxy based on weights
        selected_proxy = random.choices(available, weights=weights, k=1)[0][0]
        self.proxy_stats[selected_proxy]["last_used"] = now
        
        # Format for Playwright
        proxy_parts = selected_proxy.split(':')
        if len(proxy_parts) == 2:
            server = f"http://{selected_proxy}"
            return {"server": server}
        elif len(proxy_parts) == 4:
            server = f"http://{proxy_parts[0]}:{proxy_parts[1]}"
            return {
                "server": server,
                "username": proxy_parts[2],
                "password": proxy_parts[3]
            }
        else:
            return {"server": selected_proxy}
    
    def update_proxy_performance(self, proxy: Dict, success: bool, ban_detected: bool = False):
        """Update proxy statistics after use"""
        if not proxy or "server" not in proxy:
            return
        
        proxy_str = proxy["server"].replace("http://", "").replace("https://", "")
        
        if proxy_str not in self.proxy_stats:
            self.proxy_stats[proxy_str] = {
                "success_count": 0,
                "fail_count": 0,
                "last_used": None,
                "cooldown_until": None,
                "speed": random.uniform(0.5, 2.0),
                "ban_count": 0
            }
        
        if success:
            self.proxy_stats[proxy_str]["success_count"] += 1
        else:
            self.proxy_stats[proxy_str]["fail_count"] += 1
            # Apply cooldown for failed proxies
            self.proxy_stats[proxy_str]["cooldown_until"] = datetime.now() + timedelta(hours=2)
        
        if ban_detected:
            self.proxy_stats[proxy_str]["ban_count"] += 1
            self.proxy_stats[proxy_str]["cooldown_until"] = datetime.now() + timedelta(hours=6)
    
    def export_stats(self, filename="proxy_stats.json"):
        """Export proxy statistics to a file"""
        with open(filename, 'w') as f:
            json.dump(self.proxy_stats, f, indent=2)
    
    def import_stats(self, filename="proxy_stats.json"):
        """Import proxy statistics from a file"""
        try:
            with open(filename, 'r') as f:
                self.proxy_stats = json.load(f)
        except FileNotFoundError:
            print("No existing proxy stats found")