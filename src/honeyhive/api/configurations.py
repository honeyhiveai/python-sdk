"""Configurations API module for HoneyHive."""

from typing import List, Optional

from ..models import Configuration, PostConfigurationRequest, PutConfigurationRequest
from .base import BaseAPI


class ConfigurationsAPI(BaseAPI):
    """API for configuration operations."""

    def create_configuration(self, request: PostConfigurationRequest) -> Configuration:
        """Create a new configuration."""
        response = self.client.request(
            "POST", 
            "/configurations", 
            json={"configuration": request.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        return Configuration(**data)

    async def create_configuration_async(self, request: PostConfigurationRequest) -> Configuration:
        """Create a new configuration asynchronously."""
        response = await self.client.request_async(
            "POST", 
            "/configurations", 
            json={"configuration": request.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        return Configuration(**data)

    def get_configuration(self, configuration_id: str) -> Configuration:
        """Get a configuration by ID."""
        response = self.client.request("GET", f"/configurations/{configuration_id}")
        data = response.json()
        return Configuration(**data)

    async def get_configuration_async(self, configuration_id: str) -> Configuration:
        """Get a configuration by ID asynchronously."""
        response = await self.client.request_async("GET", f"/configurations/{configuration_id}")
        data = response.json()
        return Configuration(**data)

    def list_configurations(
        self, 
        project: Optional[str] = None, 
        env: Optional[str] = None,
        limit: int = 100
    ) -> List[Configuration]:
        """List configurations with optional filtering."""
        params = {"limit": limit}
        if project:
            params["project"] = project
        if env:
            params["env"] = env
        
        response = self.client.request("GET", "/configurations", params=params)
        data = response.json()
        return [Configuration(**config_data) for config_data in data.get("configurations", [])]

    async def list_configurations_async(
        self, 
        project: Optional[str] = None, 
        env: Optional[str] = None,
        limit: int = 100
    ) -> List[Configuration]:
        """List configurations with optional filtering asynchronously."""
        params = {"limit": limit}
        if project:
            params["project"] = project
        if env:
            params["env"] = env
        
        response = await self.client.request_async("GET", "/configurations", params=params)
        data = response.json()
        return [Configuration(**config_data) for config_data in data.get("configurations", [])]

    def update_configuration(self, configuration_id: str, request: PutConfigurationRequest) -> Configuration:
        """Update a configuration."""
        response = self.client.request(
            "PUT", 
            f"/configurations/{configuration_id}", 
            json=request.model_dump(exclude_none=True)
        )
        
        data = response.json()
        return Configuration(**data)

    async def update_configuration_async(self, configuration_id: str, request: PutConfigurationRequest) -> Configuration:
        """Update a configuration asynchronously."""
        response = await self.client.request_async(
            "PUT", 
            f"/configurations/{configuration_id}", 
            json=request.model_dump(exclude_none=True)
        )
        
        data = response.json()
        return Configuration(**data)

    def delete_configuration(self, configuration_id: str) -> bool:
        """Delete a configuration."""
        response = self.client.request("DELETE", f"/configurations/{configuration_id}")
        return response.status_code == 200

    async def delete_configuration_async(self, configuration_id: str) -> bool:
        """Delete a configuration asynchronously."""
        response = await self.client.request_async("DELETE", f"/configurations/{configuration_id}")
        return response.status_code == 200
