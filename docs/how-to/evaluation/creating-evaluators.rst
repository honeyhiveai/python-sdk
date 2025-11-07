Creating Evaluators
===================

How do I create custom metrics to score my LLM outputs?
-------------------------------------------------------

Use the ``@evaluator`` decorator to create scoring functions.

What's the simplest evaluator I can create?
-------------------------------------------

**Simple Function with @evaluator Decorator**

.. code-block:: python

   from honeyhive.experiments import evaluator
   
   @evaluator()
   def exact_match(outputs, inputs, ground_truth):
       """Check if output matches expected result."""
       expected = ground_truth.get("answer", "")
       actual = outputs.get("answer", "")
       
       # Return a score (0.0 to 1.0)
       return 1.0 if actual == expected else 0.0

**Use it in evaluate():**

.. code-block:: python

   from typing import Any, Dict
   from honeyhive.experiments import evaluate, evaluator
   
   # Your evaluation function
   def my_llm_app(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Processes datapoint and returns outputs."""
       inputs = datapoint.get("inputs", {})
       result = call_llm(inputs["prompt"])
       return {"answer": result}  # This becomes 'outputs' in evaluator
   
   # Your evaluator
   @evaluator()
   def exact_match(outputs, inputs, ground_truth):
       """Evaluator receives output from my_llm_app + datapoint context."""
       # outputs = {"answer": result} from my_llm_app
       # inputs = datapoint["inputs"]
       # ground_truth = datapoint["ground_truth"]
       expected = ground_truth.get("answer", "")
       actual = outputs.get("answer", "")
       return 1.0 if actual == expected else 0.0
   
   # Run evaluation
   result = evaluate(
       function=my_llm_app,       # Produces 'outputs'
       dataset=dataset,            # Contains 'inputs' and 'ground_truth'
       evaluators=[exact_match],   # Receives all three
       api_key="your-api-key",
       project="your-project"
   )

.. important::
   **How Evaluators Are Invoked**
   
   For each datapoint in your dataset, ``evaluate()`` does the following:
   
   1. **Calls your evaluation function** with the datapoint
   2. **Gets the output** (return value from your function)
   3. **Invokes each evaluator** with:
   
      - ``outputs`` = return value from your evaluation function
      - ``inputs`` = ``datapoint["inputs"]`` from the dataset
      - ``ground_truth`` = ``datapoint["ground_truth"]`` from the dataset
   
   This allows evaluators to compare what your function produced (``outputs``) against what was expected (``ground_truth``), with access to the original inputs for context.

**Visual Flow Diagram**

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'tertiaryColor': 'transparent', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'edgeLabelBackground': 'transparent', 'background': 'transparent'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
   flowchart TD
       Start([Dataset with Datapoints]) --> Loop{For Each Datapoint}
       
       Loop --> Extract[Extract Components:<br/>inputs = datapoint-inputs<br/>ground_truth = datapoint-ground_truth]
       
       Extract --> EvalFunc[Call Evaluation Function<br/>my_llm_app-datapoint]
       
       EvalFunc --> Output[Function Returns:<br/>outputs = answer-result]
       
       Output --> Evaluator[Call Each Evaluator<br/>evaluator-outputs-inputs-ground_truth]
       
       Evaluator --> Score[Evaluator Returns:<br/>score or score-metadata]
       
       Score --> Store[Store Results in HoneyHive]
       
       Store --> Loop
       
       Loop -->|Done| End([Experiment Complete])
       
       classDef startEnd fill:#1565c0,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef process fill:#42a5f5,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef action fill:#7b1fa2,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef success fill:#2e7d32,stroke:#333333,stroke-width:2px,color:#ffffff
       
       class Start,End startEnd
       class Extract,Output,Store process
       class EvalFunc action
       class Evaluator success

**Example Mapping:**

.. code-block:: python

   # Dataset datapoint
   datapoint = {
       "inputs": {"prompt": "What is AI?"},
       "ground_truth": {"answer": "Artificial Intelligence"}
   }
   
   # Step 1: evaluate() calls your function
   outputs = my_llm_app(datapoint)
   # outputs = {"answer": "AI is Artificial Intelligence"}
   
   # Step 2: evaluate() calls your evaluator
   score = exact_match(
       outputs=outputs,                          # From function
       inputs=datapoint["inputs"],               # From dataset
       ground_truth=datapoint["ground_truth"]    # From dataset
   )
   # score = 1.0 (match found)

What parameters must my evaluator accept?
-----------------------------------------

**(outputs, inputs, ground_truth) in That Order**

.. code-block:: python

   @evaluator()
   def my_evaluator(outputs, inputs, ground_truth):
       """Evaluator function.
       
       Args:
           outputs (dict): Return value from your function
           inputs (dict): Inputs from the datapoint
           ground_truth (dict): Expected outputs from datapoint
       
       Returns:
           float or dict: Score or detailed results
       """
       # Your scoring logic
       score = calculate_score(outputs, ground_truth)
       return score

.. important::
   **Parameter Order Matters!**
   
   1. ``outputs`` (required) - What your function returned
   2. ``inputs`` (optional) - Original inputs
   3. ``ground_truth`` (optional) - Expected outputs

What can my evaluator return?
-----------------------------

**Float, Bool, or Dict**

.. code-block:: python

   # Option 1: Return float (score only)
   @evaluator()
   def simple_score(outputs, inputs, ground_truth):
       return 0.85  # Score between 0.0 and 1.0
   
   # Option 2: Return bool (pass/fail)
   @evaluator()
   def pass_fail(outputs, inputs, ground_truth):
       return len(outputs["answer"]) > 10  # Converts to 1.0 or 0.0
   
   # Option 3: Return dict (RECOMMENDED - most informative)
   @evaluator()
   def detailed_score(outputs, inputs, ground_truth):
       score = calculate_score(outputs)
       return {
           "score": score,  # Required: 0.0 to 1.0
           "passed": score >= 0.8,
           "details": "answer too short",
           "confidence": 0.95
       }

Common Evaluator Patterns
-------------------------

**Exact Match**

.. code-block:: python

   @evaluator()
   def exact_match(outputs, inputs, ground_truth):
       """Check for exact string match."""
       expected = ground_truth.get("answer", "").lower().strip()
       actual = outputs.get("answer", "").lower().strip()
       
       return {
           "score": 1.0 if actual == expected else 0.0,
           "matched": actual == expected,
           "expected": expected,
           "actual": actual
       }

**Length Check**

.. code-block:: python

   @evaluator()
   def length_check(outputs, inputs, ground_truth):
       """Validate output length."""
       text = outputs.get("answer", "")
       word_count = len(text.split())
       
       min_words = inputs.get("min_words", 10)
       max_words = inputs.get("max_words", 200)
       
       in_range = min_words <= word_count <= max_words
       
       return {
           "score": 1.0 if in_range else 0.5,
           "word_count": word_count,
           "in_range": in_range
       }

**Contains Keywords**

.. code-block:: python

   @evaluator()
   def keyword_check(outputs, inputs, ground_truth):
       """Check if output contains required keywords."""
       answer = outputs.get("answer", "").lower()
       required_keywords = inputs.get("keywords", [])
       
       found = [kw for kw in required_keywords if kw.lower() in answer]
       score = len(found) / len(required_keywords) if required_keywords else 0.0
       
       return {
           "score": score,
           "found_keywords": found,
           "missing_keywords": list(set(required_keywords) - set(found))
       }

How do I create evaluators with custom parameters?
--------------------------------------------------

**Use Factory Functions**

.. code-block:: python

   def create_length_evaluator(min_words: int, max_words: int):
       """Factory for length evaluators with custom thresholds."""
       
       @evaluator(name=f"length_{min_words}_{max_words}")
       def length_validator(outputs, inputs, ground_truth):
           text = outputs.get("answer", "")
           word_count = len(text.split())
           
           in_range = min_words <= word_count <= max_words
           
           return {
               "score": 1.0 if in_range else 0.5,
               "word_count": word_count,
               "target_range": f"{min_words}-{max_words}"
           }
       
       return length_validator
   
   # Create different length checkers
   short_answer = create_length_evaluator(10, 50)
   medium_answer = create_length_evaluator(50, 200)
   long_answer = create_length_evaluator(200, 1000)
   
   # Use in evaluation
   result = evaluate(
       function=my_function,
       dataset=dataset,
       evaluators=[short_answer],  # Use the configured evaluator
       api_key="your-api-key",
       project="your-project"
   )

How do I use an LLM to evaluate quality?
----------------------------------------

**Call LLM in Evaluator Function**

.. code-block:: python

   import openai
   
   @evaluator()
   def llm_judge(outputs, inputs, ground_truth):
       """Use GPT-4 to judge answer quality."""
       client = openai.OpenAI()
       
       prompt = f"""
       Rate this answer on a scale of 0.0 to 1.0.
       
       Question: {inputs['question']}
       Expected: {ground_truth['answer']}
       Actual: {outputs['answer']}
       
       Consider: accuracy, completeness, clarity.
       
       Respond with ONLY a JSON object:
       {{"score": 0.0-1.0, "reasoning": "brief explanation"}}
       """
       
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[{"role": "user", "content": prompt}],
           temperature=0.0,  # Deterministic
           response_format={"type": "json_object"}
       )
       
       import json
       result = json.loads(response.choices[0].message.content)
       return result

.. warning::
   **Cost Consideration**: LLM-as-judge evaluators make API calls for each datapoint.
   
   - 100 datapoints = 100 GPT-4 calls
   - Consider using cheaper models for large datasets
   - Or use sampling: only evaluate subset of data

How do I check multiple quality dimensions?
-------------------------------------------

**Weighted Scoring Across Criteria**

.. code-block:: python

   @evaluator()
   def comprehensive_quality(outputs, inputs, ground_truth):
       """Evaluate multiple quality dimensions."""
       answer = outputs.get("answer", "")
       
       # Individual criteria
       has_answer = len(answer) > 0
       correct_length = 50 <= len(answer) <= 200
       no_profanity = not contains_profanity(answer)  # Your function
       factually_correct = check_facts(answer, ground_truth)  # Your function
       
       # Individual scores
       criteria_scores = {
           "has_answer": 1.0 if has_answer else 0.0,
           "correct_length": 1.0 if correct_length else 0.5,
           "no_profanity": 1.0 if no_profanity else 0.0,
           "factually_correct": 1.0 if factually_correct else 0.0
       }
       
       # Weighted average (adjust weights for your use case)
       weights = {
           "has_answer": 1,
           "correct_length": 1,
           "no_profanity": 2,  # More important
           "factually_correct": 3  # Most important
       }
       
       total_weight = sum(weights.values())
       weighted_sum = sum(criteria_scores[k] * weights[k] for k in criteria_scores)
       final_score = weighted_sum / total_weight
       
       return {
           "score": final_score,
           "criteria_scores": criteria_scores,
           "all_passed": all(v == 1.0 for v in criteria_scores.values())
       }

How do I check if answers are semantically similar?
---------------------------------------------------

**Use Embeddings and Cosine Similarity**

.. code-block:: python

   from sentence_transformers import SentenceTransformer
   from sklearn.metrics.pairwise import cosine_similarity
   
   # Load model once (outside evaluator for efficiency)
   model = SentenceTransformer('all-MiniLM-L6-v2')
   
   
   @evaluator()
   def semantic_similarity(outputs, inputs, ground_truth):
       """Calculate semantic similarity using embeddings."""
       expected = ground_truth.get("answer", "")
       actual = outputs.get("answer", "")
       
       # Generate embeddings
       expected_emb = model.encode([expected])
       actual_emb = model.encode([actual])
       
       # Cosine similarity
       similarity = cosine_similarity(expected_emb, actual_emb)[0][0]
       
       return {
           "score": float(similarity),
           "passed": similarity >= 0.8,
           "similarity": float(similarity)
       }

.. note::
   **Dependencies**: Install required packages:
   
   .. code-block:: bash
   
      pip install sentence-transformers scikit-learn

How do I run multiple evaluators on the same outputs?
-----------------------------------------------------

**Pass List of Evaluators**

.. code-block:: python

   from honeyhive.experiments import evaluate, evaluator
   
   @evaluator()
   def accuracy(outputs, inputs, ground_truth):
       return 1.0 if outputs["answer"] == ground_truth["answer"] else 0.0
   
   @evaluator()
   def length_check(outputs, inputs, ground_truth):
       return 1.0 if 10 <= len(outputs["answer"]) <= 200 else 0.5
   
   @evaluator()
   def has_sources(outputs, inputs, ground_truth):
       return 1.0 if "sources" in outputs else 0.0
   
   # Run all evaluators
   result = evaluate(
       function=my_function,
       dataset=dataset,
       evaluators=[accuracy, length_check, has_sources],
       api_key="your-api-key",
       project="your-project"
   )
   
   # Each evaluator's results stored as separate metrics

What if my evaluator encounters errors?
---------------------------------------

**Add Try-Except Blocks**

.. code-block:: python

   @evaluator()
   def robust_evaluator(outputs, inputs, ground_truth):
       """Evaluator with error handling."""
       try:
           # Your evaluation logic
           score = calculate_score(outputs, ground_truth)
           return {"score": score}
       
       except KeyError as e:
           # Missing expected key
           return {
               "score": 0.0,
               "error": f"Missing key: {e}",
               "error_type": "KeyError"
           }
       
       except ValueError as e:
           # Invalid value
           return {
               "score": 0.0,
               "error": f"Invalid value: {e}",
               "error_type": "ValueError"
           }
       
       except Exception as e:
           # General error
           return {
               "score": 0.0,
               "error": str(e),
               "error_type": type(e).__name__
           }

Best Practices
--------------

**Keep Evaluators Pure**

.. code-block:: python

   # ✅ Good: Pure function, no side effects
   @evaluator()
   def good_evaluator(outputs, inputs, ground_truth):
       score = calculate_score(outputs, ground_truth)
       return {"score": score}
   
   # ❌ Bad: Has side effects
   @evaluator()
   def bad_evaluator(outputs, inputs, ground_truth):
       database.save(outputs)  # Side effect!
       score = calculate_score(outputs, ground_truth)
       return {"score": score}

**Handle Missing Data**

.. code-block:: python

   @evaluator()
   def safe_evaluator(outputs, inputs, ground_truth):
       # Use .get() with defaults
       answer = outputs.get("answer", "")
       expected = ground_truth.get("answer", "") if ground_truth else ""
       
       if not answer:
           return {"score": 0.0, "reason": "No answer provided"}
       
       if not expected:
           return {"score": 0.5, "reason": "No ground truth available"}
       
       # Continue with evaluation
       score = compare(answer, expected)
       return {"score": score}

**Use Descriptive Names**

.. code-block:: python

   # ❌ Bad: Unclear name
   @evaluator(name="eval1")
   def e1(outputs, inputs, ground_truth):
       return 0.5
   
   # ✅ Good: Clear name
   @evaluator(name="answer_length_50_200_words")
   def check_answer_length(outputs, inputs, ground_truth):
       word_count = len(outputs.get("answer", "").split())
       return 1.0 if 50 <= word_count <= 200 else 0.5

See Also
--------

- :doc:`running-experiments` - Use evaluators in evaluate()
- :doc:`server-side-evaluators` - Configure evaluators in UI
- :doc:`best-practices` - Evaluation strategy design
- :doc:`../../reference/experiments/evaluators` - Complete @evaluator API reference

