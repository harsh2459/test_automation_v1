import logging
import time
from datetime import datetime
from typing import Dict, Any
import json
import os

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("logs/automation.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("AutomationSystem")
    
    def start_timer(self, name: str):
        """Start a performance timer"""
        self.start_times[name] = time.time()
    
    def end_timer(self, name: str) -> float:
        """End a performance timer and return duration"""
        if name not in self.start_times:
            return 0
        
        duration = time.time() - self.start_times[name]
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append(duration)
        return duration
    
    def log_event(self, event_type: str, details: Dict[str, Any], level: str = "INFO"):
        """Log an event with details"""
        log_message = f"{event_type}: {json.dumps(details)}"
        
        if level == "INFO":
            self.logger.info(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)
        elif level == "ERROR":
            self.logger.error(log_message)
        elif level == "DEBUG":
            self.logger.debug(log_message)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a performance report"""
        report = {}
        for name, timings in self.metrics.items():
            if timings:
                report[name] = {
                    "count": len(timings),
                    "avg_time": sum(timings) / len(timings),
                    "min_time": min(timings),
                    "max_time": max(timings),
                    "total_time": sum(timings)
                }
        return report
    
    def save_report(self, filename: str = "logs/performance_report.json"):
        """Save performance report to file"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "performance": self.get_performance_report()
        }
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

# Global monitor instance
monitor = PerformanceMonitor()