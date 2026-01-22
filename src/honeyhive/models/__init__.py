"""HoneyHive Models - Re-exported from auto-generated Pydantic models.

Usage:
    from honeyhive.models import CreateConfigurationRequest, CreateDatasetRequest, EventType
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Event types for tracing decorators.

    Example::

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


class FilterOperator(str, Enum):
    """Filter operators for event queries.

    Example::

        from honeyhive.models import EventFilter, FilterOperator

        filter = EventFilter(
            field="event_type",
            operator=FilterOperator.IS,
            value="model",
            type="string"
        )
    """

    IS = "is"
    IS_NOT = "is not"
    CONTAINS = "contains"
    NOT_CONTAINS = "not contains"
    GREATER_THAN = "greater than"


class FilterFieldType(str, Enum):
    """Field types for event filters."""

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ID = "id"


class EventFilter(BaseModel):
    """Filter for querying events.

    Used with the events.export() method to filter events by field values.

    Example::

        from honeyhive.models import EventFilter, FilterOperator

        # Filter by session_id
        filter = EventFilter(
            field="session_id",
            operator=FilterOperator.IS,
            value="abc-123",
            type="string"
        )

        # Filter by event type
        filter = EventFilter(
            field="event_type",
            operator="is",  # Can also use string
            value="model",
            type="string"
        )

        # Filter by metadata field
        filter = EventFilter(
            field="metadata.cost",
            operator="greater than",
            value="0.01",
            type="number"
        )
    """

    model_config = {"populate_by_name": True}

    field: str = Field(
        description="The field name to filter by (e.g., 'session_id', 'event_type', 'metadata.cost')"
    )
    operator: str = Field(
        description="Filter operator: 'is', 'is not', 'contains', 'not contains', 'greater than'"
    )
    value: str = Field(description="The value to filter for")
    type: str = Field(
        default="string",
        description="Data type: 'string', 'number', 'boolean', 'id'",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for API request."""
        return {
            "field": self.field,
            "operator": self.operator if isinstance(self.operator, str) else self.operator.value,
            "value": self.value,
            "type": self.type if isinstance(self.type, str) else self.type.value,
        }


class EventExportRequest(BaseModel):
    """Request model for exporting events.

    Example::

        from honeyhive.models import EventExportRequest, EventFilter

        request = EventExportRequest(
            project="my-project",
            filters=[
                EventFilter(field="session_id", operator="is", value="abc-123", type="string")
            ],
            limit=100,
        )
    """

    model_config = {"populate_by_name": True}

    project: str = Field(description="Project name associated with the events")
    filters: List[EventFilter] = Field(
        default_factory=list, description="List of filters to apply"
    )
    date_range: Optional[Dict[str, str]] = Field(
        default=None,
        alias="dateRange",
        description="Date range filter with '$gte' and '$lte' ISO timestamp strings",
    )
    projections: Optional[List[str]] = Field(
        default=None, description="Fields to include in the response"
    )
    limit: Optional[int] = Field(
        default=1000, description="Limit number of results (default 1000, max 7500)"
    )
    page: Optional[int] = Field(default=1, description="Page number (default 1)")


class EventExportResponse(BaseModel):
    """Response model for exported events."""

    model_config = {"populate_by_name": True}

    events: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of exported events"
    )
    total_events: int = Field(
        default=0,
        alias="totalEvents",
        description="Total number of events matching the filter",
    )


# Re-export all generated Pydantic models
from honeyhive._generated.models import (
    AddDatapointsResponse,
    AddDatapointsToDatasetRequest,
    BatchCreateDatapointsRequest,
    BatchCreateDatapointsResponse,
    CreateConfigurationRequest,
    DatapointMapping,
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
    "DatapointMapping",
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
    "FilterOperator",
    "FilterFieldType",
    # Event export models
    "EventFilter",
    "EventExportRequest",
    "EventExportResponse",
]
