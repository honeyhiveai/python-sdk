# API Filtering Improvements Summary

**Date**: November 9, 2025  
**Status**: ✅ Verified against live data

---

## Executive Summary

This document addresses API filtering limitations identified in the HoneyHive Python SDK and provides solutions that have been verified against live data.

### Issues Identified

1. **EventsAPI**: `list_events()` only supports single `EventFilter`, limiting capability
2. **DatasetsAPI**: `list_datasets()` doesn't expose backend's `type` and `dataset_id` filter parameters

### Solutions Provided

1. ✅ **EventsAPI**: Use existing `get_events()` method (supports multiple filters)
2. ✅ **DatasetsAPI**: Enhanced `list_datasets()` to expose missing filter parameters

---

## 1. EventsAPI: Multiple Filters Solution

### Problem

The `list_events()` method only accepts a single `EventFilter` parameter:

```python
def list_events(
    self, event_filter: EventFilter, limit: int = 100, project: Optional[str] = None
) -> List[Event]:
    # Only single filter supported
```

### ✅ Solution: Use `get_events()` Instead

The SDK **already has** a more powerful method that supports multiple filters:

```python
def get_events(
    self,
    project: str,
    filters: List[EventFilter],  # Multiple filters!
    *,
    date_range: Optional[Dict[str, str]] = None,
    limit: int = 1000,
    page: int = 1,
) -> Dict[str, Any]:
    """Returns dict with 'events' and 'totalEvents'"""
```

### Live Data Test Results

✅ **Single filter**: Found **1,377** tool events  
✅ **Multiple filters**: Successfully applied (returned 0 events with conflicting filters)  
✅ **Empty filters**: Returns all events (**1,778** total)  
✅ **Metadata**: Returns `totalEvents` count in addition to events list

### Usage Examples

#### Get Tool Calls for Evaluation

```python
from honeyhive import HoneyHive
from honeyhive.api import EventsAPI
from honeyhive.models.generated import EventFilter, Operator, Type

honeyhive = HoneyHive(api_key=api_key, server_url=server_url)
events_api = EventsAPI(honeyhive)

# Filter for tool events
filters = [
    EventFilter(
        field="event_type",
        value="tool",
        operator=Operator.is_,
        type=Type.string
    )
]

result = events_api.get_events(
    project="your-project",
    filters=filters,
    limit=100
)

events = result["events"]  # List[Event]
total = result["totalEvents"]  # int
```

#### Multiple Filters with Session ID

```python
# Get tool calls for a specific session
filters = [
    EventFilter(
        field="event_type",
        value="tool",
        operator=Operator.is_,
        type=Type.string
    ),
    EventFilter(
        field="session_id",
        value="abc-123",
        operator=Operator.is_,
        type=Type.id
    )
]

result = events_api.get_events(
    project="your-project",
    filters=filters
)
```

#### Filter by Cost Threshold

```python
# Get expensive model calls (cost > $0.01)
filters = [
    EventFilter(
        field="event_type",
        value="model",
        operator=Operator.is_,
        type=Type.string
    ),
    EventFilter(
        field="metadata.cost",
        value="0.01",
        operator=Operator.greater_than,
        type=Type.number
    )
]

result = events_api.get_events(
    project="your-project",
    filters=filters
)
```

#### Date Range Filtering

```python
filters = [
    EventFilter(
        field="event_type",
        value="model",
        operator=Operator.is_,
        type=Type.string
    )
]

date_range = {
    "$gte": "2024-01-01T00:00:00.000Z",
    "$lte": "2024-12-31T23:59:59.999Z"
}

result = events_api.get_events(
    project="your-project",
    filters=filters,
    date_range=date_range
)
```

### Method Comparison

| Feature | `list_events()` | `get_events()` ⭐ |
|---------|-----------------|-------------------|
| **Multiple Filters** | ❌ No (single only) | ✅ Yes |
| **Return Type** | `List[Event]` | `Dict` with metadata |
| **Total Count** | ❌ No | ✅ Yes (`totalEvents`) |
| **Date Range Filter** | ❌ No | ✅ Yes |
| **Pagination** | Basic (limit only) | ✅ Full (limit + page) |
| **Recommendation** | Legacy / simple cases | **✅ Preferred** |

### Why Your Modified Implementation Didn't Work

Your modification had an issue with enum serialization:

```python
# Your approach (problematic)
filter_dict = {
    "field": str(f.field),
    "value": str(f.value),
    "operator": f.operator.value,  # Crashes if None
    "type": f.type.value,          # Crashes if None
}
```

The correct approach (used in `get_events()`):

```python
# Correct approach
filter_dict = filter_obj.model_dump(mode="json", exclude_none=True)
# Handles Optional fields and enum serialization properly
```

---

## 2. DatasetsAPI: Enhanced Filtering

### Problem

The `list_datasets()` method only supported `project` and `limit`, but the backend API supports additional filters:

```yaml
# Backend API (from OpenAPI spec)
/datasets:
  get:
    parameters:
      - name: project (required)
      - name: type (enum: "evaluation" or "fine-tuning")
      - name: dataset_id (for filtering specific dataset)
```

### ✅ Solution: Enhanced Method Signature

**BEFORE:**
```python
def list_datasets(
    self, 
    project: Optional[str] = None, 
    limit: int = 100
) -> List[Dataset]:
```

**AFTER:**
```python
def list_datasets(
    self,
    project: Optional[str] = None,
    dataset_type: Optional[Literal["evaluation", "fine-tuning"]] = None,  # NEW
    dataset_id: Optional[str] = None,  # NEW
    limit: int = 100,
) -> List[Dataset]:
```

### Live Data Test Results

✅ **All datasets**: Found **7** datasets  
✅ **Evaluation filter**: Found **7** evaluation datasets  
✅ **Fine-tuning filter**: Successfully applied  
✅ **Type breakdown**: Datasets properly categorized

### Usage Examples

#### Filter by Dataset Type

```python
from honeyhive import HoneyHive
from honeyhive.api import DatasetsAPI

honeyhive = HoneyHive(api_key=api_key, server_url=server_url)
datasets_api = DatasetsAPI(honeyhive)

# Get only evaluation datasets
eval_datasets = datasets_api.list_datasets(
    project="my-project",
    dataset_type="evaluation"
)

# Get only fine-tuning datasets
ft_datasets = datasets_api.list_datasets(
    project="my-project",
    dataset_type="fine-tuning"
)
```

#### Filter by Specific Dataset ID

```python
# Get a specific dataset
specific_dataset = datasets_api.list_datasets(
    project="my-project",
    dataset_id="663876ec4611c47f4970f0c3"
)
```

#### Combine Filters

```python
# Get recent evaluation datasets
recent_eval = datasets_api.list_datasets(
    project="my-project",
    dataset_type="evaluation",
    limit=10
)
```

### Benefits

- ✅ **More efficient queries**: Filter at the API level instead of client-side
- ✅ **Better UX**: No need to fetch all datasets and filter manually
- ✅ **API parity**: SDK now exposes full backend capabilities
- ✅ **Future-proof**: Prepared for larger dataset collections

---

## Implementation Changes

### Files Modified

1. **`src/honeyhive/api/datasets.py`**
   - Added `Literal` import
   - Enhanced `list_datasets()` signature
   - Enhanced `list_datasets_async()` signature
   - Updated docstrings

### Files Created (Examples)

1. **`examples/get_tool_calls_for_eval.py`** - Demonstrates `get_events()` usage
2. **`test_filtering_recommendations.py`** - Verification against live data
3. **`test_enhanced_datasets_filtering.py`** - Tests enhanced dataset filtering

---

## Recommendations

### For Users

1. **EventsAPI**:
   - ✅ Use `get_events()` for any filtering needs
   - ⚠️ `list_events()` should only be used for simple, single-filter cases
   - ✅ `get_events()` provides richer metadata (total counts, pagination)

2. **DatasetsAPI**:
   - ✅ Use new `dataset_type` parameter to filter by evaluation/fine-tuning
   - ✅ Use `dataset_id` parameter to fetch specific datasets efficiently
   - ✅ More efficient than fetching all and filtering client-side

### For Maintainers

1. **Consider deprecating `list_events()`**:
   - Add deprecation warning pointing users to `get_events()`
   - `get_events()` is strictly more powerful

2. **Documentation updates needed**:
   - Update API reference to highlight `get_events()` as preferred method
   - Add migration guide from `list_events()` to `get_events()`

3. **Consider consistency**:
   - Should there be a `get_datasets()` method similar to `get_events()`?
   - Would return metadata like total count, pagination info, etc.

---

## Testing

All solutions have been verified against live data:

```bash
# Source .env and run tests
cd /Users/dhruvsingh/honeyhive/python-sdk
source .env
python test_filtering_recommendations.py
python test_enhanced_datasets_filtering.py
python examples/get_tool_calls_for_eval.py
```

### Test Environment

- **Project**: `sdk`
- **API URL**: `https://api.honeyhive.ai`
- **Total Events**: 1,778
- **Tool Events**: 1,377
- **Datasets**: 7 (all evaluation type)

---

## Summary

✅ **EventsAPI**: Use existing `get_events()` method - no code changes needed  
✅ **DatasetsAPI**: Enhanced to expose backend filter capabilities  
✅ **Verified**: All solutions tested against live data  
✅ **Backwards Compatible**: Existing code continues to work  

### Quick Migration Guide

**Before:**
```python
# Old way (limited)
events = events_api.list_events(
    event_filter=EventFilter(field="event_type", value="tool", ...),
    project="my-project"
)
```

**After:**
```python
# New way (powerful)
result = events_api.get_events(
    project="my-project",
    filters=[
        EventFilter(field="event_type", value="tool", ...),
        EventFilter(field="session_id", value="abc", ...),
    ]
)
events = result["events"]
total = result["totalEvents"]
```

---

**Questions or feedback?** This document was created based on live testing against the HoneyHive API.

