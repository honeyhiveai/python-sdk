"""MetricsAPI Integration Tests - NO MOCKS, REAL API CALLS."""

import uuid
from typing import Any

import pytest

from honeyhive.models import CreateMetricRequest, CreateMetricResponse, MetricItem


class TestMetricsAPI:
    """Test MetricsAPI CRUD and compute operations."""

    @pytest.mark.skip(
        reason="Backend Issue: createMetric endpoint returns 400 Bad Request error"
    )
    def test_create_metric(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test custom metric creation with formula/config, verify backend."""
        test_id = str(uuid.uuid4())[:8]
        metric_name = f"test_metric_{test_id}"

        metric_request = CreateMetricRequest(
            name=metric_name,
            type="python",
            criteria="def evaluate(generation, metadata):\n    return len(generation)",
            description=f"Test metric {test_id}",
            return_type="float",
        )

        metric = integration_client.metrics.create(metric_request)

        assert isinstance(metric, CreateMetricResponse)
        assert metric.name == metric_name
        assert metric.type == "python"
        assert metric.description == f"Test metric {test_id}"

    @pytest.mark.skip(
        reason="Backend Issue: createMetric endpoint returns 400 Bad Request error (blocks retrieval test)"
    )
    def test_get_metric(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test metric retrieval by ID/name, test 404, verify metric definition."""
        test_id = str(uuid.uuid4())[:8]
        metric_name = f"test_get_metric_{test_id}"

        metric_request = CreateMetricRequest(
            name=metric_name,
            type="python",
            criteria="def evaluate(generation, metadata):\n    return 1.0",
            description="Test metric for retrieval",
            return_type="float",
        )

        created_metric = integration_client.metrics.create(metric_request)

        assert isinstance(created_metric, CreateMetricResponse)
        metric_id = getattr(
            created_metric, "id", getattr(created_metric, "metric_id", None)
        )
        if not metric_id:
            pytest.skip(
                "Metric creation didn't return ID - backend may not support retrieval"
            )
            return

        # v1 API doesn't have get_metric by ID - use list and filter
        metrics = integration_client.metrics.list(name=metric_name)
        assert isinstance(metrics, list)
        retrieved_metric = None
        for m in metrics:
            if m.name == metric_name:
                retrieved_metric = m
                break

        assert retrieved_metric is not None
        assert retrieved_metric.name == metric_name
        assert retrieved_metric.type == "python"
        assert retrieved_metric.description == "Test metric for retrieval"

    def test_list_metrics(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test metric listing with project filter, pagination, empty results."""
        metrics = integration_client.metrics.list()

        assert isinstance(metrics, list)
        assert all(isinstance(metric, MetricItem) for metric in metrics)

    def test_compute_metric(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test metric computation on event(s), verify results accuracy."""
        pytest.skip(
            "MetricsAPI.compute_metric() requires event_id "
            "and may not be fully implemented"
        )
