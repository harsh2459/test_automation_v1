import json
import os
import hashlib
from datetime import datetime
from typing import Dict, Any

class SessionManager:
    def __init__(self):
        self.sessions_dir = "sessions"
        os.makedirs(self.sessions_dir, exist_ok=True)
    
    def create_session_id(self, proxy_info: Dict = None) -> str:
        """Create a unique session ID based on proxy and timestamp"""
        base_string = f"{datetime.now().timestamp()}"
        if proxy_info:
            proxy_str = proxy_info.get('server', '') + proxy_info.get('username', '') + proxy_info.get('password', '')
            base_string += proxy_str
        return hashlib.md5(base_string.encode()).hexdigest()[:16]
    
    def save_session_data(self, session_id: str, data: Dict[str, Any]):
        """Save session data to file"""
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        with open(session_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_session_data(self, session_id: str) -> Dict[str, Any]:
        """Load session data from file"""
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                return json.load(f)
        return {}
    
    def get_storage_state_path(self, session_id: str) -> str:
        """Get path for browser storage state"""
        return os.path.join(self.sessions_dir, f"{session_id}_storage_state.json")