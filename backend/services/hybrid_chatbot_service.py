"""
Hybrid Chatbot Orchestration Service - Multi-AI Integration

This module provides the main orchestration service for the ServiceNow Enterprise
Chatbot, integrating multiple AI services and agents to provide comprehensive
chat capabilities including knowledge search and intelligent ticket creation.

Key Features:
    - Multi-AI integration (Azure OpenAI + OCI Generative AI + Google ADK)
    - Intelligent intent detection and routing between services
    - Session state management across conversation flows
    - Seamless transition between search and ticket creation workflows
    - Context-aware conversation management and history tracking

Architecture Components:
    - Azure OpenAI for general conversation and complex reasoning
    - OCI Generative AI for specialized knowledge search operations
    - Google ADK for intelligent ticket creation with function calling
    - Conversation manager for session state and context preservation
    - Intent detection for routing user requests to appropriate agents

Workflow Orchestration:
    1. Message analysis and intent detection
    2. Route to appropriate specialized agent or service
    3. Maintain conversation context and session state
    4. Coordinate multi-step workflows (e.g., ticket creation process)
    5. Provide seamless user experience across different AI capabilities

Business Logic:
    - Detects ticket creation intents and routes to Google ADK agent
    - Handles knowledge search requests via OCI search agents
    - Manages complex multi-turn conversations with state persistence
    - Provides fallback to general AI for unspecified requests
    - Implements error handling and recovery across all services
"""

# Standard library imports
import json
from typing import Dict, Any, List, Optional

# Local imports
from agents.oci_compliant_core_search_agent import OciCompliantCoreSearchAgent
from agents.search_agent import SearchAgent
from agents.search_orchestrator import SearchOrchestrator
from agents.ticket_agent import TicketAgent
from agents.ticket_creation_agent import TicketCreationAgent
from services.azure_openai_service import AzureOpenAIService
from services.conversation_manager import ConversationManager, IntentType


class HybridChatbotService:
    """
    Main orchestration service for hybrid multi-AI chatbot functionality.
    
    This service coordinates between multiple AI providers and specialized agents
    to provide comprehensive chatbot capabilities. It handles intent detection,
    routing, session management, and workflow orchestration across different
    AI services and backend systems.
    
    Attributes:
        azure_openai (AzureOpenAIService): General AI conversation service
        conversation_manager (ConversationManager): Session and context management
        search_service: OCI-based search service (when available)
        search_agent (SearchAgent): Knowledge search agent
        ticket_agent (TicketAgent): ServiceNow ticket operations agent
        ticket_creation_agent (TicketCreationAgent): Google ADK ticket agent
        
    Methods:
        process_message(): Main entry point for message processing
        _detect_intent(): Analyze user message for intent classification
        _handle_search_request(): Process knowledge search requests
        _handle_ticket_request(): Process ticket creation requests
        _handle_general_conversation(): Handle general chat interactions
        
    Integration Points:
        - Azure OpenAI for conversational AI and complex reasoning
        - OCI Generative AI for domain-specific knowledge search
        - Google ADK for intelligent ticket creation workflows
        - ServiceNow REST API for ticket management operations
        - Session management for multi-turn conversation flows
        
    Error Handling:
        - Graceful degradation when services are unavailable
        - Fallback routing for failed intent detection
        - Comprehensive error logging and user feedback
        - Service health monitoring and automatic recovery
    """
    
    def __init__(self, search_agent: SearchAgent = None, 
                 ticket_agent: TicketAgent = None, 
                 ticket_creation_agent: TicketCreationAgent = None):
        """
        Initialize the hybrid chatbot service with AI agents and services.
        
        Sets up the multi-AI architecture by initializing all required services
        and agents, establishing connections, and configuring routing logic for
        different types of user requests.
        
        Args:
            search_agent (SearchAgent, optional): Knowledge search agent instance
            ticket_agent (TicketAgent, optional): ServiceNow ticket operations agent
            ticket_creation_agent (TicketCreationAgent, optional): Google ADK agent
            
        Note:
            - Services are initialized with graceful fallbacks for missing components
            - OCI search service requires proper AgentClient configuration
            - All agents support hot-swapping for testing and development
        """
        # Initialize core AI services
        self.azure_openai = AzureOpenAIService()
        self.conversation_manager = ConversationManager()
        
        # Initialize specialized agents
        # Note: OciCompliantCoreSearchAgent requires AgentClient 
        # Will be updated when AgentClient integration is complete
        self.search_service = None
        self.search_agent = search_agent
        self.ticket_agent = ticket_agent
        self.ticket_creation_agent = ticket_creation_agent
    
    def process_message(self, message: str, 
                       session_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user message using hybrid multi-AI approach.
        
        This is the main entry point for all chatbot interactions. It analyzes
        the user message, detects intent, routes to appropriate services, and
        manages the conversation flow while maintaining session state.
        
        Args:
            message (str): User's input message to process
            session_data (Dict[str, Any], optional): Current session context data
                
        Returns:
            Dict[str, Any]: Comprehensive response containing:
                - response (str): Generated response text for the user
                - session_data (dict): Updated session state and context
                - next_action (str): Suggested next action or workflow step
                - message_type (str): Classification of the response type
                - intent (str): Detected user intent from the message
                - confidence (float): Confidence score for intent detection
                - agent_used (str): Which agent/service processed the request
                
        Workflow:
            1. Analyze message for intent and context
            2. Update session state with new information
            3. Route to appropriate specialized agent or service
            4. Process response and update conversation history
            5. Return formatted response with next steps
            
        Raises:
            Exception: If all services fail or critical error occurs
            
        Example:
            ```python
            service = HybridChatbotService()
            result = service.process_message(
                "My laptop won't start", 
                {"user_id": "john.doe"}
            )
            print(result["response"])  # AI-generated helpful response
            ```
        """
        if session_data is None:
            session_data = {
                'intent': None,
                'confidence': 0.0,
                'rationale': '',
                'collected_data': {},
                'conversation_stage': 'greeting',
                'conversation_history': [],
                'ai_provider': 'azure_openai'  # Track which AI provider is being used
            }
        
        # Add message to conversation history
        session_data['conversation_history'].append({
            'role': 'user',
            'content': message,
            'timestamp': self._get_timestamp()
        })
        
        # Check for direct search commands first
        if self._is_direct_search_command(message):
            return self._handle_direct_search(message, session_data)
        
        # Handle different conversation stages
        if session_data['conversation_stage'] == 'greeting':
            return self._handle_greeting(message, session_data)
        elif session_data['conversation_stage'] == 'intent_detection':
            return self._handle_intent_detection(message, session_data)
        elif session_data['conversation_stage'] == 'data_collection':
            return self._handle_data_collection(message, session_data)
        elif session_data['conversation_stage'] == 'search_results':
            return self._handle_search_results(message, session_data)
        else:
            return self._handle_unknown_stage(message, session_data)
    
    def _handle_greeting(self, message: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle greeting stage"""
        try:
            # Use Azure OpenAI for intent detection
            intent_result = self.azure_openai.detect_intent(message, session_data['conversation_history'])
            
            session_data['intent'] = intent_result['intent']
            session_data['confidence'] = intent_result['confidence']
            session_data['rationale'] = intent_result['rationale']
            
            # Add AI response to conversation history
            session_data['conversation_history'].append({
                'role': 'assistant',
                'content': f"I understand you're looking for help with: {intent_result['intent']}",
                'timestamp': self._get_timestamp()
            })
            
            if intent_result['confidence'] >= 0.7:
                # High confidence - proceed to data collection
                session_data['conversation_stage'] = 'data_collection'
                next_question = self.conversation_manager.get_next_question(session_data)
                
                return {
                    'response': f"Great! I can help you with {intent_result['intent']}. {next_question}",
                    'message_type': 'intent_confirmed',
                    'next_action': 'data_collection',
                    'session_data': session_data,
                    'ai_provider': 'azure_openai'
                }
            else:
                # Low confidence - ask for clarification
                session_data['conversation_stage'] = 'intent_detection'
                return {
                    'response': f"I think you might be looking for help with {intent_result['intent']}, but I'm not completely sure. Could you tell me more about what you need help with?",
                    'message_type': 'intent_clarification',
                    'next_action': 'clarify_intent',
                    'session_data': session_data,
                    'ai_provider': 'azure_openai'
                }
        except Exception as e:
            session_data['conversation_stage'] = 'intent_detection'
            return {
                'response': "I'm here to help! Could you tell me what you need assistance with?",
                'message_type': 'greeting',
                'next_action': 'detect_intent',
                'session_data': session_data,
                'ai_provider': 'azure_openai'
            }
    
    def _handle_intent_detection(self, message: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intent detection stage"""
        try:
            # Use Azure OpenAI for intent detection
            intent_result = self.azure_openai.detect_intent(message, session_data['conversation_history'])
            
            session_data['intent'] = intent_result['intent']
            session_data['confidence'] = intent_result['confidence']
            session_data['rationale'] = intent_result['rationale']
            
            if intent_result['confidence'] >= 0.6:
                # Proceed to data collection
                session_data['conversation_stage'] = 'data_collection'
                next_question = self.conversation_manager.get_next_question(session_data)
                
                return {
                    'response': f"Perfect! I understand you need help with {intent_result['intent']}. {next_question}",
                    'message_type': 'intent_confirmed',
                    'next_action': 'data_collection',
                    'session_data': session_data,
                    'ai_provider': 'azure_openai'
                }
            else:
                # Still unclear - ask for more details
                return {
                    'response': "I'm still not sure what you need help with. Could you provide more details about your issue or request?",
                    'message_type': 'intent_clarification',
                    'next_action': 'clarify_intent',
                    'session_data': session_data,
                    'ai_provider': 'azure_openai'
                }
        except Exception as e:
            return {
                'response': "I'm having trouble understanding your request. Could you please rephrase it?",
                'message_type': 'error',
                'next_action': 'retry',
                'session_data': session_data,
                'ai_provider': 'azure_openai'
            }
    
    def _handle_data_collection(self, message: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data collection stage"""
        try:
            # Get next question
            next_question = self.conversation_manager.get_next_question(session_data)
            
            if next_question:
                # Still collecting data
                field_name = self._extract_field_from_question(next_question, session_data['intent'])
                if field_name:
                    session_data = self.conversation_manager.update_session_data(session_data, field_name, message)
                
                # Get next question
                next_question = self.conversation_manager.get_next_question(session_data)
                
                if next_question:
                    return {
                        'response': next_question,
                        'message_type': 'data_collection',
                        'next_action': 'collect_data',
                        'session_data': session_data,
                        'ai_provider': 'azure_openai'
                    }
            
            # All data collected - ALWAYS start with Search Agent first
            return self._handle_search_phase(session_data)
            
        except Exception as e:
            return {
                'response': "I'm having trouble processing your information. Could you please try again?",
                'message_type': 'error',
                'next_action': 'retry',
                'session_data': session_data,
                'ai_provider': 'azure_openai'
            }
    
    def _handle_search_phase(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search phase using OCI Agents"""
        try:
            # Build search query
            search_query = self.conversation_manager.build_search_query(session_data)
            
            # Use real OCI Search Agent if available
            if self.search_agent:
                search_results = self.search_agent.search(search_query)
                ai_provider = 'oci_search_agent'
            else:
                # Fallback to enhanced search service
                search_results = self.search_service.search_all(search_query, session_data['intent'])
                ai_provider = 'enhanced_search'
            
            # Format results
            formatted_results = self._format_search_results(search_results, session_data['intent'])
            
            # Generate data summary
            data_summary = self.conversation_manager.get_data_summary(session_data)
            
            # Add ticket creation option to search results
            ticket_option = "\n\n**If these results don't help solve your issue, you can type 'create ticket' to submit a formal request.**"
            
            # Update session
            session_data['conversation_stage'] = 'search_results'
            session_data['search_results'] = search_results
            
            return {
                'response': f"{data_summary}\n\n{formatted_results}{ticket_option}",
                'message_type': 'search_results',
                'next_action': 'present_results',
                'session_data': session_data,
                'search_results': search_results,
                'ai_provider': ai_provider
            }
            
        except Exception as e:
            # Fallback to enhanced search service
            try:
                search_results = self.search_service.search_all(search_query, session_data['intent'])
                formatted_results = self._format_search_results(search_results, session_data['intent'])
                
                session_data['conversation_stage'] = 'search_results'
                session_data['search_results'] = search_results
                
                return {
                    'response': f"{data_summary}\n\n{formatted_results}",
                    'message_type': 'search_results',
                    'next_action': 'present_results',
                    'session_data': session_data,
                    'search_results': search_results,
                    'ai_provider': 'enhanced_search'
                }
            except Exception as e2:
                return {
                    'response': "I found some information, but I'm having trouble presenting it properly. Let me try a different approach.",
                    'message_type': 'error',
                    'next_action': 'retry',
                    'session_data': session_data,
                    'ai_provider': 'fallback'
                }
    
    def _handle_direct_search(self, message: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle direct search commands"""
        try:
            # Extract search query from message
            search_query = message.replace("search for", "").replace("find", "").strip()
            
            # Use real OCI Search Agent if available
            if self.search_agent:
                search_results = self.search_agent.search(search_query)
                ai_provider = 'oci_search_agent'
            else:
                # Fallback to enhanced search service
                search_results = self.search_service.search_all(search_query, "Knowledge")
                ai_provider = 'enhanced_search'
            
            # Format results
            formatted_results = self._format_search_results(search_results, "Knowledge")
            
            # Update session data
            session_data['conversation_stage'] = 'search_results'
            session_data['search_results'] = search_results
            session_data['last_search_query'] = search_query
            
            return {
                'response': f"Here's what I found for '{search_query}':\n\n{formatted_results}",
                'message_type': 'direct_search_results',
                'next_action': 'present_results',
                'session_data': session_data,
                'search_results': search_results,
                'ai_provider': ai_provider
            }
            
        except Exception as e:
            return {
                'response': f"I'm having trouble searching for '{search_query}'. Let me try a different approach.",
                'message_type': 'error',
                'next_action': 'retry',
                'session_data': session_data,
                'ai_provider': 'fallback'
            }
    
    def _handle_search_results(self, message: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search results stage"""
        if message.lower() in ['new search', 'search again', 'new query']:
            # Reset session
            session_data = {
                'intent': None,
                'confidence': 0.0,
                'rationale': '',
                'collected_data': {},
                'conversation_stage': 'intent_detection',
                'conversation_history': session_data['conversation_history']
            }
            
            return {
                'response': "Sure! What would you like to search for or what can I help you with?",
                'message_type': 'new_search',
                'next_action': 'detect_intent',
                'session_data': session_data,
                'ai_provider': 'azure_openai'
            }
        elif message.lower() in ['create ticket', 'submit ticket', 'log ticket', 'still need help', 'not helpful', 'didn\'t help']:
            # User wants to proceed to ticket creation
            if self._is_ticket_creation_intent(session_data['intent']):
                return self._handle_ticket_creation_phase(session_data)
            else:
                return {
                    'response': "I understand the search results weren't helpful. Let me help you create a ticket for this issue. I'll need to collect some additional information first.",
                    'message_type': 'proceed_to_ticket_creation',
                    'next_action': 'collect_ticket_data',
                    'session_data': session_data,
                    'ai_provider': 'azure_openai'
                }
        else:
            # Use Azure OpenAI to generate a helpful response
            try:
                context = "You are a helpful IT support assistant. The user has just received search results and is asking a follow-up question. If the search results don't help, suggest they can create a ticket."
                response = self.azure_openai.generate_response(message, context)
                
                # Add ticket creation option to response
                response += "\n\n**If these results don't help solve your issue, you can type 'create ticket' to submit a formal request.**"
                
                return {
                    'response': response,
                    'message_type': 'follow_up',
                    'next_action': 'continue_conversation',
                    'session_data': session_data,
                    'ai_provider': 'azure_openai'
                }
            except Exception as e:
                return {
                    'response': "I'm here to help! Is there anything specific about the search results you'd like to know more about?\n\n**If these results don't help solve your issue, you can type 'create ticket' to submit a formal request.**",
                    'message_type': 'follow_up',
                    'next_action': 'continue_conversation',
                    'session_data': session_data,
                    'ai_provider': 'azure_openai'
                }
    
    def _handle_unknown_stage(self, message: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unknown conversation stage"""
        return {
            'response': "I'm not sure what to do next. Let me start over and help you with your request.",
            'message_type': 'reset',
            'next_action': 'detect_intent',
            'session_data': {
                'intent': None,
                'confidence': 0.0,
                'rationale': '',
                'collected_data': {},
                'conversation_stage': 'intent_detection',
                'conversation_history': session_data['conversation_history']
            },
            'ai_provider': 'azure_openai'
        }
    
    def _is_direct_search_command(self, message: str) -> bool:
        """Check if message is a direct search command"""
        search_commands = ['search for', 'find', 'look for', 'show me']
        return any(cmd in message.lower() for cmd in search_commands)
    
    def _extract_field_from_question(self, question: str, intent: str) -> Optional[str]:
        """Extract field name from question"""
        # This is a simplified implementation
        # In a real system, you'd have more sophisticated field extraction
        field_mapping = {
            'short_description': ['brief description', 'what is the issue'],
            'detailed_description': ['more details', 'what\'s happening'],
            'impact_scope': ['who is affected', 'impact scope'],
            'urgency': ['how urgent', 'urgency level'],
            'affected_service': ['what service', 'affected system'],
            'start_time': ['when did this', 'start time'],
            'frequency': ['how often', 'frequency']
        }
        
        question_lower = question.lower()
        for field, keywords in field_mapping.items():
            if any(keyword in question_lower for keyword in keywords):
                return field
        
        return None
    
    def _format_search_results(self, search_results: Any, intent: str) -> str:
        """Format search results for display"""
        if not search_results:
            return "No results found."
        
        # Handle different result formats
        if isinstance(search_results, str):
            # If it's a string response from OCI Agent
            return f"## Search Results\n\n{search_results}"
        
        if isinstance(search_results, dict):
            formatted = "## Search Results\n\n"
            
            # Format ticket results
            if 'tickets' in search_results and search_results['tickets']:
                formatted += "### Related Tickets\n"
                for ticket in search_results['tickets'][:3]:  # Show top 3
                    formatted += f"- **{ticket.get('number', 'N/A')}**: {ticket.get('short_description', 'No description')}\n"
                    if ticket.get('url'):
                        formatted += f"  [View Ticket]({ticket['url']})\n"
                    formatted += "\n"
            
            # Format knowledge results
            if 'knowledge' in search_results and search_results['knowledge']:
                formatted += "### Knowledge Articles\n"
                for article in search_results['knowledge'][:3]:  # Show top 3
                    formatted += f"- **{article.get('title', 'No title')}**: {article.get('summary', 'No summary')}\n"
                    if article.get('url'):
                        formatted += f"  [Read Article]({article['url']})\n"
                    formatted += "\n"
            
            # If no specific format, show the raw results
            if not formatted.strip().endswith("## Search Results"):
                formatted += f"### Raw Results\n{str(search_results)[:500]}...\n"
            
            return formatted
        
        # Fallback for other formats
        return f"## Search Results\n\n{str(search_results)[:500]}..."
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _is_ticket_creation_intent(self, intent: str) -> bool:
        """Check if the intent is for ticket creation"""
        ticket_creation_intents = [
            'create_incident', 'create_request', 'create_change', 'create_problem',
            'submit_ticket', 'log_issue', 'create_ticket', 'report_issue'
        ]
        return intent.lower() in ticket_creation_intents
    
    def _handle_ticket_creation_phase(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ticket creation phase using Ticket Creation Agent"""
        try:
            if not self.ticket_creation_agent:
                return {
                    'response': "I'm sorry, ticket creation is not available at the moment. Please contact support directly.",
                    'message_type': 'error',
                    'next_action': 'contact_support',
                    'session_data': session_data,
                    'ai_provider': 'ticket_creation_agent'
                }
            
            # Prepare intent data
            intent_data = {
                'intent': session_data['intent'],
                'confidence': session_data.get('confidence', 0.0),
                'rationale': session_data.get('rationale', '')
            }
            
            # Prepare user context
            user_context = {
                'user_id': session_data.get('user_id', 'unknown'),
                'session_id': session_data.get('session_id', 'unknown'),
                'timestamp': self._get_timestamp()
            }
            
            # Call ticket creation agent
            result = self.ticket_creation_agent.create_ticket(
                intent_data,
                session_data['collected_data'],
                user_context
            )
            
            # Update session data
            session_data['conversation_stage'] = 'ticket_creation_complete'
            session_data['ticket_result'] = result
            
            return {
                'response': result.get('response', 'Ticket creation completed'),
                'message_type': 'ticket_creation_result',
                'next_action': 'present_result',
                'session_data': session_data,
                'ticket_result': result,
                'ai_provider': 'ticket_creation_agent'
            }
            
        except Exception as e:
            return {
                'response': f"I encountered an error while creating your ticket: {str(e)}. Please try again or contact support.",
                'message_type': 'error',
                'next_action': 'retry',
                'session_data': session_data,
                'ai_provider': 'ticket_creation_agent'
            }
    
    def handle_ticket_duplicate_decision(self, decision: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user decision regarding duplicate tickets"""
        try:
            if not self.ticket_creation_agent:
                return {
                    'response': "Ticket creation agent not available",
                    'message_type': 'error',
                    'next_action': 'retry',
                    'session_data': session_data
                }
            
            # Get duplicate data from session
            duplicate_data = session_data.get('duplicate_data', {})
            intent_data = {
                'intent': session_data['intent'],
                'confidence': session_data.get('confidence', 0.0),
                'rationale': session_data.get('rationale', '')
            }
            
            # Handle the decision
            result = self.ticket_creation_agent.handle_duplicate_decision(
                decision,
                duplicate_data,
                intent_data,
                session_data['collected_data'],
                {
                    'user_id': session_data.get('user_id', 'unknown'),
                    'session_id': session_data.get('session_id', 'unknown')
                }
            )
            
            # Update session data
            session_data['conversation_stage'] = 'duplicate_decision_handled'
            session_data['duplicate_decision_result'] = result
            
            return {
                'response': result.get('message', 'Decision processed'),
                'message_type': 'duplicate_decision_result',
                'next_action': result.get('action', 'continue'),
                'session_data': session_data,
                'decision_result': result,
                'ai_provider': 'ticket_creation_agent'
            }
            
        except Exception as e:
            return {
                'response': f"Error processing your decision: {str(e)}",
                'message_type': 'error',
                'next_action': 'retry',
                'session_data': session_data,
                'ai_provider': 'ticket_creation_agent'
            }
