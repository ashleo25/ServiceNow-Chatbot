#!/usr/bin/env python3
"""
Test Google ADK Ticket Creation Agent with correct model
"""
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.ticket_creation_agent import GoogleADKTicketCreationAgent


def test_google_adk_agent():
    """Test the Google ADK Ticket Creation Agent"""
    print("🧪 Testing Google ADK Ticket Creation Agent")
    print("=" * 50)
    
    try:
        # Initialize the agent
        print("📝 Initializing Google ADK Ticket Creation Agent...")
        agent = GoogleADKTicketCreationAgent()
        
        # Test the agent initialization
        print("🔧 Testing agent initialization...")
        
        # Test a simple ticket creation request
        test_request_data = {
            "intent": {
                "ticket_type": "incident",
                "category": "Network",
                "priority": "Medium",
                "urgency": "Medium"
            },
            "user_message": "I need help with my laptop not connecting to WiFi in the office",
            "collected_data": {
                "user_id": "test_user",
                "location": "office",
                "device": "laptop"
            }
        }
        
        print(f"📋 Test request: {test_request_data['user_message']}")
        print("🚀 Processing request...")
        
        # Create ticket (not async)
        result = agent.create_ticket(test_request_data)
        
        print("✅ Test Results:")
        print(f"   Response: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_google_adk_agent()
    if success:
        print("\n🎉 Google ADK Ticket Creation Agent test completed successfully!")
    else:
        print("\n💥 Google ADK Ticket Creation Agent test failed!")