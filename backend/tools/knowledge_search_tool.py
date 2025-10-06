"""
Knowledge Base Search Tool - Specialized for knowledge base operations
"""
from typing import Dict, Any
from oci.addons.adk import tool


@tool
def search_knowledge_base(query: str, category: str = None) -> Dict[str, Any]:
    """
    Search the knowledge base for articles and documentation.
    
    Args:
        query (str): Search query
        category (str): Optional category filter
    
    Returns:
        Dict containing knowledge base search results
    """
    # Mock implementation for now - in production this would connect to actual KB
    try:
        # Simulate knowledge base search
        results = []
        
        # Sample knowledge base articles
        sample_articles = [
            {
                "title": "How to Reset Password",
                "summary": "Step-by-step guide to reset user passwords in the system",
                "url": "/kb_view.do?sysparm_article=KB0001",
                "category": "Account Management"
            },
            {
                "title": "VPN Connection Issues",
                "summary": "Troubleshooting guide for VPN connectivity problems",
                "url": "/kb_view.do?sysparm_article=KB0002", 
                "category": "Network"
            },
            {
                "title": "Software Installation Guide",
                "summary": "Instructions for installing approved software applications",
                "url": "/kb_view.do?sysparm_article=KB0003",
                "category": "Software"
            },
            {
                "title": "Email Configuration",
                "summary": "How to configure email clients for corporate accounts",
                "url": "/kb_view.do?sysparm_article=KB0004",
                "category": "Email"
            }
        ]
        
        # Filter by query
        query_lower = query.lower()
        for article in sample_articles:
            if (query_lower in article["title"].lower() or 
                query_lower in article["summary"].lower() or
                (category and category.lower() in article["category"].lower())):
                results.append(article)
        
        # If no specific matches, return some relevant articles
        if not results and len(query_lower) > 2:
            results = sample_articles[:2]
        
        return {
            "results": results,
            "total_results": len(results),
            "search_type": "knowledge_base",
            "query": query,
            "category": category
        }
        
    except Exception as e:
        return {
            "results": [],
            "total_results": 0,
            "error": f"Knowledge base search failed: {str(e)}",
            "search_type": "knowledge_base",
            "query": query
        }


@tool  
def get_article_content(article_id: str) -> Dict[str, str]:
    """
    Get detailed content of a specific knowledge base article.
    
    Args:
        article_id (str): The article identifier
    
    Returns:
        Dict containing article details
    """
    try:
        # Mock article content - in production would fetch from actual KB
        articles = {
            "KB0001": {
                "title": "How to Reset Password",
                "content": """To reset your password:
                1. Go to the login page
                2. Click 'Forgot Password'
                3. Enter your email address
                4. Check your email for reset instructions
                5. Follow the link and create a new password""",
                "last_updated": "2024-01-15",
                "author": "IT Support Team"
            },
            "KB0002": {
                "title": "VPN Connection Issues", 
                "content": """If you're having VPN connection problems:
                1. Check your internet connection
                2. Verify VPN credentials
                3. Try a different VPN server
                4. Restart the VPN client
                5. Contact IT if issues persist""",
                "last_updated": "2024-01-10",
                "author": "Network Team"
            }
        }
        
        if article_id in articles:
            return {
                "success": True,
                "article": articles[article_id]
            }
        else:
            return {
                "success": False,
                "error": f"Article {article_id} not found"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to retrieve article: {str(e)}"
        }