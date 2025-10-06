"""
Conversation Manager for handling structured data collection
"""
from typing import Dict, Any, List, Optional
from enum import Enum
import json

class IntentType(Enum):
    INCIDENT = "Incident"
    REQUEST = "Request"
    CHANGE = "Change"
    PROBLEM = "Problem"
    STATUS = "Status"
    KNOWLEDGE = "Knowledge"
    OTHER = "Other"

class ConversationManager:
    """Manages conversation flow and data collection for different intents"""
    
    def __init__(self):
        self.required_fields = {
            IntentType.INCIDENT: [
                "short_description", "detailed_description", "impact_scope", 
                "urgency", "affected_service", "start_time", "frequency"
            ],
            IntentType.REQUEST: [
                "what_requested", "business_justification", "needed_by_date"
            ],
            IntentType.CHANGE: [
                "change_type", "what_will_change", "planned_start", 
                "planned_end", "risk_plan", "affected_services"
            ],
            IntentType.PROBLEM: [
                "pattern_symptom", "impacted_groups"
            ],
            IntentType.STATUS: [
                "ticket_numbers"
            ],
            IntentType.KNOWLEDGE: [
                "topic_area"
            ]
        }
        
        self.optional_fields = {
            IntentType.INCIDENT: ["screenshots", "contact_preference", "time_window"],
            IntentType.REQUEST: ["approver", "cost_center"],
            IntentType.CHANGE: [],
            IntentType.PROBLEM: ["known_workarounds"],
            IntentType.STATUS: [],
            IntentType.KNOWLEDGE: ["symptoms", "environment"]
        }
        
        self.field_questions = {
            IntentType.INCIDENT: {
                "short_description": "What is the issue? Please provide a brief description.",
                "detailed_description": "Can you provide more details about what's happening?",
                "impact_scope": "Who is affected? (self, team, department, or organization)",
                "urgency": "How urgent is this? (low, medium, high, or critical)",
                "affected_service": "What service or system is affected?",
                "start_time": "When did this issue start?",
                "frequency": "How often does this happen? (one-time, daily, weekly, etc.)",
                "screenshots": "Do you have any screenshots or error messages?",
                "contact_preference": "How would you prefer to be contacted?",
                "time_window": "What's the best time to contact you?"
            },
            IntentType.REQUEST: {
                "what_requested": "What are you requesting?",
                "business_justification": "What's the business justification for this request?",
                "needed_by_date": "When do you need this by?",
                "approver": "Who should approve this request?",
                "cost_center": "What's the cost center or project code?"
            },
            IntentType.CHANGE: {
                "change_type": "What type of change is this? (standard, normal, or emergency)",
                "what_will_change": "What will change and why?",
                "planned_start": "When do you plan to start this change?",
                "planned_end": "When do you plan to complete this change?",
                "risk_plan": "What are the risks and rollback plan?",
                "affected_services": "What services or systems will be affected?"
            },
            IntentType.PROBLEM: {
                "pattern_symptom": "What pattern or recurring symptom are you experiencing?",
                "impacted_groups": "Which user groups or services are impacted?",
                "known_workarounds": "Are there any known workarounds?"
            },
            IntentType.STATUS: {
                "ticket_numbers": "What are the ticket numbers you'd like to check?"
            },
            IntentType.KNOWLEDGE: {
                "topic_area": "What topic or product area are you looking for information about?",
                "symptoms": "What symptoms or issues are you experiencing?",
                "environment": "What environment are you working in?"
            }
        }
    
    def get_next_question(self, session_data: Dict[str, Any]) -> Optional[str]:
        """Get the next question to ask based on current session data"""
        intent = session_data.get('intent')
        collected_data = session_data.get('collected_data', {})
        
        if not intent:
            return None
        
        try:
            intent_enum = IntentType(intent)
        except ValueError:
            return None
        
        # Check required fields first
        required = self.required_fields.get(intent_enum, [])
        for field in required:
            if field not in collected_data or not collected_data[field]:
                return self.field_questions[intent_enum].get(field, f"Please provide {field.replace('_', ' ')}")
        
        # Check optional fields
        optional = self.optional_fields.get(intent_enum, [])
        for field in optional:
            if field not in collected_data or not collected_data[field]:
                return self.field_questions[intent_enum].get(field, f"Please provide {field.replace('_', ' ')}")
        
        return None  # All fields collected
    
    def is_data_collection_complete(self, session_data: Dict[str, Any]) -> bool:
        """Check if all required data has been collected"""
        intent = session_data.get('intent')
        collected_data = session_data.get('collected_data', {})
        
        if not intent:
            return False
        
        try:
            intent_enum = IntentType(intent)
        except ValueError:
            return False
        
        required = self.required_fields.get(intent_enum, [])
        return all(field in collected_data and collected_data[field] for field in required)
    
    def update_session_data(self, session_data: Dict[str, Any], field: str, value: str) -> Dict[str, Any]:
        """Update session data with new field value"""
        if 'collected_data' not in session_data:
            session_data['collected_data'] = {}
        
        session_data['collected_data'][field] = value
        return session_data
    
    def get_data_summary(self, session_data: Dict[str, Any]) -> str:
        """Generate a summary of collected data"""
        intent = session_data.get('intent', 'Unknown')
        collected_data = session_data.get('collected_data', {})
        
        summary = f"**{intent} Request Summary:**\n\n"
        
        for field, value in collected_data.items():
            if value:
                display_name = field.replace('_', ' ').title()
                summary += f"• **{display_name}:** {value}\n"
        
        return summary
    
    def build_search_query(self, session_data: Dict[str, Any]) -> str:
        """Build a search query from collected data"""
        intent = session_data.get('intent', '')
        collected_data = session_data.get('collected_data', {})
        
        query_parts = []
        
        if intent == IntentType.INCIDENT.value:
            if collected_data.get('short_description'):
                query_parts.append(collected_data['short_description'])
            if collected_data.get('affected_service'):
                query_parts.append(collected_data['affected_service'])
            if collected_data.get('detailed_description'):
                query_parts.append(collected_data['detailed_description'])
        
        elif intent == IntentType.REQUEST.value:
            if collected_data.get('what_requested'):
                query_parts.append(collected_data['what_requested'])
            if collected_data.get('business_justification'):
                query_parts.append(collected_data['business_justification'])
        
        elif intent == IntentType.CHANGE.value:
            if collected_data.get('what_will_change'):
                query_parts.append(collected_data['what_will_change'])
            if collected_data.get('affected_services'):
                query_parts.append(collected_data['affected_services'])
        
        elif intent == IntentType.PROBLEM.value:
            if collected_data.get('pattern_symptom'):
                query_parts.append(collected_data['pattern_symptom'])
            if collected_data.get('impacted_groups'):
                query_parts.append(collected_data['impacted_groups'])
        
        elif intent == IntentType.KNOWLEDGE.value:
            if collected_data.get('topic_area'):
                query_parts.append(collected_data['topic_area'])
            if collected_data.get('symptoms'):
                query_parts.append(collected_data['symptoms'])
        
        return " ".join(query_parts) if query_parts else intent.lower()
    
    def get_greeting_message(self) -> str:
        """Get the initial greeting message"""
        return """👋 Hello! I'm your IT Support Assistant powered by Oracle Cloud Infrastructure.

I can help you with:
• **Incidents** - Something is broken or not working
• **Requests** - New services, access, or resources
• **Changes** - Modifying existing systems
• **Problems** - Recurring issues or root cause analysis
• **Status** - Check existing ticket status
• **Knowledge** - Find documentation and guides

What can I help you with today?"""
