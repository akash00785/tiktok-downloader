import os
import re
import logging
import itertools
import requests
from flask import Flask, render_template, request, jsonify, abort

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, template_folder='templates')

# Configuration
API_KEYS = [k.strip() for k in os.environ.get("API_KEYS", "").split(",") if k.strip()]
key_cycle = itertools.cycle(API_KEYS)

# URL Validator
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
        return jsonify({'success': False, 'error': 'Invalid TikTok URL provided.'}), 400

    api_url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
    
    # Retry Mechanism
    for _ in range(len(API_KEYS)):
        current_key = next(key_cycle)
        headers = {
            "x-rapidapi-host": "tiktok-video-no-watermark2.p.rapidapi.com",
            "x-rapidapi-key": current_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            response = requests.post(api_url, headers=headers, data={"url": video_url, "hd": "1"}, timeout=15)
            
            if response.status_code == 429:
                logging.warning(f"API Key {current_key[-5:]} reached limit.")
                continue
                
            result = response.json()
            if result.get('code') == 0:
                data = result.get('data', {})
                return jsonify({
                    'success': True,
                    'hd_url': data.get('hdplay'),
                    'sd_url': data.get('play'),
                    'thumbnail': data.get('cover'),
                    'title': data.get('title'),
                    'author': data.get('author', {}).get('unique_id'),
                    'duration': data.get('duration')
                })
            else:
                return jsonify({'success': False, 'error': 'Video not found or is private.'})
                
        except Exception as e:
            logging.error(f"Error occurred: {str(e)}")
            continue

    return jsonify({'success': False, 'error': 'All API keys exhausted. Please try later.'}), 503

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
