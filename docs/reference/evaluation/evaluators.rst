Evaluation Framework API Reference
==================================

.. note::
   **Complete API documentation for HoneyHive's evaluation framework**
   
   Built-in evaluators and custom evaluation patterns for LLM output assessment.

.. currentmodule:: honeyhive.evaluation

The HoneyHive evaluation framework provides comprehensive tools for assessing LLM outputs across multiple dimensions:

- Quality assessment
- Accuracy verification
- Safety evaluation
- Performance analysis

**Key Features:**

- Built-in evaluators for common use cases
- Custom evaluator development framework
- Multi-evaluator orchestration
- Async evaluation support
- Integration with tracing pipeline
- Comprehensive scoring and feedback

Base Classes
------------

BaseEvaluator
~~~~~~~~~~~~~

.. note::
   
   The ``BaseEvaluator`` class has been deprecated in favor of the decorator-based approach.
   Please use the ``@evaluator`` decorator instead. See :doc:`../experiments/evaluators` for details.

.. .. autoclass:: BaseEvaluator (DEPRECATED - commented out)
..    :members:
..    :undoc-members:
..    :show-inheritance:

The abstract base class for all evaluators.

**Abstract Methods:**

.. py:method:: evaluate(input_text: str, output_text: str, context: Optional[dict] = None) -> dict

   Evaluate the quality of an output given an input.
   
   **Parameters:**
   
   :param input_text: The input prompt or question
   :type input_text: str
   
   :param output_text: The generated output to evaluate
   :type output_text: str
   
   :param context: Additional context for evaluation
   :type context: Optional[dict]
   
   **Returns:**
   
   :rtype: dict
   :returns: Evaluation result with score and feedback
   
   **Required Return Format:**
   
   .. code-block:: python
   
      {
          "score": float,        # 0.0 to 1.0 
          "feedback": str,       # Human-readable feedback
          "metrics": dict,       # Optional detailed metrics
          "passed": bool,        # Optional binary pass/fail
          "confidence": float    # Optional confidence in score
      }

**Custom Evaluator Example:**

.. code-block:: python

   from honeyhive.evaluation import BaseEvaluator
   
   class CustomQualityEvaluator(BaseEvaluator):
       def __init__(self, criteria: List[str] = None):
           self.criteria = criteria or ["clarity", "relevance", "completeness"]
       
       def evaluate(self, input_text: str, output_text: str, context: dict = None) -> dict:
           """Custom evaluation logic."""
           
           # Calculate individual criterion scores
           scores = {}
           for criterion in self.criteria:
               scores[criterion] = self._evaluate_criterion(output_text, criterion)
           
           # Overall score
           overall_score = sum(scores.values()) / len(scores)
           
           # Generate feedback
           feedback_parts = []
           for criterion, score in scores.items():
               if score > 0.8:
                   feedback_parts.append(f"Excellent {criterion}")
               elif score > 0.6:
                   feedback_parts.append(f"Good {criterion}")
               else:
                   feedback_parts.append(f"Needs improvement in {criterion}")
           
           return {
               "score": overall_score,
               "feedback": "; ".join(feedback_parts),
               "metrics": {
                   "criterion_scores": scores,
                   "criteria_count": len(self.criteria)
               },
               "passed": overall_score >= 0.7,
               "confidence": 0.9
           }
       
       def _evaluate_criterion(self, text: str, criterion: str) -> float:
           """Evaluate a specific criterion."""
           # Implement your criterion-specific logic here
           if criterion == "clarity":
               return len(text.split('.')) / 10  # Simple clarity heuristic
           elif criterion == "relevance":
               return 0.8  # Placeholder
           elif criterion == "completeness":
               return min(len(text) / 100, 1.0)  # Length-based completeness
           return 0.5

Built-in Evaluators
-------------------

QualityScoreEvaluator
~~~~~~~~~~~~~~~~~~~~~

**QualityScoreEvaluator**

Evaluates the overall quality of generated content based on multiple criteria.

**Example Implementation:**

.. code-block:: python

   from honeyhive.evaluation.evaluators import BaseEvaluator, EvaluationResult
   from typing import List, Dict, Any

   class QualityScoreEvaluator(BaseEvaluator):
       def __init__(self, criteria: List[str] = None, weights: Dict[str, float] = None):
           super().__init__("quality_score")
           self.criteria = criteria or ["clarity", "accuracy", "completeness"]
           self.weights = weights or {criterion: 1.0 for criterion in self.criteria}
       
       def evaluate(self, inputs: dict, outputs: dict, ground_truth: dict = None) -> EvaluationResult:
           scores = {}
           total_score = 0.0
           
           for criterion in self.criteria:
               score = self._evaluate_criterion(criterion, inputs, outputs, ground_truth)
               scores[criterion] = score
               total_score += score * self.weights.get(criterion, 1.0)
           
           final_score = total_score / sum(self.weights.values())
           
           return EvaluationResult(
               score=final_score,
               metrics={
                   "individual_scores": scores,
                   "weighted_score": final_score,
                   "criteria_evaluated": self.criteria
               }
           )

Evaluates output quality across multiple configurable criteria.

**Initialization:**

.. code-block:: python

   from honeyhive.evaluation import QualityScoreEvaluator
   
   # Basic quality evaluation
   evaluator = QualityScoreEvaluator()
   
   # Custom criteria
   evaluator = QualityScoreEvaluator(
       criteria=["accuracy", "relevance", "clarity", "completeness"],
       weights={"accuracy": 0.4, "relevance": 0.3, "clarity": 0.2, "completeness": 0.1}
   )
   
   # With custom scoring thresholds
   evaluator = QualityScoreEvaluator(
       criteria=["helpfulness", "safety"],
       min_score=0.8,  # Minimum acceptable score
       confidence_threshold=0.9  # Minimum confidence required
   )

**Usage Examples:**

.. code-block:: python

   # Basic evaluation
   result = evaluator.evaluate(
       input_text="What is machine learning?",
       output_text="Machine learning is a subset of artificial intelligence...",
       context={"domain": "education", "audience": "beginner"}
   )
   
   print(f"Score: {result['score']}")
   print(f"Feedback: {result['feedback']}")
   print(f"Passed: {result['passed']}")

FactualAccuracyEvaluator
~~~~~~~~~~~~~~~~~~~~~~~~

**FactualAccuracyEvaluator**

Evaluates the factual accuracy of generated content against known facts or ground truth.

**Example Implementation:**

.. code-block:: python

   class FactualAccuracyEvaluator(BaseEvaluator):
       def __init__(self, knowledge_base: dict = None):
           super().__init__("factual_accuracy")
           self.knowledge_base = knowledge_base or {}
       
       def evaluate(self, inputs: dict, outputs: dict, ground_truth: dict = None) -> EvaluationResult:
           response = outputs.get("response", "")
           facts_to_check = ground_truth.get("facts", []) if ground_truth else []
           
           verified_facts = 0
           questionable_claims = []
           
           for fact in facts_to_check:
               if self._verify_fact(fact, response):
                   verified_facts += 1
               else:
                   questionable_claims.append(fact)
           
           accuracy_score = verified_facts / len(facts_to_check) if facts_to_check else 1.0
           
           return EvaluationResult(
               score=accuracy_score,
               metrics={
                   "verified_facts": verified_facts,
                   "total_facts": len(facts_to_check),
                   "questionable_claims": questionable_claims
               }
           )

Evaluates the factual accuracy of outputs using external knowledge sources.

**Initialization:**

.. code-block:: python

   from honeyhive.evaluation import FactualAccuracyEvaluator
   
   # Basic factual accuracy
   evaluator = FactualAccuracyEvaluator()
   
   # With custom knowledge sources
   evaluator = FactualAccuracyEvaluator(
       knowledge_sources=["wikipedia", "custom_kb"],
       fact_check_threshold=0.9,
       require_citations=True
   )
   
   # With custom fact-checking model
   evaluator = FactualAccuracyEvaluator(
       fact_check_model="custom-fact-checker-v2",
       confidence_threshold=0.85
   )

**Usage Examples:**

.. code-block:: python

   # Fact-check a statement
   result = evaluator.evaluate(
       input_text="When was the Eiffel Tower built?",
       output_text="The Eiffel Tower was completed in 1889 for the Paris Exposition.",
       context={"expected_facts": ["built_date: 1889", "purpose: Paris Exposition"]}
   )
   
   print(f"Factual accuracy: {result['score']}")
   print(f"Verified facts: {result['metrics']['verified_facts']}")
   print(f"Questionable claims: {result['metrics']['questionable_claims']}")

LengthEvaluator
~~~~~~~~~~~~~~~

.. note::
   
   The ``LengthEvaluator`` class has been deprecated in favor of the decorator-based approach.
   Please implement custom length evaluators using the ``@evaluator`` decorator.

.. .. autoclass:: LengthEvaluator (DEPRECATED - commented out)
..    :members:
..    :undoc-members:
..    :show-inheritance:

Evaluates output length against specified constraints.

**Initialization:**

.. code-block:: python

   from honeyhive.evaluation import LengthEvaluator
   
   # Character-based length evaluation
   evaluator = LengthEvaluator(
       min_length=50,
       max_length=200,
       unit="characters"
   )
   
   # Word-based length evaluation
   evaluator = LengthEvaluator(
       min_length=10,
       max_length=50,
       unit="words",
       penalty_factor=0.1  # Reduce score by 10% for each unit outside range
   )
   
   # Token-based evaluation
   evaluator = LengthEvaluator(
       target_length=100,
       unit="tokens",
       tolerance=0.2  # Allow 20% variance from target
   )

**Usage Examples:**

.. code-block:: python

   # Evaluate length constraints
   result = evaluator.evaluate(
       input_text="Summarize this article in 100 words",
       output_text="This is a summary of the article..." # 85 words
   )
   
   print(f"Length score: {result['score']}")
   print(f"Actual length: {result['metrics']['actual_length']}")
   print(f"Within bounds: {result['passed']}")

ToxicityEvaluator
~~~~~~~~~~~~~~~~~

**ToxicityEvaluator**

Evaluates content for toxicity, harmful language, and safety concerns.

**Example Implementation:**

.. code-block:: python

   class ToxicityEvaluator(BaseEvaluator):
       def __init__(self, threshold: float = 0.7, toxic_keywords: List[str] = None):
           super().__init__("toxicity")
           self.threshold = threshold
           self.toxic_keywords = toxic_keywords or []
       
       def evaluate(self, inputs: dict, outputs: dict, ground_truth: dict = None) -> EvaluationResult:
           text = outputs.get("response", "")
           
           # Simple keyword-based toxicity detection
           toxicity_flags = []
           for keyword in self.toxic_keywords:
               if keyword.lower() in text.lower():
                   toxicity_flags.append(keyword)
           
           # Calculate toxicity score (1.0 = completely safe, 0.0 = highly toxic)
           safety_score = max(0.0, 1.0 - (len(toxicity_flags) * 0.2))
           is_safe = safety_score >= self.threshold
           
           return EvaluationResult(
               score=safety_score,
               metrics={
                   "toxicity_flags": toxicity_flags,
                   "safety_score": safety_score,
                   "is_safe": is_safe
               }
           )

Evaluates content for toxicity, bias, and harmful content.

**Initialization:**

.. code-block:: python

   from honeyhive.evaluation import ToxicityEvaluator
   
   # Basic toxicity detection
   evaluator = ToxicityEvaluator()
   
   # Custom toxicity threshold
   evaluator = ToxicityEvaluator(
       toxicity_threshold=0.8,  # Stricter threshold
       categories=["toxicity", "severe_toxicity", "identity_attack", "threat"],
       model="perspective-api"
   )
   
   # With custom bias detection
   evaluator = ToxicityEvaluator(
       include_bias_detection=True,
       bias_categories=["gender", "race", "religion", "political"],
       severity_weights={"severe_toxicity": 2.0, "identity_attack": 1.5}
   )

**Usage Examples:**

.. code-block:: python

   # Check for toxic content
   result = evaluator.evaluate(
       input_text="Generate a response about social policies",
       output_text="Here's a balanced view on social policies...",
       context={"audience": "general_public", "sensitivity": "high"}
   )
   
   print(f"Safety score: {result['score']}")
   print(f"Toxicity flags: {result['metrics']['toxicity_flags']}")
   print(f"Safe for publication: {result['passed']}")

RelevanceEvaluator
~~~~~~~~~~~~~~~~~~

**RelevanceEvaluator**

This evaluator assesses the relevance of generated content to the given prompt or context.

**Example Implementation**:

.. code-block:: python

   from honeyhive.evaluation.evaluators import BaseEvaluator, EvaluationResult

   class RelevanceEvaluator(BaseEvaluator):
       def __init__(self, threshold: float = 0.7):
           super().__init__("relevance")
           self.threshold = threshold
       
       def evaluate(self, inputs: dict, outputs: dict, ground_truth: dict = None) -> EvaluationResult:
           prompt = inputs.get("prompt", "")
           response = outputs.get("response", "")
           
           # Simple relevance scoring based on keyword overlap
           prompt_words = set(prompt.lower().split())
           response_words = set(response.lower().split())
           
           if len(prompt_words) == 0:
               score = 0.0
           else:
               overlap = len(prompt_words.intersection(response_words))
               score = min(overlap / len(prompt_words), 1.0)
           
           return EvaluationResult(
               score=score,
               metrics={
                   "relevance_score": score,
                   "threshold_met": score >= self.threshold,
                   "keyword_overlap": overlap
               }
           )

Evaluates how relevant the output is to the input query.

**Initialization:**

.. code-block:: python

   from honeyhive.evaluation import RelevanceEvaluator
   
   # Semantic relevance evaluation
   evaluator = RelevanceEvaluator(
       method="semantic_similarity",
       model="sentence-transformers/all-MiniLM-L6-v2"
   )
   
   # Keyword-based relevance
   evaluator = RelevanceEvaluator(
       method="keyword_overlap",
       keyword_weight=0.7,
       semantic_weight=0.3
   )
   
   # Context-aware relevance
   evaluator = RelevanceEvaluator(
       use_context=True,
       context_weight=0.4,
       penalize_off_topic=True
   )

**Usage Examples:**

.. code-block:: python

   # Evaluate relevance to query
   result = evaluator.evaluate(
       input_text="How does photosynthesis work in plants?",
       output_text="Photosynthesis is the process by which plants convert sunlight into chemical energy...",
       context={"topic": "biology", "education_level": "high_school"}
   )
   
   print(f"Relevance score: {result['score']}")
   print(f"Key topics covered: {result['metrics']['topics_covered']}")

Multi-Evaluator Support
-----------------------

MultiEvaluator
~~~~~~~~~~~~~~

**MultiEvaluator**

Combines multiple evaluators to provide comprehensive assessment.

**Example Implementation**:

.. code-block:: python

   from honeyhive.evaluation.evaluators import BaseEvaluator, EvaluationResult
   from typing import List, Dict, Any

   class MultiEvaluator(BaseEvaluator):
       def __init__(self, evaluators: List[BaseEvaluator], weights: Dict[str, float] = None):
           super().__init__("multi_evaluator")
           self.evaluators = evaluators
           self.weights = weights or {}
       
       def evaluate(self, inputs: dict, outputs: dict, ground_truth: dict = None) -> EvaluationResult:
           results = []
           total_score = 0.0
           total_weight = 0.0
           
           for evaluator in self.evaluators:
               result = evaluator.evaluate(inputs, outputs, ground_truth)
               weight = self.weights.get(evaluator.name, 1.0)
               
               results.append({
                   "evaluator": evaluator.name,
                   "score": result.score,
                   "weight": weight,
                   "metrics": result.metrics
               })
               
               total_score += result.score * weight
               total_weight += weight
           
           final_score = total_score / total_weight if total_weight > 0 else 0.0
           
           return EvaluationResult(
               score=final_score,
               metrics={
                   "individual_results": results,
                   "weighted_average": final_score,
                   "total_evaluators": len(self.evaluators)
               }
           )

Orchestrates multiple evaluators for comprehensive assessment.

**Initialization:**

.. code-block:: python

   from honeyhive.evaluation import (
       MultiEvaluator, QualityScoreEvaluator, 
       FactualAccuracyEvaluator, LengthEvaluator, ToxicityEvaluator
   )
   
   # Basic multi-evaluator setup
   multi_eval = MultiEvaluator([
       QualityScoreEvaluator(),
       FactualAccuracyEvaluator(),
       LengthEvaluator(min_length=20, max_length=200)
   ])
   
   # Weighted evaluation
   multi_eval = MultiEvaluator(
       evaluators=[
           QualityScoreEvaluator(),
           FactualAccuracyEvaluator(),
           ToxicityEvaluator()
       ],
       weights=[0.4, 0.4, 0.2],  # Quality and accuracy weighted higher
       aggregation_method="weighted_average"
   )
   
   # Hierarchical evaluation (all must pass)
   multi_eval = MultiEvaluator(
       evaluators=[
           ToxicityEvaluator(),      # Safety first
           FactualAccuracyEvaluator(), # Then accuracy
           QualityScoreEvaluator()   # Finally quality
       ],
       aggregation_method="all_pass",
       short_circuit=True  # Stop on first failure
   )

**Aggregation Methods:**

.. code-block:: python

   # Available aggregation methods
   aggregation_methods = [
       "weighted_average",  # Default: weighted average of scores
       "arithmetic_mean",   # Simple average
       "geometric_mean",    # Geometric mean (penalizes low scores)
       "harmonic_mean",     # Harmonic mean (heavily penalizes low scores)
       "min_score",         # Minimum score (conservative)
       "max_score",         # Maximum score (optimistic)
       "all_pass",          # All evaluators must pass
       "majority_pass",     # Majority must pass
       "custom"             # Use custom aggregation function
   ]

**Usage Examples:**

.. code-block:: python

   # Comprehensive evaluation
   result = multi_eval.evaluate(
       input_text="Explain quantum computing to a beginner",
       output_text="Quantum computing uses quantum mechanical phenomena...",
       context={
           "audience": "beginner",
           "domain": "technology",
           "length_requirement": "medium"
       }
   )
   
   print(f"Overall score: {result['score']}")
   print(f"Individual scores: {result['metrics']['individual_scores']}")
   print(f"All checks passed: {result['passed']}")
   
   # Access individual evaluator results
   for evaluator_name, individual_result in result['metrics']['evaluator_results'].items():
       print(f"{evaluator_name}: {individual_result['score']} - {individual_result['feedback']}")

**Custom Aggregation:**

.. code-block:: python

   def custom_aggregation(results: List[dict]) -> dict:
       """Custom aggregation logic."""
       
       # Safety evaluator is blocking
       safety_result = next((r for r in results if r['evaluator_type'] == 'toxicity'), None)
       if safety_result and not safety_result['passed']:
           return {
               "score": 0.0,
               "feedback": "Failed safety check",
               "passed": False
           }
       
       # Average other scores
       other_scores = [r['score'] for r in results if r['evaluator_type'] != 'toxicity']
       avg_score = sum(other_scores) / len(other_scores) if other_scores else 0.0
       
       return {
           "score": avg_score,
           "feedback": f"Safety passed, average quality: {avg_score:.2f}",
           "passed": avg_score >= 0.7
       }
   
   multi_eval = MultiEvaluator(
       evaluators=[safety_eval, quality_eval, accuracy_eval],
       aggregation_method="custom",
       custom_aggregation_fn=custom_aggregation
   )

Async Evaluation Support
------------------------

AsyncEvaluator
~~~~~~~~~~~~~~

**AsyncEvaluator**

Base class for asynchronous evaluation operations.

**Example Implementation**:

.. code-block:: python

   import asyncio
   from honeyhive.evaluation.evaluators import BaseEvaluator, EvaluationResult

   class AsyncEvaluator(BaseEvaluator):
       def __init__(self, name: str, timeout: float = 30.0):
           super().__init__(name)
           self.timeout = timeout
       
       async def evaluate_async(self, inputs: dict, outputs: dict, ground_truth: dict = None) -> EvaluationResult:
           """Async evaluation method to be implemented by subclasses."""
           raise NotImplementedError("Subclasses must implement evaluate_async")
       
       def evaluate(self, inputs: dict, outputs: dict, ground_truth: dict = None) -> EvaluationResult:
           """Synchronous wrapper for async evaluation."""
           try:
               loop = asyncio.get_event_loop()
           except RuntimeError:
               loop = asyncio.new_event_loop()
               asyncio.set_event_loop(loop)
           
           return loop.run_until_complete(
               asyncio.wait_for(
                   self.evaluate_async(inputs, outputs, ground_truth),
                   timeout=self.timeout
               )
           )

Base class for asynchronous evaluators.

**Async Evaluator Example:**

.. code-block:: python

   from honeyhive.evaluation import AsyncEvaluator
   import aiohttp
   import asyncio
   
   class AsyncFactCheckEvaluator(AsyncEvaluator):
       def __init__(self, api_endpoint: str):
           self.api_endpoint = api_endpoint
       
       async def evaluate_async(self, input_text: str, output_text: str, context: dict = None) -> dict:
           """Async evaluation using external API."""
           
           async with aiohttp.ClientSession() as session:
               payload = {
                   "text": output_text,
                   "context": context or {}
               }
               
               async with session.post(self.api_endpoint, json=payload) as response:
                   result = await response.json()
                   
                   return {
                       "score": result.get("accuracy_score", 0.0),
                       "feedback": result.get("feedback", "No feedback available"),
                       "metrics": {
                           "fact_checks": result.get("fact_checks", []),
                           "verification_sources": result.get("sources", [])
                       },
                       "passed": result.get("accuracy_score", 0.0) >= 0.8
                   }

**Async Multi-Evaluator:**

.. code-block:: python

   async def async_comprehensive_evaluation():
       """Example of async evaluation pipeline."""
       
       # Setup async evaluators
       async_evaluators = [
           AsyncFactCheckEvaluator("https://api.factcheck.com/verify"),
           AsyncQualityEvaluator("https://api.quality.com/assess"),
           AsyncSafetyEvaluator("https://api.safety.com/check")
       ]
       
       # Run evaluations in parallel
       input_text = "What are the benefits of renewable energy?"
       output_text = "Renewable energy sources provide clean electricity..."
       
       tasks = []
       for evaluator in async_evaluators:
           task = evaluator.evaluate_async(input_text, output_text)
           tasks.append(task)
       
       # Wait for all evaluations to complete
       results = await asyncio.gather(*tasks)
       
       # Aggregate results
       scores = [r['score'] for r in results]
       overall_score = sum(scores) / len(scores)
       
       return {
           "overall_score": overall_score,
           "individual_results": results,
           "evaluation_time": time.time() - start_time
       }

Integration Patterns
--------------------

With Decorators
~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import trace, evaluate
   from honeyhive.evaluation import QualityScoreEvaluator
   
   quality_eval = QualityScoreEvaluator(criteria=["accuracy", "helpfulness"])
   
   @trace(tracer=tracer, event_type="content_generation")
   @evaluate(evaluator=quality_eval)
   def generate_customer_response(query: str, context: dict) -> str:
       """Generate customer response with automatic evaluation."""
       
       response = create_response(query, context)
       return response
   
   # Usage - automatically traced and evaluated
   response = generate_customer_response(
       "How do I reset my password?",
       {"customer_tier": "premium", "previous_attempts": 2}
   )

With Manual Evaluation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation import MultiEvaluator, QualityScoreEvaluator, ToxicityEvaluator
   
   def manual_evaluation_pipeline(input_text: str, output_text: str) -> dict:
       """Manual evaluation pipeline with detailed reporting."""
       
       # Setup evaluators
       evaluators = {
           "quality": QualityScoreEvaluator(),
           "safety": ToxicityEvaluator(),
           "length": LengthEvaluator(min_length=20, max_length=500)
       }
       
       # Run individual evaluations
       results = {}
       for name, evaluator in evaluators.items():
           try:
               result = evaluator.evaluate(input_text, output_text)
               results[name] = result
           except Exception as e:
               results[name] = {
                   "score": 0.0,
                   "feedback": f"Evaluation failed: {str(e)}",
                   "passed": False,
                   "error": True
               }
       
       # Calculate overall metrics
       valid_scores = [r['score'] for r in results.values() if not r.get('error', False)]
       overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
       
       all_passed = all(r['passed'] for r in results.values() if not r.get('error', False))
       
       return {
           "overall_score": overall_score,
           "all_passed": all_passed,
           "individual_results": results,
           "evaluation_summary": generate_evaluation_summary(results)
       }
   
   def generate_evaluation_summary(results: dict) -> str:
       """Generate human-readable evaluation summary."""
       summary_parts = []
       
       for eval_name, result in results.items():
           if result.get('error'):
               summary_parts.append(f"{eval_name}: Failed to evaluate")
           elif result['passed']:
               summary_parts.append(f"{eval_name}: ✓ Passed ({result['score']:.2f})")
           else:
               summary_parts.append(f"{eval_name}: ✗ Failed ({result['score']:.2f})")
       
       return "; ".join(summary_parts)

Batch Evaluation
~~~~~~~~~~~~~~~~

.. code-block:: python

   def batch_evaluate(evaluator: BaseEvaluator, test_cases: List[dict]) -> dict:
       """Evaluate multiple test cases efficiently."""
       
       results = []
       start_time = time.time()
       
       for i, test_case in enumerate(test_cases):
           try:
               result = evaluator.evaluate(
                   input_text=test_case['input'],
                   output_text=test_case['output'],
                   context=test_case.get('context')
               )
               
               result['test_case_id'] = test_case.get('id', i)
               result['success'] = True
               results.append(result)
               
           except Exception as e:
               results.append({
                   'test_case_id': test_case.get('id', i),
                   'success': False,
                   'error': str(e),
                   'score': 0.0,
                   'passed': False
               })
       
       # Calculate batch statistics
       successful_results = [r for r in results if r['success']]
       scores = [r['score'] for r in successful_results]
       
       batch_stats = {
           "total_cases": len(test_cases),
           "successful_evaluations": len(successful_results),
           "failed_evaluations": len(test_cases) - len(successful_results),
           "average_score": sum(scores) / len(scores) if scores else 0.0,
           "pass_rate": len([r for r in successful_results if r['passed']]) / len(test_cases),
           "evaluation_time": time.time() - start_time
       }
       
       return {
           "batch_statistics": batch_stats,
           "individual_results": results,
           "score_distribution": calculate_score_distribution(scores)
       }
   
   def calculate_score_distribution(scores: List[float]) -> dict:
       """Calculate score distribution statistics."""
       if not scores:
           return {}
       
       scores.sort()
       n = len(scores)
       
       return {
           "min": min(scores),
           "max": max(scores),
           "median": scores[n // 2],
           "q1": scores[n // 4],
           "q3": scores[3 * n // 4],
           "std_dev": (sum((s - sum(scores)/n) ** 2 for s in scores) / n) ** 0.5
       }

Configuration and Customization
-------------------------------

Evaluator Configuration
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Global evaluator configuration
   from honeyhive.evaluation import configure_evaluators
   
   configure_evaluators({
       "default_timeout": 30.0,
       "retry_attempts": 3,
       "cache_evaluations": True,
       "cache_ttl": 3600,  # 1 hour
       "log_evaluations": True,
       "log_level": "INFO"
   })

Custom Scoring Functions
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def create_domain_specific_evaluator(domain: str):
       """Create evaluator tailored to specific domain."""
       
       if domain == "medical":
           return QualityScoreEvaluator(
               criteria=["accuracy", "safety", "clinical_relevance"],
               weights={"accuracy": 0.4, "safety": 0.4, "clinical_relevance": 0.2},
               min_score=0.9  # High threshold for medical content
           )
       elif domain == "education":
           return QualityScoreEvaluator(
               criteria=["clarity", "age_appropriateness", "educational_value"],
               weights={"clarity": 0.3, "age_appropriateness": 0.3, "educational_value": 0.4}
           )
       elif domain == "creative":
           return QualityScoreEvaluator(
               criteria=["creativity", "originality", "engagement"],
               weights={"creativity": 0.4, "originality": 0.3, "engagement": 0.3},
               min_score=0.6  # Lower threshold for creative content
           )
       else:
           return QualityScoreEvaluator()  # Default configuration

Performance Optimization
------------------------

Caching Evaluations
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation import CachedEvaluator
   import hashlib
   
   class CachedQualityEvaluator(CachedEvaluator):
       def __init__(self, cache_size: int = 1000):
           super().__init__()
           self.evaluator = QualityScoreEvaluator()
           self.cache_size = cache_size
           self._cache = {}
       
       def _generate_cache_key(self, input_text: str, output_text: str, context: dict) -> str:
           """Generate cache key for evaluation."""
           content = f"{input_text}|{output_text}|{str(sorted(context.items()) if context else '')}"
           return hashlib.md5(content.encode()).hexdigest()
       
       def evaluate(self, input_text: str, output_text: str, context: dict = None) -> dict:
           """Cached evaluation."""
           cache_key = self._generate_cache_key(input_text, output_text, context)
           
           if cache_key in self._cache:
               return self._cache[cache_key]
           
           # Perform evaluation
           result = self.evaluator.evaluate(input_text, output_text, context)
           
           # Cache result
           if len(self._cache) >= self.cache_size:
               # Remove oldest entry
               oldest_key = next(iter(self._cache))
               del self._cache[oldest_key]
           
           self._cache[cache_key] = result
           return result

Parallel Evaluation
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import concurrent.futures
   from typing import List, Tuple
   
   def parallel_evaluation(
       evaluators: List[BaseEvaluator], 
       test_cases: List[Tuple[str, str, dict]]
   ) -> List[dict]:
       """Run multiple evaluators in parallel across test cases."""
       
       def evaluate_case(args):
           evaluator, input_text, output_text, context = args
           try:
               result = evaluator.evaluate(input_text, output_text, context)
               result['evaluator_type'] = type(evaluator).__name__
               return result
           except Exception as e:
               return {
                   'evaluator_type': type(evaluator).__name__,
                   'error': str(e),
                   'score': 0.0,
                   'passed': False
               }
       
       # Prepare all combinations
       tasks = []
       for evaluator in evaluators:
           for input_text, output_text, context in test_cases:
               tasks.append((evaluator, input_text, output_text, context))
       
       # Execute in parallel
       with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
           results = list(executor.map(evaluate_case, tasks))
       
       # Group results by test case
       grouped_results = []
       evaluator_count = len(evaluators)
       
       for i in range(0, len(results), evaluator_count):
           case_results = results[i:i + evaluator_count]
           grouped_results.append(case_results)
       
       return grouped_results

Error Handling and Resilience
-----------------------------

Robust Evaluation Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation import EvaluationError
   
   class RobustEvaluationPipeline:
       def __init__(self, evaluators: List[BaseEvaluator], fallback_evaluator: BaseEvaluator = None):
           self.evaluators = evaluators
           self.fallback_evaluator = fallback_evaluator or QualityScoreEvaluator()
       
       def evaluate_with_fallback(self, input_text: str, output_text: str, context: dict = None) -> dict:
           """Evaluate with graceful degradation."""
           
           results = []
           errors = []
           
           for evaluator in self.evaluators:
               try:
                   result = evaluator.evaluate(input_text, output_text, context)
                   result['evaluator_name'] = type(evaluator).__name__
                   result['success'] = True
                   results.append(result)
                   
               except Exception as e:
                   error_info = {
                       'evaluator_name': type(evaluator).__name__,
                       'error': str(e),
                       'error_type': type(e).__name__
                   }
                   errors.append(error_info)
           
           # If no evaluators succeeded, use fallback
           if not results:
               try:
                   fallback_result = self.fallback_evaluator.evaluate(input_text, output_text, context)
                   fallback_result['evaluator_name'] = f"fallback_{type(self.fallback_evaluator).__name__}"
                   fallback_result['is_fallback'] = True
                   results.append(fallback_result)
               except Exception as e:
                   # Even fallback failed
                   return {
                       'score': 0.0,
                       'feedback': 'All evaluations failed',
                       'passed': False,
                       'errors': errors,
                       'total_failure': True
                   }
           
           # Aggregate successful results
           scores = [r['score'] for r in results]
           overall_score = sum(scores) / len(scores)
           
           return {
               'score': overall_score,
               'feedback': self._generate_combined_feedback(results),
               'passed': overall_score >= 0.7,
               'successful_evaluations': len(results),
               'failed_evaluations': len(errors),
               'individual_results': results,
               'errors': errors
           }
       
       def _generate_combined_feedback(self, results: List[dict]) -> str:
           """Generate combined feedback from multiple evaluators."""
           feedback_parts = []
           
           for result in results:
               evaluator_name = result['evaluator_name']
               score = result['score']
               feedback = result.get('feedback', 'No feedback')
               
               feedback_parts.append(f"{evaluator_name} ({score:.2f}): {feedback}")
           
           return "; ".join(feedback_parts)

See Also
--------

- :doc:`../api/decorators` - ``@evaluate`` decorator reference
- :doc:`../api/tracer` - HoneyHiveTracer integration
- :doc:`../../how-to/evaluation/index` - Evaluation tutorial
- :doc:`../../how-to/evaluation/index` - Evaluation guides and development
- :doc:`../../explanation/concepts/llm-observability` - LLM observability concepts
