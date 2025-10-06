"""
Configuration Management - Environment Settings and API Keys

This module provides centralized configuration management for the ServiceNow
Enterprise Chatbot application. It handles environment variable loading,
validates required settings, and provides structured access to all system
configuration parameters.

Configuration Categories:
    - OCI (Oracle Cloud Infrastructure) settings for Generative AI
    - Google ADK (Application Development Kit) for Gemini integration  
    - ServiceNow REST API credentials and instance settings
    - Azure OpenAI backup service configuration
    - Application server and CORS settings
    - Logging and monitoring configuration

Security Features:
    - Environment variable based configuration
    - Sensitive data isolation from code
    - Default value fallbacks for development
    - Configuration validation methods
    - Support for multiple deployment environments

Usage:
    Import this module to access configuration values:
    ```python
    from config.config import Config
    instance_url = Config.SERVICENOW_INSTANCE_URL
    ```
"""

# Standard library imports
import os

# Third-party imports
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Centralized configuration class for all application settings.
    
    This class provides structured access to environment variables and
    configuration parameters needed throughout the application. It follows
    the twelve-factor app methodology for configuration management.
    
    Configuration Sections:
        - OCI: Oracle Cloud Infrastructure settings
        - Google: Google ADK and Gemini model configuration
        - ServiceNow: ServiceNow instance and API settings
        - Azure: Azure OpenAI backup service settings
        - Application: Server and CORS configuration
        
    Environment Variables:
        All sensitive configuration is loaded from environment variables
        with sensible defaults for development environments.
        
    Methods:
        validate_config(): Validates required configuration is present
        get_servicenow_url(): Returns cleaned ServiceNow instance URL
        is_production(): Determines if running in production environment
    """
    
    # ========================= OCI CONFIGURATION =========================
    # Oracle Cloud Infrastructure settings for Generative AI integration
    
    AUTH_TYPE = os.getenv("OCI_AUTH_TYPE", "api_key")
    PROFILE = os.getenv("OCI_PROFILE", "DEFAULT")
    REGION = os.getenv("OCI_REGION", "us-chicago-1")
    
    # OCI Authentication credentials
    OCI_TENANCY_ID = os.getenv("OCI_TENANCY_ID", "")
    OCI_USER_ID = os.getenv("OCI_USER_ID", "")
    OCI_FINGERPRINT = os.getenv("OCI_FINGERPRINT", "")
    OCI_PRIVATE_KEY_PATH = os.getenv("OCI_PRIVATE_KEY_PATH", "")
    OCI_COMPARTMENT_ID = os.getenv("OCI_COMPARTMENT_ID", "")
    OCI_MODEL_ID = os.getenv("OCI_MODEL_ID", "cohere.command")
    
    # OCI Generative AI Agent Endpoints
    SEARCH_AGENT_ENDPOINT_ID = os.getenv("SEARCH_AGENT_ENDPOINT_ID", "")
    
    # ========================= GOOGLE CONFIGURATION =========================
    # Google ADK and Gemini model settings for ticket creation
    
    GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "ash1979")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS", 
        "/Users/ashishsingh/Downloads/credentials.json"
    )
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_ADK_REGION = os.getenv("GOOGLE_ADK_REGION", "us-central1")
    GOOGLE_ADK_MODEL = os.getenv("GOOGLE_ADK_MODEL", "gemini-2.5-flash")
    TICKET_CREATION_AGENT_ID = os.getenv("TICKET_CREATION_AGENT_ID", "")
    
    # ========================= AZURE CONFIGURATION =========================
    # Azure OpenAI backup service configuration
    
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", 
                                        "2024-02-15-preview")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", 
                                           "gpt-4")
    
    # ========================= SERVICENOW CONFIGURATION =========================
    # ServiceNow instance and API settings
    
    SERVICENOW_INSTANCE_URL = os.getenv(
        "SERVICENOW_INSTANCE_URL",
        "https://dev218893.service-now.com"
    )
    SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD", "")
    SERVICENOW_DEFAULT_CALLER_ID = os.getenv("SERVICENOW_DEFAULT_CALLER_ID",
                                             "admin")
    SERVICENOW_API_VERSION = os.getenv("SERVICENOW_API_VERSION", "v2")
    SERVICENOW_TIMEOUT = os.getenv("SERVICENOW_TIMEOUT", "30")
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # CORS Configuration
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ]
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        required_fields = [
            "SEARCH_AGENT_ENDPOINT_ID"
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required configuration: {', '.join(missing_fields)}")
        
        return True
