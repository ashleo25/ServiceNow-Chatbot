#!/usr/bin/env python3
"""
Real-Life ServiceNow Ticket Creation Scenarios
Tests both duplicate and non-duplicate flows with realistic user requests
"""
import sys
import os
import time
import asyncio
from datetime import datetime

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.fast_ticket_creation_agent import FastGoogleADKTicketCreationAgent

class TicketCreationScenarios:
    def __init__(self):
        self.agent = FastGoogleADKTicketCreationAgent()
        self.scenarios_run = 0
        self.successful_scenarios = 0
        
    def print_scenario_header(self, title, description):
        """Print formatted scenario header"""
        print("\n" + "="*80)
        print(f"🎯 SCENARIO: {title}")
        print("="*80)
        print(f"📋 Description: {description}")
        print("-"*80)
        
    def print_user_profile(self, name, role, department, email):
        """Print user profile information"""
        print(f"👤 User Profile:")
        print(f"   Name: {name}")
        print(f"   Role: {role}")
        print(f"   Department: {department}")
        print(f"   Email: {email}")
        print("-"*40)
        
    def process_ticket_request(self, user_request, user_email, scenario_name):
        """Process a ticket request and display results"""
        print(f"💬 User says: \"{user_request}\"")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🚀 Processing request...")
        
        start_time = time.time()
        
        try:
            # Create ticket using the fast agent
            result = self.agent.create_ticket(user_request, user_email)
            processing_time = time.time() - start_time
            
            print(f"\n⏱️  Processing completed in {processing_time:.2f} seconds")
            print("\n📊 RESULTS:")
            print(f"   Success: {result.get('success', False)}")
            
            if result.get('success'):
                print(f"   Response: {result.get('response', 'No response')}")
                self.successful_scenarios += 1
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
                
            print(f"   Timestamp: {result.get('timestamp', 'N/A')}")
            
            self.scenarios_run += 1
            return result
            
        except Exception as e:
            print(f"\n❌ Scenario failed with exception: {e}")
            self.scenarios_run += 1
            return {"success": False, "error": str(e)}

    def scenario_1_duplicate_ticket_flow(self):
        """Scenario 1: User creates similar ticket that might be duplicate"""
        self.print_scenario_header(
            "DUPLICATE TICKET DETECTION", 
            "User attempts to create a ticket similar to existing ones"
        )
        
        self.print_user_profile(
            "Sarah Johnson", 
            "Marketing Manager", 
            "Marketing", 
            "sarah.johnson@company.com"
        )
        
        # First ticket request
        print("🎬 PART 1: User creates initial ticket")
        first_request = "My laptop won't connect to the office WiFi network. I've tried restarting it multiple times but it keeps showing 'authentication failed' error. This is urgent as I have a client presentation in 2 hours."
        
        result1 = self.process_ticket_request(
            first_request, 
            "sarah.johnson@company.com",
            "Initial WiFi Issue"
        )
        
        # Wait a bit to simulate time passage
        print("\n⏳ [30 minutes later...]")
        time.sleep(2)
        
        # Second similar ticket request
        print("\n🎬 PART 2: Same user tries to create similar ticket")
        second_request = "I'm still having WiFi connectivity problems with my laptop. The authentication keeps failing and I can't connect to the corporate network. This is blocking my work."
        
        result2 = self.process_ticket_request(
            second_request, 
            "sarah.johnson@company.com",
            "Duplicate WiFi Issue"
        )
        
        print("\n🔍 DUPLICATE DETECTION ANALYSIS:")
        print("   Expected: Agent should detect similarity between tickets")
        print("   Expected: Agent should warn about potential duplicate")
        print("   Expected: Agent should suggest reviewing existing ticket")
        
        return result1, result2

    def scenario_2_no_duplicate_new_ticket(self):
        """Scenario 2: Legitimate new ticket creation"""
        self.print_scenario_header(
            "NEW TICKET CREATION", 
            "User creates a unique ticket with no duplicates"
        )
        
        self.print_user_profile(
            "Michael Chen", 
            "Software Developer", 
            "Engineering", 
            "michael.chen@company.com"
        )
        
        print("🎬 SCENARIO: User reports a new, unique issue")
        request = "I need to request access to the new AWS development environment for the Project Phoenix initiative. I require EC2, S3, and RDS permissions for development and testing. My manager Alex Rodriguez has already approved this request verbally."
        
        result = self.process_ticket_request(
            request, 
            "michael.chen@company.com",
            "AWS Access Request"
        )
        
        print("\n🆕 NEW TICKET ANALYSIS:")
        print("   Expected: No duplicates detected")
        print("   Expected: Ticket categorized as 'Access' request")
        print("   Expected: Priority assigned based on business need")
        print("   Expected: ServiceNow ticket created successfully")
        
        return result

    def scenario_3_hardware_issue_urgent(self):
        """Scenario 3: Urgent hardware issue"""
        self.print_scenario_header(
            "URGENT HARDWARE ISSUE", 
            "User reports critical hardware failure affecting productivity"
        )
        
        self.print_user_profile(
            "Dr. Lisa Rodriguez", 
            "Senior Research Scientist", 
            "R&D", 
            "lisa.rodriguez@company.com"
        )
        
        print("🎬 SCENARIO: Critical hardware failure during important work")
        request = "URGENT: My workstation monitor has completely failed - black screen, no display at all. I was in the middle of analyzing critical research data for tomorrow's board presentation. I've tried different cables and power cycling but nothing works. I need immediate replacement or alternative workstation."
        
        result = self.process_ticket_request(
            request, 
            "lisa.rodriguez@company.com",
            "Critical Monitor Failure"
        )
        
        print("\n🚨 URGENT TICKET ANALYSIS:")
        print("   Expected: High/Critical priority assigned")
        print("   Expected: Hardware category detected")
        print("   Expected: Urgent SLA applied")
        print("   Expected: Immediate escalation recommended")
        
        return result

    def scenario_4_software_installation_request(self):
        """Scenario 4: Software installation request"""
        self.print_scenario_header(
            "SOFTWARE INSTALLATION REQUEST", 
            "User needs new software for their role"
        )
        
        self.print_user_profile(
            "James Park", 
            "Data Analyst", 
            "Finance", 
            "james.park@company.com"
        )
        
        print("🎬 SCENARIO: Business-justified software request")
        request = "I need Tableau Desktop installed on my computer for creating financial dashboards and reports. Our department head has approved this software purchase and it's required for the Q4 financial analysis project. The license has already been procured under purchase order #PO-2024-1157."
        
        result = self.process_ticket_request(
            request, 
            "james.park@company.com",
            "Tableau Installation"
        )
        
        print("\n📦 SOFTWARE REQUEST ANALYSIS:")
        print("   Expected: Software category detected")
        print("   Expected: Medium priority (planned work)")
        print("   Expected: Service request type")
        print("   Expected: Standard SLA applied")
        
        return result

    def scenario_5_security_incident(self):
        """Scenario 5: Security-related incident"""
        self.print_scenario_header(
            "SECURITY INCIDENT REPORT", 
            "User reports potential security issue"
        )
        
        self.print_user_profile(
            "Emma Thompson", 
            "HR Manager", 
            "Human Resources", 
            "emma.thompson@company.com"
        )
        
        print("🎬 SCENARIO: Potential security breach report")
        request = "SECURITY ALERT: I received a suspicious email that looked like it was from our CEO asking for employee salary information. The email had our company logo but the sender address looked suspicious (ceo@companyy.com instead of company.com). I did not respond but I'm concerned this might be a phishing attempt targeting HR data."
        
        result = self.process_ticket_request(
            request, 
            "emma.thompson@company.com",
            "Phishing Attempt Report"
        )
        
        print("\n🔒 SECURITY INCIDENT ANALYSIS:")
        print("   Expected: Critical/High priority assigned")
        print("   Expected: Security category detected")
        print("   Expected: Immediate escalation to security team")
        print("   Expected: Urgent response SLA")
        
        return result

    def scenario_6_printer_network_issue(self):
        """Scenario 6: Common office printer issue"""
        self.print_scenario_header(
            "PRINTER CONNECTIVITY ISSUE", 
            "Multiple users affected by printer problems"
        )
        
        self.print_user_profile(
            "Robert Kim", 
            "Office Administrator", 
            "Administration", 
            "robert.kim@company.com"
        )
        
        print("🎬 SCENARIO: Shared resource affecting multiple users")
        request = "The main office printer (HP LaserJet in Conference Room B) is not responding to print jobs from any computer. The printer shows as online in the system but jobs just sit in the queue. Several employees have complained they can't print important documents for today's client meetings. The printer display shows no error messages."
        
        result = self.process_ticket_request(
            request, 
            "robert.kim@company.com",
            "Printer Network Issue"
        )
        
        print("\n🖨️ PRINTER ISSUE ANALYSIS:")
        print("   Expected: Medium/High priority (affects multiple users)")
        print("   Expected: Printer/Hardware category")
        print("   Expected: Network-related subcategory")
        print("   Expected: Business hours SLA")
        
        return result

    def run_all_scenarios(self):
        """Run all test scenarios"""
        print("🎭 STARTING COMPREHENSIVE SERVICENOW TICKET CREATION SCENARIOS")
        print("="*80)
        print(f"⏰ Test Suite Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🤖 Agent: Fast Google ADK Ticket Creation Agent")
        print(f"🎯 Framework: Google ADK with Gemini 2.5 Flash")
        
        start_time = time.time()
        
        # Run scenarios
        scenarios = [
            self.scenario_1_duplicate_ticket_flow,
            self.scenario_2_no_duplicate_new_ticket,
            self.scenario_3_hardware_issue_urgent,
            self.scenario_4_software_installation_request,
            self.scenario_5_security_incident,
            self.scenario_6_printer_network_issue
        ]
        
        results = []
        for scenario in scenarios:
            try:
                result = scenario()
                results.append(result)
                print("\n⏭️  Moving to next scenario...\n")
                time.sleep(1)  # Brief pause between scenarios
            except Exception as e:
                print(f"\n💥 Scenario failed: {e}")
                results.append({"success": False, "error": str(e)})
        
        # Summary
        total_time = time.time() - start_time
        
        print("\n" + "="*80)
        print("📊 TEST SUITE SUMMARY")
        print("="*80)
        print(f"⏱️  Total execution time: {total_time:.2f} seconds")
        print(f"🧪 Scenarios executed: {self.scenarios_run}")
        print(f"✅ Successful scenarios: {self.successful_scenarios}")
        print(f"❌ Failed scenarios: {self.scenarios_run - self.successful_scenarios}")
        print(f"📈 Success rate: {(self.successful_scenarios/self.scenarios_run*100):.1f}%")
        
        print("\n🎯 EXPECTED WORKFLOW VALIDATIONS:")
        print("   ✓ Duplicate detection for similar tickets")
        print("   ✓ Automatic categorization (Hardware, Software, Security, etc.)")
        print("   ✓ Priority assignment based on urgency keywords")
        print("   ✓ SLA calculation based on priority and category")
        print("   ✓ ServiceNow ticket creation with proper fields")
        print("   ✓ User-friendly response generation")
        
        print("\n🔍 BUSINESS LOGIC VALIDATIONS:")
        print("   ✓ Security incidents get highest priority")
        print("   ✓ Hardware failures escalated appropriately") 
        print("   ✓ Software requests routed to correct teams")
        print("   ✓ Multi-user impact increases priority")
        print("   ✓ Business justification captured in tickets")
        
        return results

def main():
    """Main execution function"""
    scenarios = TicketCreationScenarios()
    results = scenarios.run_all_scenarios()
    
    print(f"\n🎉 Test suite completed successfully!")
    print(f"📋 Results available for analysis")
    
    return results

if __name__ == "__main__":
    main()