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
    GetEventsBySessionIdResponse,
    GetEventsResponse,
    GetExperimentRunResponse,
    GetExperimentRunsResponse,
    GetExperimentRunsSchemaResponse,
    GetMetricsResponse,
    GetSessionResponse,
    GetToolsResponse,
    PostEventRequest,
    PostEventResponse,
    PostExperimentRunRequest,
    PostExperimentRunResponse,
    PostSessionStartResponse,
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
        """List configurations.

        Note: project parameter is currently unused as v1 API doesn't support project filtering.
        """
        return configs_svc.getConfigurations(self._api_config)

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
        """List configurations asynchronously.

        Note: project parameter is currently unused as v1 API doesn't support project filtering.
        """
        return await configs_svc_async.getConfigurations(self._api_config)

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

    # Backwards compatible aliases
    def get_configuration(self, id: str) -> GetConfigurationsResponse:
        """Get a configuration (backwards compatible alias)."""
        return self.list()  # No single-get endpoint, returns all

    def create_configuration(
        self, request: CreateConfigurationRequest
    ) -> CreateConfigurationResponse:
        """Create a configuration (backwards compatible alias)."""
        return self.create(request)

    def update_configuration(
        self, id: str, request: UpdateConfigurationRequest
    ) -> UpdateConfigurationResponse:
        """Update a configuration (backwards compatible alias)."""
        return self.update(id, request)

    def delete_configuration(self, id: str) -> DeleteConfigurationResponse:
        """Delete a configuration (backwards compatible alias)."""
        return self.delete(id)

    def list_configurations(
        self, project: Optional[str] = None
    ) -> List[GetConfigurationsResponse]:
        """List configurations (backwards compatible alias)."""
        return self.list(project)


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

    # Backwards compatible aliases
    def get_datapoint(self, id: str) -> GetDatapointResponse:
        """Get a datapoint by ID (backwards compatible alias for get())."""
        return self.get(id)

    def create_datapoint(
        self, request: CreateDatapointRequest
    ) -> CreateDatapointResponse:
        """Create a datapoint (backwards compatible alias for create())."""
        return self.create(request)

    def update_datapoint(
        self, id: str, request: UpdateDatapointRequest
    ) -> UpdateDatapointResponse:
        """Update a datapoint (backwards compatible alias for update())."""
        return self.update(id, request)

    def delete_datapoint(self, id: str) -> DeleteDatapointResponse:
        """Delete a datapoint (backwards compatible alias for delete())."""
        return self.delete(id)

    def list_datapoints(
        self,
        datapoint_ids: Optional[List[str]] = None,
        dataset_name: Optional[str] = None,
    ) -> GetDatapointsResponse:
        """List datapoints (backwards compatible alias)."""
        return self.list(datapoint_ids=datapoint_ids, dataset_name=dataset_name)


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

    # Backwards compatible aliases
    def get_dataset(self, id: str) -> GetDatasetsResponse:
        """Get a dataset by ID (backwards compatible alias).
        
        Note: Uses list() with dataset_id filter since there's no single-get endpoint.
        """
        return self.list(dataset_id=id)

    def create_dataset(self, request: CreateDatasetRequest) -> CreateDatasetResponse:
        """Create a dataset (backwards compatible alias for create())."""
        return self.create(request)

    def update_dataset(self, request: UpdateDatasetRequest) -> UpdateDatasetResponse:
        """Update a dataset (backwards compatible alias for update())."""
        return self.update(request)

    def delete_dataset(self, id: str) -> DeleteDatasetResponse:
        """Delete a dataset (backwards compatible alias for delete())."""
        return self.delete(id)

    def list_datasets(
        self,
        dataset_id: Optional[str] = None,
        name: Optional[str] = None,
        include_datapoints: Optional[bool] = None,
    ) -> GetDatasetsResponse:
        """List datasets (backwards compatible alias)."""
        return self.list(
            dataset_id=dataset_id, name=name, include_datapoints=include_datapoints
        )


class EventsAPI(BaseAPI):
    """Events API."""

    # Supported parameters for getEvents() method
    _GET_EVENTS_SUPPORTED_PARAMS = {
        "dateRange",
        "filters",
        "projections",
        "ignore_order",
        "limit",
        "page",
        "evaluation_id",
    }

    # Sync methods
    def list(self, data: Dict[str, Any]) -> GetEventsResponse:
        """Get events."""
        # Filter data to only include supported parameters for getEvents()
        filtered_data = {
            k: v for k, v in data.items() if k in self._GET_EVENTS_SUPPORTED_PARAMS
        }
        return events_svc.getEvents(self._api_config, **filtered_data)

    def get_by_session_id(self, session_id: str) -> GetEventsBySessionIdResponse:
        """Get events by session ID (uses Control Plane endpoint)."""
        # This endpoint is on Control Plane, use cp_base_path
        cp_config = APIConfig(
            base_path=self._api_config.get_cp_base_path(),
            access_token=self._api_config.access_token,
            verify=self._api_config.verify,
        )
        return events_svc.getEventsBySessionId(cp_config, id=session_id)

    def create(self, request: PostEventRequest) -> PostEventResponse:
        """Create an event."""
        data = request.model_dump(exclude_none=True) if hasattr(request, 'model_dump') else request
        return events_svc.createEvent(self._api_config, data=data)

    def update(self, data: Dict[str, Any]) -> None:
        """Update an event."""
        return events_svc.updateEvent(self._api_config, data=data)

    def create_batch(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create events in batch."""
        return events_svc.createEventBatch(self._api_config, data=data)

    # Async methods
    async def list_async(self, data: Dict[str, Any]) -> GetEventsResponse:
        """Get events asynchronously."""
        # Filter data to only include supported parameters for getEvents()
        filtered_data = {
            k: v for k, v in data.items() if k in self._GET_EVENTS_SUPPORTED_PARAMS
        }
        return await events_svc_async.getEvents(self._api_config, **filtered_data)

    async def get_by_session_id_async(
        self, session_id: str
    ) -> GetEventsBySessionIdResponse:
        """Get events by session ID asynchronously (uses Control Plane endpoint)."""
        # This endpoint is on Control Plane, use cp_base_path
        cp_config = APIConfig(
            base_path=self._api_config.get_cp_base_path(),
            access_token=self._api_config.access_token,
            verify=self._api_config.verify,
        )
        return await events_svc_async.getEventsBySessionId(cp_config, id=session_id)

    async def create_async(self, request: PostEventRequest) -> PostEventResponse:
        """Create an event asynchronously."""
        data = request.model_dump(exclude_none=True) if hasattr(request, 'model_dump') else request
        return await events_svc_async.createEvent(self._api_config, data=data)

    async def update_async(self, data: Dict[str, Any]) -> None:
        """Update an event asynchronously."""
        return await events_svc_async.updateEvent(self._api_config, data=data)

    async def create_batch_async(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create events in batch asynchronously."""
        return await events_svc_async.createEventBatch(self._api_config, data=data)

    # Backwards compatible aliases
    def create_event(self, request: PostEventRequest) -> PostEventResponse:
        """Create an event (backwards compatible alias for create())."""
        return self.create(request)

    def update_event(self, data: Dict[str, Any]) -> None:
        """Update an event (backwards compatible alias for update())."""
        return self.update(data)

    def list_events(self, data: Dict[str, Any]) -> GetEventsResponse:
        """List events (backwards compatible alias for list())."""
        return self.list(data)

    def get_events(self, data: Dict[str, Any]) -> GetEventsResponse:
        """Get events (backwards compatible alias for list())."""
        return self.list(data)


class ExperimentsAPI(BaseAPI):
    """Experiments API."""

    # Sync methods
    def get_schema(
        self,
        dateRange: Optional[Any] = None,
        evaluation_id: Optional[str] = None,
    ) -> GetExperimentRunsSchemaResponse:
        """Get experiment runs schema.
        
        Args:
            dateRange: Filter by date range (string or dict with $gte/$lte).
            evaluation_id: Filter by evaluation/run ID.
        """
        return experiments_svc.getExperimentRunsSchema(
            self._api_config, dateRange=dateRange, evaluation_id=evaluation_id
        )

    def list_runs(
        self,
        dataset_id: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        run_ids: Optional[List[str]] = None,
        name: Optional[str] = None,
        status: Optional[str] = None,
        dateRange: Optional[Any] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> GetExperimentRunsResponse:
        """List experiment runs.
        
        Args:
            dataset_id: Filter by dataset ID.
            page: Page number for pagination.
            limit: Number of results per page.
            run_ids: Filter by specific run IDs.
            name: Filter by run name.
            status: Filter by run status.
            dateRange: Filter by date range.
            sort_by: Sort by field.
            sort_order: Sort order (asc/desc).
        """
        return experiments_svc.getRuns(
            self._api_config,
            dataset_id=dataset_id,
            page=page,
            limit=limit,
            run_ids=run_ids,
            name=name,
            status=status,
            dateRange=dateRange,
            sort_by=sort_by,
            sort_order=sort_order,
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
    async def get_schema_async(
        self,
        dateRange: Optional[Any] = None,
        evaluation_id: Optional[str] = None,
    ) -> GetExperimentRunsSchemaResponse:
        """Get experiment runs schema asynchronously.
        
        Args:
            dateRange: Filter by date range (string or dict with $gte/$lte).
            evaluation_id: Filter by evaluation/run ID.
        """
        return await experiments_svc_async.getExperimentRunsSchema(
            self._api_config, dateRange=dateRange, evaluation_id=evaluation_id
        )

    async def list_runs_async(
        self,
        dataset_id: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        run_ids: Optional[List[str]] = None,
        name: Optional[str] = None,
        status: Optional[str] = None,
        dateRange: Optional[Any] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> GetExperimentRunsResponse:
        """List experiment runs asynchronously.
        
        Args:
            dataset_id: Filter by dataset ID.
            page: Page number for pagination.
            limit: Number of results per page.
            run_ids: Filter by specific run IDs.
            name: Filter by run name.
            status: Filter by run status.
            dateRange: Filter by date range.
            sort_by: Sort by field.
            sort_order: Sort order (asc/desc).
        """
        return await experiments_svc_async.getRuns(
            self._api_config,
            dataset_id=dataset_id,
            page=page,
            limit=limit,
            run_ids=run_ids,
            name=name,
            status=status,
            dateRange=dateRange,
            sort_by=sort_by,
            sort_order=sort_order,
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
        aggregate_function: Optional[str] = None,
        filters: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Get experiment run result.
        
        Args:
            run_id: The experiment run ID.
            aggregate_function: Aggregation function to apply.
            filters: Optional filters to apply.
        """
        result = experiments_svc.getExperimentResult(
            self._api_config,
            run_id=run_id,
            aggregate_function=aggregate_function,
            filters=filters,
        )
        # GetExperimentRunResultResponse is a pass-through dict model
        return result.model_dump() if hasattr(result, "model_dump") else dict(result)

    def compare_runs(
        self,
        new_run_id: str,
        old_run_id: str,
        aggregate_function: Optional[str] = None,
        filters: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Compare two experiment runs.
        
        Args:
            new_run_id: The new run ID to compare.
            old_run_id: The old run ID to compare against.
            aggregate_function: Aggregation function to apply.
            filters: Optional filters to apply.
        """
        result = experiments_svc.getExperimentComparison(
            self._api_config,
            new_run_id=new_run_id,
            old_run_id=old_run_id,
            aggregate_function=aggregate_function,
            filters=filters,
        )
        # GetExperimentRunCompareResponse is a pass-through dict model
        return result.model_dump() if hasattr(result, "model_dump") else dict(result)

    async def get_result_async(
        self,
        run_id: str,
        aggregate_function: Optional[str] = None,
        filters: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Get experiment run result asynchronously.
        
        Args:
            run_id: The experiment run ID.
            aggregate_function: Aggregation function to apply.
            filters: Optional filters to apply.
        """
        result = await experiments_svc_async.getExperimentResult(
            self._api_config,
            run_id=run_id,
            aggregate_function=aggregate_function,
            filters=filters,
        )
        return result.model_dump() if hasattr(result, "model_dump") else dict(result)

    async def compare_runs_async(
        self,
        new_run_id: str,
        old_run_id: str,
        aggregate_function: Optional[str] = None,
        filters: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Compare two experiment runs asynchronously.
        
        Args:
            new_run_id: The new run ID to compare.
            old_run_id: The old run ID to compare against.
            aggregate_function: Aggregation function to apply.
            filters: Optional filters to apply.
        """
        result = await experiments_svc_async.getExperimentComparison(
            self._api_config,
            new_run_id=new_run_id,
            old_run_id=old_run_id,
            aggregate_function=aggregate_function,
            filters=filters,
        )
        return result.model_dump() if hasattr(result, "model_dump") else dict(result)

    # Aliases for backwards compatibility (evaluations naming)
    def get_run_result(
        self,
        run_id: str,
        aggregate_function: Optional[str] = None,
        filters: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Get experiment run result (alias for get_result)."""
        return self.get_result(run_id, aggregate_function, filters)

    def compare_run_events(
        self,
        new_run_id: str,
        old_run_id: str,
        event_name: Optional[str] = None,
        event_type: Optional[str] = None,
        filter: Optional[Any] = None,
        limit: Optional[int] = None,
        page: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Compare events between two experiment runs.
        
        Args:
            new_run_id: The new run ID to compare.
            old_run_id: The old run ID to compare against.
            event_name: Filter by event name.
            event_type: Filter by event type.
            filter: Additional filter criteria.
            limit: Maximum number of results.
            page: Page number for pagination.
        """
        return experiments_svc.getExperimentCompareEvents(
            self._api_config,
            run_id_1=new_run_id,
            run_id_2=old_run_id,
            event_name=event_name,
            event_type=event_type,
            filter=filter,
            limit=limit,
            page=page,
        )


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

    # Backwards compatible aliases
    def get_metric(self, id: str) -> GetMetricsResponse:
        """Get a metric (backwards compatible alias)."""
        return self.list()  # No single-get endpoint

    def create_metric(self, request: CreateMetricRequest) -> CreateMetricResponse:
        """Create a metric (backwards compatible alias)."""
        return self.create(request)

    def update_metric(self, request: UpdateMetricRequest) -> UpdateMetricResponse:
        """Update a metric (backwards compatible alias)."""
        return self.update(request)

    def delete_metric(self, id: str) -> DeleteMetricResponse:
        """Delete a metric (backwards compatible alias)."""
        return self.delete(id)

    def list_metrics(
        self,
        project: Optional[str] = None,
        name: Optional[str] = None,
        type: Optional[str] = None,
    ) -> GetMetricsResponse:
        """List metrics (backwards compatible alias)."""
        return self.list(project=project, name=name, type=type)


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

    # Backwards compatible aliases
    def get_project(self, id: str) -> Dict[str, Any]:
        """Get a project (backwards compatible alias)."""
        return self.list(name=id)  # Use name filter since no single-get

    def create_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a project (backwards compatible alias)."""
        return self.create(data)

    def update_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a project (backwards compatible alias)."""
        return self.update(data)

    def delete_project(self, name: str) -> Dict[str, Any]:
        """Delete a project (backwards compatible alias)."""
        return self.delete(name)

    def list_projects(self, name: Optional[str] = None) -> Dict[str, Any]:
        """List projects (backwards compatible alias)."""
        return self.list(name=name)


class SessionsAPI(BaseAPI):
    """Sessions API."""

    # Sync methods
    def get(self, session_id: str) -> GetSessionResponse:
        """Get a session by ID."""
        return sessions_svc.getSession(self._api_config, session_id=session_id)

    def delete(self, session_id: str) -> DeleteSessionResponse:
        """Delete a session."""
        return sessions_svc.deleteSession(self._api_config, session_id=session_id)

    def start(self, data: Dict[str, Any]) -> PostSessionStartResponse:
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

    async def start_async(self, data: Dict[str, Any]) -> PostSessionStartResponse:
        """Start a new session asynchronously."""
        return await session_svc_async.startSession(self._api_config, data=data)

    # Backwards compatible aliases
    def create_session(self, request: Dict[str, Any]) -> PostSessionStartResponse:
        """Create/start a session (backwards compatible alias for start())."""
        return self.start(request)

    def start_session(self, request: Dict[str, Any]) -> PostSessionStartResponse:
        """Start a session (backwards compatible alias for start())."""
        return self.start(request)

    def get_session(self, session_id: str) -> GetSessionResponse:
        """Get a session (backwards compatible alias for get())."""
        return self.get(session_id)

    def delete_session(self, session_id: str) -> DeleteSessionResponse:
        """Delete a session (backwards compatible alias for delete())."""
        return self.delete(session_id)


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

    # Backwards compatible aliases
    def get_tool(self, id: str) -> List[GetToolsResponse]:
        """Get a tool (backwards compatible alias)."""
        return self.list()  # No single-get endpoint

    def create_tool(self, request: CreateToolRequest) -> CreateToolResponse:
        """Create a tool (backwards compatible alias)."""
        return self.create(request)

    def update_tool(self, request: UpdateToolRequest) -> UpdateToolResponse:
        """Update a tool (backwards compatible alias)."""
        return self.update(request)

    def delete_tool(self, id: str) -> DeleteToolResponse:
        """Delete a tool (backwards compatible alias)."""
        return self.delete(id)

    def list_tools(self) -> List[GetToolsResponse]:
        """List tools (backwards compatible alias)."""
        return self.list()


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
        api_key: Optional[str] = None,
        *,
        # Primary URL parameters
        base_url: Optional[str] = None,
        cp_base_url: Optional[str] = None,
        # Backwards compatible alias for base_url
        server_url: Optional[str] = None,
        # Backwards compatible parameters (accepted but not used in new client)
        timeout: Optional[float] = None,
        retry_config: Optional[Any] = None,
        rate_limit_calls: Optional[int] = None,
        rate_limit_window: Optional[float] = None,
        max_connections: Optional[int] = None,
        max_keepalive: Optional[int] = None,
        test_mode: Optional[bool] = None,
        verbose: Optional[bool] = None,
        tracer_instance: Optional[Any] = None,
    ) -> None:
        """Initialize the HoneyHive client.

        Args:
            api_key: HoneyHive API key (typically starts with 'hh_').
                     Falls back to HH_API_KEY environment variable.
            base_url: API base URL for Data Plane/ingestion.
                      Falls back to HH_API_URL env var, then https://api.honeyhive.ai.
            cp_base_url: Control Plane API URL for query endpoints.
                         Falls back to HH_CP_API_URL, then HH_API_URL env var.
            server_url: Deprecated alias for base_url (for backwards compatibility).
            timeout: Request timeout in seconds (accepted for backwards compat, not used).
            retry_config: Retry configuration (accepted for backwards compat, not used).
            rate_limit_calls: Max calls per time window (accepted for backwards compat).
            rate_limit_window: Time window in seconds (accepted for backwards compat).
            max_connections: Max connections in pool (accepted for backwards compat).
            max_keepalive: Max keepalive connections (accepted for backwards compat).
            test_mode: Enable test mode (accepted for backwards compat, not used).
            verbose: Enable verbose logging (accepted for backwards compat, not used).
            tracer_instance: Tracer instance (accepted for backwards compat, not used).
        """
        import os

        # Resolve API key from parameter or environment
        self._api_key = api_key or os.environ.get("HH_API_KEY", "")

        # Resolve base URL: base_url > server_url (legacy) > env var > default
        resolved_base_url = (
            base_url
            or server_url  # Legacy parameter
            or os.environ.get("HH_API_URL")
            or "https://api.honeyhive.ai"
        )

        # Resolve CP base URL: cp_base_url > HH_CP_API_URL > HH_API_URL > base_url
        resolved_cp_base_url = (
            cp_base_url
            or os.environ.get("HH_CP_API_URL")
            or os.environ.get("HH_API_URL")
            or resolved_base_url
        )

        # Store backwards compat params (silently accepted)
        self._timeout = timeout
        self._test_mode = test_mode if test_mode is not None else False
        self._verbose = verbose if verbose is not None else False
        self._tracer_instance = tracer_instance

        # Create API config
        self._api_config = APIConfig(
            base_path=resolved_base_url,
            cp_base_path=resolved_cp_base_url,
            access_token=self._api_key,
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

        # Alias for backwards compatibility
        self.evaluations = self.experiments

    @property
    def test_mode(self) -> bool:
        """Return whether client is in test mode."""
        return self._test_mode

    @property
    def verbose(self) -> bool:
        """Return whether verbose mode is enabled."""
        return self._verbose

    @property
    def timeout(self) -> Optional[float]:
        """Return the configured timeout."""
        return self._timeout

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
