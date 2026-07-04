from flask import Flask, render_template, request, jsonify
import yt_dlp

# এখানে template_folder উল্লেখ করে দেওয়া হয়েছে যাতে সার্ভার templates ফোল্ডারটি খুঁজে পায়
app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    video_url = data.get('url')
    
    # yt_dlp কনফিগারেশন
    ydl_opts = {}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            # ভিডিওর সরাসরি লিঙ্ক বা স্ট্রিম লিঙ্ক বের করা
            url = info.get('url')
            return jsonify({'success': True, 'url': url})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Render-এ পোর্ট সমস্যা এড়ানোর জন্য এটি ব্যবহার করা ভালো
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
