"""API client configuration models for HoneyHive SDK.

This module provides Pydantic models for API client configuration
to reduce argument count in API client constructors while maintaining
backwards compatibility.

Future implementation for addressing pylint R0913/R0917 issues in:
- HoneyHive API client constructor
- Other API client classes

The hybrid approach allows both old and new usage patterns:

Old Usage (Backwards Compatible):
    client = HoneyHive(api_key="...", server_url="...", timeout=30.0)

New Usage (Future):
    config = APIClientConfig(api_key="...", server_url="...", timeout=30.0)
    client = HoneyHive(config=config)
"""

# pylint: disable=duplicate-code
# Note: Pydantic model configuration patterns are intentionally similar
# across config modules for consistency. These provide standardized
# validation and environment variable handling.

from pydantic import Field

from .base import BaseHoneyHiveConfig
from .http_client import HTTPClientConfig


class APIClientConfig(BaseHoneyHiveConfig):
    """Configuration for HoneyHive API client.

    This class defines configuration parameters for API client initialization
    to reduce argument count while maintaining backwards compatibility.
    It inherits common fields from BaseHoneyHiveConfig and composes
    HTTPClientConfig for transport-level settings.

    Inherited Fields:
        - api_key: HoneyHive API key for authentication
        - server_url: Server URL for requests (from HH_API_URL env var)
        - project: Deprecated; accepted for backwards compatibility but ignored
          (project is inferred from the API key by the backend)
        - test_mode: Enable test mode (no data sent to backend)
        - verbose: Enable verbose logging output

    API Client-Specific Fields:
        - http_config: HTTP transport configuration

    Example:
        >>> # Simple usage
        >>> config = APIClientConfig(
        ...     api_key="hh_1234567890abcdef",
        ...     server_url="https://api.dp1.us.honeyhive.ai"
        ... )

        >>> # Advanced usage with HTTP config
        >>> http_config = HTTPClientConfig(timeout=60.0, max_connections=50)
        >>> config = APIClientConfig(
        ...     api_key="hh_1234567890abcdef",
        ...     server_url="https://api.dp1.us.honeyhive.ai",
        ...     http_config=http_config
        ... )

        >>> # Future usage:
        >>> # client = HoneyHive(config=config)

        # Current backwards compatible usage:
        >>> client = HoneyHive(
        ...     bearer_auth="hh_1234567890abcdef",
        ...     server_url="https://api.dp1.us.honeyhive.ai",
        ...     timeout_ms=30000
        ... )
    """

    # Compose HTTP client configuration. The alias equal to the field name keeps
    # env_prefix from applying, so the variable stays the bare HTTP_CONFIG it has
    # always been rather than becoming HH_HTTP_CONFIG.
    http_config: HTTPClientConfig = Field(
        default_factory=HTTPClientConfig,
        validation_alias="http_config",
        description="HTTP transport configuration",
    )
