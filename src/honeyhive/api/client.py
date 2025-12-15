"""HoneyHive API Client.

This module provides the main HoneyHive client with an ergonomic interface
wrapping the auto-generated API code.

Usage:
    from honeyhive.api import HoneyHive

    client = HoneyHive(api_key="hh_...")

    # Sync usage
    configs = client.configurations.list(project="my-project")

    # Async usage
    configs = await client.configurations.list_async(project="my-project")
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

# Import async services
# Import sync services
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
from honeyhive._generated.services import (
    async_Configurations_service as configs_svc_async,
)
from honeyhive._generated.services import (
    async_Datapoints_service as datapoints_svc_async,
)
from honeyhive._generated.services import async_Datasets_service as datasets_svc_async
from honeyhive._generated.services import async_Events_service as events_svc_async
from honeyhive._generated.services import (
    async_Experiments_service as experiments_svc_async,
)
from honeyhive._generated.services import async_Metrics_service as metrics_svc_async
from honeyhive._generated.services import async_Projects_service as projects_svc_async
from honeyhive._generated.services import async_Session_service as session_svc_async
from honeyhive._generated.services import async_Sessions_service as sessions_svc_async
from honeyhive._generated.services import async_Tools_service as tools_svc_async

from ._base import BaseAPI


class ConfigurationsAPI(BaseAPI):
    """Configurations API."""

    # Sync methods
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

    # Async methods
    async def list_async(
        self, project: Optional[str] = None
    ) -> List[GetConfigurationsResponse]:
        """List configurations asynchronously."""
        return await configs_svc_async.getConfigurations(
            self._api_config, project=project
        )

    async def create_async(
        self, request: CreateConfigurationRequest
    ) -> CreateConfigurationResponse:
        """Create a configuration asynchronously."""
        return await configs_svc_async.createConfiguration(
            self._api_config, data=request
        )

    async def update_async(
        self, id: str, request: UpdateConfigurationRequest
    ) -> UpdateConfigurationResponse:
        """Update a configuration asynchronously."""
        return await configs_svc_async.updateConfiguration(
            self._api_config, id=id, data=request
        )

    async def delete_async(self, id: str) -> DeleteConfigurationResponse:
        """Delete a configuration asynchronously."""
        return await configs_svc_async.deleteConfiguration(self._api_config, id=id)


class DatapointsAPI(BaseAPI):
    """Datapoints API."""

    # Sync methods
    def list(
        self,
        datapoint_ids: Optional[List[str]] = None,
        dataset_name: Optional[str] = None,
    ) -> GetDatapointsResponse:
        """List datapoints.

        Args:
            datapoint_ids: Optional list of datapoint IDs to fetch.
            dataset_name: Optional dataset name to filter by.
        """
        return datapoints_svc.getDatapoints(
            self._api_config, datapoint_ids=datapoint_ids, dataset_name=dataset_name
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

    # Async methods
    async def list_async(
        self,
        datapoint_ids: Optional[List[str]] = None,
        dataset_name: Optional[str] = None,
    ) -> GetDatapointsResponse:
        """List datapoints asynchronously.

        Args:
            datapoint_ids: Optional list of datapoint IDs to fetch.
            dataset_name: Optional dataset name to filter by.
        """
        return await datapoints_svc_async.getDatapoints(
            self._api_config, datapoint_ids=datapoint_ids, dataset_name=dataset_name
        )

    async def get_async(self, id: str) -> GetDatapointResponse:
        """Get a datapoint by ID asynchronously."""
        return await datapoints_svc_async.getDatapoint(self._api_config, id=id)

    async def create_async(
        self, request: CreateDatapointRequest
    ) -> CreateDatapointResponse:
        """Create a datapoint asynchronously."""
        return await datapoints_svc_async.createDatapoint(
            self._api_config, data=request
        )

    async def update_async(
        self, id: str, request: UpdateDatapointRequest
    ) -> UpdateDatapointResponse:
        """Update a datapoint asynchronously."""
        return await datapoints_svc_async.updateDatapoint(
            self._api_config, id=id, data=request
        )

    async def delete_async(self, id: str) -> DeleteDatapointResponse:
        """Delete a datapoint asynchronously."""
        return await datapoints_svc_async.deleteDatapoint(self._api_config, id=id)


class DatasetsAPI(BaseAPI):
    """Datasets API."""

    # Sync methods
    def list(
        self,
        dataset_id: Optional[str] = None,
        name: Optional[str] = None,
        include_datapoints: Optional[bool] = None,
    ) -> GetDatasetsResponse:
        """List datasets.

        Args:
            dataset_id: Optional dataset ID to fetch.
            name: Optional dataset name to filter by.
            include_datapoints: Whether to include datapoints in the response.
        """
        return datasets_svc.getDatasets(
            self._api_config,
            dataset_id=dataset_id,
            name=name,
            include_datapoints=include_datapoints,
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

    # Async methods
    async def list_async(
        self,
        dataset_id: Optional[str] = None,
        name: Optional[str] = None,
        include_datapoints: Optional[bool] = None,
    ) -> GetDatasetsResponse:
        """List datasets asynchronously.

        Args:
            dataset_id: Optional dataset ID to fetch.
            name: Optional dataset name to filter by.
            include_datapoints: Whether to include datapoints in the response.
        """
        return await datasets_svc_async.getDatasets(
            self._api_config,
            dataset_id=dataset_id,
            name=name,
            include_datapoints=include_datapoints,
        )

    async def create_async(
        self, request: CreateDatasetRequest
    ) -> CreateDatasetResponse:
        """Create a dataset asynchronously."""
        return await datasets_svc_async.createDataset(self._api_config, data=request)

    async def update_async(
        self, request: UpdateDatasetRequest
    ) -> UpdateDatasetResponse:
        """Update a dataset asynchronously."""
        return await datasets_svc_async.updateDataset(self._api_config, data=request)

    async def delete_async(self, id: str) -> DeleteDatasetResponse:
        """Delete a dataset asynchronously."""
        return await datasets_svc_async.deleteDataset(self._api_config, dataset_id=id)


class EventsAPI(BaseAPI):
    """Events API."""

    # Sync methods
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

    # Async methods
    async def list_async(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get events asynchronously."""
        return await events_svc_async.getEvents(self._api_config, data=data)

    async def create_async(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an event asynchronously."""
        return await events_svc_async.createEvent(self._api_config, data=data)

    async def update_async(self, data: Dict[str, Any]) -> None:
        """Update an event asynchronously."""
        return await events_svc_async.updateEvent(self._api_config, data=data)

    async def create_batch_async(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create events in batch asynchronously."""
        return await events_svc_async.createEventBatch(self._api_config, data=data)


class ExperimentsAPI(BaseAPI):
    """Experiments API."""

    # Sync methods
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

    # Async methods
    async def get_schema_async(self, project: str) -> GetExperimentRunsSchemaResponse:
        """Get experiment runs schema asynchronously."""
        return await experiments_svc_async.getExperimentRunsSchema(
            self._api_config, project=project
        )

    async def list_runs_async(
        self,
        project: str,
        experiment_id: Optional[str] = None,
    ) -> GetExperimentRunsResponse:
        """List experiment runs asynchronously."""
        return await experiments_svc_async.getRuns(
            self._api_config, project=project, experiment_id=experiment_id
        )

    async def get_run_async(self, run_id: str) -> GetExperimentRunResponse:
        """Get an experiment run by ID asynchronously."""
        return await experiments_svc_async.getRun(self._api_config, run_id=run_id)

    async def create_run_async(
        self, request: PostExperimentRunRequest
    ) -> PostExperimentRunResponse:
        """Create an experiment run asynchronously."""
        return await experiments_svc_async.createRun(self._api_config, data=request)

    async def update_run_async(
        self, run_id: str, request: PutExperimentRunRequest
    ) -> PutExperimentRunResponse:
        """Update an experiment run asynchronously."""
        return await experiments_svc_async.updateRun(
            self._api_config, run_id=run_id, data=request
        )

    async def delete_run_async(self, run_id: str) -> DeleteExperimentRunResponse:
        """Delete an experiment run asynchronously."""
        return await experiments_svc_async.deleteRun(self._api_config, run_id=run_id)

    def get_result(
        self,
        run_id: str,
        project_id: str,
        aggregate_function: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get experiment run result."""
        result = experiments_svc.getExperimentResult(
            self._api_config,
            run_id=run_id,
            project_id=project_id,
            aggregate_function=aggregate_function,
        )
        # TODOSchema is a pass-through dict model
        return result.model_dump() if hasattr(result, "model_dump") else dict(result)

    def compare_runs(
        self,
        run_id_1: str,
        run_id_2: str,
        project_id: str,
        aggregate_function: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compare two experiment runs."""
        result = experiments_svc.getExperimentComparison(
            self._api_config,
            project_id=project_id,
            run_id_1=run_id_1,
            run_id_2=run_id_2,
            aggregate_function=aggregate_function,
        )
        # TODOSchema is a pass-through dict model
        return result.model_dump() if hasattr(result, "model_dump") else dict(result)

    async def get_result_async(
        self,
        run_id: str,
        project_id: str,
        aggregate_function: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get experiment run result asynchronously."""
        result = await experiments_svc_async.getExperimentResult(
            self._api_config,
            run_id=run_id,
            project_id=project_id,
            aggregate_function=aggregate_function,
        )
        return result.model_dump() if hasattr(result, "model_dump") else dict(result)

    async def compare_runs_async(
        self,
        run_id_1: str,
        run_id_2: str,
        project_id: str,
        aggregate_function: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compare two experiment runs asynchronously."""
        result = await experiments_svc_async.getExperimentComparison(
            self._api_config,
            project_id=project_id,
            run_id_1=run_id_1,
            run_id_2=run_id_2,
            aggregate_function=aggregate_function,
        )
        return result.model_dump() if hasattr(result, "model_dump") else dict(result)


class MetricsAPI(BaseAPI):
    """Metrics API."""

    # Sync methods
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

    # Async methods
    async def list_async(
        self,
        project: Optional[str] = None,
        name: Optional[str] = None,
        type: Optional[str] = None,
    ) -> GetMetricsResponse:
        """List metrics asynchronously."""
        return await metrics_svc_async.getMetrics(
            self._api_config, project=project, name=name, type=type
        )

    async def create_async(self, request: CreateMetricRequest) -> CreateMetricResponse:
        """Create a metric asynchronously."""
        return await metrics_svc_async.createMetric(self._api_config, data=request)

    async def update_async(self, request: UpdateMetricRequest) -> UpdateMetricResponse:
        """Update a metric asynchronously."""
        return await metrics_svc_async.updateMetric(self._api_config, data=request)

    async def delete_async(self, id: str) -> DeleteMetricResponse:
        """Delete a metric asynchronously."""
        return await metrics_svc_async.deleteMetric(self._api_config, metric_id=id)


class ProjectsAPI(BaseAPI):
    """Projects API."""

    # Sync methods
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

    # Async methods
    async def list_async(self, name: Optional[str] = None) -> Dict[str, Any]:
        """List projects asynchronously."""
        return await projects_svc_async.getProjects(self._api_config, name=name)

    async def create_async(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a project asynchronously."""
        return await projects_svc_async.createProject(self._api_config, data=data)

    async def update_async(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a project asynchronously."""
        return await projects_svc_async.updateProject(self._api_config, data=data)

    async def delete_async(self, name: str) -> Dict[str, Any]:
        """Delete a project asynchronously."""
        return await projects_svc_async.deleteProject(self._api_config, name=name)


class SessionsAPI(BaseAPI):
    """Sessions API."""

    # Sync methods
    def get(self, session_id: str) -> GetSessionResponse:
        """Get a session by ID."""
        return sessions_svc.getSession(self._api_config, session_id=session_id)

    def delete(self, session_id: str) -> DeleteSessionResponse:
        """Delete a session."""
        return sessions_svc.deleteSession(self._api_config, session_id=session_id)

    def start(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new session."""
        return session_svc.startSession(self._api_config, data=data)

    # Async methods
    async def get_async(self, session_id: str) -> GetSessionResponse:
        """Get a session by ID asynchronously."""
        return await sessions_svc_async.getSession(
            self._api_config, session_id=session_id
        )

    async def delete_async(self, session_id: str) -> DeleteSessionResponse:
        """Delete a session asynchronously."""
        return await sessions_svc_async.deleteSession(
            self._api_config, session_id=session_id
        )

    async def start_async(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new session asynchronously."""
        return await session_svc_async.startSession(self._api_config, data=data)


class ToolsAPI(BaseAPI):
    """Tools API."""

    # Sync methods
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

    # Async methods
    async def list_async(self) -> List[GetToolsResponse]:
        """List tools asynchronously."""
        return await tools_svc_async.getTools(self._api_config)

    async def create_async(self, request: CreateToolRequest) -> CreateToolResponse:
        """Create a tool asynchronously."""
        return await tools_svc_async.createTool(self._api_config, data=request)

    async def update_async(self, request: UpdateToolRequest) -> UpdateToolResponse:
        """Update a tool asynchronously."""
        return await tools_svc_async.updateTool(self._api_config, data=request)

    async def delete_async(self, id: str) -> DeleteToolResponse:
        """Delete a tool asynchronously."""
        return await tools_svc_async.deleteTool(self._api_config, tool_id=id)


class HoneyHive:
    """Main HoneyHive API client.

    Provides an ergonomic interface to the HoneyHive API with both
    sync and async methods.

    Usage:
        client = HoneyHive(api_key="hh_...")

        # Sync
        configs = client.configurations.list(project="my-project")

        # Async
        configs = await client.configurations.list_async(project="my-project")

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
        self._api_key = api_key
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

    @property
    def api_key(self) -> str:
        """Get the HoneyHive API key."""
        return self._api_key

    @property
    def server_url(self) -> str:
        """Get the HoneyHive API server URL."""
        return self._api_config.base_path

    @server_url.setter
    def server_url(self, value: str) -> None:
        """Set the HoneyHive API server URL."""
        self._api_config.base_path = value
