"""Extended models for experiments module.

This module provides extended versions of generated models to fix known issues
and add experiment-specific functionality.

Models:
    - ExperimentRunStatus: Extended status enum with all backend values
    - MetricDetail: Individual metric data from backend
    - DatapointResult: Individual datapoint result from backend
    - DatapointMetric: Individual metric for a datapoint
    - AggregatedMetrics: Aggregated metrics model with details array support
    - ExperimentResultSummary: Aggregated experiment result from backend
    - RunComparisonResult: Comparison between two experiment runs
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field
from rich.console import Console
from rich.style import Style
from rich.table import Table


class ExperimentRunStatus(str, Enum):
    """
    Extended status enum with all backend values.

    The generated Status enum only includes 'pending' and 'completed',
    but the backend supports additional states.
    """

    PENDING = "pending"
    COMPLETED = "completed"
    RUNNING = "running"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MetricDatapoints(BaseModel):
    """Pass/fail datapoint IDs for a metric."""

    passed: List[str] = Field(
        default_factory=list, description="Datapoint IDs that passed"
    )
    failed: List[str] = Field(
        default_factory=list, description="Datapoint IDs that failed"
    )


class MetricDetail(BaseModel):
    """
    Individual metric data from backend.

    This represents a single metric in the metrics.details array returned by
    GET /runs/:run_id/result endpoint.

    Backend Response Format (per OpenAPI spec):
    {
        "metric_name": "accuracy",
        "metric_type": "numeric",
        "event_name": "llm_call",
        "event_type": "model",
        "aggregate": 0.85,
        "values": [0.8, 0.9, 0.85],
        "datapoints": {
            "passed": ["dp-1", "dp-2"],
            "failed": ["dp-3"]
        }
    }
    """

    metric_name: str = Field(..., description="Name of the metric")
    metric_type: Optional[str] = Field(
        None, description="Type of metric (numeric, boolean)"
    )
    event_name: Optional[str] = Field(
        None, description="Name of the event this metric is from"
    )
    event_type: Optional[str] = Field(
        None, description="Type of event (model, chain, etc)"
    )
    aggregate: Optional[Union[float, int, bool]] = Field(
        None, description="Aggregated value for this metric"
    )
    values: List[Union[float, int, bool]] = Field(
        default_factory=list, description="Individual values for each datapoint"
    )
    datapoints: Optional[MetricDatapoints] = Field(
        None, description="Pass/fail datapoint IDs for this metric"
    )


class DatapointMetric(BaseModel):
    """
    Individual metric for a datapoint.

    This represents a single metric in the datapoint.metrics array returned by
    GET /runs/:run_id/result endpoint.
    """

    name: str = Field(..., description="Name of the metric")
    event_name: Optional[str] = Field(
        None, description="Name of the event this metric is from"
    )
    event_type: Optional[str] = Field(None, description="Type of event")
    value: Optional[Union[float, int, bool]] = Field(
        None, description="Value of the metric"
    )
    passed: Optional[bool] = Field(None, description="Whether this metric passed")


class DatapointResult(BaseModel):
    """
    Individual datapoint result from backend.

    This represents a single datapoint in the datapoints array returned by
    GET /runs/:run_id/result endpoint.

    Backend Response Format (per OpenAPI spec):
    {
        "datapoint_id": "dp-123",
        "session_id": "sess-456",
        "passed": true,
        "metrics": [
            {"name": "accuracy", "value": 0.85, "passed": true},
            ...
        ]
    }
    """

    datapoint_id: Optional[str] = Field(None, description="ID of the datapoint")
    session_id: Optional[str] = Field(None, description="ID of the session")
    passed: Optional[bool] = Field(None, description="Whether this datapoint passed")
    metrics: List[DatapointMetric] = Field(
        default_factory=list, description="Metrics for this datapoint"
    )

    model_config = ConfigDict(extra="allow")


class AggregatedMetrics(BaseModel):
    """
    Aggregated metrics model for experiment results.

    Supports the backend response format with a 'details' array containing
    MetricDetail objects.

    Backend Response Format (per OpenAPI spec):
    {
      "aggregation_function": "average",
      "details": [
        {
          "metric_name": "accuracy",
          "metric_type": "numeric",
          "event_name": "llm_call",
          "event_type": "model",
          "aggregate": 0.85,
          "values": [0.8, 0.9, 0.85],
          "datapoints": {"passed": [...], "failed": [...]}
        },
        ...
      ]
    }

    Example:
        >>> metrics = AggregatedMetrics(
        ...     aggregation_function="average",
        ...     details=[{"metric_name": "accuracy", "aggregate": 0.85}]
        ... )
        >>> metrics.get_metric("accuracy")
        MetricDetail(metric_name='accuracy', aggregate=0.85, ...)
        >>> metrics.list_metrics()
        ['accuracy']
    """

    aggregation_function: Optional[str] = Field(
        None, description="Aggregation function used (average, sum, min, max)"
    )

    details: List[MetricDetail] = Field(
        default_factory=list,
        description="List of metric details from backend",
    )

    # Allow extra fields for backward compatibility with dynamic metric keys
    model_config = ConfigDict(extra="allow")

    def get_metric(
        self, metric_name: str
    ) -> Optional[Union[MetricDetail, Dict[str, Any]]]:
        """
        Get a specific metric by name.

        Supports both the new 'details' array format (returns MetricDetail)
        and the legacy model_extra format (returns dict) for backward compatibility.

        Args:
            metric_name: Name of the metric to retrieve

        Returns:
            MetricDetail object (new format), dict (legacy format), or None if not found

        Example:
            >>> metrics.get_metric("accuracy")
            MetricDetail(metric_name='accuracy', aggregate=0.85, ...)
        """
        # First check the details array (new format)
        for metric in self.details:
            if metric.metric_name == metric_name:
                return metric
        # Fall back to model_extra (legacy format for backward compatibility)
        extra = self.model_extra or {}
        return extra.get(metric_name)

    def list_metrics(self) -> List[str]:
        """
        List all metric names in this result.

        Supports both the new 'details' array format and the legacy model_extra
        format for backward compatibility.

        Returns:
            List of metric names from details array or model_extra keys

        Example:
            >>> metrics.list_metrics()
            ['accuracy', 'latency', 'cost']
        """
        # First check the details array (new format)
        if self.details:
            # pylint: disable=not-an-iterable
            return [metric.metric_name for metric in self.details]
        # Fall back to model_extra (legacy format for backward compatibility)
        extra = self.model_extra or {}
        # Exclude known fields that aren't metrics
        return [k for k in extra.keys() if k not in ("aggregation_function",)]

    def get_all_metrics(self) -> Dict[str, Union[MetricDetail, Dict[str, Any]]]:
        """
        Get all metrics as a dictionary.

        Supports both the new 'details' array format (returns MetricDetail values)
        and the legacy model_extra format (returns dict values) for backward
        compatibility.

        Returns:
            Dictionary mapping metric names to MetricDetail objects or dicts

        Example:
            >>> metrics.get_all_metrics()
            {
                'accuracy': MetricDetail(metric_name='accuracy', aggregate=0.85, ...),
                'latency': MetricDetail(metric_name='latency', aggregate=120.5, ...)
            }
        """
        # First check the details array (new format)
        if self.details:
            # pylint: disable=not-an-iterable
            return {metric.metric_name: metric for metric in self.details}
        # Fall back to model_extra (legacy format for backward compatibility)
        extra = self.model_extra or {}
        # Exclude known fields that aren't metrics
        return {k: v for k, v in extra.items() if k not in ("aggregation_function",)}


class ExperimentResultSummary(BaseModel):
    """
    Aggregated experiment result from backend.

    This model represents the complete result of an experiment run,
    including pass/fail status, aggregated metrics, and datapoint results.

    Retrieved from: GET /runs/:run_id/result
    """

    run_id: str = Field(..., description="Experiment run identifier")

    status: str = Field(
        ..., description="Run status (pending, completed, running, failed, cancelled)"
    )

    success: bool = Field(..., description="Overall success status of the run")

    passed: List[str] = Field(
        default_factory=list, description="List of datapoint IDs that passed"
    )

    failed: List[str] = Field(
        default_factory=list, description="List of datapoint IDs that failed"
    )

    metrics: AggregatedMetrics = Field(
        ..., description="Aggregated metrics from backend"
    )

    datapoints: List[DatapointResult] = Field(
        default_factory=list,
        description="List of datapoint results from backend",
    )

    def print_table(self, run_name: Optional[str] = None) -> None:
        """
        Print evaluation results in a formatted table.

        Displays:
        - Run summary (ID, status, pass/fail counts)
        - Aggregated metrics
        - Per-datapoint details (if available)

        Args:
            run_name: Optional run name to display in table title

        Example:
            >>> result = evaluate(...)
            >>> result.print_table(run_name="My Experiment")
        """
        console = Console()

        # Print header
        title = f"Evaluation Results: {run_name or self.run_id}"
        console.print(f"\n{'=' * 80}")
        console.print(f"[bold yellow]{title}[/bold yellow]")
        console.print(f"{'=' * 80}\n")

        # Print summary
        status_emoji = "✅" if self.success else "❌"
        status_color = "green" if self.success else "red"

        console.print(f"[bold]Run ID:[/bold] {self.run_id}")
        status_text = (
            f"[bold]Status:[/bold] [{status_color}]"
            f"{status_emoji} {self.status}[/{status_color}]"
        )
        console.print(status_text)
        console.print(f"[bold]Passed:[/bold] {len(self.passed)}")
        console.print(f"[bold]Failed:[/bold] {len(self.failed)}")
        console.print()

        # Print aggregated metrics table
        metric_names = self.metrics.list_metrics()  # pylint: disable=no-member

        if metric_names:
            metrics_table = Table(
                title="Aggregated Metrics",
                show_lines=False,
                title_style=Style(color="cyan", bold=True),
            )
            metrics_table.add_column(
                "Metric", justify="left", style="magenta", no_wrap=True
            )
            metrics_table.add_column("Value", justify="right", style="green")
            metrics_table.add_column("Type", justify="center", style="blue")

            for metric_name in sorted(metric_names):
                # pylint: disable=no-member
                metric_data = self.metrics.get_metric(metric_name)
                if metric_data is not None:
                    # Handle both MetricDetail objects (new format) and dicts (legacy)
                    if isinstance(metric_data, MetricDetail):
                        aggregate_value = metric_data.aggregate
                        metric_type = metric_data.metric_type or "unknown"
                    elif isinstance(metric_data, dict):
                        aggregate_value = metric_data.get("aggregate")
                        metric_type = metric_data.get("metric_type", "unknown")
                    else:
                        aggregate_value = None
                        metric_type = "unknown"

                    # Format value based on type
                    if aggregate_value is None:
                        value_str = "N/A"
                    elif isinstance(aggregate_value, float):
                        value_str = f"{aggregate_value:.4f}"
                    else:
                        value_str = str(aggregate_value)

                    metrics_table.add_row(metric_name, value_str, metric_type)

            console.print(metrics_table)
            console.print()

        # Print per-datapoint summary if available
        if self.datapoints:
            datapoints_table = Table(
                title=f"Datapoint Results ({len(self.datapoints)} total)",
                show_lines=False,
                title_style=Style(color="cyan", bold=True),
            )
            datapoints_table.add_column(
                "Datapoint ID", justify="left", style="blue", no_wrap=False
            )
            datapoints_table.add_column(
                "Session ID", justify="left", style="blue", no_wrap=False
            )
            datapoints_table.add_column("Status", justify="center", style="green")

            for datapoint in self.datapoints[:20]:  # Limit to first 20 for display
                dp_id = datapoint.datapoint_id or "N/A"
                session_id = datapoint.session_id or "N/A"
                passed = datapoint.passed

                if passed is True:
                    status = "[green]✅ Passed[/green]"
                elif passed is False:
                    status = "[red]❌ Failed[/red]"
                else:
                    status = "❓ Unknown"

                datapoints_table.add_row(dp_id, session_id, status)

            console.print(datapoints_table)

            if len(self.datapoints) > 20:
                msg = (
                    f"\n[dim](Showing first 20 of "
                    f"{len(self.datapoints)} datapoints)[/dim]"
                )
                console.print(msg)

            console.print()

        console.print(f"{'=' * 80}\n")


class RunComparisonResult(BaseModel):
    """
    Comparison between two experiment runs.

    This model represents the delta analysis between a new run and an old run,
    including metric changes and datapoint differences.

    Retrieved from: GET /runs/:new_run_id/compare-with/:old_run_id
    """

    new_run_id: str = Field(..., description="New experiment run identifier")

    old_run_id: str = Field(..., description="Old experiment run identifier")

    common_datapoints: int = Field(
        ..., description="Number of datapoints common to both runs"
    )

    new_only_datapoints: int = Field(
        default=0, description="Number of datapoints only in new run"
    )

    old_only_datapoints: int = Field(
        default=0, description="Number of datapoints only in old run"
    )

    metric_deltas: Dict[str, Any] = Field(
        default_factory=dict, description="Metric name to delta information mapping"
    )

    def get_metric_delta(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """
        Get delta information for a specific metric.

        Args:
            metric_name: Name of the metric

        Returns:
            Delta information including new_value, old_value, delta, percent_change

        Example:
            >>> comparison.get_metric_delta("accuracy")
            {
                'new_value': 0.85,
                'old_value': 0.80,
                'delta': 0.05,
                'percent_change': 6.25
            }
        """
        return self.metric_deltas.get(metric_name)  # pylint: disable=no-member

    def list_improved_metrics(self) -> List[str]:
        """
        List metrics that improved in the new run.

        Returns:
            List of metric names where improved_count > 0
        """
        improved = []
        for (
            metric_name,
            delta_info,
        ) in self.metric_deltas.items():  # pylint: disable=no-member
            if isinstance(delta_info, dict) and delta_info.get("improved_count", 0) > 0:
                improved.append(metric_name)
        return improved

    def list_degraded_metrics(self) -> List[str]:
        """
        List metrics that degraded in the new run.

        Returns:
            List of metric names where degraded_count > 0
        """
        degraded = []
        for (
            metric_name,
            delta_info,
        ) in self.metric_deltas.items():  # pylint: disable=no-member
            if isinstance(delta_info, dict) and delta_info.get("degraded_count", 0) > 0:
                degraded.append(metric_name)
        return degraded
