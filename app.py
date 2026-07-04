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

    # এখানে অতিরিক্ত অপশন যোগ করা হয়েছে যা ব্লক হওয়ার সম্ভাবনা কমাবে
    ydl_opts = {
        'impersonate': 'chrome120',
        'quiet': False,  # এটি False রাখা হয়েছে যাতে লগে বিস্তারিত দেখা যায়
        'no_warnings': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # তথ্য এক্সট্রাক্ট করা
            info = ydl.extract_info(video_url, download=False)
            
            # লিঙ্ক খুঁজে বের করার চেষ্টা
            # অনেক সময় direct url এর বদলে formats এর ভেতরে লিঙ্ক থাকে
            video_url_final = info.get('url') or info.get('redirect_url')
            
            # যদি সরাসরি লিঙ্ক না পায়, তাহলে ফরম্যাট থেকে সেরা লিঙ্কটি নেওয়ার চেষ্টা
            if not video_url_final and 'formats' in info:
                video_url_final = info['formats'][0].get('url')

            if video_url_final:
                print(f"Success! URL found: {video_url_final}")
                return jsonify({'success': True, 'url': video_url_final})
            else:
                print("Error: Could not extract URL")
                return jsonify({'success': False, 'error': 'ভিডিও লিঙ্ক খুঁজে পাওয়া যায়নি।'})

    except Exception as e:
        error_msg = str(e)
        print(f"CRITICAL ERROR: {error_msg}")
        return jsonify({'success': False, 'error': error_msg})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
