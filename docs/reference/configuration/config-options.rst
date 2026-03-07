Configuration Options Reference
===============================

.. note::
   **Complete reference for HoneyHive SDK configuration options**
   
   This document provides detailed specifications for all configuration options available in the HoneyHive SDK.

.. important::
   **🆕 NEW: Hybrid Configuration System**
   
   The HoneyHive SDK now supports a **hybrid configuration approach** that combines modern Pydantic config objects with full backwards compatibility. You can use either approach or mix them together.

The HoneyHive SDK supports multiple configuration approaches:

**🎯 Recommended Approaches (Choose One)**:

1. **Modern Pydantic Config Objects** (Recommended for new code)
2. **Traditional Parameter Passing** (Backwards compatible)
3. **Mixed Approach** (Config objects + parameter overrides)

**📚 Additional Configuration Sources**:

- Environment variables (``HH_*`` prefixed)

Configuration Methods
---------------------

.. tabs::

   .. tab:: 🆕 Modern Config Objects (Recommended)

      **Type-safe, validated configuration with IDE support:**

      .. code-block:: python

         from honeyhive import HoneyHiveTracer
         from honeyhive.config.models import TracerConfig, SessionConfig
         
         # Create configuration objects
         config = TracerConfig(
             api_key="hh_1234567890abcdef",
             project="my-llm-project",
             session_name="user-chat-session",
             source="production",
             verbose=True,
             disable_http_tracing=True,
             test_mode=False
         )
         
         session_config = SessionConfig(
             inputs={"user_id": "123", "query": "Hello world"}
         )
         
         # Initialize with config objects
         tracer = HoneyHiveTracer(
             config=config,
             session_config=session_config
         )

      **Benefits**: Type safety, IDE autocomplete, validation, reduced argument count

   .. tab:: 🔄 Traditional Parameters (Backwards Compatible)

      **Existing code continues to work exactly as before:**

      .. code-block:: python

         from honeyhive import HoneyHiveTracer
         
         # This continues to work exactly as before
         tracer = HoneyHiveTracer(
             api_key="hh_1234567890abcdef",
             project="my-llm-project",
             session_name="user-chat-session",
             source="production",
             verbose=True,
             disable_http_tracing=True,
             test_mode=False
         )

      **Benefits**: No code changes required, familiar pattern

   .. tab:: 🔀 Mixed Approach

      **Config objects with parameter overrides (individual parameters take precedence):**

      .. code-block:: python

         from honeyhive import HoneyHiveTracer
         from honeyhive.config.models import TracerConfig
         
         # Base configuration
         config = TracerConfig(
             api_key="hh_1234567890abcdef",
             project="my-llm-project",
             source="production"
         )
         
         # Individual parameters override config values
         tracer = HoneyHiveTracer(
             config=config,
             verbose=True,  # Overrides config.verbose
             session_name="override-session"  # Additional parameter
         )

      **Benefits**: Flexible configuration with selective overrides

Configuration Precedence
------------------------

The SDK follows this precedence order (highest to lowest):

1. **Individual Parameters** - Direct parameters to ``HoneyHiveTracer()``
2. **Config Object Values** - Values from ``TracerConfig`` objects
3. **Environment Variables** - ``HH_*`` environment variables
4. **Default Values** - Built-in SDK defaults

.. note::
   Individual parameters (directly passed to ``HoneyHiveTracer()``) always take precedence over config object values, which take precedence over environment variables.

.. seealso::
   **📖 Complete Hybrid Configuration Guide**
   
   For detailed examples, advanced patterns, and comprehensive usage scenarios, see :doc:`hybrid-config-approach`.

Configuration Classes
---------------------

.. py:class:: honeyhive.config.models.TracerConfig
   :no-index:

   **Primary configuration class for HoneyHive tracer initialization.**

   Inherits common fields from :py:class:`BaseHoneyHiveConfig` and adds tracer-specific parameters.

   **Key Features**:
   
   - Type-safe Pydantic validation
   - Environment variable loading via ``AliasChoices``
   - Graceful degradation on invalid values
   - IDE autocomplete support

   **Example**:

   .. code-block:: python

      from honeyhive.config.models import TracerConfig
      
      config = TracerConfig(
          api_key="hh_1234567890abcdef",
          project="my-llm-project",
          source="production",
          verbose=True
      )

.. py:class:: honeyhive.config.models.BaseHoneyHiveConfig
   :no-index:

   **Base configuration class with common fields shared across all HoneyHive components.**

   **Common Fields**: ``api_key``, ``project``, ``test_mode``, ``verbose``

.. py:class:: honeyhive.config.models.SessionConfig
   :no-index:

   **Session-specific configuration for tracer initialization.**

   **Key Fields**: ``session_id``, ``inputs``, ``link_carrier``

.. py:class:: honeyhive.config.models.APIClientConfig
   :no-index:

   **Configuration for HoneyHive API client settings.**

.. py:class:: honeyhive.config.models.HTTPClientConfig
   :no-index:

   **HTTP client configuration including connection pooling and retry settings.**

Core Configuration Options
--------------------------

The following options are available through both traditional parameters and config objects:

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

   **Usage Examples**:

   .. tabs::

      .. tab:: Config Object

         .. code-block:: python

            from honeyhive.config.models import TracerConfig
            
            config = TracerConfig(api_key="hh_1234567890abcdef")
            tracer = HoneyHiveTracer(config=config)

      .. tab:: Traditional Parameter

         .. code-block:: python

            tracer = HoneyHiveTracer(api_key="hh_1234567890abcdef")

      .. tab:: Environment Variable

         .. code-block:: bash

            export HH_API_KEY="hh_1234567890abcdef"

         .. code-block:: python

            # API key loaded automatically from environment
            tracer = HoneyHiveTracer(project="my-project")

.. py:data:: server_url
   :type: str
   :value: "https://api.honeyhive.ai"

   **Description**: HoneyHive API server URL

   **Environment Variable**: ``HH_API_URL``
   
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

   **Description**: Default project name for operations. Required field that must match your HoneyHive project.
   
   **Environment Variable**: ``HH_PROJECT``
   
   **Required**: Yes
   
   **Format**: Alphanumeric with hyphens and underscores
   
   **Example**: ``"my-llm-application"``
   
   **Validation**: 1-100 characters, cannot start/end with special characters

.. py:data:: source
   :type: str
   :value: "dev"

   **Description**: Source identifier for tracing
   
   **Environment Variable**: ``HH_SOURCE``
   
   **Default**: ``"dev"``
   
   **Examples**:
   - ``"chat-service"``
   - ``"recommendation-engine"``
   - ``"data-pipeline"``

.. py:data:: session_name
   :type: str
   :value: None

   **Description**: Optional session name for tracing
   
   **Environment Variable**: None (set via constructor parameter only)
   
   **Default**: ``None``
   
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

.. py:data:: max_connections
   :type: int
   :value: 10

   **Description**: Maximum number of HTTP connections in pool
   
   **Environment Variable**: ``HH_MAX_CONNECTIONS``
   
   **Default**: ``10``
   
   **Range**: 1 - 1000
   
   **Use Cases**: Adjust based on concurrency requirements

.. py:data:: max_keepalive_connections
   :type: int
   :value: 20

   **Description**: Maximum keep-alive HTTP connections
   
   **Environment Variable**: ``HH_MAX_KEEPALIVE_CONNECTIONS``
   
   **Default**: ``20``
   
   **Range**: 1 - 1000

.. py:data:: pool_timeout
   :type: float
   :value: 10.0

   **Description**: Time to wait for an available connection from the pool
   
   **Environment Variable**: ``HH_POOL_TIMEOUT``
   
   **Default**: ``10.0``

OTLP Configuration
~~~~~~~~~~~~~~~~~~

.. py:data:: otlp_enabled
   :type: bool
   :value: True

   **Description**: Enable OTLP export to HoneyHive backend
   
   **Environment Variable**: ``HH_OTLP_ENABLED``
   
   **Default**: ``True``
   
   **Usage**: Set to ``False`` to disable OTLP export (useful for testing)

.. py:data:: otlp_endpoint
   :type: Optional[str]
   :value: None

   **Description**: Custom OTLP endpoint URL
   
   **Environment Variable**: ``HH_OTLP_ENDPOINT``
   
   **Default**: Auto-configured based on ``server_url``
   
   **Example**: ``"https://custom.honeyhive.ai/opentelemetry/v1/traces"``

.. py:data:: otlp_protocol
   :type: str
   :value: "http/protobuf"

   **Description**: OTLP protocol format for span export
   
   **Environment Variables**: ``HH_OTLP_PROTOCOL`` or ``OTEL_EXPORTER_OTLP_PROTOCOL``
   
   **Valid Values**:
   - ``"http/protobuf"`` (default) - Binary Protobuf format
   - ``"http/json"`` - JSON format for debugging and backend type conversion testing
   
   **Example**: Set ``HH_OTLP_PROTOCOL=http/json`` to use JSON format

.. py:data:: otlp_headers
   :type: Optional[Dict[str, Any]]
   :value: None

   **Description**: Additional HTTP headers for OTLP export requests
   
   **Environment Variable**: ``HH_OTLP_HEADERS`` (JSON string)
   
   **Example**: ``{"X-Custom-Header": "value"}``

Tracing Configuration
~~~~~~~~~~~~~~~~~~~~~

.. py:data:: disable_http_tracing
   :type: bool
   :value: True

   **Description**: Disable automatic HTTP request tracing (opt-in feature)
   
   **Environment Variable**: ``HH_DISABLE_HTTP_TRACING``
   
   **Default**: ``True`` (HTTP tracing disabled by default for performance)
   
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

OpenTelemetry Span Limits
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
   **🆕 NEW in v1.0**: Configurable span limits with automatic core attribute preservation
   
   These settings control OpenTelemetry span size limits. **The SDK defaults are optimized for 95% of use cases** - only increase limits when you actually hit them, not preemptively.

.. py:data:: max_attributes
   :type: int
   :value: 1024

   **Description**: Maximum number of attributes (key-value pairs) per span
   
   **Environment Variable**: ``HH_MAX_ATTRIBUTES``
   
   **Default**: ``1024`` (**recommended** - optimized for LLM workloads)
   
   **Backend Maximum**: ``10,000`` (supported for edge cases only)
   
   **OpenTelemetry Default**: ``128`` (SDK increases this 8x for LLM workloads)
   
   **Range**: 128 - 10,000
   
   **⚠️ Important**: The default of 1024 is **intentionally set to handle 95% of use cases**. Only increase this limit when you **actually encounter** "attribute limit exceeded" errors in production, not preemptively.
   
   **When You Might Need More**:
   - Large embeddings (>1MB) with extensive metadata
   - High-resolution image processing with detailed annotations
   - Complex multi-step chains with per-step metadata
   - Debug/development scenarios requiring verbose attribute capture
   
   **Trade-offs**:
   - **Higher limits**: Support larger payloads, more metadata
   - **Lower limits**: Reduced memory usage, faster serialization
   
   **Performance Impact**: Minimal (<1ms overhead) with lazy core attribute preservation
   
   **Important**: When limit is exceeded, OpenTelemetry uses FIFO eviction (oldest attributes dropped first). The SDK automatically preserves critical attributes (``session_id``, ``event_type``, ``event_name``, ``source``) when spans approach the limit.

   **Example**:

   .. code-block:: python

      from honeyhive.config.models import TracerConfig
      from honeyhive import HoneyHiveTracer
      
      # Default: 1024 attributes (recommended)
      tracer = HoneyHiveTracer.init(
          api_key="hh_...",
          project="my-project"
      )
      
      # Increased for large embeddings
      config = TracerConfig(
          api_key="hh_...",
          project="my-project",
          max_attributes=5000  # Increase to 5000
      )
      tracer = HoneyHiveTracer(config=config)
      
      # Or via environment variable
      # export HH_MAX_ATTRIBUTES=5000

.. py:data:: max_events
   :type: int
   :value: 1024

   **Description**: Maximum number of events per span
   
   **Environment Variable**: ``HH_MAX_EVENTS``
   
   **Default**: ``1024`` (conservative SDK default)
   
   **Backend Maximum**: ``10,000`` (increase if needed)
   
   **OpenTelemetry Default**: ``128`` (SDK increases this 8x)
   
   **Range**: 128 - 10,000
   
   **Use Cases**:
   - **Default (1024)**: Most LLM applications with typical event counts
   - **Increased (2000-5000)**: High-frequency logging, detailed trace events
   - **Maximum (10,000)**: Debug scenarios, comprehensive event capture
   
   **Note**: Events are flattened to pseudo-attributes (``_event.0.*``, ``_event.1.*``, etc.) by the ingestion service, so they count toward effective attribute limit.
   
   **Trade-offs**:
   - **Higher limits**: Capture more detailed execution flow
   - **Lower limits**: Reduced network payload size
   
   **Example**:

   .. code-block:: python

      # Increase for high-frequency event logging
      config = TracerConfig(
          api_key="hh_...",
          project="my-project",
          max_events=3000
      )

.. py:data:: max_links
   :type: int
   :value: 128

   **Description**: Maximum number of span links per span (for distributed tracing)
   
   **Environment Variable**: ``HH_MAX_LINKS``
   
   **Default**: ``128`` (typically sufficient)
   
   **Backend Maximum**: ``10,000`` (rarely needed)
   
   **OpenTelemetry Default**: ``128`` (SDK uses standard default)
   
   **Range**: 1 - 10,000
   
   **Use Cases**:
   - **Default (128)**: Standard distributed tracing scenarios
   - **Increased (500+)**: Complex microservice architectures, fan-out patterns
   
   **Note**: Span links are used for distributed tracing to link spans across service boundaries. Most applications don't need more than the default.
   
   **Example**:

   .. code-block:: python

      # Increase for complex distributed systems
      config = TracerConfig(
          api_key="hh_...",
          project="my-project",
          max_links=500
      )

.. py:data:: max_span_size
   :type: int
   :value: 10485760

   **Description**: Maximum total span size in bytes (attributes + events + links combined)
   
   **Environment Variable**: ``HH_MAX_SPAN_SIZE``
   
   **Default**: ``10485760`` (10 MB - **recommended** for most use cases)
   
   **Backend Maximum**: ``104857600`` (100 MB - supported for edge cases only)
   
   **Range**: 1,048,576 - 104,857,600 (1 MB - 100 MB)
   
   **⚠️ Important**: The default of 10 MB is **sufficient for 95% of applications** including small-to-medium images, embeddings, and typical LLM metadata. Only increase when you **actually encounter** "span size exceeded" errors.
   
   **When You Might Need More**:
   - High-resolution images (>10 MB each)
   - Audio/video file processing (>10 MB payloads)
   - Scientific computing with large matrices/tensors
   - Debug scenarios capturing extensive state
   
   **Important**: This is a **total span size limit** enforced in-memory before serialization. OpenTelemetry doesn't provide this natively, so the SDK implements custom size tracking.
   
   **Trade-offs**:
   - **Higher limits**: Support larger payloads (images, audio, video)
   - **Lower limits**: Reduced memory usage, faster network transmission
   
   **Performance Impact**: Size checking adds ~0.001ms overhead per span
   
   **Span Size Breakdown**:

   - **Attributes**: Each key-value pair (~100-1000 bytes typical)
   - **Events**: Each event with data (~50-500 bytes typical)
   - **Links**: Each link reference (~100 bytes typical)
   - **Large Data**: Images (100KB-10MB), embeddings (1KB-100KB), audio (1MB-50MB)
   
   **Example**:

   .. code-block:: python

      # Default: 10 MB
      tracer = HoneyHiveTracer.init(
          api_key="hh_...",
          project="my-project"
      )
      
      # Increased for image processing
      config = TracerConfig(
          api_key="hh_...",
          project="my-project",
          max_span_size=52428800  # 50 MB
      )
      
      # Maximum for video/audio processing
      config = TracerConfig(
          api_key="hh_...",
          project="my-project",
          max_span_size=104857600  # 100 MB (backend max)
      )

.. py:data:: preserve_core_attributes
   :type: bool
   :value: True

   **Description**: Enable automatic preservation of critical attributes to prevent data loss
   
   **Environment Variable**: ``HH_PRESERVE_CORE_ATTRIBUTES``
   
   **Default**: ``True`` (enabled - **strongly recommended**)
   
   **Behavior**: When spans approach the attribute limit (95% threshold), the SDK automatically re-sets critical attributes just before ``span.end()`` to ensure they survive OpenTelemetry's FIFO eviction policy.
   
   **Critical Attributes Protected**:
   
   - ``session_id`` (CRITICAL - required for backend ingestion)
   - ``source`` (CRITICAL - required for backend routing)
   - ``event_type`` (HIGH - required for span classification)
   - ``event_name`` (HIGH - required for span identification)
   - ``project`` (NORMAL - required for project routing)
   - ``config`` (NORMAL - optional configuration name)
   
   **Why This Matters**:
   
   OpenTelemetry uses strict FIFO (First-In-First-Out) eviction when spans exceed attribute limits. Without preservation:
   
   1. Critical attributes set early (like ``session_id``) get evicted first
   2. Backend rejects spans missing required attributes
   3. **Data loss occurs silently**
   
   With preservation enabled:
   
   1. SDK monitors attribute count per span
   2. When span reaches 95% of limit, preservation activates
   3. Critical attributes are re-set LAST (become newest)
   4. Critical attributes survive eviction, span is accepted
   
   **Performance Impact**:
   
   - **Normal spans** (<95% of limit): **Zero overhead**
   - **Large spans** (>95% of limit): **~0.5ms overhead** (lazy activation)
   - **Memory**: Negligible (only attributes checked, not copied)
   
   **When to Disable**:
   
   - ⚠️ **Never in production** - high risk of data loss
   - Debugging OpenTelemetry behavior
   - Performance profiling (measure raw OTel overhead)
   - Testing attribute eviction scenarios
   
   **Example**:

   .. code-block:: python

      # Default: Enabled (recommended)
      tracer = HoneyHiveTracer.init(
          api_key="hh_...",
          project="my-project"
      )
      
      # Explicitly enable (redundant but clear)
      config = TracerConfig(
          api_key="hh_...",
          project="my-project",
          preserve_core_attributes=True
      )
      
      # ⚠️ Disable only for debugging (NOT for production)
      config = TracerConfig(
          api_key="hh_...",
          project="my-project",
          preserve_core_attributes=False  # RISKY: Can cause data loss
      )

.. important::
   **Span Limit Configuration Best Practices**
   
   1. **Use the defaults** (1024 attrs, 10MB) - optimized for 95% of use cases
   2. **Don't preemptively increase limits** - only adjust when you hit actual errors
   3. **Monitor in production** - use HoneyHive dashboard to track span sizes
   4. **Keep preservation enabled** - prevents silent data loss from FIFO eviction
   5. **Increase incrementally** - if needed, increase by 2-3x, not to maximum
   6. **Higher limits = higher costs** - larger spans mean more memory, network, and storage
   
   **Common Configuration Scenarios**:

   .. code-block:: python

      # Scenario 1: Standard LLM application (RECOMMENDED - use defaults)
      config = TracerConfig(
          api_key="hh_...",
          project="my-project"
          # Uses defaults: 1024 attrs, 10MB, preservation ON
          # This handles 95% of use cases
      )
      
      # Scenario 2: Image processing (only if hitting limits)
      config = TracerConfig(
          api_key="hh_...",
          project="image-pipeline",
          max_attributes=2048,       # 2x increase (not 10x)
          max_span_size=20971520     # 20 MB (2x increase, not 100 MB)
      )
      
      # Scenario 3: High-resolution media (rare edge case)
      config = TracerConfig(
          api_key="hh_...",
          project="media-pipeline",
          max_attributes=3000,       # 3x increase
          max_span_size=52428800     # 50 MB (5x increase)
      )
      
      # ⚠️ Scenario 4: Maximum limits (ONLY for extreme edge cases)
      # WARNING: Higher memory usage, network costs, and processing time
      config = TracerConfig(
          api_key="hh_...",
          project="scientific-computing",
          max_attributes=10000,      # Backend maximum (use sparingly)
          max_span_size=104857600,   # Backend maximum (100 MB)
          verbose=True
      )
      # Only use maximum limits if:
      # - You've verified you actually need them
      # - You've tested memory/network impact
      # - You understand the cost implications

.. seealso::
   **Related Documentation**
   
   - :doc:`/reference/api/tracer` - Tracer initialization with span limits
   - :doc:`/reference/api/config-models` - Configuration model API reference

HTTP Transport Controls
-----------------------

.. py:data:: verify_ssl
   :type: bool
   :value: True

   **Description**: Verify SSL certificates for HTTPS requests
   
   **Environment Variable**: ``HH_VERIFY_SSL``
   
   **Default**: ``True``
   
   **Security**: Only disable for development/testing

.. py:data:: follow_redirects
   :type: bool
   :value: True

   **Description**: Follow HTTP redirects for API requests
   
   **Environment Variable**: ``HH_FOLLOW_REDIRECTS``
   
   **Default**: ``True``

.. py:data:: http_proxy
   :type: Optional[str]
   :value: None

   **Description**: HTTP proxy URL for outbound API traffic
   
   **Environment Variable**: ``HH_HTTP_PROXY``

.. py:data:: https_proxy
   :type: Optional[str]
   :value: None

   **Description**: HTTPS proxy URL for outbound API traffic
   
   **Environment Variable**: ``HH_HTTPS_PROXY``

.. py:data:: no_proxy
   :type: Optional[str]
   :value: None

   **Description**: Comma-separated hosts that should bypass proxy routing
   
   **Environment Variable**: ``HH_NO_PROXY``



Configuration Validation
------------------------

**Type Validation**:

All configuration values are validated for correct types:

.. code-block:: python

   # These will raise validation errors:
   timeout = "invalid"   # Must be float
   batch_size = -1       # Must be positive integer

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
   api_key = "invalid"          # Must start with "hh_"
   server_url = "not-a-url"     # Must be a valid URL

Configuration Best Practices
----------------------------

**Security**:

1. **Never commit API keys** to version control
2. **Use environment variables** for secrets in production
3. **Keep transport security enabled** unless you are debugging a local environment
4. **Use different API keys** for different environments

**Performance**:

1. **Tune batch size** based on your traffic patterns
2. **Adjust timeout** based on your network conditions
3. **Disable HTTP tracing** in high-performance scenarios
4. **Size connection pools** to match expected concurrency

**Reliability**:

1. **Set appropriate retry limits** for your use case
2. **Configure timeouts** to prevent hanging operations
3. **Configure flush intervals** appropriately for your environment

**Monitoring**:

1. **Track configuration changes** in your deployment pipeline
2. **Use health checks** to validate configuration


See Also
--------

- :doc:`environment-vars` - Environment variable details
- :doc:`authentication` - Authentication configuration
- :doc:`../api/tracer` - Tracer initialization with configuration
