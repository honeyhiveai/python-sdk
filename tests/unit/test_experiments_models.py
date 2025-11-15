"""Unit tests for HoneyHive Experiments Models.

This module contains comprehensive unit tests for the experiments module's
Pydantic models, including ExperimentRunStatus enum, AggregatedMetrics,
ExperimentResultSummary, and RunComparisonResult.

Tests cover:
- Enum value validation and usage
- Pydantic model initialization with required/optional fields
- Extra fields handling via ConfigDict
- Helper method functionality (get_metric, list_metrics, etc.)
- Edge cases (empty metrics, None values, invalid types)
"""

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods
# pylint: disable=no-member,use-implicit-booleaness-not-comparison
# Justification: Comprehensive test coverage requires extensive test cases
# Justification: Testing private behavior and pytest fixture patterns
# Justification: Complete test class coverage for all model functionality
# Justification: Pydantic dynamic fields and explicit empty checks in tests

import re

from honeyhive.experiments.models import (
    AggregatedMetrics,
    ExperimentResultSummary,
    ExperimentRunStatus,
    RunComparisonResult,
)


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text for easier testing."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


class TestExperimentRunStatus:
    """Test suite for ExperimentRunStatus enum."""

    def test_enum_values_exist(self) -> None:
        """Test that all expected enum values are defined."""
        assert ExperimentRunStatus.PENDING == "pending"
        assert ExperimentRunStatus.COMPLETED == "completed"
        assert ExperimentRunStatus.RUNNING == "running"
        assert ExperimentRunStatus.FAILED == "failed"
        assert ExperimentRunStatus.CANCELLED == "cancelled"

    def test_enum_value_count(self) -> None:
        """Test that enum has exactly 5 values (no extras)."""
        assert len(list(ExperimentRunStatus)) == 5

    def test_enum_value_types(self) -> None:
        """Test that all enum values are strings."""
        for status in ExperimentRunStatus:
            assert isinstance(status.value, str)

    def test_enum_can_be_used_in_comparisons(self) -> None:
        """Test that enum values can be compared."""
        status1 = ExperimentRunStatus.PENDING
        status2 = ExperimentRunStatus.PENDING
        status3 = ExperimentRunStatus.COMPLETED

        assert status1 == status2
        assert status1 != status3


class TestAggregatedMetrics:
    """Test suite for AggregatedMetrics model."""

    def test_initialization_minimal(self) -> None:
        """Test AggregatedMetrics initialization with minimal fields."""
        metrics = AggregatedMetrics()

        assert metrics.aggregation_function is None

    def test_initialization_with_aggregation_function(self) -> None:
        """Test AggregatedMetrics with aggregation function."""
        metrics = AggregatedMetrics(aggregation_function="average")

        assert metrics.aggregation_function == "average"

    def test_initialization_with_extra_fields(self) -> None:
        """Test AggregatedMetrics accepts extra fields (ConfigDict)."""
        metrics = AggregatedMetrics(
            aggregation_function="average",
            accuracy={"aggregate": 0.85, "values": [0.8, 0.9]},
            latency={"aggregate": 1.2, "values": [1.0, 1.4]},
        )

        assert metrics.aggregation_function == "average"
        assert hasattr(metrics, "accuracy")
        assert hasattr(metrics, "latency")

    def test_get_metric_existing(self) -> None:
        """Test get_metric returns existing metric."""
        metrics = AggregatedMetrics(accuracy={"aggregate": 0.85, "values": [0.8, 0.9]})

        result = metrics.get_metric("accuracy")

        assert result == {"aggregate": 0.85, "values": [0.8, 0.9]}

    def test_get_metric_nonexistent(self) -> None:
        """Test get_metric returns None for non-existent metric."""
        metrics = AggregatedMetrics()

        result = metrics.get_metric("nonexistent")

        assert result is None

    def test_list_metrics_empty(self) -> None:
        """Test list_metrics returns empty list when no metrics."""
        metrics = AggregatedMetrics(aggregation_function="average")

        result = metrics.list_metrics()

        assert result == []

    def test_list_metrics_with_metrics(self) -> None:
        """Test list_metrics returns all metric names."""
        metrics = AggregatedMetrics(
            aggregation_function="average",
            accuracy={"aggregate": 0.85},
            latency={"aggregate": 1.2},
            cost={"aggregate": 0.05},
        )

        result = metrics.list_metrics()

        assert len(result) == 3
        assert "accuracy" in result
        assert "latency" in result
        assert "cost" in result
        assert "aggregation_function" not in result  # Should be excluded

    def test_get_all_metrics_empty(self) -> None:
        """Test get_all_metrics returns empty dict when no metrics."""
        metrics = AggregatedMetrics(aggregation_function="average")

        result = metrics.get_all_metrics()

        assert result == {}

    def test_get_all_metrics_with_metrics(self) -> None:
        """Test get_all_metrics returns all metrics as dict."""
        metrics = AggregatedMetrics(
            aggregation_function="average",
            accuracy={"aggregate": 0.85},
            latency={"aggregate": 1.2},
        )

        result = metrics.get_all_metrics()

        assert len(result) == 2
        assert result["accuracy"] == {"aggregate": 0.85}
        assert result["latency"] == {"aggregate": 1.2}
        assert "aggregation_function" not in result  # Should be excluded


class TestExperimentResultSummary:
    """Test suite for ExperimentResultSummary model."""

    def test_initialization_minimal(self) -> None:
        """Test ExperimentResultSummary with minimal required fields."""
        summary = ExperimentResultSummary(
            run_id="run-123",
            status="completed",  # String, not enum
            success=True,  # Required field
            metrics=AggregatedMetrics(),
        )

        assert summary.run_id == "run-123"
        assert summary.status == "completed"
        assert summary.success is True
        assert isinstance(summary.metrics, AggregatedMetrics)
        assert summary.passed == []  # Default empty list
        assert summary.failed == []  # Default empty list
        assert summary.datapoints == []

    def test_initialization_complete(self) -> None:
        """Test ExperimentResultSummary with all fields."""
        metrics = AggregatedMetrics(
            aggregation_function="average",
            accuracy={"aggregate": 0.85},
        )

        summary = ExperimentResultSummary(
            run_id="run-123",
            status="completed",
            success=True,
            passed=["dp-1", "dp-3"],  # List of strings, not int
            failed=["dp-2"],  # List of strings, not int
            metrics=metrics,
            datapoints=[
                {"id": "dp-1", "result": "pass"},
                {"id": "dp-2", "result": "fail"},
            ],
        )

        assert summary.run_id == "run-123"
        assert summary.status == "completed"
        assert summary.success is True
        assert summary.passed == ["dp-1", "dp-3"]
        assert summary.failed == ["dp-2"]
        assert summary.metrics.aggregation_function == "average"
        assert len(summary.datapoints) == 2

    def test_status_string_values(self) -> None:
        """Test that status field accepts string values."""
        for status_value in ["pending", "completed", "running", "failed", "cancelled"]:
            summary = ExperimentResultSummary(
                run_id="run-123",
                status=status_value,
                success=True,
                metrics=AggregatedMetrics(),
            )
            assert summary.status == status_value

    def test_print_table_runs_without_error(self, capsys) -> None:
        """Test that print_table executes without errors."""
        metrics = AggregatedMetrics(
            aggregation_function="average",
            accuracy={"aggregate": 0.85, "metric_type": "numeric"},
        )
        summary = ExperimentResultSummary(
            run_id="run-123",
            status="completed",
            success=True,
            passed=["dp-1"],
            failed=["dp-2"],
            metrics=metrics,
        )

        # Should not raise any exceptions
        summary.print_table()

        # Verify some output was produced (strip ANSI codes for clean assertions)
        captured = capsys.readouterr()
        clean_output = strip_ansi(captured.out)
        assert "run-123" in clean_output
        assert "Evaluation Results" in clean_output

    def test_print_table_with_run_name(self, capsys) -> None:
        """Test that print_table displays custom run name."""
        summary = ExperimentResultSummary(
            run_id="run-123",
            status="completed",
            success=True,
            metrics=AggregatedMetrics(),
        )

        summary.print_table(run_name="My Test Run")

        captured = capsys.readouterr()
        assert "My Test Run" in captured.out

    def test_print_table_displays_metrics(self, capsys) -> None:
        """Test that print_table displays aggregated metrics."""
        metrics = AggregatedMetrics(
            aggregation_function="average",
            accuracy={"aggregate": 0.85, "metric_type": "numeric"},
            latency={"aggregate": 120.5, "metric_type": "numeric"},
        )
        summary = ExperimentResultSummary(
            run_id="run-123",
            status="completed",
            success=True,
            metrics=metrics,
        )

        summary.print_table()

        captured = capsys.readouterr()
        assert "Aggregated Metrics" in captured.out
        assert "accuracy" in captured.out
        assert "0.8500" in captured.out
        assert "latency" in captured.out
        assert "120.5000" in captured.out

    def test_print_table_handles_empty_metrics(self, capsys) -> None:
        """Test that print_table handles empty metrics gracefully."""
        metrics = AggregatedMetrics(aggregation_function="average")
        summary = ExperimentResultSummary(
            run_id="run-123",
            status="completed",
            success=True,
            metrics=metrics,
        )

        # Should not raise any exceptions
        summary.print_table()

        captured = capsys.readouterr()
        clean_output = strip_ansi(captured.out)
        # Should not show metrics table if no metrics
        assert "run-123" in clean_output

    def test_print_table_displays_success_status(self, capsys) -> None:
        """Test that print_table displays success status with emoji."""
        summary = ExperimentResultSummary(
            run_id="run-123",
            status="completed",
            success=True,
            metrics=AggregatedMetrics(),
        )

        summary.print_table()

        captured = capsys.readouterr()
        assert "✅" in captured.out
        assert "completed" in captured.out

    def test_print_table_displays_failure_status(self, capsys) -> None:
        """Test that print_table displays failure status with emoji."""
        summary = ExperimentResultSummary(
            run_id="run-123",
            status="failed",
            success=False,
            metrics=AggregatedMetrics(),
        )

        summary.print_table()

        captured = capsys.readouterr()
        assert "❌" in captured.out
        assert "failed" in captured.out

    def test_print_table_displays_pass_fail_counts(self, capsys) -> None:
        """Test that print_table displays pass/fail counts."""
        summary = ExperimentResultSummary(
            run_id="run-123",
            status="completed",
            success=True,
            passed=["dp-1", "dp-2", "dp-3"],
            failed=["dp-4"],
            metrics=AggregatedMetrics(),
        )

        summary.print_table()

        captured = capsys.readouterr()
        clean_output = strip_ansi(captured.out)
        assert "Passed: 3" in clean_output
        assert "Failed: 1" in clean_output


class TestRunComparisonResult:
    """Test suite for RunComparisonResult model."""

    def test_initialization_minimal(self) -> None:
        """Test RunComparisonResult with minimal required fields."""
        comparison = RunComparisonResult(
            new_run_id="run-new",
            old_run_id="run-old",
            common_datapoints=10,  # Required field
        )

        assert comparison.new_run_id == "run-new"
        assert comparison.old_run_id == "run-old"
        assert comparison.common_datapoints == 10
        assert comparison.new_only_datapoints == 0  # Default
        assert comparison.old_only_datapoints == 0  # Default
        assert comparison.metric_deltas == {}  # Default

    def test_initialization_complete(self) -> None:
        """Test RunComparisonResult with all fields."""
        comparison = RunComparisonResult(
            new_run_id="run-new",
            old_run_id="run-old",
            common_datapoints=8,
            new_only_datapoints=2,  # Correct field name
            old_only_datapoints=1,  # Correct field name
            metric_deltas={
                "accuracy": {
                    "new_value": 0.85,
                    "old_value": 0.80,
                    "delta": 0.05,
                    "percent_change": 6.25,
                },
                "latency": {
                    "new_value": 1.2,
                    "old_value": 1.5,
                    "delta": -0.3,
                    "percent_change": -20.0,
                },
            },
        )

        assert comparison.new_run_id == "run-new"
        assert comparison.old_run_id == "run-old"
        assert comparison.common_datapoints == 8
        assert comparison.new_only_datapoints == 2
        assert comparison.old_only_datapoints == 1
        assert len(comparison.metric_deltas) == 2

    def test_get_metric_delta_existing(self) -> None:
        """Test get_metric_delta returns existing delta."""
        comparison = RunComparisonResult(
            new_run_id="run-new",
            old_run_id="run-old",
            common_datapoints=10,
            metric_deltas={
                "accuracy": {
                    "new_value": 0.85,
                    "old_value": 0.80,
                    "delta": 0.05,
                }
            },
        )

        result = comparison.get_metric_delta("accuracy")

        assert result == {
            "new_value": 0.85,
            "old_value": 0.80,
            "delta": 0.05,
        }

    def test_get_metric_delta_nonexistent(self) -> None:
        """Test get_metric_delta returns None for non-existent metric."""
        comparison = RunComparisonResult(
            new_run_id="run-new",
            old_run_id="run-old",
            common_datapoints=10,
            metric_deltas={},
        )

        result = comparison.get_metric_delta("nonexistent")

        assert result is None

    def test_list_improved_metrics_empty(self) -> None:
        """Test list_improved_metrics returns empty list when no improvements."""
        comparison = RunComparisonResult(
            new_run_id="run-new",
            old_run_id="run-old",
            common_datapoints=10,
            metric_deltas={
                "accuracy": {"delta": -0.05},  # Degraded
                "latency": {"delta": 0.0},  # No change
            },
        )

        result = comparison.list_improved_metrics()

        assert result == []

    def test_list_improved_metrics_with_improvements(self) -> None:
        """Test list_improved_metrics returns metrics with improved_count > 0."""
        comparison = RunComparisonResult(
            new_run_id="run-new",
            old_run_id="run-old",
            common_datapoints=10,
            metric_deltas={
                "accuracy": {"improved_count": 5, "degraded_count": 0},  # Improved
                "latency": {"improved_count": 0, "degraded_count": 3},  # Degraded
                "cost": {"improved_count": 2, "degraded_count": 0},  # Improved
            },
        )

        result = comparison.list_improved_metrics()

        assert len(result) == 2
        assert "accuracy" in result
        assert "cost" in result
        assert "latency" not in result

    def test_list_degraded_metrics_empty(self) -> None:
        """Test list_degraded_metrics returns empty list when no degradations."""
        comparison = RunComparisonResult(
            new_run_id="run-new",
            old_run_id="run-old",
            common_datapoints=10,
            metric_deltas={
                "accuracy": {"delta": 0.05},  # Improved
                "latency": {"delta": 0.0},  # No change
            },
        )

        result = comparison.list_degraded_metrics()

        assert result == []

    def test_list_degraded_metrics_with_degradations(self) -> None:
        """Test list_degraded_metrics returns metrics with degraded_count > 0."""
        comparison = RunComparisonResult(
            new_run_id="run-new",
            old_run_id="run-old",
            common_datapoints=10,
            metric_deltas={
                "accuracy": {"improved_count": 5, "degraded_count": 0},  # Improved
                "latency": {"improved_count": 0, "degraded_count": 3},  # Degraded
                "cost": {"improved_count": 0, "degraded_count": 1},  # Degraded
            },
        )

        result = comparison.list_degraded_metrics()

        assert len(result) == 2
        assert "latency" in result
        assert "cost" in result
        assert "accuracy" not in result

    def test_list_improved_metrics_handles_non_dict_values(self) -> None:
        """Test list_improved_metrics handles non-dict metric values."""
        comparison = RunComparisonResult(
            new_run_id="run-new",
            old_run_id="run-old",
            common_datapoints=10,
            metric_deltas={
                "accuracy": {"improved_count": 5},  # Valid dict
                "invalid": "not-a-dict",  # Invalid type
            },
        )

        result = comparison.list_improved_metrics()

        # Should only include valid dict entries with improved_count > 0
        assert result == ["accuracy"]

    def test_list_degraded_metrics_handles_missing_delta(self) -> None:
        """Test list_degraded_metrics handles missing degraded_count field."""
        comparison = RunComparisonResult(
            new_run_id="run-new",
            old_run_id="run-old",
            common_datapoints=10,
            metric_deltas={
                "accuracy": {"new_value": 0.85},  # Missing degraded_count
                "latency": {"degraded_count": 3},  # Has degraded_count
            },
        )

        result = comparison.list_degraded_metrics()

        # Should only include entries with explicit degraded_count > 0
        assert result == ["latency"]
