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


# Re-export all generated Pydantic models
from honeyhive._generated.models import (
    AddDatapointsResponse,
    AddDatapointsToDatasetRequest,
    Configuration,
    CreateConfigurationRequest,
    CreateDatapointRequest,
    CreateDatapointResponse,
    CreateDatasetRequest,
    CreateDatasetResponse,
    CreateEventBatchRequest,
    CreateEventBatchResponse,
    CreateEventResponse,
    CreateModelEvent,
    CreateModelEventBatchRequest,
    CreateModelEventBatchResponse,
    CreateModelEventRequestBody,
    CreateProjectRequest,
    CreateToolRequest,
    CreateToolResponse,
    Datapoint,
    Dataset,
    DeleteDatapointResponse,
    DeleteExperimentRunResponse,
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
    GetExperimentRunResponse,
    GetRunsResponse,
    Metric,
    PostEventRequest,
    PostEventRequestBody,
    PostExperimentRunRequest,
    PostExperimentRunResponse,
    Project,
    PutExperimentRunRequest,
    PutExperimentRunResponse,
    SessionPropertiesBatch,
    SessionStartRequest,
    StartSessionRequestBody,
    StartSessionResponse,
    Tool,
    UpdateConfigurationRequest,
    UpdateDatapointRequest,
    UpdateDatasetRequest,
    UpdateEventRequest,
    UpdateMetricRequest,
    UpdateProjectRequest,
    UpdateToolRequest,
)

# Forwards-compatible alias: Metric is used as the create request body
CreateMetricRequest = Metric

__all__ = [
    # Generated models
    "AddDatapointsResponse",
    "AddDatapointsToDatasetRequest",
    "Configuration",
    "CreateConfigurationRequest",
    "CreateDatapointRequest",
    "CreateDatapointResponse",
    "CreateDatasetRequest",
    "CreateDatasetResponse",
    "CreateEventBatchRequest",
    "CreateEventBatchResponse",
    "CreateEventResponse",
    "CreateModelEvent",
    "CreateModelEventBatchRequest",
    "CreateModelEventBatchResponse",
    "CreateModelEventRequestBody",
    "CreateProjectRequest",
    "PostEventRequestBody",
    "CreateToolRequest",
    "CreateToolResponse",
    "Datapoint",
    "Dataset",
    "DeleteDatapointResponse",
    "DeleteExperimentRunResponse",
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
    "GetExperimentRunResponse",
    "GetRunsResponse",
    "Metric",
    "PostEventRequest",
    "PostExperimentRunRequest",
    "PostExperimentRunResponse",
    "Project",
    "PutExperimentRunRequest",
    "PutExperimentRunResponse",
    "SessionPropertiesBatch",
    "SessionStartRequest",
    "StartSessionRequestBody",
    "StartSessionResponse",
    "Tool",
    "UpdateConfigurationRequest",
    "UpdateDatapointRequest",
    "UpdateDatasetRequest",
    "UpdateEventRequest",
    "UpdateMetricRequest",
    "UpdateProjectRequest",
    "UpdateToolRequest",
    # Alias
    "CreateMetricRequest",
    # Custom types
    "EventType",
]
