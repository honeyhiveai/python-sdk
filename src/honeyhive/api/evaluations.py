"""HoneyHive API evaluations module."""

from typing import Any, Dict, Optional, cast
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
from ..utils.error_handler import APIError, ErrorContext, ErrorResponse
from .base import BaseAPI


def _convert_uuid_string(value: str) -> Any:
    """Convert a single UUID string to UUIDType, or return original on error."""
    try:
        return cast(Any, UUIDType(UUID(value)))
    except ValueError:
        return value


def _convert_uuid_list(items: list) -> list:
    """Convert a list of UUID strings to UUIDType objects."""
    converted = []
    for item in items:
        if isinstance(item, str):
            converted.append(_convert_uuid_string(item))
        else:
            converted.append(item)
    return converted


def _convert_uuids_recursively(data: Any) -> Any:
    """Recursively convert string UUIDs to UUIDType objects in response data."""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key in ["run_id", "id"] and isinstance(value, str):
                result[key] = _convert_uuid_string(value)
            elif key == "event_ids" and isinstance(value, list):
                result[key] = _convert_uuid_list(value)
            else:
                result[key] = _convert_uuids_recursively(value)
        return result
    if isinstance(data, list):
        return [_convert_uuids_recursively(item) for item in data]
    return data


class EvaluationsAPI(BaseAPI):
    """API client for HoneyHive evaluations."""

    def create_run(self, request: CreateRunRequest) -> CreateRunResponse:
        """Create a new evaluation run using CreateRunRequest model."""
        response = self.client.request(
            "POST",
            "/runs",
            json={"run": request.model_dump(mode="json", exclude_none=True)},
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
            "POST",
            "/runs",
            json={"run": request.model_dump(mode="json", exclude_none=True)},
        )

        data = response.json()

        # Convert string UUIDs to UUIDType objects recursively
        data = _convert_uuids_recursively(data)

        return CreateRunResponse(**data)

    async def create_run_from_dict_async(self, run_data: dict) -> CreateRunResponse:
        """Create a new evaluation run asynchronously from dictionary
        (legacy method)."""
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
            "PUT",
            f"/runs/{run_id}",
            json=request.model_dump(mode="json", exclude_none=True),
        )

        data = response.json()
        return UpdateRunResponse(**data)

    def update_run_from_dict(self, run_id: str, run_data: dict) -> UpdateRunResponse:
        """Update an evaluation run from dictionary (legacy method)."""
        response = self.client.request("PUT", f"/runs/{run_id}", json=run_data)

        # Check response status before parsing
        if response.status_code >= 400:
            error_body = {}
            try:
                error_body = response.json()
            except Exception:
                try:
                    error_body = {"error_text": response.text[:500]}
                except Exception:
                    pass

            # Create ErrorResponse for proper error handling
            error_response = ErrorResponse(
                error_type="APIError",
                error_message=(
                    f"HTTP {response.status_code}: Failed to update run {run_id}"
                ),
                error_code=(
                    "CLIENT_ERROR" if response.status_code < 500 else "SERVER_ERROR"
                ),
                status_code=response.status_code,
                details={
                    "run_id": run_id,
                    "update_data": run_data,
                    "error_response": error_body,
                },
                context=ErrorContext(
                    operation="update_run_from_dict",
                    method="PUT",
                    url=f"/runs/{run_id}",
                    json_data=run_data,
                ),
            )

            raise APIError(
                f"HTTP {response.status_code}: Failed to update run {run_id}",
                error_response=error_response,
                original_exception=None,
            )

        data = response.json()
        return UpdateRunResponse(**data)

    async def update_run_async(
        self, run_id: str, request: UpdateRunRequest
    ) -> UpdateRunResponse:
        """Update an evaluation run asynchronously using UpdateRunRequest model."""
        response = await self.client.request_async(
            "PUT",
            f"/runs/{run_id}",
            json=request.model_dump(mode="json", exclude_none=True),
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
        context = self._create_error_context(
            operation="delete_run",
            method="DELETE",
            path=f"/runs/{run_id}",
            additional_context={"run_id": run_id},
        )

        with self.error_handler.handle_operation(context):
            response = self.client.request("DELETE", f"/runs/{run_id}")
            data = response.json()

            # Convert string UUIDs to UUIDType objects recursively
            data = _convert_uuids_recursively(data)

            return DeleteRunResponse(**data)

    async def delete_run_async(self, run_id: str) -> DeleteRunResponse:
        """Delete an evaluation run by ID asynchronously."""
        context = self._create_error_context(
            operation="delete_run_async",
            method="DELETE",
            path=f"/runs/{run_id}",
            additional_context={"run_id": run_id},
        )

        with self.error_handler.handle_operation(context):
            response = await self.client.request_async("DELETE", f"/runs/{run_id}")
            data = response.json()

            # Convert string UUIDs to UUIDType objects recursively
            data = _convert_uuids_recursively(data)

            return DeleteRunResponse(**data)

    def get_run_result(
        self, run_id: str, aggregate_function: str = "average"
    ) -> Dict[str, Any]:
        """
        Get aggregated result for a run from backend.

        Backend Endpoint: GET /runs/:run_id/result?aggregate_function=<function>

        The backend computes all aggregations, pass/fail status, and composite metrics.

        Args:
            run_id: Experiment run ID
            aggregate_function: Aggregation function ("average", "sum", "min", "max")

        Returns:
            Dictionary with aggregated results from backend

        Example:
            >>> results = client.evaluations.get_run_result("run-123", "average")
            >>> results["success"]
            True
            >>> results["metrics"]["accuracy"]
            {'aggregate': 0.85, 'values': [0.8, 0.9, 0.85]}
        """
        response = self.client.request(
            "GET",
            f"/runs/{run_id}/result",
            params={"aggregate_function": aggregate_function},
        )
        return cast(Dict[str, Any], response.json())

    async def get_run_result_async(
        self, run_id: str, aggregate_function: str = "average"
    ) -> Dict[str, Any]:
        """Get aggregated result for a run asynchronously."""
        response = await self.client.request_async(
            "GET",
            f"/runs/{run_id}/result",
            params={"aggregate_function": aggregate_function},
        )
        return cast(Dict[str, Any], response.json())

    def get_run_metrics(self, run_id: str) -> Dict[str, Any]:
        """
        Get raw metrics for a run (without aggregation).

        Backend Endpoint: GET /runs/:run_id/metrics

        Args:
            run_id: Experiment run ID

        Returns:
            Dictionary with raw metrics data

        Example:
            >>> metrics = client.evaluations.get_run_metrics("run-123")
            >>> metrics["events"]
            [{'event_id': '...', 'metrics': {...}}, ...]
        """
        response = self.client.request("GET", f"/runs/{run_id}/metrics")
        return cast(Dict[str, Any], response.json())

    async def get_run_metrics_async(self, run_id: str) -> Dict[str, Any]:
        """Get raw metrics for a run asynchronously."""
        response = await self.client.request_async("GET", f"/runs/{run_id}/metrics")
        return cast(Dict[str, Any], response.json())

    def compare_runs(
        self, new_run_id: str, old_run_id: str, aggregate_function: str = "average"
    ) -> Dict[str, Any]:
        """
        Compare two experiment runs using backend aggregated comparison.

        Backend Endpoint: GET /runs/:new_run_id/compare-with/:old_run_id

        The backend computes metric deltas, percent changes, and datapoint differences.

        Args:
            new_run_id: New experiment run ID
            old_run_id: Old experiment run ID
            aggregate_function: Aggregation function ("average", "sum", "min", "max")

        Returns:
            Dictionary with aggregated comparison data

        Example:
            >>> comparison = client.evaluations.compare_runs("run-new", "run-old")
            >>> comparison["metric_deltas"]["accuracy"]
            {'new_value': 0.85, 'old_value': 0.80, 'delta': 0.05}
        """
        response = self.client.request(
            "GET",
            f"/runs/{new_run_id}/compare-with/{old_run_id}",
            params={"aggregate_function": aggregate_function},
        )
        return cast(Dict[str, Any], response.json())

    async def compare_runs_async(
        self, new_run_id: str, old_run_id: str, aggregate_function: str = "average"
    ) -> Dict[str, Any]:
        """Compare two experiment runs asynchronously (aggregated)."""
        response = await self.client.request_async(
            "GET",
            f"/runs/{new_run_id}/compare-with/{old_run_id}",
            params={"aggregate_function": aggregate_function},
        )
        return cast(Dict[str, Any], response.json())

    def compare_run_events(
        self,
        new_run_id: str,
        old_run_id: str,
        *,
        event_name: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        Compare events between two experiment runs with datapoint-level matching.

        Backend Endpoint: GET /runs/compare/events

        The backend matches events by datapoint_id and provides detailed
        per-datapoint comparison with improved/degraded/same classification.

        Args:
            new_run_id: New experiment run ID (run_id_1)
            old_run_id: Old experiment run ID (run_id_2)
            event_name: Optional event name filter (e.g., "initialization")
            event_type: Optional event type filter (e.g., "session")
            limit: Pagination limit (default: 100)
            page: Pagination page (default: 1)

        Returns:
            Dictionary with detailed comparison including:
            - commonDatapoints: List of common datapoint IDs
            - metrics: Per-metric comparison with improved/degraded/same lists
            - events: Paired events (event_1, event_2) for each datapoint
            - event_details: Event presence information
            - old_run: Old run metadata
            - new_run: New run metadata

        Example:
            >>> comparison = client.evaluations.compare_run_events(
            ...     "run-new", "run-old",
            ...     event_name="initialization",
            ...     event_type="session"
            ... )
            >>> len(comparison["commonDatapoints"])
            3
            >>> comparison["metrics"][0]["improved"]
            ["EXT-c1aed4cf0dfc3f16"]
        """
        params = {
            "run_id_1": new_run_id,
            "run_id_2": old_run_id,
            "limit": limit,
            "page": page,
        }

        if event_name:
            params["event_name"] = event_name
        if event_type:
            params["event_type"] = event_type

        response = self.client.request("GET", "/runs/compare/events", params=params)
        return cast(Dict[str, Any], response.json())

    async def compare_run_events_async(
        self,
        new_run_id: str,
        old_run_id: str,
        *,
        event_name: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Compare events between two experiment runs asynchronously."""
        params = {
            "run_id_1": new_run_id,
            "run_id_2": old_run_id,
            "limit": limit,
            "page": page,
        }

        if event_name:
            params["event_name"] = event_name
        if event_type:
            params["event_type"] = event_type

        response = await self.client.request_async(
            "GET", "/runs/compare/events", params=params
        )
        return cast(Dict[str, Any], response.json())
