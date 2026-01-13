"""Metrics API module for HoneyHive."""

from typing import List, Optional

from ..models import Metric, MetricEdit
from ..utils.error_handler import AuthenticationError, ErrorResponse
from .base import BaseAPI


class MetricsAPI(BaseAPI):
    """API for metric operations."""

    def create_metric(self, request: Metric) -> Metric:
        """Create a new metric using Metric model."""
        response = self.client.request(
            "POST",
            "/metrics",
            json=request.model_dump(mode="json", exclude_none=True),
        )

        data = response.json()
        # Backend returns {inserted: true, metric_id: "..."}
        if "metric_id" in data:
            # Fetch the created metric to return full object
            return self.get_metric(data["metric_id"])
        return Metric(**data)

    def create_metric_from_dict(self, metric_data: dict) -> Metric:
        """Create a new metric from dictionary (legacy method)."""
        response = self.client.request("POST", "/metrics", json=metric_data)

        data = response.json()
        # Backend returns {inserted: true, metric_id: "..."}
        if "metric_id" in data:
            # Fetch the created metric to return full object
            return self.get_metric(data["metric_id"])
        return Metric(**data)

    async def create_metric_async(self, request: Metric) -> Metric:
        """Create a new metric asynchronously using Metric model."""
        response = await self.client.request_async(
            "POST",
            "/metrics",
            json=request.model_dump(mode="json", exclude_none=True),
        )

        data = response.json()
        # Backend returns {inserted: true, metric_id: "..."}
        if "metric_id" in data:
            # Fetch the created metric to return full object
            return await self.get_metric_async(data["metric_id"])
        return Metric(**data)

    async def create_metric_from_dict_async(self, metric_data: dict) -> Metric:
        """Create a new metric asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async("POST", "/metrics", json=metric_data)

        data = response.json()
        # Backend returns {inserted: true, metric_id: "..."}
        if "metric_id" in data:
            # Fetch the created metric to return full object
            return await self.get_metric_async(data["metric_id"])
        return Metric(**data)

    def get_metric(self, metric_id: str) -> Metric:
        """Get a metric by ID."""
        # Use GET /metrics?id=... to filter by ID
        response = self.client.request("GET", "/metrics", params={"id": metric_id})
        data = response.json()

        # Backend returns array of metrics
        if isinstance(data, list) and len(data) > 0:
            return Metric(**data[0])
        if isinstance(data, list):
            raise ValueError(f"Metric with id {metric_id} not found")
        return Metric(**data)

    async def get_metric_async(self, metric_id: str) -> Metric:
        """Get a metric by ID asynchronously."""
        # Use GET /metrics?id=... to filter by ID
        response = await self.client.request_async(
            "GET", "/metrics", params={"id": metric_id}
        )
        data = response.json()

        # Backend returns array of metrics
        if isinstance(data, list) and len(data) > 0:
            return Metric(**data[0])
        if isinstance(data, list):
            raise ValueError(f"Metric with id {metric_id} not found")
        return Metric(**data)

    def list_metrics(
        self, project: Optional[str] = None, limit: int = 100
    ) -> List[Metric]:
        """List metrics with optional filtering."""
        params = {"limit": str(limit)}
        if project:
            params["project"] = project

        response = self.client.request("GET", "/metrics", params=params)
        data = response.json()

        # Backend returns array directly
        if isinstance(data, list):
            return self._process_data_dynamically(data, Metric, "metrics")
        return self._process_data_dynamically(
            data.get("metrics", []), Metric, "metrics"
        )

    async def list_metrics_async(
        self, project: Optional[str] = None, limit: int = 100
    ) -> List[Metric]:
        """List metrics asynchronously with optional filtering."""
        params = {"limit": str(limit)}
        if project:
            params["project"] = project

        response = await self.client.request_async("GET", "/metrics", params=params)
        data = response.json()

        # Backend returns array directly
        if isinstance(data, list):
            return self._process_data_dynamically(data, Metric, "metrics")
        return self._process_data_dynamically(
            data.get("metrics", []), Metric, "metrics"
        )

    def update_metric(self, metric_id: str, request: MetricEdit) -> Metric:
        """Update a metric using MetricEdit model."""
        # Backend expects PUT /metrics with id in body
        update_data = request.model_dump(mode="json", exclude_none=True)
        update_data["id"] = metric_id

        response = self.client.request(
            "PUT",
            "/metrics",
            json=update_data,
        )

        data = response.json()
        # Backend returns {updated: true}
        if data.get("updated"):
            return self.get_metric(metric_id)
        return Metric(**data)

    def update_metric_from_dict(self, metric_id: str, metric_data: dict) -> Metric:
        """Update a metric from dictionary (legacy method)."""
        # Backend expects PUT /metrics with id in body
        update_data = {**metric_data, "id": metric_id}

        response = self.client.request("PUT", "/metrics", json=update_data)

        data = response.json()
        # Backend returns {updated: true}
        if data.get("updated"):
            return self.get_metric(metric_id)
        return Metric(**data)

    async def update_metric_async(self, metric_id: str, request: MetricEdit) -> Metric:
        """Update a metric asynchronously using MetricEdit model."""
        # Backend expects PUT /metrics with id in body
        update_data = request.model_dump(mode="json", exclude_none=True)
        update_data["id"] = metric_id

        response = await self.client.request_async(
            "PUT",
            "/metrics",
            json=update_data,
        )

        data = response.json()
        # Backend returns {updated: true}
        if data.get("updated"):
            return await self.get_metric_async(metric_id)
        return Metric(**data)

    async def update_metric_from_dict_async(
        self, metric_id: str, metric_data: dict
    ) -> Metric:
        """Update a metric asynchronously from dictionary (legacy method)."""
        # Backend expects PUT /metrics with id in body
        update_data = {**metric_data, "id": metric_id}

        response = await self.client.request_async("PUT", "/metrics", json=update_data)

        data = response.json()
        # Backend returns {updated: true}
        if data.get("updated"):
            return await self.get_metric_async(metric_id)
        return Metric(**data)

    def delete_metric(self, metric_id: str) -> bool:
        """Delete a metric by ID.

        Note: Deleting metrics via API is not authorized for security reasons.
        Please use the HoneyHive web application to delete metrics.

        Args:
            metric_id: The ID of the metric to delete

        Raises:
            AuthenticationError: Always raised as this operation is not permitted
                via API
        """
        error_response = ErrorResponse(
            success=False,
            error_type="AuthenticationError",
            error_message=(
                "Deleting metrics via API is not authorized. "
                "Please use the HoneyHive web application to delete metrics."
            ),
            error_code="UNAUTHORIZED_OPERATION",
            status_code=403,
            details={
                "operation": "delete_metric",
                "metric_id": metric_id,
                "reason": "Metrics can only be deleted via the web application",
            },
        )

        raise AuthenticationError(
            "Deleting metrics via API is not authorized. Please use the webapp.",
            error_response=error_response,
        )

    async def delete_metric_async(self, metric_id: str) -> bool:
        """Delete a metric by ID asynchronously.

        Note: Deleting metrics via API is not authorized for security reasons.
        Please use the HoneyHive web application to delete metrics.

        Args:
            metric_id: The ID of the metric to delete

        Raises:
            AuthenticationError: Always raised as this operation is not permitted
                via API
        """
        error_response = ErrorResponse(
            success=False,
            error_type="AuthenticationError",
            error_message=(
                "Deleting metrics via API is not authorized. "
                "Please use the HoneyHive web application to delete metrics."
            ),
            error_code="UNAUTHORIZED_OPERATION",
            status_code=403,
            details={
                "operation": "delete_metric_async",
                "metric_id": metric_id,
                "reason": "Metrics can only be deleted via the web application",
            },
        )

        raise AuthenticationError(
            "Deleting metrics via API is not authorized. Please use the webapp.",
            error_response=error_response,
        )
