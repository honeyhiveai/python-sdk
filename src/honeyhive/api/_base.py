"""Base classes for HoneyHive API client.

This module provides base functionality that can be extended for features like:
- Automatic retries with exponential backoff
- Request/response logging
- Rate limiting
- Custom error handling
"""

import os
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

    @staticmethod
    def _resolve_project(project: Optional[str] = None) -> str:
        """Resolve project name from parameter or HH_PROJECT environment variable.

        Args:
            project: Explicit project name. If None or empty, falls back to
                     the HH_PROJECT environment variable.

        Returns:
            The resolved project name.

        Raises:
            ValueError: If no project name is available from either source.
        """
        if project:
            return project
        env_project = os.getenv("HH_PROJECT")
        if env_project:
            return env_project
        raise ValueError(
            "A project name is required. "
            "Pass it as a parameter or set the HH_PROJECT environment variable."
        )
