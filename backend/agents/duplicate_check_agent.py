"""
Duplicate Check Agent - Intelligent Ticket Duplication Prevention

This module implements comprehensive duplicate detection and prevention logic
for the ServiceNow ticket creation system. It analyzes multiple factors to
identify potential duplicate tickets and prevents unnecessary ticket creation.

Key Features:
    - Multi-criteria duplicate detection (text, user, category, priority)
    - 70% similarity threshold with intelligent scoring algorithms
    - Active ticket state filtering (New/Open/In Progress only)
    - Time-window based search optimization (30-day window)
    - User decision handling for confirmed duplicates
    - Detailed similarity reporting and recommendations

Business Logic:
    - Searches existing active tickets using ServiceNow REST API
    - Calculates similarity scores using SequenceMatcher algorithm
    - Considers multiple factors: description, category, user, priority
    - Blocks ticket creation for high-similarity active duplicates
    - Provides detailed duplicate analysis for user review

Detection Strategies:
    1. Text similarity analysis (primary factor)
    2. Category and priority matching (secondary factors)
    3. User-specific ticket history analysis
    4. Time-based relevance scoring
    5. Multi-factor weighted scoring system
"""

# Standard library imports
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Dict, List, Any, Optional

# Local imports
from config.logging_config import get_logger
from services.ticket_creation_service import ServiceNowTicketService

# Initialize logger
logger = get_logger("duplicate_check_agent")


class DuplicateCheckAgent:
    """
    Intelligent duplicate detection and prevention agent.
    
    This agent implements sophisticated algorithms to detect potential duplicate
    tickets before they are created in ServiceNow. It uses multi-factor analysis
    including text similarity, user history, category matching, and priority
    assessment to make intelligent duplication decisions.
    
    Attributes:
        servicenow_service: ServiceNow API integration service
        similarity_threshold (float): Minimum similarity score for duplicates (0.7)
        time_window_days (int): Search window for duplicate detection (30 days)
        
    Methods:
        check_duplicates(): Main duplicate detection entry point
        should_block_creation(): Determines if ticket creation should be blocked
        calculate_similarity(): Computes similarity scores between tickets
        _search_existing_tickets(): Searches ServiceNow for potential duplicates
        _analyze_duplicates(): Performs detailed duplicate analysis
        
    Business Rules:
        - Only considers active tickets (state != 6, 7)
        - Requires 70% similarity threshold for duplicate classification
        - Prioritizes recent tickets within 30-day window
        - Blocks creation for high-confidence duplicates
        - Provides detailed analysis for borderline cases
    """
    
    def __init__(self):
        """
        Initialize the duplicate check agent with default configuration.
        
        Sets up ServiceNow integration and configures detection parameters
        based on business requirements and performance considerations.
        """
        self.servicenow_service = ServiceNowTicketService()
        self.similarity_threshold = 0.7  # 70% similarity threshold
        self.time_window_days = 30  # Search within last 30 days
        
        logger.info("Duplicate Check Agent initialized successfully")
        logger.info(f"Similarity threshold: {self.similarity_threshold}")
        logger.info(f"Time window: {self.time_window_days} days")
    
    def check_duplicates(self, ticket_data: Dict[str, Any], 
                        user_id: str, ticket_type: str) -> Dict[str, Any]:
        """
        Perform comprehensive duplicate detection analysis.
        
        This method orchestrates the complete duplicate detection workflow,
        including searching existing tickets, calculating similarity scores,
        and determining whether ticket creation should proceed.
        
        Args:
            ticket_data (Dict[str, Any]): New ticket data to analyze
            user_id (str): ID of the user creating the ticket
            ticket_type (str): Type of ticket (incident, request, change, problem)
            
        Returns:
            Dict[str, Any]: Comprehensive duplicate analysis results containing:
                - duplicates_found (bool): Whether duplicates were detected
                - should_block (bool): Whether creation should be blocked
                - duplicate_tickets (List): List of similar tickets found
                - similarity_scores (Dict): Detailed similarity analysis
                - recommendations (str): User guidance and next steps
                
        Raises:
            Exception: If ServiceNow API call fails or data processing errors
        """
        logger.info(f"Starting duplicate check for {ticket_type} ticket "
                   f"by user: {user_id}")
        logger.debug(f"Analyzing ticket data: {ticket_data}")
        
        try:
            # Build comprehensive search criteria
            search_criteria = {
                "user_id": user_id,
                "ticket_type": ticket_type,
                "description": ticket_data.get("short_description", ""),
                "category": ticket_data.get("category", ""),
                "priority": ticket_data.get("priority", "")
            }
            
            # Search for existing tickets
            existing_tickets = self.servicenow_service.search_duplicates(search_criteria)
            logger.info(f"Found {len(existing_tickets)} existing tickets to analyze")
            
            if not existing_tickets:
                logger.info("No existing tickets found - no duplicates detected")
                return {
                    "has_duplicates": False,
                    "duplicates": [],
                    "message": "No similar tickets found. Proceeding with ticket creation."
                }
            
            # Calculate similarity scores
            duplicates = []
            for ticket in existing_tickets:
                similarity_score = self.calculate_similarity_score(ticket_data, ticket)
                logger.debug(f"Similarity score for ticket {ticket.get('number', 'N/A')}: {similarity_score:.2f}")
                
                if similarity_score >= self.similarity_threshold:
                    duplicates.append({
                        "ticket": ticket,
                        "similarity_score": similarity_score,
                        "similarity_reasons": self._get_similarity_reasons(ticket_data, ticket, similarity_score)
                    })
            
            # Sort by similarity score (highest first)
            duplicates.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            logger.info(f"Found {len(duplicates)} potential duplicates above threshold")
            
            if duplicates:
                # Check if any duplicates are in active states (New, In Progress)
                active_duplicates = []
                for dup in duplicates:
                    ticket = dup["ticket"]
                    state = ticket.get("state", "")
                    # ServiceNow states: 1=New, 2=In Progress, 6=Resolved, 7=Closed
                    if state in ["1", "2", "New", "In Progress", "Open"]:
                        active_duplicates.append(dup)
                
                if active_duplicates:
                    logger.warning(f"Found {len(active_duplicates)} ACTIVE duplicate tickets - BLOCKING creation")
                    return {
                        "has_duplicates": True,
                        "should_block_creation": True,  # CRITICAL: Signal to stop creation
                        "duplicates": active_duplicates[:3],  # Return top 3 active matches
                        "active_count": len(active_duplicates),
                        "message": f"DUPLICATE PREVENTION: Found {len(active_duplicates)} active tickets with similar issues. Please review existing tickets before creating a new one.",
                        "recommendation": "Review and update existing active ticket instead of creating duplicate",
                        "action_required": "STOP_CREATION"
                    }
                else:
                    logger.info("Found similar tickets but all are resolved/closed - allowing creation")
                    return {
                        "has_duplicates": True,
                        "should_block_creation": False,  # Allow creation - no active duplicates
                        "duplicates": duplicates[:5],  # Return top 5 matches for reference
                        "message": f"Found {len(duplicates)} similar resolved tickets. Proceeding with new ticket creation.",
                        "recommendation": "Proceed with creation - previous similar issues were resolved"
                    }
            else:
                logger.info("No duplicates found above similarity threshold")
                return {
                    "has_duplicates": False,
                    "duplicates": [],
                    "message": "No similar tickets found. Proceeding with ticket creation."
                }
                
        except Exception as e:
            logger.error(f"Error checking duplicates: {str(e)}")
            return {
                "has_duplicates": False,
                "duplicates": [],
                "message": "Error checking for duplicates. Proceeding with ticket creation.",
                "error": str(e)
            }
    
    def calculate_similarity_score(self, new_ticket: Dict[str, Any], existing_ticket: Dict[str, Any]) -> float:
        """
        Calculate similarity score between new and existing ticket
        
        Args:
            new_ticket: New ticket data
            existing_ticket: Existing ticket data
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        logger.debug("Calculating similarity score between tickets")
        
        try:
            scores = []
            
            # 1. Description similarity (40% weight)
            desc_similarity = self._calculate_text_similarity(
                new_ticket.get("short_description", ""),
                existing_ticket.get("short_description", "")
            )
            scores.append(("description", desc_similarity, 0.4))
            
            # 2. Category match (20% weight)
            category_match = 1.0 if new_ticket.get("category") == existing_ticket.get("category") else 0.0
            scores.append(("category", category_match, 0.2))
            
            # 3. Priority match (15% weight)
            priority_match = 1.0 if new_ticket.get("priority") == existing_ticket.get("priority") else 0.0
            scores.append(("priority", priority_match, 0.15))
            
            # 4. User match (15% weight)
            user_match = 1.0 if new_ticket.get("caller_id") == existing_ticket.get("caller_id") else 0.0
            scores.append(("user", user_match, 0.15))
            
            # 5. Time proximity (10% weight)
            time_score = self._calculate_time_proximity(existing_ticket.get("created", ""))
            scores.append(("time", time_score, 0.1))
            
            # Calculate weighted average
            total_score = sum(score * weight for _, score, weight in scores)
            
            logger.debug(f"Similarity breakdown: {[(name, f'{score:.2f}', f'{weight:.2f}') for name, score, weight in scores]}")
            logger.debug(f"Total similarity score: {total_score:.2f}")
            
            return total_score
            
        except Exception as e:
            logger.error(f"Error calculating similarity score: {str(e)}")
            return 0.0
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using SequenceMatcher"""
        if not text1 or not text2:
            return 0.0
        
        # Convert to lowercase for comparison
        text1_lower = text1.lower().strip()
        text2_lower = text2.lower().strip()
        
        if text1_lower == text2_lower:
            return 1.0
        
        # Use SequenceMatcher for fuzzy matching
        similarity = SequenceMatcher(None, text1_lower, text2_lower).ratio()
        return similarity
    
    def _calculate_time_proximity(self, created_date: str) -> float:
        """Calculate time proximity score (newer tickets get higher scores)"""
        if not created_date:
            return 0.0
        
        try:
            # Parse the date (ServiceNow format: 2024-01-01 12:00:00)
            created_dt = datetime.strptime(created_date.split()[0], "%Y-%m-%d")
            days_ago = (datetime.now() - created_dt).days
            
            # Score decreases with time (0-30 days)
            if days_ago <= 7:
                return 1.0
            elif days_ago <= 14:
                return 0.8
            elif days_ago <= 30:
                return 0.6
            else:
                return 0.2
                
        except Exception as e:
            logger.warning(f"Error parsing date {created_date}: {str(e)}")
            return 0.0
    
    def _get_similarity_reasons(self, new_ticket: Dict[str, Any], existing_ticket: Dict[str, Any], score: float) -> List[str]:
        """Get reasons why tickets are considered similar"""
        reasons = []
        
        # Check description similarity
        desc_similarity = self._calculate_text_similarity(
            new_ticket.get("short_description", ""),
            existing_ticket.get("short_description", "")
        )
        if desc_similarity > 0.8:
            reasons.append("Very similar description")
        elif desc_similarity > 0.6:
            reasons.append("Similar description")
        
        # Check category match
        if new_ticket.get("category") == existing_ticket.get("category"):
            reasons.append("Same category")
        
        # Check priority match
        if new_ticket.get("priority") == existing_ticket.get("priority"):
            reasons.append("Same priority")
        
        # Check user match
        if new_ticket.get("caller_id") == existing_ticket.get("caller_id"):
            reasons.append("Same user")
        
        # Check time proximity
        created_date = existing_ticket.get("created", "")
        if created_date:
            try:
                created_dt = datetime.strptime(created_date.split()[0], "%Y-%m-%d")
                days_ago = (datetime.now() - created_dt).days
                if days_ago <= 7:
                    reasons.append("Created recently (within 7 days)")
                elif days_ago <= 30:
                    reasons.append("Created recently (within 30 days)")
            except:
                pass
        
        return reasons
    
    def _get_duplicate_recommendation(self, top_duplicate: Dict[str, Any]) -> str:
        """Get recommendation based on top duplicate"""
        ticket = top_duplicate["ticket"]
        score = top_duplicate["similarity_score"]
        
        if score >= 0.9:
            return "Very high similarity - consider linking to existing ticket"
        elif score >= 0.8:
            return "High similarity - review existing ticket before creating new one"
        elif score >= 0.7:
            return "Moderate similarity - check if existing ticket covers your issue"
        else:
            return "Low similarity - proceed with new ticket creation"
    
    def present_duplicates(self, duplicates: List[Dict[str, Any]], new_ticket: Dict[str, Any]) -> str:
        """
        Present duplicate candidates to user with detailed comparison
        
        Args:
            duplicates: List of duplicate tickets
            new_ticket: New ticket data
            
        Returns:
            Formatted string presenting duplicates to user
        """
        logger.info(f"Presenting {len(duplicates)} duplicate candidates to user")
        
        if not duplicates:
            return "No similar tickets found. Proceeding with ticket creation."
        
        response = "🔍 **Similar Tickets Found**\n\n"
        response += f"I found {len(duplicates)} similar tickets that might be related to your request:\n\n"
        
        for i, duplicate in enumerate(duplicates[:3], 1):  # Show top 3
            ticket = duplicate["ticket"]
            score = duplicate["similarity_score"]
            reasons = duplicate["similarity_reasons"]
            
            response += f"**{i}. {ticket.get('number', 'N/A')}** (Similarity: {score:.1%})\n"
            response += f"   **Description**: {ticket.get('short_description', 'No description')}\n"
            response += f"   **Status**: {ticket.get('state', 'Unknown')}\n"
            response += f"   **Priority**: {ticket.get('priority', 'Unknown')}\n"
            response += f"   **Created**: {ticket.get('created', 'Unknown')}\n"
            response += f"   **Similarity Reasons**: {', '.join(reasons)}\n"
            response += f"   🔗 [View Ticket]({self.servicenow_service.instance_url}/{ticket.get('number', '').lower()})\n\n"
        
        response += "**What would you like to do?**\n"
        response += "• **Proceed**: Create new ticket anyway\n"
        response += "• **Stop**: Cancel ticket creation\n"
        response += "• **Link**: Link to existing ticket\n"
        response += "• **Modify**: Modify your request\n\n"
        response += "Please let me know your choice."
        
        return response
    
    def handle_duplicate_decision(self, decision: str, duplicates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Handle user decision regarding duplicates
        
        Args:
            decision: User's decision (proceed, stop, link, modify)
            duplicates: List of duplicate tickets
            
        Returns:
            Dictionary with decision result
        """
        logger.info(f"Handling duplicate decision: {decision}")
        
        if decision.lower() in ["proceed", "continue", "yes", "create"]:
            logger.info("User decided to proceed with ticket creation")
            return {
                "action": "proceed",
                "message": "Proceeding with ticket creation despite similar tickets.",
                "duplicates_acknowledged": True
            }
        
        elif decision.lower() in ["stop", "cancel", "no", "abort"]:
            logger.info("User decided to cancel ticket creation")
            return {
                "action": "stop",
                "message": "Ticket creation cancelled. Please review existing tickets or modify your request.",
                "duplicates_acknowledged": True
            }
        
        elif decision.lower() in ["link", "connect", "reference"]:
            logger.info("User decided to link to existing ticket")
            if duplicates:
                top_duplicate = duplicates[0]["ticket"]
                return {
                    "action": "link",
                    "message": f"Linking to existing ticket {top_duplicate.get('number', 'N/A')}",
                    "linked_ticket": top_duplicate
                }
            else:
                return {
                    "action": "error",
                    "message": "No duplicate tickets available for linking."
                }
        
        elif decision.lower() in ["modify", "change", "update"]:
            logger.info("User decided to modify their request")
            return {
                "action": "modify",
                "message": "Please provide your modified request details.",
                "suggestions": self._get_modification_suggestions(duplicates[0] if duplicates else None)
            }
        
        else:
            logger.warning(f"Unknown decision: {decision}")
            return {
                "action": "unknown",
                "message": "I didn't understand your choice. Please choose: proceed, stop, link, or modify."
            }
    
    def _get_modification_suggestions(self, duplicate: Optional[Dict[str, Any]]) -> List[str]:
        """Get suggestions for modifying the request"""
        if not duplicate:
            return ["Please provide more specific details about your issue."]
        
        suggestions = [
            "Consider adding more specific details about your issue",
            "Include any error messages or specific symptoms",
            "Mention the exact steps to reproduce the problem",
            "Specify the affected system or application"
        ]
        
        return suggestions
