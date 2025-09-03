Configuration Options Reference
=================================

.. note::
   **Complete reference for HoneyHive SDK configuration options**
   
   This document provides detailed specifications for all configuration options available in the HoneyHive SDK.

The HoneyHive SDK can be configured through various methods: environment variables, configuration files, direct initialization parameters, and CLI options.

Configuration Methods
---------------------

The SDK supports multiple configuration approaches, listed in order of precedence (highest to lowest):

1. **Direct Parameters** - Values passed directly to functions/classes
2. **Environment Variables** - ``HH_*`` environment variables
3. **Configuration Files** - YAML/JSON configuration files
4. **Default Values** - Built-in SDK defaults

Core Configuration Options
--------------------------

Authentication
~~~~~~~~~~~~~~

.. py:data:: api_key
   :type: str
   :value: None

   **Description**: HoneyHive API key for authentication
   
   **Environment Variable**: ``HH_API_KEY``
   
   **Required**: Yes
   
   **Format**: String starting with ``hh_``
   
   **Example**: ``"hh_1234567890abcdef..."``
   
   **Security**: Keep this secure and never commit to code repositories

.. py:data:: base_url
   :type: str
   :value: "https://api.honeyhive.ai"

   **Description**: Base URL for HoneyHive API
   
   **Environment Variable**: ``HH_BASE_URL``
   
   **Default**: ``"https://api.honeyhive.ai"``
   
   **Examples**:
   - ``"https://api.honeyhive.ai"`` (Production)
   - ``"https://api-staging.honeyhive.ai"`` (Staging)
   - ``"https://api-dev.honeyhive.ai"`` (Development)

Project Configuration
~~~~~~~~~~~~~~~~~~~~~

.. py:data:: project
   :type: str
   :value: None

   **Description**: Default project name for operations
   
   **Environment Variable**: ``HH_PROJECT``
   
   **Required**: Yes (for most operations)
   
   **Format**: Alphanumeric with hyphens and underscores
   
   **Example**: ``"my-llm-application"``
   
   **Validation**: 1-100 characters, cannot start/end with special characters

.. py:data:: source
   :type: str
   :value: None

   **Description**: Source identifier for tracing
   
   **Environment Variable**: ``HH_SOURCE``
   
   **Default**: Auto-detected from environment
   
   **Examples**:
   - ``"chat-service"``
   - ``"recommendation-engine"``
   - ``"data-pipeline"``

.. py:data:: session_name
   :type: str
   :value: None

   **Description**: Default session name for tracing
   
   **Environment Variable**: ``HH_SESSION_NAME``
   
   **Default**: Auto-generated based on context
   
   **Format**: Human-readable string
   
   **Example**: ``"user-chat-session"``

Operational Mode
~~~~~~~~~~~~~~~~

.. py:data:: test_mode
   :type: bool
   :value: False

   **Description**: Enable test mode (no data sent to HoneyHive)
   
   **Environment Variable**: ``HH_TEST_MODE``
   
   **Default**: ``False``
   
   **Values**: ``true``, ``false``
   
   **Use Cases**:
   - Unit testing
   - Development environments
   - CI/CD pipelines

.. py:data:: debug
   :type: bool
   :value: False

   **Description**: Enable debug logging
   
   **Environment Variable**: ``HH_DEBUG``
   
   **Default**: ``False``
   
   **Values**: ``true``, ``false``
   
   **Behavior**: Enables verbose logging and debug information

Performance Configuration
-------------------------

HTTP Configuration
~~~~~~~~~~~~~~~~~~

.. py:data:: timeout
   :type: float
   :value: 30.0

   **Description**: HTTP request timeout in seconds
   
   **Environment Variable**: ``HH_TIMEOUT``
   
   **Default**: ``30.0``
   
   **Range**: 1.0 - 300.0
   
   **Use Cases**: Adjust based on network conditions and latency requirements

.. py:data:: max_retries
   :type: int
   :value: 3

   **Description**: Maximum number of retry attempts for failed requests
   
   **Environment Variable**: ``HH_MAX_RETRIES``
   
   **Default**: ``3``
   
   **Range**: 0 - 10
   
   **Behavior**: Exponential backoff between retries

.. py:data:: retry_delay
   :type: float
   :value: 1.0

   **Description**: Initial retry delay in seconds
   
   **Environment Variable**: ``HH_RETRY_DELAY``
   
   **Default**: ``1.0``
   
   **Range**: 0.1 - 60.0
   
   **Behavior**: Delay doubles with each retry (exponential backoff)

.. py:data:: max_connections
   :type: int
   :value: 100

   **Description**: Maximum number of HTTP connections in pool
   
   **Environment Variable**: ``HH_MAX_CONNECTIONS``
   
   **Default**: ``100``
   
   **Range**: 1 - 1000
   
   **Use Cases**: Adjust based on concurrency requirements

.. py:data:: connection_pool_size
   :type: int
   :value: 10

   **Description**: HTTP connection pool size
   
   **Environment Variable**: ``HH_CONNECTION_POOL_SIZE``
   
   **Default**: ``10``
   
   **Range**: 1 - 100

Tracing Configuration
~~~~~~~~~~~~~~~~~~~~~

.. py:data:: disable_http_tracing
   :type: bool
   :value: False

   **Description**: Disable automatic HTTP request tracing
   
   **Environment Variable**: ``HH_DISABLE_HTTP_TRACING``
   
   **Default**: ``False``
   
   **Use Cases**: 
   - Lambda environments (performance optimization)
   - Reduce tracing overhead
   - Prevent recursive tracing

.. py:data:: batch_size
   :type: int
   :value: 100

   **Description**: Number of spans to batch before sending
   
   **Environment Variable**: ``HH_BATCH_SIZE``
   
   **Default**: ``100``
   
   **Range**: 1 - 1000
   
   **Trade-offs**: 
   - Larger batches: Better performance, higher memory usage
   - Smaller batches: Lower latency, more network calls

.. py:data:: flush_interval
   :type: float
   :value: 5.0

   **Description**: Automatic flush interval in seconds
   
   **Environment Variable**: ``HH_FLUSH_INTERVAL``
   
   **Default**: ``5.0``
   
   **Range**: 1.0 - 300.0
   
   **Behavior**: Automatically flushes pending spans at this interval

.. py:data:: max_queue_size
   :type: int
   :value: 2048

   **Description**: Maximum number of spans in memory queue
   
   **Environment Variable**: ``HH_MAX_QUEUE_SIZE``
   
   **Default**: ``2048``
   
   **Range**: 100 - 10000
   
   **Behavior**: Oldest spans are dropped when queue is full

Evaluation Configuration
------------------------

Evaluation Settings
~~~~~~~~~~~~~~~~~~~

.. py:data:: evaluation_enabled
   :type: bool
   :value: True

   **Description**: Enable automatic evaluations
   
   **Environment Variable**: ``HH_EVALUATION_ENABLED``
   
   **Default**: ``True``
   
   **Use Cases**: Disable in high-performance scenarios

.. py:data:: evaluation_timeout
   :type: float
   :value: 30.0

   **Description**: Timeout for evaluation operations in seconds
   
   **Environment Variable**: ``HH_EVALUATION_TIMEOUT``
   
   **Default**: ``30.0``
   
   **Range**: 5.0 - 300.0

.. py:data:: evaluation_parallel
   :type: bool
   :value: True

   **Description**: Run evaluations in parallel
   
   **Environment Variable**: ``HH_EVALUATION_PARALLEL``
   
   **Default**: ``True``
   
   **Performance**: Parallel execution improves throughput

.. py:data:: evaluation_max_workers
   :type: int
   :value: 4

   **Description**: Maximum parallel evaluation workers
   
   **Environment Variable**: ``HH_EVALUATION_MAX_WORKERS``
   
   **Default**: ``4``
   
   **Range**: 1 - 20

Default Evaluators
~~~~~~~~~~~~~~~~~~

.. py:data:: default_evaluators
   :type: List[str]
   :value: []

   **Description**: Default evaluators to run automatically
   
   **Environment Variable**: ``HH_DEFAULT_EVALUATORS`` (comma-separated)
   
   **Default**: ``[]`` (no automatic evaluators)
   
   **Available Evaluators**:
   - ``"quality"`` - Overall response quality
   - ``"factual_accuracy"`` - Factual correctness
   - ``"relevance"`` - Query relevance
   - ``"toxicity"`` - Content safety
   - ``"length"`` - Response length appropriateness
   
   **Example**: ``"quality,factual_accuracy,relevance"``

Logging Configuration
---------------------

Log Settings
~~~~~~~~~~~~

.. py:data:: log_level
   :type: str
   :value: "INFO"

   **Description**: Logging level for SDK operations
   
   **Environment Variable**: ``HH_LOG_LEVEL``
   
   **Default**: ``"INFO"``
   
   **Values**: ``"DEBUG"``, ``"INFO"``, ``"WARNING"``, ``"ERROR"``, ``"CRITICAL"``
   
   **Behavior**: Controls verbosity of SDK logging

.. py:data:: log_format
   :type: str
   :value: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

   **Description**: Log message format
   
   **Environment Variable**: ``HH_LOG_FORMAT``
   
   **Default**: Standard format with timestamp, logger name, level, and message
   
   **Format**: Python logging format string

.. py:data:: log_file
   :type: str
   :value: None

   **Description**: Log file path (if file logging enabled)
   
   **Environment Variable**: ``HH_LOG_FILE``
   
   **Default**: ``None`` (console logging only)
   
   **Example**: ``"/var/log/honeyhive.log"``

.. py:data:: structured_logging
   :type: bool
   :value: False

   **Description**: Enable structured JSON logging
   
   **Environment Variable**: ``HH_STRUCTURED_LOGGING``
   
   **Default**: ``False``
   
   **Use Cases**: Production environments, log aggregation systems

Security Configuration
----------------------

Data Privacy
~~~~~~~~~~~~

.. py:data:: mask_inputs
   :type: bool
   :value: False

   **Description**: Automatically mask sensitive data in inputs
   
   **Environment Variable**: ``HH_MASK_INPUTS``
   
   **Default**: ``False``
   
   **Behavior**: Replaces sensitive data with ``[MASKED]``

.. py:data:: mask_outputs
   :type: bool
   :value: False

   **Description**: Automatically mask sensitive data in outputs
   
   **Environment Variable**: ``HH_MASK_OUTPUTS``
   
   **Default**: ``False``

.. py:data:: sensitive_keys
   :type: List[str]
   :value: ["password", "token", "key", "secret"]

   **Description**: Keys to automatically mask in data
   
   **Environment Variable**: ``HH_SENSITIVE_KEYS`` (comma-separated)
   
   **Default**: Common sensitive field names
   
   **Behavior**: Case-insensitive matching

SSL/TLS Configuration
~~~~~~~~~~~~~~~~~~~~~

.. py:data:: verify_ssl
   :type: bool
   :value: True

   **Description**: Verify SSL certificates for HTTPS requests
   
   **Environment Variable**: ``HH_VERIFY_SSL``
   
   **Default**: ``True``
   
   **Security**: Only disable for development/testing

.. py:data:: ca_bundle
   :type: str
   :value: None

   **Description**: Path to custom CA bundle for SSL verification
   
   **Environment Variable**: ``HH_CA_BUNDLE``
   
   **Default**: ``None`` (use system CA bundle)
   
   **Use Cases**: Corporate networks with custom certificates

Environment-Specific Configuration
----------------------------------

Development Environment
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # development.yaml
   api_key: "hh_dev_key_123..."
   base_url: "https://api-dev.honeyhive.ai"
   project: "my-app-dev"
   test_mode: false
   debug: true
   log_level: "DEBUG"
   
   # Performance (relaxed for development)
   timeout: 60.0
   batch_size: 10
   flush_interval: 1.0
   
   # Evaluation (enabled for testing)
   evaluation_enabled: true
   default_evaluators: ["quality", "relevance"]

Staging Environment
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # staging.yaml
   api_key: "hh_staging_key_456..."
   base_url: "https://api-staging.honeyhive.ai"
   project: "my-app-staging"
   test_mode: false
   debug: false
   log_level: "INFO"
   
   # Performance (production-like)
   timeout: 30.0
   batch_size: 100
   flush_interval: 5.0
   
   # Security (moderate)
   mask_inputs: false
   mask_outputs: false

Production Environment
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # production.yaml
   api_key: "hh_prod_key_789..."
   base_url: "https://api.honeyhive.ai"
   project: "my-app-prod"
   test_mode: false
   debug: false
   log_level: "WARNING"
   structured_logging: true
   
   # Performance (optimized)
   timeout: 15.0
   batch_size: 500
   flush_interval: 10.0
   max_queue_size: 5000
   
   # Security (strict)
   mask_inputs: true
   mask_outputs: true
   sensitive_keys: ["password", "token", "key", "secret", "api_key", "auth"]
   
   # Evaluation (selective)
   evaluation_enabled: true
   evaluation_timeout: 10.0
   default_evaluators: ["toxicity"]

Lambda/Serverless Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # lambda.yaml
   api_key: "hh_lambda_key_abc..."
   project: "my-lambda-app"
   test_mode: false
   log_level: "ERROR"
   
   # Performance (optimized for cold starts)
   disable_http_tracing: true
   timeout: 5.0
   batch_size: 1
   flush_interval: 1.0
   max_queue_size: 100
   
   # Evaluation (disabled for performance)
   evaluation_enabled: false

Configuration File Formats
--------------------------

YAML Configuration
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # honeyhive.yaml
   api_key: "hh_your_api_key_here"
   base_url: "https://api.honeyhive.ai"
   project: "my-project"
   source: "my-service"
   
   # Operational settings
   test_mode: false
   debug: false
   
   # Performance settings
   timeout: 30.0
   max_retries: 3
   batch_size: 100
   flush_interval: 5.0
   
   # Tracing settings
   disable_http_tracing: false
   max_queue_size: 2048
   
   # Evaluation settings
   evaluation_enabled: true
   evaluation_parallel: true
   evaluation_timeout: 30.0
   default_evaluators:
     - "quality"
     - "relevance"
   
   # Logging settings
   log_level: "INFO"
   structured_logging: false
   
   # Security settings
   mask_inputs: false
   mask_outputs: false
   sensitive_keys:
     - "password"
     - "token"
     - "key"
     - "secret"

JSON Configuration
~~~~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "api_key": "hh_your_api_key_here",
     "base_url": "https://api.honeyhive.ai",
     "project": "my-project",
     "source": "my-service",
     "test_mode": false,
     "debug": false,
     "timeout": 30.0,
     "max_retries": 3,
     "batch_size": 100,
     "flush_interval": 5.0,
     "disable_http_tracing": false,
     "max_queue_size": 2048,
     "evaluation_enabled": true,
     "evaluation_parallel": true,
     "evaluation_timeout": 30.0,
     "default_evaluators": ["quality", "relevance"],
     "log_level": "INFO",
     "structured_logging": false,
     "mask_inputs": false,
     "mask_outputs": false,
     "sensitive_keys": ["password", "token", "key", "secret"]
   }

Configuration Loading
---------------------

**File Discovery**:

The SDK searches for configuration files in this order:

1. ``./honeyhive.yaml`` (current directory)
2. ``./honeyhive.json`` (current directory)
3. ``~/.honeyhive/config.yaml`` (user home directory)
4. ``~/.honeyhive/config.json`` (user home directory)
5. ``/etc/honeyhive/config.yaml`` (system-wide)

**Environment-Specific Files**:

You can specify environment-specific configuration:

.. code-block:: bash

   # Set environment
   export HH_ENVIRONMENT=production
   
   # SDK will look for:
   # ./honeyhive.production.yaml
   # ~/.honeyhive/config.production.yaml

**Explicit Configuration File**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   # Load specific config file
   tracer = HoneyHiveTracer.init(config_file="./my-config.yaml")

Configuration Validation
------------------------

**Type Validation**:

All configuration values are validated for correct types:

.. code-block:: python

   # These will raise validation errors:
   timeout = "invalid"  # Must be float
   batch_size = -1      # Must be positive integer
   log_level = "INVALID" # Must be valid log level

**Range Validation**:

Numeric values are validated against acceptable ranges:

.. code-block:: python

   # These will raise validation errors:
   timeout = 0.0        # Must be >= 1.0
   batch_size = 10000   # Must be <= 1000
   max_retries = -1     # Must be >= 0

**Format Validation**:

String values are validated for correct format:

.. code-block:: python

   # These will raise validation errors:
   api_key = "invalid"         # Must start with "hh_"
   log_level = "invalid"       # Must be valid log level
   base_url = "not-a-url"      # Must be valid URL

Configuration Best Practices
----------------------------

**Security**:

1. **Never commit API keys** to version control
2. **Use environment variables** for secrets in production
3. **Enable input/output masking** for sensitive data
4. **Use different API keys** for different environments

**Performance**:

1. **Tune batch size** based on your traffic patterns
2. **Adjust timeout** based on your network conditions
3. **Disable HTTP tracing** in high-performance scenarios
4. **Use appropriate queue sizes** for your memory constraints

**Reliability**:

1. **Set appropriate retry limits** for your use case
2. **Configure timeouts** to prevent hanging operations
3. **Enable debug logging** during development
4. **Use structured logging** in production

**Monitoring**:

1. **Enable appropriate log levels** for your environment
2. **Monitor queue sizes** and flush intervals
3. **Track configuration changes** in your deployment pipeline
4. **Use health checks** to validate configuration

Configuration Examples
----------------------

**High-Performance Web Service**:

.. code-block:: yaml

   # High-throughput configuration
   batch_size: 1000
   flush_interval: 10.0
   max_queue_size: 10000
   timeout: 5.0
   max_retries: 1
   disable_http_tracing: true
   evaluation_enabled: false

**Development Environment**:

.. code-block:: yaml

   # Development-friendly configuration
   debug: true
   log_level: "DEBUG"
   test_mode: true
   batch_size: 1
   flush_interval: 1.0
   evaluation_enabled: true
   default_evaluators: ["quality", "factual_accuracy"]

**Security-Conscious Environment**:

.. code-block:: yaml

   # Security-focused configuration
   mask_inputs: true
   mask_outputs: true
   sensitive_keys: 
     - "password"
     - "token"
     - "key"
     - "secret"
     - "api_key"
     - "auth"
     - "credential"
   verify_ssl: true
   structured_logging: true

See Also
--------

- :doc:`environment-vars` - Environment variable details
- :doc:`authentication` - Authentication configuration
- :doc:`../api/tracer` - Tracer initialization with configuration
- :doc:`../cli/options` - CLI configuration options
