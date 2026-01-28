from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import yt_dlp
import os
import time

app = Flask(__name__, static_folder=".", template_folder=".")
CORS(app)

# Vercel uses /tmp for writable storage
DOWNLOAD_FOLDER = "/tmp"
INSTAGRAM_COOKIES_PATH = "/tmp/instagram_cookies.txt"


def ensure_cookies_file():
    """
    Writes Instagram cookies from Vercel env variable to /tmp
    """
    cookies = os.getenv("INSTAGRAM_COOKIES")
    if not cookies:
        raise RuntimeError("Instagram cookies not found in environment variables")

    if not os.path.exists(INSTAGRAM_COOKIES_PATH):
        with open(INSTAGRAM_COOKIES_PATH, "w", encoding="utf-8") as f:
            f.write(cookies)


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
        # Ensure cookies exist (Instagram fix)
        ensure_cookies_file()

        file_id = str(int(time.time()))

        ydl_opts = {
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, f"{file_id}.%(ext)s"),
            "quiet": True,
            "noplaylist": True,
            "cachedir": "/tmp",

            # 🔥 COOKIE FIX
            "cookiefile": INSTAGRAM_COOKIES_PATH,

            # Stability for serverless
            "source_address": "0.0.0.0",
            "extractor_retries": 3,
            "fragment_retries": 3,
            "skip_unavailable_fragments": True,
        }

        if download_type == "audio":
            ydl_opts["format"] = "bestaudio/best"
        else:
            ydl_opts["format"] = "mp4/best"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = info.get("ext", "mp4")
            filename = f"{file_id}.{ext}"

        return jsonify({"download_url": f"/file/{filename}"})

    except Exception as e:
        print("Download error:", e)
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
