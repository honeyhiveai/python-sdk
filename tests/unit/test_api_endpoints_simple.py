"""Simplified tests for HoneyHive API endpoints."""

from unittest.mock import Mock, patch

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.models import (
    CreateDatapointRequest,
    CreateDatasetRequest,
    CreateEventRequest,
    CreateProjectRequest,
    CreateToolRequest,
    EventFilter,
    PostConfigurationRequest,
    PutConfigurationRequest,
)
from honeyhive.models.generated import (
    CallType,
    EnvEnum,
    EventType1,
    FunctionCallParams,
    Parameters1,
    Parameters2,
    PipelineType,
    Type3,
    Type4,
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
            mock_response.json.return_value = mock_configuration_data
            mock_request.return_value = mock_response

            result = client.configurations.create_configuration(config_request)

            assert result.project == "test-project"
            assert result.name == "test-config"
            assert result.provider == "openai"
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
            mock_response.json.return_value = mock_configuration_data
            mock_request.return_value = mock_response

            result = client.configurations.create_configuration_from_dict(config_data)

            assert result.project == "test-project"
            assert result.name == "test-config"
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

            result = client.configurations.delete_configuration(config_id)

            assert result is False


class TestEventsAPI:
    """Test events API endpoints."""

    @pytest.fixture
    def api_key(self):
        return "test-api-key-12345"

    @pytest.fixture
    def client(self, api_key):
        return HoneyHive(api_key=api_key)

    @pytest.fixture
    def mock_event_response(self):
        return {"event_id": "event-123", "success": True}

    def test_create_event_with_model(self, client, mock_event_response):
        """Test creating event using CreateEventRequest model."""
        event_request = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="test-event",
            event_type=EventType1.model,
            config={"model": "gpt-4"},
            inputs={"prompt": "test prompt"},
            duration=100.0,
            metadata={"version": "1.0"},
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_event_response
            mock_request.return_value = mock_response

            result = client.events.create_event(event_request)

            assert result.event_id == "event-123"
            assert result.success is True
            mock_request.assert_called_once()

    def test_create_event_from_dict(self, client, mock_event_response):
        """Test creating event from dictionary (legacy method)."""
        event_data = {
            "project": "test-project",
            "source": "test",
            "event_name": "test-event",
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_event_response
            mock_request.return_value = mock_response

            result = client.events.create_event_from_dict(event_data)

            assert result.event_id == "event-123"
            assert result.success is True
            mock_request.assert_called_once()

    def test_delete_event_success(self, client):
        """Test successful event deletion."""
        event_id = "event-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            result = client.events.delete_event(event_id)

            assert result is True
            mock_request.assert_called_once_with("DELETE", f"/events/{event_id}")

    def test_delete_event_failure(self, client):
        """Test failed event deletion."""
        event_id = "event-123"

        with patch.object(client, "request") as mock_request:
            mock_request.side_effect = Exception("API Error")

            result = client.events.delete_event(event_id)

            assert result is False

    def test_list_events_with_filter(self, client):
        """Test listing events with EventFilter."""
        mock_data = {
            "events": [
                {"project_id": "proj-1", "event_name": "event1"},
                {"project_id": "proj-2", "event_name": "event2"},
            ]
        }

        event_filter = EventFilter(field="project", value="test-project")

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.events.list_events(event_filter, limit=50)

            assert len(result) == 2
            assert result[0].project_id == "proj-1"
            assert result[1].project_id == "proj-2"
            mock_request.assert_called_once()

    def test_list_events_from_dict(self, client):
        """Test listing events from filter dictionary."""
        mock_data = {"events": [{"project_id": "test-project", "event_name": "event1"}]}

        event_filter = {"project": "test-project"}

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.events.list_events_from_dict(event_filter, limit=100)

            assert len(result) == 1
            assert result[0].project_id == "test-project"
            mock_request.assert_called_once()


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

            result = client.datasets.list_datasets(limit=50)

            assert len(result) == 2
            assert result[0].name == "dataset-1"
            assert result[1].name == "dataset-2"
            mock_request.assert_called_once_with(
                "GET", "/datasets", params={"limit": 50}
            )

    def test_list_datasets_with_project(self, client):
        """Test listing datasets with project filter."""
        mock_data = {"datasets": [{"project": "test-project", "name": "dataset-1"}]}

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.datasets.list_datasets(project="test-project", limit=100)

            assert len(result) == 1
            assert result[0].project == "test-project"
            mock_request.assert_called_once_with(
                "GET", "/datasets", params={"project": "test-project", "limit": 100}
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

            result = client.datasets.delete_dataset(dataset_id)

            assert result is False


class TestProjectsAPI:
    """Test projects API endpoints."""

    @pytest.fixture
    def api_key(self):
        return "test-api-key-12345"

    @pytest.fixture
    def client(self, api_key):
        return HoneyHive(api_key=api_key)

    @pytest.fixture
    def mock_project_data(self):
        return {
            "id": "project-123",
            "name": "test-project",
            "description": "Test project",
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z",
        }

    def test_create_project_with_model(self, client, mock_project_data):
        """Test creating project using CreateProjectRequest model."""
        project_request = CreateProjectRequest(
            name="test-project", description="Test project"
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_project_data
            mock_request.return_value = mock_response

            result = client.projects.create_project(project_request)

            assert result.name == "test-project"
            assert result.description == "Test project"
            mock_request.assert_called_once()

    def test_create_project_from_dict(self, client, mock_project_data):
        """Test creating project from dictionary (legacy method)."""
        project_data = {"name": "test-project", "description": "Test project"}

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_project_data
            mock_request.return_value = mock_response

            result = client.projects.create_project_from_dict(project_data)

            assert result.name == "test-project"
            assert result.description == "Test project"
            mock_request.assert_called_once()

    def test_get_project(self, client, mock_project_data):
        """Test getting project by ID."""
        project_id = "project-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_project_data
            mock_request.return_value = mock_response

            result = client.projects.get_project(project_id)

            assert result.id == project_id
            assert result.name == "test-project"
            mock_request.assert_called_once_with("GET", f"/projects/{project_id}")

    def test_list_projects(self, client):
        """Test listing projects."""
        mock_data = {
            "projects": [
                {"id": "proj-1", "name": "project-1", "description": "Project 1"},
                {"id": "proj-2", "name": "project-2", "description": "Project 2"},
            ]
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.projects.list_projects(limit=50)

            assert len(result) == 2
            assert result[0].name == "project-1"
            assert result[1].name == "project-2"
            mock_request.assert_called_once_with(
                "GET", "/projects", params={"limit": 50}
            )

    def test_delete_project_success(self, client):
        """Test successful project deletion."""
        project_id = "project-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            result = client.projects.delete_project(project_id)

            assert result is True
            mock_request.assert_called_once_with("DELETE", f"/projects/{project_id}")

    def test_delete_project_failure(self, client):
        """Test failed project deletion."""
        project_id = "project-123"

        with patch.object(client, "request") as mock_request:
            mock_request.side_effect = Exception("API Error")

            result = client.projects.delete_project(project_id)

            assert result is False


class TestDatapointsAPI:
    """Test datapoints API endpoints."""

    @pytest.fixture
    def api_key(self):
        return "test-api-key-12345"

    @pytest.fixture
    def client(self, api_key):
        return HoneyHive(api_key=api_key)

    @pytest.fixture
    def mock_datapoint_data(self):
        return {
            "_id": "datapoint-123",
            "project_id": "test-project",
            "inputs": {"query": "test query"},
            "history": [{"role": "user", "content": "test"}],
            "ground_truth": {"answer": "test answer"},
            "metadata": {"version": "1.0"},
        }

    def test_create_datapoint_with_model(self, client, mock_datapoint_data):
        """Test creating datapoint using CreateDatapointRequest model."""
        datapoint_request = CreateDatapointRequest(
            project="test-project",
            inputs={"query": "test query"},
            history=[{"role": "user", "content": "test"}],
            ground_truth={"answer": "test answer"},
            metadata={"version": "1.0"},
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_datapoint_data
            mock_request.return_value = mock_response

            result = client.datapoints.create_datapoint(datapoint_request)

            assert result.project_id == "test-project"
            assert result.inputs["query"] == "test query"
            mock_request.assert_called_once()

    def test_create_datapoint_from_dict(self, client, mock_datapoint_data):
        """Test creating datapoint from dictionary (legacy method)."""
        datapoint_data = {"project": "test-project", "inputs": {"query": "test query"}}

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_datapoint_data
            mock_request.return_value = mock_response

            result = client.datapoints.create_datapoint_from_dict(datapoint_data)

            assert result.project_id == "test-project"
            mock_request.assert_called_once()

    def test_get_datapoint(self, client, mock_datapoint_data):
        """Test getting datapoint by ID."""
        datapoint_id = "datapoint-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_datapoint_data
            mock_request.return_value = mock_response

            result = client.datapoints.get_datapoint(datapoint_id)

            # The field_id is mapped to _id in the model
            assert result.field_id == datapoint_id
            assert result.project_id == "test-project"
            mock_request.assert_called_once_with("GET", f"/datapoints/{datapoint_id}")

    def test_list_datapoints_without_project(self, client):
        """Test listing datapoints without project filter."""
        mock_data = {
            "datapoints": [
                {"project_id": "proj-1", "inputs": {"query": "query1"}},
                {"project_id": "proj-2", "inputs": {"query": "query2"}},
            ]
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.datapoints.list_datapoints(limit=50)

            assert len(result) == 2
            assert result[0].project_id == "proj-1"
            assert result[1].project_id == "proj-2"
            mock_request.assert_called_once_with(
                "GET", "/datapoints", params={"limit": 50}
            )

    def test_list_datapoints_with_project(self, client):
        """Test listing datapoints with project filter."""
        mock_data = {
            "datapoints": [
                {
                    "field_id": "dp-1",
                    "project_id": "test-project",
                    "inputs": {"query": "query1"},
                }
            ]
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.datapoints.list_datapoints(
                project="test-project", limit=100
            )

            assert len(result) == 1
            assert result[0].project_id == "test-project"
            mock_request.assert_called_once_with(
                "GET", "/datapoints", params={"project": "test-project", "limit": 100}
            )


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
            "field_id": "tool-123",
            "task": "test-project",
            "name": "test-tool",
            "description": "Test tool",
            "parameters": {"param1": "value1"},
            "tool_type": "function",
        }

    def test_create_tool_with_model(self, client, mock_tool_data):
        """Test creating tool using CreateToolRequest model."""
        tool_request = CreateToolRequest(
            task="test-project",
            name="test-tool",
            description="Test tool",
            parameters={"param1": "value1"},
            type=Type3.function,
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
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_tool_data
            mock_request.return_value = mock_response

            result = client.tools.create_tool_from_dict(tool_data)

            assert result.task == "test-project"
            mock_request.assert_called_once()

    def test_get_tool(self, client, mock_tool_data):
        """Test getting tool by ID."""
        tool_id = "tool-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_tool_data
            mock_request.return_value = mock_response

            result = client.tools.get_tool(tool_id)

            assert result.task == "test-project"
            assert result.name == "test-tool"
            mock_request.assert_called_once_with("GET", f"/tools/{tool_id}")

    def test_list_tools_without_project(self, client):
        """Test listing tools without project filter."""
        mock_data = {
            "tools": [
                {
                    "field_id": "tool-1",
                    "task": "proj-1",
                    "name": "tool1",
                    "parameters": {},
                    "tool_type": "function",
                },
                {
                    "field_id": "tool-2",
                    "task": "proj-2",
                    "name": "tool2",
                    "parameters": {},
                    "tool_type": "function",
                },
            ]
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.tools.list_tools(limit=50)

            assert len(result) == 2
            assert result[0].name == "tool1"
            assert result[1].name == "tool2"
            mock_request.assert_called_once_with("GET", "/tools", params={"limit": 50})

    def test_list_tools_with_project(self, client):
        """Test listing tools with project filter."""
        mock_data = {
            "tools": [
                {
                    "field_id": "tool-1",
                    "task": "test-project",
                    "name": "tool1",
                    "parameters": {},
                    "tool_type": "function",
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
                "GET", "/tools", params={"project": "test-project", "limit": 100}
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

            result = client.tools.delete_tool(tool_id)

            assert result is False
