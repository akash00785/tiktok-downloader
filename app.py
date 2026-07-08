import os
import re
import logging
import requests
import time
from flask import Flask, render_template, request, jsonify

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, template_folder='templates')

class KeyManager:
    def __init__(self, keys):
        self.keys = [{'val': k.strip(), 'active': True, 'failed_at': 0} for k in keys if k.strip()]
        self.cooldown = 300 # 5 minutes cooldown for failed keys

    def get_active_key(self):
        now = time.time()
        for k in self.keys:
            if not k['active'] and (now - k['failed_at'] > self.cooldown):
                k['active'] = True # Cooldown শেষ হলে রি-অ্যাক্টিভেট
            if k['active']:
                return k
        return None

    def mark_failed(self, key_val):
        for k in self.keys:
            if k['val'] == key_val:
                k['active'] = False
                k['failed_at'] = time.time()
                logging.warning(f"Key exhausted: {key_val[:5]}...")

key_manager = KeyManager(os.environ.get("API_KEYS", "").split(","))

def is_valid_url(url):
    return re.match(r'^(https?://)?(www\.)?(tiktok\.com|vm\.tiktok\.com|vt\.tiktok\.com)/.+', url)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    video_url = data.get('url')

    if not is_valid_url(video_url):
        return jsonify({'success': False, 'error': 'Invalid TikTok URL'}), 400

    for _ in range(len(key_manager.keys)):
        key_obj = key_manager.get_active_key()
        if not key_obj:
            return jsonify({'success': False, 'error': 'All API keys exhausted. Please try later.'}), 503

        headers = {
            "x-rapidapi-host": "tiktok-video-no-watermark2.p.rapidapi.com",
            "x-rapidapi-key": key_obj['val'],
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            response = requests.post("https://tiktok-video-no-watermark2.p.rapidapi.com/", 
                                     headers=headers, data={"url": video_url, "hd": "1"}, timeout=15)
            
            if response.status_code == 429:
                key_manager.mark_failed(key_obj['val'])
                continue
            
            result = response.json()
            if result.get('code') == 0:
                d = result.get('data', {})
                return jsonify({
                    'success': True,
                    'hd_url': d.get('hdplay'),
                    'sd_url': d.get('play'),
                    'thumbnail': d.get('cover'),
                    'title': d.get('title'),
                    'author': d.get('author', {}).get('unique_id'),
                    'duration': d.get('duration')
                })
            else:
                return jsonify({'success': False, 'error': 'Video not found.'})

        except Exception as e:
            logging.error(f"Request error: {str(e)}")
            continue

    return jsonify({'success': False, 'error': 'Server error, please try again.'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
