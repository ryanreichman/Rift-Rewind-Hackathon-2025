# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Configure AWS Credentials

```bash
cp .env.example .env
nano .env  # Add your AWS credentials
```

### Step 2: Start Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend runs on: **http://localhost:8000**

### Step 3: Start Frontend

Open a new terminal:

```bash
cd frontend
python -m http.server 8080
```

Frontend runs on: **http://localhost:8080**

### Step 4: Open Browser

Navigate to **http://localhost:8080** and start chatting!

## 🎯 Minimum Requirements

- Python 3.9+
- AWS Account with Bedrock access
- Claude 3.5 Sonnet enabled in AWS Bedrock
- AWS Access Key & Secret Key

## ✅ Verify Setup

1. Backend health check: http://localhost:8000/api/health
2. API docs: http://localhost:8000/docs
3. Frontend: http://localhost:8080

## 🎨 What You'll See

- **Dark futuristic interface** with neon cyan, purple, and blue accents
- **Animated particles** floating in the background
- **Real-time streaming** responses from Claude
- **Glitch effects** on the logo
- **Smooth animations** for messages

## 🔧 Common Issues

**"Backend offline"** → Check if backend is running on port 8000

**"Import errors"** → Activate virtual environment and reinstall dependencies

**"AWS errors"** → Verify credentials and Bedrock model access

---

Need more details? See the full [README.md](README.md)
