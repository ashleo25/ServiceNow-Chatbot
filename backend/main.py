"""
ServiceNow Enterprise Chatbot - FastAPI Backend Server

This module provides the main FastAPI application server for the ServiceNow 
Enterprise Chatbot. It integrates Oracle Cloud Infrastructure (OCI) Generative AI, 
Google ADK, and ServiceNow APIs to provide intelligent ticket creation and 
knowledge search capabilities.

Features:
    - RESTful API endpoints for chat interactions
    - OCI Generative AI integration for knowledge search
    - Google ADK powered ticket creation with duplicate prevention
    - ServiceNow REST API integration for ticket management
    - Hybrid chatbot service with intent detection
    - Comprehensive health monitoring and debugging endpoints

Architecture:
    - FastAPI with async/await support for high performance
    - Modular agent-based architecture for scalability
    - CORS middleware for frontend integration
    - Pydantic models for type safety and validation
    - Global agent initialization with proper lifecycle management

Version: 1.0.0
"""

# Standard library imports
import uvicorn
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, Dict, Any

# Third-party imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Local imports
from config.config import Config
from oci.addons.adk import AgentClient
from agents.oci_compliant_core_search_agent import OciCompliantCoreSearchAgent
from agents.ticket_agent import TicketAgent
from agents.ticket_creation_agent import TicketCreationAgent
from services.hybrid_chatbot_service import HybridChatbotService


# Global agent instances
# These are initialized during application startup and shared across requests
search_agent: Optional[OciCompliantCoreSearchAgent] = None
ticket_agent: Optional[TicketAgent] = None
ticket_creation_agent: Optional[TicketCreationAgent] = None
chatbot_service: Optional[HybridChatbotService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for FastAPI.
    
    Handles initialization and cleanup of AI agents and services during
    application startup and shutdown. This ensures all dependencies are
    properly configured before handling requests.
    
    Args:
        app (FastAPI): The FastAPI application instance
        
    Yields:
        None: Control is yielded to the application during its lifetime
        
    Raises:
        Exception: If agent initialization fails during startup
        
    Note:
        - Validates configuration before initializing agents
        - Creates OCI client with authentication
        - Initializes search, ticket, and chatbot services
        - Provides graceful shutdown cleanup
    """
    # Global agent references
    global search_agent, ticket_agent, ticket_creation_agent, chatbot_service
    
    try:
        # Validate configuration before proceeding
        Config.validate_config()
        print("✅ Configuration validated successfully")
        
        # Create OCI client with authentication
        client = AgentClient(
            auth_type=Config.AUTH_TYPE,
            profile=Config.PROFILE,
            region=Config.REGION
        )
        print("✅ OCI Agent Client initialized")
        
        # Initialize core agents
        search_agent = OciCompliantCoreSearchAgent(client)
        ticket_agent = TicketAgent(client)
        ticket_creation_agent = TicketCreationAgent()
        
        # Initialize hybrid chatbot service
        chatbot_service = HybridChatbotService(
            search_agent=search_agent,
            ticket_agent=ticket_agent,
            ticket_creation_agent=ticket_creation_agent
        )
        
        # Log successful initialization
        print("✅ Search Agent initialized successfully")
        print("✅ Ticket Agent initialized successfully")
        print("✅ Ticket Creation Agent initialized successfully")
        print("✅ Chatbot Service initialized successfully")
        print("🚀 Application ready to serve requests")
        
    except Exception as e:
        print(f"❌ Failed to initialize agents: {str(e)}")
        raise e
    
    # Yield control to the application
    yield
    
    # Cleanup on shutdown
    print("🔄 Shutting down agents and services...")
    # Additional cleanup logic can be added here if needed


# Create FastAPI app with comprehensive metadata
app = FastAPI(
    title="ServiceNow Enterprise Chatbot API",
    description="RESTful API for ServiceNow chatbot with OCI AI integration",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================= PYDANTIC MODELS =========================

class ChatMessage(BaseModel):
    """
    Standard chat message model for basic interactions.
    
    Attributes:
        message (str): The user's chat message content
        agent_type (str): Type of agent to handle the request 
                         ("search" or "ticket", defaults to "search")
        context (Optional[Dict[str, Any]]): Additional context data
    """
    message: str
    agent_type: str = "search"
    context: Optional[Dict[str, Any]] = None


class EnhancedChatMessage(BaseModel):
    """
    Enhanced chat message model with session management.
    
    Attributes:
        message (str): The user's chat message content
        session_data (Optional[Dict[str, Any]]): Session state and context
    """
    message: str
    session_data: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    """
    Search request model for knowledge base queries.
    
    Attributes:
        query (str): The search query string
        search_type (str): Type of search ("knowledge" or "servicenow")
    """
    query: str
    search_type: str = "knowledge"


class TicketCreationRequest(BaseModel):
    """
    Comprehensive ticket creation request model.
    
    Supports multiple ticket types (incident, change, service) with
    appropriate fields for each type.
    
    Attributes:
        ticket_type (str): Type of ticket to create
        short_description (str): Brief description of the issue
        description (str): Detailed description
        category (Optional[str]): Ticket category classification
        priority (Optional[str]): Priority level (1-5 scale)
        assigned_group (Optional[str]): Group to assign the ticket
        caller_id (Optional[str]): ID of the person reporting the issue
        change_type (Optional[str]): Type of change (for change tickets)
        risk (Optional[str]): Risk level (for change tickets)
        implementation_plan (Optional[str]): Plan details (for changes)
        requested_for (Optional[str]): Requestor (for service requests)
        service_catalog_item (Optional[str]): Catalog item name
    """
    ticket_type: str
    short_description: str
    description: str
    category: Optional[str] = "General"
    priority: Optional[str] = "3 - Medium"
    assigned_group: Optional[str] = None
    caller_id: Optional[str] = None
    change_type: Optional[str] = "Standard"
    risk: Optional[str] = "Medium"
    implementation_plan: Optional[str] = None
    requested_for: Optional[str] = None
    service_catalog_item: Optional[str] = "General Request"


class TicketStatusRequest(BaseModel):
    """
    Ticket status inquiry request model.
    
    Attributes:
        ticket_number (str): The ticket number to check
    """
    ticket_number: str


class TicketUpdateRequest(BaseModel):
    """
    Ticket update request model.
    
    Attributes:
        ticket_number (str): The ticket number to update
        work_notes (str): Work notes to add to the ticket
    """
    ticket_number: str
    work_notes: str


class DuplicateDecisionRequest(BaseModel):
    """
    Duplicate ticket decision request model.
    
    Attributes:
        decision (str): User decision (proceed, stop, link, modify)
        session_data (Dict[str, Any]): Current session context
    """
    decision: str
    session_data: Dict[str, Any]


# ========================= HEALTH & DEBUG ENDPOINTS =========================


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring service status.
    
    Returns:
        dict: Service health status and agent initialization states
        
    Example:
        GET /health
        Response: {"status": "healthy", "search_agent_initialized": true}
    """
    return {
        "status": "healthy",
        "search_agent_initialized": search_agent is not None,
        "timestamp": str(datetime.now())
    }


@app.get("/debug")
async def debug_info():
    """
    Debug endpoint for development and troubleshooting.
    
    Provides detailed information about backend services, agent states,
    and configuration for frontend integration testing.
    
    Returns:
        dict: Comprehensive debug information including:
            - Backend status and timestamp
            - Agent initialization states
            - CORS configuration
            - Service availability
    """
    search_status = "initialized" if search_agent else "not_initialized"
    ticket_status = "initialized" if ticket_agent else "not_initialized"
    chatbot_status = "initialized" if chatbot_service else "not_initialized"
    
    return {
        "message": "Backend is running",
        "timestamp": str(datetime.now()),
        "search_agent_status": search_status,
        "ticket_agent_status": ticket_status,
        "chatbot_service_status": chatbot_status,
        "cors_origins": Config.CORS_ORIGINS
    }


# ========================= TEST ENDPOINTS =========================

@app.post("/test/enhanced")
async def test_enhanced_chat():
    """
    Test endpoint for enhanced chat functionality.
    
    Validates the hybrid chatbot service with a predefined test message
    to ensure proper integration and response formatting.
    
    Returns:
        dict: Test result with status and response data
        
    Raises:
        dict: Error information if chatbot service is not available
    """
    try:
        if not chatbot_service:
            return {"error": "Chatbot service not initialized"}
        
        test_message = "Hello, I need help with my laptop"
        result = chatbot_service.process_message(test_message)
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": str(e.__traceback__)
        }


@app.get("/test/knowledge")
async def test_knowledge_search():
    """
    Test endpoint for direct knowledge base search functionality.
    
    Performs a direct test of the knowledge search capabilities using
    the Core Search Agent to validate search functionality.
    
    Returns:
        dict: Test search results or error information
    """
    try:
        if not chatbot_service:
            return {"error": "Chatbot service not initialized"}
        
        # Test knowledge base search directly using Core Search Agent
        from agents.core_search_agent import CoreSearchAgent
        search_agent = CoreSearchAgent()
        result = search_agent.search("Windows", "knowledge")
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": str(e.__traceback__)
        }

# Debug endpoint for frontend testing
@app.get("/debug")
async def debug_info():
    """Debug endpoint for frontend connection testing"""
    return {
        "message": "Backend is running",
        "timestamp": str(datetime.now()),
        "search_agent_status": "initialized" if search_agent else "not_initialized",
        "ticket_agent_status": "initialized" if ticket_agent else "not_initialized",
        "chatbot_service_status": "initialized" if chatbot_service else "not_initialized",
        "cors_origins": Config.CORS_ORIGINS
    }

# Test enhanced chat endpoint
@app.post("/test/enhanced")
async def test_enhanced_chat():
    """Test enhanced chat functionality"""
    try:
        if not chatbot_service:
            return {"error": "Chatbot service not initialized"}
        
        result = chatbot_service.process_message("Hello, I need help with my laptop")
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": str(e.__traceback__)
        }

@app.get("/test/knowledge")
async def test_knowledge_search():
    """Test knowledge base search directly"""
    try:
        if not chatbot_service:
            return {"error": "Chatbot service not initialized"}
        
        # Test knowledge base search directly using Core Search Agent
        from agents.core_search_agent import CoreSearchAgent
        search_agent = CoreSearchAgent()
        result = search_agent.search("Windows", "knowledge")
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": str(e.__traceback__)
        }

@app.get("/test/search-all")
async def test_search_all():
    """Test search_all method directly"""
    try:
        if not chatbot_service:
            return {"error": "Chatbot service not initialized"}
        
        # Test search using Core Search Agent
        from agents.core_search_agent import CoreSearchAgent
        search_agent = CoreSearchAgent()
        result = search_agent.search("Windows", "mixed")
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": str(e.__traceback__)
        }

@app.get("/test/chatbot-search")
async def test_chatbot_search():
    """Test chatbot search service directly"""
    try:
        if not chatbot_service:
            return {"error": "Chatbot service not initialized"}
        
        # Test chatbot search service directly
        result = chatbot_service.search_service.search_all("Windows", "Other")
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": str(e.__traceback__)
        }


# Ticket Creation Endpoints
class TicketCreationRequest(BaseModel):
    ticket_type: str  # incident, change, service
    short_description: str
    description: str
    category: Optional[str] = "General"
    priority: Optional[str] = "3 - Medium"
    assigned_group: Optional[str] = None
    caller_id: Optional[str] = None
    change_type: Optional[str] = "Standard"
    risk: Optional[str] = "Medium"
    implementation_plan: Optional[str] = None
    requested_for: Optional[str] = None
    service_catalog_item: Optional[str] = "General Request"

class TicketStatusRequest(BaseModel):
    ticket_number: str

class TicketUpdateRequest(BaseModel):
    ticket_number: str
    work_notes: str

@app.post("/ticket/create")
async def create_ticket(request: TicketCreationRequest):
    """Create a new ticket using the Ticket Agent"""
    try:
        if not ticket_agent:
            raise HTTPException(status_code=500, detail="Ticket agent not initialized")
        
        # Prepare ticket data
        ticket_data = {
            "short_description": request.short_description,
            "description": request.description,
            "category": request.category,
            "priority": request.priority,
            "assigned_group": request.assigned_group,
            "caller_id": request.caller_id
        }
        
        # Add type-specific data
        if request.ticket_type.lower() == "change":
            ticket_data.update({
                "change_type": request.change_type,
                "risk": request.risk,
                "implementation_plan": request.implementation_plan
            })
        elif request.ticket_type.lower() == "service":
            ticket_data.update({
                "requested_for": request.requested_for,
                "service_catalog_item": request.service_catalog_item
            })
        
        # Create the ticket
        result = ticket_agent.create_ticket(request.ticket_type, **ticket_data)
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {str(e)}")

@app.get("/ticket/status/{ticket_number}")
async def get_ticket_status(ticket_number: str):
    """Get the status of a ticket"""
    try:
        if not ticket_agent:
            raise HTTPException(status_code=500, detail="Ticket agent not initialized")
        
        result = ticket_agent.get_ticket_status(ticket_number)
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ticket status: {str(e)}")

@app.post("/ticket/update")
async def update_ticket(request: TicketUpdateRequest):
    """Update a ticket with work notes"""
    try:
        if not ticket_agent:
            raise HTTPException(status_code=500, detail="Ticket agent not initialized")
        
        result = ticket_agent.update_ticket(request.ticket_number, request.work_notes)
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating ticket: {str(e)}")

@app.get("/test/ticket-agent")
async def test_ticket_agent():
    """Test ticket agent functionality"""
    try:
        if not ticket_agent:
            return {"error": "Ticket agent not initialized"}
        
        # Test creating an incident ticket
        result = ticket_agent.create_ticket(
            "incident",
            short_description="Test incident from chatbot",
            description="This is a test incident created by the chatbot",
            category="General",
            priority="3 - Medium"
        )
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": str(e.__traceback__)
        }


# Chat endpoint
@app.post("/chat")
async def chat(chat_message: ChatMessage):
    """Main chat endpoint for search agent"""
    try:
        if not search_agent:
            raise HTTPException(status_code=500, detail="Search agent not initialized")
        
        # Only handle search agent for now
        if chat_message.agent_type != "search":
            chat_message.agent_type = "search"  # Force to search agent
        
        response = search_agent.search(chat_message.message)
        
        return {
            "response": response,
            "agent_type": "search",
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

# Enhanced chat endpoint with intent detection and structured data collection
@app.post("/chat/enhanced")
async def enhanced_chat(chat_message: EnhancedChatMessage):
    """Enhanced chat endpoint with intent detection and structured data collection"""
    try:
        if not chatbot_service:
            raise HTTPException(status_code=500, detail="Chatbot service not initialized")
        
        # Process message with chatbot service
        result = chatbot_service.process_message(chat_message.message, chat_message.session_data)
        
        return {
            "response": result["response"],
            "session_data": result["session_data"],
            "next_action": result["next_action"],
            "message_type": result["message_type"],
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing enhanced chat: {str(e)}")


# Search-specific endpoints
@app.post("/search")
async def search(search_request: SearchRequest):
    """Search knowledge base or ServiceNow"""
    try:
        if not search_agent:
            raise HTTPException(status_code=500, detail="Search agent not initialized")
        
        response = search_agent.search(
            search_request.query,
            search_request.search_type
        )
        
        return {
            "response": response,
            "query": search_request.query,
            "search_type": search_request.search_type,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}")


@app.get("/article/{article_id}")
async def get_article(article_id: str):
    """Get detailed article content"""
    try:
        if not search_agent:
            raise HTTPException(status_code=500, detail="Search agent not initialized")
        
        response = search_agent.get_article(article_id)
        
        return {
            "response": response,
            "article_id": article_id,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving article: {str(e)}")


# Ticket Creation Integration Endpoints

class DuplicateDecisionRequest(BaseModel):
    decision: str  # proceed, stop, link, modify
    session_data: Dict[str, Any]

@app.post("/ticket/duplicate-decision")
async def handle_duplicate_decision(request: DuplicateDecisionRequest):
    """Handle user decision regarding duplicate tickets"""
    try:
        if not chatbot_service:
            raise HTTPException(status_code=500, detail="Chatbot service not initialized")
        
        result = chatbot_service.handle_ticket_duplicate_decision(
            request.decision,
            request.session_data
        )
        
        return {
            "response": result.get("response", "Decision processed"),
            "message_type": result.get("message_type", "unknown"),
            "next_action": result.get("next_action", "continue"),
            "session_data": result.get("session_data", {}),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error handling duplicate decision: {str(e)}")

    @app.get("/ticket/creation/status")
    async def get_ticket_creation_status():
        """Get status of ticket creation agents"""
        try:
            if not ticket_creation_agent:
                raise HTTPException(status_code=500, detail="Ticket creation agent not initialized")

            status = ticket_creation_agent.get_agent_status()

            return {
                "status": "success",
                "agent_status": status
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting agent status: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True
    )
