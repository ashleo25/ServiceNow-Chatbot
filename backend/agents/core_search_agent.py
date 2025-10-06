"""
Core Search Agent - Entry point for search operations
"""
from typing import Dict, Any, Optional
from backend.agents.response_formatter_agent import ResponseFormatterAgent
from backend.agents.search_orchestrator import SearchOrchestrator


class CoreSearchAgent:
    """
    Core Search Agent serves as the entry point for all search operations.
    This agent receives inputs from the chatbot UI and coordinates with
    the search orchestrator to provide comprehensive search results.
    """
    
    def __init__(self):
        """Initialize the Core Search Agent."""
        self.orchestrator = SearchOrchestrator()
        self.formatter = ResponseFormatterAgent()
        self.supported_search_types = [
            "knowledge", "servicenow", "category", "mixed", "auto"
        ]
    
    def search(self, query: str, search_type: str = "auto", 
               filters: Optional[Dict[str, Any]] = None) -> str:
        """
        Main search method that serves as the entry point for all searches.
        
        Args:
            query (str): The search query from user
            search_type (str): Type of search to perform
                - "auto": Automatically determine best search approach
                - "knowledge": Search knowledge base only
                - "servicenow": Search ServiceNow tickets only
                - "category": Search by ticket category
                - "mixed": Search both knowledge base and ServiceNow
            filters (Optional[Dict]): Additional search filters
        
        Returns:
            str: Formatted search response
        """
        try:
            # Validate inputs
            if not query.strip():
                return self.formatter.format_error_response(
                    "Empty search query provided", query
                )
            
            if search_type not in self.supported_search_types:
                search_type = "auto"
            
            # If auto mode, determine best search type
            if search_type == "auto":
                search_type = self._determine_search_type(query)
            
            # Delegate to orchestrator for actual search execution
            results = self.orchestrator.execute_search(
                query=query,
                search_type=search_type,
                filters=filters or {}
            )
            
            # Format results using response formatter
            if results:
                return self.formatter.format_search_response(results, search_type)
            else:
                return self.formatter.format_no_results_response(query, search_type)
        
        except Exception as e:
            return self.formatter.format_error_response(str(e), query)
    
    def _determine_search_type(self, query: str) -> str:
        """
        Automatically determine the best search type based on query content.
        
        Args:
            query (str): User search query
        
        Returns:
            str: Determined search type
        """
        query_lower = query.lower()
        
        # Keywords that indicate ServiceNow search
        servicenow_keywords = [
            "incident", "ticket", "problem", "issue", "bug", 
            "outage", "down", "error", "failure", "broken"
        ]
        
        # Keywords that indicate knowledge base search
        knowledge_keywords = [
            "how to", "guide", "tutorial", "documentation", 
            "manual", "procedure", "instructions", "help"
        ]
        
        # Category-specific keywords
        category_keywords = {
            "hardware": ["hardware", "server", "disk", "memory", "cpu"],
            "software": ["software", "application", "app", "program"],
            "network": ["network", "connection", "wifi", "internet", "dns"]
        }
        
        # Check for category matches first
        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return "category"
        
        # Count matches for each type
        servicenow_matches = sum(1 for keyword in servicenow_keywords 
                               if keyword in query_lower)
        knowledge_matches = sum(1 for keyword in knowledge_keywords 
                              if keyword in query_lower)
        
        # Decision logic
        if servicenow_matches > knowledge_matches:
            return "servicenow"
        elif knowledge_matches > servicenow_matches:
            return "knowledge"
        else:
            # If unclear, use mixed search for comprehensive results
            return "mixed"
    
    def get_search_capabilities(self) -> Dict[str, Any]:
        """
        Return information about search capabilities.
        
        Returns:
            Dict: Available search types and their descriptions
        """
        return {
            "supported_types": self.supported_search_types,
            "descriptions": {
                "auto": "Automatically determine the best search approach",
                "knowledge": "Search knowledge base articles and documentation",
                "servicenow": "Search ServiceNow tickets and records",
                "category": "Search tickets by specific categories",
                "mixed": "Search both knowledge base and ServiceNow"
            },
            "filters": {
                "category": "Filter by ticket category (Hardware, Software, Network)",
                "priority": "Filter by priority level",
                "state": "Filter by ticket state",
                "date_range": "Filter by date range"
            }
        }