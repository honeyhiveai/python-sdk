# Customer Report Analysis - API Filtering Limitations

## Date: 2025-11-10

## Summary

Customer reported two legitimate limitations in the SDK's filtering capabilities:
1. **EventsAPI**: `list_events()` only accepts a single `EventFilter`, but they need multiple filters
2. **DatasetsAPI**: `list_datasets()` lacks filtering by dataset name or ID

## Investigation Findings

### Issue 1: EventsAPI Multiple Filters ✅ SOLUTION EXISTS

**Customer's Report:**
- `list_events()` only accepts one `EventFilter` object
- Customer attempted to modify to accept `List[EventFilter]` but filters not working

**Investigation Results:**
The SDK **already has a method** that supports multiple filters!

#### Current Implementation:

```python
# ❌ Customer is using this (single filter only)
def list_events(
    self, event_filter: EventFilter, limit: int = 100, project: Optional[str] = None
) -> List[Event]:
    """List events using EventFilter model."""
    # Only supports single filter
```

```python
# ✅ THIS METHOD ALREADY EXISTS (multiple filters supported!)
def get_events(
    self,
    project: str,
    filters: List[EventFilter],
    *,
    date_range: Optional[Dict[str, str]] = None,
    limit: int = 1000,
    page: int = 1,
) -> Dict[str, Any]:
    """Get events using filters via /events/export endpoint.
    
    This is the proper way to filter events by session_id and other criteria.
    
    Returns:
        Dict containing 'events' list and 'totalEvents' count
    """
```

**Location**: `src/honeyhive/api/events.py`, lines 384-434

**Backend Support**: Confirmed! The `/events/export` POST endpoint (backend lines 312-424) accepts an array of filters:
```javascript
var filters = _req.body.filters ? _req.body.filters : [];
```

### Issue 2: DatasetsAPI Filtering Limitations ✅ VALID ISSUE

**Customer's Report:**
- `list_datasets()` doesn't support filtering beyond project name
- Will become inefficient as datasets grow

**Investigation Results:**
The backend **supports additional filtering** but the SDK **doesn't expose it**!

#### Current SDK Implementation:

```python
def list_datasets(
    self, project: Optional[str] = None, limit: int = 100
) -> List[Dataset]:
    """List datasets with optional filtering."""
    params = {"limit": str(limit)}
    if project:
        params["project"] = project
```

**Location**: `src/honeyhive/api/datasets.py`, lines 134-146

#### Backend Capabilities (NOT exposed in SDK):

From `backend_service/app/routes/dataset.route.ts` lines 50, 83-89:

```typescript
const { project, dataset_id, name, include_datapoints } = validatedQuery.data;

// Get datasets using service
const datasets = await service.dataset_datapoint.getDatasets(
    orgId,
    projectId,
    dataset_id,  // ⚠️ NOT in SDK!
    name,        // ⚠️ NOT in SDK!
    tx,
);
```

The backend supports filtering by:
- ✅ `project` (exposed in SDK)
- ❌ `dataset_id` (NOT exposed in SDK)
- ❌ `name` (NOT exposed in SDK)
- ❌ `include_datapoints` (NOT exposed in SDK - could be useful for performance)

## Recommended Actions

### 1. EventsAPI - Documentation/Guidance Issue (Quick Fix)

**Action**: Update documentation to guide users to the correct method

**Priority**: High (customer is blocked)

**Effort**: Low (1-2 hours)

The customer should use:
```python
# Instead of this:
events_api.list_events(EventFilter(...), project="My Project")

# Use this:
result = events_api.get_events(
    project="My Project",
    filters=[
        EventFilter(field="event_name", value="tool_call", operator=..., type=...),
        EventFilter(field="session_id", value="abc123", operator=..., type=...),
        # Add as many filters as needed
    ],
    limit=100
)
events = result["events"]  # List[Event]
total = result["totalEvents"]  # int
```

**Implementation Tasks**:
- [ ] Add example to EventsAPI docstring showing both methods
- [ ] Add "See Also" cross-reference in `list_events()` pointing to `get_events()`
- [ ] Update API reference documentation
- [ ] Consider deprecating `list_events()` in favor of `get_events()`

### 2. DatasetsAPI - Missing Parameters (Enhancement)

**Action**: Add missing query parameters to match backend capabilities

**Priority**: Medium (future scalability concern)

**Effort**: Medium (4-6 hours including tests and docs)

**Proposed Enhancement**:

```python
def list_datasets(
    self,
    project: Optional[str] = None,
    dataset_id: Optional[str] = None,  # NEW
    name: Optional[str] = None,        # NEW
    include_datapoints: bool = False,  # NEW
    limit: int = 100,
) -> List[Dataset]:
    """List datasets with optional filtering.
    
    Args:
        project: Filter by project name or ID
        dataset_id: Filter by specific dataset ID (returns single dataset if found)
        name: Filter by dataset name (exact match or pattern)
        include_datapoints: Include datapoints in response (may impact performance)
        limit: Maximum number of datasets to return
    
    Returns:
        List of Dataset objects matching the filters
    
    Example:
        # Find dataset by name
        datasets = datasets_api.list_datasets(
            project="My Project",
            name="Training Data Q4",
        )
        
        # Get specific dataset with datapoints
        datasets = datasets_api.list_datasets(
            dataset_id="663876ec4611c47f4970f0c3",
            include_datapoints=True
        )
    """
    params = {"limit": str(limit)}
    if project:
        params["project"] = project
    if dataset_id:
        params["dataset_id"] = dataset_id
    if name:
        params["name"] = name
    if include_datapoints:
        params["include_datapoints"] = str(include_datapoints).lower()
    
    response = self.client.request("GET", "/datasets", params=params)
    data = response.json()
    return self._process_data_dynamically(
        data.get("testcases", []), Dataset, "testcases"
    )
```

**Implementation Tasks**:
- [x] Update `list_datasets()` and `list_datasets_async()` signatures
- [x] Add unit tests for new parameters (4 new tests)
- [x] Add integration tests with backend (2 new tests)
- [x] Update API reference documentation (docstrings with examples)
- [x] Add examples to docs showing filtering use cases
- [x] Check OpenAPI spec for parameter schemas (GetDatasetsQuerySchema)
- [x] Ensure backward compatibility (all new params are Optional)

**✅ COMPLETED - 2025-11-10**

### Weekend Progress
The team implemented `dataset_type` and `dataset_id` filtering over the weekend, partially completing this work.

### Final Implementation
Completed the remaining `name` and `include_datapoints` parameters:

**Files Modified:**
- `src/honeyhive/api/datasets.py` - Added `name` and `include_datapoints` parameters to both sync and async methods
- `tests/unit/test_api_datasets.py` - Added 4 comprehensive unit tests
- `tests/integration/test_api_clients_integration.py` - Added 2 integration tests
- `CHANGELOG.md` - Documented enhancement

**Final Signature:**
```python
def list_datasets(
    self,
    project: Optional[str] = None,
    dataset_type: Optional[Literal["evaluation", "fine-tuning"]] = None,
    dataset_id: Optional[str] = None,
    name: Optional[str] = None,
    include_datapoints: bool = False,
    limit: int = 100,
) -> List[Dataset]:
```

**Tests Added:**
1. `test_list_datasets_with_name()` - Unit test for name filtering
2. `test_list_datasets_with_include_datapoints()` - Unit test for include_datapoints
3. `test_list_datasets_with_all_filters()` - Unit test combining all filters
4. `test_list_datasets_async_with_new_filters()` - Async version tests
5. `test_list_datasets_filter_by_name()` - Integration test with real API
6. `test_list_datasets_include_datapoints()` - Integration test with real API

All tests passing ✅

## Customer Response Template

```
Hi [Customer Name],

Thank you for the detailed report! I've investigated both issues:

## EventsAPI - Solution Available!

Good news! The SDK already has what you need. Instead of `list_events()` which only supports a single filter, use `get_events()`:

```python
result = events_api.get_events(
    project="Your Project",
    filters=[
        EventFilter(field="event_type", value="tool", operator=..., type=...),
        EventFilter(field="event_name", value="tool_call", operator=..., type=...),
        # Add as many filters as you need
    ],
    limit=100,
    page=1
)

events = result["events"]  # List[Event]
total_count = result["totalEvents"]  # int
```

The `get_events()` method properly supports multiple filters and uses the `/events/export` endpoint. I'll update the docs to make this more discoverable.

## DatasetsAPI - Valid Enhancement Request

You're absolutely right about the datasets filtering limitation. The backend supports filtering by `dataset_id` and `name`, but our SDK doesn't expose these parameters yet. I'm tracking this as an enhancement:

**Short term**: Use client-side filtering after fetching
**Long term**: We'll add these parameters to `list_datasets()` in an upcoming release

Would you like me to prioritize this enhancement? If you have specific use cases, that would help us design the API update.

Best regards,
```

## Backend Code References

### Events Backend
- **File**: `/Users/josh/src/github.com/honeyhiveai/hive-kube/kubernetes/backend_service/app/routes/events.js`
- **Endpoint**: `POST /events/export` (lines 312-424)
- **Filters Support**: Array of filters (line 321: `var filters = _req.body.filters ? _req.body.filters : []`)

### Datasets Backend
- **File**: `/Users/josh/src/github.com/honeyhiveai/hive-kube/kubernetes/backend_service/app/routes/dataset.route.ts`
- **Endpoint**: `GET /datasets` (lines 33-157)
- **Query Schema**: `GetDatasetsQuerySchema` (line 42)
- **Supported Filters**: project, dataset_id, name, include_datapoints (line 50)

## OpenAPI Spec References

### Events Export
```yaml
/events/export:
  post:
    requestBody:
      properties:
        project: string
        filters: array of EventFilter  # ✅ Multiple filters supported!
        dateRange: object
        limit: integer
        page: integer
```

### Datasets Get
```yaml
/datasets:
  get:
    parameters:
      - name: project
        in: query
        type: string
      # ⚠️ Other parameters exist in backend but not documented in OpenAPI spec
```

## Next Steps

1. **Immediate**: Respond to customer with guidance on using `get_events()`
2. **Short term**: Update EventsAPI documentation with examples
3. **Medium term**: Enhance DatasetsAPI with missing filter parameters
4. **Long term**: Consider deprecating `list_events()` or making it an alias for `get_events()` with a single filter

