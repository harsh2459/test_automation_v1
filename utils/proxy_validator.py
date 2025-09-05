import requests
import concurrent.futures
from typing import List, Dict
import time

class ProxyValidator:
    def __init__(self):
        self.test_urls = [
            "http://httpbin.org/ip",
            "http://httpbin.org/user-agent",
            "http://httpbin.org/headers"
        ]
    
    def validate_proxy(self, proxy: Dict) -> bool:
        """Validate if a proxy is working and not blocked"""
        try:
            proxy_str = self._format_proxy(proxy)
            
            for test_url in self.test_urls:
                response = requests.get(
                    test_url,
                    proxies={"http": proxy_str, "https": proxy_str},
                    timeout=10
                )
                
                if response.status_code != 200:
                    return False
                    
                # Additional checks for proxy quality
                response_time = response.elapsed.total_seconds()
                if response_time > 5:  # Too slow
                    return False
                    
            return True
            
        except:
            return False
    
    def validate_proxies_batch(self, proxies: List[Dict], max_workers=10) -> List[Dict]:
        """Validate multiple proxies concurrently"""
        valid_proxies = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.validate_proxy, proxy): proxy 
                for proxy in proxies
            }
            
            for future in concurrent.futures.as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    if future.result():
                        valid_proxies.append(proxy)
                except:
                    pass
        
        return valid_proxies
    
    def _format_proxy(self, proxy: Dict) -> str:
        """Format proxy for requests library"""
        server = proxy.get("server", "")
        username = proxy.get("username", "")
        password = proxy.get("password", "")
        
        if username and password:
            return f"http://{username}:{password}@{server.replace('http://', '')}"
        else:
            return server