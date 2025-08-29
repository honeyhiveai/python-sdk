Evaluation Framework
====================

This section covers the comprehensive evaluation functionality of the HoneyHive Python SDK, including built-in evaluators, custom evaluator support, threading capabilities, and integration with the HoneyHive API.

Overview
--------

The evaluation framework provides a robust system for evaluating LLM outputs with support for:

* **Built-in Evaluators**: Pre-implemented evaluation metrics
* **Custom Evaluators**: User-defined evaluation logic
* **Threading Support**: Parallel evaluation processing
* **Decorator Pattern**: Easy integration with existing code
* **API Integration**: Store evaluation results in HoneyHive
* **Batch Processing**: Efficient evaluation of large datasets

Core Components
---------------

.. automodule:: honeyhive.evaluation.evaluators
   :members:
   :undoc-members:
   :show-inheritance:

Built-in Evaluators
-------------------

The SDK includes several pre-implemented evaluators:

* **ExactMatchEvaluator**: Perfect string matching
* **F1ScoreEvaluator**: F1 score calculation for text similarity
* **LengthEvaluator**: Text length analysis and scoring
* **SemanticSimilarityEvaluator**: Meaning-based text comparison

Custom Evaluators
-----------------

Create custom evaluators by inheriting from ``BaseEvaluator``:

.. code-block:: python

   from honeyhive.evaluation.evaluators import BaseEvaluator, EvaluationResult
   from typing import Dict, Any, Optional

   class CustomAccuracyEvaluator(BaseEvaluator):
       def __init__(self, tolerance: float = 0.1):
           super().__init__("custom_accuracy")
           self.tolerance = tolerance
       
       def evaluate(
           self, 
           inputs: Dict[str, Any], 
           outputs: Dict[str, Any], 
           ground_truth: Optional[Dict[str, Any]] = None
       ) -> EvaluationResult:
           # Your custom evaluation logic here
           score = self._calculate_accuracy(outputs, ground_truth)
           return EvaluationResult(
               score=score,
               metrics={"accuracy": score, "tolerance": self.tolerance}
           )

Decorator Pattern
-----------------

Use the ``@evaluate_decorator`` to automatically evaluate function outputs:

.. code-block:: python

   from honeyhive.evaluation.evaluators import evaluate_decorator

   @evaluate_decorator(evaluators=["exact_match", "length"])
   def generate_response(prompt: str) -> str:
       # Your LLM generation logic here
       return "Generated response"

   # Function is automatically evaluated when called
   result = generate_response("Hello, world!")

Threading Support
-----------------

The evaluation framework supports parallel processing for improved performance:

.. code-block:: python

   from honeyhive.evaluation.evaluators import evaluate_batch, evaluate_with_evaluators

   # Parallel evaluation with multiple evaluators
   results = evaluate_with_evaluators(
       inputs=[{"prompt": "Hello"}, {"prompt": "World"}],
       outputs=[{"response": "Hi"}, {"response": "Earth"}],
       evaluators=["exact_match", "length", "semantic_similarity"],
       max_workers=4  # Parallel processing
   )

   # Batch evaluation of datasets
   batch_results = evaluate_batch(
       dataset=[
           ({"prompt": "Hello"}, {"response": "Hi"}),
           ({"prompt": "World"}, {"response": "Earth"})
       ],
       evaluators=["exact_match", "length"],
       max_workers=2
   )

API Integration
---------------

Store evaluation results in HoneyHive for analysis and monitoring:

.. code-block:: python

   from honeyhive.evaluation.evaluators import create_evaluation_run

   # Create an evaluation run
   run = create_evaluation_run(
       name="model_evaluation_2024",
       project="my_project",
       results=results,
       metadata={"model_version": "1.0", "dataset": "test_set"}
   )

Usage Examples
--------------

Basic Evaluation
~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation.evaluators import evaluate

   # Simple string evaluation
   result = evaluate(
       inputs={"prompt": "What is 2+2?"},
       outputs={"response": "The answer is 4"},
       ground_truth={"expected": "4"},
       evaluators=["exact_match", "length"]
   )
   
   print(f"Overall Score: {result.score}")
   print(f"Metrics: {result.metrics}")

Advanced Evaluation Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation.evaluators import (
       evaluate_with_evaluators, 
       ExactMatchEvaluator, 
       LengthEvaluator
   )

   # Create custom evaluator instances
   custom_evaluator = CustomAccuracyEvaluator(tolerance=0.1)
   
   # Evaluate with mixed evaluator types
   results = evaluate_with_evaluators(
       inputs=[{"prompt": "Hello"}, {"prompt": "World"}],
       outputs=[{"response": "Hi"}, {"response": "Earth"}],
       evaluators=[
           "exact_match",           # String identifier
           LengthEvaluator("length"),  # Evaluator instance
           custom_evaluator,        # Custom evaluator
           lambda x, y, z: {"score": 0.8, "metrics": {"custom": 0.8}}  # Lambda function
       ],
       context={"model": "gpt-4", "temperature": 0.7},
       max_workers=4
   )

Threading and Performance
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation.evaluators import evaluate_batch
   import time

   # Large dataset evaluation with threading
   large_dataset = [
       ({"prompt": f"Question {i}"}, {"response": f"Answer {i}"})
       for i in range(1000)
   ]

   start_time = time.time()
   results = evaluate_batch(
       dataset=large_dataset,
       evaluators=["exact_match", "length"],
       max_workers=8,  # Parallel processing
       context={"batch_size": 1000}
   )
   end_time = time.time()

   print(f"Evaluated {len(results)} items in {end_time - start_time:.2f} seconds")

Integration with Tracing
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation.evaluators import evaluator
   from honeyhive import tracer

   @evaluator(evaluators=["exact_match", "length"])
   def traced_evaluation_function(prompt: str) -> str:
       with tracer.start_span("evaluation_generation") as span:
           span.set_attribute("prompt_length", len(prompt))
           response = generate_response(prompt)
           span.set_attribute("response_length", len(response))
           return response

   # Function is automatically traced and evaluated
   result = traced_evaluation_function("Generate a response")

Error Handling
~~~~~~~~~~~~~~

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
       
   except Exception as e:
       print(f"Evaluation failed: {e}")

Configuration
-------------

The evaluation framework can be configured through environment variables:

* **HH_EVALUATION_MAX_WORKERS**: Maximum number of parallel workers (default: 4)
* **HH_EVALUATION_TIMEOUT**: Evaluation timeout in seconds (default: 30)
* **HH_EVALUATION_BATCH_SIZE**: Default batch size for processing (default: 100)

Best Practices
--------------

1. **Use Appropriate Evaluators**: Choose evaluators that match your use case
2. **Leverage Threading**: Use `max_workers` for large datasets
3. **Handle Errors Gracefully**: Implement proper error handling for production use
4. **Monitor Performance**: Track evaluation times and resource usage
5. **Store Results**: Use `create_evaluation_run` to persist evaluation data
6. **Custom Evaluators**: Create domain-specific evaluators for specialized tasks
7. **Context Management**: Use evaluation context for metadata and configuration

Performance Considerations
--------------------------

* **Parallel Processing**: Use `max_workers` to parallelize evaluation
* **Batch Processing**: Process large datasets in batches for efficiency
* **Resource Management**: Monitor memory usage with large datasets
* **Caching**: Cache evaluation results when appropriate
* **Async Support**: Use async evaluators for I/O-bound operations

Threading Architecture
----------------------

The evaluation framework uses Python's `ThreadPoolExecutor` for parallel processing:

* **Context Propagation**: Uses `contextvars` to maintain context across threads
* **Thread Safety**: All evaluators are designed to be thread-safe
* **Resource Management**: Automatic cleanup of thread resources
* **Error Isolation**: Failures in one thread don't affect others
* **Scalability**: Configurable worker limits for different environments

API Reference
-------------

For detailed API documentation, see the :doc:`../api/index` section.

Examples
--------

See the :doc:`examples` section for comprehensive usage examples including:

* **Basic Usage**: Simple evaluation examples
* **Threading**: Parallel processing examples
* **Custom Evaluators**: Creating domain-specific evaluators
* **Advanced Patterns**: Mixed evaluator types and context management
* **Performance Optimization**: Large dataset handling and memory management
* **API Integration**: Storing evaluation results in HoneyHive
* **Error Handling**: Robust error handling patterns
* **Best Practices**: Production-ready evaluation workflows

.. toctree::
   :maxdepth: 1
   :caption: Evaluation Examples:

   examples
