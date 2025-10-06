"""
Search Agent implementation using OCI ADK
"""
from oci.addons.adk import Agent, AgentClient
from config.config import Config
from tools.search_tools import (
    search_knowledge_base, 
    search_service_now, 
    get_article_content,
    search_tickets_by_category,
    get_ticket_details
)


class SearchAgent:
    """Search Agent for knowledge base and ServiceNow searches"""
    
    def __init__(self, client: AgentClient):
        self.client = client
        self.agent = Agent(
            client=client,
            agent_endpoint_id=Config.SEARCH_AGENT_ENDPOINT_ID,
            instructions="""
            You are an advanced search assistant for IT support and ServiceNow.
            
            CRITICAL: Always use the available tools to search for information. 
            Never provide generic responses.
            
            Your primary functions are:
            1. Search the knowledge base for relevant articles and documentation
            2. Search ServiceNow records (incidents, problems, change requests)
            3. Search tickets by category (Hardware, Software, Network, etc.)
            4. Get detailed article content from knowledge base
            
            When users ask questions:
            - For hardware-related queries: Use search_tickets_by_category 
              with category="Hardware"
            - For incident searches: Use search_service_now with 
              table="incident" or table="all"
            - For general knowledge: Use search_knowledge_base
            - For specific ticket details: Use get_ticket_details
            
            ALWAYS call the appropriate tool function and provide detailed 
            information with actual data.
            """,
            tools=[
                search_knowledge_base,
                search_service_now,
                get_article_content,
                search_tickets_by_category
            ]
        )
        
        # Setup the agent with OCI
        self.agent.setup()
    
    def search(self, query: str, search_type: str = "knowledge") -> str:
        """
        Perform a search using the Search Agent
        
        Args:
            query (str): The search query
            search_type (str): Type of search ("knowledge" or "servicenow")
        
        Returns:
            str: The agent's response
        """
        # For now, let's use direct tool calls instead of the agent
        # This ensures we get real ServiceNow data
        
        if search_type == "servicenow" or "hardware" in query.lower() or "incident" in query.lower():
            # Use direct ServiceNow search
            from tools.search_tools import search_tickets_by_category, search_service_now
            
            # Check if it's a category-based query
            if "hardware" in query.lower():
                result = search_tickets_by_category("Hardware", limit=10)
                return self._format_search_result(result, "Hardware tickets")
            else:
                result = search_service_now(query, table="all", limit=10)
                return self._format_search_result(result, f"ServiceNow search for: {query}")
        else:
            # Use knowledge base search
            from tools.search_tools import search_knowledge_base
            result = search_knowledge_base(query)
            return self._format_search_result(result, f"Knowledge base search for: {query}")
    
    def _format_search_result(self, result: dict, search_type: str) -> str:
        """Format search results into a readable response"""
        if not result:
            return f"No results found for {search_type}."
        
        # Check for different result types
        total_results = result.get('total_results', 0)
        total_tickets = result.get('total_tickets', 0)
        
        if total_tickets == 0 and total_results == 0:
            return f"No results found for {search_type}."
        
        response = f"🔍 **{search_type}**\n\n"
        
        # Check if this is a knowledge base result first
        if ('Knowledge base' in search_type or 
            ('results' in result and result.get('results') and 
             not result.get('incidents') and not result.get('problems'))):
            # Knowledge base result
            response += "📊 **Summary:**\n"
            response += f"• Total Results: {total_results}\n\n"
            
            if result.get('results'):
                response += "📚 **Knowledge Base Articles:**\n"
                for i, article in enumerate(result['results'][:5], 1):
                    title = article.get('title', 'No title')
                    summary = article.get('summary', 'No summary')
                    url = article.get('url', '')
                    response += f"{i}. **{title}**\n"
                    response += f"   {summary}\n"
                    if url:
                        base_url = "https://dev218893.service-now.com"
                        if url.startswith('/'):
                            response += f"   🔗 [Read Article]({base_url}{url})\n"
                        else:
                            response += f"   🔗 [Read Article]({url})\n"
                    response += "\n"
            
            return response
        
        elif 'total_tickets' in result and total_tickets > 0:
            # Category search result
            response += f"📊 **Summary:**\n"
            response += f"• Total Tickets: {total_tickets}\n"
            response += f"• Incidents: {result.get('total_incidents', 0)}\n"
            response += f"• Problems: {result.get('total_problems', 0)}\n\n"
            
            if result.get('incidents'):
                response += f"📋 **Recent Incidents:**\n"
                for i, incident in enumerate(result['incidents'][:5], 1):
                    ticket_number = incident.get('number', 'N/A')
                    sys_id = incident.get('sys_id', '')
                    response += f"{i}. **{ticket_number}** - {incident.get('short_description', 'No description')}\n"
                    response += f"   Priority: {incident.get('priority', 'N/A')}, State: {incident.get('state', 'N/A')}\n"
                    if sys_id:
                        response += f"   🔗 [View Ticket](https://dev218893.service-now.com/incident.do?sys_id={sys_id})\n"
                    response += "\n"
            
            if result.get('problems'):
                response += f"🔧 **Recent Problems:**\n"
                for i, problem in enumerate(result['problems'][:3], 1):
                    ticket_number = problem.get('number', 'N/A')
                    sys_id = problem.get('sys_id', '')
                    response += f"{i}. **{ticket_number}** - {problem.get('short_description', 'No description')}\n"
                    response += f"   Priority: {problem.get('priority', 'N/A')}, State: {problem.get('state', 'N/A')}\n"
                    if sys_id:
                        response += f"   🔗 [View Problem](https://dev218893.service-now.com/problem.do?sys_id={sys_id})\n"
                    response += "\n"
        
        elif 'results' in result and total_results > 0:
            # ServiceNow search result
            response += "📊 **Summary:**\n"
            response += f"• Total Results: {total_results}\n\n"
            
            if result.get('results'):
                response += "📋 **Recent Tickets:**\n"
                for i, ticket in enumerate(result['results'][:5], 1):
                    ticket_number = ticket.get('number', 'N/A')
                    sys_id = ticket.get('sys_id', '')
                    ticket_type = ticket.get('ticket_type', 'N/A')
                    short_desc = ticket.get('short_description', 'No description')
                    priority = ticket.get('priority', 'N/A')
                    
                    response += f"{i}. **{ticket_number}** - {short_desc}\n"
                    response += f"   Type: {ticket_type}, Priority: {priority}\n"
                    
                    if sys_id:
                        base_url = "https://dev218893.service-now.com"
                        if 'Incident' in ticket_type:
                            response += f"   🔗 [View Incident]({base_url}/incident.do?sys_id={sys_id})\n"
                        elif 'Problem' in ticket_type:
                            response += f"   🔗 [View Problem]({base_url}/problem.do?sys_id={sys_id})\n"
                        elif 'Change' in ticket_type:
                            response += f"   🔗 [View Change]({base_url}/change_request.do?sys_id={sys_id})\n"
                    response += "\n"
        
        elif 'results' in result and result.get('results'):
            # Knowledge base result
            response += f"📚 **Knowledge Base Results:**\n"
            for i, article in enumerate(result['results'][:5], 1):
                title = article.get('title', 'No title')
                summary = article.get('summary', 'No summary')
                url = article.get('url', '')
                response += f"{i}. **{title}**\n"
                response += f"   {summary}\n"
                if url:
                    if url.startswith('/'):
                        response += f"   🔗 [Read Article](https://dev218893.service-now.com{url})\n"
                    else:
                        response += f"   🔗 [Read Article]({url})\n"
                response += "\n"
        
        return response
    
    def get_article(self, article_id: str) -> str:
        """
        Get detailed article content
        
        Args:
            article_id (str): The article identifier
        
        Returns:
            str: The article content
        """
        query = f"Get the full content of article: {article_id}"
        response = self.agent.run(query)
        return response.content if hasattr(response, 'content') else str(response)
