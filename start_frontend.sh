#!/bin/bash

# OCI Agents Chatbot - Frontend Startup Script

echo "🚀 Starting OCI Agents Chatbot Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or later."
    exit 1
fi

# Check Node.js version
node_version=$(node -v | cut -d'v' -f2)
required_version="16.0.0"

if [ "$(printf '%s\n' "$required_version" "$node_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Node.js $node_version is installed, but Node.js $required_version or later is required."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if backend is running
echo "🔍 Checking backend connection..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running"
else
    echo "⚠️  Backend is not running. Please start the backend first:"
    echo "   ./start_backend.sh"
    echo ""
    echo "Press Enter to continue anyway..."
    read
fi

# Start the React development server
echo "🌟 Starting React development server..."
npm start
