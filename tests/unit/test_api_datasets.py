"""Unit tests for datasets API."""

from unittest.mock import Mock, patch

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.models import CreateDatasetRequest
from honeyhive.models.generated import PipelineType, Type4


class TestDatasetsAPI:
    """Test datasets API endpoints."""

    @pytest.fixture
    def api_key(self):
        return "test-api-key-12345"

    @pytest.fixture
    def client(self, api_key):
        return HoneyHive(api_key=api_key)

    @pytest.fixture
    def mock_dataset_data(self):
        return {
            "project": "test-project",
            "name": "test-dataset",
            "description": "Test dataset",
            "type": "evaluation",
            "datapoints": ["dp-1", "dp-2"],
            "linked_evals": ["eval-1"],
            "metadata": {"version": "1.0"},
        }

    def test_create_dataset_with_model(self, client, mock_dataset_data):
        """Test creating dataset using CreateDatasetRequest model."""
        dataset_request = CreateDatasetRequest(
            project="test-project",
            name="test-dataset",
            description="Test dataset",
            type=Type4.evaluation,
            pipeline_type=PipelineType.event,
            datapoints=["dp-1", "dp-2"],
            linked_evals=["eval-1"],
            metadata={"version": "1.0"},
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_dataset_data
            mock_request.return_value = mock_response

            result = client.datasets.create_dataset(dataset_request)

            assert result.project == "test-project"
            assert result.name == "test-dataset"
            mock_request.assert_called_once()

    def test_create_dataset_from_dict(self, client, mock_dataset_data):
        """Test creating dataset from dictionary (legacy method)."""
        dataset_data = {
            "project": "test-project",
            "name": "test-dataset",
            "description": "Test dataset",
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_dataset_data
            mock_request.return_value = mock_response

            result = client.datasets.create_dataset_from_dict(dataset_data)

            assert result.project == "test-project"
            assert result.name == "test-dataset"
            mock_request.assert_called_once()

    def test_get_dataset(self, client, mock_dataset_data):
        """Test getting dataset by ID."""
        dataset_id = "dataset-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_dataset_data
            mock_request.return_value = mock_response

            result = client.datasets.get_dataset(dataset_id)

            assert result.project == "test-project"
            assert result.name == "test-dataset"
            mock_request.assert_called_once_with("GET", f"/datasets/{dataset_id}")

    def test_list_datasets_without_project(self, client):
        """Test listing datasets without project filter."""
        mock_data = {
            "datasets": [
                {"project": "proj-1", "name": "dataset-1"},
                {"project": "proj-2", "name": "dataset-2"},
            ]
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.datasets.list_datasets(limit="50")

            assert len(result) == 2
            assert result[0].name == "dataset-1"
            assert result[1].name == "dataset-2"
            mock_request.assert_called_once_with(
                "GET", "/datasets", params={"limit": "50"}
            )

    def test_list_datasets_with_project(self, client):
        """Test listing datasets with project filter."""
        mock_data = {"datasets": [{"project": "test-project", "name": "dataset-1"}]}

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.datasets.list_datasets(project="test-project", limit="100")

            assert len(result) == 1
            assert result[0].project == "test-project"
            mock_request.assert_called_once_with(
                "GET", "/datasets", params={"limit": "100", "project": "test-project"}
            )

    def test_delete_dataset_success(self, client):
        """Test successful dataset deletion."""
        dataset_id = "dataset-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            result = client.datasets.delete_dataset(dataset_id)

            assert result is True
            mock_request.assert_called_once_with("DELETE", f"/datasets/{dataset_id}")

    def test_delete_dataset_failure(self, client):
        """Test failed dataset deletion."""
        dataset_id = "dataset-123"

        with patch.object(client, "request") as mock_request:
            mock_request.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                client.datasets.delete_dataset(dataset_id)

    @pytest.mark.asyncio
    async def test_create_dataset_async(self, client, mock_dataset_data):
        """Test creating dataset asynchronously."""
        dataset_request = CreateDatasetRequest(
            name="test-dataset", description="Test dataset", project="test-project"
        )

        with patch.object(client, "request_async") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_dataset_data
            mock_request.return_value = mock_response

            result = await client.datasets.create_dataset_async(dataset_request)

            assert result.name == "test-dataset"
            mock_request.assert_called_once()

    def test_update_dataset(self, client, mock_dataset_data):
        """Test updating dataset using from_dict method."""
        dataset_id = "dataset-123"
        update_data = {"description": "Updated description"}

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_dataset_data
            mock_request.return_value = mock_response

            result = client.datasets.update_dataset_from_dict(dataset_id, update_data)

            assert result.name == "test-dataset"
            mock_request.assert_called_once_with(
                "PUT", f"/datasets/{dataset_id}", json=update_data
            )
