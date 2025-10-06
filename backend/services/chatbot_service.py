"""
Main Chatbot Service that orchestrates intent detection, conversation management, and search
"""
from typing import Dict, Any, List, Optional
from services.intent_detection import IntentDetectionService
from services.conversation_manager import ConversationManager, IntentType
from agents.oci_compliant_core_search_agent import OciCompliantCoreSearchAgent
import json

class ChatbotService:
    """Main chatbot service that handles the complete conversation flow"""
    
    def __init__(self):
        self.intent_detector = IntentDetectionService()
        self.conversation_manager = ConversationManager()
        # Note: OciCompliantCoreSearchAgent requires AgentClient
        # For now, keeping existing functionality
        self.search_service = None  # Will be initialized when AgentClient is available
    
    def process_message(self, message: str, session_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a user message and return appropriate response
        
        Args:
            message (str): User's message
            session_data (dict): Current session data
            
        Returns:
            Dict with response, session_data, and next_action
        """
        if session_data is None:
            session_data = {
                'intent': None,
                'confidence': 0.0,
                'collected_data': {},
                'conversation_stage': 'greeting',
                'conversation_history': []
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
        """Handle initial greeting and detect intent from first message"""
        # If this is the first message and it's not just a greeting, detect intent
        if message.strip() and not any(greeting_word in message.lower() for greeting_word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            # Detect intent from the first message
            intent_result = self.intent_detector.detect_intent(message, session_data['conversation_history'])
            
            session_data['intent'] = intent_result['intent']
            session_data['confidence'] = intent_result['confidence']
            session_data['rationale'] = intent_result['rationale']
            
            # If confidence is good, move to data collection
            if intent_result['confidence'] >= 0.5:
                session_data['conversation_stage'] = 'data_collection'
                next_question = self.conversation_manager.get_next_question(session_data)
                
                response = f"Got it! I understand you need help with **{intent_result['intent']}** issues. {intent_result['rationale']}\n\n"
                response += f"{next_question}"
                
                return {
                    'response': response,
                    'session_data': session_data,
                    'next_action': 'collect_data',
                    'message_type': 'data_collection'
                }
            else:
                # Low confidence, ask for clarification
                session_data['conversation_stage'] = 'intent_detection'
                clarification_question = self._get_clarification_question(intent_result['intent'])
                return {
                    'response': f"I think you might be asking about **{intent_result['intent']}** issues, but I'm not completely sure. {clarification_question}",
                    'session_data': session_data,
                    'next_action': 'wait_for_clarification',
                    'message_type': 'clarification'
                }
        else:
            # Show greeting and move to intent detection
            greeting = self.conversation_manager.get_greeting_message()
            session_data['conversation_stage'] = 'intent_detection'
            
            return {
                'response': greeting,
                'session_data': session_data,
                'next_action': 'wait_for_intent',
                'message_type': 'greeting'
            }
    
    def _handle_intent_detection(self, message: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intent detection"""
        # Detect intent
        intent_result = self.intent_detector.detect_intent(message, session_data['conversation_history'])
        
        session_data['intent'] = intent_result['intent']
        session_data['confidence'] = intent_result['confidence']
        session_data['rationale'] = intent_result['rationale']
        
        # If confidence is low, ask for clarification
        if intent_result['confidence'] < 0.5:
            clarification_question = self._get_clarification_question(intent_result['intent'])
            return {
                'response': f"I think you might be asking about **{intent_result['intent']}** issues, but I'm not completely sure. {clarification_question}",
                'session_data': session_data,
                'next_action': 'wait_for_clarification',
                'message_type': 'clarification'
            }
        
        # Move to data collection
        session_data['conversation_stage'] = 'data_collection'
        
        # Get first question
        next_question = self.conversation_manager.get_next_question(session_data)
        
        response = f"Got it! I understand you need help with **{intent_result['intent']}** issues. {intent_result['rationale']}\n\n"
        response += f"{next_question}"
        
        return {
            'response': response,
            'session_data': session_data,
            'next_action': 'collect_data',
            'message_type': 'data_collection'
        }
    
    def _handle_data_collection(self, message: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data collection phase"""
        # Determine which field this answer is for
        next_question = self.conversation_manager.get_next_question(session_data)
        
        if next_question:
            # Extract field name from the question
            field_name = self._extract_field_from_question(next_question, session_data['intent'])
            if field_name:
                session_data = self.conversation_manager.update_session_data(session_data, field_name, message)
            
            # Get next question
            next_question = self.conversation_manager.get_next_question(session_data)
            
            if next_question:
                # Show confirmation of what was collected
                confirmation = self._get_field_confirmation(field_name, message)
                response = f"{confirmation}\n\n{next_question}"
                
                return {
                    'response': response,
                    'session_data': session_data,
                    'next_action': 'collect_data',
                    'message_type': 'data_collection'
                }
        
        # All data collected, move to search
        return self._handle_search_phase(session_data)
    
    def _handle_search_phase(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search phase after data collection is complete"""
        # Build search query
        search_query = self.conversation_manager.build_search_query(session_data)
        
        # Perform search
        search_results = self.search_service.search_all(search_query, session_data['intent'])
        
        # Format results
        formatted_results = self._format_search_results(search_results, session_data['intent'])
        
        # Show data summary
        data_summary = self.conversation_manager.get_data_summary(session_data)
        
        response = f"{data_summary}\n\n{formatted_results}"
        
        session_data['conversation_stage'] = 'search_results'
        session_data['search_results'] = search_results
        
        return {
            'response': response,
            'session_data': session_data,
            'next_action': 'show_results',
            'message_type': 'search_results',
            'search_results': search_results
        }
    
    def _handle_search_results(self, message: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user interaction with search results"""
        # Check if user wants to start over or ask follow-up questions
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['new', 'start over', 'reset', 'another']):
            # Reset session
            session_data = {
                'intent': None,
                'confidence': 0.0,
                'collected_data': {},
                'conversation_stage': 'intent_detection',
                'conversation_history': session_data['conversation_history']
            }
            
            return {
                'response': "Sure! Let's start fresh. What can I help you with today?",
                'session_data': session_data,
                'next_action': 'wait_for_intent',
                'message_type': 'reset'
            }
        
        # Handle follow-up questions
        if any(word in message_lower for word in ['more', 'details', 'explain', 'how']):
            return {
                'response': "I'd be happy to provide more details. Could you be more specific about what you'd like to know more about?",
                'session_data': session_data,
                'next_action': 'wait_for_followup',
                'message_type': 'followup'
            }
        
        # Default response
        return {
            'response': "Is there anything else I can help you with? You can ask for more details about the results or start a new request.",
            'session_data': session_data,
            'next_action': 'wait_for_response',
            'message_type': 'general'
        }
    
    def _handle_unknown_stage(self, message: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unknown conversation stage"""
        return {
            'response': "I'm not sure how to help with that. Let's start over - what can I help you with today?",
            'session_data': {
                'intent': None,
                'confidence': 0.0,
                'collected_data': {},
                'conversation_stage': 'intent_detection',
                'conversation_history': []
            },
            'next_action': 'wait_for_intent',
            'message_type': 'reset'
        }
    
    def _get_clarification_question(self, intent: str) -> str:
        """Get clarification question based on intent"""
        clarification_questions = {
            'Incident': "Are you reporting something that's broken or not working?",
            'Request': "Are you asking for a new service, access, or resource?",
            'Change': "Do you need to modify or update an existing system?",
            'Problem': "Are you experiencing recurring issues that need investigation?",
            'Status': "Do you want to check the status of existing tickets?",
            'Knowledge': "Are you looking for information or documentation?",
            'Other': "Could you provide more details about what you need help with?"
        }
        return clarification_questions.get(intent, "Could you provide more details?")
    
    def _extract_field_from_question(self, question: str, intent: str) -> Optional[str]:
        """Extract field name from question"""
        # This is a simplified approach - in practice, you'd want more sophisticated matching
        field_mapping = {
            'Incident': {
                'issue': 'short_description',
                'details': 'detailed_description',
                'affected': 'impact_scope',
                'urgent': 'urgency',
                'service': 'affected_service',
                'started': 'start_time',
                'often': 'frequency'
            },
            'Request': {
                'requesting': 'what_requested',
                'justification': 'business_justification',
                'needed by': 'needed_by_date'
            },
            'Change': {
                'type of change': 'change_type',
                'change': 'what_will_change',
                'start': 'planned_start',
                'end': 'planned_end',
                'risk': 'risk_plan',
                'affected': 'affected_services'
            },
            'Problem': {
                'pattern': 'pattern_symptom',
                'groups': 'impacted_groups',
                'workaround': 'known_workarounds'
            },
            'Status': {
                'ticket': 'ticket_numbers'
            },
            'Knowledge': {
                'topic': 'topic_area',
                'symptoms': 'symptoms',
                'environment': 'environment'
            }
        }
        
        intent_mapping = field_mapping.get(intent, {})
        question_lower = question.lower()
        
        for keyword, field in intent_mapping.items():
            if keyword in question_lower:
                return field
        
        return None
    
    def _get_field_confirmation(self, field_name: str, value: str) -> str:
        """Get confirmation message for collected field"""
        if not field_name:
            return "Thank you for that information."
        
        display_name = field_name.replace('_', ' ').title()
        return f"✅ **{display_name}:** {value}"
    
    def _format_search_results(self, search_results: Dict[str, Any], intent: str) -> str:
        """Format search results for display"""
        response = "🔍 **Search Results:**\n\n"
        
        # Format ticket results
        tickets = search_results.get('tickets', {})
        if tickets.get('tickets'):
            response += f"📋 **Found {tickets['total_count']} related tickets:**\n\n"
            
            for i, ticket in enumerate(tickets['tickets'][:5], 1):
                response += f"{i}. **[{ticket['number']}]({ticket['url']})** - {ticket['title']}\n"
                response += f"   Status: {ticket['state']}, Priority: {ticket['priority']}\n"
                response += f"   Created: {ticket['created']}\n\n"
        
        # Format knowledge base results
        knowledge = search_results.get('knowledge', {})
        if knowledge.get('articles'):
            response += f"📚 **Found {knowledge['total_count']} knowledge articles:**\n\n"
            
            for i, article in enumerate(knowledge['articles'][:3], 1):
                response += f"{i}. **[{article['title']}]({article['url']})**\n"
                response += f"   Category: {article['category']}\n"
                response += f"   Updated: {article['updated']}\n\n"
        
        if not tickets.get('tickets') and not knowledge.get('articles'):
            response += "No relevant tickets or knowledge articles found. You may want to create a new ticket for this issue.\n\n"
        
        response += "💡 **Next Steps:**\n"
        response += "• Click on any ticket or article link to view details\n"
        response += "• If you need to create a new ticket, let me know\n"
        response += "• Ask me for more details about any result\n"
        response += "• Type 'new' to start a different request\n"
        
        return response
    
    def _is_direct_search_command(self, message: str) -> bool:
        """Check if the message is a direct search command"""
        message_lower = message.lower()
        search_keywords = [
            'search for similar issues',
            'search for similar',
            'find similar issues',
            'find similar',
            'look for similar',
            'search similar',
            'find related',
            'search related',
            'look up',
            'search tickets',
            'find tickets',
            'search knowledge',
            'find articles'
        ]
        
        return any(keyword in message_lower for keyword in search_keywords)
    
    def _handle_direct_search(self, message: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle direct search commands"""
        # Extract the search query from the message
        search_query = self._extract_search_query(message)
        
        if not search_query:
            return {
                'response': "I'd be happy to search for similar issues! Could you please tell me what specific problem or topic you'd like me to search for?",
                'session_data': session_data,
                'next_action': 'wait_for_search_query',
                'message_type': 'clarification'
            }
        
        # Perform the search
        try:
            # Determine search type based on query content
            search_type = self._determine_search_type(search_query)
            
            # Perform search using enhanced search service
            search_results = self.search_service.search_all(search_query, 'Other')
            
            # Format the results
            formatted_response = self._format_direct_search_results(search_results, search_query)
            
            # Update session data
            session_data['conversation_stage'] = 'search_results'
            session_data['search_results'] = search_results
            session_data['last_search_query'] = search_query
            
            return {
                'response': formatted_response,
                'session_data': session_data,
                'next_action': 'show_search_results',
                'message_type': 'search_results',
                'search_results': search_results
            }
            
        except Exception as e:
            return {
                'response': f"I encountered an error while searching: {str(e)}. Please try again or rephrase your search query.",
                'session_data': session_data,
                'next_action': 'wait_for_retry',
                'message_type': 'error'
            }
    
    def _extract_search_query(self, message: str) -> str:
        """Extract the actual search query from a direct search command"""
        message_lower = message.lower()
        
        # Remove common search command phrases
        search_phrases_to_remove = [
            'search for similar issues on',
            'search for similar issues',
            'search for similar',
            'find similar issues on',
            'find similar issues',
            'find similar',
            'look for similar issues on',
            'look for similar issues',
            'look for similar',
            'search similar issues on',
            'search similar issues',
            'search similar',
            'find related to',
            'find related',
            'search related to',
            'search related',
            'look up',
            'search tickets for',
            'search tickets',
            'find tickets for',
            'find tickets',
            'search knowledge for',
            'search knowledge',
            'find articles about',
            'find articles'
        ]
        
        # Find and remove the search command phrase
        for phrase in search_phrases_to_remove:
            if phrase in message_lower:
                # Remove the phrase and clean up
                query = message.replace(phrase, '').strip()
                # Remove any remaining "on" or "about" at the beginning
                query = query.lstrip('on ').lstrip('about ').strip()
                return query
        
        # If no specific phrase found, return the original message
        return message.strip()
    
    def _determine_search_type(self, query: str) -> str:
        """Determine the type of search based on query content"""
        query_lower = query.lower()
        
        # Check for specific keywords that indicate search type
        if any(word in query_lower for word in ['ticket', 'incident', 'problem', 'change', 'request']):
            return 'servicenow'
        elif any(word in query_lower for word in ['how to', 'guide', 'procedure', 'documentation', 'article']):
            return 'knowledge'
        else:
            return 'all'  # Search both
    
    def _format_direct_search_results(self, search_results: Dict[str, Any], query: str) -> str:
        """Format direct search results for display with professional styling"""
        response = f"## 🔍 Search Results for: \"{query}\"\n\n"
        
        # Format ticket results
        tickets = search_results.get('tickets', {})
        if tickets.get('tickets'):
            response += f"### 📋 Related Tickets ({tickets['total_count']} found)\n\n"
            
            for i, ticket in enumerate(tickets['tickets'][:8], 1):
                # Format priority and status with emojis
                priority_emoji = self._get_priority_emoji(ticket.get('priority', ''))
                status_emoji = self._get_status_emoji(ticket.get('state', ''))
                
                response += f"**{i}. [{ticket['number']}]({ticket['url']})** {priority_emoji}\n"
                response += f"   **Title:** {ticket['title']}\n"
                response += f"   **Status:** {status_emoji} {ticket['state']} | **Priority:** {priority_emoji} {ticket['priority']}\n"
                
                # Add category if available
                if ticket.get('category'):
                    response += f"   **Category:** {ticket['category']}\n"
                
                # Format dates
                created_date = self._format_date(ticket.get('created', ''))
                response += f"   **Created:** {created_date}\n"
                
                # Add relevance score if available
                if 'relevance_score' in ticket:
                    relevance_percent = int(ticket['relevance_score'] * 100)
                    response += f"   **Relevance:** {relevance_percent}%\n"
                
                response += "\n"
        else:
            response += "### 📋 Related Tickets\n\n"
            response += "No related tickets found. This might be a new issue that hasn't been reported yet.\n\n"
        
        # Format knowledge base results
        knowledge = search_results.get('knowledge', {})
        if knowledge.get('articles'):
            response += f"### 📚 Knowledge Articles ({knowledge['total_count']} found)\n\n"
            
            for i, article in enumerate(knowledge['articles'][:5], 1):
                response += f"**{i}. [{article['title']}]({article['url']})**\n"
                
                if article.get('category'):
                    response += f"   **Category:** {article['category']}\n"
                
                # Format dates
                updated_date = self._format_date(article.get('updated', ''))
                response += f"   **Updated:** {updated_date}\n"
                
                # Add view count if available
                if article.get('view_count', 0) > 0:
                    response += f"   **Views:** {article['view_count']}\n"
                
                # Add relevance score if available
                if 'relevance_score' in article:
                    relevance_percent = int(article['relevance_score'] * 100)
                    response += f"   **Relevance:** {relevance_percent}%\n"
                
                response += "\n"
        else:
            response += "### 📚 Knowledge Articles\n\n"
            response += "No knowledge articles found. You might want to create a new ticket for this issue.\n\n"
        
        # Add helpful next steps
        response += "---\n\n"
        response += "### 💡 Next Steps\n\n"
        response += "• **Click any link** to view full details in ServiceNow\n"
        response += "• **Ask for more details** about any specific result\n"
        response += "• **Search again** with different keywords\n"
        response += "• **Create a new ticket** if this is a new issue\n"
        
        return response
    
    def _get_priority_emoji(self, priority: str) -> str:
        """Get emoji for priority level"""
        priority_lower = priority.lower()
        if '1' in priority_lower or 'critical' in priority_lower:
            return "🔴"
        elif '2' in priority_lower or 'high' in priority_lower:
            return "🟠"
        elif '3' in priority_lower or 'medium' in priority_lower:
            return "🟡"
        elif '4' in priority_lower or 'low' in priority_lower:
            return "🟢"
        else:
            return "⚪"
    
    def _get_status_emoji(self, state: str) -> str:
        """Get emoji for ticket status"""
        state_lower = state.lower()
        if state_lower in ['new', 'open']:
            return "🆕"
        elif state_lower in ['in progress', 'assigned', 'work in progress']:
            return "🔄"
        elif state_lower in ['resolved', 'closed']:
            return "✅"
        elif state_lower in ['cancelled', 'cancelled by user']:
            return "❌"
        elif state_lower in ['pending', 'waiting']:
            return "⏳"
        else:
            return "📋"
    
    def _format_date(self, date_str: str) -> str:
        """Format date string for display"""
        if not date_str:
            return "Unknown"
        
        try:
            # Parse ServiceNow date format
            if 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            
            # Calculate relative time
            now = datetime.now()
            diff = now - date_obj.replace(tzinfo=None)
            
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                return "Just now"
        except:
            return date_str

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
