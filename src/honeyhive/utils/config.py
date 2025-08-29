"""Configuration management for HoneyHive SDK."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class APIConfig:
    """API configuration settings."""

    api_key: Optional[str] = None
    api_url: str = "https://api.honeyhive.ai"
    project: Optional[str] = None
    source: str = "production"


@dataclass
class TracingConfig:
    """Tracing configuration settings."""

    disable_tracing: bool = False
    disable_http_tracing: bool = False
    test_mode: bool = False
    debug_mode: bool = False
    verbose: bool = False  # Enable verbose logging for API debugging


@dataclass
class OTLPConfig:
    """OTLP configuration settings."""

    otlp_enabled: bool = True
    otlp_endpoint: Optional[str] = None
    otlp_headers: Optional[dict] = None


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


@dataclass
class ExperimentConfig:
    """Experiment harness configuration settings."""

    experiment_id: Optional[str] = None
    experiment_name: Optional[str] = None
    experiment_variant: Optional[str] = None
    experiment_group: Optional[str] = None
    experiment_metadata: Optional[dict] = None


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
        """Initialize sub-configurations with defaults."""
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
        """Get project from sub-configuration."""
        return self.api.project if self.api else None

    @project.setter
    def project(self, value: Optional[str]) -> None:
        """Set project in sub-configuration."""
        if self.api:
            self.api.project = value

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
