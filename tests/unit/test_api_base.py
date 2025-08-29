"""Comprehensive tests for HoneyHive API modules."""

from unittest.mock import Mock, patch

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.api.configurations import ConfigurationsAPI
from honeyhive.api.datapoints import DatapointsAPI
from honeyhive.api.datasets import DatasetsAPI
from honeyhive.api.evaluations import EvaluationsAPI
from honeyhive.api.events import (
    BatchCreateEventRequest,
    BatchCreateEventResponse,
    CreateEventResponse,
    EventsAPI,
    UpdateEventRequest,
)
from honeyhive.api.metrics import MetricsAPI
from honeyhive.api.projects import ProjectsAPI
from honeyhive.api.session import SessionAPI, SessionResponse, SessionStartResponse
from honeyhive.api.tools import ToolsAPI
from honeyhive.models import (
    Configuration,
    CreateDatapointRequest,
    CreateDatasetRequest,
    CreateEventRequest,
    CreateProjectRequest,
    CreateRunRequest,
    CreateToolRequest,
    Datapoint,
    Dataset,
    EventFilter,
    Metric,
    PostConfigurationRequest,
    Project,
    SessionStartRequest,
    Tool,
    UpdateToolRequest,
)

# Type: ignore comments for pytest decorators
pytest_mark_asyncio = pytest.mark.asyncio  # type: ignore


class TestSessionAPI:
    """Test Session API functionality."""

    def test_session_api_initialization(self, api_key: str) -> None:
        """Test SessionAPI initialization."""
        client = HoneyHive(api_key=api_key)
        session_api = SessionAPI(client)
        assert session_api.client == client

    def test_start_session(self, api_key: str) -> None:
        """Test starting a session."""
        client = HoneyHive(api_key=api_key)
        session_api = SessionAPI(client)

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {"session_id": "test-session-123"}
            mock_request.return_value = mock_response

            response = session_api.start_session(
                project="test-project", session_name="test-session", source="test"
            )

            assert isinstance(response, SessionStartResponse)
            assert response.session_id == "test-session-123"
            mock_request.assert_called_once()

    @pytest_mark_asyncio  # type: ignore
    async def test_start_session_async(self, api_key: str) -> None:
        """Test starting a session asynchronously."""
        client = HoneyHive(api_key=api_key)
        session_api = SessionAPI(client)

        with patch.object(client, "request_async") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {"session_id": "test-session-123"}
            mock_request.return_value = mock_response

            response = await session_api.start_session_async(
                project="test-project", session_name="test-session", source="test"
            )

            assert isinstance(response, SessionStartResponse)
            assert response.session_id == "test-session-123"
            mock_request.assert_called_once()

    def test_get_session(self, api_key: str) -> None:
        """Test getting a session."""
        client = HoneyHive(api_key=api_key)
        session_api = SessionAPI(client)

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {"event_id": "test-event-123"}
            mock_request.return_value = mock_response

            response = session_api.get_session("test-session-123")

            assert isinstance(response, SessionResponse)
            assert response.event.event_id == "test-event-123"
            mock_request.assert_called_once()

    def test_create_session_with_model(self, api_key: str) -> None:
        """Test creating a session using SessionStartRequest model."""
        client = HoneyHive(api_key=api_key)
        session_api = SessionAPI(client)

        session_request = SessionStartRequest(
            project="test-project", session_name="test-session", source="test"
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {"session_id": "test-session-123"}
            mock_request.return_value = mock_response

            response = session_api.create_session(session_request)

            assert isinstance(response, SessionStartResponse)
            assert response.session_id == "test-session-123"
            mock_request.assert_called_once()
            # Verify the model was serialized correctly
            call_args = mock_request.call_args
            assert "session" in call_args[1]["json"]
            assert call_args[1]["json"]["session"]["project"] == "test-project"

    def test_create_session_from_dict_legacy(self, api_key: str) -> None:
        """Test creating a session using legacy dictionary method."""
        client = HoneyHive(api_key=api_key)
        session_api = SessionAPI(client)

        session_data = {
            "project": "test-project",
            "session_name": "test-session",
            "source": "test",
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {"session_id": "test-session-123"}
            mock_request.return_value = mock_response

            response = session_api.create_session_from_dict(session_data)

            assert isinstance(response, SessionStartResponse)
            assert response.session_id == "test-session-123"
            mock_request.assert_called_once()


class TestEventsAPI:
    """Test Events API functionality."""

    def test_events_api_initialization(self, api_key: str) -> None:
        """Test EventsAPI initialization."""
        client = HoneyHive(api_key=api_key)
        events_api = EventsAPI(client)
        assert events_api.client == client

    def test_create_event(self, api_key: str) -> None:
        """Test creating an event."""
        client = HoneyHive(api_key=api_key)
        events_api = EventsAPI(client)

        event_request = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="test-event",
            event_type="tool",
            config={"model": "test-model"},
            inputs={"prompt": "test prompt"},
            duration=100.0,
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "event_id": "test-event-123",
                "success": True,
            }
            mock_request.return_value = mock_response

            response = events_api.create_event(event_request)

            assert isinstance(response, CreateEventResponse)
            assert response.event_id == "test-event-123"
            assert response.success is True
            mock_request.assert_called_once()

    def test_update_event(self, api_key: str) -> None:
        """Test updating an event."""
        client = HoneyHive(api_key=api_key)
        events_api = EventsAPI(client)

        update_request = UpdateEventRequest(
            event_id="test-event-123", metadata={"test": "value"}
        )

        with patch.object(client, "request") as mock_request:
            mock_request.return_value = Mock()

            events_api.update_event(update_request)

            mock_request.assert_called_once()

    def test_create_event_batch(self, api_key: str) -> None:
        """Test creating multiple events."""
        client = HoneyHive(api_key=api_key)
        events_api = EventsAPI(client)

        events = [
            CreateEventRequest(
                project="test-project",
                source="test",
                event_name="test-event-1",
                event_type="tool",
                config={"model": "test-model-1"},
                inputs={"prompt": "test prompt 1"},
                duration=100.0,
            ),
            CreateEventRequest(
                project="test-project",
                source="test",
                event_name="test-event-2",
                event_type="tool",
                config={"model": "test-model-2"},
                inputs={"prompt": "test prompt 2"},
                duration=150.0,
            ),
        ]

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "event_ids": ["event-1", "event-2"],
                "success": True,
            }
            mock_request.return_value = mock_response

            batch_request = BatchCreateEventRequest(events=events)
            response = events_api.create_event_batch(batch_request)

            assert isinstance(response, BatchCreateEventResponse)
            assert len(response.event_ids) == 2
            assert response.success is True

    def test_create_event_batch_from_list(self, api_key: str) -> None:
        """Test creating multiple events from list using new model-based method."""
        client = HoneyHive(api_key=api_key)
        events_api = EventsAPI(client)

        events = [
            CreateEventRequest(
                project="test-project",
                source="test",
                event_name="test-event-1",
                event_type="tool",
                config={"model": "test-model-1"},
                inputs={"prompt": "test prompt 1"},
                duration=100.0,
            ),
            CreateEventRequest(
                project="test-project",
                source="test",
                event_name="test-event-2",
                event_type="tool",
                config={"model": "test-model-2"},
                inputs={"prompt": "test prompt 2"},
                duration=150.0,
            ),
        ]

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "event_ids": ["event-1", "event-2"],
                "success": True,
            }
            mock_request.return_value = mock_response

            response = events_api.create_event_batch_from_list(events)

            assert isinstance(response, BatchCreateEventResponse)
            assert len(response.event_ids) == 2
            assert response.success is True

    def test_list_events_with_filter_model(self, api_key: str) -> None:
        """Test listing events using EventFilter model."""
        client = HoneyHive(api_key=api_key)
        events_api = EventsAPI(client)

        event_filter = EventFilter(
            field="metadata.demo_type", value="api_client_models"
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "events": [
                    {"event_id": "event-1", "event_name": "Event 1"},
                    {"event_id": "event-2", "event_name": "Event 2"},
                ]
            }
            mock_request.return_value = mock_response

            events = events_api.list_events(event_filter, limit=50)

            assert len(events) == 2
            mock_request.assert_called_once()
            # Verify filter parameters were converted correctly
            call_args = mock_request.call_args
            assert call_args[1]["params"]["field"] == "metadata.demo_type"
            assert call_args[1]["params"]["value"] == "api_client_models"


class TestToolsAPI:
    """Test Tools API functionality."""

    def test_tools_api_initialization(self, api_key: str) -> None:
        """Test ToolsAPI initialization."""
        client = HoneyHive(api_key=api_key)
        tools_api = ToolsAPI(client)
        assert tools_api.client == client

    def test_create_tool(self, api_key: str) -> None:
        """Test creating a tool."""
        client = HoneyHive(api_key=api_key)
        tools_api = ToolsAPI(client)

        tool_request = CreateToolRequest(
            task="test-project",
            name="test-tool",
            description="A test tool",
            parameters={"param1": "value1"},
            type="function",
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "field_id": "tool-123",
                "name": "test-tool",
                "task": "test-project",
                "parameters": {"param1": "value1"},
                "tool_type": "function",
            }
            mock_request.return_value = mock_response

            response = tools_api.create_tool(tool_request)

            assert isinstance(response, Tool)
            assert response.name == "test-tool"
            mock_request.assert_called_once()

    def test_get_tool(self, api_key: str) -> None:
        """Test getting a tool."""
        client = HoneyHive(api_key=api_key)
        tools_api = ToolsAPI(client)

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "_id": "tool-123",
                "name": "test-tool",
                "task": "test-project",
                "parameters": {"param1": "value1"},
                "tool_type": "function",
            }
            mock_request.return_value = mock_response

            response = tools_api.get_tool("tool-123")

            assert isinstance(response, Tool)
            assert response.field_id == "tool-123"
            mock_request.assert_called_once()

    def test_list_tools(self, api_key: str) -> None:
        """Test listing tools."""
        client = HoneyHive(api_key=api_key)
        tools_api = ToolsAPI(client)

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "tools": [
                    {
                        "id": "tool-1",
                        "name": "tool-1",
                        "task": "test-project",
                        "parameters": {"param1": "value1"},
                        "tool_type": "function",
                    },
                    {
                        "id": "tool-2",
                        "name": "tool-2",
                        "task": "test-project",
                        "parameters": {"param2": "value2"},
                        "tool_type": "function",
                    },
                ]
            }
            mock_request.return_value = mock_response

            response = tools_api.list_tools(project="test-project")

            assert len(response) == 2
            assert all(isinstance(tool, Tool) for tool in response)
            mock_request.assert_called_once()

    def test_update_tool(self, api_key: str) -> None:
        """Test updating a tool."""
        client = HoneyHive(api_key=api_key)
        tools_api = ToolsAPI(client)

        update_request = UpdateToolRequest(
            id="tool-123",
            name="updated-tool",
            description="Updated description",
            parameters={"param1": "updated-value"},
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "field_id": "tool-123",
                "name": "updated-tool",
                "task": "test-project",
                "parameters": {"param1": "updated-value"},
                "tool_type": "function",
            }
            mock_request.return_value = mock_response

            response = tools_api.update_tool("tool-123", update_request)

            assert isinstance(response, Tool)
            assert response.name == "updated-tool"
            mock_request.assert_called_once()

    def test_delete_tool(self, api_key: str) -> None:
        """Test deleting a tool."""
        client = HoneyHive(api_key=api_key)
        tools_api = ToolsAPI(client)

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            result = tools_api.delete_tool("tool-123")

            assert result is True
            mock_request.assert_called_once()


class TestDatapointsAPI:
    """Test Datapoints API functionality."""

    def test_datapoints_api_initialization(self, api_key: str) -> None:
        """Test DatapointsAPI initialization."""
        client = HoneyHive(api_key=api_key)
        datapoints_api = DatapointsAPI(client)
        assert datapoints_api.client == client

    def test_create_datapoint(self, api_key: str) -> None:
        """Test creating a datapoint."""
        client = HoneyHive(api_key=api_key)
        datapoints_api = DatapointsAPI(client)

        datapoint_request = CreateDatapointRequest(
            project="test-project", inputs={"key": "value"}
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "_id": "dp-123",
                "inputs": {"key": "value"},
                "project_id": "test-project",
            }
            mock_request.return_value = mock_response

            response = datapoints_api.create_datapoint(datapoint_request)

            assert isinstance(response, Datapoint)
            assert response.field_id == "dp-123"
            mock_request.assert_called_once()

    def test_list_datapoints(self, api_key: str) -> None:
        """Test listing datapoints."""
        client = HoneyHive(api_key=api_key)
        datapoints_api = DatapointsAPI(client)

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "datapoints": [
                    {"id": "dp-1", "data": {"key": "value1"}},
                    {"id": "dp-2", "data": {"key": "value2"}},
                ]
            }
            mock_request.return_value = mock_response

            response = datapoints_api.list_datapoints(project="test-project")

            assert len(response) == 2
            assert all(isinstance(dp, Datapoint) for dp in response)
            mock_request.assert_called_once()


class TestDatasetsAPI:
    """Test Datasets API functionality."""

    def test_datasets_api_initialization(self, api_key: str) -> None:
        """Test DatasetsAPI initialization."""
        client = HoneyHive(api_key=api_key)
        datasets_api = DatasetsAPI(client)
        assert datasets_api.client == client

    def test_create_dataset(self, api_key: str) -> None:
        """Test creating a dataset."""
        client = HoneyHive(api_key=api_key)
        datasets_api = DatasetsAPI(client)

        dataset_request = CreateDatasetRequest(
            project="test-project", name="test-dataset", description="A test dataset"
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {"id": "ds-123", "name": "test-dataset"}
            mock_request.return_value = mock_response

            response = datasets_api.create_dataset(dataset_request)

            assert isinstance(response, Dataset)
            assert response.name == "test-dataset"
            mock_request.assert_called_once()


class TestConfigurationsAPI:
    """Test Configurations API functionality."""

    def test_configurations_api_initialization(self, api_key: str) -> None:
        """Test ConfigurationsAPI initialization."""
        client = HoneyHive(api_key=api_key)
        configs_api = ConfigurationsAPI(client)
        assert configs_api.client == client

    def test_create_configuration(self, api_key: str) -> None:
        """Test creating a configuration."""
        client = HoneyHive(api_key=api_key)
        configs_api = ConfigurationsAPI(client)

        from honeyhive.models.generated import Parameters2

        config_request = PostConfigurationRequest(
            project="test-project",
            provider="test-provider",
            name="test-config",
            parameters=Parameters2(call_type="chat", model="gpt-4"),
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "_id": "cfg-123",
                "name": "test-config",
                "project": "test-project",
                "provider": "test-provider",
                "parameters": {"call_type": "chat", "model": "gpt-4"},
            }
            mock_request.return_value = mock_response

            response = configs_api.create_configuration(config_request)

            assert isinstance(response, Configuration)
            assert response.name == "test-config"
            mock_request.assert_called_once()


class TestProjectsAPI:
    """Test Projects API functionality."""

    def test_projects_api_initialization(self, api_key: str) -> None:
        """Test ProjectsAPI initialization."""
        client = HoneyHive(api_key=api_key)
        projects_api = ProjectsAPI(client)
        assert projects_api.client == client

    def test_create_project(self, api_key: str) -> None:
        """Test creating a project."""
        client = HoneyHive(api_key=api_key)
        projects_api = ProjectsAPI(client)

        project_request = CreateProjectRequest(
            name="test-project", description="A test project"
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "id": "proj-123",
                "name": "test-project",
                "description": "A test project",
            }
            mock_request.return_value = mock_response

            response = projects_api.create_project(project_request)

            assert isinstance(response, Project)
            assert response.name == "test-project"
            mock_request.assert_called_once()


class TestMetricsAPI:
    """Test Metrics API functionality."""

    def test_metrics_api_initialization(self, api_key: str) -> None:
        """Test MetricsAPI initialization."""
        client = HoneyHive(api_key=api_key)
        metrics_api = MetricsAPI(client)
        assert metrics_api.client == client

    def test_create_metric(self, api_key: str) -> None:
        """Test creating a metric."""
        client = HoneyHive(api_key=api_key)
        metrics_api = MetricsAPI(client)

        metric = Metric(
            name="test-metric",
            description="A test metric",
            task="test-task",
            type="custom",
            return_type="float",
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "_id": "metric-123",
                "name": "test-metric",
                "description": "A test metric",
                "task": "test-task",
                "type": "custom",
                "return_type": "float",
            }
            mock_request.return_value = mock_response

            response = metrics_api.create_metric(metric)

            assert isinstance(response, Metric)
            assert response.name == "test-metric"
            mock_request.assert_called_once()


class TestEvaluationsAPI:
    """Test Evaluations API functionality."""

    def test_evaluations_api_initialization(self, api_key: str) -> None:
        """Test EvaluationsAPI initialization."""
        client = HoneyHive(api_key=api_key)
        evaluations_api = EvaluationsAPI(client)
        assert evaluations_api.client == client

    def test_create_evaluation_run(self, api_key: str) -> None:
        """Test creating an evaluation run."""
        client = HoneyHive(api_key=api_key)
        evaluations_api = EvaluationsAPI(client)

        from uuid import uuid4

        from honeyhive.models.generated import UUIDType

        run_request = CreateRunRequest(
            project="test-project",
            name="test-evaluation-run",
            event_ids=[UUIDType(uuid4()), UUIDType(uuid4())],
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "evaluation": {"run_id": "run-123"},
                "run_id": "run-123",
            }
            mock_request.return_value = mock_response

            # Mock the CreateRunResponse creation to avoid UUIDType validation issues
            with patch(
                "honeyhive.api.evaluations.CreateRunResponse"
            ) as mock_response_class:
                mock_response_instance = Mock()
                mock_response_instance.run_id = "run-123"
                mock_response_class.return_value = mock_response_instance

                response = evaluations_api.create_run(run_request)

                assert response.run_id == "run-123"
                mock_request.assert_called_once()


class TestAPIErrorHandling:
    """Test API error handling."""

    def test_api_error_handling(self, api_key: str) -> None:
        """Test API error handling."""
        client = HoneyHive(api_key=api_key)
        session_api = SessionAPI(client)

        with patch.object(client, "request") as mock_request:
            mock_request.side_effect = Exception("API Error")

            with pytest.raises(Exception, match="API Error"):
                session_api.start_session(
                    project="test-project", session_name="test-session", source="test"
                )

    def test_api_invalid_response(self, api_key: str) -> None:
        """Test API invalid response handling."""
        client = HoneyHive(api_key=api_key)
        session_api = SessionAPI(client)

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.side_effect = Exception("Invalid JSON")
            mock_request.return_value = mock_response

            with pytest.raises(Exception, match="Invalid JSON"):
                session_api.start_session(
                    project="test-project", session_name="test-session", source="test"
                )


class TestAPIPerformance:
    """Test API performance characteristics."""

    def test_api_batch_operations(self, api_key: str) -> None:
        """Test API batch operations performance."""
        client = HoneyHive(api_key=api_key)
        events_api = EventsAPI(client)

        # Create many events
        events = [
            CreateEventRequest(
                project="test-project",
                source="test",
                event_name=f"test-event-{i}",
                event_type="tool",
                config={"model": f"test-model-{i}"},
                inputs={"prompt": f"test prompt {i}"},
                duration=100.0 + i,
            )
            for i in range(100)
        ]

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "event_ids": [f"event-{i}" for i in range(100)],
                "success": True,
            }
            mock_request.return_value = mock_response

            import time

            start_time = time.time()

            batch_request = BatchCreateEventRequest(events=events)
            response = events_api.create_event_batch(batch_request)

            end_time = time.time()
            duration = end_time - start_time

            # Should complete in reasonable time
            assert duration < 1.0
            assert len(response.event_ids) == 100
            assert response.success is True
