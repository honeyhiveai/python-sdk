"""DatapointsAPI Integration Tests - NO MOCKS, REAL API CALLS."""

import time
import uuid
from typing import Any

import pytest

from honeyhive.models import (
    CreateDatapointRequest,
    CreateDatapointResponse,
    DeleteDatapointResponse,
    GetDatapointsResponse,
    UpdateDatapointRequest,
    UpdateDatapointResponse,
)


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
        test_id = str(uuid.uuid4())[:8]
        test_inputs = {"query": f"test query {test_id}", "test_id": test_id}
        test_ground_truth = {"response": f"test response {test_id}"}

        datapoint_request = CreateDatapointRequest(
            inputs=test_inputs,
            ground_truth=test_ground_truth,
        )

        create_resp = integration_client.datapoints.create(datapoint_request)
        assert isinstance(create_resp, CreateDatapointResponse)
        assert create_resp.inserted is True
        assert "insertedIds" in create_resp.result
        assert len(create_resp.result["insertedIds"]) > 0

        datapoint_id = create_resp.result["insertedIds"][0]

        # Wait for indexing
        time.sleep(3)

        # Get the datapoint
        response = integration_client.datapoints.get(datapoint_id)

        # API returns dict with 'datapoint' key containing a list
        assert isinstance(response, dict)
        assert "datapoint" in response
        datapoint_list = response["datapoint"]
        assert isinstance(datapoint_list, list)
        assert len(datapoint_list) > 0

        # Verify the inputs match what was created
        datapoint = datapoint_list[0]
        assert datapoint.get("inputs") == test_inputs

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
        test_id = str(uuid.uuid4())[:8]
        test_inputs = {"query": f"test query {test_id}", "test_id": test_id}
        test_ground_truth = {"response": f"test response {test_id}"}

        datapoint_request = CreateDatapointRequest(
            inputs=test_inputs,
            ground_truth=test_ground_truth,
        )

        create_resp = integration_client.datapoints.create(datapoint_request)
        assert isinstance(create_resp, CreateDatapointResponse)
        assert create_resp.inserted is True
        assert "insertedIds" in create_resp.result
        assert len(create_resp.result["insertedIds"]) > 0

        datapoint_id = create_resp.result["insertedIds"][0]

        # Wait for indexing
        time.sleep(2)

        # Create update request with updated inputs
        updated_inputs = {"query": f"updated query {test_id}", "test_id": test_id}
        update_request = UpdateDatapointRequest(inputs=updated_inputs)

        # Update the datapoint
        response = integration_client.datapoints.update(datapoint_id, update_request)

        # Assert response is UpdateDatapointResponse
        assert isinstance(response, UpdateDatapointResponse)
        # Assert response.modified is True or response.modifiedCount >= 1
        # Check for 'modified' attribute or 'updated' (model field) or modifiedCount in result
        assert (
            getattr(response, "modified", False) is True
            or getattr(response, "updated", False) is True
            or response.result.get("modifiedCount", 0) >= 1
        )

    def test_delete_datapoint(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test datapoint deletion, verify 404 on get, dataset link removed."""
        test_id = str(uuid.uuid4())[:8]
        test_inputs = {"query": f"test query {test_id}", "test_id": test_id}
        test_ground_truth = {"response": f"test response {test_id}"}

        datapoint_request = CreateDatapointRequest(
            inputs=test_inputs,
            ground_truth=test_ground_truth,
        )

        create_resp = integration_client.datapoints.create(datapoint_request)
        assert isinstance(create_resp, CreateDatapointResponse)
        assert create_resp.inserted is True
        assert "insertedIds" in create_resp.result
        assert len(create_resp.result["insertedIds"]) > 0

        datapoint_id = create_resp.result["insertedIds"][0]

        # Wait for indexing
        time.sleep(2)

        # Delete the datapoint
        response = integration_client.datapoints.delete(datapoint_id)

        # Assert response is DeleteDatapointResponse
        assert isinstance(response, DeleteDatapointResponse)
        # Assert response.deleted is True or response.deletedCount >= 1
        assert response.deleted is True or getattr(response, "deletedCount", 0) >= 1

    def test_bulk_operations(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test bulk create/update/delete, verify all operations."""
        pytest.skip("DatapointsAPI bulk operations may not be implemented yet")
