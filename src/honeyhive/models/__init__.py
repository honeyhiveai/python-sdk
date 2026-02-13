"""HoneyHive Models - Re-exported from auto-generated Pydantic models.

Usage:
    from honeyhive.models import PostConfigurationRequest, CreateDatasetRequest, EventType
"""

from typing import Any, Dict

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


# Re-export all 34 generated Pydantic models
from honeyhive._generated.models import (
    Configuration,
    CreateDatapointRequest,
    CreateDatasetRequest,
    CreateEventRequest,
    CreateModelEvent,
    CreateProjectRequest,
    CreateRunRequest,
    CreateRunResponse,
    CreateToolRequest,
    Datapoint,
    Dataset,
    DatasetUpdate,
    DeleteRunResponse,
    EvaluationRun,
    Event,
    EventFilter,
    ExperimentComparisonResponse,
    ExperimentResultResponse,
    GetRunResponse,
    GetRunsResponse,
    Metric,
    MetricEdit,
    PostConfigurationRequest,
    Project,
    PutConfigurationRequest,
    SessionPropertiesBatch,
    SessionStartRequest,
    Tool,
    UpdateDatapointRequest,
    UpdateProjectRequest,
    UpdateRunRequest,
    UpdateRunResponse,
    UpdateToolRequest,
    UUIDType,
)

# Backwards-compatible aliases: FED model names → NWD model names
# These allow existing code that uses FED naming to keep working.
CreateConfigurationRequest = PostConfigurationRequest
UpdateConfigurationRequest = PutConfigurationRequest
UpdateDatasetRequest = DatasetUpdate
PostExperimentRunRequest = CreateRunRequest
PutExperimentRunRequest = UpdateRunRequest
PostEventRequest = CreateEventRequest

__all__ = [
    # Generated models (NWD names)
    "Configuration",
    "CreateDatapointRequest",
    "CreateDatasetRequest",
    "CreateEventRequest",
    "CreateModelEvent",
    "CreateProjectRequest",
    "CreateRunRequest",
    "CreateRunResponse",
    "CreateToolRequest",
    "Datapoint",
    "Dataset",
    "DatasetUpdate",
    "DeleteRunResponse",
    "EvaluationRun",
    "Event",
    "EventFilter",
    "ExperimentComparisonResponse",
    "ExperimentResultResponse",
    "GetRunResponse",
    "GetRunsResponse",
    "Metric",
    "MetricEdit",
    "PostConfigurationRequest",
    "Project",
    "PutConfigurationRequest",
    "SessionPropertiesBatch",
    "SessionStartRequest",
    "Tool",
    "UpdateDatapointRequest",
    "UpdateProjectRequest",
    "UpdateRunRequest",
    "UpdateRunResponse",
    "UpdateToolRequest",
    "UUIDType",
    # Backwards-compatible aliases (FED names)
    "CreateConfigurationRequest",
    "UpdateConfigurationRequest",
    "UpdateDatasetRequest",
    "PostExperimentRunRequest",
    "PutExperimentRunRequest",
    "PostEventRequest",
    # Custom types
    "EventType",
]
