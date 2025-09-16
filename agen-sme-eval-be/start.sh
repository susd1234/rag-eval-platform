#!/bin/bash

# AI SME Evaluation Platform Startup Script

echo "🚀 Starting AI SME Evaluation Platform..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp env.example .env
    echo "✏️  Please edit .env file with your API keys before running the service."
    echo "📝 Required: OPENAI_API_KEY or ANTHROPIC_API_KEY"
    read -p "Press Enter after updating .env file..."
fi

# Start the service
echo "🌟 Starting FastAPI service on port 9777..."
python app.py
