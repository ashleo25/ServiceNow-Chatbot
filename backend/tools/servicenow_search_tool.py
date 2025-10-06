"""
ServiceNow Search Tool - Specialized for ServiceNow ticket operations
"""
from typing import Dict, List, Any
from oci.addons.adk import tool
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()


class ServiceNowClient:
    """ServiceNow API client for ticket operations"""
    
    def __init__(self):
        instance_url = os.getenv("SERVICENOW_INSTANCE_URL", "")
        self.instance_url = instance_url.replace(
            "/login.do?user_name=admin&sys_action=sysverb_login&user_password=Bb7Q8Iqp%2Fp-B", 
            ""
        )
        self.username = os.getenv("SERVICENOW_USERNAME", "")
        self.password = os.getenv("SERVICENOW_PASSWORD", "")
        self.timeout = int(os.getenv("SERVICENOW_TIMEOUT", "30"))
        
        # Create basic auth header
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def search_incidents(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for incidents based on query"""
        try:
            search_params = {
                "sysparm_query": f"short_descriptionCONTAINS{query}^ORdescriptionCONTAINS{query}",
                "sysparm_limit": str(limit),
                "sysparm_fields": "sys_id,number,short_description,category,priority,state"
            }
            
            url = f"{self.instance_url}/api/now/table/incident"
            response = requests.get(
                url, headers=self.headers, params=search_params, timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("result", [])
            else:
                print(f"ServiceNow API error: {response.status_code}")
                return []
        except Exception as e:
            print(f"ServiceNow search failed: {str(e)}")
            return []
    
    def search_problems(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for problems based on query"""
        try:
            search_params = {
                "sysparm_query": f"short_descriptionCONTAINS{query}^ORdescriptionCONTAINS{query}",
                "sysparm_limit": str(limit),
                "sysparm_fields": "sys_id,number,short_description,category,priority,state"
            }
            
            url = f"{self.instance_url}/api/now/table/problem"
            response = requests.get(
                url, headers=self.headers, params=search_params, timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("result", [])
            else:
                print(f"ServiceNow API error: {response.status_code}")
                return []
        except Exception as e:
            print(f"ServiceNow search failed: {str(e)}")
            return []


# Global client instance
servicenow_client = ServiceNowClient()


@tool
def search_service_now(query: str, table: str = "incident", limit: int = 15) -> Dict[str, Any]:
    """
    Search ServiceNow records (incidents, problems, change requests).
    
    Args:
        query (str): Search query
        table (str): Table to search ("incident", "problem", "all")
        limit (int): Maximum number of results
    
    Returns:
        Dict containing ServiceNow search results
    """
    try:
        all_results = []
        
        if table == "incident" or table == "all":
            incidents = servicenow_client.search_incidents(query, limit)
            for incident in incidents:
                incident['ticket_type'] = 'Incident'
            all_results.extend(incidents)
        
        if table == "problem" or table == "all":
            problems = servicenow_client.search_problems(query, limit)
            for problem in problems:
                problem['ticket_type'] = 'Problem'
            all_results.extend(problems)
        
        return {
            "results": all_results[:limit],
            "total_results": len(all_results),
            "search_type": "servicenow",
            "query": query,
            "table": table
        }
        
    except Exception as e:
        return {
            "results": [],
            "total_results": 0,
            "error": f"ServiceNow search failed: {str(e)}",
            "search_type": "servicenow",
            "query": query
        }


@tool
def search_tickets_by_category(category: str, limit: int = 15) -> Dict[str, Any]:
    """
    Search tickets by category (Hardware, Software, Network, etc.).
    
    Args:
        category (str): Category to search for
        limit (int): Maximum number of results
    
    Returns:
        Dict containing categorized ticket results
    """
    try:
        incidents = servicenow_client.search_incidents(category, limit)
        problems = servicenow_client.search_problems(category, limit)
        
        # Filter by category
        filtered_incidents = [
            incident for incident in incidents 
            if incident.get('category', '').lower() == category.lower()
        ]
        
        filtered_problems = [
            problem for problem in problems 
            if problem.get('category', '').lower() == category.lower()
        ]
        
        return {
            "incidents": filtered_incidents,
            "problems": filtered_problems,
            "total_incidents": len(filtered_incidents),
            "total_problems": len(filtered_problems),
            "total_tickets": len(filtered_incidents) + len(filtered_problems),
            "category": category,
            "search_type": "category"
        }
        
    except Exception as e:
        return {
            "incidents": [],
            "problems": [],
            "total_tickets": 0,
            "error": f"Category search failed: {str(e)}",
            "category": category,
            "search_type": "category"
        }


@tool
def get_ticket_details(ticket_number: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific ticket.
    
    Args:
        ticket_number (str): Ticket number (e.g., INC0000123)
    
    Returns:
        Dict containing ticket details
    """
    try:
        # Mock implementation - in production would query ServiceNow API
        ticket_details = {
            "number": ticket_number,
            "short_description": "Sample ticket description",
            "description": "Detailed description of the issue",
            "state": "In Progress",
            "priority": "2 - High",
            "category": "Hardware",
            "assigned_to": "IT Support",
            "created": "2024-01-15 10:30:00",
            "updated": "2024-01-15 14:15:00"
        }
        
        return {
            "success": True,
            "ticket": ticket_details,
            "search_type": "ticket_details"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get ticket details: {str(e)}",
            "ticket_number": ticket_number,
            "search_type": "ticket_details"
        }