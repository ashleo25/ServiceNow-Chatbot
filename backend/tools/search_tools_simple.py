"""
Simplified search tools for testing without OCI ADK
"""
from typing import Dict, List, Optional
import requests
import json


def search_knowledge_base(query: str, category: Optional[str] = None) -> Dict[str, any]:
    """
    Search the knowledge base for relevant information based on the query.
    
    Args:
        query (str): The search query string
        category (str, optional): Optional category to filter search results
    
    Returns:
        Dict containing search results with title, content, and relevance score
    """
    # Mock knowledge base search - replace with actual implementation
    mock_results = [
        {
            "title": "ServiceNow Incident Management",
            "content": "Incident management in ServiceNow helps track and resolve IT service disruptions...",
            "category": "incident_management",
            "relevance_score": 0.95,
            "url": "/knowledge/incident-management"
        },
        {
            "title": "User Account Management",
            "content": "Learn how to manage user accounts, reset passwords, and handle access requests...",
            "category": "user_management",
            "relevance_score": 0.87,
            "url": "/knowledge/user-account-management"
        },
        {
            "title": "System Maintenance Procedures",
            "content": "Standard procedures for system maintenance and scheduled downtime...",
            "category": "maintenance",
            "relevance_score": 0.82,
            "url": "/knowledge/system-maintenance"
        }
    ]
    
    # Filter by category if provided
    if category:
        mock_results = [r for r in mock_results if r["category"] == category]
    
    # Simple keyword matching for relevance
    query_lower = query.lower()
    filtered_results = []
    for result in mock_results:
        if any(keyword in result["content"].lower() or keyword in result["title"].lower() 
               for keyword in query_lower.split()):
            filtered_results.append(result)
    
    return {
        "query": query,
        "results": filtered_results[:5],  # Limit to top 5 results
        "total_results": len(filtered_results)
    }


def search_service_now(query: str, table: str = "incident") -> Dict[str, any]:
    """
    Search ServiceNow records based on the query.
    
    Args:
        query (str): The search query string
        table (str): ServiceNow table to search (default: incident)
    
    Returns:
        Dict containing ServiceNow search results
    """
    # Mock ServiceNow search - replace with actual ServiceNow API integration
    mock_servicenow_results = [
        {
            "sys_id": "INC0012345",
            "number": "INC0012345",
            "short_description": "Email server not responding",
            "state": "In Progress",
            "priority": "2 - High",
            "assigned_to": "John Smith",
            "created": "2024-01-15 10:30:00"
        },
        {
            "sys_id": "INC0012346",
            "number": "INC0012346", 
            "short_description": "VPN connection issues",
            "state": "New",
            "priority": "3 - Medium",
            "assigned_to": "Jane Doe",
            "created": "2024-01-15 11:15:00"
        }
    ]
    
    # Filter results based on query
    query_lower = query.lower()
    filtered_results = []
    for result in mock_servicenow_results:
        if (query_lower in result["short_description"].lower() or 
            query_lower in result["number"].lower()):
            filtered_results.append(result)
    
    return {
        "query": query,
        "table": table,
        "results": filtered_results,
        "total_results": len(filtered_results)
    }


def get_article_content(article_id: str) -> Dict[str, str]:
    """
    Retrieve the full content of a specific knowledge base article.
    
    Args:
        article_id (str): The unique identifier for the article
    
    Returns:
        Dict containing the article content and metadata
    """
    # Mock article content - replace with actual implementation
    mock_articles = {
        "incident-management": {
            "title": "ServiceNow Incident Management",
            "content": """
            Incident Management in ServiceNow is a critical process for IT service management.
            
            Key features include:
            - Automatic incident creation from monitoring tools
            - Assignment and routing based on categories
            - SLA tracking and escalation
            - Integration with change management
            
            Best practices:
            1. Always provide clear, descriptive incident titles
            2. Include relevant system information and error messages
            3. Update incidents regularly with progress notes
            4. Close incidents only after confirming resolution
            """,
            "last_updated": "2024-01-10",
            "author": "IT Knowledge Team"
        }
    }
    
    article = mock_articles.get(article_id, {
        "title": "Article Not Found",
        "content": "The requested article could not be found.",
        "last_updated": None,
        "author": None
    })
    
    return article
