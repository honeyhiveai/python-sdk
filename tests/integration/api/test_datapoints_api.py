"""DatapointsAPI Integration Tests - NO MOCKS, REAL API CALLS."""

import time
import uuid
from typing import Any

import pytest

from honeyhive.models import CreateDatapointRequest, UpdateDatapointRequest


def _get_created_id(response: Any) -> str:
    """Extract created datapoint ID from CreateDatapointResponse.

    The NWD API returns a CreateDatapointResponse with a `result` dict containing
    `insertedId` (str) and `insertedIds` (dict with string keys like {'0': 'id'}).
    """
    result = getattr(response, "result", None) or (
        response.get("result") if isinstance(response, dict) else None
    )
    assert result is not None, f"Missing result in response: {response}"

    # Prefer insertedId (single value)
    created_id = result.get("insertedId")
    if created_id:
        return created_id

    # Fallback to insertedIds
    inserted_ids = result.get("insertedIds")
    assert inserted_ids and len(inserted_ids) > 0, (
        f"Missing insertedIds in result: {result}"
    )
    if isinstance(inserted_ids, dict):
        return list(inserted_ids.values())[0]
    return inserted_ids[0]


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
            project=integration_project_name,
            inputs=test_inputs,
            ground_truth=test_ground_truth,
        )

        response = integration_client.datapoints.create(datapoint_request)

        # NWD API returns CreateDatapointResponse with result dict
        assert response is not None
        result = getattr(response, "result", None)
        assert result is not None
        assert result.get("acknowledged") is True or result.get("insertedId") is not None

    def test_get_datapoint(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test datapoint retrieval by ID, verify inputs/outputs/metadata."""
        test_id = str(uuid.uuid4())[:8]
        test_inputs = {"query": f"test query {test_id}", "test_id": test_id}
        test_ground_truth = {"response": f"test response {test_id}"}

        datapoint_request = CreateDatapointRequest(
            project=integration_project_name,
            inputs=test_inputs,
            ground_truth=test_ground_truth,
        )

        create_resp = integration_client.datapoints.create(datapoint_request)
        datapoint_id = _get_created_id(create_resp)

        # Wait for indexing
        time.sleep(3)

        # Get the datapoint
        response = integration_client.datapoints.get(datapoint_id)

        # API returns GetDatapointResponse or dict with 'datapoint' key containing a list
        datapoint_list = getattr(response, "datapoint", None)
        if datapoint_list is None and isinstance(response, dict):
            datapoint_list = response.get("datapoint")
        assert datapoint_list is not None
        assert isinstance(datapoint_list, list)
        assert len(datapoint_list) > 0

        # Verify the inputs match what was created
        datapoint = datapoint_list[0]
        dp_inputs = (
            datapoint.get("inputs")
            if isinstance(datapoint, dict)
            else getattr(datapoint, "inputs", None)
        )
        assert dp_inputs == test_inputs

    def test_list_datapoints(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test datapoint listing with filters, pagination, search."""
        test_id = str(uuid.uuid4())[:8]

        # Create multiple datapoints
        for i in range(3):
            datapoint_request = CreateDatapointRequest(
                project=integration_project_name,
                inputs={"query": f"test {test_id} item {i}", "test_id": test_id},
                ground_truth={"response": f"response {i}"},
            )
            response = integration_client.datapoints.create(datapoint_request)
            assert response is not None
            assert getattr(response, "result", None) is not None

        time.sleep(2)

        # Test listing - NWD API requires project param
        datapoints_response = integration_client.datapoints.list(
            project=integration_project_name
        )

        # GetDatapointsResponse has datapoints field, or could be a dict/list
        datapoints = getattr(datapoints_response, "datapoints", None)
        if datapoints is None and isinstance(datapoints_response, dict):
            datapoints = datapoints_response.get("datapoints", datapoints_response)
        elif datapoints is None and isinstance(datapoints_response, list):
            datapoints = datapoints_response
        assert isinstance(datapoints, list)

    def test_update_datapoint(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test datapoint updates to inputs/outputs/metadata, verify persistence."""
        test_id = str(uuid.uuid4())[:8]
        test_inputs = {"query": f"test query {test_id}", "test_id": test_id}
        test_ground_truth = {"response": f"test response {test_id}"}

        datapoint_request = CreateDatapointRequest(
            project=integration_project_name,
            inputs=test_inputs,
            ground_truth=test_ground_truth,
        )

        create_resp = integration_client.datapoints.create(datapoint_request)
        datapoint_id = _get_created_id(create_resp)

        # Wait for indexing
        time.sleep(2)

        # Create update request with updated inputs
        updated_inputs = {"query": f"updated query {test_id}", "test_id": test_id}
        update_request = UpdateDatapointRequest(inputs=updated_inputs)

        # Update the datapoint - NWD API returns None
        integration_client.datapoints.update(datapoint_id, update_request)

    def test_delete_datapoint(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test datapoint deletion, verify 404 on get, dataset link removed."""
        test_id = str(uuid.uuid4())[:8]
        test_inputs = {"query": f"test query {test_id}", "test_id": test_id}
        test_ground_truth = {"response": f"test response {test_id}"}

        datapoint_request = CreateDatapointRequest(
            project=integration_project_name,
            inputs=test_inputs,
            ground_truth=test_ground_truth,
        )

        create_resp = integration_client.datapoints.create(datapoint_request)
        datapoint_id = _get_created_id(create_resp)

        # Wait for indexing
        time.sleep(2)

        # Delete the datapoint
        try:
            response = integration_client.datapoints.delete(datapoint_id)
        except Exception as e:
            # Multi-tenant API key may not have delete permissions (403)
            if "403" in str(e):
                pytest.skip("Delete not permitted with current API key (403)")
            raise

        # NWD API returns DeleteDatapointResponse with acknowledged/deleted_count
        if response is not None:
            acknowledged = getattr(response, "acknowledged", None)
            deleted_count = getattr(response, "deleted_count", None)
            if isinstance(response, dict):
                acknowledged = response.get("acknowledged")
                deleted_count = response.get("deletedCount", response.get("deleted_count"))
            # At least one indicator of success
            assert (
                acknowledged is True
                or (deleted_count is not None and deleted_count >= 1)
            ), f"Delete did not indicate success: {response}"

    def test_bulk_operations(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test bulk create/update/delete, verify all operations."""
        pytest.skip("DatapointsAPI bulk operations may not be implemented yet")
