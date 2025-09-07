import random
import time
from datetime import datetime
import pytz

class EnvironmentSimulator:
    def __init__(self):
        self.timezone = None
        self.locale = None
        self.geographic_profile = None
        
    def generate_environmental_context(self, fingerprint):
        """Create a complete environmental context"""
        self.timezone = fingerprint.get('timezone', 'America/New_York')
        self.locale = fingerprint.get('locale', 'en-US')
        self.geographic_profile = self._select_geographic_profile()
        
        return {
            'timezone': self.timezone,
            'locale': self.locale,
            'geographic_profile': self.geographic_profile,
            'local_time': self._get_local_time(),
            'cultural_context': self._get_cultural_context(),
            'behavior_modifiers': self._get_behavior_modifiers()
        }
    
    def _select_geographic_profile(self):
        """Select a geographic profile based on timezone"""
        profiles = {
            'America/': {
                'scroll_speed': random.uniform(0.8, 1.5),
                'reading_speed': random.uniform(0.9, 1.3),
                'interaction_style': 'direct',
                'common_actions': ['scroll', 'click', 'hover']
            },
            'Europe/': {
                'scroll_speed': random.uniform(0.7, 1.2),
                'reading_speed': random.uniform(0.8, 1.1),
                'interaction_style': 'exploratory',
                'common_actions': ['scroll', 'hover', 'click', 'right-click']
            },
            'Asia/': {
                'scroll_speed': random.uniform(1.0, 1.8),
                'reading_speed': random.uniform(1.1, 1.6),
                'interaction_style': 'quick',
                'common_actions': ['scroll', 'click']
            }
        }
        
        for region, profile in profiles.items():
            if self.timezone.startswith(region):
                return profile
        
        return profiles['America/']  # Default
    
    def _get_local_time(self):
        """Get current time in the target timezone"""
        tz = pytz.timezone(self.timezone)
        return datetime.now(tz)
    
    def _get_cultural_context(self):
        """Add cultural context to behavior"""
        contexts = {
            'en-US': {'reading_pattern': 'f-shaped', 'attention_span': 45},
            'en-GB': {'reading_pattern': 'linear', 'attention_span': 55},
            'de-DE': {'reading_pattern': 'thorough', 'attention_span': 60},
            'ja-JP': {'reading_pattern': 'detailed', 'attention_span': 70}
        }
        return contexts.get(self.locale, contexts['en-US'])
    
    def _get_behavior_modifiers(self):
        """Get behavior modifiers based on time of day"""
        hour = self._get_local_time().hour
        
        if 5 <= hour < 12:  # Morning
            return {'energy_level': 'high', 'interaction_rate': 1.2}
        elif 12 <= hour < 17:  # Afternoon
            return {'energy_level': 'medium', 'interaction_rate': 1.0}
        elif 17 <= hour < 22:  # Evening
            return {'energy_level': 'medium', 'interaction_rate': 0.9}
        else:  # Night
            return {'energy_level': 'low', 'interaction_rate': 0.7}