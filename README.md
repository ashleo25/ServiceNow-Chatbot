# ServiceNow Chatbot

A complete, runnable LLM-powered ServiceNow chatbot with modern React frontend and Python backend.

## Features

The chatbot provides intelligent ServiceNow ticket management with the following capabilities:

- ✅ **Duplicate ticket detection** - Checks for existing tickets by the same user
- ✅ **Similar ticket search** - Finds related tickets across all users and shows resolutions
- ✅ **Ticket linking** - Links users to existing tickets when appropriate
- ✅ **New incident creation** - Creates new tickets when no similar issues exist
- ✅ **Chat history** - Persistent conversation history with sidebar navigation
- ✅ **Modern UI** - Clean, responsive React interface with TypeScript

![ServiceNow Chatbot Demo](https://github.com/user-attachments/assets/0064ea20-cab7-4f56-97cc-81d5030425ca)

## Architecture

### Backend (Python + FastAPI-compatible)
- **File**: `backend/simple_server.py`
- **Technology**: Python 3.11+ with built-in HTTP server (no external dependencies)
- **Features**:
  - RESTful API for chat messaging
  - Intelligent ticket analysis using similarity scoring
  - Mock ServiceNow ticket database
  - CORS-enabled for frontend integration

### Frontend (React + TypeScript + Vite)
- **Directory**: `frontend/`
- **Technology**: React 18, TypeScript, Vite, Custom CSS (Tailwind-style utilities)
- **Features**:
  - Modern chat interface with message bubbles
  - Real-time chat history sidebar
  - Responsive design
  - Type-safe API integration

## Quick Start

### Backend
```bash
cd backend
python3 simple_server.py
# Server runs on http://localhost:8001
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:5173
```

## API Endpoints

- `GET /` - Health check
- `POST /chat/message` - Send chat message
- `GET /chat/history/{user_id}` - Get chat history
- `POST /tickets/search` - Search similar tickets
- `POST /tickets/create` - Create new incident
- `GET /tickets/user/{user_id}` - Get user tickets

## Demo Scenarios

The chatbot demonstrates all required functionality:

1. **Email Issue** → Finds duplicate resolved ticket (INC0001001)
2. **VPN Problem** → Shows resolution from similar ticket (INC0001002)
3. **Slow Computer** → Links to existing open ticket (INC0001003)
4. **New Issues** → Offers to create new incidents

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI version (requires pip install)
│   ├── simple_server.py     # Standalone version (no dependencies)
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── api.ts          # API client
│   │   ├── App.tsx         # Main app component
│   │   └── index.css       # Custom CSS utilities
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Vite configuration
└── README.md               # This file
```

The implementation provides a solid foundation for a production ServiceNow chatbot with all the requested features working end-to-end.
