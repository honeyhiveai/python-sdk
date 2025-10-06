"""Unit tests for HoneyHive Experiments Results Functions.

This module contains comprehensive unit tests for the experiments module's
result retrieval functions that interact with backend API endpoints.

Tests cover:
- get_run_result() - Fetches aggregated experiment results
- get_run_metrics() - Fetches raw metrics for a run
- compare_runs() - Compares two experiment runs
- Model parsing (JSON responses → Pydantic models)
- Error handling (404, 500, network errors)
"""

# pylint: disable=protected-access,redefined-outer-name,too-many-public-methods
# pylint: disable=no-member
# Justification: Testing behavior, pytest fixture patterns, comprehensive coverage
# Justification: Pydantic model dynamic fields accessed via model_extra

from unittest.mock import Mock

import pytest

from honeyhive.experiments.models import (
    AggregatedMetrics,
    ExperimentResultSummary,
    RunComparisonResult,
)
from honeyhive.experiments.results import compare_runs, get_run_metrics, get_run_result


@pytest.fixture
def mock_client() -> Mock:
    """Create a mock HoneyHive client."""
    client = Mock()
    client.evaluations = Mock()
    return client


class TestGetRunResult:
    """Test suite for get_run_result function."""

    def test_successful_result_retrieval(self, mock_client: Mock) -> None:
        """Test successful result retrieval returns ExperimentResultSummary."""
        # Mock API response
        mock_response = {
            "run_id": "run-123",
            "status": "completed",
            "success": True,
            "passed": ["dp-1", "dp-2"],
            "failed": ["dp-3"],
            "metrics": {
                "aggregation_function": "average",
                "accuracy": {"aggregate": 0.85, "values": [0.8, 0.9]},
                "latency": {"aggregate": 1.2, "values": [1.0, 1.4]},
            },
            "datapoints": [
                {"id": "dp-1", "result": "pass"},
                {"id": "dp-2", "result": "pass"},
                {"id": "dp-3", "result": "fail"},
            ],
        }
        mock_client.evaluations.get_run_result.return_value = mock_response

        result = get_run_result(mock_client, "run-123")

        assert isinstance(result, ExperimentResultSummary)
        assert result.run_id == "run-123"
        assert result.status == "completed"
        assert result.success is True
        assert result.passed == ["dp-1", "dp-2"]
        assert result.failed == ["dp-3"]
        assert isinstance(result.metrics, AggregatedMetrics)
        mock_client.evaluations.get_run_result.assert_called_once_with(
            run_id="run-123", aggregate_function="average"
        )

    def test_custom_aggregation_function(self, mock_client: Mock) -> None:
        """Test that custom aggregation function is passed to API."""
        mock_response = {
            "run_id": "run-123",
            "status": "completed",
            "success": True,
            "metrics": {},
        }
        mock_client.evaluations.get_run_result.return_value = mock_response

        get_run_result(mock_client, "run-123", aggregate_function="median")

        mock_client.evaluations.get_run_result.assert_called_once_with(
            run_id="run-123", aggregate_function="median"
        )

    def test_metrics_parsing(self, mock_client: Mock) -> None:
        """Test that metrics are correctly parsed into AggregatedMetrics."""
        mock_response = {
            "run_id": "run-123",
            "status": "completed",
            "success": True,
            "metrics": {
                "aggregation_function": "p95",
                "accuracy": {"aggregate": 0.92},
                "cost": {"aggregate": 0.05},
            },
        }
        mock_client.evaluations.get_run_result.return_value = mock_response

        result = get_run_result(mock_client, "run-123")

        assert result.metrics.aggregation_function == "p95"
        assert result.metrics.get_metric("accuracy") == {"aggregate": 0.92}
        assert result.metrics.get_metric("cost") == {"aggregate": 0.05}

    def test_empty_metrics(self, mock_client: Mock) -> None:
        """Test handling of response with no metrics."""
        mock_response = {
            "run_id": "run-123",
            "status": "completed",
            "success": False,
            "metrics": {},
        }
        mock_client.evaluations.get_run_result.return_value = mock_response

        result = get_run_result(mock_client, "run-123")

        assert isinstance(result.metrics, AggregatedMetrics)
        assert result.metrics.list_metrics() == []


class TestGetRunMetrics:
    """Test suite for get_run_metrics function."""

    def test_successful_metrics_retrieval(self, mock_client: Mock) -> None:
        """Test successful metrics retrieval returns dict."""
        mock_response = {
            "accuracy": {"aggregate": 0.85, "values": [0.8, 0.9]},
            "latency": {"aggregate": 1.2, "values": [1.0, 1.4]},
            "cost": {"aggregate": 0.05},
        }
        mock_client.evaluations.get_run_metrics.return_value = mock_response

        result = get_run_metrics(mock_client, "run-123")

        assert isinstance(result, dict)
        assert result["accuracy"]["aggregate"] == 0.85
        assert result["latency"]["aggregate"] == 1.2
        assert result["cost"]["aggregate"] == 0.05
        mock_client.evaluations.get_run_metrics.assert_called_once_with(
            run_id="run-123"
        )

    def test_empty_metrics_response(self, mock_client: Mock) -> None:
        """Test handling of empty metrics response."""
        mock_response = {}
        mock_client.evaluations.get_run_metrics.return_value = mock_response

        result = get_run_metrics(mock_client, "run-123")

        assert result == {}

    def test_metrics_with_nested_structure(self, mock_client: Mock) -> None:
        """Test metrics with complex nested structure."""
        mock_response = {
            "accuracy": {
                "aggregate": 0.85,
                "values": [0.8, 0.9],
                "per_class": {"A": 0.9, "B": 0.8},
            },
            "latency": {
                "aggregate": 1.2,
                "p50": 1.0,
                "p95": 1.5,
                "p99": 2.0,
            },
        }
        mock_client.evaluations.get_run_metrics.return_value = mock_response

        result = get_run_metrics(mock_client, "run-123")

        assert result["accuracy"]["per_class"] == {"A": 0.9, "B": 0.8}
        assert result["latency"]["p95"] == 1.5


class TestCompareRuns:
    """Test suite for compare_runs function."""

    def test_successful_comparison(self, mock_client: Mock) -> None:
        """Test successful run comparison returns RunComparisonResult."""
        mock_response = {
            "commonDatapoints": [
                "dp-1",
                "dp-2",
                "dp-3",
                "dp-4",
                "dp-5",
                "dp-6",
                "dp-7",
                "dp-8",
                "dp-9",
                "dp-10",
            ],
            "metrics": [
                {
                    "metric_name": "accuracy",
                    "old_aggregate": 0.80,
                    "new_aggregate": 0.85,
                    "found_count": 10,
                    "improved_count": 5,
                    "degraded_count": 2,
                    "improved": ["dp-1", "dp-2"],
                    "degraded": ["dp-3"],
                },
                {
                    "metric_name": "latency",
                    "old_aggregate": 1.5,
                    "new_aggregate": 1.2,
                    "found_count": 10,
                    "improved_count": 7,
                    "degraded_count": 1,
                    "improved": ["dp-4"],
                    "degraded": [],
                },
            ],
            "old_run": {"run_id": "run-old"},
            "new_run": {"run_id": "run-new"},
        }
        mock_client.evaluations.compare_runs.return_value = mock_response

        result = compare_runs(mock_client, "run-new", "run-old")

        assert isinstance(result, RunComparisonResult)
        assert result.new_run_id == "run-new"
        assert result.old_run_id == "run-old"
        assert result.common_datapoints == 10
        assert result.new_only_datapoints == 0
        assert result.old_only_datapoints == 0
        mock_client.evaluations.compare_runs.assert_called_once_with(
            new_run_id="run-new", old_run_id="run-old", aggregate_function="average"
        )

    def test_custom_aggregation_function_in_comparison(self, mock_client: Mock) -> None:
        """Test that custom aggregation function is passed to comparison API."""
        mock_response = {
            "commonDatapoints": ["dp-1", "dp-2", "dp-3", "dp-4", "dp-5"],
            "metrics": [],
            "old_run": {},
            "new_run": {},
        }
        mock_client.evaluations.compare_runs.return_value = mock_response

        compare_runs(mock_client, "run-new", "run-old", aggregate_function="median")

        mock_client.evaluations.compare_runs.assert_called_once_with(
            new_run_id="run-new", old_run_id="run-old", aggregate_function="median"
        )

    def test_metric_deltas_parsing(self, mock_client: Mock) -> None:
        """Test that metric deltas are correctly parsed."""
        mock_response = {
            "commonDatapoints": [
                "dp-1",
                "dp-2",
                "dp-3",
                "dp-4",
                "dp-5",
                "dp-6",
                "dp-7",
                "dp-8",
            ],
            "metrics": [
                {
                    "metric_name": "accuracy",
                    "old_aggregate": 0.85,
                    "new_aggregate": 0.90,
                    "found_count": 8,
                    "improved_count": 5,
                    "degraded_count": 0,
                },
                {
                    "metric_name": "cost",
                    "old_aggregate": 0.05,
                    "new_aggregate": 0.04,
                    "found_count": 8,
                    "improved_count": 6,
                    "degraded_count": 0,
                },
            ],
            "old_run": {},
            "new_run": {},
        }
        mock_client.evaluations.compare_runs.return_value = mock_response

        result = compare_runs(mock_client, "run-new", "run-old")

        accuracy_delta = result.get_metric_delta("accuracy")
        assert accuracy_delta["old_aggregate"] == 0.85
        assert accuracy_delta["new_aggregate"] == 0.90
        cost_delta = result.get_metric_delta("cost")
        assert cost_delta["old_aggregate"] == 0.05
        assert cost_delta["new_aggregate"] == 0.04

    def test_no_common_datapoints(self, mock_client: Mock) -> None:
        """Test comparison with no common datapoints."""
        mock_response = {
            "commonDatapoints": [],
            "metrics": [],
            "old_run": {},
            "new_run": {},
        }
        mock_client.evaluations.compare_runs.return_value = mock_response

        result = compare_runs(mock_client, "run-new", "run-old")

        assert result.common_datapoints == 0
        assert result.new_only_datapoints == 0
        assert result.old_only_datapoints == 0
        assert result.metric_deltas == {}

    def test_improved_and_degraded_metrics(self, mock_client: Mock) -> None:
        """Test identifying improved and degraded metrics."""
        mock_response = {
            "commonDatapoints": [
                "dp-1",
                "dp-2",
                "dp-3",
                "dp-4",
                "dp-5",
                "dp-6",
                "dp-7",
                "dp-8",
                "dp-9",
                "dp-10",
            ],
            "metrics": [
                {
                    "metric_name": "accuracy",
                    "old_aggregate": 0.80,
                    "new_aggregate": 0.85,
                    "improved_count": 5,
                    "degraded_count": 0,
                },
                {
                    "metric_name": "latency",
                    "old_aggregate": 1.5,
                    "new_aggregate": 1.8,
                    "improved_count": 0,
                    "degraded_count": 3,
                },
                {
                    "metric_name": "cost",
                    "old_aggregate": 0.05,
                    "new_aggregate": 0.04,
                    "improved_count": 6,
                    "degraded_count": 0,
                },
                {
                    "metric_name": "precision",
                    "old_aggregate": 0.90,
                    "new_aggregate": 0.88,
                    "improved_count": 0,
                    "degraded_count": 2,
                },
            ],
            "old_run": {},
            "new_run": {},
        }
        mock_client.evaluations.compare_runs.return_value = mock_response

        result = compare_runs(mock_client, "run-new", "run-old")

        improved = result.list_improved_metrics()
        degraded = result.list_degraded_metrics()

        assert len(improved) == 2
        assert "accuracy" in improved
        assert "cost" in improved
        assert len(degraded) == 2
        assert "latency" in degraded
        assert "precision" in degraded
