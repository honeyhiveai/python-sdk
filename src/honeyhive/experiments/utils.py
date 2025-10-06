"""Utility functions for experiments module.

This module provides utility functions for:
- External dataset ID generation with EXT- prefix
- External datapoint ID generation
- Run request data preparation with EXT- transformation
"""

import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple


def generate_external_dataset_id(
    datapoints: List[Dict[str, Any]], custom_id: Optional[str] = None
) -> str:
    """
    Generate EXT- prefixed dataset ID for external datasets.

    External datasets are managed by the user (not stored in HoneyHive).
    They require an EXT- prefix to distinguish them from HoneyHive datasets.

    Args:
        datapoints: List of datapoint dictionaries
        custom_id: Optional custom ID (will be prefixed with EXT-)

    Returns:
        Dataset ID with EXT- prefix

    Examples:
        >>> datapoints = [{"inputs": {"query": "test"}}]
        >>> generate_external_dataset_id(datapoints)
        'EXT-a1b2c3d4e5f6'

        >>> generate_external_dataset_id(datapoints, custom_id="my-dataset")
        'EXT-my-dataset'
    """
    if custom_id:
        # Ensure custom ID has EXT- prefix
        if not custom_id.startswith("EXT-"):
            return f"EXT-{custom_id}"
        return custom_id

    # Generate hash-based ID for deterministic identification
    content = json.dumps(datapoints, sort_keys=True)
    hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
    return f"EXT-{hash_value}"


def generate_external_datapoint_id(
    datapoint: Dict[str, Any], index: int, custom_id: Optional[str] = None
) -> str:
    """
    Generate EXT- prefixed datapoint ID for external datapoints.

    Args:
        datapoint: Datapoint dictionary
        index: Index in dataset (for stable ordering)
        custom_id: Optional custom ID (will be prefixed with EXT-)

    Returns:
        Datapoint ID with EXT- prefix

    Examples:
        >>> datapoint = {"inputs": {"query": "test"}}
        >>> generate_external_datapoint_id(datapoint, 0)
        'EXT-f1e2d3c4b5a6'

        >>> generate_external_datapoint_id(datapoint, 0, custom_id="dp-1")
        'EXT-dp-1'
    """
    if custom_id:
        if not custom_id.startswith("EXT-"):
            return f"EXT-{custom_id}"
        return custom_id

    # Generate hash-based ID with index for uniqueness
    content = json.dumps(datapoint, sort_keys=True)
    hash_value = hashlib.sha256(f"{content}{index}".encode()).hexdigest()[:16]
    return f"EXT-{hash_value}"


def prepare_external_dataset(
    datapoints: List[Dict[str, Any]], custom_dataset_id: Optional[str] = None
) -> Tuple[str, List[str]]:
    """
    Prepare external dataset with EXT- IDs.

    This function generates a dataset ID and datapoint IDs for an external
    dataset, ensuring all IDs have the EXT- prefix.

    Args:
        datapoints: List of datapoint dictionaries
        custom_dataset_id: Optional custom dataset ID

    Returns:
        Tuple of (dataset_id, datapoint_ids)

    Examples:
        >>> datapoints = [
        ...     {"inputs": {"query": "test1"}},
        ...     {"inputs": {"query": "test2"}}
        ... ]
        >>> dataset_id, datapoint_ids = prepare_external_dataset(datapoints)
        >>> dataset_id.startswith("EXT-")
        True
        >>> all(dp_id.startswith("EXT-") for dp_id in datapoint_ids)
        True
    """
    # Generate dataset ID
    dataset_id = generate_external_dataset_id(datapoints, custom_dataset_id)

    # Generate datapoint IDs
    datapoint_ids = []
    for idx, dp in enumerate(datapoints):
        # Check if datapoint already has an ID
        custom_dp_id = dp.get("id") or dp.get("datapoint_id")
        dp_id = generate_external_datapoint_id(dp, idx, custom_dp_id)
        datapoint_ids.append(dp_id)

    return dataset_id, datapoint_ids


def prepare_run_request_data(  # pylint: disable=unused-argument
    run_id: str,
    name: str,
    project: str,
    *,
    dataset_id: Optional[str],
    event_ids: Optional[List[str]] = None,
    datapoint_ids: Optional[List[str]] = None,
    configuration: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    results: Optional[Dict[str, Any]] = None,
    status: str = "pending",
) -> Dict[str, Any]:
    """
    Prepare run request data with EXT- transformation.

    CRITICAL: Backend requires special handling for external datasets:
    - If dataset_id starts with "EXT-":
      - Move to metadata.offline_dataset_id
      - Set dataset_id = None (prevents FK constraint error)
    - Otherwise, use dataset_id normally

    Backend Logic (from backend_service/app/services/experiment_run.service.ts):
    ```typescript
    if (dataset_id && dataset_id.startsWith('EXT-')) {
        metadata = { ...metadata, offline_dataset_id: dataset_id };
        dataset_id = undefined; // Avoid FK constraint
    }
    ```

    Args:
        run_id: Experiment run identifier
        name: Run name
        project: Project identifier
        dataset_id: Dataset identifier (may have EXT- prefix)
        event_ids: List of event/session IDs (optional)
        configuration: Run configuration (optional)
        metadata: Additional metadata (optional)
        description: Run description (optional)
        results: Run results (optional)
        status: Run status (default: "pending")

    Returns:
        Request data dictionary ready for backend API

    Examples:
        >>> # External dataset
        >>> data = prepare_run_request_data(
        ...     run_id="run-123",
        ...     name="My Experiment",
        ...     project="proj-456",
        ...     dataset_id="EXT-abc123"
        ... )
        >>> data["dataset_id"]  # None (moved to metadata)
        >>> data["metadata"]["offline_dataset_id"]
        'EXT-abc123'

        >>> # HoneyHive dataset
        >>> data = prepare_run_request_data(
        ...     run_id="run-123",
        ...     name="My Experiment",
        ...     project="proj-456",
        ...     dataset_id="ds-789"
        ... )
        >>> data["dataset_id"]
        'ds-789'
    """
    # Initialize request data
    request_data: Dict[str, Any] = {
        "project": project,
        "name": name,
        "event_ids": event_ids or [],
        "datapoint_ids": datapoint_ids or [],
        "configuration": configuration or {},
        "metadata": metadata or {},
        "status": status,
    }

    # Add optional fields if provided
    if description:
        request_data["description"] = description
    if results:
        request_data["results"] = results

    # Handle EXT- prefix transformation
    if dataset_id and dataset_id.startswith("EXT-"):
        # Store external dataset ID in metadata
        request_data["metadata"]["offline_dataset_id"] = dataset_id
        # Clear dataset_id to avoid FK constraint
        request_data["dataset_id"] = None
    else:
        request_data["dataset_id"] = dataset_id

    return request_data
