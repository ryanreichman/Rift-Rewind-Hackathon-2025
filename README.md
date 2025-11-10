# Summoners Reunion - AI Chat Agent

A futuristic AI chat application powered by **AWS Bedrock** and **Claude 3.5 Sonnet**. Features real-time streaming responses with a stunning gamer-themed interface.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)
![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-FF9900.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🤖 **AI-Powered Chat** - Intelligent conversations using Claude 3.5 Sonnet via AWS Bedrock
- ⚡ **Real-time Streaming** - Server-Sent Events (SSE) for live response streaming
- 🎮 **Gamer Aesthetic** - Dark theme with neon accents and futuristic animations
- 🔒 **Secure** - AWS credentials management with environment variables
- 📱 **Responsive** - Works seamlessly on desktop and mobile devices
- 🎨 **Visual Effects** - Particle systems, glitch effects, and smooth animations

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │   HTTP  │   Backend    │  Boto3  │ AWS Bedrock │
│  (Vanilla   │◄───────►│   (FastAPI)  │◄───────►│   (Claude)  │
│     JS)     │   SSE   │              │         │             │
└─────────────┘         └──────────────┘         └─────────────┘
```

## 📁 Project Structure

```
summoners-reunion/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── bedrock_agent.py      # AWS Bedrock integration with boto3
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py            # Configuration management
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py             # Pydantic models
│   ├── __init__.py
│   ├── main.py                    # FastAPI server
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── css/
│   │   └── styles.css             # Futuristic gamer theme
│   ├── js/
│   │   ├── chat.js                # Chat logic & SSE handling
│   │   └── ui.js                  # Animations & visual effects
│   └── index.html                 # Main chat interface
├── .env.example                   # Environment variables template
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- AWS Account with Bedrock access
- AWS credentials (Access Key ID & Secret Access Key)
- Claude 3.5 Sonnet model enabled in AWS Bedrock

### 1. Clone the Repository

```bash
cd summoners-reunion
```

### 2. Set Up AWS Bedrock

#### Enable Claude Model in AWS Console

1. Navigate to **AWS Bedrock Console**
2. Go to **Model Access** in the left sidebar
3. Request access to **Anthropic Claude 3.5 Sonnet**
4. Wait for approval (usually instant for most accounts)

#### Create IAM User with Bedrock Permissions

1. Go to **IAM Console** → **Users** → **Create User**
2. Attach the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

3. Create **Access Key** and save the credentials

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your AWS credentials
nano .env  # or use your preferred editor
```

Update the `.env` file:

```env
AWS_ACCESS_KEY_ID=your_actual_access_key_here
AWS_SECRET_ACCESS_KEY=your_actual_secret_key_here
AWS_REGION=us-east-1

BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

### 4. Set Up Python Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Run the Backend Server

```bash
# From the backend directory
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start on `http://localhost:8000`

### 6. Run the Frontend

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Start a simple HTTP server
# Python 3:
python -m http.server 8080

# Or use any other static file server
# Node.js (if you have it installed):
# npx http-server -p 8080
```

The frontend will be available at `http://localhost:8080`

### 7. Open the Application

Navigate to `http://localhost:8080` in your web browser and start chatting!

## 🎨 Design Features

### Color Palette

- **Background**: Deep blacks (#0a0a0f, #14141f)
- **Accents**:
  - Neon Cyan (#00fff5)
  - Electric Purple (#b24bf3)
  - Bright Blue (#4d7cfe)
  - Hot Pink (#ff2e97)

### Visual Effects

- **Particle System** - Floating particles in the background
- **Scanlines** - Retro CRT monitor effect
- **Glitch Effects** - Text glitch animations
- **Glow Effects** - Neon glow on interactive elements
- **Smooth Animations** - Message slide-ins and transitions

## 🔧 Configuration

### Backend Configuration

Edit `backend/config/settings.py` to customize:

- **Model Parameters**: `max_tokens`, `temperature`, `top_p`
- **CORS Origins**: Allowed frontend domains
- **Conversation History**: Maximum messages to keep

### Frontend Configuration

Edit `frontend/js/chat.js` to customize:

- **API Base URL**: Backend server location
- **Health Check Interval**: Status check frequency
- **Reconnect Delay**: Retry timing for failed connections

## 📊 API Endpoints

### Health Check

```http
GET /api/health
```

**Response:**
```json
{
    "status": "healthy",
    "app_name": "Summoners Reunion AI Agent",
    "timestamp": "2025-01-15T10:30:00",
    "bedrock_configured": true
}
```

### Chat (Streaming)

```http
POST /api/chat/stream
Content-Type: application/json

{
    "message": "Hello!",
    "conversation_history": []
}
```

**Response:** Server-Sent Events (SSE) stream

### Chat (Non-streaming)

```http
POST /api/chat
Content-Type: application/json

{
    "message": "Hello!",
    "conversation_history": []
}
```

**Response:**
```json
{
    "message": "Hello! How can I help you?",
    "role": "assistant",
    "timestamp": "2025-01-15T10:30:00",
    "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0"
}
```

## 🐛 Troubleshooting

### Backend Issues

**Error: "Bedrock agent not initialized"**
- Check AWS credentials in `.env` file
- Verify IAM user has Bedrock permissions
- Ensure Claude model access is enabled in AWS Console

**Error: "Region not available"**
- Claude may not be available in your selected region
- Try `us-east-1` or `us-west-2`

**Import errors**
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend Issues

**"Backend is offline" message**
- Verify backend is running on port 8000
- Check `apiBaseUrl` in `frontend/js/chat.js`
- Check CORS settings in `backend/config/settings.py`

**Messages not streaming**
- Check browser console for errors
- Verify EventSource API is supported in your browser
- Check network tab for SSE connection

## 🔐 Security Best Practices

1. **Never commit `.env` file** to version control
2. **Rotate AWS credentials** regularly
3. **Use IAM roles** instead of access keys in production
4. **Enable CloudWatch logging** for monitoring
5. **Implement rate limiting** for production use
6. **Use HTTPS** in production environments

## 🚀 Deployment

### Backend Deployment (AWS Lambda + API Gateway)

1. Package the backend application
2. Create Lambda function with Python 3.9+ runtime
3. Set environment variables in Lambda
4. Create API Gateway REST API
5. Configure CORS and routes

### Frontend Deployment (AWS S3 + CloudFront)

1. Build frontend assets
2. Create S3 bucket with static website hosting
3. Upload files to S3
4. Create CloudFront distribution
5. Update `apiBaseUrl` to point to backend API

### Alternative: Docker Deployment

```dockerfile
# Dockerfile example for backend
FROM python:3.9-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **AWS Bedrock** - For providing Claude model access
- **Anthropic** - For developing Claude
- **FastAPI** - For the excellent Python web framework
- **boto3** - For AWS SDK integration

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check AWS Bedrock documentation
- Review FastAPI documentation

---

**Built with ❤️ for gamers and AI enthusiasts**
