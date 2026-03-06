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

.. py:decorator:: trace(event_type: Optional[str] = None, event_name: Optional[str] = None, tracer: Optional[HoneyHiveTracer] = None, **kwargs) -> Callable

   Decorator for automatic function tracing with HoneyHive.

   **Parameters:**

   :param event_type: Event type for categorization. Must be one of: ``"model"``, ``"tool"``, or ``"chain"``
   :type event_type: Optional[str]

   :param event_name: Name of the event. Defaults to the function name if not provided.
   :type event_name: Optional[str]

   :param tracer: HoneyHiveTracer instance to use for creating spans. If not provided, auto-discovers from context.
   :type tracer: Optional[HoneyHiveTracer]
   
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
       event_type="security_operation"
   )
   def process_payment(credit_card: str, amount: float) -> dict:
       """Secure function tracing without exposing sensitive data."""

       # Manual attribute setting for non-sensitive data
       tracer.enrich_span(
           metadata={
               "payment.amount": amount,
               "payment.currency": "USD",
               "operation.type": "payment_processing"
           }
       )

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
       tracer.enrich_span({
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
               tracer.enrich_span({
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
           
           tracer.enrich_span({
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
           
           tracer.enrich_span({
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
           
           tracer.enrich_span({
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
       
       tracer.enrich_span({
           "input.data_size": len(data),
           "operation.start_time": time.time()
       })
       
       if not data:
           raise ValueError("Data cannot be empty")
       
       if len(data) > 1000:
           raise RuntimeError("Data too large to process")
       
       # Normal processing
       result = [process_item(item) for item in data]
       
       tracer.enrich_span({
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
       
       tracer.enrich_span({
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
       
       tracer.enrich_span({
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
       
       tracer.enrich_span({
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
       
       tracer.enrich_span({
           "async.processing_time": 0.1,
           "data.items": len(data)
       })
       
       return {"processed": len(data), "status": "complete"}

Helper Functions
----------------

Span Enrichment
~~~~~~~~~~~~~~~

Use ``tracer.enrich_span()`` to add metadata, metrics, feedback, and other attributes to the currently active span. This is an instance method on ``HoneyHiveTracer``.

**Method Signature:**

.. py:method:: HoneyHiveTracer.enrich_span(attributes=None, metadata=None, metrics=None, feedback=None, inputs=None, outputs=None, config=None, user_properties=None, error=None, event_id=None, **kwargs)
   :no-index:

   Add attributes to the currently active span.

   :param attributes: Simple dictionary routed to metadata namespace.
   :type attributes: Optional[Dict[str, Any]]
   :param metadata: Business context data. Routes to ``honeyhive_metadata.*``.
   :type metadata: Optional[Dict[str, Any]]
   :param metrics: Numeric measurements. Routes to ``honeyhive_metrics.*``.
   :type metrics: Optional[Dict[str, Any]]
   :param feedback: User or system feedback. Routes to ``honeyhive_feedback.*``.
   :type feedback: Optional[Dict[str, Any]]
   :param inputs: Input data. Routes to ``honeyhive_inputs.*``.
   :type inputs: Optional[Dict[str, Any]]
   :param outputs: Output data. Routes to ``honeyhive_outputs.*``.
   :type outputs: Optional[Dict[str, Any]]
   :param config: Configuration parameters. Routes to ``honeyhive_config.*``.
   :type config: Optional[Dict[str, Any]]
   :param user_properties: User-specific properties. Routes to ``honeyhive_user_properties.*``.
   :type user_properties: Optional[Dict[str, Any]]
   :param error: Error message string. Stored as ``honeyhive_error``.
   :type error: Optional[str]
   :param event_id: Unique event identifier. Stored as ``honeyhive_event_id``.
   :type event_id: Optional[str]
   :param kwargs: Arbitrary kwargs routed to metadata namespace.
   :returns: True if enrichment succeeded, False otherwise.
   :rtype: bool

.. code-block:: python

   @trace(tracer=tracer, event_type="tool")
   def process_request(user_id: str, query: str) -> str:
       tracer.enrich_span(
           metadata={"user_id": user_id, "query_length": len(query)},
           metrics={"priority": 1}
       )
       return call_llm(query)

Session Enrichment
~~~~~~~~~~~~~~~~~~

Use ``tracer.enrich_session()`` to add data to the entire session (all spans in the current session).

**Method Signature:**

.. py:method:: HoneyHiveTracer.enrich_session(metadata=None, inputs=None, outputs=None, config=None, feedback=None, metrics=None, user_properties=None, session_id=None, **kwargs)
   :no-index:

   Update the current session with additional data.

   :param metadata: Additional metadata for the session.
   :type metadata: Optional[Dict[str, Any]]
   :param inputs: Session input data.
   :type inputs: Optional[Dict[str, Any]]
   :param outputs: Session output data.
   :type outputs: Optional[Dict[str, Any]]
   :param config: Configuration data.
   :type config: Optional[Dict[str, Any]]
   :param feedback: User feedback or evaluation results.
   :type feedback: Optional[Dict[str, Any]]
   :param metrics: Performance metrics.
   :type metrics: Optional[Dict[str, Any]]
   :param user_properties: User-specific properties.
   :type user_properties: Optional[Dict[str, Any]]
   :param session_id: Explicit session ID override. If not provided, uses tracer's current session.
   :type session_id: Optional[str]

.. code-block:: python

   tracer = HoneyHiveTracer.init(project="my-app")
   tracer.enrich_session(
       user_properties={"user_id": "user-123", "plan": "premium"},
       metadata={"environment": "production"}
   )

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
           tracer.enrich_span({
               "processing.phase": "validation"
           })
           
           validate_data(data)
           logger.debug("Data validation completed")
           
           tracer.enrich_span({
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
       # - Any custom attributes from tracer.enrich_span()
       logger.info("Processing user request", extra={
           "user_id": user_id,
           "operation_type": "user_processing"
       })
       
       tracer.enrich_span({
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
       tracer.enrich_span(attributes)
       
       # Process data
       result = process_data_efficiently(data)
       
       # Final attributes
       end_time = time.time()
       tracer.enrich_span({
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
       
       tracer.enrich_span({
           "function.version": "2.0",
           "input.data_keys": list(data.keys())
       })
       
       try:
           # Main processing logic
           validated_data = validate_input(data)
           tracer.enrich_span({"validation.status": "passed"})
           
           processed_data = process_validated_data(validated_data)
           tracer.enrich_span({"processing.status": "completed"})
           
           return processed_data
           
       except ValueError as e:
           # Handle validation errors
           tracer.enrich_span({
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
           tracer.enrich_span({
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
           tracer.enrich_span({
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
               tracer.enrich_span({
                   "retry.max_attempts": max_retries,
                   "retry.backoff_factor": backoff_factor
               })
               
               last_error = None
               
               for attempt in range(max_retries):
                   try:
                       tracer.enrich_span({
                           "retry.current_attempt": attempt + 1,
                           "retry.is_retry": attempt > 0
                       })
                       
                       result = func(*args, **kwargs)
                       
                       tracer.enrich_span({
                           "retry.success": True,
                           "retry.attempts_used": attempt + 1
                       })
                       
                       return result
                       
                   except Exception as e:
                       last_error = e
                       wait_time = backoff_factor * (2 ** attempt)
                       
                       tracer.enrich_span({
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
                           tracer.enrich_span({
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
       
       tracer.enrich_span({
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
               tracer.enrich_span({
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
       
       tracer.enrich_span({
           "user.id": user_id,
           "api.endpoint": "/api/users",
           "api.version": "v1"
       })
       
       user_data = fetch_user_data(user_id)
       
       if user_data:
           tracer.enrich_span({
               "user.found": True,
               "user.tier": user_data.get("tier", "standard")
           })
           return jsonify(user_data)
       else:
           tracer.enrich_span({"user.found": False})
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
           tracer.enrich_span({
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
           tracer.enrich_span(request.state.trace_context)
       
       tracer.enrich_span({
           "user.id": user_id,
           "endpoint.type": "user_lookup",
           "api.framework": "fastapi"
       })
       
       # Simulate async user lookup
       user_data = await async_fetch_user(user_id)
       
       if user_data:
           tracer.enrich_span({
               "user.found": True,
               "user.data_size": len(str(user_data))
           })
           return user_data
       else:
           tracer.enrich_span({"user.found": False})
           raise HTTPException(status_code=404, detail="User not found")

Best Practices
--------------

**Decorator Ordering:**

Apply ``@trace`` as the outermost decorator. Use other decorators below it as needed.

**Sensitive Data Handling:**

.. code-block:: python

   @trace(
       tracer=tracer,
               event_type="security_operation"
   )
   def handle_sensitive_operation(api_key: str, user_data: dict) -> dict:
       """Handle sensitive data without logging it."""
       
       # Add safe metadata manually
       tracer.enrich_span({
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
