"""Configuration management for HoneyHive SDK."""

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean value from environment variable.

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Boolean value from environment or default
    """
    value = os.getenv(key, "").lower()
    if value in ("true", "1", "yes", "on"):
        return True
    elif value in ("false", "0", "no", "off"):
        return False
    return default


def _get_env_int(key: str, default: int = 0) -> int:
    """Get integer value from environment variable.

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Integer value from environment or default
    """
    try:
        return int(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default


def _get_env_float(key: str, default: float = 0.0) -> float:
    """Get float value from environment variable.

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Float value from environment or default
    """
    try:
        return float(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default


def _get_env_json(key: str, default: Optional[dict] = None) -> Optional[dict]:
    """Get JSON value from environment variable.

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Dict value from environment or default
    """
    value = os.getenv(key)
    if not value:
        return default
    try:
        result = json.loads(value)
        # Ensure we return a dict or None
        if isinstance(result, dict):
            return result
        return default
    except (json.JSONDecodeError, TypeError):
        return default


@dataclass
class APIConfig:
    """API configuration settings."""

    api_key: Optional[str] = None
    api_url: str = "https://api.honeyhive.ai"
    # project removed - backend derives from API key
    source: str = "production"

    def __post_init__(self) -> None:
        """Load configuration from environment variables."""
        # Load from HH_ prefixed variables first, then standard alternatives
        if self.api_key is None:
            self.api_key = os.getenv("HH_API_KEY")

        # API URL with fallback to standard
        env_api_url = os.getenv("HH_API_URL") or os.getenv("API_URL")
        if env_api_url:
            self.api_url = env_api_url

        # Source environment
        env_source = (
            os.getenv("HH_SOURCE") or os.getenv("SOURCE") or os.getenv("ENVIRONMENT")
        )
        if env_source:
            self.source = env_source


@dataclass
class TracingConfig:
    """Tracing configuration settings."""

    disable_tracing: bool = False
    disable_http_tracing: bool = False
    test_mode: bool = False
    debug_mode: bool = False
    verbose: bool = False  # Enable verbose logging for API debugging

    def __post_init__(self) -> None:
        """Load configuration from environment variables."""
        # Tracing configuration
        self.disable_tracing = _get_env_bool("HH_DISABLE_TRACING", self.disable_tracing)
        self.disable_http_tracing = _get_env_bool(
            "HH_DISABLE_HTTP_TRACING", self.disable_http_tracing
        )
        self.test_mode = _get_env_bool("HH_TEST_MODE", self.test_mode)
        self.debug_mode = _get_env_bool("HH_DEBUG_MODE", self.debug_mode)
        self.verbose = _get_env_bool("HH_VERBOSE", self.verbose)


@dataclass
class OTLPConfig:
    """OTLP configuration settings."""

    otlp_enabled: bool = True
    otlp_endpoint: Optional[str] = None
    otlp_headers: Optional[dict] = None

    def __post_init__(self) -> None:
        """Load configuration from environment variables."""
        # OTLP configuration
        self.otlp_enabled = _get_env_bool("HH_OTLP_ENABLED", self.otlp_enabled)

        # OTLP endpoint
        env_endpoint = os.getenv("HH_OTLP_ENDPOINT") or os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT"
        )
        if env_endpoint:
            self.otlp_endpoint = env_endpoint

        # OTLP headers
        env_headers = _get_env_json("HH_OTLP_HEADERS") or _get_env_json(
            "OTEL_EXPORTER_OTLP_HEADERS"
        )
        if env_headers:
            self.otlp_headers = env_headers


@dataclass
class HTTPClientConfig:
    """HTTP client configuration settings."""

    max_connections: int = 10
    max_keepalive_connections: int = 20
    keepalive_expiry: float = 30.0
    pool_timeout: float = 10.0
    rate_limit_calls: int = 100
    rate_limit_window: float = 60.0
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None
    no_proxy: Optional[str] = None
    verify_ssl: bool = True
    follow_redirects: bool = True

    def __post_init__(self) -> None:
        """Load configuration from environment variables."""
        # Connection pool settings
        self.max_connections = _get_env_int(
            "HH_MAX_CONNECTIONS", self.max_connections
        ) or _get_env_int("HTTP_MAX_CONNECTIONS", self.max_connections)
        self.max_keepalive_connections = _get_env_int(
            "HH_MAX_KEEPALIVE_CONNECTIONS", self.max_keepalive_connections
        ) or _get_env_int(
            "HTTP_MAX_KEEPALIVE_CONNECTIONS", self.max_keepalive_connections
        )
        self.keepalive_expiry = _get_env_float(
            "HH_KEEPALIVE_EXPIRY", self.keepalive_expiry
        ) or _get_env_float("HTTP_KEEPALIVE_EXPIRY", self.keepalive_expiry)
        self.pool_timeout = _get_env_float(
            "HH_POOL_TIMEOUT", self.pool_timeout
        ) or _get_env_float("HTTP_POOL_TIMEOUT", self.pool_timeout)

        # Rate limiting
        self.rate_limit_calls = _get_env_int(
            "HH_RATE_LIMIT_CALLS", self.rate_limit_calls
        ) or _get_env_int("HTTP_RATE_LIMIT_CALLS", self.rate_limit_calls)
        self.rate_limit_window = _get_env_float(
            "HH_RATE_LIMIT_WINDOW", self.rate_limit_window
        ) or _get_env_float("HTTP_RATE_LIMIT_WINDOW", self.rate_limit_window)

        # Proxy settings
        self.http_proxy = (
            os.getenv("HH_HTTP_PROXY")
            or os.getenv("HTTP_PROXY")
            or os.getenv("http_proxy")
        )
        self.https_proxy = (
            os.getenv("HH_HTTPS_PROXY")
            or os.getenv("HTTPS_PROXY")
            or os.getenv("https_proxy")
        )
        self.no_proxy = (
            os.getenv("HH_NO_PROXY") or os.getenv("NO_PROXY") or os.getenv("no_proxy")
        )

        # SSL and redirects
        self.verify_ssl = _get_env_bool(
            "HH_VERIFY_SSL", self.verify_ssl
        ) or _get_env_bool("VERIFY_SSL", self.verify_ssl)
        self.follow_redirects = _get_env_bool(
            "HH_FOLLOW_REDIRECTS", self.follow_redirects
        ) or _get_env_bool("FOLLOW_REDIRECTS", self.follow_redirects)


@dataclass
class ExperimentConfig:
    """Experiment harness configuration settings."""

    experiment_id: Optional[str] = None
    experiment_name: Optional[str] = None
    experiment_variant: Optional[str] = None
    experiment_group: Optional[str] = None
    experiment_metadata: Optional[dict] = None

    def __post_init__(self) -> None:
        """Load configuration from environment variables."""
        # Experiment identification with multiple standard alternatives
        self.experiment_id = (
            os.getenv("HH_EXPERIMENT_ID")
            or os.getenv("EXPERIMENT_ID")
            or os.getenv("MLFLOW_EXPERIMENT_ID")
            or os.getenv("WANDB_RUN_ID")
            or os.getenv("COMET_EXPERIMENT_KEY")
        )

        self.experiment_name = (
            os.getenv("HH_EXPERIMENT_NAME")
            or os.getenv("EXPERIMENT_NAME")
            or os.getenv("MLFLOW_EXPERIMENT_NAME")
            or os.getenv("WANDB_PROJECT")
            or os.getenv("COMET_PROJECT_NAME")
        )

        # Experiment variants and groups
        self.experiment_variant = (
            os.getenv("HH_EXPERIMENT_VARIANT")
            or os.getenv("EXPERIMENT_VARIANT")
            or os.getenv("VARIANT")
            or os.getenv("AB_TEST_VARIANT")
            or os.getenv("TREATMENT")
        )

        self.experiment_group = (
            os.getenv("HH_EXPERIMENT_GROUP")
            or os.getenv("EXPERIMENT_GROUP")
            or os.getenv("GROUP")
            or os.getenv("AB_TEST_GROUP")
            or os.getenv("COHORT")
        )

        # Experiment metadata with multiple formats
        self.experiment_metadata = (
            _get_env_json("HH_EXPERIMENT_METADATA")
            or _get_env_json("EXPERIMENT_METADATA")
            or _get_env_json("MLFLOW_TAGS")
            or _get_env_json("WANDB_TAGS")
            or _get_env_json("COMET_TAGS")
        )


@dataclass
class Config:
    """Configuration for HoneyHive SDK.

    Centralized configuration management for all SDK components
    including API settings, tracing configuration, HTTP client settings,
    and experiment harness configuration.
    """

    # Core configuration
    version: str = "0.1.0"
    timeout: float = 30.0
    max_retries: int = 3

    # Sub-configurations
    api: Optional[APIConfig] = None
    tracing: Optional[TracingConfig] = None
    otlp: Optional[OTLPConfig] = None
    http_client: Optional[HTTPClientConfig] = None
    experiment: Optional[ExperimentConfig] = None

    def __post_init__(self) -> None:
        """Initialize sub-configurations with defaults and load from environment."""
        # Load SDK-level configuration from environment
        self.timeout = _get_env_float("HH_TIMEOUT", self.timeout)
        self.max_retries = _get_env_int("HH_MAX_RETRIES", self.max_retries)

        # Initialize sub-configurations (they will load their own env vars)
        if self.api is None:
            self.api = APIConfig()
        if self.tracing is None:
            self.tracing = TracingConfig()
        if self.otlp is None:
            self.otlp = OTLPConfig()
        if self.http_client is None:
            self.http_client = HTTPClientConfig()
        if self.experiment is None:
            self.experiment = ExperimentConfig()

    @property
    def api_key(self) -> Optional[str]:
        """Get API key from sub-configuration."""
        return self.api.api_key if self.api else None

    @api_key.setter
    def api_key(self, value: Optional[str]) -> None:
        """Set API key in sub-configuration."""
        if self.api:
            self.api.api_key = value

    @property
    def api_url(self) -> str:
        """Get API URL from sub-configuration."""
        return self.api.api_url if self.api else "https://api.honeyhive.ai"

    @api_url.setter
    def api_url(self, value: str) -> None:
        """Set API URL in sub-configuration."""
        if self.api:
            self.api.api_url = value

    @property
    def project(self) -> Optional[str]:
        """Get project from sub-configuration - deprecated, returns None."""
        # Project removed - backend derives from API key scope
        return None

    @project.setter
    def project(self, value: Optional[str]) -> None:
        """Set project in sub-configuration - deprecated, no-op."""
        # Project removed - backend derives from API key scope
        pass

    @property
    def source(self) -> str:
        """Get source from sub-configuration."""
        return self.api.source if self.api else "production"

    @source.setter
    def source(self, value: str) -> None:
        """Set source in sub-configuration."""
        if self.api:
            self.api.source = value

    @property
    def disable_tracing(self) -> bool:
        """Get disable_tracing from sub-configuration."""
        return self.tracing.disable_tracing if self.tracing else False

    @property
    def disable_http_tracing(self) -> bool:
        """Get disable_http_tracing from sub-configuration."""
        return self.tracing.disable_http_tracing if self.tracing else False

    @property
    def test_mode(self) -> bool:
        """Get test_mode from sub-configuration."""
        return self.tracing.test_mode if self.tracing else False

    @test_mode.setter
    def test_mode(self, value: bool) -> None:
        """Set test_mode in sub-configuration."""
        if self.tracing:
            self.tracing.test_mode = value

    @property
    def debug_mode(self) -> bool:
        """Get debug_mode from sub-configuration."""
        return self.tracing.debug_mode if self.tracing else False

    @debug_mode.setter
    def debug_mode(self, value: bool) -> None:
        """Set debug_mode in sub-configuration."""
        if self.tracing:
            self.tracing.debug_mode = value

    @debug_mode.deleter
    def debug_mode(self) -> None:
        """Delete debug_mode from sub-configuration."""
        if self.tracing:
            delattr(self.tracing, "debug_mode")

    @property
    def verbose(self) -> bool:
        """Get verbose from sub-configuration."""
        return self.tracing.verbose if self.tracing else False

    @verbose.setter
    def verbose(self, value: bool) -> None:
        """Set verbose in sub-configuration."""
        if self.tracing:
            self.tracing.verbose = value

    @verbose.deleter
    def verbose(self) -> None:
        """Delete verbose from sub-configuration."""
        if self.tracing:
            delattr(self.tracing, "verbose")

    @property
    def otlp_enabled(self) -> bool:
        """Get otlp_enabled from sub-configuration."""
        return self.otlp.otlp_enabled if self.otlp else True

    @property
    def otlp_endpoint(self) -> Optional[str]:
        """Get otlp_endpoint from sub-configuration."""
        return self.otlp.otlp_endpoint if self.otlp else None

    @property
    def otlp_headers(self) -> Optional[dict]:
        """Get otlp_headers from sub-configuration."""
        return self.otlp.otlp_headers if self.otlp else None

    @property
    def max_connections(self) -> int:
        """Get max_connections from sub-configuration."""
        return self.http_client.max_connections if self.http_client else 10

    @property
    def max_keepalive_connections(self) -> int:
        """Get max_keepalive_connections from sub-configuration."""
        return self.http_client.max_keepalive_connections if self.http_client else 20

    @property
    def keepalive_expiry(self) -> float:
        """Get keepalive_expiry from sub-configuration."""
        return self.http_client.keepalive_expiry if self.http_client else 30.0

    @property
    def pool_timeout(self) -> float:
        """Get pool_timeout from sub-configuration."""
        return self.http_client.pool_timeout if self.http_client else 10.0

    @property
    def rate_limit_calls(self) -> int:
        """Get rate_limit_calls from sub-configuration."""
        return self.http_client.rate_limit_calls if self.http_client else 100

    @property
    def rate_limit_window(self) -> float:
        """Get rate_limit_window from sub-configuration."""
        return self.http_client.rate_limit_window if self.http_client else 60.0

    @property
    def http_proxy(self) -> Optional[str]:
        """Get http_proxy from sub-configuration."""
        return self.http_client.http_proxy if self.http_client else None

    @property
    def https_proxy(self) -> Optional[str]:
        """Get https_proxy from sub-configuration."""
        return self.http_client.https_proxy if self.http_client else None

    @property
    def no_proxy(self) -> Optional[str]:
        """Get no_proxy from sub-configuration."""
        return self.http_client.no_proxy if self.http_client else None

    @property
    def verify_ssl(self) -> bool:
        """Get verify_ssl from sub-configuration."""
        return self.http_client.verify_ssl if self.http_client else True

    @property
    def follow_redirects(self) -> bool:
        """Get follow_redirects from sub-configuration."""
        return self.http_client.follow_redirects if self.http_client else True

    @property
    def experiment_id(self) -> Optional[str]:
        """Get experiment_id from sub-configuration."""
        return self.experiment.experiment_id if self.experiment else None

    @property
    def experiment_name(self) -> Optional[str]:
        """Get experiment_name from sub-configuration."""
        return self.experiment.experiment_name if self.experiment else None

    @property
    def experiment_variant(self) -> Optional[str]:
        """Get experiment_variant from sub-configuration."""
        return self.experiment.experiment_variant if self.experiment else None

    @property
    def experiment_group(self) -> Optional[str]:
        """Get experiment_group from sub-configuration."""
        return self.experiment.experiment_group if self.experiment else None

    @property
    def experiment_metadata(self) -> Optional[dict]:
        """Get experiment_metadata from sub-configuration."""
        return self.experiment.experiment_metadata if self.experiment else None


# Global configuration instance
config = Config()


def reload_config() -> None:
    """Reload configuration from environment variables.

    Creates a new global configuration instance with updated
    values from environment variables.
    """
    global config
    config = Config()


def get_config() -> Config:
    """Get the global configuration instance.

    Returns:
        The global configuration instance
    """
    return config
