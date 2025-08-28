"""Evaluations API module for HoneyHive."""

from typing import List, Optional

from ..models import EvaluationRun, CreateRunRequest, UpdateRunRequest, GetRunsResponse
from .base import BaseAPI


class EvaluationsAPI(BaseAPI):
    """API for evaluation operations."""

    def create_evaluation_run(self, request: CreateRunRequest) -> EvaluationRun:
        """Create a new evaluation run."""
        response = self.client.request(
            "POST", 
            "/evaluations/runs", 
            json={"run": request.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        return EvaluationRun(**data)

    async def create_evaluation_run_async(self, request: CreateRunRequest) -> EvaluationRun:
        """Create a new evaluation run asynchronously."""
        response = await self.client.request_async(
            "POST", 
            "/evaluations/runs", 
            json={"run": request.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        return EvaluationRun(**data)

    def get_evaluation_run(self, run_id: str) -> EvaluationRun:
        """Get an evaluation run by ID."""
        response = self.client.request("GET", f"/evaluations/runs/{run_id}")
        data = response.json()
        return EvaluationRun(**data)

    async def get_evaluation_run_async(self, run_id: str) -> EvaluationRun:
        """Get an evaluation run by ID asynchronously."""
        response = await self.client.request_async("GET", f"/evaluations/runs/{run_id}")
        data = response.json()
        return EvaluationRun(**data)

    def list_evaluation_runs(
        self, 
        project: Optional[str] = None, 
        limit: int = 100
    ) -> List[EvaluationRun]:
        """List evaluation runs with optional filtering."""
        params = {"limit": limit}
        if project:
            params["project"] = project
        
        response = self.client.request("GET", "/evaluations/runs", params=params)
        data = response.json()
        return [EvaluationRun(**run_data) for run_data in data.get("runs", [])]

    async def list_evaluation_runs_async(
        self, 
        project: Optional[str] = None, 
        limit: int = 100
    ) -> List[EvaluationRun]:
        """List evaluation runs with optional filtering asynchronously."""
        params = {"limit": limit}
        if project:
            params["project"] = project
        
        response = await self.client.request_async("GET", "/evaluations/runs", params=params)
        data = response.json()
        return [EvaluationRun(**run_data) for run_data in data.get("runs", [])]

    def update_evaluation_run(self, run_id: str, request: UpdateRunRequest) -> EvaluationRun:
        """Update an evaluation run."""
        response = self.client.request(
            "PUT", 
            f"/evaluations/runs/{run_id}", 
            json=request.model_dump(exclude_none=True)
        )
        
        data = response.json()
        return EvaluationRun(**data)

    async def update_evaluation_run_async(self, run_id: str, request: UpdateRunRequest) -> EvaluationRun:
        """Update an evaluation run asynchronously."""
        response = await self.client.request_async(
            "PUT", 
            f"/evaluations/runs/{run_id}", 
            json=request.model_dump(exclude_none=True)
        )
        
        data = response.json()
        return EvaluationRun(**data)

    def delete_evaluation_run(self, run_id: str) -> bool:
        """Delete an evaluation run."""
        response = self.client.request("DELETE", f"/evaluations/runs/{run_id}")
        return response.status_code == 200

    async def delete_evaluation_run_async(self, run_id: str) -> bool:
        """Delete an evaluation run asynchronously."""
        response = await self.client.request_async("DELETE", f"/evaluations/runs/{run_id}")
        return response.status_code == 200
