HoneyHive Python SDK Documentation
==================================

Welcome to the comprehensive documentation for the HoneyHive Python SDK. This SDK provides LLM observability, evaluation, and tracing capabilities with OpenTelemetry integration.

🚀 **What's New: Comprehensive Evaluation Framework**
-----------------------------------------------------

The SDK now includes a **production-ready evaluation framework** with threading support, built-in evaluators, custom evaluator support, and seamless API integration.

**Key Features:**
- **Threading Support**: Parallel evaluation processing with `ThreadPoolExecutor`
- **Built-in Evaluators**: Exact match, F1 score, length, and semantic similarity
- **Custom Evaluators**: Extensible framework for domain-specific evaluation
- **Decorator Pattern**: Seamless integration with `@evaluate_decorator`
- **API Integration**: Store evaluation results in HoneyHive
- **Batch Processing**: Efficient evaluation of large datasets

**Quick Start:**

.. code-block:: python

   from honeyhive.evaluation.evaluators import evaluate_decorator
   
   @evaluate_decorator(evaluators=["exact_match", "length"])
   def generate_response(prompt: str) -> str:
       return "Generated response"

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   README
   API_REFERENCE
   FEATURE_LIST
   IMPLEMENTATION_GUIDE
   OPENINFERENCE_INTEGRATION
   EVALUATION_CHANGELOG
   api/index
   tracer/index
   evaluation/index
   utils/index
   examples/README
   examples/BASIC_USAGE_PATTERNS
   examples/ADVANCED_PATTERNS
   examples/PRACTICAL_EXAMPLES

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
