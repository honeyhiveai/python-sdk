Production Deployment Guide
===========================

.. note::
   **Production-ready deployment**
   
   This guide walks you through deploying HoneyHive in production environments with proper security, monitoring, and scalability considerations.

Overview
--------

Deploying HoneyHive in production requires careful consideration of:

- **Security**: API key management and data protection
- **Performance**: Minimizing overhead and optimizing throughput
- **Reliability**: Error handling and failover strategies
- **Monitoring**: Observing the observability system itself
- **Scalability**: Handling high-volume applications

This guide provides step-by-step instructions for each consideration.

Security Configuration
----------------------

API Key Management
~~~~~~~~~~~~~~~~~~

**Never hardcode API keys in production code.**

**Option 1: Environment Variables (Recommended)**

.. code-block:: bash

   # .env file (not committed to version control)
   HH_API_KEY=hh_prod_your_production_key_here
   HH_SOURCE=production

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer
   
   # Secure initialization
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       source=os.getenv("HH_SOURCE")
   )

**Option 2: AWS Secrets Manager**

.. code-block:: python

   import boto3
   import json
   from honeyhive import HoneyHiveTracer
   
   def get_honeyhive_config():
       """Retrieve HoneyHive configuration from AWS Secrets Manager."""
       client = boto3.client('secretsmanager', region_name='us-east-1')
       
       try:
           response = client.get_secret_value(SecretId='prod/honeyhive/config')
           config = json.loads(response['SecretString'])
           
           return {
               'api_key': config['api_key'],
               'project': config['project'],
               'source': config.get('source', 'production')
           }
       except Exception as e:
           # Handle gracefully - don't crash the application
           print(f"Warning: Could not retrieve HoneyHive config: {e}")
           return None
   
   # Initialize with secrets
   config = get_honeyhive_config()
   if config:
       tracer = HoneyHiveTracer.init(**config)
   else:
       tracer = None  # Graceful degradation

**Option 3: HashiCorp Vault**

.. code-block:: python

   import hvac
   from honeyhive import HoneyHiveTracer
   
   def get_vault_config():
       """Retrieve configuration from HashiCorp Vault."""
       client = hvac.Client(url=os.getenv('VAULT_URL'))
       client.token = os.getenv('VAULT_TOKEN')
       
       try:
           response = client.secrets.kv.v2.read_secret_version(
               path='honeyhive/production'
           )
           return response['data']['data']
       except Exception as e:
           print(f"Warning: Vault access failed: {e}")
           return None

Network Security
~~~~~~~~~~~~~~~~

**Configure TLS and network security**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       base_url="https://api.honeyhive.ai",  # Always use HTTPS
       timeout=30.0,  # Reasonable timeout
       # Configure for corporate environments
       verify_ssl=True,  # Verify SSL certificates
   )

**Firewall and Proxy Configuration**:

.. code-block:: python

   import os
   
   # Configure proxy if needed
   os.environ['HTTPS_PROXY'] = 'https://corporate-proxy:8080'
   os.environ['HTTP_PROXY'] = 'http://corporate-proxy:8080'
   
   # Or configure in code
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       # Custom HTTP configuration if needed
   )

Performance Optimization
------------------------

Minimize Overhead
~~~~~~~~~~~~~~~~~

**1. Selective Tracing**

Don't trace everything - focus on business-critical operations:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   import random
   
   from honeyhive.models import EventType
   
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY")
       
   )
   
   # Trace critical business operations
   @trace(tracer=tracer, event_type=EventType.session)
   def process_payment(user_id: str, amount: float):
       # Always trace financial operations
       pass
   
   # Sample high-frequency operations
   @trace(tracer=tracer, event_type=EventType.tool)
   def handle_api_request(request):
       # Only trace 1% of API requests
       if random.random() < 0.01:
           # Detailed tracing
           pass

**2. Async Processing**

Use async patterns for high-throughput applications:

.. code-block:: python

   import asyncio
   from honeyhive import HoneyHiveTracer, trace
   
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY")
       
   )
   
   @trace(tracer=tracer)
   async def process_user_request(user_id: str):
       """Async processing with automatic tracing."""
       # Non-blocking I/O operations
       user_data = await fetch_user_data(user_id)
       result = await process_data(user_data)
       return result

**3. Batch Operations**

Group operations to reduce overhead:

.. code-block:: python

   @trace(tracer=tracer, event_type=EventType.tool)
   def process_batch(items: list):
       """Process multiple items in one traced operation."""
       results = []
       
       with tracer.trace("batch_validation") as span:
           valid_items = [item for item in items if validate_item(item)]
           span.set_attribute("batch.valid_count", len(valid_items))
       
       with tracer.trace("batch_processing") as span:
           results = [process_item(item) for item in valid_items]
           span.set_attribute("batch.processed_count", len(results))
       
       return results

Error Handling & Reliability
----------------------------

Graceful Degradation
~~~~~~~~~~~~~~~~~~~~

**Never let tracing crash your application**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   import logging
   
   logger = logging.getLogger(__name__)
   
   def create_safe_tracer():
       """Create tracer with error handling."""
       try:
           tracer = HoneyHiveTracer.init(
               api_key=os.getenv("HH_API_KEY"),               source=os.getenv("HH_SOURCE", "production"),
               timeout=10.0  # Don't wait too long
           )
           logger.info("HoneyHive tracer initialized successfully")
           return tracer
       except Exception as e:
           logger.warning(f"HoneyHive initialization failed: {e}")
           return None
   
   # Global tracer with safe initialization
   TRACER = create_safe_tracer()
   
   def safe_trace(func):
       """Decorator that only traces if tracer is available."""
       if TRACER:
           return trace(tracer=TRACER)(func)
       else:
           return func  # No tracing, but function still works
   
   @safe_trace
   def critical_business_function():
       """This function works whether tracing is available or not."""
       # Your business logic here
       return "success"

Retry Logic
~~~~~~~~~~~

**Handle transient network issues**:

.. code-block:: python

   import time
   import random
   from honeyhive import HoneyHiveTracer
   
   def create_resilient_tracer(max_retries=3):
       """Create tracer with retry logic."""
       for attempt in range(max_retries):
           try:
               tracer = HoneyHiveTracer.init(
                   api_key=os.getenv("HH_API_KEY"),                   timeout=5.0 + attempt * 2  # Increasing timeout
               )
               return tracer
           except Exception as e:
               if attempt == max_retries - 1:
                   logger.error(f"Failed to initialize tracer after {max_retries} attempts")
                   return None
               
               # Exponential backoff
               delay = (2 ** attempt) + random.uniform(0, 1)
               time.sleep(delay)
               logger.warning(f"Tracer init attempt {attempt + 1} failed, retrying in {delay:.1f}s")

Circuit Breaker Pattern
~~~~~~~~~~~~~~~~~~~~~~~

**Prevent cascading failures**:

.. code-block:: python

   import time
   from enum import Enum
   
   class CircuitState(Enum):
       CLOSED = "closed"      # Normal operation
       OPEN = "open"         # Failing, don't try
       HALF_OPEN = "half_open"  # Testing if recovered
   
   class HoneyHiveCircuitBreaker:
       def __init__(self, failure_threshold=5, recovery_timeout=60):
           self.failure_threshold = failure_threshold
           self.recovery_timeout = recovery_timeout
           self.failure_count = 0
           self.last_failure_time = None
           self.state = CircuitState.CLOSED
           self.tracer = None
       
       def get_tracer(self):
           """Get tracer with circuit breaker protection."""
           if self.state == CircuitState.OPEN:
               if time.time() - self.last_failure_time > self.recovery_timeout:
                   self.state = CircuitState.HALF_OPEN
               else:
                   return None  # Circuit is open, don't try
           
           if self.state in [CircuitState.CLOSED, CircuitState.HALF_OPEN]:
               try:
                   if not self.tracer:
                       self.tracer = HoneyHiveTracer.init(
                           api_key=os.getenv("HH_API_KEY")                       )
                   
                   # Reset on success
                   if self.state == CircuitState.HALF_OPEN:
                       self.state = CircuitState.CLOSED
                       self.failure_count = 0
                   
                   return self.tracer
               
               except Exception as e:
                   self.failure_count += 1
                   self.last_failure_time = time.time()
                   
                   if self.failure_count >= self.failure_threshold:
                       self.state = CircuitState.OPEN
                       logger.warning("HoneyHive circuit breaker opened")
                   
                   return None
   
   # Global circuit breaker
   honeyhive_cb = HoneyHiveCircuitBreaker()
   
   def get_safe_tracer():
       return honeyhive_cb.get_tracer()

Monitoring Production Health
----------------------------

Application Metrics
~~~~~~~~~~~~~~~~~~~

**Monitor your own tracing performance**:

.. code-block:: python

   import time
   import logging
   from collections import defaultdict
   from honeyhive import HoneyHiveTracer, trace
   
   class TracingMetrics:
       def __init__(self):
           self.trace_count = 0
           self.trace_errors = 0
           self.trace_latency = []
           self.last_reset = time.time()
       
       def record_trace(self, duration: float, success: bool):
           self.trace_count += 1
           self.trace_latency.append(duration)
           if not success:
               self.trace_errors += 1
       
       def get_stats(self):
           if not self.trace_latency:
               return {"trace_count": 0, "error_rate": 0, "avg_latency": 0}
           
           return {
               "trace_count": self.trace_count,
               "error_rate": self.trace_errors / self.trace_count,
               "avg_latency": sum(self.trace_latency) / len(self.trace_latency),
               "p95_latency": sorted(self.trace_latency)[int(0.95 * len(self.trace_latency))]
           }
   
   # Global metrics
   tracing_metrics = TracingMetrics()
   
   def monitored_trace(tracer, event_type=None):
       """Trace decorator with monitoring."""
       def decorator(func):
           def wrapper(*args, **kwargs):
               start_time = time.time()
               success = True
               
               try:
                   if tracer:
                       return trace(tracer=tracer, event_type=event_type)(func)(*args, **kwargs)
                   else:
                       return func(*args, **kwargs)
               except Exception as e:
                   success = False
                   raise
               finally:
                   duration = time.time() - start_time
                   tracing_metrics.record_trace(duration, success)
           
           return wrapper
       return decorator

Health Check Endpoints
~~~~~~~~~~~~~~~~~~~~~~

**Add health checks for your tracing infrastructure**:

.. code-block:: python

   from flask import Flask, jsonify
   from honeyhive import HoneyHiveTracer
   
   app = Flask(__name__)
   
   @app.route('/health/tracing')
   def tracing_health():
       """Health check for tracing infrastructure."""
       try:
           # Test tracer connectivity
           test_tracer = HoneyHiveTracer.init(
               api_key=os.getenv("HH_API_KEY"),
               timeout=5.0
           )
           
           # Quick connectivity test
           with test_tracer.trace("health_check_test") as span:
               span.set_attribute("test.timestamp", time.time())
           
           stats = tracing_metrics.get_stats()
           
           return jsonify({
               "status": "healthy",
               "tracing": {
                   "connected": True,
                   "metrics": stats
               }
           }), 200
           
       except Exception as e:
           return jsonify({
               "status": "unhealthy",
               "tracing": {
                   "connected": False,
                   "error": str(e)
               }
           }), 503

Logging Integration
~~~~~~~~~~~~~~~~~~~

**Integrate with your existing logging infrastructure**:

.. code-block:: python

   import logging
   import json
   from honeyhive import HoneyHiveTracer, trace, enrich_span
   
   # Configure structured logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s %(levelname)s %(name)s %(message)s'
   )
   
   logger = logging.getLogger(__name__)
   
   class HoneyHiveLogHandler(logging.Handler):
       """Custom log handler that adds trace context."""
       
       def __init__(self, tracer):
           super().__init__()
           self.tracer = tracer
       
       def emit(self, record):
           # Add log entry to current span if available
           if hasattr(self.tracer, 'current_span') and self.tracer.current_span:
               enrich_span({
                   f"log.{record.levelname.lower()}": record.getMessage(),
                   "log.timestamp": record.created
               })
   
   # Set up integrated logging
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY")
       
   )
   
   # Add HoneyHive handler to logger
   honeyhive_handler = HoneyHiveLogHandler(tracer)
   logger.addHandler(honeyhive_handler)

Deployment Strategies
---------------------

Blue-Green Deployment
~~~~~~~~~~~~~~~~~~~~~

**Safely deploy tracing changes**:

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer
   
   def create_environment_tracer():
       """Create tracer based on deployment environment."""
       env = os.getenv("DEPLOYMENT_ENV", "blue")
       
       # Different projects for blue/green deployments
       project_mapping = {
           "blue": "production-app",
           "green": "production-app-green",
           "staging": "staging-app"
       }
       
       return HoneyHiveTracer.init(
           api_key=os.getenv("HH_API_KEY"), "production-app"),
           source=f"production-{env}"
       )

Canary Deployment
~~~~~~~~~~~~~~~~~

**Gradual rollout of tracing changes**:

.. code-block:: python

   import random
   from honeyhive import HoneyHiveTracer
   
   def create_canary_tracer():
       """Create tracer with canary deployment logic."""
       canary_percentage = float(os.getenv("CANARY_PERCENTAGE", "0"))
       
       if random.random() < canary_percentage / 100:
           # Canary version
           return HoneyHiveTracer.init(
               api_key=os.getenv("HH_API_KEY"),
               source="production-canary"
           )
       else:
           # Stable version
           return HoneyHiveTracer.init(
               api_key=os.getenv("HH_API_KEY"),
               source="production-stable"
           )

Container Deployment
--------------------

Docker Configuration
~~~~~~~~~~~~~~~~~~~~

**Dockerfile for production deployment**:

.. code-block:: dockerfile

   FROM python:3.11-slim
   
   # Create non-root user
   RUN groupadd -r appuser && useradd -r -g appuser appuser
   
   # Set working directory
   WORKDIR /app
   
   # Install dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application code
   COPY . .
   
   # Switch to non-root user
   USER appuser
   
   # Environment variables (will be overridden by orchestrator)
   ENV HH_API_KEY=""
   ENV HH_SOURCE="production"
   
   # Health check
   HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
     CMD python -c "import requests; requests.get('http://localhost:8000/health/tracing')"
   
   # Start application
   CMD ["python", "app.py"]

**docker-compose.yml for production**:

.. code-block:: yaml

   version: '3.8'
   
   services:
     app:
       build: .
       environment:
         - HH_API_KEY=${HH_API_KEY}
         - HH_SOURCE=${HH_SOURCE:-production}
       ports:
         - "8000:8000"
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/health/tracing"]
         interval: 30s
         timeout: 10s
         retries: 3
       deploy:
         resources:
           limits:
             memory: 512M
             cpus: '0.5'

Kubernetes Deployment
~~~~~~~~~~~~~~~~~~~~~

**ConfigMap for configuration**:

.. code-block:: yaml

   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: honeyhive-config
   data:
     HH_SOURCE: "production"
     HH_BASE_URL: "https://api.honeyhive.ai"

**Secret for API key**:

.. code-block:: yaml

   apiVersion: v1
   kind: Secret
   metadata:
     name: honeyhive-secret
   type: Opaque
   data:
     HH_API_KEY: <base64-encoded-api-key>

**Deployment manifest**:

.. code-block:: yaml

   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: app-with-honeyhive
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: myapp
     template:
       metadata:
         labels:
           app: myapp
       spec:
         containers:
         - name: app
           image: myapp:latest
           envFrom:
           - configMapRef:
               name: honeyhive-config
           env:
           - name: HH_API_KEY
             valueFrom:
               secretKeyRef:
                 name: honeyhive-secret
                 key: HH_API_KEY
           livenessProbe:
             httpGet:
               path: /health/tracing
               port: 8000
             initialDelaySeconds: 30
             periodSeconds: 30
           readinessProbe:
             httpGet:
               path: /health/tracing
               port: 8000
             initialDelaySeconds: 5
             periodSeconds: 10

Production Checklist
--------------------

Before Going Live
~~~~~~~~~~~~~~~~~

**Security:**
- [ ] API keys stored in secure secret management
- [ ] HTTPS-only communication configured
- [ ] Network access properly restricted
- [ ] No sensitive data in trace attributes

**Performance:**
- [ ] Tracing overhead measured and acceptable
- [ ] Selective tracing strategy implemented
- [ ] Batch processing for high-volume operations
- [ ] Circuit breaker pattern implemented

**Reliability:**
- [ ] Graceful degradation when tracing fails
- [ ] Retry logic for transient failures
- [ ] Health checks for tracing infrastructure
- [ ] Monitoring and alerting in place

**Operations:**
- [ ] Deployment strategy tested
- [ ] Rollback plan prepared
- [ ] Documentation updated
- [ ] Team trained on troubleshooting

**Compliance:**
- [ ] Data retention policies configured
- [ ] Privacy requirements met
- [ ] Audit logging enabled
- [ ] Compliance team approval obtained

Ongoing Maintenance
~~~~~~~~~~~~~~~~~~~

**Weekly:**
- Monitor tracing performance metrics
- Review error rates and patterns
- Check for new SDK updates

**Monthly:**
- Analyze tracing data for insights
- Review and optimize trace selection
- Update documentation as needed

**Quarterly:**
- Security review of configuration
- Performance optimization review
- Disaster recovery testing

**Best Practices Summary:**

1. **Security First**: Never compromise on API key security
2. **Graceful Degradation**: Tracing failures shouldn't crash your app
3. **Monitor Everything**: Monitor your monitoring system
4. **Start Simple**: Begin with basic tracing, add complexity gradually
5. **Test Thoroughly**: Test tracing in staging environments first

.. tip::
   Production observability is about balance - you want comprehensive visibility without impacting application performance or reliability. Start conservative and expand your tracing coverage based on actual operational needs.
