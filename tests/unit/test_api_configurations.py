"""Unit tests for honeyhive.api.configurations.

This module contains comprehensive unit tests for the ConfigurationsAPI class
and CreateConfigurationResponse dataclass, ensuring proper isolation and mocking.
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

import inspect
from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest

from honeyhive.api.configurations import ConfigurationsAPI, CreateConfigurationResponse
from honeyhive.models import (
    Configuration,
    Parameters1,
    Parameters2,
    PostConfigurationRequest,
    PutConfigurationRequest,
)
from honeyhive.models.generated import CallType, Type6


class TestCreateConfigurationResponse:
    """Test suite for CreateConfigurationResponse dataclass."""

    def test_initialization_with_all_parameters(self) -> None:
        """Test CreateConfigurationResponse initialization with all parameters."""
        # Arrange
        acknowledged = True
        inserted_id = "config-123"
        success = True

        # Act
        response = CreateConfigurationResponse(
            acknowledged=acknowledged, inserted_id=inserted_id, success=success
        )

        # Assert
        assert response.acknowledged is True
        assert response.inserted_id == "config-123"
        assert response.success is True

    def test_initialization_with_minimal_parameters(self) -> None:
        """Test CreateConfigurationResponse initialization with minimal parameters."""
        # Arrange
        acknowledged = False
        inserted_id = ""

        # Act
        response = CreateConfigurationResponse(
            acknowledged=acknowledged, inserted_id=inserted_id
        )

        # Assert
        assert response.acknowledged is False
        assert response.inserted_id == ""
        assert response.success is True  # Default value

    def test_initialization_with_default_success(self) -> None:
        """Test CreateConfigurationResponse uses default success value."""
        # Arrange
        acknowledged = True
        inserted_id = "test-id"

        # Act
        response = CreateConfigurationResponse(
            acknowledged=acknowledged, inserted_id=inserted_id
        )

        # Assert
        assert response.success is True  # Default value

    def test_dataclass_equality(self) -> None:
        """Test CreateConfigurationResponse equality comparison."""
        # Arrange
        response1 = CreateConfigurationResponse(
            acknowledged=True, inserted_id="config-123", success=True
        )
        response2 = CreateConfigurationResponse(
            acknowledged=True, inserted_id="config-123", success=True
        )
        response3 = CreateConfigurationResponse(
            acknowledged=False, inserted_id="config-456", success=False
        )

        # Act & Assert
        assert response1 == response2
        assert response1 != response3

    def test_dataclass_string_representation(self) -> None:
        """Test CreateConfigurationResponse string representation."""
        # Arrange
        response = CreateConfigurationResponse(
            acknowledged=True, inserted_id="config-123", success=True
        )

        # Act
        str_repr = str(response)

        # Assert
        assert "CreateConfigurationResponse" in str_repr
        assert "acknowledged=True" in str_repr
        assert "inserted_id='config-123'" in str_repr
        assert "success=True" in str_repr


class TestConfigurationsAPIInitialization:
    """Test suite for ConfigurationsAPI initialization."""

    def test_initialization_with_client(self, mock_client: Mock) -> None:
        """Test ConfigurationsAPI initialization with client."""
        # Arrange
        mock_client.server_url = "https://api.test.com"

        # Act
        api = ConfigurationsAPI(mock_client)

        # Assert
        assert api.client == mock_client
        assert hasattr(api, "error_handler")
        assert api._client_name == "ConfigurationsAPI"

    def test_inherits_from_base_api(self, mock_client: Mock) -> None:
        """Test ConfigurationsAPI inherits from BaseAPI."""
        # Arrange
        mock_client.server_url = "https://api.test.com"

        # Act
        api = ConfigurationsAPI(mock_client)

        # Assert
        assert hasattr(api, "client")
        assert hasattr(api, "error_handler")
        assert hasattr(api, "_client_name")
        assert hasattr(api, "_create_error_context")


class TestConfigurationsAPICreateConfiguration:
    """Test suite for ConfigurationsAPI create_configuration method."""

    def test_create_configuration_success(self, mock_client: Mock) -> None:
        """Test create_configuration with successful response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        parameters = Parameters2(call_type=CallType.chat, model="gpt-3.5-turbo")
        request = PostConfigurationRequest(
            project="test-project",
            name="test-config",
            provider="openai",
            parameters=parameters,
        )
        mock_response = Mock()
        mock_response.json.return_value = {
            "acknowledged": True,
            "insertedId": "config-123",
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.create_configuration(request)

            # Assert
            assert isinstance(result, CreateConfigurationResponse)
            assert result.acknowledged is True
            assert result.inserted_id == "config-123"
            assert result.success is True
            mock_client.request.assert_called_once_with(
                "POST",
                "/configurations",
                json=request.model_dump(mode="json", exclude_none=True),
            )

    def test_create_configuration_failure_response(self, mock_client: Mock) -> None:
        """Test create_configuration with failure response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        parameters = Parameters2(call_type=CallType.chat, model="gpt-3.5-turbo")
        request = PostConfigurationRequest(
            project="test-project",
            name="test-config",
            provider="openai",
            parameters=parameters,
        )
        mock_response = Mock()
        mock_response.json.return_value = {"acknowledged": False, "insertedId": ""}

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.create_configuration(request)

            # Assert
            assert isinstance(result, CreateConfigurationResponse)
            assert result.acknowledged is False
            assert result.inserted_id == ""
            assert result.success is False

    def test_create_configuration_missing_fields_response(
        self, mock_client: Mock
    ) -> None:
        """Test create_configuration with missing fields in response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        parameters = Parameters2(call_type=CallType.chat, model="gpt-3.5-turbo")
        request = PostConfigurationRequest(
            project="test-project",
            name="test-config",
            provider="openai",
            parameters=parameters,
        )
        mock_response = Mock()
        mock_response.json.return_value = {}  # Empty response

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.create_configuration(request)

            # Assert
            assert isinstance(result, CreateConfigurationResponse)
            assert result.acknowledged is False  # Default from get()
            assert result.inserted_id == ""  # Default from get()
            assert result.success is False  # Default from get()

    def test_create_configuration_request_serialization(
        self, mock_client: Mock
    ) -> None:
        """Test create_configuration properly serializes request."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        parameters = Parameters2(call_type=CallType.chat, model="gpt-3.5-turbo")
        request = PostConfigurationRequest(
            project="test-project",
            name="test-config",
            provider="openai",
            parameters=parameters,
        )
        mock_response = Mock()
        mock_response.json.return_value = {"acknowledged": True, "insertedId": "test"}

        with patch.object(
            mock_client, "request", return_value=mock_response
        ) as mock_request:
            # Act
            api.create_configuration(request)

            # Assert
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "POST"
            assert call_args[0][1] == "/configurations"
            assert "json" in call_args[1]
            # Verify the request was serialized properly
            serialized_data = call_args[1]["json"]
            assert isinstance(serialized_data, dict)


class TestConfigurationsAPICreateConfigurationFromDict:
    """Test suite for ConfigurationsAPI create_configuration_from_dict method."""

    def test_create_configuration_from_dict_success(self, mock_client: Mock) -> None:
        """Test create_configuration_from_dict with successful response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_data = {
            "project": "test-project",
            "name": "test-config",
            "provider": "openai",
            "parameters": {"call_type": "chat", "model": "gpt-3.5-turbo"},
        }
        mock_response = Mock()
        mock_response.json.return_value = {
            "acknowledged": True,
            "insertedId": "config-456",
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.create_configuration_from_dict(config_data)

            # Assert
            assert isinstance(result, CreateConfigurationResponse)
            assert result.acknowledged is True
            assert result.inserted_id == "config-456"
            assert result.success is True
            mock_client.request.assert_called_once_with(
                "POST", "/configurations", json=config_data
            )

    def test_create_configuration_from_dict_failure(self, mock_client: Mock) -> None:
        """Test create_configuration_from_dict with failure response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_data = {"name": "invalid-config"}
        mock_response = Mock()
        mock_response.json.return_value = {"acknowledged": False, "insertedId": ""}

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.create_configuration_from_dict(config_data)

            # Assert
            assert isinstance(result, CreateConfigurationResponse)
            assert result.acknowledged is False
            assert result.inserted_id == ""
            assert result.success is False

    def test_create_configuration_from_dict_empty_data(self, mock_client: Mock) -> None:
        """Test create_configuration_from_dict with empty data."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_data: Dict[str, Any] = {}
        mock_response = Mock()
        mock_response.json.return_value = {"acknowledged": False, "insertedId": ""}

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.create_configuration_from_dict(config_data)

            # Assert
            assert isinstance(result, CreateConfigurationResponse)
            mock_client.request.assert_called_once_with(
                "POST", "/configurations", json=config_data
            )


class TestConfigurationsAPICreateConfigurationAsync:
    """Test suite for ConfigurationsAPI create_configuration_async method."""

    @pytest.mark.asyncio
    async def test_create_configuration_async_success(self, mock_client: Mock) -> None:
        """Test create_configuration_async with successful response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        parameters = Parameters2(call_type=CallType.chat, model="gpt-3.5-turbo")
        request = PostConfigurationRequest(
            project="test-project",
            name="async-config",
            provider="openai",
            parameters=parameters,
        )
        mock_response = Mock()
        mock_response.json.return_value = {
            "acknowledged": True,
            "insertedId": "async-config-123",
        }

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await api.create_configuration_async(request)

            # Assert
            assert isinstance(result, CreateConfigurationResponse)
            assert result.acknowledged is True
            assert result.inserted_id == "async-config-123"
            assert result.success is True
            mock_client.request_async.assert_called_once_with(
                "POST",
                "/configurations",
                json=request.model_dump(mode="json", exclude_none=True),
            )

    @pytest.mark.asyncio
    async def test_create_configuration_async_failure(self, mock_client: Mock) -> None:
        """Test create_configuration_async with failure response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        parameters = Parameters2(call_type=CallType.chat, model="gpt-3.5-turbo")
        request = PostConfigurationRequest(
            project="test-project",
            name="async-config",
            provider="openai",
            parameters=parameters,
        )
        mock_response = Mock()
        mock_response.json.return_value = {"acknowledged": False, "insertedId": ""}

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await api.create_configuration_async(request)

            # Assert
            assert isinstance(result, CreateConfigurationResponse)
            assert result.acknowledged is False
            assert result.inserted_id == ""
            assert result.success is False


class TestConfigurationsAPICreateConfigurationFromDictAsync:
    """Test suite for ConfigurationsAPI create_configuration_from_dict_async method."""

    @pytest.mark.asyncio
    async def test_create_configuration_from_dict_async_success(
        self, mock_client: Mock
    ) -> None:
        """Test create_configuration_from_dict_async with successful response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_data = {
            "project": "test-project",
            "name": "async-dict-config",
            "provider": "openai",
            "parameters": {"call_type": "chat", "model": "gpt-3.5-turbo"},
        }
        mock_response = Mock()
        mock_response.json.return_value = {
            "acknowledged": True,
            "insertedId": "async-dict-config-123",
        }

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await api.create_configuration_from_dict_async(config_data)

            # Assert
            assert isinstance(result, CreateConfigurationResponse)
            assert result.acknowledged is True
            assert result.inserted_id == "async-dict-config-123"
            assert result.success is True
            mock_client.request_async.assert_called_once_with(
                "POST", "/configurations", json=config_data
            )

    @pytest.mark.asyncio
    async def test_create_configuration_from_dict_async_failure(
        self, mock_client: Mock
    ) -> None:
        """Test create_configuration_from_dict_async with failure response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_data = {"name": "invalid-async-config"}
        mock_response = Mock()
        mock_response.json.return_value = {"acknowledged": False, "insertedId": ""}

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await api.create_configuration_from_dict_async(config_data)

            # Assert
            assert isinstance(result, CreateConfigurationResponse)
            assert result.acknowledged is False
            assert result.inserted_id == ""
            assert result.success is False


class TestConfigurationsAPIGetConfiguration:
    """Test suite for ConfigurationsAPI get_configuration method."""

    def test_get_configuration_success(self, mock_client: Mock) -> None:
        """Test get_configuration with successful response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_id = "config-123"
        config_data = {
            "id": config_id,
            "project": "test-project",
            "name": "test-config",
            "provider": "openai",
            "parameters": {"call_type": "chat", "model": "gpt-3.5-turbo"},
        }
        mock_response = Mock()
        mock_response.json.return_value = config_data

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.get_configuration(config_id)

            # Assert
            assert isinstance(result, Configuration)
            mock_client.request.assert_called_once_with(
                "GET", f"/configurations/{config_id}"
            )

    def test_get_configuration_with_different_id(self, mock_client: Mock) -> None:
        """Test get_configuration with different configuration ID."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_id = "different-config-456"
        config_data = {
            "id": config_id,
            "project": "test-project",
            "name": "different-config",
            "provider": "anthropic",
            "parameters": {"call_type": "completion", "model": "claude-3"},
            "type": "LLM",
        }
        mock_response = Mock()
        mock_response.json.return_value = config_data

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.get_configuration(config_id)

            # Assert
            assert isinstance(result, Configuration)
            mock_client.request.assert_called_once_with(
                "GET", f"/configurations/{config_id}"
            )

    def test_get_configuration_empty_id(self, mock_client: Mock) -> None:
        """Test get_configuration with empty configuration ID."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_id = ""
        config_data = {
            "id": "",
            "project": "test-project",
            "name": "empty-config",
            "provider": "openai",
            "parameters": {"call_type": "chat", "model": "gpt-3.5-turbo"},
        }
        mock_response = Mock()
        mock_response.json.return_value = config_data

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.get_configuration(config_id)

            # Assert
            assert isinstance(result, Configuration)
            mock_client.request.assert_called_once_with("GET", "/configurations/")


class TestConfigurationsAPIGetConfigurationAsync:
    """Test suite for ConfigurationsAPI get_configuration_async method."""

    @pytest.mark.asyncio
    async def test_get_configuration_async_success(self, mock_client: Mock) -> None:
        """Test get_configuration_async with successful response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_id = "async-config-123"
        config_data = {
            "id": config_id,
            "project": "test-project",
            "name": "async-test-config",
            "provider": "openai",
            "parameters": {"call_type": "chat", "model": "gpt-3.5-turbo"},
        }
        mock_response = Mock()
        mock_response.json.return_value = config_data

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await api.get_configuration_async(config_id)

            # Assert
            assert isinstance(result, Configuration)
            mock_client.request_async.assert_called_once_with(
                "GET", f"/configurations/{config_id}"
            )

    @pytest.mark.asyncio
    async def test_get_configuration_async_different_id(
        self, mock_client: Mock
    ) -> None:
        """Test get_configuration_async with different configuration ID."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_id = "async-different-456"
        config_data = {
            "id": config_id,
            "project": "test-project",
            "name": "async-different-config",
            "provider": "anthropic",
            "parameters": {"call_type": "completion", "model": "claude-3"},
            "type": "LLM",
        }
        mock_response = Mock()
        mock_response.json.return_value = config_data

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await api.get_configuration_async(config_id)

            # Assert
            assert isinstance(result, Configuration)
            mock_client.request_async.assert_called_once_with(
                "GET", f"/configurations/{config_id}"
            )


class TestConfigurationsAPIListConfigurations:
    """Test suite for ConfigurationsAPI list_configurations method."""

    def test_list_configurations_default_parameters(self, mock_client: Mock) -> None:
        """Test list_configurations with default parameters."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        configurations_data = [
            {
                "id": "config-1",
                "project": "test-project",
                "name": "config-1",
                "provider": "openai",
                "parameters": {"call_type": "chat", "model": "gpt-3.5-turbo"},
            },
            {
                "id": "config-2",
                "project": "test-project",
                "name": "config-2",
                "provider": "openai",
                "parameters": {"call_type": "chat", "model": "gpt-4"},
            },
        ]
        mock_response = Mock()
        mock_response.json.return_value = configurations_data

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.list_configurations()

            # Assert
            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(config, Configuration) for config in result)
            mock_client.request.assert_called_once_with(
                "GET", "/configurations", params={"limit": 100}
            )

    def test_list_configurations_with_project_filter(self, mock_client: Mock) -> None:
        """Test list_configurations with project filter."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        project = "test-project"
        configurations_data = [
            {
                "id": "config-1",
                "project": project,
                "name": "config-1",
                "provider": "openai",
                "parameters": {"call_type": "chat", "model": "gpt-3.5-turbo"},
            }
        ]
        mock_response = Mock()
        mock_response.json.return_value = configurations_data

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.list_configurations(project=project)

            # Assert
            assert isinstance(result, list)
            assert len(result) == 1
            assert all(isinstance(config, Configuration) for config in result)
            mock_client.request.assert_called_once_with(
                "GET", "/configurations", params={"limit": 100, "project": project}
            )

    def test_list_configurations_with_custom_limit(self, mock_client: Mock) -> None:
        """Test list_configurations with custom limit."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        limit = 50
        configurations_data = [
            {
                "id": "config-1",
                "project": "test-project",
                "name": "config-1",
                "provider": "openai",
                "parameters": {"call_type": "chat", "model": "gpt-3.5-turbo"},
            }
        ]
        mock_response = Mock()
        mock_response.json.return_value = configurations_data

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.list_configurations(limit=limit)

            # Assert
            assert isinstance(result, list)
            assert len(result) == 1
            mock_client.request.assert_called_once_with(
                "GET", "/configurations", params={"limit": limit}
            )

    def test_list_configurations_with_project_and_limit(
        self, mock_client: Mock
    ) -> None:
        """Test list_configurations with both project and limit."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        project = "test-project"
        limit = 25
        configurations_data = [
            {
                "id": "config-1",
                "project": project,
                "name": "config-1",
                "provider": "openai",
                "parameters": {"call_type": "chat", "model": "gpt-3.5-turbo"},
            }
        ]
        mock_response = Mock()
        mock_response.json.return_value = configurations_data

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.list_configurations(project=project, limit=limit)

            # Assert
            assert isinstance(result, list)
            assert len(result) == 1
            mock_client.request.assert_called_once_with(
                "GET", "/configurations", params={"limit": limit, "project": project}
            )

    def test_list_configurations_legacy_format_response(
        self, mock_client: Mock
    ) -> None:
        """Test list_configurations with legacy format response (configurations key)."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        configurations_data = [
            {
                "id": "config-1",
                "project": "test-project",
                "name": "config-1",
                "provider": "openai",
                "parameters": {"call_type": "chat", "model": "gpt-3.5-turbo"},
            },
            {
                "id": "config-2",
                "project": "test-project",
                "name": "config-2",
                "provider": "openai",
                "parameters": {"call_type": "chat", "model": "gpt-4"},
            },
        ]
        legacy_response = {"configurations": configurations_data}
        mock_response = Mock()
        mock_response.json.return_value = legacy_response

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.list_configurations()

            # Assert
            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(config, Configuration) for config in result)

    def test_list_configurations_empty_legacy_format(self, mock_client: Mock) -> None:
        """Test list_configurations with empty legacy format response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        legacy_response: Dict[str, List[Dict[str, Any]]] = {"configurations": []}
        mock_response = Mock()
        mock_response.json.return_value = legacy_response

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.list_configurations()

            # Assert
            assert isinstance(result, list)
            assert len(result) == 0

    def test_list_configurations_missing_configurations_key(
        self, mock_client: Mock
    ) -> None:
        """Test list_configurations with legacy format missing configurations key."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        legacy_response = {"other_key": "value"}
        mock_response = Mock()
        mock_response.json.return_value = legacy_response

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.list_configurations()

            # Assert
            assert isinstance(result, list)
            assert len(result) == 0  # Empty list from get("configurations", [])

    def test_list_configurations_empty_direct_list(self, mock_client: Mock) -> None:
        """Test list_configurations with empty direct list response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        configurations_data: List[Dict[str, Any]] = []
        mock_response = Mock()
        mock_response.json.return_value = configurations_data

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.list_configurations()

            # Assert
            assert isinstance(result, list)
            assert len(result) == 0


class TestConfigurationsAPIListConfigurationsAsync:
    """Test suite for ConfigurationsAPI list_configurations_async method."""

    @pytest.mark.asyncio
    async def test_list_configurations_async_default_parameters(
        self, mock_client: Mock
    ) -> None:
        """Test list_configurations_async with default parameters."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        configurations_data = [
            {
                "id": "async-config-1",
                "project": "test-project",
                "name": "async-config-1",
                "provider": "openai",
                "parameters": {"call_type": "chat", "model": "gpt-3.5-turbo"},
            },
            {
                "id": "async-config-2",
                "project": "test-project",
                "name": "async-config-2",
                "provider": "openai",
                "parameters": {"call_type": "chat", "model": "gpt-4"},
            },
        ]
        mock_response = Mock()
        mock_response.json.return_value = configurations_data

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await api.list_configurations_async()

            # Assert
            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(config, Configuration) for config in result)
            mock_client.request_async.assert_called_once_with(
                "GET", "/configurations", params={"limit": 100}
            )

    @pytest.mark.asyncio
    async def test_list_configurations_async_with_project_filter(
        self, mock_client: Mock
    ) -> None:
        """Test list_configurations_async with project filter."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        project = "async-test-project"
        configurations_data = [
            {
                "id": "async-config-1",
                "project": project,
                "name": "async-config-1",
                "provider": "openai",
                "parameters": {"call_type": "chat", "model": "gpt-3.5-turbo"},
            }
        ]
        mock_response = Mock()
        mock_response.json.return_value = configurations_data

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await api.list_configurations_async(project=project)

            # Assert
            assert isinstance(result, list)
            assert len(result) == 1
            mock_client.request_async.assert_called_once_with(
                "GET", "/configurations", params={"limit": 100, "project": project}
            )

    @pytest.mark.asyncio
    async def test_list_configurations_async_legacy_format(
        self, mock_client: Mock
    ) -> None:
        """Test list_configurations_async with legacy format response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        configurations_data = [
            {
                "id": "async-config-1",
                "project": "test-project",
                "name": "async-config-1",
                "provider": "openai",
                "parameters": {"call_type": "chat", "model": "gpt-3.5-turbo"},
            }
        ]
        legacy_response = {"configurations": configurations_data}
        mock_response = Mock()
        mock_response.json.return_value = legacy_response

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await api.list_configurations_async()

            # Assert
            assert isinstance(result, list)
            assert len(result) == 1
            assert all(isinstance(config, Configuration) for config in result)


class TestConfigurationsAPIUpdateConfiguration:
    """Test suite for ConfigurationsAPI update_configuration method."""

    def test_update_configuration_success(self, mock_client: Mock) -> None:
        """Test update_configuration with successful response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_id = "config-123"
        parameters = Parameters1(call_type=CallType.chat, model="gpt-4")
        request = PutConfigurationRequest(
            project="test-project",
            name="updated-config",
            provider="openai",
            parameters=parameters,
        )
        updated_config_data = {
            "id": config_id,
            "project": "test-project",
            "name": "updated-config",
            "provider": "openai",
            "parameters": {"call_type": "chat", "model": "gpt-4"},
        }
        mock_response = Mock()
        mock_response.json.return_value = updated_config_data

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.update_configuration(config_id, request)

            # Assert
            assert isinstance(result, Configuration)
            mock_client.request.assert_called_once_with(
                "PUT",
                f"/configurations/{config_id}",
                json=request.model_dump(mode="json", exclude_none=True),
            )

    def test_update_configuration_different_id(self, mock_client: Mock) -> None:
        """Test update_configuration with different configuration ID."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_id = "different-config-456"
        parameters = Parameters1(call_type=CallType.completion, model="claude-3")
        request = PutConfigurationRequest(
            project="test-project",
            name="different-updated-config",
            provider="anthropic",
            parameters=parameters,
            type=Type6.LLM,
        )
        updated_config_data = {
            "id": config_id,
            "project": "test-project",
            "name": "different-updated-config",
            "provider": "anthropic",
            "parameters": {"call_type": "completion", "model": "claude-3"},
            "type": "LLM",
        }
        mock_response = Mock()
        mock_response.json.return_value = updated_config_data

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.update_configuration(config_id, request)

            # Assert
            assert isinstance(result, Configuration)
            mock_client.request.assert_called_once_with(
                "PUT",
                f"/configurations/{config_id}",
                json=request.model_dump(mode="json", exclude_none=True),
            )

    def test_update_configuration_request_serialization(
        self, mock_client: Mock
    ) -> None:
        """Test update_configuration properly serializes request."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_id = "config-123"
        parameters = Parameters1(call_type=CallType.chat, model="gpt-3.5-turbo")
        request = PutConfigurationRequest(
            project="test-project",
            name="serialization-test",
            provider="openai",
            parameters=parameters,
        )
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": config_id,
            "project": "test-project",
            "name": "serialization-test",
            "provider": "openai",
            "parameters": {"call_type": "chat", "model": "gpt-3.5-turbo"},
        }

        with patch.object(
            mock_client, "request", return_value=mock_response
        ) as mock_request:
            # Act
            api.update_configuration(config_id, request)

            # Assert
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "PUT"
            assert call_args[0][1] == f"/configurations/{config_id}"
            assert "json" in call_args[1]
            serialized_data = call_args[1]["json"]
            assert isinstance(serialized_data, dict)


class TestConfigurationsAPIUpdateConfigurationFromDict:
    """Test suite for ConfigurationsAPI update_configuration_from_dict method."""

    def test_update_configuration_from_dict_success(self, mock_client: Mock) -> None:
        """Test update_configuration_from_dict with successful response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_id = "dict-config-123"
        config_data = {
            "project": "test-project",
            "name": "dict-updated-config",
            "provider": "openai",
            "parameters": {"call_type": "chat", "model": "gpt-4"},
        }
        updated_config_data = {
            "id": config_id,
            "project": "test-project",
            "name": "dict-updated-config",
            "provider": "openai",
            "parameters": {"call_type": "chat", "model": "gpt-4"},
        }
        mock_response = Mock()
        mock_response.json.return_value = updated_config_data

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.update_configuration_from_dict(config_id, config_data)

            # Assert
            assert isinstance(result, Configuration)
            mock_client.request.assert_called_once_with(
                "PUT", f"/configurations/{config_id}", json=config_data
            )

    def test_update_configuration_from_dict_empty_data(self, mock_client: Mock) -> None:
        """Test update_configuration_from_dict with empty data."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_id = "empty-dict-config"
        config_data: Dict[str, Any] = {}
        updated_config_data = {
            "id": config_id,
            "project": "test-project",
            "name": "empty-config",
            "provider": "openai",
            "parameters": {"call_type": "chat", "model": "gpt-3.5-turbo"},
        }
        mock_response = Mock()
        mock_response.json.return_value = updated_config_data

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.update_configuration_from_dict(config_id, config_data)

            # Assert
            assert isinstance(result, Configuration)
            mock_client.request.assert_called_once_with(
                "PUT", f"/configurations/{config_id}", json=config_data
            )


class TestConfigurationsAPIUpdateConfigurationAsync:
    """Test suite for ConfigurationsAPI update_configuration_async method."""

    @pytest.mark.asyncio
    async def test_update_configuration_async_success(self, mock_client: Mock) -> None:
        """Test update_configuration_async with successful response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_id = "async-update-config-123"
        parameters = Parameters1(call_type=CallType.chat, model="gpt-4")
        request = PutConfigurationRequest(
            project="test-project",
            name="async-updated-config",
            provider="openai",
            parameters=parameters,
        )
        updated_config_data = {
            "id": config_id,
            "project": "test-project",
            "name": "async-updated-config",
            "provider": "openai",
            "parameters": {"call_type": "chat", "model": "gpt-4"},
        }
        mock_response = Mock()
        mock_response.json.return_value = updated_config_data

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await api.update_configuration_async(config_id, request)

            # Assert
            assert isinstance(result, Configuration)
            mock_client.request_async.assert_called_once_with(
                "PUT",
                f"/configurations/{config_id}",
                json=request.model_dump(mode="json", exclude_none=True),
            )

    @pytest.mark.asyncio
    async def test_update_configuration_async_different_id(
        self, mock_client: Mock
    ) -> None:
        """Test update_configuration_async with different configuration ID."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_id = "async-different-update-456"
        parameters = Parameters1(call_type=CallType.completion, model="claude-3")
        request = PutConfigurationRequest(
            project="test-project",
            name="async-different-updated",
            provider="anthropic",
            parameters=parameters,
            type=Type6.LLM,
        )
        updated_config_data = {
            "id": config_id,
            "project": "test-project",
            "name": "async-different-updated",
            "provider": "anthropic",
            "parameters": {"call_type": "completion", "model": "claude-3"},
            "type": "LLM",
        }
        mock_response = Mock()
        mock_response.json.return_value = updated_config_data

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await api.update_configuration_async(config_id, request)

            # Assert
            assert isinstance(result, Configuration)
            mock_client.request_async.assert_called_once_with(
                "PUT",
                f"/configurations/{config_id}",
                json=request.model_dump(mode="json", exclude_none=True),
            )


class TestConfigurationsAPIUpdateConfigurationFromDictAsync:
    """Test suite for ConfigurationsAPI update_configuration_from_dict_async method."""

    @pytest.mark.asyncio
    async def test_update_configuration_from_dict_async_success(
        self, mock_client: Mock
    ) -> None:
        """Test update_configuration_from_dict_async with successful response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_id = "async-dict-update-123"
        config_data = {
            "project": "test-project",
            "name": "async-dict-updated-config",
            "provider": "openai",
            "parameters": {"call_type": "chat", "model": "gpt-4"},
        }
        updated_config_data = {
            "id": config_id,
            "project": "test-project",
            "name": "async-dict-updated-config",
            "provider": "openai",
            "parameters": {"call_type": "chat", "model": "gpt-4"},
        }
        mock_response = Mock()
        mock_response.json.return_value = updated_config_data

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await api.update_configuration_from_dict_async(
                config_id, config_data
            )

            # Assert
            assert isinstance(result, Configuration)
            mock_client.request_async.assert_called_once_with(
                "PUT", f"/configurations/{config_id}", json=config_data
            )

    @pytest.mark.asyncio
    async def test_update_configuration_from_dict_async_empty_data(
        self, mock_client: Mock
    ) -> None:
        """Test update_configuration_from_dict_async with empty data."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        config_id = "async-empty-dict-update"
        config_data: Dict[str, Any] = {}
        updated_config_data = {
            "id": config_id,
            "project": "test-project",
            "name": "async-empty-config",
            "provider": "openai",
            "parameters": {"call_type": "chat", "model": "gpt-3.5-turbo"},
        }
        mock_response = Mock()
        mock_response.json.return_value = updated_config_data

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await api.update_configuration_from_dict_async(
                config_id, config_data
            )

            # Assert
            assert isinstance(result, Configuration)
            mock_client.request_async.assert_called_once_with(
                "PUT", f"/configurations/{config_id}", json=config_data
            )


class TestConfigurationsAPIDeleteConfiguration:
    """Test suite for ConfigurationsAPI delete_configuration method."""

    def test_delete_configuration_success(self, mock_client: Mock) -> None:
        """Test delete_configuration with successful response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        mock_client.server_url = "https://api.test.com"
        config_id = "delete-config-123"
        mock_response = Mock()
        mock_response.status_code = 200

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.delete_configuration(config_id)

            # Assert
            assert result is True
            mock_client.request.assert_called_once_with(
                "DELETE", f"/configurations/{config_id}"
            )

    def test_delete_configuration_failure(self, mock_client: Mock) -> None:
        """Test delete_configuration with failure response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        mock_client.server_url = "https://api.test.com"
        config_id = "delete-config-456"
        mock_response = Mock()
        mock_response.status_code = 404

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.delete_configuration(config_id)

            # Assert
            assert result is False
            mock_client.request.assert_called_once_with(
                "DELETE", f"/configurations/{config_id}"
            )

    def test_delete_configuration_server_error(self, mock_client: Mock) -> None:
        """Test delete_configuration with server error response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        mock_client.server_url = "https://api.test.com"
        config_id = "delete-config-error"
        mock_response = Mock()
        mock_response.status_code = 500

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.delete_configuration(config_id)

            # Assert
            assert result is False

    def test_delete_configuration_uses_error_handler(self, mock_client: Mock) -> None:
        """Test delete_configuration uses error handler context."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        mock_client.server_url = "https://api.test.com"
        config_id = "error-handler-test"
        mock_response = Mock()
        mock_response.status_code = 200

        with patch.object(api, "_create_error_context") as mock_create_context:
            with patch.object(
                api.error_handler, "handle_operation"
            ) as mock_handle_operation:
                with patch.object(mock_client, "request", return_value=mock_response):
                    # Act
                    result = api.delete_configuration(config_id)

                    # Assert
                    assert result is True
                    mock_create_context.assert_called_once_with(
                        operation="delete_configuration",
                        method="DELETE",
                        path=f"/configurations/{config_id}",
                        additional_context={"config_id": config_id},
                    )
                    mock_handle_operation.assert_called_once()

    def test_delete_configuration_empty_id(self, mock_client: Mock) -> None:
        """Test delete_configuration with empty configuration ID."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        mock_client.server_url = "https://api.test.com"
        config_id = ""
        mock_response = Mock()
        mock_response.status_code = 200

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = api.delete_configuration(config_id)

            # Assert
            assert result is True
            mock_client.request.assert_called_once_with("DELETE", "/configurations/")


class TestConfigurationsAPIDeleteConfigurationAsync:
    """Test suite for ConfigurationsAPI delete_configuration_async method."""

    @pytest.mark.asyncio
    async def test_delete_configuration_async_success(self, mock_client: Mock) -> None:
        """Test delete_configuration_async with successful response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        mock_client.server_url = "https://api.test.com"
        config_id = "async-delete-config-123"
        mock_response = Mock()
        mock_response.status_code = 200

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await api.delete_configuration_async(config_id)

            # Assert
            assert result is True
            mock_client.request_async.assert_called_once_with(
                "DELETE", f"/configurations/{config_id}"
            )

    @pytest.mark.asyncio
    async def test_delete_configuration_async_failure(self, mock_client: Mock) -> None:
        """Test delete_configuration_async with failure response."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        mock_client.server_url = "https://api.test.com"
        config_id = "async-delete-config-456"
        mock_response = Mock()
        mock_response.status_code = 404

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await api.delete_configuration_async(config_id)

            # Assert
            assert result is False
            mock_client.request_async.assert_called_once_with(
                "DELETE", f"/configurations/{config_id}"
            )

    @pytest.mark.asyncio
    async def test_delete_configuration_async_uses_error_handler(
        self, mock_client: Mock
    ) -> None:
        """Test delete_configuration_async uses error handler context."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        mock_client.server_url = "https://api.test.com"
        config_id = "async-error-handler-test"
        mock_response = Mock()
        mock_response.status_code = 200

        with patch.object(api, "_create_error_context") as mock_create_context:
            with patch.object(
                api.error_handler, "handle_operation"
            ) as mock_handle_operation:
                with patch.object(
                    mock_client, "request_async", return_value=mock_response
                ):
                    # Act
                    result = await api.delete_configuration_async(config_id)

                    # Assert
                    assert result is True
                    mock_create_context.assert_called_once_with(
                        operation="delete_configuration_async",
                        method="DELETE",
                        path=f"/configurations/{config_id}",
                        additional_context={"config_id": config_id},
                    )
                    mock_handle_operation.assert_called_once()


class TestConfigurationsAPIEdgeCases:
    """Test suite for ConfigurationsAPI edge cases and error conditions."""

    def test_api_inherits_base_api_methods(self, mock_client: Mock) -> None:
        """Test ConfigurationsAPI inherits BaseAPI methods."""
        # Arrange
        mock_client.server_url = "https://api.test.com"
        api = ConfigurationsAPI(mock_client)

        # Act & Assert
        assert hasattr(api, "_create_error_context")
        assert hasattr(api, "_process_data_dynamically")
        assert callable(getattr(api, "_create_error_context"))
        assert callable(getattr(api, "_process_data_dynamically"))

    def test_create_error_context_functionality(self, mock_client: Mock) -> None:
        """Test _create_error_context method functionality."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        mock_client.server_url = "https://api.test.com"

        # Act
        context = api._create_error_context(
            operation="test_operation",
            method="POST",
            path="/test/path",
            additional_context={"test_key": "test_value"},
        )

        # Assert
        assert context.operation == "test_operation"
        assert context.method == "POST"
        assert context.url == "https://api.test.com/test/path"
        assert context.client_name == "ConfigurationsAPI"
        assert context.additional_context == {
            "additional_context": {"test_key": "test_value"}
        }

    def test_configurations_api_class_name(self, mock_client: Mock) -> None:
        """Test ConfigurationsAPI sets correct class name."""
        # Arrange & Act
        api = ConfigurationsAPI(mock_client)

        # Assert
        assert api._client_name == "ConfigurationsAPI"

    def test_all_methods_exist(self, mock_client: Mock) -> None:
        """Test all expected methods exist on ConfigurationsAPI."""
        # Arrange
        api = ConfigurationsAPI(mock_client)
        expected_methods = [
            "create_configuration",
            "create_configuration_from_dict",
            "create_configuration_async",
            "create_configuration_from_dict_async",
            "get_configuration",
            "get_configuration_async",
            "list_configurations",
            "list_configurations_async",
            "update_configuration",
            "update_configuration_from_dict",
            "update_configuration_async",
            "update_configuration_from_dict_async",
            "delete_configuration",
            "delete_configuration_async",
        ]

        # Act & Assert
        for method_name in expected_methods:
            assert hasattr(api, method_name)
            assert callable(getattr(api, method_name))

    def test_method_signatures_are_correct(self, mock_client: Mock) -> None:
        """Test method signatures match expected parameters."""
        # Arrange
        api = ConfigurationsAPI(mock_client)

        # Act & Assert - Check key method signatures

        # Check create_configuration signature
        sig = inspect.signature(api.create_configuration)
        params = list(sig.parameters.keys())
        assert "request" in params
        assert sig.return_annotation == CreateConfigurationResponse

        # Check get_configuration signature
        sig = inspect.signature(api.get_configuration)
        params = list(sig.parameters.keys())
        assert "config_id" in params
        assert sig.return_annotation == Configuration

        # Check list_configurations signature
        sig = inspect.signature(api.list_configurations)
        params = list(sig.parameters.keys())
        assert "project" in params
        assert "limit" in params

        # Check delete_configuration signature
        sig = inspect.signature(api.delete_configuration)
        params = list(sig.parameters.keys())
        assert "config_id" in params
        assert sig.return_annotation == bool
