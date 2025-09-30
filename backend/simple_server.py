#!/usr/bin/env python3
"""
Simple ServiceNow Chatbot Backend
Using Python's built-in HTTP server and JSON modules for minimal dependencies
"""

import http.server
import socketserver
import json
import urllib.parse
import uuid
from datetime import datetime
import logging
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceNowAgent:
    """Main agent for handling ServiceNow operations"""
    
    def __init__(self):
        # Mock data for demonstration
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
    
    def check_duplicate_tickets(self, user_id, description):
        """Check for duplicate tickets by the same user"""
        user_tickets = [t for t in self.tickets_db if t["user_id"] == user_id]
        duplicates = []
        
        for ticket in user_tickets:
            # Simple keyword matching
            if any(word in ticket["description"].lower() for word in description.lower().split()):
                duplicates.append(ticket)
        
        return duplicates
    
    def search_similar_tickets(self, description, limit=5):
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
                similar_tickets.append({
                    "ticket_id": ticket["id"],
                    "title": ticket["title"],
                    "description": ticket["description"],
                    "status": ticket["status"],
                    "similarity_score": similarity,
                    "resolution": ticket.get("resolution")
                })
        
        # Sort by similarity score
        similar_tickets.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similar_tickets[:limit]
    
    def create_incident(self, user_id, title, description, priority="3", category="general"):
        """Create a new incident ticket"""
        incident_id = f"INC{len(self.tickets_db) + 1:07d}"
        
        new_ticket = {
            "id": incident_id,
            "title": title,
            "description": description,
            "user_id": user_id,
            "status": "open",
            "priority": priority,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "resolution": None
        }
        
        self.tickets_db.append(new_ticket)
        
        return {
            "ticket_id": incident_id,
            "status": "created",
            "message": f"New incident {incident_id} has been created successfully."
        }
    
    def process_chat_message(self, user_id, message):
        """Process chat message and provide intelligent response"""
        
        # Search for similar tickets first (across all users)
        similar_tickets = self.search_similar_tickets(message)
        
        if similar_tickets:
            resolved_tickets = [t for t in similar_tickets if t["status"] == "resolved" and t["resolution"]]
            
            if resolved_tickets:
                # Show resolution from similar resolved tickets
                best_match = resolved_tickets[0]
                response = f"I found a similar resolved ticket: {best_match['ticket_id']} - {best_match['title']}\n\n"
                response += f"Resolution: {best_match['resolution']}\n\n"
                response += "Does this help resolve your issue? If not, I can create a new ticket for you."
                return response
            else:
                # Check for duplicates by the same user first
                duplicates = self.check_duplicate_tickets(user_id, message)
                if duplicates:
                    duplicate_info = "\n".join([f"- {t['id']}: {t['title']} ({t['status']})" for t in duplicates])
                    return f"I found some existing tickets from you that might be related:\n{duplicate_info}\n\nWould you like me to update an existing ticket or create a new one?"
                
                # Link to existing open ticket
                open_ticket = similar_tickets[0]
                response = f"I found a similar open ticket: {open_ticket['ticket_id']} - {open_ticket['title']}\n\n"
                response += "This might be related to your issue. Would you like me to add your information to this existing ticket or create a new one?"
                return response
        
        # Check for duplicates by the same user if no similar tickets found
        duplicates = self.check_duplicate_tickets(user_id, message)
        if duplicates:
            duplicate_info = "\n".join([f"- {t['id']}: {t['title']} ({t['status']})" for t in duplicates])
            return f"I found some existing tickets from you that might be related:\n{duplicate_info}\n\nWould you like me to update an existing ticket or create a new one?"
        
        # No similar tickets found, suggest creating new incident
        return "I don't see any similar existing tickets. Let me create a new incident for you. Could you provide a brief title for your issue?"

# Global agent instance
agent = ServiceNowAgent()

class ChatbotHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the chatbot API"""
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self.send_json_response({"message": "ServiceNow Chatbot API is running"})
        elif path == '/health':
            self.send_json_response({"status": "healthy", "timestamp": datetime.now().isoformat()})
        elif path.startswith('/chat/history/'):
            user_id = path.split('/')[-1]
            messages = agent.chat_history.get(user_id, [])
            self.send_json_response({"messages": messages})
        elif path.startswith('/tickets/user/'):
            user_id = path.split('/')[-1]
            user_tickets = [t for t in agent.tickets_db if t["user_id"] == user_id]
            self.send_json_response({"tickets": user_tickets})
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if path == '/chat/message':
                self.handle_chat_message(data)
            elif path == '/tickets/search':
                self.handle_ticket_search(data)
            elif path == '/tickets/create':
                self.handle_ticket_create(data)
            else:
                self.send_error(404, "Not Found")
                
        except Exception as e:
            logger.error(f"Error processing POST request: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def handle_chat_message(self, data):
        """Handle chat message"""
        user_id = data.get('user_id')
        message = data.get('message')
        
        if not user_id or not message:
            self.send_error(400, "Missing user_id or message")
            return
        
        # Process the message with the agent
        response = agent.process_chat_message(user_id, message)
        
        # Store message in chat history
        if user_id not in agent.chat_history:
            agent.chat_history[user_id] = []
        
        # Add user message
        user_msg = {
            "id": str(uuid.uuid4()),
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "is_user": True
        }
        agent.chat_history[user_id].append(user_msg)
        
        # Add bot response
        bot_msg = {
            "id": str(uuid.uuid4()),
            "message": response,
            "timestamp": datetime.now().isoformat(),
            "is_user": False
        }
        agent.chat_history[user_id].append(bot_msg)
        
        self.send_json_response({"response": response, "message_id": bot_msg["id"]})
    
    def handle_ticket_search(self, data):
        """Handle ticket search"""
        description = data.get("description", "")
        similar_tickets = agent.search_similar_tickets(description)
        self.send_json_response({"tickets": similar_tickets})
    
    def handle_ticket_create(self, data):
        """Handle ticket creation"""
        user_id = data.get('user_id')
        title = data.get('title')
        description = data.get('description')
        priority = data.get('priority', '3')
        category = data.get('category', 'general')
        
        if not user_id or not title or not description:
            self.send_error(400, "Missing required fields")
            return
        
        result = agent.create_incident(user_id, title, description, priority, category)
        self.send_json_response(result)
    
    def send_json_response(self, data):
        """Send JSON response with CORS headers"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

def run_server(port=8000):
    """Run the HTTP server"""
    with socketserver.TCPServer(("", port), ChatbotHandler) as httpd:
        logger.info(f"ServiceNow Chatbot API server starting on port {port}")
        logger.info(f"Visit http://localhost:{port} to check if the server is running")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")

if __name__ == "__main__":
    run_server()