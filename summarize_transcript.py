import requests
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk

# Download NLTK data (required for sumy)
nltk.download('punkt')

# Fetch transcript from the API
def fetch_transcript(video_url, api_url="http://127.0.0.1:5001/fetch-transcript"):
    payload = {"url": video_url}
    headers = {"Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers)
    response.raise_for_status()  # Raise an error if the request fails
    return response.json().get("transcript")

# Summarize the transcript
def summarize_text(text, sentence_count=10):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return " ".join(str(sentence) for sentence in summary)

# Main function
def main():
    video_url = "https://www.youtube.com/watch?v=KjIHZqPi5M8&t=1s"  # Replace with your video URL
    api_url = "https://7b6e-2a02-c7c-f47f-3200-a4f2-b0e5-f998-71e9.ngrok-free.app/fetch-transcript"  # Your ngrok URL
    try:
        transcript = fetch_transcript(video_url, api_url)
        if not transcript:
            print("No transcript available.")
            return
        print("Original Transcript:")
        print(transcript)
        print("\nSummary:")
        summary = summarize_text(transcript, sentence_count=10)
        print(summary)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
