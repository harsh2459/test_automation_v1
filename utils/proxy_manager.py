# utils/proxy_manager.py
from utils.proxy_validator import ProxyValidator
import random
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json


class AdvancedProxyManager:
    def __init__(self, proxy_sources: Optional[List[str]] = None):
        """Manage loading, validating, and selecting proxies with basic telemetry."""
        self.proxy_sources = proxy_sources or [
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
        ]

        # Start with a couple of known proxies (as dicts!). Will be replaced after validation.
        self.proxies: List[Dict[str, str]] = [
            {"server": "http://8.219.97.248:80"},
            {"server": "http://176.126.103.194:44214"},
        ]

        self.proxy_stats: Dict[str, Dict] = {}
        self.last_refresh = datetime.now()
        self.validator = ProxyValidator()
        self.session_proxy_map: Dict[str, Dict] = {}  # session_id -> proxy dict
        self.load_proxies()

    def get_proxy_for_session(
        self,
        session_id: str,
        proxy_type: Optional[str] = None,
        min_success_rate: float = 0.7,
        cooldown_hours: int = 2,
        max_ban_count: int = 3,
    ) -> Optional[Dict]:
        """Return a sticky proxy for the given session if still valid; otherwise choose a new one."""
        if session_id in self.session_proxy_map:
            assigned_proxy = self.session_proxy_map[session_id]
            proxy_key = assigned_proxy["server"].replace("http://", "").replace("https://", "")
            stats = self.proxy_stats.get(proxy_key, {})
            if stats.get("ban_count", 0) < max_ban_count and (
                not stats.get("cooldown_until") or datetime.now() > stats["cooldown_until"]
            ):
                return assigned_proxy
            # Unstick if not valid anymore
            self.session_proxy_map.pop(session_id, None)

        proxy = self.get_proxy(proxy_type, min_success_rate, cooldown_hours, max_ban_count)
        if proxy:
            self.session_proxy_map[session_id] = proxy
        return proxy

    def load_proxies(self, max_proxies: int = 100) -> None:
        """Load and validate proxies from multiple sources, with a maximum limit."""
        raw_proxies: List[str] = []

        # 1) Fetch from remote sources
        for source in self.proxy_sources:
            try:
                response = requests.get(source, timeout=15)
                if response.status_code == 200 and response.text:
                    items = [p.strip() for p in response.text.strip().splitlines() if p.strip()]
                    raw_proxies.extend(items)
                    print(f"[ProxyManager] Loaded {len(items)} proxies from {source}")
                    # Early break if we already have plenty to sample from
                    if len(raw_proxies) >= max_proxies * 3:
                        break
            except Exception as e:
                print(f"[ProxyManager] Error loading proxies from {source}: {e}")
                continue

        # 2) Merge with a hardcoded fallback list
        hardcoded_proxies = [
            "8.219.97.248:80",
            "176.126.103.194:44214",
            "65.108.251.40:53535",
            "52.188.28.218:3128",
            "159.69.57.20:8880",
            "64.92.82.61:8081",
            "23.95.150.145",
            "198.23.239.134",
            "45.38.107.97",
            "107.172.163.27",
            "64.137.96.74",
            "45.43.186.39",
            "154.203.43.247",
            "216.10.27.159",
            "136.0.207.84",
            "142.147.128.93"
            # ... add more if you have them
        ]
        raw_proxies.extend(hardcoded_proxies)

        # 3) Deduplicate
        raw_proxies = list(set(raw_proxies))
        print(f"[ProxyManager] Total raw proxies gathered: {len(raw_proxies)}")

        # 4) Limit the number we validate (sample for variety)
        if len(raw_proxies) > max_proxies * 2:
            raw_proxies = random.sample(raw_proxies, max_proxies * 2)
            print(f"[ProxyManager] Limiting to {len(raw_proxies)} proxies for validation")

        # 5) Convert strings to validator objects
        proxy_objects: List[Dict[str, str]] = []
        for proxy_str in raw_proxies:
            parts = proxy_str.split(":")
            if len(parts) == 2:
                host, port = parts
                proxy_objects.append({"server": f"http://{host}:{port}"})
            elif len(parts) == 4:
                host, port, user, pwd = parts
                proxy_objects.append(
                    {"server": f"http://{host}:{port}", "username": user, "password": pwd}
                )
            # else: skip other formats

        print(f"[ProxyManager] Validating {len(proxy_objects)} proxies...")
        validated = self.validator.validate_proxies_batch(proxy_objects)

        # 6) Cap the final pool
        self.proxies = random.sample(validated, max_proxies) if len(validated) > max_proxies else validated
        print(f"[ProxyManager] Final validated proxies: {len(self.proxies)}")

        # 7) Initialize stats for new entries
        for p in self.proxies:
            key = p["server"].replace("http://", "").replace("https://", "")
            if key not in self.proxy_stats:
                self.proxy_stats[key] = {
                    "success_count": 0,
                    "fail_count": 0,
                    "last_used": None,
                    "cooldown_until": None,
                    "speed": random.uniform(0.5, 2.0),  # synthetic speed score
                    "ban_count": 0,
                }

        self.last_refresh = datetime.now()

    def get_proxy(
        self,
        proxy_type: Optional[str] = None,  # reserved for future use
        min_success_rate: float = 0.7,
        cooldown_hours: int = 2,
        max_ban_count: int = 3,
    ) -> Optional[Dict]:
        """Choose a proxy based on recent performance and cooldown/bans."""
        now = datetime.now()

        # Periodic refresh or if pool too small
        if (now - self.last_refresh) > timedelta(hours=6) or len(self.proxies) < 10:
            self.load_proxies()

        # Filter candidates
        available_keys: List[str] = []
        for proxy_key, stats in self.proxy_stats.items():
            if stats.get("ban_count", 0) >= max_ban_count:
                continue
            if stats.get("cooldown_until") and now < stats["cooldown_until"]:
                continue

            total = stats["success_count"] + stats["fail_count"]
            if total > 0:
                success_rate = stats["success_count"] / total
                if success_rate < min_success_rate:
                    continue

            available_keys.append(proxy_key)

        if not available_keys:
            print("[ProxyManager] No available proxies meeting criteria")
            return None

        # Weighted choice by performance & recency
        weights: List[float] = []
        for proxy_key in available_keys:
            stats = self.proxy_stats[proxy_key]
            total = stats["success_count"] + stats["fail_count"]
            success_rate = stats["success_count"] / total if total > 0 else 0.5
            weight = success_rate * (1 / max(stats["speed"], 0.01))
            if stats["last_used"]:
                hours_since = (now - stats["last_used"]).total_seconds() / 3600
                weight *= min(1.0, max(hours_since, 0.0) / 24.0)
            weight *= (1 - (stats["ban_count"] / (max_ban_count + 1)))
            weights.append(max(weight, 0.001))

        chosen_key = random.choices(available_keys, weights=weights, k=1)[0]

        # Find matching object in self.proxies
        for p in self.proxies:
            key = p["server"].replace("http://", "").replace("https://", "")
            if key == chosen_key:
                self.proxy_stats[chosen_key]["last_used"] = now
                return p

        # Fallback (should be rare)
        self.proxy_stats[chosen_key]["last_used"] = now
        return {"server": f"http://{chosen_key}"}

    def update_proxy_performance(self, proxy: Optional[Dict], success: bool, ban_detected: bool = False) -> None:
        """Update proxy statistics after a request finishes."""
        if not proxy or "server" not in proxy:
            return

        key = proxy["server"].replace("http://", "").replace("https://", "")

        if key not in self.proxy_stats:
            self.proxy_stats[key] = {
                "success_count": 0,
                "fail_count": 0,
                "last_used": None,
                "cooldown_until": None,
                "speed": random.uniform(0.5, 2.0),
                "ban_count": 0,
            }

        if success:
            self.proxy_stats[key]["success_count"] += 1
        else:
            self.proxy_stats[key]["fail_count"] += 1
            self.proxy_stats[key]["cooldown_until"] = datetime.now() + timedelta(hours=2)

        if ban_detected:
            self.proxy_stats[key]["ban_count"] += 1
            self.proxy_stats[key]["cooldown_until"] = datetime.now() + timedelta(hours=6)

    def export_stats(self, filename: str = "proxy_stats.json") -> None:
        """Export proxy statistics to a JSON file."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.proxy_stats, f, indent=2, ensure_ascii=False)

    def import_stats(self, filename: str = "proxy_stats.json") -> None:
        """Import proxy statistics from a JSON file (if present)."""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.proxy_stats = json.load(f)
        except FileNotFoundError:
            print("[ProxyManager] No existing proxy stats found")
