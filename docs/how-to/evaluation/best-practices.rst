Best Practices
==============

How do I design an effective evaluation strategy?
-------------------------------------------------

Follow these proven patterns for experiment design and execution.

Start Simple, Scale Up
----------------------

**Phase 1: Proof of Concept (10-20 datapoints)**

.. code-block:: python

   # Start small
   small_dataset = dataset[:10]
   
   result = evaluate(
       function=my_function,
       dataset=small_dataset,
       evaluators=[exact_match],  # One simple evaluator
       api_key="your-api-key",
       project="your-project"
   )

**Phase 2: Validation (50-100 datapoints)**

.. code-block:: python

   medium_dataset = dataset[:100]
   
   result = evaluate(
       function=my_function,
       dataset=medium_dataset,
       evaluators=[exact_match, length_check, quality],
       api_key="your-api-key",
       project="your-project"
   )

**Phase 3: Production (500+ datapoints)**

.. code-block:: python

   result = evaluate(
       function=my_function,
       dataset=full_dataset,
       evaluators=[exact_match, llm_judge, semantic_sim, safety],
       max_workers=20,  # Parallel execution
       api_key="your-api-key",
       project="your-project"
   )

How do I balance cost and thoroughness?
---------------------------------------

**Tiered Evaluation Strategy**

.. code-block:: python

   def evaluate_with_priority(function, dataset, priority="normal"):
       """Adjust evaluation depth based on priority."""
       
       if priority == "critical":
           evaluators = [exact_match, semantic_sim, llm_judge, safety]
           workers = 20
       elif priority == "normal":
           evaluators = [exact_match, length_check]
           workers = 10
       else:  # "low"
           evaluators = [exact_match]
           workers = 5
       
       return evaluate(
           function=function,
           dataset=dataset,
           evaluators=evaluators,
           max_workers=workers,
           api_key="your-api-key",
           project="your-project"
       )

Ensure Reproducibility
----------------------

**Use Deterministic Settings**

.. code-block:: python

   # For LLM calls
   response = client.chat.completions.create(
       model="gpt-4",
       messages=messages,
       temperature=0.0,  # Deterministic
       seed=42  # Reproducible
   )
   
   # For LLM-as-judge evaluators
   @evaluator()
   def llm_judge(outputs, inputs, ground_truth):
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[...],
           temperature=0.0,
           seed=42
       )
       return score

See Also
--------

- :doc:`running-experiments` - Core workflows
- :doc:`creating-evaluators` - Build evaluators
- :doc:`troubleshooting` - Fix common issues

