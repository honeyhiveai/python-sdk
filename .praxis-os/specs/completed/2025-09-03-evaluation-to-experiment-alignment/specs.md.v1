# Technical Specifications - Evaluation to Experiment Framework Alignment

**Date**: 2025-09-04  
**Status**: Technical Specification  
**Priority**: High  
**Branch**: complete-refactor  

## Architecture Changes

This specification defines the comprehensive technical changes required to align the current HoneyHive Python SDK evaluation implementation with the official HoneyHive experiment framework, ensuring full backward compatibility while introducing enhanced experiment management capabilities.

## Problem Statement

The current SDK implementation uses outdated terminology and lacks key functionality required by the official HoneyHive experiment framework:

1. **Terminology Mismatch**: Uses "evaluation" instead of "experiment" terminology
2. **Missing Metadata Linking**: No proper `run_id`, `dataset_id`, `datapoint_id` metadata on events
3. **Incomplete Experiment Run Support**: Limited integration with the experiment run workflow
4. **No Client-side Dataset Support**: Missing external dataset handling capabilities
5. **Limited Results Management**: No SDK functionality for experiment results export
6. **Missing Main Evaluate Function**: No function that executes a user-provided function against the dataset

## Current State Analysis

### ✅ What's Working
- Basic evaluation framework with evaluators and decorators
- API integration for evaluation runs
- Data models for EvaluationRun, Datapoint, Dataset
- Comprehensive test coverage
- **Advanced multi-threading with two-level parallelism**
- **High-performance batch processing capabilities**

### ❌ What's Missing
- Experiment terminology and concepts
- Proper metadata linking for experiment runs
- Client-side dataset support with `EXT-` prefix
- Experiment results export functionality
- GitHub integration for automated runs
- **Main evaluate function that executes user functions against datasets**

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

#### New Architecture  
```
src/honeyhive/
├── experiments/              # NEW: Primary experiment module
│   ├── __init__.py          # New experiment exports + compatibility aliases
│   ├── core.py              # Core experiment functionality
│   ├── context.py           # Experiment context management
│   ├── dataset.py           # External dataset support
│   ├── results.py           # Result structures using official models
│   └── evaluators.py        # Enhanced evaluator framework
├── evaluation/              # MAINTAINED: Backward compatibility
│   ├── __init__.py          # Compatibility imports from experiments/
│   └── evaluators.py        # Maintained with deprecation warnings
└── api/
    ├── experiments.py       # NEW: Experiment API client
    └── evaluations.py       # MAINTAINED: Compatibility wrapper
```

### 2. Core Data Model Changes

#### Current Implementation
```python
# src/honeyhive/evaluation/evaluators.py
@dataclass
class EvaluationResult:
    """Current evaluation result structure."""
    evaluator_name: str
    score: Union[float, int, bool]
    explanation: Optional[str] = None

@dataclass 
class EvaluationContext:
    """Current evaluation context."""
    project: str
    metadata: Optional[Dict[str, Any]] = None
```

#### Enhanced Implementation Using Generated Models
```python
# src/honeyhive/experiments/core.py
from typing import Union, Optional, Dict, Any, List
from honeyhive.models.generated import (
    EvaluationRun,                    # Use existing run model
    ExperimentResultResponse,         # Use existing result response
    ExperimentComparisonResponse,     # Use existing comparison response
    Dataset,                          # Use existing dataset model
    Datapoint,                        # Use existing datapoint model
    CreateRunRequest,                 # Use existing request model
    CreateRunResponse,                # Use existing response model
    Datapoint1,                       # Use existing result datapoint model
    Metrics,                          # Use existing metrics model
)

# Simple context class for metadata linking - minimal addition
class ExperimentContext:
    """Lightweight experiment context for metadata linking."""
    
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
    
    def to_trace_metadata(self, datapoint_id: str) -> Dict[str, str]:
        """Convert to tracer metadata format for event linking."""
        return {
            "run_id": self.run_id,
            "dataset_id": self.dataset_id,
            "datapoint_id": datapoint_id,
            "source": self.source
        }
    
    def to_evaluation_run(self, name: Optional[str] = None) -> EvaluationRun:
        """Convert to official EvaluationRun model."""
        return EvaluationRun(
            run_id=self.run_id,
            project=self.project,
            dataset_id=self.dataset_id,
            name=name or f"experiment-{self.run_id[:8]}",
            metadata=self.metadata,
            status="running"
        )

# Type aliases for clarity - use existing models directly
ExperimentRun = EvaluationRun                    # Alias existing model
ExperimentResult = ExperimentResultResponse      # Use existing response model
ExperimentComparison = ExperimentComparisonResponse  # Use existing comparison model
```

### 3. Backward Compatibility Implementation

#### Compatibility Layer
```python
# src/honeyhive/evaluation/__init__.py
"""Backward compatibility layer for evaluation module."""

import warnings
from typing import TYPE_CHECKING

# Import all new functionality from experiments module
from ..experiments import (
    ExperimentContext as _ExperimentContext,
    evaluate as _evaluate,
    create_experiment_run as _create_experiment_run,
    # ... other imports
)
# Import official models directly
from ..models.generated import (
    EvaluationRun as _EvaluationRun,
    ExperimentResultResponse as _ExperimentResultResponse,
    # ... other official models
)

# Backward compatibility aliases
class EvaluationContext(_ExperimentContext):
    """Backward compatibility alias for ExperimentContext."""
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "EvaluationContext is deprecated. Use ExperimentContext instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)

# Direct aliases to official models - no custom classes needed
EvaluationResult = _ExperimentResultResponse  # Use official response model
EvaluationRun = _EvaluationRun  # Use official evaluation run model

def create_evaluation_run(*args, **kwargs):
    """Backward compatibility function for create_experiment_run."""
    warnings.warn(
        "create_evaluation_run is deprecated. Use create_experiment_run instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return _create_experiment_run(*args, **kwargs)

# Export all current functionality
__all__ = [
    "EvaluationContext",  # Compatibility alias
    "EvaluationResult",   # Compatibility alias  
    "create_evaluation_run",  # Compatibility function
    "evaluate",
    # ... all other current exports
]
```

### 2. Metadata Linking Implementation

#### 2.1 Event Metadata Requirements
Every event in an experiment run must include:
```python
metadata = {
    "run_id": "uuid-string",
    "dataset_id": "uuid-string", 
    "datapoint_id": "uuid-string",
    "source": "evaluation"  # Always "evaluation" for experiment runs
}
```

#### 2.2 Tracer Integration
- Extend `HoneyHiveTracer` to support experiment run context
- Add methods for setting experiment run metadata
- Ensure all traced events include required metadata

#### 2.3 Experiment Run Context  
```python
# Lightweight context class for metadata linking only
class ExperimentContext:
    """Lightweight experiment context for metadata linking."""
    
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
    
    def to_evaluation_run(self, name: Optional[str] = None) -> EvaluationRun:
        """Convert to official EvaluationRun model."""
        from ..models.generated import EvaluationRun
        return EvaluationRun(
            run_id=self.run_id,
            project=self.project,
            dataset_id=self.dataset_id,
            name=name or f"experiment-{self.run_id[:8]}",
            metadata=self.metadata
        )
```

### 3. Client-side Dataset Support

#### 3.1 External Dataset Handling
```python
def create_external_dataset(
    datapoints: List[Dict[str, Any]],
    project: str,
    custom_dataset_id: Optional[str] = None
) -> Tuple[str, List[str]]:
    """
    Create client-side dataset with EXT- prefix.
    
    Returns:
        Tuple of (dataset_id, datapoint_ids)
    """
```

#### 3.2 Dataset ID Generation
- Generate hash-based IDs for external datasets
- Prefix with `EXT-` to avoid platform collisions
- Support custom IDs with `EXT-` prefix

#### 3.3 Datapoint ID Generation
- Hash individual datapoints for unique identification
- Ensure consistency across experiment runs
- Support custom IDs with `EXT-` prefix

### 4. Enhanced Experiment Management

#### 4.1 Main Experiment Evaluation Function Implementation

```python
# src/honeyhive/experiments/core.py
from typing import Callable, Optional, List, Dict, Any, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid
import logging
from contextlib import contextmanager

from ..tracer import HoneyHiveTracer, get_default_tracer
from ..api.client import HoneyHive
from .context import ExperimentContext
from .dataset import create_external_dataset, validate_dataset
from .evaluators import evaluate_with_evaluators
from .results import aggregate_experiment_results
from ..models.generated import ExperimentResultResponse

logger = logging.getLogger(__name__)

def evaluate(
    function: Callable,
    hh_api_key: Optional[str] = None,
    hh_project: Optional[str] = None,
    name: Optional[str] = None,
    suite: Optional[str] = None,
    dataset_id: Optional[str] = None,
    dataset: Optional[List[Dict[str, Any]]] = None,
    evaluators: Optional[List[Any]] = None,
    max_workers: int = 10,
    verbose: bool = False,
    server_url: Optional[str] = None,
    context: Optional[ExperimentContext] = None,
) -> ExperimentResultResponse:
    """
    Main experiment evaluation function that executes a function against a dataset.
    
    Args:
        function: User function to execute against each datapoint
        hh_api_key: HoneyHive API key (defaults to environment variable)
        hh_project: HoneyHive project name (defaults to environment variable)
        name: Experiment run name
        suite: Experiment suite name
        dataset_id: HoneyHive dataset ID or external dataset ID
        dataset: Raw dataset as list of dictionaries
        evaluators: List of evaluators to run against outputs
        max_workers: Maximum number of worker threads
        verbose: Enable verbose logging
        server_url: HoneyHive server URL override
        context: Pre-created experiment context
        
    Returns:
        ExperimentResultResponse with comprehensive experiment results
        
    Raises:
        ValueError: If neither dataset_id nor dataset is provided
        RuntimeError: If function execution fails for all datapoints
    """
    
    # Initialize API client
    client = HoneyHive(
        api_key=hh_api_key,
        project=hh_project,
        server_url=server_url
    )
    
    # Prepare dataset
    if dataset is not None:
        # Create external dataset
        dataset_id, datapoint_ids = create_external_dataset(
            datapoints=dataset,
            project=hh_project or client.project,
            custom_dataset_id=dataset_id
        )
        dataset_for_execution = dataset
    elif dataset_id is not None:
        # Fetch dataset from HoneyHive
        dataset_response = client.datasets.get_dataset(dataset_id)
        if not dataset_response or not dataset_response.datapoints:
            raise ValueError(f"Dataset {dataset_id} not found or empty")
        dataset_for_execution = [dp.dict() for dp in dataset_response.datapoints]
        datapoint_ids = [dp.id for dp in dataset_response.datapoints]
    else:
        raise ValueError("Either 'dataset' or 'dataset_id' must be provided")
    
    # Create or use provided experiment context
    if context is None:
        run_id = str(uuid.uuid4())
        context = ExperimentContext(
            run_id=run_id,
            dataset_id=dataset_id,
            project=hh_project or client.project,
            source="evaluation"
        )
    
    # Create experiment run via API
    experiment_run = client.experiments.create_experiment_run(
        name=name or f"experiment-{context.run_id[:8]}",
        project=context.project,
        dataset_id=context.dataset_id,
        configuration={
            "function_name": getattr(function, "__name__", "anonymous"),
            "evaluators": [str(e) for e in (evaluators or [])],
            "max_workers": max_workers,
            "suite": suite
        },
        metadata=context.metadata
    )
    
    if experiment_run:
        context.run_id = experiment_run.id
    
    # Execute experiment run
    return _execute_experiment_run(
        function=function,
        dataset=dataset_for_execution,
        datapoint_ids=datapoint_ids,
        evaluators=evaluators or [],
        context=context,
        max_workers=max_workers,
        verbose=verbose,
        client=client
    )


def _execute_experiment_run(
    function: Callable,
    dataset: List[Dict[str, Any]],
    datapoint_ids: List[str],
    evaluators: List[Any],
    context: ExperimentContext,
    max_workers: int,
    verbose: bool,
    client: HoneyHive
) -> ExperimentResultResponse:
    """Execute the complete experiment run workflow with multi-threading."""
    
    results = []
    successful_executions = 0
    failed_executions = 0
    
    def execute_single_datapoint(datapoint: Dict[str, Any], datapoint_id: str) -> Dict[str, Any]:
        """Execute function against a single datapoint with proper tracing."""
        
        inputs = datapoint.get("inputs", {})
        ground_truth = datapoint.get("ground_truth")
        
        # Create trace metadata for this datapoint
        trace_metadata = context.to_trace_metadata(datapoint_id)
        
        try:
            # Get or create tracer with experiment context
            tracer = get_default_tracer()
            if tracer is None:
                tracer = HoneyHiveTracer(
                    project=context.project,
                    metadata=trace_metadata
                )
            else:
                # Set experiment metadata on existing tracer
                tracer.set_metadata(trace_metadata)
            
            with tracer:
                # Execute function with inputs and ground_truth
                if ground_truth is not None:
                    outputs = function(inputs, ground_truth)
                else:
                    outputs = function(inputs)
                
                # Run evaluators against outputs
                evaluator_results = []
                if evaluators:
                    evaluator_results = evaluate_with_evaluators(
                        evaluators=evaluators,
                        inputs=inputs,
                        outputs=outputs,
                        ground_truth=ground_truth,
                        context=context,
                        max_workers=1,  # Single evaluator per datapoint
                        run_concurrently=False
                    )
                
                return {
                    "datapoint_id": datapoint_id,
                    "inputs": inputs,
                    "outputs": outputs,
                    "ground_truth": ground_truth,
                    "evaluator_results": evaluator_results,
                    "status": "success",
                    "error": None
                }
                
        except Exception as e:
            logger.error(f"Function execution failed for datapoint {datapoint_id}: {e}")
            return {
                "datapoint_id": datapoint_id,
                "inputs": inputs,
                "outputs": None,
                "ground_truth": ground_truth,
                "evaluator_results": None,
                "status": "failed",
                "error": str(e)
            }
    
    # Execute function against dataset with threading
    if verbose:
        logger.info(f"Executing function against {len(dataset)} datapoints with {max_workers} workers")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all datapoint executions
        future_to_datapoint = {
            executor.submit(execute_single_datapoint, datapoint, datapoint_ids[i]): i
            for i, datapoint in enumerate(dataset)
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_datapoint):
            try:
                result = future.result()
                results.append(result)
                
                if result["status"] == "success":
                    successful_executions += 1
                else:
                    failed_executions += 1
                    
                if verbose:
                    logger.info(f"Completed datapoint {result['datapoint_id']}: {result['status']}")
                    
            except Exception as e:
                failed_executions += 1
                logger.error(f"Future execution failed: {e}")
    
    # Validate execution results
    if successful_executions == 0:
        raise RuntimeError("All datapoint executions failed")
    
    if verbose:
        logger.info(f"Experiment execution complete: {successful_executions} successful, {failed_executions} failed")
    
    # Aggregate results and create final experiment result using official models
    return aggregate_experiment_results(
        results=results,
        context=context,
        client=client
    )  # Returns ExperimentResultResponse


@contextmanager
def experiment_context(
    run_id: str,
    dataset_id: str,
    project: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """Context manager for experiment execution with automatic cleanup."""
    
    context = ExperimentContext(
        run_id=run_id,
        dataset_id=dataset_id,
        project=project,
        metadata=metadata
    )
    
    try:
        yield context
    finally:
        # Cleanup logic if needed
        pass
```

#### 4.2 Function Execution Flow
The main evaluation process follows this flow:

```python
def _execute_experiment_run(
    function: Callable,
    dataset: List[Dict[str, Any]],
    evaluators: List[Any],
    context: ExperimentContext,
    max_workers: int = 10,
) -> ExperimentResultResponse:
    """
    Execute the complete experiment run workflow.
    
    1. Execute function against each datapoint
    2. Run evaluators against function outputs
    3. Aggregate results and metrics
    4. Return structured experiment results
    """
    results = []
    
    # Execute function against dataset
    for datapoint in dataset:
        inputs = datapoint.get("inputs", {})
        ground_truth = datapoint.get("ground_truth")
        
        # Execute the function with proper context
        with HoneyHiveTracer(
            project=context.project,
            metadata={
                "run_id": context.run_id,
                "dataset_id": context.dataset_id,
                "datapoint_id": datapoint.get("id", str(uuid.uuid4())),
                "source": "evaluation"
            }
        ):
            try:
                # Execute function with inputs and ground_truth
                if ground_truth is not None:
                    outputs = function(inputs, ground_truth)
                else:
                    outputs = function(inputs)
                
                # Run evaluators against outputs
                evaluator_results = evaluate_with_evaluators(
                    evaluators=evaluators,
                    inputs=inputs,
                    outputs=outputs,
                    ground_truth=ground_truth,
                    context=context,
                    max_workers=1,  # Single evaluator per datapoint
                    run_concurrently=False
                )
                
                results.append({
                    "inputs": inputs,
                    "outputs": outputs,
                    "ground_truth": ground_truth,
                    "evaluator_results": evaluator_results
                })
                
            except Exception as e:
                logger.error(f"Function execution failed for datapoint: {e}")
                # Record failure with error metadata
                results.append({
                    "inputs": inputs,
                    "outputs": None,
                    "ground_truth": ground_truth,
                    "error": str(e),
                    "evaluator_results": None
                })
    
    # Aggregate results and create final experiment result
    return _aggregate_experiment_results(results, context)
```

#### 4.3 Enhanced Experiment Run Creation
```python
def create_experiment_run(
    name: str,
    project: str,
    dataset_id: str,
    configuration: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    client: Optional[HoneyHive] = None
) -> Optional[ExperimentRun]:
    """
    Create a complete experiment run with proper metadata linking.
    """
```

#### 4.4 Experiment Run Results
```python
def get_experiment_results(
    run_id: str,
    client: Optional[HoneyHive] = None
) -> Optional[ExperimentResultResponse]:
    """
    Retrieve experiment run results from HoneyHive platform.
    """
```

#### 4.5 Experiment Comparison
```python
def compare_experiments(
    run_ids: List[str],
    client: Optional[HoneyHive] = None
) -> Optional[ExperimentComparisonResponse]:
    """
    Compare multiple experiment runs for performance analysis.
    """
```

### 5. Enhanced Evaluator Framework

#### 5.1 Using Official Generated Models for Results

Instead of custom dataclasses, leverage existing generated models:

```python
# src/honeyhive/experiments/evaluators.py
from honeyhive.models.generated import (
    ExperimentResultResponse,    # For complete experiment results
    Datapoint1,                  # For individual datapoint results  
    Metrics,                     # For aggregated metrics
    Detail,                      # For individual metric details
    EvaluationRun,              # For run information
)

# Type aliases for clarity
EvaluatorResult = Detail                    # Use official Detail model for evaluator results
ExperimentRunResult = ExperimentResultResponse  # Use official response model
```

#### 5.2 Evaluator Result Processing

Process evaluator results using official models:

```python
def process_evaluator_result(
    evaluator_name: str,
    score: Union[float, int, bool, str],
    explanation: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Detail:
    """Convert evaluator output to official Detail model."""
    return Detail(
        metric_name=evaluator_name,
        value=score,
        explanation=explanation,
        metadata=metadata
    )

def aggregate_experiment_results(
    results: List[Dict[str, Any]],
    context: ExperimentContext,
    client: HoneyHive
) -> ExperimentResultResponse:
    """Aggregate individual results into official ExperimentResultResponse."""
    
    # Process individual datapoint results
    datapoint_results = []
    all_evaluator_details = []
    
    for result in results:
        if result["status"] == "success":
            # Create Datapoint1 result using official model
            datapoint_result = Datapoint1(
                datapoint_id=result["datapoint_id"],
                inputs=result["inputs"],
                outputs=result["outputs"],
                ground_truth=result.get("ground_truth"),
                passed=True,  # Determine based on evaluator results
                metrics=[
                    process_evaluator_result(
                        evaluator_name=eval_result.get("evaluator_name", "unknown"),
                        score=eval_result.get("score", 0),
                        explanation=eval_result.get("explanation")
                    )
                    for eval_result in result.get("evaluator_results", [])
                ]
            )
            datapoint_results.append(datapoint_result)
            
            # Collect all evaluator details for aggregation
            if result.get("evaluator_results"):
                all_evaluator_details.extend(result["evaluator_results"])
    
    # Create aggregated metrics using official Metrics model
    aggregate_metrics = Metrics(
        details=[
            process_evaluator_result(
                evaluator_name=detail.get("evaluator_name", "unknown"),
                score=detail.get("score", 0),
                explanation=detail.get("explanation")
            )
            for detail in all_evaluator_details
        ]
    )
    
    # Return official ExperimentResultResponse
    return ExperimentResultResponse(
        status="completed",
        success=len([r for r in results if r["status"] == "success"]) > 0,
        passed=[r["datapoint_id"] for r in results if r["status"] == "success"],
        failed=[r["datapoint_id"] for r in results if r["status"] == "failed"],
        metrics=aggregate_metrics,
        datapoints=datapoint_results
    )
```

### 6. Multi-Threading and Performance

#### 6.1 Advanced Two-Level Threading System
The experiment framework leverages the existing advanced multi-threading capabilities:

```python
def evaluate_experiment_batch(
    evaluators: List[Union[str, BaseEvaluator, Callable]],
    dataset: List[Dict[str, Any]],
    max_workers: int = 4,
    run_concurrently: bool = True,
    context: Optional[ExperimentContext] = None,
) -> List[Detail]:  # Return list of official Detail models
    """
    Evaluate experiment batch with advanced two-level threading.
    
    Level 1: Dataset parallelism (max_workers threads)
    Level 2: Evaluator parallelism within each dataset thread
    """
```

#### 6.2 Threading Architecture
- **Dataset Level**: Parallel processing of multiple datapoints
- **Evaluator Level**: Parallel execution of multiple evaluators per datapoint
- **Context Isolation**: Proper `contextvars` handling for thread safety
- **Resource Optimization**: Configurable worker counts for optimal performance

#### 6.3 Performance Characteristics
- **5x performance improvement** over single-threaded execution
- **Scalable**: Handles large datasets with multiple evaluators efficiently
- **Configurable**: Adjustable threading levels based on system capabilities
- **Thread-safe**: Advanced context isolation and error handling

#### 6.4 Threading Configuration
```python
# Example: High-performance experiment run
results = evaluate_experiment_batch(
    evaluators=["accuracy", "relevance", "coherence", "toxicity"],
    dataset=large_dataset,  # 1000+ datapoints
    max_workers=8,          # Dataset-level parallelism
    run_concurrently=True,   # Enable threading
    context=experiment_context
)
```

### 7. GitHub Integration Support

#### 7.1 GitHub Actions Integration
```python
def setup_github_experiment_workflow(
    project: str,
    dataset_id: str,
    evaluators: List[str],
    thresholds: Dict[str, float]
) -> str:
    """
    Generate GitHub Actions workflow for automated experiment runs.
    """
```

#### 7.2 Performance Thresholds
```python
def set_performance_thresholds(
    run_id: str,
    thresholds: Dict[str, float],
    client: Optional[HoneyHive] = None
) -> bool:
    """
    Set performance thresholds for experiment runs.
    """
```

## Data Model Integration

### Official HoneyHive Data Models

The implementation will use the official data models from the OpenAPI specification:

#### Experiment Results (`ExperimentResultResponse`)
```python
class ExperimentResultResponse(BaseModel):
    status: Optional[str] = None
    success: Optional[bool] = None
    passed: Optional[List[str]] = None
    failed: Optional[List[str]] = None
    metrics: Optional[Metrics] = None
    datapoints: Optional[List[Datapoint1]] = None
```

#### Experiment Comparison (`ExperimentComparisonResponse`)
```python
class ExperimentComparisonResponse(BaseModel):
    metrics: Optional[List[Metric2]] = None
    commonDatapoints: Optional[List[str]] = None
    event_details: Optional[List[EventDetail]] = None
    old_run: Optional[OldRun] = None
    new_run: Optional[NewRun] = None
```

#### Supporting Models
- **Metrics**: Aggregated metric information with details
- **Detail**: Individual metric details with aggregation
- **Datapoint1**: Individual datapoint results
- **Metric2**: Comparison-specific metric information
- **EventDetail**: Event presence and type information
- **OldRun/NewRun**: Run information for comparison

### Data Model Usage

#### Results Retrieval
```python
def get_experiment_results(run_id: str) -> Optional[ExperimentResultResponse]:
    """Retrieve results using official data model."""
    response = api.get_run(run_id)
    return response.results  # Returns ExperimentResultResponse
```

#### Results Analysis
```python
def analyze_results(results: ExperimentResultResponse) -> Dict[str, Any]:
    """Analyze results using official data structure."""
    analysis = {
        "total_metrics": len(results.metrics.details) if results.metrics else 0,
        "passed_datapoints": len(results.passed) if results.passed else 0,
        "failed_datapoints": len(results.failed) if results.failed else 0,
        "success_rate": results.success
    }
    return analysis
```

#### Comparison Analysis
```python
def analyze_comparison(comparison: ExperimentComparisonResponse) -> Dict[str, Any]:
    """Analyze comparison results using official data structure."""
    if not comparison.metrics:
        return {"error": "No comparison data"}
    
    analysis = {
        "total_metrics": len(comparison.metrics),
        "improved": sum(1 for m in comparison.metrics if m.improved_count),
        "degraded": sum(1 for m in comparison.metrics if m.degraded_count),
        "stable": sum(1 for m in comparison.metrics if m.same_count)
    }
    return analysis
```

## Same-Day Implementation Plan - Release Candidate

### Phase 1: Core Setup (Hours 0-1) - 9:00-10:00 AM
1. ✅ Create `src/honeyhive/experiments/` module structure
2. ✅ Implement backward compatibility aliases in `evaluation/`
3. ✅ Set up imports using generated models only
4. ✅ Basic ExperimentContext class implementation

### Phase 2: Core Functionality (Hours 1-3) - 10:00 AM-12:00 PM  
1. ✅ Extend tracer for experiment metadata injection
2. ✅ Implement main `evaluate()` function signature
3. ✅ Basic function execution against dataset
4. ✅ Integration with existing multi-threading capabilities

### Phase 3: Dataset & Results (Hours 3-5) - 1:00-3:00 PM
1. ✅ External dataset creation with `EXT-` prefix
2. ✅ Result aggregation using ExperimentResultResponse
3. ✅ API integration for experiment run creation
4. ✅ Backward compatibility validation

### Phase 4: Testing & Validation (Hours 5-7) - 3:00-5:00 PM
1. ✅ Unit test implementation for core functionality
2. ✅ Integration test for end-to-end workflow
3. ✅ Performance validation with existing benchmarks
4. ✅ Type safety and lint validation

### Phase 5: Documentation & Release (Hours 7-9) - 5:00-7:00 PM
1. ✅ Update existing examples to use new experiment API
2. ✅ Migration guide creation
3. ✅ API documentation updates
4. ✅ Release candidate preparation

### Parallel Tasks (Throughout Day)
- ✅ **Continuous testing**: Run test suite after each major change
- ✅ **Documentation updates**: Real-time doc updates as features complete
- ✅ **Backward compatibility**: Verify existing code works throughout

## Backward Compatibility

### Required Compatibility
- All existing evaluation decorators must continue to work
- Current API endpoints must remain functional
- Existing data models must be accessible through aliases
- Current examples must run without modification
- **Multi-threading capabilities must be preserved and enhanced**

### Migration Path
1. **Immediate**: New functionality available alongside existing
2. **Short-term**: Deprecation warnings for old terminology
3. **Long-term**: Gradual migration to new experiment framework

## Testing Requirements

### Mandatory Testing Standards Compliance

This implementation MUST follow HoneyHive Python SDK testing standards:

#### Testing Requirements - MANDATORY
- **Zero Failing Tests Policy**: ALL commits must have 100% passing tests  
- **Coverage**: Minimum 80% project-wide (enforced), 70% individual files
- **tox Orchestration**: All testing through tox environments

```bash
# Required test execution before any commit
tox -e unit           # Unit tests (MUST pass 100%)
tox -e integration    # Integration tests (MUST pass 100%)
tox -e lint          # Static analysis (MUST pass 100%)
tox -e format        # Code formatting (MUST pass 100%)
tox -e py311 -e py312 -e py313  # All Python versions (MUST pass)
```

### Unit Tests
- 100% coverage for new experiment functionality
- Backward compatibility tests for existing features
- Error handling and edge case coverage
- Data model validation tests using official models
- **Multi-threading functionality validation**
- **Main evaluate function execution testing**
- **Type hint validation for all new functions**

### Integration Tests
- End-to-end experiment run workflow
- **Function execution against dataset validation**
- Metadata linking validation
- External dataset creation and management
- API integration testing with official models
- **Multi-threading performance and thread safety tests**

### Performance Tests
- Large dataset handling (1000+ datapoints)
- Concurrent experiment runs  
- Memory usage optimization
- **Multi-threading scalability testing**
- **Thread safety validation under load**
- **Function execution performance under load**

## Standards Compliance

### Technical Requirements Alignment

This specification aligns with all HoneyHive Python SDK technical standards:

#### Python & Type Safety
- **Python 3.11+**: Full compatibility with supported versions (3.11, 3.12, 3.13)
- **Type Hints**: ALL functions, methods, and class attributes properly typed
- **Enum Usage**: Proper EventType enum usage in all documentation examples
- **Import Validation**: Complete imports in all code examples
- **Mypy Compliance**: All examples pass mypy validation

#### Code Quality Standards
- **Black Formatting**: 88-character lines, automatic formatting
- **isort**: Import sorting with black profile
- **Pylint**: Static analysis compliance
- **Pre-commit**: Automated quality enforcement

#### Documentation Standards  
- **Divio System**: Follows TUTORIAL/HOW-TO/REFERENCE/EXPLANATION structure
- **Working Examples**: All code examples tested and functional
- **Type Safety**: EventType enums, complete imports, mypy validation
- **Accessibility**: WCAG 2.1 AA compliance

#### API Design Standards
- **OpenAPI 3.0**: Full specification compliance
- **REST Principles**: RESTful API design
- **Pydantic Models**: Request/response validation using official models
- **OpenTelemetry**: W3C trace context standard compliance

### Environment & Configuration
- **Environment Variables**: HH_* prefix convention maintained
- **Configuration Hierarchy**: Constructor > Env > Defaults pattern
- **Graceful Degradation**: No failures when HoneyHive API unavailable

### Migration Strategy

#### Backwards Compatibility Requirements
- All existing evaluation decorators continue working
- Current API endpoints remain functional  
- Existing data models accessible through aliases
- Current examples run without modification
- **Multi-threading capabilities preserved and enhanced**

#### Rollout Plan
1. **Alpha**: Internal testing with new experiment framework
2. **Beta**: Select user testing with feature flags
3. **GA**: Full release with migration documentation
4. **Deprecation**: Gradual phase-out of old terminology (12+ months)

## Documentation Updates

### Required Documentation
1. **Migration Guide**: From evaluation to experiment framework
2. **Experiment Tutorials**: Complete workflow examples
3. **API Reference**: Updated with new terminology and data models
4. **Integration Guides**: GitHub Actions and CI/CD setup
5. **Performance Guide**: Multi-threading configuration and optimization

### Documentation Standards
- Follow Divio documentation system
- Include working code examples
- Provide step-by-step tutorials
- Include troubleshooting guides
- **Document multi-threading best practices and configuration**

## Success Criteria

### Functional Requirements
- [ ] All experiment terminology properly implemented
- [ ] Metadata linking working on all traced events
- [ ] Client-side dataset support functional
- [ ] **Main evaluate function executes user functions against datasets**
- [ ] Experiment run management complete
- [ ] GitHub integration working
- [ ] Backward compatibility maintained
- [ ] Official data models properly integrated
- [ ] **Advanced multi-threading capabilities preserved and enhanced**

### Quality Requirements
- [ ] 100% test coverage for new experiment functionality
- [ ] All tests passing across Python versions
- [ ] Documentation complete and accurate
- [ ] Performance benchmarks met
- [ ] Security review completed
- [ ] **Multi-threading performance validated**

### User Experience Requirements
- [ ] Smooth migration path for existing users
- [ ] Clear examples and tutorials
- [ ] Intuitive API design
- [ ] Comprehensive error messages
- [ ] Performance monitoring and alerts
- [ ] **Multi-threading configuration guidance**

## Risk Assessment

### High Risk
- **Breaking Changes**: Potential for breaking existing integrations
- **Performance Impact**: Metadata injection on all events
- **Complexity**: Increased complexity of experiment management
- **Multi-threading**: Ensuring thread safety in complex scenarios
- **Function Execution**: Ensuring user functions execute safely and efficiently

### Mitigation Strategies
- **Gradual Migration**: Phased implementation with backward compatibility
- **Performance Testing**: Comprehensive benchmarking before release
- **User Feedback**: Early access program for key users
- **Thread Safety**: Comprehensive testing of multi-threading scenarios
- **Function Safety**: Sandboxed execution and comprehensive error handling

## Dependencies

### Internal Dependencies
- Tracer framework updates
- API client enhancements
- Data model modifications
- Test framework updates
- **Multi-threading framework preservation**

### External Dependencies
- HoneyHive platform API compatibility
- GitHub Actions integration
- Performance monitoring tools

## Timeline

Same-day implementation (10.25-hour critical path):

- **Hours 0-3**: Core terminology and metadata linking (Phases 1-2)
- **Hours 3-7**: Dataset support and experiment management (Phases 3-4)  
- **Hours 7-9**: GitHub integration (Phase 5)
- **Hours 9-10.25**: Testing, documentation, and release preparation (Phase 6)

## Next Steps

1. **Immediate**: Begin Phase 1 module structure setup
2. **Hour 1**: Complete core module refactoring and begin tracer integration
3. **Ongoing**: Continuous testing and validation throughout implementation
4. **Hour 10**: Final testing and release candidate preparation

---

**Document Version**: 1.0  
**Last Updated**: 2025-09-04  
**Next Review**: 2025-09-10
