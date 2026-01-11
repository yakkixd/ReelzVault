from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__, static_folder=".", template_folder=".")
CORS(app)

# VERCEL FIX: Use /tmp directory for temporary storage
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
        reel_id = url.rstrip("/").split("/")[-1]
        file_id = reel_id
        output_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp4")

        # VERCEL FIX: Simplified yt-dlp options
        # Note: Large downloads might still time out on Vercel (10s limit)
        ydl_opts = {
            "outtmpl": output_path,
            "format": "mp4/best", # simplify format to avoid merging needs
            "quiet": True,
            "noplaylist": True,
            "cachedir": "/tmp", # Force cache to writable directory
            "source_address": "0.0.0.0" # Force IPv4 to avoid IPv6 issues on some serverless envs
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return jsonify({"download_url": f"/file/{file_id}"})

    except Exception as e:
        print(f"Error: {e}") # Log error for Vercel logs
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

# Vercel requires the 'app' object to be available. 
# app.run() is ignored by Vercel but useful for local testing.
if __name__ == "__main__":
    app.run(debug=True)
