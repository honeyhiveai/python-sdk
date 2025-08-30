Evaluation Framework Examples
=============================

This section provides comprehensive examples of using the HoneyHive evaluation framework, including threading support, custom evaluators, and advanced usage patterns.

Basic Usage
-----------

Simple Evaluation
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation.evaluators import evaluate

   # Basic evaluation with built-in evaluators
   result = evaluate(
       inputs={"prompt": "What is 2+2?"},
       outputs={"response": "The answer is 4"},
       ground_truth={"expected": "4"},
       evaluators=["exact_match", "length"]
   )
   
   print(f"Overall Score: {result.score}")
   print(f"Metrics: {result.metrics}")
   # Output:
   # Overall Score: 0.5
   # Metrics: {'exact_match': {'score': 0.0, 'feedback': 'No exact match'}, 
   #           'length': {'char_count': 18, 'word_count': 5}}

Decorator Pattern
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation.evaluators import evaluate_decorator

   @evaluate_decorator(evaluators=["exact_match", "length"])
   def generate_response(prompt: str) -> str:
       # Your LLM generation logic here
       return "Generated response based on the prompt"

   # Function is automatically evaluated when called
   result = generate_response("Hello, world!")
   print(f"Evaluation result: {result}")

Threading and Parallel Processing
---------------------------------

Parallel Evaluation
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation.evaluators import evaluate_with_evaluators
   import time

   # Large dataset evaluation with threading
   large_dataset = [
       ({"prompt": f"Question {i}"}, {"response": f"Answer {i}"})
       for i in range(1000)
   ]

   start_time = time.time()
   results = evaluate_with_evaluators(
       inputs=[item[0] for item in large_dataset],
       outputs=[item[1] for item in large_dataset],
       evaluators=["exact_match", "length"],
       max_workers=8,  # Parallel processing
       context={"batch_size": 1000}
   )
   end_time = time.time()

   print(f"Evaluated {len(results)} items in {end_time - start_time:.2f} seconds")
   print(f"Average score: {sum(r.score for r in results) / len(results):.3f}")

Batch Processing
~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation.evaluators import evaluate_batch

   # Batch evaluation of datasets
   batch_results = evaluate_batch(
       dataset=[
           ({"prompt": "Hello"}, {"response": "Hi"}),
           ({"prompt": "World"}, {"response": "Earth"}),
           ({"prompt": "Python"}, {"response": "Programming language"})
       ],
       evaluators=["exact_match", "length"],
       max_workers=2,
       context={"model": "gpt-4", "temperature": 0.7}
   )

   for i, result in enumerate(batch_results):
       print(f"Item {i}: Score {result.score:.3f}, Metrics: {result.metrics}")

Custom Evaluators
-----------------

Creating Custom Evaluators
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation.evaluators import BaseEvaluator, EvaluationResult
   from typing import Dict, Any, Optional
   import re

   class SentimentEvaluator(BaseEvaluator):
       def __init__(self, positive_words: list = None, negative_words: list = None):
           super().__init__("sentiment")
           self.positive_words = positive_words or ["good", "great", "excellent", "amazing"]
           self.negative_words = negative_words or ["bad", "terrible", "awful", "horrible"]
       
       def evaluate(
           self, 
           inputs: Dict[str, Any], 
           outputs: Dict[str, Any], 
           ground_truth: Optional[Dict[str, Any]] = None
       ) -> EvaluationResult:
           response = outputs.get("response", "")
           response_lower = response.lower()
           
           positive_count = sum(1 for word in self.positive_words if word in response_lower)
           negative_count = sum(1 for word in self.negative_words if word in response_lower)
           
           if positive_count > negative_count:
               score = min(1.0, positive_count / max(positive_count + negative_count, 1))
               sentiment = "positive"
           elif negative_count > positive_count:
               score = min(1.0, negative_count / max(positive_count + negative_count, 1))
               sentiment = "negative"
           else:
               score = 0.5
               sentiment = "neutral"
           
           return EvaluationResult(
               score=score,
               metrics={
                   "sentiment": sentiment,
                   "positive_words": positive_count,
                   "negative_words": negative_count,
                   "total_sentiment_words": positive_count + negative_count
               }
           )

   # Using the custom evaluator
   custom_evaluator = SentimentEvaluator()
   result = evaluate(
       inputs={"prompt": "How was your day?"},
       outputs={"response": "It was a great day!"},
       evaluators=[custom_evaluator]
   )
   
   print(f"Sentiment Score: {result.score}")
   print(f"Sentiment: {result.metrics['sentiment']['sentiment']}")

Advanced Custom Evaluator
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class AccuracyEvaluator(BaseEvaluator):
       def __init__(self, tolerance: float = 0.1):
           super().__init__("accuracy")
           self.tolerance = tolerance
       
       def evaluate(
           self, 
           inputs: Dict[str, Any], 
           outputs: Dict[str, Any], 
           ground_truth: Optional[Dict[str, Any]] = None
       ) -> EvaluationResult:
           if not ground_truth:
               return EvaluationResult(score=0.0, metrics={"error": "No ground truth provided"})
           
           predicted = outputs.get("response", "")
           expected = ground_truth.get("expected", "")
           
           # Calculate accuracy based on your domain logic
           if isinstance(predicted, (int, float)) and isinstance(expected, (int, float)):
               # Numeric comparison
               diff = abs(predicted - expected)
               if diff <= self.tolerance:
                   score = 1.0
               else:
                   score = max(0.0, 1.0 - (diff / max(abs(expected), 1)))
           else:
               # String comparison with fuzzy matching
               score = self._calculate_string_similarity(predicted, expected)
           
           return EvaluationResult(
               score=score,
               metrics={
                   "tolerance": self.tolerance,
                   "predicted": predicted,
                   "expected": expected,
                   "difference": abs(predicted - expected) if isinstance(predicted, (int, float)) else None
               }
           )
       
       def _calculate_string_similarity(self, pred: str, exp: str) -> float:
           # Simple Levenshtein-based similarity
           if pred == exp:
               return 1.0
           
           # Calculate edit distance
           m, n = len(pred), len(exp)
           dp = [[0] * (n + 1) for _ in range(m + 1)]
           
           for i in range(m + 1):
               dp[i][0] = i
           for j in range(n + 1):
               dp[0][j] = j
           
           for i in range(1, m + 1):
               for j in range(1, n + 1):
                   if pred[i-1] == exp[j-1]:
                       dp[i][j] = dp[i-1][j-1]
                   else:
                       dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
           
           max_len = max(m, n)
           similarity = 1.0 - (dp[m][n] / max_len)
           return max(0.0, similarity)

Advanced Usage Patterns
-----------------------

Mixed Evaluator Types
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation.evaluators import (
       evaluate_with_evaluators, 
       ExactMatchEvaluator, 
       LengthEvaluator
   )

   # Create custom evaluator instances
   custom_evaluator = SentimentEvaluator()
   
   # Evaluate with mixed evaluator types
   results = evaluate_with_evaluators(
       inputs=[{"prompt": "Hello"}, {"prompt": "World"}],
       outputs=[{"response": "Hi"}, {"response": "Earth"}],
       evaluators=[
           "exact_match",                    # String identifier
           LengthEvaluator("length"),        # Evaluator instance
           custom_evaluator,                 # Custom evaluator
           lambda x, y, z: {                # Lambda function
               "score": 0.8, 
               "metrics": {"custom": 0.8}
           }
       ],
       context={"model": "gpt-4", "temperature": 0.7},
       max_workers=4
   )

   for i, result in enumerate(results):
       print(f"Result {i}: Score {result.score:.3f}")
       print(f"  Metrics: {result.metrics}")

Context and Metadata
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Using evaluation context for rich metadata
   context = {
       "model": "gpt-4",
       "temperature": 0.7,
       "max_tokens": 100,
       "dataset": "test_set_2024",
       "evaluation_date": "2024-01-15",
       "evaluator_config": {
           "exact_match": {"case_sensitive": False},
           "length": {"min_length": 10, "max_length": 100}
       }
   }

   results = evaluate_with_evaluators(
       inputs=[{"prompt": "Hello"}],
       outputs=[{"response": "Hi there, how are you today?"}],
       evaluators=["exact_match", "length"],
       context=context,
       max_workers=2
   )

   # Context is preserved in results
   print(f"Evaluation Context: {results[0].metadata.get('context', {})}")

Error Handling and Resilience
-----------------------------

Robust Error Handling
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation.evaluators import evaluate_with_evaluators

   # Robust error handling in evaluation
   try:
       results = evaluate_with_evaluators(
           inputs=[{"prompt": "Hello"}],
           outputs=[{"response": "Hi"}],
           evaluators=["exact_match", "failing_evaluator"],
           max_workers=2
       )
       
       # Failed evaluators are logged but don't crash the process
       print(f"Successful evaluations: {len(results)}")
       
       # Check for failed evaluators
       for result in results:
           if "error" in result.metadata:
               print(f"Evaluator failed: {result.metadata['error']}")
       
   except Exception as e:
       print(f"Evaluation failed: {e}")

Custom Error Handling
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class RobustEvaluator(BaseEvaluator):
       def __init__(self, name: str, fallback_score: float = 0.0):
           super().__init__(name)
           self.fallback_score = fallback_score
       
       def evaluate(
           self, 
           inputs: Dict[str, Any], 
           outputs: Dict[str, Any], 
           ground_truth: Optional[Dict[str, Any]] = None
       ) -> EvaluationResult:
           try:
               # Your evaluation logic here
               score = self._calculate_score(inputs, outputs, ground_truth)
               return EvaluationResult(
                   score=score,
                   metrics={"calculated_score": score}
               )
           except Exception as e:
               # Graceful fallback
               return EvaluationResult(
                   score=self.fallback_score,
                   metrics={
                       "error": str(e),
                       "fallback_score": self.fallback_score,
                       "status": "failed"
                   }
               )
       
       def _calculate_score(self, inputs, outputs, ground_truth):
           # Your actual evaluation logic
           # This is just a placeholder
           return 0.8

Integration with Tracing
------------------------

Tracing-Integrated Evaluation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation.evaluators import evaluator
   from honeyhive import tracer

   @evaluator(evaluators=["exact_match", "length"])
   def traced_evaluation_function(prompt: str) -> str:
       with tracer.start_span("evaluation_generation") as span:
           span.set_attribute("prompt_length", len(prompt))
           span.set_attribute("model", "gpt-4")
           
           response = generate_response(prompt)
           
           span.set_attribute("response_length", len(response))
           span.set_attribute("generation_time", time.time())
           
           return response

   # Function is automatically traced and evaluated
   result = traced_evaluation_function("Generate a response")

Performance Optimization
------------------------

Optimizing for Large Datasets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   from concurrent.futures import ThreadPoolExecutor
   from honeyhive.evaluation.evaluators import evaluate_batch

   def optimize_evaluation_workflow():
       # Large dataset
       dataset_size = 10000
       dataset = [
           ({"prompt": f"Question {i}"}, {"response": f"Answer {i}"})
           for i in range(dataset_size)
       ]
       
       # Test different worker configurations
       worker_configs = [1, 2, 4, 8, 16]
       
       for workers in worker_configs:
           start_time = time.time()
           
           results = evaluate_batch(
               dataset=dataset,
               evaluators=["exact_match", "length"],
               max_workers=workers,
               context={"optimization_test": True}
           )
           
           end_time = time.time()
           duration = end_time - start_time
           
           print(f"Workers: {workers:2d}, Time: {duration:6.2f}s, "
                 f"Rate: {dataset_size/duration:8.1f} items/sec")

   # Run optimization test
   optimize_evaluation_workflow()

Memory Management
~~~~~~~~~~~~~~~~~

.. code-block:: python

   def memory_efficient_evaluation():
       # Process in chunks to manage memory
       chunk_size = 1000
       total_items = 50000
       
       all_results = []
       
       for chunk_start in range(0, total_items, chunk_size):
           chunk_end = min(chunk_start + chunk_size, total_items)
           
           # Process chunk
           chunk_dataset = [
               ({"prompt": f"Q{i}"}, {"response": f"A{i}"})
               for i in range(chunk_start, chunk_end)
           ]
           
           chunk_results = evaluate_batch(
               dataset=chunk_dataset,
               evaluators=["exact_match", "length"],
               max_workers=4
           )
           
           # Process results immediately
           for result in chunk_results:
               # Do something with the result
               all_results.append(result.score)
           
           # Clear chunk data to free memory
           del chunk_dataset
           del chunk_results
           
           print(f"Processed chunk {chunk_start//chunk_size + 1}/{(total_items + chunk_size - 1)//chunk_size}")

API Integration Examples
------------------------

Creating Evaluation Runs
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation.evaluators import create_evaluation_run

   # Create an evaluation run
   run = create_evaluation_run(
       name="model_evaluation_2024",
       project="my_project",
       results=results,
       metadata={
           "model_version": "1.0",
           "dataset": "test_set",
           "evaluation_date": "2024-01-15",
           "total_items": len(results),
           "average_score": sum(r.score for r in results) / len(results)
       }
   )

   if run:
       print(f"Created evaluation run: {run.run_id}")
   else:
       print("Failed to create evaluation run")

Batch API Operations
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def batch_evaluation_with_api():
       # Process large dataset in batches
       batch_size = 100
       total_results = []
       
       for i in range(0, len(large_dataset), batch_size):
           batch = large_dataset[i:i + batch_size]
           
           # Evaluate batch
           batch_results = evaluate_batch(
               dataset=batch,
               evaluators=["exact_match", "length"],
               max_workers=4
           )
           
           # Store batch results
           run = create_evaluation_run(
               name=f"batch_evaluation_{i//batch_size + 1}",
               project="my_project",
               results=batch_results,
               metadata={"batch_number": i//batch_size + 1}
           )
           
           total_results.extend(batch_results)
           
           print(f"Processed batch {i//batch_size + 1}")
       
       return total_results

Best Practices
--------------

1. **Choose Appropriate Evaluators**: Select evaluators that match your use case
2. **Leverage Threading**: Use `max_workers` for large datasets
3. **Handle Errors Gracefully**: Implement proper error handling for production use
4. **Monitor Performance**: Track evaluation times and resource usage
5. **Store Results**: Use `create_evaluation_run` to persist evaluation data
6. **Custom Evaluators**: Create domain-specific evaluators for specialized tasks
7. **Context Management**: Use evaluation context for metadata and configuration
8. **Memory Management**: Process large datasets in chunks
9. **Thread Safety**: Ensure custom evaluators are thread-safe
10. **Performance Testing**: Test different worker configurations for your environment

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Evaluation framework configuration
   export HH_EVALUATION_MAX_WORKERS=8
   export HH_EVALUATION_TIMEOUT=60
   export HH_EVALUATION_BATCH_SIZE=1000
   export HH_EVALUATION_LOG_LEVEL=INFO

Programmatic Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation.evaluators import evaluate_with_evaluators

   # Configure evaluation parameters
   results = evaluate_with_evaluators(
       inputs=inputs,
       outputs=outputs,
       evaluators=evaluators,
       max_workers=16,        # Override default
       context={
           "timeout": 120,     # Custom timeout
           "batch_size": 500,  # Custom batch size
           "log_level": "DEBUG"
       }
   )

This comprehensive examples section demonstrates all the capabilities of the evaluation framework, from basic usage to advanced patterns and performance optimization.
