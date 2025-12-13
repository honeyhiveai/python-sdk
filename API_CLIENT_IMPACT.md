# API Client Impact Analysis: v0 → v1 Models

## Summary

| File | Models Imported | v1 Status | Changes Needed |
|------|-----------------|-----------|----------------|
| datapoints.py | 3 | ✅ All exist | None |
| tools.py | 3 | ⚠️ 1 missing | Rename 1 |
| metrics.py | 2 | ⚠️ 1 missing | Rename 1 |
| configurations.py | 3 | ❌ All missing | Rename 3 |
| datasets.py | 3 | ⚠️ 2 missing | Rename 2 |
| session.py | 2 | ❌ All missing | Rename 1, TODOSchema 1 |
| events.py | 3 | ❌ All missing | Rename 1, TODOSchema 2 |
| evaluations.py | 7 | ❌ All missing | Rename 6, remove UUIDType |
| projects.py | 3 | ❌ All missing | TODOSchema 3 |

---

## Detailed Analysis

### ✅ datapoints.py - No Changes Needed
```python
from ..models import CreateDatapointRequest, Datapoint, UpdateDatapointRequest
```
| Import | v1 Status |
|--------|-----------|
| CreateDatapointRequest | ✅ Exists |
| Datapoint | ✅ Exists |
| UpdateDatapointRequest | ✅ Exists |

---

### ⚠️ tools.py - 1 Rename
```python
from ..models import CreateToolRequest, Tool, UpdateToolRequest
```
| Import | v1 Status | Action |
|--------|-----------|--------|
| CreateToolRequest | ✅ Exists | None |
| Tool | ❌ Missing | Rename from `GetToolsResponseItem` |
| UpdateToolRequest | ✅ Exists | None |

---

### ⚠️ metrics.py - 1 Rename
```python
from ..models import Metric, MetricEdit
```
| Import | v1 Status | Action |
|--------|-----------|--------|
| Metric | ✅ Exists | None |
| MetricEdit | ❌ Missing | Rename from `UpdateMetricRequest` |

---

### ❌ configurations.py - 3 Renames
```python
from ..models import Configuration, PostConfigurationRequest, PutConfigurationRequest
```
| Import | v1 Status | Action |
|--------|-----------|--------|
| Configuration | ❌ Missing | Rename from `GetConfigurationsResponseItem` |
| PostConfigurationRequest | ❌ Missing | Rename from `CreateConfigurationRequest` |
| PutConfigurationRequest | ❌ Missing | Rename from `UpdateConfigurationRequest` |

---

### ⚠️ datasets.py - 2 Renames
```python
from ..models import CreateDatasetRequest, Dataset, DatasetUpdate
```
| Import | v1 Status | Action |
|--------|-----------|--------|
| CreateDatasetRequest | ✅ Exists | None |
| Dataset | ❌ Missing | Need to create/extract from response types |
| DatasetUpdate | ❌ Missing | Rename from `UpdateDatasetRequest` |

**Note**: v1 has no standalone `Dataset` schema. Options:
1. Create alias from response type fields
2. Inline the type in datasets.py
3. Add `Dataset` schema to v1 spec

---

### ❌ session.py - 1 Rename, 1 TODOSchema
```python
from ..models import Event, SessionStartRequest
```
| Import | v1 Status | Action |
|--------|-----------|--------|
| Event | ❌ Missing | Rename from `EventNode` |
| SessionStartRequest | ❌ TODOSchema | **Needs Zod implementation** |

---

### ❌ events.py - 1 Rename, 2 TODOSchema
```python
from ..models import CreateEventRequest, Event, EventFilter
```
| Import | v1 Status | Action |
|--------|-----------|--------|
| CreateEventRequest | ❌ TODOSchema | **Needs Zod implementation** |
| Event | ❌ Missing | Rename from `EventNode` |
| EventFilter | ❌ Missing | **Needs Zod implementation** (or inline as query params) |

---

### ❌ evaluations.py - 6 Renames, Remove UUIDType
```python
from ..models import (
    CreateRunRequest,
    CreateRunResponse,
    DeleteRunResponse,
    GetRunResponse,
    GetRunsResponse,
    UpdateRunRequest,
    UpdateRunResponse,
)
from ..models.generated import UUIDType
```
| Import | v1 Status | Action |
|--------|-----------|--------|
| CreateRunRequest | ❌ Missing | Rename from `PostExperimentRunRequest` |
| CreateRunResponse | ❌ Missing | Rename from `PostExperimentRunResponse` |
| DeleteRunResponse | ❌ Missing | Rename from `DeleteExperimentRunResponse` |
| GetRunResponse | ❌ Missing | Rename from `GetExperimentRunResponse` |
| GetRunsResponse | ❌ Missing | Rename from `GetExperimentRunsResponse` |
| UpdateRunRequest | ❌ Missing | Rename from `PutExperimentRunRequest` |
| UpdateRunResponse | ❌ Missing | Rename from `PutExperimentRunResponse` |
| UUIDType | ❌ Missing | Remove usage, use `str` or `UUID` directly |

**Note**: The `UUIDType` wrapper is used for backwards compatibility. Options:
1. Add `UUIDType` as alias: `UUIDType = RootModel[UUID]` in generated.py
2. Refactor evaluations.py to use `UUID` directly
3. Add to v1 spec

---

### ❌ projects.py - 3 TODOSchema (Blocked)
```python
from ..models import CreateProjectRequest, Project, UpdateProjectRequest
```
| Import | v1 Status | Action |
|--------|-----------|--------|
| CreateProjectRequest | ❌ TODOSchema | **Needs Zod implementation** |
| Project | ❌ TODOSchema | **Needs Zod implementation** |
| UpdateProjectRequest | ❌ TODOSchema | **Needs Zod implementation** |

**⚠️ BLOCKED**: Projects API cannot work until Zod schemas are implemented.

---

## Action Items

### Option A: Rename in v1 Spec (Recommended)
Update your Zod→OpenAPI script to use v0-compatible names:

```
GetConfigurationsResponseItem  →  Configuration
CreateConfigurationRequest     →  PostConfigurationRequest
UpdateConfigurationRequest     →  PutConfigurationRequest
GetToolsResponseItem           →  Tool
UpdateMetricRequest            →  MetricEdit
UpdateDatasetRequest           →  DatasetUpdate
EventNode                      →  Event
PostExperimentRunRequest       →  CreateRunRequest
PostExperimentRunResponse      →  CreateRunResponse
DeleteExperimentRunResponse    →  DeleteRunResponse
GetExperimentRunResponse       →  GetRunResponse
GetExperimentRunsResponse      →  GetRunsResponse
PutExperimentRunRequest        →  UpdateRunRequest
PutExperimentRunResponse       →  UpdateRunResponse
```

### Option B: Add Aliases in models/__init__.py
```python
# Backwards-compatible aliases
from .generated import GetConfigurationsResponseItem as Configuration
from .generated import CreateConfigurationRequest as PostConfigurationRequest
# ... etc
```

### Blocked - Needs Zod Implementation
These won't work until proper schemas replace TODOSchema:
- SessionStartRequest
- CreateEventRequest
- EventFilter (or inline as Dict)
- CreateProjectRequest
- Project
- UpdateProjectRequest

### Special Cases
1. **Dataset**: No standalone schema exists - need to add or inline
2. **UUIDType**: Add to spec or refactor to use `UUID` directly
