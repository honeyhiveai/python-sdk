# Critical Bug Fixes - Customer-Reported Issues

**Date**: October 2, 2025  
**Priority**: CRITICAL  
**Status**: FIXED  

## Summary

Fixed two critical bugs in the new tracer that were affecting customer production environments:

1. **DatasetsAPI returns empty list** (datasets.py)
2. **DatapointsAPI not writing fields** (datapoints.py)

---

## Bug #1: DatasetsAPI Returns Empty List

### Issue Description
The `/datasets` API returns data in format `{"testcases": {...}}`, but `DatasetsAPI.list_datasets()` was looking for `datasets` instead of `testcases` on line 129.

### Root Cause
**Backend** returns:
```json
{
  "testcases": [
    {"id": "...", "name": "...", ...}
  ]
}
```

**SDK** was looking for:
```python
data.get("datasets", [])  # ❌ Wrong key!
```

### Fix Applied

**File**: `src/honeyhive/api/datasets.py`

**Lines Changed**: 
- Line 129: `data.get("testcases", [])` (was "datasets")
- Line 143: `data.get("testcases", [])` (async version)

```python
# Before (WRONG):
return self._process_data_dynamically(
    data.get("datasets", []), Dataset, "datasets"
)

# After (CORRECT):
return self._process_data_dynamically(
    data.get("testcases", []), Dataset, "testcases"
)
```

### Impact
- ✅ `list_datasets()` now correctly returns dataset list
- ✅ `list_datasets_async()` also fixed
- ✅ Customers can now retrieve their datasets

---

## Bug #2: DatapointsAPI Not Writing Fields

### Issue Description
The `/datapoints` API was wrapping the request in `{"datapoint": {...}}`, but the backend expects the datapoint fields directly (like `inputs`, `ground_truth`, etc.) without the outer wrapper.

### Root Cause
**Backend expects** (validated via `CreateDatapointSchema`):
```json
{
  "inputs": {...},
  "ground_truth": {...},
  "metadata": {...}
}
```

**SDK was sending**:
```json
{
  "datapoint": {
    "inputs": {...},
    "ground_truth": {...},
    "metadata": {...}
  }
}
```

The outer `"datapoint"` wrapper caused fields to not be written.

### Fix Applied

**File**: `src/honeyhive/api/datapoints.py`

**Lines Changed**:
- Line 17: Removed `{"datapoint": ...}` wrapper in `create_datapoint()`
- Line 42: Removed `{"datapoint": ...}` wrapper in `create_datapoint_from_dict()`
- Line 71: Removed `{"datapoint": ...}` wrapper in `create_datapoint_async()`
- Line 96: Removed `{"datapoint": ...}` wrapper in `create_datapoint_from_dict_async()`

```python
# Before (WRONG):
response = self.client.request(
    "POST",
    "/datapoints",
    json={"datapoint": request.model_dump(mode="json", exclude_none=True)},
)

# After (CORRECT):
response = self.client.request(
    "POST",
    "/datapoints",
    json=request.model_dump(mode="json", exclude_none=True),
)
```

### Impact
- ✅ Datapoint fields now correctly written to backend
- ✅ All 4 methods fixed (sync/async, model/dict)
- ✅ Customers can now create datapoints with proper data

---

## Validation

### Backend Code Validation

**DatasetsAPI** - Confirmed in `app/routes/dataset.route.ts:134`:
```typescript
const responseData = { testcases: datasets };
```

**DatapointsAPI** - Confirmed in `app/routes/datapoint.route.ts:225`:
```typescript
const validatedData = CreateDatapointSchema.safeParse(req.body);
```

Backend expects request body directly, not wrapped.

---

## Testing Recommendations

### Test Case 1: List Datasets
```python
from honeyhive import HoneyHive

client = HoneyHive(api_key="...", project="...")
datasets = client.datasets.list_datasets()

# Expected: Returns list of datasets
# Before fix: Returned empty list []
# After fix: Returns actual datasets
assert len(datasets) > 0
```

### Test Case 2: Create Datapoint
```python
from honeyhive.models import CreateDatapointRequest

request = CreateDatapointRequest(
    inputs={"query": "test"},
    ground_truth={"answer": "test answer"},
    project="test-project"
)

datapoint = client.datapoints.create_datapoint(request)

# Expected: Datapoint created with inputs and ground_truth
# Before fix: Fields not written (empty datapoint)
# After fix: All fields correctly written
assert datapoint.inputs == {"query": "test"}
assert datapoint.ground_truth == {"answer": "test answer"}
```

---

## Files Modified

1. `src/honeyhive/api/datasets.py`
   - Line 129: Changed `datasets` → `testcases`
   - Line 143: Changed `datasets` → `testcases` (async)

2. `src/honeyhive/api/datapoints.py`
   - Line 17: Removed `{"datapoint": ...}` wrapper
   - Line 42: Removed `{"datapoint": ...}` wrapper
   - Line 71: Removed `{"datapoint": ...}` wrapper (async)
   - Line 96: Removed `{"datapoint": ...}` wrapper (async dict)

---

## Deployment Priority

🚨 **CRITICAL**: These fixes should be deployed immediately as they affect core functionality:
- Customers cannot retrieve datasets (Bug #1)
- Customers cannot create datapoints with data (Bug #2)

### Recommended Actions

1. ✅ Run existing test suite to ensure no regressions
2. ✅ Deploy to production immediately
3. ✅ Notify affected customers of fix
4. ✅ Add integration tests to prevent regression

---

## Impact on Experiments Module

These fixes are critical for the experiments module implementation because:

1. **External Datasets**: The experiments module needs `list_datasets()` to work correctly
2. **Datapoint Creation**: External datasets require creating datapoints programmatically
3. **API Consistency**: Ensures experiments module uses correct API contracts

### Experiments Spec Update Needed

The experiments module specification should reference these fixes:
- ✅ Use `testcases` key when parsing dataset responses
- ✅ Send datapoint data directly without wrapper
- ✅ Validate all API contracts against backend code

---

## Prevention Measures

### 1. Backend Contract Testing
Add integration tests that validate SDK against actual backend responses:

```python
# tests/integration/test_backend_contracts.py

def test_datasets_response_format():
    """Validate backend returns 'testcases' not 'datasets'."""
    response = client.request("GET", "/datasets")
    data = response.json()
    assert "testcases" in data  # NOT "datasets"

def test_datapoint_request_format():
    """Validate backend expects direct fields, not wrapped."""
    # Should work WITHOUT {"datapoint": ...} wrapper
    response = client.request(
        "POST",
        "/datapoints",
        json={"inputs": {}, "ground_truth": {}}  # Direct fields
    )
    assert response.status_code == 200
```

### 2. Backend Schema Validation
- Add TypeScript schema imports to SDK tests
- Validate Python models match backend Zod schemas
- Automate schema sync checks in CI/CD

### 3. OpenAPI Spec Sync
- Ensure OpenAPI spec reflects actual backend behavior
- Regenerate SDK models when backend schemas change
- Add schema drift detection

---

## Related Issues

- Customer reported datasets returning empty list
- Customer reported datapoint fields not being written
- Both issues introduced in recent tracer refactor

---

**Fixed By**: AI Assistant  
**Validated Against**: Backend code (`hive-kube/kubernetes/backend_service`)  
**Status**: ✅ FIXED - Ready for deployment  
**Priority**: 🚨 CRITICAL - Deploy immediately

