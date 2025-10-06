"""
Google ADK Ticket Creation Agent - Complete Implementation
Orchestrates ticket creation workflow using Google ADK framework with Gemini
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os

# Google ADK imports
from vertexai.preview.generative_models import (
    GenerativeModel,
    Tool,
    FunctionDeclaration,
    Part,
    Content
)
import vertexai

from config.logging_config import get_logger
from config.config import Config
from agents.duplicate_check_agent import DuplicateCheckAgent
from agents.ticket_create_agent import TicketCreateAgent
from agents.ticket_response_agent import TicketResponseAgent
from agents.priority_sla_agent import PrioritySLAAgent

logger = get_logger("google_adk_ticket_creation_agent")


class GoogleADKTicketCreationAgent:
    """
    Google ADK Ticket Creation Agent using Gemini
    Orchestrates ticket creation flow with Google ADK framework
    """
    
    def __init__(self):
        # Initialize legacy agents for business logic reuse
        self.duplicate_check_agent = DuplicateCheckAgent()
        self.ticket_create_agent = TicketCreateAgent()
        self.ticket_response_agent = TicketResponseAgent()
        self.priority_sla_agent = PrioritySLAAgent()
        
        # Lazy initialization flags
        self._vertex_ai_initialized = False
        self._model_initialized = False
        self.model = None
        self.chat = None
        self.ticket_tools = None
        
        logger.info("Google ADK Ticket Creation Agent created (lazy initialization)")
    
    def _initialize_vertex_ai(self):
        """Initialize Vertex AI if not already done"""
        if not self._vertex_ai_initialized:
            try:
                logger.info("Initializing Vertex AI...")
                vertexai.init(
                    project=Config.GOOGLE_CLOUD_PROJECT_ID,
                    location=Config.GOOGLE_ADK_REGION
                )
                self._vertex_ai_initialized = True
                logger.info("✅ Vertex AI initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Vertex AI: {str(e)}")
                raise
    
    def _initialize_model(self):
        """Initialize Gemini model and tools if not already done"""
        if not self._model_initialized:
            try:
                self._initialize_vertex_ai()
                
                logger.info("Setting up Google ADK function declarations...")
                self._setup_function_declarations()
                
                logger.info("Creating Google ADK tools...")
                self.ticket_tools = Tool(
                    function_declarations=self.function_declarations
                )
                
                logger.info("Initializing Gemini model...")
                self.model = GenerativeModel(
                    model_name=Config.GOOGLE_ADK_MODEL,
                    tools=[self.ticket_tools],
                    system_instruction=self._get_system_instruction()
                )
                
                logger.info("Starting chat session...")
                self.chat = self.model.start_chat()
                
                self._model_initialized = True
                
                logger.info("=" * 80)
                logger.info("GOOGLE ADK TICKET CREATION AGENT FULLY INITIALIZED")
                logger.info(f"Model: {Config.GOOGLE_ADK_MODEL}")
                logger.info(f"Project: {Config.GOOGLE_CLOUD_PROJECT_ID}")
                logger.info(f"Region: {Config.GOOGLE_ADK_REGION}")
                logger.info("Google ADK Tools: 4 functions registered")
                logger.info("=" * 80)
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize model: {str(e)}")
                raise
    
    def _setup_function_declarations(self):
        """Setup Google ADK function declarations"""
        self.function_declarations = [
            FunctionDeclaration(
                name="check_duplicates",
                description="Check for duplicate tickets in ServiceNow",
                parameters={
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Ticket description to check"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User ID creating the ticket"
                        },
                        "ticket_type": {
                            "type": "string",
                            "enum": ["incident", "request", "change", "problem"],
                            "description": "Type of ticket"
                        },
                        "category": {
                            "type": "string",
                            "description": "Ticket category"
                        }
                    },
                    "required": ["description", "user_id", "ticket_type"]
                }
            ),
            FunctionDeclaration(
                name="assign_priority_sla",
                description="Assign priority and SLA based on ticket details",
                parameters={
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Ticket description"
                        },
                        "impact": {
                            "type": "string",
                            "description": "Impact level (High/Medium/Low)"
                        },
                        "urgency": {
                            "type": "string",
                            "description": "Urgency level (High/Medium/Low)"
                        },
                        "category": {
                            "type": "string",
                            "description": "Ticket category"
                        }
                    },
                    "required": ["description", "impact", "urgency"]
                }
            ),
            FunctionDeclaration(
                name="create_servicenow_ticket",
                description="Create ticket in ServiceNow system",
                parameters={
                    "type": "object",
                    "properties": {
                        "ticket_type": {
                            "type": "string",
                            "enum": ["incident", "request", "change", "problem"],
                            "description": "Type of ticket to create"
                        },
                        "ticket_data": {
                            "type": "string",
                            "description": "JSON string with ticket details"
                        }
                    },
                    "required": ["ticket_type", "ticket_data"]
                }
            ),
            FunctionDeclaration(
                name="generate_response",
                description="Generate user-friendly response",
                parameters={
                    "type": "object",
                    "properties": {
                        "ticket_result": {
                            "type": "string",
                            "description": "JSON string with ticket result"
                        },
                        "ticket_type": {
                            "type": "string",
                            "description": "Type of ticket created"
                        }
                    },
                    "required": ["ticket_result", "ticket_type"]
                }
            )
        ]
    
    def _get_system_instruction(self):
        """Get system instruction for Gemini model"""
        return """
        You are an expert IT support ticket creation assistant using Google ADK.
        
        Your workflow:
        1. Check duplicates first using check_duplicates function
        2. If no duplicates, assign priority using assign_priority_sla
        3. Create ticket using create_servicenow_ticket function
        4. Generate response using generate_response function
        
        Guidelines:
        - Always use the function tools for all operations
        - Never bypass the duplicate check step
        - Assign appropriate priority based on impact and urgency
        - Provide clear, helpful responses to users
        - Handle errors gracefully and inform users
        
        Execute the complete workflow for every ticket creation request.
        """
    
    def create_ticket(self, request_data):
        """
        Main entry point for Google ADK ticket creation
        Args:
            request_data: Dictionary with user request and intent
        Returns:
            dict: Complete ticket creation response
        """
        try:
            # Ensure model is initialized before use
            if not self._model_initialized:
                self._initialize_model()
            
            logger.info("=" * 80)
            logger.info("GOOGLE ADK TICKET CREATION WORKFLOW STARTED")
            logger.info(f"Request: {request_data}")
            logger.info("=" * 80)
            
            # Extract intent and data
            intent = request_data.get('intent', {})
            user_message = request_data.get('user_message', '')
            collected_data = request_data.get('collected_data', {})
            
            # Prepare request for Gemini
            prompt = self._prepare_ticket_prompt(
                intent, user_message, collected_data
            )
            
            # Send to Gemini model with tools
            response = self.chat.send_message(prompt)
            
            # Process response and function calls
            result = self._process_model_response(response)
            
            logger.info("GOOGLE ADK TICKET CREATION WORKFLOW COMPLETED")
            logger.info("=" * 80)
            
            return result
            
        except Exception as e:
            logger.error(f"Google ADK ticket creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Ticket creation failed. Please try again."
            }
    
    def _prepare_ticket_prompt(self, intent, user_message, collected_data):
        """Prepare prompt for Gemini model"""
        prompt = f"""
        Please help create a ticket with the following information:
        
        User Message: {user_message}
        
        Intent Details:
        - Type: {intent.get('ticket_type', 'incident')}
        - Category: {intent.get('category', '')}
        - Priority Intent: {intent.get('priority', '')}
        - Urgency Intent: {intent.get('urgency', '')}
        
        Collected Data:
        {json.dumps(collected_data, indent=2)}
        
        Please execute the complete ticket creation workflow:
        1. Check for duplicates
        2. Assign priority and SLA
        3. Create the ticket
        4. Generate user response
        """
        return prompt
    
    def _process_model_response(self, response):
        """Process Gemini model response and handle function calls"""
        try:
            # Check if model wants to call functions
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                
                if hasattr(candidate, 'content') and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            # Execute function call
                            function_call = part.function_call
                            result = self._execute_function_call(function_call)
                            
                            # Create function response
                            from vertexai.preview.generative_models import FunctionResponse
                            function_response = FunctionResponse(
                                name=function_call.name,
                                response=result
                            )
                            
                            # Continue conversation with function result
                            next_response = self.chat.send_message(function_response)
                            
                            return self._process_model_response(next_response)
                        
                        elif hasattr(part, 'text') and part.text:
                            # Regular text response
                            return {
                                "success": True,
                                "message": part.text,
                                "source": "google_adk_gemini"
                            }
            
            return {
                "success": False,
                "message": "No valid response from model"
            }
            
        except Exception as e:
            logger.error(f"Error processing model response: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_function_call(self, function_call):
        """Execute Google ADK function calls using existing business logic"""
        function_name = function_call.name
        args = function_call.args if hasattr(function_call, 'args') else {}
        
        try:
            logger.info(f"Executing Google ADK function: {function_name}")
            logger.info(f"Function args: {args}")
            
            if function_name == "check_duplicates":
                return self._handle_check_duplicates(args)
            elif function_name == "assign_priority_sla":
                return self._handle_assign_priority_sla(args)
            elif function_name == "create_servicenow_ticket":
                return self._handle_create_servicenow_ticket(args)
            elif function_name == "generate_response":
                return self._handle_generate_response(args)
            else:
                raise ValueError(f"Unknown function: {function_name}")
                
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _handle_check_duplicates(self, args):
        """Handle duplicate check using existing agent"""
        try:
            # Extract data for duplicate check agent method signature
            description = args.get('description', '')
            user_id = args.get('user_id', '')
            ticket_type = args.get('ticket_type', 'incident')
            category = args.get('category', '')
            
            # Prepare ticket_data for duplicate check agent
            ticket_data = {
                'description': description,
                'category': category,
                'short_description': description[:50] if description else ''
            }
            
            # Use existing duplicate check agent with correct signature
            result = self.duplicate_check_agent.check_duplicates(
                ticket_data, user_id, ticket_type
            )
            
            logger.info(f"Duplicate check result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Duplicate check failed: {str(e)}")
            return {
                "has_duplicates": False,
                "error": str(e)
            }
    
    def _handle_assign_priority_sla(self, args):
        """Handle priority/SLA assignment using existing agent"""
        try:
            description = args.get('description', '')
            impact = args.get('impact', 'Medium')
            urgency = args.get('urgency', 'Medium')
            category = args.get('category', '')
            
            # Prepare ticket data for priority SLA agent
            ticket_data = {
                'description': description,
                'impact': impact,
                'urgency': urgency,
                'category': category
            }
            
            # Use existing priority SLA agent with correct method name
            result = self.priority_sla_agent.assign_priority_and_sla(
                ticket_data, 'incident'
            )
            
            logger.info(f"Priority/SLA assignment result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Priority/SLA assignment failed: {str(e)}")
            return {
                "priority": 3,
                "priority_name": "Medium",
                "sla": {"response_time": "4 hours", "resolution_time": "24 hours"},
                "error": str(e)
            }
    
    def _handle_create_servicenow_ticket(self, args):
        """Handle ServiceNow ticket creation using existing agent"""
        try:
            ticket_type = args.get('ticket_type', 'incident')
            ticket_data = json.loads(args.get('ticket_data', '{}'))
            
            # Use existing ticket create agent
            result = self.ticket_create_agent.create_ticket(
                ticket_type, ticket_data
            )
            
            logger.info(f"ServiceNow ticket creation result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"ServiceNow ticket creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _handle_generate_response(self, args):
        """Handle response generation using existing agent"""
        try:
            ticket_result = json.loads(args.get('ticket_result', '{}'))
            ticket_type = args.get('ticket_type', 'incident')
            
            # Use existing ticket response agent
            result = self.ticket_response_agent.generate_response(
                ticket_result, ticket_type
            )
            
            logger.info(f"Response generation result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return {
                "message": "Ticket operation completed with some issues",
                "error": str(e)
            }
    
    def get_conversation_history(self):
        """Get conversation history for debugging"""
        try:
            if hasattr(self.chat, 'history'):
                return self.chat.history
            return []
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    def reset_chat(self):
        """Reset chat session"""
        try:
            self.chat = self.model.start_chat()
            logger.info("Google ADK chat session reset")
        except Exception as e:
            logger.error(f"Error resetting chat: {str(e)}")


# Maintain backward compatibility with existing import
class TicketCreationAgent(GoogleADKTicketCreationAgent):
    """
    Backward compatibility wrapper for existing imports
    """
    pass