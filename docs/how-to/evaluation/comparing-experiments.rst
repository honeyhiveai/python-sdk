Comparing Experiments
=====================

How do I compare two experiment runs to see if I improved?
----------------------------------------------------------

Use the ``compare_runs()`` function to analyze differences between runs.

What's the simplest way to compare two runs?
--------------------------------------------

**Run Twice, Then Compare**

.. code-block:: python

   from honeyhive.experiments import evaluate, compare_runs
   from honeyhive import HoneyHive
   
   # Run baseline
   baseline_result = evaluate(
       function=baseline_function,
       dataset=dataset,
       evaluators=[accuracy_evaluator],
       api_key="your-api-key",
       project="your-project",
       name="gpt-3.5-baseline"
   )
   
   # Run improved version
   improved_result = evaluate(
       function=improved_function,
       dataset=dataset,  # SAME dataset!
       evaluators=[accuracy_evaluator],  # SAME evaluators!
       api_key="your-api-key",
       project="your-project",
       name="gpt-4-improved"
   )
   
   # Compare
   client = HoneyHive(api_key="your-api-key")
   comparison = compare_runs(
       client=client,
       new_run_id=improved_result.run_id,
       old_run_id=baseline_result.run_id
   )
   
   # Check results
   print(f"Common datapoints: {comparison.common_datapoints}")
   print(f"Improved metrics: {comparison.list_improved_metrics()}")
   print(f"Degraded metrics: {comparison.list_degraded_metrics()}")

What does the comparison object contain?
----------------------------------------

**Key Fields Explained**

.. code-block:: python

   comparison = compare_runs(client, new_run_id, old_run_id)
   
   # Datapoint counts
   comparison.common_datapoints  # Items in both runs
   comparison.new_only_datapoints  # Items only in new run
   comparison.old_only_datapoints  # Items only in old run
   
   # Metric deltas
   comparison.metric_deltas  # Dict of changes per metric
   
   # Helper methods
   comparison.list_improved_metrics()  # List of improved metric names
   comparison.list_degraded_metrics()  # List of degraded metric names

**Example Output:**

.. code-block:: python

   # metric_deltas structure
   {
       "accuracy": {
           "old_aggregate": 0.75,
           "new_aggregate": 0.85,  # Improved!
           "found_count": 10,
           "improved_count": 5,
           "degraded_count": 2,
           "improved": ["EXT-datapoint-1", "EXT-datapoint-3"],
           "degraded": ["EXT-datapoint-7"]
       },
       "length_check": {
           "old_aggregate": 0.90,
           "new_aggregate": 0.88,  # Degraded slightly
           "found_count": 10,
           "improved_count": 1,
           "degraded_count": 2
       }
   }

What's the difference between aggregate and event-level comparison?
-------------------------------------------------------------------

**Two Comparison Modes**

**Aggregate Comparison** (using ``compare_runs()``):
- Compares overall metrics across all datapoints
- Shows average improvement/degradation
- Good for: High-level "did I improve?"

**Event-Level Comparison** (using API directly):
- Compares individual datapoint results
- Shows which specific inputs improved/degraded
- Good for: Debugging specific failures

.. code-block:: python

   # Aggregate comparison
   comparison = compare_runs(client, new_run_id, old_run_id)
   print(f"Overall accuracy improved: {comparison.metric_deltas['accuracy']['new_aggregate'] > comparison.metric_deltas['accuracy']['old_aggregate']}")
   
   # Event-level comparison (via API)
   event_comparison = client.evaluations.compare_run_events(
       new_run_id=new_run_id,
       old_run_id=old_run_id,
       event_type="session",
       limit=100
   )
   
   # See individual event pairs
   for pair in event_comparison["events"]:
       datapoint_id = pair["datapoint_id"]
       event_1_metrics = pair["event_1"]["metrics"]
       event_2_metrics = pair["event_2"]["metrics"]
       print(f"{datapoint_id}: {event_2_metrics} → {event_1_metrics}")

Best Practices for Comparison
-----------------------------

**Use the SAME Dataset**

.. code-block:: python

   # ✅ Good: Same dataset for both runs
   dataset = load_dataset()  # Load once
   
   baseline = evaluate(function=v1, dataset=dataset)  # ...more args
   improved = evaluate(function=v2, dataset=dataset)  # ...more args
   
   # Now comparison is meaningful
   
  # ❌ Bad: Different datasets
  baseline = evaluate(function=v1, dataset=dataset1)  # ...more args
  improved = evaluate(function=v2, dataset=dataset2)  # ...more args (Different!)
   
   # Comparison is meaningless - comparing apples to oranges

**Use the SAME Evaluators**

.. code-block:: python

   # Define evaluators once
   evaluators = [accuracy, length_check, quality_score]
   
  # Use for both runs
  baseline = evaluate(function=v1, dataset=dataset, evaluators=evaluators)  # ...more args
  improved = evaluate(function=v2, dataset=dataset, evaluators=evaluators)  # ...more args

**Use Descriptive Names for Easy Identification**

.. code-block:: python

  # ✅ Good: Easy to identify in dashboard
  baseline = evaluate(function=v1, dataset=dataset, name="gpt-3.5-baseline-2024-01-15")  # ...more args
  improved = evaluate(function=v2, dataset=dataset, name="gpt-4-with-rag-2024-01-15")  # ...more args
  
  # ❌ Bad: Hard to remember which is which
  baseline = evaluate(function=v1, dataset=dataset, name="run1")  # ...more args
  improved = evaluate(function=v2, dataset=dataset, name="run2")  # ...more args

How do I know if my changes actually improved things?
-----------------------------------------------------

**Check Multiple Signals**

.. code-block:: python

   comparison = compare_runs(client, new_run_id, old_run_id)
   
   # 1. Check overall metrics
   improved_metrics = comparison.list_improved_metrics()
   degraded_metrics = comparison.list_degraded_metrics()
   
   if len(improved_metrics) > len(degraded_metrics):
       print("✅ Overall improvement!")
   else:
       print("⚠️ Mixed results or regression")
   
   # 2. Check specific important metrics
   accuracy_delta = comparison.metric_deltas.get("accuracy", {})
   if accuracy_delta.get("new_aggregate", 0) > accuracy_delta.get("old_aggregate", 0):
       print("✅ Accuracy improved")
   
   # 3. Check trade-offs
   if "accuracy" in improved_metrics and "latency" in degraded_metrics:
       print("⚠️ Trade-off: More accurate but slower")

Show me a complete comparison workflow
--------------------------------------

**Iterative Testing Pattern**

.. code-block:: python

   from honeyhive.experiments import evaluate, compare_runs
   from honeyhive import HoneyHive
   
   # Shared test data
   dataset = load_test_dataset()
   evaluators = [accuracy, quality, length]
   
   client = HoneyHive(api_key="your-api-key")
   
   # Iteration 1: Baseline
   v1_result = evaluate(
       function=version_1_function,
       dataset=dataset,
       evaluators=evaluators,
       api_key="your-api-key",
       project="my-project",
       name="v1-baseline"
   )
   
   # Iteration 2: Try improvement
   v2_result = evaluate(
       function=version_2_function,
       dataset=dataset,
       evaluators=evaluators,
       api_key="your-api-key",
       project="my-project",
       name="v2-better-prompt"
   )
   
   # Compare
   comparison = compare_runs(
       client=client,
       new_run_id=v2_result.run_id,
       old_run_id=v1_result.run_id
   )
   
   # Decision logic
   if "accuracy" in comparison.list_improved_metrics():
       print("✅ v2 is better! Deploy it.")
       production_version = version_2_function
   else:
       print("❌ v2 is worse. Keep v1.")
       production_version = version_1_function
       
       # Try again with different approach
       v3_result = evaluate(
           function=version_3_function,
           dataset=dataset,
           evaluators=evaluators,
           api_key="your-api-key",
           project="my-project",
           name="v3-different-model"
       )
       
       comparison = compare_runs(
           client=client,
           new_run_id=v3_result.run_id,
           old_run_id=v1_result.run_id
       )

Common Comparison Scenarios
---------------------------

**Prompt Engineering**

.. code-block:: python

   def test_prompt_variant(prompt_template):
       """Test a prompt variant against baseline."""
       result = evaluate(
           function=lambda inputs, gt: llm_call(prompt_template.format(**inputs)),
           dataset=dataset,
           evaluators=[accuracy, quality],
           api_key="your-api-key",
           project="prompt-testing",
           name=f"prompt-{hash(prompt_template)}"
       )
       return result
   
   # Test multiple prompts
   baseline = test_prompt_variant("Answer: {question}")
   variant1 = test_prompt_variant("Think step by step. {question}")
   variant2 = test_prompt_variant("You are an expert. {question}")
   
   # Compare each to baseline
   comp1 = compare_runs(client, variant1.run_id, baseline.run_id)
   comp2 = compare_runs(client, variant2.run_id, baseline.run_id)

**Model Selection**

.. code-block:: python

   models = ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"]
   results = {}
   
   for model in models:
       result = evaluate(
           function=lambda inputs, gt: call_model(model, inputs),
           dataset=dataset,
           evaluators=evaluators,
           api_key="your-api-key",
           project="model-comparison",
           name=f"model-{model}"
       )
       results[model] = result
   
   # Compare all to baseline (gpt-3.5)
   baseline_run_id = results["gpt-3.5-turbo"].run_id
   
   for model in ["gpt-4", "claude-3-sonnet"]:
       comparison = compare_runs(
           client=client,
           new_run_id=results[model].run_id,
           old_run_id=baseline_run_id
       )
       print(f"\n{model} vs gpt-3.5:")
       print(f"  Improved: {comparison.list_improved_metrics()}")
       print(f"  Degraded: {comparison.list_degraded_metrics()}")

See Also
--------

- :doc:`running-experiments` - Run experiments to compare
- :doc:`result-analysis` - Detailed result analysis
- :doc:`../../reference/experiments/results` - Complete compare_runs() API reference
