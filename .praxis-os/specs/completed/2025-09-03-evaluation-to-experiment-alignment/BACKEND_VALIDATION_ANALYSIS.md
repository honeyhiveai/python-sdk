# Backend Validation Analysis
## Experiment/Evaluation Run Endpoints

**Source:** `/Users/dhruvsingh/honeyhive/hive-kube/kubernetes/backend_service`  
**Last Updated:** October 2, 2025  
**Purpose:** Understanding backend API requirements for SDK implementation

---

## Executive Summary

The backend code reveals **critical implementation details** that differ from the generated SDK models:

### 🚨 Critical Findings

1. **External Dataset Handling (EXT- prefix)**
   - ✅ Backend **explicitly handles** `EXT-` prefix
   - ✅ External datasets stored in `metadata.offline_dataset_id` (not `dataset_id` field)
   - ✅ Prevents foreign key constraint errors
   - ✅ Logic exists for both CREATE and LIST operations

2. **Response Field Name**
   - ⚠️ Backend returns `evaluation` (not `experiment_run` or `run`)
   - Legacy naming preserved for backward compatibility

3. **Legacy Field Support**
   - ✅ Backend still accepts legacy fields (`evaluators`, `session_ids`, `datapoint_ids`)
   - ✅ Automatically transforms them into `metadata`

4. **Run ID Generation**
   - ✅ Backend auto-generates UUID v4 `run_id`
   - ✅ SDK should NOT generate it (let backend do it)

---

## 1. External Dataset Logic (EXT- Prefix)

### 1.1 Backend Implementation

**From `experiment_run.service.ts:50-58` (CREATE):**
```typescript
// Handle offline datasets
// If the dataset is offline, store in metadata instead of dataset_id
// linking offline datasets will lead to foreign key constraint errors
let datasetId = data.dataset_id;
const datasetMetadata = data.metadata || {};
if (datasetId?.startsWith('EXT-')) {
  datasetMetadata.offline_dataset_id = datasetId;
  datasetId = undefined;  // Clear dataset_id to avoid FK constraint
}
```

**From `experiment_run.service.ts:158-169` (LIST):**
```typescript
if (datasetId) {
  // Handle offline datasets
  if (datasetId.startsWith('EXT-')) {
    where.metadata = {
      path: ['offline_dataset_id'],
      equals: datasetId,
    };
  } else {
    where.dataset_id = datasetId;
  }
}
```

**From `experiment_run.service.ts:180-199` (RESPONSE TRANSFORMATION):**
```typescript
experimentRuns.forEach((run) => {
  try {
    // try to handle offline datasets
    if (
      run.metadata &&
      (run.metadata as any).offline_dataset_id &&
      typeof (run.metadata as any).offline_dataset_id === 'string'
    ) {
      let datasetId = (run.metadata as any).offline_dataset_id;
      if (!datasetId?.startsWith('EXT-')) {
        throw new Error(`Offline dataset_id must start with EXT: ${datasetId}`);
      }
      run.dataset_id = datasetId;  // Move back to dataset_id for response
      delete (run.metadata as any).offline_dataset_id;
    }
  } catch (error) {
    return run;
  }
});
```

### 1.2 SDK Implementation Requirements

**✅ CORRECT Approach:**
```python
# SDK should handle EXT- prefix transparently
def create_run(
    project: str,
    name: str,
    dataset_id: str,  # User provides "my-dataset" or "EXT-my-dataset"
    **kwargs
) -> CreateRunResponse:
    # Check if external dataset
    if dataset_id and dataset_id.startswith("EXT-"):
        # Store in metadata, not dataset_id field
        metadata = kwargs.get("metadata", {})
        metadata["offline_dataset_id"] = dataset_id
        kwargs["metadata"] = metadata
        kwargs["dataset_id"] = None  # Clear dataset_id
    else:
        kwargs["dataset_id"] = dataset_id
    
    # Make API call
    response = client.request("POST", "/runs", json={
        "project": project,
        "name": name,
        **kwargs
    })
    
    return CreateRunResponse(**response.json())
```

**❌ WRONG Approach:**
```python
# DON'T just pass dataset_id with EXT- prefix to backend
# It will cause foreign key constraint errors!
response = client.request("POST", "/runs", json={
    "project": project,
    "dataset_id": "EXT-my-dataset",  # ❌ BAD!
})
```

### 1.3 EXT- Prefix Validation

**Backend Requirement (from code):**
- ✅ Must start with `EXT-`
- ✅ Backend validates and throws error if `offline_dataset_id` doesn't start with `EXT-`
- ✅ SDK should ensure proper prefix

**SDK Helper Functions:**
```python
def ensure_external_dataset_id(dataset_id: str) -> str:
    """Ensure dataset ID has EXT- prefix for external datasets.
    
    Args:
        dataset_id: User-provided dataset ID
        
    Returns:
        Dataset ID with EXT- prefix
        
    Examples:
        >>> ensure_external_dataset_id("my-dataset")
        'EXT-my-dataset'
        
        >>> ensure_external_dataset_id("EXT-already-prefixed")
        'EXT-already-prefixed'
    """
    if not dataset_id:
        return dataset_id
    
    if dataset_id.startswith("EXT-"):
        return dataset_id
    
    return f"EXT-{dataset_id}"


def is_external_dataset(dataset_id: str) -> bool:
    """Check if a dataset ID is for an external dataset.
    
    Args:
        dataset_id: Dataset ID to check
        
    Returns:
        True if external dataset (starts with EXT-)
    """
    return bool(dataset_id and dataset_id.startswith("EXT-"))
```

---

## 2. Request/Response Schema Validation

### 2.1 POST /runs - Create Experiment Run

**Request Schema (`PostExperimentRunRequestSchema`):**
```typescript
{
  project?: string,              // Project name (optional if in auth context)
  name?: string,                 // Run name
  description?: string,          // Run description
  status?: ExperimentRunStatus,  // pending|completed|failed|cancelled|running
  metadata?: any,                // JSON metadata (EXT- datasets go here!)
  results?: any,                 // JSON results
  dataset_id?: string | null,    // Dataset ID (null for external datasets)
  event_ids?: string[],          // Array of UUID v4 event IDs
  configuration?: any,           // JSON configuration
  
  // Legacy fields (still accepted, transformed to metadata)
  tenant?: string,               // Legacy org_id
  evaluators?: any[],            // Legacy, goes to metadata.evaluators
  session_ids?: string[],        // Legacy, goes to metadata.session_ids
  datapoint_ids?: string[],      // Legacy, goes to metadata.datapoint_ids
  passing_ranges?: any,          // Legacy, goes to metadata.passing_ranges
}
```

**Response Schema (`PostExperimentRunResponseSchema`):**
```typescript
{
  evaluation: ExperimentRun,  // ⚠️ Note: called "evaluation" not "experiment_run"
  run_id: string,             // UUID v4 (generated by backend)
}
```

### 2.2 PUT /runs/:run_id - Update Experiment Run

**Request Schema (`PutExperimentRunRequestSchema`):**
```typescript
{
  name?: string,
  description?: string,
  status?: ExperimentRunStatus,
  metadata?: any,              // ⚠️ MERGED with existing metadata (not replaced!)
  results?: any,               // ⚠️ MERGED with existing results
  event_ids?: string[],
  configuration?: any,         // ⚠️ MERGED with existing configuration
  
  // Legacy fields
  evaluators?: any[],
  session_ids?: string[],
  datapoint_ids?: string[],
  passing_ranges?: any,
}
```

**⚠️ CRITICAL: Merge Behavior**

From `experiment_run.service.ts:262-280`:
```typescript
// Merge JSON objects instead of replacing them
if (data.metadata !== undefined) {
  updateData.metadata = {
    ...((existingRun.metadata as object) || {}),
    ...data.metadata,  // New values override old ones
  };
}
// Same for results and configuration
```

**Implication for SDK:**
- ✅ Partial updates are safe (backend merges)
- ✅ Can update individual fields without losing others
- ⚠️ To remove a field, must explicitly set it to `null`

### 2.3 GET /runs - List Experiment Runs

**Query Parameters:**
```typescript
{
  project?: string,      // Project name or ID
  dataset_id?: string,   // Filter by dataset (supports EXT- prefix!)
}
```

**Response:**
```typescript
{
  evaluations: ExperimentRun[]  // Array of runs
}
```

### 2.4 ExperimentRun Model

**From backend (`ExperimentRunSchema`):**
```typescript
{
  id: string,                    // NanoId (internal DB ID)
  run_id: string,                // UUID v4 (user-facing ID)
  name?: string,
  description?: string,
  status?: ExperimentRunStatus,
  metadata?: any,                // JSON (contains offline_dataset_id for EXT-)
  results?: any,                 // JSON
  created_at: Date,
  updated_at?: Date,
  org_id: string,                // NanoId
  project_id: string,            // NanoId
  dataset_id?: string,           // NanoId (null for external datasets)
  event_ids?: string[],          // UUID v4 array
  configuration?: any,           // JSON
}
```

---

## 3. Status Enum Values

**From `experiment_run.schema.js:9-16`:**
```typescript
enum ExperimentRunStatus {
  PENDING = "pending",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
  RUNNING = "running"
}
```

**SDK Should Use:**
```python
from enum import Enum

class ExperimentRunStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RUNNING = "running"
```

---

## 4. Legacy Field Transformation

### 4.1 Backend Transformation Logic

**From `experiment_run.schema.js:55-81`:**
```typescript
.transform((data) => {
  // Transform legacy fields into metadata
  const transformedMetadata = data.metadata ? { ...data.metadata } : {};
  
  if (data.evaluators && data.evaluators.length > 0) {
    transformedMetadata.evaluators = data.evaluators;
  }
  if (data.session_ids && data.session_ids.length > 0) {
    transformedMetadata.session_ids = data.session_ids;
  }
  if (data.datapoint_ids && data.datapoint_ids.length > 0) {
    transformedMetadata.datapoint_ids = data.datapoint_ids;
  }
  if (data.passing_ranges) {
    transformedMetadata.passing_ranges = data.passing_ranges;
  }
  
  return {
    ...data,
    metadata: Object.keys(transformedMetadata).length > 0 
      ? transformedMetadata 
      : data.metadata
  };
})
```

### 4.2 SDK Should Support Both

**Option 1: Use metadata directly (RECOMMENDED):**
```python
create_run(
    project="my-project",
    name="Test Run",
    metadata={
        "evaluators": ["accuracy", "f1_score"],
        "session_ids": ["uuid1", "uuid2"],
        "datapoint_ids": ["id1", "id2"],
        "offline_dataset_id": "EXT-my-dataset",  # External dataset
    }
)
```

**Option 2: Use legacy fields (backward compatible):**
```python
create_run(
    project="my-project",
    name="Test Run",
    evaluators=["accuracy", "f1_score"],
    session_ids=["uuid1", "uuid2"],
    datapoint_ids=["id1", "id2"],
    dataset_id="EXT-my-dataset",  # Backend transforms to metadata
)
```

---

## 5. Run ID Generation

### 5.1 Backend Generates run_id

**From `experiment_run.service.ts:46-48`:**
```typescript
// Generate unique run_id
const runId = uuidv4();
console.debug(`Generated run ID: ${runId}`);
```

**Implication:**
- ❌ SDK should NOT generate `run_id`
- ✅ Backend always generates it
- ✅ Returned in response: `{ evaluation: {...}, run_id: "..." }`

### 5.2 Difference Between `id` and `run_id`

| Field | Type | Purpose | Who Generates | User-Facing |
|-------|------|---------|---------------|-------------|
| `id` | NanoId | Internal DB primary key | Backend (Prisma) | ❌ No |
| `run_id` | UUID v4 | User-facing experiment ID | Backend | ✅ Yes |

**Usage:**
- Use `run_id` for all API operations
- Ignore `id` (internal only)

---

## 6. API Endpoint Routes

**From `experiment_run.route.ts`:**

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/runs` | Create experiment run | ✅ Yes |
| PUT | `/runs/:run_id` | Update experiment run | ✅ Yes |
| GET | `/runs` | List experiment runs | ✅ Yes |
| GET | `/runs/:run_id` | Get single experiment run | ✅ Yes |
| GET | `/runs/:run_id/metrics` | Get run metrics | ✅ Yes |
| GET | `/runs/:run_id/result` | Get run result summary | ✅ Yes |
| GET | `/runs/:new_run_id/compare-with/:old_run_id` | Compare runs | ✅ Yes |
| GET | `/runs/compare/events` | Compare events between runs | ✅ Yes |
| DELETE | `/runs/:run_id` | Delete experiment run | ✅ Yes |

---

## 7. Error Handling

**From backend code:**

### 7.1 Common Errors

| Status | Error | Cause |
|--------|-------|-------|
| 400 | Invalid request body | Schema validation failed |
| 400 | Project not found | Invalid project name/ID |
| 404 | Run not found | Invalid run_id |
| 500 | Internal server error | Unexpected backend error |

### 7.2 External Dataset Validation

**From `experiment_run.service.ts:190`:**
```typescript
if (!datasetId?.startsWith('EXT-')) {
  throw new Error(`Offline dataset_id must start with EXT: ${datasetId}`);
}
```

**SDK Should Validate:**
```python
def validate_external_dataset_id(dataset_id: str) -> None:
    """Validate external dataset ID format.
    
    Raises:
        ValueError: If dataset ID doesn't start with EXT-
    """
    if dataset_id and not dataset_id.startswith("EXT-"):
        raise ValueError(
            f"External dataset_id must start with 'EXT-': {dataset_id}"
        )
```

---

## 8. SDK Implementation Checklist

### 8.1 Must-Have Features

- [ ] **EXT- Prefix Handling**
  - [ ] Detect external datasets (starts with `EXT-`)
  - [ ] Move to `metadata.offline_dataset_id` automatically
  - [ ] Clear `dataset_id` field for external datasets
  - [ ] Helper functions: `ensure_external_dataset_id()`, `is_external_dataset()`

- [ ] **Response Field Mapping**
  - [ ] Map `evaluation` to `experiment_run` or `run` (user-friendly naming)
  - [ ] Extract `run_id` from response
  - [ ] Handle both legacy and new field names

- [ ] **Status Enum**
  - [ ] Define `ExperimentRunStatus` enum
  - [ ] Use string values: "pending", "completed", "failed", "cancelled", "running"

- [ ] **Merge Behavior for Updates**
  - [ ] Document that metadata/results/configuration are merged
  - [ ] Provide option to replace vs merge (if needed)

- [ ] **Legacy Field Support**
  - [ ] Accept `evaluators`, `session_ids`, `datapoint_ids` as parameters
  - [ ] Transform to metadata automatically
  - [ ] Document backward compatibility

### 8.2 Nice-to-Have Features

- [ ] **Validation**
  - [ ] Validate `run_id` is UUID v4 format
  - [ ] Validate `status` is valid enum value
  - [ ] Validate external dataset IDs start with `EXT-`

- [ ] **Type Safety**
  - [ ] Use Pydantic models for request/response
  - [ ] Proper type hints for all fields
  - [ ] Enum for status values

- [ ] **Error Messages**
  - [ ] Clear error messages for validation failures
  - [ ] Helpful hints for common mistakes

---

## 9. Code Examples

### 9.1 Create Run with External Dataset

**✅ CORRECT:**
```python
from honeyhive import HoneyHive
from honeyhive.experiments import create_run

client = HoneyHive(api_key="...")

# External dataset - SDK handles EXT- prefix
response = create_run(
    client=client,
    project="my-project",
    name="Experiment 1",
    dataset_id="EXT-my-dataset",  # SDK moves to metadata
    status="running",
    metadata={
        "custom_field": "value",
    }
)

# Response
print(response.run_id)  # UUID v4
print(response.experiment_run.status)  # "running"
```

**Backend receives:**
```json
{
  "project": "my-project",
  "name": "Experiment 1",
  "dataset_id": null,
  "status": "running",
  "metadata": {
    "offline_dataset_id": "EXT-my-dataset",
    "custom_field": "value"
  }
}
```

### 9.2 Create Run with Internal Dataset

**✅ CORRECT:**
```python
response = create_run(
    client=client,
    project="my-project",
    name="Experiment 2",
    dataset_id="abc123xyz",  # Internal dataset (NanoId)
    status="pending"
)
```

**Backend receives:**
```json
{
  "project": "my-project",
  "name": "Experiment 2",
  "dataset_id": "abc123xyz",
  "status": "pending"
}
```

### 9.3 Update Run (Partial Update)

**✅ CORRECT:**
```python
from honeyhive.experiments import update_run

# Only update status - other fields preserved
update_run(
    client=client,
    run_id="existing-run-uuid",
    status="completed",
    results={
        "accuracy": 0.95,
        "f1_score": 0.92,
    }
)
```

**Backend merges:**
```json
{
  "name": "Original Name",        // Preserved
  "status": "completed",          // Updated
  "metadata": {                   // Preserved
    "offline_dataset_id": "EXT-my-dataset"
  },
  "results": {                    // Merged
    "accuracy": 0.95,
    "f1_score": 0.92
  }
}
```

### 9.4 List Runs by External Dataset

**✅ CORRECT:**
```python
from honeyhive.experiments import list_runs

# List runs for external dataset
runs = list_runs(
    client=client,
    project="my-project",
    dataset_id="EXT-my-dataset"  # Backend queries metadata
)

for run in runs:
    print(f"{run.run_id}: {run.name} - {run.status}")
```

---

## 10. Critical Implementation Notes

### 10.1 Field Name Mismatch

⚠️ **Backend uses "evaluation" in responses, not "experiment_run"**

**SDK Should:**
```python
class CreateRunResponse(BaseModel):
    """Response from creating an experiment run."""
    
    run_id: str = Field(..., description="UUID v4 run identifier")
    experiment_run: ExperimentRun = Field(..., alias="evaluation")
    
    class Config:
        populate_by_name = True  # Accept both "evaluation" and "experiment_run"
```

### 10.2 Metadata Merge Strategy

⚠️ **Backend MERGES metadata, results, configuration (doesn't replace)**

**SDK Should Document:**
```python
def update_run(
    client: HoneyHive,
    run_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    results: Optional[Dict[str, Any]] = None,
    **kwargs
) -> UpdateRunResponse:
    """Update an experiment run.
    
    ⚠️ Important: metadata, results, and configuration are MERGED with
    existing values, not replaced. To remove a field, set it to None explicitly.
    
    Args:
        client: HoneyHive client
        run_id: Run ID to update
        metadata: Metadata to merge (not replace)
        results: Results to merge (not replace)
        **kwargs: Other fields to update
    """
    pass
```

### 10.3 External Dataset ID Format

⚠️ **Backend validates EXT- prefix strictly**

**SDK Should:**
1. Auto-add `EXT-` prefix if missing (user-friendly)
2. OR validate and raise clear error (strict mode)

**Recommendation: Auto-add (user-friendly)**
```python
def ensure_external_prefix(dataset_id: str) -> str:
    """Ensure external dataset has EXT- prefix."""
    if not dataset_id.startswith("EXT-"):
        return f"EXT-{dataset_id}"
    return dataset_id
```

---

## 11. Comparison with Generated Models

### 11.1 Generated Models (from SDK)

**Current SDK models (from OpenAPI):**
```python
class CreateRunRequest(BaseModel):
    project: str
    name: Optional[str] = None
    description: Optional[str] = None
    # ... other fields
```

### 11.2 Required Adjustments

**SDK needs to:**
1. ✅ Add EXT- prefix handling logic (not in generated models)
2. ✅ Add field name aliases (`evaluation` → `experiment_run`)
3. ✅ Document merge behavior for updates
4. ✅ Add helper functions for external datasets

**Approach:**
- Keep generated models for API requests
- Add wrapper functions with business logic
- Provide high-level API that handles EXT- logic

```python
# Low-level (generated)
from honeyhive.api.evaluations import EvaluationsAPI

api = EvaluationsAPI(client)
response = api.create_run(CreateRunRequest(...))

# High-level (with business logic)
from honeyhive.experiments import create_experiment_run

response = create_experiment_run(
    client=client,
    project="my-project",
    dataset_id="my-dataset",  # Auto-adds EXT- prefix
)
```

---

## 12. Next Steps

1. **Update Generated Models**
   - Check if OpenAPI spec is complete
   - Regenerate if needed

2. **Create Wrapper Functions**
   - `create_experiment_run()` with EXT- logic
   - `update_experiment_run()` with merge documentation
   - `list_experiment_runs()` with filtering

3. **Add Helper Utilities**
   - `ensure_external_dataset_id()`
   - `is_external_dataset()`
   - `validate_experiment_run_status()`

4. **Write Integration Tests**
   - Test EXT- prefix handling
   - Test merge behavior
   - Test field name mapping

5. **Document Behavior**
   - Clear docs on external vs internal datasets
   - Examples of merge behavior
   - Migration guide from legacy fields

---

**Document Status:** ✅ COMPLETE - Backend validation analyzed  
**Last Updated:** October 2, 2025  
**Next Review:** After generated models validation

