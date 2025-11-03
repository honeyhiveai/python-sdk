Server-Side Evaluators
======================

When should I use server-side evaluators vs client-side evaluators?
-------------------------------------------------------------------

Use server-side for evaluators configured in HoneyHive UI that run automatically.

Client-Side vs Server-Side
--------------------------

**Client-Side Evaluators** (``@evaluator``):
- Defined in your code
- Run during ``evaluate()`` call
- You control the logic
- Good for: Custom metrics, rapid iteration

**Server-Side Evaluators**:
- Configured in HoneyHive UI
- Run automatically on the backend
- Managed by your team
- Good for: Standardized metrics, async evaluation

How do I use evaluators configured in the UI?
---------------------------------------------

**They Run Automatically**

Server-side evaluators run automatically when:
- Experiments complete
- Traces are created
- Specific triggers are met

You don't need to pass them to ``evaluate()`` - they're configured in your project settings.

**To configure:**

1. Go to HoneyHive dashboard
2. Navigate to Evaluators section  
3. Create new evaluator
4. Configure trigger conditions
5. Evaluators run automatically

Can I use both client-side and server-side evaluators?
------------------------------------------------------

**Yes! They Complement Each Other**

.. code-block:: python

   from honeyhive.experiments import evaluate, evaluator
   
   # Client-side evaluator (runs immediately)
   @evaluator()
   def custom_metric(outputs, inputs, ground_truth):
       return calculate_custom_score(outputs)
   
   # Run experiment with client-side evaluator
   result = evaluate(
       function=my_function,
       dataset=dataset,
       evaluators=[custom_metric],  # Client-side
       api_key="your-api-key",
       project="your-project"
   )
   
   # Server-side evaluators run automatically on backend
   # Results appear in dashboard after processing

See Also
--------

- :doc:`creating-evaluators` - Create client-side evaluators
- :doc:`running-experiments` - Use evaluators in experiments

