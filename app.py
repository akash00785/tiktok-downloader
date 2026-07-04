from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    video_url = data.get('url')
    
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            url = info.get('url')
            return jsonify({'success': True, 'url': url})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
  
