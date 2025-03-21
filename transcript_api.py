from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = Flask(__name__)

# Function to extract video ID from URL
def get_video_id(youtube_url):
    video_id_match = re.search(r"(?:v=)([0-9A-Za-z_-]{11})", youtube_url)
    if not video_id_match:
        raise ValueError("Invalid YouTube URL")
    return video_id_match.group(1)

# API endpoint to fetch transcript
@app.route('/fetch-transcript', methods=['POST'])
def fetch_transcript():
    try:
        data = request.get_json()
        youtube_url = data.get('url')
        if not youtube_url:
            return jsonify({"error": "No URL provided"}), 400
        video_id = get_video_id(youtube_url)
        # Define proxy configuration
        proxies = {
            "http": "http://18.223.25.15:8080",  # New proxy IP and port
            "https": "http://18.223.25.15:8080"   # New proxy IP and port
        }
        # Fetch transcript using the proxy
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'], proxies=proxies)
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return jsonify({"transcript": transcript_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)