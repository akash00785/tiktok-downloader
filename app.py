from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__, template_folder='templates')

API_KEY = "1767026ffamsh2e8f6444c4d41b2p1af27ejsn62de6dc97c5b"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    video_url = data.get('url')
    if not video_url:
        return jsonify({'success': False, 'error': 'URL দেওয়া হয়নি'})

    api_url = "https://tiktok-video-no-watermark2.p.rapidapi.com/" 
    headers = {
        "x-rapidapi-host": "tiktok-video-no-watermark2.p.rapidapi.com",
        "x-rapidapi-key": API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {"url": video_url, "hd": "1"}

    try:
        response = requests.post(api_url, headers=headers, data=payload)
        result = response.json()
        
        # এখানে পুরো রেজাল্টটি লগ-এ প্রিন্ট করছি
        print(f"DEBUG RESPONSE: {result}") 
        
        if result.get('status') == 'success':
            # রেসপন্স অনুযায়ী লিঙ্ক বের করা
            download_url = result.get('data', {}).get('play') or result.get('data', {}).get('url')
            return jsonify({'success': True, 'url': download_url})
        else:
            return jsonify({'success': False, 'error': f"API Error: {result.get('msg', 'Unknown Error')}"})
            
    except Exception as e:
        print(f"CODE ERROR: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
