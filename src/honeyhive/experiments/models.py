"""Extended models for experiments module.

This module provides extended versions of generated models to fix known issues
and add experiment-specific functionality.

Models:
    - ExperimentRunStatus: Extended status enum with all backend values
    - AggregatedMetrics: Fixed metrics model with dynamic key support
    - ExperimentResultSummary: Aggregated experiment result from backend
    - RunComparisonResult: Comparison between two experiment runs
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


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


class AggregatedMetrics(BaseModel):
    """
    Aggregated metrics model for experiment results with dynamic metric keys.

    This is distinct from the generated 'Metrics' model which has incorrect structure.
    The backend returns dynamic keys for metric names, and this model handles them.

    Backend Response Format:
    {
      "aggregation_function": "average",
      "<metric_name>": {  # Dynamic keys for each metric!
        "metric_name": "accuracy",
        "metric_type": "numeric",
        "event_name": "llm_call",
        "event_type": "model",
        "aggregate": 0.85,
        "values": [0.8, 0.9, 0.85],
        "passing_range": [0.7, 1.0],
        "datapoints": {...}
      },
      "<another_metric>": {...}
    }

    Example:
        >>> metrics = AggregatedMetrics(
        ...     aggregation_function="average",
        ...     accuracy={"aggregate": 0.85, "values": [0.8, 0.9]}
        ... )
        >>> metrics.get_metric("accuracy")
        {'aggregate': 0.85, 'values': [0.8, 0.9]}
        >>> metrics.list_metrics()
        ['accuracy']
    """

    aggregation_function: Optional[str] = Field(
        None, description="Aggregation function used (average, sum, min, max)"
    )

    # Allow extra fields for dynamic metric keys
    model_config = ConfigDict(extra="allow")

    def get_metric(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific metric by name.

        Args:
            metric_name: Name of the metric to retrieve

        Returns:
            Metric data dictionary or None if not found

        Example:
            >>> metrics.get_metric("accuracy")
            {'aggregate': 0.85, 'values': [0.8, 0.9]}
        """
        return getattr(self, metric_name, None)

    def list_metrics(self) -> List[str]:
        """
        List all metric names in this result.

        Returns:
            List of metric names (excluding aggregation_function)

        Example:
            >>> metrics.list_metrics()
            ['accuracy', 'latency', 'cost']
        """
        extra = self.model_extra or {}
        return list(extra.keys())

    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics as a dictionary.

        Returns:
            Dictionary mapping metric names to metric data

        Example:
            >>> metrics.get_all_metrics()
            {
                'accuracy': {'aggregate': 0.85, ...},
                'latency': {'aggregate': 120.5, ...}
            }
        """
        extra = self.model_extra or {}
        return dict(extra)


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
        ..., description="Aggregated metrics with dynamic keys"
    )

    datapoints: List[Any] = Field(
        default_factory=list,
        description="List of datapoint results (Datapoint1 from generated)",
    )


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
