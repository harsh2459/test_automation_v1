# utils/proxy_validator.py
import requests
import concurrent.futures
from typing import List, Dict


class ProxyValidator:
    def __init__(self):
        self.test_urls = [
            "http://httpbin.org/ip",
            "http://httpbin.org/user-agent",
            "http://httpbin.org/headers",
        ]

    def validate_proxy(self, proxy: Dict) -> bool:
        """Validate if a proxy is working with more lenient checks"""
        try:
            proxy_str = self._format_proxy(proxy)

            # Try just one test URL with a shorter timeout
            test_url = "http://httpbin.org/ip"
            response = requests.get(
                test_url,
                proxies={"http": proxy_str, "https": proxy_str},
                timeout=5,  # Reduced from 10 to 5 seconds
            )

            # Accept any non-server-error response
            return response.status_code < 500

        except Exception:
            return False

    def validate_proxies_batch(
        self, proxies: List[Dict], max_workers: int = 20, timeout: int = 8
    ) -> List[Dict]:
        """Validate multiple proxies concurrently with optimized settings"""
        valid_proxies: List[Dict] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.validate_proxy, proxy): proxy for proxy in proxies
            }

            for future in concurrent.futures.as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    if future.result():
                        valid_proxies.append(proxy)
                        # Early exit if we already have many valid proxies
                        if len(valid_proxies) >= 100:
                            break
                except Exception:
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
