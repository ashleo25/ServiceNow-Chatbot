"""
Ticket Create Agent - Creates tickets in ServiceNow with validation and error handling
"""
from typing import Dict, Any, Optional
from datetime import datetime
from config.logging_config import get_logger
from services.ticket_creation_service import ServiceNowTicketService

logger = get_logger("ticket_create_agent")

class TicketCreateAgent:
    """
    Sub-Agent 2: ServiceNow Ticket Creation
    Responsibilities:
    - Format data for ServiceNow API
    - Create tickets in appropriate ServiceNow tables
    - Validate ticket creation success
    - Handle creation errors and retries
    - Set initial ticket status and assignments
    - Generate ticket URLs and references
    """
    
    def __init__(self):
        self.servicenow_service = ServiceNowTicketService()
        
        # Field mappings for different ticket types
        self.field_mappings = {
            "incident": {
                "short_description": "short_description",
                "description": "description",
                "category": "category",
                "priority": "priority",
                "urgency": "urgency",
                "impact": "impact",
                "caller_id": "caller_id",
                "assigned_to": "assigned_to",
                "assignment_group": "assignment_group"
            },
            "request": {
                "short_description": "short_description",
                "description": "description",
                "category": "category",
                "priority": "priority",
                "caller_id": "requested_for",
                "assigned_to": "assigned_to",
                "assignment_group": "assignment_group"
            },
            "change": {
                "short_description": "short_description",
                "description": "description",
                "category": "category",
                "priority": "priority",
                "caller_id": "requested_by",
                "assigned_to": "assigned_to",
                "assignment_group": "assignment_group",
                "change_type": "change_type",
                "risk": "risk"
            },
            "problem": {
                "short_description": "short_description",
                "description": "description",
                "category": "category",
                "priority": "priority",
                "caller_id": "reported_by",
                "assigned_to": "assigned_to",
                "assignment_group": "assignment_group"
            }
        }
        
        logger.info("Ticket Create Agent initialized")
        logger.info(f"Supported ticket types: {list(self.field_mappings.keys())}")
    
    def create_ticket(self, ticket_data: Dict[str, Any], ticket_type: str) -> Dict[str, Any]:
        """
        Create ticket in ServiceNow based on type
        
        Args:
            ticket_data: Collected ticket data
            ticket_type: Type of ticket (incident, request, change, problem)
            
        Returns:
            Dictionary with creation result
        """
        logger.info(f"Starting ticket creation for type: {ticket_type}")
        logger.debug(f"Ticket data: {ticket_data}")
        
        try:
            # Step 1: Format data for ServiceNow
            formatted_data = self.format_ticket_data(ticket_data, ticket_type)
            logger.debug(f"Formatted data: {formatted_data}")
            
            # Step 2: Create ticket in ServiceNow
            creation_result = self._create_ticket_in_servicenow(formatted_data, ticket_type)
            logger.info(f"Ticket creation result: {creation_result.get('success', False)}")
            
            if not creation_result.get("success", False):
                logger.error(f"Ticket creation failed: {creation_result.get('error', 'Unknown error')}")
                return creation_result
            
            # Step 3: Validate creation (immediately after creation)
            validation_result = self.validate_creation(
                creation_result["ticket_id"], 
                ticket_type
            )
            logger.info(f"Ticket validation result: {validation_result.get('success', False)}")
            
            if not validation_result["success"]:
                logger.error(f"Ticket validation failed: {validation_result.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "error": f"Ticket created but validation failed: {validation_result.get('error')}",
                    "ticket_id": creation_result.get("ticket_id"),
                    "validation_error": validation_result
                }
            
            # Step 4: Set initial status (only if validation successful)
            status_result = self.set_initial_status(
                creation_result["ticket_id"], 
                ticket_type,
                formatted_data
            )
            logger.info(f"Status setting result: {status_result.get('success', False)}")
            
            # Combine all results
            final_result = {
                "success": True,
                "ticket_id": creation_result["ticket_id"],
                "ticket_number": creation_result["ticket_number"],
                "ticket_url": creation_result["ticket_url"],
                "table": creation_result["table"],
                "validation": validation_result,
                "status": status_result,
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"Ticket creation completed successfully: {creation_result['ticket_number']}")
            return final_result
            
        except Exception as e:
            logger.error(f"Error in ticket creation process: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "ticket_type": ticket_type
            }
    
    def format_ticket_data(self, raw_data: Dict[str, Any], ticket_type: str) -> Dict[str, Any]:
        """
        Format collected data for ServiceNow API
        
        Args:
            raw_data: Raw collected data
            ticket_type: Type of ticket
            
        Returns:
            Formatted data for ServiceNow
        """
        logger.debug(f"Formatting data for {ticket_type} ticket")
        
        try:
            if ticket_type not in self.field_mappings:
                raise ValueError(f"Unsupported ticket type: {ticket_type}")
            
            field_mapping = self.field_mappings[ticket_type]
            formatted_data = {}
            
            # Map fields according to ticket type
            for source_field, target_field in field_mapping.items():
                if source_field in raw_data and raw_data[source_field]:
                    formatted_data[target_field] = raw_data[source_field]
            
            # Set default values
            formatted_data = self._set_default_values(formatted_data, ticket_type)
            
            # Add work notes
            formatted_data["work_notes"] = f"Ticket created via chatbot on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            logger.debug(f"Formatted data: {formatted_data}")
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error formatting ticket data: {str(e)}")
            raise
    
    def _set_default_values(self, data: Dict[str, Any], ticket_type: str) -> Dict[str, Any]:
        """Set default values for required fields"""
        
        # Set default priority if not provided
        if "priority" not in data or not data["priority"]:
            data["priority"] = "3"  # Medium priority
        
        # Set default category if not provided
        if "category" not in data or not data["category"]:
            data["category"] = "General"
        
        # Set default urgency for incidents
        if ticket_type == "incident" and "urgency" not in data:
            data["urgency"] = "3"  # Medium urgency
        
        # Set default impact for incidents
        if ticket_type == "incident" and "impact" not in data:
            data["impact"] = "3"  # Medium impact
        
        # Set default change type for changes
        if ticket_type == "change" and "change_type" not in data:
            data["change_type"] = "Minor"
        
        # Set default risk for changes
        if ticket_type == "change" and "risk" not in data:
            data["risk"] = "Low"
        
        return data
    
    def _create_ticket_in_servicenow(self, formatted_data: Dict[str, Any], ticket_type: str) -> Dict[str, Any]:
        """Create ticket in ServiceNow using appropriate method"""
        logger.debug(f"Creating {ticket_type} ticket in ServiceNow")
        
        try:
            if ticket_type == "incident":
                return self.servicenow_service.create_incident(formatted_data)
            elif ticket_type == "request":
                return self.servicenow_service.create_service_request(formatted_data)
            elif ticket_type == "change":
                return self.servicenow_service.create_change_request(formatted_data)
            elif ticket_type == "problem":
                return self.servicenow_service.create_problem(formatted_data)
            else:
                raise ValueError(f"Unsupported ticket type: {ticket_type}")
                
        except Exception as e:
            logger.error(f"Error creating {ticket_type} ticket: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_creation(self, ticket_id: str, ticket_type: str) -> Dict[str, Any]:
        """
        Validate ticket was created successfully
        
        Args:
            ticket_id: ServiceNow ticket ID
            ticket_type: Type of ticket
            
        Returns:
            Validation result
        """
        logger.debug(f"Validating {ticket_type} ticket: {ticket_id}")
        
        try:
            # Determine table name
            table_mapping = {
                "incident": "incident",
                "request": "sc_request",
                "change": "change_request",
                "problem": "problem"
            }
            
            if ticket_type not in table_mapping:
                return {
                    "success": False,
                    "error": f"Unsupported ticket type for validation: {ticket_type}"
                }
            
            table = table_mapping[ticket_type]
            
            # Check if ticket exists
            exists = self.servicenow_service.validate_ticket_exists(ticket_id, table)
            
            if not exists:
                logger.error(f"Ticket validation failed: {ticket_id} not found in {table}")
                return {
                    "success": False,
                    "error": f"Ticket {ticket_id} not found in ServiceNow"
                }
            
            # Get ticket details for additional validation
            ticket_details = self.servicenow_service.get_ticket_details(ticket_id, table)
            
            if not ticket_details:
                logger.warning(f"Could not retrieve ticket details for {ticket_id}")
                return {
                    "success": True,
                    "warning": "Ticket exists but details could not be retrieved"
                }
            
            # Validate required fields are populated
            validation_checks = self._validate_ticket_fields(ticket_details, ticket_type)
            
            logger.info(f"Ticket validation successful: {ticket_id}")
            return {
                "success": True,
                "ticket_id": ticket_id,
                "ticket_details": ticket_details,
                "validation_checks": validation_checks
            }
            
        except Exception as e:
            logger.error(f"Error validating ticket {ticket_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_ticket_fields(self, ticket_details: Dict[str, Any], ticket_type: str) -> Dict[str, Any]:
        """Validate that required fields are populated"""
        validation_checks = {
            "has_short_description": bool(ticket_details.get("short_description")),
            "has_description": bool(ticket_details.get("description")),
            "has_category": bool(ticket_details.get("category")),
            "has_priority": bool(ticket_details.get("priority")),
            "has_state": bool(ticket_details.get("state"))
        }
        
        # Check if all required fields are present
        all_valid = all(validation_checks.values())
        
        return {
            "all_fields_valid": all_valid,
            "checks": validation_checks,
            "missing_fields": [field for field, valid in validation_checks.items() if not valid]
        }
    
    def set_initial_status(self, ticket_id: str, ticket_type: str, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set initial ticket status and assignments
        
        Args:
            ticket_id: ServiceNow ticket ID
            ticket_type: Type of ticket
            ticket_data: Original ticket data
            
        Returns:
            Status setting result
        """
        logger.debug(f"Setting initial status for {ticket_type} ticket: {ticket_id}")
        
        try:
            # Determine table name
            table_mapping = {
                "incident": "incident",
                "request": "sc_request",
                "change": "change_request",
                "problem": "problem"
            }
            
            if ticket_type not in table_mapping:
                return {
                    "success": False,
                    "error": f"Unsupported ticket type for status setting: {ticket_type}"
                }
            
            table = table_mapping[ticket_type]
            
            # Set initial status based on ticket type
            status_updates = self._get_initial_status_updates(ticket_type, ticket_data)
            
            if not status_updates:
                logger.info(f"No status updates needed for {ticket_type} ticket")
                return {
                    "success": True,
                    "message": "No status updates required"
                }
            
            # Update ticket status
            url = f"{self.servicenow_service.instance_url}/api/now/table/{table}/{ticket_id}"
            response = self.servicenow_service._make_request("PATCH", url, status_updates)
            
            if response.get("success", False):
                logger.info(f"Status updated successfully for {ticket_id}")
                return {
                    "success": True,
                    "updates": status_updates,
                    "message": "Status updated successfully"
                }
            else:
                logger.warning(f"Status update failed for {ticket_id}: {response.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "error": response.get("error", "Status update failed")
                }
                
        except Exception as e:
            logger.error(f"Error setting status for {ticket_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_initial_status_updates(self, ticket_type: str, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get initial status updates based on ticket type"""
        updates = {}
        
        if ticket_type == "incident":
            # Set state to "New" if not already set
            updates["state"] = "1"  # New
            updates["incident_state"] = "1"  # New
            
        elif ticket_type == "request":
            # Set state to "New" if not already set
            updates["state"] = "1"  # New
            
        elif ticket_type == "change":
            # Set state to "New" if not already set
            updates["state"] = "1"  # New
            updates["change_state"] = "1"  # New
            
        elif ticket_type == "problem":
            # Set state to "New" if not already set
            updates["state"] = "1"  # New
            updates["problem_state"] = "1"  # New
        
        # Add assignment group if specified
        if ticket_data.get("assignment_group"):
            updates["assignment_group"] = ticket_data["assignment_group"]
        
        # Add assigned user if specified
        if ticket_data.get("assigned_to"):
            updates["assigned_to"] = ticket_data["assigned_to"]
        
        return updates
    
    def handle_creation_errors(self, error: Exception, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle ticket creation errors
        
        Args:
            error: Exception that occurred
            ticket_data: Original ticket data
            
        Returns:
            Error handling result
        """
        logger.error(f"Handling creation error: {str(error)}")
        
        try:
            error_message = str(error)
            
            # Parse common ServiceNow errors
            if "duplicate" in error_message.lower():
                return {
                    "error_type": "duplicate",
                    "message": "A ticket with similar information already exists",
                    "suggestion": "Please check existing tickets or modify your request"
                }
            
            elif "required field" in error_message.lower():
                return {
                    "error_type": "missing_field",
                    "message": "Required field is missing",
                    "suggestion": "Please provide all required information"
                }
            
            elif "permission" in error_message.lower():
                return {
                    "error_type": "permission",
                    "message": "Insufficient permissions to create ticket",
                    "suggestion": "Contact your administrator for access"
                }
            
            elif "timeout" in error_message.lower():
                return {
                    "error_type": "timeout",
                    "message": "Request timed out",
                    "suggestion": "Please try again in a few moments"
                }
            
            else:
                return {
                    "error_type": "unknown",
                    "message": "An unexpected error occurred",
                    "suggestion": "Please try again or contact support"
                }
                
        except Exception as e:
            logger.error(f"Error handling creation error: {str(e)}")
            return {
                "error_type": "handler_error",
                "message": "Error occurred while handling the error",
                "suggestion": "Please contact support"
            }
