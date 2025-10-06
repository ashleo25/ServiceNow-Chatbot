"""
Search Utilities - Common utilities for search operations
"""
from typing import Dict, Any, List
import re


def preprocess_query(query: str) -> str:
    """
    Preprocess search query for better results.
    
    Args:
        query (str): Raw search query
    
    Returns:
        str: Processed query
    """
    if not query:
        return ""
    
    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query.strip())
    
    # Remove special characters that might interfere with search
    query = re.sub(r'[^\w\s-]', '', query)
    
    return query


def deduplicate_results(results: List[Dict], key_field: str = "sys_id") -> List[Dict]:
    """
    Remove duplicate results based on a key field.
    
    Args:
        results (List[Dict]): List of result dictionaries
        key_field (str): Field to use for deduplication
    
    Returns:
        List[Dict]: Deduplicated results
    """
    seen = set()
    deduplicated = []
    
    for result in results:
        key_value = result.get(key_field)
        if key_value and key_value not in seen:
            seen.add(key_value)
            deduplicated.append(result)
    
    return deduplicated


def validate_search_params(query: str, limit: int = None) -> Dict[str, Any]:
    """
    Validate search parameters.
    
    Args:
        query (str): Search query
        limit (int): Result limit
    
    Returns:
        Dict: Validation result with success flag and errors
    """
    errors = []
    
    if not query or len(query.strip()) < 2:
        errors.append("Query must be at least 2 characters long")
    
    if limit is not None and (limit < 1 or limit > 100):
        errors.append("Limit must be between 1 and 100")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def extract_search_intent(query: str) -> str:
    """
    Extract search intent from query text.
    
    Args:
        query (str): Search query
    
    Returns:
        str: Detected intent
    """
    query_lower = query.lower()
    
    # Knowledge base indicators
    if any(keyword in query_lower for keyword in 
           ['how to', 'guide', 'instruction', 'documentation', 'article']):
        return "knowledge"
    
    # ServiceNow ticket indicators
    if any(keyword in query_lower for keyword in 
           ['ticket', 'incident', 'problem', 'issue', 'bug']):
        return "servicenow"
    
    # Category indicators
    if any(keyword in query_lower for keyword in 
           ['hardware', 'software', 'network', 'security']):
        return "category"
    
    return "general"


def merge_search_results(knowledge_results: Dict, servicenow_results: Dict) -> Dict[str, Any]:
    """
    Merge results from multiple search sources.
    
    Args:
        knowledge_results (Dict): Knowledge base results
        servicenow_results (Dict): ServiceNow results
    
    Returns:
        Dict: Merged results
    """
    merged = {
        "knowledge_results": knowledge_results.get("results", []),
        "servicenow_results": servicenow_results.get("results", []),
        "total_knowledge": knowledge_results.get("total_results", 0),
        "total_servicenow": servicenow_results.get("total_results", 0),
        "search_type": "mixed",
        "sources": ["knowledge_base", "servicenow"]
    }
    
    merged["total_results"] = merged["total_knowledge"] + merged["total_servicenow"]
    
    return merged