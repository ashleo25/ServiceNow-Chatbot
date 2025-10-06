"""
Priority and SLA Assignment Agent
Implements intelligent priority and SLA logic based on ServiceNow best practices
"""
import logging
import re
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
from config.logging_config import get_logger

logger = get_logger("priority_sla_agent")

class PrioritySLAAgent:
    """
    Agent responsible for intelligent priority and SLA assignment
    """
    
    def __init__(self):
        self.priority_keywords = {
            'critical': {
                'keywords': ['down', 'outage', 'crashed', 'breach', 'security', 'data loss', 'complete failure', 'system down'],
                'priority': 1,
                'weight': 10
            },
            'high': {
                'keywords': ['urgent', 'critical', 'vip', 'ceo', 'production', 'severe', 'major', 'broken'],
                'priority': 2,
                'weight': 8
            },
            'medium': {
                'keywords': ['slow', 'error', 'issue', 'problem', 'not working', 'trouble', 'difficulty'],
                'priority': 3,
                'weight': 5
            },
            'low': {
                'keywords': ['request', 'access', 'password', 'install', 'question', 'help', 'information'],
                'priority': 4,
                'weight': 3
            },
            'planning': {
                'keywords': ['enhancement', 'feature', 'improvement', 'future', 'documentation', 'training'],
                'priority': 5,
                'weight': 1
            }
        }
        
        self.impact_keywords = {
            'organization': ['everyone', 'all users', 'entire company', 'company-wide', 'organization-wide'],
            'department': ['department', 'team', 'group', 'division'],
            'individual': ['me', 'my', 'personal', 'individual']
        }
        
        self.sla_rules = {
            1: {'response_hours': 1, 'resolution_hours': 4, 'business_hours_only': False},
            2: {'response_hours': 4, 'resolution_hours': 8, 'business_hours_only': True},
            3: {'response_hours': 8, 'resolution_hours': 24, 'business_hours_only': True},
            4: {'response_hours': 24, 'resolution_hours': 40, 'business_hours_only': True},
            5: {'response_hours': 48, 'resolution_hours': 80, 'business_hours_only': True}
        }
        
        logger.info("PrioritySLAAgent initialized with comprehensive rules")

    def assign_priority_and_sla(self, ticket_data: Dict[str, Any], intent: str) -> Dict[str, Any]:
        """
        Assign priority and SLA based on ticket data and intent
        
        Args:
            ticket_data: Collected ticket information
            intent: Detected intent (Incident, Request, Change, Problem)
            
        Returns:
            Dict with priority, SLA, and reasoning
        """
        try:
            logger.info(f"Assigning priority and SLA for {intent} ticket")
            
            # Extract text for analysis
            description = ticket_data.get('detailed_description', '') or ticket_data.get('description', '')
            short_description = ticket_data.get('short_description', '')
            impact_scope = ticket_data.get('impact_scope', '')
            urgency = ticket_data.get('urgency', '')
            
            # Combine all text for analysis
            full_text = f"{short_description} {description} {impact_scope} {urgency}".lower()
            
            # Calculate priority score
            priority_score = self._calculate_priority_score(full_text, impact_scope, urgency)
            
            # Determine final priority
            priority = self._determine_priority(priority_score, intent)
            
            # Calculate SLA
            sla = self._calculate_sla(priority, intent)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(priority, sla, full_text, impact_scope, urgency)
            
            result = {
                'priority': priority,
                'priority_name': self._get_priority_name(priority),
                'sla': sla,
                'reasoning': reasoning,
                'auto_assigned': True
            }
            
            logger.info(f"Assigned Priority {priority} ({result['priority_name']}) with SLA: {sla['response_time']} response, {sla['resolution_time']} resolution")
            
            return result
            
        except Exception as e:
            logger.error(f"Error assigning priority and SLA: {str(e)}")
            # Return default priority and SLA
            return self._get_default_priority_sla(intent)

    def _calculate_priority_score(self, text: str, impact_scope: str, urgency: str) -> int:
        """Calculate priority score based on text analysis"""
        score = 0
        
        # Analyze keywords
        for category, data in self.priority_keywords.items():
            for keyword in data['keywords']:
                if keyword in text:
                    score += data['weight']
                    logger.debug(f"Found {category} keyword '{keyword}' - adding {data['weight']} points")
        
        # Analyze impact scope
        impact_scope_lower = impact_scope.lower()
        if any(keyword in impact_scope_lower for keyword in self.impact_keywords['organization']):
            score += 15
            logger.debug("Organization-wide impact detected - adding 15 points")
        elif any(keyword in impact_scope_lower for keyword in self.impact_keywords['department']):
            score += 8
            logger.debug("Department-wide impact detected - adding 8 points")
        elif any(keyword in impact_scope_lower for keyword in self.impact_keywords['individual']):
            score += 3
            logger.debug("Individual impact detected - adding 3 points")
        
        # Analyze urgency
        urgency_lower = urgency.lower()
        if 'critical' in urgency_lower:
            score += 12
        elif 'high' in urgency_lower:
            score += 8
        elif 'medium' in urgency_lower:
            score += 4
        elif 'low' in urgency_lower:
            score += 1
            
        return score

    def _determine_priority(self, score: int, intent: str) -> int:
        """Determine final priority based on score and intent"""
        # Adjust thresholds based on intent
        if intent.lower() in ['incident', 'problem']:
            # Incidents and problems can be more critical
            if score >= 25:
                return 1
            elif score >= 18:
                return 2
            elif score >= 10:
                return 3
            elif score >= 5:
                return 4
            else:
                return 5
        else:
            # Requests and changes are typically lower priority
            if score >= 30:
                return 2
            elif score >= 20:
                return 3
            elif score >= 10:
                return 4
            else:
                return 5

    def _calculate_sla(self, priority: int, intent: str) -> Dict[str, Any]:
        """Calculate SLA based on priority and intent"""
        sla_rule = self.sla_rules.get(priority, self.sla_rules[5])
        
        # Adjust SLA for different intents
        if intent.lower() == 'incident':
            # Incidents get faster response
            response_hours = max(1, sla_rule['response_hours'] - 1)
        elif intent.lower() == 'request':
            # Requests can be slower
            response_hours = sla_rule['response_hours'] + 2
        else:
            response_hours = sla_rule['response_hours']
        
        # Calculate resolution time
        resolution_hours = sla_rule['resolution_hours']
        
        # Convert to business days if needed
        if sla_rule['business_hours_only']:
            response_time = f"{response_hours} business hours"
            resolution_time = f"{resolution_hours // 8} business days"
        else:
            response_time = f"{response_hours} hours"
            resolution_time = f"{resolution_hours} hours"
        
        return {
            'response_time': response_time,
            'resolution_time': resolution_time,
            'business_hours_only': sla_rule['business_hours_only'],
            'response_hours': response_hours,
            'resolution_hours': resolution_hours
        }

    def _generate_reasoning(self, priority: int, sla: Dict[str, Any], text: str, impact_scope: str, urgency: str) -> str:
        """Generate human-readable reasoning for priority assignment"""
        reasons = []
        
        # Priority reasoning
        priority_name = self._get_priority_name(priority)
        reasons.append(f"Assigned Priority {priority} ({priority_name})")
        
        # Keyword analysis
        found_keywords = []
        for category, data in self.priority_keywords.items():
            for keyword in data['keywords']:
                if keyword in text:
                    found_keywords.append(f"'{keyword}' ({category})")
        
        if found_keywords:
            reasons.append(f"Keywords detected: {', '.join(found_keywords[:3])}")
        
        # Impact scope reasoning
        if impact_scope:
            reasons.append(f"Impact scope: {impact_scope}")
        
        # Urgency reasoning
        if urgency:
            reasons.append(f"Urgency: {urgency}")
        
        # SLA reasoning
        reasons.append(f"SLA: {sla['response_time']} response, {sla['resolution_time']} resolution")
        
        return " | ".join(reasons)

    def _get_priority_name(self, priority: int) -> str:
        """Get priority name from number"""
        priority_names = {
            1: "Critical",
            2: "High", 
            3: "Medium",
            4: "Low",
            5: "Planning"
        }
        return priority_names.get(priority, "Unknown")

    def _get_default_priority_sla(self, intent: str) -> Dict[str, Any]:
        """Get default priority and SLA when assignment fails"""
        default_priority = 3 if intent.lower() in ['incident', 'problem'] else 4
        
        return {
            'priority': default_priority,
            'priority_name': self._get_priority_name(default_priority),
            'sla': self._calculate_sla(default_priority, intent),
            'reasoning': f"Default assignment due to processing error",
            'auto_assigned': False
        }

    def validate_priority_assignment(self, priority: int, ticket_data: Dict[str, Any]) -> bool:
        """Validate if assigned priority makes sense"""
        try:
            # Re-assign priority
            new_assignment = self.assign_priority_and_sla(ticket_data, 'incident')
            
            # Check if priority is within reasonable range
            priority_diff = abs(priority - new_assignment['priority'])
            
            if priority_diff <= 1:
                return True
            else:
                logger.warning(f"Priority validation failed: assigned {priority}, calculated {new_assignment['priority']}")
                return False
                
        except Exception as e:
            logger.error(f"Error validating priority assignment: {str(e)}")
            return True  # Assume valid if validation fails

    def get_priority_guidelines(self) -> str:
        """Get priority assignment guidelines for users"""
        return """
        **Priority Assignment Guidelines:**
        
        **Priority 1 (Critical)**: Complete service outage, security breach, data loss
        **Priority 2 (High)**: Significant service degradation, VIP user impacted
        **Priority 3 (Medium)**: Moderate impact with workaround available
        **Priority 4 (Low)**: Minor impact, single user affected
        **Priority 5 (Planning)**: No immediate impact, future enhancement
        
        **SLA Response Times:**
        - P1: 1 hour (24/7)
        - P2: 4 hours (business hours)
        - P3: 8 hours (business hours)
        - P4: 24 hours (business hours)
        - P5: 48 hours (business hours)
        """
