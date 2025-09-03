Troubleshooting Common Issues
=============================

.. note::
   **Problem-solving guide**
   
   This guide helps you diagnose and fix common issues when using the HoneyHive SDK. Each problem includes symptoms, diagnosis steps, and solutions.

Quick Diagnosis
---------------

**Not seeing traces in your dashboard?**

1. :ref:`check-api-key` - Verify API key configuration
2. :ref:`check-connectivity` - Test network connectivity
3. :ref:`ssl-connectivity` - Fix SSL/TLS certificate issues
4. :ref:`check-project-config` - Verify project settings

**Import or installation errors?**

1. :ref:`installation-issues` - Fix installation problems
2. :ref:`dependency-conflicts` - Resolve dependency conflicts
3. :ref:`python-version` - Check Python version compatibility

**Tracing not working as expected?**

1. :ref:`trace-debugging` - Debug trace collection
2. :ref:`event-type-validation` - Validate event_type values  
3. :ref:`instrumentor-issues` - Fix instrumentor problems
4. **Instrumentor initialization order** - Ensure tracer is initialized before instrumentors
5. :ref:`performance-issues` - Address performance concerns

Installation & Setup Issues
---------------------------

.. _installation-issues:

Installation Problems
~~~~~~~~~~~~~~~~~~~~~

**Symptom**: ``pip install honeyhive`` fails or takes very long

**Diagnosis**:

.. code-block:: bash

   # Check Python version
   python --version
   
   # Check pip version
   pip --version
   
   # Try verbose installation
   pip install -v honeyhive

**Solutions**:

1. **Update pip and Python**:

   .. code-block:: bash

      # Update pip
      pip install --upgrade pip
      
      # Check Python version (requires 3.11+)
      python --version

2. **Use virtual environment**:

   .. code-block:: bash

      # Create virtual environment
      python -m venv honeyhive-env
      
      # Activate (Linux/Mac)
      source honeyhive-env/bin/activate
      
      # Activate (Windows)
      honeyhive-env\Scripts\activate
      
      # Install in clean environment
      pip install honeyhive

3. **Clear pip cache**:

   .. code-block:: bash

      pip cache purge
      pip install honeyhive

.. _dependency-conflicts:

Dependency Conflicts
~~~~~~~~~~~~~~~~~~~~

**Symptom**: Installation succeeds but imports fail with version conflicts

**Diagnosis**:

.. code-block:: bash

   # Check installed packages
   pip list | grep -E "(opentelemetry|honeyhive)"
   
   # Check for conflicts
   pip check

**Solutions**:

1. **Use fresh virtual environment** (recommended):

   .. code-block:: bash

      python -m venv fresh-env
      source fresh-env/bin/activate
      pip install honeyhive

2. **Upgrade conflicting packages**:

   .. code-block:: bash

      pip install --upgrade opentelemetry-api opentelemetry-sdk

3. **Use specific versions**:

   .. code-block:: bash

      pip install "opentelemetry-api>=1.20.0" "honeyhive"

.. _python-version:

Python Version Issues
~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Import errors or unexpected behavior

**Diagnosis**:

.. code-block:: python

   import sys
   print(f"Python version: {sys.version}")
   
   # Check if version is 3.11+
   if sys.version_info < (3, 11):
       print("❌ Python 3.11+ required")
   else:
       print("✅ Python version compatible")

**Solution**:

Install Python 3.11 or higher:

- **Mac**: ``brew install python@3.11``
- **Ubuntu**: ``sudo apt install python3.11``
- **Windows**: Download from `python.org <https://python.org>`_

Configuration Issues
--------------------

.. _check-api-key:

API Key Problems
~~~~~~~~~~~~~~~~

**Symptom**: Traces not appearing in dashboard, authentication errors

**Diagnosis**:

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer
   
   # Check API key
   api_key = os.getenv("HH_API_KEY") or "your-hardcoded-key"
   print(f"API Key: {api_key[:8]}..." if api_key else "❌ No API key found")
   
   # Test tracer initialization
   try:
       tracer = HoneyHiveTracer.init(api_key=api_key, project="test")
       print("✅ Tracer initialized successfully")
   except Exception as e:
       print(f"❌ Tracer initialization failed: {e}")

**Solutions**:

1. **Verify API key format**:

   .. code-block:: bash

      # API keys start with 'hh_'
      echo $HH_API_KEY | grep "^hh_"

2. **Set environment variables**:

   .. code-block:: bash

      export HH_API_KEY="hh_your_actual_key_here"
      export HH_PROJECT="your-project-name"

3. **Test with explicit values**:

   .. code-block:: python

      # Temporarily test with explicit values
      tracer = HoneyHiveTracer.init(
          api_key="hh_your_actual_key",
          project="test-project"
      )

.. _check-connectivity:

Network Connectivity
~~~~~~~~~~~~~~~~~~~~

**Symptom**: Timeouts, connection errors, no traces reaching dashboard

**Diagnosis**:

.. code-block:: python

   import requests
   
   # Test HoneyHive API connectivity
   try:
       response = requests.get("https://api.honeyhive.ai/api/v1/health", timeout=10)
       print(f"✅ API reachable: {response.status_code}")
   except requests.exceptions.RequestException as e:
       print(f"❌ API unreachable: {e}")

**Solutions**:

1. **Check firewall/proxy settings**:

   .. code-block:: bash

      # Test direct connection
      curl -I https://api.honeyhive.ai/health

2. **Configure proxy** (if needed):

   .. code-block:: python

      import os
      
      # Set proxy environment variables
      os.environ["HTTP_PROXY"] = "http://your-proxy:8080"
      os.environ["HTTPS_PROXY"] = "https://your-proxy:443"

3. **Test with increased timeout**:

   .. code-block:: python

      tracer = HoneyHiveTracer.init(
          api_key="your-key",
          project="test",
          timeout=30  # Increase timeout
      )

.. _ssl-connectivity:

SSL/TLS Certificate Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**: SSL certificate errors, HTTPS connection failures, certificate verification errors

**Common Error Messages**:
- ``ssl.SSLCertVerificationError: certificate verify failed``
- ``requests.exceptions.SSLError: HTTPSConnectionPool``
- ``SSL: CERTIFICATE_VERIFY_FAILED``

**Diagnosis**:

.. code-block:: python

   import ssl
   import requests
   
   # Test basic SSL connectivity
   try:
       response = requests.get("https://api.honeyhive.ai/api/v1/health", timeout=10)
       print(f"✅ SSL connection successful: {response.status_code}")
   except requests.exceptions.SSLError as e:
       print(f"❌ SSL Error: {e}")
   except Exception as e:
       print(f"❌ Connection Error: {e}")
   
   # Check SSL context
   context = ssl.create_default_context()
   print(f"SSL Protocol: {context.protocol}")
   print(f"Check hostname: {context.check_hostname}")
   print(f"Verify mode: {context.verify_mode}")
   
   # Check HoneyHive SSL configuration
   import os
   hh_verify_ssl = os.getenv("HH_VERIFY_SSL", "true")
   print(f"HH_VERIFY_SSL: {hh_verify_ssl}")
   if hh_verify_ssl.lower() == "false":
       print("⚠️  SSL verification is disabled via HH_VERIFY_SSL")

**CLI Validation**:

.. code-block:: bash

   # Test SSL connectivity with curl
   curl -v https://api.honeyhive.ai/health
   
   # Test with specific SSL options
   curl --tlsv1.2 https://api.honeyhive.ai/health
   
   # Check certificate details
   openssl s_client -connect api.honeyhive.ai:443 -servername api.honeyhive.ai
   
   # Check HoneyHive SSL environment variable
   echo "HH_VERIFY_SSL: ${HH_VERIFY_SSL:-true}"

**Solutions**:

1. **Update certificates and Python**:

   .. code-block:: bash

      # Update system certificates (macOS)
      /Applications/Python\ 3.x/Install\ Certificates.command
      
      # Update system certificates (Ubuntu)
      sudo apt-get update && sudo apt-get install ca-certificates
      
      # Update pip and requests
      pip install --upgrade pip requests urllib3

2. **Configure custom SSL context**:

   .. code-block:: python

      import ssl
      import requests
      from requests.adapters import HTTPAdapter
      from urllib3.poolmanager import PoolManager
      
      class SSLAdapter(HTTPAdapter):
          def init_poolmanager(self, *args, **kwargs):
              context = ssl.create_default_context()
              context.check_hostname = False
              context.verify_mode = ssl.CERT_NONE  # Only for debugging
              kwargs['ssl_context'] = context
              return super().init_poolmanager(*args, **kwargs)
      
      # Use custom SSL adapter (only for debugging)
      session = requests.Session()
      session.mount('https://', SSLAdapter())
      
      # Test connection
      response = session.get("https://api.honeyhive.ai/api/v1/health")

3. **Corporate environment SSL configuration**:

   .. code-block:: python

      import os
      import ssl
      import certifi
      
      # Option 1: Use custom certificate bundle
      os.environ['REQUESTS_CA_BUNDLE'] = '/path/to/corporate/ca-bundle.crt'
      os.environ['SSL_CERT_FILE'] = '/path/to/corporate/ca-bundle.crt'
      
      # Option 2: Add corporate certificates to certifi
      corporate_ca_path = '/path/to/corporate-ca.crt'
      certifi_ca_bundle = certifi.where()
      
      # Append corporate CA to certifi bundle
      with open(certifi_ca_bundle, 'ab') as f:
          with open(corporate_ca_path, 'rb') as corporate_ca:
              f.write(corporate_ca.read())

4. **HoneyHive tracer with custom SSL**:

   .. code-block:: python

      import requests
      from honeyhive import HoneyHiveTracer
      
      # Create session with custom SSL settings
      session = requests.Session()
      
      # For corporate environments with custom CAs
      session.verify = '/path/to/corporate/ca-bundle.crt'
      
      # Or disable SSL verification (NOT recommended for production)
      # session.verify = False
      
      # Initialize tracer with custom session
      tracer = HoneyHiveTracer.init(
          api_key="your-key",
          project="test",
          session=session  # Use custom session for all API calls
      )

5. **Environment variable configuration**:

   .. code-block:: bash

      # Set certificate bundle path
      export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
      export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
      
      # For corporate proxy with custom certificates
      export CURL_CA_BUNDLE=/path/to/corporate/ca-bundle.crt
      
      # HoneyHive-specific SSL configuration
      export HH_VERIFY_SSL=true   # Enable SSL verification (default)
      export HH_VERIFY_SSL=false  # Disable SSL verification (debugging only)

6. **Quick SSL troubleshooting with HH_VERIFY_SSL**:

   .. code-block:: bash

      # Temporarily disable SSL verification for debugging
      export HH_VERIFY_SSL=false
      python your_script.py  # Test if SSL is the issue
      
      # Re-enable SSL verification
      export HH_VERIFY_SSL=true
      
      # Or test inline
      HH_VERIFY_SSL=false python -c "
      from honeyhive import HoneyHiveTracer
      tracer = HoneyHiveTracer.init(api_key='test', project='ssl-debug')
      print('SSL verification bypassed for testing')
      "

**Security Best Practices**:

.. warning::
   **Never disable SSL verification in production!** 
   
   Disabling SSL verification (``verify=False`` or ``HH_VERIFY_SSL=false``) should only be used for debugging and testing. In production:
   
   - Always use proper certificate bundles
   - Keep certificates up to date
   - Use corporate certificate authorities when required
   - Monitor certificate expiration dates
   - Ensure ``HH_VERIFY_SSL`` is set to ``true`` or unset (defaults to ``true``)

**Testing SSL Configuration**:

.. code-block:: python

   def test_ssl_configuration():
       """Test SSL configuration with HoneyHive API."""
       import requests
       from honeyhive import HoneyHiveTracer
       
       print("🔍 Testing SSL Configuration...")
       
       # Test 1: Basic HTTPS connection
       try:
           response = requests.get("https://api.honeyhive.ai/api/v1/health", timeout=10)
           print(f"✅ HTTPS connectivity: {response.status_code}")
       except Exception as e:
           print(f"❌ HTTPS failed: {e}")
           return False
       
       # Test 2: HoneyHive tracer initialization
       try:
           tracer = HoneyHiveTracer.init(
               api_key="test-key",
               project="ssl-test"
           )
           print("✅ Tracer initialization successful")
       except Exception as e:
           print(f"❌ Tracer initialization failed: {e}")
           return False
       
       print("🎉 SSL configuration appears to be working")
       return True
   
   # Run the test
   test_ssl_configuration()

**Corporate Environment Checklist**:

1. **Check corporate firewall rules** - Ensure HTTPS traffic to ``api.honeyhive.ai`` is allowed
2. **Verify proxy configuration** - Configure HTTPS_PROXY if required  
3. **Install corporate certificates** - Add your organization's CA certificates
4. **Test with IT department** - Coordinate with network administrators for SSL issues
5. **Monitor certificate expiration** - Set up alerts for certificate renewals

.. _check-project-config:

Project Configuration
~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Traces appear in wrong project or don't appear at all

**Diagnosis**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   tracer = HoneyHiveTracer.init(api_key="your-key", project="test")
   
   print(f"Project: {tracer.project}")
   print(f"Source: {tracer.source}")
   print(f"Session ID: {tracer.session_id}")

**CLI Validation**:

.. code-block:: bash

   # List available projects
   honeyhive project list
   
   # Get project details
   honeyhive project get --name "your-project-name"
   
   # Test event creation in specific project
   honeyhive event create \
     --project "your-project-name" \
     --event-type "model" \
     --event-name "project-validation-test"

**Solutions**:

1. **Verify project name matches dashboard**:

   - Check project name in HoneyHive dashboard
   - Ensure exact spelling and case

2. **Use explicit configuration**:

   .. code-block:: python

      tracer = HoneyHiveTracer.init(
          api_key="your-key",
          project="exact-project-name",  # Must match dashboard
          source="development"           # Clear source identifier
      )

.. _event-type-validation:

Event Type Validation
~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Events rejected or not appearing due to invalid event_type values

**Valid Event Types**: Only ``"model"``, ``"tool"``, and ``"chain"`` are accepted.

**CLI Validation**:

.. code-block:: bash

   # Test valid event types
   honeyhive event create --project "test" --event-type "model" --event-name "model-test"
   honeyhive event create --project "test" --event-type "tool" --event-name "tool-test"  
   honeyhive event create --project "test" --event-type "chain" --event-name "chain-test"
   
   # Search by event type
   honeyhive event search --query "event_type:model"
   honeyhive event search --query "event_type:tool"
   honeyhive event search --query "event_type:chain"
   
   # Validate recent events have correct types
   honeyhive event search \
     --query "start_time:>$(date -d '1 hour ago' --iso-8601)" \
     --fields "event_id,event_type,event_name" \
     --limit 10

**Code Validation**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   
   tracer = HoneyHiveTracer.init(api_key="your-key", project="test")
   
   # ✅ Valid event types
   @trace(tracer=tracer, event_type=EventType.model)
   def llm_call():
       """For LLM model calls and interactions."""
       pass
   
   @trace(tracer=tracer, event_type="tool") 
   def api_call():
       """For tool/function calls and external APIs."""
       pass
   
   @trace(tracer=tracer, event_type=EventType.chain)
   def workflow():
       """For chain/workflow operations and multi-step processes.""" 
       pass
   
   # ❌ Invalid event types - these will be rejected
   # @trace(tracer=tracer, event_type=EventType.model)           # Use "model" instead
   # @trace(tracer=tracer, event_type="evaluation")    # Use "tool" instead
   # @trace(tracer=tracer, event_type="custom")        # Use appropriate valid type

Tracing Issues
--------------

.. _trace-debugging:

Traces Not Being Captured
~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Functions run but no traces appear

**Diagnosis**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   
   # Enable debug logging
   import logging
   logging.basicConfig(level=logging.DEBUG)
   
   tracer = HoneyHiveTracer.init(
       api_key="your-key",
       project="debug-test",
       verbose=True  # Enable verbose logging
   )
   
   @trace(tracer=tracer)
   def test_function():
       return "test result"
   
   # Check if trace decorator is working
   result = test_function()
   print(f"Result: {result}")

**Solutions**:

1. **Verify tracer is passed to decorator**:

   .. code-block:: python

      # ❌ Missing tracer parameter
      @trace
      def my_function():
          pass
      
      # ✅ Correct usage
      @trace(tracer=tracer)
      def my_function():
          pass

2. **Check for decorator placement**:

   .. code-block:: python

      # ❌ Wrong order
      @some_other_decorator
      @trace(tracer=tracer)
      def my_function():
          pass
      
      # ✅ Correct order (trace should be closest to function)
      @trace(tracer=tracer)
      @some_other_decorator
      def my_function():
          pass

3. **Test with simple function**:

   .. code-block:: python

      @trace(tracer=tracer)
      def simple_test():
          print("This should be traced")
          return 42
      
      simple_test()

.. _instrumentor-issues:

Instrumentor Problems
~~~~~~~~~~~~~~~~~~~~~

**Symptom**: LLM calls not being traced automatically

**Diagnosis**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   # Check if instrumentor is properly installed
   try:
       instrumentor = OpenAIInstrumentor()
       print("✅ Instrumentor available")
   except ImportError as e:
       print(f"❌ Instrumentor import failed: {e}")
   
   # Initialize with instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-key",
       project="test",
       instrumentors=[instrumentor],
       verbose=True
   )

**Solutions**:

1. **Install required instrumentor**:

   .. code-block:: bash

      # For OpenAI
      pip install openinference-instrumentation-openai
      
      # For Anthropic
      pip install openinference-instrumentation-anthropic

2. **Verify instrumentor compatibility**:

   .. code-block:: python

      # Check instrumentor version
      import openinference.instrumentation.openai
      print(f"Instrumentor version: {openinference.instrumentation.openai.__version__}")

3. **Manual instrumentor setup**:

   .. code-block:: python

      from openinference.instrumentation.openai import OpenAIInstrumentor
      
      # Manual instrumentation
      OpenAIInstrumentor().instrument()
      
      # Then initialize tracer normally
      tracer = HoneyHiveTracer.init(api_key="your-key", project="test")

Instrumentor Initialization Order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Instrumentors not working, missing LLM traces despite correct setup

**Problem**: Instrumentors initialized before tracer, causing tracing to fail

**Diagnosis**:

.. code-block:: python

   # ❌ WRONG: Instrumentor initialized before tracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from honeyhive import HoneyHiveTracer
   
   # This happens too early - tracer doesn't exist yet
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument()  # ❌ No tracer configured yet
   
   # Tracer initialized after instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-key",
       project="test"
   )

**CLI Validation**:

.. code-block:: bash

   # Test if LLM calls are being traced
   honeyhive event search \
     --query "event_type:model AND start_time:>$(date -d '10 minutes ago' --iso-8601)" \
     --limit 5
   
   # Should show recent LLM events - if empty, instrumentor may not be working

**Solutions**:

1. **Initialize tracer first, then instrumentors**:

   .. code-block:: python

      from honeyhive import HoneyHiveTracer
      from openinference.instrumentation.openai import OpenAIInstrumentor
      
      # ✅ CORRECT: Initialize tracer first
      tracer = HoneyHiveTracer.init(
          api_key="your-key",
          project="test"
      )
      
      # Then initialize instrumentor
      instrumentor = OpenAIInstrumentor()
      instrumentor.instrument()

2. **Use HoneyHive's built-in instrumentor management**:

   .. code-block:: python

      from honeyhive import HoneyHiveTracer
      from openinference.instrumentation.openai import OpenAIInstrumentor
      
      # ✅ RECOMMENDED: Let HoneyHive manage instrumentors
      tracer = HoneyHiveTracer.init(
          api_key="your-key",
          project="test",
          instrumentors=[OpenAIInstrumentor()]  # Initialized in correct order
      )

3. **Verify initialization order in modules**:

   .. code-block:: python

      # config.py - Initialize tracer first
      from honeyhive import HoneyHiveTracer
      
      tracer = HoneyHiveTracer.init(
          api_key="your-key",
          project="production"
      )
      
      # services.py - Import tracer, then set up instrumentors
      from .config import tracer
      from openinference.instrumentation.openai import OpenAIInstrumentor
      
      # Safe to instrument now that tracer exists
      OpenAIInstrumentor().instrument()

4. **Test instrumentor functionality**:

   .. code-block:: python

      import openai
      from honeyhive import HoneyHiveTracer
      from openinference.instrumentation.openai import OpenAIInstrumentor
      
      # Initialize in correct order
      tracer = HoneyHiveTracer.init(api_key="your-key", project="test")
      OpenAIInstrumentor().instrument()
      
      # Test LLM call - should create automatic traces
      client = openai.OpenAI()
      response = client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[{"role": "user", "content": "Hello!"}]
      )
      
      print("If setup is correct, this call should appear in your HoneyHive dashboard")

**Common Initialization Patterns**:

.. code-block:: python

   # Pattern 1: Application startup
   def initialize_app():
       # 1. Initialize tracer first
       tracer = HoneyHiveTracer.init(
           api_key=os.getenv("HH_API_KEY"),
           project=os.getenv("HH_PROJECT")
       )
       
       # 2. Then initialize instrumentors
       from openinference.instrumentation.openai import OpenAIInstrumentor
       OpenAIInstrumentor().instrument()
       
       return tracer
   
   # Pattern 2: Class-based initialization
   class LLMService:
       def __init__(self):
           # Initialize tracer in constructor
           self.tracer = HoneyHiveTracer.init(
               api_key="your-key",
               project="llm-service"
           )
           
           # Then set up instrumentors
           from openinference.instrumentation.openai import OpenAIInstrumentor
           OpenAIInstrumentor().instrument()

Performance Issues
------------------

.. _performance-issues:

High Latency or Overhead
~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Application becomes slow after adding tracing

**Diagnosis**:

.. code-block:: python

   import time
   from honeyhive import HoneyHiveTracer, trace
   
   tracer = HoneyHiveTracer.init(api_key="your-key", project="perf-test")
   
   # Measure overhead
   def without_tracing():
       time.sleep(0.001)  # Simulate work
   
   @trace(tracer=tracer)
   def with_tracing():
       time.sleep(0.001)  # Same work
   
   # Time both functions
   import timeit
   
   no_trace_time = timeit.timeit(without_tracing, number=100)
   trace_time = timeit.timeit(with_tracing, number=100)
   
   overhead = trace_time - no_trace_time
   print(f"Tracing overhead: {overhead:.4f}s for 100 calls")

**Solutions**:

1. **Reduce trace frequency**:

   .. code-block:: python

      import random
      
      @trace(tracer=tracer)
      def sampled_function():
          # Only trace 10% of calls
          if random.random() < 0.1:
              # Do tracing work
              pass

2. **Use async tracing for I/O operations**:

   .. code-block:: python

      @trace(tracer=tracer)
      async def async_operation():
          # Async tracing has lower overhead for I/O
          pass

3. **Optimize span creation**:

   .. code-block:: python

      # ❌ Too many spans
      @trace(tracer=tracer)
      def process_items(items):
          for item in items:
              with tracer.trace(f"process_item_{item}"):
                  process_single_item(item)
      
      # ✅ Batch processing
      @trace(tracer=tracer)
      def process_items(items):
          # Single span for batch
          results = [process_single_item(item) for item in items]
          return results

Memory Usage Issues
~~~~~~~~~~~~~~~~~~~

**Symptom**: Memory usage increases over time

**Solutions**:

1. **Check for span leaks**:

   .. code-block:: python

      # Ensure spans are properly closed
      with tracer.trace("operation") as span:
          # Work here
          pass  # Span automatically closed

2. **Limit trace data size**:

   .. code-block:: python

      @trace(tracer=tracer)
      def process_large_data(data):
          # Don't trace large objects directly
          result = expensive_operation(data)
          
          # Trace summary instead
          enrich_span({
              "data.size": len(data),
              "result.summary": summarize(result)  # Not full result
          })

Error Patterns
--------------

Common Error Messages
~~~~~~~~~~~~~~~~~~~~~

**"ModuleNotFoundError: No module named 'honeyhive'"**

.. code-block:: bash

   # Solution: Install the package
   pip install honeyhive

**"AttributeError: 'NoneType' object has no attribute 'trace'"**

.. code-block:: python

   # Problem: Tracer not initialized
   tracer = None
   
   @trace(tracer=tracer)  # ❌ tracer is None
   def my_function():
       pass
   
   # Solution: Initialize tracer first
   tracer = HoneyHiveTracer.init(api_key="key", project="project")

**"ValueError: API key is required"**

.. code-block:: python

   # Problem: Missing API key
   tracer = HoneyHiveTracer.init()  # ❌ No API key
   
   # Solution: Provide API key
   tracer = HoneyHiveTracer.init(api_key="your-key", project="project")

**"ConnectionError: Unable to connect to HoneyHive API"**

- Check internet connectivity
- Verify API endpoint (should be ``https://api.honeyhive.ai``)
- Check firewall/proxy settings

Getting More Help
-----------------

**Enable Debug Logging**:

.. code-block:: python

   import logging
   
   # Enable debug logging for HoneyHive
   logging.basicConfig(level=logging.DEBUG)
   logger = logging.getLogger("honeyhive")
   logger.setLevel(logging.DEBUG)

**Collect Diagnostic Information**:

.. code-block:: python

   import sys
   import honeyhive
   
   print("Diagnostic Information:")
   print(f"Python version: {sys.version}")
   print(f"HoneyHive version: {honeyhive.__version__}")
   print(f"Platform: {sys.platform}")
   
   # Test basic functionality
   try:
       tracer = HoneyHiveTracer.init(api_key="test", project="test")
       print("✅ Basic initialization works")
   except Exception as e:
       print(f"❌ Initialization failed: {e}")

**CLI Validation Commands**:

Use the HoneyHive CLI to validate your configuration and test connectivity:

.. code-block:: bash

   # Check CLI installation and version
   honeyhive --version
   
   # Validate API key and connectivity
   honeyhive project list
   
   # Test event creation with valid event_type
   honeyhive event create \
     --project "test-project" \
     --event-type "model" \
     --event-name "cli-validation-test" \
     --inputs '{"test": "validation"}' \
     --outputs '{"result": "success"}'
   
   # Search for recent events with valid event_type filter
   honeyhive event search \
     --project "test-project" \
     --query "event_type:model AND start_time:>$(date -d '1 hour ago' --iso-8601)" \
     --limit 5
   
   # Validate specific event types (model, tool, chain)
   honeyhive event search --query "event_type:model" --limit 1
   honeyhive event search --query "event_type:tool" --limit 1  
   honeyhive event search --query "event_type:chain" --limit 1
   
   # Check for recent errors
   honeyhive event search \
     --query "status:error AND start_time:>$(date -d '24 hours ago' --iso-8601)" \
     --fields "event_id,event_type,event_name,error,start_time"
   
   # Validate project configuration
   honeyhive project get --name "your-project-name"

**Contact Support**:

When contacting support, include:

1. Python version (``python --version``)
2. HoneyHive SDK version
3. Error messages and stack traces
4. Minimal code example that reproduces the issue
5. Operating system and environment details

**Community Resources**:

- `Discord Community <https://discord.gg/honeyhive>`_ - Chat with other users
- `GitHub Issues <https://github.com/honeyhiveai/python-sdk/issues>`_ - Report bugs
- Documentation: :doc:`../reference/index` - API reference

.. tip::
   Many issues can be resolved by using a fresh virtual environment. If you're experiencing unusual behavior, try creating a clean environment and installing only HoneyHive to isolate the issue.
