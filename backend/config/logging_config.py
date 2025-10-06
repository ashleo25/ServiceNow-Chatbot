"""
Comprehensive logging configuration for Ticket Creation Agents
"""
import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

class TicketCreationLogger:
    """Centralized logging configuration for ticket creation agents"""
    
    def __init__(self, log_level=logging.INFO):
        self.log_level = log_level
        self.setup_logging()
    
    def setup_logging(self):
        """Setup comprehensive logging configuration"""
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler for all logs
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "ticket_creation.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
        
        # Error handler for errors only
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "ticket_creation_errors.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # Agent-specific handlers
        self.setup_agent_loggers(log_dir, detailed_formatter)
        
        # Log startup
        logger = logging.getLogger(__name__)
        logger.info("=" * 80)
        logger.info("TICKET CREATION AGENTS LOGGING INITIALIZED")
        logger.info(f"Log Level: {logging.getLevelName(self.log_level)}")
        logger.info(f"Log Directory: {log_dir.absolute()}")
        logger.info("=" * 80)
    
    def setup_agent_loggers(self, log_dir, formatter):
        """Setup specific loggers for each agent"""
        
        agents = [
            "ticket_creation_agent",
            "duplicate_check_agent", 
            "ticket_create_agent",
            "ticket_response_agent",
            "servicenow_service"
        ]
        
        for agent in agents:
            # Create agent-specific logger
            agent_logger = logging.getLogger(agent)
            agent_logger.setLevel(logging.DEBUG)
            
            # Agent-specific file handler
            agent_handler = logging.handlers.RotatingFileHandler(
                log_dir / f"{agent}.log",
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3
            )
            agent_handler.setLevel(logging.DEBUG)
            agent_handler.setFormatter(formatter)
            agent_logger.addHandler(agent_handler)
            
            # Prevent propagation to root logger to avoid duplicates
            agent_logger.propagate = False

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name"""
    return logging.getLogger(name)

# Initialize logging
TicketCreationLogger()
