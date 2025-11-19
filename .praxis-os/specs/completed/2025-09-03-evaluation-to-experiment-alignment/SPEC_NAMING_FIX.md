# Specification Naming Conflict Resolution

**Date**: October 2, 2025  
**Issue**: Naming conflict with `Metrics` model  
**Resolution**: Renamed to `AggregatedMetrics`  

---

## Issue Identified

The experiments spec originally proposed a `Metrics` model that would conflict with:

1. **Generated Model**: `Metrics` class exists in `src/honeyhive/models/generated.py:707`
2. **MetricsAPI**: `MetricsAPI` class works with `Metric` model in similar namespace
3. **Import Confusion**: Would cause ambiguous imports and naming conflicts

---

## Resolution

### ❌ Original Name (Conflicting)
```python
# experiments/models.py
class Metrics(BaseModel):
    """Aggregated metrics for experiment results."""
    aggregation_function: Optional[str] = None
    model_config = ConfigDict(extra="allow")
```

**Problems**:
- Conflicts with `honeyhive.models.generated.Metrics`
- Ambiguous in context of `MetricsAPI`
- Unclear distinction from individual `Metric` model

---

### ✅ New Name (Clear and Distinct)
```python
# experiments/models.py
class AggregatedMetrics(BaseModel):
    """Aggregated metrics model for experiment results with dynamic metric keys.
    
    This is distinct from the generated 'Metrics' model which has incorrect structure.
    """
    aggregation_function: Optional[str] = None
    model_config = ConfigDict(extra="allow")
```

**Advantages**:
- ✅ No conflict with generated `Metrics`
- ✅ Clear semantic meaning: "aggregated" metrics from backend
- ✅ Distinct from individual `Metric` used by `MetricsAPI`
- ✅ Self-documenting name
- ✅ Follows naming pattern: `AggregatedMetrics` for collection of aggregated metric data

---

## Updated Models

### Full Model Hierarchy
```python
# src/honeyhive/experiments/models.py

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

# 1. Status enum (extended from generated)
class ExperimentRunStatus(str, Enum):
    """Extended status enum with all backend values."""
    PENDING = "pending"
    COMPLETED = "completed"
    RUNNING = "running"
    FAILED = "failed"
    CANCELLED = "cancelled"

# 2. Aggregated metrics (fixed structure)
class AggregatedMetrics(BaseModel):
    """
    Aggregated metrics model for experiment results with dynamic metric keys.
    
    Distinct from honeyhive.models.generated.Metrics which has incorrect structure.
    Backend returns dynamic keys for metric names, this model handles them.
    """
    aggregation_function: Optional[str] = None
    model_config = ConfigDict(extra="allow")
    
    def get_metric(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific metric by name."""
        return getattr(self, metric_name, None)
    
    def list_metrics(self) -> List[str]:
        """List all metric names."""
        return [k for k in self.__dict__ if k != "aggregation_function"]
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics as dictionary."""
        return {k: v for k, v in self.__dict__.items() 
                if k != "aggregation_function"}

# 3. Result summary (uses AggregatedMetrics)
class ExperimentResultSummary(BaseModel):
    """Aggregated experiment result from backend."""
    run_id: str
    status: str
    success: bool
    passed: List[str]
    failed: List[str]
    metrics: AggregatedMetrics  # ✅ Clear name
    datapoints: List[Any]

# 4. Comparison result
class RunComparisonResult(BaseModel):
    """Comparison between two experiment runs."""
    new_run_id: str
    old_run_id: str
    common_datapoints: int
    new_only_datapoints: int
    old_only_datapoints: int
    metric_deltas: Dict[str, Any]
```

---

## Import Clarity

### Before (Confusing)
```python
from honeyhive.models.generated import Metrics  # Generated model
from honeyhive.experiments.models import Metrics  # ❌ Conflict!
```

### After (Clear)
```python
from honeyhive.models.generated import Metrics  # Generated model (wrong structure)
from honeyhive.experiments.models import AggregatedMetrics  # ✅ Clear, distinct
```

---

## Usage Examples

### Creating Result Summary
```python
from honeyhive.experiments.models import ExperimentResultSummary, AggregatedMetrics

# Parse backend response
metrics_data = response.metrics.dict()
aggregated = AggregatedMetrics(**metrics_data)

# Access metrics
avg_score = aggregated.get_metric("accuracy")
all_metrics = aggregated.list_metrics()

# Create summary
summary = ExperimentResultSummary(
    run_id="...",
    status="completed",
    success=True,
    passed=["dp1", "dp2"],
    failed=[],
    metrics=aggregated,  # Clear what this is
    datapoints=[...]
)
```

### No Confusion with MetricsAPI
```python
from honeyhive import HoneyHive
from honeyhive.models import Metric  # Individual metric definition
from honeyhive.experiments.models import AggregatedMetrics  # Experiment aggregates

client = HoneyHive(api_key="...")

# Define a metric (MetricsAPI)
metric = Metric(
    name="accuracy",
    type="numeric",
    threshold=0.8
)
client.metrics.create_metric(metric)

# Get experiment results with aggregated metrics
result = client.experiments.get_run_result("run_id")
# result.metrics is AggregatedMetrics, not Metric or generated Metrics
```

---

## Files Updated

1. ✅ `specs.md` - All references updated
   - Model definition: `Metrics` → `AggregatedMetrics`
   - Usage in `ExperimentResultSummary`
   - Code examples updated

2. ✅ `tasks.md` - Task deliverables updated
   - TASK-001: Create `AggregatedMetrics` model
   - Acceptance criteria: No naming conflicts

3. ✅ `SPEC_NAMING_FIX.md` - Created (this document)

---

## Validation

### Namespace Check
```python
# ✅ All distinct, no conflicts
from honeyhive.models import Metric          # Individual metric (MetricsAPI)
from honeyhive.models.generated import Metrics  # Generated (wrong structure)
from honeyhive.experiments.models import AggregatedMetrics  # Experiment results
```

### Semantic Clarity
- **`Metric`**: Individual metric definition (threshold, type, etc.)
- **`Metrics`**: Generated model (incorrect structure, from OpenAPI)
- **`AggregatedMetrics`**: Backend-computed aggregated metrics for experiment runs

---

## Benefits of New Name

1. ✅ **No Conflicts**: Distinct from existing `Metrics` and `Metric`
2. ✅ **Clear Purpose**: "Aggregated" indicates backend computation
3. ✅ **Self-Documenting**: Obvious what this model contains
4. ✅ **Namespace Clean**: Easy to reason about imports
5. ✅ **Future-Proof**: Won't conflict with future metrics-related additions

---

**Status**: ✅ RESOLVED  
**Updated By**: AI Assistant (based on user feedback)  
**All Spec Files**: Updated with new naming

