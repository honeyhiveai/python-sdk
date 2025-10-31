Advanced Tracing Patterns
=========================

**Problem:** You need sophisticated tracing patterns for complex scenarios: context propagation across service boundaries, conditional tracing, dynamic sampling, trace correlation, and distributed system tracing.

**Solution:** Implement advanced patterns that go beyond basic span creation and enrichment for production-grade observability.

.. note::
   **Prerequisites**
   
   Before using these patterns, ensure you're familiar with:
   
   - :doc:`span-enrichment` - Basic enrichment patterns
   - :doc:`custom-spans` - Custom span creation
   - :doc:`class-decorators` - Class-level tracing

.. contents:: Quick Navigation
   :local:
   :depth: 2

Context Propagation
-------------------

**When to Use:** Trace requests across multiple services, async operations, or thread boundaries.

Cross-Service Tracing
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   from opentelemetry import trace as otel_trace
   from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
   import requests
   
   tracer = HoneyHiveTracer.init(project="distributed-system")
   propagator = TraceContextTextMapPropagator()
   
   @trace(tracer=tracer)
   def call_downstream_service(user_id: str) -> dict:
       """Call downstream service with trace context propagation."""
       from honeyhive import enrich_span
       
       # Get current span context
       current_span = otel_trace.get_current_span()
       carrier = {}
       
       # Inject trace context into HTTP headers
       propagator.inject(carrier)
       
       enrich_span({
           "service.downstream": "user-service",
           "service.user_id": user_id
       })
       
       # Make HTTP request with trace context headers
       response = requests.post(
           "https://user-service/api/process",
           json={"user_id": user_id},
           headers=carrier  # Trace context propagated
       )
       
       enrich_span({"service.response_code": response.status_code})
       
       return response.json()

Async Context Propagation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from honeyhive import trace
   from opentelemetry.context import attach, detach, get_current
   
   @trace(tracer=tracer)
   async def async_workflow(query: str) -> str:
       """Async workflow with context propagation."""
       from honeyhive import enrich_span
       
       enrich_span({"workflow.type": "async", "workflow.query": query})
       
       # Context is automatically propagated to async tasks
       results = await asyncio.gather(
           async_task_1(query),
           async_task_2(query)
       )
       
       enrich_span({"workflow.tasks_completed": len(results)})
       return " ".join(results)
   
   @trace(tracer=tracer)
   async def async_task_1(query: str) -> str:
       """Async task with inherited trace context."""
       from honeyhive import enrich_span
       enrich_span({"task.name": "task_1"})
       
       await asyncio.sleep(0.1)  # Simulate async work
       return "Result 1"
   
   @trace(tracer=tracer)
   async def async_task_2(query: str) -> str:
       """Async task with inherited trace context."""
       from honeyhive import enrich_span
       enrich_span({"task.name": "task_2"})
       
       await asyncio.sleep(0.1)  # Simulate async work
       return "Result 2"

Conditional Tracing
-------------------

**When to Use:** Apply tracing selectively based on runtime conditions.

Sampling-Based Tracing
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import random
   from honeyhive import HoneyHiveTracer
   
   tracer = HoneyHiveTracer.init(project="sampled-tracing")
   
   def conditional_trace(sample_rate: float = 0.1):
       """Decorator that applies tracing based on sample rate."""
       def decorator(func):
           def wrapper(*args, **kwargs):
               # Sample: trace only sample_rate% of requests
               should_trace = random.random() < sample_rate
               
               if should_trace:
                   from honeyhive import trace
                   return trace(tracer=tracer)(func)(*args, **kwargs)
               else:
                   # Execute without tracing
                   return func(*args, **kwargs)
           
           return wrapper
       return decorator
   
   @conditional_trace(sample_rate=0.1)  # Trace 10% of requests
   def high_volume_operation(data: dict) -> dict:
       """High-volume operation with sampling."""
       return {"processed": True, **data}

User-Based Tracing
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def trace_for_users(user_ids: set):
       """Trace only for specific users."""
       def decorator(func):
           def wrapper(user_id: str, *args, **kwargs):
               should_trace = user_id in user_ids
               
               if should_trace:
                   from honeyhive import trace, enrich_span
                   
                   @trace(tracer=tracer)
                   def traced_func(user_id, *args, **kwargs):
                       enrich_span({"user.id": user_id, "user.traced": True})
                       return func(user_id, *args, **kwargs)
                   
                   return traced_func(user_id, *args, **kwargs)
               else:
                   return func(user_id, *args, **kwargs)
           
           return wrapper
       return decorator
   
   # Trace only for beta users
   BETA_USERS = {"user_123", "user_456"}
   
   @trace_for_users(BETA_USERS)
   def beta_feature(user_id: str, data: dict) -> dict:
       """Feature traced only for beta users."""
       return {"feature": "beta", "user": user_id, **data}

Dynamic Sampling
----------------

**When to Use:** Adjust trace sampling based on runtime metrics or system load.

Adaptive Sampling
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   from collections import deque
   
   class AdaptiveSampler:
       """Adjust sampling rate based on request volume."""
       
       def __init__(self, base_rate: float = 0.1, window_size: int = 100):
           self.base_rate = base_rate
           self.window_size = window_size
           self.request_times = deque(maxlen=window_size)
       
       def should_sample(self) -> bool:
           """Determine if current request should be sampled."""
           current_time = time.time()
           self.request_times.append(current_time)
           
           if len(self.request_times) < 2:
               return True  # Always sample first requests
           
           # Calculate requests per second
           time_span = current_time - self.request_times[0]
           rps = len(self.request_times) / time_span if time_span > 0 else 0
           
           # Reduce sampling rate under high load
           if rps > 100:
               sample_rate = self.base_rate / 10
           elif rps > 50:
               sample_rate = self.base_rate / 2
           else:
               sample_rate = self.base_rate
           
           return random.random() < sample_rate
   
   # Global sampler
   sampler = AdaptiveSampler(base_rate=0.1)
   
   def adaptive_trace(func):
       """Decorator with adaptive sampling."""
       def wrapper(*args, **kwargs):
           if sampler.should_sample():
               from honeyhive import trace
               return trace(tracer=tracer)(func)(*args, **kwargs)
           else:
               return func(*args, **kwargs)
       
       return wrapper
   
   @adaptive_trace
   def high_traffic_endpoint(request_data: dict) -> dict:
       """Endpoint with adaptive sampling."""
       return {"status": "processed"}

Trace Correlation
-----------------

**When to Use:** Link related traces across different operations or sessions.

Request ID Correlation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import uuid
   from contextvars import ContextVar
   
   # Context variable for request tracking
   request_id_var: ContextVar[str] = ContextVar('request_id', default=None)
   
   def with_request_id(func):
       """Decorator that adds request ID to all spans."""
       def wrapper(*args, **kwargs):
           # Generate or propagate request ID
           request_id = request_id_var.get() or str(uuid.uuid4())
           request_id_var.set(request_id)
           
           from honeyhive import trace, enrich_span
           
           @trace(tracer=tracer)
           def traced_func(*args, **kwargs):
               enrich_span({"request.id": request_id})
               return func(*args, **kwargs)
           
           return traced_func(*args, **kwargs)
       
       return wrapper
   
   @with_request_id
   def handle_request(data: dict) -> dict:
       """Handle request with correlated request ID."""
       # All child operations will have the same request ID
       process_step_1(data)
       process_step_2(data)
       return {"status": "complete"}
   
   @with_request_id
   def process_step_1(data: dict):
       """Step 1 - shares request ID from parent."""
       pass
   
   @with_request_id
   def process_step_2(data: dict):
       """Step 2 - shares request ID from parent."""
       pass

Session Correlation
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.models import EventType
   
   class SessionTracker:
       """Track multiple operations within a session."""
       
       def __init__(self, session_id: str):
           self.session_id = session_id
           self.operation_count = 0
       
       def trace_operation(self, operation_name: str):
           """Trace operation with session context."""
           def decorator(func):
               def wrapper(*args, **kwargs):
                   self.operation_count += 1
                   
                   from honeyhive import trace, enrich_span
                   
                   @trace(tracer=tracer, event_type=EventType.chain)
                   def traced_func(*args, **kwargs):
                       enrich_span({
                           "session.id": self.session_id,
                           "session.operation": operation_name,
                           "session.operation_number": self.operation_count
                       })
                       return func(*args, **kwargs)
                   
                   return traced_func(*args, **kwargs)
               
               return wrapper
           return decorator
   
   # Usage
   session = SessionTracker("session_abc123")
   
   @session.trace_operation("login")
   def user_login(username: str):
       """Login operation tracked in session."""
       return {"logged_in": True}
   
   @session.trace_operation("fetch_data")
   def fetch_user_data(user_id: str):
       """Data fetch tracked in session."""
       return {"data": "..."}

Error Recovery Patterns
-----------------------

**When to Use:** Implement retry logic with comprehensive tracing.

Traced Retry Pattern
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   from functools import wraps
   
   def traced_retry(max_attempts: int = 3, backoff: float = 1.0):
       """Retry decorator with trace enrichment."""
       def decorator(func):
           @wraps(func)
           def wrapper(*args, **kwargs):
               from honeyhive import trace, enrich_span
               
               @trace(tracer=tracer)
               def retry_wrapper(*args, **kwargs):
                   enrich_span({
                       "retry.max_attempts": max_attempts,
                       "retry.backoff": backoff
                   })
                   
                   for attempt in range(1, max_attempts + 1):
                       try:
                           enrich_span({f"retry.attempt_{attempt}": "started"})
                           result = func(*args, **kwargs)
                           
                           enrich_span({
                               "retry.succeeded_at_attempt": attempt,
                               "retry.total_attempts": attempt
                           })
                           return result
                       
                       except Exception as e:
                           enrich_span({
                               f"retry.attempt_{attempt}_failed": str(e),
                               f"retry.attempt_{attempt}_error_type": type(e).__name__
                           })
                           
                           if attempt == max_attempts:
                               enrich_span({"retry.all_failed": True})
                               raise
                           
                           # Exponential backoff
                           sleep_time = backoff * (2 ** (attempt - 1))
                           enrich_span({f"retry.attempt_{attempt}_backoff_s": sleep_time})
                           time.sleep(sleep_time)
                   
                   return None  # Should never reach here
               
               return retry_wrapper(*args, **kwargs)
           
           return wrapper
       return decorator
   
   @traced_retry(max_attempts=3, backoff=1.0)
   def unreliable_api_call(endpoint: str) -> dict:
       """API call with retry logic and tracing."""
       # Simulate unreliable call
       return requests.get(endpoint).json()

Performance Monitoring
----------------------

**When to Use:** Track detailed performance metrics within traces.

Resource Usage Tracing
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import psutil
   import os
   
   def trace_with_resources(func):
       """Trace function with resource usage metrics."""
       def wrapper(*args, **kwargs):
           from honeyhive import trace, enrich_span
           
           @trace(tracer=tracer)
           def traced_func(*args, **kwargs):
               process = psutil.Process(os.getpid())
               
               # Before execution
               cpu_before = process.cpu_percent()
               mem_before = process.memory_info().rss / 1024 / 1024  # MB
               
               enrich_span({
                   "resources.cpu_before_%": cpu_before,
                   "resources.memory_before_mb": mem_before
               })
               
               start_time = time.perf_counter()
               result = func(*args, **kwargs)
               duration = time.perf_counter() - start_time
               
               # After execution
               cpu_after = process.cpu_percent()
               mem_after = process.memory_info().rss / 1024 / 1024
               
               enrich_span({
                   "resources.duration_ms": duration * 1000,
                   "resources.cpu_after_%": cpu_after,
                   "resources.memory_after_mb": mem_after,
                   "resources.memory_delta_mb": mem_after - mem_before
               })
               
               return result
           
           return traced_func(*args, **kwargs)
       
       return wrapper
   
   @trace_with_resources
   def memory_intensive_operation(data_size: int):
       """Operation with resource monitoring."""
       # Memory-intensive work
       large_data = [0] * (data_size * 1000000)
       return len(large_data)

Best Practices
--------------

**1. Choose Appropriate Patterns**

- **High-volume systems**: Use adaptive sampling
- **Distributed systems**: Implement context propagation
- **Debug scenarios**: Use user-based or conditional tracing
- **Performance-critical**: Use resource usage tracing

**2. Combine Patterns**

.. code-block:: python

   @adaptive_trace  # Sampling
   @with_request_id  # Correlation
   @traced_retry(max_attempts=3)  # Error handling
   def complex_operation(data: dict) -> dict:
       """Operation with multiple advanced patterns."""
       return process_data(data)

**3. Monitor Sampling Effectiveness**

.. code-block:: python

   # Track sampling statistics
   from collections import defaultdict
   
   sampling_stats = defaultdict(int)
   
   def track_sampling(func):
       def wrapper(*args, **kwargs):
           sampled = sampler.should_sample()
           sampling_stats['total'] += 1
           if sampled:
               sampling_stats['sampled'] += 1
           
           return func(*args, **kwargs) if not sampled else traced_func(*args, **kwargs)
       return wrapper
   
   # Periodically log stats
   sample_rate = sampling_stats['sampled'] / sampling_stats['total']
   print(f"Current sample rate: {sample_rate:.2%}")

Next Steps
----------

- :doc:`span-enrichment` - Comprehensive enrichment patterns
- :doc:`custom-spans` - Custom span creation
- :doc:`/how-to/deployment/production` - Production tracing strategies

**Key Takeaway:** Advanced tracing patterns enable sophisticated observability for complex, distributed, and high-scale LLM applications. Use context propagation for distributed systems, conditional tracing for high-volume services, and correlation patterns for debugging multi-step workflows. ✨

