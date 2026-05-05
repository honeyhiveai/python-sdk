"""Canonical re-export hub for generated Pydantic models.

This is the ONLY non-generated module that imports from
``honeyhive._generated.models``. Everything else (client.py, tests, the public
``honeyhive.models`` package) imports from here so we have a single seam
between auto-generated code and the rest of the SDK.

When the canonical spec drifts from what we want to expose publicly, add the
override here as a subclass or alias of the generated model — never modify
``_generated/`` (it gets clobbered on regeneration).
"""

from honeyhive._generated.models import (
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
    GetEventsSchemaResponse,
    GetExperimentRunMetricsQuery,
    GetExperimentRunParams,
    GetExperimentRunResponse,
    GetExperimentRunResultQuery,
    GetExperimentRunsQuery,
    GetExperimentRunsResponse,
    GetMetricsQuery,
    GetMetricsResponse,
    LegacyDeleteDatasetQuery,
    LegacyEvent,
    LegacyGetEventsSchemaQuery,
    LegacyGetExperimentRunCompareEventsQuery,
    LegacyGetExperimentRunCompareParams,
    LegacyGetExperimentRunCompareQuery,
    LegacyPostEventBatchRequest,
    LegacyPostEventRequest,
    LegacyRemoveDatapointFromDatasetParams,
    LegacyUpdateDatasetRequest,
    LegacyUpdateEventRequest,
    LegacyUpdateMetricRequest,
    MetricItem,
    Pagination,
    PostEventBatchRequest,
    PostEventBatchResponse,
    PostEventResponse,
    PostExperimentRunRequest,
    PostExperimentRunResponse,
    PostSessionRequest,
    PostSessionStartResponse,
    PutExperimentRunRequest,
    PutExperimentRunResponse,
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
    UpdateDatasetResponse,
    UpdateMetricResponse,
)


# Public name for dataset update requests. The canonical spec renamed this
# to the new PUT /datasets/{dataset_id} shape (no dataset_id in the body),
# but the Python SDK still calls the legacy PUT /datasets endpoint to avoid
# breaking customers.
class UpdateDatasetRequest(LegacyUpdateDatasetRequest):
    pass


# Public name for metric update requests. The canonical spec renamed this
# to the new PUT /metrics/{metric_id} shape (no id in the body), but the
# Python SDK still calls the legacy PUT /metrics endpoint to avoid breaking
# customers who pass `id` in the request body.
class UpdateMetricRequest(LegacyUpdateMetricRequest):
    pass


# Public name kept pointing at the legacy events-schema query model. The
# canonical spec forked GET /events/schema into GET /v1/runs/{run_id}/schema
# and GET /v1/runs/schema (HHAI-4990); the generated GetRunSchemaQuery /
# GetRunsSchemaQuery models target those new routes and use `.strict()`,
# but the Python SDK still calls the legacy /v1/events/schema endpoint, so
# existing customer imports keep resolving to a model that mirrors the wire
# shape we actually send (dateRange + evaluation_id, non-strict).
class GetEventsSchemaQuery(LegacyGetEventsSchemaQuery):
    pass


# Back-compat aliases preserved from the earlier GET /runs/schema → GET /events/schema
# rename (#3440); kept importable here so customer code that still uses the
# old names continues to resolve.
GetExperimentRunsSchemaQuery = GetEventsSchemaQuery
GetExperimentRunsSchemaResponse = GetEventsSchemaResponse


# Public name preserved for backwards compatibility — was the query schema
# for the legacy DELETE /datasets endpoint, retained here so existing imports
# continue to resolve after the schema fork.
class DeleteDatasetQuery(LegacyDeleteDatasetQuery):
    pass


# Public name kept pointing at the legacy params schema. The new
# RemoveDatapointFromDatasetParams in the generated module is `.strict()`,
# but on the Python side both shapes are field-identical so existing
# customer imports keep working unchanged.
class RemoveDatapointFromDatasetParams(LegacyRemoveDatapointFromDatasetParams):
    pass


# Public names kept pointing at the legacy compare-with schemas. The new
# GetExperimentRunCompare* generated models target /v1/runs/{new_run_id}/compare/{old_run_id}
# and add `.strict()`. The Python SDK still calls the legacy compare-with
# endpoint (compare_runs / compare_runs_async) so existing customer imports
# keep resolving to a model that mirrors the wire shape we actually send.
class GetExperimentRunCompareParams(LegacyGetExperimentRunCompareParams):
    pass


class GetExperimentRunCompareQuery(LegacyGetExperimentRunCompareQuery):
    pass


# Public name kept pointing at the legacy compare/events query schema. The new
# GetExperimentRunCompareEventsQuery generated model targets
# /v1/runs/{new_run_id}/compare/{old_run_id}/events (no run_ids, `.strict()`),
# but the Python SDK still calls the legacy /v1/runs/compare/events endpoint
# so existing customer imports keep resolving to a model that mirrors the
# wire shape we actually send (run_id_1 / run_id_2 in the query string).
class GetExperimentRunCompareEventsQuery(LegacyGetExperimentRunCompareEventsQuery):
    pass


# Public name kept pointing at the legacy event-create schema. The new
# generated PostEventRequest targets POST /v1/events with a bare event-object
# body and drops the deprecated `project` field. The Python SDK still calls
# the legacy POST /events endpoint (events.create / events.create_async) so
# existing customer code that constructs PostEventRequest(event={...}) keeps
# resolving to the wrapped wire shape we send.
class PostEventRequest(LegacyPostEventRequest):
    pass


# Public name kept pointing at the legacy event-batch schema. The new
# generated PostEventBatchRequest (in _generated/models/) targets
# POST /v1/events/batch with a body that, on the Zod / TypeScript-SDK side,
# is `.strict()` and drops the deprecated `is_single_session` and `session`
# aliases at the top level and the deprecated `project` field per event. The
# strictness is a TS-SDK-boundary contract; this Pydantic alias inherits
# `model_config["extra"] = "allow"` from LegacyPostEventBatchRequest and so
# does NOT reject `is_single_session=True` or `session={...}` at construction
# time. That's by design — the public Python alias is a back-compat shim, not
# a v1-strict enforcer. The Python SDK still calls the legacy
# POST /events/batch endpoint (events.create_batch / events.create_batch_async)
# so existing customer code that constructs
# PostEventBatchRequest(events=[...], is_single_session=True, session={...})
# keeps resolving to the legacy wire shape we send.
class PostEventBatchRequest(LegacyPostEventBatchRequest):
    pass


# Public name kept pointing at the legacy event-update schema. The new
# generated UpdateEventRequest targets PUT /v1/events/{event_id} (event_id in
# the URL path, not the body). The Python SDK still calls the legacy
# PUT /events endpoint (events.update / events.update_async) so existing
# customer code that constructs UpdateEventRequest(event_id=..., metadata=...)
# keeps resolving to the wire shape we actually send.
class UpdateEventRequest(LegacyUpdateEventRequest):
    pass


# Note: models prefixed with Legacy are intentionally not re-exported — they are
# implementation details of the aliases above
__all__ = [
    "AddDatapointsResponse",
    "AddDatapointsToDatasetRequest",
    "BatchCreateDatapointsRequest",
    "BatchCreateDatapointsResponse",
    "ConfigurationItem",
    "CreateConfigurationRequest",
    "CreateConfigurationResponse",
    "CreateDatapointRequest",
    "CreateDatapointResponse",
    "CreateDatasetRequest",
    "CreateDatasetResponse",
    "CreateMetricRequest",
    "CreateMetricResponse",
    "DatapointMapping",
    "DeleteConfigurationResponse",
    "DeleteDatapointParams",
    "DeleteDatapointResponse",
    "DeleteDatasetParams",
    "DeleteDatasetQuery",
    "DeleteDatasetResponse",
    "DeleteExperimentRunParams",
    "DeleteExperimentRunResponse",
    "DeleteMetricResponse",
    "Event",
    "GetConfigurationsQuery",
    "GetConfigurationsResponse",
    "GetDatapointParams",
    "GetDatapointResponse",
    "GetDatapointsQuery",
    "GetDatapointsResponse",
    "GetDatasetsResponse",
    "GetEventsQuery",
    "GetEventsResponse",
    "GetEventsSchemaQuery",
    "GetEventsSchemaResponse",
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
    "GetMetricsQuery",
    "GetMetricsResponse",
    "LegacyEvent",
    "MetricItem",
    "Pagination",
    "PostEventBatchRequest",
    "PostEventBatchResponse",
    "PostEventRequest",
    "PostEventResponse",
    "PostExperimentRunRequest",
    "PostExperimentRunResponse",
    "PostSessionRequest",
    "PostSessionStartResponse",
    "PutExperimentRunRequest",
    "PutExperimentRunResponse",
    "RemoveDatapointFromDatasetParams",
    "RemoveDatapointResponse",
    "RunMetricRequest",
    "RunMetricResponse",
    "StartSessionRequest",
    "TODOSchema",
    "UpdateConfigurationRequest",
    "UpdateConfigurationResponse",
    "UpdateDatapointParams",
    "UpdateDatapointRequest",
    "UpdateDatapointResponse",
    "UpdateDatasetRequest",
    "UpdateDatasetResponse",
    "UpdateEventRequest",
    "UpdateMetricRequest",
    "UpdateMetricResponse",
]
