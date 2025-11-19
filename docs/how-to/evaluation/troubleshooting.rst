Troubleshooting
===============

Common issues and solutions for running experiments.

Slow Experiments
----------------

**Problem: My experiments take too long**

**Solutions:**

1. **Use Parallel Execution:**

.. code-block:: python

   result = evaluate(
       function=my_function,
       dataset=dataset,
       max_workers=20,  # Process 20 items at once
       api_key="your-api-key",
       project="your-project"
   )

2. **Start with Smaller Dataset:**

.. code-block:: python

   # Test on sample first
   result = evaluate(
       function=my_function,
       dataset=dataset[:100],  # First 100 items
       api_key="your-api-key",
       project="your-project"
   )

3. **Reduce LLM-as-Judge Evaluators:**

LLM evaluators are expensive. Use cheaper models or fewer evaluators.

Evaluator Errors
----------------

**Problem: My evaluator is throwing errors**

**Solution: Add Error Handling:**

.. code-block:: python

   @evaluator()
   def robust_evaluator(outputs, inputs, ground_truth):
       try:
           score = calculate_score(outputs, ground_truth)
           return {"score": score}
       except Exception as e:
           return {"score": 0.0, "error": str(e)}

Inconsistent Results
--------------------

**Problem: LLM-as-judge gives different scores each time**

**Solution: Use temperature=0.0:**

.. code-block:: python

   @evaluator()
   def consistent_judge(outputs, inputs, ground_truth):
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[...],
           temperature=0.0,  # Deterministic
           seed=42
       )
       return score

Missing Results
---------------

**Problem: I don't see results in the dashboard**

**Checklist:**

1. Check API key and project name
2. Verify experiment completed successfully
3. Wait a few seconds for backend processing
4. Check run_id in dashboard search

See Also
--------

- :doc:`running-experiments` - Core workflows
- :doc:`best-practices` - Evaluation strategies

