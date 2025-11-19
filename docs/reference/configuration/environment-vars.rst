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
   * - ``HH_API_SECRET``
     - *Optional*
     - Additional API secret for enhanced security (enterprise only)

**Examples:**

.. code-block:: bash

   # Basic authentication
   export HH_API_KEY="hh_1234567890abcdef"
   
   # Enterprise authentication with secret
   export HH_API_KEY="hh_enterprise_key"
   export HH_API_SECRET="secret_key_for_enhanced_security"


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
     - ``"unknown"``
     - Source environment identifier (e.g., production, staging)
   * - ``HH_SESSION_NAME``
     - *Auto-generated*
     - Default session name for trace grouping

**Examples:**

.. code-block:: bash

   # Production configuration
   export HH_SOURCE="production"
   export HH_SESSION_NAME="prod-session-$(date +%Y%m%d)"
   
   # Development configuration
   export HH_SOURCE="development"
   export HH_SESSION_NAME="dev-local"


Network Configuration
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``HH_BASE_URL``
     - ``"https://api.honeyhive.ai"``
     - HoneyHive API endpoint URL
   * - ``HH_SERVER_URL``
     - *None*
     - Alias for ``HH_BASE_URL`` (for backward compatibility)
   * - ``HH_TIMEOUT``
     - ``30.0``
     - Request timeout in seconds
   * - ``HH_MAX_RETRIES``
     - ``3``
     - Maximum number of retry attempts for failed requests

**Examples:**

.. code-block:: bash

   # Custom deployment
   export HH_BASE_URL="https://honeyhive.mycompany.com"
   export HH_TIMEOUT="60.0"
   export HH_MAX_RETRIES="5"
   
   # Development with local server
   export HH_BASE_URL="http://localhost:8080"
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
   * - ``HH_DEBUG``
     - ``false``
     - Enable debug logging and verbose output
   * - ``HH_LOG_LEVEL``
     - ``"INFO"``
     - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

**Examples:**

.. code-block:: bash

   # Test environment
   export HH_TEST_MODE="true"
   export HH_DEBUG="true"
   export HH_LOG_LEVEL="DEBUG"
   
   # Production environment
   export HH_TEST_MODE="false"
   export HH_DEBUG="false"
   export HH_LOG_LEVEL="WARNING"

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
   * - ``HH_MAX_QUEUE_SIZE``
     - ``1000``
     - Maximum number of spans in memory queue

**Examples:**

.. code-block:: bash

   # High-throughput configuration
   export HH_BATCH_SIZE="500"
   export HH_FLUSH_INTERVAL="10.0"
   export HH_MAX_QUEUE_SIZE="5000"
   
   # Low-latency configuration
   export HH_BATCH_SIZE="10"
   export HH_FLUSH_INTERVAL="1.0"
   export HH_MAX_QUEUE_SIZE="100"

Connection Pooling
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``HH_MAX_CONNECTIONS``
     - ``50``
     - Maximum concurrent HTTP connections
   * - ``HH_MAX_KEEPALIVE_CONNECTIONS``
     - ``10``
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
   * - ``HH_CAPTURE_INPUTS``
     - ``true``
     - Default setting for capturing function inputs
   * - ``HH_CAPTURE_OUTPUTS``
     - ``true``
     - Default setting for capturing function outputs
   * - ``HH_CAPTURE_EXCEPTIONS``
     - ``true``
     - Whether to capture exception details in traces

Backwards Compatibility Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``HONEYHIVE_TELEMETRY``
     - ``true``
     - Enable/disable git metadata collection for sessions
   * - ``HH_VERBOSE``
     - ``false``
     - Enable verbose debug logging throughout tracer initialization
   * - ``HH_DISABLE_BATCH``
     - ``false``
     - Use SimpleSpanProcessor instead of BatchSpanProcessor for immediate export

**Examples:**

.. code-block:: bash

   # Security-conscious configuration
   export HH_CAPTURE_INPUTS="false"
   export HH_CAPTURE_OUTPUTS="false"
   export HH_CAPTURE_EXCEPTIONS="true"
   
   # Full observability configuration
   export HH_CAPTURE_INPUTS="true"
   export HH_CAPTURE_OUTPUTS="true"
   export HH_CAPTURE_EXCEPTIONS="true"
   export HH_DISABLE_HTTP_TRACING="false"
   
   # Backwards compatibility configuration
   export HONEYHIVE_TELEMETRY="false"  # Disable git metadata collection
   export HH_VERBOSE="true"             # Enable debug logging
   export HH_DISABLE_BATCH="true"       # Use immediate export for debugging


Sampling Configuration
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``HH_SAMPLING_RATE``
     - ``1.0``
     - Global sampling rate (0.0 to 1.0)
   * - ``HH_ERROR_SAMPLING_RATE``
     - ``1.0``
     - Sampling rate for error traces
   * - ``HH_SLOW_THRESHOLD``
     - ``1000.0``
     - Threshold in milliseconds for slow trace sampling

**Examples:**

.. code-block:: bash

   # Production sampling (10% of normal traces, all errors)
   export HH_SAMPLING_RATE="0.1"
   export HH_ERROR_SAMPLING_RATE="1.0"
   export HH_SLOW_THRESHOLD="500.0"
   
   # Development (all traces)
   export HH_SAMPLING_RATE="1.0"
   export HH_ERROR_SAMPLING_RATE="1.0"

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
   * - ``HH_SSL_CERT_PATH``
     - *None*
     - Path to custom SSL certificate file
   * - ``HH_SSL_KEY_PATH``
     - *None*
     - Path to SSL private key file (client certificates)

**Examples:**

.. code-block:: bash

   # Enterprise SSL configuration
   export HH_VERIFY_SSL="true"
   export HH_SSL_CERT_PATH="/etc/ssl/certs/honeyhive.pem"
   export HH_SSL_KEY_PATH="/etc/ssl/private/honeyhive.key"
   
   # Development with self-signed certificates
   export HH_VERIFY_SSL="false"

Proxy Configuration
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``HH_PROXY_URL``
     - *None*
     - HTTP/HTTPS proxy URL
   * - ``HH_PROXY_USERNAME``
     - *None*
     - Proxy authentication username
   * - ``HH_PROXY_PASSWORD``
     - *None*
     - Proxy authentication password

**Examples:**

.. code-block:: bash

   # Corporate proxy
   export HH_PROXY_URL="http://proxy.company.com:8080"
   export HH_PROXY_USERNAME="proxy_user"
   export HH_PROXY_PASSWORD="proxy_password"

Data Privacy
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``HH_SANITIZE_INPUTS``
     - ``false``
     - Automatically sanitize sensitive data in inputs
   * - ``HH_SANITIZE_OUTPUTS``
     - ``false``
     - Automatically sanitize sensitive data in outputs
   * - ``HH_PII_PATTERNS``
     - *Default patterns*
     - Custom regex patterns for PII detection

**Examples:**

.. code-block:: bash

   # Privacy-focused configuration
   export HH_SANITIZE_INPUTS="true"
   export HH_SANITIZE_OUTPUTS="true"
   export HH_PII_PATTERNS="email,phone,ssn,credit_card"


Evaluation Configuration
------------------------

Evaluator Settings
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Variable
     - Default
     - Description
   * - ``HH_ENABLE_EVALUATION``
     - ``true``
     - Enable automatic evaluation
   * - ``HH_EVALUATION_TIMEOUT``
     - ``30.0``
     - Timeout for evaluation requests in seconds
   * - ``HH_EVALUATION_RETRIES``
     - ``2``
     - Number of retries for failed evaluations

**Examples:**

.. code-block:: bash

   # Evaluation configuration
   export HH_ENABLE_EVALUATION="true"
   export HH_EVALUATION_TIMEOUT="60.0"
   export HH_EVALUATION_RETRIES="3"

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
   HH_SOURCE="development"
   HH_TEST_MODE="false"
   HH_DEBUG="true"
   HH_LOG_LEVEL="DEBUG"
   HH_SAMPLING_RATE="1.0"
   HH_BATCH_SIZE="10"
   HH_FLUSH_INTERVAL="1.0"
   HH_CAPTURE_INPUTS="true"
   HH_CAPTURE_OUTPUTS="true"

Staging Environment
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # .env.staging
   HH_API_KEY="hh_staging_key_here"
   HH_SOURCE="staging"
   HH_TEST_MODE="false"
   HH_DEBUG="false"
   HH_LOG_LEVEL="INFO"
   HH_SAMPLING_RATE="0.5"
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
   HH_DEBUG="false"
   HH_LOG_LEVEL="WARNING"
   HH_SAMPLING_RATE="0.1"
   HH_ERROR_SAMPLING_RATE="1.0"
   HH_BATCH_SIZE="200"
   HH_FLUSH_INTERVAL="10.0"
   HH_MAX_CONNECTIONS="100"
   HH_TIMEOUT="60.0"
   HH_SANITIZE_INPUTS="true"
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
   ENV HH_LOG_LEVEL="INFO"
   
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
         - HH_DEBUG=false
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
           - name: HH_LOG_LEVEL
             value: "INFO"

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
   from honeyhive.utils import validate_configuration
   
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
       
       # Validate numeric values
       numeric_vars = {
           'HH_TIMEOUT': (1.0, 300.0),
           'HH_BATCH_SIZE': (1, 10000),
           'HH_SAMPLING_RATE': (0.0, 1.0)
       }
       
       for var, (min_val, max_val) in numeric_vars.items():
           if value_str := os.getenv(var):
               try:
                   value = float(value_str)
                   if not min_val <= value <= max_val:
                       raise ValueError(f"{var} must be between {min_val} and {max_val}")
               except ValueError:
                   raise ValueError(f"{var} must be a valid number")
       
       # Validate boolean values
       boolean_vars = ['HH_TEST_MODE', 'HH_DEBUG', 'HH_VERIFY_SSL']
       for var in boolean_vars:
           if value_str := os.getenv(var):
               if value_str.lower() not in ['true', 'false']:
                   raise ValueError(f"{var} must be 'true' or 'false'")
       
       print("✓ HoneyHive configuration is valid")


Configuration Loading Patterns
------------------------------

Hierarchical Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   from typing import Dict, Any
   
   class HoneyHiveConfig:
       """Hierarchical configuration with environment override."""
       
       def __init__(self, config_file: str = None, env_prefix: str = "HH_"):
           self.env_prefix = env_prefix
           self.config = self._load_base_config()
           
           if config_file:
               self.config.update(self._load_file_config(config_file))
           
           self.config.update(self._load_env_config())
       
       def _load_base_config(self) -> Dict[str, Any]:
           """Load default configuration."""
           return {
               'api_key': None,
               'project': 'default',
               'source': 'unknown',
               'test_mode': False,
               'debug': False,
               'timeout': 30.0,
               'batch_size': 100,
               'sampling_rate': 1.0
           }
       
       def _load_file_config(self, config_file: str) -> Dict[str, Any]:
           """Load configuration from file."""
           import json
           with open(config_file) as f:
               return json.load(f)
       
       def _load_env_config(self) -> Dict[str, Any]:
           """Load configuration from environment variables."""
           config = {}
           
           env_mapping = {
               'HH_API_KEY': 'api_key',
               'HH_PROJECT': 'project',
               'HH_SOURCE': 'source',
               'HH_TEST_MODE': 'test_mode',
               'HH_DEBUG': 'debug',
               'HH_TIMEOUT': 'timeout',
               'HH_BATCH_SIZE': 'batch_size',
               'HH_SAMPLING_RATE': 'sampling_rate'
           }
           
           for env_var, config_key in env_mapping.items():
               if value := os.getenv(env_var):
                   # Type conversion
                   if config_key in ['test_mode', 'debug']:
                       config[config_key] = value.lower() == 'true'
                   elif config_key in ['timeout', 'sampling_rate']:
                       config[config_key] = float(value)
                   elif config_key in ['batch_size']:
                       config[config_key] = int(value)
                   else:
                       config[config_key] = value
           
           return config
       
       def get(self, key: str, default=None):
           """Get configuration value."""
           return self.config.get(key, default)
       
       def __getitem__(self, key: str):
           """Dictionary-style access."""
           return self.config[key]


Configuration Factory
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   class ConfigurationFactory:
       """Factory for creating configured HoneyHive instances."""
       
       @staticmethod
       def create_from_environment() -> HoneyHiveTracer:
           """Create tracer from environment variables."""
           return HoneyHiveTracer.init(
               project=os.getenv('HH_PROJECT', 'default-project')  # Or set HH_PROJECT environment variable
           )
       
       @staticmethod
       def create_for_testing() -> HoneyHiveTracer:
           """Create tracer configured for testing."""
           return HoneyHiveTracer.init(
               api_key=os.getenv('HH_API_KEY', 'test_key'),  # Or set HH_API_KEY environment variable
               project=os.getenv('HH_PROJECT', 'test-project'),  # Or set HH_PROJECT environment variable
               source='test',                                 # Or set HH_SOURCE environment variable
               test_mode=True                                 # Or set HH_TEST_MODE=true environment variable
           )
       
       @staticmethod
       def create_for_production() -> HoneyHiveTracer:
           """Create production-optimized tracer."""
           return HoneyHiveTracer.init(
               api_key=os.getenv('HH_API_KEY'),              # Or set HH_API_KEY environment variable
               project=os.getenv('HH_PROJECT', 'production-project'),  # Or set HH_PROJECT environment variable
               source='production'                           # Or set HH_SOURCE environment variable
           )


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

   # Solution: Reduce batch size and queue size
   export HH_BATCH_SIZE="50"
   export HH_MAX_QUEUE_SIZE="500"
   export HH_FLUSH_INTERVAL="2.0"

**Issue: SSL Certificate Errors**

.. code-block:: bash

   # For development only - disable SSL verification
   export HH_VERIFY_SSL="false"
   
   # For production - use proper certificates
   export HH_SSL_CERT_PATH="/path/to/cert.pem"


Configuration Debugging
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   from honeyhive.utils import get_configuration_summary
   
   def debug_configuration():
       """Debug current configuration."""
       print("HoneyHive Configuration Debug:")
       print("=" * 40)
       
       # Core settings
       print(f"API Key: {'✓ Set' if os.getenv('HH_API_KEY') else '✗ Missing'}")
       print(f"Project: {os.getenv('HH_PROJECT', 'default')}")
       print(f"Source: {os.getenv('HH_SOURCE', 'unknown')}")
       print(f"Test Mode: {os.getenv('HH_TEST_MODE', 'false')}")
       
       # Network settings
       print(f"Base URL: {os.getenv('HH_BASE_URL', 'https://api.honeyhive.ai')}")
       print(f"Timeout: {os.getenv('HH_TIMEOUT', '30.0')}s")
       
       # Performance settings
       print(f"Batch Size: {os.getenv('HH_BATCH_SIZE', '100')}")
       print(f"Sampling Rate: {os.getenv('HH_SAMPLING_RATE', '1.0')}")
       
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
- :doc:`../../tutorials/advanced-configuration` - Advanced configuration patterns
- :doc:`../../how-to/deployment/production` - Production deployment guide
- :doc:`../../how-to/index` - Configuration troubleshooting (see Troubleshooting section)