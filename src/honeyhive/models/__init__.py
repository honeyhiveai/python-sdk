"""HoneyHive Models - Public Facade.

This module re-exports from the underlying model implementation (_v0 or _v1).
Only one implementation will be present in a published package.
"""

try:
    # Prefer v1 if available
    from honeyhive._v1.models import *  # noqa: F401, F403

    __models_version__ = "v1"
except ImportError:
    # Fall back to v0
    from honeyhive._v0.models.generated import (  # noqa: F401
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
        Datapoint1,
        Datapoints,
        Dataset,
        DatasetUpdate,
        DeleteRunResponse,
        Detail,
        EvaluationRun,
        Event,
        EventDetail,
        EventFilter,
        EventType,
        ExperimentComparisonResponse,
        ExperimentResultResponse,
        GetRunResponse,
        GetRunsResponse,
        Metric,
        Metric1,
        Metric2,
        MetricEdit,
        Metrics,
        NewRun,
        OldRun,
        Parameters,
        Parameters1,
        Parameters2,
        PostConfigurationRequest,
        Project,
        PutConfigurationRequest,
        SelectedFunction,
        SessionPropertiesBatch,
        SessionStartRequest,
        Threshold,
        Tool,
        UpdateDatapointRequest,
        UpdateProjectRequest,
        UpdateRunRequest,
        UpdateRunResponse,
        UpdateToolRequest,
        UUIDType,
    )
    from honeyhive._v0.models.tracing import TracingParams  # noqa: F401

    __models_version__ = "v0"

__all__ = [
    # Session models
    "SessionStartRequest",
    "SessionPropertiesBatch",
    # Event models
    "Event",
    "EventType",
    "EventFilter",
    "CreateEventRequest",
    "CreateModelEvent",
    "EventDetail",
    # Metric models
    "Metric",
    "Metric1",
    "Metric2",
    "MetricEdit",
    "Metrics",
    "Threshold",
    # Tool models
    "Tool",
    "CreateToolRequest",
    "UpdateToolRequest",
    # Datapoint models
    "Datapoint",
    "Datapoint1",
    "Datapoints",
    "CreateDatapointRequest",
    "UpdateDatapointRequest",
    # Dataset models
    "Dataset",
    "CreateDatasetRequest",
    "DatasetUpdate",
    # Project models
    "Project",
    "CreateProjectRequest",
    "UpdateProjectRequest",
    # Configuration models
    "Configuration",
    "Parameters",
    "Parameters1",
    "Parameters2",
    "PutConfigurationRequest",
    "PostConfigurationRequest",
    # Experiment/Run models
    "EvaluationRun",
    "CreateRunRequest",
    "UpdateRunRequest",
    "UpdateRunResponse",
    "CreateRunResponse",
    "GetRunsResponse",
    "GetRunResponse",
    "DeleteRunResponse",
    "ExperimentResultResponse",
    "ExperimentComparisonResponse",
    "OldRun",
    "NewRun",
    # Utility models
    "UUIDType",
    "SelectedFunction",
    "Detail",
    # Tracing models
    "TracingParams",
    # Version info
    "__models_version__",
]
