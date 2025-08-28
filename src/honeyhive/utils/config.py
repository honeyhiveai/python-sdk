"""Configuration utilities for HoneyHive SDK."""

import os
import json
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration for HoneyHive SDK."""
    
    # API Configuration
    api_key: Optional[str] = None
    api_url: str = "https://api.honeyhive.ai"
    project: Optional[str] = None
    source: str = "production"
    
    # Tracing Configuration
    disable_tracing: bool = False
    disable_http_tracing: bool = False
    test_mode: bool = False
    debug_mode: bool = False
    
    # OTLP Configuration
    otlp_enabled: bool = True
    otlp_endpoint: Optional[str] = None
    otlp_headers: Optional[dict] = None
    
    # SDK Configuration
    version: str = "0.1.0"
    timeout: float = 30.0
    max_retries: int = 3
    
    def __post_init__(self):
        """Load configuration from environment variables."""
        self.api_key = self.api_key or os.getenv("HH_API_KEY")
        self.api_url = os.getenv("HH_API_URL", self.api_url)
        self.project = self.project or os.getenv("HH_PROJECT")
        self.source = os.getenv("HH_SOURCE", self.source)
        
        # Tracing configuration
        self.disable_tracing = os.getenv("HH_DISABLE_TRACING", "false").lower() == "true"
        self.disable_http_tracing = os.getenv("HH_DISABLE_HTTP_TRACING", "false").lower() == "true"
        self.test_mode = os.getenv("HH_TEST_MODE", "false").lower() == "true"
        self.debug_mode = os.getenv("HH_DEBUG_MODE", "false").lower() == "true"
        
        # OTLP configuration
        self.otlp_enabled = os.getenv("HH_OTLP_ENABLED", "true").lower() == "true"
        self.otlp_endpoint = os.getenv("HH_OTLP_ENDPOINT")
        
        # Parse OTLP headers if provided
        otlp_headers_str = os.getenv("HH_OTLP_HEADERS")
        if otlp_headers_str:
            try:
                self.otlp_headers = json.loads(otlp_headers_str)
            except (json.JSONDecodeError, ImportError):
                self.otlp_headers = None
    
    def reload(self):
        """Reload configuration from environment variables."""
        # Update instance attributes from environment variables
        self.api_key = os.getenv("HH_API_KEY") or self.api_key
        self.api_url = os.getenv("HH_API_URL", self.api_url)
        self.project = os.getenv("HH_PROJECT") or self.project
        self.source = os.getenv("HH_SOURCE", self.source)
        
        # Tracing configuration
        self.disable_tracing = os.getenv("HH_DISABLE_TRACING", "false").lower() == "true"
        self.disable_http_tracing = os.getenv("HH_DISABLE_HTTP_TRACING", "false").lower() == "true"
        self.test_mode = os.getenv("HH_TEST_MODE", "false").lower() == "true"
        self.debug_mode = os.getenv("HH_DEBUG_MODE", "false").lower() == "true"
        
        # OTLP configuration
        self.otlp_enabled = os.getenv("HH_OTLP_ENABLED", "true").lower() == "true"
        self.otlp_endpoint = os.getenv("HH_OTLP_ENDPOINT")
        
        # Parse OTLP headers if provided
        otlp_headers_str = os.getenv("HH_OTLP_HEADERS")
        if otlp_headers_str:
            try:
                self.otlp_headers = json.loads(otlp_headers_str)
            except (json.JSONDecodeError, ImportError):
                self.otlp_headers = None


# Global configuration instance
config = Config()

def reload_config():
    """Reload configuration from environment variables."""
    global config
    config = Config()

def get_config() -> Config:
    """Get the global configuration instance."""
    return config
