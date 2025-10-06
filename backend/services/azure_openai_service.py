"""
Azure OpenAI Service for Intent Detection and General AI Tasks
"""
import json
import os
from typing import Dict, Any, Optional, List
from openai import AzureOpenAI
from config.config import Config

class AzureOpenAIService:
    """Service for Azure OpenAI integration"""
    
    def __init__(self):
        # Azure OpenAI configuration
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        
        if not all([self.api_key, self.endpoint, self.deployment_name]):
            print("⚠️ Azure OpenAI configuration incomplete, using fallback")
            self.client = None
            self.use_azure = False
        else:
            try:
                self.client = AzureOpenAI(
                    api_key=self.api_key,
                    api_version=self.api_version,
                    azure_endpoint=self.endpoint
                )
                self.use_azure = True
                print("✅ Azure OpenAI client initialized")
            except Exception as e:
                print(f"⚠️ Azure OpenAI client initialization failed: {e}")
                self.client = None
                self.use_azure = False
    
    def detect_intent(self, user_message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Detect user intent using Azure OpenAI
        
        Args:
            user_message (str): User's message
            conversation_history (list): Previous conversation context
            
        Returns:
            Dict with intent, confidence, and rationale
        """
        try:
            if not self.use_azure:
                return self._fallback_intent_detection(user_message)
            
            # Build context from conversation history
            context = ""
            if conversation_history:
                context = "Previous conversation:\n"
                for msg in conversation_history[-3:]:  # Last 3 messages for context
                    context += f"{msg.get('role', 'user')}: {msg.get('content', '')}\n"
            
            prompt = f"""
You are an IT support intent classifier. Analyze the user's message and classify it into one of these categories:

1. Incident - Something is broken or not working
2. Request - Requesting a new service, access, or resource
3. Change - Requesting to modify existing systems or processes
4. Problem - Recurring issues or root cause analysis
5. Status - Checking status of existing tickets
6. Knowledge - Looking for information or documentation
7. Other - General questions or unclear intent

{context}

User message: "{user_message}"

Respond with a JSON object containing:
- intent: one of the categories above
- confidence: number between 0.0 and 1.0
- rationale: brief explanation of why this intent was chosen

Examples:
- "My laptop won't start" → {{"intent": "Incident", "confidence": 0.9, "rationale": "Hardware failure requiring immediate attention"}}
- "I need access to the database" → {{"intent": "Request", "confidence": 0.8, "rationale": "Requesting new access permissions"}}
- "Can you help me understand how to reset passwords?" → {{"intent": "Knowledge", "confidence": 0.7, "rationale": "Seeking procedural information"}}

JSON response:"""

            # Call Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are an expert IT support intent classifier. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            # Parse the response
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            try:
                # Find JSON in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    # Validate the result
                    if all(key in result for key in ['intent', 'confidence', 'rationale']):
                        return {
                            'intent': result['intent'],
                            'confidence': float(result['confidence']),
                            'rationale': result['rationale']
                        }
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Error parsing Azure OpenAI response: {e}")
            
            # Fallback to simple keyword-based detection
            return self._fallback_intent_detection(user_message)
            
        except Exception as e:
            print(f"Error in Azure OpenAI intent detection: {e}")
            return self._fallback_intent_detection(user_message)
    
    def generate_response(self, prompt: str, context: str = None) -> str:
        """
        Generate a response using Azure OpenAI
        
        Args:
            prompt (str): The prompt to send
            context (str): Additional context
            
        Returns:
            Generated response text
        """
        try:
            if not self.use_azure:
                return "Azure OpenAI not available"
            
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error in Azure OpenAI response generation: {e}")
            return "I'm sorry, I'm having trouble generating a response right now."
    
    def _fallback_intent_detection(self, user_message: str) -> Dict[str, Any]:
        """Fallback keyword-based intent detection"""
        message_lower = user_message.lower()
        
        # Incident keywords
        incident_keywords = ['broken', 'not working', 'error', 'failed', 'down', 'issue', 'problem', 'crash', 'hang']
        if any(keyword in message_lower for keyword in incident_keywords):
            return {'intent': 'Incident', 'confidence': 0.7, 'rationale': 'Detected incident keywords'}
        
        # Request keywords
        request_keywords = ['need', 'want', 'request', 'access', 'permission', 'account', 'user']
        if any(keyword in message_lower for keyword in request_keywords):
            return {'intent': 'Request', 'confidence': 0.6, 'rationale': 'Detected request keywords'}
        
        # Change keywords
        change_keywords = ['change', 'modify', 'update', 'upgrade', 'migrate', 'deploy']
        if any(keyword in message_lower for keyword in change_keywords):
            return {'intent': 'Change', 'confidence': 0.6, 'rationale': 'Detected change keywords'}
        
        # Status keywords
        status_keywords = ['status', 'check', 'ticket', 'progress', 'update']
        if any(keyword in message_lower for keyword in status_keywords):
            return {'intent': 'Status', 'confidence': 0.7, 'rationale': 'Detected status keywords'}
        
        # Knowledge keywords
        knowledge_keywords = ['how', 'what', 'where', 'when', 'why', 'help', 'guide', 'documentation']
        if any(keyword in message_lower for keyword in knowledge_keywords):
            return {'intent': 'Knowledge', 'confidence': 0.6, 'rationale': 'Detected knowledge keywords'}
        
        return {'intent': 'Other', 'confidence': 0.3, 'rationale': 'Unable to determine specific intent'}
