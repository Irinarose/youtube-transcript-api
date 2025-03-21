from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import re
import requests
import os
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Path to the Bright Data certificate (relative to the script)
cert_path = os.path.join(os.path.dirname(__file__), 'brightdata_proxy_ca.crt')

# Create a session with the certificate
session = requests.Session()
session.verify = cert_path

# Function to extract video ID from URL
def get_video_id(youtube_url):
    logger.debug(f"Extracting video ID from URL: {youtube_url}")
    video_id_match = re.search(r"(?:v=)([0-9A-Za-z_-]{11})", youtube_url)
    if not video_id_match:
        logger.error("Invalid YouTube URL")
        raise ValueError("Invalid YouTube URL")
    return video_id_match.group(1)

# API endpoint to fetch transcript
@app.route('/fetch-transcript', methods=['POST'])
def fetch_transcript():
    try:
        logger.info("Received request to fetch transcript")
        data = request.get_json()
        youtube_url = data.get('url')
        if not youtube_url:
            logger.warning("No URL provided in request")
            return jsonify({"error": "No URL provided"}), 400
        video_id = get_video_id(youtube_url)
        logger.debug(f"Video ID: {video_id}")

        # Define proxy configuration
        proxies = {
            "http": "http://brd-customer-hl_dbf2a686-zone-residential_proxy1:kgvk3uownv4d@brd.superproxy.io:33335",
            "https": "http://brd-customer-hl_dbf2a686-zone-residential_proxy1:kgvk3uownv4d@brd.superproxy.io:33335"
        }
        logger.debug(f"Using proxies: {proxies}")

        # Fetch transcript using the proxy with custom session
        logger.info(f"Fetching transcript for video ID: {video_id}")
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'], proxies=proxies, http_client=session)
        transcript_text = " ".join([entry['text'] for entry in transcript])
        logger.info("Successfully fetched transcript")
        return jsonify({"transcript": transcript_text})
    except Exception as e:
        logger.error(f"Error fetching transcript: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))  # Use PORT environment variable, default to 5001
    logger.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port)