Advanced Setup and Configuration
=================================

.. note::
   **Tutorial Goal**: Master advanced HoneyHive configurations for complex production scenarios including multi-environment setups, custom instrumentors, and enterprise features.

This tutorial covers advanced setup scenarios that go beyond basic installation, designed for production deployments and complex architectures.

What You'll Learn
-----------------

- Multi-environment configuration strategies
- Custom instrumentor development
- Advanced tracing patterns for microservices
- Performance optimization techniques
- Enterprise security configurations
- Custom evaluation pipelines

Prerequisites
-------------

- Complete all basic tutorials (:doc:`01-quick-start` through :doc:`05-trace-enrichment`)
- Familiarity with OpenTelemetry concepts
- Production deployment experience
- Understanding of your application architecture

Multi-Environment Configuration
--------------------------------

**Problem**: You need different HoneyHive configurations for development, staging, and production environments.

**Solution**: Environment-based configuration with inheritance and overrides.

**Step 1: Create Configuration Classes**

.. code-block:: python

   # config/honeyhive_config.py
   from dataclasses import dataclass
   from typing import Optional, List
   import os
   
   @dataclass
   class HoneyHiveConfig:
       """Base configuration for HoneyHive."""
       api_key: str
       project: str
       source: str = "production"
       test_mode: bool = False
       batch_size: int = 100
       flush_interval: float = 5.0
       timeout: float = 30.0
       instrumentors: Optional[List] = None
       
       @classmethod
       def from_environment(cls, env: str = None) -> "HoneyHiveConfig":
           """Create config from environment variables."""
           env = env or os.getenv("ENVIRONMENT", "production")
           
           if env == "development":
               return DevelopmentConfig()
           elif env == "staging":
               return StagingConfig()
           elif env == "production":
               return ProductionConfig()
           else:
               raise ValueError(f"Unknown environment: {env}")
   
   @dataclass
   class DevelopmentConfig(HoneyHiveConfig):
       """Development environment configuration."""
       api_key: str = os.getenv("HH_API_KEY_DEV", "")
       project: str = "myapp-dev"
       source: str = "development"
       test_mode: bool = True
       batch_size: int = 10  # Smaller batches for faster feedback
       flush_interval: float = 1.0  # More frequent flushing
       timeout: float = 10.0  # Shorter timeout for faster failures
   
   @dataclass
   class StagingConfig(HoneyHiveConfig):
       """Staging environment configuration."""
       api_key: str = os.getenv("HH_API_KEY_STAGING", "")
       project: str = "myapp-staging"
       source: str = "staging"
       test_mode: bool = False
       batch_size: int = 50
       flush_interval: float = 3.0
       timeout: float = 20.0
   
   @dataclass
   class ProductionConfig(HoneyHiveConfig):
       """Production environment configuration."""
       api_key: str = os.getenv("HH_API_KEY_PROD", "")
       project: str = "myapp-production"
       source: str = "production"
       test_mode: bool = False
       batch_size: int = 200  # Larger batches for efficiency
       flush_interval: float = 10.0  # Less frequent flushing
       timeout: float = 60.0  # Longer timeout for stability

**Step 2: Initialize with Environment Configuration**

.. code-block:: python

   # main.py
   from honeyhive import HoneyHiveTracer
   from config.honeyhive_config import HoneyHiveConfig
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   def initialize_tracing() -> HoneyHiveTracer:
       """Initialize HoneyHive tracing based on environment."""
       
       config = HoneyHiveConfig.from_environment()
       
       # Add instrumentors based on environment
       instrumentors = []
       if not config.test_mode:
           instrumentors.append(OpenAIInstrumentor())
       
       tracer = HoneyHiveTracer.init(
           api_key=config.api_key,           source=config.source,
           test_mode=config.test_mode,
           instrumentors=instrumentors
       )
       
       print(f"HoneyHive initialized for {config.source} environment")
       return tracer
   
   # Global tracer instance
   tracer = initialize_tracing()

**Step 3: Environment-Specific Docker Configuration**

.. code-block:: dockerfile

   # Dockerfile
   FROM python:3.11-slim
   
   # Install dependencies
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   # Copy application
   COPY . /app
   WORKDIR /app
   
   # Default to production, override with docker run
   ENV ENVIRONMENT=production
   
   CMD ["python", "main.py"]

.. code-block:: yaml

   # docker-compose.yml
   version: '3.8'
   services:
     app-dev:
       build: .
       environment:
         - ENVIRONMENT=development
         - HH_API_KEY_DEV=${HH_API_KEY_DEV}
       volumes:
         - .:/app  # Live code reloading for development
     
     app-staging:
       build: .
       environment:
         - ENVIRONMENT=staging
         - HH_API_KEY_STAGING=${HH_API_KEY_STAGING}
     
     app-prod:
       build: .
       environment:
         - ENVIRONMENT=production
         - HH_API_KEY_PROD=${HH_API_KEY_PROD}

Custom Instrumentor Development
--------------------------------

**Problem**: You're using an LLM provider that doesn't have an existing instrumentor.

**Solution**: Build a custom instrumentor following OpenTelemetry patterns.

**Step 1: Create Base Instrumentor Structure**

.. code-block:: python

   # instrumentors/custom_llm_instrumentor.py
   from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
   from opentelemetry.instrumentation.utils import unwrap
   from opentelemetry import trace
   from typing import Collection
   import functools
   import time
   
   class CustomLLMInstrumentor(BaseInstrumentor):
       """Instrumentor for Custom LLM Provider."""
       
       def instrumentation_dependencies(self) -> Collection[str]:
           """Return list of packages this instrumentor depends on."""
           return ["custom-llm-sdk>=1.0.0"]
       
       def _instrument(self, **kwargs):
           """Apply instrumentation to the custom LLM SDK."""
           tracer_provider = kwargs.get("tracer_provider")
           tracer = trace.get_tracer(__name__, tracer_provider=tracer_provider)
           
           # Import the LLM SDK modules to instrument
           try:
               import custom_llm_sdk
           except ImportError:
               return
           
           # Wrap the completion method
           _wrap_completion_create(custom_llm_sdk, tracer)
           _wrap_chat_create(custom_llm_sdk, tracer)
           
       def _uninstrument(self, **kwargs):
           """Remove instrumentation from the custom LLM SDK."""
           try:
               import custom_llm_sdk
               unwrap(custom_llm_sdk.Completion, "create")
               unwrap(custom_llm_sdk.Chat, "create")
           except ImportError:
               pass
   
   def _wrap_completion_create(sdk_module, tracer):
       """Wrap the completion.create method."""
       original_create = sdk_module.Completion.create
       
       @functools.wraps(original_create)
       def wrapped_create(*args, **kwargs):
           with tracer.start_as_current_span("custom_llm.completion") as span:
               # Extract parameters
               model = kwargs.get("model", "unknown")
               max_tokens = kwargs.get("max_tokens", 0)
               prompt = args[0] if args else kwargs.get("prompt", "")
               
               # Set span attributes
               span.set_attribute("llm.provider", "custom_llm")
               span.set_attribute("llm.model", model)
               span.set_attribute("llm.max_tokens", max_tokens)
               span.set_attribute("llm.prompt_length", len(str(prompt)))
               
               start_time = time.time()
               
               try:
                   # Make the actual API call
                   response = original_create(*args, **kwargs)
                   
                   # Extract response information
                   completion_text = getattr(response, "text", "")
                   tokens_used = getattr(response, "tokens_used", 0)
                   
                   # Set response attributes
                   span.set_attribute("llm.completion_length", len(completion_text))
                   span.set_attribute("llm.tokens_used", tokens_used)
                   span.set_attribute("llm.success", True)
                   
                   return response
                   
               except Exception as e:
                   span.set_attribute("llm.success", False)
                   span.set_attribute("llm.error", str(e))
                   span.record_exception(e)
                   raise
               
               finally:
                   duration = time.time() - start_time
                   span.set_attribute("llm.duration", duration)
       
       sdk_module.Completion.create = wrapped_create

**Step 2: Advanced Instrumentor with Context Extraction**

.. code-block:: python

   # instrumentors/advanced_custom_instrumentor.py
   from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
   from opentelemetry import trace, baggage
   from opentelemetry.semconv.trace import SpanAttributes
   import json
   import hashlib
   
   class AdvancedCustomLLMInstrumentor(BaseInstrumentor):
       """Advanced instrumentor with context extraction and custom attributes."""
       
       def __init__(self, capture_content: bool = True, capture_usage: bool = True):
           super().__init__()
           self.capture_content = capture_content
           self.capture_usage = capture_usage
       
       def _instrument(self, **kwargs):
           tracer_provider = kwargs.get("tracer_provider")
           tracer = trace.get_tracer(__name__, tracer_provider=tracer_provider)
           
           try:
               import custom_llm_sdk
               self._wrap_with_advanced_tracing(custom_llm_sdk, tracer)
           except ImportError:
               pass
       
       def _wrap_with_advanced_tracing(self, sdk_module, tracer):
           """Apply advanced tracing with context extraction."""
           original_create = sdk_module.Chat.create
           
           @functools.wraps(original_create)
           def wrapped_create(*args, **kwargs):
               # Extract operation name from context
               operation_name = baggage.get_baggage("operation_name", "custom_llm.chat")
               
               with tracer.start_as_current_span(operation_name) as span:
                   # Extract comprehensive parameters
                   model = kwargs.get("model", "unknown")
                   messages = kwargs.get("messages", [])
                   temperature = kwargs.get("temperature", 1.0)
                   max_tokens = kwargs.get("max_tokens", 0)
                   
                   # Calculate input characteristics
                   total_input_length = sum(len(msg.get("content", "")) for msg in messages)
                   message_count = len(messages)
                   
                   # Set OpenTelemetry semantic conventions
                   span.set_attribute(SpanAttributes.LLM_VENDOR, "custom_llm")
                   span.set_attribute(SpanAttributes.LLM_REQUEST_MODEL, model)
                   span.set_attribute(SpanAttributes.LLM_REQUEST_MAX_TOKENS, max_tokens)
                   span.set_attribute(SpanAttributes.LLM_REQUEST_TEMPERATURE, temperature)
                   
                   # Custom attributes
                   span.set_attribute("llm.input.message_count", message_count)
                   span.set_attribute("llm.input.total_length", total_input_length)
                   
                   # Capture content if enabled
                   if self.capture_content:
                       span.set_attribute("llm.input.messages", json.dumps(messages))
                   
                   # Create content hash for deduplication
                   content_hash = hashlib.md5(
                       json.dumps(messages, sort_keys=True).encode()
                   ).hexdigest()
                   span.set_attribute("llm.input.content_hash", content_hash)
                   
                   try:
                       response = original_create(*args, **kwargs)
                       
                       # Extract response details
                       response_content = getattr(response, "content", "")
                       finish_reason = getattr(response, "finish_reason", "unknown")
                       
                       # Usage information
                       if self.capture_usage and hasattr(response, "usage"):
                           usage = response.usage
                           span.set_attribute("llm.usage.input_tokens", usage.input_tokens)
                           span.set_attribute("llm.usage.output_tokens", usage.output_tokens)
                           span.set_attribute("llm.usage.total_tokens", usage.total_tokens)
                       
                       # Response attributes
                       span.set_attribute("llm.response.length", len(response_content))
                       span.set_attribute("llm.response.finish_reason", finish_reason)
                       
                       if self.capture_content:
                           span.set_attribute("llm.response.content", response_content)
                       
                       span.set_status(trace.Status(trace.StatusCode.OK))
                       return response
                       
                   except Exception as e:
                       span.set_status(
                           trace.Status(trace.StatusCode.ERROR, str(e))
                       )
                       span.record_exception(e)
                       raise
           
           sdk_module.Chat.create = wrapped_create

**Step 3: Use Custom Instrumentor with HoneyHive**

.. code-block:: python

   # main.py
   from honeyhive import HoneyHiveTracer
   from instrumentors.advanced_custom_instrumentor import AdvancedCustomLLMInstrumentor
   
   # Initialize with custom instrumentor
   custom_instrumentor = AdvancedCustomLLMInstrumentor(
       capture_content=True,
       capture_usage=True
   )
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[custom_instrumentor]
   )
   
   # Now your custom LLM calls will be automatically traced
   import custom_llm_sdk
   
   client = custom_llm_sdk.Client()
   response = client.chat.create(
       model="custom-model-v1",
       messages=[{"role": "user", "content": "Hello!"}]
   )

Microservices Tracing Architecture
----------------------------------

**Problem**: You have a microservices architecture and need distributed tracing across services.

**Solution**: Context propagation and service-specific tracing configuration.

**Step 1: Service Base Class with Tracing**

.. code-block:: python

   # services/base_service.py
   from honeyhive import HoneyHiveTracer, trace
   from opentelemetry import trace as otel_trace
   from opentelemetry.propagate import inject, extract
   from typing import Dict, Any
   import json
   
   class BaseService:
       """Base class for microservices with HoneyHive tracing."""
       
       def __init__(self, service_name: str, version: str = "1.0.0"):
           self.service_name = service_name
           self.version = version
           self.tracer = self._initialize_tracer()
       
       def _initialize_tracer(self) -> HoneyHiveTracer:
           """Initialize service-specific tracer."""
           return HoneyHiveTracer.init(
               api_key=os.getenv("HH_API_KEY"),               source=os.getenv("ENVIRONMENT", "production"),
               session_name=f"{self.service_name}-{self.version}"
           )
       
       @trace(tracer=lambda self: self.tracer)
       def call_service(self, service_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
           """Make an HTTP call to another service with trace context propagation."""
           
           # Prepare headers for context propagation
           headers = {"Content-Type": "application/json"}
           inject(headers)  # Inject trace context into headers
           
           # Add service metadata
           current_span = otel_trace.get_current_span()
           current_span.set_attribute("service.name", self.service_name)
           current_span.set_attribute("service.version", self.version)
           current_span.set_attribute("target.service_url", service_url)
           current_span.set_attribute("request.payload_size", len(json.dumps(payload)))
           
           try:
               response = requests.post(
                   service_url,
                   json=payload,
                   headers=headers,
                   timeout=30
               )
               response.raise_for_status()
               
               result = response.json()
               current_span.set_attribute("response.status_code", response.status_code)
               current_span.set_attribute("response.payload_size", len(json.dumps(result)))
               
               return result
               
           except requests.exceptions.RequestException as e:
               current_span.set_attribute("error.type", type(e).__name__)
               current_span.set_attribute("error.message", str(e))
               raise
       
       def extract_trace_context(self, headers: Dict[str, str]) -> None:
           """Extract trace context from incoming request headers."""
           # This should be called at the beginning of request handlers
           extract(headers)

**Step 2: Service-Specific Implementation**

.. code-block:: python

   # services/llm_service.py
   from services.base_service import BaseService
   from honeyhive import trace, enrich_span
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   class LLMService(BaseService):
       """Service responsible for LLM operations."""
       
       def __init__(self):
           super().__init__("llm-service", "2.1.0")
           
           # Add LLM-specific instrumentor
           self.tracer.add_instrumentor(OpenAIInstrumentor())
           self.openai_client = openai.OpenAI()
       
       @trace(tracer=lambda self: self.tracer, event_type="llm_completion")
       def generate_completion(self, prompt: str, user_id: str = None) -> Dict[str, Any]:
           """Generate LLM completion with full observability."""
           
           enrich_span({
               "service.operation": "generate_completion",
               "user.id": user_id,
               "prompt.length": len(prompt),
               "prompt.type": self._classify_prompt(prompt)
           })
           
           # Get user context from user service
           user_context = {}
           if user_id:
               user_context = self.call_service(
                   "http://user-service/api/context",
                   {"user_id": user_id}
               )
           
           # Prepare context-aware prompt
           if user_context:
               enhanced_prompt = f"""
               User Context: {user_context.get('preferences', {})}
               Request: {prompt}
               """
           else:
               enhanced_prompt = prompt
           
           response = self.openai_client.chat.completions.create(
               model="gpt-4",
               messages=[{"role": "user", "content": enhanced_prompt}],
               max_tokens=500
           )
           
           completion = response.choices[0].message.content
           
           enrich_span({
               "completion.length": len(completion),
               "completion.tokens": response.usage.total_tokens,
               "user.context_available": bool(user_context)
           })
           
           return {
               "completion": completion,
               "tokens_used": response.usage.total_tokens,
               "model": "gpt-4",
               "user_context_applied": bool(user_context)
           }
       
       def _classify_prompt(self, prompt: str) -> str:
           """Classify the type of prompt for better analytics."""
           if "question" in prompt.lower() or "?" in prompt:
               return "question"
           elif "summarize" in prompt.lower() or "summary" in prompt.lower():
               return "summarization"
           elif "translate" in prompt.lower():
               return "translation"
           return "general"

**Step 3: API Gateway with Distributed Tracing**

.. code-block:: python

   # services/api_gateway.py
   from flask import Flask, request, jsonify
   from services.base_service import BaseService
   from services.llm_service import LLMService
   from honeyhive import trace, enrich_span
   
   app = Flask(__name__)
   
   class APIGateway(BaseService):
       """API Gateway with distributed tracing."""
       
       def __init__(self):
           super().__init__("api-gateway", "1.0.0")
           self.llm_service = LLMService()
       
       @trace(tracer=lambda self: self.tracer, event_type="api_request")
       def handle_completion_request(self, request_data: dict, headers: dict) -> dict:
           """Handle completion request with full tracing."""
           
           # Extract trace context from incoming request
           self.extract_trace_context(headers)
           
           # Extract request information
           prompt = request_data.get("prompt", "")
           user_id = request_data.get("user_id")
           
           enrich_span({
               "api.endpoint": "/completion",
               "api.method": "POST",
               "api.user_id": user_id,
               "api.request_size": len(str(request_data))
           })
           
           try:
               # Call LLM service (this will create child spans)
               result = self.llm_service.generate_completion(prompt, user_id)
               
               enrich_span({
                   "api.success": True,
                   "api.response_size": len(str(result))
               })
               
               return {
                   "status": "success",
                   "data": result
               }
               
           except Exception as e:
               enrich_span({
                   "api.success": False,
                   "api.error": str(e)
               })
               raise
   
   # Flask routes
   gateway = APIGateway()
   
   @app.route("/completion", methods=["POST"])
   def completion():
       try:
           result = gateway.handle_completion_request(
               request.json,
               dict(request.headers)
           )
           return jsonify(result)
       except Exception as e:
           return jsonify({"error": str(e)}), 500

Performance Optimization Techniques
------------------------------------

**Problem**: You need to optimize HoneyHive performance for high-throughput applications.

**Solution**: Advanced configuration and sampling strategies.

**Step 1: Intelligent Sampling**

.. code-block:: python

   # performance/sampling.py
   from honeyhive import HoneyHiveTracer, trace
   import random
   import time
   from typing import Callable
   
   class IntelligentSampler:
       """Intelligent sampling based on various factors."""
       
       def __init__(self, base_rate: float = 0.1):
           self.base_rate = base_rate
           self.error_rate = 1.0  # Always sample errors
           self.slow_request_rate = 1.0  # Always sample slow requests
           self.slow_threshold = 2.0  # seconds
           
       def should_sample(self, context: dict) -> bool:
           """Determine if a trace should be sampled."""
           
           # Always sample errors
           if context.get("has_error", False):
               return True
           
           # Always sample slow requests
           if context.get("duration", 0) > self.slow_threshold:
               return True
           
           # Sample premium users more frequently
           if context.get("user_tier") == "premium":
               return random.random() < self.base_rate * 5  # 5x sampling rate
           
           # Sample based on endpoint importance
           endpoint = context.get("endpoint", "")
           if endpoint in ["/payment", "/checkout", "/signup"]:
               return random.random() < self.base_rate * 3  # 3x sampling rate
           
           # Base sampling rate for everything else
           return random.random() < self.base_rate
   
   # Global sampler instance
   sampler = IntelligentSampler(base_rate=0.05)  # 5% base sampling
   
   def conditional_trace(tracer: HoneyHiveTracer, **span_attributes):
       """Decorator that applies intelligent sampling."""
       def decorator(func: Callable):
           def wrapper(*args, **kwargs):
               start_time = time.time()
               
               # Collect context for sampling decision
               context = {
                   "endpoint": kwargs.get("endpoint", func.__name__),
                   "user_tier": kwargs.get("user_tier", "standard"),
                   "has_error": False,
                   "duration": 0
               }
               
               try:
                   result = func(*args, **kwargs)
                   context["duration"] = time.time() - start_time
                   
                   # Apply sampling decision
                   if sampler.should_sample(context):
                       # Create trace retroactively if sampled
                       with tracer.trace(func.__name__, **span_attributes) as span:
                           for key, value in context.items():
                               span.set_attribute(f"sampling.{key}", value)
                           span.set_attribute("sampling.sampled", True)
                   
                   return result
                   
               except Exception as e:
                   context["has_error"] = True
                   context["duration"] = time.time() - start_time
                   
                   # Always trace errors
                   with tracer.trace(func.__name__, **span_attributes) as span:
                       for key, value in context.items():
                           span.set_attribute(f"sampling.{key}", value)
                       span.set_attribute("sampling.forced_by_error", True)
                       span.record_exception(e)
                   
                   raise
           
           return wrapper
       return decorator

**Step 2: Batch Processing Optimization**

.. code-block:: python

   # performance/batch_processing.py
   from honeyhive import HoneyHiveTracer, trace, enrich_span
   import asyncio
   from concurrent.futures import ThreadPoolExecutor
   from typing import List, Dict, Any
   
   class OptimizedBatchProcessor:
       """Optimized batch processing with efficient tracing."""
       
       def __init__(self, tracer: HoneyHiveTracer, max_workers: int = 10):
           self.tracer = tracer
           self.max_workers = max_workers
           
       @trace(tracer=lambda self: self.tracer, event_type=EventType.tool)
       def process_batch_efficiently(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
           """Process a batch of items with optimized tracing."""
           
           enrich_span({
               "batch.size": len(items),
               "batch.max_workers": self.max_workers,
               "batch.processing_strategy": "thread_pool"
           })
           
           # Group items by similarity to optimize processing
           grouped_items = self._group_similar_items(items)
           
           enrich_span({
               "batch.groups": len(grouped_items),
               "batch.avg_group_size": len(items) / len(grouped_items) if grouped_items else 0
           })
           
           results = []
           
           with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
               # Submit groups for processing
               futures = []
               for group_id, group_items in grouped_items.items():
                   future = executor.submit(self._process_group, group_id, group_items)
                   futures.append(future)
               
               # Collect results
               for future in futures:
                   group_results = future.result()
                   results.extend(group_results)
           
           enrich_span({
               "batch.results_count": len(results),
               "batch.success_rate": len(results) / len(items) if items else 0
           })
           
           return results
       
       def _group_similar_items(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
           """Group similar items together for efficient processing."""
           groups = {}
           
           for item in items:
               # Group by item type or characteristics
               group_key = item.get("type", "default")
               if group_key not in groups:
                   groups[group_key] = []
               groups[group_key].append(item)
           
           return groups
       
       def _process_group(self, group_id: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
           """Process a group of similar items."""
           
           # Create a single span for the entire group instead of individual spans
           with self.tracer.trace(f"process_group_{group_id}") as span:
               span.set_attribute("group.id", group_id)
               span.set_attribute("group.size", len(items))
               
               results = []
               errors = 0
               
               for item in items:
                   try:
                       result = self._process_single_item(item)
                       results.append(result)
                   except Exception as e:
                       errors += 1
                       # Log error but don't create individual spans
                       span.add_event(f"item_error", {"error": str(e), "item_id": item.get("id")})
               
               span.set_attribute("group.success_count", len(results))
               span.set_attribute("group.error_count", errors)
               span.set_attribute("group.success_rate", len(results) / len(items))
               
               return results
       
       def _process_single_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
           """Process a single item (without creating individual spans)."""
           # Actual processing logic here
           return {"processed": True, "original": item}

Custom Evaluation Pipelines
---------------------------

**Problem**: You need sophisticated evaluation pipelines for your specific use case.

**Solution**: Build custom evaluation architecture with HoneyHive integration.

**Step 1: Advanced Evaluation Framework**

.. code-block:: python

   # evaluation/advanced_framework.py
   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.evaluation import BaseEvaluator
   from typing import List, Dict, Any, Optional
   import asyncio
   from concurrent.futures import ThreadPoolExecutor
   
   class AdvancedEvaluationPipeline:
       """Advanced evaluation pipeline with parallel processing and caching."""
       
       def __init__(self, tracer: HoneyHiveTracer):
           self.tracer = tracer
           self.evaluators: List[BaseEvaluator] = []
           self.cache: Dict[str, Any] = {}
           self.executor = ThreadPoolExecutor(max_workers=5)
       
       def add_evaluator(self, evaluator: BaseEvaluator, weight: float = 1.0):
           """Add an evaluator to the pipeline with optional weighting."""
           self.evaluators.append({
               "evaluator": evaluator,
               "weight": weight,
               "name": evaluator.__class__.__name__
           })
       
       @trace(tracer=lambda self: self.tracer, event_type="evaluation_pipeline")
       async def evaluate_batch(self, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
           """Evaluate a batch of samples using all evaluators."""
           
           enrich_span({
               "evaluation.sample_count": len(samples),
               "evaluation.evaluator_count": len(self.evaluators),
               "evaluation.mode": "batch_parallel"
           })
           
           # Run evaluations in parallel
           evaluation_tasks = []
           
           for evaluator_config in self.evaluators:
               task = self._evaluate_with_evaluator(evaluator_config, samples)
               evaluation_tasks.append(task)
           
           # Wait for all evaluations to complete
           evaluation_results = await asyncio.gather(*evaluation_tasks, return_exceptions=True)
           
           # Aggregate results
           aggregated_results = self._aggregate_evaluation_results(
               evaluation_results, samples
           )
           
           enrich_span({
               "evaluation.completed_evaluators": len([r for r in evaluation_results if not isinstance(r, Exception)]),
               "evaluation.failed_evaluators": len([r for r in evaluation_results if isinstance(r, Exception)]),
               "evaluation.overall_score": aggregated_results.get("overall_score", 0)
           })
           
           return aggregated_results
       
       async def _evaluate_with_evaluator(self, evaluator_config: Dict, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
           """Evaluate samples with a specific evaluator."""
           
           evaluator = evaluator_config["evaluator"]
           evaluator_name = evaluator_config["name"]
           
           with self.tracer.trace(f"evaluator_{evaluator_name}") as span:
               span.set_attribute("evaluator.name", evaluator_name)
               span.set_attribute("evaluator.weight", evaluator_config["weight"])
               span.set_attribute("evaluator.sample_count", len(samples))
               
               results = []
               cache_hits = 0
               
               for sample in samples:
                   # Check cache first
                   cache_key = self._generate_cache_key(evaluator_name, sample)
                   
                   if cache_key in self.cache:
                       results.append(self.cache[cache_key])
                       cache_hits += 1
                   else:
                       # Run evaluation
                       try:
                           result = evaluator.evaluate(
                               sample["input"],
                               sample["output"],
                               sample.get("context", {})
                           )
                           self.cache[cache_key] = result
                           results.append(result)
                       except Exception as e:
                           span.add_event("evaluation_error", {"error": str(e), "sample_id": sample.get("id")})
                           results.append({"score": 0.0, "error": str(e)})
               
               span.set_attribute("evaluator.cache_hits", cache_hits)
               span.set_attribute("evaluator.cache_hit_rate", cache_hits / len(samples))
               
               return {
                   "evaluator": evaluator_name,
                   "weight": evaluator_config["weight"],
                   "results": results
               }
       
       def _generate_cache_key(self, evaluator_name: str, sample: Dict[str, Any]) -> str:
           """Generate a cache key for an evaluation."""
           import hashlib
           content = f"{evaluator_name}_{sample['input']}_{sample['output']}"
           return hashlib.md5(content.encode()).hexdigest()
       
       def _aggregate_evaluation_results(self, evaluation_results: List, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
           """Aggregate results from multiple evaluators."""
           
           # Filter out exceptions
           valid_results = [r for r in evaluation_results if not isinstance(r, Exception)]
           
           if not valid_results:
               return {"overall_score": 0.0, "error": "No valid evaluation results"}
           
           # Calculate weighted average
           total_weight = sum(r["weight"] for r in valid_results)
           weighted_scores = []
           
           for i, sample in enumerate(samples):
               sample_scores = []
               sample_weights = []
               
               for result in valid_results:
                   if i < len(result["results"]) and "score" in result["results"][i]:
                       sample_scores.append(result["results"][i]["score"])
                       sample_weights.append(result["weight"])
               
               if sample_scores:
                   weighted_score = sum(
                       score * weight for score, weight in zip(sample_scores, sample_weights)
                   ) / sum(sample_weights)
                   weighted_scores.append(weighted_score)
           
           overall_score = sum(weighted_scores) / len(weighted_scores) if weighted_scores else 0.0
           
           return {
               "overall_score": overall_score,
               "sample_scores": weighted_scores,
               "evaluator_results": valid_results,
               "sample_count": len(samples)
           }

Enterprise Security Configuration
----------------------------------

**Problem**: You need enterprise-grade security for HoneyHive in a corporate environment.

**Solution**: Implement comprehensive security measures and audit logging.

**Step 1: Secure Configuration Management**

.. code-block:: python

   # security/secure_config.py
   import os
   import boto3
   import json
   from cryptography.fernet import Fernet
   from honeyhive import HoneyHiveTracer
   from typing import Dict, Any, Optional
   
   class SecureHoneyHiveConfig:
       """Enterprise security configuration for HoneyHive."""
       
       def __init__(self, encryption_key: Optional[str] = None):
           self.encryption_key = encryption_key or os.getenv("HH_ENCRYPTION_KEY")
           self.cipher = Fernet(self.encryption_key.encode()) if self.encryption_key else None
           
       def get_secure_tracer(self, environment: str = "production") -> HoneyHiveTracer:
           """Get a securely configured tracer."""
           
           config = self._load_secure_config(environment)
           
           # Validate configuration
           self._validate_config(config)
           
           # Initialize with security settings
           tracer = HoneyHiveTracer.init(
               api_key=config["api_key"],               source=environment,
               base_url=config.get("base_url", "https://api.honeyhive.ai"),
               timeout=config.get("timeout", 30),
               # Security-specific settings
               verify_ssl=True,
               max_retries=3,
               backoff_factor=1.0
           )
           
           # Add security audit logging
           self._setup_audit_logging(tracer, environment)
           
           return tracer
       
       def _load_secure_config(self, environment: str) -> Dict[str, Any]:
           """Load configuration from secure storage."""
           
           # Try AWS Secrets Manager first
           try:
               return self._load_from_secrets_manager(environment)
           except Exception:
               pass
           
           # Fall back to encrypted environment variables
           try:
               return self._load_from_encrypted_env(environment)
           except Exception:
               pass
           
           # Final fallback to regular environment variables (with warnings)
           self._log_security_warning("Using unencrypted environment variables")
           return self._load_from_env(environment)
       
       def _load_from_secrets_manager(self, environment: str) -> Dict[str, Any]:
           """Load from AWS Secrets Manager."""
           client = boto3.client('secretsmanager')
           secret_name = f"honeyhive/{environment}"
           
           response = client.get_secret_value(SecretId=secret_name)
           return json.loads(response['SecretString'])
       
       def _load_from_encrypted_env(self, environment: str) -> Dict[str, Any]:
           """Load from encrypted environment variables."""
           if not self.cipher:
               raise ValueError("Encryption key required for encrypted config")
           
           encrypted_config = os.getenv(f"HH_CONFIG_{environment.upper()}")
           if not encrypted_config:
               raise ValueError(f"No encrypted config found for {environment}")
           
           decrypted_data = self.cipher.decrypt(encrypted_config.encode())
           return json.loads(decrypted_data.decode())
       
       def _load_from_env(self, environment: str) -> Dict[str, Any]:
           """Load from regular environment variables."""
           return {
               "api_key": os.getenv(f"HH_API_KEY_{environment.upper()}"),
               "project": os.getenv(f"HH_PROJECT_{environment.upper()}"),
               "base_url": os.getenv(f"HH_BASE_URL_{environment.upper()}"),
               "timeout": int(os.getenv(f"HH_TIMEOUT_{environment.upper()}", "30"))
           }
       
       def _validate_config(self, config: Dict[str, Any]) -> None:
           """Validate configuration for security compliance."""
           
           if not config.get("api_key"):
               raise ValueError("API key is required")
           
           if not config["api_key"].startswith("hh_"):
               raise ValueError("Invalid API key format")
           
           if len(config["api_key"]) < 32:
               raise ValueError("API key appears to be too short")
           
           # Validate base URL
           base_url = config.get("base_url", "")
           if base_url and not base_url.startswith("https://"):
               raise ValueError("Base URL must use HTTPS")
       
       def _setup_audit_logging(self, tracer: HoneyHiveTracer, environment: str) -> None:
           """Set up security audit logging."""
           
           # This would integrate with your enterprise logging system
           audit_logger = self._get_audit_logger()
           
           audit_logger.info(
               "HoneyHive tracer initialized",
               extra={
                   "environment": environment,
                   "project": tracer.project,
                   "user": os.getenv("USER", "unknown"),
                   "host": os.getenv("HOSTNAME", "unknown"),
                   "security_level": "enterprise"
               }
           )
       
       def _get_audit_logger(self):
           """Get enterprise audit logger."""
           import logging
           return logging.getLogger("honeyhive.security.audit")
       
       def _log_security_warning(self, message: str) -> None:
           """Log security warnings."""
           audit_logger = self._get_audit_logger()
           audit_logger.warning(f"SECURITY WARNING: {message}")

This advanced setup tutorial provides comprehensive guidance for complex production scenarios. The content covers real-world challenges that enterprise users face when implementing LLM observability at scale.

<function_calls>
<invoke name="todo_write">
<parameter name="merge">true
