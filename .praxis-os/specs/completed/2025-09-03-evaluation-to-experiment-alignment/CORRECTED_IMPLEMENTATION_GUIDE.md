# CORRECTED Comprehensive Implementation Guide
**Based on: Main Branch + Complete-Refactor Tracer + Real Requirements**

**Date**: October 2, 2025  
**Source of Truth Hierarchy**: main branch > docs > internal spec  
**Architecture**: Complete-refactor tracer with multi-instance design

---

## 🎯 Critical Clarifications

### 1. Metadata Requirements (FROM MAIN BRANCH - SOURCE OF TRUTH)

```python
# ✅ CORRECT - All fields required in session metadata
metadata = {
    "run_id": "<run_id>",           # ✅ Required
    "dataset_id": "<dataset_id>",   # ✅ Required
    "datapoint_id": "<datapoint_id>", # ✅ Required
    "source": "evaluation"          # ✅ Required (in both tracer config & metadata)
}
```

**Key Insight**: The official docs were wrong/incomplete. Main branch has the correct structure.

### 2. Tracer Configuration = Session Metadata

From your clarification:
> "source should be in both tracer config and session metadata - they are the same thing, since tracer config is automatically set on session metadata"

```python
# When you set tracer config:
tracer = HoneyHiveTracer(
    api_key=api_key,
    project=project,
    source="evaluation",      # ✅ Tracer config
    run_id=run_id,            # ✅ Auto-populates metadata
    dataset_id=dataset_id,    # ✅ Auto-populates metadata
    datapoint_id=datapoint_id # ✅ Auto-populates metadata
)

# These automatically become session metadata via tracer's built-in functionality
```

### 3. Tracer Multi-Instance Architecture

From the docs:
- Each tracer instance is **completely isolated**
- Has its own API client, logger, cache
- Thread-safe multi-instance operation
- No shared state between instances

**For experiments with concurrency**: Create one tracer instance per datapoint execution thread.

### 4. Generated Models (Pydantic v2)

Use models from `src/honeyhive/models/generated.py`:
- `EvaluationRun` - For runs
- `ExperimentResultResponse` - For results
- `ExperimentComparisonResponse` - For comparisons
- `Datapoint`, `Datapoint1` - For datapoints
- `Metrics`, `Detail` - For metrics

---

## 🏗️ Architecture Overview

### Source of Truth: Main Branch
✅ Has correct metadata structure  
✅ Has working multi-threading  
✅ Has comprehensive evaluator framework  
✅ Has external dataset handling with EXT- prefix  

### Infrastructure: Complete-Refactor
✅ Multi-instance tracer architecture  
✅ Built-in experiment metadata functionality  
✅ Pydantic v2 generated models  
✅ Better API client  

### Goal: Combine Best of Both
- Port main branch interfaces (backward compatibility)
- Use complete-refactor tracer (multi-instance architecture)
- Improve implementation (align with new SDK practices)
- Add experiment terminology (with backward compatibility)

---

## 📋 Implementation Plan

### Phase 1: Create Experiments Module Structure

#### File: `src/honeyhive/experiments/__init__.py`

```python
"""HoneyHive Experiments Module.

This module provides experiment execution capabilities using the tracer's
built-in experiment metadata functionality and multi-instance architecture.

Architecture:
    - Uses tracer multi-instance design for thread-safe concurrent execution
    - Leverages tracer's built-in experiment metadata (run_id, dataset_id, datapoint_id)
    - Uses Pydantic v2 generated models exclusively
    - Maintains backward compatibility with evaluation module
"""

from typing import Any, Callable, Dict, List, Optional

# Import generated models (Pydantic v2)
from ..models.generated import (
    CreateRunRequest,
    CreateRunResponse,
    UpdateRunRequest,
    UpdateRunResponse,
    GetRunResponse,
    ExperimentResultResponse,
    ExperimentComparisonResponse,
    EvaluationRun,
    Datapoint,
    Datapoint1,
    Metrics,
    Detail,
)

# Import from submodules
from .core import evaluate
from .context import ExperimentContext
from .dataset import create_external_dataset, generate_datapoint_id
from .evaluators import evaluator, aevaluator, run_evaluators

# Type aliases for experiment terminology
ExperimentRun = EvaluationRun  # Already Pydantic v2 model
ExperimentResult = ExperimentResultResponse  # Already Pydantic v2 model

__all__ = [
    # Main functions
    "evaluate",
    
    # Models (generated)
    "ExperimentRun",
    "ExperimentResult",
    "ExperimentResultResponse",
    "ExperimentComparisonResponse",
    "CreateRunRequest",
    "CreateRunResponse",
    
    # Context and dataset
    "ExperimentContext",
    "create_external_dataset",
    "generate_datapoint_id",
    
    # Evaluators
    "evaluator",
    "aevaluator",
    "run_evaluators",
]
```

#### File: `src/honeyhive/experiments/context.py`

```python
"""Experiment context for metadata management.

This module uses the tracer's built-in experiment metadata functionality
instead of manually setting metadata fields.
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class ExperimentContext:
    """Experiment context for managing run metadata.
    
    This class works with the tracer's built-in experiment metadata
    functionality. Fields set here are automatically propagated to
    session metadata via the tracer configuration.
    
    Attributes:
        run_id: Evaluation run identifier
        project: HoneyHive project name
        dataset_id: Dataset identifier (always set, even for external)
        source: Source environment (default: "evaluation")
        metadata: Additional custom metadata
        use_honeyhive_dataset: Whether using platform-managed dataset
    """
    
    run_id: str
    project: str
    dataset_id: str  # Always required (main branch is source of truth)
    source: str = "evaluation"
    metadata: Optional[Dict[str, Any]] = None
    use_honeyhive_dataset: bool = False
    
    def to_tracer_config(self, datapoint_id: str) -> Dict[str, Any]:
        """Convert to tracer configuration.
        
        These fields are automatically set on session metadata via the
        tracer's built-in experiment metadata functionality.
        
        Args:
            datapoint_id: Datapoint identifier (required)
            
        Returns:
            Dictionary of tracer configuration that auto-populates metadata
        """
        config = {
            # Core tracer config
            "api_key": None,  # Will be set by caller
            "project": self.project,
            "source": self.source,  # ✅ Auto-populates metadata
            
            # Experiment metadata (auto-populates via tracer)
            "is_evaluation": True,
            "run_id": self.run_id,           # ✅ Auto-populates metadata
            "dataset_id": self.dataset_id,   # ✅ Auto-populates metadata
            "datapoint_id": datapoint_id,    # ✅ Auto-populates metadata
        }
        
        # Add custom metadata if provided
        if self.metadata:
            config["metadata"] = self.metadata
        
        return config
    
    def to_run_request(self, name: str, status: str = "running") -> "CreateRunRequest":
        """Convert to run creation request.
        
        Uses generated Pydantic v2 model.
        
        Args:
            name: Run name
            status: Run status
            
        Returns:
            CreateRunRequest model instance
        """
        from ..models.generated import CreateRunRequest
        
        return CreateRunRequest(
            project=self.project,
            name=name,
            dataset_id=self.dataset_id,
            status=status,
            metadata=self.metadata or {}
        )
```

#### File: `src/honeyhive/experiments/core.py`

```python
"""Core experiment execution using tracer multi-instance architecture.

This module implements the evaluate() function using:
1. Tracer's built-in experiment metadata functionality
2. Multi-instance tracer architecture for thread-safe concurrency
3. Generated Pydantic v2 models exclusively
4. Main branch's proven metadata structure
"""

import os
import uuid
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List, Optional, Tuple
import logging
import contextvars

from ..api.client import HoneyHive
from ..tracer import HoneyHiveTracer
from ..models.generated import (
    CreateRunRequest,
    UpdateRunRequest,
    ExperimentResultResponse,
    Datapoint1,
    Metrics,
    Detail,
)
from .context import ExperimentContext
from .dataset import create_external_dataset, fetch_honeyhive_dataset
from .evaluators import run_evaluators

logger = logging.getLogger(__name__)


def evaluate(
    function: Callable,
    *,
    # API credentials
    api_key: Optional[str] = None,
    project: Optional[str] = None,
    
    # Run configuration
    name: Optional[str] = None,
    
    # Dataset configuration (one required)
    dataset_id: Optional[str] = None,  # HoneyHive dataset
    dataset: Optional[List[Dict[str, Any]]] = None,  # External dataset
    
    # Evaluation configuration
    evaluators: Optional[List[Any]] = None,
    
    # Execution configuration
    max_workers: int = 10,
    run_concurrently: bool = True,
    
    # Optional overrides
    server_url: Optional[str] = None,
    verbose: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
) -> ExperimentResultResponse:
    """Execute a function against a dataset with evaluation.
    
    This function uses the tracer's multi-instance architecture for
    thread-safe concurrent execution. Each datapoint gets its own
    independent tracer instance.
    
    Args:
        function: User function to execute against each datapoint
        api_key: HoneyHive API key (defaults to HH_API_KEY env var)
        project: Project name (defaults to HH_PROJECT env var)
        name: Experiment run name
        dataset_id: HoneyHive dataset ID (for platform-managed data)
        dataset: External dataset as list of dicts (for user-managed data)
        evaluators: List of evaluator functions
        max_workers: Number of parallel workers (tracer instances)
        run_concurrently: Enable concurrent execution
        server_url: HoneyHive server URL override
        verbose: Enable verbose logging
        metadata: Additional run metadata
        
    Returns:
        ExperimentResultResponse (Pydantic v2 generated model)
        
    Raises:
        ValueError: If invalid inputs provided
        RuntimeError: If execution fails
        
    Example:
        >>> from honeyhive.experiments import evaluate
        >>> 
        >>> def my_function(inputs: Dict, ground_truth: Dict) -> str:
        ...     return f"Response: {inputs['query']}"
        >>> 
        >>> results = evaluate(
        ...     function=my_function,
        ...     dataset=[
        ...         {"inputs": {"query": "test"}, "ground_truth": "answer"}
        ...     ],
        ...     evaluators=[accuracy_evaluator],
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
        raise ValueError("api_key and project required (env or params)")
    
    # Initialize API client (shared across threads)
    client = HoneyHive(
        api_key=api_key,
        server_url=server_url,
        verbose=verbose
    )
    
    # Determine dataset type
    use_honeyhive_dataset = dataset_id is not None
    
    #==========================================================================
    # STEP 1: Prepare Dataset
    #==========================================================================
    
    if use_honeyhive_dataset:
        # Fetch HoneyHive dataset
        if verbose:
            logger.info(f"Fetching HoneyHive dataset: {dataset_id}")
        
        dataset_data, datapoint_ids = fetch_honeyhive_dataset(
            client=client,
            dataset_id=dataset_id,
            project=project
        )
    else:
        # Create external dataset with EXT- prefix
        if verbose:
            logger.info(f"Creating external dataset with {len(dataset)} datapoints")
        
        dataset_id, datapoint_ids = create_external_dataset(
            datapoints=dataset,
            project=project
        )
        dataset_data = dataset
    
    num_datapoints = len(dataset_data)
    
    if verbose:
        logger.info(f"Dataset prepared: {num_datapoints} datapoints")
    
    #==========================================================================
    # STEP 2: Create Evaluation Run
    #==========================================================================
    
    run_name = name or f"experiment-{uuid.uuid4().hex[:8]}"
    
    if verbose:
        logger.info(f"Creating evaluation run: {run_name}")
    
    # Create run using generated Pydantic v2 model
    run_request = CreateRunRequest(
        project=project,
        name=run_name,
        dataset_id=dataset_id,  # ✅ Always set (main branch is source of truth)
        status="running",
        metadata=metadata or {}
    )
    
    run_response = client.evaluations.create_run(run_request)
    
    if not run_response or not hasattr(run_response, 'run_id'):
        raise RuntimeError("Failed to create evaluation run")
    
    run_id = str(run_response.run_id)
    
    if verbose:
        logger.info(f"Created run: {run_id}")
    
    # Create experiment context
    context = ExperimentContext(
        run_id=run_id,
        project=project,
        dataset_id=dataset_id,
        source="evaluation",
        metadata=metadata,
        use_honeyhive_dataset=use_honeyhive_dataset
    )
    
    #==========================================================================
    # STEP 3: Execute Function Against Dataset (Multi-Instance Architecture)
    #==========================================================================
    
    start_time = time.time()
    session_ids = []
    results = []
    
    def execute_single_datapoint(idx: int) -> Dict[str, Any]:
        """Execute function for single datapoint with dedicated tracer instance.
        
        Each execution gets its own tracer instance following the
        multi-instance architecture. This ensures complete isolation
        and thread safety.
        """
        
        # Get datapoint data
        datapoint_data = dataset_data[idx]
        datapoint_id = datapoint_ids[idx]
        
        inputs = datapoint_data.get("inputs", {})
        ground_truth = datapoint_data.get("ground_truth", {})
        
        # Get tracer config from context (auto-populates metadata)
        tracer_config = context.to_tracer_config(datapoint_id=datapoint_id)
        tracer_config["api_key"] = api_key
        tracer_config["server_url"] = server_url
        tracer_config["verbose"] = verbose
        
        # Create dedicated tracer instance for this datapoint
        # ✅ Multi-instance architecture: Each thread gets isolated tracer
        tracer = HoneyHiveTracer(**tracer_config)
        
        session_id = tracer.session_id
        
        try:
            # Execute user function
            # Note: Function execution happens within tracer context
            if ground_truth:
                outputs = function(inputs, ground_truth)
            else:
                outputs = function(inputs)
            
            # Run evaluators if provided
            evaluator_results = []
            if evaluators:
                evaluator_results = run_evaluators(
                    evaluators=evaluators,
                    inputs=inputs,
                    outputs=outputs,
                    ground_truth=ground_truth
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
            
            # Flush even on error
            try:
                tracer.flush()
            except:
                pass
            
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
    # ✅ Uses ThreadPoolExecutor (not multiprocessing) per tracer docs
    if run_concurrently and max_workers > 1:
        if verbose:
            logger.info(f"Executing with {max_workers} workers (multi-instance)")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks with context propagation
            futures = []
            for i in range(num_datapoints):
                # Copy context for thread isolation (contextvars pattern)
                ctx = contextvars.copy_context()
                future = executor.submit(ctx.run, execute_single_datapoint, i)
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    session_ids.append(result["session_id"])
                    
                    if verbose and result["status"] == "success":
                        logger.info(f"✓ Completed: {result['datapoint_id']}")
                    elif verbose:
                        logger.warning(f"✗ Failed: {result['datapoint_id']}")
                        
                except Exception as e:
                    logger.error(f"Future execution failed: {e}")
    else:
        # Sequential execution
        if verbose:
            logger.info("Executing sequentially")
        
        for i in range(num_datapoints):
            result = execute_single_datapoint(i)
            results.append(result)
            session_ids.append(result["session_id"])
    
    end_time = time.time()
    duration = end_time - start_time
    
    if verbose:
        logger.info(f"Execution complete: {duration:.2f}s")
    
    #==========================================================================
    # STEP 4: Aggregate Results (Using Generated Models)
    #==========================================================================
    
    # Aggregate into ExperimentResultResponse (Pydantic v2)
    experiment_result = _aggregate_results(
        results=results,
        context=context
    )
    
    #==========================================================================
    # STEP 5: Update Run Status
    #==========================================================================
    
    if verbose:
        logger.info(f"Updating run status with {len(session_ids)} sessions")
    
    try:
        update_request = UpdateRunRequest(
            event_ids=session_ids,
            status="completed"
        )
        
        client.evaluations.update_run(
            run_id=run_id,
            request=update_request
        )
    except Exception as e:
        logger.warning(f"Failed to update run status: {e}")
    
    return experiment_result


def _aggregate_results(
    results: List[Dict[str, Any]],
    context: ExperimentContext
) -> ExperimentResultResponse:
    """Aggregate results into ExperimentResultResponse.
    
    Uses generated Pydantic v2 models exclusively.
    
    Args:
        results: List of individual datapoint results
        context: Experiment context
        
    Returns:
        ExperimentResultResponse (generated model)
    """
    
    # Process datapoints
    datapoint_results = []
    all_metrics = []
    
    passed_ids = []
    failed_ids = []
    
    for result in results:
        if result["status"] == "success":
            passed_ids.append(result["datapoint_id"])
            
            # Create Datapoint1 result (generated model)
            metrics_list = []
            if result.get("evaluator_results"):
                for eval_result in result["evaluator_results"]:
                    # Use Detail model (generated)
                    detail = Detail(
                        metric_name=eval_result.get("name", "unknown"),
                        value=eval_result.get("score"),
                        explanation=eval_result.get("explanation")
                    )
                    metrics_list.append(detail)
                    all_metrics.append(detail)
            
            datapoint = Datapoint1(
                datapoint_id=result["datapoint_id"],
                inputs=result["inputs"],
                outputs=result["outputs"],
                ground_truth=result.get("ground_truth"),
                passed=True,
                metrics=metrics_list
            )
            datapoint_results.append(datapoint)
        else:
            failed_ids.append(result["datapoint_id"])
    
    # Create Metrics aggregate (generated model)
    aggregate_metrics = Metrics(details=all_metrics)
    
    # Create ExperimentResultResponse (generated model)
    return ExperimentResultResponse(
        status="completed",
        success=len(passed_ids) > 0,
        passed=passed_ids,
        failed=failed_ids,
        metrics=aggregate_metrics,
        datapoints=datapoint_results
    )
```

#### File: `src/honeyhive/experiments/dataset.py`

```python
"""Dataset handling for experiments.

Includes external dataset creation with EXT- prefix handling and
edge case management from main branch.
"""

import hashlib
import json
from typing import Any, Dict, List, Tuple

from ..api.client import HoneyHive


def generate_datapoint_id(datapoint: Dict[str, Any]) -> str:
    """Generate hash-based ID for a datapoint.
    
    This preserves the logic from main branch for consistent
    ID generation.
    
    Args:
        datapoint: Datapoint dictionary
        
    Returns:
        EXT- prefixed hash ID
    """
    # Handle custom ID if provided
    if isinstance(datapoint, dict) and "id" in datapoint:
        return _add_ext_prefix(str(datapoint["id"]))
    
    # Generate hash-based ID
    try:
        datapoint_json = json.dumps(datapoint, sort_keys=True)
        hash_id = hashlib.md5(datapoint_json.encode('utf-8')).hexdigest()[:24]
        return _add_ext_prefix(hash_id)
    except Exception:
        # Fallback for non-serializable data
        hash_id = hashlib.md5(str(datapoint).encode('utf-8')).hexdigest()[:24]
        return _add_ext_prefix(hash_id)


def _add_ext_prefix(id_string: str) -> str:
    """Add EXT- prefix if not already present.
    
    Args:
        id_string: ID string
        
    Returns:
        EXT- prefixed ID
    """
    if not isinstance(id_string, str):
        id_string = str(id_string)
    
    if not id_string.startswith("EXT-"):
        return f"EXT-{id_string}"
    
    return id_string


def create_external_dataset(
    datapoints: List[Dict[str, Any]],
    project: str,
    custom_dataset_id: Optional[str] = None
) -> Tuple[str, List[str]]:
    """Create external dataset with EXT- prefixed IDs.
    
    This preserves the main branch logic for external dataset
    handling including edge cases.
    
    Args:
        datapoints: List of datapoint dictionaries
        project: Project name
        custom_dataset_id: Optional custom dataset ID
        
    Returns:
        Tuple of (dataset_id, list of datapoint_ids)
    """
    # Validate dataset
    if not isinstance(datapoints, list):
        raise ValueError("datapoints must be a list")
    
    if not all(isinstance(dp, dict) for dp in datapoints):
        raise ValueError("All datapoints must be dictionaries")
    
    # Generate datapoint IDs
    datapoint_ids = [generate_datapoint_id(dp) for dp in datapoints]
    
    # Generate dataset ID
    if custom_dataset_id:
        dataset_id = _add_ext_prefix(custom_dataset_id)
    else:
        # Hash entire dataset for consistency
        dataset_json = json.dumps(datapoints, sort_keys=True)
        hash_id = hashlib.md5(dataset_json.encode('utf-8')).hexdigest()[:24]
        dataset_id = _add_ext_prefix(hash_id)
    
    return dataset_id, datapoint_ids


def fetch_honeyhive_dataset(
    client: HoneyHive,
    dataset_id: str,
    project: str
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Fetch dataset from HoneyHive platform.
    
    Args:
        client: HoneyHive API client
        dataset_id: Dataset ID
        project: Project name
        
    Returns:
        Tuple of (datapoints list, datapoint_ids list)
    """
    # Fetch dataset
    dataset_response = client.datasets.get_dataset(
        dataset_id=dataset_id,
        project=project
    )
    
    if not dataset_response or not hasattr(dataset_response, 'datapoints'):
        raise ValueError(f"Dataset {dataset_id} not found or has no datapoints")
    
    # Get datapoint IDs
    datapoint_ids = dataset_response.datapoints
    
    # Fetch individual datapoints
    datapoints = []
    for dp_id in datapoint_ids:
        dp_response = client.datapoints.get_datapoint(id=str(dp_id))
        if dp_response:
            datapoints.append({
                "inputs": dp_response.inputs or {},
                "ground_truth": dp_response.ground_truth or {}
            })
    
    return datapoints, [str(dp_id) for dp_id in datapoint_ids]
```

---

## 🧪 Implementation Checklist

### Must-Haves ✅
- [ ] **Experiment terminology** - With backward compatibility
- [ ] **Generated models** - Pydantic v2 exclusively
- [ ] **Module reorganization** - Experiments module structure
- [ ] **Backward compatibility** - Evaluation imports still work
- [ ] **Tracer multi-instance** - One instance per thread
- [ ] **Built-in metadata** - Use tracer's experiment functionality
- [ ] **External datasets** - EXT- prefix and edge cases
- [ ] **Evaluator execution** - Properly implemented

### Nice-to-Haves 🎯
- [ ] **GitHub integration** - Check existing git functionality
- [ ] **Performance optimization** - Beyond main branch
- [ ] **Enhanced error handling** - Better than main branch

---

## 🔑 Key Implementation Points

### 1. Use Tracer's Built-In Experiment Metadata

```python
# ✅ CORRECT - Let tracer handle metadata
tracer = HoneyHiveTracer(
    api_key=api_key,
    project=project,
    source="evaluation",      # Auto-populates metadata
    run_id=run_id,            # Auto-populates metadata
    dataset_id=dataset_id,    # Auto-populates metadata
    datapoint_id=datapoint_id # Auto-populates metadata
)

# ❌ WRONG - Don't manually set metadata
metadata = {"run_id": run_id, ...}  # Tracer does this automatically
```

### 2. Multi-Instance Architecture for Concurrency

```python
# ✅ CORRECT - One tracer per thread
def execute_single_datapoint(idx: int):
    tracer = HoneyHiveTracer(...)  # New instance
    # Execute with this dedicated tracer
    
with ThreadPoolExecutor(max_workers=8) as executor:
    # Each task gets its own tracer instance
    futures = [executor.submit(execute_single_datapoint, i) for i in range(n)]

# ❌ WRONG - Sharing tracer across threads
tracer = HoneyHiveTracer(...)  # Single instance
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(task, tracer) for ...]  # Don't share!
```

### 3. Use ThreadPoolExecutor (Not Multiprocessing)

Per tracer docs: Thread-safe multi-instance operation.

```python
# ✅ CORRECT - ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    # Thread-safe with tracer multi-instance architecture
    pass

# ❌ WRONG - Multiprocessing
from multiprocessing import Pool  # Don't use this
```

### 4. Context Propagation for Thread Safety

```python
# ✅ CORRECT - Copy context per thread
import contextvars

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = []
    for i in range(n):
        ctx = contextvars.copy_context()  # Copy context
        future = executor.submit(ctx.run, execute_task, i)
        futures.append(future)
```

### 5. External Dataset Edge Cases

From main branch - preserve this logic:

```python
def generate_datapoint_id(datapoint: Dict[str, Any]) -> str:
    # Handle custom ID
    if isinstance(datapoint, dict) and "id" in datapoint:
        return _add_ext_prefix(str(datapoint["id"]))
    
    # Generate hash
    try:
        datapoint_json = json.dumps(datapoint, sort_keys=True)
        hash_id = hashlib.md5(datapoint_json.encode('utf-8')).hexdigest()[:24]
        return _add_ext_prefix(hash_id)
    except Exception:
        # Fallback for non-serializable data
        hash_id = hashlib.md5(str(datapoint).encode('utf-8')).hexdigest()[:24]
        return _add_ext_prefix(hash_id)
```

---

## ✅ Validation Checklist

Before considering implementation complete:

- [ ] All metadata fields present (run_id, dataset_id, datapoint_id, source)
- [ ] Tracer multi-instance architecture used correctly
- [ ] ThreadPoolExecutor (not multiprocessing)
- [ ] Context propagation implemented
- [ ] Generated Pydantic v2 models used exclusively
- [ ] External dataset EXT- prefix working
- [ ] Edge cases handled (non-serializable data, custom IDs)
- [ ] Evaluator execution implemented
- [ ] Backward compatibility maintained
- [ ] Tests written and passing

---

**Next Step**: Begin implementation with `ExperimentContext` using tracer's built-in metadata functionality.

