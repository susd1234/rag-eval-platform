#!/bin/bash

# AI SME Evaluation Platform - Full Stack Launch Script
# This script starts both the FastAPI backend and React frontend

echo "🚀 Starting AI SME Evaluation Platform - Full Stack"
echo "=================================================="

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if backend port is available
if check_port 9777; then
    echo "⚠️  Port 9777 is already in use. Backend may already be running."
else
    echo "✅ Port 9777 is available for backend"
fi

# Check if frontend port is available
if check_port 3000; then
    echo "⚠️  Port 3000 is already in use. Frontend may already be running."
else
    echo "✅ Port 3000 is available for frontend"
fi

echo ""
echo "🔧 Starting Backend (FastAPI)..."
echo "   Backend will be available at: http://localhost:9777"
echo "   API Documentation: http://localhost:9777/docs"
echo ""

# Start backend in background
cd agen-sme-eval-be
if [ ! -d "venv" ]; then
    echo "📦 Setting up Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Start backend
python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

echo ""
echo "🎨 Starting Frontend (React)..."
echo "   Frontend will be available at: http://localhost:3000"
echo ""

# Start frontend in background
cd ../agen-sme-eval-ui-react
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "🎉 Full Stack Application Started!"
echo "=================================="
echo "   Backend API: http://localhost:9777"
echo "   Frontend UI: http://localhost:3000"
echo "   API Docs: http://localhost:9777/docs"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
