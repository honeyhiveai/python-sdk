"""Configurations API module for HoneyHive."""

from dataclasses import dataclass
from typing import List, Optional

from ..models import (
    Configuration,
    PostConfigurationRequest,
    PutConfigurationRequest,
)
from .base import BaseAPI


@dataclass
class CreateConfigurationResponse:
    """Response from configuration creation API.

    Note: This is a custom response model because the configurations API returns
    a MongoDB-style operation result (acknowledged, insertedId, etc.) rather than
    the created Configuration object like other APIs. This should ideally be added
    to the generated models if this response format is standardized.
    """

    acknowledged: bool
    inserted_id: str
    success: bool = True


class ConfigurationsAPI(BaseAPI):
    """API for configuration operations."""

    def create_configuration(
        self, request: PostConfigurationRequest
    ) -> CreateConfigurationResponse:
        """Create a new configuration using PostConfigurationRequest model."""
        response = self.client.request(
            "POST",
            "/configurations",
            json=request.model_dump(mode="json", exclude_none=True),
        )

        data = response.json()
        return CreateConfigurationResponse(
            acknowledged=data.get("acknowledged", False),
            inserted_id=data.get("insertedId", ""),
            success=data.get("acknowledged", False),
        )

    def create_configuration_from_dict(
        self, config_data: dict
    ) -> CreateConfigurationResponse:
        """Create a new configuration from dictionary (legacy method).

        Note: This method now returns CreateConfigurationResponse to match the \
        actual API behavior.
        The API returns MongoDB-style operation results, not the full \
        Configuration object.
        """
        response = self.client.request("POST", "/configurations", json=config_data)

        data = response.json()
        return CreateConfigurationResponse(
            acknowledged=data.get("acknowledged", False),
            inserted_id=data.get("insertedId", ""),
            success=data.get("acknowledged", False),
        )

    async def create_configuration_async(
        self, request: PostConfigurationRequest
    ) -> CreateConfigurationResponse:
        """Create a new configuration asynchronously using \
        PostConfigurationRequest model."""
        response = await self.client.request_async(
            "POST",
            "/configurations",
            json=request.model_dump(mode="json", exclude_none=True),
        )

        data = response.json()
        return CreateConfigurationResponse(
            acknowledged=data.get("acknowledged", False),
            inserted_id=data.get("insertedId", ""),
            success=data.get("acknowledged", False),
        )

    async def create_configuration_from_dict_async(
        self, config_data: dict
    ) -> CreateConfigurationResponse:
        """Create a new configuration asynchronously from dictionary (legacy method).

        Note: This method now returns CreateConfigurationResponse to match the \
        actual API behavior.
        The API returns MongoDB-style operation results, not the full \
        Configuration object.
        """
        response = await self.client.request_async(
            "POST", "/configurations", json=config_data
        )

        data = response.json()
        return CreateConfigurationResponse(
            acknowledged=data.get("acknowledged", False),
            inserted_id=data.get("insertedId", ""),
            success=data.get("acknowledged", False),
        )

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

        # Handle both formats: list directly or object with "configurations" key
        if isinstance(data, list):
            # New format: API returns list directly
            configurations_data = data
        else:
            # Legacy format: API returns object with "configurations" key
            configurations_data = data.get("configurations", [])

        return [Configuration(**config_data) for config_data in configurations_data]

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

        # Handle both formats: list directly or object with "configurations" key
        if isinstance(data, list):
            # New format: API returns list directly
            configurations_data = data
        else:
            # Legacy format: API returns object with "configurations" key
            configurations_data = data.get("configurations", [])

        return [Configuration(**config_data) for config_data in configurations_data]

    def update_configuration(
        self, config_id: str, request: PutConfigurationRequest
    ) -> Configuration:
        """Update a configuration using PutConfigurationRequest model."""
        response = self.client.request(
            "PUT",
            f"/configurations/{config_id}",
            json=request.model_dump(mode="json", exclude_none=True),
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
            json=request.model_dump(mode="json", exclude_none=True),
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
        context = self._create_error_context(
            operation="delete_configuration",
            method="DELETE",
            path=f"/configurations/{config_id}",
            additional_context={"config_id": config_id},
        )

        with self.error_handler.handle_operation(context):
            response = self.client.request("DELETE", f"/configurations/{config_id}")
            return response.status_code == 200

    async def delete_configuration_async(self, config_id: str) -> bool:
        """Delete a configuration by ID asynchronously."""
        context = self._create_error_context(
            operation="delete_configuration_async",
            method="DELETE",
            path=f"/configurations/{config_id}",
            additional_context={"config_id": config_id},
        )

        with self.error_handler.handle_operation(context):
            response = await self.client.request_async(
                "DELETE", f"/configurations/{config_id}"
            )
            return response.status_code == 200
