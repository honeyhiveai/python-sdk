"""Base classes for HoneyHive API client.

This module provides base functionality that can be extended for features like:
- Automatic retries with exponential backoff
- Request/response logging
- Rate limiting
- Custom error handling
"""

from typing import Optional

from honeyhive._generated.api_config import APIConfig


class BaseAPI:
    """Base class for API resource namespaces.

    Provides shared configuration and extensibility hooks for all API resources.
    Subclasses can override methods to add cross-cutting concerns like retries.
    """

    def __init__(self, api_config: APIConfig) -> None:
        self._api_config = api_config

    @property
    def api_config(self) -> APIConfig:
        """Access the API configuration."""
        return self._api_config
