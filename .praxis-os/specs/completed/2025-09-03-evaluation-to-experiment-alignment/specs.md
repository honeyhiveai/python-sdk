# Technical Specifications - Evaluation to Experiment Framework Alignment

**Date**: 2025-09-04  
**Last Updated**: 2025-10-02 (v2.0)  
**Status**: Technical Specification - Implementation Ready  
**Priority**: High  
**Branch**: complete-refactor  
**Version**: 2.0

> **Version 2.0 Update**: Comprehensive specification update based on backend code analysis, tracer architecture validation, and generated models review. See `CHANGELOG.md` for detailed evolution from v1.0 → v2.0.

## Architecture Changes

This specification defines the comprehensive technical changes required to align the current HoneyHive Python SDK evaluation implementation with the official HoneyHive experiment framework, ensuring full backward compatibility while leveraging backend services for aggregation and comparison.

## Problem Statement

The current SDK implementation uses outdated terminology and lacks key functionality required by the official HoneyHive experiment framework:

1. **Terminology Mismatch**: Uses "evaluation" instead of "experiment" terminology
2. **Incomplete Metadata Linking**: Missing automatic propagation of run_id, dataset_id, datapoint_id, source
3. **Manual Aggregation**: SDK was computing statistics client-side instead of using backend endpoints
4. **External Dataset Support**: Missing EXT- prefix transformation logic
5. **Limited Results Management**: No integration with backend result/comparison endpoints
6. **Tracer Integration**: Not leveraging tracer's built-in experiment metadata functionality

## Current State Analysis

### ✅ What's Working (Main Branch)
- Metadata structure with run_id, dataset_id, datapoint_id, source
- Basic evaluator framework with decorators
- Multi-threading with ThreadPoolExecutor
- EXT- prefix generation for external datasets
- evaluator execution and aggregation

### ❌ What's Missing (Complete-Refactor Branch)
- Proper tracer integration with is_evaluation=True
- Backend result endpoint integration
- Backend comparison endpoint integration
- Generated models usage (85% coverage available)
- EXT- prefix transformation for backend compatibility

### 🔄 What Needs Porting
- Evaluator framework from main → complete-refactor
- Metadata structure (run_id, dataset_id, datapoint_id, source)
- External dataset ID generation logic
- Multi-threading pattern (but improved with tracer multi-instance)

## Architecture Implementation

### 1. Module Structure Changes

#### Current Architecture
```
src/honeyhive/
├── evaluation/
│   ├── __init__.py           # Current evaluation exports
│   └── evaluators.py         # Core evaluation functionality
└── api/
    └── evaluations.py        # Evaluation API client
```

#### New Architecture (v2.0)
```
src/honeyhive/
├── experiments/              # NEW: Primary experiment module
│   ├── __init__.py          # Experiment exports + backward compat aliases
│   ├── core.py              # run_experiment() with tracer multi-instance
│   ├── models.py            # Extended models (Metrics fix, Status enum)
│   ├── utils.py             # EXT- prefix generation
│   ├── results.py           # get_run_result(), compare_runs() (backend)
│   └── evaluators.py        # Ported from main (enhanced)
├── evaluation/              # MAINTAINED: Backward compatibility
│   ├── __init__.py          # Imports from experiments/ with warnings
│   └── evaluators.py        # Deprecated, imports from experiments/
└── api/
    ├── experiments.py       # Experiment API (if needed)
    └── evaluations.py       # MAINTAINED: Already exists
```

### 2. Core Data Model Changes (v2.0 Updated)

#### Generated Models Usage (85% Coverage)
```python
# src/honeyhive/experiments/__init__.py
from honeyhive.models.generated import (
    EvaluationRun,                    # ✅ Use as-is
    CreateRunRequest,                 # ⚠️ event_ids incorrectly required
    CreateRunResponse,                # ✅ Use as-is (maps "evaluation" field)
    ExperimentResultResponse,         # ⚠️ Metrics structure needs fix
    Detail,                           # ✅ Use as-is
    Datapoint1,                       # ✅ Use as-is
    Metric1,                          # ✅ Use as-is
    Status,                           # ⚠️ Missing: running, failed, cancelled
)

# Type aliases for experiment terminology
ExperimentRun = EvaluationRun
```

#### Extended Models for Remaining 15%
```python
# src/honeyhive/experiments/models.py
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

# Extended Status enum (missing from generated)
class ExperimentRunStatus(str, Enum):
    """Extended status enum with all backend values."""
    PENDING = "pending"
    COMPLETED = "completed"
    RUNNING = "running"         # Missing from generated
    FAILED = "failed"           # Missing from generated
    CANCELLED = "cancelled"     # Missing from generated

# Fixed AggregatedMetrics model (generated Metrics has wrong structure)
class AggregatedMetrics(BaseModel):
    """
    Aggregated metrics model for experiment results with dynamic metric keys.
    
    This is distinct from the generated 'Metrics' model which has incorrect structure.
    
    Backend returns:
    {
      "aggregation_function": "average",
      "<metric_name>": {  # Dynamic keys!
        "metric_name": "...",
        "metric_type": "...",
        "aggregate": 0.85,
        "values": [...],
        ...
      }
    }
    """
    aggregation_function: Optional[str] = None
    
    # Allow extra fields for dynamic metric keys
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

# Experiment result summary (for frontend display)
class ExperimentResultSummary(BaseModel):
    """Aggregated experiment result from backend."""
    run_id: str
    status: str
    success: bool
    passed: List[str]
    failed: List[str]
    metrics: AggregatedMetrics
    datapoints: List[Any]  # List of Datapoint1 from generated

# Run comparison result (from backend)
class RunComparisonResult(BaseModel):
    """Comparison between two experiment runs."""
    new_run_id: str
    old_run_id: str
    common_datapoints: int
    new_only_datapoints: int
    old_only_datapoints: int
    metric_deltas: Dict[str, Any]  # Metric name -> delta info
```

#### Minimal Context Class
```python
# src/honeyhive/experiments/core.py
from typing import Optional, Dict, Any

class ExperimentContext:
    """
    Lightweight experiment context for metadata linking.
    
    NOTE: This is NOT a replacement for tracer config. This is just
    a convenience class for organizing experiment metadata.
    """
    
    def __init__(
        self, 
        run_id: str, 
        dataset_id: str, 
        project: str, 
        source: str = "evaluation",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.run_id = run_id
        self.dataset_id = dataset_id
        self.project = project
        self.source = source
        self.metadata = metadata or {}
    
    def to_tracer_config(self, datapoint_id: str) -> Dict[str, Any]:
        """
        Convert to tracer initialization config.
        
        This returns kwargs for HoneyHiveTracer(...) initialization.
        """
        return {
            "project": self.project,
            "is_evaluation": True,
            "run_id": self.run_id,
            "dataset_id": self.dataset_id,
            "datapoint_id": datapoint_id,
            "source": self.source,
        }
```

### 3. External Dataset Support (v2.0 Updated)

#### EXT- Prefix Generation
```python
# src/honeyhive/experiments/utils.py
import hashlib
import json
from typing import List, Dict, Any, Tuple, Optional

def generate_external_dataset_id(
    datapoints: List[Dict[str, Any]],
    custom_id: Optional[str] = None
) -> str:
    """
    Generate EXT- prefixed dataset ID.
    
    Args:
        datapoints: List of datapoint dictionaries
        custom_id: Optional custom ID (will be prefixed with EXT-)
    
    Returns:
        Dataset ID with EXT- prefix
    """
    if custom_id:
        # Ensure custom ID has EXT- prefix
        if not custom_id.startswith("EXT-"):
            return f"EXT-{custom_id}"
        return custom_id
    
    # Generate hash-based ID
    content = json.dumps(datapoints, sort_keys=True)
    hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
    return f"EXT-{hash_value}"

def generate_external_datapoint_id(
    datapoint: Dict[str, Any],
    index: int,
    custom_id: Optional[str] = None
) -> str:
    """
    Generate EXT- prefixed datapoint ID.
    
    Args:
        datapoint: Datapoint dictionary
        index: Index in dataset (for stable ordering)
        custom_id: Optional custom ID (will be prefixed with EXT-)
    
    Returns:
        Datapoint ID with EXT- prefix
    """
    if custom_id:
        if not custom_id.startswith("EXT-"):
            return f"EXT-{custom_id}"
        return custom_id
    
    # Generate hash-based ID
    content = json.dumps(datapoint, sort_keys=True)
    hash_value = hashlib.sha256(f"{content}{index}".encode()).hexdigest()[:16]
    return f"EXT-{hash_value}"

def prepare_external_dataset(
    datapoints: List[Dict[str, Any]],
    custom_dataset_id: Optional[str] = None
) -> Tuple[str, List[str]]:
    """
    Prepare external dataset with EXT- IDs.
    
    Args:
        datapoints: List of datapoint dictionaries
        custom_dataset_id: Optional custom dataset ID
    
    Returns:
        Tuple of (dataset_id, datapoint_ids)
    """
    dataset_id = generate_external_dataset_id(datapoints, custom_dataset_id)
    
    datapoint_ids = []
    for idx, dp in enumerate(datapoints):
        # Check if datapoint already has an ID
        custom_dp_id = dp.get("id") or dp.get("datapoint_id")
        dp_id = generate_external_datapoint_id(dp, idx, custom_dp_id)
        datapoint_ids.append(dp_id)
    
    return dataset_id, datapoint_ids
```

#### Backend Transformation (v2.0 NEW)
```python
# IMPORTANT: Backend expects EXT- datasets in metadata, NOT dataset_id

def prepare_run_request_data(
    run_id: str,
    name: str,
    project: str,
    dataset_id: str,
    event_ids: Optional[List[str]] = None,
    configuration: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Prepare run request data with EXT- transformation.
    
    Backend Logic:
    - If dataset_id starts with "EXT-":
      - Move to metadata.offline_dataset_id
      - Set dataset_id = None (prevents FK constraint error)
    - Otherwise, use dataset_id normally
    """
    request_data = {
        "project": project,
        "name": name,
        "event_ids": event_ids or [],  # Backend accepts empty list
        "configuration": configuration or {},
        "metadata": metadata or {},
        "status": "pending",
    }
    
    # Handle EXT- prefix transformation
    if dataset_id and dataset_id.startswith("EXT-"):
        # Store external dataset ID in metadata
        request_data["metadata"]["offline_dataset_id"] = dataset_id
        # Clear dataset_id to avoid FK constraint
        request_data["dataset_id"] = None
    else:
        request_data["dataset_id"] = dataset_id
    
    return request_data
```

### 4. Tracer Integration (v2.0 CRITICAL)

#### Multi-Instance Pattern
```python
# src/honeyhive/experiments/core.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Dict, Any
from honeyhive.tracer import HoneyHiveTracer

def run_experiment(
    function: Callable,
    dataset: List[Dict[str, Any]],
    experiment_context: ExperimentContext,
    api_key: str,
    max_workers: int = 10,
) -> List[Dict[str, Any]]:
    """
    Run experiment with tracer multi-instance pattern.
    
    CRITICAL: Each datapoint gets its OWN tracer instance for isolation.
    This prevents:
    - Metadata contamination between datapoints
    - Race conditions in concurrent execution
    - Session ID collisions
    """
    
    def process_datapoint(datapoint: Dict[str, Any], datapoint_id: str) -> Dict[str, Any]:
        """Process single datapoint with isolated tracer."""
        
        # Create tracer config for this datapoint
        tracer_config = experiment_context.to_tracer_config(datapoint_id)
        
        # Create NEW tracer instance for this datapoint
        tracer = HoneyHiveTracer(
            api_key=api_key,
            **tracer_config
        )
        
        try:
            # Execute function with tracer active
            # Tracer automatically adds all experiment metadata to spans!
            inputs = datapoint.get("inputs", {})
            ground_truth = datapoint.get("ground_truth")
            
            outputs = function(inputs, ground_truth)
            
            return {
                "datapoint_id": datapoint_id,
                "inputs": inputs,
                "outputs": outputs,
                "ground_truth": ground_truth,
                "status": "success",
            }
        except Exception as e:
            return {
                "datapoint_id": datapoint_id,
                "status": "failed",
                "error": str(e),
            }
        finally:
            # CRITICAL: Flush tracer to ensure all spans sent
            tracer.flush()
    
    # Use ThreadPoolExecutor for I/O-bound concurrent execution
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all datapoint executions
        future_to_datapoint = {}
        for idx, datapoint in enumerate(dataset):
            datapoint_id = datapoint.get("id") or f"dp-{idx}"
            future = executor.submit(process_datapoint, datapoint, datapoint_id)
            future_to_datapoint[future] = datapoint_id
        
        # Collect results as they complete
        for future in as_completed(future_to_datapoint):
            datapoint_id = future_to_datapoint[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    "datapoint_id": datapoint_id,
                    "status": "failed",
                    "error": str(e),
                })
    
    return results
```

#### Why ThreadPoolExecutor (Not Multiprocessing)
```python
# From tracer documentation analysis:

# ✅ ThreadPoolExecutor is correct for:
# 1. I/O-bound operations (API calls, LLM inference)
# 2. Tracer multi-instance isolation (each tracer independent)
# 3. Shared memory access (less overhead than multiprocessing)
# 4. Python 3.11+ (GIL improvements for I/O operations)

# ❌ Multiprocessing would be overkill because:
# 1. Experiment execution is I/O-bound, not CPU-bound
# 2. Serialization overhead for multiprocessing is significant
# 3. Tracer instances already provide isolation
# 4. Thread safety is sufficient (no shared mutable state)
```

### 5. Result Aggregation (v2.0 CRITICAL - Use Backend!)

#### Result Endpoint Integration
```python
# src/honeyhive/experiments/results.py
from typing import Optional, Dict, Any
from honeyhive.api.client import HoneyHive
from honeyhive.experiments.models import ExperimentResultSummary, RunComparisonResult

def get_run_result(
    client: HoneyHive,
    run_id: str,
    aggregate_function: str = "average"
) -> ExperimentResultSummary:
    """
    Get aggregated experiment result from backend.
    
    Backend Endpoint: GET /runs/:run_id/result?aggregate_function=<function>
    
    Backend computes:
    - Pass/fail status for each datapoint
    - Metric aggregations (average, sum, min, max)
    - Composite metrics
    - Overall run status
    
    DO NOT compute these client-side!
    
    Args:
        client: HoneyHive API client
        run_id: Experiment run ID
        aggregate_function: "average", "sum", "min", "max"
    
    Returns:
        ExperimentResultSummary with all aggregated metrics
    """
    # Use existing API client method (may need to add to evaluations.py)
    response = client.evaluations.get_run_result(
        run_id=run_id,
        aggregate_function=aggregate_function
    )
    
    return ExperimentResultSummary(
        run_id=run_id,
        status=response.status,
        success=response.success,
        passed=response.passed,
        failed=response.failed,
        metrics=AggregatedMetrics(**response.metrics.dict()),  # Use fixed model
        datapoints=response.datapoints,
    )

def get_run_metrics(
    client: HoneyHive,
    run_id: str
) -> Dict[str, Any]:
    """
    Get raw metrics for a run (without aggregation).
    
    Backend Endpoint: GET /runs/:run_id/metrics
    
    Returns:
        Raw metrics data from backend
    """
    return client.evaluations.get_run_metrics(run_id=run_id)

def compare_runs(
    client: HoneyHive,
    new_run_id: str,
    old_run_id: str,
    aggregate_function: str = "average"
) -> RunComparisonResult:
    """
    Compare two experiment runs using backend endpoint.
    
    Backend Endpoint: GET /runs/:new_run_id/compare-with/:old_run_id
    
    Backend computes:
    - Common datapoints between runs
    - Metric deltas (new - old)
    - Percent changes ((new - old) / old * 100)
    - Statistical significance (if applicable)
    
    DO NOT compute these client-side!
    
    Args:
        client: HoneyHive API client
        new_run_id: New experiment run ID
        old_run_id: Old experiment run ID
        aggregate_function: "average", "sum", "min", "max"
    
    Returns:
        RunComparisonResult with delta calculations
    """
    response = client.evaluations.compare_runs(
        new_run_id=new_run_id,
        old_run_id=old_run_id,
        aggregate_function=aggregate_function
    )
    
    return RunComparisonResult(
        new_run_id=new_run_id,
        old_run_id=old_run_id,
        common_datapoints=response.common_datapoints,
        new_only_datapoints=response.new_only_datapoints,
        old_only_datapoints=response.old_only_datapoints,
        metric_deltas=response.metric_deltas,
    )
```

#### ❌ NO Client-Side Aggregation
```python
# ❌ DELETE THIS PATTERN (from v1.0 spec):
def aggregate_experiment_results(results: List[Dict]) -> Dict:
    """DO NOT IMPLEMENT - Backend handles this!"""
    raise NotImplementedError(
        "Client-side aggregation is not supported. "
        "Use get_run_result() to retrieve backend-computed aggregates."
    )

# ✅ CORRECT PATTERN (v2.0):
# 1. Execute function against dataset with tracer
# 2. Run evaluators (they send metrics to backend via events)
# 3. Call get_run_result() to retrieve aggregated results from backend
```

### 6. Complete Evaluate Function (v2.0)

```python
# src/honeyhive/experiments/core.py
from typing import Callable, Optional, List, Dict, Any
import uuid
from honeyhive.api.client import HoneyHive
from honeyhive.experiments.utils import prepare_external_dataset, prepare_run_request_data
from honeyhive.experiments.results import get_run_result
from honeyhive.experiments.evaluators import run_evaluators
from honeyhive.experiments.models import ExperimentResultSummary

def evaluate(
    function: Callable,
    dataset: Optional[List[Dict[str, Any]]] = None,
    dataset_id: Optional[str] = None,
    evaluators: Optional[List[Callable]] = None,
    api_key: Optional[str] = None,
    project: Optional[str] = None,
    name: Optional[str] = None,
    max_workers: int = 10,
    aggregate_function: str = "average",
) -> ExperimentResultSummary:
    """
    Run experiment evaluation with backend aggregation.
    
    Workflow:
    1. Prepare dataset (external or HoneyHive)
    2. Create experiment run via API
    3. Execute function against dataset with tracer multi-instance
    4. Run evaluators (send metrics via events)
    5. Retrieve aggregated results from backend
    
    Args:
        function: User function to execute
        dataset: External dataset (list of dicts)
        dataset_id: HoneyHive dataset ID
        evaluators: List of evaluator functions
        api_key: HoneyHive API key
        project: HoneyHive project
        name: Experiment run name
        max_workers: ThreadPool size
        aggregate_function: "average", "sum", "min", "max"
    
    Returns:
        ExperimentResultSummary with backend-computed aggregates
    """
    # Initialize client
    client = HoneyHive(api_key=api_key, project=project)
    
    # Step 1: Prepare dataset
    if dataset is not None:
        # External dataset
        dataset_id, datapoint_ids = prepare_external_dataset(dataset)
        dataset_list = dataset
    elif dataset_id is not None:
        # Fetch HoneyHive dataset
        ds_response = client.datasets.get_dataset(dataset_id)
        dataset_list = [dp.dict() for dp in ds_response.datapoints]
        datapoint_ids = [dp.id for dp in ds_response.datapoints]
    else:
        raise ValueError("Provide either 'dataset' or 'dataset_id'")
    
    # Step 2: Create experiment run
    run_id = str(uuid.uuid4())
    run_data = prepare_run_request_data(
        run_id=run_id,
        name=name or f"experiment-{run_id[:8]}",
        project=client.project,
        dataset_id=dataset_id,
        event_ids=[],  # Empty initially
        configuration={
            "function": function.__name__,
            "evaluators": [e.__name__ for e in (evaluators or [])],
            "max_workers": max_workers,
        },
    )
    
    run_response = client.evaluations.create_run(**run_data)
    run_id = run_response.run_id or run_id
    
    # Step 3: Create experiment context
    context = ExperimentContext(
        run_id=run_id,
        dataset_id=dataset_id,
        project=client.project,
        source="evaluation",
    )
    
    # Step 4: Execute experiment with tracer multi-instance
    execution_results = run_experiment(
        function=function,
        dataset=dataset_list,
        experiment_context=context,
        api_key=client.api_key,
        max_workers=max_workers,
    )
    
    # Step 5: Run evaluators (if provided)
    if evaluators:
        run_evaluators(
            execution_results=execution_results,
            evaluators=evaluators,
            experiment_context=context,
            api_key=client.api_key,
            max_workers=max_workers,
        )
    
    # Step 6: Retrieve aggregated results from backend
    result_summary = get_run_result(
        client=client,
        run_id=run_id,
        aggregate_function=aggregate_function,
    )
    
    return result_summary
```

### 7. Backward Compatibility Layer

```python
# src/honeyhive/evaluation/__init__.py
"""
Backward compatibility layer for evaluation module.

This module maintains 100% backward compatibility with existing code
while redirecting to the new experiments module.
"""
import warnings
from typing import TYPE_CHECKING

# Import everything from experiments module
from honeyhive.experiments import (
    evaluate as _evaluate,
    run_experiment as _run_experiment,
    ExperimentContext as _ExperimentContext,
    get_run_result as _get_run_result,
    compare_runs as _compare_runs,
)

# Import generated models directly
from honeyhive.models.generated import (
    EvaluationRun as _EvaluationRun,
    ExperimentResultResponse as _ExperimentResultResponse,
)

# Deprecated aliases with warnings
def evaluate(*args, **kwargs):
    """Backward compatibility wrapper for evaluate()."""
    warnings.warn(
        "honeyhive.evaluation.evaluate is deprecated. "
        "Use honeyhive.experiments.evaluate instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _evaluate(*args, **kwargs)

class EvaluationContext(_ExperimentContext):
    """Backward compatibility alias for ExperimentContext."""
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "EvaluationContext is deprecated. "
            "Use ExperimentContext instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)

# Direct aliases (no warnings for model imports)
EvaluationRun = _EvaluationRun
EvaluationResult = _ExperimentResultResponse

__all__ = [
    "evaluate",
    "EvaluationContext",
    "EvaluationRun",
    "EvaluationResult",
    # ... all other exports
]
```

### 8. API Client Extensions

```python
# src/honeyhive/api/evaluations.py (extend existing)

class EvaluationsAPI:
    """Evaluation runs API client (already exists)."""
    
    # ... existing methods ...
    
    # Add result endpoints (v2.0)
    def get_run_result(
        self,
        run_id: str,
        aggregate_function: str = "average"
    ) -> Dict[str, Any]:
        """
        Get aggregated result for a run.
        
        Backend: GET /runs/:run_id/result?aggregate_function=<function>
        """
        return self._client.get(
            f"/runs/{run_id}/result",
            params={"aggregate_function": aggregate_function}
        )
    
    def get_run_metrics(self, run_id: str) -> Dict[str, Any]:
        """
        Get raw metrics for a run.
        
        Backend: GET /runs/:run_id/metrics
        """
        return self._client.get(f"/runs/{run_id}/metrics")
    
    def compare_runs(
        self,
        new_run_id: str,
        old_run_id: str,
        aggregate_function: str = "average"
    ) -> Dict[str, Any]:
        """
        Compare two runs.
        
        Backend: GET /runs/:new_run_id/compare-with/:old_run_id
        """
        return self._client.get(
            f"/runs/{new_run_id}/compare-with/{old_run_id}",
            params={"aggregate_function": aggregate_function}
        )
```

## Implementation Phases

### Phase 1: Core Infrastructure (Day 1 Morning)
1. ✅ Create `experiments/models.py` with extended models
2. ✅ Create `experiments/utils.py` with EXT- prefix logic
3. ✅ Create `experiments/results.py` with backend endpoint functions
4. ✅ Create `experiments/__init__.py` with imports and aliases

### Phase 2: Tracer Integration (Day 1 Afternoon)
1. ✅ Create `experiments/core.py` with run_experiment()
2. ✅ Implement tracer multi-instance pattern
3. ✅ Test concurrent execution with isolated tracers
4. ✅ Validate metadata propagation

### Phase 3: Evaluator Framework (Day 1 Evening)
1. ✅ Port evaluators from main branch
2. ✅ Adapt to tracer multi-instance architecture
3. ✅ Test evaluator execution
4. ✅ Validate metrics sent to backend

### Phase 4: Integration (Day 2 Morning)
1. ✅ Implement complete evaluate() function
2. ✅ Integrate result endpoint calls
3. ✅ Test end-to-end workflow
4. ✅ Validate EXT- prefix transformation

### Phase 5: Backward Compatibility (Day 2 Afternoon)
1. ✅ Create evaluation/__init__.py wrapper
2. ✅ Add deprecation warnings
3. ✅ Test all old imports work
4. ✅ Validate no breaking changes

### Phase 6: Testing & Documentation (Day 2 Evening)
1. ✅ Write comprehensive tests
2. ✅ Update documentation
3. ✅ Create migration guide
4. ✅ Prepare release candidate

## Testing Requirements

### Unit Tests
- ✅ EXT- prefix generation
- ✅ External dataset preparation
- ✅ Tracer config generation
- ✅ Model extensions (Metrics, Status)

### Integration Tests
- ✅ Tracer multi-instance isolation
- ✅ Backend result endpoint integration
- ✅ Backend comparison endpoint integration
- ✅ EXT- prefix transformation

### End-to-End Tests
- ✅ Complete evaluate() workflow
- ✅ External dataset evaluation
- ✅ HoneyHive dataset evaluation
- ✅ Evaluator execution
- ✅ Result aggregation
- ✅ Run comparison

### Backward Compatibility Tests
- ✅ All old imports work
- ✅ Deprecation warnings logged
- ✅ No functional changes
- ✅ Existing tests pass

## Standards Compliance

### Agent OS Standards
- ✅ Generated models usage (85% coverage)
- ✅ Backward compatibility maintained
- ✅ Comprehensive testing (>90%)
- ✅ Documentation complete

### HoneyHive Standards
- ✅ Backend aggregation used (not client-side)
- ✅ EXT- prefix transformation implemented
- ✅ Tracer multi-instance pattern followed
- ✅ Metadata propagation automatic

---

**Document Version**: 2.0  
**Last Updated**: 2025-10-02  
**Next Review**: After Phase 1 implementation  
**Analysis References**: 
- BACKEND_VALIDATION_ANALYSIS.md
- TRACER_INTEGRATION_ANALYSIS.md
- RESULT_ENDPOINTS_ANALYSIS.md
- GENERATED_MODELS_VALIDATION.md
- CHANGELOG.md

