"""HoneyHive Models - Re-exported from auto-generated Pydantic models.

Usage:
    from honeyhive.models import CreateConfigurationRequest, CreateDatasetRequest, EventType
"""

from enum import Enum


class EventType(str, Enum):
    """Event types for tracing decorators.

    Usage:
        from honeyhive import trace
        from honeyhive.models import EventType

        @trace(event_type=EventType.tool)
        def my_function():
            pass
    """

    model = "model"
    tool = "tool"
    chain = "chain"
    session = "session"
    generic = "generic"


# Re-export all generated Pydantic models
from honeyhive._generated.models import (
    AddDatapointsResponse,
    AddDatapointsToDatasetRequest,
    BatchCreateDatapointsRequest,
    BatchCreateDatapointsResponse,
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
    DeleteDatapointParams,
    DeleteDatapointResponse,
    DeleteDatasetQuery,
    DeleteDatasetResponse,
    DeleteEventParams,
    DeleteEventResponse,
    DeleteExperimentRunParams,
    DeleteExperimentRunResponse,
    DeleteMetricQuery,
    DeleteMetricResponse,
    DeleteSessionResponse,
    DeleteToolQuery,
    DeleteToolResponse,
    Event,
    GetConfigurationsQuery,
    GetConfigurationsResponse,
    GetDatapointParams,
    GetDatapointResponse,
    GetDatapointsQuery,
    GetDatapointsResponse,
    GetDatasetsQuery,
    GetDatasetsResponse,
    GetEventsBySessionIdParams,
    GetEventsBySessionIdResponse,
    GetEventsChartQuery,
    GetEventsChartResponse,
    GetEventsQuery,
    GetEventsResponse,
    GetExperimentRunCompareEventsQuery,
    GetExperimentRunCompareParams,
    GetExperimentRunCompareQuery,
    GetExperimentRunMetricsQuery,
    GetExperimentRunParams,
    GetExperimentRunResponse,
    GetExperimentRunResultQuery,
    GetExperimentRunsQuery,
    GetExperimentRunsResponse,
    GetExperimentRunsSchemaQuery,
    GetExperimentRunsSchemaResponse,
    GetMetricsQuery,
    GetMetricsResponse,
    GetSessionResponse,
    GetToolsResponse,
    PostEventRequest,
    PostEventResponse,
    PostExperimentRunRequest,
    PostExperimentRunResponse,
    PostSessionRequest,
    PostSessionStartResponse,
    PutExperimentRunRequest,
    PutExperimentRunResponse,
    RemoveDatapointFromDatasetParams,
    RemoveDatapointResponse,
    RunMetricRequest,
    RunMetricResponse,
    TODOSchema,
    UpdateConfigurationRequest,
    UpdateConfigurationResponse,
    UpdateDatapointParams,
    UpdateDatapointRequest,
    UpdateDatapointResponse,
    UpdateDatasetRequest,
    UpdateDatasetResponse,
    UpdateMetricRequest,
    UpdateMetricResponse,
    UpdateToolRequest,
    UpdateToolResponse,
)

__all__ = [
    # Configuration models
    "CreateConfigurationRequest",
    "CreateConfigurationResponse",
    "DeleteConfigurationResponse",
    "GetConfigurationsQuery",
    "GetConfigurationsResponse",
    "UpdateConfigurationRequest",
    "UpdateConfigurationResponse",
    # Datapoint models
    "BatchCreateDatapointsRequest",
    "BatchCreateDatapointsResponse",
    "CreateDatapointRequest",
    "CreateDatapointResponse",
    "DeleteDatapointParams",
    "DeleteDatapointResponse",
    "GetDatapointParams",
    "GetDatapointResponse",
    "GetDatapointsQuery",
    "GetDatapointsResponse",
    "UpdateDatapointParams",
    "UpdateDatapointRequest",
    "UpdateDatapointResponse",
    # Dataset models
    "AddDatapointsResponse",
    "AddDatapointsToDatasetRequest",
    "CreateDatasetRequest",
    "CreateDatasetResponse",
    "DeleteDatasetQuery",
    "DeleteDatasetResponse",
    "GetDatasetsQuery",
    "GetDatasetsResponse",
    "RemoveDatapointFromDatasetParams",
    "RemoveDatapointResponse",
    "UpdateDatasetRequest",
    "UpdateDatasetResponse",
    # Event models
    "DeleteEventParams",
    "DeleteEventResponse",
    "Event",
    "GetEventsBySessionIdParams",
    "GetEventsBySessionIdResponse",
    "GetEventsChartQuery",
    "GetEventsChartResponse",
    "GetEventsQuery",
    "GetEventsResponse",
    "PostEventRequest",
    "PostEventResponse",
    # Experiment models
    "DeleteExperimentRunParams",
    "DeleteExperimentRunResponse",
    "GetExperimentRunCompareEventsQuery",
    "GetExperimentRunCompareParams",
    "GetExperimentRunCompareQuery",
    "GetExperimentRunMetricsQuery",
    "GetExperimentRunParams",
    "GetExperimentRunResponse",
    "GetExperimentRunResultQuery",
    "GetExperimentRunsQuery",
    "GetExperimentRunsResponse",
    "GetExperimentRunsSchemaQuery",
    "GetExperimentRunsSchemaResponse",
    "PostExperimentRunRequest",
    "PostExperimentRunResponse",
    "PutExperimentRunRequest",
    "PutExperimentRunResponse",
    # Metric models
    "CreateMetricRequest",
    "CreateMetricResponse",
    "DeleteMetricQuery",
    "DeleteMetricResponse",
    "GetMetricsQuery",
    "GetMetricsResponse",
    "RunMetricRequest",
    "RunMetricResponse",
    "UpdateMetricRequest",
    "UpdateMetricResponse",
    # Session models
    "DeleteSessionResponse",
    "GetSessionResponse",
    "PostSessionRequest",
    "PostSessionStartResponse",
    # Tool models
    "CreateToolRequest",
    "CreateToolResponse",
    "DeleteToolQuery",
    "DeleteToolResponse",
    "GetToolsResponse",
    "UpdateToolRequest",
    "UpdateToolResponse",
    # Other
    "TODOSchema",
    # Enums
    "EventType",
]
