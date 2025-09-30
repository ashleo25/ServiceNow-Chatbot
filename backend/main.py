"""
ServiceNow Chatbot Backend
A FastAPI-based backend for an LLM-powered ServiceNow chatbot that handles:
- Duplicate ticket detection
- Similar ticket search
- Ticket linking
- New incident creation
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ServiceNow Chatbot API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    id: str
    user_id: str
    message: str
    timestamp: datetime
    is_user: bool
    response: Optional[str] = None

class TicketSearchResult(BaseModel):
    ticket_id: str
    title: str
    description: str
    status: str
    similarity_score: float
    resolution: Optional[str] = None

class NewIncidentRequest(BaseModel):
    user_id: str
    title: str
    description: str
    priority: str = "3"
    category: str = "general"

class ServiceNowAgent:
    """Main agent for handling ServiceNow operations"""
    
    def __init__(self):
        # Mock data for demonstration - in production, this would connect to actual ServiceNow API
        self.tickets_db = [
            {
                "id": "INC0001001",
                "title": "Email not working",
                "description": "Cannot send or receive emails",
                "user_id": "user123",
                "status": "resolved",
                "resolution": "Restarted email service and updated Exchange settings"
            },
            {
                "id": "INC0001002", 
                "title": "VPN connection issues",
                "description": "Cannot connect to corporate VPN",
                "user_id": "user456",
                "status": "resolved",
                "resolution": "Updated VPN client and provided new connection profile"
            },
            {
                "id": "INC0001003",
                "title": "Laptop running slow",
                "description": "Computer performance is very slow",
                "user_id": "user789",
                "status": "open",
                "resolution": None
            }
        ]
        
        self.chat_history = {}  # user_id -> list of messages
    
    async def check_duplicate_tickets(self, user_id: str, description: str) -> List[Dict[str, Any]]:
        """Check for duplicate tickets by the same user"""
        user_tickets = [t for t in self.tickets_db if t["user_id"] == user_id]
        duplicates = []
        
        for ticket in user_tickets:
            # Simple keyword matching - in production, use embeddings or NLP
            if any(word in ticket["description"].lower() for word in description.lower().split()):
                duplicates.append(ticket)
        
        return duplicates
    
    async def search_similar_tickets(self, description: str, limit: int = 5) -> List[TicketSearchResult]:
        """Search for similar tickets across all users"""
        similar_tickets = []
        description_words = set(description.lower().split())
        
        for ticket in self.tickets_db:
            ticket_words = set(ticket["description"].lower().split())
            # Calculate similarity score using Jaccard similarity
            intersection = len(description_words.intersection(ticket_words))
            union = len(description_words.union(ticket_words))
            similarity = intersection / union if union > 0 else 0
            
            if similarity > 0.1:  # Threshold for similarity
                similar_tickets.append(TicketSearchResult(
                    ticket_id=ticket["id"],
                    title=ticket["title"],
                    description=ticket["description"],
                    status=ticket["status"],
                    similarity_score=similarity,
                    resolution=ticket.get("resolution")
                ))
        
        # Sort by similarity score
        similar_tickets.sort(key=lambda x: x.similarity_score, reverse=True)
        return similar_tickets[:limit]
    
    async def create_incident(self, request: NewIncidentRequest) -> Dict[str, Any]:
        """Create a new incident ticket"""
        incident_id = f"INC{len(self.tickets_db) + 1:07d}"
        
        new_ticket = {
            "id": incident_id,
            "title": request.title,
            "description": request.description,
            "user_id": request.user_id,
            "status": "open",
            "priority": request.priority,
            "category": request.category,
            "created_at": datetime.now().isoformat(),
            "resolution": None
        }
        
        self.tickets_db.append(new_ticket)
        
        return {
            "ticket_id": incident_id,
            "status": "created",
            "message": f"New incident {incident_id} has been created successfully."
        }
    
    async def process_chat_message(self, user_id: str, message: str) -> str:
        """Process chat message and provide intelligent response"""
        
        # Check for duplicates first
        duplicates = await self.check_duplicate_tickets(user_id, message)
        if duplicates:
            duplicate_info = "\n".join([f"- {t['id']}: {t['title']} ({t['status']})" for t in duplicates])
            return f"I found some existing tickets from you that might be related:\n{duplicate_info}\n\nWould you like me to update an existing ticket or create a new one?"
        
        # Search for similar tickets
        similar_tickets = await self.search_similar_tickets(message)
        
        if similar_tickets:
            resolved_tickets = [t for t in similar_tickets if t.status == "resolved" and t.resolution]
            
            if resolved_tickets:
                # Show resolution from similar resolved tickets
                best_match = resolved_tickets[0]
                response = f"I found a similar resolved ticket: {best_match.ticket_id} - {best_match.title}\n\n"
                response += f"Resolution: {best_match.resolution}\n\n"
                response += "Does this help resolve your issue? If not, I can create a new ticket for you."
                return response
            else:
                # Link to existing open ticket
                open_ticket = similar_tickets[0]
                response = f"I found a similar open ticket: {open_ticket.ticket_id} - {open_ticket.title}\n\n"
                response += "This might be related to your issue. Would you like me to add your information to this existing ticket or create a new one?"
                return response
        
        # No similar tickets found, suggest creating new incident
        return "I don't see any similar existing tickets. Let me create a new incident for you. Could you provide a brief title for your issue?"

# Global agent instance
agent = ServiceNowAgent()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections.remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.user_connections:
            await self.user_connections[user_id].send_text(message)

manager = ConnectionManager()

# API Endpoints
@app.get("/")
async def root():
    return {"message": "ServiceNow Chatbot API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/chat/message")
async def send_message(message: ChatMessage):
    """Send a chat message and get response"""
    try:
        # Process the message with the agent
        response = await agent.process_chat_message(message.user_id, message.message)
        
        # Store message in chat history
        if message.user_id not in agent.chat_history:
            agent.chat_history[message.user_id] = []
        
        # Add user message
        user_msg = {
            "id": str(uuid.uuid4()),
            "message": message.message,
            "timestamp": datetime.now().isoformat(),
            "is_user": True
        }
        agent.chat_history[message.user_id].append(user_msg)
        
        # Add bot response
        bot_msg = {
            "id": str(uuid.uuid4()),
            "message": response,
            "timestamp": datetime.now().isoformat(),
            "is_user": False
        }
        agent.chat_history[message.user_id].append(bot_msg)
        
        return {"response": response, "message_id": bot_msg["id"]}
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail="Error processing message")

@app.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str):
    """Get chat history for a user"""
    return {"messages": agent.chat_history.get(user_id, [])}

@app.post("/tickets/search")
async def search_tickets(query: Dict[str, str]):
    """Search for similar tickets"""
    description = query.get("description", "")
    similar_tickets = await agent.search_similar_tickets(description)
    return {"tickets": similar_tickets}

@app.post("/tickets/create")
async def create_ticket(request: NewIncidentRequest):
    """Create a new incident ticket"""
    result = await agent.create_incident(request)
    return result

@app.get("/tickets/user/{user_id}")
async def get_user_tickets(user_id: str):
    """Get all tickets for a specific user"""
    user_tickets = [t for t in agent.tickets_db if t["user_id"] == user_id]
    return {"tickets": user_tickets}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message
            response = await agent.process_chat_message(user_id, message_data["message"])
            
            # Send response back
            response_data = {
                "id": str(uuid.uuid4()),
                "message": response,
                "timestamp": datetime.now().isoformat(),
                "is_user": False
            }
            
            await manager.send_personal_message(json.dumps(response_data), user_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"User {user_id} disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)