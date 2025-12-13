# V0 → V1 Schema Mapping Analysis

## Status Legend
- ✓ = Already matching (no change needed)
- ← = Rename needed (FROM → TO)
- ⚠ = Uses TODOSchema placeholder (needs Zod schema implementation)
- ✗ = Utility/variant type (may not need explicit schema)

---

## Already Matching (no change needed)
```
CreateDatapointRequest        ✓
CreateDatasetRequest          ✓
CreateToolRequest             ✓
Datapoint                     ✓
Datapoint1                    ✓
EventType                     ✓
Metric                        ✓
Parameters                    ✓
Parameters1                   ✓
Parameters2                   ✓
SelectedFunction              ✓
Threshold                     ✓
UpdateDatapointRequest        ✓
UpdateToolRequest             ✓
```

---

## Need Renaming in Zod Schema Names

| v0 Name (expected)        | v1 Current Name                | Action                    |
|---------------------------|--------------------------------|---------------------------|
| Configuration             | GetConfigurationsResponseItem  | Rename → Configuration    |
| PostConfigurationRequest  | CreateConfigurationRequest     | Rename → PostConfigurationRequest |
| PutConfigurationRequest   | UpdateConfigurationRequest     | Rename → PutConfigurationRequest |
| Tool                      | GetToolsResponseItem           | Rename → Tool             |
| Event                     | EventNode                      | Rename → Event            |
| EvaluationRun             | GetExperimentRunResponse       | Rename → EvaluationRun    |
| GetRunResponse            | GetExperimentRunResponse       | (same as above)           |
| GetRunsResponse           | GetExperimentRunsResponse      | Rename → GetRunsResponse  |
| CreateRunRequest          | PostExperimentRunRequest       | Rename → CreateRunRequest |
| CreateRunResponse         | PostExperimentRunResponse      | Rename → CreateRunResponse|
| UpdateRunRequest          | PutExperimentRunRequest        | Rename → UpdateRunRequest |
| UpdateRunResponse         | PutExperimentRunResponse       | Rename → UpdateRunResponse|
| DeleteRunResponse         | DeleteExperimentRunResponse    | Rename → DeleteRunResponse|
| DatasetUpdate             | UpdateDatasetRequest           | Rename → DatasetUpdate    |
| MetricEdit                | UpdateMetricRequest            | Rename → MetricEdit       |
| Metrics                   | GetMetricsResponse             | Rename → Metrics          |
| Datapoints                | GetDatapointsResponse          | Rename → Datapoints       |

---

## Uses TODOSchema Placeholder (needs Zod implementation)

These endpoints reference `TODOSchema` in the v1 OpenAPI spec, meaning the actual
schema hasn't been implemented in `@hive-kube/core-ts` Zod definitions yet.

| v0 Name                     | v1 Endpoint                          | Notes                              |
|-----------------------------|--------------------------------------|------------------------------------|
| SessionStartRequest         | POST /session/start                  | `session` field uses TODOSchema    |
| SessionPropertiesBatch      | POST /events/batch                   | `session_properties` uses TODOSchema |
| CreateEventRequest          | POST /events                         | `event` field uses TODOSchema      |
| CreateModelEvent            | POST /events/model                   | `model_event` field uses TODOSchema|
| Project                     | GET /projects response               | Array items use TODOSchema         |
| CreateProjectRequest        | POST /projects request               | Uses TODOSchema                    |
| UpdateProjectRequest        | PUT /projects request                | Uses TODOSchema                    |
| ExperimentResultResponse    | GET /runs/{id}/result response       | Uses TODOSchema                    |
| ExperimentComparisonResponse| GET /runs/{id1}/compare-with/{id2}   | Uses TODOSchema                    |

**TODOSchema definition (from spec):**
```yaml
TODOSchema:
  type: object
  properties:
    message:
      type: string
      description: Placeholder - Zod schema not yet implemented
  required:
    - message
  description: 'TODO: This is a placeholder schema. Proper Zod schemas need to
    be created in @hive-kube/core-ts for: Sessions, Events, Projects, and
    Experiment comparison/result endpoints.'
```

---

## Utility/Variant Types (may not need explicit schema)

| v0 Name      | Analysis                                                    |
|--------------|-------------------------------------------------------------|
| UUIDType     | Utility wrapper type - v1 may use raw `string` format: uuid |
| Detail       | Generic detail type - may be inlined or removed             |
| Metric1      | Variant type - check if consolidated into single Metric     |
| Metric2      | Variant type - check if consolidated into single Metric     |
| EventDetail  | May be inlined in EventNode or removed                      |
| EventFilter  | Query param type - may be inlined in endpoint params        |
| Dataset      | No standalone schema, only Create/Update/Get variants exist |
| NewRun       | Possibly used in comparison responses - check if needed     |
| OldRun       | Possibly used in comparison responses - check if needed     |

---

## Summary

### Immediate Actions (for Zod→OpenAPI script)
1. **Rename 16 schemas** to match v0 naming conventions
2. **Implement TODOSchema replacements** for 9 endpoints (Sessions, Events, Projects, Experiment results)

### Lower Priority
3. Decide on utility types (UUIDType, Detail, Metric1/2, etc.)
4. Verify EventFilter/EventDetail are covered by EventNode or query params

### Questions to Resolve
- Should `UUIDType` be a dedicated schema or just `string` with `format: uuid`?
- Are `Metric1`/`Metric2` variants still needed, or is single `Metric` sufficient?
- Are `NewRun`/`OldRun` used in comparison responses?
