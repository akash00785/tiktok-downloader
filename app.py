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
        
        # এখানে আসল পরিবর্তন: 'status' এর বদলে 'code' চেক করছি
        if result.get('code') == 0:
            # লিঙ্কটি 'data' এর ভেতরে 'play' কী-তে আছে
            download_url = result.get('data', {}).get('play')
            return jsonify({'success': True, 'url': download_url})
        else:
            return jsonify({'success': False, 'error': 'API-তে ভিডিও পাওয়া যায়নি'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
