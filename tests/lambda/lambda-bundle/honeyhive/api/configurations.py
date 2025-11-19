"""Configurations API module for HoneyHive."""

from typing import List, Optional

from ..models import (
    Configuration,
    PostConfigurationRequest,
    PutConfigurationRequest,
)
from .base import BaseAPI


class ConfigurationsAPI(BaseAPI):
    """API for configuration operations."""

    def create_configuration(self, request: PostConfigurationRequest) -> Configuration:
        """Create a new configuration using PostConfigurationRequest model."""
        response = self.client.request(
            "POST",
            "/configurations",
            json={"configuration": request.model_dump(exclude_none=True)},
        )

        data = response.json()
        return Configuration(**data)

    def create_configuration_from_dict(self, config_data: dict) -> Configuration:
        """Create a new configuration from dictionary (legacy method)."""
        response = self.client.request(
            "POST", "/configurations", json={"configuration": config_data}
        )

        data = response.json()
        return Configuration(**data)

    async def create_configuration_async(
        self, request: PostConfigurationRequest
    ) -> Configuration:
        """Create a new configuration asynchronously using PostConfigurationRequest model."""
        response = await self.client.request_async(
            "POST",
            "/configurations",
            json={"configuration": request.model_dump(exclude_none=True)},
        )

        data = response.json()
        return Configuration(**data)

    async def create_configuration_from_dict_async(
        self, config_data: dict
    ) -> Configuration:
        """Create a new configuration asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async(
            "POST", "/configurations", json={"configuration": config_data}
        )

        data = response.json()
        return Configuration(**data)

    def get_configuration(self, config_id: str) -> Configuration:
        """Get a configuration by ID."""
        response = self.client.request("GET", f"/configurations/{config_id}")
        data = response.json()
        return Configuration(**data)

    async def get_configuration_async(self, config_id: str) -> Configuration:
        """Get a configuration by ID asynchronously."""
        response = await self.client.request_async(
            "GET", f"/configurations/{config_id}"
        )
        data = response.json()
        return Configuration(**data)

    def list_configurations(
        self, project: Optional[str] = None, limit: int = 100
    ) -> List[Configuration]:
        """List configurations with optional filtering."""
        params: dict = {"limit": limit}
        if project:
            params["project"] = project

        response = self.client.request("GET", "/configurations", params=params)
        data = response.json()
        return [
            Configuration(**config_data)
            for config_data in data.get("configurations", [])
        ]

    async def list_configurations_async(
        self, project: Optional[str] = None, limit: int = 100
    ) -> List[Configuration]:
        """List configurations asynchronously with optional filtering."""
        params: dict = {"limit": limit}
        if project:
            params["project"] = project

        response = await self.client.request_async(
            "GET", "/configurations", params=params
        )
        data = response.json()
        return [
            Configuration(**config_data)
            for config_data in data.get("configurations", [])
        ]

    def update_configuration(
        self, config_id: str, request: PutConfigurationRequest
    ) -> Configuration:
        """Update a configuration using PutConfigurationRequest model."""
        response = self.client.request(
            "PUT",
            f"/configurations/{config_id}",
            json=request.model_dump(exclude_none=True),
        )

        data = response.json()
        return Configuration(**data)

    def update_configuration_from_dict(
        self, config_id: str, config_data: dict
    ) -> Configuration:
        """Update a configuration from dictionary (legacy method)."""
        response = self.client.request(
            "PUT", f"/configurations/{config_id}", json=config_data
        )

        data = response.json()
        return Configuration(**data)

    async def update_configuration_async(
        self, config_id: str, request: PutConfigurationRequest
    ) -> Configuration:
        """Update a configuration asynchronously using PutConfigurationRequest model."""
        response = await self.client.request_async(
            "PUT",
            f"/configurations/{config_id}",
            json=request.model_dump(exclude_none=True),
        )

        data = response.json()
        return Configuration(**data)

    async def update_configuration_from_dict_async(
        self, config_id: str, config_data: dict
    ) -> Configuration:
        """Update a configuration asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async(
            "PUT", f"/configurations/{config_id}", json=config_data
        )

        data = response.json()
        return Configuration(**data)

    def delete_configuration(self, config_id: str) -> bool:
        """Delete a configuration by ID."""
        try:
            response = self.client.request("DELETE", f"/configurations/{config_id}")
            return response.status_code == 200
        except Exception:
            return False

    async def delete_configuration_async(self, config_id: str) -> bool:
        """Delete a configuration by ID asynchronously."""
        try:
            response = await self.client.request_async(
                "DELETE", f"/configurations/{config_id}"
            )
            return response.status_code == 200
        except Exception:
            return False
