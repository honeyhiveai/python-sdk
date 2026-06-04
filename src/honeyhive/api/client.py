"""HoneyHive API Client.

This module provides the main HoneyHive client with an ergonomic interface
wrapping the auto-generated API code.

Usage::

    from honeyhive.api import HoneyHive

    client = HoneyHive(api_key="your-api-key")

    # Sync usage
    configs = client.configurations.list()

    # Async usage
    configs = await client.configurations.list_async()
"""

import asyncio
import logging
import os
import warnings
from typing import Any, Dict, List, Optional, TypeVar, Union

import httpx

try:
    from warnings import deprecated
except ImportError:
    from typing_extensions import deprecated

from honeyhive._generated.api_config import APIConfig

# Import async services
# Import sync services
from honeyhive._generated.services import Charts_service as charts_svc
from honeyhive._generated.services import Configurations_service as configs_svc
from honeyhive._generated.services import Datapoints_service as datapoints_svc
from honeyhive._generated.services import Datasets_service as datasets_svc
from honeyhive._generated.services import Events_service as events_svc
from honeyhive._generated.services import Experiments_service as experiments_svc
from honeyhive._generated.services import Metric_Versions_service as metric_versions_svc
from honeyhive._generated.services import Metrics_service as metrics_svc
from honeyhive._generated.services import Sessions_service as sessions_svc
from honeyhive._generated.services import async_Charts_service as charts_svc_async
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
from honeyhive._generated.services import (
    async_Metric_Versions_service as metric_versions_svc_async,
)
from honeyhive._generated.services import async_Metrics_service as metrics_svc_async
from honeyhive._generated.services import async_Sessions_service as sessions_svc_async

# Import models used in type hints
from honeyhive.models import (
    AddDatapointsResponse,
    AddDatapointsToDatasetRequest,
    ConfigurationItem,
    CreateChartRequest,
    CreateChartResponse,
    CreateConfigurationRequest,
    CreateConfigurationResponse,
    CreateDatapointRequest,
    CreateDatapointResponse,
    CreateDatasetRequest,
    CreateDatasetResponse,
    CreateMetricRequest,
    CreateMetricResponse,
    CreateMetricVersionRequest,
    CreateMetricVersionResponse,
    DeleteChartResponse,
    DeleteConfigurationResponse,
    DeleteDatapointResponse,
    DeleteDatasetResponse,
    DeleteExperimentRunResponse,
    DeleteMetricResponse,
    DeployMetricVersionResponse,
    EventExportResponse,
    EventFilter,
    GetChartResponse,
    GetChartsResponse,
    GetDatapointResponse,
    GetDatapointsResponse,
    GetDatasetsResponse,
    GetEventsQuery,
    GetEventsResponse,
    GetEventsSchemaResponse,
    GetExperimentRunResponse,
    GetExperimentRunsResponse,
    GetMetricVersionsResponse,
    MetricItem,
    Pagination,
    PostEventBatchRequest,
    PostEventBatchResponse,
    PostEventRequest,
    PostEventResponse,
    PostExperimentRunRequest,
    PostExperimentRunResponse,
    PostSessionStartResponse,
    PutExperimentRunRequest,
    PutExperimentRunResponse,
    RemoveDatapointResponse,
    StartSessionRequest,
    UpdateChartRequest,
    UpdateChartResponse,
    UpdateConfigurationRequest,
    UpdateConfigurationResponse,
    UpdateDatapointRequest,
    UpdateDatapointResponse,
    UpdateDatasetRequest,
    UpdateDatasetResponse,
    UpdateEventRequest,
    UpdateMetricRequest,
    UpdateMetricResponse,
)
from honeyhive.utils.retry import RetryConfig

from ._base import BaseAPI

logger = logging.getLogger(__name__)

# Maximum number of array items to send in a single query string request.
# Real-world URL length limits (8-16 KB) cap practical array sizes at ~170-340
# items for typical 26-char IDs. Batching at 100 keeps us safely within bounds.
QUERY_BATCH_SIZE = 100

# Default read timeout for event export requests (seconds).
# The default httpx timeout of 5s is too low for large exports (e.g. 7500 events
# can take 30s+). Override via the HH_EXPORT_TIMEOUT_SECONDS env var.
_DEFAULT_EXPORT_READ_TIMEOUT = 300.0


def _build_export_timeout() -> httpx.Timeout:
    """Build the timeout for export HTTP clients.

    Reads the ``HH_EXPORT_TIMEOUT_SECONDS`` environment variable (if set) to
    override the default read timeout.  Connect / write / pool timeouts stay
    short so unreachable hosts fail fast.
    """
    read = _DEFAULT_EXPORT_READ_TIMEOUT
    env_val = os.environ.get("HH_EXPORT_TIMEOUT_SECONDS")
    if env_val is not None:
        try:
            parsed = float(env_val)
            if parsed > 0:
                read = parsed
            else:
                logger.warning(
                    "HH_EXPORT_TIMEOUT_SECONDS must be positive, got %s; "
                    "using default %s",
                    env_val,
                    _DEFAULT_EXPORT_READ_TIMEOUT,
                )
        except (ValueError, TypeError):
            logger.warning(
                "HH_EXPORT_TIMEOUT_SECONDS is not a valid number: %r; using default %s",
                env_val,
                _DEFAULT_EXPORT_READ_TIMEOUT,
            )
    return httpx.Timeout(connect=10.0, read=read, write=30.0, pool=10.0)


EXPORT_TIMEOUT = _build_export_timeout()


T = TypeVar("T")


def _chunk_list(items: List[T], size: int) -> List[List[T]]:
    """Split a list into chunks of the given size."""
    return [items[i : i + size] for i in range(0, len(items), size)]


class ChartsAPI(BaseAPI):
    """Charts API."""

    def list(self) -> GetChartsResponse:
        """List charts in the current scope."""
        return charts_svc.getCharts(self._api_config)

    def get(self, chart_id: str) -> GetChartResponse:
        """Get a chart by ID."""
        return charts_svc.getChart(self._api_config, chart_id=chart_id)

    def create(self, request: CreateChartRequest) -> CreateChartResponse:
        """Create a chart."""
        return charts_svc.createChart(self._api_config, data=request)

    def update(self, chart_id: str, request: UpdateChartRequest) -> UpdateChartResponse:
        """Update a chart."""
        return charts_svc.updateChart(self._api_config, chart_id=chart_id, data=request)

    def delete(self, chart_id: str) -> DeleteChartResponse:
        """Delete a chart."""
        return charts_svc.deleteChart(self._api_config, chart_id=chart_id)

    async def list_async(self) -> GetChartsResponse:
        """List charts in the current scope asynchronously."""
        return await charts_svc_async.getCharts(self._api_config)

    async def get_async(self, chart_id: str) -> GetChartResponse:
        """Get a chart by ID asynchronously."""
        return await charts_svc_async.getChart(self._api_config, chart_id=chart_id)

    async def create_async(self, request: CreateChartRequest) -> CreateChartResponse:
        """Create a chart asynchronously."""
        return await charts_svc_async.createChart(self._api_config, data=request)

    async def update_async(
        self, chart_id: str, request: UpdateChartRequest
    ) -> UpdateChartResponse:
        """Update a chart asynchronously."""
        return await charts_svc_async.updateChart(
            self._api_config, chart_id=chart_id, data=request
        )

    async def delete_async(self, chart_id: str) -> DeleteChartResponse:
        """Delete a chart asynchronously."""
        return await charts_svc_async.deleteChart(self._api_config, chart_id=chart_id)


class ConfigurationsAPI(BaseAPI):
    """Configurations API."""

    # Sync methods
    def list(self, project: Optional[str] = None) -> List[ConfigurationItem]:
        """List configurations.

        Note:
            The v1 API does not currently support project filtering.
        """
        if project is not None:
            warnings.warn(
                "The 'project' parameter is no longer supported for "
                "configurations.list() and will be removed in v2.0.",
                DeprecationWarning,
                stacklevel=2,
            )
        del project
        # Preserve the high-level SDK list surface by unwrapping the transport envelope.
        response = configs_svc.getConfigurations(self._api_config)
        return response.configurations

    def create(
        self, request: CreateConfigurationRequest
    ) -> CreateConfigurationResponse:
        """Create a configuration."""
        return configs_svc.createConfiguration(self._api_config, data=request)

    def update(
        self, id: str, request: UpdateConfigurationRequest
    ) -> UpdateConfigurationResponse:
        """Update a configuration."""
        return configs_svc.updateConfiguration(
            self._api_config, configId=id, data=request
        )

    def delete(self, id: str) -> DeleteConfigurationResponse:
        """Delete a configuration."""
        return configs_svc.deleteConfiguration(self._api_config, configId=id)

    # Async methods
    async def list_async(
        self, project: Optional[str] = None
    ) -> List[ConfigurationItem]:
        """List configurations asynchronously.

        Note:
            The v1 API does not currently support project filtering.
        """
        if project is not None:
            warnings.warn(
                "The 'project' parameter is no longer supported for "
                "configurations.list() and will be removed in v2.0.",
                DeprecationWarning,
                stacklevel=2,
            )
        del project
        response = await configs_svc_async.getConfigurations(self._api_config)
        return response.configurations

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
            self._api_config, configId=id, data=request
        )

    async def delete_async(self, id: str) -> DeleteConfigurationResponse:
        """Delete a configuration asynchronously."""
        return await configs_svc_async.deleteConfiguration(
            self._api_config, configId=id
        )

    # Backwards compatible aliases
    def get_configuration(self, id: str) -> List[ConfigurationItem]:
        """Get a configuration (backwards compatible alias)."""
        del id
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
    ) -> List[ConfigurationItem]:
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

        When datapoint_ids exceeds QUERY_BATCH_SIZE, requests are automatically
        batched to stay within URL length limits and the results are merged.

        Args:
            datapoint_ids: Optional list of datapoint IDs to fetch.
            dataset_name: Optional dataset name to filter by.
        """
        # Batch if the list is large enough to risk exceeding URL length limits.
        if datapoint_ids and len(datapoint_ids) > QUERY_BATCH_SIZE:
            all_datapoints: List[Any] = []
            batches = _chunk_list(datapoint_ids, QUERY_BATCH_SIZE)
            for i, batch in enumerate(batches):
                try:
                    resp = datapoints_svc.getDatapoints(
                        self._api_config,
                        datapoint_ids=batch,
                        dataset_name=dataset_name,
                    )
                except Exception:
                    logger.warning(
                        "Batch %d/%d failed (%d IDs)", i + 1, len(batches), len(batch)
                    )
                    raise
                all_datapoints.extend(resp.datapoints)
            # Skip re-validation — items are already validated Datapoint instances.
            return GetDatapointsResponse.model_construct(datapoints=all_datapoints)

        return datapoints_svc.getDatapoints(
            self._api_config, datapoint_ids=datapoint_ids, dataset_name=dataset_name
        )

    def get(self, id: str) -> GetDatapointResponse:
        """Get a datapoint by ID."""
        return datapoints_svc.getDatapoint(self._api_config, datapoint_id=id)

    def create(self, request: CreateDatapointRequest) -> CreateDatapointResponse:
        """Create a datapoint."""
        return datapoints_svc.createDatapoint(self._api_config, data=request)

    def update(
        self, id: str, request: UpdateDatapointRequest
    ) -> UpdateDatapointResponse:
        """Update a datapoint."""
        return datapoints_svc.updateDatapoint(
            self._api_config, datapoint_id=id, data=request
        )

    def delete(self, id: str) -> DeleteDatapointResponse:
        """Delete a datapoint."""
        return datapoints_svc.deleteDatapoint(self._api_config, datapoint_id=id)

    # Async methods
    async def list_async(
        self,
        datapoint_ids: Optional[List[str]] = None,
        dataset_name: Optional[str] = None,
    ) -> GetDatapointsResponse:
        """List datapoints asynchronously.

        When datapoint_ids exceeds QUERY_BATCH_SIZE, requests are automatically
        batched to stay within URL length limits and the results are merged.

        Args:
            datapoint_ids: Optional list of datapoint IDs to fetch.
            dataset_name: Optional dataset name to filter by.
        """
        # Batch if the list is large enough to risk exceeding URL length limits.
        if datapoint_ids and len(datapoint_ids) > QUERY_BATCH_SIZE:
            batches = _chunk_list(datapoint_ids, QUERY_BATCH_SIZE)
            resps = await asyncio.gather(
                *(
                    datapoints_svc_async.getDatapoints(
                        self._api_config,
                        datapoint_ids=batch,
                        dataset_name=dataset_name,
                    )
                    for batch in batches
                )
            )
            all_datapoints: List[Any] = []
            for resp in resps:
                all_datapoints.extend(resp.datapoints)
            # Skip re-validation — items are already validated Datapoint instances.
            return GetDatapointsResponse.model_construct(datapoints=all_datapoints)

        return await datapoints_svc_async.getDatapoints(
            self._api_config, datapoint_ids=datapoint_ids, dataset_name=dataset_name
        )

    async def get_async(self, id: str) -> GetDatapointResponse:
        """Get a datapoint by ID asynchronously."""
        return await datapoints_svc_async.getDatapoint(
            self._api_config, datapoint_id=id
        )

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
            self._api_config, datapoint_id=id, data=request
        )

    async def delete_async(self, id: str) -> DeleteDatapointResponse:
        """Delete a datapoint asynchronously."""
        return await datapoints_svc_async.deleteDatapoint(
            self._api_config, datapoint_id=id
        )

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
    ) -> GetDatasetsResponse:
        """List datasets.

        Args:
            dataset_id: Optional dataset ID to fetch.
            name: Optional dataset name to filter by.
        """
        return datasets_svc.getDatasets(
            self._api_config,
            dataset_id=dataset_id,
            name=name,
        )

    def create(self, request: CreateDatasetRequest) -> CreateDatasetResponse:
        """Create a dataset."""
        return datasets_svc.createDataset(self._api_config, data=request)

    def update(self, request: UpdateDatasetRequest) -> UpdateDatasetResponse:
        """Update a dataset."""
        return datasets_svc.updateDatasetLegacy(self._api_config, data=request)

    def delete(self, id: str) -> DeleteDatasetResponse:
        """Delete a dataset."""
        return datasets_svc.deleteDatasetLegacy(self._api_config, dataset_id=id)

    def add_datapoints(
        self, dataset_id: str, request: AddDatapointsToDatasetRequest
    ) -> AddDatapointsResponse:
        """Add datapoints to a dataset.

        Args:
            dataset_id: The unique identifier of the dataset to add datapoints to.
            request: The request containing data and mapping for the datapoints.

        Returns:
            AddDatapointsResponse with inserted status and datapoint IDs.
        """
        return datasets_svc.addDatapoints(
            self._api_config, dataset_id=dataset_id, data=request
        )

    def remove_datapoint(
        self, dataset_id: str, datapoint_id: str
    ) -> RemoveDatapointResponse:
        """Remove a datapoint from a dataset.

        Args:
            dataset_id: The unique identifier of the dataset.
            datapoint_id: The unique identifier of the datapoint to remove.

        Returns:
            RemoveDatapointResponse with dereferenced status and message.
        """
        return datasets_svc.removeDatapointLegacy(
            self._api_config, dataset_id=dataset_id, datapoint_id=datapoint_id
        )

    # Async methods
    async def list_async(
        self,
        dataset_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> GetDatasetsResponse:
        """List datasets asynchronously.

        Args:
            dataset_id: Optional dataset ID to fetch.
            name: Optional dataset name to filter by.
        """
        return await datasets_svc_async.getDatasets(
            self._api_config,
            dataset_id=dataset_id,
            name=name,
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
        return await datasets_svc_async.updateDatasetLegacy(
            self._api_config, data=request
        )

    async def delete_async(self, id: str) -> DeleteDatasetResponse:
        """Delete a dataset asynchronously."""
        return await datasets_svc_async.deleteDatasetLegacy(
            self._api_config, dataset_id=id
        )

    async def add_datapoints_async(
        self, dataset_id: str, request: AddDatapointsToDatasetRequest
    ) -> AddDatapointsResponse:
        """Add datapoints to a dataset asynchronously.

        Args:
            dataset_id: The unique identifier of the dataset to add datapoints to.
            request: The request containing data and mapping for the datapoints.

        Returns:
            AddDatapointsResponse with inserted status and datapoint IDs.
        """
        return await datasets_svc_async.addDatapoints(
            self._api_config, dataset_id=dataset_id, data=request
        )

    async def remove_datapoint_async(
        self, dataset_id: str, datapoint_id: str
    ) -> RemoveDatapointResponse:
        """Remove a datapoint from a dataset asynchronously.

        Args:
            dataset_id: The unique identifier of the dataset.
            datapoint_id: The unique identifier of the datapoint to remove.

        Returns:
            RemoveDatapointResponse with dereferenced status and message.
        """
        return await datasets_svc_async.removeDatapointLegacy(
            self._api_config, dataset_id=dataset_id, datapoint_id=datapoint_id
        )

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
    ) -> GetDatasetsResponse:
        """List datasets (backwards compatible alias)."""
        return self.list(dataset_id=dataset_id, name=name)


class EventsAPI(BaseAPI):
    """Events API.

    Event reads and writes now go through Data Plane endpoints. Legacy helpers
    like list() and get_by_session_id() are retained for backward compatibility
    on top of the export endpoint.
    """

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
    def list(
        self,
        query: Optional[Union[GetEventsQuery, Dict[str, Any]]] = None,
        *,
        data: Optional[Union[GetEventsQuery, Dict[str, Any]]] = None,
    ) -> GetEventsResponse:
        """Get events via the legacy list helper.

        Args:
            query: Query parameters as GetEventsQuery model or dict.
                   Supported fields: dateRange, filters, projections,
                   ignore_order, limit, page, evaluation_id
            data: Backwards compatible alias for query.

        Returns:
            GetEventsResponse with matching events
        """
        # Support the legacy `data=` keyword while keeping the canonical `query=`
        # interface aligned with the current wrapper signature.
        payload = data if data is not None else query
        if payload is None:
            raise ValueError("EventsAPI.list requires query or data")

        # Convert to dict if Pydantic model
        if hasattr(payload, "model_dump"):
            payload_data = payload.model_dump(exclude_none=True)
        else:
            payload_data = payload

        # Filter data to only include supported parameters for the legacy list()
        # helper. The canonical spec exposes event reads through export().
        filtered_data = {
            k: v
            for k, v in payload_data.items()
            if k in self._GET_EVENTS_SUPPORTED_PARAMS
        }
        export_response = self.export(
            filters=filtered_data.get("filters"),
            date_range=filtered_data.get("dateRange"),
            projections=filtered_data.get("projections"),
            limit=filtered_data.get("limit", 1000),
            page=filtered_data.get("page", 1),
        )
        return GetEventsResponse(
            events=export_response.events,
            totalEvents=export_response.total_events,
        )

    @deprecated(
        "events.get_by_session_id() is deprecated; use events.export() with a "
        "session_id filter instead.",
        category=None,
    )
    def get_by_session_id(
        self,
        session_id: str,
        project: Optional[str] = None,
        *,
        limit: int = 1000,
    ) -> EventExportResponse:
        """Get events by session ID using the Data Plane export endpoint.

        Deprecated: this compatibility helper wraps export() with a session_id
        filter. New code should call events.export() directly.
        Events are returned sorted by start_time in chronological order.

        Args:
            session_id: The session ID to fetch events for.
            project: Project name associated with the events. Deprecated in v1.0
                and will be removed in v2.0. The backend now infers project from
                session_id.
            limit: Maximum number of events to return (default 1000).

        Returns:
            EventExportResponse with events for the session, sorted by start_time.

        Example::

            response = client.events.export(
                filters=[
                    EventFilter(
                        field="session_id",
                        operator="is",
                        value="abc-123",
                        type="string",
                    )
                ]
            )
            for event in response.events:
                print(event["event_name"])
        """
        logger.debug(
            "get_by_session_id called: session_id=%s limit=%d",
            session_id,
            limit,
        )
        warnings.warn(
            "events.get_by_session_id() is deprecated and kept for backward "
            "compatibility only. Use events.export() with a session_id filter "
            "instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if project is not None:
            warnings.warn(
                "The 'project' parameter is deprecated and will be removed in v2.0. "
                "The backend now infers project from session_id.",
                DeprecationWarning,
                stacklevel=2,
            )

        result = self.export(
            project=project,
            filters=[
                EventFilter(
                    field="session_id",
                    operator="is",
                    value=session_id,
                    type="string",
                )
            ],
            limit=limit,
            _sort_by_time=True,  # Enable time-based sorting
        )
        logger.debug(
            "get_by_session_id result: session_id=%s events=%d total=%d",
            session_id,
            len(result.events),
            result.total_events,
        )
        return result

    def create(self, request: PostEventRequest) -> PostEventResponse:
        """Create an event."""
        return events_svc.createEventLegacy(self._api_config, data=request)

    def update(self, data: UpdateEventRequest) -> None:
        """Update an event."""
        return events_svc.updateEventLegacy(self._api_config, data=data)

    def create_batch(self, data: PostEventBatchRequest) -> PostEventBatchResponse:
        """Create events in batch."""
        return events_svc.createEventBatchLegacy(self._api_config, data=data)

    def export(
        self,
        project: Optional[str] = None,
        filters: Optional[List[Union[EventFilter, Dict[str, Any]]]] = None,
        *,
        date_range: Optional[Dict[str, str]] = None,
        projections: Optional[List[str]] = None,
        limit: int = 1000,
        page: int = 1,
        _sort_by_time: bool = False,
    ) -> EventExportResponse:
        """Export events via POST /events/export (Data Plane).

        This is the primary method for retrieving events from HoneyHive.
        It uses the Data Plane endpoint which supports filtering by session_id,
        event_type, and other fields.

        Args:
            project: Project name associated with the events. Deprecated in v1.0
                and will be removed in v2.0. The backend now infers project from
                filters (e.g., session_id).
            filters: List of EventFilter objects or dicts with filter criteria.
                Each filter should have: field, operator, value, type.
            date_range: Optional date range filter with '$gte' and '$lte' keys
                containing ISO timestamp strings.
            projections: Optional list of fields to include in the response.
            limit: Maximum number of results (default 1000, max 7500).
            page: Page number for pagination (default 1).
            _sort_by_time: Internal flag to sort events by start_time (default False).

        Returns:
            EventExportResponse with events list and total_events count.

        Example::

            from honeyhive.models import EventFilter

            # Export events for a session
            response = client.events.export(
                filters=[
                    EventFilter(
                        field="session_id",
                        operator="is",
                        value="abc-123",
                        type="string"
                    )
                ],
                limit=100
            )

            for event in response.events:
                print(event["event_name"])

            # Export with date range
            response = client.events.export(
                filters=[],
                date_range={
                    "$gte": "2024-01-01T00:00:00Z",
                    "$lte": "2024-01-31T23:59:59Z"
                }
            )
        """
        if project is not None:
            warnings.warn(
                "The 'project' parameter is deprecated and will be removed in v2.0. "
                "The backend now infers project from filters (e.g., session_id).",
                DeprecationWarning,
                stacklevel=2,
            )

        # Build filters array
        filters_data = []
        if filters:
            for f in filters:
                if isinstance(f, EventFilter):
                    filters_data.append(f.to_dict())
                elif isinstance(f, dict):
                    filters_data.append(f)

        # Build request body
        request_body: Dict[str, Any] = {
            "filters": filters_data,
            "limit": limit,
            "page": page,
        }

        # Only include project if provided (for backwards compatibility)
        if project is not None:
            request_body["project"] = project

        if date_range:
            request_body["dateRange"] = date_range
        if projections:
            request_body["projections"] = projections

        # Make direct request to /events/export (bypasses generated model issues)
        base_path = self._api_config.base_path
        headers = self._api_config.get_default_headers()

        # Log outgoing request metadata
        logger.debug(
            "export request: POST %s/v1/events/export limit=%d page=%d",
            base_path,
            limit,
            page,
        )

        # Execute with retry logic for transient errors (502, 503, 504, etc.)
        retry_config = RetryConfig.default()
        with httpx.Client(
            base_url=base_path,
            verify=self._api_config.verify,
            timeout=EXPORT_TIMEOUT,
        ) as client:
            response = retry_config.execute(
                lambda: client.request(
                    "POST",
                    "/v1/events/export",
                    headers=headers,
                    json=request_body,
                ),
                operation="export()",
            )

        data = response.json()
        events = data.get("events", [])
        total_events = data.get("totalEvents", data.get("count", 0))

        logger.debug(
            "export result: %d events, total_events=%d",
            len(events),
            total_events,
        )
        if not events:
            logger.debug(
                "export returned empty events list; limit=%d page=%d",
                limit,
                page,
            )

        # Sort events by start_time if requested (fixes jumbled order issue)
        if _sort_by_time and events:
            events = self._sort_events_by_time(events)

        return EventExportResponse(
            events=events,
            total_events=total_events,
        )

    def _sort_events_by_time(
        self, events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Sort events by start_time in chronological order.

        Args:
            events: List of event dictionaries.

        Returns:
            Sorted list of events by start_time.
        """

        def get_start_time(event: Dict[str, Any]) -> float:
            """Extract start_time from event, handling various formats."""
            # Try different possible field names for start time
            start_time = (
                event.get("start_time")
                or event.get("startTime")
                or event.get("created_at")
            )
            if start_time is None:
                return 0.0
            # Handle both numeric timestamps and ISO string formats
            if isinstance(start_time, (int, float)):
                return float(start_time)
            if isinstance(start_time, str):
                try:
                    from datetime import datetime

                    # Try ISO format parsing
                    if "T" in start_time:
                        dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                        return dt.timestamp()
                except (ValueError, TypeError):
                    pass
            return 0.0

        return sorted(events, key=get_start_time)

    # Async methods
    async def list_async(
        self, query: Union[GetEventsQuery, Dict[str, Any]]
    ) -> GetEventsResponse:
        """Get events asynchronously via the legacy list helper.

        Args:
            query: Query parameters as GetEventsQuery model or dict.

        Returns:
            GetEventsResponse with matching events
        """
        # Convert to dict if Pydantic model
        if hasattr(query, "model_dump"):
            data = query.model_dump(exclude_none=True)
        else:
            data = query

        # Filter data to only include supported parameters for the legacy list()
        # helper. The canonical spec exposes event reads through export().
        filtered_data = {
            k: v for k, v in data.items() if k in self._GET_EVENTS_SUPPORTED_PARAMS
        }
        export_response = await self.export_async(
            filters=filtered_data.get("filters"),
            date_range=filtered_data.get("dateRange"),
            projections=filtered_data.get("projections"),
            limit=filtered_data.get("limit", 1000),
            page=filtered_data.get("page", 1),
        )
        return GetEventsResponse(
            events=export_response.events,
            totalEvents=export_response.total_events,
        )

    @deprecated(
        "events.get_by_session_id_async() is deprecated; use "
        "events.export_async() with a session_id filter instead.",
        category=None,
    )
    async def get_by_session_id_async(
        self,
        session_id: str,
        project: Optional[str] = None,
        *,
        limit: int = 1000,
    ) -> EventExportResponse:
        """Get events by session ID asynchronously using the Data Plane export endpoint.

        Deprecated: this compatibility helper wraps export_async() with a
        session_id filter. New code should call events.export_async() directly.
        Events are returned sorted by start_time in chronological order.

        Args:
            session_id: The session ID to fetch events for.
            project: Project name associated with the events. Deprecated in v1.0
                and will be removed in v2.0. The backend now infers project from
                session_id.
            limit: Maximum number of events to return (default 1000).

        Returns:
            EventExportResponse with events for the session, sorted by start_time.
        """
        logger.debug(
            "get_by_session_id_async called: session_id=%s limit=%d",
            session_id,
            limit,
        )
        warnings.warn(
            "events.get_by_session_id_async() is deprecated and kept for backward "
            "compatibility only. Use events.export_async() with a session_id "
            "filter instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if project is not None:
            warnings.warn(
                "The 'project' parameter is deprecated and will be removed in v2.0. "
                "The backend now infers project from session_id.",
                DeprecationWarning,
                stacklevel=2,
            )

        result = await self.export_async(
            project=project,
            filters=[
                EventFilter(
                    field="session_id",
                    operator="is",
                    value=session_id,
                    type="string",
                )
            ],
            limit=limit,
            _sort_by_time=True,  # Enable time-based sorting
        )
        logger.debug(
            "get_by_session_id_async result: session_id=%s events=%d total=%d",
            session_id,
            len(result.events),
            result.total_events,
        )
        return result

    async def create_async(self, request: PostEventRequest) -> PostEventResponse:
        """Create an event asynchronously."""
        return await events_svc_async.createEventLegacy(self._api_config, data=request)

    async def update_async(self, data: UpdateEventRequest) -> None:
        """Update an event asynchronously."""
        return await events_svc_async.updateEventLegacy(self._api_config, data=data)

    async def create_batch_async(
        self, data: PostEventBatchRequest
    ) -> PostEventBatchResponse:
        """Create events in batch asynchronously."""
        return await events_svc_async.createEventBatchLegacy(
            self._api_config, data=data
        )

    async def export_async(
        self,
        project: Optional[str] = None,
        filters: Optional[List[Union[EventFilter, Dict[str, Any]]]] = None,
        *,
        date_range: Optional[Dict[str, str]] = None,
        projections: Optional[List[str]] = None,
        limit: int = 1000,
        page: int = 1,
        _sort_by_time: bool = False,
    ) -> EventExportResponse:
        """Export events via POST /events/export asynchronously (Data Plane).

        Async version of export(). See export() for full documentation.

        Args:
            project: Project name associated with the events. Deprecated in v1.0
                and will be removed in v2.0. The backend now infers project from
                filters (e.g., session_id).
            filters: List of EventFilter objects or dicts with filter criteria.
            date_range: Optional date range filter.
            projections: Optional list of fields to include in the response.
            limit: Maximum number of results (default 1000, max 7500).
            page: Page number for pagination (default 1).
            _sort_by_time: Internal flag to sort events by start_time (default False).

        Returns:
            EventExportResponse with events list and total_events count.
        """
        if project is not None:
            warnings.warn(
                "The 'project' parameter is deprecated and will be removed in v2.0. "
                "The backend now infers project from filters (e.g., session_id).",
                DeprecationWarning,
                stacklevel=2,
            )

        # Build filters array
        filters_data = []
        if filters:
            for f in filters:
                if isinstance(f, EventFilter):
                    filters_data.append(f.to_dict())
                elif isinstance(f, dict):
                    filters_data.append(f)

        # Build request body
        request_body: Dict[str, Any] = {
            "filters": filters_data,
            "limit": limit,
            "page": page,
        }

        # Only include project if provided (for backwards compatibility)
        if project is not None:
            request_body["project"] = project

        if date_range:
            request_body["dateRange"] = date_range
        if projections:
            request_body["projections"] = projections

        # Make direct async request to /events/export
        base_path = self._api_config.base_path
        headers = self._api_config.get_default_headers()

        # Log outgoing request metadata
        logger.debug(
            "export_async request: POST %s/v1/events/export limit=%d page=%d",
            base_path,
            limit,
            page,
        )

        # Execute with retry logic for transient errors (502, 503, 504, etc.)
        retry_config = RetryConfig.default()
        async with httpx.AsyncClient(
            base_url=base_path,
            verify=self._api_config.verify,
            timeout=EXPORT_TIMEOUT,
        ) as client:
            response = await retry_config.execute_async(
                lambda: client.request(
                    "POST",
                    "/v1/events/export",
                    headers=headers,
                    json=request_body,
                ),
                operation="export_async()",
            )

        data = response.json()
        events = data.get("events", [])
        total_events = data.get("totalEvents", data.get("count", 0))

        logger.debug(
            "export_async result: %d events, total_events=%d",
            len(events),
            total_events,
        )
        if not events:
            logger.debug(
                "export_async returned empty events list; limit=%d page=%d",
                limit,
                page,
            )

        # Sort events by start_time if requested (fixes jumbled order issue)
        if _sort_by_time and events:
            events = self._sort_events_by_time(events)

        return EventExportResponse(
            events=events,
            total_events=total_events,
        )

    # Backwards compatible aliases
    def create_event(self, request: PostEventRequest) -> PostEventResponse:
        """Create an event (backwards compatible alias for create())."""
        return self.create(request)

    def update_event(self, data: Dict[str, Any]) -> None:
        """Update an event (backwards compatible alias for update())."""
        return self.update(data)

    def list_events(
        self,
        project: Optional[str] = None,
        filters: Optional[List[Union[EventFilter, Dict[str, Any]]]] = None,
        *,
        date_range: Optional[Dict[str, str]] = None,
        projections: Optional[List[str]] = None,
        limit: int = 1000,
        page: int = 1,
    ) -> EventExportResponse:
        """List events via export endpoint (backwards compatible alias).

        This is a backwards compatible alias for export(). Uses the Data Plane
        POST /events/export endpoint.

        Args:
            project: Project name. Deprecated in v1.0 and will be removed in v2.0.
            filters: List of EventFilter objects or dicts.
            date_range: Optional date range filter.
            projections: Optional list of fields to include.
            limit: Maximum number of results (default 1000).
            page: Page number (default 1).

        Returns:
            EventExportResponse with events and total count.
        """
        return self.export(
            project=project,
            filters=filters,
            date_range=date_range,
            projections=projections,
            limit=limit,
            page=page,
        )

    def get_events(
        self,
        project: Optional[str] = None,
        filters: Optional[List[Union[EventFilter, Dict[str, Any]]]] = None,
        *,
        date_range: Optional[Dict[str, str]] = None,
        projections: Optional[List[str]] = None,
        limit: int = 1000,
        page: int = 1,
    ) -> EventExportResponse:
        """Get events via export endpoint (backwards compatible alias).

        This is a backwards compatible alias for export(). Uses the Data Plane
        POST /events/export endpoint.

        Args:
            project: Project name. Deprecated in v1.0 and will be removed in v2.0.
            filters: List of EventFilter objects or dicts.
            date_range: Optional date range filter.
            projections: Optional list of fields to include.
            limit: Maximum number of results (default 1000).
            page: Page number (default 1).

        Returns:
            EventExportResponse with events and total count.
        """
        return self.export(
            project=project,
            filters=filters,
            date_range=date_range,
            projections=projections,
            limit=limit,
            page=page,
        )

    async def list_events_async(
        self,
        project: Optional[str] = None,
        filters: Optional[List[Union[EventFilter, Dict[str, Any]]]] = None,
        *,
        date_range: Optional[Dict[str, str]] = None,
        projections: Optional[List[str]] = None,
        limit: int = 1000,
        page: int = 1,
    ) -> EventExportResponse:
        """List events asynchronously (backwards compatible alias for export_async).

        Args:
            project: Project name. Deprecated in v1.0 and will be removed in v2.0.
        """
        return await self.export_async(
            project=project,
            filters=filters,
            date_range=date_range,
            projections=projections,
            limit=limit,
            page=page,
        )

    async def get_events_async(
        self,
        project: Optional[str] = None,
        filters: Optional[List[Union[EventFilter, Dict[str, Any]]]] = None,
        *,
        date_range: Optional[Dict[str, str]] = None,
        projections: Optional[List[str]] = None,
        limit: int = 1000,
        page: int = 1,
    ) -> EventExportResponse:
        """Get events asynchronously (backwards compatible alias for export_async).

        Args:
            project: Project name. Deprecated in v1.0 and will be removed in v2.0.
        """
        return await self.export_async(
            project=project,
            filters=filters,
            date_range=date_range,
            projections=projections,
            limit=limit,
            page=page,
        )


class ExperimentsAPI(BaseAPI):
    """Experiments API."""

    # Sync methods
    def get_schema(
        self,
        dateRange: Optional[Any] = None,
        evaluation_id: Optional[str] = None,
    ) -> GetEventsSchemaResponse:
        """Get experiment runs schema.

        Args:
            dateRange: Filter by date range (string or dict with $gte/$lte).
            evaluation_id: Filter by evaluation/run ID.
        """
        return events_svc.getEventsSchemaLegacy(
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

        When run_ids exceeds QUERY_BATCH_SIZE, requests are automatically
        batched to stay within URL length limits and the results are merged.

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
        # Batch if the list is large enough to risk exceeding URL length limits.
        if run_ids and len(run_ids) > QUERY_BATCH_SIZE:
            return self._batched_list_runs(
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

    def _batched_list_runs(
        self, *, run_ids: List[str], **kwargs: Any
    ) -> GetExperimentRunsResponse:
        """Fetch runs in batches and merge the responses."""
        # Pagination doesn't apply when batching by IDs — each batch must
        # return all matching runs for its chunk.
        kwargs.pop("page", None)
        kwargs.pop("limit", None)

        all_evaluations: List[Any] = []
        all_metrics: List[str] = []
        total = 0
        total_unfiltered = 0

        batches = _chunk_list(run_ids, QUERY_BATCH_SIZE)
        for i, batch in enumerate(batches):
            try:
                resp = experiments_svc.getRuns(
                    self._api_config, run_ids=batch, **kwargs
                )
            except Exception:
                logger.warning(
                    "Batch %d/%d failed (%d run IDs)",
                    i + 1,
                    len(batches),
                    len(batch),
                )
                raise
            all_evaluations.extend(resp.evaluations)
            all_metrics.extend(resp.metrics)
            total += resp.pagination.total
            total_unfiltered += resp.pagination.total_unfiltered

        return GetExperimentRunsResponse.model_construct(
            evaluations=all_evaluations,
            metrics=list(dict.fromkeys(all_metrics)),  # deduplicate, preserve order
            pagination=Pagination(
                page=1,
                limit=total,
                total=total,
                total_unfiltered=total_unfiltered,
                total_pages=1,
                has_next=False,
                has_prev=False,
            ),
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
    ) -> GetEventsSchemaResponse:
        """Get experiment runs schema asynchronously.

        Args:
            dateRange: Filter by date range (string or dict with $gte/$lte).
            evaluation_id: Filter by evaluation/run ID.
        """
        return await events_svc_async.getEventsSchemaLegacy(
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

        When run_ids exceeds QUERY_BATCH_SIZE, requests are automatically
        batched to stay within URL length limits and the results are merged.

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
        # Batch if the list is large enough to risk exceeding URL length limits.
        if run_ids and len(run_ids) > QUERY_BATCH_SIZE:
            return await self._batched_list_runs_async(
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

    async def _batched_list_runs_async(
        self, *, run_ids: List[str], **kwargs: Any
    ) -> GetExperimentRunsResponse:
        """Fetch runs in batches (async, parallel) and merge the responses."""
        # Strip pagination params — each batch fetches its full slice.
        kwargs.pop("page", None)
        kwargs.pop("limit", None)

        batches = _chunk_list(run_ids, QUERY_BATCH_SIZE)
        resps = await asyncio.gather(
            *(
                experiments_svc_async.getRuns(self._api_config, run_ids=batch, **kwargs)
                for batch in batches
            )
        )

        all_evaluations: List[Any] = []
        all_metrics: List[str] = []
        total = 0
        total_unfiltered = 0
        for resp in resps:
            all_evaluations.extend(resp.evaluations)
            all_metrics.extend(resp.metrics)
            total += resp.pagination.total
            total_unfiltered += resp.pagination.total_unfiltered

        return GetExperimentRunsResponse.model_construct(
            evaluations=all_evaluations,
            metrics=list(dict.fromkeys(all_metrics)),  # deduplicate, preserve order
            pagination=Pagination(
                page=1,
                limit=total,
                total=total,
                total_unfiltered=total_unfiltered,
                total_pages=1,
                has_next=False,
                has_prev=False,
            ),
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
        result = experiments_svc.getExperimentResultLegacy(
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
        result = experiments_svc.getExperimentComparisonLegacy(
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
        result = await experiments_svc_async.getExperimentResultLegacy(
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
        result = await experiments_svc_async.getExperimentComparisonLegacy(
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
        return experiments_svc.getExperimentCompareEventsLegacy(
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
    ) -> List[MetricItem]:
        """List metrics."""
        # Keep the legacy filters in the public signature for back-compat, but
        # warn because the dataplane metrics list endpoint no longer honors them.
        if project is not None or name is not None:
            warnings.warn(
                "The 'project' and 'name' parameters are no longer supported for "
                "metrics.list() and will be removed in v2.0.",
                DeprecationWarning,
                stacklevel=2,
            )
        # The regenerated client only supports filtering by metric type or ID.
        del project, name
        # Preserve the high-level SDK list surface by unwrapping the transport envelope.
        response = metrics_svc.getMetrics(self._api_config, type=type)
        return response.metrics

    def create(self, request: CreateMetricRequest) -> CreateMetricResponse:
        """Create a metric."""
        return metrics_svc.createMetric(self._api_config, data=request)

    def update(self, request: UpdateMetricRequest) -> UpdateMetricResponse:
        """Update a metric."""
        return metrics_svc.updateMetricLegacy(self._api_config, data=request)

    def delete(self, id: str) -> DeleteMetricResponse:
        """Delete a metric."""
        return metrics_svc.deleteMetricLegacy(self._api_config, metric_id=id)

    # Async methods
    async def list_async(
        self,
        project: Optional[str] = None,
        name: Optional[str] = None,
        type: Optional[str] = None,
    ) -> List[MetricItem]:
        """List metrics asynchronously."""
        # Keep the legacy filters in the public signature for back-compat, but
        # warn because the dataplane metrics list endpoint no longer honors them.
        if project is not None or name is not None:
            warnings.warn(
                "The 'project' and 'name' parameters are no longer supported for "
                "metrics.list() and will be removed in v2.0.",
                DeprecationWarning,
                stacklevel=2,
            )
        del project, name
        response = await metrics_svc_async.getMetrics(self._api_config, type=type)
        return response.metrics

    async def create_async(self, request: CreateMetricRequest) -> CreateMetricResponse:
        """Create a metric asynchronously."""
        return await metrics_svc_async.createMetric(self._api_config, data=request)

    async def update_async(self, request: UpdateMetricRequest) -> UpdateMetricResponse:
        """Update a metric asynchronously."""
        return await metrics_svc_async.updateMetricLegacy(
            self._api_config, data=request
        )

    async def delete_async(self, id: str) -> DeleteMetricResponse:
        """Delete a metric asynchronously."""
        return await metrics_svc_async.deleteMetricLegacy(
            self._api_config, metric_id=id
        )

    # Backwards compatible aliases
    def get_metric(self, id: str) -> List[MetricItem]:
        """Get a metric (backwards compatible alias)."""
        response = metrics_svc.getMetrics(self._api_config, id=id)
        return response.metrics

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
    ) -> List[MetricItem]:
        """List metrics (backwards compatible alias)."""
        return self.list(project=project, name=name, type=type)


class MetricVersionsAPI(BaseAPI):
    """Metric Versions API.

    Each metric has an immutable history of versions; one version at a time is
    marked as deployed (used by evaluations). Versions are nested under the
    parent metric at ``/v1/metrics/{metric_id}/versions``.
    """

    # Sync methods
    def list(self, metric_id: str) -> GetMetricVersionsResponse:
        """List all versions for a metric, oldest-first."""
        return metric_versions_svc.getMetricVersions(
            self._api_config, metric_id=metric_id
        )

    def create(
        self, metric_id: str, request: CreateMetricVersionRequest
    ) -> CreateMetricVersionResponse:
        """Create a new version of a metric.

        Set ``request.deploy_immediately = True`` to atomically mark the new
        version as deployed in the same transaction.
        """
        return metric_versions_svc.createMetricVersion(
            self._api_config, metric_id=metric_id, data=request
        )

    def deploy(self, metric_id: str, version_name: str) -> DeployMetricVersionResponse:
        """Deploy an existing version of a metric, replacing the live version."""
        return metric_versions_svc.deployMetricVersion(
            self._api_config, metric_id=metric_id, version_name=version_name
        )

    # Async methods
    async def list_async(self, metric_id: str) -> GetMetricVersionsResponse:
        """List all versions for a metric asynchronously."""
        return await metric_versions_svc_async.getMetricVersions(
            self._api_config, metric_id=metric_id
        )

    async def create_async(
        self, metric_id: str, request: CreateMetricVersionRequest
    ) -> CreateMetricVersionResponse:
        """Create a new version of a metric asynchronously."""
        return await metric_versions_svc_async.createMetricVersion(
            self._api_config, metric_id=metric_id, data=request
        )

    async def deploy_async(
        self, metric_id: str, version_name: str
    ) -> DeployMetricVersionResponse:
        """Deploy an existing version of a metric asynchronously."""
        return await metric_versions_svc_async.deployMetricVersion(
            self._api_config, metric_id=metric_id, version_name=version_name
        )


class SessionsAPI(BaseAPI):
    """Sessions API."""

    # The canonical spec only exposes session creation here. Session reads should
    # go through the event query/export helpers, keyed by session_id.

    @staticmethod
    def _coerce_start_session_request(
        data: Union[StartSessionRequest, Dict[str, Any]],
    ) -> StartSessionRequest:
        """Normalize session start inputs to the generated request model."""
        if isinstance(data, StartSessionRequest):
            return data

        if "session" in data:
            return StartSessionRequest(**data)

        # Older SDK callers pass the raw session payload directly. Keep accepting
        # that flat shape and wrap it into the nested request model for back-compat.
        warnings.warn(
            "Passing a flat session payload to sessions.start() is deprecated and "
            "will be removed in v2.0. Pass StartSessionRequest(session=...) or "
            "{'session': {...}} instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        return StartSessionRequest(session=data)

    def start(
        self, data: Union[StartSessionRequest, Dict[str, Any]]
    ) -> PostSessionStartResponse:
        """Start a new session."""
        request = self._coerce_start_session_request(data)
        return sessions_svc.startSessionLegacy(self._api_config, data=request)

    # Async methods
    async def start_async(
        self, data: Union[StartSessionRequest, Dict[str, Any]]
    ) -> PostSessionStartResponse:
        """Start a new session asynchronously."""
        request = self._coerce_start_session_request(data)
        return await sessions_svc_async.startSessionLegacy(
            self._api_config, data=request
        )

    # Backwards compatible aliases
    def create_session(
        self, request: Union[StartSessionRequest, Dict[str, Any]]
    ) -> PostSessionStartResponse:
        """Create/start a session (backwards compatible alias for start())."""
        return self.start(request)

    def start_session(
        self, request: Union[StartSessionRequest, Dict[str, Any]]
    ) -> PostSessionStartResponse:
        """Start a session (backwards compatible alias for start())."""
        return self.start(request)


class HoneyHive:
    """Main HoneyHive API client.

    Provides an ergonomic interface to the HoneyHive API with both
    sync and async methods.

    Example::

        client = HoneyHive(api_key="your-api-key")

        # Sync
        configs = client.configurations.list()

        # Async
        configs = await client.configurations.list_async()

    Attributes:
        configurations: API for managing configurations.
        datapoints: API for managing datapoints.
        datasets: API for managing datasets.
        events: API for managing events.
        experiments: API for managing experiment runs.
        metrics: API for managing metrics.
        sessions: API for managing sessions.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        # `project` sits at positional slot #2 to mirror the legacy SDK shape
        # — pre-1.0 callers wrote `HoneyHive("key", "project-name")` positionally.
        # Keeping the slot reserved means those calls still execute (with a
        # DeprecationWarning) instead of binding the value to `base_url` or
        # raising TypeError. The argument is otherwise ignored.
        project: Optional[str] = None,
        *,
        # Primary URL parameter
        base_url: Optional[str] = None,
        # Backwards compatible alias for base_url
        server_url: Optional[str] = None,
        # Backwards compatible parameters (accepted but not used in new client)
        cp_base_url: Optional[str] = None,
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
            api_key: HoneyHive API key (typically starts with ``hh_``).
                     Falls back to HH_API_KEY environment variable.
            project: Deprecated. Accepted for backwards compatibility only;
                the backend infers project context from the API key and session.
                Ignored when constructing the client.
            base_url: API base URL for HoneyHive.
                      Falls back to HH_API_URL env var, then https://api.dp1.us.honeyhive.ai.
            server_url: Deprecated alias for base_url (for backwards compatibility).
            cp_base_url: Deprecated. Accepted for backwards compatibility but ignored;
                the SDK now uses a single base_url for all operations.
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

        if project is not None:
            warnings.warn(
                "The 'project' argument to HoneyHive() is deprecated and ignored; "
                "it will be removed in v2.0. Remove it from HoneyHive() calls.",
                DeprecationWarning,
                stacklevel=2,
            )

        if cp_base_url is not None:
            warnings.warn(
                "The 'cp_base_url' parameter is no longer used and will be removed "
                "in v2.0. The SDK now uses a single base_url for all operations.",
                DeprecationWarning,
                stacklevel=2,
            )

        # Resolve API key from parameter or environment
        self._api_key = api_key or os.environ.get("HH_API_KEY", "")

        # Resolve base URL: base_url > server_url (legacy) > env var > default
        resolved_base_url = (
            base_url
            or server_url  # Legacy parameter
            or os.environ.get("HH_API_URL")
            or "https://api.dp1.us.honeyhive.ai"
        )

        # Store backwards compat params (silently accepted)
        self._timeout = timeout
        self._test_mode = test_mode if test_mode is not None else False
        self._verbose = verbose if verbose is not None else False
        self._tracer_instance = tracer_instance

        # Create API config
        self._api_config = APIConfig(
            base_path=resolved_base_url,
            access_token=self._api_key,
        )

        # Initialize API namespaces
        self.charts = ChartsAPI(self._api_config)
        self.configurations = ConfigurationsAPI(self._api_config)
        self.datapoints = DatapointsAPI(self._api_config)
        self.datasets = DatasetsAPI(self._api_config)
        self.events = EventsAPI(self._api_config)
        self.experiments = ExperimentsAPI(self._api_config)
        self.metrics = MetricsAPI(self._api_config)
        self.metric_versions = MetricVersionsAPI(self._api_config)
        self.sessions = SessionsAPI(self._api_config)

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
