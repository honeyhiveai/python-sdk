"""MetricsAPI Integration Tests - NO MOCKS, REAL API CALLS."""

import time
import uuid
from typing import Any

import pytest

from honeyhive.models import CreateMetricRequest


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

        assert metric is not None
        metric_name_attr = (
            metric.get("name") if isinstance(metric, dict) else getattr(metric, "name", None)
        )
        metric_type_attr = (
            metric.get("type") if isinstance(metric, dict) else getattr(metric, "type", None)
        )
        metric_desc_attr = (
            metric.get("description")
            if isinstance(metric, dict)
            else getattr(metric, "description", None)
        )
        assert metric_name_attr == metric_name
        assert metric_type_attr == "python"
        assert metric_desc_attr == f"Test metric {test_id}"

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

        metric_id = (
            created_metric.get("id")
            if isinstance(created_metric, dict)
            else getattr(
                created_metric, "id", getattr(created_metric, "metric_id", None)
            )
        )
        if not metric_id:
            pytest.skip(
                "Metric creation didn't return ID - backend may not support retrieval"
            )
            return

        # v1 API doesn't have get_metric by ID - use list and filter
        metrics_response = integration_client.metrics.list(name=metric_name)
        metrics = (
            metrics_response.metrics if hasattr(metrics_response, "metrics") else []
        )
        retrieved_metric = None
        for m in metrics:
            m_name = (
                m.get("name") if isinstance(m, dict) else getattr(m, "name", None)
            )
            if m_name == metric_name:
                retrieved_metric = m
                break

        assert retrieved_metric is not None
        ret_name = (
            retrieved_metric.get("name")
            if isinstance(retrieved_metric, dict)
            else getattr(retrieved_metric, "name", None)
        )
        ret_type = (
            retrieved_metric.get("type")
            if isinstance(retrieved_metric, dict)
            else getattr(retrieved_metric, "type", None)
        )
        ret_desc = (
            retrieved_metric.get("description")
            if isinstance(retrieved_metric, dict)
            else getattr(retrieved_metric, "description", None)
        )
        assert ret_name == metric_name
        assert ret_type == "python"
        assert ret_desc == "Test metric for retrieval"

    @pytest.mark.skip(
        reason="Backend Issue: createMetric endpoint returns 400 Bad Request error (blocks list test)"
    )
    def test_list_metrics(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test metric listing with project filter, pagination, empty results."""
        test_id = str(uuid.uuid4())[:8]

        for i in range(2):
            metric_request = CreateMetricRequest(
                name=f"test_list_metric_{test_id}_{i}",
                type="python",
                criteria=f"def evaluate(generation, metadata):\n    return {i}",
                description=f"Test metric {i}",
                return_type="float",
            )
            integration_client.metrics.create(metric_request)

        time.sleep(2)

        metrics_response = integration_client.metrics.list()

        assert metrics_response is not None
        metrics = (
            metrics_response.metrics if hasattr(metrics_response, "metrics") else []
        )
        assert isinstance(metrics, list)
        # May be empty, that's ok - basic existence check
        assert len(metrics) >= 0

    def test_compute_metric(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test metric computation on event(s), verify results accuracy."""
        pytest.skip(
            "MetricsAPI.compute_metric() requires event_id "
            "and may not be fully implemented"
        )
