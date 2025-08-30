CLI Reference
=============

The HoneyHive CLI provides command-line tools for managing configuration, monitoring system status, debugging API calls, and performing administrative tasks.

.. contents:: Table of Contents
   :local:
   :depth: 2

Installation & Setup
--------------------

The CLI is automatically available after installing the HoneyHive Python SDK:

.. code-block:: bash

   pip install honeyhive
   
   # Verify installation
   honeyhive --help

Global Options
--------------

All CLI commands support these global options:

.. code-block:: bash

   honeyhive [OPTIONS] COMMAND [ARGS]...

**Global Options:**

* ``--version`` - Show version and exit
* ``-c, --config PATH`` - Configuration file path
* ``-v, --verbose`` - Enable verbose logging
* ``--debug`` - Enable debug mode
* ``--help`` - Show help message

Configuration Management
-------------------------

The ``config`` command group manages HoneyHive configuration settings.

Show Configuration
~~~~~~~~~~~~~~~~~~

Display current configuration in various formats:

.. code-block:: bash

   # Show configuration in JSON format (default)
   honeyhive config show
   
   # Show in YAML format
   honeyhive config show --format yaml
   
   # Show as environment variables
   honeyhive config show --format env

**Example Output:**

.. code-block:: json

   {
     "api_key": "hh_your_api_key_here",
     "api_url": "https://api.honeyhive.ai",
     "project": "my-project",
     "source": "production",
     "debug_mode": false,
     "test_mode": false,
     "experiment_id": null,
     "experiment_name": null,
     "experiment_variant": null,
     "experiment_group": null,
     "experiment_metadata": null
   }

Set Configuration
~~~~~~~~~~~~~~~~~

Update configuration values:

.. code-block:: bash

   # Set API key
   honeyhive config set --key api_key --value "your-api-key"
   
   # Set project
   honeyhive config set --key project --value "my-project"
   
   # Set source environment
   honeyhive config set --key source --value "development"

Tracing Commands
----------------

The ``trace`` command group provides tracing management capabilities.

Start Trace Span
~~~~~~~~~~~~~~~~~

Create and start a trace span interactively:

.. code-block:: bash

   # Start a simple span
   honeyhive trace start --name "manual_operation"
   
   # Start span with session ID
   honeyhive trace start --name "user_session" --session-id "session_123"
   
   # Start span with attributes (JSON format)
   honeyhive trace start --name "ai_request" --attributes '{"model": "gpt-4", "temperature": 0.7}'

The span will remain active until you press Enter, allowing you to perform operations that will be traced.

Enrich Session
~~~~~~~~~~~~~~

Add metadata, feedback, and metrics to a session:

.. code-block:: bash

   # Enrich with metadata
   honeyhive trace enrich --session-id "session_123" --metadata '{"user_type": "premium"}'
   
   # Enrich with feedback
   honeyhive trace enrich --session-id "session_123" --feedback '{"rating": 5, "comment": "Great!"}'
   
   # Enrich with metrics
   honeyhive trace enrich --session-id "session_123" --metrics '{"response_time": 0.5, "accuracy": 0.95}'
   
   # Combine multiple enrichments
   honeyhive trace enrich --session-id "session_123" \
     --metadata '{"user_type": "premium"}' \
     --feedback '{"rating": 5}' \
     --metrics '{"response_time": 0.5}'

API Client Commands
-------------------

The ``api`` command group provides direct API interaction capabilities.

Make API Request
~~~~~~~~~~~~~~~~

Send HTTP requests to the HoneyHive API:

.. code-block:: bash

   # Simple GET request
   honeyhive api request --method GET --url "/sessions"
   
   # POST request with data
   honeyhive api request --method POST --url "/events" \
     --data '{"event_name": "test", "event_type": "demo"}'
   
   # Request with custom headers
   honeyhive api request --method GET --url "/projects" \
     --headers '{"Authorization": "Bearer your-token"}'
   
   # Request with timeout
   honeyhive api request --method GET --url "/sessions" --timeout 10.0

**Example Output:**

.. code-block:: text

   Status: 200
   Duration: 0.234s
   Headers: {'content-type': 'application/json', 'content-length': '156'}
   Response: {
     "sessions": [
       {"id": "session_123", "project": "my-project"}
     ]
   }

Monitoring & Performance
------------------------

The ``monitor`` command group provides system monitoring capabilities.

System Status
~~~~~~~~~~~~~

Display comprehensive system status:

.. code-block:: bash

   honeyhive monitor status

**Example Output:**

.. code-block:: text

   === Configuration Status ===
   API Key: ✓
   Project: my-project
   Source: production
   Debug Mode: False
   Tracing Enabled: True

   === Tracer Status ===
   ℹ️  Tracer status: Multi-instance mode enabled
      Create tracers with: HoneyHiveTracer(api_key='...', project='...')
      Multiple tracers can coexist in the same runtime

   === Cache Status ===
   ✓ Cache active
     Size: 45/1000
     Hit Rate: 87.50%

   === Connection Pool Status ===
   ✓ Connection pool active
     Total Requests: 123
     Pool Hits: 98
     Pool Misses: 25

Real-time Monitoring
~~~~~~~~~~~~~~~~~~~~

Monitor system performance in real-time:

.. code-block:: bash

   # Monitor for 60 seconds with 5-second intervals (default)
   honeyhive monitor watch
   
   # Custom duration and interval
   honeyhive monitor watch --duration 120 --interval 2.0

Press ``Ctrl+C`` to stop monitoring early.

Performance Analysis
--------------------

The ``performance`` command group provides benchmarking capabilities.

Run Benchmarks
~~~~~~~~~~~~~~

Execute performance benchmarks:

.. code-block:: bash

   # Default benchmark (1000 iterations, 100 warmup)
   honeyhive performance benchmark
   
   # Custom iterations and warmup
   honeyhive performance benchmark --iterations 5000 --warmup 500

**Example Output:**

.. code-block:: text

   Running performance benchmarks...
   Iterations: 1000
   Warmup: 100

   Warming up...
   Warmup completed

   === Cache Performance ===
   Set operations: 12,500 ops/s
   Get operations: 25,000 ops/s

   === Tracer Performance ===
   ℹ️  Tracer benchmarks: Multi-instance mode enabled
      Create a tracer for benchmarking:
      tracer = HoneyHiveTracer(api_key='...', project='...')

Resource Management
-------------------

Clean Up Resources
~~~~~~~~~~~~~~~~~~

Safely shut down and clean up SDK resources:

.. code-block:: bash

   honeyhive cleanup

This command closes caches, connection pools, and other system resources.

Environment Variables
---------------------

The CLI respects all HoneyHive environment variables:

.. code-block:: bash

   # Set environment variables
   export HH_API_KEY="your-api-key"
   export HH_PROJECT="my-project"
   export HH_SOURCE="development"
   export HH_VERBOSE="true"
   export HH_DEBUG_MODE="true"
   
   # CLI will automatically use these values
   honeyhive config show

Common Workflows
----------------

Development Setup
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Check current configuration
   honeyhive config show
   
   # 2. Set development configuration
   honeyhive config set --key api_key --value "dev-api-key"
   honeyhive config set --key project --value "my-dev-project"
   honeyhive config set --key source --value "development"
   
   # 3. Verify system status
   honeyhive monitor status

Debugging API Issues
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Enable verbose mode
   honeyhive --verbose config show
   
   # 2. Test API connectivity
   honeyhive api request --method GET --url "/sessions"
   
   # 3. Monitor system performance
   honeyhive monitor watch --duration 30

Performance Analysis
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Check system status
   honeyhive monitor status
   
   # 2. Run benchmarks
   honeyhive performance benchmark
   
   # 3. Monitor real-time performance
   honeyhive monitor watch --duration 60

Session Management
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Start a traced operation
   honeyhive trace start --name "user_workflow" --session-id "session_123"
   
   # 2. Enrich the session with results
   honeyhive trace enrich --session-id "session_123" \
     --metadata '{"workflow_type": "data_processing"}' \
     --metrics '{"duration": 2.5, "success_rate": 0.95}'

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**CLI Command Not Found**

.. code-block:: bash

   # Ensure package is installed in development mode
   pip install -e .
   
   # Or reinstall the package
   pip install --force-reinstall honeyhive

**Configuration Not Loading**

.. code-block:: bash

   # Check environment variables
   honeyhive config show --format env
   
   # Verify configuration file location
   honeyhive --config /path/to/config.yaml config show

**API Connection Issues**

.. code-block:: bash

   # Test with verbose logging
   honeyhive --verbose api request --method GET --url "https://api.honeyhive.ai/health"
   
   # Check system status
   honeyhive monitor status

**Performance Issues**

.. code-block:: bash

   # Run benchmarks to identify bottlenecks
   honeyhive performance benchmark
   
   # Monitor real-time performance
   honeyhive monitor watch

TLS/SSL Issues
~~~~~~~~~~~~~~

TLS (Transport Layer Security) issues are common when connecting to HTTPS APIs. Here are diagnostic and resolution steps:

**Diagnosing TLS Issues**

.. code-block:: bash

   # Test basic connectivity with verbose logging
   honeyhive --verbose api request --method GET --url "https://api.honeyhive.ai/health"
   
   # Check TLS certificate information
   openssl s_client -connect api.honeyhive.ai:443 -servername api.honeyhive.ai
   
   # Test with curl for comparison
   curl -v https://api.honeyhive.ai/health

**Common TLS Error Messages:**

1. **SSL Certificate Verification Failed**

   .. code-block:: text
   
      Error: SSL: CERTIFICATE_VERIFY_FAILED
   
   **Solutions:**
   
   .. code-block:: bash
   
      # Update certificates (macOS)
      /Applications/Python\ 3.x/Install\ Certificates.command
      
      # Update certificates (Linux)
      sudo apt-get update && sudo apt-get install ca-certificates
      
      # Update certificates (Windows)
      pip install --upgrade certifi

2. **TLS Version Mismatch**

   .. code-block:: text
   
      Error: SSL: TLSV1_ALERT_PROTOCOL_VERSION
   
   **Solutions:**
   
   .. code-block:: bash
   
      # Check Python TLS support
      python -c "import ssl; print(ssl.OPENSSL_VERSION)"
      
      # Upgrade Python/OpenSSL if needed
      pip install --upgrade requests urllib3

3. **Certificate Authority Issues**

   .. code-block:: text
   
      Error: SSL: CERTIFICATE_VERIFY_FAILED certificate verify failed: unable to get local issuer certificate
   
   **Solutions:**
   
   .. code-block:: bash
   
      # Set certificate bundle path
      export SSL_CERT_FILE=$(python -m certifi)
      export REQUESTS_CA_BUNDLE=$(python -m certifi)
      
      # Test after setting certificates
      honeyhive api request --method GET --url "https://api.honeyhive.ai/health"

4. **Corporate Firewall/Proxy Issues**

   .. code-block:: text
   
      Error: SSL: CERTIFICATE_VERIFY_FAILED certificate verify failed: self signed certificate in certificate chain
   
   **Solutions:**
   
   .. code-block:: bash
   
      # Configure proxy settings
      export HTTPS_PROXY=https://proxy.company.com:8080
      export HTTP_PROXY=http://proxy.company.com:8080
      
      # Add corporate certificates to Python
      cat /path/to/corporate-cert.pem >> $(python -m certifi)
      
      # Test with proxy
      honeyhive --verbose api request --method GET --url "https://api.honeyhive.ai/health"

**TLS Verification Control**

The SDK respects both HoneyHive-specific and standard TLS verification environment variables:

.. code-block:: bash

   # Disable TLS verification (WARNING: Use only for development/debugging)
   # Method 1: HoneyHive-specific variable (recommended)
   export HH_VERIFY_SSL=false
   
   # Method 2: Standard variables
   export PYTHONHTTPSVERIFY=0
   export SSL_VERIFY=false
   export REQUESTS_CA_BUNDLE=""
   
   # Test with TLS verification disabled
   honeyhive api request --method GET --url "https://api.honeyhive.ai/health"
   
   # Re-enable TLS verification
   export HH_VERIFY_SSL=true
   export PYTHONHTTPSVERIFY=1
   export SSL_VERIFY=true
   export REQUESTS_CA_BUNDLE=$(python -m certifi)

**Advanced TLS Debugging**

.. code-block:: bash

   # Enable detailed SSL debugging in Python
   export PYTHONHTTPSVERIFY=0  # WARNING: Only for debugging, disables SSL verification
   export CURL_CA_BUNDLE=""    # Clear curl certificate bundle
   
   # Run with maximum verbosity
   honeyhive --verbose --debug api request --method GET --url "https://api.honeyhive.ai/health"
   
   # Check certificate chain
   python -c "
   import ssl
   import socket
   
   context = ssl.create_default_context()
   with socket.create_connection(('api.honeyhive.ai', 443)) as sock:
       with context.wrap_socket(sock, server_hostname='api.honeyhive.ai') as ssock:
           print('SSL certificate:', ssock.getpeercert())
           print('SSL version:', ssock.version())
           print('SSL cipher:', ssock.cipher())
   "

**Environment-Specific TLS Solutions**

**Docker/Container Environments:**

.. code-block:: bash

   # Update certificates in container
   RUN apt-get update && apt-get install -y ca-certificates
   
   # Or for Alpine Linux
   RUN apk add --no-cache ca-certificates

**macOS Specific:**

.. code-block:: bash

   # Install certificates for Python
   /Applications/Python\ 3.x/Install\ Certificates.command
   
   # Or manually update
   pip install --upgrade certifi
   
   # Check keychain certificates
   security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain

**Windows Specific:**

.. code-block:: bash

   # Update Windows certificate store
   certlm.msc  # Open certificate manager
   
   # Update Python certificates
   pip install --upgrade pip certifi requests urllib3
   
   # Set certificate environment variable
   set SSL_CERT_FILE=%LOCALAPPDATA%\Programs\Python\Python3x\Lib\site-packages\certifi\cacert.pem

**Testing TLS Configuration**

.. code-block:: bash

   # Test TLS versions supported
   python -c "
   import ssl
   context = ssl.create_default_context()
   print('Supported protocols:', context.protocol)
   print('Available ciphers:', len(context.get_ciphers()))
   "
   
   # Test specific TLS version
   openssl s_client -tls1_2 -connect api.honeyhive.ai:443
   openssl s_client -tls1_3 -connect api.honeyhive.ai:443
   
   # Verify certificate chain
   openssl verify -CAfile $(python -m certifi) <(openssl s_client -connect api.honeyhive.ai:443 -servername api.honeyhive.ai 2>/dev/null | openssl x509)

**TLS Environment Variables Reference**

The SDK recognizes these TLS-related environment variables (HoneyHive-specific variables take precedence):

.. code-block:: bash

   # TLS verification control (HoneyHive-specific - recommended)
   export HH_VERIFY_SSL=true         # true=verify, false=skip verification
   
   # TLS verification control (standard alternatives)
   export PYTHONHTTPSVERIFY=1        # 1=verify, 0=skip verification
   export SSL_VERIFY=true            # true=verify, false=skip verification
   export VERIFY_SSL=true            # true=verify, false=skip verification
   
   # Certificate bundle location
   export SSL_CERT_FILE=/path/to/ca-bundle.crt
   export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt
   export CURL_CA_BUNDLE=/path/to/ca-bundle.crt
   
   # Proxy settings (HoneyHive-specific)
   export HH_HTTPS_PROXY=https://proxy.company.com:8080
   export HH_HTTP_PROXY=http://proxy.company.com:8080
   export HH_NO_PROXY=localhost,127.0.0.1,.company.com
   
   # Proxy settings (standard alternatives)
   export HTTPS_PROXY=https://proxy.company.com:8080
   export HTTP_PROXY=http://proxy.company.com:8080
   export NO_PROXY=localhost,127.0.0.1,.company.com
   
   # Test current TLS configuration
   honeyhive api request --method GET --url "https://api.honeyhive.ai/health"

**TLS Best Practices**

1. **Keep certificates updated:**

   .. code-block:: bash
   
      # Regular certificate updates
      pip install --upgrade certifi requests urllib3
      
      # Verify certificate validity
      python -c "import certifi; print(certifi.where())"

2. **Use environment variables:**

   .. code-block:: bash
   
      # Set in your shell profile (.bashrc, .zshrc, etc.)
      export SSL_CERT_FILE=$(python -m certifi)
      export REQUESTS_CA_BUNDLE=$(python -m certifi)

3. **Monitor certificate expiration:**

   .. code-block:: bash
   
      # Check certificate expiration
      echo | openssl s_client -connect api.honeyhive.ai:443 2>/dev/null | openssl x509 -noout -dates

**Emergency TLS Bypass (Development Only)**

.. code-block:: bash

   # WARNING: Only use for development/debugging
   # This disables SSL verification - NEVER use in production
   
   # Method 1: HoneyHive-specific variable (recommended)
   export HH_VERIFY_SSL=false
   
   # Method 2: Python-specific variables
   export PYTHONHTTPSVERIFY=0
   export CURL_CA_BUNDLE=""
   
   # Method 3: Standard SDK variables
   export SSL_VERIFY=false
   export REQUESTS_CA_BUNDLE=""
   
   # Test connectivity with verification disabled
   honeyhive api request --method GET --url "https://api.honeyhive.ai/health"
   
   # Remember to re-enable verification when done
   export HH_VERIFY_SSL=true
   export PYTHONHTTPSVERIFY=1
   export SSL_VERIFY=true
   export REQUESTS_CA_BUNDLE=$(python -m certifi)
   
   # Or unset the variables entirely
   unset HH_VERIFY_SSL PYTHONHTTPSVERIFY CURL_CA_BUNDLE SSL_VERIFY REQUESTS_CA_BUNDLE

Getting Help
------------

Each command and subcommand provides detailed help:

.. code-block:: bash

   # General help
   honeyhive --help
   
   # Command group help
   honeyhive config --help
   honeyhive trace --help
   honeyhive api --help
   honeyhive monitor --help
   honeyhive performance --help
   
   # Specific command help
   honeyhive config show --help
   honeyhive trace start --help
   honeyhive api request --help
