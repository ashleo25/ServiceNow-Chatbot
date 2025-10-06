"""
Search Orchestrator - Optimized coordination for microservices search
"""
from typing import Dict, Any, Optional
from backend.tools.knowledge_search_tool import search_knowledge_base, get_article_content
from backend.tools.servicenow_search_tool import search_service_now, search_tickets_by_category, get_ticket_details
from backend.tools.search_utils import (
    preprocess_query, extract_search_intent, merge_search_results,
    validate_search_params, deduplicate_results
)
from config.logging_config import get_logger

logger = get_logger("search_orchestrator")


class SearchOrchestrator:
    """
    Optimized Search Orchestrator for microservices architecture.
    
    Responsibilities:
    - Control flow and intent routing
    - Coordinate specialized search tools
    - Merge results from multiple sources
    - Handle error recovery and fallbacks
    """
    
    def __init__(self):
        """Initialize the search orchestrator."""
        self.available_search_types = [
            "knowledge", "servicenow", "category", "mixed"
        ]
    
    def execute_search(self, query: str, search_type: str = "mixed", 
                      filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute search based on type and return structured results.
        
        Args:
            query (str): Search query
            search_type (str): Type of search to perform
            filters (Optional[Dict]): Additional search filters
        
        Returns:
            Dict: Structured search results
        """
        try:
            # Preprocess query
            processed_query = preprocess_query(query)
            intent = extract_search_intent(query)
            
            # Validate parameters
            if not validate_search_params(query, search_type, filters):
                return {"error": "Invalid search parameters"}
            
            logger.info(f"Executing {search_type} search for: {processed_query}")
            
            # Route to appropriate search method
            if search_type == "knowledge":
                return self._search_knowledge_base(processed_query, filters)
            elif search_type == "servicenow":
                return self._search_servicenow(processed_query, filters)
            elif search_type == "category":
                return self._search_by_category(processed_query, filters)
            elif search_type == "mixed":
                return self._search_mixed(processed_query, filters)
            else:
                return {"error": f"Unsupported search type: {search_type}"}
        
        except Exception as e:
            logger.error(f"Search execution error: {str(e)}")
            return {"error": str(e)}
    
    def _search_knowledge_base(self, query: str, 
                              filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Search knowledge base using specialized tool."""
        try:
            # Use knowledge search tool
            results = search_knowledge_base(query)
            
            if results:
                return {
                    "search_type": "knowledge_base",
                    "total_results": results.get("total_results", 0),
                    "results": results.get("results", []),
                    "query": query
                }
            else:
                return {"search_type": "knowledge_base", "total_results": 0}
        
        except Exception as e:
            logger.error(f"Knowledge base search error: {str(e)}")
            return {"error": f"Knowledge base search failed: {str(e)}"}
    
    def _search_servicenow(self, query: str, 
                          filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Search ServiceNow using specialized tool."""
        try:
            # Determine table to search
            table = filters.get("table", "all") if filters else "all"
            limit = filters.get("limit", 10) if filters else 10
            
            # Use ServiceNow search tool
            results = search_service_now(query, table=table, limit=limit)
            
            if results:
                return {
                    "search_type": "servicenow",
                    "total_results": results.get("total_results", 0),
                    "results": results.get("results", []),
                    "query": query
                }
            else:
                return {"search_type": "servicenow", "total_results": 0}
        
        except Exception as e:
            logger.error(f"ServiceNow search error: {str(e)}")
            return {"error": f"ServiceNow search failed: {str(e)}"}
    
    def _search_by_category(self, query: str, 
                           filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Search by category using specialized tool."""
        try:
            # Extract category from query or filters
            category = self._extract_category(query, filters)
            limit = filters.get("limit", 10) if filters else 10
            
            # Use category search tool
            results = search_tickets_by_category(category, limit=limit)
            
            if results:
                return {
                    "search_type": "category",
                    "category": category,
                    "total_tickets": results.get("total_tickets", 0),
                    "total_incidents": results.get("total_incidents", 0),
                    "total_problems": results.get("total_problems", 0),
                    "incidents": results.get("incidents", []),
                    "problems": results.get("problems", []),
                    "query": query
                }
            else:
                return {"search_type": "category", "total_tickets": 0}
        
        except Exception as e:
            logger.error(f"Category search error: {str(e)}")
            return {"error": f"Category search failed: {str(e)}"}
    
    def _search_mixed(self, query: str, 
                     filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute mixed search across multiple sources."""
        try:
            # Search both knowledge base and ServiceNow
            knowledge_results = self._search_knowledge_base(query, filters)
            servicenow_results = self._search_servicenow(query, filters)
            
            # Merge results
            merged_results = merge_search_results([
                knowledge_results, servicenow_results
            ])
            
            # Deduplicate if needed
            final_results = deduplicate_results(merged_results)
            
            return {
                "search_type": "mixed",
                "total_knowledge": knowledge_results.get("total_results", 0),
                "total_servicenow": servicenow_results.get("total_results", 0),
                "knowledge_results": knowledge_results.get("results", []),
                "servicenow_results": servicenow_results.get("results", []),
                "query": query
            }
        
        except Exception as e:
            logger.error(f"Mixed search error: {str(e)}")
            return {"error": f"Mixed search failed: {str(e)}"}
    
    def _extract_category(self, query: str, 
                         filters: Optional[Dict] = None) -> str:
        """Extract category from query or filters."""
        if filters and "category" in filters:
            return filters["category"]
        
        query_lower = query.lower()
        if "hardware" in query_lower:
            return "Hardware"
        elif "software" in query_lower:
            return "Software"
        elif "network" in query_lower:
            return "Network"
        else:
            return "General"
    
    def _determine_search_type(self, query: str, intent: str) -> SearchType:
        """Determine the type of search needed based on query and intent"""
        
        # Check intent-based routing first
        if intent.lower() in self.intent_routing:
            return self.intent_routing[intent.lower()]
        
        # Query-based analysis
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['article', 'documentation', 'how to', 'guide']):
            return SearchType.KNOWLEDGE_BASE
        elif any(keyword in query_lower for keyword in ['ticket', 'incident', 'problem', 'change']):
            return SearchType.SERVICENOW_TICKETS
        elif any(keyword in query_lower for keyword in ['hardware', 'software', 'network', 'security']):
            return SearchType.CATEGORY_BASED
        else:
            return SearchType.MIXED
    
    def _select_strategy(self, search_type: SearchType, user_context: Dict[str, Any] = None) -> SearchStrategy:
        """Select the best search strategy based on search type and context"""
        
        # Strategy selection rules
        if search_type == SearchType.KNOWLEDGE_BASE:
            # OCI Agent is better for knowledge base searches
            return SearchStrategy.OCI_AGENT_FIRST if self.search_agent else SearchStrategy.ENHANCED_SERVICE_FIRST
        
        elif search_type == SearchType.SERVICENOW_TICKETS:
            # Enhanced service might be better for complex ServiceNow queries
            return SearchStrategy.ENHANCED_SERVICE_FIRST
        
        elif search_type == SearchType.CATEGORY_BASED:
            # OCI Agent has good category tools
            return SearchStrategy.OCI_AGENT_FIRST if self.search_agent else SearchStrategy.ENHANCED_SERVICE_FIRST
        
        else:  # MIXED
            # Use parallel search for mixed queries
            return SearchStrategy.PARALLEL if self.search_agent else SearchStrategy.ENHANCED_SERVICE_FIRST
    
    def _execute_search(self, query: str, intent: str, search_type: SearchType, strategy: SearchStrategy) -> Dict[str, Any]:
        """Execute search based on the selected strategy"""
        
        if strategy == SearchStrategy.OCI_AGENT_FIRST:
            return self._execute_oci_first(query, intent, search_type)
        
        elif strategy == SearchStrategy.ENHANCED_SERVICE_FIRST:
            return self._execute_enhanced_first(query, intent, search_type)
        
        elif strategy == SearchStrategy.PARALLEL:
            return self._execute_parallel(query, intent, search_type)
        
        elif strategy == SearchStrategy.FALLBACK_CHAIN:
            return self._execute_fallback_chain(query, intent, search_type)
        
        else:
            raise ValueError(f"Unknown search strategy: {strategy}")
    
    def _execute_oci_first(self, query: str, intent: str, search_type: SearchType) -> Dict[str, Any]:
        """Execute OCI Agent search first, fallback to enhanced service"""
        
        if not self.search_agent:
            return self._execute_enhanced_search(query, intent)
        
        try:
            # Try OCI Agent first
            search_query_type = "knowledge" if search_type == SearchType.KNOWLEDGE_BASE else "servicenow"
            oci_results = self.search_agent.search(query, search_query_type)
            
            return {
                'primary_results': oci_results,
                'primary_source': 'oci_agent',
                'fallback_used': False,
                'search_successful': True
            }
            
        except Exception as e:
            logger.warning(f"OCI Agent search failed, falling back to enhanced service: {str(e)}")
            # Fallback to enhanced service
            enhanced_results = self._execute_enhanced_search(query, intent)
            enhanced_results['fallback_used'] = True
            enhanced_results['primary_source'] = 'enhanced_service'
            enhanced_results['oci_error'] = str(e)
            return enhanced_results
    
    def _execute_enhanced_first(self, query: str, intent: str, search_type: SearchType) -> Dict[str, Any]:
        """Execute Enhanced Service search first"""
        return self._execute_enhanced_search(query, intent)
    
    def _execute_parallel(self, query: str, intent: str, search_type: SearchType) -> Dict[str, Any]:
        """Execute both searches in parallel and merge results"""
        
        if not self.search_agent:
            return self._execute_enhanced_search(query, intent)
        
        try:
            # Execute both searches
            search_query_type = "knowledge" if search_type == SearchType.KNOWLEDGE_BASE else "servicenow"
            oci_results = self.search_agent.search(query, search_query_type)
            enhanced_results = self._execute_enhanced_search(query, intent)
            
            # Merge results
            return {
                'oci_results': oci_results,
                'enhanced_results': enhanced_results['primary_results'],
                'primary_source': 'parallel',
                'search_successful': True,
                'fallback_used': False
            }
            
        except Exception as e:
            logger.error(f"Parallel search failed: {str(e)}")
            # Fallback to enhanced only
            return self._execute_enhanced_search(query, intent)
    
    def _execute_enhanced_search(self, query: str, intent: str) -> Dict[str, Any]:
        """Execute enhanced search service"""
        try:
            results = self.enhanced_search.search_all(query, intent)
            return {
                'primary_results': results,
                'primary_source': 'enhanced_service',
                'search_successful': True,
                'fallback_used': False
            }
        except Exception as e:
            logger.error(f"Enhanced search failed: {str(e)}")
            return {
                'primary_results': None,
                'primary_source': 'none',
                'search_successful': False,
                'error': str(e)
            }
    
    def _format_results(self, results: Dict[str, Any], search_type: SearchType, strategy: SearchStrategy) -> Dict[str, Any]:
        """Format and standardize search results"""
        
        if not results.get('search_successful', False):
            return {
                'success': False,
                'error': results.get('error', 'Unknown search error'),
                'results': [],
                'total_results': 0
            }
        
        # Extract primary results
        primary_results = results.get('primary_results')
        if isinstance(primary_results, str):
            # OCI Agent returns formatted string
            return {
                'success': True,
                'formatted_response': primary_results,
                'source': results.get('primary_source', 'unknown'),
                'search_type': search_type.value,
                'strategy': strategy.value
            }
        elif isinstance(primary_results, dict):
            # Enhanced service returns structured data
            return {
                'success': True,
                'results': primary_results.get('results', []),
                'total_results': primary_results.get('total_results', 0),
                'source': results.get('primary_source', 'unknown'),
                'search_type': search_type.value,
                'strategy': strategy.value
            }
        else:
            return {
                'success': False,
                'error': 'Invalid result format',
                'results': [],
                'total_results': 0
            }
    
    def _handle_search_error(self, query: str, intent: str, error_msg: str) -> Dict[str, Any]:
        """Handle search errors gracefully"""
        return {
            'success': False,
            'error': error_msg,
            'query': query,
            'intent': intent,
            'fallback_message': "I'm sorry, I'm having trouble searching right now. Please try again later or contact support.",
            'results': [],
            'total_results': 0
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    # Health check methods
    def health_check(self) -> Dict[str, Any]:
        """Check health of all search services"""
        health = {
            'orchestrator': 'healthy',
            'oci_agent': 'unavailable',
            'enhanced_service': 'unknown'
        }
        
        # Check OCI Agent
        if self.search_agent:
            try:
                # Simple test search
                test_result = self.search_agent.search("test", "knowledge")
                health['oci_agent'] = 'healthy' if test_result else 'unhealthy'
            except Exception:
                health['oci_agent'] = 'unhealthy'
        
        # Check Enhanced Service
        try:
            test_result = self.enhanced_search.search_all("test", "general")
            health['enhanced_service'] = 'healthy' if test_result else 'unhealthy'
        except Exception:
            health['enhanced_service'] = 'unhealthy'
        
        return health