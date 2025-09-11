"""Unit tests for configurations API."""

from unittest.mock import Mock, patch

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.models import PostConfigurationRequest, PutConfigurationRequest
from honeyhive.models.generated import (
    CallType,
    EnvEnum,
    FunctionCallParams,
    Parameters1,
    Parameters2,
)


class TestConfigurationsAPI:
    """Test configurations API endpoints."""

    @pytest.fixture
    def api_key(self):
        return "test-api-key-12345"

    @pytest.fixture
    def client(self, api_key):
        return HoneyHive(api_key=api_key)

    @pytest.fixture
    def mock_configuration_data(self):
        return {
            "_id": "config-123",
            "project": "test-project",
            "name": "test-config",
            "provider": "openai",
            "parameters": {
                "call_type": "chat",
                "model": "gpt-4",
                "hyperparameters": {"temperature": 0.7},
            },
            "type": "LLM",
            "user_properties": {"team": "test-team"},
        }

    def test_create_configuration_with_model(self, client, mock_configuration_data):
        """Test creating configuration using PostConfigurationRequest model."""
        config_request = PostConfigurationRequest(
            project="test-project",
            name="test-config",
            provider="openai",
            parameters=Parameters2(
                call_type=CallType.chat,
                model="gpt-4",
                hyperparameters={"temperature": 0.7},
                responseFormat={"type": "text"},
                selectedFunctions=[],
                functionCallParams=FunctionCallParams.auto,
                forceFunction={"enabled": False},
            ),
            env=[EnvEnum.prod],
            user_properties={"team": "test-team"},
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "acknowledged": True,
                "insertedId": "config-123",
                "success": True,
            }
            mock_request.return_value = mock_response

            result = client.configurations.create_configuration(config_request)

            # Should return CreateConfigurationResponse, not Configuration
            from honeyhive.api.configurations import CreateConfigurationResponse

            assert isinstance(result, CreateConfigurationResponse)
            assert result.acknowledged is True
            assert result.inserted_id == "config-123"
            assert result.success is True
            mock_request.assert_called_once()

    def test_create_configuration_from_dict(self, client, mock_configuration_data):
        """Test creating configuration from dictionary (legacy method)."""
        config_data = {
            "project": "test-project",
            "name": "test-config",
            "provider": "openai",
            "parameters": {"call_type": "chat", "model": "gpt-4"},
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "acknowledged": True,
                "insertedId": "config-123",
                "success": True,
            }
            mock_request.return_value = mock_response

            result = client.configurations.create_configuration_from_dict(config_data)

            # Should return CreateConfigurationResponse, not Configuration
            from honeyhive.api.configurations import CreateConfigurationResponse

            assert isinstance(result, CreateConfigurationResponse)
            assert result.acknowledged is True
            assert result.inserted_id == "config-123"
            assert result.success is True
            mock_request.assert_called_once()

    def test_get_configuration(self, client, mock_configuration_data):
        """Test getting configuration by ID."""
        config_id = "config-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_configuration_data
            mock_request.return_value = mock_response

            result = client.configurations.get_configuration(config_id)

            # The field_id is mapped to _id in the model
            assert result.field_id == config_id
            assert result.project == "test-project"
            mock_request.assert_called_once_with("GET", f"/configurations/{config_id}")

    def test_list_configurations_without_project(self, client):
        """Test listing configurations without project filter."""
        mock_data = {
            "configurations": [
                {
                    "_id": "config-1",
                    "project": "proj-1",
                    "name": "config-1",
                    "provider": "openai",
                    "type": "LLM",
                    "parameters": {"call_type": "chat", "model": "gpt-4"},
                },
                {
                    "_id": "config-2",
                    "project": "proj-2",
                    "name": "config-2",
                    "provider": "anthropic",
                    "type": "LLM",
                    "parameters": {"call_type": "completion", "model": "claude-3"},
                },
            ]
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.configurations.list_configurations(limit=50)

            assert len(result) == 2
            assert result[0].field_id == "config-1"
            assert result[1].field_id == "config-2"
            mock_request.assert_called_once_with(
                "GET", "/configurations", params={"limit": 50}
            )

    def test_list_configurations_with_project(self, client):
        """Test listing configurations with project filter."""
        mock_data = {
            "configurations": [
                {
                    "field_id": "config-1",
                    "project": "test-project",
                    "name": "config-1",
                    "provider": "openai",
                    "type": "LLM",
                    "parameters": {"call_type": "chat", "model": "gpt-4"},
                }
            ]
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.configurations.list_configurations(
                project="test-project", limit=100
            )

            assert len(result) == 1
            assert result[0].project == "test-project"
            mock_request.assert_called_once_with(
                "GET",
                "/configurations",
                params={"project": "test-project", "limit": 100},
            )

    def test_update_configuration_with_model(self, client, mock_configuration_data):
        """Test updating configuration using PutConfigurationRequest model."""
        config_id = "config-123"
        update_request = PutConfigurationRequest(
            project="test-project",
            name="updated-config",
            provider="anthropic",
            parameters=Parameters1(
                call_type=CallType.completion,
                model="claude-3",
                hyperparameters={"temperature": 0.5},
                responseFormat={"type": "text"},
                selectedFunctions=[],
                functionCallParams=FunctionCallParams.auto,
                forceFunction={"enabled": False},
            ),
            env=[EnvEnum.staging],
            user_properties={"team": "updated-team"},
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_configuration_data
            mock_request.return_value = mock_response

            result = client.configurations.update_configuration(
                config_id, update_request
            )

            assert result.field_id == config_id
            mock_request.assert_called_once()

    def test_delete_configuration_success(self, client):
        """Test successful configuration deletion."""
        config_id = "config-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            result = client.configurations.delete_configuration(config_id)

            assert result is True
            mock_request.assert_called_once_with(
                "DELETE", f"/configurations/{config_id}"
            )

    def test_delete_configuration_failure(self, client):
        """Test failed configuration deletion."""
        config_id = "config-123"

        with patch.object(client, "request") as mock_request:
            mock_request.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                client.configurations.delete_configuration(config_id)

    def test_configurations_async_method_exists(self, client):
        """Test that async methods exist on configurations API for coverage."""
        # Just test that the methods exist - no actual async call
        assert hasattr(client.configurations, "create_configuration_async")
        assert hasattr(client.configurations, "get_configuration_async")
        assert callable(client.configurations.create_configuration_async)

    @pytest.mark.asyncio
    async def test_create_configuration_async(self, client, mock_configuration_data):
        """Test creating configuration asynchronously."""
        config_request = PostConfigurationRequest(
            project="test-project",
            name="test-config",
            provider="openai",
            parameters={"call_type": "chat", "model": "gpt-4"},
            type="LLM",
        )

        with patch.object(client, "request_async") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "acknowledged": True,
                "insertedId": "config-123",
                "success": True,
            }
            mock_request.return_value = mock_response

            result = await client.configurations.create_configuration_async(
                config_request
            )

            # Should return CreateConfigurationResponse, not Configuration
            from honeyhive.api.configurations import CreateConfigurationResponse

            assert isinstance(result, CreateConfigurationResponse)
            assert result.acknowledged is True
            assert result.inserted_id == "config-123"
            assert result.success is True
            mock_request.assert_called_once()
