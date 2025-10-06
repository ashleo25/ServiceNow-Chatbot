"""
OCI ADK Compliant Core Search Agent - Updated to follow OCI guidelines
"""
from typing import Dict, Any, Optional
from oci.addons.adk import Agent, AgentClient, tool
from config.config import Config
from tools.knowledge_search_tool import search_knowledge_base, get_article_content
from tools.servicenow_search_tool import search_service_now, search_tickets_by_category
from tools.search_utils import preprocess_query, extract_search_intent


class OciCompliantCoreSearchAgent:
    """
    OCI ADK Compliant Core Search Agent following Oracle's recommendations.
    
    This agent serves as a Supervisor Agent that orchestrates multiple
    specialized search tools (Collaborator Agents) following OCI's
    "Agent as a Tool" pattern.
    """
    
    def __init__(self, client: AgentClient):
        """Initialize the OCI ADK compliant Core Search Agent."""
        self.client = client
        
        # Initialize as OCI Agent with proper tool orchestration
        self.agent = Agent(
            client=client,
            agent_endpoint_id=Config.SEARCH_AGENT_ENDPOINT_ID,
            instructions="""
            You are an intelligent search orchestrator for IT support and ServiceNow operations.
            
            CORE RESPONSIBILITIES:
            1. Analyze user queries to determine optimal search strategy
            2. Orchestrate multiple specialized search tools
            3. Provide comprehensive, contextually relevant responses
            
            SEARCH STRATEGY:
            - For knowledge/documentation queries: Use search_knowledge_base
            - For ServiceNow ticket queries: Use search_service_now
            - For category-specific searches: Use search_tickets_by_category
            - For comprehensive searches: Use multiple tools and correlate results
            
            TOOL USAGE GUIDELINES:
            - Always preprocess queries for better results
            - Use intent detection to select appropriate tools
            - Combine results from multiple sources when beneficial
            - Provide structured, actionable responses with relevant links
            
            RESPONSE FORMAT:
            - Include search summaries with result counts
            - Provide direct links to tickets/articles
            - Offer relevant follow-up suggestions
            - Format responses for optimal user experience
            """,
            tools=[
                # Core search tools following OCI ADK pattern
                search_knowledge_base,
                search_service_now,
                get_article_content,
                search_tickets_by_category,
                self._orchestrate_mixed_search,
                self._analyze_search_intent
            ]
        )
        
        # Setup the agent with OCI
        self.agent.setup()
    
    @tool
    def _orchestrate_mixed_search(self, query: str, 
                                 search_scope: str = "comprehensive") -> Dict[str, Any]:
        """
        OCI ADK tool for orchestrating searches across multiple sources.
        
        Args:
            query (str): Search query
            search_scope (str): Scope of search (comprehensive, focused, targeted)
        
        Returns:
            Dict: Orchestrated search results from multiple sources
        """
        try:
            processed_query = preprocess_query(query)
            
            # Execute parallel searches based on scope
            results = {}
            
            if search_scope in ["comprehensive", "knowledge"]:
                kb_results = search_knowledge_base(processed_query)
                results["knowledge"] = kb_results
            
            if search_scope in ["comprehensive", "servicenow"]:
                sn_results = search_service_now(processed_query, table="all", limit=10)
                results["servicenow"] = sn_results
            
            # Merge and correlate results
            merged_results = self._merge_search_results(results)
            
            return {
                "status": "success",
                "search_type": "orchestrated_mixed",
                "query": query,
                "total_sources": len(results),
                "results": merged_results
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Mixed search orchestration failed: {str(e)}"
            }
    
    @tool
    def _analyze_search_intent(self, query: str) -> Dict[str, Any]:
        """
        OCI ADK tool for analyzing search intent and recommending strategy.
        
        Args:
            query (str): User search query
        
        Returns:
            Dict: Intent analysis and recommended search strategy
        """
        try:
            intent = extract_search_intent(query)
            processed_query = preprocess_query(query)
            
            # Determine optimal search strategy
            strategy = self._determine_search_strategy(query, intent)
            
            return {
                "status": "success",
                "original_query": query,
                "processed_query": processed_query,
                "detected_intent": intent,
                "recommended_strategy": strategy,
                "confidence": strategy.get("confidence", 0.8)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Intent analysis failed: {str(e)}"
            }
    
    def search(self, query: str, search_type: str = "auto", 
               filters: Optional[Dict[str, Any]] = None) -> str:
        """
        Main search method using OCI Agent's chat functionality.
        
        Args:
            query (str): Search query
            search_type (str): Type of search (auto, knowledge, servicenow, mixed)
            filters (Optional[Dict]): Additional search filters
        
        Returns:
            str: Agent's response using OCI ADK
        """
        try:
            # Construct agent prompt based on search type
            if search_type == "auto":
                prompt = f"Analyze this query and provide the most appropriate search results: {query}"
            elif search_type == "knowledge":
                prompt = f"Search the knowledge base for: {query}"
            elif search_type == "servicenow":
                prompt = f"Search ServiceNow tickets for: {query}"
            elif search_type == "mixed":
                prompt = f"Perform a comprehensive search across all sources for: {query}"
            else:
                prompt = f"Search for: {query}"
            
            # Add filters to prompt if provided
            if filters:
                filter_info = ", ".join([f"{k}: {v}" for k, v in filters.items()])
                prompt += f" (Filters: {filter_info})"
            
            # Use OCI Agent's chat method for intelligent response
            response = self.agent.chat(message=prompt)
            
            return response
        
        except Exception as e:
            return f"Search failed: {str(e)}. Please try again or contact support."
    
    def _merge_search_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Merge and correlate results from multiple search sources."""
        merged = {
            "total_results": 0,
            "sources": [],
            "knowledge_articles": [],
            "servicenow_tickets": [],
            "correlations": []
        }
        
        if "knowledge" in results and results["knowledge"]:
            kb_data = results["knowledge"]
            merged["knowledge_articles"] = kb_data.get("results", [])
            merged["total_results"] += kb_data.get("total_results", 0)
            merged["sources"].append("knowledge_base")
        
        if "servicenow" in results and results["servicenow"]:
            sn_data = results["servicenow"]
            merged["servicenow_tickets"] = sn_data.get("results", [])
            merged["total_results"] += sn_data.get("total_results", 0)
            merged["sources"].append("servicenow")
        
        return merged
    
    def _determine_search_strategy(self, query: str, intent: str) -> Dict[str, Any]:
        """Determine optimal search strategy based on query and intent."""
        query_lower = query.lower()
        
        strategies = {
            "knowledge_focused": {
                "tools": ["search_knowledge_base"],
                "confidence": 0.9,
                "reason": "Query indicates need for documentation/procedures"
            },
            "servicenow_focused": {
                "tools": ["search_service_now", "search_tickets_by_category"],
                "confidence": 0.9,
                "reason": "Query indicates need for ticket/incident information"
            },
            "comprehensive": {
                "tools": ["_orchestrate_mixed_search"],
                "confidence": 0.8,
                "reason": "Query could benefit from multiple sources"
            }
        }
        
        # Decision logic
        if any(kw in query_lower for kw in ["how to", "guide", "procedure", "documentation"]):
            return strategies["knowledge_focused"]
        elif any(kw in query_lower for kw in ["ticket", "incident", "problem", "outage"]):
            return strategies["servicenow_focused"]
        else:
            return strategies["comprehensive"]
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get OCI Agent status and configuration."""
        return {
            "agent_endpoint_id": Config.CORE_SEARCH_AGENT_ENDPOINT_ID,
            "tools_count": len(self.agent.tools),
            "available_tools": [tool.__name__ for tool in self.agent.tools],
            "status": "active" if self.agent else "inactive"
        }