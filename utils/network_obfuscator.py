import random
import time
from datetime import datetime

class NetworkObfuscator:
    def __init__(self):
        self.request_timings = []
        self.last_request = None
        
    def simulate_network_conditions(self, request_type):
        """Simulate realistic network conditions for requests"""
        # Base timing based on request type
        base_times = {
            "navigation": random.uniform(1.5, 3.5),
            "resource": random.uniform(0.1, 1.2),
            "xhr": random.uniform(0.3, 2.0),
            "fetch": random.uniform(0.2, 1.8)
        }
        
        base_time = base_times.get(request_type, random.uniform(0.5, 2.0))
        
        # Add variability based on time of day
        hour = datetime.now().hour
        if 0 <= hour < 6:  # Night - faster
            base_time *= random.uniform(0.7, 0.9)
        elif 18 <= hour < 24:  # Evening - slower
            base_time *= random.uniform(1.1, 1.3)
        
        # Add random jitter
        jitter = random.uniform(0.8, 1.2)
        final_time = base_time * jitter
        
        # Ensure minimum time between requests
        if self.last_request:
            elapsed = time.time() - self.last_request
            if elapsed < 0.1:  # Minimum 100ms between requests
                final_time += (0.1 - elapsed)
        
        self.last_request = time.time()
        self.request_timings.append((request_type, final_time))
        
        return final_time
    
    def get_traffic_profile(self):
        """Generate a traffic profile for this session"""
        if not self.request_timings:
            return {"average_request_time": 1.0, "request_pattern": "steady"}
        
        total_time = sum(t for _, t in self.request_timings)
        avg_time = total_time / len(self.request_timings)
        
        # Analyze request pattern
        times = [t for _, t in self.request_timings]
        variance = sum((t - avg_time) ** 2 for t in times) / len(times)
        
        if variance < 0.1:
            pattern = "steady"
        elif variance < 0.5:
            pattern = "variable"
        else:
            pattern = "bursty"
        
        return {
            "average_request_time": avg_time,
            "request_pattern": pattern,
            "total_requests": len(self.request_timings)
        }