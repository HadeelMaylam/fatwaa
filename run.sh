#!/bin/bash
# Quick start script for Linux/Mac

echo "===================================="
echo "Starting Fatwa RAG System"
echo "===================================="

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "ERROR: Virtual environment not found!"
    echo "Please run: python -m venv venv"
    echo "Then run: pip install -r requirements.txt"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Start the server
echo ""
echo "Starting FastAPI server..."
echo "API will be available at: http://localhost:8000"
echo "Documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app/main.py
