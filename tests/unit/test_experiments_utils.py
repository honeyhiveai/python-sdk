"""Unit tests for HoneyHive Experiments Utilities.

This module contains comprehensive unit tests for the experiments module's
utility functions, focusing on EXT- prefix generation, dataset preparation,
and request data transformation.

Tests cover:
- Deterministic ID generation with SHA256 hashing
- Custom ID override logic
- External dataset preparation and ID assignment
- Critical EXT- prefix transformation for backend compatibility
- Edge cases (empty datasets, missing fields, None values)
"""

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods
# pylint: disable=unused-variable,use-implicit-booleaness-not-comparison
# Justification: Comprehensive test coverage requires extensive test cases
# Justification: Testing private behavior and pytest fixture patterns
# Justification: Complete test class coverage for all utility functions
# Justification: Some variables extracted for clarity, explicit empty checks in tests

from typing import Any, Dict, List

from honeyhive.experiments.utils import (
    generate_external_datapoint_id,
    generate_external_dataset_id,
    prepare_external_dataset,
    prepare_run_request_data,
)


class TestGenerateExternalDatasetId:
    """Test suite for generate_external_dataset_id function."""

    def test_generates_ext_prefix(self) -> None:
        """Test that generated ID starts with EXT- prefix."""
        datapoints = [
            {"inputs": {"text": "hello"}, "ground_truth": {"label": "greeting"}}
        ]

        result = generate_external_dataset_id(datapoints)

        assert result.startswith("EXT-")

    def test_deterministic_same_input(self) -> None:
        """Test that same input generates same ID (deterministic hashing)."""
        datapoints = [
            {"inputs": {"text": "hello"}, "ground_truth": {"label": "greeting"}},
            {"inputs": {"text": "goodbye"}, "ground_truth": {"label": "farewell"}},
        ]

        id1 = generate_external_dataset_id(datapoints)
        id2 = generate_external_dataset_id(datapoints)

        assert id1 == id2

    def test_different_inputs_generate_different_ids(self) -> None:
        """Test that different inputs generate different IDs."""
        datapoints1 = [{"inputs": {"text": "hello"}}]
        datapoints2 = [{"inputs": {"text": "goodbye"}}]

        id1 = generate_external_dataset_id(datapoints1)
        id2 = generate_external_dataset_id(datapoints2)

        assert id1 != id2

    def test_custom_id_override(self) -> None:
        """Test that custom_id parameter overrides generation."""
        datapoints = [{"inputs": {"text": "hello"}}]
        custom_id = "my-custom-dataset"

        result = generate_external_dataset_id(datapoints, custom_id=custom_id)

        assert result == "EXT-my-custom-dataset"

    def test_custom_id_adds_prefix_if_missing(self) -> None:
        """Test that EXT- prefix is added to custom ID if not present."""
        datapoints = [{"inputs": {"text": "hello"}}]
        custom_id = "my-dataset"  # No EXT- prefix

        result = generate_external_dataset_id(datapoints, custom_id=custom_id)

        assert result == "EXT-my-dataset"

    def test_custom_id_preserves_existing_prefix(self) -> None:
        """Test that existing EXT- prefix in custom ID is not duplicated."""
        datapoints = [{"inputs": {"text": "hello"}}]
        custom_id = "EXT-my-dataset"  # Already has prefix

        result = generate_external_dataset_id(datapoints, custom_id=custom_id)

        assert result == "EXT-my-dataset"
        assert result.count("EXT-") == 1  # Not duplicated

    def test_empty_datapoints_list(self) -> None:
        """Test behavior with empty datapoints list."""
        datapoints: List[Dict[str, Any]] = []

        result = generate_external_dataset_id(datapoints)

        assert result.startswith("EXT-")
        # Should still generate a valid ID (hash of empty list)

    def test_order_matters_for_hash(self) -> None:
        """Test that datapoint order affects generated hash."""
        dp1 = {"inputs": {"text": "hello"}}
        dp2 = {"inputs": {"text": "goodbye"}}

        id_order1 = generate_external_dataset_id([dp1, dp2])
        id_order2 = generate_external_dataset_id([dp2, dp1])

        # Different order should produce different hash
        assert id_order1 != id_order2


class TestGenerateExternalDatapointId:
    """Test suite for generate_external_datapoint_id function."""

    def test_generates_ext_prefix(self) -> None:
        """Test that generated ID starts with EXT- prefix."""
        datapoint = {"inputs": {"text": "hello"}, "ground_truth": {"label": "greeting"}}

        result = generate_external_datapoint_id(datapoint, index=0)

        assert result.startswith("EXT-")

    def test_deterministic_same_input(self) -> None:
        """Test that same input and index generates same ID."""
        datapoint = {"inputs": {"text": "hello"}}

        id1 = generate_external_datapoint_id(datapoint, index=0)
        id2 = generate_external_datapoint_id(datapoint, index=0)

        assert id1 == id2

    def test_different_datapoints_generate_different_ids(self) -> None:
        """Test that different datapoints generate different IDs."""
        dp1 = {"inputs": {"text": "hello"}}
        dp2 = {"inputs": {"text": "goodbye"}}

        id1 = generate_external_datapoint_id(dp1, index=0)
        id2 = generate_external_datapoint_id(dp2, index=0)

        assert id1 != id2

    def test_different_indices_generate_different_ids(self) -> None:
        """Test that different indices generate different IDs (even same datapoint)."""
        datapoint = {"inputs": {"text": "hello"}}

        id1 = generate_external_datapoint_id(datapoint, index=0)
        id2 = generate_external_datapoint_id(datapoint, index=1)

        # Different index should produce different hash
        assert id1 != id2

    def test_custom_id_override(self) -> None:
        """Test that custom_id parameter overrides generation."""
        datapoint = {"inputs": {"text": "hello"}}
        custom_id = "my-custom-datapoint"

        result = generate_external_datapoint_id(datapoint, index=0, custom_id=custom_id)

        assert result == "EXT-my-custom-datapoint"

    def test_custom_id_adds_prefix_if_missing(self) -> None:
        """Test that EXT- prefix is added to custom ID if not present."""
        datapoint = {"inputs": {"text": "hello"}}
        custom_id = "my-datapoint"

        result = generate_external_datapoint_id(datapoint, index=0, custom_id=custom_id)

        assert result == "EXT-my-datapoint"

    def test_datapoint_with_existing_id_field(self) -> None:
        """Test that datapoint with existing 'id' field still generates new ID."""
        datapoint = {
            "id": "existing-id",
            "inputs": {"text": "hello"},
        }

        result = generate_external_datapoint_id(datapoint, index=0)

        # Should generate new ID, not use existing one
        assert result.startswith("EXT-")
        assert result != "existing-id"


class TestPrepareExternalDataset:
    """Test suite for prepare_external_dataset function."""

    def test_returns_dataset_id_and_datapoint_ids(self) -> None:
        """Test that function returns tuple of (dataset_id, datapoint_ids)."""
        datapoints = [{"inputs": {"text": "hello"}}]

        result = prepare_external_dataset(datapoints)

        assert isinstance(result, tuple)
        assert len(result) == 2
        dataset_id, datapoint_ids = result
        assert isinstance(dataset_id, str)
        assert isinstance(datapoint_ids, list)
        assert all(isinstance(dp_id, str) for dp_id in datapoint_ids)

    def test_generates_ids_for_all_datapoints(self) -> None:
        """Test that IDs are generated for all datapoints."""
        datapoints = [
            {"inputs": {"text": "hello"}},
            {"inputs": {"text": "goodbye"}},
            {"inputs": {"text": "thanks"}},
        ]

        dataset_id, datapoint_ids = prepare_external_dataset(datapoints)

        assert len(datapoint_ids) == 3
        for dp_id in datapoint_ids:
            assert dp_id.startswith("EXT-")

    def test_generates_valid_ext_ids(self) -> None:
        """Test that all generated IDs are valid EXT- prefixed IDs."""
        datapoints = [
            {
                "inputs": {"text": "hello"},
                "ground_truth": {"label": "greeting"},
                "metadata": {"source": "test"},
            }
        ]

        dataset_id, datapoint_ids = prepare_external_dataset(datapoints)

        # Check dataset ID
        assert dataset_id.startswith("EXT-")
        assert len(dataset_id) > 4  # More than just "EXT-"

        # Check datapoint IDs
        assert len(datapoint_ids) == 1
        assert datapoint_ids[0].startswith("EXT-")
        assert len(datapoint_ids[0]) > 4

    def test_datapoints_with_existing_ids_use_them_as_custom(self) -> None:
        """Test that existing IDs in datapoints are used as custom IDs."""
        datapoints = [
            {"id": "my-id-1", "inputs": {"text": "hello"}},
            {"id": "my-id-2", "inputs": {"text": "goodbye"}},
        ]

        _, datapoint_ids = prepare_external_dataset(datapoints)

        # Existing IDs should be used (with EXT- prefix added)
        assert datapoint_ids[0] == "EXT-my-id-1"
        assert datapoint_ids[1] == "EXT-my-id-2"

    def test_custom_dataset_id_override(self) -> None:
        """Test that custom_dataset_id parameter is used."""
        datapoints = [{"inputs": {"text": "hello"}}]
        custom_id = "my-test-dataset"

        dataset_id, _ = prepare_external_dataset(
            datapoints, custom_dataset_id=custom_id
        )

        assert dataset_id == "EXT-my-test-dataset"

    def test_empty_datapoints_list(self) -> None:
        """Test behavior with empty datapoints list."""
        datapoints: List[Dict[str, Any]] = []

        dataset_id, datapoint_ids = prepare_external_dataset(datapoints)

        assert dataset_id.startswith("EXT-")
        assert datapoint_ids == []

    def test_datapoint_ids_are_unique(self) -> None:
        """Test that all generated datapoint IDs are unique."""
        datapoints = [
            {"inputs": {"text": "hello"}},
            {"inputs": {"text": "goodbye"}},
            {"inputs": {"text": "thanks"}},
        ]

        _, datapoint_ids = prepare_external_dataset(datapoints)

        assert len(datapoint_ids) == len(set(datapoint_ids))  # All unique

    def test_deterministic_generation(self) -> None:
        """Test that same input produces same IDs (deterministic)."""
        datapoints = [
            {"inputs": {"text": "hello"}},
            {"inputs": {"text": "goodbye"}},
        ]

        dataset_id1, datapoint_ids1 = prepare_external_dataset(datapoints)
        dataset_id2, datapoint_ids2 = prepare_external_dataset(datapoints)

        assert dataset_id1 == dataset_id2
        assert datapoint_ids1[0] == datapoint_ids2[0]
        assert datapoint_ids1[1] == datapoint_ids2[1]


class TestPrepareRunRequestData:
    """Test suite for prepare_run_request_data function."""

    def test_includes_required_fields(self) -> None:
        """Test that required fields are included in output."""
        result = prepare_run_request_data(
            run_id="run-123",  # Not included in output (used for API endpoint)
            name="test-run",
            project="test-project",
            dataset_id="ds-123",
        )

        # run_id is NOT in output (it's used for the API endpoint path)
        assert "run_id" not in result
        # These fields ARE in output
        assert result["name"] == "test-run"
        assert result["project"] == "test-project"
        assert result["status"] == "pending"  # Default value

    def test_non_ext_dataset_id_preserved(self) -> None:
        """Test that non-EXT dataset_id is preserved as-is."""
        data = {
            "run_id": "run-123",
            "name": "test-run",
            "project": "test-project",
            "dataset_id": "regular-dataset-id",
        }

        result = prepare_run_request_data(**data)

        assert result["dataset_id"] == "regular-dataset-id"
        assert "metadata" not in result or "offline_dataset_id" not in result.get(
            "metadata", {}
        )

    def test_ext_dataset_id_transformation(self) -> None:
        """Test CRITICAL EXT- prefix transformation to metadata.offline_dataset_id."""
        data = {
            "run_id": "run-123",
            "name": "test-run",
            "project": "test-project",
            "dataset_id": "EXT-abc123def456",
        }

        result = prepare_run_request_data(**data)

        # EXT- dataset_id should be moved to metadata.offline_dataset_id
        assert result["dataset_id"] is None
        assert "metadata" in result
        assert result["metadata"]["offline_dataset_id"] == "EXT-abc123def456"

    def test_ext_transformation_preserves_existing_metadata(self) -> None:
        """Test that EXT- transformation preserves existing metadata fields."""
        data = {
            "run_id": "run-123",
            "name": "test-run",
            "project": "test-project",
            "dataset_id": "EXT-abc123",
            "metadata": {
                "custom_field": "custom_value",
                "another_field": 42,
            },
        }

        result = prepare_run_request_data(**data)

        assert result["dataset_id"] is None
        assert result["metadata"]["offline_dataset_id"] == "EXT-abc123"
        assert result["metadata"]["custom_field"] == "custom_value"
        assert result["metadata"]["another_field"] == 42

    def test_none_dataset_id_handled(self) -> None:
        """Test that None dataset_id is handled gracefully."""
        data = {
            "run_id": "run-123",
            "name": "test-run",
            "project": "test-project",
            "dataset_id": None,
        }

        result = prepare_run_request_data(**data)

        assert result["dataset_id"] is None
        # Should not create metadata.offline_dataset_id for None

    def test_optional_fields_included_when_provided(self) -> None:
        """Test that optional fields are included when provided."""
        data = {
            "run_id": "run-123",
            "name": "test-run",
            "project": "test-project",
            "dataset_id": "ds-123",
            "event_ids": ["evt-1", "evt-2"],
            "configuration": {"param1": "value1"},
            "description": "Test description",
            "results": {"accuracy": 0.95},
            "status": "completed",
        }

        result = prepare_run_request_data(**data)

        assert result["event_ids"] == ["evt-1", "evt-2"]
        assert result["configuration"] == {"param1": "value1"}
        assert result["description"] == "Test description"
        assert result["results"] == {"accuracy": 0.95}
        assert result["status"] == "completed"

    def test_empty_event_ids_list_default(self) -> None:
        """Test that event_ids defaults to empty list when not provided."""
        data = {
            "run_id": "run-123",
            "name": "test-run",
            "project": "test-project",
            "dataset_id": "ds-123",
        }

        result = prepare_run_request_data(**data)

        # event_ids should default to empty list
        assert "event_ids" in result
        assert result["event_ids"] == []
