import random
import hashlib
import json
from typing import Dict, List

class FingerprintManager:
    def __init__(self):
        self.canvas_templates = self._load_canvas_templates()
        self.webgl_configs = self._load_webgl_configs()
        self.font_profiles = self._load_font_profiles()
        self.audio_profiles = self._load_audio_profiles()
    
    def get_comprehensive_fingerprint(self) -> Dict:
        """Generate a complete browser fingerprint with more variability"""
        # Create a more "messy" fingerprint with intentional slight inconsistencies
        platforms = ["Win32", "MacIntel", "Linux x86_64"]
        chosen_platform = random.choice(platforms)
        
        # Sometimes create slight inconsistencies (like real browsers)
        if random.random() < 0.2:  # 20% chance of inconsistency
            if chosen_platform == "Win32":
                user_agent = random.choice([
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
                ])
            elif chosen_platform == "MacIntel":
                user_agent = random.choice([
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
                ])
            else:  # Linux
                user_agent = random.choice([
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
                    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"
                ])
        else:
            user_agent = self.get_random_user_agent()
        return {
            "user_agent": self.get_random_user_agent(),
            "canvas": self.generate_canvas_fingerprint(),
            "webgl": self.generate_webgl_fingerprint(),
            "fonts": self.get_font_fingerprint(),
            "audio": self.generate_audio_fingerprint(),
            "hardwareConcurrency": random.choice([2, 4, 6, 8, 12, 16]),
            "deviceMemory": random.choice([4, 8, 16]),
            "platform": random.choice(["Win32", "MacIntel", "Linux x86_64"]),
            "screenWidth": random.randint(1200, 1920),
            "screenHeight": random.randint(800, 1080),
            "colorDepth": random.choice([24, 30, 32]),
            "timezone": self.get_timezone(),
            "language": self.get_language(),
            "session_id": hashlib.md5(str(random.random()).encode()).hexdigest()[:12],
        }
    
    @staticmethod
    def get_random_user_agent():
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62",
        ]
        return random.choice(user_agents)
    
    def generate_canvas_fingerprint(self) -> str:
        """Generate a unique canvas fingerprint"""
        template = random.choice(self.canvas_templates)
        variation = hashlib.md5(str(random.random()).encode()).hexdigest()[:10]
        return f"{template}-{variation}"
    
    def generate_webgl_fingerprint(self) -> Dict:
        """Generate WebGL vendor/renderer fingerprint"""
        config = random.choice(self.webgl_configs)
        return {
            "vendor": config["vendor"],
            "renderer": config["renderer"],
            "unmasked_vendor": config.get("unmasked_vendor", config["vendor"]),
            "unmasked_renderer": config.get("unmasked_renderer", config["renderer"]),
        }
    
    def get_font_fingerprint(self) -> List[str]:
        """Return a font list appropriate for the platform"""
        platform = random.choice(["windows", "mac", "linux"])
        return self.font_profiles[platform]
    
    def generate_audio_fingerprint(self) -> Dict:
        """Generate audio context fingerprint"""
        profile = random.choice(self.audio_profiles)
        return {
            "frequency": profile["base_freq"] * random.uniform(0.95, 1.05),
            "damping": profile["base_damp"] * random.uniform(0.95, 1.05),
        }
    
    def get_timezone(self) -> str:
        """Get a random timezone"""
        timezones = [
            "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
            "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Moscow",
            "Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata", "Australia/Sydney"
        ]
        return random.choice(timezones)
    
    def get_language(self) -> str:
        """Get a random language"""
        languages = ["en-US", "en-GB", "de-DE", "fr-FR", "ja-JP", "es-ES", "pt-BR", "ru-RU"]
        return random.choice(languages)
    
    def _load_canvas_templates(self) -> List[str]:
        return ["normal", "noise", "curve", "gradient", "pattern", "textured", "geometric"]
    
    def _load_webgl_configs(self) -> List[Dict]:
        return [
            {"vendor": "Google Inc.", "renderer": "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)"},
            {"vendor": "NVIDIA Corporation", "renderer": "NVIDIA GeForce RTX 3060/PCIe/SSE2"},
            {"vendor": "AMD", "renderer": "AMD Radeon RX 6700 XT"},
            {"vendor": "Intel Inc.", "renderer": "Intel Iris Xe Graphics"},
            {"vendor": "Apple Inc.", "renderer": "Apple M1 Pro"},
        ]
    
    def _load_font_profiles(self) -> Dict[str, List[str]]:
        return {
            "windows": [
                "Arial", "Times New Roman", "Courier New", "Verdana", "Tahoma",
                "Segoe UI", "Microsoft Sans Serif", "Calibri", "Cambria"
            ],
            "mac": [
                "Helvetica", "Helvetica Neue", "San Francisco", "Menlo", "Monaco",
                "Lucida Grande", "Geneva", "Arial", "Times"
            ],
            "linux": [
                "Ubuntu", "Liberation Sans", "DejaVu Sans", "FreeSans",
                "Roboto", "Open Sans", "Noto Sans", "Arial"
            ],
        }
    
    def _load_audio_profiles(self) -> List[Dict]:
        return [
            {"base_freq": 44100, "base_damp": 0.002},
            {"base_freq": 48000, "base_damp": 0.0015},
            {"base_freq": 32000, "base_damp": 0.003},
            {"base_freq": 22050, "base_damp": 0.0025},
        ]