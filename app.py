from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import yt_dlp
import os
import time
import base64

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__, static_folder=".", template_folder=".")

# 🔐 Lock CORS to your frontend only
CORS(app, origins=[
    "https://your-site.vercel.app"  # ← CHANGE THIS
])

# 🔒 Rate limiter (serverless-safe)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"]
)

# Vercel writable directory
DOWNLOAD_FOLDER = "/tmp"
INSTAGRAM_COOKIES_PATH = "/tmp/instagram_cookies.txt"

# Limit payload size (anti-abuse)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB


# 🔑 API KEY CHECK
def require_api_key(req):
    api_key = req.headers.get("X-API-Key")
    return api_key and api_key == os.getenv("API_KEY")


def ensure_cookies_file():
    """
    Writes Base64-decoded Instagram cookies from env to /tmp
    """
    cookies_b64 = os.getenv("INSTAGRAM_COOKIES_B64")
    if not cookies_b64:
        raise RuntimeError("Instagram cookies not found in environment variables")

    data = base64.b64decode(cookies_b64)
    with open(INSTAGRAM_COOKIES_PATH, "wb") as f:
        f.write(data)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
@limiter.limit("5 per minute")  # 🚦 per-IP rate limit
def download_media():

    # 🔐 API key protection
    if not require_api_key(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json or {}
    url = data.get("url")
    download_type = data.get("type", "video")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # 🔎 Allow only Instagram
    if "instagram.com" not in url:
        return jsonify({"error": "Only Instagram URLs are allowed"}), 400

    try:
        # Soft delay (anti-detection)
        time.sleep(2)

        ensure_cookies_file()

        file_id = str(int(time.time()))

        ydl_opts = {
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, f"{file_id}.%(ext)s"),
            "quiet": True,
            "noplaylist": True,
            "cachedir": "/tmp",
            "cookiefile": INSTAGRAM_COOKIES_PATH,

            # Serverless stability
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
        return jsonify({"error": "Download failed"}), 500


@app.route("/file/<filename>")
@limiter.limit("20 per hour")
def serve_file(filename):
    try:
        path = os.path.join(DOWNLOAD_FOLDER, filename)
        if not os.path.exists(path):
            return jsonify({"error": "File not found or expired"}), 404
        return send_file(path, as_attachment=True)
    except Exception:
        return jsonify({"error": "File error"}), 500


# 🔍 TEMP DEBUG (REMOVE AFTER CONFIRMING)
@app.route("/debug/env")
def debug_env():
    val = os.getenv("INSTAGRAM_COOKIES_B64")
    return jsonify({
        "exists": bool(val),
        "length": len(val) if val else 0
    })


if __name__ == "__main__":
    app.run(debug=True, port=5001)
