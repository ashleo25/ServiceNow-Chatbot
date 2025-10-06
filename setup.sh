#!/bin/bash

# OCI Agents Chatbot - Complete Setup Script

echo "🎯 Setting up OCI Agents Chatbot..."

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "📋 Prerequisites check..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or later."
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or later."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup backend
echo ""
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate and install dependencies
echo "📥 Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating environment configuration..."
    cp env.example .env
    echo "⚠️  Please edit backend/.env with your OCI credentials:"
    echo "   - OCI_AUTH_TYPE=api_key"
    echo "   - OCI_PROFILE=DEFAULT"
    echo "   - OCI_REGION=us-chicago-1"
    echo "   - SEARCH_AGENT_ENDPOINT_ID=your_search_agent_endpoint_id"
    echo "   - TICKET_AGENT_ENDPOINT_ID=your_ticket_agent_endpoint_id"
fi

cd ..

# Setup frontend
echo ""
echo "🔧 Setting up frontend..."
cd frontend

# Install dependencies
echo "📥 Installing Node.js dependencies..."
npm install

cd ..

echo ""
echo "🎉 Setup completed!"
echo ""
echo "📖 Next steps:"
echo "1. Edit backend/.env with your OCI credentials and agent endpoint IDs"
echo "2. Start the backend: ./start_backend.sh"
echo "3. Start the frontend: ./start_frontend.sh"
echo "4. Open http://localhost:3000 in your browser"
echo ""
echo "📚 For detailed setup instructions, see README.md"
