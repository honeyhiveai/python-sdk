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

.. seealso::
   **Tracer Performance Benchmarks**
   
   HoneyHive provides comprehensive performance benchmarking capabilities. The SDK consistently achieves:
   
   - **Overhead Latency**: < 10ms tracer overhead per operation
   - **Memory Usage**: < 50MB memory overhead
   - **Network I/O**: Tracer traffic < 10% of LLM traffic
   - **Export Latency**: < 100ms average export time
   - **Trace Coverage**: 100% of requests traced
   - **Attribute Completeness**: All required span attributes captured
   
   Contact the HoneyHive team for detailed performance benchmarking reports and high-throughput validation data.

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

**The SDK provides built-in graceful degradation** - tracing failures will never crash your application.

HoneyHive automatically handles errors in tracing operations, ensuring your business logic continues uninterrupted even if the tracing infrastructure is unavailable.

**Comprehensive Error Handling:**

All SDK operations are wrapped in try-except blocks that catch and log errors without propagating them:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   import logging
   
   logger = logging.getLogger(__name__)
   
   # ✅ Tracer initialization - NEVER throws exceptions
   # Even with invalid API key, network failures, or configuration errors
   tracer = HoneyHiveTracer.init(
       api_key="invalid-key",  # Won't crash - gracefully degrades
       source=os.getenv("HH_SOURCE", "production"),
       timeout=10.0  # Configure timeout for slow networks (default: 30s)
   )
   
   # ✅ Decorator tracing - NEVER throws exceptions
   # Works even if HoneyHive API is down or unreachable
   @trace(tracer=tracer)
   def critical_business_function():
       """This function ALWAYS executes - tracing errors logged but not raised."""
       # Your business logic here - never interrupted by tracing errors
       return "success"
   
   # ✅ Manual span enrichment - NEVER throws exceptions
   # Even with invalid data types or API failures
   @trace(tracer=tracer)
   def user_request_handler(user_id, query):
       try:
           result = process_query(query)
           # Enrichment errors are caught internally
           tracer.enrich_span(metadata={"user_id": user_id})
           return result
       except Exception as e:
           # Your error handling - SDK never adds exceptions here
           logger.error(f"Business logic error: {e}")
           raise

**What Gets Caught Internally:**

1. **Network Failures**: Timeouts, connection errors, DNS failures
2. **Authentication Errors**: Invalid API keys, expired tokens
3. **Serialization Errors**: Invalid span data, encoding issues
4. **API Errors**: Rate limits, service unavailable, malformed responses
5. **Configuration Errors**: Invalid URLs, missing environment variables

.. note::
   **Timeout Configuration**
   
   The ``timeout`` parameter controls how long the SDK waits for API responses before gracefully degrading. Lower timeouts (5-10s) ensure faster degradation in network issues, while higher timeouts (30-60s) accommodate slow networks. Default is 30 seconds.

**Evidence in Production:**

.. code-block:: python

   # REAL-WORLD TEST: These ALL work without exceptions
   
   # ❌ Invalid API key → Logs warning, continues execution
   tracer1 = HoneyHiveTracer.init(api_key="invalid")
   
   # ❌ HoneyHive API down → Logs error, continues execution  
   tracer2 = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       server_url="https://nonexistent-domain.invalid"
   )
   
   # ❌ Network timeout → Logs timeout, continues execution
   tracer3 = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       timeout=0.001  # Impossibly short timeout
   )
   
   # ✅ ALL of the above initialize successfully and your code continues
   # ✅ Traced functions execute normally even with failed tracers
   # ✅ Check logs for warnings - application never crashes

Network Retries
~~~~~~~~~~~~~~~

**The SDK provides built-in network retry logic** for transient failures.

HoneyHive automatically retries failed API requests with exponential backoff, handling temporary network issues without requiring manual retry implementation.

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   # Simple initialization - retries are automatic
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       source=os.getenv("HH_SOURCE", "production")
   )
   
   # The SDK handles:
   # - Network timeouts → automatic retry with backoff
   # - Transient API errors → automatic retry with backoff
   # - Connection failures → graceful degradation after retries

.. note::
   **Built-in Retry Behavior**
   
   The SDK automatically retries failed requests up to 3 times with exponential backoff. This handles most transient network issues without requiring custom retry logic.

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
