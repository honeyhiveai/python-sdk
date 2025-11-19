"""Unit tests for honeyhive.api.tools.

This module contains comprehensive unit tests for the ToolsAPI class,
covering all CRUD operations for tools with both sync and async methods.
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

# pylint: disable=too-few-public-methods
# Justification: Test classes group related tests, not provide public interface

from unittest.mock import MagicMock, Mock, patch

import pytest

from honeyhive.api.base import BaseAPI
from honeyhive.api.tools import ToolsAPI
from honeyhive.models import CreateToolRequest, Tool, UpdateToolRequest
from honeyhive.models.generated import Type3


class TestToolsAPIInitialization:
    """Test ToolsAPI initialization and inheritance."""

    def test_tools_api_inherits_from_base_api(self, mock_client: Mock) -> None:
        """Test that ToolsAPI properly inherits from BaseAPI."""
        # Act
        tools_api = ToolsAPI(mock_client)

        # Assert
        assert isinstance(tools_api, BaseAPI)
        assert tools_api.client is mock_client
        assert hasattr(tools_api, "error_handler")
        assert hasattr(tools_api, "_client_name")

    def test_tools_api_initialization_sets_client_name(self, mock_client: Mock) -> None:
        """Test that ToolsAPI sets proper client name for error handling."""
        # Act
        tools_api = ToolsAPI(mock_client)

        # Assert
        assert tools_api._client_name == "ToolsAPI"


class TestCreateTool:
    """Test create_tool method with CreateToolRequest."""

    def test_create_tool_success(self, mock_client: Mock) -> None:
        """Test successful tool creation with CreateToolRequest."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": "tool-123",
            "task": "test-project",
            "name": "test-tool",
            "description": "Test tool description",
            "parameters": {"param1": "value1"},
            "tool_type": "function",
        }

        request = CreateToolRequest(
            task="test-project",
            name="test-tool",
            description="Test tool description",
            parameters={"param1": "value1"},
            type=Type3.function,
        )

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = tools_api.create_tool(request)

            # Assert
            assert isinstance(result, Tool)
            assert result.field_id == "tool-123"
            assert result.task == "test-project"
            assert result.name == "test-tool"
            assert result.description == "Test tool description"
            assert result.parameters == {"param1": "value1"}

            # Verify API call
            mock_client.request.assert_called_once_with(
                "POST",
                "/tools",
                json={"tool": request.model_dump(mode="json", exclude_none=True)},
            )

    def test_create_tool_with_minimal_request(self, mock_client: Mock) -> None:
        """Test tool creation with minimal required fields."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": "tool-456",
            "task": "minimal-project",
            "name": "minimal-tool",
            "parameters": {},
            "tool_type": "tool",
        }

        request = CreateToolRequest(
            task="minimal-project", name="minimal-tool", parameters={}, type=Type3.tool
        )

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = tools_api.create_tool(request)

            # Assert
            assert isinstance(result, Tool)
            assert result.field_id == "tool-456"
            assert result.task == "minimal-project"
            assert result.name == "minimal-tool"
            assert result.parameters == {}

    def test_create_tool_handles_api_error(self, mock_client: Mock) -> None:
        """Test that create_tool handles API errors properly."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        request = CreateToolRequest(
            task="test-project", name="test-tool", parameters={}, type=Type3.function
        )

        with patch.object(mock_client, "request", side_effect=Exception("API Error")):
            # Act & Assert
            with pytest.raises(Exception, match="API Error"):
                tools_api.create_tool(request)


class TestCreateToolFromDict:
    """Test create_tool_from_dict legacy method."""

    def test_create_tool_from_dict_success(self, mock_client: Mock) -> None:
        """Test successful tool creation from dictionary."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": "tool-dict-123",
            "task": "dict-project",
            "name": "dict-tool",
            "description": "Tool from dict",
            "parameters": {"key": "value"},
            "tool_type": "function",
        }

        tool_data = {
            "task": "dict-project",
            "name": "dict-tool",
            "description": "Tool from dict",
            "parameters": {"key": "value"},
            "type": "function",
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = tools_api.create_tool_from_dict(tool_data)

            # Assert
            assert isinstance(result, Tool)
            assert result.field_id == "tool-dict-123"
            assert result.task == "dict-project"
            assert result.name == "dict-tool"

            # Verify API call
            mock_client.request.assert_called_once_with(
                "POST", "/tools", json={"tool": tool_data}
            )

    def test_create_tool_from_dict_empty_dict(self, mock_client: Mock) -> None:
        """Test tool creation from empty dictionary."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": "empty-tool",
            "task": "",
            "name": "",
            "parameters": {},
            "tool_type": "tool",
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = tools_api.create_tool_from_dict({})

            # Assert
            assert isinstance(result, Tool)
            assert result.field_id == "empty-tool"


class TestCreateToolAsync:
    """Test create_tool_async method with CreateToolRequest."""

    @pytest.mark.asyncio
    async def test_create_tool_async_success(self, mock_client: Mock) -> None:
        """Test successful async tool creation with CreateToolRequest."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": "async-tool-123",
            "task": "async-project",
            "name": "async-tool",
            "description": "Async test tool",
            "parameters": {"async_param": "async_value"},
            "tool_type": "function",
        }

        request = CreateToolRequest(
            task="async-project",
            name="async-tool",
            description="Async test tool",
            parameters={"async_param": "async_value"},
            type=Type3.function,
        )

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await tools_api.create_tool_async(request)

            # Assert
            assert isinstance(result, Tool)
            assert result.field_id == "async-tool-123"
            assert result.task == "async-project"
            assert result.name == "async-tool"

            # Verify async API call
            mock_client.request_async.assert_called_once_with(
                "POST",
                "/tools",
                json={"tool": request.model_dump(mode="json", exclude_none=True)},
            )

    @pytest.mark.asyncio
    async def test_create_tool_async_handles_error(self, mock_client: Mock) -> None:
        """Test that create_tool_async handles errors properly."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        request = CreateToolRequest(
            task="error-project", name="error-tool", parameters={}, type=Type3.function
        )

        with patch.object(
            mock_client, "request_async", side_effect=Exception("Async API Error")
        ):
            # Act & Assert
            with pytest.raises(Exception, match="Async API Error"):
                await tools_api.create_tool_async(request)


class TestCreateToolFromDictAsync:
    """Test create_tool_from_dict_async legacy method."""

    @pytest.mark.asyncio
    async def test_create_tool_from_dict_async_success(self, mock_client: Mock) -> None:
        """Test successful async tool creation from dictionary."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": "async-dict-tool",
            "task": "async-dict-project",
            "name": "async-dict-tool",
            "parameters": {"async_key": "async_value"},
            "tool_type": "tool",
        }

        tool_data = {
            "task": "async-dict-project",
            "name": "async-dict-tool",
            "parameters": {"async_key": "async_value"},
            "type": "tool",
        }

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await tools_api.create_tool_from_dict_async(tool_data)

            # Assert
            assert isinstance(result, Tool)
            assert result.field_id == "async-dict-tool"
            assert result.task == "async-dict-project"

            # Verify async API call
            mock_client.request_async.assert_called_once_with(
                "POST", "/tools", json={"tool": tool_data}
            )


class TestGetTool:
    """Test get_tool method."""

    def test_get_tool_success(self, mock_client: Mock) -> None:
        """Test successful tool retrieval by ID."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        tool_id = "get-tool-123"
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": tool_id,
            "task": "get-project",
            "name": "retrieved-tool",
            "description": "Retrieved tool description",
            "parameters": {"retrieved_param": "retrieved_value"},
            "tool_type": "function",
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = tools_api.get_tool(tool_id)

            # Assert
            assert isinstance(result, Tool)
            assert result.field_id == tool_id
            assert result.task == "get-project"
            assert result.name == "retrieved-tool"

            # Verify API call
            mock_client.request.assert_called_once_with("GET", f"/tools/{tool_id}")

    def test_get_tool_with_special_characters_in_id(self, mock_client: Mock) -> None:
        """Test tool retrieval with special characters in ID."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        tool_id = "tool-with-special-chars_123-456"
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": tool_id,
            "task": "special-project",
            "name": "special-tool",
            "parameters": {},
            "tool_type": "tool",
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = tools_api.get_tool(tool_id)

            # Assert
            assert isinstance(result, Tool)
            assert result.field_id == tool_id

            # Verify API call with special ID
            mock_client.request.assert_called_once_with("GET", f"/tools/{tool_id}")

    def test_get_tool_handles_not_found(self, mock_client: Mock) -> None:
        """Test that get_tool handles not found errors."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        tool_id = "nonexistent-tool"

        with patch.object(
            mock_client, "request", side_effect=Exception("Tool not found")
        ):
            # Act & Assert
            with pytest.raises(Exception, match="Tool not found"):
                tools_api.get_tool(tool_id)


class TestGetToolAsync:
    """Test get_tool_async method."""

    @pytest.mark.asyncio
    async def test_get_tool_async_success(self, mock_client: Mock) -> None:
        """Test successful async tool retrieval by ID."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        tool_id = "async-get-tool-123"
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": tool_id,
            "task": "async-get-project",
            "name": "async-retrieved-tool",
            "parameters": {"async_retrieved": "value"},
            "tool_type": "function",
        }

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await tools_api.get_tool_async(tool_id)

            # Assert
            assert isinstance(result, Tool)
            assert result.field_id == tool_id
            assert result.task == "async-get-project"

            # Verify async API call
            mock_client.request_async.assert_called_once_with(
                "GET", f"/tools/{tool_id}"
            )


class TestListTools:
    """Test list_tools method with optional filtering."""

    def test_list_tools_without_project_filter(self, mock_client: Mock) -> None:
        """Test listing tools without project filter."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "_id": "list-tool-1",
                "task": "list-project-1",
                "name": "list-tool-1",
                "parameters": {},
                "tool_type": "function",
            },
            {
                "_id": "list-tool-2",
                "task": "list-project-2",
                "name": "list-tool-2",
                "parameters": {},
                "tool_type": "tool",
            },
        ]

        mock_processed_tools = [
            Mock(spec=Tool, field_id="list-tool-1", name="list-tool-1"),
            Mock(spec=Tool, field_id="list-tool-2", name="list-tool-2"),
        ]

        with patch.object(mock_client, "request", return_value=mock_response):
            with patch.object(
                tools_api,
                "_process_data_dynamically",
                return_value=mock_processed_tools,
            ):
                # Act
                result = tools_api.list_tools()

                # Assert
                assert isinstance(result, list)
                assert len(result) == 2
                assert all(isinstance(tool, Mock) for tool in result)

                # Verify API call without project filter
                mock_client.request.assert_called_once_with(
                    "GET", "/tools", params={"limit": "100"}
                )

                # Verify data processing was called (mock was patched)
                assert hasattr(tools_api, "_process_data_dynamically")

    def test_list_tools_with_project_filter(self, mock_client: Mock) -> None:
        """Test listing tools with project filter."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        project_name = "filtered-project"
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "_id": "filtered-tool-1",
                "task": project_name,
                "name": "filtered-tool-1",
                "parameters": {},
                "tool_type": "function",
            }
        ]

        mock_processed_tools = [
            Mock(spec=Tool, field_id="filtered-tool-1", task=project_name)
        ]

        with patch.object(mock_client, "request", return_value=mock_response):
            with patch.object(
                tools_api,
                "_process_data_dynamically",
                return_value=mock_processed_tools,
            ):
                # Act
                result = tools_api.list_tools(project=project_name)

                # Assert
                assert isinstance(result, list)
                assert len(result) == 1

                # Verify API call with project filter
                mock_client.request.assert_called_once_with(
                    "GET", "/tools", params={"limit": "100", "project": project_name}
                )

    def test_list_tools_with_custom_limit(self, mock_client: Mock) -> None:
        """Test listing tools with custom limit."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        custom_limit = 50
        mock_response = Mock()
        mock_response.json.return_value = []

        with patch.object(mock_client, "request", return_value=mock_response):
            with patch.object(tools_api, "_process_data_dynamically", return_value=[]):
                # Act
                result = tools_api.list_tools(limit=custom_limit)

                # Assert
                assert isinstance(result, list)
                assert len(result) == 0

                # Verify API call with custom limit
                mock_client.request.assert_called_once_with(
                    "GET", "/tools", params={"limit": "50"}
                )

    def test_list_tools_with_project_and_limit(self, mock_client: Mock) -> None:
        """Test listing tools with both project filter and custom limit."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        project_name = "combined-project"
        custom_limit = 25
        mock_response = Mock()
        mock_response.json.return_value = []

        with patch.object(mock_client, "request", return_value=mock_response):
            with patch.object(tools_api, "_process_data_dynamically", return_value=[]):
                # Act
                result = tools_api.list_tools(project=project_name, limit=custom_limit)

                # Assert
                assert isinstance(result, list)

                # Verify API call with both parameters
                mock_client.request.assert_called_once_with(
                    "GET", "/tools", params={"limit": "25", "project": project_name}
                )

    def test_list_tools_handles_object_response_format(self, mock_client: Mock) -> None:
        """Test listing tools when API returns object with 'tools' key."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        mock_response = Mock()
        mock_response.json.return_value = {
            "tools": [
                {
                    "_id": "object-tool-1",
                    "task": "object-project",
                    "name": "object-tool-1",
                    "parameters": {},
                    "tool_type": "function",
                }
            ],
            "total": 1,
            "page": 1,
        }

        mock_processed_tools = [
            Mock(spec=Tool, field_id="object-tool-1", name="object-tool-1")
        ]

        with patch.object(mock_client, "request", return_value=mock_response):
            with patch.object(
                tools_api,
                "_process_data_dynamically",
                return_value=mock_processed_tools,
            ):
                # Act
                result = tools_api.list_tools()

                # Assert
                assert isinstance(result, list)
                assert len(result) == 1

                # Verify that data processing was called (mock was patched)
                assert hasattr(tools_api, "_process_data_dynamically")

    def test_list_tools_handles_empty_response(self, mock_client: Mock) -> None:
        """Test listing tools with empty response."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        mock_response = Mock()
        mock_response.json.return_value = []

        with patch.object(mock_client, "request", return_value=mock_response):
            with patch.object(tools_api, "_process_data_dynamically", return_value=[]):
                # Act
                result = tools_api.list_tools()

                # Assert
                assert isinstance(result, list)
                assert len(result) == 0


class TestListToolsAsync:
    """Test list_tools_async method with optional filtering."""

    @pytest.mark.asyncio
    async def test_list_tools_async_without_project_filter(
        self, mock_client: Mock
    ) -> None:
        """Test async listing tools without project filter."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "_id": "async-list-tool-1",
                "task": "async-list-project",
                "name": "async-list-tool-1",
                "parameters": {},
                "tool_type": "function",
            }
        ]

        mock_processed_tools = [
            Mock(spec=Tool, field_id="async-list-tool-1", name="async-list-tool-1")
        ]

        with patch.object(mock_client, "request_async", return_value=mock_response):
            with patch.object(
                tools_api,
                "_process_data_dynamically",
                return_value=mock_processed_tools,
            ):
                # Act
                result = await tools_api.list_tools_async()

                # Assert
                assert isinstance(result, list)
                assert len(result) == 1

                # Verify async API call
                mock_client.request_async.assert_called_once_with(
                    "GET", "/tools", params={"limit": "100"}
                )

    @pytest.mark.asyncio
    async def test_list_tools_async_with_project_filter(
        self, mock_client: Mock
    ) -> None:
        """Test async listing tools with project filter."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        project_name = "async-filtered-project"
        mock_response = Mock()
        mock_response.json.return_value = []

        with patch.object(mock_client, "request_async", return_value=mock_response):
            with patch.object(tools_api, "_process_data_dynamically", return_value=[]):
                # Act
                result = await tools_api.list_tools_async(
                    project=project_name, limit=75
                )

                # Assert
                assert isinstance(result, list)

                # Verify async API call with parameters
                mock_client.request_async.assert_called_once_with(
                    "GET", "/tools", params={"limit": "75", "project": project_name}
                )


class TestUpdateTool:
    """Test update_tool method with UpdateToolRequest."""

    def test_update_tool_success(self, mock_client: Mock) -> None:
        """Test successful tool update with UpdateToolRequest."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        tool_id = "update-tool-123"
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": tool_id,
            "task": "updated-project",
            "name": "updated-tool",
            "description": "Updated description",
            "parameters": {"updated_param": "updated_value"},
            "tool_type": "function",
        }

        request = UpdateToolRequest(
            id=tool_id,
            name="updated-tool",
            description="Updated description",
            parameters={"updated_param": "updated_value"},
        )

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = tools_api.update_tool(tool_id, request)

            # Assert
            assert isinstance(result, Tool)
            assert result.field_id == tool_id
            assert result.name == "updated-tool"
            assert result.description == "Updated description"

            # Verify API call
            mock_client.request.assert_called_once_with(
                "PUT",
                f"/tools/{tool_id}",
                json=request.model_dump(mode="json", exclude_none=True),
            )

    def test_update_tool_with_minimal_fields(self, mock_client: Mock) -> None:
        """Test tool update with minimal required fields."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        tool_id = "minimal-update-tool"
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": tool_id,
            "task": "minimal-project",
            "name": "minimal-updated-tool",
            "parameters": {},
            "tool_type": "tool",
        }

        request = UpdateToolRequest(
            id=tool_id, name="minimal-updated-tool", parameters={}
        )

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = tools_api.update_tool(tool_id, request)

            # Assert
            assert isinstance(result, Tool)
            assert result.field_id == tool_id
            assert result.name == "minimal-updated-tool"


class TestUpdateToolFromDict:
    """Test update_tool_from_dict legacy method."""

    def test_update_tool_from_dict_success(self, mock_client: Mock) -> None:
        """Test successful tool update from dictionary."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        tool_id = "dict-update-tool"
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": tool_id,
            "task": "dict-updated-project",
            "name": "dict-updated-tool",
            "description": "Dict updated description",
            "parameters": {"dict_param": "dict_value"},
            "tool_type": "function",
        }

        tool_data = {
            "name": "dict-updated-tool",
            "description": "Dict updated description",
            "parameters": {"dict_param": "dict_value"},
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = tools_api.update_tool_from_dict(tool_id, tool_data)

            # Assert
            assert isinstance(result, Tool)
            assert result.field_id == tool_id
            assert result.name == "dict-updated-tool"

            # Verify API call
            mock_client.request.assert_called_once_with(
                "PUT", f"/tools/{tool_id}", json=tool_data
            )


class TestUpdateToolAsync:
    """Test update_tool_async method with UpdateToolRequest."""

    @pytest.mark.asyncio
    async def test_update_tool_async_success(self, mock_client: Mock) -> None:
        """Test successful async tool update with UpdateToolRequest."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        tool_id = "async-update-tool"
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": tool_id,
            "task": "async-updated-project",
            "name": "async-updated-tool",
            "parameters": {"async_updated": "value"},
            "tool_type": "function",
        }

        request = UpdateToolRequest(
            id=tool_id, name="async-updated-tool", parameters={"async_updated": "value"}
        )

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await tools_api.update_tool_async(tool_id, request)

            # Assert
            assert isinstance(result, Tool)
            assert result.field_id == tool_id
            assert result.name == "async-updated-tool"

            # Verify async API call
            mock_client.request_async.assert_called_once_with(
                "PUT",
                f"/tools/{tool_id}",
                json=request.model_dump(mode="json", exclude_none=True),
            )


class TestUpdateToolFromDictAsync:
    """Test update_tool_from_dict_async legacy method."""

    @pytest.mark.asyncio
    async def test_update_tool_from_dict_async_success(self, mock_client: Mock) -> None:
        """Test successful async tool update from dictionary."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        tool_id = "async-dict-update-tool"
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": tool_id,
            "task": "async-dict-project",
            "name": "async-dict-updated-tool",
            "parameters": {"async_dict": "value"},
            "tool_type": "tool",
        }

        tool_data = {
            "name": "async-dict-updated-tool",
            "parameters": {"async_dict": "value"},
        }

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await tools_api.update_tool_from_dict_async(tool_id, tool_data)

            # Assert
            assert isinstance(result, Tool)
            assert result.field_id == tool_id
            assert result.name == "async-dict-updated-tool"

            # Verify async API call
            mock_client.request_async.assert_called_once_with(
                "PUT", f"/tools/{tool_id}", json=tool_data
            )


class TestDeleteTool:
    """Test delete_tool method with error handling."""

    def test_delete_tool_success(self, mock_client: Mock) -> None:
        """Test successful tool deletion."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        tool_id = "delete-tool-123"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_error_handler = Mock()
        mock_context_manager = MagicMock()
        mock_error_handler.handle_operation.return_value = mock_context_manager

        # Mock client base_url for error context creation
        mock_client.server_url = "https://api.honeyhive.ai"

        with patch.object(tools_api, "error_handler", mock_error_handler):
            with patch.object(mock_client, "request", return_value=mock_response):
                # Act
                result = tools_api.delete_tool(tool_id)

                # Assert
                assert result is True

                # Verify error context creation and handling
                mock_error_handler.handle_operation.assert_called_once()

                # Verify API call
                mock_client.request.assert_called_once_with(
                    "DELETE", f"/tools/{tool_id}"
                )

    def test_delete_tool_failure_status_code(self, mock_client: Mock) -> None:
        """Test tool deletion with non-200 status code."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        tool_id = "delete-fail-tool"
        mock_response = Mock()
        mock_response.status_code = 404
        mock_error_handler = Mock()
        mock_context_manager = MagicMock()
        mock_error_handler.handle_operation.return_value = mock_context_manager

        # Mock client base_url for error context creation
        mock_client.server_url = "https://api.honeyhive.ai"

        with patch.object(tools_api, "error_handler", mock_error_handler):
            with patch.object(mock_client, "request", return_value=mock_response):
                # Act
                result = tools_api.delete_tool(tool_id)

                # Assert
                assert result is False

                # Verify API call was made
                mock_client.request.assert_called_once_with(
                    "DELETE", f"/tools/{tool_id}"
                )

    def test_delete_tool_creates_proper_error_context(self, mock_client: Mock) -> None:
        """Test that delete_tool creates proper error context."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        tool_id = "context-test-tool"
        mock_response = Mock()
        mock_response.status_code = 200

        # Mock client base_url for error context creation
        mock_client.server_url = "https://api.honeyhive.ai"

        with patch.object(tools_api, "_create_error_context") as mock_create_context:
            with patch.object(
                tools_api.error_handler, "handle_operation"
            ) as mock_handle:
                with patch.object(mock_client, "request", return_value=mock_response):
                    # Act
                    result = tools_api.delete_tool(tool_id)

                    # Assert
                    assert result is True

                    # Verify error context creation
                    mock_create_context.assert_called_once_with(
                        operation="delete_tool",
                        method="DELETE",
                        path=f"/tools/{tool_id}",
                        additional_context={"tool_id": tool_id},
                    )

                    # Verify error handler was called with context
                    mock_handle.assert_called_once_with(
                        mock_create_context.return_value
                    )


class TestDeleteToolAsync:
    """Test delete_tool_async method with error handling."""

    @pytest.mark.asyncio
    async def test_delete_tool_async_success(self, mock_client: Mock) -> None:
        """Test successful async tool deletion."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        tool_id = "async-delete-tool"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_error_handler = Mock()
        mock_context_manager = MagicMock()
        mock_error_handler.handle_operation.return_value = mock_context_manager

        # Mock client base_url for error context creation
        mock_client.server_url = "https://api.honeyhive.ai"

        with patch.object(tools_api, "error_handler", mock_error_handler):
            with patch.object(mock_client, "request_async", return_value=mock_response):
                # Act
                result = await tools_api.delete_tool_async(tool_id)

                # Assert
                assert result is True

                # Verify error handling
                mock_error_handler.handle_operation.assert_called_once()

                # Verify async API call
                mock_client.request_async.assert_called_once_with(
                    "DELETE", f"/tools/{tool_id}"
                )

    @pytest.mark.asyncio
    async def test_delete_tool_async_creates_proper_error_context(
        self, mock_client: Mock
    ) -> None:
        """Test that delete_tool_async creates proper error context."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        tool_id = "async-context-test-tool"
        mock_response = Mock()
        mock_response.status_code = 200

        # Mock client base_url for error context creation
        mock_client.server_url = "https://api.honeyhive.ai"

        with patch.object(tools_api, "_create_error_context") as mock_create_context:
            with patch.object(
                tools_api.error_handler, "handle_operation"
            ) as mock_handle:
                mock_handle.return_value = MagicMock()  # Context manager support
                with patch.object(
                    mock_client, "request_async", return_value=mock_response
                ):
                    # Act
                    result = await tools_api.delete_tool_async(tool_id)

                    # Assert
                    assert result is True

                    # Verify error context creation
                    mock_create_context.assert_called_once_with(
                        operation="delete_tool_async",
                        method="DELETE",
                        path=f"/tools/{tool_id}",
                        additional_context={"tool_id": tool_id},
                    )

    @pytest.mark.asyncio
    async def test_delete_tool_async_failure(self, mock_client: Mock) -> None:
        """Test async tool deletion with failure status code."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        tool_id = "async-delete-fail-tool"
        mock_response = Mock()
        mock_response.status_code = 500
        mock_error_handler = Mock()
        mock_context_manager = MagicMock()
        mock_error_handler.handle_operation.return_value = mock_context_manager

        # Mock client base_url for error context creation
        mock_client.server_url = "https://api.honeyhive.ai"

        with patch.object(tools_api, "error_handler", mock_error_handler):
            with patch.object(mock_client, "request_async", return_value=mock_response):
                # Act
                result = await tools_api.delete_tool_async(tool_id)

                # Assert
                assert result is False


class TestToolsAPIEdgeCases:
    """Test edge cases and error scenarios."""

    def test_tools_api_handles_none_client(self) -> None:
        """Test ToolsAPI behavior with None client."""
        # Act & Assert
        with pytest.raises(AttributeError):
            tools_api = ToolsAPI(None)  # type: ignore[arg-type]
            # This will fail when accessing None.base_url in error context creation
            tools_api.delete_tool("test-tool")

    def test_tools_api_handles_invalid_response_format(self, mock_client: Mock) -> None:
        """Test handling of invalid JSON response format."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid JSON"):
                tools_api.get_tool("test-tool")

    def test_list_tools_handles_none_response_data(self, mock_client: Mock) -> None:
        """Test list_tools handling of None response data."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        mock_response = Mock()
        mock_response.json.return_value = None

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act & Assert - Should raise AttributeError when calling .get() on None
            with pytest.raises(
                AttributeError, match="'NoneType' object has no attribute 'get'"
            ):
                tools_api.list_tools()

    def test_tools_api_preserves_base_api_functionality(
        self, mock_client: Mock
    ) -> None:
        """Test that ToolsAPI preserves BaseAPI functionality."""
        # Arrange
        tools_api = ToolsAPI(mock_client)

        # Act & Assert
        assert hasattr(tools_api, "_create_error_context")
        assert hasattr(tools_api, "_process_data_dynamically")
        assert hasattr(tools_api, "error_handler")
        assert callable(tools_api._create_error_context)
        assert callable(tools_api._process_data_dynamically)


class TestToolsAPIParameterValidation:
    """Test parameter validation and type handling."""

    def test_list_tools_limit_parameter_conversion(self, mock_client: Mock) -> None:
        """Test that limit parameter is properly converted to string."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        mock_response = Mock()
        mock_response.json.return_value = []

        with patch.object(mock_client, "request", return_value=mock_response):
            with patch.object(tools_api, "_process_data_dynamically", return_value=[]):
                # Act
                tools_api.list_tools(limit=150)

                # Assert - verify limit is converted to string
                mock_client.request.assert_called_once_with(
                    "GET", "/tools", params={"limit": "150"}
                )

    def test_create_tool_model_dump_exclude_none(self, mock_client: Mock) -> None:
        """Test that CreateToolRequest properly excludes None values."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": "test-tool",
            "task": "test-project",
            "name": "test-tool",
            "parameters": {},
            "tool_type": "function",
        }

        request = CreateToolRequest(
            task="test-project",
            name="test-tool",
            description=None,  # This should be excluded
            parameters={},
            type=Type3.function,
        )

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            tools_api.create_tool(request)

            # Assert - verify model_dump was called with proper parameters
            expected_json = {"tool": request.model_dump(mode="json", exclude_none=True)}
            mock_client.request.assert_called_once_with(
                "POST", "/tools", json=expected_json
            )

    def test_update_tool_model_dump_exclude_none(self, mock_client: Mock) -> None:
        """Test that UpdateToolRequest properly excludes None values."""
        # Arrange
        tools_api = ToolsAPI(mock_client)
        tool_id = "update-test-tool"
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": tool_id,
            "task": "test-project",
            "name": "updated-tool",
            "parameters": {},
            "tool_type": "function",
        }

        request = UpdateToolRequest(
            id=tool_id,
            name="updated-tool",
            description=None,  # This should be excluded
            parameters={},
        )

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            tools_api.update_tool(tool_id, request)

            # Assert - verify model_dump was called with proper parameters
            expected_json = request.model_dump(mode="json", exclude_none=True)
            mock_client.request.assert_called_once_with(
                "PUT", f"/tools/{tool_id}", json=expected_json
            )
