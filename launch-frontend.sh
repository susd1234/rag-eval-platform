#!/bin/bash

# AI SME Evaluation Platform - Frontend Launch Script
# This script starts the React frontend for the AI SME Evaluation Platform

echo "🚀 Starting AI SME Evaluation Platform - React Frontend"
echo "=================================================="

# Check if we're in the right directory
if [ ! -d "agen-sme-eval-ui-react" ]; then
    echo "❌ Error: agen-sme-eval-ui-react directory not found!"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Navigate to the React frontend directory
cd agen-sme-eval-ui-react

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if backend is running
echo "🔍 Checking backend status..."
if curl -s http://localhost:9777/evaluation/system/health > /dev/null; then
    echo "✅ Backend is running on port 9777"
else
    echo "⚠️  Warning: Backend not detected on port 9777"
    echo "   Please start the backend first using: ./launch.sh"
    echo "   The frontend will still start but API calls will fail."
fi

echo ""
echo "🎨 Starting React development server..."
echo "   Frontend will be available at: http://localhost:3000"
echo "   Backend API: http://localhost:9777"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the React development server
npm start
