import random
import time
import math
from typing import Callable, List
import numpy as np

class AdvancedBehaviorSimulator:
    def __init__(self):
        self.action_patterns = self._load_behavior_patterns()
        self.last_action_time = 0
        self.action_history = []
    
    def simulate_mouse_movement(self, page, start_x, start_y, end_x, end_y):
        """Simulate human-like mouse movement with acceleration curves"""
        # Generate a Bezier curve with random control points
        control1_x = random.uniform(start_x, end_x)
        control1_y = random.uniform(start_y, end_y)
        control2_x = random.uniform(start_x, end_x)
        control2_y = random.uniform(start_y, end_y)
        
        # Generate points along the curve with variable density
        num_points = random.randint(8, 25)
        points = []
        
        for i in range(num_points):
            t = i / (num_points - 1)
            # Cubic Bezier formula with some randomness
            x = (1-t)**3 * start_x + 3*(1-t)**2*t * control1_x + 3*(1-t)*t**2 * control2_x + t**3 * end_x
            y = (1-t)**3 * start_y + 3*(1-t)**2*t * control1_y + 3*(1-t)*t**2 * control2_y + t**3 * end_y
            
            # Add some randomness to the points
            x += random.uniform(-5, 5)
            y += random.uniform(-5, 5)
            
            points.append((x, y))
        
        # Move through points with variable speed (slower at curves)
        for i, (x, y) in enumerate(points):
            # Calculate speed based on curve sharpness
            if i > 0 and i < len(points) - 1:
                prev_point = points[i-1]
                next_point = points[i+1]
                
                # Calculate angle between points
                angle = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
                angle_diff = abs(math.atan2(y - prev_point[1], x - prev_point[0]) - angle)
                
                # Slower on curves
                speed_factor = 1 - min(angle_diff / math.pi, 0.5)
            else:
                speed_factor = 1
            
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.01, 0.05) * speed_factor)
    
    def simulate_typing(self, text, page, element):
        """Simulate human typing with mistakes and corrections"""
        element.click()
        time.sleep(random.uniform(0.1, 0.7))
        
        typed = ""
        words = text.split()
        word_index = 0
        
        while word_index < len(words):
            word = words[word_index]
            
            # Occasionally pause between words
            if word_index > 0 and random.random() < 0.4:
                pause_time = random.uniform(0.1, 0.5)
                time.sleep(pause_time)
            
            # Type the word character by character
            for i, char in enumerate(word):
                # Occasionally make a mistake (more common at beginning of words)
                if random.random() < 0.03 + (0.02 if i == 0 else 0):
                    wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                    page.keyboard.type(wrong_char)
                    time.sleep(random.uniform(0.1, 0.4))
                    
                    # Sometimes notice and correct immediately, sometimes not
                    if random.random() < 0.7:
                        page.keyboard.press('Backspace')
                        time.sleep(random.uniform(0.1, 0.3))
                    else:
                        # Type a few more characters before noticing
                        for _ in range(random.randint(1, 3)):
                            if i + 1 < len(word):
                                next_char = word[i+1]
                                page.keyboard.type(next_char)
                                time.sleep(random.uniform(0.05, 0.2))
                                i += 1
                        
                        # Then correct all mistakes
                        for _ in range(random.randint(2, 5)):
                            page.keyboard.press('Backspace')
                            time.sleep(random.uniform(0.1, 0.2))
                        
                        # Retype the word correctly
                        page.keyboard.type(word[:i+1])
                        time.sleep(random.uniform(0.05, 0.15) * (i+1))
                        break
                
                # Type the character with variable speed
                page.keyboard.type(char)
                typed += char
                time.sleep(random.uniform(0.05, 0.25))
                
                # Occasionally pause for "thinking" mid-word
                if random.random() < 0.01 and len(typed) > 5:
                    time.sleep(random.uniform(0.3, 1.0))
            
            # Add space after word
            if word_index < len(words) - 1:
                page.keyboard.press('Space')
                time.sleep(random.uniform(0.05, 0.15))
            
            word_index += 1
    
    def simulate_scrolling(self, page, scroll_amount=None):
        """Simulate human-like scrolling patterns"""
        if scroll_amount is None:
            scroll_amount = random.randint(300, 1200)
        
        # Determine scroll direction
        direction = -1 if random.random() < 0.5 else 1
        scroll_amount *= direction
        
        # Scroll in chunks with variable speed and occasional overshooting
        total_scrolled = 0
        target_scroll = scroll_amount
        
        while abs(total_scrolled) < abs(target_scroll):
            # Vary chunk size
            chunk_size = random.randint(50, 200) * (1 if target_scroll > 0 else -1)
            
            # Occasionally overshoot or undershoot
            if random.random() < 0.2:
                chunk_size *= random.uniform(1.2, 1.8)
            
            # Scroll the chunk
            page.evaluate(f"window.scrollBy(0, {chunk_size})")
            total_scrolled += chunk_size
            
            # Vary pause time between scrolls
            pause_time = random.uniform(0.3, 1.5)
            
            # Occasionally add a longer pause
            if random.random() < 0.1:
                pause_time += random.uniform(1.0, 3.0)
            
            time.sleep(pause_time)
            
            # Occasionally scroll back a bit (human-like behavior)
            if random.random() < 0.15:
                backscroll = random.randint(20, 80) * (-1 if chunk_size > 0 else 1)
                page.evaluate(f"window.scrollBy(0, {backscroll})")
                time.sleep(random.uniform(0.2, 0.8))
                total_scrolled += backscroll
    
    def simulate_browsing_pattern(self, page, actions: List[Callable]):
        """Simulate a natural browsing pattern with varied actions"""
        # Start with some initial random actions
        initial_actions = random.randint(2, 6)
        for _ in range(initial_actions):
            action = random.choice(actions)
            action()
            
            # Vary time between actions
            action_delay = random.expovariate(1/2.0)  # Exponential distribution
            time.sleep(min(action_delay, 5.0))  # Cap at 5 seconds
        
        # Simulate reading/consuming content with variable time
        reading_time = random.lognormvariate(3.0, 0.8)  # Log-normal distribution
        time.sleep(min(reading_time, 120))  # Cap at 2 minutes
        
        # More actions after "reading" with different pattern
        post_reading_actions = random.randint(1, 4)
        for _ in range(post_reading_actions):
            action = random.choice(actions)
            action()
            
            # Shorter delays after reading
            action_delay = random.expovariate(1/1.0)
            time.sleep(min(action_delay, 3.0))
    
    def simulate_element_interaction(self, page, selector, action_type="click"):
        """Simulate human interaction with a specific element"""
        elements = page.query_selector_all(selector)
        if not elements:
            return False
        
        element = random.choice(elements)
        
        try:
            # Get element position
            box = element.bounding_box()
            if not box:
                return False
            
            # Move mouse to element with human-like movement
            viewport = page.viewport_size
            start_x = random.randint(0, viewport["width"])
            start_y = random.randint(0, viewport["height"])
            
            self.simulate_mouse_movement(page, start_x, start_y, 
                                       box["x"] + box["width"]/2, 
                                       box["y"] + box["height"]/2)
            
            # Vary hover time before action
            hover_time = random.uniform(0.2, 1.5)
            time.sleep(hover_time)
            
            # Perform the action
            if action_type == "click":
                element.click()
            elif action_type == "hover":
                element.hover()
            elif action_type == "type" and element.is_editable():
                test_text = "Test input " + str(random.randint(1, 100))
                self.simulate_typing(test_text, page, element)
            
            # Vary time after action
            post_action_time = random.uniform(0.5, 2.0)
            time.sleep(post_action_time)
            
            return True
            
        except Exception as e:
            print(f"Error interacting with element: {e}")
            return False
    
    def _load_behavior_patterns(self):
        """Load different behavior patterns for different user types"""
        return {
            "casual": {
                "scroll_speed": random.uniform(0.8, 1.2),
                "typing_speed": random.uniform(0.7, 1.1),
                "action_delay": random.uniform(1.0, 3.0),
                "reading_time_mean": 25.0,
                "reading_time_std": 0.7,
            },
            "focused": {
                "scroll_speed": random.uniform(1.2, 1.8),
                "typing_speed": random.uniform(1.1, 1.5),
                "action_delay": random.uniform(0.5, 1.5),
                "reading_time_mean": 45.0,
                "reading_time_std": 0.5,
            },
            "distracted": {
                "scroll_speed": random.uniform(0.5, 0.9),
                "typing_speed": random.uniform(0.5, 0.9),
                "action_delay": random.uniform(2.0, 5.0),
                "reading_time_mean": 15.0,
                "reading_time_std": 1.2,
            }
        }
    
    def get_random_pattern(self):
        """Get a random behavior pattern"""
        return random.choice(list(self.action_patterns.keys()))