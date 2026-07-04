from flask import Flask, render_template, request, jsonify
import yt_dlp
import os
import traceback # নতুন লাইব্রেরি যোগ করা হয়েছে

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

    ydl_opts = {
        'impersonate': 'chrome120',
        'quiet': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            url = info.get('url') or info.get('redirect_url')
            return jsonify({'success': True, 'url': url})
            
    except Exception as e:
        # এটি লগে একদম স্পষ্ট করে দেখিয়ে দেবে কী সমস্যা হচ্ছে
        error_details = traceback.format_exc()
        print(f"--- TRACEBACK ERROR ---\n{error_details}\n-----------------------")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
