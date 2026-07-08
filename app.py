from flask import Flask, render_template, request, jsonify
import requests
import re
import os
import itertools

app = Flask(__name__, template_folder='templates')

# API Keys Configuration
api_keys = os.environ.get("API_KEYS", "").split(",")
api_keys = [k.strip() for k in api_keys if k.strip()]
key_cycle = itertools.cycle(api_keys)

def is_valid_url(url):
    pattern = r'^(https?://)?(www\.)?(tiktok\.com|vm\.tiktok\.com|vt\.tiktok\.com)/.+'
    return re.match(pattern, url)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    video_url = data.get('url')

    if not is_valid_url(video_url):
        return jsonify({'success': False, 'error': 'Invalid TikTok URL'})

    api_url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
    
    # Retry logic implementation
    for _ in range(len(api_keys)):
        current_key = next(key_cycle)
        headers = {
            "x-rapidapi-host": "tiktok-video-no-watermark2.p.rapidapi.com",
            "x-rapidapi-key": current_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            response = requests.post(api_url, headers=headers, data={"url": video_url, "hd": "1"}, timeout=15)
            
            if response.status_code == 429: # Rate limit
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
                return jsonify({'success': False, 'error': 'Video not found or Private'})
                
        except requests.exceptions.Timeout:
            continue
        except Exception as e:
            continue

    return jsonify({'success': False, 'error': 'All API Keys exhausted or Server Error'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
