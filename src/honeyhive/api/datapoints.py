"""Datapoints API module for HoneyHive."""

from typing import List, Optional

from ..models import Datapoint, CreateDatapointRequest, UpdateDatapointRequest
from .base import BaseAPI


class DatapointsAPI(BaseAPI):
    """API for datapoint operations."""

    def create_datapoint(self, request: CreateDatapointRequest) -> Datapoint:
        """Create a new datapoint."""
        response = self.client.request(
            "POST", 
            "/datapoints", 
            json={"datapoint": request.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        return Datapoint(**data)

    async def create_datapoint_async(self, request: CreateDatapointRequest) -> Datapoint:
        """Create a new datapoint asynchronously."""
        response = await self.client.request_async(
            "POST", 
            "/datapoints", 
            json={"datapoint": request.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        return Datapoint(**data)

    def get_datapoint(self, datapoint_id: str) -> Datapoint:
        """Get a datapoint by ID."""
        response = self.client.request("GET", f"/datapoints/{datapoint_id}")
        data = response.json()
        return Datapoint(**data)

    async def get_datapoint_async(self, datapoint_id: str) -> Datapoint:
        """Get a datapoint by ID asynchronously."""
        response = await self.client.request_async("GET", f"/datapoints/{datapoint_id}")
        data = response.json()
        return Datapoint(**data)

    def list_datapoints(
        self, 
        project: Optional[str] = None, 
        dataset: Optional[str] = None,
        limit: int = 100
    ) -> List[Datapoint]:
        """List datapoints with optional filtering."""
        params = {"limit": limit}
        if project:
            params["project"] = project
        if dataset:
            params["dataset"] = dataset
        
        response = self.client.request("GET", "/datapoints", params=params)
        data = response.json()
        return [Datapoint(**datapoint_data) for datapoint_data in data.get("datapoints", [])]

    async def list_datapoints_async(
        self, 
        project: Optional[str] = None, 
        dataset: Optional[str] = None,
        limit: int = 100
    ) -> List[Datapoint]:
        """List datapoints with optional filtering asynchronously."""
        params = {"limit": limit}
        if project:
            params["project"] = project
        if dataset:
            params["dataset"] = dataset
        
        response = await self.client.request_async("GET", "/datapoints", params=params)
        data = response.json()
        return [Datapoint(**datapoint_data) for datapoint_data in data.get("datapoints", [])]

    def update_datapoint(self, datapoint_id: str, request: UpdateDatapointRequest) -> Datapoint:
        """Update a datapoint."""
        response = self.client.request(
            "PUT", 
            f"/datapoints/{datapoint_id}", 
            json=request.model_dump(exclude_none=True)
        )
        
        data = response.json()
        return Datapoint(**data)

    async def update_datapoint_async(self, datapoint_id: str, request: UpdateDatapointRequest) -> Datapoint:
        """Update a datapoint asynchronously."""
        response = await self.client.request_async(
            "PUT", 
            f"/datapoints/{datapoint_id}", 
            json=request.model_dump(exclude_none=True)
        )
        
        data = response.json()
        return Datapoint(**data)

    def delete_datapoint(self, datapoint_id: str) -> bool:
        """Delete a datapoint."""
        response = self.client.request("DELETE", f"/datapoints/{datapoint_id}")
        return response.status_code == 200

    async def delete_datapoint_async(self, datapoint_id: str) -> bool:
        """Delete a datapoint asynchronously."""
        response = await self.client.request_async("DELETE", f"/datapoints/{datapoint_id}")
        return response.status_code == 200
