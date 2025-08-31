"""Unit tests for datapoints API."""

from unittest.mock import Mock, patch

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.models import CreateDatapointRequest


class TestDatapointsAPI:
    """Test datapoints API endpoints."""

    @pytest.fixture
    def api_key(self):
        return "test-api-key-12345"

    @pytest.fixture
    def client(self, api_key):
        return HoneyHive(api_key=api_key)

    @pytest.fixture
    def mock_datapoint_data(self):
        return {
            "_id": "datapoint-123",
            "project_id": "test-project",
            "inputs": {"query": "test query"},
            "history": [{"role": "user", "content": "test"}],
            "ground_truth": {"answer": "test answer"},
            "metadata": {"version": "1.0"},
        }

    def test_create_datapoint_with_model(self, client, mock_datapoint_data):
        """Test creating datapoint using CreateDatapointRequest model."""
        datapoint_request = CreateDatapointRequest(
            project="test-project",
            inputs={"query": "test query"},
            history=[{"role": "user", "content": "test"}],
            ground_truth={"answer": "test answer"},
            metadata={"version": "1.0"},
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_datapoint_data
            mock_request.return_value = mock_response

            result = client.datapoints.create_datapoint(datapoint_request)

            assert result.project_id == "test-project"
            assert result.inputs["query"] == "test query"
            mock_request.assert_called_once()

    def test_create_datapoint_from_dict(self, client, mock_datapoint_data):
        """Test creating datapoint from dictionary (legacy method)."""
        datapoint_data = {"project": "test-project", "inputs": {"query": "test query"}}

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_datapoint_data
            mock_request.return_value = mock_response

            result = client.datapoints.create_datapoint_from_dict(datapoint_data)

            assert result.project_id == "test-project"
            mock_request.assert_called_once()

    def test_get_datapoint(self, client, mock_datapoint_data):
        """Test getting datapoint by ID."""
        datapoint_id = "datapoint-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_datapoint_data
            mock_request.return_value = mock_response

            result = client.datapoints.get_datapoint(datapoint_id)

            # The field_id is mapped to _id in the model
            assert result.field_id == datapoint_id
            assert result.project_id == "test-project"
            mock_request.assert_called_once_with("GET", f"/datapoints/{datapoint_id}")

    def test_list_datapoints_without_project(self, client):
        """Test listing datapoints without project filter."""
        mock_data = {
            "datapoints": [
                {"project_id": "proj-1", "inputs": {"query": "query1"}},
                {"project_id": "proj-2", "inputs": {"query": "query2"}},
            ]
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.datapoints.list_datapoints(limit="50")

            assert len(result) == 2
            assert result[0].project_id == "proj-1"
            assert result[1].project_id == "proj-2"
            mock_request.assert_called_once_with(
                "GET", "/datapoints", params={"limit": "50"}
            )

    def test_list_datapoints_with_project(self, client):
        """Test listing datapoints with project filter."""
        mock_data = {
            "datapoints": [
                {"project_id": "test-project", "inputs": {"query": "query1"}}
            ]
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.datapoints.list_datapoints(
                project="test-project", limit="100"
            )

            assert len(result) == 1
            assert result[0].project_id == "test-project"
            mock_request.assert_called_once_with(
                "GET", "/datapoints", params={"project": "test-project", "limit": "100"}
            )

    @pytest.mark.asyncio
    async def test_create_datapoint_async(self, client, mock_datapoint_data):
        """Test creating datapoint asynchronously."""
        datapoint_request = CreateDatapointRequest(
            project="test-project",
            inputs={"query": "test query"},
            ground_truth={"answer": "test answer"},
            history=[{"role": "user", "content": "test"}],
            metadata={"version": "1.0"},
        )

        with patch.object(client, "request_async") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_datapoint_data
            mock_request.return_value = mock_response

            result = await client.datapoints.create_datapoint_async(datapoint_request)

            assert result.project_id == "test-project"
            mock_request.assert_called_once()

    def test_update_datapoint(self, client, mock_datapoint_data):
        """Test updating datapoint using from_dict method."""
        datapoint_id = "datapoint-123"
        update_data = {"inputs": {"query": "updated query"}}

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_datapoint_data
            mock_request.return_value = mock_response

            result = client.datapoints.update_datapoint_from_dict(
                datapoint_id, update_data
            )

            assert result.project_id == "test-project"
            mock_request.assert_called_once_with(
                "PUT", f"/datapoints/{datapoint_id}", json=update_data
            )
