#!/bin/bash

# Tello AI Web Interface - Setup Script
# This script installs all dependencies for the project

set -e  # Exit on error

echo "=========================================="
echo "Tello AI Web Interface - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python --version || {
    echo "Error: Python is not installed. Please install Python 3.10 or higher."
    exit 1
}
echo ""

# Backend setup
echo "=========================================="
echo "Setting up Backend..."
echo "=========================================="

cd backend

echo "Creating virtual environment..."
python -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Backend setup complete!"
echo ""

# Return to project root
cd ..

# Frontend setup
echo "=========================================="
echo "Setting up Frontend..."
echo "=========================================="

cd frontend

echo "Installing Node.js dependencies..."
npm install

echo "Frontend setup complete!"
echo ""

# Return to project root
cd ..

# Create .env file template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "=========================================="
    echo "Creating .env file template..."
    echo "=========================================="
    cat > .env << EOF
# Google Gemini API Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite
EOF
    echo ".env file created. Please edit it with your actual API key."
    echo ""
fi

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Google Gemini API key"
echo "2. Start the backend:"
echo "   cd backend && source venv/bin/activate && cd .."
echo "   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "4. Open your browser to http://localhost:5173"
echo ""
echo "For testing without a real drone, use execution_mode: 'mock'"
echo "=========================================="
