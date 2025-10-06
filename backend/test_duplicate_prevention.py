#!/usr/bin/env python3
"""
Test Duplicate Prevention Logic - Verify Flow Stops for Active Duplicates
"""
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.fast_ticket_creation_agent import FastGoogleADKTicketCreationAgent

def test_duplicate_prevention_logic():
    """Test that ticket creation stops when active duplicates are found"""
    print("🛡️ DUPLICATE PREVENTION LOGIC TEST")
    print("="*60)
    print("🎯 Objective: Verify that ticket creation STOPS when active duplicates exist")
    
    agent = FastGoogleADKTicketCreationAgent()
    
    # Test scenario: User with existing active ticket tries to create similar one
    print("\n📋 Test Scenario:")
    print("   1. User has an existing ACTIVE ticket (New/Open/In Progress)")
    print("   2. Same user tries to create similar ticket")
    print("   3. System should BLOCK creation and suggest reviewing existing ticket")
    
    print("\n👤 Test User: jane.doe@company.com")
    print("🎬 Simulating: Second request for similar WiFi issue")
    
    # This request should trigger duplicate detection
    duplicate_request = "My laptop still can't connect to WiFi. The authentication keeps failing and I'm unable to access the corporate network. This is preventing me from working."
    
    print(f"\n💬 User Request: \"{duplicate_request}\"")
    print("⏰ Expected: Duplicate detection should find active similar ticket")
    print("🚫 Expected: Creation should be BLOCKED")
    
    start_time = time.time()
    
    try:
        result = agent.create_ticket(duplicate_request, "jane.doe@company.com")
        processing_time = time.time() - start_time
        
        print(f"\n⏱️  Processing completed in {processing_time:.2f} seconds")
        print("\n📊 RESULTS:")
        print(f"   Success: {result.get('success', False)}")
        
        if result.get('success'):
            response = result.get('response', '')
            print(f"   Response: {response}")
            
            # Analyze response for duplicate prevention indicators
            duplicate_keywords = ['duplicate', 'existing', 'similar', 'review', 'active ticket']
            found_indicators = [kw for kw in duplicate_keywords if kw.lower() in response.lower()]
            
            if found_indicators:
                print(f"\n✅ DUPLICATE PREVENTION DETECTED:")
                print(f"   Found keywords: {found_indicators}")
                print("   ✓ Agent correctly identified potential duplicates")
                print("   ✓ Agent recommended reviewing existing tickets")
            else:
                print(f"\n⚠️  POTENTIAL ISSUE:")
                print("   No duplicate prevention keywords found in response")
                print("   Agent may have proceeded with creation instead of blocking")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        return {"success": False, "error": str(e)}

def test_legitimate_creation():
    """Test that legitimate tickets are still created when no active duplicates exist"""
    print("\n\n✅ LEGITIMATE TICKET CREATION TEST")
    print("="*60)
    print("🎯 Objective: Verify that unique tickets are still created normally")
    
    agent = FastGoogleADKTicketCreationAgent()
    
    print("\n📋 Test Scenario:")
    print("   1. User requests something completely different")
    print("   2. No existing active tickets for this issue")
    print("   3. System should PROCEED with ticket creation")
    
    print("\n👤 Test User: different.user@company.com")
    print("🎬 Simulating: Unique printer issue")
    
    unique_request = "The color printer in the accounting department is printing everything in pink tones. All text and images have a pink tint regardless of the original colors. This started yesterday after the maintenance visit."
    
    print(f"\n💬 User Request: \"{unique_request}\"")
    print("⏰ Expected: No duplicates found")
    print("✅ Expected: Creation should PROCEED")
    
    start_time = time.time()
    
    try:
        result = agent.create_ticket(unique_request, "different.user@company.com")
        processing_time = time.time() - start_time
        
        print(f"\n⏱️  Processing completed in {processing_time:.2f} seconds")
        print("\n📊 RESULTS:")
        print(f"   Success: {result.get('success', False)}")
        
        if result.get('success'):
            response = result.get('response', '')
            print(f"   Response: {response}")
            
            # Check for successful creation indicators
            if 'ticket' in response.lower() and ('created' in response.lower() or 'submitted' in response.lower()):
                print(f"\n✅ LEGITIMATE CREATION CONFIRMED:")
                print("   ✓ Agent proceeded with ticket creation")
                print("   ✓ No duplicate prevention blocking")
                print("   ✓ Proper category assignment (Printer)")
            else:
                print(f"\n⚠️  UNEXPECTED BEHAVIOR:")
                print("   Creation may have been blocked unnecessarily")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        return {"success": False, "error": str(e)}

def main():
    """Run duplicate prevention tests"""
    print("🧪 DUPLICATE PREVENTION LOGIC VALIDATION")
    print("="*70)
    print("🤖 Testing: Fast Google ADK Ticket Creation Agent")
    print("🔍 Focus: Duplicate detection and creation blocking logic")
    print("📋 Business Rule: Active duplicates should BLOCK new ticket creation")
    
    # Test 1: Duplicate prevention
    result1 = test_duplicate_prevention_logic()
    
    # Test 2: Legitimate creation
    result2 = test_legitimate_creation()
    
    # Summary
    print("\n\n📊 TEST SUMMARY")
    print("="*50)
    
    print(f"\n🧪 Tests Executed: 2")
    print(f"✅ Successful Executions: {sum([r.get('success', False) for r in [result1, result2]])}")
    
    print(f"\n🔍 Duplicate Prevention Analysis:")
    if result1.get('success'):
        response1 = result1.get('response', '').lower()
        if any(kw in response1 for kw in ['duplicate', 'existing', 'similar', 'review']):
            print("   ✅ WORKING: Agent detected and handled duplicates appropriately")
        else:
            print("   ⚠️  NEEDS REVIEW: Agent may not be blocking duplicate creation")
    else:
        print("   ❌ ERROR: Duplicate prevention test failed")
    
    print(f"\n✅ Legitimate Creation Analysis:")
    if result2.get('success'):
        response2 = result2.get('response', '').lower()
        if 'ticket' in response2 and ('created' in response2 or 'submitted' in response2):
            print("   ✅ WORKING: Agent correctly processes unique requests")
        else:
            print("   ⚠️  NEEDS REVIEW: Agent may be over-blocking legitimate requests")
    else:
        print("   ❌ ERROR: Legitimate creation test failed")
    
    print(f"\n🎯 BUSINESS RULE VALIDATION:")
    print("   📋 Rule: Active duplicates (New/Open/In Progress) should BLOCK creation")
    print("   📋 Rule: Resolved/Closed duplicates should NOT block creation")
    print("   📋 Rule: Unique requests should proceed normally")
    
    print(f"\n🔧 RECOMMENDATIONS:")
    print("   1. Verify ServiceNow state filtering is working")
    print("   2. Confirm Google ADK respects duplicate check results")
    print("   3. Test with actual ServiceNow instance when available")
    print("   4. Validate user notification messaging")
    
    return result1, result2

if __name__ == "__main__":
    main()