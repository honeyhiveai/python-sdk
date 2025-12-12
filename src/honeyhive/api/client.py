"""HoneyHive API Client.

This module provides the main HoneyHive client with an ergonomic interface
wrapping the auto-generated API code.

Usage:
    from honeyhive.api import HoneyHive

    client = HoneyHive(api_key="hh_...")

    # Configurations
    configs = client.configurations.list(project="my-project")
    client.configurations.create(CreateConfigurationRequest(...))

    # Datasets
    datasets = client.datasets.list(project="my-project")

    # Experiments
    runs = client.experiments.list_runs(project="my-project")
"""

from typing import Any, Dict, List, Optional

from honeyhive._generated.api_config import APIConfig

# Import models used in type hints
from honeyhive._generated.models import (
    CreateConfigurationRequest,
    CreateConfigurationResponse,
    CreateDatapointRequest,
    CreateDatapointResponse,
    CreateDatasetRequest,
    CreateDatasetResponse,
    CreateMetricRequest,
    CreateMetricResponse,
    CreateToolRequest,
    CreateToolResponse,
    DeleteConfigurationResponse,
    DeleteDatapointResponse,
    DeleteDatasetResponse,
    DeleteExperimentRunResponse,
    DeleteMetricResponse,
    DeleteSessionResponse,
    DeleteToolResponse,
    GetConfigurationsResponse,
    GetDatapointResponse,
    GetDatapointsResponse,
    GetDatasetsResponse,
    GetExperimentRunResponse,
    GetExperimentRunsResponse,
    GetExperimentRunsSchemaResponse,
    GetMetricsResponse,
    GetSessionResponse,
    GetToolsResponse,
    PostExperimentRunRequest,
    PostExperimentRunResponse,
    PutExperimentRunRequest,
    PutExperimentRunResponse,
    UpdateConfigurationRequest,
    UpdateConfigurationResponse,
    UpdateDatapointRequest,
    UpdateDatapointResponse,
    UpdateDatasetRequest,
    UpdateDatasetResponse,
    UpdateMetricRequest,
    UpdateMetricResponse,
    UpdateToolRequest,
    UpdateToolResponse,
)

# Import all services
from honeyhive._generated.services import Configurations_service as configs_svc
from honeyhive._generated.services import Datapoints_service as datapoints_svc
from honeyhive._generated.services import Datasets_service as datasets_svc
from honeyhive._generated.services import Events_service as events_svc
from honeyhive._generated.services import Experiments_service as experiments_svc
from honeyhive._generated.services import Metrics_service as metrics_svc
from honeyhive._generated.services import Projects_service as projects_svc
from honeyhive._generated.services import Session_service as session_svc
from honeyhive._generated.services import Sessions_service as sessions_svc
from honeyhive._generated.services import Tools_service as tools_svc

from ._base import BaseAPI


class ConfigurationsAPI(BaseAPI):
    """Configurations API."""

    def list(self, project: Optional[str] = None) -> List[GetConfigurationsResponse]:
        """List configurations."""
        return configs_svc.getConfigurations(self._api_config, project=project)

    def create(
        self, request: CreateConfigurationRequest
    ) -> CreateConfigurationResponse:
        """Create a configuration."""
        return configs_svc.createConfiguration(self._api_config, data=request)

    def update(
        self, id: str, request: UpdateConfigurationRequest
    ) -> UpdateConfigurationResponse:
        """Update a configuration."""
        return configs_svc.updateConfiguration(self._api_config, id=id, data=request)

    def delete(self, id: str) -> DeleteConfigurationResponse:
        """Delete a configuration."""
        return configs_svc.deleteConfiguration(self._api_config, id=id)


class DatapointsAPI(BaseAPI):
    """Datapoints API."""

    def list(
        self,
        project: str,
        dataset_id: Optional[str] = None,
        type: Optional[str] = None,
    ) -> GetDatapointsResponse:
        """List datapoints."""
        return datapoints_svc.getDatapoints(
            self._api_config, project=project, dataset_id=dataset_id, type=type
        )

    def get(self, id: str) -> GetDatapointResponse:
        """Get a datapoint by ID."""
        return datapoints_svc.getDatapoint(self._api_config, id=id)

    def create(self, request: CreateDatapointRequest) -> CreateDatapointResponse:
        """Create a datapoint."""
        return datapoints_svc.createDatapoint(self._api_config, data=request)

    def update(
        self, id: str, request: UpdateDatapointRequest
    ) -> UpdateDatapointResponse:
        """Update a datapoint."""
        return datapoints_svc.updateDatapoint(self._api_config, id=id, data=request)

    def delete(self, id: str) -> DeleteDatapointResponse:
        """Delete a datapoint."""
        return datapoints_svc.deleteDatapoint(self._api_config, id=id)


class DatasetsAPI(BaseAPI):
    """Datasets API."""

    def list(
        self,
        project: Optional[str] = None,
        name: Optional[str] = None,
        type: Optional[str] = None,
    ) -> GetDatasetsResponse:
        """List datasets."""
        return datasets_svc.getDatasets(
            self._api_config, project=project, name=name, type=type
        )

    def create(self, request: CreateDatasetRequest) -> CreateDatasetResponse:
        """Create a dataset."""
        return datasets_svc.createDataset(self._api_config, data=request)

    def update(self, request: UpdateDatasetRequest) -> UpdateDatasetResponse:
        """Update a dataset."""
        return datasets_svc.updateDataset(self._api_config, data=request)

    def delete(self, id: str) -> DeleteDatasetResponse:
        """Delete a dataset."""
        return datasets_svc.deleteDataset(self._api_config, dataset_id=id)


class EventsAPI(BaseAPI):
    """Events API."""

    def list(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get events."""
        return events_svc.getEvents(self._api_config, data=data)

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an event."""
        return events_svc.createEvent(self._api_config, data=data)

    def update(self, data: Dict[str, Any]) -> None:
        """Update an event."""
        return events_svc.updateEvent(self._api_config, data=data)

    def create_batch(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create events in batch."""
        return events_svc.createEventBatch(self._api_config, data=data)


class ExperimentsAPI(BaseAPI):
    """Experiments API."""

    def get_schema(self, project: str) -> GetExperimentRunsSchemaResponse:
        """Get experiment runs schema."""
        return experiments_svc.getExperimentRunsSchema(
            self._api_config, project=project
        )

    def list_runs(
        self,
        project: str,
        experiment_id: Optional[str] = None,
    ) -> GetExperimentRunsResponse:
        """List experiment runs."""
        return experiments_svc.getRuns(
            self._api_config, project=project, experiment_id=experiment_id
        )

    def get_run(self, run_id: str) -> GetExperimentRunResponse:
        """Get an experiment run by ID."""
        return experiments_svc.getRun(self._api_config, run_id=run_id)

    def create_run(
        self, request: PostExperimentRunRequest
    ) -> PostExperimentRunResponse:
        """Create an experiment run."""
        return experiments_svc.createRun(self._api_config, data=request)

    def update_run(
        self, run_id: str, request: PutExperimentRunRequest
    ) -> PutExperimentRunResponse:
        """Update an experiment run."""
        return experiments_svc.updateRun(self._api_config, run_id=run_id, data=request)

    def delete_run(self, run_id: str) -> DeleteExperimentRunResponse:
        """Delete an experiment run."""
        return experiments_svc.deleteRun(self._api_config, run_id=run_id)


class MetricsAPI(BaseAPI):
    """Metrics API."""

    def list(
        self,
        project: Optional[str] = None,
        name: Optional[str] = None,
        type: Optional[str] = None,
    ) -> GetMetricsResponse:
        """List metrics."""
        return metrics_svc.getMetrics(
            self._api_config, project=project, name=name, type=type
        )

    def create(self, request: CreateMetricRequest) -> CreateMetricResponse:
        """Create a metric."""
        return metrics_svc.createMetric(self._api_config, data=request)

    def update(self, request: UpdateMetricRequest) -> UpdateMetricResponse:
        """Update a metric."""
        return metrics_svc.updateMetric(self._api_config, data=request)

    def delete(self, id: str) -> DeleteMetricResponse:
        """Delete a metric."""
        return metrics_svc.deleteMetric(self._api_config, metric_id=id)


class ProjectsAPI(BaseAPI):
    """Projects API."""

    def list(self, name: Optional[str] = None) -> Dict[str, Any]:
        """List projects."""
        return projects_svc.getProjects(self._api_config, name=name)

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a project."""
        return projects_svc.createProject(self._api_config, data=data)

    def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a project."""
        return projects_svc.updateProject(self._api_config, data=data)

    def delete(self, name: str) -> Dict[str, Any]:
        """Delete a project."""
        return projects_svc.deleteProject(self._api_config, name=name)


class SessionsAPI(BaseAPI):
    """Sessions API."""

    def get(self, session_id: str) -> GetSessionResponse:
        """Get a session by ID."""
        return sessions_svc.getSession(self._api_config, session_id=session_id)

    def delete(self, session_id: str) -> DeleteSessionResponse:
        """Delete a session."""
        return sessions_svc.deleteSession(self._api_config, session_id=session_id)

    def start(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new session."""
        return session_svc.startSession(self._api_config, data=data)


class ToolsAPI(BaseAPI):
    """Tools API."""

    def list(self) -> List[GetToolsResponse]:
        """List tools."""
        return tools_svc.getTools(self._api_config)

    def create(self, request: CreateToolRequest) -> CreateToolResponse:
        """Create a tool."""
        return tools_svc.createTool(self._api_config, data=request)

    def update(self, request: UpdateToolRequest) -> UpdateToolResponse:
        """Update a tool."""
        return tools_svc.updateTool(self._api_config, data=request)

    def delete(self, id: str) -> DeleteToolResponse:
        """Delete a tool."""
        return tools_svc.deleteTool(self._api_config, tool_id=id)


class HoneyHive:
    """Main HoneyHive API client.

    Provides an ergonomic interface to the HoneyHive API.

    Usage:
        client = HoneyHive(api_key="hh_...")

        # List configurations
        configs = client.configurations.list(project="my-project")

        # Create a dataset
        from honeyhive.models import CreateDatasetRequest
        dataset = client.datasets.create(CreateDatasetRequest(...))

    Attributes:
        configurations: API for managing configurations.
        datapoints: API for managing datapoints.
        datasets: API for managing datasets.
        events: API for managing events.
        experiments: API for managing experiment runs.
        metrics: API for managing metrics.
        projects: API for managing projects.
        sessions: API for managing sessions.
        tools: API for managing tools.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.honeyhive.ai",
    ) -> None:
        """Initialize the HoneyHive client.

        Args:
            api_key: HoneyHive API key (typically starts with 'hh_').
            base_url: API base URL (default: https://api.honeyhive.ai).
        """
        self._api_config = APIConfig(
            base_path=base_url,
            access_token=api_key,
        )

        # Initialize API namespaces
        self.configurations = ConfigurationsAPI(self._api_config)
        self.datapoints = DatapointsAPI(self._api_config)
        self.datasets = DatasetsAPI(self._api_config)
        self.events = EventsAPI(self._api_config)
        self.experiments = ExperimentsAPI(self._api_config)
        self.metrics = MetricsAPI(self._api_config)
        self.projects = ProjectsAPI(self._api_config)
        self.sessions = SessionsAPI(self._api_config)
        self.tools = ToolsAPI(self._api_config)

    @property
    def api_config(self) -> APIConfig:
        """Access the underlying API configuration."""
        return self._api_config
