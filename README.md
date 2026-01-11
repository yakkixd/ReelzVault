# 🎥 InstaReelz 3D – Pro Edition

A **high‑fidelity, immersive Instagram Reel downloader interface** featuring a dynamic **3D particle background** and a clean, professional **glassmorphism UI**.

> ⚡ Built for style, performance, and a premium user experience.

---

## ✨ Features

### 🌌 Immersive 3D Background  
Interactive **Three.js** particle system with smooth mouse‑based parallax effects.

### 🎨 Modern UI/UX  
- Glassmorphism cards  
- Inter typography  
- Smooth transitions  
- "Pro" aesthetic  

### ⚙️ Reactive State Management  
- Visual loading indicators  
- Error handling with feedback  
- Success state with **Confetti animation**  

### 📱 Responsive Design  
Fully adaptive layout using **Tailwind CSS**.

---

## 🚀 Getting Started

### 1️⃣ Frontend Setup

The frontend is a **single self‑contained HTML file**.

**Steps:**  
1. Download `index.html`  
2. Open it in any modern web browser  

---

### 2️⃣ Backend Setup (Required)

The frontend sends requests to:

```
http://127.0.0.1:5000/download
```

You need a simple **Flask backend** to handle downloading.

#### 📦 Prerequisites

```
pip install flask flask-cors instaloader
```

#### 📄 Create `app.py`

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download_reel():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    print(f"Processing URL: {url}")
    time.sleep(2)
    
    return jsonify({
        'download_url': '/static/sample_video.mp4',
        'message': 'Success'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

#### ▶️ Run the Server

```
python app.py
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| HTML5 & CSS3 | Structure & styling |
| Tailwind CSS | UI & responsiveness |
| Three.js | 3D particle background |
| Lucide Icons | Icons |
| JavaScript (ES6+) | Logic |
| Flask | Backend |
| Flask‑CORS | Cross‑origin support |

---

## ⚠️ Disclaimer

This project is for **educational purposes only**.  
Downloading Instagram content may violate their **Terms of Service**.  
Please respect copyright laws and creators’ rights.

---

## 📄 License

**MIT License**  
Free to use, modify, and distribute.

---

## ⭐ Extra

If you liked this project, consider giving it a star and building your own **Pro‑style web tools** 🚀
