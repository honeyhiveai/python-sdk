============================
Configuration Models API
============================

.. meta::
   :description: Complete API reference for HoneyHive SDK's Pydantic configuration models
   :keywords: configuration models, Pydantic, TracerConfig, BaseHoneyHiveConfig, type safety

Overview
========

The HoneyHive SDK provides **type-safe Pydantic configuration models** that enable modern, validated configuration with IDE autocomplete support and graceful degradation.

.. contents:: Table of Contents
   :local:
   :depth: 3

.. currentmodule:: honeyhive.config.models

Base Configuration Classes
==========================

BaseHoneyHiveConfig
-------------------

.. autoclass:: BaseHoneyHiveConfig
   :members:
   :undoc-members:
   :show-inheritance:

**Base configuration class with common fields shared across all HoneyHive components.**

**Key Features:**

- **Environment Variable Loading**: Automatic loading via ``AliasChoices``
- **Type Safety**: Full Pydantic v2 validation
- **Graceful Degradation**: Invalid values replaced with safe defaults
- **IDE Support**: Complete autocomplete and type checking

**Common Fields:**

.. py:attribute:: api_key
   :type: str

   HoneyHive API key for authentication.
   
   **Environment Variable**: ``HH_API_KEY``
   
   **Required**: Yes
   
   **Format**: String starting with ``hh_``

.. py:attribute:: project
   :type: str

   Project name (required by backend API).
   
   **Environment Variable**: ``HH_PROJECT``
   
   **Required**: Yes

.. py:attribute:: test_mode
   :type: bool
   :value: False

   Enable test mode (no data sent to backend).
   
   **Environment Variable**: ``HH_TEST_MODE``

.. py:attribute:: verbose
   :type: bool
   :value: False

   Enable verbose logging output.
   
   **Environment Variable**: ``HH_VERBOSE``

**Example Usage:**

.. code-block:: python

   from honeyhive.config.models import BaseHoneyHiveConfig
   
   # Direct instantiation
   config = BaseHoneyHiveConfig(
       api_key="hh_1234567890abcdef",
       project="my-project",
       verbose=True
   )
   
   # Environment variable loading
   import os
   os.environ["HH_API_KEY"] = "hh_1234567890abcdef"
   os.environ["HH_PROJECT"] = "my-project"
   
   config = BaseHoneyHiveConfig()  # Loads from environment

Domain-Specific Configuration Classes
=====================================

TracerConfig
------------

.. autoclass:: TracerConfig
   :members:
   :undoc-members:
   :show-inheritance:

**Primary configuration class for HoneyHive tracer initialization.**

Inherits all fields from :py:class:`BaseHoneyHiveConfig` and adds tracer-specific parameters.

**Tracer-Specific Fields:**

.. py:attribute:: source
   :type: str
   :value: "dev"

   Source environment identifier.
   
   **Environment Variable**: ``HH_SOURCE``
   
   **Examples**: ``"production"``, ``"staging"``, ``"development"``

.. py:attribute:: server_url
   :type: str
   :value: "https://api.honeyhive.ai"

   Custom HoneyHive server URL.
   
   **Environment Variable**: ``HH_API_URL``

.. py:attribute:: disable_http_tracing
   :type: bool
   :value: True

   Disable automatic HTTP request tracing.
   
   **Environment Variable**: ``HH_DISABLE_HTTP_TRACING``

.. py:attribute:: disable_batch
   :type: bool
   :value: False

   Disable span batching for immediate export.
   
   **Environment Variable**: ``HH_DISABLE_BATCH``

.. py:attribute:: disable_tracing
   :type: bool
   :value: False

   Completely disable tracing (emergency override).
   
   **Environment Variable**: ``HH_DISABLE_TRACING``

.. py:attribute:: cache_enabled
   :type: bool
   :value: True

   Enable response caching.
   
   **Environment Variable**: ``HH_CACHE_ENABLED``

.. py:attribute:: cache_max_size
   :type: int
   :value: 1000

   Maximum cache size (number of entries).
   
   **Environment Variable**: ``HH_CACHE_MAX_SIZE``

.. py:attribute:: cache_ttl
   :type: int
   :value: 3600

   Cache time-to-live in seconds.
   
   **Environment Variable**: ``HH_CACHE_TTL``

.. py:attribute:: cache_cleanup_interval
   :type: int
   :value: 300

   Cache cleanup interval in seconds.
   
   **Environment Variable**: ``HH_CACHE_CLEANUP_INTERVAL``

**Example Usage:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from honeyhive.config.models import TracerConfig
   
   # Full configuration
   config = TracerConfig(
       api_key="hh_1234567890abcdef",
       project="my-llm-project",
       source="production",
       verbose=True,
       disable_http_tracing=False,
       cache_enabled=True,
       cache_max_size=2000
   )
   
   tracer = HoneyHiveTracer(config=config)

SessionConfig
-------------

.. autoclass:: SessionConfig
   :members:
   :undoc-members:
   :show-inheritance:

**Session-specific configuration for tracer initialization.**

**Session Fields:**

.. py:attribute:: session_name
   :type: Optional[str]
   :value: None

   Custom session name for grouping related traces.

.. py:attribute:: session_id
   :type: Optional[str]
   :value: None

   Explicit session identifier.

.. py:attribute:: inputs
   :type: Optional[Dict[str, Any]]
   :value: None

   Session input parameters.

.. py:attribute:: outputs
   :type: Optional[Dict[str, Any]]
   :value: None

   Session output parameters.

.. py:attribute:: metadata
   :type: Optional[Dict[str, Any]]
   :value: None

   Additional session metadata.

**Example Usage:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from honeyhive.config.models import TracerConfig, SessionConfig
   
   tracer_config = TracerConfig(
       api_key="hh_1234567890abcdef",
       project="my-project"
   )
   
   session_config = SessionConfig(
       session_name="user-chat-session",
       inputs={"user_id": "123", "query": "Hello world"},
       metadata={"version": "1.0", "environment": "production"}
   )
   
   tracer = HoneyHiveTracer(
       config=tracer_config,
       session_config=session_config
   )

EvaluationConfig
----------------

.. autoclass:: EvaluationConfig
   :members:
   :undoc-members:
   :show-inheritance:

**Evaluation-specific configuration parameters.**

**Evaluation Fields:**

.. py:attribute:: is_evaluation
   :type: bool
   :value: False

   Mark this as an evaluation run.

.. py:attribute:: run_id
   :type: Optional[str]
   :value: None

   Evaluation run identifier.

.. py:attribute:: dataset_id
   :type: Optional[str]
   :value: None

   Dataset identifier for evaluation.

.. py:attribute:: datapoint_id
   :type: Optional[str]
   :value: None

   Specific datapoint identifier.

**Example Usage:**

.. code-block:: python

   from honeyhive.config.models import EvaluationConfig
   
   eval_config = EvaluationConfig(
       is_evaluation=True,
       run_id="eval_run_123",
       dataset_id="dataset_456"
   )

APIClientConfig
---------------

.. autoclass:: APIClientConfig
   :members:
   :undoc-members:
   :show-inheritance:

**Configuration for HoneyHive API client settings.**

Inherits from :py:class:`BaseHoneyHiveConfig`.

**Example Usage:**

.. code-block:: python

   from honeyhive.config.models import APIClientConfig
   
   api_config = APIClientConfig(
       api_key="hh_1234567890abcdef",
       project="my-project",
       server_url="https://custom.honeyhive.com"
   )

HTTPClientConfig
----------------

.. autoclass:: HTTPClientConfig
   :members:
   :undoc-members:
   :show-inheritance:

**HTTP client configuration including connection pooling and retry settings.**

**HTTP Configuration Fields:**

.. py:attribute:: timeout
   :type: float
   :value: 30.0

   Request timeout in seconds.
   
   **Environment Variable**: ``HH_TIMEOUT``

.. py:attribute:: max_connections
   :type: int
   :value: 100

   Maximum number of HTTP connections.
   
   **Environment Variable**: ``HH_MAX_CONNECTIONS``

.. py:attribute:: max_keepalive_connections
   :type: int
   :value: 20

   Maximum number of keep-alive connections.
   
   **Environment Variable**: ``HH_MAX_KEEPALIVE_CONNECTIONS``

.. py:attribute:: keepalive_expiry
   :type: float
   :value: 30.0

   Keep-alive connection expiry time in seconds.
   
   **Environment Variable**: ``HH_KEEPALIVE_EXPIRY``

.. py:attribute:: pool_timeout
   :type: float
   :value: 10.0

   Connection pool timeout in seconds.
   
   **Environment Variable**: ``HH_POOL_TIMEOUT``

.. py:attribute:: rate_limit_calls
   :type: int
   :value: 100

   Rate limit: maximum calls per window.
   
   **Environment Variable**: ``HH_RATE_LIMIT_CALLS``

.. py:attribute:: rate_limit_window
   :type: int
   :value: 60

   Rate limit window in seconds.
   
   **Environment Variable**: ``HH_RATE_LIMIT_WINDOW``

.. py:attribute:: max_retries
   :type: int
   :value: 3

   Maximum number of retry attempts.
   
   **Environment Variable**: ``HH_MAX_RETRIES``

.. py:attribute:: http_proxy
   :type: Optional[str]
   :value: None

   HTTP proxy URL.
   
   **Environment Variable**: ``HTTP_PROXY``

.. py:attribute:: https_proxy
   :type: Optional[str]
   :value: None

   HTTPS proxy URL.
   
   **Environment Variable**: ``HTTPS_PROXY``

.. py:attribute:: no_proxy
   :type: Optional[str]
   :value: None

   Comma-separated list of hosts to bypass proxy.
   
   **Environment Variable**: ``NO_PROXY``

.. py:attribute:: verify_ssl
   :type: bool
   :value: True

   Enable SSL certificate verification.
   
   **Environment Variable**: ``HH_VERIFY_SSL``

.. py:attribute:: follow_redirects
   :type: bool
   :value: True

   Follow HTTP redirects.
   
   **Environment Variable**: ``HH_FOLLOW_REDIRECTS``

**Example Usage:**

.. code-block:: python

   from honeyhive.config.models import HTTPClientConfig
   
   http_config = HTTPClientConfig(
       timeout=60.0,
       max_connections=200,
       rate_limit_calls=200,
       rate_limit_window=60,
       http_proxy="http://proxy.company.com:8080"
   )

ExperimentConfig
----------------

.. autoclass:: ExperimentConfig
   :members:
   :undoc-members:
   :show-inheritance:

**Experiment-specific configuration parameters.**

**Experiment Fields:**

.. py:attribute:: experiment_id
   :type: Optional[str]
   :value: None

   Unique experiment identifier.
   
   **Environment Variable**: ``HH_EXPERIMENT_ID``

.. py:attribute:: experiment_name
   :type: Optional[str]
   :value: None

   Human-readable experiment name.
   
   **Environment Variable**: ``HH_EXPERIMENT_NAME``

.. py:attribute:: experiment_variant
   :type: Optional[str]
   :value: None

   Experiment variant identifier.
   
   **Environment Variable**: ``HH_EXPERIMENT_VARIANT``

.. py:attribute:: experiment_group
   :type: Optional[str]
   :value: None

   Experiment group for A/B testing.
   
   **Environment Variable**: ``HH_EXPERIMENT_GROUP``

.. py:attribute:: experiment_metadata
   :type: Optional[Dict[str, Any]]
   :value: None

   Additional experiment metadata.
   
   **Environment Variable**: ``HH_EXPERIMENT_METADATA`` (JSON string)

**Example Usage:**

.. code-block:: python

   from honeyhive.config.models import ExperimentConfig
   
   experiment_config = ExperimentConfig(
       experiment_id="exp_123",
       experiment_name="LLM Response Quality Test",
       experiment_variant="variant_a",
       experiment_group="control",
       experiment_metadata={"model": "gpt-4", "temperature": 0.7}
   )

OTLPConfig
----------

.. autoclass:: OTLPConfig
   :members:
   :undoc-members:
   :show-inheritance:

**OTLP (OpenTelemetry Protocol) export configuration parameters.**

**OTLP Fields:**

.. py:attribute:: otlp_enabled
   :type: bool
   :value: True

   Enable OTLP export.
   
   **Environment Variable**: ``HH_OTLP_ENABLED``

.. py:attribute:: otlp_endpoint
   :type: Optional[str]
   :value: None

   Custom OTLP endpoint URL.
   
   **Environment Variable**: ``HH_OTLP_ENDPOINT``

.. py:attribute:: otlp_headers
   :type: Optional[Dict[str, Any]]
   :value: None

   OTLP headers in JSON format.
   
   **Environment Variable**: ``HH_OTLP_HEADERS`` (JSON string)

.. py:attribute:: otlp_protocol
   :type: str
   :value: "http/protobuf"

   OTLP protocol format: ``"http/protobuf"`` (default) or ``"http/json"``.
   
   **Environment Variables**: ``HH_OTLP_PROTOCOL`` or ``OTEL_EXPORTER_OTLP_PROTOCOL``

.. py:attribute:: batch_size
   :type: int
   :value: 100

   OTLP batch size for performance optimization.
   
   **Environment Variable**: ``HH_BATCH_SIZE``

.. py:attribute:: flush_interval
   :type: float
   :value: 5.0

   OTLP flush interval in seconds.
   
   **Environment Variable**: ``HH_FLUSH_INTERVAL``

.. py:attribute:: max_export_batch_size
   :type: int
   :value: 512

   Maximum export batch size.
   
   **Environment Variable**: ``HH_MAX_EXPORT_BATCH_SIZE``

.. py:attribute:: export_timeout
   :type: float
   :value: 30.0

   Export timeout in seconds.
   
   **Environment Variable**: ``HH_EXPORT_TIMEOUT``

**Example Usage:**

.. code-block:: python

   from honeyhive.config.models import OTLPConfig
   
   # Use JSON format for OTLP export
   otlp_config = OTLPConfig(
       otlp_protocol="http/json",
       batch_size=200,
       flush_interval=1.0
   )
   
   # Or via environment variable
   # export HH_OTLP_PROTOCOL=http/json
   otlp_config = OTLPConfig()  # Loads from HH_OTLP_PROTOCOL

Environment Variable Integration
================================

All configuration models support **automatic environment variable loading** using Pydantic's ``AliasChoices`` feature.

**Environment Variable Patterns:**

- **Core Settings**: ``HH_API_KEY``, ``HH_PROJECT``, ``HH_SOURCE``
- **Operational**: ``HH_TEST_MODE``, ``HH_VERBOSE``, ``HH_DISABLE_TRACING``
- **Performance**: ``HH_TIMEOUT``, ``HH_MAX_CONNECTIONS``, ``HH_RATE_LIMIT_*``
- **Caching**: ``HH_CACHE_ENABLED``, ``HH_CACHE_MAX_SIZE``, ``HH_CACHE_TTL``
- **Experiments**: ``HH_EXPERIMENT_ID``, ``HH_EXPERIMENT_NAME``
- **OTLP**: ``HH_OTLP_ENABLED``, ``HH_OTLP_ENDPOINT``, ``HH_OTLP_PROTOCOL``, ``HH_OTLP_HEADERS``, ``HH_BATCH_SIZE``, ``HH_FLUSH_INTERVAL``

**Priority Order:**

1. **Direct Parameters**: Values passed to config constructors
2. **Environment Variables**: ``HH_*`` prefixed variables
3. **Default Values**: Built-in configuration defaults

**Example:**

.. code-block:: bash

   # Set environment variables
   export HH_API_KEY="hh_1234567890abcdef"
   export HH_PROJECT="my-project"
   export HH_VERBOSE="true"
   export HH_CACHE_MAX_SIZE="2000"

.. code-block:: python

   from honeyhive.config.models import TracerConfig
   
   # Loads all values from environment variables
   config = TracerConfig()
   
   # Override specific values
   config = TracerConfig(verbose=False)  # Overrides HH_VERBOSE

Error Handling and Validation
=============================

All configuration models use **Pydantic v2 validation** with graceful degradation:

**Validation Features:**

- **Type Safety**: Automatic type conversion and validation
- **Format Validation**: API key format, URL validation, UUID validation
- **Range Validation**: Numeric ranges, positive values
- **Graceful Degradation**: Invalid values replaced with safe defaults
- **Clear Error Messages**: Detailed validation error reporting

**API Key Validation:**

.. code-block:: python

   from honeyhive.config.models import TracerConfig
   
   # Valid API key
   config = TracerConfig(api_key="hh_1234567890abcdef")
   
   # Invalid API key - validation error with clear message
   try:
       config = TracerConfig(api_key="invalid_key")
   except ValueError as e:
       print(f"Validation error: {e}")

**URL Validation:**

.. code-block:: python

   # Valid URL
   config = TracerConfig(server_url="https://api.honeyhive.ai")
   
   # Invalid URL - graceful degradation to default
   config = TracerConfig(server_url="not-a-url")
   # config.server_url will be "https://api.honeyhive.ai"

**Numeric Validation:**

.. code-block:: python

   # Valid values
   config = TracerConfig(cache_max_size=1000, cache_ttl=3600)
   
   # Invalid values - graceful degradation
   config = TracerConfig(cache_max_size=-100, cache_ttl="invalid")
   # config.cache_max_size will be 1000 (default)
   # config.cache_ttl will be 3600 (default)

Migration from Legacy Configuration
===================================

The new configuration models provide **100% backwards compatibility** with existing parameter-based initialization:

**Legacy Pattern (Still Works):**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   tracer = HoneyHiveTracer(
       api_key="hh_1234567890abcdef",
       project="my-project",
       verbose=True,
       disable_http_tracing=True
   )

**Modern Pattern (Recommended):**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from honeyhive.config.models import TracerConfig
   
   config = TracerConfig(
       api_key="hh_1234567890abcdef",
       project="my-project",
       verbose=True,
       disable_http_tracing=True
   )
   
   tracer = HoneyHiveTracer(config=config)

**Mixed Pattern (Flexible):**

.. code-block:: python

   config = TracerConfig(
       api_key="hh_1234567890abcdef",
       project="my-project"
   )
   
   # Individual parameters override config values
   tracer = HoneyHiveTracer(
       config=config,
       verbose=True,  # Overrides config.verbose
       disable_http_tracing=True  # Overrides config.disable_http_tracing
   )

See Also
========

- :doc:`../configuration/hybrid-config-approach` - Complete hybrid configuration guide
- :doc:`../configuration/config-options` - Configuration options reference
- :doc:`tracer` - HoneyHiveTracer API reference
- :doc:`tracer-architecture` - Tracer architecture overview
