"""
Ticket Response Agent - Generates user-friendly responses and ticket summaries
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from config.logging_config import get_logger

logger = get_logger("ticket_response_agent")

class TicketResponseAgent:
    """
    Sub-Agent 3: User Communication & Response Generation
    Responsibilities:
    - Generate user-friendly ticket creation confirmations
    - Create detailed ticket summaries
    - Format ticket information for display
    - Handle error messages and explanations
    - Generate follow-up recommendations
    - Create ticket URLs and navigation links
    """
    
    def __init__(self):
        self.servicenow_base_url = "https://dev218893.service-now.com"
        
        # Response templates
        self.response_templates = {
            "success": {
                "incident": "✅ **Incident Created Successfully!**",
                "request": "✅ **Service Request Created Successfully!**",
                "change": "✅ **Change Request Created Successfully!**",
                "problem": "✅ **Problem Ticket Created Successfully!**"
            },
            "error": {
                "creation_failed": "❌ **Ticket Creation Failed**",
                "validation_failed": "⚠️ **Ticket Validation Failed**",
                "duplicate_found": "🔍 **Similar Tickets Found**",
                "permission_denied": "🚫 **Access Denied**"
            }
        }
        
        logger.info("Ticket Response Agent initialized")
        logger.info(f"ServiceNow base URL: {self.servicenow_base_url}")
    
    def generate_creation_response(self, ticket_result: Dict[str, Any], ticket_type: str) -> str:
        """
        Generate user response for successful ticket creation
        
        Args:
            ticket_result: Ticket creation result
            ticket_type: Type of ticket created
            
        Returns:
            Formatted response string
        """
        logger.info(f"Generating creation response for {ticket_type} ticket")
        
        try:
            ticket_id = ticket_result.get("ticket_id", "N/A")
            ticket_number = ticket_result.get("ticket_number", "N/A")
            ticket_url = ticket_result.get("ticket_url", "")
            
            # Get template
            template = self.response_templates["success"].get(ticket_type, "✅ **Ticket Created Successfully!**")
            
            response = f"{template}\n\n"
            response += f"**Ticket Details:**\n"
            response += f"- **Ticket ID**: {ticket_id}\n"
            response += f"- **Ticket Number**: {ticket_number}\n"
            response += f"- **Type**: {ticket_type.title()}\n"
            
            # Add status information
            if ticket_result.get("status", {}).get("updates"):
                status_info = ticket_result["status"]["updates"]
                if "state" in status_info:
                    response += f"- **Status**: {self._get_status_description(status_info['state'], ticket_type)}\n"
            
            # Add priority and SLA information
            priority = ticket_result.get("priority", ticket_result.get("validation", {}).get("ticket_details", {}).get("priority"))
            priority_name = ticket_result.get("priority_name", "Unknown")
            sla_response = ticket_result.get("sla_response_time", "Not specified")
            sla_resolution = ticket_result.get("sla_resolution_time", "Not specified")
            
            if priority:
                response += f"- **Priority**: {priority} ({priority_name})\n"
                response += f"- **SLA Response**: {sla_response}\n"
                response += f"- **SLA Resolution**: {sla_resolution}\n"
            
            # Add creation time
            created_at = ticket_result.get("created_at", datetime.now().isoformat())
            response += f"- **Created**: {self._format_datetime(created_at)}\n"
            
            # Add ticket URL
            if ticket_url:
                response += f"\n🔗 **View Ticket**: [Open in ServiceNow]({ticket_url})\n"
            
            # Add next steps
            response += self._get_next_steps(ticket_type, ticket_result)
            
            # Add contact information
            response += self._get_contact_information()
            
            logger.info(f"Generated creation response for ticket {ticket_number}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating creation response: {str(e)}")
            return self.generate_error_response({
                "error": str(e),
                "error_type": "response_generation_failed"
            }, ticket_type)
    
    def generate_error_response(self, error_result: Dict[str, Any], ticket_type: str = "ticket") -> str:
        """
        Generate user response for creation errors
        
        Args:
            error_result: Error information
            ticket_type: Type of ticket (for context)
            
        Returns:
            Formatted error response string
        """
        logger.info(f"Generating error response for {ticket_type} ticket")
        
        try:
            error_type = error_result.get("error_type", "unknown")
            error_message = error_result.get("error", "An unknown error occurred")
            
            # Get error template
            template = self.response_templates["error"].get(error_type, "❌ **Error Occurred**")
            
            response = f"{template}\n\n"
            response += f"**Error Details:**\n"
            response += f"- **Message**: {error_message}\n"
            response += f"- **Type**: {error_type.replace('_', ' ').title()}\n"
            response += f"- **Time**: {self._format_datetime(datetime.now().isoformat())}\n"
            
            # Add specific error handling
            if error_type == "duplicate":
                response += self._get_duplicate_error_guidance()
            elif error_type == "missing_field":
                response += self._get_missing_field_guidance()
            elif error_type == "permission":
                response += self._get_permission_error_guidance()
            elif error_type == "timeout":
                response += self._get_timeout_guidance()
            else:
                response += self._get_general_error_guidance()
            
            # Add retry options
            response += self._get_retry_options(error_type)
            
            # Add contact information
            response += self._get_contact_information()
            
            logger.info(f"Generated error response for {error_type}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating error response: {str(e)}")
            return f"❌ **Critical Error**\n\nAn error occurred while generating the error response. Please contact support immediately."
    
    def format_ticket_summary(self, ticket_data: Dict[str, Any], ticket_id: str) -> str:
        """
        Format ticket information for user display
        
        Args:
            ticket_data: Ticket data
            ticket_id: ServiceNow ticket ID
            
        Returns:
            Formatted ticket summary
        """
        logger.debug(f"Formatting ticket summary for {ticket_id}")
        
        try:
            summary = f"**Ticket Summary**\n\n"
            
            # Basic information
            summary += f"**Description**: {ticket_data.get('short_description', 'No description')}\n"
            summary += f"**Category**: {ticket_data.get('category', 'General')}\n"
            summary += f"**Priority**: {self._get_priority_description(ticket_data.get('priority', '3'))}\n"
            
            # Additional details
            if ticket_data.get('description'):
                desc = ticket_data['description'][:200] + "..." if len(ticket_data['description']) > 200 else ticket_data['description']
                summary += f"**Details**: {desc}\n"
            
            # Impact information for incidents
            if ticket_data.get('urgency'):
                summary += f"**Urgency**: {self._get_urgency_description(ticket_data['urgency'])}\n"
            
            if ticket_data.get('impact'):
                summary += f"**Impact**: {self._get_impact_description(ticket_data['impact'])}\n"
            
            # Change-specific information
            if ticket_data.get('change_type'):
                summary += f"**Change Type**: {ticket_data['change_type']}\n"
            
            if ticket_data.get('risk'):
                summary += f"**Risk Level**: {ticket_data['risk']}\n"
            
            logger.debug(f"Formatted ticket summary for {ticket_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Error formatting ticket summary: {str(e)}")
            return f"**Ticket Summary**\n\nError formatting ticket details. Please contact support."
    
    def create_ticket_links(self, ticket_id: str, ticket_type: str) -> Dict[str, str]:
        """
        Create clickable links for ticket
        
        Args:
            ticket_id: ServiceNow ticket ID
            ticket_type: Type of ticket
            
        Returns:
            Dictionary of links
        """
        logger.debug(f"Creating links for {ticket_type} ticket: {ticket_id}")
        
        try:
            # Determine table name for URL
            table_mapping = {
                "incident": "incident",
                "request": "sc_request",
                "change": "change_request",
                "problem": "problem"
            }
            
            table = table_mapping.get(ticket_type, "incident")
            
            # Create various links
            links = {
                "servicenow_url": f"{self.servicenow_base_url}/{table}.do?sys_id={ticket_id}",
                "mobile_url": f"{self.servicenow_base_url}/m/{table}.do?sys_id={ticket_id}",
                "api_url": f"{self.servicenow_base_url}/api/now/table/{table}/{ticket_id}",
                "email_subject": f"Re: {ticket_type.title()} Ticket {ticket_id}"
            }
            
            logger.debug(f"Created {len(links)} links for ticket {ticket_id}")
            return links
            
        except Exception as e:
            logger.error(f"Error creating ticket links: {str(e)}")
            return {}
    
    def generate_follow_up_recommendations(self, ticket_type: str, ticket_data: Dict[str, Any]) -> str:
        """
        Generate follow-up recommendations
        
        Args:
            ticket_type: Type of ticket
            ticket_data: Ticket data
            
        Returns:
            Formatted recommendations
        """
        logger.debug(f"Generating follow-up recommendations for {ticket_type}")
        
        try:
            recommendations = "**Follow-up Recommendations:**\n\n"
            
            # General recommendations
            recommendations += "• **Track Progress**: Check your ticket status regularly\n"
            recommendations += "• **Provide Updates**: Add work notes if you have additional information\n"
            recommendations += "• **Respond Promptly**: Reply to any requests from the support team\n"
            
            # Type-specific recommendations
            if ticket_type == "incident":
                recommendations += "• **Monitor Impact**: Keep track of any business impact\n"
                recommendations += "• **Test Resolution**: Verify the fix works as expected\n"
                recommendations += "• **Document Workarounds**: Note any temporary solutions used\n"
            
            elif ticket_type == "request":
                recommendations += "• **Prepare for Implementation**: Gather any required approvals\n"
                recommendations += "• **Schedule Time**: Plan for the service delivery\n"
                recommendations += "• **Review Requirements**: Ensure all details are clear\n"
            
            elif ticket_type == "change":
                recommendations += "• **Review Change Plan**: Ensure all stakeholders are informed\n"
                recommendations += "• **Schedule Implementation**: Coordinate with affected teams\n"
                recommendations += "• **Prepare Rollback**: Have a rollback plan ready\n"
            
            elif ticket_type == "problem":
                recommendations += "• **Monitor Recurrence**: Watch for similar issues\n"
                recommendations += "• **Document Root Cause**: Help identify the underlying cause\n"
                recommendations += "• **Share Knowledge**: Help prevent similar problems\n"
            
            # SLA information
            recommendations += f"\n**Expected Timeline:**\n"
            recommendations += f"• **Response Time**: {self._get_response_time(ticket_data.get('priority', '3'))}\n"
            recommendations += f"• **Resolution Time**: {self._get_resolution_time(ticket_data.get('priority', '3'), ticket_type)}\n"
            
            logger.debug(f"Generated follow-up recommendations for {ticket_type}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating follow-up recommendations: {str(e)}")
            return "**Follow-up Recommendations:**\n\nError generating recommendations. Please contact support."
    
    def _get_next_steps(self, ticket_type: str, ticket_result: Dict[str, Any]) -> str:
        """Get next steps based on ticket type"""
        next_steps = "\n**Next Steps:**\n"
        
        if ticket_type == "incident":
            next_steps += "• You'll receive email updates on progress\n"
            next_steps += "• A support technician will be assigned\n"
            next_steps += "• Monitor the ticket for status changes\n"
        
        elif ticket_type == "request":
            next_steps += "• Your request will be reviewed and approved\n"
            next_steps += "• You'll be notified of the implementation schedule\n"
            next_steps += "• Prepare for any required meetings or approvals\n"
        
        elif ticket_type == "change":
            next_steps += "• The change will be reviewed by the Change Advisory Board\n"
            next_steps += "• You'll receive approval notifications\n"
            next_steps += "• Schedule implementation with affected teams\n"
        
        elif ticket_type == "problem":
            next_steps += "• A problem manager will be assigned\n"
            next_steps += "• Root cause analysis will be performed\n"
            next_steps += "• You'll be updated on findings and solutions\n"
        
        return next_steps
    
    def _get_contact_information(self) -> str:
        """Get contact information"""
        return "\n**Need Help?**\n• **IT Support**: (555) 123-4567\n• **Email**: support@company.com\n• **Portal**: [ServiceNow Portal](https://dev218893.service-now.com)\n"
    
    def _get_status_description(self, state: str, ticket_type: str) -> str:
        """Get human-readable status description"""
        status_mapping = {
            "1": "New",
            "2": "In Progress",
            "3": "On Hold",
            "4": "Resolved",
            "5": "Closed",
            "6": "Cancelled"
        }
        return status_mapping.get(state, f"State {state}")
    
    def _get_priority_description(self, priority: str) -> str:
        """Get human-readable priority description"""
        priority_mapping = {
            "1": "Critical",
            "2": "High",
            "3": "Medium",
            "4": "Low",
            "5": "Planning"
        }
        return priority_mapping.get(priority, f"Priority {priority}")
    
    def _get_urgency_description(self, urgency: str) -> str:
        """Get human-readable urgency description"""
        urgency_mapping = {
            "1": "Critical",
            "2": "High",
            "3": "Medium",
            "4": "Low"
        }
        return urgency_mapping.get(urgency, f"Urgency {urgency}")
    
    def _get_impact_description(self, impact: str) -> str:
        """Get human-readable impact description"""
        impact_mapping = {
            "1": "Critical",
            "2": "High",
            "3": "Medium",
            "4": "Low"
        }
        return impact_mapping.get(impact, f"Impact {impact}")
    
    def _format_datetime(self, dt_string: str) -> str:
        """Format datetime string for display"""
        try:
            if 'T' in dt_string:
                dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(dt_string)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return dt_string
    
    def _get_response_time(self, priority: str) -> str:
        """Get expected response time based on priority"""
        response_times = {
            "1": "15 minutes",
            "2": "1 hour",
            "3": "4 hours",
            "4": "8 hours",
            "5": "24 hours"
        }
        return response_times.get(priority, "4 hours")
    
    def _get_resolution_time(self, priority: str, ticket_type: str) -> str:
        """Get expected resolution time based on priority and type"""
        if ticket_type == "incident":
            resolution_times = {
                "1": "2 hours",
                "2": "8 hours",
                "3": "24 hours",
                "4": "72 hours",
                "5": "1 week"
            }
        else:
            resolution_times = {
                "1": "4 hours",
                "2": "1 day",
                "3": "3 days",
                "4": "1 week",
                "5": "2 weeks"
            }
        return resolution_times.get(priority, "24 hours")
    
    def _get_duplicate_error_guidance(self) -> str:
        """Get guidance for duplicate errors"""
        return "\n**Guidance:**\n• Check if a similar ticket already exists\n• Consider linking to existing ticket\n• Modify your request to be more specific\n"
    
    def _get_missing_field_guidance(self) -> str:
        """Get guidance for missing field errors"""
        return "\n**Guidance:**\n• Ensure all required fields are filled\n• Check the form for validation errors\n• Contact support if fields are unclear\n"
    
    def _get_permission_error_guidance(self) -> str:
        """Get guidance for permission errors"""
        return "\n**Guidance:**\n• Contact your IT administrator for access\n• Check if you have the correct role\n• Verify your account permissions\n"
    
    def _get_timeout_guidance(self) -> str:
        """Get guidance for timeout errors"""
        return "\n**Guidance:**\n• Wait a few moments and try again\n• Check your internet connection\n• Contact support if the issue persists\n"
    
    def _get_general_error_guidance(self) -> str:
        """Get general error guidance"""
        return "\n**Guidance:**\n• Try again in a few moments\n• Check your input for errors\n• Contact support if the issue persists\n"
    
    def _get_retry_options(self, error_type: str) -> str:
        """Get retry options based on error type"""
        if error_type in ["timeout", "unknown"]:
            return "\n**Retry Options:**\n• Wait 2-3 minutes and try again\n• Refresh the page and retry\n• Contact support if retries fail\n"
        else:
            return "\n**Retry Options:**\n• Fix the identified issues and try again\n• Contact support for assistance\n"
