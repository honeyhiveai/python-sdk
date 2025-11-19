Evaluators
==========

Decorator-based system for defining custom quality checks and evaluators.

Overview
--------

Evaluators assess the quality of LLM outputs. HoneyHive uses a modern **decorator-based approach** instead of class inheritance, making evaluators simpler and more flexible.

**Key Features:**

- Simple function-based definitions
- Support for both sync and async evaluators
- Flexible return formats (dict, float, bool)
- Automatic metric aggregation
- Per-evaluator configuration

@evaluator Decorator
--------------------

.. py:decorator:: evaluator(func=None, *, name=None, settings=None)

   Decorator to mark a function as a synchronous evaluator.

   :param func: Function to decorate (when used as ``@evaluator`` without parentheses).
   :type func: Optional[Callable]
   
   :param name: Optional custom name for the evaluator. Defaults to function name.
   :type name: Optional[str]
   
   :param settings: Optional evaluator configuration.
   :type settings: Optional[EvaluatorSettings]
   
   :returns: Decorated evaluator function.
   :rtype: Callable

   **Signature Requirements:**

   Your evaluator function must accept these parameters:

   .. code-block:: python

      def my_evaluator(outputs, inputs, ground_truth):

          Args:
              outputs: Dict returned by your function
              inputs: Dict from datapoint["inputs"]
              ground_truth: Dict from datapoint["ground_truth"] (optional)
          
          Returns:
              Dict with "score" and optional metrics,
              or float (interpreted as score),
              or bool (1.0 if True, 0.0 if False)

          return {"score": 0.9, "passed": True}

   **Basic Usage (No Arguments)**

   .. code-block:: python

      from honeyhive.experiments import evaluator
      
      @evaluator
      def accuracy_check(outputs, inputs, ground_truth):
          """Check if output matches expected result."""
          return {
              "score": 1.0 if outputs == ground_truth else 0.0,
              "passed": outputs == ground_truth
          }

   **With Custom Name**

   .. code-block:: python

      @evaluator(name="custom_accuracy_v2")
      def accuracy_check(outputs, inputs, ground_truth):
          return {"score": calculate_score(outputs, ground_truth)}

   **With Settings**

   .. code-block:: python

      from honeyhive.experiments import evaluator, EvaluatorSettings
      
      @evaluator(settings=EvaluatorSettings(
          threshold=0.8,
          weight=2.0,
          enabled=True
      ))
      def weighted_accuracy(outputs, inputs, ground_truth):
          score = calculate_accuracy(outputs, ground_truth)
          return {"score": score}

   **Return Formats**

   Evaluators can return various formats:

   .. code-block:: python

      # Dict with score and metadata (RECOMMENDED)
      @evaluator
      def detailed_evaluator(outputs, inputs, ground_truth):
          return {
              "score": 0.85,
              "passed": True,
              "confidence": 0.95,
              "reason": "Output matches expected pattern"
          }
      
      # Simple float score
      @evaluator
      def simple_score(outputs, inputs, ground_truth):
          return 0.85  # Interpreted as {"score": 0.85}
      
      # Boolean (1.0 if True, 0.0 if False)
      @evaluator
      def pass_fail(outputs, inputs, ground_truth):
          return outputs["answer"] == ground_truth["answer"]

@aevaluator Decorator
---------------------

.. py:decorator:: aevaluator(func=None, *, name=None, settings=None)

   Decorator to mark a function as an asynchronous evaluator.

   Same parameters and behavior as ``@evaluator``, but for async functions.

   :param func: Async function to decorate.
   :type func: Optional[Callable]
   
   :param name: Optional custom name for the evaluator.
   :type name: Optional[str]
   
   :param settings: Optional evaluator configuration.
   :type settings: Optional[EvaluatorSettings]
   
   :returns: Decorated async evaluator function.
   :rtype: Callable

   **Basic Async Evaluator**

   .. code-block:: python

      from honeyhive.experiments import aevaluator
      import httpx
      
      @aevaluator
      async def external_api_check(outputs, inputs, ground_truth):
          """Call external API to validate output."""
          async with httpx.AsyncClient() as client:
              response = await client.post(
                  "https://api.example.com/validate",
                  json={"output": outputs, "expected": ground_truth}
              )
              data = response.json()
              
              return {
                  "score": data["score"],
                  "api_confidence": data["confidence"]
              }

   **Multiple Async Operations**

   .. code-block:: python

      @aevaluator
      async def multi_source_validation(outputs, inputs, ground_truth):
          """Validate against multiple external sources."""
          async with httpx.AsyncClient() as client:
              # Run validations concurrently
              results = await asyncio.gather(
                  client.post("https://api1.com/check", json=outputs),
                  client.post("https://api2.com/check", json=outputs),
                  client.post("https://api3.com/check", json=outputs),
              )
              
              scores = [r.json()["score"] for r in results]
              avg_score = sum(scores) / len(scores)
              
              return {
                  "score": avg_score,
                  "individual_scores": scores,
                  "sources_checked": len(scores)
              }

   **Mixing Sync and Async**

   You can use both sync and async evaluators together:

   .. code-block:: python

      @evaluator
      def fast_local_check(outputs, inputs, ground_truth):
          """Quick local validation."""
          return {"score": local_validation(outputs)}
      
      @aevaluator
      async def slow_api_check(outputs, inputs, ground_truth):
          """Slower external validation."""
          result = await external_api.validate(outputs)
          return {"score": result.score}
      
      # Use both in evaluate()
      result = evaluate(
          function=my_function,
          dataset=test_data,
          evaluators=[fast_local_check, slow_api_check],  # Mixed!
          api_key="key",
          project="project"
      )

EvaluatorSettings
-----------------

.. py:class:: EvaluatorSettings

   Configuration for individual evaluators.

   :param threshold: Minimum score to consider as "passed".
   :type threshold: Optional[float]
   
   :param weight: Relative weight for aggregation (default: 1.0).
   :type weight: Optional[float]
   
   :param enabled: Whether this evaluator is active (default: True).
   :type enabled: bool
   
   :param timeout: Maximum execution time in seconds.
   :type timeout: Optional[float]
   
   :param retry_count: Number of retries on failure.
   :type retry_count: int

   **Usage Example**

   .. code-block:: python

      from honeyhive.experiments import evaluator, EvaluatorSettings
      
      @evaluator(settings=EvaluatorSettings(
          threshold=0.7,      # Pass if score >= 0.7
          weight=2.0,         # Double weight in aggregation
          enabled=True,       # Can disable without removing
          timeout=5.0,        # 5 second timeout
          retry_count=3       # Retry up to 3 times
      ))
      def critical_evaluator(outputs, inputs, ground_truth):
          return {"score": validate(outputs)}

EvalResult
----------

.. py:class:: EvalResult

   Result object returned by evaluators (internal representation).

   :param score: Numerical score (typically 0.0 to 1.0).
   :type score: float
   
   :param passed: Whether evaluation passed threshold.
   :type passed: bool
   
   :param metrics: Additional metrics and metadata.
   :type metrics: Dict[str, Any]

   .. note::
      This class is used internally. Your evaluator functions return dicts,
      which are automatically converted to ``EvalResult`` objects.

Aggregation Functions
---------------------

When multiple evaluators run on the same datapoint, their scores are aggregated.

.. py:function:: mean(scores)

   Calculate arithmetic mean of scores.

   .. code-block:: python

      >>> mean([0.8, 0.9, 0.7])
      0.8

.. py:function:: median(scores)

   Calculate median score.

   .. code-block:: python

      >>> median([0.8, 0.9, 0.7, 0.6, 1.0])
      0.8

.. py:function:: mode(scores)

   Calculate mode (most common score).

   .. code-block:: python

      >>> mode([0.8, 0.8, 0.9, 0.7, 0.8])
      0.8

Evaluator Patterns
------------------

**1. Exact Match**

.. code-block:: python

   @evaluator
   def exact_match(outputs, inputs, ground_truth):
       """Check for exact string match."""
       return {
           "score": 1.0 if outputs["answer"] == ground_truth["answer"] else 0.0,
           "matched": outputs["answer"] == ground_truth["answer"]
       }

**2. Semantic Similarity**

.. code-block:: python

   from sentence_transformers import SentenceTransformer
   from sklearn.metrics.pairwise import cosine_similarity
   
   model = SentenceTransformer('all-MiniLM-L6-v2')
   
   @evaluator
   def semantic_similarity(outputs, inputs, ground_truth):
       """Calculate semantic similarity between output and expected."""
       output_embedding = model.encode([outputs["answer"]])
       expected_embedding = model.encode([ground_truth["answer"]])
       
       similarity = cosine_similarity(output_embedding, expected_embedding)[0][0]
       
       return {
           "score": float(similarity),
           "passed": similarity >= 0.8,
           "similarity": float(similarity)
       }

**3. Length Validation**

.. code-block:: python

   @evaluator
   def length_check(outputs, inputs, ground_truth):
       """Validate output length is within acceptable range."""
       text = outputs.get("answer", "")
       word_count = len(text.split())
       
       min_words = inputs.get("min_words", 10)
       max_words = inputs.get("max_words", 100)
       
       in_range = min_words <= word_count <= max_words
       
       return {
           "score": 1.0 if in_range else 0.0,
           "word_count": word_count,
           "in_range": in_range,
           "min_words": min_words,
           "max_words": max_words
       }

**4. Multi-Criteria Evaluation**

.. code-block:: python

   @evaluator
   def comprehensive_quality(outputs, inputs, ground_truth):
       """Evaluate multiple quality criteria."""
       answer = outputs.get("answer", "")
       
       # Individual criteria
       has_answer = len(answer) > 0
       correct_length = 50 <= len(answer) <= 200
       no_profanity = not contains_profanity(answer)
       factually_correct = check_facts(answer, ground_truth)
       
       # Weighted score
       criteria_scores = {
           "has_answer": 1.0 if has_answer else 0.0,
           "correct_length": 1.0 if correct_length else 0.5,
           "no_profanity": 1.0 if no_profanity else 0.0,
           "factually_correct": 1.0 if factually_correct else 0.0
       }
       
       # Average with weights
       weights = {"has_answer": 1, "correct_length": 1, "no_profanity": 2, "factually_correct": 3}
       total_weight = sum(weights.values())
       weighted_sum = sum(criteria_scores[k] * weights[k] for k in criteria_scores)
       final_score = weighted_sum / total_weight
       
       return {
           "score": final_score,
           "criteria_scores": criteria_scores,
           "all_passed": all(criteria_scores.values())
       }

**5. LLM-as-Judge**

.. code-block:: python

   import openai
   
   @evaluator
   def llm_judge(outputs, inputs, ground_truth):
       """Use an LLM to judge output quality."""
       client = openai.OpenAI()
       
       prompt = f"""
       Evaluate the following answer for accuracy and relevance.
       
       Question: {inputs['query']}
       Expected Answer: {ground_truth['answer']}
       Actual Answer: {outputs['answer']}
       
       Provide a score from 0.0 to 1.0 and explain your reasoning.

       
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[{"role": "user", "content": prompt}]
       )
       
       # Parse response (assumes structured format)
       result = parse_llm_response(response.choices[0].message.content)
       
       return {
           "score": result["score"],
           "reasoning": result["explanation"]
       }

Best Practices
--------------

**1. Keep Evaluators Pure**

Avoid side effects in evaluators:

.. code-block:: python

   # GOOD
   @evaluator
   def pure_evaluator(outputs, inputs, ground_truth):
       return {"score": calculate_score(outputs, ground_truth)}
   
   # BAD - Has side effects
   @evaluator
   def impure_evaluator(outputs, inputs, ground_truth):
       database.save_result(outputs)  # Side effect!
       return {"score": 0.9}

**2. Handle Missing Data Gracefully**

.. code-block:: python

   @evaluator
   def robust_evaluator(outputs, inputs, ground_truth):
       # Handle missing keys
       answer = outputs.get("answer", "")
       expected = ground_truth.get("answer", "") if ground_truth else ""
       
       if not answer:
           return {"score": 0.0, "error": "No answer provided"}
       
       if not expected:
           return {"score": 0.5, "warning": "No ground truth available"}
       
       return {"score": compare(answer, expected)}

**3. Provide Detailed Metadata**

.. code-block:: python

   @evaluator
   def detailed_evaluator(outputs, inputs, ground_truth):
       score = calculate_score(outputs, ground_truth)
       
       return {
           "score": score,
           "passed": score >= 0.8,
           # Add debugging info
           "output_length": len(str(outputs)),
           "processing_method": "semantic_similarity",
           "confidence": calculate_confidence(score),
           "suggestions": generate_improvements(outputs, ground_truth) if score < 0.8 else None
       }

**4. Use Timeouts for External Calls**

.. code-block:: python

   import asyncio
   
   @aevaluator
   async def api_evaluator_with_timeout(outputs, inputs, ground_truth):
       try:
           # Set timeout
           async with asyncio.timeout(5.0):
               result = await external_api.validate(outputs)
               return {"score": result.score}
       except asyncio.TimeoutError:
           return {"score": 0.0, "error": "API timeout"}

See Also
--------

- :doc:`core-functions` - Run evaluators with evaluate()
- :doc:`models` - Result data models
- :doc:`../../../how-to/evaluation/index` - Evaluator tutorial
- :doc:`../../../how-to/evaluation/index` - Evaluator patterns

