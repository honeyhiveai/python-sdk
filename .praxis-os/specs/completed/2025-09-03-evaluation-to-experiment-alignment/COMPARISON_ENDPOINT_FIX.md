# Comparison Endpoint Fix - 2025-10-02

## 🐛 Problem

The `compare_runs()` function in `experiments/results.py` was using the **wrong backend endpoint**, causing it to return 0 common datapoints even though the SDK was generating consistent `EXT-` prefixed datapoint IDs.

### Root Cause

There are **TWO different comparison endpoints** in the backend, each serving a different purpose:

1. **`GET /runs/:new_run_id/compare-with/:old_run_id`** - **Aggregated Metric Comparison**
   - Returns: `{commonDatapoints: [...], metrics: [...], event_details: [...], old_run: {...}, new_run: {...}}`
   - **Use case**: Metric aggregation, improvement/regression analysis

2. **`GET /runs/compare/events`** - **Event-by-Event Pairs**
   - Returns: `{events: [{datapoint_id, event_1, event_2}], totalEvents: "3"}`
   - **Use case**: Detailed inspection of individual event pairs

### The Bug

The SDK wrapper was calling the **wrong endpoint**:

```python
# BEFORE (BROKEN)
response = client.evaluations.compare_run_events(  # ❌ Wrong endpoint
    new_run_id=new_run_id,
    old_run_id=old_run_id,
    event_name=event_name,  # ❌ Not supported by aggregated endpoint
    event_type=event_type,  # ❌ Not supported by aggregated endpoint
)

# Expected: {"commonDatapoints": [...], "metrics": [...]}
# Got:      {"events": [...], "totalEvents": "3"}

common_datapoints_list = response.get("commonDatapoints", [])  # ❌ Returns []
```

---

## ✅ Solution

### 1. Updated `experiments/results.py:compare_runs()`

**File**: `src/honeyhive/experiments/results.py`

**Changes**:
- **Removed**: `event_name` and `event_type` parameters (not supported by aggregated endpoint)
- **Changed**: Call to `client.evaluations.compare_runs()` instead of `compare_run_events()`
- **Updated**: Docstring to reflect correct endpoint and behavior

```python
# AFTER (FIXED)
def compare_runs(
    client: Any,
    new_run_id: str,
    old_run_id: str,
    aggregate_function: str = "average",  # ✅ Supported parameter
) -> RunComparisonResult:
    """
    Compare two experiment runs using backend aggregated comparison.

    Backend Endpoint: GET /runs/:new_run_id/compare-with/:old_run_id
    """
    # Use aggregated comparison endpoint
    response = client.evaluations.compare_runs(  # ✅ Correct endpoint
        new_run_id=new_run_id,
        old_run_id=old_run_id,
        aggregate_function=aggregate_function,
    )

    # Now correctly parses:
    # {"commonDatapoints": [...], "metrics": [...], "old_run": {...}, "new_run": {...}}
    common_datapoints_list = response.get("commonDatapoints", [])  # ✅ Works!
    ...
```

### 2. Updated Integration Test

**File**: `tests/integration/test_experiments_integration.py`

**Changes**:
- Removed `event_name` and `event_type` parameters from `compare_runs()` call
- Fixed attribute names: `new_datapoints` → `new_only_datapoints`, `old_datapoints` → `old_only_datapoints`

```python
# BEFORE
comparison = compare_runs(
    client=integration_client,
    new_run_id=improved_run_id,
    old_run_id=baseline_run_id,
    aggregate_function="average",
    event_name="initialization",  # ❌ Not supported
    event_type="session",         # ❌ Not supported
)

assert comparison.new_datapoints == 0  # ❌ Wrong attribute name

# AFTER
comparison = compare_runs(
    client=integration_client,
    new_run_id=improved_run_id,
    old_run_id=baseline_run_id,
    aggregate_function="average",  # ✅ Only supported parameter
)

assert comparison.new_only_datapoints == 0  # ✅ Correct attribute name
```

---

## 📊 Test Results

### Before Fix
```
FAILED - AssertionError: Should have 3 common datapoints, got 0
```

### After Fix
```
✅ Run IDs match
✅ Common datapoints: 3
✅ No new/old datapoints (same dataset)
✅ Detected improvements and regressions
PASSED [100%]
```

---

## 🎯 Key Takeaways

### 1. Two Endpoints, Two Purposes

| Endpoint | Purpose | Returns | When to Use |
|----------|---------|---------|-------------|
| `/runs/:new_run_id/compare-with/:old_run_id` | **Aggregated Comparison** | `commonDatapoints`, `metrics` array with improved/degraded lists | Metric analysis, dashboards, high-level comparison |
| `/runs/compare/events` | **Event Pairs** | `events` array with paired `event_1`/`event_2` objects | Detailed event inspection, debugging individual executions |

### 2. SDK Implementation

Both endpoints are exposed in `src/honeyhive/api/evaluations.py`:
- `compare_runs()` → Aggregated comparison
- `compare_run_events()` → Event-by-event pairs

### 3. High-Level Wrapper

The `experiments/results.py:compare_runs()` wrapper should use the **aggregated endpoint** for:
- Metric delta calculation
- Improvement/regression detection
- Common datapoint identification
- Statistical aggregation

For detailed event inspection, users can directly call:
```python
client.evaluations.compare_run_events(
    new_run_id="...",
    old_run_id="...",
    event_name="initialization",
    event_type="session",
)
```

---

## 📝 Related Documentation

- **Endpoint Coverage Matrix**: `.praxis-os/specs/2025-09-03-evaluation-to-experiment-alignment/ENDPOINT_COVERAGE_MATRIX.md`
  - Complete breakdown of all 9 backend endpoints
  - Detailed response structures
  - SDK coverage status

---

## ✅ Status: **FIXED**

**Commit Summary**:
- Fixed `compare_runs()` to use correct backend endpoint
- Removed unsupported parameters (`event_name`, `event_type`)
- Updated integration test
- All tests now passing with 3 common datapoints correctly identified

**Files Modified**:
1. `src/honeyhive/experiments/results.py`
2. `tests/integration/test_experiments_integration.py`

**Verified**: Integration test confirms backend correctly matches datapoints by `datapoint_id` and returns full metric analysis.

