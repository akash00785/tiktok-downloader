from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({'success': False, 'error': 'URL দেওয়া হয়নি'})

    # impersonate বাদ দিয়ে সাধারণ হেডার্স ব্যবহার করছি যা অনেক সার্ভারে কাজ করে
    ydl_opts = {
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            url = info.get('url') or info.get('redirect_url')
            
            if url:
                return jsonify({'success': True, 'url': url})
            else:
                return jsonify({'success': False, 'error': 'ভিডিও লিঙ্ক পাওয়া যায়নি'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
