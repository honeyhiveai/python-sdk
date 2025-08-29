# Advanced Patterns

Complex use cases and best practices for the HoneyHive Python SDK.

## Table of Contents

- [Custom Instrumentors](#custom-instrumentors)
- [Advanced Span Management](#advanced-span-management)
- [Performance Optimization](#performance-optimization)
- [Integration Patterns](#integration-patterns)

---

## Custom Instrumentors

### Custom OpenInference Instrumentor

```python
from openinference.instrumentation.base import BaseInstrumentor
from opentelemetry import trace

class CustomAIInstrumentor(BaseInstrumentor):
    def __init__(self, service_name="custom-ai"):
        self.service_name = service_name
        self._is_instrumented = False
    
    def instrument(self, **kwargs):
        if self._is_instrumented:
            return
        
        # Custom instrumentation logic
        self._instrument_custom_ai()
        self._is_instrumented = True
    
    def _instrument_custom_ai(self):
        """Instrument custom AI operations."""
        # Implementation details
        pass

# Usage
tracer = HoneyHiveTracer(
    instrumentors=[CustomAIInstrumentor("my-ai-service")]
)
```

### Conditional Instrumentation

```python
class ConditionalInstrumentor:
    def __init__(self, condition_func):
        self.condition_func = condition_func
        self.instrumentors = []
    
    def add_instrumentor(self, instrumentor):
        self.instrumentors.append(instrumentor)
    
    def instrument(self):
        if self.condition_func():
            for instrumentor in self.instrumentors:
                instrumentor.instrument()

# Usage
def should_instrument():
    return os.getenv("ENVIRONMENT") == "production"

conditional = ConditionalInstrumentor(should_instrument)
conditional.add_instrumentor(OpenAIInstrumentor())
conditional.instrument()
```

---

## Advanced Span Management

### Span Context Propagation

```python
from opentelemetry import context, trace

def propagate_context_to_thread():
    """Propagate span context to a new thread."""
    
    with tracer.start_span("parent-operation") as parent_span:
        # Get current context
        ctx = context.get_current()
        
        def worker_function():
            # Attach context to new thread
            context.attach(ctx)
            
            with tracer.start_span("worker-operation") as worker_span:
                worker_span.set_attribute("thread.id", threading.get_ident())
                # Worker logic here
                pass
        
        # Start worker thread
        thread = threading.Thread(target=worker_function)
        thread.start()
        thread.join()
```

### Custom Span Attributes

```python
class CustomSpanManager:
    def __init__(self, tracer):
        self.tracer = tracer
    
    def start_custom_span(self, name, **attributes):
        """Start span with custom attributes."""
        
        # Add default attributes
        default_attrs = {
            "service.version": "1.0.0",
            "deployment.environment": os.getenv("ENVIRONMENT", "development"),
            "timestamp": time.time()
        }
        
        # Merge with custom attributes
        all_attributes = {**default_attrs, **attributes}
        
        return self.tracer.start_span(name, all_attributes)

# Usage
span_manager = CustomSpanManager(tracer)
with span_manager.start_custom_span("custom-operation", user_id="123"):
    # Operation logic
    pass
```

---

## Performance Optimization

### Span Batching

```python
class SpanBatcher:
    def __init__(self, tracer, batch_size=100):
        self.tracer = tracer
        self.batch_size = batch_size
        self.pending_spans = []
        self.lock = threading.Lock()
    
    def add_span(self, span_data):
        """Add span data to batch."""
        with self.lock:
            self.pending_spans.append(span_data)
            
            if len(self.pending_spans) >= self.batch_size:
                self.flush_batch()
    
    def flush_batch(self):
        """Flush pending spans."""
        with self.lock:
            if self.pending_spans:
                # Process batch
                self._process_batch(self.pending_spans)
                self.pending_spans.clear()
    
    def _process_batch(self, spans):
        """Process a batch of spans."""
        # Batch processing logic
        pass

# Usage
batcher = SpanBatcher(tracer)
for i in range(1000):
    batcher.add_span({"operation": f"op_{i}", "data": f"data_{i}"})
batcher.flush_batch()
```

### Memory Management

```python
class MemoryAwareTracer:
    def __init__(self, tracer, max_spans=1000):
        self.tracer = tracer
        self.max_spans = max_spans
        self.active_spans = []
        self.lock = threading.Lock()
    
    def start_span(self, name, attributes=None):
        """Start span with memory management."""
        
        with self.lock:
            # Check memory usage
            if len(self.active_spans) >= self.max_spans:
                self._cleanup_old_spans()
            
            # Create span
            span = self.tracer.start_span(name, attributes)
            self.active_spans.append(span)
            
            return span
    
    def _cleanup_old_spans(self):
        """Clean up old spans to free memory."""
        # Remove completed spans
        self.active_spans = [span for span in self.active_spans if span.is_recording()]
        
        # If still too many, force cleanup
        if len(self.active_spans) >= self.max_spans:
            self.active_spans = self.active_spans[-self.max_spans//2:]

# Usage
memory_tracer = MemoryAwareTracer(tracer, max_spans=500)
```

---

## Integration Patterns

### Framework Integration

```python
class FrameworkIntegration:
    def __init__(self, tracer):
        self.tracer = tracer
    
    def integrate_with_fastapi(self, app):
        """Integrate with FastAPI application."""
        
        @app.middleware("http")
        async def tracing_middleware(request, call_next):
            with self.tracer.start_span("http-request") as span:
                span.set_attribute("http.method", request.method)
                span.set_attribute("http.url", str(request.url))
                
                response = await call_next(request)
                
                span.set_attribute("http.status_code", response.status_code)
                return response
    
    def integrate_with_celery(self, celery_app):
        """Integrate with Celery tasks."""
        
        @celery_app.task(bind=True)
        def traced_task(self, *args, **kwargs):
            with self.tracer.start_span("celery-task") as span:
                span.set_attribute("celery.task_name", self.name)
                span.set_attribute("celery.task_id", self.request.id)
                
                # Execute task
                return self.run(*args, **kwargs)

# Usage
integration = FrameworkIntegration(tracer)
integration.integrate_with_fastapi(app)
integration.integrate_with_celery(celery_app)
```

### Custom Metrics Collection

```python
class MetricsCollector:
    def __init__(self, tracer):
        self.tracer = tracer
        self.metrics = {}
        self.lock = threading.Lock()
    
    def record_metric(self, name, value, labels=None):
        """Record a custom metric."""
        
        with self.lock:
            if name not in self.metrics:
                self.metrics[name] = []
            
            metric_data = {
                "value": value,
                "timestamp": time.time(),
                "labels": labels or {}
            }
            
            self.metrics[name].append(metric_data)
    
    def get_metrics(self):
        """Get collected metrics."""
        with self.lock:
            return self.metrics.copy()
    
    def export_metrics_to_span(self, span_name):
        """Export metrics to a span."""
        
        with self.tracer.start_span(span_name) as span:
            for metric_name, metric_values in self.metrics.items():
                if metric_values:
                    latest_value = metric_values[-1]["value"]
                    span.set_attribute(f"metric.{metric_name}", latest_value)

# Usage
collector = MetricsCollector(tracer)
collector.record_metric("api_calls", 1, {"endpoint": "/users"})
collector.export_metrics_to_span("metrics-export")
```

---

## Best Practices

### 1. Custom Instrumentors
- Extend BaseInstrumentor for custom frameworks
- Implement proper cleanup in uninstrument method
- Use conditional logic for performance-critical paths

### 2. Advanced Span Management
- Propagate context across thread boundaries
- Use custom attributes for business logic
- Implement proper span lifecycle management

### 3. Performance Optimization
- Batch spans for high-volume operations
- Implement memory-aware span management
- Use sampling for production workloads

### 4. Integration Patterns
- Integrate with your application framework
- Collect custom metrics and business data
- Implement proper error handling and recovery

---

This guide covers advanced usage patterns for the HoneyHive SDK. For basic patterns, refer to the Basic Usage Patterns guide.
