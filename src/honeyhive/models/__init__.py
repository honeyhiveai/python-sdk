"""HoneyHive Models - Re-exported from auto-generated Pydantic models.

Usage:
    from honeyhive.models import CreateConfigurationRequest, CreateDatasetRequest, EventType
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# LegacyEvent is the typed Pydantic model for events returned by the v1 events
# export endpoint. It has `extra="allow"` so any backend fields not yet in the
# OpenAPI spec still flow through unchanged, and exposes every field tests and
# customers access (event_id, event_name, metadata, session_id, project_id,
# inputs, outputs, source, event_type, start_time, end_time, duration, etc.).
from honeyhive.models.models import LegacyEvent


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
    """Field types for event filters.

    The server only accepts ``string``, ``number``, ``boolean``, ``datetime``;
    use ``STRING`` for UUID-style fields like ``session_id`` / ``event_id``.
    """

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    # DEPRECATED: never accepted by the backend (the server enum is
    # string|number|boolean|datetime). Kept as an alias so existing imports
    # don't AttributeError, but the wire value "id" is rejected with HTTP 400.
    # Use STRING for UUID/ID fields. Will be removed in a future SDK major.
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
        description="Data type: 'string', 'number', 'boolean', 'datetime'",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for API request."""
        return {
            "field": self.field,
            "operator": (
                self.operator if isinstance(self.operator, str) else self.operator.value
            ),
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
    """Response model for exported events.

    The ``events`` list returns typed :class:`LegacyEvent` models. Pydantic
    coerces raw dicts returned by the backend into ``LegacyEvent`` at
    construction time; ``extra="allow"`` on ``LegacyEvent`` preserves any
    backend fields not yet declared in the OpenAPI spec.

    Migration from dict-based access::

        response.events[0]["event_id"]       # old
        response.events[0].event_id          # new
        response.events[0].model_dump()      # escape hatch returning dict
    """

    model_config = {"populate_by_name": True}

    events: List[LegacyEvent] = Field(
        default_factory=list, description="List of exported events"
    )
    total_events: int = Field(
        default=0,
        alias="totalEvents",
        description="Total number of events matching the filter",
    )


# Re-export all generated Pydantic models
from honeyhive.models.models import (
    AddDatapointsResponse,
    AddDatapointsToDatasetRequest,
    BatchCreateDatapointsRequest,
    BatchCreateDatapointsResponse,
    ConfigurationItem,
    CreateConfigurationRequest,
    CreateConfigurationResponse,
    CreateDatapointRequest,
    CreateDatapointResponse,
    CreateDatasetRequest,
    CreateDatasetResponse,
    CreateMetricRequest,
    CreateMetricResponse,
    DatapointMapping,
    DeleteConfigurationResponse,
    DeleteDatapointParams,
    DeleteDatapointResponse,
    DeleteDatasetParams,
    DeleteDatasetQuery,
    DeleteDatasetResponse,
    DeleteExperimentRunParams,
    DeleteExperimentRunResponse,
    DeleteMetricResponse,
    Event,
    GetConfigurationsQuery,
    GetConfigurationsResponse,
    GetDatapointParams,
    GetDatapointResponse,
    GetDatapointsQuery,
    GetDatapointsResponse,
    GetDatasetsResponse,
    GetEventsQuery,
    GetEventsResponse,
    GetEventsSchemaQuery,
    GetEventsSchemaResponse,
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
    MetricItem,
    Pagination,
    PostEventBatchRequest,
    PostEventBatchResponse,
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
    StartSessionRequest,
    TODOSchema,
    UpdateConfigurationRequest,
    UpdateConfigurationResponse,
    UpdateDatapointParams,
    UpdateDatapointRequest,
    UpdateDatapointResponse,
    UpdateDatasetRequest,
    UpdateDatasetResponse,
    UpdateEventRequest,
    UpdateMetricRequest,
    UpdateMetricResponse,
)

__all__ = [
    # Configuration models
    "ConfigurationItem",
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
    "DeleteDatasetParams",
    "DeleteDatasetQuery",
    "DeleteDatasetResponse",
    "GetDatasetsResponse",
    "RemoveDatapointFromDatasetParams",
    "RemoveDatapointResponse",
    "UpdateDatasetRequest",
    "UpdateDatasetResponse",
    # Event models
    "Event",
    "GetEventsQuery",
    "GetEventsResponse",
    "LegacyEvent",
    "PostEventBatchRequest",
    "PostEventBatchResponse",
    "PostEventRequest",
    "PostEventResponse",
    "UpdateEventRequest",
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
    "GetEventsSchemaQuery",
    "GetEventsSchemaResponse",
    "PostExperimentRunRequest",
    "PostExperimentRunResponse",
    "PutExperimentRunRequest",
    "PutExperimentRunResponse",
    # Metric models
    "CreateMetricRequest",
    "CreateMetricResponse",
    "DeleteMetricResponse",
    "GetMetricsQuery",
    "GetMetricsResponse",
    "MetricItem",
    "RunMetricRequest",
    "RunMetricResponse",
    "UpdateMetricRequest",
    "UpdateMetricResponse",
    # Session models
    "PostSessionRequest",
    "PostSessionStartResponse",
    "StartSessionRequest",
    # Other
    "Pagination",
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
