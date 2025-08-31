"""Unit tests for metrics API."""

from unittest.mock import Mock, patch

import pytest

from honeyhive.api.client import HoneyHive


class TestMetricsAPI:
    """Test metrics API endpoints."""

    @pytest.fixture
    def api_key(self):
        return "test-api-key-12345"

    @pytest.fixture
    def client(self, api_key):
        return HoneyHive(api_key=api_key)

    @pytest.fixture
    def mock_metric_data(self):
        return {
            "id": "metric-123",
            "task": "test-project",
            "name": "test-metric",
            "description": "Test metric",
            "type": "custom",
            "return_type": "float",
            "criteria": "Test criteria",
        }

    def test_create_metric_from_dict(self, client, mock_metric_data):
        """Test creating metric from dictionary."""
        metric_data = {
            "task": "test-project",
            "name": "test-metric",
            "description": "Test metric",
            "type": "custom",
            "return_type": "float",
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_metric_data
            mock_request.return_value = mock_response

            result = client.metrics.create_metric_from_dict(metric_data)

            assert result.task == "test-project"
            assert result.name == "test-metric"
            mock_request.assert_called_once()

    def test_get_metric(self, client, mock_metric_data):
        """Test getting metric by ID."""
        metric_id = "metric-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_metric_data
            mock_request.return_value = mock_response

            result = client.metrics.get_metric(metric_id)

            assert result.task == "test-project"
            mock_request.assert_called_once_with("GET", f"/metrics/{metric_id}")

    def test_list_metrics(self, client):
        """Test listing metrics."""
        mock_data = {
            "metrics": [
                {
                    "id": "metric-1",
                    "task": "proj-1",
                    "name": "metric-1",
                    "description": "Test metric 1",
                    "type": "custom",
                    "return_type": "float",
                },
                {
                    "id": "metric-2",
                    "task": "proj-2",
                    "name": "metric-2",
                    "description": "Test metric 2",
                    "type": "custom",
                    "return_type": "float",
                },
            ]
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.metrics.list_metrics(limit=50)

            assert len(result) == 2
            assert result[0].name == "metric-1"
            assert result[1].name == "metric-2"
            mock_request.assert_called_once_with(
                "GET", "/metrics", params={"limit": "50"}
            )

    def test_delete_metric_success(self, client):
        """Test successful metric deletion."""
        metric_id = "metric-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            result = client.metrics.delete_metric(metric_id)

            assert result is True
            mock_request.assert_called_once_with("DELETE", f"/metrics/{metric_id}")

    def test_delete_metric_failure(self, client):
        """Test failed metric deletion."""
        metric_id = "metric-123"

        with patch.object(client, "request") as mock_request:
            mock_request.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                client.metrics.delete_metric(metric_id)

    @pytest.mark.asyncio
    async def test_create_metric_async(self, client, mock_metric_data):
        """Test creating metric asynchronously."""
        metric_data = {
            "task": "test-project",
            "name": "test-metric",
            "description": "Test metric",
            "type": "custom",
            "return_type": "float",
        }

        with patch.object(client, "request_async") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_metric_data
            mock_request.return_value = mock_response

            result = await client.metrics.create_metric_from_dict_async(metric_data)

            assert result.task == "test-project"
            assert result.name == "test-metric"
            mock_request.assert_called_once()

    def test_update_metric(self, client, mock_metric_data):
        """Test updating metric using from_dict method."""
        metric_id = "metric-123"
        update_data = {"description": "Updated description"}

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_metric_data
            mock_request.return_value = mock_response

            result = client.metrics.update_metric_from_dict(metric_id, update_data)

            assert result.task == "test-project"
            mock_request.assert_called_once_with(
                "PUT", f"/metrics/{metric_id}", json=update_data
            )
