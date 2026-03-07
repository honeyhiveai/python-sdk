Environment Variables Reference
===============================

.. note::
   **Complete reference for HoneyHive SDK environment variables**
   
   Configure the SDK behavior through environment variables for different deployment scenarios.

The HoneyHive SDK supports comprehensive configuration through environment variables, allowing for flexible deployment across different environments without code changes.

.. note::
   **Runtime Configuration Support** (v0.1.0rc2+)
   
   Environment variables are now properly picked up when set at runtime, after SDK import. This enables dynamic configuration changes without restarting the application.


Core Configuration Variables
----------------------------

Authentication
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``HH_API_KEY``
     - *Required*
     - HoneyHive API key for authentication. Format: ``hh_...``

**Examples:**

.. code-block:: bash

   # Basic authentication
   export HH_API_KEY="hh_1234567890abcdef"


Project Configuration
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``HH_PROJECT``
     - *Required*
     - Project name for HoneyHive operations. Must match your HoneyHive project.
   * - ``HH_SOURCE``
     - ``"dev"``
     - Source environment identifier (e.g., dev, staging, production)

**Examples:**

.. code-block:: bash

   # Production configuration
   export HH_SOURCE="production"
   
   # Development configuration
   export HH_SOURCE="development"


Network Configuration
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``HH_API_URL``
     - ``"https://api.honeyhive.ai"``
     - HoneyHive API endpoint URL
   * - ``HH_TIMEOUT``
     - ``30.0``
     - Request timeout in seconds
   * - ``HH_MAX_RETRIES``
     - ``3``
     - Maximum number of retry attempts for failed requests

**Examples:**

.. code-block:: bash

   # Custom deployment
   export HH_API_URL="https://honeyhive.mycompany.com"
   export HH_TIMEOUT="60.0"
   export HH_MAX_RETRIES="5"
   
   # Development with local server
   export HH_API_URL="http://localhost:8080"
   export HH_TIMEOUT="10.0"


Testing and Development
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``HH_TEST_MODE``
     - ``false``
     - Enable test mode (no data sent to HoneyHive)
   * - ``HH_VERBOSE``
     - ``false``
     - Enable verbose debug logging throughout tracer initialization

**Examples:**

.. code-block:: bash

   # Test environment
   export HH_TEST_MODE="true"
   export HH_VERBOSE="true"
   
   # Production environment
   export HH_TEST_MODE="false"

Performance Configuration
-------------------------

Batching and Buffering
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``HH_BATCH_SIZE``
     - ``100``
     - Number of spans to batch before sending
   * - ``HH_FLUSH_INTERVAL``
     - ``5.0``
     - Automatic flush interval in seconds

**Examples:**

.. code-block:: bash

   # High-throughput configuration
   export HH_BATCH_SIZE="500"
   export HH_FLUSH_INTERVAL="10.0"
   
   # Low-latency configuration
   export HH_BATCH_SIZE="10"
   export HH_FLUSH_INTERVAL="1.0"

Connection Pooling
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``HH_MAX_CONNECTIONS``
     - ``10``
     - Maximum concurrent HTTP connections
   * - ``HH_MAX_KEEPALIVE_CONNECTIONS``
     - ``20``
     - Maximum persistent connections
   * - ``HH_KEEPALIVE_EXPIRY``
     - ``30.0``
     - Connection keepalive timeout in seconds

**Examples:**

.. code-block:: bash

   # High-concurrency configuration
   export HH_MAX_CONNECTIONS="200"
   export HH_MAX_KEEPALIVE_CONNECTIONS="50"
   export HH_KEEPALIVE_EXPIRY="60.0"


Tracing Configuration
---------------------

Instrumentation Control
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``HH_DISABLE_HTTP_TRACING``
     - ``true``
     - Disable automatic HTTP request tracing
   * - ``HH_DISABLE_BATCH``
     - ``false``
     - Use SimpleSpanProcessor instead of BatchSpanProcessor for immediate export
   * - ``HH_DISABLE_TRACING``
     - ``false``
     - Disable all tracing functionality



Security Configuration
----------------------

SSL/TLS Settings
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``HH_VERIFY_SSL``
     - ``true``
     - Verify SSL certificates for HTTPS requests
   * - ``HH_FOLLOW_REDIRECTS``
     - ``true``
     - Follow HTTP redirects for API requests

**Examples:**

.. code-block:: bash

   # Development with self-signed certificates
   export HH_VERIFY_SSL="false"
   export HH_FOLLOW_REDIRECTS="true"

Proxy Configuration
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``HH_HTTP_PROXY``
     - *None*
     - HTTP proxy URL
   * - ``HH_HTTPS_PROXY``
     - *None*
     - HTTPS proxy URL
   * - ``HH_NO_PROXY``
     - *None*
     - Comma-separated list of hosts that bypass proxy routing

**Examples:**

.. code-block:: bash

   # Corporate proxy
   export HH_HTTP_PROXY="http://proxy.company.com:8080"
   export HH_HTTPS_PROXY="http://proxy.company.com:8080"
   export HH_NO_PROXY="localhost,127.0.0.1,.internal"

Provider-Specific Variables
---------------------------

OpenAI Configuration
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``OPENAI_API_KEY``
     - *None*
     - OpenAI API key (used by OpenAI instrumentor)
   * - ``OPENAI_BASE_URL``
     - *OpenAI default*
     - Custom OpenAI API endpoint
   * - ``OPENAI_ORGANIZATION``
     - *None*
     - OpenAI organization ID

**Examples:**

.. code-block:: bash

   # OpenAI configuration
   export OPENAI_API_KEY="sk-..."
   export OPENAI_ORGANIZATION="org-..."

Anthropic Configuration
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``ANTHROPIC_API_KEY``
     - *None*
     - Anthropic API key (used by Anthropic instrumentor)
   * - ``ANTHROPIC_BASE_URL``
     - *Anthropic default*
     - Custom Anthropic API endpoint

**Examples:**

.. code-block:: bash

   # Anthropic configuration
   export ANTHROPIC_API_KEY="sk-ant-..."


Environment-Specific Configurations
-----------------------------------

Development Environment
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # .env.development
   HH_API_KEY="hh_dev_key_here"
   HH_SOURCE="dev"
   HH_TEST_MODE="false"
   HH_VERBOSE="true"
   HH_BATCH_SIZE="10"
   HH_FLUSH_INTERVAL="1.0"

Staging Environment
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # .env.staging
   HH_API_KEY="hh_staging_key_here"
   HH_SOURCE="staging"
   HH_TEST_MODE="false"
   HH_BATCH_SIZE="50"
   HH_FLUSH_INTERVAL="3.0"
   HH_TIMEOUT="45.0"

Production Environment
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # .env.production
   HH_API_KEY="hh_prod_key_here"
   HH_SOURCE="production"
   HH_TEST_MODE="false"
   HH_BATCH_SIZE="200"
   HH_FLUSH_INTERVAL="10.0"
   HH_MAX_CONNECTIONS="100"
   HH_TIMEOUT="60.0"
   HH_VERIFY_SSL="true"


Container Deployment
--------------------

Docker Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: dockerfile

   # Dockerfile
   FROM python:3.11-slim
   
   # Install application
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . /app
   WORKDIR /app
   
   # Environment variables with defaults
   ENV HH_SOURCE="container"
   ENV HH_BATCH_SIZE="100"
   ENV HH_FLUSH_INTERVAL="5.0"
   CMD ["python", "app.py"]

**Docker Compose:**

.. code-block:: yaml

   # docker-compose.yml
   version: '3.8'
   services:
     app:
       build: .
       environment:
         - HH_API_KEY=${HH_API_KEY}
         - HH_SOURCE=docker-compose
         - HH_BATCH_SIZE=150
         - HH_TIMEOUT=45.0
       env_file:
         - .env.production

Kubernetes Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # k8s-deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: honeyhive-app
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: honeyhive-app
     template:
       metadata:
         labels:
           app: honeyhive-app
       spec:
         containers:
         - name: app
           image: myapp:latest
           env:
           - name: HH_API_KEY
             valueFrom:
               secretKeyRef:
                 name: honeyhive-secret
                 key: api-key
           - name: HH_PROJECT
             value: "k8s-production-app"
           - name: HH_SOURCE
             value: "kubernetes"
           - name: HH_BATCH_SIZE
             value: "200"
           - name: HH_MAX_CONNECTIONS
             value: "100"

--------------------------

.. code-block:: yaml

   apiVersion: v1
   kind: Secret
   metadata:
     name: honeyhive-secret
   type: Opaque
   data:
     api-key: <base64-encoded-api-key>

Configuration Validation
------------------------

Environment Variable Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   
   def validate_honeyhive_config():
       """Validate HoneyHive environment configuration."""
       
       # Required variables
       required_vars = ['HH_API_KEY']
       missing_vars = [var for var in required_vars if not os.getenv(var)]
       
       if missing_vars:
           raise ValueError(f"Missing required environment variables: {missing_vars}")
       
       # Validate API key format
       api_key = os.getenv('HH_API_KEY')
       if not api_key.startswith('hh_'):
           raise ValueError("HH_API_KEY must start with 'hh_'")
       
       print("✓ HoneyHive configuration is valid")


Troubleshooting Configuration
-----------------------------

Common Issues
~~~~~~~~~~~~~

**Issue: API Key Not Found**

.. code-block:: bash

   # Error: HoneyHive API key not found
   # Solution: Set the environment variable
   export HH_API_KEY="your_api_key_here"

**Issue: Connection Timeout**

.. code-block:: bash

   # Error: Request timeout
   # Solution: Increase timeout or check network
   export HH_TIMEOUT="60.0"
   export HH_MAX_RETRIES="5"

**Issue: High Memory Usage**

.. code-block:: bash

   # Solution: Reduce batch size
   export HH_BATCH_SIZE="50"
   export HH_FLUSH_INTERVAL="2.0"

**Issue: SSL Certificate Errors**

.. code-block:: bash

   # For development only - disable SSL verification
   export HH_VERIFY_SSL="false"


Configuration Debugging
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   def debug_configuration():
       """Debug current configuration."""
       print("HoneyHive Configuration Debug:")
       print("=" * 40)
       
       # Core settings
       print(f"API Key: {'✓ Set' if os.getenv('HH_API_KEY') else '✗ Missing'}")
       print(f"Project: {os.getenv('HH_PROJECT', 'default')}")
       print(f"Source: {os.getenv('HH_SOURCE', 'dev')}")
       print(f"Test Mode: {os.getenv('HH_TEST_MODE', 'false')}")
       
       # Network settings
       print(f"Base URL: {os.getenv('HH_API_URL', 'https://api.honeyhive.ai')}")
       print(f"Timeout: {os.getenv('HH_TIMEOUT', '30.0')}s")
       
       # Performance settings
       print(f"Batch Size: {os.getenv('HH_BATCH_SIZE', '100')}")
       
       # Debug environment
       all_hh_vars = {k: v for k, v in os.environ.items() if k.startswith('HH_')}
       if all_hh_vars:
           print("\nAll HH_ Environment Variables:")
           for key, value in sorted(all_hh_vars.items()):
               # Mask sensitive values
               if 'key' in key.lower() or 'secret' in key.lower():
                   masked_value = value[:8] + "..." if len(value) > 8 else "***"
                   print(f"  {key}={masked_value}")
               else:
                   print(f"  {key}={value}")

See Also
--------

- :doc:`../api/tracer` - HoneyHiveTracer configuration options
