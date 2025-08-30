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

🧪 **Testing & Quality Assurance**
----------------------------------

The SDK maintains high quality through comprehensive testing with **72.10% coverage** (exceeds 70% requirement).

**Test Statistics:**

* **Total Tests**: 816 tests (99.75% success rate)
* **Coverage**: 72.10% (4,158 statements, 1,160 missed)
* **Unit Tests**: 21 test files
* **Integration Tests**: 8 test files  
* **Tracer Tests**: 1 test file

**Quality Features:**

* **Test Isolation**: Clean environment setup with proper cleanup
* **I/O Error Prevention**: OpenTelemetry mocking prevents test crashes
* **Multi-Python Support**: Python 3.11, 3.12, and 3.13
* **Coverage Enforcement**: 70% minimum requirement (✅ exceeded)

**Coverage Highlights:**

* **High Coverage**: Evaluators (85%), Cache (98%), Logger (98%)
* **Areas for Improvement**: CLI, Metrics API, Connection Pool

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   README
   API_REFERENCE
   FEATURE_LIST
   IMPLEMENTATION_GUIDE
   OPENINFERENCE_INTEGRATION
   EVALUATION_CHANGELOG
   TESTING
   LAMBDA_TESTING
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
