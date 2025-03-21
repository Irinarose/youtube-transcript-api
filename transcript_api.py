from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

app = Flask(__name__)

# Custom HTTP adapter to disable SSL verification (for testing only)
class NoSSLVerificationAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.check_hostname = False
        context.verify_mode = False
        kwargs['ssl_context'] = context
        return super(NoSSLVerificationAdapter, self).init_poolmanager(*args, **kwargs)

# Create a custom session with the adapter
session = requests.Session()
session.mount('https://', NoSSLVerificationAdapter())

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
            "http": "http://brd-customer-hl_dbf2a686-zone-residential_proxy1:kgvk3uownv4d@brd.superproxy.io:33335",
            "https": "http://brd-customer-hl_dbf2a686-zone-residential_proxy1:kgvk3uownv4d@brd.superproxy.io:33335"
        }
        # Fetch transcript using the proxy with custom session
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'], proxies=proxies, http_client=session)
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return jsonify({"transcript": transcript_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)