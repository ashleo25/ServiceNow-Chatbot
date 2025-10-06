# OCI Generative AI Agents - ServiceNow Chatbot

A React-based chatbot integrated with Oracle Cloud Infrastructure (OCI) Generative AI Agents using the ADK toolkit. This project includes Search Agent and Ticket Creation Agent capabilities.

## Project Structure

```
OCIAgents-ServiceNow/
├── backend/                 # Python backend with OCI ADK
│   ├── agents/             # Agent implementations
│   ├── tools/              # Custom tools for agents
│   ├── config/             # Configuration files
│   └── requirements.txt    # Python dependencies
├── frontend/               # React chatbot frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   └── styles/         # CSS styles
│   └── package.json        # Node.js dependencies
├── config/                 # Shared configuration
└── README.md              # This file
```

## Features

- **Search Agent**: Intelligent search capabilities using OCI Generative AI
- **Ticket Creation Agent**: Automated ticket creation and management
- **Modern React UI**: Clean, responsive chatbot interface
- **OCI ADK Integration**: Full integration with Oracle Cloud Infrastructure
- **Real-time Communication**: WebSocket support for real-time chat

## Prerequisites

- Python 3.10 or later
- Node.js 16 or later
- OCI account with Generative AI Agents service access
- Agent endpoint OCID from OCI Console

## Quick Start

1. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Configuration**:
   - Update `backend/config/config.py` with your OCI credentials
   - Set your agent endpoint OCID in the configuration

## Documentation

For detailed OCI ADK documentation, visit: https://docs.oracle.com/en-us/iaas/Content/generative-ai-agents/adk/api-reference/quickstart.htm
