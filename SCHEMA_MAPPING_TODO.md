# V0 Name (expected)          →  V1 Current Name (rename FROM → TO)
# ================================================================

# Already matching (no change needed):
CreateDatapointRequest        ✓  (same)
CreateDatasetRequest          ✓  (same)
CreateToolRequest             ✓  (same)
Datapoint                     ✓  (same)
Datapoint1                    ✓  (same)
EventType                     ✓  (same)
Metric                        ✓  (same)
Parameters                    ✓  (same)
Parameters1                   ✓  (same)
Parameters2                   ✓  (same)
SelectedFunction              ✓  (same)
Threshold                     ✓  (same)
UpdateDatapointRequest        ✓  (same)
UpdateToolRequest             ✓  (same)

# Need renaming in your Zod schema names:
Configuration                 ←  GetConfigurationsResponseItem
PostConfigurationRequest      ←  CreateConfigurationRequest
PutConfigurationRequest       ←  UpdateConfigurationRequest
Tool                          ←  GetToolsResponseItem
Event                         ←  EventNode
EvaluationRun                 ←  GetExperimentRunResponse
GetRunResponse                ←  GetExperimentRunResponse (duplicate?)
GetRunsResponse               ←  GetExperimentRunsResponse
CreateRunRequest              ←  PostExperimentRunRequest
CreateRunResponse             ←  PostExperimentRunResponse
UpdateRunRequest              ←  PutExperimentRunRequest
UpdateRunResponse             ←  PutExperimentRunResponse
DeleteRunResponse             ←  DeleteExperimentRunResponse
DatasetUpdate                 ←  UpdateDatasetRequest
MetricEdit                    ←  UpdateMetricRequest
Metrics                       ←  GetMetricsResponse
Datapoints                    ←  GetDatapointsResponse

# Missing in v1 (need to add schemas or remove from exports):
SessionStartRequest           ✗  not found
SessionPropertiesBatch        ✗  not found
CreateEventRequest            ✗  not found
CreateModelEvent              ✗  not found
EventDetail                   ✗  not found
EventFilter                   ✗  not found
Project                       ✗  not found
CreateProjectRequest          ✗  not found
UpdateProjectRequest          ✗  not found
Dataset                       ✗  not found (only Create/Update/Get)
UUIDType                      ✗  not found
Detail                        ✗  not found
Metric1                       ✗  not found
Metric2                       ✗  not found
ExperimentComparisonResponse  ✗  not found
ExperimentResultResponse      ✗  not found
NewRun                        ✗  not found
OldRun                        ✗  not found
