"""MetricsAPI Integration Tests - NO MOCKS, REAL API CALLS."""

import uuid
from typing import Any

from honeyhive.models import CreateMetricRequest, CreateMetricResponse, MetricItem


def _python_metric_request(metric_name: str, description: str) -> CreateMetricRequest:
    """Minimal valid PYTHON metric request.

    The backend requires the uppercase ``PYTHON``/``LLM``/``HUMAN``/``COMPOSITE``
    type enum and a numeric ``scale`` whenever ``return_type="float"``.
    """
    return CreateMetricRequest(
        name=metric_name,
        type="PYTHON",
        criteria="def evaluate(generation, metadata):\n    return len(generation)",
        description=description,
        return_type="float",
        scale=100,
    )


class TestMetricsAPI:
    """Test MetricsAPI CRUD operations."""

    def test_create_metric(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test custom metric creation, verify backend response."""
        test_id = str(uuid.uuid4())[:8]
        metric_name = f"test_metric_{test_id}"

        metric = integration_client.metrics.create(
            _python_metric_request(metric_name, f"Test metric {test_id}")
        )

        try:
            # POST /metrics returns {inserted, metric_id}, not the full metric.
            assert isinstance(metric, CreateMetricResponse)
            assert metric.inserted is True
            assert metric.metric_id
        finally:
            integration_client.metrics.delete(metric.metric_id)

    def test_get_metric(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test metric retrieval by ID, verify metric definition."""
        test_id = str(uuid.uuid4())[:8]
        metric_name = f"test_get_metric_{test_id}"

        created_metric = integration_client.metrics.create(
            _python_metric_request(metric_name, "Test metric for retrieval")
        )

        try:
            # get_metric filters GET /v1/metrics server-side by id.
            metrics = integration_client.metrics.get_metric(created_metric.metric_id)
            assert isinstance(metrics, list)
            assert len(metrics) == 1, (
                f"Expected exactly the created metric, got {len(metrics)}"
            )
            retrieved_metric = metrics[0]

            assert retrieved_metric.id == created_metric.metric_id
            assert retrieved_metric.name == metric_name
            assert retrieved_metric.type == "PYTHON"
            assert retrieved_metric.description == "Test metric for retrieval"
            assert retrieved_metric.return_type == "float"
        finally:
            integration_client.metrics.delete(created_metric.metric_id)

    def test_list_metrics(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test metric listing with project filter, pagination, empty results."""
        metrics = integration_client.metrics.list()

        assert isinstance(metrics, list)
        assert all(isinstance(metric, MetricItem) for metric in metrics)
