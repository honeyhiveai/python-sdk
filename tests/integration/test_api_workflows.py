"""API workflow integration tests for HoneyHive."""

from unittest.mock import Mock, patch

import pytest

from honeyhive.models.generated import (
    CallType,
    CreateDatapointRequest,
    CreateEventRequest,
    CreateRunRequest,
    CreateToolRequest,
    EventType1,
    Parameters2,
    PostConfigurationRequest,
    SessionStartRequest,
    Type3,
    UUIDType,
)

from ..utils import (
    create_openai_config_request,
    create_session_request,
    mock_api_error_response,
    mock_success_response,
)


class TestAPIWorkflows:
    """Integration tests for API workflows."""

    def test_session_creation_workflow(self, integration_client, mock_api_responses):
        """Test session creation workflow."""
        with patch.object(integration_client, "request") as mock_request:
            mock_request.return_value = mock_success_response(
                mock_api_responses["session"]
            )

            session_request = create_session_request()

            session_response = integration_client.sessions.create_session(
                session_request
            )
            assert session_response.session_id == "session-integration-123"

    def test_event_creation_workflow(self, integration_client, mock_api_responses):
        """Test event creation workflow."""
        with patch.object(integration_client, "request") as mock_request:
            mock_request.return_value = mock_success_response(
                mock_api_responses["event"]
            )

            event_request = CreateEventRequest(
                project="integration-test-project",
                source="integration-test",
                event_name="integration-event",
                event_type=EventType1.model,
                config={"model": "gpt-4"},
                inputs={"prompt": "integration test"},
                duration=150.0,
                event_id="test-event-id",
                session_id="test-session-id",
                parent_id="test-parent-id",
                children_ids=[],
                outputs={},
                error=None,
                start_time=None,
                end_time=None,
                metadata={},
                feedback={},
                metrics={},
                user_properties={},
            )

            event_response = integration_client.events.create_event(event_request)
            assert event_response.event_id == "event-integration-123"
            assert event_response.success is True

    def test_datapoint_creation_workflow(self, integration_client, mock_api_responses):
        """Test datapoint creation workflow."""
        with patch.object(integration_client, "request") as mock_request:
            mock_request.return_value = mock_success_response(
                mock_api_responses["datapoint"]
            )

            datapoint_request = CreateDatapointRequest(
                project="integration-test-project",
                inputs={"query": "integration test query"},
                history=[],
                ground_truth={},
                linked_event=None,
                linked_datasets=[],
                metadata={},
            )

            datapoint_response = integration_client.datapoints.create_datapoint(
                datapoint_request
            )
            assert datapoint_response.field_id == "datapoint-integration-123"

    def test_configuration_workflow(self, integration_client, mock_api_responses):
        """Test configuration creation workflow."""
        with patch.object(integration_client, "request") as mock_request:
            mock_request.return_value = mock_success_response(
                mock_api_responses["configuration"]
            )

            config_request = create_openai_config_request(
                project="integration-test-project", name="integration-config"
            )

            config_response = integration_client.configurations.create_configuration(
                config_request
            )
            assert config_response.name == "config-integration-123"

    def test_tool_creation_workflow(self, integration_client, mock_api_responses):
        """Test tool creation workflow."""
        with patch.object(integration_client, "request") as mock_request:
            mock_request.return_value = mock_success_response(
                mock_api_responses["tool"]
            )

            tool_request = CreateToolRequest(
                task="integration-test-project",
                name="integration-tool",
                description="Test tool for integration",
                parameters={"test": True},
                type=Type3.function,
            )

            tool_response = integration_client.tools.create_tool(tool_request)
            assert tool_response.field_id == "tool-integration-123"

    def test_evaluation_workflow(self, integration_client, mock_api_responses):
        """Test evaluation run workflow."""
        with patch.object(integration_client, "request") as mock_request:
            mock_request.return_value = mock_success_response(
                mock_api_responses["evaluation"]
            )

            # Mock UUID creation
            with patch("uuid.uuid4") as mock_uuid:
                mock_uuid.return_value = "test-uuid-123"

                run_request = CreateRunRequest(
                    project="integration-test-project",
                    name="integration-evaluation",
                    event_ids=[UUIDType("12345678-1234-1234-1234-123456789abc")],
                    dataset_id=None,
                    datapoint_ids=[],
                    configuration={"metrics": ["accuracy", "precision"]},
                    metadata={},
                    status=None,
                )

                run_response = integration_client.evaluations.create_run(run_request)
                assert (
                    str(run_response.run_id) == "12345678-1234-1234-1234-123456789abc"
                )

    def test_list_operations_workflow(self, integration_client):
        """Test list operations workflow."""
        with patch.object(integration_client, "request") as mock_request:
            # Mock list responses
            mock_request.return_value = mock_success_response(
                {
                    "configurations": [
                        {
                            "name": "config-1",
                            "project": "test-project",
                            "provider": "openai",
                            "parameters": {"call_type": "chat", "model": "gpt-4"},
                        },
                        {
                            "name": "config-2",
                            "project": "test-project",
                            "provider": "anthropic",
                            "parameters": {"call_type": "chat", "model": "claude-3"},
                        },
                    ]
                }
            )

            configs = integration_client.configurations.list_configurations(limit=10)
            assert len(configs) == 2
            assert configs[0].name == "config-1"
            assert configs[1].name == "config-2"

    @pytest.mark.error_handling
    def test_error_handling_workflow(self, integration_client):
        """Test error handling in workflows."""
        with patch.object(integration_client, "request") as mock_request:
            mock_request.side_effect = mock_api_error_response()

            with pytest.raises(Exception, match="API Error"):
                integration_client.sessions.create_session(create_session_request())

    def test_async_workflow(self, integration_client, mock_api_responses):
        """Test async API workflow."""
        with patch.object(integration_client, "request") as mock_request:
            mock_request.return_value = mock_success_response(
                mock_api_responses["session"]
            )

            session_response = integration_client.sessions.start_session(
                project="integration-test-project",
                session_name="test-session",
                source="integration-test",
            )
            assert session_response.session_id == "session-integration-123"
