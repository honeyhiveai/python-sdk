"""Result functions for experiments module.

This module provides functions to retrieve experiment results from backend endpoints.

CRITICAL: DO NOT compute aggregates client-side!
The backend already provides sophisticated aggregation endpoints that compute:
- Pass/fail determination
- Metric aggregations (average, sum, min, max)
- Composite metrics
- Run comparisons with deltas

Backend Endpoints, with ``project_id`` and a data plane API key:
- GET /projects/:project_id/runs/:run_id/summary - Get aggregated result
- GET /projects/:project_id/runs/:new_run_id/compare/:old_run_id - Compare runs

Backend Endpoints, with the classic API key (deprecated):
- GET /runs/:run_id/result - Get aggregated result
- GET /runs/:new_run_id/compare-with/:old_run_id - Compare runs
"""

import warnings
from typing import Any, Dict, List, Optional, cast

from honeyhive.api.client import _warn_call_without_project_id
from honeyhive.experiments.models import (
    AggregatedMetrics,
    DatapointResult,
    ExperimentResultSummary,
    RunComparisonResult,
)

# Every value the project-scoped result and comparison operations accept for
# ``aggregate_function``. They refuse any other value, where the operations
# the project API key reaches use "average" instead. A unit test holds this
# equal to the enum the OpenAPI spec declares.
_SCOPED_AGGREGATE_FUNCTIONS = (
    "average",
    "min",
    "max",
    "median",
    "p90",
    "p95",
    "p99",
    "sum",
    "count",
)


def _resolve_project_id(
    client: Any, project_id: Optional[str], function: str
) -> Optional[str]:
    """The project a result function's request names, or None for the project key's.

    ``project_id`` is ignored only for a client that holds a project API key
    and no data plane API key. These functions accepted and ignored
    ``project_id`` before data plane keys existed, so that call keeps reading
    the project key's project rather than failing. A client with neither key
    gets ``project_id`` back, so its request is refused naming the data plane
    key, which is the key a caller who passes ``project_id`` is missing.

    Both warnings count this helper and the public function that calls it, so
    they land on the line that called that function.
    """
    if project_id is None:
        # _warn_call_without_project_id adds its own frame to the count.
        _warn_call_without_project_id("experiments", function, stacklevel=4)
        return None
    if not client.data_plane_api_key and client.api_key:
        warnings.warn(
            f"The 'project_id' argument to {function}() needs a data plane API "
            "key and is ignored without one, so this call uses the classic API "
            "key, which is deprecated and will stop working in v2.0. Configure "
            "a data plane API key with data_plane_api_key or the "
            "HH_DATA_PLANE_API_KEY environment variable.",
            DeprecationWarning,
            stacklevel=3,
        )
        return None
    return project_id


def _scoped_aggregate_function(aggregate_function: Optional[str]) -> Optional[str]:
    """The value a project-scoped request sends for ``aggregate_function``.

    A value the scoped operations refuse becomes "average", which is what the
    operations the project API key reaches do with it. The warning counts this
    helper, the private function that calls it, and the public function above
    that, so it lands on the line that called the public function.
    """
    if aggregate_function is None or aggregate_function in _SCOPED_AGGREGATE_FUNCTIONS:
        return aggregate_function
    warnings.warn(
        f"aggregate_function {aggregate_function!r} is not one of "
        f"{', '.join(_SCOPED_AGGREGATE_FUNCTIONS)}. Using 'average'.",
        UserWarning,
        stacklevel=4,
    )
    return "average"


def get_run_result(
    client: Any,  # HoneyHive client
    run_id: str,
    project_id: Optional[str] = None,
    aggregate_function: str = "average",
) -> ExperimentResultSummary:
    """
    Get aggregated experiment result from backend.

    The backend computes:
    - Pass/fail status for each datapoint
    - Metric aggregations (average, sum, min, max)
    - Composite metrics
    - Overall run status

    ❌ DO NOT compute these client-side!
    ✅ Use backend endpoint for all aggregations

    Accepted keys:
        Data plane fine-grained API key with ``project.experiment_run.get``,
        with ``project_id``; Classic API key without ``project_id``
        (deprecated)

    Args:
        client: HoneyHive API client
        run_id: Experiment run ID
        project_id: The project that holds the run. A client with a classic
            API key and no data plane API key ignores it and reads the classic
            key's project, which is deprecated.
        aggregate_function: Aggregation function: "average", "min", "max",
            "median", "p90", "p95", "p99", "sum" or "count". Any other value
            is treated as "average".

    Returns:
        ExperimentResultSummary with all aggregated metrics

    Raises:
        HTTPError: If backend request fails
        ValueError: If response format is invalid

    Examples:
        >>> from honeyhive import HoneyHive
        >>> client = HoneyHive(data_plane_api_key="...")
        >>> result = get_run_result(client, "run-123", "project-id", "average")
        >>> result.success
        True
        >>> result.metrics.get_metric("accuracy")
        {'aggregate': 0.85, 'values': [0.8, 0.9, 0.85]}
    """
    return _get_run_result(
        client,
        run_id,
        aggregate_function,
        project_id=_resolve_project_id(client, project_id, "get_run_result"),
    )


def _get_run_result(
    client: Any,
    run_id: str,
    aggregate_function: Optional[str] = "average",
    *,
    project_id: Optional[str],
) -> ExperimentResultSummary:
    """The request ``get_run_result()`` sends, and its parsed response.

    It never warns about a missing ``project_id``. ``project_id`` is None for
    the request the project API key sends.
    """
    if project_id is not None:
        aggregate_function = _scoped_aggregate_function(aggregate_function)
    response = client.experiments._get_result(
        run_id=run_id, aggregate_function=aggregate_function, project_id=project_id
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


def get_run_metrics(
    client: Any,
    run_id: str,
    project_id: Optional[str] = None,
) -> Dict[str, Any]:  # HoneyHive client
    """
    Get raw metrics for a run (without aggregation).

    This returns raw metric data without aggregation, useful for:
    - Debugging individual datapoint metrics
    - Custom aggregation logic (if needed)
    - Detailed metric analysis

    Accepted keys:
        Data plane fine-grained API key with ``project.experiment_run.get``,
        with ``project_id``; Classic API key without ``project_id``
        (deprecated)

    Args:
        client: HoneyHive API client
        run_id: Experiment run ID
        project_id: The project that holds the run. A client with a classic
            API key and no data plane API key ignores it and reads the classic
            key's project, which is deprecated.

    Returns:
        Raw metrics data from backend

    Examples:
        >>> metrics = get_run_metrics(client, "run-123", "project-id")
        >>> metrics["event_details"]
        [{'event_name': '...', 'event_type': '...'}, ...]
    """
    return cast(
        Dict[str, Any],
        client.experiments._get_result(
            run_id=run_id,
            project_id=_resolve_project_id(client, project_id, "get_run_metrics"),
        ),
    )


def compare_runs(
    client: Any,  # HoneyHive client
    new_run_id: str,
    old_run_id: str,
    project_id: Optional[str] = None,
    aggregate_function: str = "average",
) -> RunComparisonResult:
    """
    Compare two experiment runs using backend aggregated comparison.

    The backend computes aggregated metrics for both runs and then compares them:
    - Common datapoints between runs (by datapoint_id)
    - Per-metric improved/degraded/same classification
    - Old and new aggregate values for each metric
    - Statistical aggregation (average, sum, min, max)

    ❌ DO NOT compute these client-side!
    ✅ Use backend endpoint for all comparisons

    Accepted keys:
        Data plane fine-grained API key with ``project.experiment_run.get``,
        with ``project_id``; Classic API key without ``project_id``
        (deprecated)

    Args:
        client: HoneyHive API client
        new_run_id: New experiment run ID
        old_run_id: Old experiment run ID
        project_id: The project that holds both runs. A client with a
            classic API key and no data plane API key ignores it and compares
            runs in the classic key's project, which is deprecated.
        aggregate_function: Aggregation function: "average", "min", "max",
            "median", "p90", "p95", "p99", "sum" or "count". Any other value
            is treated as "average".

    Returns:
        RunComparisonResult with delta calculations

    Examples:
        >>> comparison = compare_runs(client, "run-new", "run-old", "project-id")
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
    return _compare_runs(
        client,
        new_run_id,
        old_run_id,
        aggregate_function,
        project_id=_resolve_project_id(client, project_id, "compare_runs"),
    )


def _compare_runs(
    client: Any,
    new_run_id: str,
    old_run_id: str,
    aggregate_function: Optional[str] = "average",
    *,
    project_id: Optional[str],
) -> RunComparisonResult:
    """The request ``compare_runs()`` sends, and its parsed response.

    It never warns about a missing ``project_id``. ``project_id`` is None for
    the request the project API key sends.
    """
    if project_id is not None:
        aggregate_function = _scoped_aggregate_function(aggregate_function)
    response = client.experiments._compare_runs(
        new_run_id=new_run_id,
        old_run_id=old_run_id,
        aggregate_function=aggregate_function,
        project_id=project_id,
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
