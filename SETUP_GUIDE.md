# OCI Generative AI Agents Chatbot - Setup Guide

This guide will help you set up and run the OCI Generative AI Agents chatbot with React frontend and Python backend.

## Prerequisites

### 1. OCI Account Setup
- Oracle Cloud Infrastructure account with Generative AI Agents service access
- Required permissions for OCI Generative AI Agents service
- Agent endpoint OCIDs (you'll get these from OCI Console)

### 2. Software Requirements
- **Python 3.10 or later**
- **Node.js 16 or later**
- **npm** (comes with Node.js)
- **Git** (for cloning the repository)

### 3. OCI Configuration
- OCI CLI configured with API key authentication
- OCI config file at `~/.oci/config`

## Quick Start

### Option 1: Automated Setup
```bash
# Run the complete setup script
./setup.sh
```

### Option 2: Manual Setup

#### Step 1: Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your OCI credentials
```

#### Step 2: Frontend Setup
```bash
cd frontend

# Install dependencies
npm install
```

## Configuration

### 1. OCI Agent Endpoints Setup

Before running the application, you need to create agent endpoints in OCI Console:

1. **Login to OCI Console**
   - Go to [OCI Console](https://cloud.oracle.com)
   - Navigate to "Generative AI Agents" service

2. **Create Search Agent**
   - Create a new agent instance
   - Name: "Search Agent"
   - Instructions: "You are a helpful search assistant for IT support and knowledge management"
   - Keep "Automatically create an endpoint" checked
   - Copy the agent endpoint OCID

3. **Create Ticket Agent**
   - Create another agent instance
   - Name: "Ticket Agent"
   - Instructions: "You are a specialized ticket creation and management assistant for ServiceNow"
   - Keep "Automatically create an endpoint" checked
   - Copy the agent endpoint OCID

### 2. Environment Configuration

Edit `backend/.env` file:

```env
# OCI Configuration
OCI_AUTH_TYPE=api_key
OCI_PROFILE=DEFAULT
OCI_REGION=us-chicago-1

# Agent Endpoint IDs (Get these from OCI Console)
SEARCH_AGENT_ENDPOINT_ID=ocid1.agentendpoint.oc1.xxxxx
TICKET_AGENT_ENDPOINT_ID=ocid1.agentendpoint.oc1.xxxxx

# ServiceNow Configuration (Optional)
SERVICENOW_INSTANCE=your-instance.service-now.com
SERVICENOW_USERNAME=your-username
SERVICENOW_PASSWORD=your-password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. OCI CLI Configuration

Ensure your OCI CLI is configured:

```bash
# Configure OCI CLI
oci setup config

# Test authentication
oci iam user get --user-id $(oci iam user list --query 'data[0].id' --raw-output)
```

## Running the Application

### Start Backend
```bash
./start_backend.sh
# OR
cd backend
source venv/bin/activate
python main.py
```

The backend will start on `http://localhost:8000`

### Start Frontend
```bash
./start_frontend.sh
# OR
cd frontend
npm start
```

The frontend will start on `http://localhost:3000`

## Features

### Search Agent
- **Knowledge Base Search**: Search through IT documentation and articles
- **ServiceNow Search**: Query incidents, changes, and service requests
- **Article Retrieval**: Get detailed content from specific articles

### Ticket Agent
- **Incident Creation**: Create incident tickets for IT issues
- **Change Requests**: Submit change requests for system modifications
- **Service Requests**: Create service requests for new services
- **Ticket Management**: Check status and update existing tickets

## API Endpoints

### Chat Endpoints
- `POST /chat` - Send message to selected agent
- `POST /search` - Search knowledge base or ServiceNow
- `GET /article/{article_id}` - Get article content

### Ticket Endpoints
- `POST /ticket/create` - Create new ticket
- `POST /ticket/status` - Check ticket status
- `POST /ticket/update` - Update ticket notes

### Utility Endpoints
- `GET /health` - Health check

## Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Check if backend is running on port 8000
   - Verify OCI credentials in `.env` file
   - Ensure agent endpoints are active in OCI Console

2. **Agent Initialization Failed**
   - Verify agent endpoint OCIDs are correct
   - Check OCI permissions for Generative AI Agents service
   - Ensure region supports Generative AI Agents service

3. **Frontend Build Errors**
   - Run `npm install` in frontend directory
   - Check Node.js version (16+ required)
   - Clear npm cache: `npm cache clean --force`

4. **CORS Errors**
   - Backend CORS is configured for localhost:3000
   - Check if frontend is running on correct port

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export DEBUG=1
python main.py
```

### Logs

Backend logs are displayed in the terminal. For production deployment, consider using proper logging configuration.

## Development

### Project Structure
```
OCIAgents-ServiceNow/
├── backend/                 # Python FastAPI backend
│   ├── agents/             # Agent implementations
│   ├── tools/              # Custom tools for agents
│   ├── config/             # Configuration files
│   └── main.py             # FastAPI application
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   └── context/        # React context
│   └── public/             # Static files
└── scripts/                # Startup scripts
```

### Adding New Tools

1. Create tool function in `backend/tools/`
2. Add `@tool` decorator
3. Import and add to agent tools list
4. Update agent instructions if needed

### Customizing UI

- Modify components in `frontend/src/components/`
- Update styles in corresponding `.css` files
- Add new features in `frontend/src/services/api.js`

## Production Deployment

### Backend Deployment
- Use production WSGI server (Gunicorn)
- Set up proper logging
- Configure environment variables
- Use reverse proxy (Nginx)

### Frontend Deployment
- Build production bundle: `npm run build`
- Serve static files with web server
- Configure API URL for production backend

## Support

For issues and questions:
1. Check this setup guide
2. Review OCI Generative AI Agents documentation
3. Check GitHub issues (if applicable)
4. Contact OCI support for service-related issues

## License

This project is provided as-is for demonstration purposes. Please review Oracle's terms of service for OCI Generative AI Agents.
