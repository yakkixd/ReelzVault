from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import yt_dlp
import os
import time
import base64

app = Flask(__name__, static_folder=".", template_folder=".")
CORS(app)

DOWNLOAD_FOLDER = "/tmp"
COOKIES_PATH = "/tmp/cookies.txt"


def ensure_cookies_file():
    cookies_b64 = os.getenv("COOKIES_B64")
    if not cookies_b64:
        raise RuntimeError("Cookies not found in environment variables")

    with open(COOKIES_PATH, "wb") as f:
        f.write(base64.b64decode(cookies_b64))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download_media():
    data = request.json or {}
    url = data.get("url")
    download_type = data.get("type", "video")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        ensure_cookies_file()

        file_id = str(int(time.time()))

        ydl_opts = {
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, f"{file_id}.%(ext)s"),
            "quiet": True,
            "noplaylist": True,
            "cachedir": "/tmp",
            "cookiefile": COOKIES_PATH,
            "source_address": "0.0.0.0",
            "extractor_retries": 3,
            "fragment_retries": 3,
            "skip_unavailable_fragments": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
            }
        }

        if download_type == "audio":
            ydl_opts["format"] = "bestaudio/best"
        else:
            ydl_opts["format"] = "best[ext=mp4]/best"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = info.get("ext", "mp4")
            filename = f"{file_id}.{ext}"

        return jsonify({"download_url": f"/file/{filename}"})

    except Exception as e:
        print("Download error:", e)
        return jsonify({"error": "Download failed"}), 500


@app.route("/file/<filename>")
def serve_file(filename):
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    if not os.path.exists(path):
        return jsonify({"error": "File not found or expired"}), 404
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
