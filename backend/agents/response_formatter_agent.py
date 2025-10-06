"""
Response Formatter Agent - Specialized for formatting search results
"""
from typing import Dict, Any


class ResponseFormatterAgent:
    """
    Agent responsible for formatting search results into user-friendly responses.
    """
    
    def __init__(self):
        self.base_url = "https://dev218893.service-now.com"
    
    def format_search_response(self, results: Dict[str, Any], search_type: str) -> str:
        """
        Format search results based on type.
        
        Args:
            results (Dict): Search results
            search_type (str): Type of search performed
        
        Returns:
            str: Formatted response
        """
        if not results:
            return "No results found for your search."
        
        if search_type == "knowledge_base":
            return self.format_knowledge_results(results)
        elif search_type == "servicenow":
            return self.format_servicenow_results(results)
        elif search_type == "category":
            return self.format_category_results(results)
        elif search_type == "mixed":
            return self.format_mixed_results(results)
        else:
            return self.format_generic_results(results)
    
    def format_knowledge_results(self, results: Dict[str, Any]) -> str:
        """Format knowledge base search results."""
        if not results.get("results"):
            return "No knowledge base articles found for your query."
        
        response = f"🔍 **Knowledge Base Search Results**\n\n"
        response += f"📊 **Summary:**\n"
        response += f"• Total Articles Found: {results.get('total_results', 0)}\n\n"
        
        response += f"📚 **Relevant Articles:**\n"
        for i, article in enumerate(results['results'][:5], 1):
            title = article.get('title', 'No title')
            summary = article.get('summary', 'No summary available')
            url = article.get('url', '')
            
            response += f"{i}. **{title}**\n"
            response += f"   {summary}\n"
            
            if url:
                if url.startswith('/'):
                    full_url = f"{self.base_url}{url}"
                else:
                    full_url = url
                response += f"   🔗 [Read Article]({full_url})\n"
            response += "\n"
        
        return response
    
    def format_servicenow_results(self, results: Dict[str, Any]) -> str:
        """Format ServiceNow search results."""
        if not results.get("results"):
            return "No ServiceNow tickets found for your query."
        
        response = f"🎫 **ServiceNow Search Results**\n\n"
        response += f"📊 **Summary:**\n"
        response += f"• Total Tickets Found: {results.get('total_results', 0)}\n\n"
        
        response += f"📋 **Recent Tickets:**\n"
        for i, ticket in enumerate(results['results'][:5], 1):
            number = ticket.get('number', 'N/A')
            description = ticket.get('short_description', 'No description')
            ticket_type = ticket.get('ticket_type', 'N/A')
            priority = ticket.get('priority', 'N/A')
            state = ticket.get('state', 'N/A')
            sys_id = ticket.get('sys_id', '')
            
            response += f"{i}. **{number}** - {description}\n"
            response += f"   Type: {ticket_type} | Priority: {priority} | State: {state}\n"
            
            if sys_id:
                if 'Incident' in ticket_type:
                    url = f"{self.base_url}/incident.do?sys_id={sys_id}"
                    response += f"   🔗 [View Incident]({url})\n"
                elif 'Problem' in ticket_type:
                    url = f"{self.base_url}/problem.do?sys_id={sys_id}"
                    response += f"   🔗 [View Problem]({url})\n"
            response += "\n"
        
        return response
    
    def format_category_results(self, results: Dict[str, Any]) -> str:
        """Format category-based search results."""
        category = results.get('category', 'Unknown')
        total_tickets = results.get('total_tickets', 0)
        
        if total_tickets == 0:
            return f"No {category} tickets found."
        
        response = f"🏷️ **{category} Tickets**\n\n"
        response += f"📊 **Summary:**\n"
        response += f"• Total {category} Tickets: {total_tickets}\n"
        response += f"• Incidents: {results.get('total_incidents', 0)}\n"
        response += f"• Problems: {results.get('total_problems', 0)}\n\n"
        
        # Format incidents
        if results.get('incidents'):
            response += f"📋 **Recent {category} Incidents:**\n"
            for i, incident in enumerate(results['incidents'][:3], 1):
                number = incident.get('number', 'N/A')
                description = incident.get('short_description', 'No description')
                priority = incident.get('priority', 'N/A')
                sys_id = incident.get('sys_id', '')
                
                response += f"{i}. **{number}** - {description}\n"
                response += f"   Priority: {priority}\n"
                
                if sys_id:
                    url = f"{self.base_url}/incident.do?sys_id={sys_id}"
                    response += f"   🔗 [View Incident]({url})\n"
                response += "\n"
        
        # Format problems
        if results.get('problems'):
            response += f"🔧 **Recent {category} Problems:**\n"
            for i, problem in enumerate(results['problems'][:3], 1):
                number = problem.get('number', 'N/A')
                description = problem.get('short_description', 'No description')
                priority = problem.get('priority', 'N/A')
                sys_id = problem.get('sys_id', '')
                
                response += f"{i}. **{number}** - {description}\n"
                response += f"   Priority: {priority}\n"
                
                if sys_id:
                    url = f"{self.base_url}/problem.do?sys_id={sys_id}"
                    response += f"   🔗 [View Problem]({url})\n"
                response += "\n"
        
        return response
    
    def format_mixed_results(self, results: Dict[str, Any]) -> str:
        """Format mixed search results from multiple sources."""
        response = f"🔍 **Comprehensive Search Results**\n\n"
        
        total_knowledge = results.get('total_knowledge', 0)
        total_servicenow = results.get('total_servicenow', 0)
        
        response += f"📊 **Summary:**\n"
        response += f"• Knowledge Articles: {total_knowledge}\n"
        response += f"• ServiceNow Tickets: {total_servicenow}\n"
        response += f"• Total Results: {total_knowledge + total_servicenow}\n\n"
        
        # Format knowledge results
        if results.get('knowledge_results'):
            response += f"📚 **Knowledge Base Articles:**\n"
            for i, article in enumerate(results['knowledge_results'][:3], 1):
                title = article.get('title', 'No title')
                summary = article.get('summary', 'No summary')
                url = article.get('url', '')
                
                response += f"{i}. **{title}**\n"
                response += f"   {summary}\n"
                
                if url:
                    if url.startswith('/'):
                        full_url = f"{self.base_url}{url}"
                    else:
                        full_url = url
                    response += f"   🔗 [Read Article]({full_url})\n"
                response += "\n"
        
        # Format ServiceNow results
        if results.get('servicenow_results'):
            response += f"🎫 **Related Tickets:**\n"
            for i, ticket in enumerate(results['servicenow_results'][:3], 1):
                number = ticket.get('number', 'N/A')
                description = ticket.get('short_description', 'No description')
                ticket_type = ticket.get('ticket_type', 'N/A')
                sys_id = ticket.get('sys_id', '')
                
                response += f"{i}. **{number}** - {description}\n"
                response += f"   Type: {ticket_type}\n"
                
                if sys_id and 'Incident' in ticket_type:
                    url = f"{self.base_url}/incident.do?sys_id={sys_id}"
                    response += f"   🔗 [View Ticket]({url})\n"
                response += "\n"
        
        return response
    
    def format_generic_results(self, results: Dict[str, Any]) -> str:
        """Format generic search results."""
        return f"Search completed. Found {results.get('total_results', 0)} results."
    
    def format_error_response(self, error_msg: str, query: str = "") -> str:
        """Format error responses."""
        response = f"❌ **Search Error**\n\n"
        response += f"I encountered an issue while searching"
        if query:
            response += f" for: '{query}'"
        response += ".\n\n"
        response += f"**Error Details:** {error_msg}\n\n"
        response += "Please try again with a different search term or contact support if the issue persists."
        
        return response
    
    def format_no_results_response(self, query: str, search_type: str = "") -> str:
        """Format no results found response."""
        response = f"🔍 **No Results Found**\n\n"
        response += f"I couldn't find any results for: '{query}'"
        if search_type:
            response += f" in {search_type}"
        response += ".\n\n"
        response += "**Suggestions:**\n"
        response += "• Try different keywords\n"
        response += "• Check spelling\n"
        response += "• Use broader search terms\n"
        response += "• Contact support for assistance\n"
        
        return response