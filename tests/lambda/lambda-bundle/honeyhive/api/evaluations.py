"""HoneyHive API evaluations module."""

import uuid
from typing import Any, Dict, List, Optional, cast
from uuid import UUID

from ..models import (
    CreateRunRequest,
    CreateRunResponse,
    DeleteRunResponse,
    GetRunResponse,
    GetRunsResponse,
    UpdateRunRequest,
    UpdateRunResponse,
)
from ..models.generated import UUIDType
from .base import BaseAPI


def _convert_uuids_recursively(data: Any) -> Any:
    """Recursively convert string UUIDs to UUIDType objects in response data."""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key in ["run_id", "id"] and isinstance(value, str):
                try:
                    result[key] = cast(Any, UUIDType(UUID(value)))
                except ValueError:
                    # If UUID conversion fails, keep the original string value
                    result[key] = value
            else:
                result[key] = _convert_uuids_recursively(value)
        return result
    elif isinstance(data, list):
        return [_convert_uuids_recursively(item) for item in data]
    else:
        return data


class EvaluationsAPI(BaseAPI):
    """API client for HoneyHive evaluations."""

    def create_run(self, request: CreateRunRequest) -> CreateRunResponse:
        """Create a new evaluation run using CreateRunRequest model."""
        response = self.client.request(
            "POST", "/runs", json={"run": request.model_dump(exclude_none=True)}
        )

        data = response.json()

        # Convert string UUIDs to UUIDType objects recursively
        data = _convert_uuids_recursively(data)

        return CreateRunResponse(**data)

    def create_run_from_dict(self, run_data: dict) -> CreateRunResponse:
        """Create a new evaluation run from dictionary (legacy method)."""
        response = self.client.request("POST", "/runs", json={"run": run_data})

        data = response.json()

        # Convert string UUIDs to UUIDType objects recursively
        data = _convert_uuids_recursively(data)

        return CreateRunResponse(**data)

    async def create_run_async(self, request: CreateRunRequest) -> CreateRunResponse:
        """Create a new evaluation run asynchronously using CreateRunRequest model."""
        response = await self.client.request_async(
            "POST", "/runs", json={"run": request.model_dump(exclude_none=True)}
        )

        data = response.json()

        # Convert string UUIDs to UUIDType objects recursively
        data = _convert_uuids_recursively(data)

        return CreateRunResponse(**data)

    async def create_run_from_dict_async(self, run_data: dict) -> CreateRunResponse:
        """Create a new evaluation run asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async(
            "POST", "/runs", json={"run": run_data}
        )

        data = response.json()

        # Convert string UUIDs to UUIDType objects recursively
        data = _convert_uuids_recursively(data)

        return CreateRunResponse(**data)

    def get_run(self, run_id: str) -> GetRunResponse:
        """Get an evaluation run by ID."""
        response = self.client.request("GET", f"/runs/{run_id}")
        data = response.json()

        # Convert string UUIDs to UUIDType objects recursively
        data = _convert_uuids_recursively(data)

        return GetRunResponse(**data)

    async def get_run_async(self, run_id: str) -> GetRunResponse:
        """Get an evaluation run asynchronously."""
        response = await self.client.request_async("GET", f"/runs/{run_id}")
        data = response.json()

        # Convert string UUIDs to UUIDType objects recursively
        data = _convert_uuids_recursively(data)

        return GetRunResponse(**data)

    def list_runs(
        self, project: Optional[str] = None, limit: int = 100
    ) -> GetRunsResponse:
        """List evaluation runs with optional filtering."""
        params: dict = {"limit": limit}
        if project:
            params["project"] = project

        response = self.client.request("GET", "/runs", params=params)
        data = response.json()

        # Convert string UUIDs to UUIDType objects recursively
        data = _convert_uuids_recursively(data)

        return GetRunsResponse(**data)

    async def list_runs_async(
        self, project: Optional[str] = None, limit: int = 100
    ) -> GetRunsResponse:
        """List evaluation runs asynchronously."""
        params: dict = {"limit": limit}
        if project:
            params["project"] = project

        response = await self.client.request_async("GET", "/runs", params=params)
        data = response.json()

        # Convert string UUIDs to UUIDType objects recursively
        data = _convert_uuids_recursively(data)

        return GetRunsResponse(**data)

    def update_run(self, run_id: str, request: UpdateRunRequest) -> UpdateRunResponse:
        """Update an evaluation run using UpdateRunRequest model."""
        response = self.client.request(
            "PUT", f"/runs/{run_id}", json=request.model_dump(exclude_none=True)
        )

        data = response.json()
        return UpdateRunResponse(**data)

    def update_run_from_dict(self, run_id: str, run_data: dict) -> UpdateRunResponse:
        """Update an evaluation run from dictionary (legacy method)."""
        response = self.client.request("PUT", f"/runs/{run_id}", json=run_data)

        data = response.json()
        return UpdateRunResponse(**data)

    async def update_run_async(
        self, run_id: str, request: UpdateRunRequest
    ) -> UpdateRunResponse:
        """Update an evaluation run asynchronously using UpdateRunRequest model."""
        response = await self.client.request_async(
            "PUT", f"/runs/{run_id}", json=request.model_dump(exclude_none=True)
        )

        data = response.json()
        return UpdateRunResponse(**data)

    async def update_run_from_dict_async(
        self, run_id: str, run_data: dict
    ) -> UpdateRunResponse:
        """Update an evaluation run asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async(
            "PUT", f"/runs/{run_id}", json=run_data
        )

        data = response.json()
        return UpdateRunResponse(**data)

    def delete_run(self, run_id: str) -> DeleteRunResponse:
        """Delete an evaluation run by ID."""
        try:
            response = self.client.request("DELETE", f"/runs/{run_id}")
            data = response.json()

            # Convert string UUIDs to UUIDType objects recursively
            data = _convert_uuids_recursively(data)

            return DeleteRunResponse(**data)
        except Exception:
            # Convert string run_id to UUIDType for the response
            try:
                uuid_obj = UUID(run_id)
                return DeleteRunResponse(id=UUIDType(uuid_obj), deleted=False)
            except ValueError:
                # If run_id is not a valid UUID, create a dummy one
                return DeleteRunResponse(id=UUIDType(uuid.uuid4()), deleted=False)

    async def delete_run_async(self, run_id: str) -> DeleteRunResponse:
        """Delete an evaluation run by ID asynchronously."""
        try:
            response = await self.client.request_async("DELETE", f"/runs/{run_id}")
            data = response.json()

            # Convert string UUIDs to UUIDType objects recursively
            data = _convert_uuids_recursively(data)

            return DeleteRunResponse(**data)
        except Exception:
            # Convert string run_id to UUIDType for the response
            try:
                uuid_obj = UUID(run_id)
                return DeleteRunResponse(id=UUIDType(uuid_obj), deleted=False)
            except ValueError:
                # If run_id is not a valid UUID, create a dummy one
                return DeleteRunResponse(id=UUIDType(uuid.uuid4()), deleted=False)
