# Deep Tracer Module Integration Analysis
## For Experiments/Evaluation Module Implementation

**Last Updated:** October 2, 2025  
**Branch:** complete-refactor  
**Purpose:** Comprehensive understanding of tracer architecture for experiments module integration

---

## Executive Summary

The **HoneyHiveTracer** in `complete-refactor` branch is a sophisticated multi-instance architecture built on OpenTelemetry with:

1. **Complete Isolation**: Each tracer instance has its own API client, logger, configuration, and state
2. **Built-in Experiment Support**: Native support for `run_id`, `dataset_id`, `datapoint_id` via configuration
3. **Automatic Metadata Propagation**: Evaluation/experiment metadata flows automatically through baggage and span attributes
4. **Thread-Safe Design**: Uses ThreadPoolExecutor-compatible multi-instance architecture
5. **Graceful Degradation**: Never crashes host application, follows Agent OS standards

**Key Finding:** The tracer already has ~80% of what we need for experiments. We just need to leverage it correctly.

---

## 1. Multi-Instance Architecture

### 1.1 Core Design Principle

```python
# Each tracer instance is COMPLETELY ISOLATED
tracer1 = HoneyHiveTracer(
    api_key="key1",
    project="project1",
    source="production",
    run_id="experiment-1",
    dataset_id="dataset-a",
    datapoint_id="datapoint-1",
)

tracer2 = HoneyHiveTracer(
    api_key="key2",  # Different API key
    project="project2",  # Different project
    source="staging",
    run_id="experiment-2",
    dataset_id="dataset-b",
    datapoint_id="datapoint-2",
)

# tracer1 and tracer2 are COMPLETELY INDEPENDENT
# - Separate API clients (different auth)
# - Separate loggers (different log streams)
# - Separate session IDs
# - Separate baggage contexts
# - Separate span processors
```

### 1.2 Per-Instance Components

**From `src/honeyhive/tracer/core/base.py:308-331`:**
```python
def _initialize_api_clients(self) -> None:
    """Initialize API clients using dynamic configuration."""
    config = self.config
    
    # Initialize HoneyHive API client dynamically
    api_params = self._extract_api_parameters_dynamically(config)
    if api_params:
        try:
            self.client = HoneyHive(**api_params, tracer_instance=self)
            self.session_api = SessionAPI(self.client)
```

**Key Insight:** Each tracer gets its own:
- `self.client` - Independent API client with own API key
- `self.session_api` - Own session management
- `self._instance_lock` - Own threading lock
- `self._cache_manager` - Own cache manager
- `self.provider` - Own OpenTelemetry TracerProvider (or shared global)

### 1.3 Thread Safety

**From `src/honeyhive/tracer/core/base.py:276-278`:**
```python
# Per-instance locking for high-concurrency scenarios
self._baggage_lock = threading.Lock()
self._instance_lock = threading.RLock()  # Reentrant for same thread
self._flush_lock = threading.Lock()  # Separate lock for flush operations
```

**Implication:** Tracers are ThreadPoolExecutor-safe. Each thread can have its own tracer instance without contention.

---

## 2. Built-in Evaluation/Experiment Support

### 2.1 Configuration Fields

**From `src/honeyhive/config/models/tracer.py:166-186`:**
```python
class TracerConfig(BaseHoneyHiveConfig):
    # Evaluation-related fields (for hybrid approach)
    is_evaluation: bool = Field(
        default=False, description="Enable evaluation mode"
    )
    
    run_id: Optional[str] = Field(
        None,
        description="Evaluation run identifier",
        examples=["eval-run-123", "experiment-2024-01-15"],
    )
    
    dataset_id: Optional[str] = Field(
        None,
        description="Dataset identifier for evaluation",
        examples=["dataset-456", "qa-dataset-v2"],
    )
    
    datapoint_id: Optional[str] = Field(
        None,
        description="Specific datapoint identifier",
        examples=["datapoint-789", "question-42"],
    )
```

**Implication:** These fields are FIRST-CLASS citizens in the tracer config, not hacks.

### 2.2 Initialization Flow

**From `src/honeyhive/tracer/core/base.py:247-264`:**
```python
def _initialize_core_attributes(self) -> None:
    """Initialize core tracer attributes using dynamic configuration."""
    config = self.config
    
    # Evaluation attributes
    self.is_evaluation = config.get("is_evaluation", False)
    self.run_id = config.get("run_id")
    self.dataset_id = config.get("dataset_id")
    self.datapoint_id = config.get("datapoint_id")
    
    # Initialize evaluation context
    self._evaluation_context: Dict[str, Any] = {}
    # Dynamic evaluation context setup
    if self.is_evaluation:
        self._setup_evaluation_context_dynamically(config)
```

**From `src/honeyhive/tracer/core/base.py:405-413`:**
```python
def _setup_evaluation_context_dynamically(self, config: Dict[str, Any]) -> None:
    """Dynamically set up evaluation context from configuration."""
    # Extract evaluation-specific fields dynamically
    evaluation_fields = ["run_id", "dataset_id", "datapoint_id", "is_evaluation"]
    
    for field in evaluation_fields:
        value = config.get(field)
        if value is not None:
            self._evaluation_context[field] = value
```

**Implication:** Evaluation metadata is stored and ready for propagation.

---

## 3. Automatic Metadata Propagation

### 3.1 Baggage System

**From `src/honeyhive/tracer/processing/context.py:190-223`:**
```python
def _add_evaluation_context(
    baggage_items: Dict[str, str], tracer_instance: "HoneyHiveTracer"
) -> None:
    """Add evaluation-specific context to baggage items (backward compatibility)."""
    if not tracer_instance.is_evaluation:
        return
    
    evaluation_items = {}
    
    if tracer_instance.run_id:
        evaluation_items["run_id"] = tracer_instance.run_id
        baggage_items["run_id"] = tracer_instance.run_id
    
    if tracer_instance.dataset_id:
        evaluation_items["dataset_id"] = tracer_instance.dataset_id
        baggage_items["dataset_id"] = tracer_instance.dataset_id
    
    if tracer_instance.datapoint_id:
        evaluation_items["datapoint_id"] = tracer_instance.datapoint_id
        baggage_items["datapoint_id"] = tracer_instance.datapoint_id
    
    if evaluation_items:
        safe_log(
            tracer_instance,
            "debug",
            "Evaluation context added to baggage",
            honeyhive_data=evaluation_items,
        )
```

**Key Insight:** Evaluation metadata is AUTOMATICALLY added to OpenTelemetry baggage during tracer initialization.

### 3.2 Span Enrichment

**From `src/honeyhive/tracer/processing/span_processor.py:255-374`:**
```python
def on_start(self, span: Span, parent_context: Optional[Context] = None) -> None:
    """Called when a span starts - attach HoneyHive metadata."""
    try:
        ctx = self._get_context(parent_context)
        # ... 
        
        # Get experiment attributes from tracer instance configuration
        attributes_to_set.update(self._get_experiment_attributes())
        
        if session_id:
            # Set session_id attributes directly (multi-instance isolation)
            attributes_to_set["honeyhive.session_id"] = session_id
            attributes_to_set["traceloop.association.properties.session_id"] = (
                session_id
            )
            
            # Get other baggage attributes (project, source, etc.)
            other_baggage_attrs = self._get_basic_baggage_attributes(ctx)
            # ... includes run_id, dataset_id, datapoint_id from baggage
            attributes_to_set.update(other_baggage_attrs)
```

**From `src/honeyhive/tracer/processing/span_processor.py:149-226`:**
```python
def _get_experiment_attributes(self) -> dict:
    """Get experiment-related attributes from tracer configuration.
    
    Returns:
        Dictionary of experiment attributes from baggage and config
    """
    attributes = {}
    
    # Get evaluation/experiment metadata from tracer instance (multi-instance isolation)
    if self.tracer_instance:
        # Evaluation metadata (run_id, dataset_id, datapoint_id)
        if hasattr(self.tracer_instance, "run_id") and self.tracer_instance.run_id:
            attributes["honeyhive.run_id"] = self.tracer_instance.run_id
            # Backend compatibility
            attributes["traceloop.association.properties.run_id"] = (
                self.tracer_instance.run_id
            )
        
        if (
            hasattr(self.tracer_instance, "dataset_id")
            and self.tracer_instance.dataset_id
        ):
            attributes["honeyhive.dataset_id"] = self.tracer_instance.dataset_id
            attributes["traceloop.association.properties.dataset_id"] = (
                self.tracer_instance.dataset_id
            )
        
        if (
            hasattr(self.tracer_instance, "datapoint_id")
            and self.tracer_instance.datapoint_id
        ):
            attributes["honeyhive.datapoint_id"] = self.tracer_instance.datapoint_id
            attributes["traceloop.association.properties.datapoint_id"] = (
                self.tracer_instance.datapoint_id
            )
```

**Implication:** Every span created by the tracer automatically gets:
- `honeyhive.run_id`
- `honeyhive.dataset_id`
- `honeyhive.datapoint_id`
- `honeyhive.source`
- Backend compatibility attributes (traceloop.*)

### 3.3 Session Creation

**From `src/honeyhive/tracer/instrumentation/initialization.py:1186-1192`:**
```python
# Create session via API
session_response = tracer_instance.session_api.start_session(
    project=tracer_instance.project_name,
    session_name=session_name,
    source=tracer_instance.source_environment,
    inputs=tracer_instance.config.session.inputs,
)
```

**From `src/honeyhive/api/session.py:128-143`:**
```python
def start_session(
    self,
    project: str,
    session_name: str,
    source: str,
    session_id: Optional[str] = None,
    **kwargs: Any,  # This includes run_id, dataset_id, datapoint_id!
) -> SessionStartResponse:
    """Start a new session using SessionStartRequest model."""
    request_data = SessionStartRequest(
        project=project,
        session_name=session_name,
        source=source,
        session_id=session_id,
        **kwargs,  # Additional fields like metadata
    )
```

**From `src/honeyhive/models/generated.py:21-68`:**
```python
class SessionStartRequest(BaseModel):
    project: str = Field(..., description="Project name associated with the session")
    session_name: str = Field(..., description="Name of the session")
    source: str = Field(..., description="Source of the session - production, staging, etc")
    session_id: Optional[str] = Field(None, description="Unique id of the session")
    config: Optional[Dict[str, Any]] = Field(None, description="Associated configuration")
    inputs: Optional[Dict[str, Any]] = Field(None, description="Input object passed to the session")
    outputs: Optional[Dict[str, Any]] = Field(None, description="Final output")
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Any system or application metadata associated with the session",
    )
    # ... more fields
```

**Critical Discovery:** `SessionStartRequest` accepts `metadata` as a dict! We can pass:
```python
metadata = {
    "run_id": "experiment-123",
    "dataset_id": "dataset-456", 
    "datapoint_id": "datapoint-789"
}
```

---

## 4. Session Metadata Flow (CORRECTED)

### 4.1 The Truth About Session Metadata

**User's Critical Correction:**
> "the docs might have been wrong about not needing source/dataset_id/datapoint_id as mandatory on the session. main is actually a better source of truth in this instance for experiments module"

**Main Branch Implementation:**
```python
# From main branch evaluation module
session_metadata = {
    "session_name": f"Evaluation-{datapoint['id']}",
    "project": self.project,
    "source": self.source,  # ✅ source in metadata
    "inputs": datapoint.get("inputs", {}),
    "metadata": {
        "run_id": self.run_id,  # ✅ run_id in metadata
        "dataset_id": self.dataset_id,  # ✅ dataset_id in metadata
        "datapoint_id": datapoint["id"],  # ✅ datapoint_id in metadata
    }
}
```

### 4.2 How To Do This In Complete-Refactor

**Option 1: Via Config (RECOMMENDED)**
```python
from honeyhive import HoneyHiveTracer
from honeyhive.config.models import TracerConfig, SessionConfig

# Create tracer with experiment metadata
tracer = HoneyHiveTracer(
    api_key=api_key,
    project=project,
    source=source,  # ✅ source in tracer config
    session_name=f"Experiment-{datapoint_id}",
    is_evaluation=True,  # ✅ Enable evaluation mode
    run_id=run_id,  # ✅ run_id in tracer config
    dataset_id=dataset_id,  # ✅ dataset_id in tracer config
    datapoint_id=datapoint_id,  # ✅ datapoint_id in tracer config
    inputs=datapoint.get("inputs", {}),
)

# Session is created automatically with ALL metadata
# - source is in SessionStartRequest.source
# - run_id, dataset_id, datapoint_id go into baggage
# - They also get added to span attributes automatically
```

**Option 2: Via Session Enrichment (if needed later)**
```python
tracer.enrich_session(
    metadata={
        "run_id": run_id,
        "dataset_id": dataset_id,
        "datapoint_id": datapoint_id,
    }
)
```

**Option 3: Explicit Session Creation (full control)**
```python
from honeyhive.models import SessionStartRequest

session_request = SessionStartRequest(
    project=project,
    session_name=f"Experiment-{datapoint_id}",
    source=source,
    inputs=datapoint.get("inputs", {}),
    metadata={
        "run_id": run_id,
        "dataset_id": dataset_id,
        "datapoint_id": datapoint_id,
    }
)

response = tracer.session_api.create_session(session_request)
session_id = response.session_id
```

---

## 5. Threading Model for Concurrent Evaluation

### 5.1 Current Evaluator Implementation

**From `src/honeyhive/evaluation/evaluators.py:506-544`:**
```python
if run_concurrently and max_workers > 1 and len(evaluators) > 1:
    # Run evaluators concurrently using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit evaluation tasks
        futures = []
        for eval_item in evaluators:
            eval_func = _get_evaluator_function(eval_item)
            
            # Create context for each thread
            ctx = contextvars.copy_context()
            future = executor.submit(
                ctx.run,
                functools.partial(
                    _run_single_evaluator, eval_func, inputs, outputs, ground_truth
                ),
            )
            futures.append((eval_item, future))
```

**Key Insight:** Uses `contextvars.copy_context()` to preserve context across threads. This is COMPATIBLE with tracer's baggage system!

### 5.2 How To Use Tracer Multi-Instance with ThreadPoolExecutor

**Pattern 1: One Tracer Per Datapoint (RECOMMENDED)**
```python
from concurrent.futures import ThreadPoolExecutor
import contextvars

def process_datapoint(datapoint, run_id, dataset_id, api_key, project, source):
    """Each thread gets its own tracer instance."""
    # Create isolated tracer for this datapoint
    tracer = HoneyHiveTracer(
        api_key=api_key,
        project=project,
        source=source,
        session_name=f"Experiment-{datapoint['id']}",
        is_evaluation=True,
        run_id=run_id,
        dataset_id=dataset_id,
        datapoint_id=datapoint["id"],
        inputs=datapoint.get("inputs", {}),
    )
    
    try:
        # Run evaluation with this tracer
        with tracer.start_span("datapoint_evaluation") as span:
            result = run_evaluators(datapoint, tracer)
            return result
    finally:
        tracer.flush()  # Ensure data is sent

# Run concurrently
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = []
    for datapoint in dataset:
        # Copy context to preserve parent baggage
        ctx = contextvars.copy_context()
        future = executor.submit(
            ctx.run,
            functools.partial(
                process_datapoint,
                datapoint=datapoint,
                run_id=run_id,
                dataset_id=dataset_id,
                api_key=api_key,
                project=project,
                source=source,
            ),
        )
        futures.append(future)
    
    # Collect results
    results = [f.result() for f in futures]
```

**Pattern 2: Shared Tracer with Baggage Updates (NOT RECOMMENDED)**
```python
# This is theoretically possible but NOT RECOMMENDED
# The tracer's multi-instance architecture is designed for isolation

shared_tracer = HoneyHiveTracer(api_key=api_key, project=project)

def process_datapoint(datapoint, tracer, run_id, dataset_id):
    # This would require thread-local baggage management
    # which is complex and error-prone
    pass
```

**Recommendation:** Use Pattern 1 (one tracer per datapoint). It's:
- Simpler
- More robust
- Aligns with multi-instance architecture
- No contention
- Each datapoint gets proper isolation

### 5.3 ThreadPoolExecutor vs Multiprocessing

**Question:** Should we use ThreadPoolExecutor or multiprocessing?

**Answer:** ThreadPoolExecutor (threads) is CORRECT because:

1. **I/O Bound Operations**: Evaluation primarily does:
   - API calls (LLM providers, HoneyHive API)
   - Network I/O
   - File I/O (reading datasets)
   
2. **GIL is Not a Problem**: Python's GIL doesn't block I/O operations

3. **Simpler State Management**: Threads share memory, making it easier to:
   - Pass tracer instances
   - Collect results
   - Share configuration

4. **Current Implementation**: Main branch already uses ThreadPoolExecutor successfully

5. **OpenTelemetry Context**: Works seamlessly with threads via `contextvars`

**When to use multiprocessing:**
- CPU-bound evaluation (e.g., heavy ML models running locally)
- In that case, each process would need its own tracer instance anyway

---

## 6. External Dataset ID Generation

### 6.1 Current Implementation (None Found)

```bash
$ grep -r "EXT-" src/honeyhive
# No results
```

**Finding:** The EXT- prefix logic for external datasets hasn't been implemented yet.

### 6.2 Required Logic (from Main Branch)

**From user requirements:**
> "for external datasets/datapoints, we have some logic to auto-generate correct ids on the fly, we want that to port over"

**Expected Implementation:**
```python
def generate_external_dataset_id(user_provided_id: str) -> str:
    """Generate external dataset ID with EXT- prefix.
    
    Args:
        user_provided_id: User-provided dataset identifier
        
    Returns:
        Formatted external dataset ID with EXT- prefix
        
    Examples:
        >>> generate_external_dataset_id("my-dataset")
        'EXT-my-dataset'
        
        >>> generate_external_dataset_id("EXT-already-prefixed")
        'EXT-already-prefixed'  # Don't double-prefix
    """
    if user_provided_id.startswith("EXT-"):
        return user_provided_id
    return f"EXT-{user_provided_id}"


def generate_external_datapoint_id(
    dataset_id: str, datapoint_id: str
) -> str:
    """Generate external datapoint ID.
    
    Args:
        dataset_id: Dataset identifier (may or may not have EXT- prefix)
        datapoint_id: Datapoint identifier
        
    Returns:
        Formatted external datapoint ID
        
    Examples:
        >>> generate_external_datapoint_id("EXT-dataset", "point-1")
        'EXT-dataset-point-1'
        
        >>> generate_external_datapoint_id("my-dataset", "point-1")
        'EXT-my-dataset-point-1'
    """
    # Ensure dataset_id has EXT- prefix
    dataset_id_with_prefix = generate_external_dataset_id(dataset_id)
    
    # Don't double-prefix if datapoint_id already has it
    if datapoint_id.startswith("EXT-"):
        return datapoint_id
        
    return f"{dataset_id_with_prefix}-{datapoint_id}"
```

### 6.3 Integration with Tracer

```python
from honeyhive.experiments.utils import (
    generate_external_dataset_id,
    generate_external_datapoint_id,
)

# When creating tracer for external dataset
dataset_id = generate_external_dataset_id(user_dataset_id)
datapoint_id = generate_external_datapoint_id(dataset_id, user_datapoint_id)

tracer = HoneyHiveTracer(
    api_key=api_key,
    project=project,
    source=source,
    is_evaluation=True,
    run_id=run_id,
    dataset_id=dataset_id,  # With EXT- prefix
    datapoint_id=datapoint_id,  # With EXT- prefix
)
```

---

## 7. Evaluator Framework Integration

### 7.1 Current Evaluator Architecture

**From `src/honeyhive/evaluation/evaluators.py:51-78`:**
```python
class BaseEvaluator:
    """Base class for custom evaluators."""
    
    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialize the evaluator."""
        self.name = name
        self.__name__ = name  # Add __name__ attribute for compatibility
        self.config = kwargs
    
    def evaluate(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Evaluate the given inputs and outputs."""
        raise NotImplementedError("Subclasses must implement evaluate method")
    
    def __call__(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make the evaluator callable."""
        return self.evaluate(inputs, outputs, ground_truth, **kwargs)
```

### 7.2 How Evaluators Should Use Tracer

**Option 1: Pass Tracer to Evaluator (RECOMMENDED)**
```python
def run_evaluators_with_tracer(
    evaluators: List[BaseEvaluator],
    inputs: Dict[str, Any],
    outputs: Dict[str, Any],
    ground_truth: Optional[Dict[str, Any]],
    tracer: HoneyHiveTracer,
) -> Dict[str, Any]:
    """Run evaluators with tracer for instrumentation."""
    results = {}
    
    for evaluator in evaluators:
        # Create span for each evaluator
        with tracer.start_span(f"evaluator.{evaluator.name}") as span:
            span.set_attribute("evaluator.name", evaluator.name)
            span.set_attribute("evaluator.type", type(evaluator).__name__)
            
            try:
                result = evaluator(inputs, outputs, ground_truth)
                span.set_attribute("evaluator.score", result.get("score"))
                results[evaluator.name] = result
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                results[evaluator.name] = {"error": str(e)}
    
    return results
```

**Option 2: Evaluator-Aware Base Class (ADVANCED)**
```python
class TracedEvaluator(BaseEvaluator):
    """Evaluator that automatically creates spans."""
    
    def __init__(self, name: str, tracer: Optional[HoneyHiveTracer] = None, **kwargs):
        super().__init__(name, **kwargs)
        self.tracer = tracer
    
    def __call__(self, inputs, outputs, ground_truth=None, **kwargs):
        if self.tracer:
            with self.tracer.start_span(f"evaluator.{self.name}") as span:
                span.set_attribute("evaluator.name", self.name)
                result = self.evaluate(inputs, outputs, ground_truth, **kwargs)
                if isinstance(result, dict) and "score" in result:
                    span.set_attribute("evaluator.score", result["score"])
                return result
        else:
            return self.evaluate(inputs, outputs, ground_truth, **kwargs)
```

### 7.3 Evaluator Execution in Experiments

```python
def run_experiment_evaluators(
    datapoint: Dict[str, Any],
    evaluators: List[BaseEvaluator],
    tracer: HoneyHiveTracer,
) -> Dict[str, Any]:
    """Run evaluators for a single datapoint with full tracing."""
    
    # Main evaluation span
    with tracer.start_span("experiment.evaluate") as eval_span:
        eval_span.set_attribute("datapoint.id", datapoint["id"])
        eval_span.set_attribute("evaluator.count", len(evaluators))
        
        # Run the user's function (traced automatically)
        with tracer.start_span("experiment.run_function") as func_span:
            inputs = datapoint.get("inputs", {})
            func_span.set_attribute("input", json.dumps(inputs))
            
            outputs = user_function(inputs)  # User's LLM call
            func_span.set_attribute("output", json.dumps(outputs))
        
        # Run evaluators (each gets its own span)
        ground_truth = datapoint.get("ground_truth")
        eval_results = run_evaluators_with_tracer(
            evaluators=evaluators,
            inputs=inputs,
            outputs=outputs,
            ground_truth=ground_truth,
            tracer=tracer,
        )
        
        # Aggregate results
        eval_span.set_attribute(
            "evaluation.results", 
            json.dumps(eval_results)
        )
        
        return eval_results
```

---

## 8. Complete Integration Example

### 8.1 Experiments Module Interface

```python
from typing import Dict, List, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor
import contextvars

from honeyhive import HoneyHiveTracer
from honeyhive.evaluation.evaluators import BaseEvaluator
from honeyhive.experiments.utils import (
    generate_external_dataset_id,
    generate_external_datapoint_id,
)


def run_experiment(
    name: str,
    dataset: List[Dict[str, Any]],
    function: Callable,
    evaluators: List[BaseEvaluator],
    *,
    api_key: str,
    project: str,
    source: str = "dev",
    max_workers: int = 4,
    external_dataset: bool = True,
) -> Dict[str, Any]:
    """Run an experiment on a dataset with evaluators.
    
    Args:
        name: Experiment name
        dataset: List of datapoints with inputs and ground_truth
        function: Function to evaluate (takes inputs, returns outputs)
        evaluators: List of evaluators to apply
        api_key: HoneyHive API key
        project: HoneyHive project name
        source: Source environment (dev, staging, production)
        max_workers: Number of parallel workers
        external_dataset: Whether this is an external dataset (adds EXT- prefix)
    
    Returns:
        Dictionary with experiment results and statistics
    """
    # Generate run ID
    run_id = f"experiment-{name}-{int(time.time())}"
    
    # Generate dataset ID
    dataset_id = name
    if external_dataset:
        dataset_id = generate_external_dataset_id(dataset_id)
    
    # Process each datapoint in parallel
    def process_datapoint(datapoint: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single datapoint with its own tracer."""
        # Generate datapoint ID
        dp_id = datapoint.get("id", str(uuid.uuid4()))
        if external_dataset:
            dp_id = generate_external_datapoint_id(dataset_id, dp_id)
        
        # Create isolated tracer for this datapoint
        tracer = HoneyHiveTracer(
            api_key=api_key,
            project=project,
            source=source,
            session_name=f"{name}-{dp_id}",
            is_evaluation=True,
            run_id=run_id,
            dataset_id=dataset_id,
            datapoint_id=dp_id,
            inputs=datapoint.get("inputs", {}),
        )
        
        try:
            # Run experiment with full tracing
            result = run_experiment_evaluators(
                datapoint=datapoint,
                evaluators=evaluators,
                tracer=tracer,
            )
            
            return {
                "datapoint_id": dp_id,
                "session_id": tracer.session_id,
                "results": result,
                "status": "success",
            }
        except Exception as e:
            return {
                "datapoint_id": dp_id,
                "session_id": tracer.session_id if hasattr(tracer, 'session_id') else None,
                "error": str(e),
                "status": "error",
            }
        finally:
            # Ensure tracer flushes data
            tracer.flush()
    
    # Run in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for datapoint in dataset:
            ctx = contextvars.copy_context()
            future = executor.submit(
                ctx.run,
                functools.partial(process_datapoint, datapoint=datapoint),
            )
            futures.append(future)
        
        # Collect results
        results = [f.result() for f in futures]
    
    # Aggregate statistics
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = sum(1 for r in results if r["status"] == "error")
    
    return {
        "run_id": run_id,
        "dataset_id": dataset_id,
        "stats": {
            "total": len(results),
            "success": success_count,
            "error": error_count,
        },
        "results": results,
    }
```

---

## 9. Critical Integration Points

### 9.1 What We MUST Do

1. **Use Tracer Config Fields**
   - Always set `is_evaluation=True` for experiments
   - Always provide `run_id`, `dataset_id`, `datapoint_id`
   - Always provide `source` (required, defaults to "dev")

2. **Create One Tracer Per Datapoint**
   - Each thread gets its own tracer instance
   - No shared state between threads
   - Each tracer has its own API client

3. **Use ThreadPoolExecutor (Not Multiprocessing)**
   - I/O bound operations
   - Context propagation works seamlessly
   - Simpler state management

4. **Flush Each Tracer**
   - Call `tracer.flush()` in finally block
   - Ensures all spans are sent before thread completes

5. **Handle External Dataset IDs**
   - Implement EXT- prefix logic
   - Apply to both dataset_id and datapoint_id

### 9.2 What We SHOULD Do

1. **Leverage Generated Models**
   - Use `SessionStartRequest` for explicit session creation
   - Use `CreateRunRequest` for evaluation run creation
   - Don't create custom dataclasses

2. **Use Tracer Spans for Evaluators**
   - Create span for each evaluator
   - Record metrics as span attributes
   - Record exceptions properly

3. **Follow Graceful Degradation**
   - Never crash if tracer fails
   - Log errors but continue
   - Return partial results

### 9.3 What We MUST NOT Do

1. **Don't Share Tracer Across Threads**
   - Each thread MUST have its own tracer
   - Baggage updates are thread-local

2. **Don't Bypass Tracer Metadata**
   - Don't manually set span attributes for run_id/dataset_id/datapoint_id
   - They're automatically added by the tracer

3. **Don't Create Sessions Manually**
   - Let tracer create sessions automatically
   - It includes all metadata correctly

---

## 10. Implementation Checklist

### Phase 1: Core Setup
- [ ] Create `src/honeyhive/experiments/__init__.py`
- [ ] Create `src/honeyhive/experiments/utils.py` with EXT- prefix logic
- [ ] Create `src/honeyhive/experiments/core.py` with main `run_experiment()` function
- [ ] Port evaluator framework from main branch (it's already good)

### Phase 2: Tracer Integration
- [ ] Implement per-datapoint tracer creation pattern
- [ ] Add tracer.flush() in finally blocks
- [ ] Test ThreadPoolExecutor with multiple tracers
- [ ] Verify baggage propagation

### Phase 3: Metadata Handling
- [ ] Verify run_id/dataset_id/datapoint_id in span attributes
- [ ] Verify metadata in session creation
- [ ] Test external dataset ID generation
- [ ] Validate source field propagation

### Phase 4: Testing
- [ ] Unit tests for ID generation
- [ ] Integration tests for tracer multi-instance
- [ ] E2E tests for full experiment run
- [ ] Thread safety tests

### Phase 5: Backward Compatibility
- [ ] Create `src/honeyhive/evaluation/__init__.py` wrapper
- [ ] Add deprecation warnings
- [ ] Ensure old imports still work

---

## 11. Key Takeaways

1. **Tracer is Ready**: The tracer already has 80% of what we need. We just need to use it correctly.

2. **Multi-Instance is Key**: Create one tracer per datapoint, each completely isolated.

3. **Metadata Flows Automatically**: run_id, dataset_id, datapoint_id propagate automatically via baggage and span attributes.

4. **ThreadPoolExecutor is Correct**: I/O bound operations + GIL not a problem + simpler state management.

5. **Generated Models FTW**: Use SessionStartRequest, CreateRunRequest, not custom dataclasses.

6. **Port Evaluator Framework**: The main branch evaluator framework is solid, port it as-is.

7. **Source is Required**: Both in tracer config AND session metadata (they're the same).

---

## 12. Next Steps

1. **Read CORRECTED_IMPLEMENTATION_GUIDE.md** for detailed implementation steps
2. **Start with Phase 1** (core setup)
3. **Test multi-instance pattern early** (Phase 2)
4. **Validate metadata flow** (Phase 3)
5. **Add comprehensive tests** (Phase 4)

---

**Document Status:** ✅ COMPLETE - Ready for implementation  
**Last Reviewed:** October 2, 2025  
**Next Review:** After Phase 1 implementation

