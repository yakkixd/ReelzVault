from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import yt_dlp
import os
import time

app = Flask(__name__, static_folder=".", template_folder=".")
CORS(app)

# VERCEL FIX: Use /tmp directory for temporary storage (Vercel is read-only elsewhere)
DOWNLOAD_FOLDER = "/tmp"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download_reel():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Generate a safe filename
        reel_id = url.rstrip("/").split("/")[-1]
        # Fallback if ID extraction fails
        if not reel_id: 
            reel_id = str(int(time.time()))
            
        file_id = reel_id
        output_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp4")

        # Config specifically tuned for Serverless environments
        ydl_opts = {
            "outtmpl": output_path,
            "format": "mp4/best", 
            "quiet": True,
            "noplaylist": True,
            "cachedir": "/tmp", # Force cache to writable directory
            "source_address": "0.0.0.0" # Avoid IPv6 issues
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return jsonify({"download_url": f"/file/{file_id}"})

    except Exception as e:
        print(f"Error: {e}") 
        return jsonify({"error": str(e)}), 500

@app.route("/file/<file_id>")
def serve_file(file_id):
    try:
        path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp4")
        if not os.path.exists(path):
             return jsonify({"error": "File not found or expired"}), 404
        return send_file(path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Mac Users: Port 5000 is often blocked by AirPlay. We use 5001 locally.
    app.run(debug=True, port=5001)
