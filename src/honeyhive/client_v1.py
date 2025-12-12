"""HoneyHive API Client - Ergonomic wrapper over generated client.

This module provides a user-friendly interface to the HoneyHive API,
wrapping the auto-generated Pydantic-based client code with a cleaner API.

Usage:
    from honeyhive import HoneyHiveClient
    from honeyhive.models_v1 import CreateConfigurationRequest

    client = HoneyHiveClient(api_key="hh_...")

    # List configurations
    configs = client.configurations.list(project="my-project")

    # Create a configuration
    request = CreateConfigurationRequest(name="my-config", provider="openai")
    response = client.configurations.create(request)
"""

from typing import List, Optional

# Import from generated client
from honeyhive._generated.api_config import APIConfig
from honeyhive._generated.models import (
    Configuration,
    CreateConfigurationRequest,
    CreateConfigurationResponse,
)
from honeyhive._generated.services.async_Configurations_service import (
    createConfiguration as createConfigurationAsync,
)
from honeyhive._generated.services.async_Configurations_service import (
    getConfigurations as getConfigurationsAsync,
)
from honeyhive._generated.services.Configurations_service import (
    createConfiguration,
    getConfigurations,
)


class ConfigurationsAPI:
    """Configurations API with ergonomic interface."""

    def __init__(self, api_config: APIConfig):
        self._api_config = api_config

    def list(self, project: Optional[str] = None) -> List[Configuration]:
        """List configurations.

        Args:
            project: Optional project name to filter by

        Returns:
            List of Configuration objects
        """
        return getConfigurations(self._api_config, project=project)

    async def list_async(self, project: Optional[str] = None) -> List[Configuration]:
        """List configurations asynchronously.

        Args:
            project: Optional project name to filter by

        Returns:
            List of Configuration objects
        """
        return await getConfigurationsAsync(self._api_config, project=project)

    def create(
        self, request: CreateConfigurationRequest
    ) -> CreateConfigurationResponse:
        """Create a new configuration.

        Args:
            request: Configuration creation request

        Returns:
            CreateConfigurationResponse with acknowledged status and insertedId
        """
        return createConfiguration(self._api_config, data=request)

    async def create_async(
        self, request: CreateConfigurationRequest
    ) -> CreateConfigurationResponse:
        """Create a new configuration asynchronously.

        Args:
            request: Configuration creation request

        Returns:
            CreateConfigurationResponse with acknowledged status and insertedId
        """
        return await createConfigurationAsync(self._api_config, data=request)


class HoneyHiveClient:
    """Main HoneyHive API client with ergonomic interface.

    This client wraps the auto-generated Pydantic-based API client with a cleaner,
    more Pythonic interface.

    Usage:
        client = HoneyHiveClient(api_key="hh_...")

        # List configurations
        configs = client.configurations.list()

        # Create a configuration
        from honeyhive.models_v1 import CreateConfigurationRequest
        request = CreateConfigurationRequest(name="test", provider="openai")
        response = client.configurations.create(request)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.honeyhive.ai",
    ):
        """Initialize the HoneyHive client.

        Args:
            api_key: HoneyHive API key (typically starts with 'hh_')
            base_url: API base URL (default: https://api.honeyhive.ai)
        """
        # Create API config with authentication
        self._api_config = APIConfig(
            base_path=base_url,
            access_token=api_key,
        )

        # Initialize API namespaces
        self.configurations = ConfigurationsAPI(self._api_config)

    @property
    def api_config(self) -> APIConfig:
        """Access the underlying API configuration."""
        return self._api_config
