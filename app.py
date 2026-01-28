from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import yt_dlp
import os
import time
import base64

app = Flask(__name__, static_folder=".", template_folder=".")
CORS(app)

# Vercel writable directory
DOWNLOAD_FOLDER = "/tmp"
INSTAGRAM_COOKIES_PATH = "/tmp/instagram_cookies.txt"


def ensure_cookies_file():
    """
    Writes Base64-decoded Instagram cookies from env to /tmp
    """
    cookies_b64 = os.getenv("INSTAGRAM_COOKIES_B64")
    if not cookies_b64:
        raise RuntimeError("Instagram cookies not found in environment variables")

    # Always rewrite (safe + simple for serverless)
    data = base64.b64decode(cookies_b64)

    with open(INSTAGRAM_COOKIES_PATH, "wb") as f:
        f.write(data)


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
        # 🔥 Ensure Instagram cookies exist
        ensure_cookies_file()

        file_id = str(int(time.time()))

        ydl_opts = {
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, f"{file_id}.%(ext)s"),
            "quiet": True,
            "noplaylist": True,
            "cachedir": "/tmp",

            # ✅ COOKIE FIX
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


# 🔍 Optional debug (remove after testing)
@app.route("/debug/env")
def debug_env():
    val = os.getenv("INSTAGRAM_COOKIES_B64")
    return jsonify({
        "exists": bool(val),
        "length": len(val) if val else 0
    })


if __name__ == "__main__":
    app.run(debug=True, port=5001)
