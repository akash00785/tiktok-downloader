from flask import Flask, render_template, request, jsonify
import requests
import os
import random

app = Flask(__name__, template_folder='templates')

api_keys_string = os.environ.get("API_KEYS")
API_KEYS = api_keys_string.split(",") if api_keys_string else []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    if not API_KEYS:
        return jsonify({'success': False, 'error': 'API Key not configured'})

    data = request.json
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({'success': False, 'error': 'URL not provided'})

    api_url = "https://tiktok-video-no-watermark2.p.rapidapi.com/" 
    selected_key = random.choice(API_KEYS)
    
    headers = {
        "x-rapidapi-host": "tiktok-video-no-watermark2.p.rapidapi.com",
        "x-rapidapi-key": selected_key,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {"url": video_url, "hd": "1"}

    try:
        response = requests.post(api_url, headers=headers, data=payload)
        result = response.json()
        
        if result.get('code') == 0:
            data_content = result.get('data', {})
            download_url = data_content.get('hdplay') or data_content.get('play')
            return jsonify({'success': True, 'url': download_url})
        else:
            return jsonify({'success': False, 'error': 'API could not find video'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
