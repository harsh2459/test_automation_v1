from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('wallpaper_analytics.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS visits
                 (id INTEGER PRIMARY KEY, ip TEXT, user_agent TEXT, 
                 timestamp DATETIME, referrer TEXT, country TEXT, 
                 session_id TEXT, fingerprint TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS ad_clicks
                 (id INTEGER PRIMARY KEY, ip TEXT, user_agent TEXT, 
                 timestamp DATETIME, ad_id INTEGER, session_id TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    # Capture all available information
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    referrer = request.headers.get('Referer')
    session_id = request.args.get('session_id', 'unknown')
    fingerprint = request.args.get('fingerprint', 'unknown')
    
    # Get all headers for better tracking
    all_headers = dict(request.headers)
    
    print(f"New visit - IP: {ip}, Session: {session_id}, Fingerprint: {fingerprint}")
    print(f"User Agent: {user_agent}")
    
    # Enhanced country detection (you can add a geoIP service later)
    country = "Unknown"
    if ip.startswith('192.168') or ip == '127.0.0.1':
        country = "Local"
    else:
        # Simple country detection based on common IP patterns
        country = self._detect_country_from_ip(ip)
    
    conn = sqlite3.connect('wallpaper_analytics.db')
    c = conn.cursor()
    c.execute('INSERT INTO visits (ip, user_agent, timestamp, referrer, country, session_id, fingerprint) VALUES (?, ?, ?, ?, ?, ?, ?)',
              (ip, user_agent, datetime.now(), referrer, country, session_id, fingerprint))
    conn.commit()
    conn.close()
    
    return render_template('index.html')

def _detect_country_from_ip(self, ip):
    """Simple country detection - replace with a real geoIP service later"""
    # This is a simplified version - in production, use a service like ipapi.co
    country_codes = {
        '93.': 'DE', '80.': 'UK', '194.': 'FR', '5.': 'ES', 
        '5.': 'IT', '5.': 'NL', '5.': 'PL', '5.': 'SE'
    }
    
    for prefix, country in country_codes.items():
        if ip.startswith(prefix):
            return country
    return "Unknown"

@app.route('/ad-click')
def ad_click():
    ad_id = request.args.get('ad_id', 1)
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    session_id = request.args.get('session_id', 'unknown')
    referrer = request.headers.get('Referer', 'direct')
    
    print(f"Ad click detected - Ad ID: {ad_id}, Session: {session_id}, IP: {ip}")
    
    conn = sqlite3.connect('wallpaper_analytics.db')
    c = conn.cursor()
    c.execute('INSERT INTO ad_clicks (ip, user_agent, timestamp, ad_id, session_id, referrer) VALUES (?, ?, ?, ?, ?, ?)',
              (ip, user_agent, datetime.now(), ad_id, session_id, referrer))
    conn.commit()
    
    # Get updated click count
    c.execute('SELECT COUNT(*) FROM ad_clicks')
    total_clicks = c.fetchone()[0]
    conn.close()
    
    return jsonify({'status': 'success', 'ad_id': ad_id, 'total_clicks': total_clicks})

@app.route('/analytics')
def analytics():
    conn = sqlite3.connect('wallpaper_analytics.db')
    c = conn.cursor()
    
    # Get total visits
    c.execute('SELECT COUNT(*) FROM visits')
    total_visits = c.fetchone()[0]
    
    # Get unique visitors (based on IP + User Agent combination)
    c.execute('SELECT COUNT(DISTINCT ip || user_agent) FROM visits')
    unique_visitors = c.fetchone()[0]
    
    # Get ad clicks
    c.execute('SELECT COUNT(*) FROM ad_clicks')
    total_clicks = c.fetchone()[0]
    
    # Get recent visits with more details
    c.execute('SELECT * FROM visits ORDER BY timestamp DESC LIMIT 50')
    recent_visits = c.fetchall()
    
    # Get recent ad clicks
    c.execute('SELECT * FROM ad_clicks ORDER BY timestamp DESC LIMIT 20')
    recent_clicks = c.fetchall()
    
    conn.close()
    
    return render_template('analytics.html', 
                         total_visits=total_visits,
                         unique_visitors=unique_visitors,
                         total_clicks=total_clicks,
                         recent_visits=recent_visits,
                         recent_clicks=recent_clicks)

if __name__ == '__main__':
    app.run(debug=True, port=5000)