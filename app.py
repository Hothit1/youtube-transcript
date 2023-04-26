from flask import Flask, render_template, request, redirect, url_for
import re
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

def extract_video_id_from_url(url):
    video_id_pattern = r"(?:https?:\/\/)?(?:www\.)?youtu(?:\.be\/|be\.com\/(?:watch\?v=|v\/|embed\/|playlist\?list=|user\/))([^\?&\"'>]+)"
    match = re.match(video_id_pattern, url)
    return match.group(1) if match else None

def get_transcript(video_id):
    languages = ['en', 'vi']
    for language in languages:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            return transcript, None
        except Exception as e:
            print(f"Error fetching transcript in {language}: {e}")

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript, None
    except Exception as e:
        print(f"Error fetching transcript in any available language: {e}")
        return None, str(e)

def format_transcript(transcript):
    return "\n".join([line['text'] for line in transcript])

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        video_id = extract_video_id_from_url(url)

        if not video_id:
            return "Invalid YouTube URL.", 400
        else:
            transcript, error = get_transcript(video_id)

            if transcript:
                formatted_transcript = format_transcript(transcript)
                return render_template("transcript.html", transcript=formatted_transcript)
            else:
                return f"Could not fetch transcript. Error: {error}", 400

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
