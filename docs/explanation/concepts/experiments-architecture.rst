Experiments Architecture
========================

.. note::
   This document explains how experiments work in HoneyHive, including the execution flow, component relationships, and evaluation lifecycle.

What are Experiments?
---------------------

Experiments in HoneyHive are systematic evaluations of LLM applications that help you:

- **Test changes** to prompts, models, or application logic
- **Measure quality** with automated evaluators
- **Compare performance** across different versions
- **Track improvements** over time

Unlike simple tracing (which captures *what happened*), experiments evaluate *how well it happened*.

**Key Distinction:**

.. code-block:: text

   Tracing:
   ✓ Captured 1000 requests
   ✓ Average latency: 2.3s
   ✓ Token usage: 450K tokens
   
   Experiments:
   ✓ Accuracy: 87% (improved from 82%)
   ✓ User satisfaction: 4.2/5
   ✓ Cost per quality response: $0.03 (down from $0.05)
   ✓ Which prompt works better? (A vs B)

How Experiments Work
--------------------

The Experiment Lifecycle
~~~~~~~~~~~~~~~~~~~~~~~~

An experiment follows a clear execution path:

.. code-block:: text

   1. Setup Phase
      └─→ Load dataset (code-defined or HoneyHive-managed)
      └─→ Initialize tracer for each datapoint
      └─→ Prepare evaluators
   
   2. Execution Phase (for each datapoint)
      └─→ Create isolated tracer instance
      └─→ Call evaluation function with datapoint
      └─→ Capture traces automatically
      └─→ Collect function outputs
   
   3. Evaluation Phase (for each datapoint)
      └─→ Run evaluators on outputs
      └─→ Compute metrics
      └─→ Send results to backend
   
   4. Aggregation Phase (backend)
      └─→ Aggregate metrics across all datapoints
      └─→ Generate run statistics
      └─→ Enable comparison with other runs

**Visual Flow:**

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#ffffff', 'lineColor': '#ffffff', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'tertiaryColor': 'transparent', 'clusterBkg': 'transparent', 'clusterBorder': '#ffffff', 'edgeLabelBackground': 'transparent', 'background': 'transparent'}, 'flowchart': {'linkColor': '#ffffff', 'linkWidth': 2}}}%%
   graph TB
       subgraph "1. Setup"
           DS[Dataset<br/>inputs + ground_truth]
           FUNC[Evaluation Function<br/>Your LLM logic]
           EVALS[Evaluators<br/>Quality checks]
       end
       
       subgraph "2. Per-Datapoint Execution"
           TRACER[Isolated Tracer<br/>Multi-instance]
           EXEC[Execute Function<br/>datapoint → outputs]
           TRACE[Capture Traces<br/>spans + metrics]
       end
       
       subgraph "3. Per-Datapoint Evaluation"
           RUN_EVAL[Run Evaluators<br/>outputs + ground_truth]
           METRICS[Compute Metrics<br/>scores + metadata]
       end
       
       subgraph "4. Backend Aggregation"
           SEND[Send to Backend<br/>HoneyHive API]
           AGG[Aggregate Results<br/>across datapoints]
           STORE[Store Run Results<br/>with metrics]
       end
       
       DS --> EXEC
       FUNC --> EXEC
       TRACER --> EXEC
       EXEC --> TRACE
       TRACE --> RUN_EVAL
       EVALS --> RUN_EVAL
       RUN_EVAL --> METRICS
       METRICS --> SEND
       SEND --> AGG
       AGG --> STORE
       
       style DS fill:#1b5e20,stroke:#ffffff,stroke-width:2px,color:#ffffff
       style FUNC fill:#1b5e20,stroke:#ffffff,stroke-width:2px,color:#ffffff
       style EVALS fill:#1b5e20,stroke:#ffffff,stroke-width:2px,color:#ffffff
       style TRACER fill:#01579b,stroke:#ffffff,stroke-width:2px,color:#ffffff
       style EXEC fill:#01579b,stroke:#ffffff,stroke-width:2px,color:#ffffff
       style TRACE fill:#01579b,stroke:#ffffff,stroke-width:2px,color:#ffffff
       style RUN_EVAL fill:#e65100,stroke:#ffffff,stroke-width:2px,color:#ffffff
       style METRICS fill:#e65100,stroke:#ffffff,stroke-width:2px,color:#ffffff
       style SEND fill:#4a148c,stroke:#ffffff,stroke-width:2px,color:#ffffff
       style AGG fill:#4a148c,stroke:#ffffff,stroke-width:2px,color:#ffffff
       style STORE fill:#4a148c,stroke:#ffffff,stroke-width:2px,color:#ffffff

Component Relationships
~~~~~~~~~~~~~~~~~~~~~~~

**The Four Key Components:**

1. **Dataset**: Test cases with inputs and expected outputs
2. **Evaluation Function**: Your LLM application logic
3. **Evaluators**: Automated quality assessment functions
4. **Tracer**: Captures execution details (multi-instance)

**How They Interact:**

.. code-block:: python

   from honeyhive.experiments import evaluate, evaluator
   
   # 1. Dataset: What to test
   dataset = [
       {
           "inputs": {"question": "What is AI?"},
           "ground_truth": {"answer": "Artificial Intelligence..."}
       }
   ]
   
   # 2. Evaluation Function: What to run
   def my_llm_app(datapoint):
       inputs = datapoint.get("inputs", {})
       # Your LLM logic here
       return {"answer": call_llm(inputs["question"])}
   
   # 3. Evaluator: How to score
   @evaluator
   def accuracy_check(outputs, inputs, ground_truth):
       return {
           "score": 1.0 if outputs["answer"] == ground_truth["answer"] else 0.0
       }
   
   # 4. Run experiment (tracer created automatically)
   result = evaluate(
       function=my_llm_app,
       dataset=dataset,
       evaluators=[accuracy_check],
       api_key="key",
       project="project"
   )

Multi-Instance Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each datapoint gets its **own isolated tracer instance**:

.. code-block:: text

   Datapoint 1 → Tracer Instance 1 → Session ID: session_abc_1
   Datapoint 2 → Tracer Instance 2 → Session ID: session_abc_2
   Datapoint 3 → Tracer Instance 3 → Session ID: session_abc_3

**Why This Matters:**

- ✅ **Isolation**: No cross-contamination between test cases
- ✅ **Parallel execution**: Can process multiple datapoints simultaneously
- ✅ **Clear attribution**: Each session maps to exactly one datapoint
- ✅ **Session enrichment**: Can add metadata per datapoint

**Example:**

.. code-block:: python

   def my_function(datapoint, tracer):  # tracer auto-injected
       inputs = datapoint.get("inputs", {})
       
       # Each datapoint has isolated tracer
       tracer.enrich_session(
           metadata={"test_case_id": inputs.get("id")}
       )
       
       result = call_llm(inputs["query"])
       return {"answer": result}
   
   # Each execution gets its own tracer instance
   # Datapoint 1: tracer_1 → traces stored under session_1
   # Datapoint 2: tracer_2 → traces stored under session_2

Data Flow Through the System
-----------------------------

Input Data Structure
~~~~~~~~~~~~~~~~~~~~

**Dataset Format:**

.. code-block:: python

   [
       {
           "inputs": {
               # Parameters passed to your function
               "question": "What is machine learning?",
               "context": "ML is a subset of AI",
               "model": "gpt-4"
           },
           "ground_truth": {
               # Expected outputs for evaluation
               "answer": "Machine learning is...",
               "category": "AI/ML",
               "confidence": "high"
           }
       },
       # ... more datapoints
   ]

**Function Signature (v1.0+):**

.. code-block:: python

   from typing import Any, Dict
   
   def evaluation_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Your function receives the complete datapoint."""
       inputs = datapoint.get("inputs", {})
       ground_truth = datapoint.get("ground_truth", {})
       
       # Process inputs
       result = your_logic(inputs)
       
       # Return outputs
       return {"answer": result}

Execution Data Flow
~~~~~~~~~~~~~~~~~~~

**Step-by-Step Data Transformation:**

.. code-block:: text

   1. Dataset Entry:
      {
          "inputs": {"query": "What is 2+2?"},
          "ground_truth": {"answer": "4"}
      }
   
   2. Function Receives Datapoint:
      datapoint = {
          "inputs": {"query": "What is 2+2?"},
          "ground_truth": {"answer": "4"}
      }
   
   3. Function Returns Outputs:
      outputs = {"answer": "4", "confidence": "high"}
   
   4. Evaluator Receives:
      - outputs: {"answer": "4", "confidence": "high"}
      - inputs: {"query": "What is 2+2?"}
      - ground_truth: {"answer": "4"}
   
   5. Evaluator Returns Metrics:
      {
          "exact_match": 1.0,
          "confidence_check": 1.0
      }
   
   6. Backend Aggregates:
      Run Results:
      - exact_match: avg(1.0, 0.8, 1.0, ...) = 0.93
      - confidence_check: avg(1.0, 1.0, 0.5, ...) = 0.85

Evaluation Metadata
~~~~~~~~~~~~~~~~~~~

The system automatically tracks:

.. code-block:: python

   # Per-datapoint metadata (automatically added)
   {
       "run_id": "run_abc123",
       "dataset_id": "dataset_xyz789",
       "datapoint_id": "EXT-datapoint-1",
       "session_id": "session_unique_id",
       "execution_time_ms": 1234,
       "tracer_instance_id": "tracer_1"
   }

This metadata propagates through:

- Span attributes (via OpenTelemetry baggage)
- Session metadata
- Backend storage
- Results API

Experiments vs Traces
----------------------

Understanding the Relationship
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Experiments **use** tracing but add evaluation on top:

.. code-block:: text

   Tracing Alone:
   ├─ Captures execution details
   ├─ Stores spans and attributes
   ├─ Shows what happened
   └─ No quality assessment
   
   Experiments (Tracing + Evaluation):
   ├─ Everything tracing does, PLUS:
   ├─ Runs evaluators on outputs
   ├─ Computes quality metrics
   ├─ Enables comparison
   └─ Drives improvement decisions

**When to Use Each:**

.. code-block:: python

   # Tracing only: Production monitoring
   from honeyhive import HoneyHiveTracer
   
   tracer = HoneyHiveTracer.init(api_key="key", project="project")
   
   @trace(tracer=tracer)
   def production_endpoint(user_query):
       # Just capture what happens in production
       return process_query(user_query)
   
   # Experiments: Testing and improvement
   from honeyhive.experiments import evaluate
   
   result = evaluate(
       function=production_endpoint,
       dataset=test_dataset,  # Controlled test cases
       evaluators=[quality_evaluator],  # Automated scoring
       api_key="key",
       project="project"
   )
   # Use results to improve before deploying

**Complementary Usage:**

.. code-block:: python

   # 1. Develop with experiments
   baseline_result = evaluate(function=v1, dataset=test_data)
   improved_result = evaluate(function=v2, dataset=test_data)
   
   # 2. Compare and choose best
   if improved_result.metrics.accuracy > baseline_result.metrics.accuracy:
       deploy(v2)
   
   # 3. Monitor in production with tracing
   @trace(tracer=tracer)
   def production_v2(query):
       return v2(query)

Evaluation Lifecycle
--------------------

Phase 1: Initialization
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # When evaluate() is called:
   
   1. Load/validate dataset
      - If dataset_id provided: fetch from HoneyHive
      - If dataset list provided: generate EXT- ID
      - Validate structure (inputs, ground_truth)
   
   2. Setup run metadata
      - Generate unique run_id
      - Create experiment name
      - Record timestamp
   
   3. Initialize evaluators
      - Validate evaluator signatures
      - Prepare async/sync execution
   
   4. Prepare execution plan
      - Determine parallelization (max_workers)
      - Setup tracer instances pool
      - Initialize progress tracking

Phase 2: Execution Loop
~~~~~~~~~~~~~~~~~~~~~~~

**For each datapoint (potentially in parallel):**

.. code-block:: python

   for datapoint in dataset:
       # 1. Create isolated tracer
       tracer = create_tracer_instance(
           api_key=api_key,
           project=project,
           session_name=f"{experiment_name}-{datapoint_id}"
       )
       
       # 2. Add evaluation metadata to baggage
       set_baggage({
           "honeyhive.run_id": run_id,
           "honeyhive.dataset_id": dataset_id,
           "honeyhive.datapoint_id": datapoint_id
       })
       
       # 3. Execute function
       try:
           if function_accepts_tracer(function):
               outputs = function(datapoint, tracer=tracer)
           else:
               outputs = function(datapoint)
       except Exception as e:
           outputs = {"error": str(e)}
       
       # 4. Run evaluators
       metrics = {}
       for evaluator in evaluators:
           result = evaluator(
               outputs=outputs,
               inputs=datapoint["inputs"],
               ground_truth=datapoint["ground_truth"]
           )
           metrics.update(result)
       
       # 5. Send to backend
       send_datapoint_result(
           run_id=run_id,
           datapoint_id=datapoint_id,
           session_id=tracer.session_id,
           outputs=outputs,
           metrics=metrics
       )

Phase 3: Backend Aggregation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Happens automatically on HoneyHive backend:**

.. code-block:: text

   1. Collect Results:
      - Gather all datapoint results for run_id
      - Associate with session traces
      - Link metrics to datapoints
   
   2. Compute Aggregates:
      For each metric (e.g., "accuracy"):
        - Calculate mean across all datapoints
        - Calculate median, min, max
        - Count improved/degraded cases
        - Generate distributions
   
   3. Store Run Metadata:
      - Total datapoints processed
      - Success/failure counts
      - Execution time statistics
      - Cost analysis
   
   4. Enable Comparison:
      - Index run for fast comparison
      - Link to dataset for reproducibility
      - Store evaluator configurations

Phase 4: Results Access
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.experiments import get_run_result, compare_runs
   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="key")
   
   # Access aggregated results
   result = get_run_result(client, run_id="run_123")
   
   print(f"Status: {result.status}")
   print(f"Metrics: {result.metrics}")  # Aggregated metrics
   print(f"Datapoints: {result.passed}/{result.total}")
   
   # Compare with another run
   comparison = compare_runs(
       client=client,
       new_run_id="run_456",
       old_run_id="run_123"
   )
   
   print(f"Improved metrics: {comparison.list_improved_metrics()}")
   print(f"Degraded metrics: {comparison.list_degraded_metrics()}")

Backend Aggregation
-------------------

Why Backend Aggregation?
~~~~~~~~~~~~~~~~~~~~~~~~~

**Previous approach (client-side):**

.. code-block:: text

   ❌ Client calculates all metrics
   ❌ Must process full dataset to get results
   ❌ No incremental updates
   ❌ Comparison requires downloading all data
   ❌ Slow for large datasets

**Current approach (backend-powered):**

.. code-block:: text

   ✅ Backend handles aggregation
   ✅ Results available as data arrives
   ✅ Incremental metrics updates
   ✅ Fast comparison (server-side)
   ✅ Scales to millions of datapoints

Aggregation Strategies
~~~~~~~~~~~~~~~~~~~~~~~

**1. Metric Aggregation:**

.. code-block:: python

   # For each metric across all datapoints:
   
   {
       "metric_name": "accuracy",
       "values": [1.0, 0.8, 1.0, 0.9, 1.0],  # Individual scores
       
       # Aggregated statistics:
       "aggregate": {
           "mean": 0.94,
           "median": 1.0,
           "min": 0.8,
           "max": 1.0,
           "std_dev": 0.089
       },
       
       # Distribution:
       "distribution": {
           "0.0-0.2": 0,
           "0.2-0.4": 0,
           "0.4-0.6": 0,
           "0.6-0.8": 0,
           "0.8-1.0": 5
       }
   }

**2. Comparison Aggregation:**

.. code-block:: python

   # When comparing two runs:
   
   {
       "metric_name": "accuracy",
       "old_run": {
           "mean": 0.82,
           "datapoints": 100
       },
       "new_run": {
           "mean": 0.94,
           "datapoints": 100
       },
       
       # Comparison analysis:
       "comparison": {
           "delta": +0.12,  # Improvement
           "percent_change": +14.6,
           "common_datapoints": 100,
           "improved_count": 15,  # Specific datapoints that improved
           "degraded_count": 3,   # Specific datapoints that degraded
           "unchanged_count": 82
       }
   }

**3. Cost Aggregation:**

.. code-block:: python

   # Automatic cost tracking:
   
   {
       "total_tokens": 125000,
       "total_cost_usd": 3.75,
       
       "by_model": {
           "gpt-4": {
               "tokens": 50000,
               "cost": 3.00
           },
           "gpt-3.5-turbo": {
               "tokens": 75000,
               "cost": 0.75
           }
       },
       
       "cost_per_datapoint": 0.0375,
       "cost_per_success": 0.0395  # Only successful evaluations
   }

Best Practices
--------------

1. Structure Experiments for Reproducibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ✅ Good: Clear, versioned experiment
   
   EXPERIMENT_VERSION = "v2.1"
   DATASET_ID = "qa-dataset-v1"  # Stable dataset reference
   
   result = evaluate(
       function=my_function,
       dataset_id=DATASET_ID,  # Use managed dataset
       evaluators=[accuracy, quality, latency],
       name=f"experiment-{EXPERIMENT_VERSION}-{datetime.now().isoformat()}",
       api_key=api_key,
       project=project
   )
   
   # Save results
   with open(f"results-{EXPERIMENT_VERSION}.json", "w") as f:
       json.dump(result.to_dict(), f)

2. Use Consistent Evaluators for Comparison
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ✅ Good: Same evaluators for all runs
   
   evaluators = [accuracy_evaluator, quality_evaluator]
   
   baseline = evaluate(
       function=v1_function,
       dataset=dataset,
       evaluators=evaluators,  # Same evaluators
       name="baseline-v1"
   )
   
   improved = evaluate(
       function=v2_function,
       dataset=dataset,  # Same dataset
       evaluators=evaluators,  # Same evaluators
       name="improved-v2"
   )
   
   # Now comparison is meaningful
   comparison = compare_runs(client, improved.run_id, baseline.run_id)

3. Leverage Multi-Instance Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ✅ Good: Use tracer parameter when needed
   
   def my_function(datapoint, tracer):
       """Function with tracer access for session enrichment."""
       inputs = datapoint.get("inputs", {})
       
       # Enrich session with experiment metadata
       tracer.enrich_session(
           metadata={
               "test_type": inputs.get("category"),
               "difficulty": inputs.get("difficulty")
           }
       )
       
       result = process(inputs)
       return result
   
   # Tracer automatically provided by evaluate()
   evaluate(function=my_function, dataset=dataset)

4. Start Simple, Add Complexity Gradually
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Phase 1: Basic experiment
   result = evaluate(
       function=my_function,
       dataset=small_dataset  # Start small
   )
   
   # Phase 2: Add evaluators
   result = evaluate(
       function=my_function,
       dataset=small_dataset,
       evaluators=[basic_evaluator]  # Add simple evaluator
   )
   
   # Phase 3: Scale up
   result = evaluate(
       function=my_function,
       dataset=full_dataset,  # Full dataset
       evaluators=[eval1, eval2, eval3],  # Multiple evaluators
       max_workers=10  # Parallel processing
   )
   
   # Phase 4: Comparison workflow
   comparison = compare_runs(client, new_run, old_run)

5. Monitor Experiment Costs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Track costs across experiments
   
   result = evaluate(
       function=my_function,
       dataset=dataset,
       evaluators=evaluators,
       verbose=True  # See progress and costs
   )
   
   # Access cost information
   print(f"Total tokens: {result.total_tokens}")
   print(f"Estimated cost: ${result.estimated_cost}")
   print(f"Cost per datapoint: ${result.estimated_cost / len(dataset)}")
   
   # Set cost budgets
   if result.estimated_cost > 10.0:
       print("⚠️ Experiment exceeded budget!")

Common Patterns
---------------

A/B Testing Pattern
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.experiments import evaluate, compare_runs
   from honeyhive import HoneyHive
   
   # Test two variants
   variant_a = evaluate(
       function=prompt_variant_a,
       dataset=test_dataset,
       evaluators=evaluators,
       name="variant-a-test"
   )
   
   variant_b = evaluate(
       function=prompt_variant_b,
       dataset=test_dataset,  # Same dataset!
       evaluators=evaluators,  # Same evaluators!
       name="variant-b-test"
   )
   
   # Compare
   client = HoneyHive(api_key=api_key)
   comparison = compare_runs(client, variant_b.run_id, variant_a.run_id)
   
   # Decide
   if "accuracy" in comparison.list_improved_metrics():
       deploy(variant_b)
   else:
       deploy(variant_a)

Progressive Improvement Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Iterative improvement workflow
   
   def improve_iteratively():
       current_best = baseline_function
       current_best_score = 0
       
       for iteration in range(10):
           # Generate variant
           variant = generate_improvement(current_best)
           
           # Test variant
           result = evaluate(
               function=variant,
               dataset=test_dataset,
               evaluators=[accuracy_evaluator],
               name=f"iteration-{iteration}"
           )
           
           # Compare
           if result.metrics.accuracy > current_best_score:
               print(f"✅ Iteration {iteration}: Improved to {result.metrics.accuracy}")
               current_best = variant
               current_best_score = result.metrics.accuracy
           else:
               print(f"❌ Iteration {iteration}: No improvement")
       
       return current_best

Regression Testing Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Ensure changes don't break existing behavior
   
   def regression_test(new_function):
       """Test new function against baseline."""
       
       # Run on regression test suite
       new_result = evaluate(
           function=new_function,
           dataset_id="regression-test-suite-v1",  # Stable test set
           evaluators=[accuracy, quality, safety],
           name="regression-check"
       )
       
       # Compare with baseline
       baseline_run_id = get_latest_baseline_run()
       comparison = compare_runs(
           client,
           new_run_id=new_result.run_id,
           old_run_id=baseline_run_id
       )
       
       # Check for regressions
       degraded = comparison.list_degraded_metrics()
       if degraded:
           raise ValueError(f"Regression detected in metrics: {degraded}")
       
       print("✅ No regressions detected")
       return new_result

See Also
--------

- :doc:`../../tutorials/05-run-first-experiment` - Hands-on experiment tutorial
- :doc:`../../how-to/evaluation/running-experiments` - Practical experiment guide
- :doc:`../../how-to/evaluation/comparing-experiments` - Comparison workflows
- :doc:`tracing-fundamentals` - Understanding tracing concepts
- :doc:`../../reference/experiments/experiments` - Complete API reference

