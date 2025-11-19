====================================
Advanced Configuration Guide
====================================

.. meta::
   :description: Comprehensive guide to advanced HoneyHive SDK configuration patterns using Pydantic models
   :keywords: advanced configuration, Pydantic models, multi-instance, environment variables

Overview
========

This tutorial covers advanced configuration patterns for the HoneyHive SDK, including multi-instance setups, environment-based configuration, and production deployment strategies.

.. contents:: Table of Contents
   :local:
   :depth: 3

Prerequisites
=============

- Completed the :doc:`01-setup-first-tracer` tutorial
- Understanding of Python environment variables
- Familiarity with configuration management concepts

What You'll Learn
=================

By the end of this tutorial, you'll understand:

1. **Advanced Configuration Patterns**: Complex configuration scenarios
2. **Multi-Instance Architecture**: Running multiple tracers simultaneously  
3. **Environment-Based Configuration**: Different configs for dev/staging/prod
4. **Production Best Practices**: Secure, scalable configuration strategies
5. **Configuration Validation**: Type safety and error handling

Configuration Patterns
======================

Basic Configuration Review
--------------------------

The HoneyHive SDK supports three configuration approaches:

.. tabs::

   .. tab:: Modern Pydantic (Recommended)

      .. code-block:: python

         from honeyhive import HoneyHiveTracer
         from honeyhive.config.models import TracerConfig
         
         config = TracerConfig(
             api_key="hh_1234567890abcdef",
             project="my-project",
             verbose=True
         )
         tracer = HoneyHiveTracer(config=config)

   .. tab:: Traditional Parameters

      .. code-block:: python

         from honeyhive import HoneyHiveTracer
         
         tracer = HoneyHiveTracer(
             api_key="hh_1234567890abcdef",
             project="my-project",
             verbose=True
         )

   .. tab:: Mixed Approach

      .. code-block:: python

         from honeyhive.config.models import TracerConfig
         
         config = TracerConfig(api_key="hh_key", project="my-project")
         tracer = HoneyHiveTracer(config=config, verbose=True)

Advanced Configuration Patterns
===============================

1. Environment-Based Configuration
----------------------------------

**Scenario**: Different configurations for development, staging, and production environments.

**Implementation**:

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer
   from honeyhive.config.models import TracerConfig
   
   def create_tracer_for_environment() -> HoneyHiveTracer:
       """Create tracer based on current environment."""
       
       environment = os.getenv("ENVIRONMENT", "development")
       
       if environment == "production":
           config = TracerConfig(
               api_key=os.getenv("HH_PROD_API_KEY"),
               project="production-llm-app",
               source="production",
               verbose=False,  # Minimal logging in prod
               disable_http_tracing=True,  # Reduce overhead
               cache_enabled=True,
               cache_max_size=5000
           )
       elif environment == "staging":
           config = TracerConfig(
               api_key=os.getenv("HH_STAGING_API_KEY"),
               project="staging-llm-app",
               source="staging",
               verbose=True,
               disable_http_tracing=False,
               cache_enabled=True,
               cache_max_size=2000
           )
       else:  # development
           config = TracerConfig(
               api_key=os.getenv("HH_DEV_API_KEY"),
               project="dev-llm-app",
               source="development",
               verbose=True,
               disable_http_tracing=False,
               test_mode=True,  # Don't send data to backend in dev
               cache_enabled=False  # Disable caching for testing
           )
       
       return HoneyHiveTracer(config=config)
   
   # Usage
   tracer = create_tracer_for_environment()

**Environment Variables Setup**:

.. code-block:: bash

   # Development
   export ENVIRONMENT="development"
   export HH_DEV_API_KEY="hh_dev_1234567890abcdef"
   
   # Staging
   export ENVIRONMENT="staging"
   export HH_STAGING_API_KEY="hh_staging_1234567890abcdef"
   
   # Production
   export ENVIRONMENT="production"
   export HH_PROD_API_KEY="hh_prod_1234567890abcdef"

2. Multi-Instance Configuration
-------------------------------

**Scenario**: Running multiple tracers for different services or workflows.

**Implementation**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from honeyhive.config.models import TracerConfig
   from typing import Dict
   
   class MultiTracerManager:
       """Manages multiple HoneyHive tracer instances."""
       
       def __init__(self):
           self.tracers: Dict[str, HoneyHiveTracer] = {}
           self._initialize_tracers()
       
       def _initialize_tracers(self):
           """Initialize tracers for different services."""
           
           # Data Pipeline Tracer
           self.tracers["data_pipeline"] = HoneyHiveTracer(
               config=TracerConfig(
                   api_key=os.getenv("HH_DATA_API_KEY"),
                   project="data-pipeline",
                   source="etl-service",
                   verbose=False,
                   cache_enabled=True,
                   cache_max_size=10000
               )
           )
           
           # LLM Inference Tracer
           self.tracers["llm_inference"] = HoneyHiveTracer(
               config=TracerConfig(
                   api_key=os.getenv("HH_INFERENCE_API_KEY"),
                   project="llm-inference",
                   source="inference-service",
                   verbose=True,
                   disable_http_tracing=False,
                   cache_enabled=True,
                   cache_max_size=5000
               )
           )
           
           # Evaluation Tracer
           self.tracers["evaluation"] = HoneyHiveTracer(
               config=TracerConfig(
                   api_key=os.getenv("HH_EVAL_API_KEY"),
                   project="model-evaluation",
                   source="evaluation-service",
                   verbose=True,
                   test_mode=False
               )
           )
       
       def get_tracer(self, service: str) -> HoneyHiveTracer:
           """Get tracer for specific service."""
           if service not in self.tracers:
               raise ValueError(f"Unknown service: {service}")
           return self.tracers[service]
       
       def trace_data_pipeline(self, func):
           """Decorator for data pipeline functions."""
           return self.tracers["data_pipeline"].trace(func)
       
       def trace_llm_inference(self, func):
           """Decorator for LLM inference functions."""
           return self.tracers["llm_inference"].trace(func)
       
       def trace_evaluation(self, func):
           """Decorator for evaluation functions."""
           return self.tracers["evaluation"].trace(func)
   
   # Global tracer manager
   tracer_manager = MultiTracerManager()
   
   # Usage examples
   @tracer_manager.trace_data_pipeline
   def process_raw_data(data):
       """Process raw data through ETL pipeline."""
       # Data processing logic
       return processed_data
   
   @tracer_manager.trace_llm_inference
   def generate_response(prompt):
       """Generate LLM response."""
       # LLM inference logic
       return response
   
   @tracer_manager.trace_evaluation
   def evaluate_model_performance(model, dataset):
       """Evaluate model performance."""
       # Evaluation logic
       return metrics

3. Session-Based Configuration
------------------------------

**Scenario**: Different session configurations for various user interactions.

**Implementation**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from honeyhive.config.models import TracerConfig, SessionConfig
   from typing import Optional, Dict, Any
   
   class SessionAwareTracer:
       """Tracer with dynamic session configuration."""
       
       def __init__(self, base_config: TracerConfig):
           self.base_tracer = HoneyHiveTracer(config=base_config)
       
      def create_user_session(
          self,
          user_id: str,
          session_type: str = "chat",
          user_metadata: Optional[Dict[str, Any]] = None
      ) -> HoneyHiveTracer:
          """Create tracer with user-specific session."""
          
          # session_name goes in TracerConfig, not SessionConfig
          tracer_config = self.base_tracer.config.model_copy(update={
              "session_name": f"{session_type}-{user_id}"
          })
          
          # SessionConfig only has: session_id, inputs, link_carrier
          session_config = SessionConfig(
              inputs={
                  "user_id": user_id,
                  "session_type": session_type,
                  "timestamp": datetime.now().isoformat(),
                  **(user_metadata or {})
              }
          )
          
          return HoneyHiveTracer(
              config=tracer_config,
              session_config=session_config
          )
       
      def create_batch_session(
          self,
          batch_id: str,
          batch_size: int
      ) -> HoneyHiveTracer:
          """Create tracer for batch processing."""
          
          # Update tracer config with session_name
          tracer_config = self.base_tracer.config.model_copy(update={
              "session_name": f"batch-{batch_id}"
          })
          
          # SessionConfig only has: session_id, inputs, link_carrier  
          session_config = SessionConfig(
              inputs={
                  "batch_id": batch_id,
                  "batch_size": batch_size,
                  "processing_type": "batch"
              }
          )
          
          return HoneyHiveTracer(
              config=tracer_config,
              session_config=session_config
          )
   
   # Usage
   base_config = TracerConfig(
       api_key="hh_1234567890abcdef",
       project="chat-application",
       source="production"
   )
   
   session_tracer = SessionAwareTracer(base_config)
   
   # Create user-specific tracer
   user_tracer = session_tracer.create_user_session(
       user_id="user_123",
       session_type="support_chat",
       metadata={"priority": "high", "department": "technical"}
   )
   
   @user_tracer.trace
   def handle_user_query(query: str):
       """Handle user query with session context."""
       # Query handling logic
       return response

4. Configuration Validation and Error Handling
----------------------------------------------

**Scenario**: Robust configuration with validation and graceful error handling.

**Implementation**:

.. code-block:: python

   from honeyhive.config.models import TracerConfig
   from pydantic import ValidationError
   import logging
   
   logger = logging.getLogger(__name__)
   
   def create_validated_tracer(
       api_key: str,
       project: str,
       **kwargs
   ) -> Optional[HoneyHiveTracer]:
       """Create tracer with comprehensive validation."""
       
       try:
           # Attempt to create configuration
           config = TracerConfig(
               api_key=api_key,
               project=project,
               **kwargs
           )
           
           # Validate API key format
           if not api_key.startswith("hh_"):
               logger.warning("API key doesn't follow expected format (hh_*)")
           
           # Create tracer
           tracer = HoneyHiveTracer(config=config)
           
           # Test tracer initialization
           if hasattr(tracer, 'test_connection'):
               if not tracer.test_connection():
                   logger.warning("Tracer connection test failed")
           
           logger.info(f"Successfully created tracer for project: {project}")
           return tracer
           
       except ValidationError as e:
           logger.error(f"Configuration validation failed: {e}")
           
           # Create fallback tracer with minimal config
           try:
               fallback_config = TracerConfig(
                   api_key=api_key,
                   project=project,
                   test_mode=True,  # Safe fallback
                   verbose=False
               )
               logger.info("Created fallback tracer in test mode")
               return HoneyHiveTracer(config=fallback_config)
           except Exception as fallback_error:
               logger.error(f"Fallback tracer creation failed: {fallback_error}")
               return None
       
       except Exception as e:
           logger.error(f"Unexpected error creating tracer: {e}")
           return None
   
   # Usage with error handling
   tracer = create_validated_tracer(
       api_key="hh_1234567890abcdef",
       project="my-project",
       cache_max_size=-100,  # Invalid value - will be handled gracefully
       server_url="invalid-url"  # Invalid URL - will use default
   )
   
   if tracer:
       @tracer.trace
       def my_function():
           return "Hello, World!"
   else:
       logger.error("Failed to create tracer - running without tracing")
       
       def my_function():
           return "Hello, World!"

Production Configuration Strategies
===================================

1. Docker Environment Configuration
-----------------------------------

**Dockerfile**:

.. code-block:: dockerfile

   FROM python:3.11-slim
   
   # Install dependencies
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   # Copy application
   COPY . /app
   WORKDIR /app
   
   # Set environment variables with defaults
   ENV ENVIRONMENT=production
   ENV HH_VERBOSE=false
   ENV HH_CACHE_ENABLED=true
   ENV HH_CACHE_MAX_SIZE=5000
   
   CMD ["python", "app.py"]

**docker-compose.yml**:

.. code-block:: yaml

   version: '3.8'
   services:
     app:
       build: .
       environment:
         - ENVIRONMENT=production
         - HH_API_KEY=${HH_PROD_API_KEY}
         - HH_PROJECT=production-app
         - HH_SOURCE=docker-compose
         - HH_VERBOSE=false
         - HH_CACHE_ENABLED=true
       env_file:
         - .env.production

**Application Code**:

.. code-block:: python

   from honeyhive.config.models import TracerConfig
   from honeyhive import HoneyHiveTracer
   
   # Configuration loaded from environment
   config = TracerConfig()  # Automatically loads from HH_* env vars
   tracer = HoneyHiveTracer(config=config)

2. Kubernetes Configuration
---------------------------

**ConfigMap**:

.. code-block:: yaml

   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: honeyhive-config
   data:
     HH_PROJECT: "k8s-production-app"
     HH_SOURCE: "kubernetes"
     HH_VERBOSE: "false"
     HH_CACHE_ENABLED: "true"
     HH_CACHE_MAX_SIZE: "10000"

**Secret**:

.. code-block:: yaml

   apiVersion: v1
   kind: Secret
   metadata:
     name: honeyhive-secrets
   type: Opaque
   data:
     HH_API_KEY: <base64-encoded-api-key>

**Deployment**:

.. code-block:: yaml

   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: my-app
   spec:
     template:
       spec:
         containers:
         - name: app
           image: my-app:latest
           envFrom:
           - configMapRef:
               name: honeyhive-config
           - secretRef:
               name: honeyhive-secrets

3. AWS Lambda Configuration
---------------------------

**Lambda Environment Variables**:

.. code-block:: python

   import json
   import os
   from honeyhive import HoneyHiveTracer
   from honeyhive.config.models import TracerConfig
   
   # Initialize tracer once (outside handler for reuse)
   config = TracerConfig(
       api_key=os.environ["HH_API_KEY"],
       project=os.environ.get("HH_PROJECT", "lambda-app"),
       source="aws-lambda",
       verbose=os.environ.get("HH_VERBOSE", "false").lower() == "true",
       cache_enabled=False,  # Lambda is stateless
       disable_batch=True   # Immediate export for short-lived functions
   )
   tracer = HoneyHiveTracer(config=config)
   
   @tracer.trace
   def lambda_handler(event, context):
       """AWS Lambda handler with tracing."""
       
       # Your Lambda logic here
       result = process_event(event)
       
       return {
           'statusCode': 200,
           'body': json.dumps(result)
       }
   
   @tracer.trace
   def process_event(event):
       """Process the Lambda event."""
       # Processing logic
       return {"processed": True}

Configuration Best Practices
============================

1. Security Best Practices
--------------------------

**✅ DO:**

- Store API keys in environment variables or secure secret management systems
- Use different API keys for different environments
- Rotate API keys regularly
- Use ``test_mode=True`` in development to avoid sending data

**❌ DON'T:**

- Hardcode API keys in source code
- Commit API keys to version control
- Use production API keys in development/testing
- Log API keys in application logs

**Example Secure Configuration**:

.. code-block:: python

   import os
   from honeyhive.config.models import TracerConfig
   
   def create_secure_config():
       """Create configuration with security best practices."""
       
       # Validate API key is present
       api_key = os.getenv("HH_API_KEY")
       if not api_key:
           raise ValueError("HH_API_KEY environment variable is required")
       
       # Validate API key format
       if not api_key.startswith("hh_"):
           raise ValueError("Invalid API key format")
       
       # Create configuration
       config = TracerConfig(
           api_key=api_key,
           project=os.getenv("HH_PROJECT", "default-project"),
           source=os.getenv("HH_SOURCE", "application"),
           test_mode=os.getenv("ENVIRONMENT") != "production"
       )
       
       return config

2. Performance Best Practices
-----------------------------

**Production Configuration**:

.. code-block:: python

   # High-performance production configuration
   production_config = TracerConfig(
       api_key=os.getenv("HH_API_KEY"),
       project="production-app",
       source="production",
       verbose=False,                    # Reduce logging overhead
       disable_http_tracing=True,        # Reduce HTTP tracing overhead
       cache_enabled=True,               # Enable caching
       cache_max_size=10000,             # Large cache for high throughput
       cache_ttl=3600,                   # 1 hour cache TTL
       disable_batch=False               # Use batching for efficiency
   )

**Development Configuration**:

.. code-block:: python

   # Development configuration with debugging
   development_config = TracerConfig(
       api_key=os.getenv("HH_DEV_API_KEY"),
       project="dev-app",
       source="development",
       verbose=True,                     # Enable verbose logging
       test_mode=True,                   # Don't send data to backend
       disable_http_tracing=False,       # Enable HTTP tracing for debugging
       cache_enabled=False,              # Disable caching for testing
       disable_batch=True                # Immediate export for debugging
   )

3. Monitoring and Observability
-------------------------------

**Configuration with Monitoring**:

.. code-block:: python

   import logging
   from honeyhive.config.models import TracerConfig
   from honeyhive import HoneyHiveTracer
   
   # Set up logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)
   
   class MonitoredTracer:
       """Tracer wrapper with monitoring capabilities."""
       
       def __init__(self, config: TracerConfig):
           self.config = config
           self.tracer = HoneyHiveTracer(config=config)
           self._setup_monitoring()
       
       def _setup_monitoring(self):
           """Set up monitoring for tracer operations."""
           
           # Log configuration (without sensitive data)
           logger.info(f"Initialized tracer for project: {self.config.project}")
           logger.info(f"Source: {self.config.source}")
           logger.info(f"Verbose mode: {self.config.verbose}")
           logger.info(f"Test mode: {self.config.test_mode}")
           
           # Set up health checks
           if hasattr(self.tracer, 'health_check'):
               try:
                   health_status = self.tracer.health_check()
                   logger.info(f"Tracer health check: {health_status}")
               except Exception as e:
                   logger.warning(f"Tracer health check failed: {e}")
       
       def trace(self, func):
           """Trace function with monitoring."""
           
           def wrapper(*args, **kwargs):
               try:
                   return self.tracer.trace(func)(*args, **kwargs)
               except Exception as e:
                   logger.error(f"Tracing error in {func.__name__}: {e}")
                   # Continue execution without tracing
                   return func(*args, **kwargs)
           
           return wrapper

Troubleshooting
===============

Common Configuration Issues
---------------------------

**Issue 1: API Key Validation Errors**

.. code-block:: python

   # Problem: Invalid API key format
   config = TracerConfig(api_key="invalid_key")  # Missing 'hh_' prefix
   
   # Solution: Validate API key format
   api_key = "hh_1234567890abcdef"
   if not api_key.startswith("hh_"):
       raise ValueError("API key must start with 'hh_'")
   
   config = TracerConfig(api_key=api_key)

**Issue 2: Environment Variable Not Loading**

.. code-block:: python

   # Problem: Environment variables not being loaded
   config = TracerConfig()  # Expected to load from HH_* env vars
   
   # Solution: Verify environment variables are set
   import os
   
   required_vars = ["HH_API_KEY", "HH_PROJECT"]
   for var in required_vars:
       if not os.getenv(var):
           raise ValueError(f"Required environment variable {var} is not set")
   
   config = TracerConfig()

**Issue 3: Configuration Conflicts**

.. code-block:: python

   # Problem: Mixed configuration with conflicts
   config = TracerConfig(verbose=False)
   tracer = HoneyHiveTracer(config=config, verbose=True)  # Which takes precedence?
   
   # Solution: Understand precedence order
   # 1. Individual parameters (highest)
   # 2. Config object values
   # 3. Environment variables
   # 4. Default values (lowest)
   
   # In this case, verbose=True (individual parameter) wins

Next Steps
==========

Now that you understand advanced configuration patterns:

1. **Implement Environment-Based Config**: Set up different configurations for your environments
2. **Try Multi-Instance Setup**: Experiment with multiple tracers for different services
3. **Add Configuration Validation**: Implement robust error handling in your applications
4. **Review Security Practices**: Ensure your API keys and configurations are secure

**Related Documentation:**

- :doc:`../reference/configuration/hybrid-config-approach` - Complete configuration reference
- :doc:`../reference/api/config-models` - Configuration models API
- :doc:`../reference/api/tracer-architecture` - Tracer architecture details
- :doc:`../how-to/migration-compatibility/migration-guide` - Migration guide with multi-instance examples
