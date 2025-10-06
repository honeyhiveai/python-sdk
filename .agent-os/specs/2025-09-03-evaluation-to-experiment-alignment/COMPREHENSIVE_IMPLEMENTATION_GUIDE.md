# Comprehensive Implementation Guide
**Aligning SDK with Official HoneyHive Docs Specification**

**Date**: October 2, 2025  
**Branch**: complete-refactor  
**Source**: [HoneyHive Manual Evaluation Docs](https://docs.honeyhive.ai/sdk-reference/manual-eval-instrumentation)

---

## 🎯 Three-Source Analysis

### Source 1: Main Branch (Current Working Implementation)
**Status**: ✅ Functional but non-compliant
- Has working evaluation module
- Uses custom dataclasses ❌
- Has proper multi-threading ✅
- Missing experiment terminology ❌

### Source 2: Complete-Refactor Branch (Target Branch)
**Status**: ⚠️ Partially refactored
- Improved tracer architecture ✅
- Better configuration system ✅
- **NO experiments module yet** ❌
- **NO evaluation module**  ❌

### Source 3: Official HoneyHive Docs (Source of Truth)
**Status**: 📚 Authoritative specification
- Defines exact API flow
- Specifies required metadata fields
- Two paths: HoneyHive datasets vs. External datasets

---

## 📚 Understanding the Official Docs Specification

Based on the [HoneyHive documentation](https://docs.honeyhive.ai/sdk-reference/manual-eval-instrumentation), here's what the platform **actually expects**:

### Core API Flow

#### Path 1: External Datasets (User-Managed Data)
```
1. POST /runs          → Create run (no dataset_id in request)
                         Request: { name, project, status, metadata }
                         
2. Fetch Data          → From your own source
                         
3. POST /session/start → Start session
                         metadata.run_id = <run_id_from_step_1>
                         
4. Log Events          → With session_id from step 3
                         
5. PUT /runs           → Update run to completed
                         event_ids = [list of session_ids]
                         status = "completed"
```

#### Path 2: HoneyHive Datasets (Platform-Managed Data)
```
1. GET /datasets       → Fetch dataset → get dataset_id
                         
2. POST /runs          → Create run WITH dataset_id
                         Request: { name, project, dataset_id, status, metadata }
                         
3. GET /datapoint/{id} → Fetch specific datapoints
                         
4. POST /session/start → Start session
                         metadata.run_id = <run_id>
                         metadata.datapoint_id = <datapoint_id>
                         
5. Log Events          → With session_id
                         
6. PUT /runs           → Update run to completed
                         event_ids = [list of session_ids]
                         status = "completed"
```

---

## 🔑 Critical Insights from Official Docs

### 1. **Metadata Requirements Are PATH-SPECIFIC**

**For External Datasets:**
```python
# Session metadata MUST include:
metadata = {
    "run_id": "<evaluation_run_id>"
    # That's it! No dataset_id or datapoint_id required
}
```

**For HoneyHive Datasets:**
```python
# Session metadata MUST include:
metadata = {
    "run_id": "<evaluation_run_id>",
    "datapoint_id": "<datapoint_id>"  # From GET /datapoint/{id}
    # Note: dataset_id is in the run, not session metadata
}
```

### 2. **The `source` Field Is NOT Mentioned**

**Important Discovery**: The official docs **do NOT mention** `source="evaluation"` in session metadata.

However, based on the tracer implementation in complete-refactor:
```python
# src/honeyhive/tracer/core/base.py (Line 255)
self.source = config.get("source")
```

The `source` field appears to be a tracer-level configuration, not session metadata.

### 3. **`dataset_id` Location Matters**

```python
# ✅ CORRECT per docs
POST /runs with { dataset_id: "..." }  # In run creation

# ❌ WRONG (current main branch does this)
POST /session/start with metadata.dataset_id  # Not documented
```

The `dataset_id` goes in the **run creation** request, NOT in session metadata (except implicitly through the run_id link).

### 4. **Session IDs = Event IDs**

```python
# When completing the run:
PUT /runs/{run_id} with {
    event_ids: [session_id_1, session_id_2, ...]  # List of session IDs
    status: "completed"
}
```

---

## 🏗️ Architecture That Matches All Three Sources

### Target Architecture (Combines Best of All Three)

```
src/honeyhive/
├── experiments/                    # NEW - Primary module
│   ├── __init__.py                # Public API + backward compat
│   ├── core.py                    # Main evaluate() function
│   ├── context.py                 # ExperimentContext class
│   ├── dataset.py                 # External dataset handling
│   ├── results.py                 # Result aggregation
│   └── evaluators.py              # Evaluator framework (from main)
│
├── evaluation/                    # MAINTAINED - Compatibility layer
│   ├── __init__.py                # Imports from experiments/ with deprecation
│   └── evaluators.py              # Compatibility re-exports
│
├── tracer/                        # PRESERVED - From complete-refactor
│   └── ... (current refactored tracer)
│
├── api/                           # ENHANCED
│   ├── evaluations.py             # Already good! (from complete-refactor)
│   └── ... (other APIs)
│
└── models/
    ├── generated.py               # Official generated models
    └── ... (other models)
```

---

## 📋 Detailed Implementation Plan

### Phase 1: Create Experiments Module Structure

#### Step 1.1: Create `src/honeyhive/experiments/__init__.py`

```python
"""HoneyHive Experiments Module - Official Implementation.

This module provides experiment execution capabilities aligned with the
official HoneyHive platform. It supports both HoneyHive-managed datasets
and external (user-managed) datasets.

Official Documentation:
    https://docs.honeyhive.ai/sdk-reference/manual-eval-instrumentation
"""

from typing import Any, Callable, Dict, List, Optional

# Import generated models (NO custom dataclasses)
from ..models.generated import (
    CreateRunRequest,
    CreateRunResponse,
    UpdateRunRequest,
    UpdateRunResponse,
    GetRunResponse,
    # Note: There's no ExperimentResultResponse in generated models yet
    # We'll need to check what's actually available
)

# Import from submodules
from .context import ExperimentContext
from .core import evaluate, run_experiment
from .dataset import create_external_dataset, validate_dataset
from .evaluators import evaluator, aevaluator  # Re-export from main

# Type aliases for experiment terminology
ExperimentRun = CreateRunResponse  # Use generated model
# ExperimentResult = will use generated model when available

__all__ = [
    # Main functions
    "evaluate",
    "run_experiment",
    
    # Context and dataset management
    "ExperimentContext",
    "create_external_dataset",
    "validate_dataset",
    
    # Evaluators
    "evaluator",
    "aevaluator",
    
    # Type aliases
    "ExperimentRun",
]
```

#### Step 1.2: Create `src/honeyhive/experiments/context.py`

```python
"""Experiment context management for metadata linking."""

from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class ExperimentContext:
    """Lightweight context for experiment metadata linking.
    
    This class manages the metadata required for linking events to experiment
    runs according to the official HoneyHive documentation.
    
    Official Documentation:
        https://docs.honeyhive.ai/sdk-reference/manual-eval-instrumentation
    
    Attributes:
        run_id: Evaluation run identifier (from POST /runs)
        project: HoneyHive project name
        dataset_id: Dataset identifier (optional, for HH datasets)
        metadata: Additional custom metadata
        use_honeyhive_dataset: Whether using HoneyHive-managed dataset
    """
    
    run_id: str
    project: str
    dataset_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    use_honeyhive_dataset: bool = False
    
    def to_session_metadata(self, datapoint_id: Optional[str] = None) -> Dict[str, Any]:
        """Convert to session metadata format per official docs.
        
        Per the official documentation:
        - For external datasets: Only run_id is required
        - For HoneyHive datasets: run_id + datapoint_id are required
        - dataset_id goes in run creation, NOT session metadata
        
        Args:
            datapoint_id: Datapoint identifier (required for HH datasets)
            
        Returns:
            Dictionary of session metadata
            
        Raises:
            ValueError: If datapoint_id is None for HoneyHive datasets
        """
        session_metadata = {
            "run_id": self.run_id,
        }
        
        # Add datapoint_id for HoneyHive datasets only
        if self.use_honeyhive_dataset:
            if datapoint_id is None:
                raise ValueError(
                    "datapoint_id is required for HoneyHive-managed datasets"
                )
            session_metadata["datapoint_id"] = datapoint_id
        
        # Add custom metadata if provided
        if self.metadata:
            session_metadata.update(self.metadata)
        
        return session_metadata
    
    def to_tracer_config(self, datapoint_id: Optional[str] = None) -> Dict[str, Any]:
        """Convert to tracer configuration format.
        
        This provides tracer-level configuration for the refactored tracer
        in complete-refactor branch.
        
        Args:
            datapoint_id: Datapoint identifier (optional)
            
        Returns:
            Dictionary of tracer configuration
        """
        config = {
            "project": self.project,
            "source": "evaluation",  # Tracer-level field, not session metadata
            "is_evaluation": True,
            "run_id": self.run_id,
        }
        
        if self.dataset_id:
            config["dataset_id"] = self.dataset_id
        
        if datapoint_id:
            config["datapoint_id"] = datapoint_id
        
        return config
```

#### Step 1.3: Create `src/honeyhive/experiments/core.py`

```python
"""Core experiment execution following official HoneyHive documentation.

This module implements the exact API flow described in:
https://docs.honeyhive.ai/sdk-reference/manual-eval-instrumentation
"""

import os
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List, Optional
import logging

from ..api.client import HoneyHive
from ..models.generated import CreateRunRequest, UpdateRunRequest
from ..tracer import HoneyHiveTracer
from .context import ExperimentContext
from .dataset import create_external_dataset, validate_dataset
from .evaluators import evaluate_with_evaluators

logger = logging.getLogger(__name__)


def evaluate(
    function: Callable,
    *,
    # API credentials
    api_key: Optional[str] = None,
    project: Optional[str] = None,
    
    # Run configuration
    name: Optional[str] = None,
    
    # Dataset configuration (one of these required)
    dataset_id: Optional[str] = None,  # For HoneyHive datasets
    dataset: Optional[List[Dict[str, Any]]] = None,  # For external datasets
    
    # Evaluation configuration
    evaluators: Optional[List[Any]] = None,
    
    # Execution configuration
    max_workers: int = 10,
    run_concurrently: bool = True,
    
    # Optional overrides
    server_url: Optional[str] = None,
    verbose: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute a function against a dataset with evaluation.
    
    This function implements the official HoneyHive evaluation workflow as
    documented at: https://docs.honeyhive.ai/sdk-reference/manual-eval-instrumentation
    
    It supports two paths:
    1. **External Datasets**: User-managed data (pass `dataset`)
    2. **HoneyHive Datasets**: Platform-managed data (pass `dataset_id`)
    
    Args:
        function: User function to execute against each datapoint.
                 Signature: fn(inputs: Dict) -> Any or fn(inputs: Dict, ground_truth: Dict) -> Any
        api_key: HoneyHive API key (defaults to HH_API_KEY env var)
        project: HoneyHive project name (defaults to HH_PROJECT env var)
        name: Experiment run name
        dataset_id: HoneyHive dataset identifier (for Path 2)
        dataset: List of datapoints as dicts (for Path 1)
        evaluators: List of evaluator functions
        max_workers: Number of parallel workers
        run_concurrently: Whether to run in parallel
        server_url: HoneyHive server URL override
        verbose: Enable verbose logging
        metadata: Additional metadata for the run
    
    Returns:
        Dictionary containing:
            - run_id: Evaluation run identifier
            - session_ids: List of session IDs
            - results: List of individual results
            - stats: Execution statistics
            
    Raises:
        ValueError: If neither dataset nor dataset_id provided
        ValueError: If both dataset and dataset_id provided
        RuntimeError: If API calls fail
        
    Example - External Dataset (Path 1):
        >>> results = evaluate(
        ...     function=my_llm_pipeline,
        ...     dataset=[
        ...         {"inputs": {"query": "..."}, "ground_truth": "..."},
        ...         # ...
        ...     ],
        ...     evaluators=[accuracy, relevance],
        ...     max_workers=8
        ... )
        
    Example - HoneyHive Dataset (Path 2):
        >>> results = evaluate(
        ...     function=my_llm_pipeline,
        ...     dataset_id="ds-123abc",
        ...     evaluators=[accuracy, relevance],
        ...     max_workers=8
        ... )
    """
    
    # Validate inputs
    if dataset is None and dataset_id is None:
        raise ValueError("Either 'dataset' or 'dataset_id' must be provided")
    
    if dataset is not None and dataset_id is not None:
        raise ValueError("Cannot provide both 'dataset' and 'dataset_id'")
    
    # Get credentials
    api_key = api_key or os.environ.get("HH_API_KEY")
    project = project or os.environ.get("HH_PROJECT")
    
    if not api_key or not project:
        raise ValueError("api_key and project must be provided or set in environment")
    
    # Initialize API client
    client = HoneyHive(
        api_key=api_key,
        server_url=server_url,
        verbose=verbose
    )
    
    # Determine which path we're using
    use_honeyhive_dataset = dataset_id is not None
    
    #==========================================================================
    # STEP 1: Prepare Dataset
    #==========================================================================
    
    if use_honeyhive_dataset:
        # Path 2: HoneyHive Dataset
        # Step 1: GET /datasets (fetch dataset)
        if verbose:
            logger.info(f"Fetching HoneyHive dataset: {dataset_id}")
        
        dataset_response = client.datasets.get_dataset(
            dataset_id=dataset_id,
            project=project
        )
        
        if not dataset_response or not hasattr(dataset_response, 'datapoints'):
            raise ValueError(f"Dataset {dataset_id} not found or has no datapoints")
        
        # Extract datapoints for execution
        datapoint_ids = dataset_response.datapoints  # List of IDs
        num_datapoints = len(datapoint_ids)
        
    else:
        # Path 1: External Dataset
        # Validate dataset format
        if not isinstance(dataset, list):
            raise ValueError("dataset must be a list of dictionaries")
        
        if not all(isinstance(item, dict) for item in dataset):
            raise ValueError("All items in dataset must be dictionaries")
        
        # Create external dataset with EXT- prefix
        if verbose:
            logger.info(f"Creating external dataset with {len(dataset)} datapoints")
        
        dataset_id, datapoint_ids = create_external_dataset(
            datapoints=dataset,
            project=project
        )
        
        num_datapoints = len(dataset)
    
    #==========================================================================
    # STEP 2: Create Evaluation Run (POST /runs)
    #==========================================================================
    
    if verbose:
        logger.info(f"Creating evaluation run for {num_datapoints} datapoints")
    
    # Prepare run request per official docs
    run_request = CreateRunRequest(
        project=project,
        name=name or f"evaluation-{uuid.uuid4().hex[:8]}",
        dataset_id=dataset_id,  # ✅ Per docs: dataset_id goes here
        status="running",
        metadata=metadata or {}
    )
    
    # Create run via API
    run_response = client.evaluations.create_run(run_request)
    
    if not run_response or not hasattr(run_response, 'run_id'):
        raise RuntimeError("Failed to create evaluation run")
    
    run_id = str(run_response.run_id)
    
    if verbose:
        logger.info(f"Created evaluation run: {run_id}")
    
    # Create experiment context
    context = ExperimentContext(
        run_id=run_id,
        project=project,
        dataset_id=dataset_id,
        metadata=metadata,
        use_honeyhive_dataset=use_honeyhive_dataset
    )
    
    #==========================================================================
    # STEP 3: Execute Function Against Dataset
    #==========================================================================
    
    session_ids = []
    results = []
    
    def execute_single_datapoint(idx: int) -> Dict[str, Any]:
        """Execute function for a single datapoint following official docs."""
        
        # Get datapoint data
        if use_honeyhive_dataset:
            # Path 2: Fetch datapoint via API (GET /datapoint/{id})
            datapoint_id = str(datapoint_ids[idx])
            
            datapoint_response = client.datapoints.get_datapoint(id=datapoint_id)
            
            if not datapoint_response:
                raise ValueError(f"Datapoint {datapoint_id} not found")
            
            inputs = datapoint_response.inputs or {}
            ground_truth = datapoint_response.ground_truth or {}
            
        else:
            # Path 1: Use external dataset
            datapoint_id = datapoint_ids[idx]
            datapoint_data = dataset[idx]
            
            inputs = datapoint_data.get("inputs", {})
            ground_truth = datapoint_data.get("ground_truth", {})
        
        # Get session metadata per official docs
        session_metadata = context.to_session_metadata(
            datapoint_id=datapoint_id if use_honeyhive_dataset else None
        )
        
        # Initialize tracer with proper configuration
        tracer_config = context.to_tracer_config(datapoint_id=datapoint_id)
        
        tracer = HoneyHiveTracer(
            api_key=api_key,
            **tracer_config,
            verbose=verbose,
            server_url=server_url,
            # Additional session metadata per docs
            metadata=session_metadata
        )
        
        session_id = tracer.session_id
        
        try:
            # Execute user function
            if ground_truth:
                outputs = function(inputs, ground_truth)
            else:
                outputs = function(inputs)
            
            # Run evaluators if provided
            evaluator_results = []
            if evaluators:
                evaluator_results = evaluate_with_evaluators(
                    evaluators=evaluators,
                    inputs=inputs,
                    outputs=outputs,
                    ground_truth=ground_truth,
                    context=context
                )
            
            # Flush tracer to ensure events are sent
            tracer.flush()
            
            return {
                "session_id": session_id,
                "datapoint_id": datapoint_id,
                "inputs": inputs,
                "outputs": outputs,
                "ground_truth": ground_truth,
                "evaluator_results": evaluator_results,
                "status": "success",
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error executing datapoint {datapoint_id}: {e}")
            
            return {
                "session_id": session_id,
                "datapoint_id": datapoint_id,
                "inputs": inputs,
                "outputs": None,
                "ground_truth": ground_truth,
                "evaluator_results": None,
                "status": "failed",
                "error": str(e)
            }
    
    # Execute with optional concurrency
    if run_concurrently and max_workers > 1:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(execute_single_datapoint, i)
                for i in range(num_datapoints)
            ]
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    session_ids.append(result["session_id"])
                except Exception as e:
                    logger.error(f"Future execution failed: {e}")
    else:
        # Sequential execution
        for i in range(num_datapoints):
            result = execute_single_datapoint(i)
            results.append(result)
            session_ids.append(result["session_id"])
    
    #==========================================================================
    # STEP 4: Complete Evaluation Run (PUT /runs)
    #==========================================================================
    
    if verbose:
        logger.info(f"Completing evaluation run with {len(session_ids)} sessions")
    
    # Update run to completed per official docs
    update_request = UpdateRunRequest(
        event_ids=session_ids,  # ✅ Per docs: session IDs go here as event_ids
        status="completed"
    )
    
    try:
        client.evaluations.update_run(
            run_id=run_id,
            request=update_request
        )
    except Exception as e:
        logger.warning(f"Failed to mark run as completed: {e}")
    
    # Return results
    return {
        "run_id": run_id,
        "session_ids": session_ids,
        "results": results,
        "stats": {
            "total": len(results),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "failed")
        }
    }


# Alias for backward compatibility
run_experiment = evaluate
```

---

## 📊 Key Differences from Main Branch

### 1. **Metadata Structure (CRITICAL)**

**Main Branch (WRONG per docs):**
```python
metadata = {
    "run_id": run_id,
    "dataset_id": dataset_id,        # ❌ Not per docs
    "datapoint_id": datapoint_id,
    # Missing: source field
}
```

**Official Docs (CORRECT):**
```python
# For external datasets:
metadata = {
    "run_id": run_id
    # That's ALL
}

# For HoneyHive datasets:
metadata = {
    "run_id": run_id,
    "datapoint_id": datapoint_id
    # dataset_id goes in run creation, not here
}
```

### 2. **`source` Field Location**

**Main Branch:** Tries to put `source` in session metadata

**Official Docs + Complete-Refactor Tracer:** `source` is a **tracer-level configuration**, not session metadata:

```python
# ✅ CORRECT
tracer = HoneyHiveTracer(
    source="evaluation",  # Tracer config
    metadata={...}        # Session metadata (no source here)
)
```

### 3. **`dataset_id` Location**

**Main Branch (WRONG):**
```python
POST /session/start with metadata.dataset_id
```

**Official Docs (CORRECT):**
```python
POST /runs with { dataset_id: "..." }  # In run creation
# dataset_id NOT in session metadata
```

### 4. **Event IDs**

**Official Docs:**
```python
PUT /runs/{run_id} with {
    event_ids: [session_id_1, session_id_2, ...]  # Session IDs
    status: "completed"
}
```

This is actually what main branch does correctly!

---

## ✅ Backward Compatibility Layer

### `src/honeyhive/evaluation/__init__.py`

```python
"""Backward compatibility layer for evaluation module.

This module provides compatibility with the old evaluation API while
redirecting to the new experiments module. All new code should use
the experiments module directly.
"""

import warnings
from typing import Any, Callable, Dict, List, Optional

# Import from experiments module
from ..experiments import (
    evaluate as _evaluate,
    ExperimentContext as _ExperimentContext,
    create_external_dataset as _create_external_dataset,
)
from ..experiments.evaluators import evaluator, aevaluator

# Deprecated aliases with warnings
def evaluate(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """Deprecated: Use honeyhive.experiments.evaluate instead.
    
    This function is maintained for backward compatibility only.
    """
    warnings.warn(
        "honeyhive.evaluation.evaluate is deprecated. "
        "Use honeyhive.experiments.evaluate instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return _evaluate(*args, **kwargs)


class EvaluationContext(_ExperimentContext):
    """Deprecated: Use ExperimentContext instead."""
    
    def __init__(self, *args: Any, **kwargs: Any):
        warnings.warn(
            "EvaluationContext is deprecated. Use ExperimentContext instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)


def create_external_dataset(*args: Any, **kwargs: Any):
    """Deprecated: Use experiments.create_external_dataset instead."""
    warnings.warn(
        "evaluation.create_external_dataset is deprecated. "
        "Use experiments.create_external_dataset instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return _create_external_dataset(*args, **kwargs)


__all__ = [
    "evaluate",
    "evaluator",
    "aevaluator",
    "EvaluationContext",
    "create_external_dataset",
]
```

---

## 🧪 Testing Strategy

### Test 1: External Dataset Path

```python
def test_external_dataset_evaluation():
    """Test evaluation with external dataset per official docs."""
    
    # Define test function
    def my_function(inputs: Dict, ground_truth: Dict) -> str:
        return f"Response to: {inputs.get('query')}"
    
    # Define test dataset
    dataset = [
        {"inputs": {"query": "test1"}, "ground_truth": "answer1"},
        {"inputs": {"query": "test2"}, "ground_truth": "answer2"},
    ]
    
    # Run evaluation
    results = evaluate(
        function=my_function,
        dataset=dataset,
        api_key="test-key",
        project="test-project",
        name="test-run"
    )
    
    # Verify results
    assert results["run_id"] is not None
    assert len(results["session_ids"]) == 2
    assert results["stats"]["total"] == 2
    
    # Verify session metadata (external dataset path)
    # Should only have run_id, NOT datapoint_id or dataset_id
```

### Test 2: HoneyHive Dataset Path

```python
def test_honeyhive_dataset_evaluation():
    """Test evaluation with HoneyHive dataset per official docs."""
    
    # Define test function
    def my_function(inputs: Dict) -> str:
        return f"Response to: {inputs.get('query')}"
    
    # Run evaluation with HoneyHive dataset
    results = evaluate(
        function=my_function,
        dataset_id="ds-123abc",
        api_key="test-key",
        project="test-project"
    )
    
    # Verify results
    assert results["run_id"] is not None
    assert len(results["session_ids"]) > 0
    
    # Verify session metadata (HoneyHive dataset path)
    # Should have both run_id AND datapoint_id
```

### Test 3: Metadata Validation

```python
def test_session_metadata_format():
    """Test that session metadata matches official docs format."""
    
    # External dataset context
    context_external = ExperimentContext(
        run_id="run-123",
        project="test-project",
        use_honeyhive_dataset=False
    )
    
    metadata_external = context_external.to_session_metadata()
    
    # Per official docs: external datasets only need run_id
    assert metadata_external == {"run_id": "run-123"}
    assert "datapoint_id" not in metadata_external
    assert "dataset_id" not in metadata_external
    
    # HoneyHive dataset context
    context_hh = ExperimentContext(
        run_id="run-123",
        project="test-project",
        dataset_id="ds-456",
        use_honeyhive_dataset=True
    )
    
    metadata_hh = context_hh.to_session_metadata(datapoint_id="dp-789")
    
    # Per official docs: HH datasets need run_id + datapoint_id
    assert metadata_hh == {
        "run_id": "run-123",
        "datapoint_id": "dp-789"
    }
    assert "dataset_id" not in metadata_hh  # Goes in run, not session
```

---

## 🎯 Implementation Checklist

### Phase 1: Core Structure (2-3 hours)
- [ ] Create `src/honeyhive/experiments/` directory
- [ ] Implement `experiments/__init__.py`
- [ ] Implement `experiments/context.py` with path-specific metadata
- [ ] Implement `experiments/core.py` with both API paths
- [ ] Implement `experiments/dataset.py` for external datasets

### Phase 2: Evaluator Integration (1-2 hours)
- [ ] Copy evaluator framework from main branch
- [ ] Update to use experiment context
- [ ] Ensure compatibility with new metadata structure

### Phase 3: Backward Compatibility (1 hour)
- [ ] Implement `evaluation/__init__.py` compatibility layer
- [ ] Add deprecation warnings
- [ ] Test backward compatibility

### Phase 4: Testing (2-3 hours)
- [ ] Unit tests for ExperimentContext
- [ ] Integration tests for both API paths
- [ ] Metadata validation tests
- [ ] Backward compatibility tests

### Phase 5: Documentation (1-2 hours)
- [ ] API reference documentation
- [ ] Migration guide
- [ ] Examples for both paths
- [ ] Link to official docs

---

## 📝 Key Takeaways

1. **Follow the Official Docs Exactly**: The HoneyHive docs define TWO distinct paths with DIFFERENT metadata requirements

2. **Metadata is Path-Specific**:
   - External datasets: Only `run_id`
   - HoneyHive datasets: `run_id` + `datapoint_id`
   - `dataset_id` goes in **run creation**, not session metadata

3. **`source` is Tracer-Level**: Not session metadata

4. **Use Generated Models**: No custom dataclasses

5. **Maintain Backward Compatibility**: Old code must still work

---

**Next Step**: Begin Phase 1 implementation with `ExperimentContext` and proper metadata structure per official docs.

