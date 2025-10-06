"""
Intent Detection Service using OCI Generative AI
"""
import json
from typing import Dict, Any, Optional
from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import GenerateTextDetails
from config.config import Config

class IntentDetectionService:
    """Service for detecting user intent using OCI Generative AI"""
    
    def __init__(self):
        # Check if OCI configuration is available
        if (Config.OCI_TENANCY_ID and Config.OCI_USER_ID and 
            Config.OCI_FINGERPRINT and Config.OCI_PRIVATE_KEY_PATH and 
            Config.OCI_COMPARTMENT_ID):
            try:
                self.client = GenerativeAiInferenceClient(
                    config={
                        "region": Config.REGION,
                        "tenancy": Config.OCI_TENANCY_ID,
                        "user": Config.OCI_USER_ID,
                        "fingerprint": Config.OCI_FINGERPRINT,
                        "key_file": Config.OCI_PRIVATE_KEY_PATH
                    }
                )
                self.compartment_id = Config.OCI_COMPARTMENT_ID
                self.model_id = Config.OCI_MODEL_ID or "cohere.command"
                self.use_oci = True
                print("✅ OCI Generative AI client initialized")
            except Exception as e:
                print(f"⚠️ OCI client initialization failed: {e}")
                self.client = None
                self.use_oci = False
        else:
            print("⚠️ OCI configuration incomplete, using fallback intent detection")
            self.client = None
            self.use_oci = False
    
    def detect_intent(self, user_message: str, conversation_history: list = None) -> Dict[str, Any]:
        """
        Detect user intent from message
        
        Args:
            user_message (str): User's message
            conversation_history (list): Previous conversation context
            
        Returns:
            Dict with intent, confidence, and rationale
        """
        try:
            # Use fallback if OCI is not available
            if not self.use_oci:
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

            # Call OCI Generative AI
            from oci.generative_ai_inference.models import CohereLlmInferenceRequest, OnDemandServingMode
            
            inference_request = CohereLlmInferenceRequest(
                prompt=prompt,
                max_tokens=200,
                temperature=0.1
            )
            
            generate_text_details = GenerateTextDetails(
                compartment_id=self.compartment_id,
                serving_mode=OnDemandServingMode(model_id=self.model_id),
                inference_request=inference_request
            )
            
            response = self.client.generate_text(generate_text_details)
            
            # Parse the response
            response_text = response.data.choices[0].message.content.strip()
            
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
                print(f"Error parsing intent detection response: {e}")
            
            # Fallback to simple keyword-based detection
            return self._fallback_intent_detection(user_message)
            
        except Exception as e:
            print(f"Error in intent detection: {e}")
            return self._fallback_intent_detection(user_message)
    
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
