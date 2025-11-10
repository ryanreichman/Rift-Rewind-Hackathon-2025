#!/bin/bash

# Summoners Reunion - Startup Script
# This script starts both the backend and frontend servers

echo "🚀 Starting Summoners Reunion AI Chat Agent..."

# Start backend
echo "📡 Starting backend server..."
cd backend
source venv/bin/activate
python3 main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend server..."
cd ../frontend
python3 -m http.server 8080 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "✅ All servers started successfully!"
echo ""
echo "📊 Access the application:"
echo "   Frontend: http://localhost:8080"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Server logs:"
echo "   Backend: backend.log"
echo "   Frontend: frontend.log"
echo ""
echo "🛑 To stop the servers, run:"
echo "   pkill -f 'python3 main.py'"
echo "   pkill -f 'python3 -m http.server 8080'"
echo ""
