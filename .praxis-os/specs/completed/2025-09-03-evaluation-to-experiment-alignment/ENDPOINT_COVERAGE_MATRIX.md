# Backend Experiment Runs API Endpoint Coverage Matrix

**Generated**: 2025-10-02  
**Purpose**: Complete mapping of backend `/runs` endpoints to Python SDK implementations

---

## 📊 Summary

| Category | Total | Covered | Missing | Coverage % |
|----------|-------|---------|---------|-----------|
| **Endpoints** | 9 | 9 | 0 | **100%** |
| **Sync Methods** | 9 | 9 | 0 | **100%** |
| **Async Methods** | 9 | 9 | 0 | **100%** |

---

## 🎯 Detailed Endpoint Breakdown

### 1️⃣ **POST /runs** - Create Experiment Run

**Backend**: `experiment_run.route.ts:41-132`
```typescript
router.post('/', asyncWrapper(async (req: AuthenticatedRequest, res) => {
  // Creates new experiment run
  // Returns: { evaluation: {...}, run_id: "..." }
}));
```

**SDK Coverage**: ✅ **FULLY COVERED**
- **File**: `src/honeyhive/api/evaluations.py`
- **Sync Methods**:
  - `create_run(request: CreateRunRequest) -> CreateRunResponse` (L54-67)
  - `create_run_from_dict(run_data: dict) -> CreateRunResponse` (L69-78)
- **Async Methods**:
  - `create_run_async(request: CreateRunRequest) -> CreateRunResponse` (L80-93)
  - `create_run_from_dict_async(run_data: dict) -> CreateRunResponse` (L95-107)

**Request Body**:
```json
{
  "run": {
    "project": "string",
    "name": "string",
    "description": "string | null",
    "status": "pending | running | completed | failed | cancelled",
    "metadata": {},
    "results": {},
    "dataset_id": "string | null",
    "event_ids": ["uuid"],
    "configuration": {}
  }
}
```

**Response**:
```json
{
  "evaluation": { /* EvaluationRun object */ },
  "run_id": "uuid"
}
```

---

### 2️⃣ **PUT /runs/:run_id** - Update Experiment Run

**Backend**: `experiment_run.route.ts:135-213`
```typescript
router.put('/:run_id', asyncWrapper(async (req: AuthenticatedRequest, res) => {
  // Updates existing experiment run
  // Merges metadata, results, configuration
  // Returns: { evaluation: {...} }
}));
```

**SDK Coverage**: ✅ **FULLY COVERED**
- **File**: `src/honeyhive/api/evaluations.py`
- **Sync Methods**:
  - `update_run(run_id: str, request: UpdateRunRequest) -> UpdateRunResponse` (L161-170)
  - `update_run_from_dict(run_id: str, run_data: dict) -> UpdateRunResponse` (L172-177)
- **Async Methods**:
  - `update_run_async(run_id: str, request: UpdateRunRequest) -> UpdateRunResponse` (L179-190)
  - `update_run_from_dict_async(run_id: str, run_data: dict) -> UpdateRunResponse` (L192-201)

**Request Body** (all fields optional):
```json
{
  "name": "string",
  "description": "string",
  "status": "pending | running | completed | failed | cancelled",
  "metadata": {},
  "results": {},
  "event_ids": ["uuid"],
  "configuration": {}
}
```

**Response**:
```json
{
  "evaluation": { /* Updated EvaluationRun object */ }
}
```

**⚠️ Critical Backend Behavior**:
- `metadata`, `results`, `configuration` are **MERGED** (not replaced)
- `event_ids` is **REPLACED** if provided
- `EXT-` prefixed `dataset_id` is moved to `metadata.offline_dataset_id`

---

### 3️⃣ **GET /runs** - List Experiment Runs

**Backend**: `experiment_run.route.ts:216-281`
```typescript
router.get('/', asyncWrapper(async (req: AuthenticatedRequest, res) => {
  // Lists all experiment runs for a project
  // Optional: filter by dataset_id
  // Returns: { evaluations: [...] }
}));
```

**SDK Coverage**: ✅ **FULLY COVERED**
- **File**: `src/honeyhive/api/evaluations.py`
- **Sync Methods**:
  - `list_runs(project: Optional[str] = None, limit: int = 100) -> GetRunsResponse` (L129-143)
- **Async Methods**:
  - `list_runs_async(project: Optional[str] = None, limit: int = 100) -> GetRunsResponse` (L145-159)

**Query Parameters**:
- `project` (optional): Project name or ID
- `dataset_id` (optional): Filter by dataset
- `limit` (optional): Not exposed in backend, but SDK includes it

**Response**:
```json
{
  "evaluations": [
    { /* EvaluationRun object */ },
    ...
  ]
}
```

---

### 4️⃣ **GET /runs/:run_id** - Get Single Experiment Run

**Backend**: `experiment_run.route.ts:284-346`
```typescript
router.get('/:run_id', asyncWrapper(async (req: AuthenticatedRequest, res) => {
  // Retrieves a single experiment run by ID
  // Returns: { evaluation: {...} }
}));
```

**SDK Coverage**: ✅ **FULLY COVERED**
- **File**: `src/honeyhive/api/evaluations.py`
- **Sync Methods**:
  - `get_run(run_id: str) -> GetRunResponse` (L109-117)
- **Async Methods**:
  - `get_run_async(run_id: str) -> GetRunResponse` (L119-127)

**Response**:
```json
{
  "evaluation": {
    "run_id": "uuid",
    "project": "string",
    "name": "string",
    "event_ids": ["uuid"],
    "dataset_id": "string | null",
    "datapoint_ids": ["string"],
    "results": {},
    "configuration": {},
    "metadata": {},
    "status": "string"
  }
}
```

**⚠️ SDK Enhancement**: Includes UUID conversion utility `_convert_uuids_recursively()` to handle backend returning UUIDs as strings.

---

### 5️⃣ **GET /runs/:run_id/metrics** - Get Run Metrics (Raw)

**Backend**: `experiment_run.route.ts:349-442`
```typescript
router.get('/:run_id/metrics', asyncWrapper(async (req: AuthenticatedRequest, res) => {
  // Calls: getEventMetrics(orgId, projectId, dateRange, filters, run_id)
  // Returns raw event metrics without aggregation
}));
```

**SDK Coverage**: ✅ **FULLY COVERED**
- **File**: `src/honeyhive/api/evaluations.py`
- **Sync Methods**:
  - `get_run_metrics(run_id: str) -> Dict[str, Any]` (L281-299)
- **Async Methods**:
  - `get_run_metrics_async(run_id: str) -> Dict[str, Any]` (L301-304)

**Query Parameters**:
- `dateRange` (optional): Not exposed in SDK yet
- `filters` (optional): Not exposed in SDK yet

**Response** (example):
```json
{
  "events": [
    {
      "event_id": "uuid",
      "metrics": {
        "accuracy": 0.85,
        "latency": 120
      },
      "timestamp": "2025-10-02T..."
    }
  ]
}
```

**⚠️ SDK Gap**: Does not expose `dateRange` and `filters` query parameters.

---

### 6️⃣ **GET /runs/:run_id/result** - Get Run Result (Aggregated)

**Backend**: `experiment_run.route.ts:445-528`
```typescript
router.get('/:run_id/result', asyncWrapper(async (req: AuthenticatedRequest, res) => {
  // Calls: computeEvaluationSummary(orgId, projectId, run_id, aggregate_function, filters)
  // Returns aggregated metrics, pass/fail status, composite metrics
}));
```

**SDK Coverage**: ✅ **FULLY COVERED**
- **File**: `src/honeyhive/api/evaluations.py`
- **Sync Methods**:
  - `get_run_result(run_id: str, aggregate_function: str = "average") -> Dict[str, Any]` (L239-268)
- **Async Methods**:
  - `get_run_result_async(run_id: str, aggregate_function: str = "average") -> Dict[str, Any]` (L270-279)

**Query Parameters**:
- `aggregate_function`: `"average"` | `"sum"` | `"min"` | `"max"` (default: "average")
- `filters` (optional): Not exposed in SDK yet

**Response** (example):
```json
{
  "success": true,
  "passed": 85,
  "failed": 15,
  "metrics": {
    "accuracy": {
      "aggregate": 0.85,
      "values": [0.8, 0.9, 0.85],
      "min": 0.8,
      "max": 0.9,
      "count": 3
    }
  },
  "datapoints": [...]
}
```

**⚠️ SDK Gap**: Does not expose `filters` query parameter.

---

### 7️⃣ **GET /runs/:new_run_id/compare-with/:old_run_id** - Compare Runs (Aggregated)

**Backend**: `experiment_run.route.ts:531-614`
```typescript
router.get('/:new_run_id/compare-with/:old_run_id', asyncWrapper(async (req: AuthenticatedRequest, res) => {
  // 1. Gets summaries for both runs via computeEvaluationSummary()
  // 2. Compares via compareRunMetrics(oldRunSummary, newRunSummary)
  // Returns: metric deltas, percent changes, common/new/old datapoints
}));
```

**SDK Coverage**: ✅ **FULLY COVERED**
- **File**: `src/honeyhive/api/evaluations.py`
- **Sync Methods**:
  - `compare_runs(new_run_id: str, old_run_id: str, aggregate_function: str = "average") -> Dict[str, Any]` (L306-334)
- **Async Methods**:
  - `compare_runs_async(new_run_id: str, old_run_id: str, aggregate_function: str = "average") -> Dict[str, Any]` (L336-345)

**Query Parameters**:
- `aggregate_function`: `"average"` | `"sum"` | `"min"` | `"max"` (default: "average")
- `filters` (optional): Not exposed in SDK yet

**Response Structure** (from `compareRunMetrics()`):
```json
{
  "commonDatapoints": ["id1", "id2", ...],  // List of common datapoint IDs
  "metrics": [
    {
      "metric_name": "accuracy",
      "event_name": "initialization",
      "metric_type": "CLIENT_SIDE",
      "event_type": "session",
      "old_aggregate": 0.80,
      "new_aggregate": 0.85,
      "found_count": 3,
      "improved_count": 1,
      "degraded_count": 0,
      "same_count": 2,
      "improved": ["id1"],
      "degraded": [],
      "same": ["id2", "id3"],
      "old_values": [0.8, 0.75, 0.85],
      "new_values": [0.9, 0.8, 0.85]
    }
  ],
  "event_details": [
    {
      "event_name": "initialization",
      "event_type": "session",
      "presence": "both"
    }
  ],
  "old_run": { /* EvaluationRun */ },
  "new_run": { /* EvaluationRun */ }
}
```

**⚠️ Critical Note**: This endpoint returns a **LIST** of common datapoints (`commonDatapoints`), NOT a count. The SDK wrapper in `experiments/results.py` was incorrectly expecting this.

**⚠️ SDK Gap**: Does not expose `filters` query parameter.

---

### 8️⃣ **GET /runs/compare/events** - Compare Run Events (Datapoint-Level)

**Backend**: `experiment_run.route.ts:617-690`
```typescript
router.get('/compare/events', asyncWrapper(async (req: AuthenticatedRequest, res) => {
  // Calls: getSessionComparisonForEvaluations(orgId, projectId, filter, run_id_1, run_id_2, event_name, event_type, limit, skip)
  // Returns paired events for each common datapoint
}));
```

**SDK Coverage**: ✅ **FULLY COVERED**
- **File**: `src/honeyhive/api/evaluations.py`
- **Sync Methods**:
  - `compare_run_events(new_run_id: str, old_run_id: str, event_name: str = None, event_type: str = None, limit: int = 100, page: int = 1) -> Dict[str, Any]` (L347-405)
- **Async Methods**:
  - `compare_run_events_async(new_run_id: str, old_run_id: str, event_name: str = None, event_type: str = None, limit: int = 100, page: int = 1) -> Dict[str, Any]` (L407-432)

**Query Parameters**:
- `run_id_1` (required): New run ID
- `run_id_2` (required): Old run ID
- `event_name` (optional): Filter by event name (e.g., "initialization")
- `event_type` (optional): Filter by event type (e.g., "session")
- `limit` (optional, default: 10): Pagination limit
- `page` (optional, default: 1): Pagination page
- `filter` (optional): Not exposed in SDK yet

**Response**:
```json
{
  "events": [
    {
      "datapoint_id": "EXT-abc123",
      "event_1": { /* Full session/event object from run_id_1 */ },
      "event_2": { /* Full session/event object from run_id_2 */ }
    }
  ],
  "totalEvents": "3"
}
```

**⚠️ Critical Difference from `/runs/:new_run_id/compare-with/:old_run_id`**:
- This endpoint returns **paired events** (event_1, event_2) for each common datapoint
- The aggregated comparison endpoint returns **metrics analysis** with improved/degraded lists
- **Use Case**: This is for detailed event-by-event comparison, NOT for metric aggregation

**⚠️ SDK Gap**: Does not expose `filter` query parameter.

---

### 9️⃣ **DELETE /runs/:run_id** - Delete Experiment Run

**Backend**: `experiment_run.route.ts:693-751`
```typescript
router.delete('/:run_id', asyncWrapper(async (req: AuthenticatedRequest, res) => {
  // Deletes experiment run
  // Returns: { success: true }
}));
```

**SDK Coverage**: ✅ **FULLY COVERED**
- **File**: `src/honeyhive/api/evaluations.py`
- **Sync Methods**:
  - `delete_run(run_id: str) -> DeleteRunResponse` (L203-219)
- **Async Methods**:
  - `delete_run_async(run_id: str) -> DeleteRunResponse` (L221-237)

**Response**:
```json
{
  "success": true
}
```

---

## 🔍 SDK Implementation Details

### File: `src/honeyhive/api/evaluations.py`

**Key Features**:
1. **UUID Conversion Utility** (`_convert_uuids_recursively()`):
   - Automatically converts string UUIDs from backend to `UUIDType` objects
   - Handles nested structures (dicts, lists)
   - Special handling for `event_ids` arrays
   
2. **Dual Method Pattern**:
   - `*_from_dict()` methods for legacy/flexible usage
   - Pydantic model methods for type-safe usage
   
3. **Full Async Support**:
   - Every endpoint has an async variant
   
4. **Error Handling**:
   - Uses `BaseAPI.error_handler` for consistent error reporting

---

## ⚠️ Known SDK Gaps

### 1. Missing Query Parameters

| Endpoint | Missing Parameter | Impact |
|----------|-------------------|--------|
| `GET /runs/:run_id/metrics` | `dateRange`, `filters` | Cannot filter metrics by date or custom filters |
| `GET /runs/:run_id/result` | `filters` | Cannot filter aggregation results |
| `GET /runs/:new_run_id/compare-with/:old_run_id` | `filters` | Cannot filter comparison results |
| `GET /runs/compare/events` | `filter` | Cannot filter event comparison |

**Recommendation**: Add optional `filters` parameter to all relevant methods.

### 2. Response Structure Misalignment

**Issue**: The SDK wrapper in `experiments/results.py:compare_runs()` expects the response from `/runs/compare/events` but is currently calling `/runs/:new_run_id/compare-with/:old_run_id`.

**Current State**:
```python
# experiments/results.py:163
response = client.evaluations.compare_run_events(  # ✅ NOW CORRECT
    new_run_id=new_run_id,
    old_run_id=old_run_id,
    event_name=event_name,
    event_type=event_type,
)

# Parsing expects:
common_datapoints_list = response.get("commonDatapoints", [])  # ❌ WRONG KEY
```

**Problem**: `/runs/compare/events` returns `{"events": [...], "totalEvents": "3"}`, NOT `{"commonDatapoints": [...], "metrics": [...]}`.

**The two endpoints serve different purposes**:
1. `/runs/:new_run_id/compare-with/:old_run_id` → Aggregated metrics comparison (has `commonDatapoints` and `metrics` arrays)
2. `/runs/compare/events` → Detailed event pairs (has `events` array with `event_1`/`event_2` objects)

---

## 🎯 Recommendations

### 1. **Expose Missing Query Parameters**

Add to all relevant methods:
```python
def get_run_metrics(
    self, 
    run_id: str,
    date_range: Optional[Dict[str, Any]] = None,  # ← NEW
    filters: Optional[List[Dict[str, Any]]] = None  # ← NEW
) -> Dict[str, Any]:
    params = {}
    if date_range:
        params["dateRange"] = json.dumps(date_range)
    if filters:
        params["filters"] = json.dumps(filters)
    # ...
```

### 2. **Fix `compare_runs()` Wrapper**

The high-level `experiments/results.py:compare_runs()` function should use `/runs/:new_run_id/compare-with/:old_run_id` (which returns the aggregated comparison), NOT `/runs/compare/events` (which returns event pairs).

**Current (broken)**:
```python
# experiments/results.py
response = client.evaluations.compare_run_events(...)  # ❌ Wrong endpoint
common_datapoints_list = response.get("commonDatapoints", [])  # ❌ Key doesn't exist
```

**Correct**:
```python
# experiments/results.py
response = client.evaluations.compare_runs(  # ✅ Use aggregated comparison
    new_run_id=new_run_id,
    old_run_id=old_run_id,
    aggregate_function=aggregate_function,
)

# Parse the correct structure
common_datapoints_list = response.get("commonDatapoints", [])  # ✅ This key exists
metrics_array = response.get("metrics", [])  # ✅ This key exists
```

### 3. **Add Dedicated Event Comparison Function**

Create a separate high-level function for event-by-event comparison:

```python
# experiments/results.py

def compare_run_events_detailed(
    client: Any,
    new_run_id: str,
    old_run_id: str,
    event_name: str = None,
    event_type: str = None,
    limit: int = 100,
    page: int = 1,
) -> Dict[str, Any]:
    """
    Get detailed event-by-event comparison between two runs.
    
    Returns paired events (event_1, event_2) for each common datapoint.
    Use this for detailed inspection of individual datapoint executions.
    
    For aggregated metric comparison, use compare_runs() instead.
    """
    response = client.evaluations.compare_run_events(
        new_run_id=new_run_id,
        old_run_id=old_run_id,
        event_name=event_name,
        event_type=event_type,
        limit=limit,
        page=page,
    )
    
    return {
        "events": response.get("events", []),
        "total_events": int(response.get("totalEvents", "0")),
    }
```

### 4. **Document Endpoint Purposes**

Add clear documentation explaining:
- `/runs/:new_run_id/compare-with/:old_run_id` → For metric aggregation and improvement/regression analysis
- `/runs/compare/events` → For detailed event-by-event inspection

---

## ✅ Coverage Status: **100%**

All 9 backend endpoints are covered in the SDK with both sync and async methods. The main issues are:
1. Missing query parameter exposure (`filters`, `dateRange`)
2. Incorrect endpoint usage in `experiments/results.py:compare_runs()` wrapper
3. Response structure parsing errors due to endpoint mismatch

**Action Items**:
1. ✅ Expose `filters` parameter in relevant methods
2. ✅ Fix `compare_runs()` to use correct endpoint
3. ✅ Add dedicated `compare_run_events_detailed()` function
4. ✅ Document the difference between the two comparison endpoints

---

**End of Endpoint Coverage Matrix**

