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
    verbose: bool = False  # Enable verbose logging for API debugging
    
    # OTLP Configuration
    otlp_enabled: bool = True
    otlp_endpoint: Optional[str] = None
    otlp_headers: Optional[dict] = None
    
    # SDK Configuration
    version: str = "0.1.0"
    timeout: float = 30.0
    max_retries: int = 3
    
    # HTTP Client Configuration
    max_connections: int = 10
    max_keepalive_connections: int = 20
    keepalive_expiry: float = 30.0
    pool_timeout: float = 10.0
    rate_limit_calls: int = 100
    rate_limit_window: float = 60.0
    
    # Additional HTTP Client Settings
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None
    no_proxy: Optional[str] = None
    verify_ssl: bool = True
    follow_redirects: bool = True
    
    # Experiment Harness Configuration
    experiment_id: Optional[str] = None
    experiment_name: Optional[str] = None
    experiment_variant: Optional[str] = None
    experiment_group: Optional[str] = None
    experiment_metadata: Optional[dict] = None
    
    def _load_http_client_config(self):
        """Load HTTP client configuration from environment variables."""
        # Support both HoneyHive-specific and standard HTTP client environment variables
        max_connections_str = os.getenv("HH_MAX_CONNECTIONS") or os.getenv("HTTP_MAX_CONNECTIONS")
        if max_connections_str:
            try:
                self.max_connections = int(max_connections_str)
            except (ValueError, TypeError):
                pass
        
        max_keepalive_str = os.getenv("HH_MAX_KEEPALIVE_CONNECTIONS") or os.getenv("HTTP_MAX_KEEPALIVE_CONNECTIONS")
        if max_keepalive_str:
            try:
                self.max_keepalive_connections = int(max_keepalive_str)
            except (ValueError, TypeError):
                pass
        
        keepalive_expiry_str = os.getenv("HH_KEEPALIVE_EXPIRY") or os.getenv("HTTP_KEEPALIVE_EXPIRY")
        if keepalive_expiry_str:
            try:
                self.keepalive_expiry = float(keepalive_expiry_str)
            except (ValueError, TypeError):
                pass
        
        pool_timeout_str = os.getenv("HH_POOL_TIMEOUT") or os.getenv("HTTP_POOL_TIMEOUT")
        if pool_timeout_str:
            try:
                self.pool_timeout = float(pool_timeout_str)
            except (ValueError, TypeError):
                pass
        
        rate_limit_calls_str = os.getenv("HH_RATE_LIMIT_CALLS") or os.getenv("HTTP_RATE_LIMIT_CALLS")
        if rate_limit_calls_str:
            try:
                self.rate_limit_calls = int(rate_limit_calls_str)
            except (ValueError, TypeError):
                pass
        
        rate_limit_window_str = os.getenv("HH_RATE_LIMIT_WINDOW") or os.getenv("HTTP_RATE_LIMIT_WINDOW")
        if rate_limit_window_str:
            try:
                self.rate_limit_window = float(rate_limit_window_str)
            except (ValueError, TypeError):
                pass
        
        # Additional HTTP Client Settings
        self.http_proxy = (
            os.getenv("HH_HTTP_PROXY") or 
            os.getenv("HTTP_PROXY") or 
            os.getenv("http_proxy")
        )
        
        self.https_proxy = (
            os.getenv("HH_HTTPS_PROXY") or 
            os.getenv("HTTPS_PROXY") or 
            os.getenv("https_proxy")
        )
        
        self.no_proxy = (
            os.getenv("HH_NO_PROXY") or 
            os.getenv("NO_PROXY") or 
            os.getenv("no_proxy")
        )
        
        verify_ssl_str = os.getenv("HH_VERIFY_SSL") or os.getenv("VERIFY_SSL")
        if verify_ssl_str:
            self.verify_ssl = verify_ssl_str.lower() not in ("false", "0", "no", "off")
        
        follow_redirects_str = os.getenv("HH_FOLLOW_REDIRECTS") or os.getenv("FOLLOW_REDIRECTS")
        if follow_redirects_str:
            self.follow_redirects = follow_redirects_str.lower() not in ("false", "0", "no", "off")
    
    def _load_experiment_config(self):
        """Load experiment harness configuration from environment variables."""
        # Support both HoneyHive-specific and standard experiment harness environment variables
        self.experiment_id = (
            os.getenv("HH_EXPERIMENT_ID") or 
            os.getenv("EXPERIMENT_ID") or 
            os.getenv("MLFLOW_EXPERIMENT_ID") or
            os.getenv("WANDB_RUN_ID") or
            os.getenv("COMET_EXPERIMENT_KEY")
        )
        
        self.experiment_name = (
            os.getenv("HH_EXPERIMENT_NAME") or 
            os.getenv("EXPERIMENT_NAME") or 
            os.getenv("MLFLOW_EXPERIMENT_NAME") or
            os.getenv("WANDB_PROJECT") or
            os.getenv("COMET_PROJECT_NAME")
        )
        
        self.experiment_variant = (
            os.getenv("HH_EXPERIMENT_VARIANT") or 
            os.getenv("EXPERIMENT_VARIANT") or 
            os.getenv("VARIANT") or
            os.getenv("AB_TEST_VARIANT") or
            os.getenv("TREATMENT")
        )
        
        self.experiment_group = (
            os.getenv("HH_EXPERIMENT_GROUP") or 
            os.getenv("EXPERIMENT_GROUP") or 
            os.getenv("GROUP") or
            os.getenv("AB_TEST_GROUP") or
            os.getenv("COHORT")
        )
        
        # Parse experiment metadata if provided
        experiment_metadata_str = (
            os.getenv("HH_EXPERIMENT_METADATA") or 
            os.getenv("EXPERIMENT_METADATA") or 
            os.getenv("MLFLOW_TAGS") or
            os.getenv("WANDB_TAGS") or
            os.getenv("COMET_TAGS")
        )
        
        if experiment_metadata_str:
            try:
                # Handle different formats: JSON, comma-separated, key=value
                if experiment_metadata_str.startswith('{') and experiment_metadata_str.endswith('}'):
                    # JSON format
                    self.experiment_metadata = json.loads(experiment_metadata_str)
                elif '=' in experiment_metadata_str:
                    # key=value format
                    metadata = {}
                    for item in experiment_metadata_str.split(','):
                        if '=' in item:
                            key, value = item.split('=', 1)
                            metadata[key.strip()] = value.strip()
                    self.experiment_metadata = metadata
                else:
                    # Comma-separated format
                    self.experiment_metadata = {
                        "tags": [tag.strip() for tag in experiment_metadata_str.split(',')]
                    }
            except (json.JSONDecodeError, Exception):
                # Fallback to simple string format
                self.experiment_metadata = {"raw": experiment_metadata_str}
    
    def __post_init__(self):
        """Load configuration from environment variables."""
        # Backwards compatibility: Maintain all existing HH_ environment variables
        self.api_key = self.api_key or os.getenv("HH_API_KEY")
        self.api_url = os.getenv("HH_API_URL", self.api_url)
        self.project = self.project or os.getenv("HH_PROJECT")
        self.source = os.getenv("HH_SOURCE", self.source)
        
        # Tracing configuration
        self.disable_tracing = os.getenv("HH_DISABLE_TRACING", "false").lower() == "true"
        self.disable_http_tracing = os.getenv("HH_DISABLE_HTTP_TRACING", "false").lower() == "true"
        self.test_mode = os.getenv("HH_TEST_MODE", "false").lower() == "true"
        self.debug_mode = os.getenv("HH_DEBUG_MODE", "false").lower() == "true"
        self.verbose = os.getenv("HH_VERBOSE", "false").lower() == "true"
        
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
        
        # Load HTTP client and experiment configurations
        self._load_http_client_config()
        self._load_experiment_config()
    
    def reload(self):
        """Reload configuration from environment variables."""
        # Update instance attributes from environment variables
        # Backwards compatibility: Maintain all existing HH_ environment variables
        self.api_key = os.getenv("HH_API_KEY") or self.api_key
        self.api_url = os.getenv("HH_API_URL", self.api_url)
        self.project = os.getenv("HH_PROJECT") or self.project
        self.source = os.getenv("HH_SOURCE", self.source)
        
        # Tracing configuration
        self.disable_tracing = os.getenv("HH_DISABLE_TRACING", "false").lower() == "true"
        self.disable_http_tracing = os.getenv("HH_DISABLE_HTTP_TRACING", "false").lower() == "true"
        self.test_mode = os.getenv("HH_TEST_MODE", "false").lower() == "true"
        self.debug_mode = os.getenv("HH_DEBUG_MODE", "false").lower() == "true"
        self.verbose = os.getenv("HH_VERBOSE", "false").lower() == "true"
        
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
        
        # Load HTTP client and experiment configurations
        self._load_http_client_config()
        self._load_experiment_config()


# Global configuration instance
config = Config()

def reload_config():
    """Reload configuration from environment variables."""
    global config
    config = Config()

def get_config() -> Config:
    """Get the global configuration instance."""
    return config
