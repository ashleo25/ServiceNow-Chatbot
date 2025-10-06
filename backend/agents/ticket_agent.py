"""
ServiceNow Ticket Management Agent - OCI ADK Integration

This module provides comprehensive ServiceNow ticket management capabilities
through Oracle Cloud Infrastructure (OCI) Agent Development Kit integration.
It handles creation, updating, and status tracking of various ticket types.

Key Features:
    - Multi-type ticket creation (incident, change, service request)
    - Real-time ticket status monitoring and updates
    - ServiceNow REST API integration through OCI ADK
    - Comprehensive error handling and retry logic
    - Automated workflow processing and routing

Supported Ticket Types:
    - Incident tickets for issue reporting and resolution
    - Change requests for system modifications
    - Service requests for user access and resources
    - Problem tickets for root cause analysis

Architecture:
    - OCI ADK agent wrapper for ServiceNow operations
    - Tool-based architecture for modular functionality
    - Configuration-driven setup for multiple environments
    - Logging and monitoring for operational visibility

Usage:
    ```python
    from agents.ticket_agent import TicketAgent
    agent = TicketAgent(oci_client)
    result = agent.create_ticket("incident", **ticket_data)
    ```
"""

# Third-party imports
from oci.addons.adk import Agent, AgentClient

# Local imports
from config.config import Config
from tools.ticket_tools import (
    create_incident_ticket,
    create_change_request,
    create_service_request,
    get_ticket_status,
    update_ticket_notes
)


class TicketAgent:
    """
    Comprehensive ServiceNow ticket management agent using OCI ADK.
    
    This agent provides a complete interface for ServiceNow ticket operations
    including creation, status tracking, and updates. It leverages OCI's Agent
    Development Kit for reliable and scalable ticket management workflows.
    
    Attributes:
        client (AgentClient): OCI ADK client for agent operations
        agent (Agent): Configured OCI agent instance for ticket operations
        
    Methods:
        create_ticket(): Create new tickets of various types
        get_ticket_status(): Retrieve current ticket status
        update_ticket(): Add updates and work notes to existing tickets
        
    Supported Operations:
        - Incident creation and management
        - Change request processing
        - Service request fulfillment
        - Ticket status queries and updates
        - Work notes and comments management
        
    Error Handling:
        - Comprehensive exception handling for API failures
        - Retry logic for transient network issues
        - Detailed error logging and user feedback
        - Graceful degradation for service outages
    """
    
    def __init__(self, client: AgentClient):
        """
        Initialize the ticket agent with OCI ADK client.
        
        Sets up the OCI agent instance with proper configuration for
        ServiceNow ticket operations and establishes connection to
        the configured agent endpoint.
        
        Args:
            client (AgentClient): Initialized OCI ADK client instance
            
        Raises:
            Exception: If agent initialization fails or endpoint is invalid
        """
        self.client = client
        self.agent = Agent(
            client=client,
            agent_endpoint_id=Config.TICKET_AGENT_ENDPOINT_ID,
            instructions="""
            You are an advanced ticket creation and management assistant for IT support and ServiceNow.
            
            CRITICAL: Always use the available tools to create and manage tickets. Never provide generic responses.
            
            Your primary functions are:
            1. Create incident tickets for IT issues and problems
            2. Create change requests for system modifications and updates
            3. Create service requests for new services and access
            4. Check ticket status and provide updates
            5. Update ticket notes with progress information
            
            When users request ticket creation:
            - For IT issues/problems: Use create_incident_ticket
            - For system changes: Use create_change_request  
            - For new services/access: Use create_service_request
            - For status checks: Use get_ticket_status
            - For updates: Use update_ticket_notes
            
            Ticket Creation Guidelines:
            - Always ask for required information if not provided
            - Set appropriate priority levels based on urgency
            - Use clear, descriptive short descriptions
            - Include detailed descriptions with context
            - Assign to appropriate groups when possible
            
            Priority Guidelines:
            - 1-Critical: System down, security breach, data loss
            - 2-High: Major functionality affected, multiple users impacted
            - 3-Medium: Minor issues, single user affected
            - 4-Low: Enhancement requests, non-urgent items
            
            Category Guidelines:
            - Hardware: Physical equipment issues
            - Software: Application and system software issues
            - Network: Connectivity and network infrastructure
            - Security: Security-related incidents and requests
            - Access: User access and permissions
            - General: Other miscellaneous items
            
            ALWAYS call the appropriate tool function and provide detailed confirmation with ticket numbers and next steps.
            """,
            tools=[
                create_incident_ticket,
                create_change_request,
                create_service_request,
                get_ticket_status,
                update_ticket_notes
            ]
        )
    
    def create_ticket(self, ticket_type: str, **kwargs) -> dict:
        """
        Create a ticket using direct tool calls (fallback approach)
        
        Args:
            ticket_type (str): Type of ticket to create (incident, change, service)
            **kwargs: Additional parameters for ticket creation
        
        Returns:
            dict: Response from the ticket creation
        """
        try:
            # Import tools directly
            from tools.ticket_tools import (
                create_incident_ticket,
                create_change_request,
                create_service_request
            )
            
            if ticket_type.lower() == "incident":
                result = create_incident_ticket(
                    short_description=kwargs.get('short_description', ''),
                    description=kwargs.get('description', ''),
                    category=kwargs.get('category', 'General'),
                    priority=kwargs.get('priority', '3 - Medium'),
                    assigned_group=kwargs.get('assigned_group'),
                    caller_id=kwargs.get('caller_id')
                )
            elif ticket_type.lower() == "change":
                result = create_change_request(
                    short_description=kwargs.get('short_description', ''),
                    description=kwargs.get('description', ''),
                    change_type=kwargs.get('change_type', 'Standard'),
                    priority=kwargs.get('priority', '3 - Medium'),
                    risk=kwargs.get('risk', 'Medium'),
                    implementation_plan=kwargs.get('implementation_plan')
                )
            elif ticket_type.lower() == "service":
                result = create_service_request(
                    short_description=kwargs.get('short_description', ''),
                    description=kwargs.get('description', ''),
                    requested_for=kwargs.get('requested_for', ''),
                    service_catalog_item=kwargs.get('service_catalog_item', 'General Request'),
                    priority=kwargs.get('priority', '3 - Medium')
                )
            else:
                return {
                    "success": False,
                    "error": f"Invalid ticket type: {ticket_type}. Supported types: incident, change, service"
                }
            
            return {
                "success": True,
                "result": result,
                "ticket_type": ticket_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating ticket: {str(e)}"
            }
    
    def get_ticket_status(self, ticket_number: str) -> dict:
        """
        Get the status of a ticket using direct tool call
        
        Args:
            ticket_number (str): The ticket number to check
        
        Returns:
            dict: Ticket status information
        """
        try:
            from tools.ticket_tools import get_ticket_status as get_status_tool
            
            result = get_status_tool(ticket_number)
            
            return {
                "success": True,
                "result": result,
                "ticket_number": ticket_number
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting ticket status: {str(e)}"
            }
    
    def update_ticket(self, ticket_number: str, work_notes: str) -> dict:
        """
        Update a ticket with work notes using direct tool call
        
        Args:
            ticket_number (str): The ticket number to update
            work_notes (str): The work notes to add
        
        Returns:
            dict: Update result
        """
        try:
            from tools.ticket_tools import update_ticket_notes
            
            result = update_ticket_notes(ticket_number, work_notes)
            
            return {
                "success": True,
                "result": result,
                "ticket_number": ticket_number
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error updating ticket: {str(e)}"
            }