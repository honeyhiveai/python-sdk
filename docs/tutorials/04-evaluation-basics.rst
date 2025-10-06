Evaluation Basics Tutorial
===========================

.. note::
   **Tutorial Goal**: Run your first experiment in HoneyHive (15 minutes)

This **hands-on tutorial** walks you through running your first experiment to evaluate an LLM application.

.. tip::
   **Need advanced patterns?** See :doc:`../how-to/evaluation/index` for detailed evaluation guides.

What You'll Learn
-----------------

By the end of this tutorial, you'll be able to:

- Run a simple experiment using ``evaluate()``
- Create a test dataset
- View results in the HoneyHive dashboard

Prerequisites
-------------

- Complete :doc:`03-llm-integration` tutorial
- OpenAI API key (or another LLM provider)
- HoneyHive API key and project

**Time Required**: 15 minutes

Your First Experiment
----------------------

An experiment in HoneyHive tests your LLM application across multiple inputs. Think of it like unit testing, but for AI.

**Three Simple Parts:**

1. **Dataset**: Your test cases (inputs + expected outputs)
2. **Function**: Your LLM application  
3. **evaluate()**: Runs the tests and tracks results

Step 1: Create Your Test Dataset
----------------------------------

Create a simple dataset with test questions:

.. code-block:: python

   dataset = [
       {
           "inputs": {"question": "What is the capital of France?"},
           "ground_truths": {"answer": "Paris"}
       },
       {
           "inputs": {"question": "What is 2+2?"},
           "ground_truths": {"answer": "4"}
       }
   ]

Each item has:
- **inputs**: What you pass to your function
- **ground_truths**: The expected answer (optional)

Step 2: Write Your Function
-----------------------------

Write the function you want to test:

.. code-block:: python

   import openai
   
   def answer_question(inputs, ground_truths):
       """Answer questions using GPT."""
       client = openai.OpenAI()
       
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[
               {"role": "user", "content": inputs["question"]}
           ]
       )
       
       return {"answer": response.choices[0].message.content}

.. note::
   Your function must accept ``inputs`` and ``ground_truths`` parameters in that order.

Step 3: Run the Experiment
----------------------------

Now run your experiment:

.. code-block:: python

   from honeyhive.experiments import evaluate
   
   result = evaluate(
       function=answer_question,
       dataset=dataset,
       api_key="your-api-key",      # Or set HH_API_KEY env var
       project="your-project",      # Or set HH_PROJECT env var
       name="My First Experiment"
   )
   
   print(f"✅ Experiment complete! Run ID: {result.run_id}")

That's it! Your experiment runs your function on each test case and stores the results.

Step 4: View Your Results
---------------------------

Open your HoneyHive dashboard to see:

- Each test case's input and output
- Any errors that occurred
- Execution traces for debugging

You can now iterate on your function and run new experiments to see if you improved!

Next Steps
----------

Congratulations! You've run your first experiment. Now you can:

**Add Evaluators** (Optional)

Want to automatically score your outputs? Add evaluators:

.. code-block:: python

   from honeyhive.experiments import evaluator
   
   @evaluator()
   def check_answer_length(outputs, inputs, ground_truths):
       """Check if answer is reasonable length."""
       length = len(outputs.get("answer", ""))
       return 1.0 if 10 <= length <= 200 else 0.5
   
   # Run with evaluators
   result = evaluate(
       function=answer_question,
       dataset=dataset,
       evaluators=[check_answer_length],
       api_key="your-api-key",
       project="your-project"
   )

.. note::
   **Evaluator Parameter Order**: Evaluators must accept parameters in this order:
   
   1. ``outputs`` (required): The return value from your function
   2. ``inputs`` (optional): The inputs dict from the datapoint
   3. ``ground_truths`` (optional): The ground_truths dict from the datapoint

**Learn More**

- :doc:`../how-to/evaluation/index` - Detailed evaluation patterns and problem-solving
- :doc:`../reference/experiments/experiments` - Complete API reference
- `Compare experiments <https://docs.honeyhive.ai/evaluation/comparing_evals>`_ - Compare multiple runs

What's Next?
------------

You now know how to run experiments! Try:

1. Test your actual LLM application
2. Add more test cases to your dataset
3. Compare results between experiments
4. Share results with your team

Happy experimenting! 🎉
