"""Unit tests for tools API."""

from unittest.mock import Mock, patch

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.models import CreateToolRequest
from honeyhive.models.generated import Type3


class TestToolsAPI:
    """Test tools API endpoints."""

    @pytest.fixture
    def api_key(self):
        return "test-api-key-12345"

    @pytest.fixture
    def client(self, api_key):
        return HoneyHive(api_key=api_key)

    @pytest.fixture
    def mock_tool_data(self):
        return {
            "_id": "tool-123",
            "task": "test-project",
            "name": "test-tool",
            "description": "Test tool",
            "tool_type": "function",
            "parameters": {"param1": "value1"},
        }

    def test_create_tool_with_model(self, client, mock_tool_data):
        """Test creating tool using CreateToolRequest model."""
        tool_request = CreateToolRequest(
            task="test-project",
            name="test-tool",
            description="Test tool",
            type=Type3.function,
            parameters={"param1": "value1"},
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_tool_data
            mock_request.return_value = mock_response

            result = client.tools.create_tool(tool_request)

            assert result.task == "test-project"
            assert result.name == "test-tool"
            mock_request.assert_called_once()

    def test_create_tool_from_dict(self, client, mock_tool_data):
        """Test creating tool from dictionary (legacy method)."""
        tool_data = {
            "task": "test-project",
            "name": "test-tool",
            "description": "Test tool",
            "tool_type": "function",
            "parameters": {"param1": "value1"},
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_tool_data
            mock_request.return_value = mock_response

            result = client.tools.create_tool_from_dict(tool_data)

            assert result.task == "test-project"
            assert result.name == "test-tool"
            mock_request.assert_called_once()

    def test_get_tool(self, client, mock_tool_data):
        """Test getting tool by ID."""
        tool_id = "tool-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_tool_data
            mock_request.return_value = mock_response

            result = client.tools.get_tool(tool_id)

            assert result.field_id == tool_id
            assert result.task == "test-project"
            mock_request.assert_called_once_with("GET", f"/tools/{tool_id}")

    def test_list_tools_without_project(self, client):
        """Test listing tools without project filter."""
        mock_data = {
            "tools": [
                {
                    "field_id": "tool-1",
                    "task": "proj-1",
                    "name": "tool-1",
                    "tool_type": "function",
                    "parameters": {},
                },
                {
                    "field_id": "tool-2",
                    "task": "proj-2",
                    "name": "tool-2",
                    "tool_type": "function",
                    "parameters": {},
                },
            ]
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.tools.list_tools(limit=50)

            assert len(result) == 2
            assert result[0].name == "tool-1"
            assert result[1].name == "tool-2"
            mock_request.assert_called_once_with(
                "GET", "/tools", params={"limit": "50"}
            )

    def test_list_tools_with_project(self, client):
        """Test listing tools with project filter."""
        mock_data = {
            "tools": [
                {
                    "field_id": "tool-1",
                    "task": "test-project",
                    "name": "tool-1",
                    "tool_type": "function",
                    "parameters": {},
                }
            ]
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.tools.list_tools(project="test-project", limit=100)

            assert len(result) == 1
            assert result[0].task == "test-project"
            mock_request.assert_called_once_with(
                "GET", "/tools", params={"project": "test-project", "limit": "100"}
            )

    def test_delete_tool_success(self, client):
        """Test successful tool deletion."""
        tool_id = "tool-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            result = client.tools.delete_tool(tool_id)

            assert result is True
            mock_request.assert_called_once_with("DELETE", f"/tools/{tool_id}")

    def test_delete_tool_failure(self, client):
        """Test failed tool deletion."""
        tool_id = "tool-123"

        with patch.object(client, "request") as mock_request:
            mock_request.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                client.tools.delete_tool(tool_id)

    @pytest.mark.asyncio
    async def test_create_tool_async(self, client, mock_tool_data):
        """Test creating tool asynchronously."""
        tool_request = CreateToolRequest(
            task="test-project",
            name="test-tool",
            description="Test tool",
            type=Type3.function,
            parameters={"param1": "value1"},
        )

        with patch.object(client, "request_async") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_tool_data
            mock_request.return_value = mock_response

            result = await client.tools.create_tool_async(tool_request)

            assert result.task == "test-project"
            assert result.name == "test-tool"
            mock_request.assert_called_once()
