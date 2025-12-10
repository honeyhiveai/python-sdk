"""Result functions for experiments module.

This module provides functions to retrieve experiment results from backend endpoints.

CRITICAL: DO NOT compute aggregates client-side!
The backend already provides sophisticated aggregation endpoints that compute:
- Pass/fail determination
- Metric aggregations (average, sum, min, max)
- Composite metrics
- Run comparisons with deltas

Backend Endpoints:
- GET /runs/:run_id/result - Get aggregated result
- GET /runs/:run_id/metrics - Get raw metrics
- GET /runs/:new_run_id/compare-with/:old_run_id - Compare runs
"""

from typing import Any, Dict, List, cast

from honeyhive.experiments.models import (
    AggregatedMetrics,
    DatapointResult,
    ExperimentResultSummary,
    RunComparisonResult,
)


def get_run_result(
    client: Any, run_id: str, aggregate_function: str = "average"  # HoneyHive client
) -> ExperimentResultSummary:
    """
    Get aggregated experiment result from backend.

    Backend Endpoint: GET /runs/:run_id/result?aggregate_function=<function>

    The backend computes:
    - Pass/fail status for each datapoint
    - Metric aggregations (average, sum, min, max)
    - Composite metrics
    - Overall run status

    ❌ DO NOT compute these client-side!
    ✅ Use backend endpoint for all aggregations

    Args:
        client: HoneyHive API client
        run_id: Experiment run ID
        aggregate_function: Aggregation function ("average", "sum", "min", "max")

    Returns:
        ExperimentResultSummary with all aggregated metrics

    Raises:
        HTTPError: If backend request fails
        ValueError: If response format is invalid

    Examples:
        >>> from honeyhive import HoneyHive
        >>> client = HoneyHive(api_key="...")
        >>> result = get_run_result(client, "run-123", "average")
        >>> result.success
        True
        >>> result.metrics.get_metric("accuracy")
        {'aggregate': 0.85, 'values': [0.8, 0.9, 0.85]}
    """
    # Use existing API client method (will be added to evaluations.py)
    # For now, call directly
    response = client.evaluations.get_run_result(
        run_id=run_id, aggregate_function=aggregate_function
    )

    # Parse datapoints into DatapointResult objects
    raw_datapoints: List[Dict[str, Any]] = response.get("datapoints", [])
    datapoints: List[DatapointResult] = [DatapointResult(**dp) for dp in raw_datapoints]

    # Parse response into ExperimentResultSummary
    return ExperimentResultSummary(
        run_id=run_id,
        status=response.get("status", "unknown"),
        success=response.get("success", False),
        passed=response.get("passed", []),
        failed=response.get("failed", []),
        metrics=AggregatedMetrics(**response.get("metrics", {})),
        datapoints=datapoints,
    )


def get_run_metrics(client: Any, run_id: str) -> Dict[str, Any]:  # HoneyHive client
    """
    Get raw metrics for a run (without aggregation).

    Backend Endpoint: GET /runs/:run_id/metrics

    This returns raw metric data without aggregation, useful for:
    - Debugging individual datapoint metrics
    - Custom aggregation logic (if needed)
    - Detailed metric analysis

    Args:
        client: HoneyHive API client
        run_id: Experiment run ID

    Returns:
        Raw metrics data from backend

    Examples:
        >>> metrics = get_run_metrics(client, "run-123")
        >>> metrics["events"]
        [{'event_id': '...', 'metrics': {...}}, ...]
    """
    return cast(Dict[str, Any], client.evaluations.get_run_metrics(run_id=run_id))


def compare_runs(
    client: Any,  # HoneyHive client
    new_run_id: str,
    old_run_id: str,
    aggregate_function: str = "average",
) -> RunComparisonResult:
    """
    Compare two experiment runs using backend aggregated comparison.

    Backend Endpoint: GET /runs/:new_run_id/compare-with/:old_run_id

    The backend computes aggregated metrics for both runs and then compares them:
    - Common datapoints between runs (by datapoint_id)
    - Per-metric improved/degraded/same classification
    - Old and new aggregate values for each metric
    - Statistical aggregation (average, sum, min, max)

    ❌ DO NOT compute these client-side!
    ✅ Use backend endpoint for all comparisons

    Args:
        client: HoneyHive API client
        new_run_id: New experiment run ID
        old_run_id: Old experiment run ID
        aggregate_function: Aggregation function ("average", "sum", "min", "max")

    Returns:
        RunComparisonResult with delta calculations

    Examples:
        >>> comparison = compare_runs(client, "run-new", "run-old")
        >>> comparison.common_datapoints
        3
        >>> delta = comparison.get_metric_delta("accuracy")
        >>> delta
        {
            'old_aggregate': 0.80,
            'new_aggregate': 0.85,
            'found_count': 3,
            'improved_count': 1,
            'degraded_count': 0,
            'improved': ['EXT-abc123'],
            'degraded': []
        }
        >>> comparison.list_improved_metrics()
        ['accuracy', 'error_rate']
        >>> comparison.list_degraded_metrics()
        []
    """
    # Use aggregated comparison endpoint (NOT compare_run_events)
    # This endpoint returns the metric analysis we need
    response = client.evaluations.compare_runs(
        new_run_id=new_run_id,
        old_run_id=old_run_id,
        aggregate_function=aggregate_function,
    )

    # Parse commonDatapoints (list of IDs, not a count)
    common_datapoints_list = response.get("commonDatapoints", [])
    common_datapoints_count = len(common_datapoints_list)

    # Build metric_deltas from metrics array
    metric_deltas = {}
    for metric_data in response.get("metrics", []):
        metric_name = metric_data.get("metric_name")
        if metric_name:
            metric_deltas[metric_name] = {
                "old_aggregate": metric_data.get("old_aggregate"),
                "new_aggregate": metric_data.get("new_aggregate"),
                "found_count": metric_data.get("found_count", 0),
                "improved_count": metric_data.get("improved_count", 0),
                "degraded_count": metric_data.get("degraded_count", 0),
                "same_count": metric_data.get("same_count", 0),
                "improved": metric_data.get("improved", []),
                "degraded": metric_data.get("degraded", []),
                "same": metric_data.get("same", []),
                "old_values": metric_data.get("old_values", []),
                "new_values": metric_data.get("new_values", []),
            }

        # Extract new/old run data if needed (for future use)
        _old_run = response.get("old_run", {})
        _new_run = response.get("new_run", {})

    # Calculate new_only and old_only datapoints
    # (For now, we don't have this data from the backend response)
    new_only_count = 0
    old_only_count = 0

    return RunComparisonResult(
        new_run_id=new_run_id,
        old_run_id=old_run_id,
        common_datapoints=common_datapoints_count,
        new_only_datapoints=new_only_count,
        old_only_datapoints=old_only_count,
        metric_deltas=metric_deltas,
    )
