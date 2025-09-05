# human_behavior.py
import random
import time
import math
from typing import Callable, List
import numpy as np

class AdvancedBehaviorSimulator:
    def __init__(self):
        self.action_patterns = self._load_behavior_patterns()
    
    def simulate_mouse_movement(self, page, start_x, start_y, end_x, end_y):
        """Simulate human-like mouse movement with acceleration curves"""
        # Generate a Bezier curve with random control points
        control1_x = random.uniform(start_x, end_x)
        control1_y = random.uniform(start_y, end_y)
        control2_x = random.uniform(start_x, end_x)
        control2_y = random.uniform(start_y, end_y)
        
        # Generate points along the curve
        num_points = random.randint(8, 20)
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            # Cubic Bezier formula
            x = (1-t)**3 * start_x + 3*(1-t)**2*t * control1_x + 3*(1-t)*t**2 * control2_x + t**3 * end_x
            y = (1-t)**3 * start_y + 3*(1-t)**2*t * control1_y + 3*(1-t)*t**2 * control2_y + t**3 * end_y
            points.append((x, y))
        
        # Move through points with variable speed
        for x, y in points:
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.01, 0.05))
    
    def simulate_typing(self, text, page, element):
        """Simulate human typing with mistakes and corrections"""
        element.click()
        time.sleep(random.uniform(0.1, 0.5))
        
        typed = ""
        for char in text:
            # Occasionally make a mistake
            if random.random() < 0.03:  # 3% chance of error
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                page.keyboard.type(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                page.keyboard.press('Backspace')
                time.sleep(random.uniform(0.1, 0.2))
            
            # Type the character with variable speed
            page.keyboard.type(char)
            typed += char
            time.sleep(random.uniform(0.05, 0.2))
            
            # Occasionally pause for "thinking"
            if random.random() < 0.02 and len(typed) > 5:
                time.sleep(random.uniform(0.5, 1.5))
    
    def simulate_scrolling(self, page, scroll_amount=None):
        """Simulate human-like scrolling patterns"""
        if scroll_amount is None:
            scroll_amount = random.randint(300, 1000)
        
        # Scroll in chunks with occasional overshooting
        chunks = random.randint(3, 8)
        chunk_size = scroll_amount / chunks
        
        for i in range(chunks):
            # Scroll the chunk
            page.evaluate(f"window.scrollBy(0, {chunk_size})")
            
            # Occasionally overshoot and correct
            if random.random() < 0.2:
                overshoot = random.randint(50, 150)
                page.evaluate(f"window.scrollBy(0, {overshoot})")
                time.sleep(random.uniform(0.1, 0.3))
                page.evaluate(f"window.scrollBy(0, {-overshoot})")
            
            time.sleep(random.uniform(0.5, 1.5))
    
    def simulate_browsing_pattern(self, page, actions: List[Callable]):
        """Simulate a natural browsing pattern with varied actions"""
        # Start with some initial random actions
        for _ in range(random.randint(2, 5)):
            random.choice(actions)()
            time.sleep(random.uniform(1.0, 3.0))
        
        # Simulate reading/consuming content
        reading_time = random.expovariate(1/30)  # Exponential distribution, mean 30s
        time.sleep(min(reading_time, 120))  # Cap at 2 minutes
        
        # More actions after "reading"
        for _ in range(random.randint(1, 3)):
            random.choice(actions)()
            time.sleep(random.uniform(0.5, 2.0))
    
    def _load_behavior_patterns(self):
        """Load different behavior patterns for different user types"""
        return {
            "casual": {
                "scroll_speed": random.uniform(0.8, 1.2),
                "typing_speed": random.uniform(0.7, 1.1),
                "action_delay": random.uniform(1.0, 3.0),
            },
            "focused": {
                "scroll_speed": random.uniform(1.2, 1.8),
                "typing_speed": random.uniform(1.1, 1.5),
                "action_delay": random.uniform(0.5, 1.5),
            },
            "distracted": {
                "scroll_speed": random.uniform(0.5, 0.9),
                "typing_speed": random.uniform(0.5, 0.9),
                "action_delay": random.uniform(2.0, 5.0),
            }
        }