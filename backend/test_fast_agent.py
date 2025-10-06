#!/usr/bin/env python3
"""
Test the fast-loading Google ADK Ticket Creation Agent
"""
import sys
import os
import time

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.fast_ticket_creation_agent import FastGoogleADKTicketCreationAgent

def test_fast_agent():
    """Test the fast-loading agent"""
    print("🚀 Testing Fast Google ADK Ticket Creation Agent")
    print("=" * 55)
    
    try:
        # Test import and creation speed
        start_time = time.time()
        print("📝 Creating fast agent...")
        agent = FastGoogleADKTicketCreationAgent()
        creation_time = time.time() - start_time
        print(f"⚡ Agent created in {creation_time:.3f} seconds")
        
        # Test ticket creation (this will load dependencies)
        print("\n🎯 Testing ticket creation...")
        test_request = "My laptop screen keeps flickering and going black randomly, making it impossible to work on important presentations"
        
        start_time = time.time()
        result = agent.create_ticket(test_request, "john.doe@company.com")
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing took {processing_time:.2f} seconds")
        print("\n📋 Results:")
        print(f"   Success: {result.get('success', False)}")
        
        if result.get('success'):
            print(f"   Response: {result.get('response', 'No response')}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fast_agent()
    if success:
        print("\n🎉 Fast Google ADK agent test completed successfully!")
    else:
        print("\n💥 Fast Google ADK agent test failed!")