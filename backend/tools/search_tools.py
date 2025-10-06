"""
Search-related tools for the Search Agent with ServiceNow integration
"""
from typing import Dict, List, Optional
from oci.addons.adk import tool
import requests
import json
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ServiceNowClient:
    """ServiceNow API client for searching historical tickets"""
    
    def __init__(self):
        self.instance_url = os.getenv("SERVICENOW_INSTANCE_URL", "").replace("/login.do?user_name=admin&sys_action=sysverb_login&user_password=Bb7Q8Iqp%2Fp-B", "")
        self.username = os.getenv("SERVICENOW_USERNAME", "")
        self.password = os.getenv("SERVICENOW_PASSWORD", "")
        self.api_version = os.getenv("SERVICENOW_API_VERSION", "v2")
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
            # Construct the search query
            search_params = {
                "sysparm_query": f"short_descriptionCONTAINS{query}^ORdescriptionCONTAINS{query}^ORcategoryCONTAINS{query}",
                "sysparm_limit": str(limit),
                "sysparm_fields": "sys_id,number,short_description,description,category,priority,state,assigned_to,created,resolved,work_notes"
            }
            
            url = f"{self.instance_url}/api/now/table/incident"
            response = requests.get(url, headers=self.headers, params=search_params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("result", [])
            else:
                print(f"ServiceNow API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error searching ServiceNow incidents: {e}")
            return []
    
    def search_problems(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for problems based on query"""
        try:
            search_params = {
                "sysparm_query": f"short_descriptionCONTAINS{query}^ORdescriptionCONTAINS{query}^ORcategoryCONTAINS{query}",
                "sysparm_limit": str(limit),
                "sysparm_fields": "sys_id,number,short_description,description,category,priority,state,assigned_to,created,resolved,work_notes"
            }
            
            url = f"{self.instance_url}/api/now/table/problem"
            response = requests.get(url, headers=self.headers, params=search_params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("result", [])
            else:
                print(f"ServiceNow API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error searching ServiceNow problems: {e}")
            return []
    
    def search_changes(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for change requests based on query"""
        try:
            search_params = {
                "sysparm_query": f"short_descriptionCONTAINS{query}^ORdescriptionCONTAINS{query}^ORcategoryCONTAINS{query}",
                "sysparm_limit": str(limit),
                "sysparm_fields": "sys_id,number,short_description,description,category,priority,state,assigned_to,created,resolved,work_notes"
            }
            
            url = f"{self.instance_url}/api/now/table/change_request"
            response = requests.get(url, headers=self.headers, params=search_params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("result", [])
            else:
                print(f"ServiceNow API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error searching ServiceNow changes: {e}")
            return []

# Initialize ServiceNow client
servicenow_client = ServiceNowClient()


@tool
def search_knowledge_base(query: str, category: Optional[str] = None) -> Dict[str, any]:
    """
    Search the knowledge base for relevant information based on the query.
    
    Args:
        query (str): The search query string
        category (str, optional): Optional category to filter search results
    
    Returns:
        Dict containing search results with title, content, and relevance score
    """
    try:
        # Search ServiceNow knowledge base
        search_params = {
            "sysparm_query": f"short_descriptionCONTAINS{query}^ORtextCONTAINS{query}^ORcategoryCONTAINS{query}",
            "sysparm_limit": "10",
            "sysparm_fields": "sys_id,number,short_description,text,category,state,workflow_state,author,created,updated"
        }
        
        url = f"{servicenow_client.instance_url}/api/now/table/kb_knowledge"
        response = requests.get(url, headers=servicenow_client.headers, params=search_params, timeout=servicenow_client.timeout)
        
        if response.status_code == 200:
            data = response.json()
            kb_articles = data.get("result", [])
            
            # Format results
            formatted_results = []
            for article in kb_articles:
                formatted_results.append({
                    "title": article.get("short_description", "No title"),
                    "content": article.get("text", "No content")[:200] + "..." if article.get("text") else "No content",
                    "summary": article.get("text", "No summary")[:100] + "..." if article.get("text") else "No summary",
                    "category": article.get("category", "General"),
                    "relevance_score": 0.9,  # High relevance for ServiceNow results
                    "url": f"/kb_view.do?sysparm_article={article.get('sys_id', '')}",
                    "sys_id": article.get("sys_id", ""),
                    "number": article.get("number", ""),
                    "state": article.get("state", ""),
                    "author": article.get("author", ""),
                    "created": article.get("created", ""),
                    "updated": article.get("updated", "")
                })
            
            # Filter by category if provided
            if category:
                formatted_results = [r for r in formatted_results if category.lower() in r["category"].lower()]
            
            return {
                "query": query,
                "results": formatted_results[:5],  # Limit to top 5 results
                "total_results": len(formatted_results)
            }
        else:
            print(f"ServiceNow KB search failed: {response.status_code}")
            return {
                "query": query,
                "results": [],
                "total_results": 0,
                "error": f"ServiceNow API error: {response.status_code}"
            }
            
    except Exception as e:
        print(f"Error searching knowledge base: {e}")
        return {
            "query": query,
            "results": [],
            "total_results": 0,
            "error": str(e)
        }


@tool
def search_service_now(query: str, table: str = "incident", priority: str = None, limit: int = 15) -> Dict[str, any]:
    """
    Search ServiceNow records based on the query with advanced filtering options.
    
    Args:
        query (str): The search query string
        table (str): ServiceNow table to search (incident, problem, change_request, all)
        priority (str): Filter by priority level (1=Critical, 2=High, 3=Medium, 4=Low)
        limit (int): Maximum number of results to return
    
    Returns:
        Dict containing ServiceNow search results with analysis
    """
    try:
        all_results = []
        
        if table == "all" or table == "incident":
            incidents = servicenow_client.search_incidents(query, limit)
            all_results.extend([{**incident, "ticket_type": "Incident"} for incident in incidents])
        
        if table == "all" or table == "problem":
            problems = servicenow_client.search_problems(query, limit)
            all_results.extend([{**problem, "ticket_type": "Problem"} for problem in problems])
        
        if table == "all" or table == "change_request":
            changes = servicenow_client.search_changes(query, limit)
            all_results.extend([{**change, "ticket_type": "Change Request"} for change in changes])
        
        # Filter by priority if specified
        if priority:
            all_results = [
                result for result in all_results 
                if result.get('priority', '').startswith(priority)
            ]
        
        # Limit results
        all_results = all_results[:limit]
        
        # Analyze results
        priority_counts = {}
        state_counts = {}
        type_counts = {}
        
        for result in all_results:
            # Count by priority
            pri = result.get('priority', 'Unknown')
            priority_counts[pri] = priority_counts.get(pri, 0) + 1
            
            # Count by state
            state = result.get('state', 'Unknown')
            state_counts[state] = state_counts.get(state, 0) + 1
            
            # Count by type
            ticket_type = result.get('ticket_type', 'Unknown')
            type_counts[ticket_type] = type_counts.get(ticket_type, 0) + 1
        
        return {
            "query": query,
            "table": table,
            "priority_filter": priority,
            "results": all_results,
            "total_results": len(all_results),
            "priority_breakdown": priority_counts,
            "state_breakdown": state_counts,
            "type_breakdown": type_counts,
            "source": "ServiceNow API",
            "analysis": f"Found {len(all_results)} tickets matching '{query}'" + 
                       (f" with priority {priority}" if priority else "") +
                       f" across {len(type_counts)} ticket types"
        }
    except Exception as e:
        return {
            "query": query,
            "table": table,
            "results": [],
            "total_results": 0,
            "error": f"ServiceNow search failed: {str(e)}",
            "source": "ServiceNow API"
        }


@tool
def get_article_content(article_id: str) -> Dict[str, str]:
    """
    Retrieve the full content of a specific knowledge base article.
    
    Args:
        article_id (str): The unique identifier for the article
    
    Returns:
        Dict containing the article content and metadata
    """
    # Mock article content - replace with actual implementation
    mock_articles = {
        "incident-management": {
            "title": "ServiceNow Incident Management",
            "content": """
            Incident Management in ServiceNow is a critical process for IT service management.
            
            Key features include:
            - Automatic incident creation from monitoring tools
            - Assignment and routing based on categories
            - SLA tracking and escalation
            - Integration with change management
            
            Best practices:
            1. Always provide clear, descriptive incident titles
            2. Include relevant system information and error messages
            3. Update incidents regularly with progress notes
            4. Close incidents only after confirming resolution
            """,
            "last_updated": "2024-01-10",
            "author": "IT Knowledge Team"
        }
    }
    
    article = mock_articles.get(article_id, {
        "title": "Article Not Found",
        "content": "The requested article could not be found.",
        "last_updated": None,
        "author": None
    })
    
    return article


@tool
def search_tickets_by_category(category: str, limit: int = 15) -> Dict[str, any]:
    """
    Search tickets by specific category.
    
    Args:
        category (str): The category to search for (e.g., "Hardware", "Software", "Network", "Security")
        limit (int): Maximum number of results to return
    
    Returns:
        Dict containing tickets in the specified category
    """
    try:
        # Search incidents by category
        incidents = servicenow_client.search_incidents(category, limit)
        
        # Filter by exact category match
        category_incidents = [
            incident for incident in incidents 
            if incident.get('category', '').lower() == category.lower()
        ]
        
        # Search problems by category
        problems = servicenow_client.search_problems(category, limit)
        category_problems = [
            problem for problem in problems 
            if problem.get('category', '').lower() == category.lower()
        ]
        
        return {
            "category": category,
            "incidents": category_incidents,
            "problems": category_problems,
            "total_incidents": len(category_incidents),
            "total_problems": len(category_problems),
            "total_tickets": len(category_incidents) + len(category_problems)
        }
        
    except Exception as e:
        return {
            "category": category,
            "error": f"Category search failed: {str(e)}",
            "total_tickets": 0
        }


@tool
@tool
def get_ticket_details(ticket_number: str) -> Dict[str, any]:
    """
    Get detailed information about a specific ticket.
    
    Args:
        ticket_number (str): The ticket number to look up (e.g., INC0012345)
    
    Returns:
        Dict containing detailed ticket information
    """
    try:
        # Try to find the ticket in incidents first
        incidents = servicenow_client.search_incidents(ticket_number, limit=1)
        if incidents:
            return {
                "ticket_number": ticket_number,
                "ticket_type": "Incident",
                "details": incidents[0],
                "found": True
            }
        
        # Try problems
        problems = servicenow_client.search_problems(ticket_number, limit=1)
        if problems:
            return {
                "ticket_number": ticket_number,
                "ticket_type": "Problem",
                "details": problems[0],
                "found": True
            }
        
        # Try change requests
        changes = servicenow_client.search_changes(ticket_number, limit=1)
        if changes:
            return {
                "ticket_number": ticket_number,
                "ticket_type": "Change Request",
                "details": changes[0],
                "found": True
            }
        
        return {
            "ticket_number": ticket_number,
            "found": False,
            "message": "Ticket not found"
        }
        
    except Exception as e:
        return {
            "ticket_number": ticket_number,
            "error": f"Ticket lookup failed: {str(e)}",
            "found": False
        }
