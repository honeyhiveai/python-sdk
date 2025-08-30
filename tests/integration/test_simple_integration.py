"""Simple integration tests for HoneyHive."""

from unittest.mock import Mock, patch

import pytest

from honeyhive.models.generated import (
    CallType,
    CreateDatapointRequest,
    CreateEventRequest,
    EventType1,
    Parameters2,
    PostConfigurationRequest,
    SessionStartRequest,
)

from ..utils import (
    create_openai_config_request,
    create_session_request,
    mock_api_error_response,
    mock_success_response,
)


class TestSimpleIntegration:
    """Simple integration tests for basic functionality."""

    def test_basic_datapoint_creation(self, integration_client):
        """Test basic datapoint creation workflow."""
        with patch.object(integration_client, "request") as mock_request:
            mock_request.return_value = mock_success_response(
                {"_id": "datapoint-123", "project_id": "test-project"}
            )

            datapoint_request = CreateDatapointRequest(
                project="test-project", inputs={"query": "test query"}
            )

            datapoint_response = integration_client.datapoints.create_datapoint(
                datapoint_request
            )
            assert datapoint_response.field_id == "datapoint-123"

    def test_basic_configuration_creation(self, integration_client):
        """Test basic configuration creation workflow."""
        with patch.object(integration_client, "request") as mock_request:
            mock_request.return_value = mock_success_response(
                {
                    "name": "test-config",
                    "project": "test-project",
                    "provider": "openai",
                    "parameters": {"call_type": "chat", "model": "gpt-4"},
                }
            )

            config_request = create_openai_config_request()

            config_response = integration_client.configurations.create_configuration(
                config_request
            )
            assert config_response.name == "test-config"

    def test_model_serialization_workflow(self):
        """Test that models can be created and serialized."""
        # Test session request
        session_request = create_session_request()

        session_dict = session_request.model_dump(exclude_none=True)
        assert session_dict["project"] == "test-project"
        assert session_dict["session_name"] == "test-session"

        # Test event request
        event_request = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="test-event",
            event_type=EventType1.model,
            config={"model": "gpt-4"},
            inputs={"prompt": "test"},
            duration=100.0,
        )

        event_dict = event_request.model_dump(exclude_none=True)
        assert event_dict["project"] == "test-project"
        assert event_dict["event_type"] == EventType1.model
        assert event_dict["config"]["model"] == "gpt-4"

    def test_error_handling(self, integration_client):
        """Test error handling in integration scenarios."""
        with patch.object(integration_client, "request") as mock_request:
            mock_request.side_effect = mock_api_error_response()

            with pytest.raises(Exception, match="API Error"):
                # Test with a simple method call instead of session creation
                integration_client.datapoints.list_datapoints(limit=1)

    def test_environment_configuration(self, integration_client):
        """Test that environment configuration is properly set."""
        assert integration_client.test_mode is False  # Integration tests use real API
        assert integration_client.base_url == "https://api.honeyhive.ai"

    def test_fixture_availability(self, integration_client, mock_api_responses):
        """Test that all fixtures are properly available."""
        assert integration_client is not None
        assert mock_api_responses is not None
        assert "session" in mock_api_responses
        assert "event" in mock_api_responses
        assert "datapoint" in mock_api_responses
