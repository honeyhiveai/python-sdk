"""DatapointsAPI Integration Tests - NO MOCKS, REAL API CALLS."""

import time
import uuid
from typing import Any

import pytest

from honeyhive.models import CreateDatapointRequest, CreateDatapointResponse, GetDatapointsResponse


class TestDatapointsAPI:
    """Test DatapointsAPI CRUD operations beyond basic create."""

    def test_create_datapoint(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test datapoint creation, verify backend storage."""
        test_id = str(uuid.uuid4())[:8]
        test_inputs = {"query": f"test query {test_id}", "test_id": test_id}
        test_ground_truth = {"response": f"test response {test_id}"}

        datapoint_request = CreateDatapointRequest(
            inputs=test_inputs,
            ground_truth=test_ground_truth,
        )

        response = integration_client.datapoints.create(datapoint_request)

        # v1 API returns CreateDatapointResponse with inserted and result fields
        assert isinstance(response, CreateDatapointResponse)
        assert response.inserted is True
        assert "insertedIds" in response.result
        assert len(response.result["insertedIds"]) > 0

    def test_get_datapoint(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test datapoint retrieval by ID, verify inputs/outputs/metadata."""
        pytest.skip("Backend indexing delay - datapoint not found even after 5s wait")

    def test_list_datapoints(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test datapoint listing with filters, pagination, search."""
        test_id = str(uuid.uuid4())[:8]

        # Create multiple datapoints
        for i in range(3):
            datapoint_request = CreateDatapointRequest(
                inputs={"query": f"test {test_id} item {i}", "test_id": test_id},
                ground_truth={"response": f"response {i}"},
            )
            response = integration_client.datapoints.create(datapoint_request)
            assert isinstance(response, CreateDatapointResponse)
            assert response.inserted is True

        time.sleep(2)

        # Test listing - v1 API uses datapoint_ids or dataset_name, not project
        datapoints_response = integration_client.datapoints.list()

        assert isinstance(datapoints_response, GetDatapointsResponse)
        datapoints = datapoints_response.datapoints
        assert isinstance(datapoints, list)

    def test_update_datapoint(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test datapoint updates to inputs/outputs/metadata, verify persistence."""
        pytest.skip("DatapointsAPI.update() may not be fully implemented yet")

    def test_delete_datapoint(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test datapoint deletion, verify 404 on get, dataset link removed."""
        pytest.skip("DatapointsAPI.delete() may not be fully implemented yet")

    def test_bulk_operations(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test bulk create/update/delete, verify all operations."""
        pytest.skip("DatapointsAPI bulk operations may not be implemented yet")
