# Quick Start: Filtering Best Practices

## TL;DR

🚨 **For EventsAPI with multiple filters**: Use `get_events()` (NOT `list_events()`)  
🚨 **For DatasetsAPI**: Now supports `dataset_type` and `dataset_id` filters

---

## EventsAPI: Use `get_events()` ⭐

### ✅ Correct Way (Multiple Filters)

```python
from honeyhive import HoneyHive
from honeyhive.api import EventsAPI
from honeyhive.models.generated import EventFilter, Operator, Type

honeyhive = HoneyHive(api_key=api_key, server_url=server_url)
events_api = EventsAPI(honeyhive)

# Multiple filters work!
result = events_api.get_events(
    project="your-project",
    filters=[
        EventFilter(
            field="event_type",
            value="tool",
            operator=Operator.is_,
            type=Type.string
        ),
        EventFilter(
            field="session_id",
            value="your-session-id",
            operator=Operator.is_,
            type=Type.id
        )
    ],
    limit=100
)

events = result["events"]  # List[Event]
total = result["totalEvents"]  # int - total matching events
```

### ❌ Old Way (Single Filter Only)

```python
# This only supports ONE filter
events = events_api.list_events(
    event_filter=EventFilter(...),  # Only one filter
    project="your-project",
    limit=100
)
# Returns List[Event] - no total count
```

### Why `get_events()` is Better

| Feature | `list_events()` | `get_events()` |
|---------|-----------------|----------------|
| Multiple filters | ❌ | ✅ |
| Total count | ❌ | ✅ |
| Date ranges | ❌ | ✅ |
| Pagination | Basic | Full |

---

## DatasetsAPI: New Filter Parameters ⭐

### ✅ Enhanced Method (NEW)

```python
from honeyhive import HoneyHive
from honeyhive.api import DatasetsAPI

honeyhive = HoneyHive(api_key=api_key, server_url=server_url)
datasets_api = DatasetsAPI(honeyhive)

# Filter by type (NEW!)
eval_datasets = datasets_api.list_datasets(
    project="your-project",
    dataset_type="evaluation"  # or "fine-tuning"
)

# Filter by ID (NEW!)
specific = datasets_api.list_datasets(
    project="your-project",
    dataset_id="663876ec4611c47f4970f0c3"
)

# Combine filters (NEW!)
recent = datasets_api.list_datasets(
    project="your-project",
    dataset_type="evaluation",
    limit=10
)
```

---

## Common Use Cases

### 1. Get Tool Calls for Evaluation

```python
result = events_api.get_events(
    project="my-project",
    filters=[
        EventFilter(
            field="event_type",
            value="tool",
            operator=Operator.is_,
            type=Type.string
        )
    ]
)

print(f"Found {result['totalEvents']} tool calls")
for event in result['events']:
    print(f"  - {event.event_name}")
```

### 2. Get Expensive Model Calls

```python
result = events_api.get_events(
    project="my-project",
    filters=[
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
)
```

### 3. Get Events in Date Range

```python
result = events_api.get_events(
    project="my-project",
    filters=[
        EventFilter(
            field="event_type",
            value="model",
            operator=Operator.is_,
            type=Type.string
        )
    ],
    date_range={
        "$gte": "2024-01-01T00:00:00.000Z",
        "$lte": "2024-12-31T23:59:59.999Z"
    }
)
```

### 4. Get Only Evaluation Datasets

```python
eval_datasets = datasets_api.list_datasets(
    project="my-project",
    dataset_type="evaluation"
)
```

---

## Available Filter Operators

```python
from honeyhive.models.generated import Operator, Type

# Operators
Operator.is_              # "is"
Operator.is_not           # "is not"
Operator.contains         # "contains"
Operator.not_contains     # "not contains"
Operator.greater_than     # "greater than"

# Types
Type.string               # "string"
Type.number               # "number"
Type.boolean              # "boolean"
Type.id                   # "id" (for object IDs)
```

---

## Examples

See:
- `examples/get_tool_calls_for_eval.py` - Comprehensive examples
- `test_filtering_recommendations.py` - Live data verification
- `test_enhanced_datasets_filtering.py` - Dataset filtering tests

---

## Questions?

See `API_FILTERING_IMPROVEMENTS_SUMMARY.md` for full details, test results, and rationale.

