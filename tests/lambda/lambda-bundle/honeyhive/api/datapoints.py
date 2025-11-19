"""Datapoints API module for HoneyHive."""

from typing import List, Optional

from ..models import CreateDatapointRequest, Datapoint, UpdateDatapointRequest
from .base import BaseAPI


class DatapointsAPI(BaseAPI):
    """API for datapoint operations."""

    def create_datapoint(self, request: CreateDatapointRequest) -> Datapoint:
        """Create a new datapoint using CreateDatapointRequest model."""
        response = self.client.request(
            "POST",
            "/datapoints",
            json={"datapoint": request.model_dump(exclude_none=True)},
        )

        data = response.json()
        return Datapoint(**data)

    def create_datapoint_from_dict(self, datapoint_data: dict) -> Datapoint:
        """Create a new datapoint from dictionary (legacy method)."""
        response = self.client.request(
            "POST", "/datapoints", json={"datapoint": datapoint_data}
        )

        data = response.json()
        return Datapoint(**data)

    async def create_datapoint_async(
        self, request: CreateDatapointRequest
    ) -> Datapoint:
        """Create a new datapoint asynchronously using CreateDatapointRequest model."""
        response = await self.client.request_async(
            "POST",
            "/datapoints",
            json={"datapoint": request.model_dump(exclude_none=True)},
        )

        data = response.json()
        return Datapoint(**data)

    async def create_datapoint_from_dict_async(self, datapoint_data: dict) -> Datapoint:
        """Create a new datapoint asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async(
            "POST", "/datapoints", json={"datapoint": datapoint_data}
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
        limit: int = 100,
    ) -> List[Datapoint]:
        """List datapoints with optional filtering."""
        params = {"limit": str(limit)}
        if project:
            params["project"] = project
        if dataset:
            params["dataset"] = dataset

        response = self.client.request("GET", "/datapoints", params=params)
        data = response.json()
        return [
            Datapoint(**datapoint_data) for datapoint_data in data.get("datapoints", [])
        ]

    async def list_datapoints_async(
        self,
        project: Optional[str] = None,
        dataset: Optional[str] = None,
        limit: int = 100,
    ) -> List[Datapoint]:
        """List datapoints asynchronously with optional filtering."""
        params = {"limit": str(limit)}
        if project:
            params["project"] = project
        if dataset:
            params["dataset"] = dataset

        response = await self.client.request_async("GET", "/datapoints", params=params)
        data = response.json()
        return [
            Datapoint(**datapoint_data) for datapoint_data in data.get("datapoints", [])
        ]

    def update_datapoint(
        self, datapoint_id: str, request: UpdateDatapointRequest
    ) -> Datapoint:
        """Update a datapoint using UpdateDatapointRequest model."""
        response = self.client.request(
            "PUT",
            f"/datapoints/{datapoint_id}",
            json=request.model_dump(exclude_none=True),
        )

        data = response.json()
        return Datapoint(**data)

    def update_datapoint_from_dict(
        self, datapoint_id: str, datapoint_data: dict
    ) -> Datapoint:
        """Update a datapoint from dictionary (legacy method)."""
        response = self.client.request(
            "PUT", f"/datapoints/{datapoint_id}", json=datapoint_data
        )

        data = response.json()
        return Datapoint(**data)

    async def update_datapoint_async(
        self, datapoint_id: str, request: UpdateDatapointRequest
    ) -> Datapoint:
        """Update a datapoint asynchronously using UpdateDatapointRequest model."""
        response = await self.client.request_async(
            "PUT",
            f"/datapoints/{datapoint_id}",
            json=request.model_dump(exclude_none=True),
        )

        data = response.json()
        return Datapoint(**data)

    async def update_datapoint_from_dict_async(
        self, datapoint_id: str, datapoint_data: dict
    ) -> Datapoint:
        """Update a datapoint asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async(
            "PUT", f"/datapoints/{datapoint_id}", json=datapoint_data
        )

        data = response.json()
        return Datapoint(**data)
