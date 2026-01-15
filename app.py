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
    # Get the download type (video or audio), default to video
    download_type = data.get("type", "video") 

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Generate a unique filename based on time to avoid collisions
        file_id = str(int(time.time()))
        
        # Determine extension based on type
        ext = "mp4" if download_type == "video" else "m4a"
        output_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.{ext}")

        # Config specifically tuned for Serverless environments
        ydl_opts = {
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, f"{file_id}.%(ext)s"),
            "quiet": True,
            "noplaylist": True,
            "cachedir": "/tmp", 
            "source_address": "0.0.0.0",
            # FIX FOR INSTAGRAM ERROR: Add a real User-Agent to look like a browser
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5"
            }
        }

        if download_type == "audio":
            # Best audio, usually m4a or webm. 
            # We avoid 'mp3' conversion because Vercel doesn't have FFmpeg installed.
            ydl_opts["format"] = "bestaudio/best"
        else:
            # Best video that is compatible (mp4)
            ydl_opts["format"] = "mp4/best"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Update file_id with the actual extension yt-dlp chose if it changed
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
