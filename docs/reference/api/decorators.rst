Decorators API Reference
========================

.. note::
   **Complete API documentation for HoneyHive decorators**
   
   Decorators provide the simplest way to add tracing and evaluation to your functions with minimal code changes.

.. currentmodule:: honeyhive

The HoneyHive SDK provides powerful decorators that automatically instrument your functions with tracing and evaluation capabilities. These decorators work seamlessly with both synchronous and asynchronous functions, providing comprehensive observability with minimal code changes.

**Key Features:**

- Zero-code-change instrumentation
- Automatic context propagation
- Comprehensive error handling
- Support for sync and async functions
- Flexible configuration options
- Built-in performance optimization
- Integration with evaluation framework

@trace Decorator
----------------

.. autofunction:: trace
   :no-index:

The ``@trace`` decorator automatically creates spans for function execution with comprehensive context capture.

**Function Signature:**

.. py:decorator:: trace(tracer: HoneyHiveTracer, event_type: Optional[str] = None, include_inputs: bool = True, include_outputs: bool = True, **span_attributes) -> Callable

   Decorator for automatic function tracing with HoneyHive.
   
   **Parameters:**
   
   :param tracer: HoneyHiveTracer instance to use for creating spans
   :type tracer: HoneyHiveTracer
   
   :param event_type: Event type for categorization. Must be one of: ``"model"``, ``"tool"``, or ``"chain"``
   :type event_type: Optional[str]
   
   :param include_inputs: Whether to capture function arguments. Default: True
   :type include_inputs: bool
   
   :param include_outputs: Whether to capture function return values. Default: True
   :type include_outputs: bool
   
   :param span_attributes: Additional attributes to set on the span
   :type span_attributes: Any
   
   **Returns:**
   
   :rtype: Callable
   :returns: Decorated function with automatic tracing enabled

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   
   # Initialize tracer
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key"
       
   )
   
   # Basic function tracing
   @trace(tracer=tracer)
   def simple_function(x: int, y: int) -> int:
       """Simple function with automatic tracing."""
       return x + y
   
   # Usage - automatically traced
   result = simple_function(5, 3)  # Creates span "simple_function"

Advanced Configuration
~~~~~~~~~~~~~~~~~~~~~~

**Custom Span Names and Event Types:**

.. code-block:: python

   @trace(
       tracer=tracer,
       event_type="user_authentication"
   )
   def authenticate_user(username: str, password: str) -> bool:
       """Authenticate user with custom event type."""
       # Authentication logic here
       return validate_credentials(username, password)

**Selective Input/Output Capture:**

.. code-block:: python

   @trace(
       tracer=tracer,
       include_inputs=False,     # Don't capture sensitive arguments
       include_outputs=True,     # Do capture return values
       event_type="security_operation"
   )
   def process_payment(credit_card: str, amount: float) -> dict:
       """Secure function tracing without exposing sensitive data."""
       
       # Manual attribute setting for non-sensitive data
       enrich_span({
           "payment.amount": amount,
           "payment.currency": "USD",
           "operation.type": "payment_processing"
       })
       
       return process_credit_card_payment(credit_card, amount)

**With Initial Span Attributes:**

.. code-block:: python

   from honeyhive.models import EventType
   
   @trace(
       tracer=tracer,
       event_type=EventType.tool,
       operation_category="batch",
       priority="high",
       team="data-engineering"
   )
   def batch_process_data(data_batch: list) -> list:
       """Function with predefined span attributes."""
       
       # Additional dynamic attributes
       enrich_span({
           "batch.size": len(data_batch),
           "batch.timestamp": time.time()
       })
       
       return [process_item(item) for item in data_batch]

Async Function Support
~~~~~~~~~~~~~~~~~~~~~~

The ``@trace`` decorator works seamlessly with async functions:

.. code-block:: python

   import asyncio
   import aiohttp
   
   @trace(tracer=tracer, event_type="async_api_call")
   async def fetch_user_data(user_id: str) -> dict:
       """Async function with automatic tracing."""
       async with aiohttp.ClientSession() as session:
           url = f"https://api.example.com/users/{user_id}"
           async with session.get(url) as response:
               enrich_span({
                   "http.url": url,
                   "http.status_code": response.status,
                   "user.id": user_id
               })
               return await response.json()
   
   # Usage
   result = await fetch_user_data("user_123")

Class Method Support
~~~~~~~~~~~~~~~~~~~~

Use with instance methods, class methods, and static methods:

.. code-block:: python

   class UserService:
       def __init__(self, tracer: HoneyHiveTracer):
           self.tracer = tracer
       
       @trace(tracer=lambda self: self.tracer, event_type="user_lookup")
       def get_user(self, user_id: str) -> dict:
           """Instance method with tracing."""
           user = fetch_user_from_db(user_id)
           
           enrich_span({
               "user.id": user_id,
               "user.found": user is not None,
               "database.table": "users"
           })
           
           return user
       
       @classmethod
       @trace(tracer=tracer, event_type="user_validation")
       def validate_email(cls, email: str) -> bool:
           """Class method with tracing."""
           is_valid = "@" in email and "." in email
           
           enrich_span({
               "email.valid": is_valid,
               "validation.type": "email_format"
           })
           
           return is_valid
       
       @staticmethod
       @trace(tracer=tracer, event_type="security_utility")
       def hash_password(password: str) -> str:
           """Static method with tracing."""
           import hashlib
           
           hashed = hashlib.sha256(password.encode()).hexdigest()
           
           enrich_span({
               "security.operation": "password_hash",
               "input.length": len(password),
               "output.length": len(hashed)
           })
           
           return hashed

Error Handling and Exception Capture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The decorator automatically captures exceptions with detailed context:

.. code-block:: python

   @trace(tracer=tracer, event_type="risky_operation")
   def operation_that_might_fail(data: list) -> list:
       """Function demonstrating automatic exception capture."""
       
       enrich_span({
           "input.data_size": len(data),
           "operation.start_time": time.time()
       })
       
       if not data:
           raise ValueError("Data cannot be empty")
       
       if len(data) > 1000:
           raise RuntimeError("Data too large to process")
       
       # Normal processing
       result = [process_item(item) for item in data]
       
       enrich_span({
           "output.result_size": len(result),
           "operation.success": True
       })
       
       return result
   
   # The decorator automatically captures:
   # - Exception type and message
   # - Full stack trace
   # - Span status marked as ERROR
   # - Execution time until failure
   
   try:
       result = operation_that_might_fail([])
   except ValueError as e:
       # Exception details are already captured in trace
       print(f"Operation failed: {e}")

Nested Function Tracing
~~~~~~~~~~~~~~~~~~~~~~~

Decorators automatically handle nested function calls with proper parent-child relationships:

.. code-block:: python

   @trace(tracer=tracer, event_type="parent_operation")
   def parent_function(data: dict) -> dict:
       """Parent function that calls other traced functions."""
       
       enrich_span({
           "operation.level": "parent",
           "data.keys": list(data.keys())
       })
       
       # Child function calls are automatically linked
       validated_data = validate_data(data)
       processed_data = process_data(validated_data)
       
       return processed_data
   
   @trace(tracer=tracer, event_type=EventType.tool)
   def validate_data(data: dict) -> dict:
       """Child function - automatically becomes a child span."""
       
       enrich_span({
           "operation.level": "child",
           "validation.rules": ["required_fields", "data_types"],
           "validation.items_count": len(data)
       })
       
       # Validation logic
       if not data:
           raise ValueError("Data is required")
       
       return data
   
   @trace(tracer=tracer, event_type=EventType.tool)
   def process_data(data: dict) -> dict:
       """Another child function - also becomes a child span."""
       
       enrich_span({
           "operation.level": "child",
           "processing.algorithm": "advanced",
           "processing.items": len(data)
       })
       
       # Processing logic
       return {k: v.upper() if isinstance(v, str) else v for k, v in data.items()}

@atrace Decorator
-----------------

.. autofunction:: atrace

Alias for ``@trace`` specifically for async functions (both work identically).

**Usage:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, atrace
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key"
       
   )
   
   @atrace(tracer=tracer, event_type="async_processing")
   async def async_process_data(data: list) -> dict:
       """Async data processing with tracing."""
       await asyncio.sleep(0.1)  # Simulate async work
       
       enrich_span({
           "async.processing_time": 0.1,
           "data.items": len(data)
       })
       
       return {"processed": len(data), "status": "complete"}

@evaluate Decorator
-------------------

.. autofunction:: evaluate

The ``@evaluate`` decorator automatically evaluates function outputs using specified evaluators.

**Function Signature:**

.. py:decorator:: evaluate(evaluator: BaseEvaluator, include_inputs: bool = True, include_outputs: bool = True, evaluation_context: Optional[dict] = None) -> Callable
   :no-index:

   Decorator for automatic function output evaluation.
   
   **Parameters:**
   
   :param evaluator: Evaluator instance to use for assessment
   :type evaluator: BaseEvaluator
   
   :param include_inputs: Whether to include inputs in evaluation context. Default: True
   :type include_inputs: bool
   
   :param include_outputs: Whether to include outputs in evaluation context. Default: True
   :type include_outputs: bool
   
   :param evaluation_context: Additional context for evaluation
   :type evaluation_context: Optional[dict]
   
   **Returns:**
   
   :rtype: Callable
   :returns: Decorated function with automatic evaluation

Basic Evaluation
~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, evaluate
   from honeyhive.evaluation import FactualAccuracyEvaluator
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key"
       
   )
   
   fact_evaluator = FactualAccuracyEvaluator()
   
   @trace(tracer=tracer, event_type="factual_qa")
   @evaluate(evaluator=fact_evaluator)
   def answer_factual_question(question: str) -> str:
       """Answer a factual question with automatic evaluation."""
       
       # Simulate LLM call or knowledge lookup
       if "capital" in question.lower() and "france" in question.lower():
           return "The capital of France is Paris."
       elif "largest" in question.lower() and "ocean" in question.lower():
           return "The Pacific Ocean is the largest ocean on Earth."
       else:
           return "I don't have enough information to answer that question."
   
   # Function is both traced and evaluated automatically
   answer = answer_factual_question("What is the capital of France?")
   # Result: Trace created + Factual accuracy evaluated

Multiple Evaluators
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation import (
       MultiEvaluator,
       QualityScoreEvaluator,
       LengthEvaluator,
       FactualAccuracyEvaluator
   )
   
   # Combine multiple evaluators for comprehensive assessment
   multi_evaluator = MultiEvaluator([
       FactualAccuracyEvaluator(),
       QualityScoreEvaluator(criteria=["clarity", "relevance", "completeness"]),
       LengthEvaluator(min_length=20, max_length=200)
   ])
   
   @trace(tracer=tracer, event_type="comprehensive_response")
   @evaluate(evaluator=multi_evaluator)
   def generate_comprehensive_response(prompt: str) -> str:
       """Generate response evaluated by multiple criteria."""
       
       # Simulate response generation
       if "explain" in prompt.lower():
           return f"Here's a detailed explanation of {prompt}: [comprehensive answer]"
       else:
           return f"Response to: {prompt}"
   
   # All evaluators run automatically
   result = generate_comprehensive_response("Explain quantum computing")

Evaluation with Context
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @trace(tracer=tracer, event_type="contextual_response")
   @evaluate(
       evaluator=QualityScoreEvaluator(),
       evaluation_context={
           "domain": "customer_support",
           "audience": "technical_users",
           "expected_tone": "professional_helpful"
       }
   )
   def handle_technical_support(query: str, user_tier: str) -> str:
       """Technical support with domain-specific evaluation."""
       
       # Generate context-aware response
       if user_tier == "enterprise":
           response = f"Enterprise support for: {query}. Here's the detailed technical solution..."
       else:
           response = f"Standard support for: {query}. Here's the solution..."
       
       return response

Custom Evaluators
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation import BaseEvaluator
   
   class CustomLengthQualityEvaluator(BaseEvaluator):
       def __init__(self, target_length: int = 100):
           self.target_length = target_length
       
       def evaluate(self, input_text: str, output_text: str, context: dict = None) -> dict:
           """Custom evaluation based on response length and quality."""
           length = len(output_text)
           
           # Calculate length score
           length_score = 1.0 - abs(length - self.target_length) / self.target_length
           length_score = max(0.0, min(1.0, length_score))
           
           # Simple quality heuristics
           quality_score = 0.5
           if "detailed" in output_text.lower():
               quality_score += 0.2
           if "example" in output_text.lower():
               quality_score += 0.2
           if len(output_text.split('.')) > 2:  # Multiple sentences
               quality_score += 0.1
           
           overall_score = (length_score + quality_score) / 2
           
           return {
               "score": overall_score,
               "feedback": f"Length: {length} chars (target: {self.target_length}), Quality indicators: {'good' if quality_score > 0.7 else 'fair'}",
               "metrics": {
                   "length_score": length_score,
                   "quality_score": quality_score,
                   "actual_length": length,
                   "target_length": self.target_length
               }
           }
   
   custom_evaluator = CustomLengthQualityEvaluator(target_length=150)
   
   @trace(tracer=tracer, event_type="custom_evaluation")
   @evaluate(evaluator=custom_evaluator)
   def generate_targeted_content(topic: str) -> str:
       """Generate content with custom evaluation criteria."""
       
       # Content generation with target length in mind
       base_content = f"Here's detailed information about {topic}."
       
       if len(base_content) < 150:
           base_content += " This includes comprehensive examples and practical applications that demonstrate the key concepts."
       
       return base_content

Async Evaluation
~~~~~~~~~~~~~~~~

.. code-block:: python

   @atrace(tracer=tracer, event_type="async_evaluation")
   @evaluate(evaluator=FactualAccuracyEvaluator())
   async def async_research_question(question: str) -> str:
       """Async function with automatic evaluation."""
       
       # Simulate async research
       await asyncio.sleep(0.2)
       
       # Generate research-based response
       response = f"Based on research, here's the answer to '{question}': [researched answer]"
       
       return response
   
   # Usage
   result = await async_research_question("What are the benefits of renewable energy?")

Combined Decorators
-------------------

Use both decorators together for comprehensive observability and evaluation:

**Standard Combination:**

.. code-block:: python

   @trace(tracer=tracer, event_type="llm_generation")
   @evaluate(evaluator=QualityScoreEvaluator(criteria=["accuracy", "relevance"]))
   def llm_content_generation(prompt: str) -> str:
       """LLM function with both tracing and evaluation."""
       
       # Add tracing context
       enrich_span({
           "prompt.length": len(prompt),
           "model.provider": "openai",
           "model.name": "gpt-4"
       })
       
       # Simulate LLM call
       response = call_llm_api(prompt)
       
       enrich_span({
           "response.length": len(response),
           "operation.success": True
       })
       
       return response

**Advanced Multi-Evaluator Combination:**

.. code-block:: python

   @trace(
       tracer=tracer,
       event_type="customer_service_ai",
       service="support_bot",
       version="2.1"
   )
   @evaluate(
       evaluator=MultiEvaluator([
           FactualAccuracyEvaluator(),
           QualityScoreEvaluator(criteria=["helpfulness", "clarity", "empathy"]),
           LengthEvaluator(min_length=50, max_length=300),
           CustomLengthQualityEvaluator(target_length=150)
       ])
   )
   def handle_customer_inquiry(inquiry: str, customer_tier: str) -> str:
       """Customer service with comprehensive observability."""
       
       # Add customer context
       enrich_span({
           "customer.tier": customer_tier,
           "inquiry.category": classify_inquiry(inquiry),
           "inquiry.complexity": get_complexity_score(inquiry)
       })
       
       # Generate response based on tier
       if customer_tier == "premium":
           response = generate_premium_response(inquiry)
       else:
           response = generate_standard_response(inquiry)
       
       enrich_span({
           "response.type": "generated",
           "response.personalized": customer_tier == "premium"
       })
       
       return response

**Async Combined Usage:**

.. code-block:: python

   @atrace(tracer=tracer, event_type="async_content_analysis")
   @evaluate(
       evaluator=MultiEvaluator([
           QualityScoreEvaluator(),
           FactualAccuracyEvaluator()
       ])
   )
   async def analyze_and_summarize(document: str) -> str:
       """Async document analysis with tracing and evaluation."""
       
       enrich_span({
           "document.length": len(document),
           "analysis.type": "comprehensive"
       })
       
       # Async analysis
       analysis = await perform_async_analysis(document)
       summary = await generate_async_summary(analysis)
       
       enrich_span({
           "summary.length": len(summary),
           "analysis.duration": time.time() - start_time
       })
       
       return summary

Helper Functions
----------------

enrich_span()
~~~~~~~~~~~~~

.. autofunction:: enrich_span

Add attributes to the currently active span without needing direct span reference. Supports multiple invocation patterns for flexibility: simple dictionary, keyword arguments, and reserved namespaces for structured data organization.

**Function Signature:**

.. py:function:: enrich_span(attributes=None, *, metadata=None, metrics=None, feedback=None, inputs=None, outputs=None, config=None, error=None, event_id=None, tracer=None, **kwargs)
   :no-index:

   Add attributes to the currently active span with namespace support.
   
   **Parameters:**
   
   :param attributes: Simple dictionary that routes to metadata namespace. Use for quick metadata enrichment.
   :type attributes: Optional[Dict[str, Any]]
   
   :param metadata: Business context data (user IDs, features, session info). Routes to ``honeyhive_metadata.*`` namespace.
   :type metadata: Optional[Dict[str, Any]]
   
   :param metrics: Numeric measurements (latencies, scores, counts). Routes to ``honeyhive_metrics.*`` namespace.
   :type metrics: Optional[Dict[str, Any]]
   
   :param feedback: User or system feedback (ratings, thumbs up/down). Routes to ``honeyhive_feedback.*`` namespace.
   :type feedback: Optional[Dict[str, Any]]
   
   :param inputs: Input data to the operation. Routes to ``honeyhive_inputs.*`` namespace.
   :type inputs: Optional[Dict[str, Any]]
   
   :param outputs: Output data from the operation. Routes to ``honeyhive_outputs.*`` namespace.
   :type outputs: Optional[Dict[str, Any]]
   
   :param config: Configuration parameters (model settings, hyperparameters). Routes to ``honeyhive_config.*`` namespace.
   :type config: Optional[Dict[str, Any]]
   
   :param error: Error message or exception string. Stored as direct ``honeyhive_error`` attribute (not namespaced).
   :type error: Optional[str]
   
   :param event_id: Unique event identifier. Stored as direct ``honeyhive_event_id`` attribute (not namespaced).
   :type event_id: Optional[str]
   
   :param tracer: Optional tracer instance for advanced usage. Usually auto-detected from context.
   :type tracer: Optional[Any]
   
   :param kwargs: Arbitrary keyword arguments that route to metadata namespace. Use for concise inline enrichment.
   :type kwargs: Any
   
   **Returns:**
   
   :rtype: UnifiedEnrichSpan
   :returns: Enrichment object that can be used as context manager or directly

**Multiple Invocation Patterns:**

The function supports four different invocation patterns that can be mixed:

**Pattern 1: Simple Dictionary (Quick Metadata)**

.. code-block:: python

   # Pass a single dict - routes to metadata namespace
   enrich_span({
       "user_id": "user_123",
       "feature": "chat",
       "session": "abc"
   })
   
   # Backend storage:
   # honeyhive_metadata.user_id = "user_123"
   # honeyhive_metadata.feature = "chat"
   # honeyhive_metadata.session = "abc"

**Pattern 2: Keyword Arguments (Concise Enrichment)**

.. code-block:: python

   # Pass keyword arguments - also route to metadata
   enrich_span(
       user_id="user_123",
       feature="chat",
       score=0.95
   )
   
   # Backend storage: same as simple dict pattern

**Pattern 3: Reserved Namespaces (Structured Organization)**

.. code-block:: python

   # Use explicit namespaces for organized data
   enrich_span(
       metadata={"user_id": "user_123", "session": "abc"},
       metrics={"latency_ms": 150, "score": 0.95},
       feedback={"rating": 5, "helpful": True},
       inputs={"query": "What is AI?"},
       outputs={"answer": "AI is..."},
       config={"model": "gpt-4", "temperature": 0.7},
       error="Optional error message",
       event_id="evt_unique_id"
   )
   
   # Each namespace creates nested attributes in backend:
   # honeyhive_metadata.* for metadata
   # honeyhive_metrics.* for metrics
   # honeyhive_feedback.* for feedback
   # honeyhive_inputs.* for inputs
   # honeyhive_outputs.* for outputs
   # honeyhive_config.* for config
   # honeyhive_error (direct attribute, no nesting)
   # honeyhive_event_id (direct attribute, no nesting)

**Pattern 4: Mixed Usage (Combine Patterns)**

.. code-block:: python

   # Combine multiple patterns - later values override
   enrich_span(
       metadata={"user_id": "user_123"},
       metrics={"score": 0.95},
       feature="chat",      # Adds to metadata
       priority="high"      # Also adds to metadata
   )
   
   # Backend storage:
   # honeyhive_metadata.user_id = "user_123"
   # honeyhive_metadata.feature = "chat"
   # honeyhive_metadata.priority = "high"
   # honeyhive_metrics.score = 0.95

**Namespace Routing Rules:**

1. **Reserved Parameters** (metadata, metrics, etc.) → Applied first
2. **attributes Dict** → Applied second, routes to metadata namespace
3. **kwargs** → Applied last (wins conflicts), routes to metadata namespace

**Context Manager Pattern:**

.. code-block:: python

   # Use as context manager for scoped enrichment
   with enrich_span(metadata={"operation": "batch_processing"}):
       # Enrichment is active within this block
       process_batch_items()
   
   # Use with boolean check
   if enrich_span(user_tier="premium"):
       # Process for premium users
       pass

**Usage in Decorated Functions:**

.. code-block:: python

   @trace(tracer=tracer, event_type="user_processing")
   def process_user_request(user_id: str, request_data: dict):
       """Process user request with additional context."""
       
       # Add business context to the span
       enrich_span({
           "user.id": user_id,
           "user.tier": get_user_tier(user_id),
           "request.type": request_data.get("type", "unknown"),
           "request.size": len(str(request_data)),
           "request.timestamp": time.time()
       })
       
       # Processing logic
       result = process_request(request_data)
       
       # Add result context
       enrich_span({
           "result.status": "success",
           "result.size": len(str(result)),
           "processing.items_processed": result.get("items_processed", 0)
       })
       
       return result

**Conditional Enrichment:**

.. code-block:: python

   @trace(tracer=tracer, event_type="conditional_processing")
   def conditional_processing(user_id: str, options: dict):
       """Example of conditional span enrichment."""
       
       # Always add basic info
       enrich_span({
           "user.id": user_id,
           "options.count": len(options)
       })
       
       # Conditionally add detailed info
       user_tier = get_user_tier(user_id)
       if user_tier == "premium":
           enrich_span({
               "user.tier": user_tier,
               "user.premium_features": get_premium_features(user_id),
               "processing.enhanced": True
           })
       
       # Add debug info in development
       if os.getenv("ENVIRONMENT") == "development":
           enrich_span({
               "debug.options": str(options),
               "debug.stack_depth": len(inspect.stack())
           })

**In Nested Helper Functions:**

.. code-block:: python

   @trace(tracer=tracer, event_type="main_operation")
   def main_operation(data: list):
       """Main operation that calls helper functions."""
       
       enrich_span({
           "main.operation_type": "batch_processing",
           "main.input_size": len(data)
       })
       
       results = []
       for item in data:
           result = process_item(item)  # Helper function adds its own context
           results.append(result)
       
       enrich_span({
           "main.output_size": len(results),
           "main.success_rate": len([r for r in results if r.get("success", False)]) / len(results)
       })
       
       return results
   
   def process_item(item: dict):
       """Helper function that enriches the active span."""
       # This adds to the span created by main_operation
       enrich_span({
           "item.id": item.get("id"),
           "item.type": item.get("type", "unknown"),
           "item.processing_method": "standard"
       })
       
       # Process the item
       return {"success": True, "processed_item": item}

enrich_session()
~~~~~~~~~~~~~~~~

.. autofunction:: enrich_session

Add metadata, metrics, and context to entire sessions (collections of related spans) with backend persistence.

**Function Signature:**

.. py:function:: enrich_session(session_id=None, *, metadata=None, inputs=None, outputs=None, config=None, feedback=None, metrics=None, user_properties=None, **kwargs)
   :no-index:

   Add metadata and metrics to a session with backend persistence.
   
   **Parameters:**
   
   :param session_id: Explicit session ID to enrich. If not provided, uses the active session from context.
   :type session_id: Optional[str]
   
   :param metadata: Business context data (user IDs, features, session info).
   :type metadata: Optional[Dict[str, Any]]
   
   :param inputs: Input data for the session (e.g., initial query, configuration).
   :type inputs: Optional[Dict[str, Any]]
   
   :param outputs: Output data from the session (e.g., final response, results).
   :type outputs: Optional[Dict[str, Any]]
   
   :param config: Configuration parameters for the session (model settings, hyperparameters).
   :type config: Optional[Dict[str, Any]]
   
   :param feedback: User or system feedback for the session (ratings, quality scores).
   :type feedback: Optional[Dict[str, Any]]
   
   :param metrics: Numeric measurements for the session (latency, cost, token counts).
   :type metrics: Optional[Dict[str, Any]]
   
   :param user_properties: User-specific properties (user_id, plan, etc.). Stored as a separate field in the backend, not merged into metadata.
   :type user_properties: Optional[Dict[str, Any]]
   
   :param kwargs: Additional keyword arguments (passed through for extensibility).
   :type kwargs: Any
   
   **Returns:**
   
   :rtype: None
   :returns: None (updates session in backend via API call)

**Key Differences from enrich_span:**

1. **Backend Persistence**: Makes API calls to persist data (expect ~50-200ms per call)
2. **Session Scope**: Affects the entire session, not just the current span
3. **Complex Data**: Supports nested dictionaries and lists
4. **Explicit Session ID**: Can target any session by ID, not just the active one

**Basic Usage:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, enrich_session
   import openai
   
   # Initialize tracer (creates a session automatically)
   tracer = HoneyHiveTracer.init(
       project="my-app",
       session_name="user-123-chat"
   )
   
   # Enrich the active session
   enrich_session(
       metadata={
           "user_id": "user_123",
           "subscription_tier": "premium",
           "feature": "chat_assistant"
       },
       metrics={
           "total_tokens": 1500,
           "total_cost": 0.045
       }
   )
   
   # All subsequent traces in this session will be associated with this metadata
   client = openai.OpenAI()
   response = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Hello!"}]
   )

**Enrich Specific Session:**

.. code-block:: python

   from honeyhive import enrich_session
   
   # Target a specific session by ID
   enrich_session(
       session_id="sess_abc123xyz",
       metadata={
           "experiment": "variant_b",
           "completed": True
       },
       feedback={
           "user_rating": 5,
           "helpful": True
       }
   )

**Backwards Compatible Signatures:**

.. code-block:: python

   # Legacy: positional session_id (still supported)
   enrich_session(
       "sess_abc123",  # session_id as first positional arg
       metadata={"user_id": "user_456"}
   )
   
  # Legacy: user_properties parameter (still supported)
  enrich_session(
      session_id="sess_abc123",
      user_properties={
          "tier": "premium",
          "region": "us-east"
      }
  )
  # Result: user_properties stored as a separate field in the backend:
  # {"user_properties": {"tier": "premium", "region": "us-east"}}

**Session Lifecycle Management:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, enrich_session
   import openai
   from datetime import datetime
   
   def managed_workflow(user_id: str, task: str):
       """Enrich session across lifecycle stages."""
       
       tracer = HoneyHiveTracer.init(
           project="workflows",
           session_name=f"{task}-{user_id}"
       )
       
       # Start: Add initial metadata
       enrich_session(
           metadata={
               "user_id": user_id,
               "task": task,
               "status": "started",
               "started_at": datetime.now().isoformat()
           }
       )
       
       try:
           # In Progress: Update status
           enrich_session(
               metadata={"status": "in_progress"}
           )
           
           # Do work
           client = openai.OpenAI()
           response = client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[{"role": "user", "content": f"Help with: {task}"}]
           )
           
           # Success: Add final metadata
           enrich_session(
               metadata={
                   "status": "completed",
                   "completed_at": datetime.now().isoformat()
               },
               outputs={
                   "result": response.choices[0].message.content
               }
           )
           
           return response.choices[0].message.content
           
       except Exception as e:
           # Error: Add error metadata
           enrich_session(
               metadata={
                   "status": "failed",
                   "error_type": type(e).__name__
               }
           )
           raise

**Best Practices:**

- Enrich at key lifecycle points (start, progress, completion)
- Use consistent naming conventions for metadata keys
- Add business-relevant context (user IDs, feature flags, experiments)
- Include performance metrics (cost, latency, token counts)
- Don't include sensitive data (passwords, API keys, PII)
- Don't call excessively (it makes API calls)

**See Also:**

- :doc:`/how-to/advanced-tracing/session-enrichment` - Comprehensive session enrichment guide
- :doc:`/how-to/advanced-tracing/span-enrichment` - Span enrichment patterns
- :doc:`/how-to/advanced-tracing/advanced-patterns` - Advanced session and tracing patterns

get_logger()
~~~~~~~~~~~~

.. autofunction:: get_logger

Get a structured logger that integrates with HoneyHive tracing.

**Function Signature:**

.. py:function:: get_logger(name: Optional[str] = None) -> logging.Logger
   :no-index:

   Get a logger with HoneyHive integration.
   
   **Parameters:**
   
   :param name: Logger name. If None, uses calling module name
   :type name: Optional[str]
   
   **Returns:**
   
   :rtype: logging.Logger
   :returns: Configured logger with HoneyHive integration

**Basic Usage:**

.. code-block:: python

   from honeyhive import get_logger
   
   logger = get_logger(__name__)
   
   @trace(tracer=tracer, event_type="complex_operation")
   def complex_operation(data: dict):
       """Complex operation with integrated logging."""
       
       logger.info("Starting complex operation", extra={
           "data_size": len(data),
           "operation_id": generate_operation_id()
       })
       
       try:
           # Processing logic
           enrich_span({
               "processing.phase": "validation"
           })
           
           validate_data(data)
           logger.debug("Data validation completed")
           
           enrich_span({
               "processing.phase": "transformation"
           })
           
           result = transform_data(data)
           logger.info("Operation completed successfully", extra={
               "result_size": len(result),
               "transformation_type": "advanced"
           })
           
           return result
           
       except ValidationError as e:
           logger.warning("Data validation failed", extra={
               "error": str(e),
               "validation_rules_failed": e.failed_rules
           })
           raise
           
       except Exception as e:
           logger.error("Operation failed unexpectedly", extra={
               "error": str(e),
               "error_type": type(e).__name__
           })
           raise

**Logger with Trace Context:**

The logger automatically includes trace context in log entries:

.. code-block:: python

   @trace(tracer=tracer, event_type="logged_operation")
   def logged_operation(user_id: str):
       """Function demonstrating automatic trace context in logs."""
       
       logger = get_logger(__name__)
       
       # This log entry will automatically include:
       # - trace_id: Current trace ID
       # - span_id: Current span ID
       # - Any custom attributes from enrich_span()
       logger.info("Processing user request", extra={
           "user_id": user_id,
           "operation_type": "user_processing"
       })
       
       enrich_span({
           "user.id": user_id,
           "operation.logged": True
       })
       
       # More processing...
       logger.info("User processing completed")

Performance Optimization
------------------------

**Selective Tracing for High-Frequency Functions:**

.. code-block:: python

   import random
   
   def should_trace() -> bool:
       """Sample 10% of calls for high-frequency functions."""
       return random.random() < 0.1
   
   # Conditional decorator application
   def conditional_trace(func):
       if should_trace():
           return trace(tracer=tracer, event_type="high_frequency")(func)
       return func
   
   @conditional_trace
   def high_frequency_function(item: str) -> str:
       """Function called thousands of times - only 10% traced."""
       return item.upper()

**Lazy Tracer Resolution:**

.. code-block:: python

   # For cases where tracer isn't available at decoration time
   def get_current_tracer() -> HoneyHiveTracer:
       """Get tracer from application context."""
       # Example: Flask application context
       from flask import current_app
       return current_app.tracer
   
   @trace(tracer=get_current_tracer, event_type="dynamic_tracer")
   def function_with_dynamic_tracer(data: str) -> str:
       """Function with dynamically resolved tracer."""
       return data.lower()

**Efficient Attribute Management:**

.. code-block:: python

   @trace(tracer=tracer, event_type="efficient_operation")
   def efficient_operation(data: list):
       """Demonstrate efficient attribute management."""
       
       # Batch attribute setting for better performance
       start_time = time.time()
       
       attributes = {
           "operation.start_time": start_time,
           "input.size": len(data),
           "input.type": type(data).__name__,
           "operation.version": "2.1"
       }
       
       # Set all attributes at once
       enrich_span(attributes)
       
       # Process data
       result = process_data_efficiently(data)
       
       # Final attributes
       end_time = time.time()
       enrich_span({
           "operation.end_time": end_time,
           "operation.duration": end_time - start_time,
           "output.size": len(result),
           "operation.efficiency": len(result) / (end_time - start_time)
       })
       
       return result

Error Handling Patterns
-----------------------

**Custom Exception Handling:**

.. code-block:: python

   @trace(tracer=tracer, event_type="error_handling_demo")
   def robust_function_with_custom_error_handling(data: dict):
       """Function with comprehensive error handling patterns."""
       
       enrich_span({
           "function.version": "2.0",
           "input.data_keys": list(data.keys())
       })
       
       try:
           # Main processing logic
           validated_data = validate_input(data)
           enrich_span({"validation.status": "passed"})
           
           processed_data = process_validated_data(validated_data)
           enrich_span({"processing.status": "completed"})
           
           return processed_data
           
       except ValueError as e:
           # Handle validation errors
           enrich_span({
               "error.type": "validation_error",
               "error.message": str(e),
               "error.recoverable": True,
               "error.handling": "return_default"
           })
           
           logger.warning("Validation failed, using default values", extra={
               "error": str(e),
               "fallback_strategy": "default_values"
           })
           
           return get_default_values()
           
       except ProcessingError as e:
           # Handle processing errors
           enrich_span({
               "error.type": "processing_error",
               "error.message": str(e),
               "error.recoverable": False,
               "error.handling": "retry_recommended"
           })
           
           logger.error("Processing failed", extra={
               "error": str(e),
               "retry_recommended": True
           })
           
           raise ProcessingRetryableError(f"Processing failed: {e}") from e
           
       except Exception as e:
           # Handle unexpected errors
           enrich_span({
               "error.type": "unexpected_error",
               "error.class": type(e).__name__,
               "error.message": str(e),
               "error.recoverable": False,
               "error.handling": "propagate"
           })
           
           logger.exception("Unexpected error occurred")
           raise

**Retry Logic Integration:**

.. code-block:: python

   def trace_with_retry(max_retries: int = 3, backoff_factor: float = 1.0):
       """Decorator factory combining tracing with retry logic."""
       
       def decorator(func):
           @trace(tracer=tracer, event_type="retryable_operation")
           def wrapper(*args, **kwargs):
               enrich_span({
                   "retry.max_attempts": max_retries,
                   "retry.backoff_factor": backoff_factor
               })
               
               last_error = None
               
               for attempt in range(max_retries):
                   try:
                       enrich_span({
                           "retry.current_attempt": attempt + 1,
                           "retry.is_retry": attempt > 0
                       })
                       
                       result = func(*args, **kwargs)
                       
                       enrich_span({
                           "retry.success": True,
                           "retry.attempts_used": attempt + 1
                       })
                       
                       return result
                       
                   except Exception as e:
                       last_error = e
                       wait_time = backoff_factor * (2 ** attempt)
                       
                       enrich_span({
                           f"retry.attempt_{attempt + 1}.error": str(e),
                           f"retry.attempt_{attempt + 1}.wait_time": wait_time
                       })
                       
                       if attempt < max_retries - 1:
                           logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s", extra={
                               "error": str(e),
                               "attempt": attempt + 1,
                               "wait_time": wait_time
                           })
                           time.sleep(wait_time)
                       else:
                           enrich_span({
                               "retry.success": False,
                               "retry.exhausted": True,
                               "retry.final_error": str(e)
                           })
               
               # All retries exhausted
               raise last_error
           
           return wrapper
       return decorator
   
   @trace_with_retry(max_retries=3, backoff_factor=0.5)
   def flaky_external_service_call(url: str) -> dict:
       """Function with built-in retry and tracing."""
       import requests
       
       response = requests.get(url, timeout=5)
       response.raise_for_status()
       
       enrich_span({
           "http.url": url,
           "http.status_code": response.status_code,
           "http.response_size": len(response.content)
       })
       
       return response.json()

Framework Integration Examples
------------------------------

**Flask Integration:**

.. code-block:: python

   from flask import Flask, request, g
   from honeyhive import HoneyHiveTracer, trace, get_logger
   
   app = Flask(__name__)
   tracer = HoneyHiveTracer.init()
   logger = get_logger(__name__)
   
   @app.before_request
   def before_request():
       """Set up tracing context for each request."""
       g.request_start_time = time.time()
   
   @app.after_request
   def after_request(response):
       """Add request context to any active spans."""
       if hasattr(g, 'request_start_time'):
           duration = time.time() - g.request_start_time
           try:
               enrich_span({
                   "http.method": request.method,
                   "http.url": request.url,
                   "http.status_code": response.status_code,
                   "http.duration": duration
               })
           except:
               pass  # No active span
       return response
   
   @app.route("/api/users/<user_id>")
   @trace(tracer=tracer, event_type="user_api")
   def get_user_api(user_id: str):
       """API endpoint with automatic tracing."""
       
       logger.info("User API request", extra={
           "user_id": user_id,
           "endpoint": "/api/users"
       })
       
       enrich_span({
           "user.id": user_id,
           "api.endpoint": "/api/users",
           "api.version": "v1"
       })
       
       user_data = fetch_user_data(user_id)
       
       if user_data:
           enrich_span({
               "user.found": True,
               "user.tier": user_data.get("tier", "standard")
           })
           return jsonify(user_data)
       else:
           enrich_span({"user.found": False})
           return jsonify({"error": "User not found"}), 404

**FastAPI Integration:**

.. code-block:: python

   from fastapi import FastAPI, Request, Depends
   from honeyhive import HoneyHiveTracer, trace
   import time
   
   app = FastAPI()
   tracer = HoneyHiveTracer.init()
   
   @app.middleware("http")
   async def tracing_middleware(request: Request, call_next):
       """Add request context to all traced functions."""
       start_time = time.time()
       
       # Set request context that traced functions can access
       request.state.trace_context = {
           "request.method": request.method,
           "request.url": str(request.url),
           "request.start_time": start_time
       }
       
       response = await call_next(request)
       
       # Try to enrich any active span with request info
       try:
           duration = time.time() - start_time
           enrich_span({
               **request.state.trace_context,
               "request.duration": duration,
               "response.status_code": response.status_code
           })
       except:
           pass  # No active span
       
       return response
   
   @app.get("/api/users/{user_id}")
   @trace(tracer=tracer, event_type="fastapi_user_lookup")
   async def get_user_endpoint(user_id: str, request: Request):
       """FastAPI endpoint with automatic tracing."""
       
       # Access request context
       if hasattr(request.state, 'trace_context'):
           enrich_span(request.state.trace_context)
       
       enrich_span({
           "user.id": user_id,
           "endpoint.type": "user_lookup",
           "api.framework": "fastapi"
       })
       
       # Simulate async user lookup
       user_data = await async_fetch_user(user_id)
       
       if user_data:
           enrich_span({
               "user.found": True,
               "user.data_size": len(str(user_data))
           })
           return user_data
       else:
           enrich_span({"user.found": False})
           raise HTTPException(status_code=404, detail="User not found")

Best Practices
--------------

**Decorator Ordering:**

.. code-block:: python

   # Correct order: @trace outermost, @evaluate innermost
   @trace(tracer=tracer, event_type="llm_operation")
   @evaluate(evaluator=QualityScoreEvaluator())
   @other_decorator
   def properly_decorated_function(prompt: str) -> str:
       """Function with properly ordered decorators."""
       return generate_response(prompt)

**Sensitive Data Handling:**

.. code-block:: python

   @trace(
       tracer=tracer,
       include_inputs=False,    # Don't log sensitive inputs
       include_outputs=False,   # Don't log sensitive outputs
       event_type="security_operation"
   )
   def handle_sensitive_operation(api_key: str, user_data: dict) -> dict:
       """Handle sensitive data without logging it."""
       
       # Add safe metadata manually
       enrich_span({
           "operation.type": "data_encryption",
           "user.id": user_data.get("id"),  # Safe to log user ID
           "operation.timestamp": time.time(),
           "security.level": "high"
           # Don't log api_key or sensitive user_data
       })
       
       return perform_secure_operation(api_key, user_data)

**Performance Considerations:**

.. code-block:: python

   # For high-frequency functions, use sampling
   import random
   
   def should_trace_call() -> bool:
       return random.random() < 0.1  # 10% sampling
   
   def conditional_trace_decorator(func):
       """Apply tracing conditionally for performance."""
       if should_trace_call():
           return trace(tracer=tracer, event_type="high_frequency")(func)
       return func
   
   @conditional_trace_decorator
   def high_frequency_function(item: str) -> str:
       """Function called many times per second."""
       return item.process()

**Resource Management:**

.. code-block:: python

   import atexit
   
   # Ensure proper cleanup when using decorators globally
   tracer = HoneyHiveTracer.init(
       api_key="your-key"
       
   )
   
   def cleanup_tracer():
       """Clean up tracer resources."""
       tracer.flush(timeout=5.0)
       tracer.close()
   
   atexit.register(cleanup_tracer)

Common Pitfalls and Solutions
-----------------------------

**Problem: Decorator Applied at Import Time**

.. code-block:: python

   # ❌ Problematic: Tracer might not be initialized yet
   tracer = None  # Will be initialized later
   
   @trace(tracer=tracer)  # tracer is None at decoration time!
   def problematic_function():
       pass
   
   # ✅ Solution 1: Lazy tracer resolution
   def get_current_tracer():
       return current_app.tracer  # Get from app context
   
   @trace(tracer=get_current_tracer)
   def solution1_function():
       pass
   
   # ✅ Solution 2: Late decoration
   def solution2_function():
       pass
   
   # Apply decorator after tracer is initialized
   tracer = HoneyHiveTracer.init(api_key="key" )
   solution2_function = trace(tracer=tracer)(solution2_function)

**Problem: Circular Import with Global Tracer**

.. code-block:: python

   # ❌ Problematic circular import pattern
   # module_a.py
   from module_b import tracer  # Circular import!
   
   @trace(tracer=tracer)
   def function_a():
       pass
   
   # ✅ Solution: Use dependency injection
   def create_traced_functions(tracer: HoneyHiveTracer):
       """Create functions with injected tracer."""
       
       @trace(tracer=tracer)
       def function_a():
           pass
       
       @trace(tracer=tracer)
       def function_b():
           pass
       
       return {
           "function_a": function_a,
           "function_b": function_b
       }

**Problem: Memory Leaks in Long-Running Applications**

.. code-block:: python

   # ✅ Solution: Proper resource management
   import weakref
   
   class TracerManager:
       def __init__(self):
           self._tracers = weakref.WeakSet()
       
       def create_tracer(self, **kwargs):
           tracer = HoneyHiveTracer.init(**kwargs)
           self._tracers.add(tracer)
           return tracer
       
       def cleanup_all(self):
           for tracer in self._tracers:
               try:
                   tracer.flush(timeout=2.0)
                   tracer.close()
               except:
                   pass
   
   # Global tracer manager
   tracer_manager = TracerManager()
   
   def get_service_tracer(service_name: str):
       return tracer_manager.create_tracer(           source="production"
       )
   
   # Clean shutdown
   import atexit
   atexit.register(tracer_manager.cleanup_all)

See Also
--------

- :doc:`tracer` - HoneyHiveTracer API reference
- :doc:`client` - HoneyHive client API reference
- :doc:`../evaluation/evaluators` - Built-in evaluators reference
- :doc:`../../tutorials/01-setup-first-tracer` - Basic tracing tutorial
- :doc:`../../how-to/evaluation/index` - Evaluation tutorial
- :doc:`../../how-to/advanced-tracing/custom-spans` - Advanced tracing patterns
- :doc:`../../explanation/concepts/tracing-fundamentals` - Tracing concepts and theory