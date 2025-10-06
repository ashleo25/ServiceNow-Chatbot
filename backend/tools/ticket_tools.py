"""
Ticket creation and management tools for the Ticket Creation Agent
"""
from typing import Dict, List, Optional
from oci.addons.adk import tool
import requests
import json
from datetime import datetime


@tool
def create_incident_ticket(
    short_description: str,
    description: str,
    category: str = "General",
    priority: str = "3 - Medium",
    assigned_group: Optional[str] = None,
    caller_id: Optional[str] = None
) -> Dict[str, any]:
    """
    Create a new incident ticket in ServiceNow.
    
    Args:
        short_description (str): Brief description of the incident
        description (str): Detailed description of the incident
        category (str): Incident category (default: General)
        priority (str): Priority level (1-Critical, 2-High, 3-Medium, 4-Low)
        assigned_group (str, optional): Group to assign the ticket to
        caller_id (str, optional): ID of the person reporting the incident
    
    Returns:
        Dict containing the created ticket information
    """
    # Mock ticket creation - replace with actual ServiceNow API integration
    ticket_number = f"INC{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    mock_ticket = {
        "sys_id": f"sys_{ticket_number}",
        "number": ticket_number,
        "short_description": short_description,
        "description": description,
        "category": category,
        "priority": priority,
        "state": "New",
        "assigned_group": assigned_group or "IT Support",
        "caller_id": caller_id or "system",
        "created": datetime.now().isoformat(),
        "created_by": "chatbot",
        "work_notes": "Ticket created via AI chatbot"
    }
    
    # In a real implementation, you would make an API call to ServiceNow here
    # Example:
    # response = requests.post(
    #     f"https://{Config.SERVICENOW_INSTANCE}/api/now/table/incident",
    #     auth=(Config.SERVICENOW_USERNAME, Config.SERVICENOW_PASSWORD),
    #     headers={"Content-Type": "application/json"},
    #     json=mock_ticket
    # )
    
    return {
        "success": True,
        "ticket": mock_ticket,
        "message": f"Incident ticket {ticket_number} created successfully"
    }


@tool
def create_change_request(
    short_description: str,
    description: str,
    change_type: str = "Standard",
    priority: str = "3 - Medium",
    risk: str = "Medium",
    implementation_plan: Optional[str] = None
) -> Dict[str, any]:
    """
    Create a new change request in ServiceNow.
    
    Args:
        short_description (str): Brief description of the change
        description (str): Detailed description of the change
        change_type (str): Type of change (Standard, Normal, Emergency)
        priority (str): Priority level (1-Critical, 2-High, 3-Medium, 4-Low)
        risk (str): Risk level (Low, Medium, High)
        implementation_plan (str, optional): Detailed implementation plan
    
    Returns:
        Dict containing the created change request information
    """
    # Mock change request creation
    change_number = f"CHG{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    mock_change = {
        "sys_id": f"sys_{change_number}",
        "number": change_number,
        "short_description": short_description,
        "description": description,
        "change_type": change_type,
        "priority": priority,
        "risk": risk,
        "state": "New",
        "implementation_plan": implementation_plan or "To be determined",
        "created": datetime.now().isoformat(),
        "created_by": "chatbot",
        "work_notes": "Change request created via AI chatbot"
    }
    
    return {
        "success": True,
        "change_request": mock_change,
        "message": f"Change request {change_number} created successfully"
    }


@tool
def create_service_request(
    short_description: str,
    description: str,
    requested_for: str,
    service_catalog_item: str = "General Request",
    priority: str = "3 - Medium"
) -> Dict[str, any]:
    """
    Create a new service request in ServiceNow.
    
    Args:
        short_description (str): Brief description of the service request
        description (str): Detailed description of the service request
        requested_for (str): User requesting the service
        service_catalog_item (str): Type of service being requested
        priority (str): Priority level (1-Critical, 2-High, 3-Medium, 4-Low)
    
    Returns:
        Dict containing the created service request information
    """
    # Mock service request creation
    request_number = f"REQ{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    mock_request = {
        "sys_id": f"sys_{request_number}",
        "number": request_number,
        "short_description": short_description,
        "description": description,
        "requested_for": requested_for,
        "service_catalog_item": service_catalog_item,
        "priority": priority,
        "state": "New",
        "created": datetime.now().isoformat(),
        "created_by": "chatbot",
        "work_notes": "Service request created via AI chatbot"
    }
    
    return {
        "success": True,
        "service_request": mock_request,
        "message": f"Service request {request_number} created successfully"
    }


@tool
def get_ticket_status(ticket_number: str) -> Dict[str, any]:
    """
    Get the current status of a ticket by its number.
    
    Args:
        ticket_number (str): The ticket number to look up
    
    Returns:
        Dict containing the ticket status and details
    """
    # Mock ticket status lookup - replace with actual ServiceNow API integration
    mock_tickets = {
        "INC0012345": {
            "number": "INC0012345",
            "short_description": "Email server not responding",
            "state": "In Progress",
            "priority": "2 - High",
            "assigned_to": "John Smith",
            "created": "2024-01-15 10:30:00",
            "last_updated": "2024-01-15 14:20:00",
            "work_notes": "Investigating server logs, found network connectivity issue"
        },
        "CHG0012346": {
            "number": "CHG0012346",
            "short_description": "Database server maintenance",
            "state": "Approved",
            "priority": "3 - Medium",
            "assigned_to": "Database Team",
            "created": "2024-01-14 09:00:00",
            "last_updated": "2024-01-15 11:30:00",
            "work_notes": "Change approved, scheduled for maintenance window"
        }
    }
    
    ticket = mock_tickets.get(ticket_number, {
        "number": ticket_number,
        "error": "Ticket not found",
        "message": f"No ticket found with number {ticket_number}"
    })
    
    return ticket


@tool
def update_ticket_notes(ticket_number: str, work_notes: str) -> Dict[str, any]:
    """
    Update work notes for an existing ticket.
    
    Args:
        ticket_number (str): The ticket number to update
        work_notes (str): The work notes to add
    
    Returns:
        Dict containing the update result
    """
    # Mock ticket update - replace with actual ServiceNow API integration
    return {
        "success": True,
        "ticket_number": ticket_number,
        "message": f"Work notes updated for ticket {ticket_number}",
        "updated_notes": work_notes,
        "timestamp": datetime.now().isoformat()
    }
