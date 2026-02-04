from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import yt_dlp
import os
import time

app = Flask(__name__, static_folder=".", template_folder=".")
CORS(app)

# VERCEL FIX: Use /tmp directory for temporary storage
DOWNLOAD_FOLDER = "/tmp"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download_media():
    data = request.json
    url = data.get("url")
    download_type = data.get("type", "video") 

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        file_id = str(int(time.time()))
        ext = "mp4" if download_type == "video" else "m4a"
        output_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.{ext}")

        ydl_opts = {
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, f"{file_id}.%(ext)s"),
            "quiet": True,
            "noplaylist": True,
            "cachedir": "/tmp", 
            "source_address": "0.0.0.0",
            # User-Agent to look like a real browser
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            },
            "extractor_args": {
                "instagram": {
                    "imp_user_agent": ["ios"]
                },
                "youtube": {
                    "skip": ["dash", "hls"] # Skip streaming formats that require ffmpeg merging
                }
            }
        }

        # Check for cookies.txt
        if os.path.exists("cookies.txt"):
            ydl_opts["cookiefile"] = "cookies.txt"

        if download_type == "audio":
            # Best audio (m4a/webm)
            ydl_opts["format"] = "bestaudio/best"
        else:
            # CRITICAL FOR YOUTUBE ON VERCEL:
            # We ask for 'best[ext=mp4]' which looks for the best *single file* (video+audio) in mp4.
            # If we just asked for 'bestvideo', it might give us a video-only stream that needs ffmpeg to merge.
            ydl_opts["format"] = "best[ext=mp4]/best"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            actual_ext = info.get('ext', ext)
            file_id = f"{file_id}.{actual_ext}"

        return jsonify({"download_url": f"/file/{file_id}"})

    except Exception as e:
        print(f"Error: {e}") 
        return jsonify({"error": str(e)}), 500

@app.route("/file/<filename>")
def serve_file(filename):
    try:
        path = os.path.join(DOWNLOAD_FOLDER, filename)
        if not os.path.exists(path):
             return jsonify({"error": "File not found or expired"}), 404
        return send_file(path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
