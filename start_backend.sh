#!/bin/bash

# OCI Agents Chatbot - Backend Startup Script

echo "🚀 Starting OCI Agents Chatbot Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or later."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $python_version is installed, but Python $required_version or later is required."
    exit 1
fi

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your OCI credentials and agent endpoint IDs"
    echo "   - OCI_AUTH_TYPE"
    echo "   - OCI_PROFILE" 
    echo "   - OCI_REGION"
    echo "   - SEARCH_AGENT_ENDPOINT_ID"
    echo "   - TICKET_AGENT_ENDPOINT_ID"
    echo ""
    echo "Press Enter to continue after updating .env file..."
    read
fi

# Start the backend server
echo "🌟 Starting FastAPI server..."
python main.py
