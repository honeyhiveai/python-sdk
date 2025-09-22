"""Unit tests for API workflows in HoneyHive."""

import uuid
from typing import Any, Dict
from unittest.mock import Mock

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.models.generated import (
    CreateDatapointRequest,
    CreateEventRequest,
    CreateRunRequest,
    CreateToolRequest,
    EventType1,
    Type3,
    UUIDType,
)
from tests.utils import (
    create_openai_config_request,
    create_session_request,
)


class TestAPIWorkflows:
    """Unit tests for API workflows."""

    @pytest.fixture
    def mock_client(self) -> Mock:
        """Create a mock HoneyHive client for unit testing."""
        client = Mock(spec=HoneyHive)
        # Configure nested attributes for API endpoints
        client.sessions = Mock()
        client.events = Mock()
        client.datapoints = Mock()
        client.configurations = Mock()
        client.tools = Mock()
        client.evaluations = Mock()
        return client

    @pytest.fixture
    def mock_responses(self) -> Dict[str, Any]:
        """Mock API response data for unit tests."""
        return {
            "session": {
                "session_id": "test-session-123",
                "project": "test-project",
                "session_name": "test-session",
                "source": "test",
                "status": "active",
            },
            "event": {
                "event_id": "test-event-123",
                "project": "test-project",
                "event_name": "test-event",
                "event_type": "model",
                "success": True,
            },
            "datapoint": {
                "id": "test-datapoint-123",
                "project": "test-project",
                "inputs": {"query": "test query"},
                "ground_truth": {},
            },
            "configuration": {
                "name": "test-config",
                "project": "test-project",
                "provider": "openai",
                "parameters": {"model": "gpt-4"},
            },
            "tool": {
                "name": "tool-integration-123",
                "task": "test-project",
                "description": "Test tool",
                "type": "function",
            },
            "evaluation": {
                "run_id": "12345678-1234-1234-1234-123456789abc",
                "project": "test-project",
                "name": "test-evaluation",
                "status": "completed",
            },
        }

    def test_session_creation_workflow(
        self, mock_client: Any, mock_responses: Any
    ) -> None:
        """Test session creation workflow with mocked client."""
        # Setup mock
        mock_client.sessions.create_session.return_value = Mock(
            session_id=mock_responses["session"]["session_id"]
        )

        # Execute
        session_request = create_session_request()
        session_response = mock_client.sessions.create_session(session_request)

        # Verify
        assert session_response.session_id == mock_responses["session"]["session_id"]
        mock_client.sessions.create_session.assert_called_once_with(session_request)

    def test_event_creation_workflow(
        self, mock_client: Any, mock_responses: Any
    ) -> None:
        """Test event creation workflow with mocked client."""
        # Setup mock
        mock_client.events.create_event.return_value = Mock(
            event_id=mock_responses["event"]["event_id"]
        )

        # Create request
        event_request = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="test-event",
            event_type=EventType1.model,
            config={"model": "gpt-4"},
            inputs={"prompt": "test prompt"},
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

        # Execute
        event_response = mock_client.events.create_event(event_request)

        # Verify
        assert event_response.event_id == mock_responses["event"]["event_id"]
        mock_client.events.create_event.assert_called_once_with(event_request)

    def test_datapoint_creation_workflow(  # pylint: disable=unused-argument
        self, mock_client: Any, mock_responses: Any
    ) -> None:
        """Test datapoint creation workflow with mocked client."""
        # Setup mock
        mock_datapoint = Mock()
        mock_datapoint.inputs = {"query": "test query"}
        mock_client.datapoints.create_datapoint.return_value = mock_datapoint

        # Create request
        datapoint_request = CreateDatapointRequest(
            project="test-project",
            inputs={"query": "test query"},
            history=[],
            ground_truth={},
            linked_event=None,
            linked_datasets=[],
            metadata={},
        )

        # Execute
        datapoint_response = mock_client.datapoints.create_datapoint(datapoint_request)

        # Verify
        assert datapoint_response is not None
        assert hasattr(datapoint_response, "inputs")
        assert datapoint_response.inputs == {"query": "test query"}
        mock_client.datapoints.create_datapoint.assert_called_once_with(
            datapoint_request
        )

    def test_configuration_workflow(
        self, mock_client: Any, mock_responses: Any
    ) -> None:
        """Test configuration creation workflow with mocked client."""
        # Setup mock
        mock_config = Mock()
        mock_config.name = mock_responses["configuration"]["name"]
        mock_client.configurations.create_configuration.return_value = mock_config

        # Create request
        config_request = create_openai_config_request(
            "test-project", "test-config"  # Use positional args for compatibility
        )

        # Execute
        config_response = mock_client.configurations.create_configuration(
            config_request
        )

        # Verify
        assert config_response.name == mock_responses["configuration"]["name"]
        mock_client.configurations.create_configuration.assert_called_once_with(
            config_request
        )

    def test_tool_creation_workflow(  # pylint: disable=unused-argument
        self, mock_client: Any, mock_responses: Any
    ) -> None:
        """Test tool creation workflow with mocked client."""
        # Setup mock
        mock_tool = Mock()
        mock_tool.name = "tool-integration-123"
        mock_client.tools.create_tool.return_value = mock_tool

        # Create request
        tool_request = CreateToolRequest(
            task="test-project",
            name="test-tool",
            description="Test tool for unit testing",
            parameters={"test": True},
            type=Type3.function,
        )

        # Execute
        tool_response = mock_client.tools.create_tool(tool_request)

        # Verify
        assert tool_response is not None
        assert hasattr(tool_response, "name")
        assert tool_response.name == "tool-integration-123"
        mock_client.tools.create_tool.assert_called_once_with(tool_request)

    def test_evaluation_workflow(self, mock_client: Any) -> None:
        """Test evaluation run workflow with mocked client."""
        # Setup mock
        mock_client.evaluations.create_run.return_value = Mock(
            run_id="12345678-1234-1234-1234-123456789abc"
        )

        # Create request
        run_request = CreateRunRequest(
            project="test-project",
            name="test-evaluation",
            event_ids=[UUIDType(uuid.UUID("12345678-1234-1234-1234-123456789abc"))],
            dataset_id=None,
            datapoint_ids=[],
            configuration={"metrics": ["accuracy", "precision"]},
            metadata={},
            status=None,
        )

        # Execute
        run_response = mock_client.evaluations.create_run(run_request)

        # Verify
        assert str(run_response.run_id) == "12345678-1234-1234-1234-123456789abc"
        mock_client.evaluations.create_run.assert_called_once_with(run_request)

    def test_list_operations_workflow(self, mock_client: Any) -> None:
        """Test list operations workflow with mocked client."""
        # Setup mock
        mock_config1 = Mock()
        mock_config1.name = "config-1"
        mock_config1.project = "test-project"

        mock_config2 = Mock()
        mock_config2.name = "config-2"
        mock_config2.project = "test-project"

        mock_configs = [mock_config1, mock_config2]
        mock_client.configurations.list_configurations.return_value = mock_configs

        # Execute
        configs = mock_client.configurations.list_configurations(limit=10)

        # Verify
        assert len(configs) == 2
        assert configs[0].name == "config-1"
        assert configs[1].name == "config-2"
        mock_client.configurations.list_configurations.assert_called_once_with(limit=10)

    @pytest.mark.error_handling
    def test_error_handling_workflow(self, mock_client: Any) -> None:
        """Test error handling in workflows with mocked client."""
        # Setup mock to raise exception
        mock_client.sessions.create_session.side_effect = Exception("API Error")

        # Execute and verify exception
        with pytest.raises(Exception, match="API Error"):
            mock_client.sessions.create_session(create_session_request())

        mock_client.sessions.create_session.assert_called_once()

    def test_async_workflow(self, mock_client: Any, mock_responses: Any) -> None:
        """Test async API workflow with mocked client."""
        # Setup mock
        mock_client.sessions.start_session.return_value = Mock(
            session_id=mock_responses["session"]["session_id"]
        )

        # Execute
        session_response = mock_client.sessions.start_session(
            project="test-project",
            session_name="test-session",
            source="test",
        )

        # Verify
        assert session_response.session_id == mock_responses["session"]["session_id"]
        mock_client.sessions.start_session.assert_called_once_with(
            project="test-project",
            session_name="test-session",
            source="test",
        )
