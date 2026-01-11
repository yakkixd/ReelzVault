from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__, static_folder=".", template_folder=".")
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download_reel():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    reel_id = url.rstrip("/").split("/")[-1]
    file_id = reel_id

    output_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp4")

    ydl_opts = {
        "outtmpl": output_path,
        "format": "mp4",
        "quiet": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return jsonify({"download_url": f"/file/{file_id}"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/file/<file_id>")
def serve_file(file_id):
    path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp4")
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
