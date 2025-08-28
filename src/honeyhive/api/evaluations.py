"""Evaluations API module for HoneyHive."""

from typing import List, Optional

from ..models import EvaluationRun, CreateRunRequest, UpdateRunRequest, UpdateRunResponse, CreateRunResponse, GetRunsResponse, GetRunResponse, DeleteRunResponse
from .base import BaseAPI


class EvaluationsAPI(BaseAPI):
    """API for evaluation operations."""

    def create_run(self, request: CreateRunRequest) -> CreateRunResponse:
        """Create a new evaluation run using CreateRunRequest model."""
        response = self.client.request(
            "POST", 
            "/runs", 
            json={"run": request.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        return CreateRunResponse(**data)

    def create_run_from_dict(self, run_data: dict) -> CreateRunResponse:
        """Create a new evaluation run from dictionary (legacy method)."""
        response = self.client.request(
            "POST", 
            "/runs", 
            json={"run": run_data}
        )
        
        data = response.json()
        return CreateRunResponse(**data)

    async def create_run_async(self, request: CreateRunRequest) -> CreateRunResponse:
        """Create a new evaluation run asynchronously using CreateRunRequest model."""
        response = await self.client.request_async(
            "POST", 
            "/runs", 
            json={"run": request.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        return CreateRunResponse(**data)

    async def create_run_from_dict_async(self, run_data: dict) -> CreateRunResponse:
        """Create a new evaluation run asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async(
            "POST", 
            "/runs", 
            json={"run": run_data}
        )
        
        data = response.json()
        return CreateRunResponse(**data)

    def get_run(self, run_id: str) -> GetRunResponse:
        """Get an evaluation run by ID."""
        response = self.client.request("GET", f"/runs/{run_id}")
        data = response.json()
        return GetRunResponse(**data)

    async def get_run_async(self, run_id: str) -> GetRunResponse:
        """Get an evaluation run by ID asynchronously."""
        response = await self.client.request_async("GET", f"/runs/{run_id}")
        data = response.json()
        return GetRunResponse(**data)

    def list_runs(
        self, 
        project: Optional[str] = None, 
        limit: int = 100
    ) -> GetRunsResponse:
        """List evaluation runs with optional filtering."""
        params: dict = {"limit": limit}
        if project:
            params["project"] = project
        
        response = self.client.request("GET", "/runs", params=params)
        data = response.json()
        return GetRunsResponse(**data)

    async def list_runs_async(
        self, 
        project: Optional[str] = None, 
        limit: int = 100
    ) -> GetRunsResponse:
        """List evaluation runs asynchronously with optional filtering."""
        params: dict = {"limit": limit}
        if project:
            params["project"] = project
        
        response = await self.client.request_async("GET", "/runs", params=params)
        data = response.json()
        return GetRunsResponse(**data)

    def update_run(self, run_id: str, request: UpdateRunRequest) -> UpdateRunResponse:
        """Update an evaluation run using UpdateRunRequest model."""
        response = self.client.request(
            "PUT", 
            f"/runs/{run_id}", 
            json=request.model_dump(exclude_none=True)
        )
        
        data = response.json()
        return UpdateRunResponse(**data)

    def update_run_from_dict(self, run_id: str, run_data: dict) -> UpdateRunResponse:
        """Update an evaluation run from dictionary (legacy method)."""
        response = self.client.request(
            "PUT", 
            f"/runs/{run_id}", 
            json=run_data
        )
        
        data = response.json()
        return UpdateRunResponse(**data)

    async def update_run_async(self, run_id: str, request: UpdateRunRequest) -> UpdateRunResponse:
        """Update an evaluation run asynchronously using UpdateRunRequest model."""
        response = await self.client.request_async(
            "PUT", 
            f"/runs/{run_id}", 
            json=request.model_dump(exclude_none=True)
        )
        
        data = response.json()
        return UpdateRunResponse(**data)

    async def update_run_from_dict_async(self, run_id: str, run_data: dict) -> UpdateRunResponse:
        """Update an evaluation run asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async(
            "PUT", 
            f"/runs/{run_id}", 
            json=run_data
        )
        
        data = response.json()
        return UpdateRunResponse(**data)

    def delete_run(self, run_id: str) -> DeleteRunResponse:
        """Delete an evaluation run by ID."""
        try:
            response = self.client.request("DELETE", f"/runs/{run_id}")
            data = response.json()
            return DeleteRunResponse(**data)
        except Exception:
            return DeleteRunResponse(id=run_id, deleted=False)

    async def delete_run_async(self, run_id: str) -> DeleteRunResponse:
        """Delete an evaluation run by ID asynchronously."""
        try:
            response = await self.client.request_async("DELETE", f"/runs/{run_id}")
            data = response.json()
            return DeleteRunResponse(**data)
        except Exception:
            return DeleteRunResponse(id=run_id, deleted=False)
