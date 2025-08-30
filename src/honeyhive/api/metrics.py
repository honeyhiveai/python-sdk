"""Metrics API module for HoneyHive."""

from typing import List, Optional

from ..models import Metric, MetricEdit
from .base import BaseAPI


class MetricsAPI(BaseAPI):
    """API for metric operations."""

    def create_metric(self, request: Metric) -> Metric:
        """Create a new metric using Metric model."""
        response = self.client.request(
            "POST", "/metrics", json={"metric": request.model_dump(exclude_none=True)}
        )

        data = response.json()
        return Metric(**data)

    def create_metric_from_dict(self, metric_data: dict) -> Metric:
        """Create a new metric from dictionary (legacy method)."""
        response = self.client.request("POST", "/metrics", json={"metric": metric_data})

        data = response.json()
        return Metric(**data)

    async def create_metric_async(self, request: Metric) -> Metric:
        """Create a new metric asynchronously using Metric model."""
        response = await self.client.request_async(
            "POST", "/metrics", json={"metric": request.model_dump(exclude_none=True)}
        )

        data = response.json()
        return Metric(**data)

    async def create_metric_from_dict_async(self, metric_data: dict) -> Metric:
        """Create a new metric asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async(
            "POST", "/metrics", json={"metric": metric_data}
        )

        data = response.json()
        return Metric(**data)

    def get_metric(self, metric_id: str) -> Metric:
        """Get a metric by ID."""
        response = self.client.request("GET", f"/metrics/{metric_id}")
        data = response.json()
        return Metric(**data)

    async def get_metric_async(self, metric_id: str) -> Metric:
        """Get a metric by ID asynchronously."""
        response = await self.client.request_async("GET", f"/metrics/{metric_id}")
        data = response.json()
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
        return [Metric(**metric_data) for metric_data in data.get("metrics", [])]

    async def list_metrics_async(
        self, project: Optional[str] = None, limit: int = 100
    ) -> List[Metric]:
        """List metrics asynchronously with optional filtering."""
        params = {"limit": str(limit)}
        if project:
            params["project"] = project

        response = await self.client.request_async("GET", "/metrics", params=params)
        data = response.json()
        return [Metric(**metric_data) for metric_data in data.get("metrics", [])]

    def update_metric(self, metric_id: str, request: MetricEdit) -> Metric:
        """Update a metric using MetricEdit model."""
        response = self.client.request(
            "PUT", f"/metrics/{metric_id}", json=request.model_dump(exclude_none=True)
        )

        data = response.json()
        return Metric(**data)

    def update_metric_from_dict(self, metric_id: str, metric_data: dict) -> Metric:
        """Update a metric from dictionary (legacy method)."""
        response = self.client.request("PUT", f"/metrics/{metric_id}", json=metric_data)

        data = response.json()
        return Metric(**data)

    async def update_metric_async(self, metric_id: str, request: MetricEdit) -> Metric:
        """Update a metric asynchronously using MetricEdit model."""
        response = await self.client.request_async(
            "PUT", f"/metrics/{metric_id}", json=request.model_dump(exclude_none=True)
        )

        data = response.json()
        return Metric(**data)

    async def update_metric_from_dict_async(
        self, metric_id: str, metric_data: dict
    ) -> Metric:
        """Update a metric asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async(
            "PUT", f"/metrics/{metric_id}", json=metric_data
        )

        data = response.json()
        return Metric(**data)

    def delete_metric(self, metric_id: str) -> bool:
        """Delete a metric by ID."""
        try:
            response = self.client.request("DELETE", f"/metrics/{metric_id}")
            return response.status_code == 200
        except Exception:
            return False

    async def delete_metric_async(self, metric_id: str) -> bool:
        """Delete a metric by ID asynchronously."""
        try:
            response = await self.client.request_async(
                "DELETE", f"/metrics/{metric_id}"
            )
            return response.status_code == 200
        except Exception:
            return False
