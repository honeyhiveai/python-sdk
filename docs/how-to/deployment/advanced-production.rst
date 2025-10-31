Advanced Production Patterns
============================


**Problem:** You need advanced resilience patterns, custom monitoring implementations, and sophisticated deployment strategies for mission-critical production environments.


**Solution:** Implement these advanced patterns for production-grade reliability and observability.


.. note::
   **Prerequisites**
   
   
   Before implementing these advanced patterns, ensure you have:
   
   
   - Basic production deployment working (see :doc:`production`)
   - Understanding of circuit breakers and resilience patterns
   - Monitoring infrastructure in place
   - Staging environment for testing


This guide covers advanced patterns beyond basic production deployment.


Circuit Breaker Pattern
-----------------------


**When to Use:**


- High-volume applications where HoneyHive failures shouldn't impact your service
- Mission-critical systems requiring graceful degradation
- Applications with strict uptime SLAs


**Implementation:**


.. code-block:: python


   import time
   from enum import Enum
   from honeyhive import HoneyHiveTracer
   import logging
   
   
   logger = logging.getLogger(__name__)
   
   
   class CircuitState(Enum):
       CLOSED = "closed"      # Normal operation - requests allowed
       OPEN = "open"          # Failing - requests blocked  
       HALF_OPEN = "half_open"  # Testing recovery - limited requests
   
   
   class HoneyHiveCircuitBreaker:
       """Circuit breaker for HoneyHive tracer initialization."""
       
       
       def __init__(
           self,
           failure_threshold: int = 5,
           recovery_timeout: int = 60,
           half_open_max_calls: int = 3
       ):
           self.failure_threshold = failure_threshold
           self.recovery_timeout = recovery_timeout
           self.half_open_max_calls = half_open_max_calls
           
           
           self.failure_count = 0
           self.success_count = 0
           self.half_open_calls = 0
           self.last_failure_time = None
           self.state = CircuitState.CLOSED
           self.tracer = None
       
       
       def get_tracer(self):
           """Get tracer with circuit breaker protection."""
           
           
           # Circuit is OPEN - block requests
           if self.state == CircuitState.OPEN:
               if time.time() - self.last_failure_time > self.recovery_timeout:
                   logger.info("Circuit breaker moving to HALF_OPEN state")
                   self.state = CircuitState.HALF_OPEN
                   self.half_open_calls = 0
               else:
                   # Still in cooldown period
                   return None
           
           
           # Circuit is HALF_OPEN - limited testing
           if self.state == CircuitState.HALF_OPEN:
               if self.half_open_calls >= self.half_open_max_calls:
                   return None  # Max test calls reached
               self.half_open_calls += 1
           
           
           # Try to get/create tracer
           if self.state in [CircuitState.CLOSED, CircuitState.HALF_OPEN]:
               try:
                   if not self.tracer:
                       self.tracer = HoneyHiveTracer.init(
                           api_key=os.getenv("HH_API_KEY"),
                           project=os.getenv("HH_PROJECT")
                       )
                   
                   
                   # Success - update state
                   if self.state == CircuitState.HALF_OPEN:
                       self.success_count += 1
                       if self.success_count >= self.half_open_max_calls:
                           logger.info("Circuit breaker CLOSED - recovery successful")
                           self.state = CircuitState.CLOSED
                           self.failure_count = 0
                           self.success_count = 0
                   
                   
                   return self.tracer
               
               
               except Exception as e:
                   self.failure_count += 1
                   self.last_failure_time = time.time()
                   logger.warning(f"HoneyHive tracer failure #{self.failure_count}: {e}")
                   
                   
                   if self.failure_count >= self.failure_threshold:
                       self.state = CircuitState.OPEN
                       logger.error(
                           f"Circuit breaker OPENED after {self.failure_count} failures"
                       )
                   
                   
                   return None
   
   
   # Global circuit breaker instance
   honeyhive_circuit_breaker = HoneyHiveCircuitBreaker(
       failure_threshold=5,
       recovery_timeout=60
   )
   
   
   def get_safe_tracer():
       """Get tracer with circuit breaker protection."""
       tracer = honeyhive_circuit_breaker.get_tracer()
       
       
       if not tracer:
           logger.warning("HoneyHive tracer unavailable (circuit breaker active)")
       
       
       return tracer
   
   
   # Usage in application
   tracer = get_safe_tracer()
   if tracer:
       # Tracing enabled
       from openinference.instrumentation.openai import OpenAIInstrumentor
       instrumentor = OpenAIInstrumentor()
       instrumentor.instrument(tracer_provider=tracer.provider)


**Benefits:**


- Prevents cascading failures
- Automatic recovery testing
- Graceful degradation
- Reduced error noise in logs


**Monitoring Circuit Breaker:**


.. code-block:: python


   def get_circuit_breaker_metrics():
       """Get current circuit breaker state for monitoring."""
       return {
           "state": honeyhive_circuit_breaker.state.value,
           "failure_count": honeyhive_circuit_breaker.failure_count,
           "last_failure": honeyhive_circuit_breaker.last_failure_time,
           "is_available": honeyhive_circuit_breaker.state != CircuitState.OPEN
       }


Custom Monitoring Implementation
--------------------------------


**When to Use:**


- Need detailed metrics about tracing performance
- Custom alerting requirements
- Integration with existing monitoring systems (Prometheus, DataDog, etc.)


**Comprehensive Monitoring Class:**


.. code-block:: python


   import time
   import logging
   from collections import defaultdict, deque
   from typing import Dict, List
   from dataclasses import dataclass, field
   from datetime import datetime
   
   
   @dataclass
   class TracingMetrics:
       """Comprehensive tracing metrics collector."""
       
       
       trace_count: int = 0
       trace_errors: int = 0
       trace_latencies: deque = field(default_factory=lambda: deque(maxlen=1000))
       error_types: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
       traces_by_endpoint: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
       last_reset: float = field(default_factory=time.time)
       
       
       def record_trace(
           self,
           duration: float,
           success: bool,
           endpoint: str = None,
           error_type: str = None
       ):
           """Record a trace attempt."""
           self.trace_count += 1
           self.trace_latencies.append(duration)
           
           
           if endpoint:
               self.traces_by_endpoint[endpoint] += 1
           
           
           if not success:
               self.trace_errors += 1
               if error_type:
                   self.error_types[error_type] += 1
       
       
       def get_stats(self) -> dict:
           """Get comprehensive statistics."""
           if not self.trace_latencies:
               return {
                   "trace_count": 0,
                   "error_rate": 0,
                   "avg_latency_ms": 0,
                   "p50_latency_ms": 0,
                   "p95_latency_ms": 0,
                   "p99_latency_ms": 0
               }
           
           
           sorted_latencies = sorted(self.trace_latencies)
           n = len(sorted_latencies)
           
           
           return {
               "trace_count": self.trace_count,
               "error_count": self.trace_errors,
               "error_rate": self.trace_errors / self.trace_count if self.trace_count > 0 else 0,
               "avg_latency_ms": sum(sorted_latencies) / n,
               "p50_latency_ms": sorted_latencies[int(0.50 * n)],
               "p95_latency_ms": sorted_latencies[int(0.95 * n)],
               "p99_latency_ms": sorted_latencies[int(0.99 * n)],
               "error_types": dict(self.error_types),
               "traces_by_endpoint": dict(self.traces_by_endpoint),
               "uptime_seconds": time.time() - self.last_reset
           }
       
       
       def reset(self):
           """Reset all metrics."""
           self.trace_count = 0
           self.trace_errors = 0
           self.trace_latencies.clear()
           self.error_types.clear()
           self.traces_by_endpoint.clear()
           self.last_reset = time.time()
   
   
   # Global metrics instance
   tracing_metrics = TracingMetrics()
   
   
   def monitored_trace(tracer, event_type=None):
       """Decorator that adds monitoring to traces."""
       def decorator(func):
           def wrapper(*args, **kwargs):
               start_time = time.time()
               success = True
               error_type = None
               endpoint = func.__name__
               
               
               try:
                   if tracer:
                       result = trace(tracer=tracer, event_type=event_type)(func)(*args, **kwargs)
                   else:
                       result = func(*args, **kwargs)
                   return result
               except Exception as e:
                   success = False
                   error_type = type(e).__name__
                   raise
               finally:
                   duration = (time.time() - start_time) * 1000  # Convert to ms
                   tracing_metrics.record_trace(
                       duration=duration,
                       success=success,
                       endpoint=endpoint,
                       error_type=error_type
                   )
           
           
           return wrapper
       return decorator


**Prometheus Integration:**


.. code-block:: python


   from prometheus_client import Counter, Histogram, Gauge
   
   
   # Define Prometheus metrics
   trace_counter = Counter(
       'honeyhive_traces_total',
       'Total number of traces sent',
       ['endpoint', 'status']
   )
   
   
   trace_latency = Histogram(
       'honeyhive_trace_latency_seconds',
       'Trace operation latency',
       ['endpoint']
   )
   
   
   trace_errors = Counter(
       'honeyhive_trace_errors_total',
       'Total tracing errors',
       ['error_type']
   )
   
   
   circuit_breaker_state = Gauge(
       'honeyhive_circuit_breaker_state',
       'Circuit breaker state (0=closed, 1=half_open, 2=open)'
   )
   
   
   def export_to_prometheus():
       """Export metrics to Prometheus."""
       stats = tracing_metrics.get_stats()
       
       
       # Update Prometheus metrics
       for endpoint, count in stats['traces_by_endpoint'].items():
           trace_counter.labels(endpoint=endpoint, status='success').inc(count)
       
       
       for error_type, count in stats['error_types'].items():
           trace_errors.labels(error_type=error_type).inc(count)
       
       
       # Update circuit breaker state
       state_mapping = {
           CircuitState.CLOSED: 0,
           CircuitState.HALF_OPEN: 1,
           CircuitState.OPEN: 2
       }
       circuit_breaker_state.set(
           state_mapping.get(honeyhive_circuit_breaker.state, 0)
       )


Blue-Green Deployment Strategy
------------------------------


**When to Use:**


- Zero-downtime tracing configuration changes
- Safe rollout of new HoneyHive features
- A/B testing tracing strategies


**Implementation:**


.. code-block:: python


   import os
   from honeyhive import HoneyHiveTracer
   
   
   class DeploymentManager:
       """Manage blue-green deployments for tracing."""
       
       
       def __init__(self):
           self.current_environment = os.getenv("DEPLOYMENT_ENV", "blue")
           self.tracers = {}
       
       
       def create_environment_tracer(self) -> HoneyHiveTracer:
           """Create tracer based on deployment environment."""
           
           
           # Environment-specific configuration
           env_configs = {
               "blue": {
                   "project": "production-app",
                   "source": "production-blue"
               },
               "green": {
                   "project": "production-app-green",
                   "source": "production-green"
               },
               "staging": {
                   "project": "staging-app",
                   "source": "staging"
               }
           }
           
           
           config = env_configs.get(self.current_environment, env_configs["blue"])
           
           
           if self.current_environment not in self.tracers:
               self.tracers[self.current_environment] = HoneyHiveTracer.init(
                   api_key=os.getenv("HH_API_KEY"),
                   **config
               )
           
           
           return self.tracers[self.current_environment]
       
       
       def switch_environment(self, new_env: str):
           """Switch to a different environment."""
           if new_env in ["blue", "green", "staging"]:
               self.current_environment = new_env
               return self.create_environment_tracer()
           else:
               raise ValueError(f"Invalid environment: {new_env}")
   
   
   # Global deployment manager
   deployment_manager = DeploymentManager()
   tracer = deployment_manager.create_environment_tracer()


**Canary Deployment with Gradual Rollout:**


.. code-block:: python


   import random
   
   
   class CanaryDeploymentManager:
       """Gradual rollout with canary deployment."""
       
       
       def __init__(self):
           self.canary_percentage = float(os.getenv("CANARY_PERCENTAGE", "0"))
           self.stable_tracer = None
           self.canary_tracer = None
       
       
       def get_tracer(self, user_id: str = None) -> HoneyHiveTracer:
           """Get tracer based on canary rollout percentage."""
           
           
           # Determine if this request goes to canary
           is_canary = random.random() < (self.canary_percentage / 100)
           
           
           if is_canary:
               if not self.canary_tracer:
                   self.canary_tracer = HoneyHiveTracer.init(
                       api_key=os.getenv("HH_API_KEY"),
                       project=os.getenv("HH_PROJECT"),
                       source="production-canary"
                   )
               return self.canary_tracer
           else:
               if not self.stable_tracer:
                   self.stable_tracer = HoneyHiveTracer.init(
                       api_key=os.getenv("HH_API_KEY"),
                       project=os.getenv("HH_PROJECT"),
                       source="production-stable"
                   )
               return self.stable_tracer
   
   
   canary_manager = CanaryDeploymentManager()


**Traffic-Based Routing:**


.. code-block:: python


   from flask import request
   
   
   def get_deployment_tracer():
       """Route to different tracers based on request headers."""
       
       
       # Check for deployment routing header
       deployment_tier = request.headers.get("X-Deployment-Tier", "stable")
       
       
       if deployment_tier == "canary":
           return canary_manager.canary_tracer
       elif deployment_tier == "experimental":
           return create_experimental_tracer()
       else:
           return canary_manager.stable_tracer


Best Practices
--------------


**1. Circuit Breaker Configuration:**


- Set `failure_threshold` based on your error budget (typically 3-5 failures)
- Set `recovery_timeout` to allow time for issues to resolve (60-120 seconds)
- Monitor circuit breaker state changes


**2. Monitoring Strategy:**


- Export metrics every 60 seconds
- Alert on error rate > 5%
- Alert on circuit breaker state changes
- Dashboard all key metrics


**3. Deployment Safety:**


- Start with 5% canary traffic
- Increase to 25%, then 50%, then 100% over 24-48 hours
- Monitor error rates at each stage
- Have rollback procedure ready


**4. Performance Tuning:**


- Use connection pooling for high-volume applications
- Batch trace exports (handled automatically by SDK)
- Monitor trace latency - should be <10ms


Integration Examples
--------------------


**Complete Production Setup:**


.. code-block:: python


   """
   production_tracing.py - Complete production tracing setup
   """

   from honeyhive import HoneyHiveTracer
   import os
   import logging
   import time
   
   
   logger = logging.getLogger(__name__)
   
   
   # Initialize with all advanced patterns
   tracer = None
   
   
   try:
       # Circuit breaker protected initialization
       tracer = get_safe_tracer()
       
       
       if tracer:
           # Setup monitoring
           from openinference.instrumentation.openai import OpenAIInstrumentor
           instrumentor = OpenAIInstrumentor()
           instrumentor.instrument(tracer_provider=tracer.provider)
           
           
           logger.info("HoneyHive tracing initialized successfully")
       else:
           logger.warning("HoneyHive tracing unavailable (circuit breaker)")
   
   
   except Exception as e:
       logger.error(f"Failed to initialize HoneyHive: {e}")
       tracer = None
   
   
   # Export metrics every 60 seconds
   import threading
   
   
   def export_metrics_loop():
       while True:
           time.sleep(60)
           try:
               export_to_prometheus()
               logger.debug("Metrics exported to Prometheus")
           except Exception as e:
               logger.error(f"Failed to export metrics: {e}")
   
   
   metrics_thread = threading.Thread(target=export_metrics_loop, daemon=True)
   metrics_thread.start()


Next Steps
----------


- :doc:`production` - Basic production deployment guide
- :doc:`/how-to/monitoring/index` - Monitoring and alerting
- :doc:`/how-to/llm-application-patterns` - Application architecture patterns


**Key Takeaway:** Advanced production patterns provide resilience, comprehensive monitoring, and safe deployment strategies for mission-critical applications. Implement these patterns when basic deployment isn't enough for your reliability requirements. ✨




