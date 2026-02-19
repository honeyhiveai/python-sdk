"""HoneyHive Models - Re-exported from auto-generated Pydantic models.

Usage:
    from honeyhive.models import CreateConfigurationRequest, CreateDatasetRequest, EventType
"""

from enum import Enum
from typing import Any, Dict


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


# Re-export all 55 generated Pydantic models
from honeyhive._generated.models import (
    AddDatapointsRequest,
    AddDatapointsResponse,
    Configuration,
    CreateDatapointRequest,
    CreateDatapointResponse,
    CreateDatasetRequest,
    CreateDatasetResponse,
    CreateEventBatchRequest,
    CreateEventBatchResponse,
    CreateEventRequest,
    CreateEventRequestBody,
    CreateEventResponse,
    CreateModelEvent,
    CreateModelEventBatchRequest,
    CreateModelEventBatchResponse,
    CreateModelEventRequestBody,
    CreateProjectRequest,
    CreateRunRequest,
    CreateRunResponse,
    CreateToolRequest,
    CreateToolResponse,
    Datapoint,
    Dataset,
    DatasetUpdate,
    DeleteDatapointResponse,
    DeleteRunResponse,
    EvaluationRun,
    Event,
    EventFilter,
    ExperimentComparisonResponse,
    ExperimentResultResponse,
    GetDatapointResponse,
    GetDatapointsResponse,
    GetDatasetsResponse,
    GetEventsRequest,
    GetEventsResponse,
    GetRunResponse,
    GetRunsResponse,
    Metric,
    MetricEdit,
    PostConfigurationRequest,
    Project,
    PutConfigurationRequest,
    SessionPropertiesBatch,
    SessionStartRequest,
    StartSessionRequestBody,
    StartSessionResponse,
    Tool,
    UpdateDatapointRequest,
    UpdateEventRequest,
    UpdateProjectRequest,
    UpdateRunRequest,
    UpdateRunResponse,
    UpdateToolRequest,
)

# Forwards-compatible aliases for legacy model names.
CreateConfigurationRequest = PostConfigurationRequest
UpdateConfigurationRequest = PutConfigurationRequest
UpdateDatasetRequest = DatasetUpdate
PostExperimentRunRequest = CreateRunRequest
PutExperimentRunRequest = UpdateRunRequest
PostEventRequest = CreateEventRequest
CreateMetricRequest = Metric
UpdateMetricRequest = MetricEdit
AddDatapointsToDatasetRequest = AddDatapointsRequest

__all__ = [
    # Generated models
    "AddDatapointsResponse",
    "Configuration",
    "CreateDatapointRequest",
    "CreateDatapointResponse",
    "CreateDatasetRequest",
    "CreateDatasetResponse",
    "CreateEventBatchRequest",
    "CreateEventBatchResponse",
    "CreateEventRequestBody",
    "CreateEventResponse",
    "CreateModelEvent",
    "CreateModelEventBatchRequest",
    "CreateModelEventBatchResponse",
    "CreateModelEventRequestBody",
    "CreateProjectRequest",
    "CreateRunResponse",
    "CreateToolRequest",
    "CreateToolResponse",
    "Datapoint",
    "Dataset",
    "DeleteDatapointResponse",
    "DeleteRunResponse",
    "EvaluationRun",
    "Event",
    "EventFilter",
    "ExperimentComparisonResponse",
    "ExperimentResultResponse",
    "GetDatapointResponse",
    "GetDatapointsResponse",
    "GetDatasetsResponse",
    "GetEventsRequest",
    "GetEventsResponse",
    "GetRunResponse",
    "GetRunsResponse",
    "Project",
    "SessionPropertiesBatch",
    "SessionStartRequest",
    "StartSessionRequestBody",
    "StartSessionResponse",
    "Tool",
    "UpdateDatapointRequest",
    "UpdateEventRequest",
    "UpdateProjectRequest",
    "UpdateRunResponse",
    "UpdateToolRequest",
    # Forwards-compatible aliases
    "CreateConfigurationRequest",
    "UpdateConfigurationRequest",
    "UpdateDatasetRequest",
    "PostExperimentRunRequest",
    "PutExperimentRunRequest",
    "PostEventRequest",
    "CreateMetricRequest",
    "UpdateMetricRequest",
    "AddDatapointsToDatasetRequest",
    # Custom types
    "EventType",
]
