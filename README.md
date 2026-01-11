# 🎥 InstaReelz 3D – Pro Edition

A **professional Instagram Reel downloader** with a stunning **3D particle background** and a clean, modern **glassmorphism UI**.

> Sleek. Fast. Stylish.

---

## ✨ Features

### 🌌 3D Background  
A dynamic particle background that reacts to mouse movement for a premium feel.

### 🎨 Modern Design  
- Glass-style card UI  
- Smooth typography  
- Clean "Pro" aesthetic  

### ⚙️ Interactive Features  
- Loading spinner while processing  
- Error messages for failed downloads  
- Confetti animation on success  

### 📱 Mobile Friendly  
Works perfectly on both **mobile** and **desktop** devices.

---

## 🚀 How to Run It

### 1️⃣ Setup Files

1. Create a new project folder  
2. Put `index.html` inside it  
3. Create a file named `app.py` in the same folder  

---

### 2️⃣ Setup Backend (Server)

You need Python to make the download button work.

#### 📦 Requirements

- Python 3.x  
- Install required libraries:

```bash
pip install flask flask-cors yt-dlp
```

---

### 📄 Paste This Into `app.py`

```python
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import yt_dlp
import os

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
    output_path = os.path.join(DOWNLOAD_FOLDER, f"{reel_id}.mp4")

    ydl_opts = {
        "outtmpl": output_path,
        "format": "mp4",
        "quiet": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return jsonify({"download_url": f"/file/{reel_id}"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/file/<file_id>")
def serve_file(file_id):
    path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp4")
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
```

---

### ▶️ Start the App

1. Open Terminal / Command Prompt  
2. Go to your project folder  
3. Run:

```bash
python app.py
```

4. Open your browser and visit:

```
http://127.0.0.1:5000
```

---

## 🛠️ Tools Used

| Tool | Purpose |
|------|---------|
| HTML & CSS | Website structure |
| Tailwind CSS | Styling |
| Three.js | 3D effects |
| Flask | Backend server |
| yt-dlp | Video downloading |

---

## ⚠️ Note

This project is for **learning purposes only**.  
Please respect content creators and platform rules.

---

## 📄 License

**MIT License** – Free to use for your own projects.

---

## ⭐ Bonus

Customize it, add new features, and build your own **Pro tools** 🚀
