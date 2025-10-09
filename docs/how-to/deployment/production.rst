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

**Recommended: Environment Variables**

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

**Enterprise Secret Management:**

For production environments, use dedicated secret management services:

- **AWS Secrets Manager**: Retrieve from ``secretsmanager`` using boto3
- **HashiCorp Vault**: Use ``hvac`` client to fetch from ``kv`` store
- **Azure Key Vault**: Use ``azure-keyvault-secrets`` SDK
- **Google Secret Manager**: Use ``google-cloud-secret-manager``

All services follow the same pattern: fetch credentials at startup, handle failures gracefully, and return ``None`` if unavailable to enable graceful degradation.

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

.. note::
   **Advanced Patterns Available**
   
   For advanced resilience patterns including circuit breakers, see :doc:`advanced-production`.

Monitoring Production Health
----------------------------

Application Metrics
~~~~~~~~~~~~~~~~~~~

**Monitor your tracing performance**:

.. code-block:: python

   import time
   import logging
   
   logger = logging.getLogger(__name__)
   
   class SimpleTracingMetrics:
       """Basic tracing metrics for production monitoring."""
       
       def __init__(self):
           self.trace_count = 0
           self.trace_errors = 0
       
       def record_trace(self, success: bool):
           self.trace_count += 1
           if not success:
               self.trace_errors += 1
       
       def get_error_rate(self) -> float:
           if self.trace_count == 0:
               return 0.0
           return self.trace_errors / self.trace_count
   
   # Global metrics
   tracing_metrics = SimpleTracingMetrics()

.. note::
   For comprehensive monitoring with latency tracking, error type breakdown, and Prometheus integration, see :doc:`advanced-production`.

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

**Integrate tracing with your logging**:

.. code-block:: python

   import logging
   from honeyhive import HoneyHiveTracer, enrich_span
   
   logger = logging.getLogger(__name__)
   
   # Log important events and add to trace
   logger.info("Processing request")
   enrich_span({
       "log.message": "Processing request",
       "log.level": "INFO"
   })

Deployment Strategies
---------------------

**Standard Deployment:**

The simplest approach is a single tracer instance for your production environment:

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer
   
   # Single production tracer
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       project="production-app",
       source="production"
   )

.. note::
   **Advanced Deployment Strategies**
   
   For blue-green deployments, canary rollouts, and traffic-based routing, see :doc:`advanced-production`.

Container Deployment
--------------------

Docker Configuration
~~~~~~~~~~~~~~~~~~~~

**Key HoneyHive-specific Docker configuration**:

.. code-block:: dockerfile

   # Use Python 3.11+ for HoneyHive SDK
   FROM python:3.11-slim
   
   # Install HoneyHive SDK
   RUN pip install honeyhive>=0.1.0
   
   # HoneyHive environment variables (overridden at runtime)
   ENV HH_API_KEY=""
   ENV HH_SOURCE="production"

**docker-compose.yml** - pass HoneyHive credentials:

.. code-block:: yaml

   services:
     app:
       environment:
         - HH_API_KEY=${HH_API_KEY}
         - HH_SOURCE=production

Kubernetes Deployment
~~~~~~~~~~~~~~~~~~~~~

**Store API key in Kubernetes Secret**:

.. code-block:: bash

   kubectl create secret generic honeyhive-secret \
     --from-literal=api-key=<your-api-key>

**Reference in Deployment**:

.. code-block:: yaml

   env:
   - name: HH_API_KEY
     valueFrom:
       secretKeyRef:
         name: honeyhive-secret
         key: api-key
   - name: HH_SOURCE
     value: "production"

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
