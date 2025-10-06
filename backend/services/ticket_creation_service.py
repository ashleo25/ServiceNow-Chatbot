"""
ServiceNow integration service for ticket creation operations
"""
import requests
import base64
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from config.logging_config import get_logger
from config.config import Config

logger = get_logger("servicenow_service")

class ServiceNowTicketService:
    """ServiceNow integration for ticket operations"""
    
    def __init__(self):
        self.instance_url = Config.SERVICENOW_INSTANCE_URL.replace("/login.do?user_name=admin&sys_action=sysverb_login&user_password=Bb7Q8Iqp%2Fp-B", "")
        self.username = Config.SERVICENOW_USERNAME
        self.password = Config.SERVICENOW_PASSWORD
        self.api_version = Config.SERVICENOW_API_VERSION
        self.timeout = int(Config.SERVICENOW_TIMEOUT)
        
        # Create basic auth header
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        logger.info(f"ServiceNow service initialized for instance: {self.instance_url}")
    
    def search_duplicates(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for potential duplicate tickets
        
        Args:
            criteria: Search criteria including user_id, ticket_type, description, etc.
            
        Returns:
            List of potential duplicate tickets
        """
        logger.info(f"Searching for duplicates with criteria: {criteria}")
        
        try:
            # Build search query
            query_parts = []
            
            if criteria.get("user_id"):
                query_parts.append(f"caller_id={criteria['user_id']}")
            
            if criteria.get("ticket_type"):
                if criteria["ticket_type"] == "incident":
                    query_parts.append("sys_class_name=incident")
                elif criteria["ticket_type"] == "request":
                    query_parts.append("sys_class_name=sc_request")
                elif criteria["ticket_type"] == "change":
                    query_parts.append("sys_class_name=change_request")
                elif criteria["ticket_type"] == "problem":
                    query_parts.append("sys_class_name=problem")
            
            if criteria.get("description"):
                # Search in short_description and description
                desc = criteria["description"].replace("'", "\\'")
                query_parts.append(f"short_descriptionCONTAINS{desc}^ORdescriptionCONTAINS{desc}")
            
            if criteria.get("category"):
                query_parts.append(f"category={criteria['category']}")
            
            # Add time filter (last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            query_parts.append(f"sys_created_on>={thirty_days_ago}")
            
            # CRITICAL: Filter for active ticket states only (New, Open, In Progress)
            # ServiceNow state values: 1=New, 2=In Progress, 6=Resolved, 7=Closed
            query_parts.append("state!=6^state!=7")  # Exclude Resolved and Closed
            
            search_query = "^".join(query_parts)
            
            # Search parameters
            search_params = {
                "sysparm_query": search_query,
                "sysparm_limit": "20",
                "sysparm_fields": "sys_id,number,short_description,description,category,priority,state,assigned_to,created,resolved,work_notes,caller_id"
            }
            
            # Determine table based on ticket type
            table = "incident"
            if criteria.get("ticket_type") == "request":
                table = "sc_request"
            elif criteria.get("ticket_type") == "change":
                table = "change_request"
            elif criteria.get("ticket_type") == "problem":
                table = "problem"
            
            url = f"{self.instance_url}/api/now/table/{table}"
            logger.debug(f"Searching duplicates in table: {table}")
            logger.debug(f"Search query: {search_query}")
            
            response = requests.get(url, headers=self.headers, params=search_params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("result", [])
                logger.info(f"Found {len(results)} potential duplicates")
                return results
            else:
                logger.error(f"Duplicate search failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching duplicates: {str(e)}")
            return []
    
    def create_incident(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create incident ticket in ServiceNow"""
        logger.info(f"Creating incident ticket with data: {data.get('short_description', 'No description')}")
        
        try:
            # Format data for ServiceNow
            default_caller = Config.SERVICENOW_DEFAULT_CALLER_ID
            incident_data = {
                "short_description": data.get("short_description", ""),
                "description": data.get("description", ""),
                "category": data.get("category", "General"),
                "priority": data.get("priority", "3"),
                "urgency": data.get("urgency", "3"),
                "impact": data.get("impact", "3"),
                "caller_id": data.get("caller_id", default_caller),
                "assigned_to": data.get("assigned_to", ""),
                "assignment_group": data.get("assignment_group", ""),
                "work_notes": f"Ticket created via chatbot on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
            
            url = f"{self.instance_url}/api/now/table/incident"
            response = requests.post(url, headers=self.headers, json=incident_data, timeout=self.timeout)
            
            if response.status_code == 201:
                result = response.json().get("result", {})
                ticket_id = result.get("sys_id", "")
                ticket_number = result.get("number", "")
                ticket_url = f"{self.instance_url}/incident.do?sys_id={ticket_id}"
                
                logger.info(f"Incident created successfully: {ticket_number} ({ticket_id})")
                
                return {
                    "success": True,
                    "ticket_id": ticket_id,
                    "ticket_number": ticket_number,
                    "ticket_url": ticket_url,
                    "table": "incident"
                }
            else:
                logger.error(f"Incident creation failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"ServiceNow API error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error creating incident: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_service_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create service request in ServiceNow"""
        logger.info(f"Creating service request with data: {data.get('short_description', 'No description')}")
        
        try:
            # Format data for ServiceNow
            request_data = {
                "short_description": data.get("short_description", ""),
                "description": data.get("description", ""),
                "category": data.get("category", "General"),
                "priority": data.get("priority", "3"),
                "requested_for": data.get("caller_id", ""),
                "assigned_to": data.get("assigned_to", ""),
                "assignment_group": data.get("assignment_group", ""),
                "work_notes": f"Service request created via chatbot on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
            
            url = f"{self.instance_url}/api/now/table/sc_request"
            response = requests.post(url, headers=self.headers, json=request_data, timeout=self.timeout)
            
            if response.status_code == 201:
                result = response.json().get("result", {})
                ticket_id = result.get("sys_id", "")
                ticket_number = result.get("number", "")
                ticket_url = f"{self.instance_url}/sc_request.do?sys_id={ticket_id}"
                
                logger.info(f"Service request created successfully: {ticket_number} ({ticket_id})")
                
                return {
                    "success": True,
                    "ticket_id": ticket_id,
                    "ticket_number": ticket_number,
                    "ticket_url": ticket_url,
                    "table": "sc_request"
                }
            else:
                logger.error(f"Service request creation failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"ServiceNow API error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error creating service request: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_change_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create change request in ServiceNow"""
        logger.info(f"Creating change request with data: {data.get('short_description', 'No description')}")
        
        try:
            # Format data for ServiceNow
            change_data = {
                "short_description": data.get("short_description", ""),
                "description": data.get("description", ""),
                "category": data.get("category", "General"),
                "priority": data.get("priority", "3"),
                "requested_by": data.get("caller_id", ""),
                "assigned_to": data.get("assigned_to", ""),
                "assignment_group": data.get("assignment_group", ""),
                "change_type": data.get("change_type", "Minor"),
                "risk": data.get("risk", "Low"),
                "work_notes": f"Change request created via chatbot on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
            
            url = f"{self.instance_url}/api/now/table/change_request"
            response = requests.post(url, headers=self.headers, json=change_data, timeout=self.timeout)
            
            if response.status_code == 201:
                result = response.json().get("result", {})
                ticket_id = result.get("sys_id", "")
                ticket_number = result.get("number", "")
                ticket_url = f"{self.instance_url}/change_request.do?sys_id={ticket_id}"
                
                logger.info(f"Change request created successfully: {ticket_number} ({ticket_id})")
                
                return {
                    "success": True,
                    "ticket_id": ticket_id,
                    "ticket_number": ticket_number,
                    "ticket_url": ticket_url,
                    "table": "change_request"
                }
            else:
                logger.error(f"Change request creation failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"ServiceNow API error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error creating change request: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_problem(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create problem ticket in ServiceNow"""
        logger.info(f"Creating problem ticket with data: {data.get('short_description', 'No description')}")
        
        try:
            # Format data for ServiceNow
            problem_data = {
                "short_description": data.get("short_description", ""),
                "description": data.get("description", ""),
                "category": data.get("category", "General"),
                "priority": data.get("priority", "3"),
                "reported_by": data.get("caller_id", ""),
                "assigned_to": data.get("assigned_to", ""),
                "assignment_group": data.get("assignment_group", ""),
                "work_notes": f"Problem ticket created via chatbot on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
            
            url = f"{self.instance_url}/api/now/table/problem"
            response = requests.post(url, headers=self.headers, json=problem_data, timeout=self.timeout)
            
            if response.status_code == 201:
                result = response.json().get("result", {})
                ticket_id = result.get("sys_id", "")
                ticket_number = result.get("number", "")
                ticket_url = f"{self.instance_url}/problem.do?sys_id={ticket_id}"
                
                logger.info(f"Problem ticket created successfully: {ticket_number} ({ticket_id})")
                
                return {
                    "success": True,
                    "ticket_id": ticket_id,
                    "ticket_number": ticket_number,
                    "ticket_url": ticket_url,
                    "table": "problem"
                }
            else:
                logger.error(f"Problem creation failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"ServiceNow API error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error creating problem: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_ticket_exists(self, ticket_id: str, table: str) -> bool:
        """Validate that a ticket exists in ServiceNow"""
        logger.debug(f"Validating ticket exists: {ticket_id} in table: {table}")
        
        try:
            url = f"{self.instance_url}/api/now/table/{table}/{ticket_id}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                logger.debug(f"Ticket validation successful: {ticket_id}")
                return True
            else:
                logger.warning(f"Ticket validation failed: {ticket_id} - {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error validating ticket: {str(e)}")
            return False
    
    def get_ticket_details(self, ticket_id: str, table: str) -> Dict[str, Any]:
        """Get detailed ticket information"""
        logger.debug(f"Getting ticket details: {ticket_id} from table: {table}")
        
        try:
            url = f"{self.instance_url}/api/now/table/{table}/{ticket_id}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json().get("result", {})
                logger.debug(f"Retrieved ticket details for: {ticket_id}")
                return result
            else:
                logger.error(f"Failed to get ticket details: {ticket_id} - {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting ticket details: {str(e)}")
            return {}
    
    def _make_request(self, method: str, url: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to ServiceNow"""
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=self.timeout)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data, timeout=self.timeout)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
            if response.status_code in [200, 201, 204]:
                return {
                    "success": True,
                    "data": response.json() if response.content else {}
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
