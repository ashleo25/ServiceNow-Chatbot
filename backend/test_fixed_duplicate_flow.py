#!/usr/bin/env python3
"""
Test Fixed Duplicate Flow - No Duplicates Should Continue Creation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.duplicate_check_agent import DuplicateCheckAgent
from unittest.mock import patch
from config.logging_config import get_logger

logger = get_logger("test_fixed_flow")


def test_no_duplicates_continues_creation():
    """Test that no duplicates found continues with ticket creation"""
    print("🧪 TESTING FIXED DUPLICATE FLOW")
    print("=" * 45)
    
    print("\n📋 Test Case: No Duplicates Found Should Continue Creation")
    
    try:
        # Mock no duplicates found
        mock_no_duplicates = []
        
        with patch('services.ticket_creation_service.ServiceNowTicketService.search_duplicates') as mock_search:
            mock_search.return_value = mock_no_duplicates
            
            duplicate_agent = DuplicateCheckAgent()
            
            test_ticket = {
                'short_description': 'New unique issue not seen before',
                'description': 'This is a completely new problem',
                'caller_id': 'admin'
            }
            
            result = duplicate_agent.check_duplicates(
                ticket_data=test_ticket,
                user_id='admin',
                ticket_type='incident'
            )
            
            print("✅ Duplicate Check Results:")
            print(f"   Has duplicates: {result.get('has_duplicates', False)}")
            print(f"   Should block: {result.get('should_block_creation', 'Not set')}")
            print(f"   Message: {result.get('message', 'N/A')}")
            
            # Verify correct behavior
            has_duplicates = result.get('has_duplicates', False)
            should_block = result.get('should_block_creation', False)  # Default False = allow creation
            
            if not has_duplicates and not should_block:
                print("🎉 SUCCESS: No duplicates found, creation should continue!")
                print("✅ Workflow: check_duplicates → assign_priority → create_ticket")
                print("💡 should_block_creation not set = allow creation")
                return True
            else:
                print("❌ FAILURE: Logic error in duplicate handling")
                print(f"   Expected: has_duplicates=False, should_block=False")
                print(f"   Got: has_duplicates={has_duplicates}, should_block={should_block}")
                return False
    
    except Exception as e:
        print(f"❌ TEST FAILED: {str(e)}")
        return False


def test_resolved_duplicates_continues_creation():
    """Test that resolved duplicates allow new ticket creation"""
    print("\n📋 Test Case: Resolved Duplicates Should Continue Creation")
    
    try:
        # Mock resolved duplicates
        mock_resolved_duplicates = [{
            'sys_id': 'mock123',
            'number': 'INC0000123',
            'short_description': 'Similar issue but resolved',
            'description': 'This was fixed already',
            'category': 'Network',
            'priority': '3',
            'state': '6',  # Resolved - should NOT block
            'caller_id': 'admin',
            'created': '2025-10-05'
        }]
        
        with patch('services.ticket_creation_service.ServiceNowTicketService.search_duplicates') as mock_search:
            mock_search.return_value = mock_resolved_duplicates
            
            duplicate_agent = DuplicateCheckAgent()
            
            test_ticket = {
                'short_description': 'Similar network issue happening again',
                'description': 'Network problems like before',
                'caller_id': 'admin'
            }
            
            result = duplicate_agent.check_duplicates(
                ticket_data=test_ticket,
                user_id='admin',
                ticket_type='incident'
            )
            
            print("✅ Duplicate Check Results:")
            print(f"   Has duplicates: {result.get('has_duplicates', False)}")
            print(f"   Should block: {result.get('should_block_creation', 'Not set')}")
            print(f"   Message: {result.get('message', 'N/A')}")
            
            # Verify correct behavior
            has_duplicates = result.get('has_duplicates', False)
            should_block = result.get('should_block_creation', True)  # Default True to catch errors
            
            if has_duplicates and not should_block:
                print("🎉 SUCCESS: Resolved duplicates found but creation continues!")
                print("✅ Workflow: check_duplicates → assign_priority → create_ticket")
                print("💡 Note: Resolved tickets shown for reference only")
                return True
            else:
                print("❌ FAILURE: Resolved duplicates should not block creation")
                print(f"   Expected: has_duplicates=True, should_block=False")
                print(f"   Got: has_duplicates={has_duplicates}, should_block={should_block}")
                return False
                
    except Exception as e:
        print(f"❌ TEST FAILED: {str(e)}")
        return False


def test_active_duplicates_blocks_creation():
    """Test that active duplicates still block creation (regression test)"""
    print("\n📋 Test Case: Active Duplicates Should Block Creation")
    
    try:
        # Mock active duplicates
        mock_active_duplicates = [{
            'sys_id': 'mock124',
            'number': 'INC0000124',
            'short_description': 'Same active issue',
            'description': 'This is still open',
            'category': 'Network',
            'priority': '3',
            'state': '2',  # In Progress - should BLOCK
            'caller_id': 'admin',
            'created': '2025-10-06'
        }]
        
        with patch('services.ticket_creation_service.ServiceNowTicketService.search_duplicates') as mock_search:
            mock_search.return_value = mock_active_duplicates
            
            duplicate_agent = DuplicateCheckAgent()
            
            test_ticket = {
                'short_description': 'Same network issue again',
                'description': 'Network problems still happening',
                'caller_id': 'admin'
            }
            
            result = duplicate_agent.check_duplicates(
                ticket_data=test_ticket,
                user_id='admin',
                ticket_type='incident'
            )
            
            print("✅ Duplicate Check Results:")
            print(f"   Has duplicates: {result.get('has_duplicates', False)}")
            print(f"   Should block: {result.get('should_block_creation', 'Not set')}")
            print(f"   Active count: {result.get('active_count', 0)}")
            print(f"   Message: {result.get('message', 'N/A')}")
            
            # Verify correct behavior
            has_duplicates = result.get('has_duplicates', False)
            should_block = result.get('should_block_creation', False)
            active_count = result.get('active_count', 0)
            
            if has_duplicates and should_block and active_count > 0:
                print("🎉 SUCCESS: Active duplicates correctly block creation!")
                print("🚫 Workflow: check_duplicates → STOP (no further functions)")
                return True
            else:
                print("❌ FAILURE: Active duplicates should block creation")
                print(f"   Expected: has_duplicates=True, should_block=True, active_count>0")
                print(f"   Got: has_duplicates={has_duplicates}, should_block={should_block}, active_count={active_count}")
                return False
                
    except Exception as e:
        print(f"❌ TEST FAILED: {str(e)}")
        return False


if __name__ == "__main__":
    print("🧪 TESTING FIXED DUPLICATE WORKFLOW")
    print("Verifying: No duplicates → Continue creation")
    print("Verifying: Resolved duplicates → Continue creation")
    print("Verifying: Active duplicates → Block creation")
    
    test1 = test_no_duplicates_continues_creation()
    test2 = test_resolved_duplicates_continues_creation()
    test3 = test_active_duplicates_blocks_creation()
    
    print("\n🎯 TEST SUMMARY")
    print("=" * 30)
    print(f"✅ No duplicates continue: {'PASS' if test1 else 'FAIL'}")
    print(f"✅ Resolved duplicates continue: {'PASS' if test2 else 'FAIL'}")
    print(f"✅ Active duplicates block: {'PASS' if test3 else 'FAIL'}")
    
    all_passed = test1 and test2 and test3
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ DUPLICATE FLOW IS WORKING CORRECTLY!")
        print("🚀 Ready for ServiceNow ticket creation testing")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("🔧 Need to review duplicate logic")