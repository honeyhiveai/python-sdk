================================
Hybrid Configuration Approach
================================

.. meta::
   :description: Comprehensive reference for HoneyHive SDK's hybrid configuration system with Pydantic models and backwards compatibility
   :keywords: configuration, pydantic, backwards compatibility, tracer initialization

Overview
========

The HoneyHive SDK implements a **hybrid configuration approach** that provides both modern, type-safe configuration objects and full backwards compatibility with existing parameter-based initialization.

This system addresses pylint R0913/R0917 "too many arguments" issues while maintaining 100% backwards compatibility with existing code.

.. contents:: Table of Contents
   :local:
   :depth: 3

Architecture
============

The configuration system is organized into two main components:

1. **Runtime Configuration** (``global_config.py``) - SDK-wide settings with environment variable loading
2. **Domain Models** (``config/models/``) - Pydantic models for initialization and validation

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#ffffff', 'lineColor': '#ffffff', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'tertiaryColor': 'transparent', 'clusterBkg': 'transparent', 'clusterBorder': '#ffffff', 'edgeLabelBackground': 'transparent', 'background': 'transparent'}, 'flowchart': {'linkColor': '#ffffff', 'linkWidth': 2}}}%%
   graph TB
       subgraph "Configuration Class Hierarchy"
           A[BaseHoneyHiveConfig]
           A --> B[TracerConfig]
           A --> C[SessionConfig]  
           A --> D[EvaluationConfig]
           A --> E[APIClientConfig]
           
           SM[ServerURLMixin] --> B
           SM --> E
           
           HC[HTTPClientConfig]
           EC[ExperimentConfig]
       end
       
       subgraph "HoneyHiveTracer Initialization"
           F[HoneyHiveTracer] --> G{Initialization Method}
           G -->|Traditional| H[Individual Parameters]
           G -->|Modern| I[Config Objects]
           G -->|Mixed| J[Config + Parameter Overrides]
           
           I --> B
           I --> C
           I --> D
       end
       
       H --> K[merge_configs_with_params]
       I --> K
       J --> K
       K --> L[Validated Configuration]
       
       classDef config fill:#1565c0,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef tracer fill:#2e7d32,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef method fill:#ef6c00,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef result fill:#7b1fa2,stroke:#333333,stroke-width:2px,color:#ffffff
       
       class A,B,C,D,E config
       class F tracer
       class H,I,J method
       class K,L result

Usage Patterns
==============

The hybrid approach supports three usage patterns, all fully compatible:

1. **Backwards Compatible** (Existing Code)
2. **Modern Config Objects** (Recommended for New Code)  
3. **Mixed Approach** (Config Objects with Parameter Overrides)

Backwards Compatible Usage
--------------------------

**All existing code continues to work unchanged:**

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

Modern Config Objects Usage
---------------------------

**Recommended for new code - cleaner and more maintainable:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from honeyhive.config.models import TracerConfig, SessionConfig
   
   # Create configuration objects
   config = TracerConfig(
       api_key="hh_1234567890abcdef",
       project="my-llm-project",
       source="production",
       verbose=True,
       disable_http_tracing=True,
       test_mode=False
   )
   
   session_config = SessionConfig(
       session_name="user-chat-session",
       inputs={"user_id": "123", "query": "Hello world"}
   )
   
   # Initialize with config objects
   tracer = HoneyHiveTracer(
       config=config,
       session_config=session_config
   )

Mixed Approach Usage
--------------------

**Config objects with parameter overrides (individual parameters take precedence):**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from honeyhive.config.models import TracerConfig
   
   # Base configuration
   config = TracerConfig(
       api_key="hh_1234567890abcdef",
       project="my-llm-project",
       verbose=False  # Set to False in config
   )
   
   # Override specific parameters
   tracer = HoneyHiveTracer(
       config=config,
       verbose=True,  # This overrides config.verbose=False
       session_name="special-session"  # Additional parameter
   )

Configuration Models Reference
==============================

BaseHoneyHiveConfig
-------------------

Base class containing common fields shared across all domain-specific configurations.

**Fields:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Field
     - Type
     - Default
     - Description
   * - ``api_key``
     - ``Optional[str]``
     - ``None``
     - HoneyHive API key for authentication (env: ``HH_API_KEY``)
   * - ``project``
     - ``Optional[str]``
     - ``None``
     - Project name required by backend API (env: ``HH_PROJECT``)
   * - ``test_mode``
     - ``bool``
     - ``False``
     - Enable test mode - no data sent to backend (env: ``HH_TEST_MODE``)
   * - ``verbose``
     - ``bool``
     - ``False``
     - Enable verbose logging output (env: ``HH_VERBOSE``)

**Validation Rules:**

- ``api_key``: Must be non-empty string if provided
- ``project``: Must be non-empty string, no special characters (``/``, ``\``, ``?``, ``#``, ``&``)

**Example:**

.. code-block:: python

   from honeyhive.config.models import BaseHoneyHiveConfig
   
   # Not used directly, but inherited by domain-specific configs
   class MyConfig(BaseHoneyHiveConfig):
       custom_field: str = "default"

TracerConfig
------------

Core tracer configuration with validation, inherits from ``BaseHoneyHiveConfig``.

**Additional Fields:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Field
     - Type
     - Default
     - Description
   * - ``session_name``
     - ``Optional[str]``
     - ``None``
     - Human-readable session identifier
   * - ``source``
     - ``str``
     - ``"dev"``
     - Source environment identifier (env: ``HH_SOURCE``)
   * - ``server_url``
     - ``Optional[str]``
     - ``None``
     - Custom HoneyHive server URL (env: ``HH_API_URL``)
   * - ``disable_http_tracing``
     - ``bool``
     - ``True``
     - Disable HTTP request tracing (env: ``HH_DISABLE_HTTP_TRACING``)
   * - ``disable_batch``
     - ``bool``
     - ``False``
     - Disable batch processing of spans (env: ``HH_DISABLE_BATCH``)

**Validation Rules:**

- ``server_url``: Must be valid HTTP/HTTPS URL if provided
- ``source``: Must be non-empty string

**Example:**

.. code-block:: python

   from honeyhive.config.models import TracerConfig
   
   config = TracerConfig(
       api_key="hh_1234567890abcdef",
       project="my-llm-project",
       session_name="user-chat-session",
       source="production",
       server_url="https://api.honeyhive.ai",
       verbose=True,
       disable_http_tracing=True
   )

SessionConfig
-------------

Session-specific configuration parameters, inherits from ``BaseHoneyHiveConfig``.

**Additional Fields:**

.. list-table::
   :header-rows: 1
   :widths: 20 20 15 45

   * - Field
     - Type
     - Default
     - Description
   * - ``session_id``
     - ``Optional[str]``
     - ``None``
     - Existing session ID to attach to (must be valid UUID)
   * - ``inputs``
     - ``Optional[Dict[str, Any]]``
     - ``None``
     - Session input data
   * - ``link_carrier``
     - ``Optional[Dict[str, Any]]``
     - ``None``
     - Context propagation carrier for distributed tracing

**Validation Rules:**

- ``session_id``: Must be valid UUID string if provided (normalized to lowercase)

**Example:**

.. code-block:: python

   from honeyhive.config.models import SessionConfig
   
   session_config = SessionConfig(
       session_id="550e8400-e29b-41d4-a716-446655440000",
       inputs={"user_id": "123", "query": "Hello world"},
       link_carrier={"traceparent": "00-...", "baggage": "..."}
   )

EvaluationConfig
----------------

Evaluation-specific configuration parameters, inherits from ``BaseHoneyHiveConfig``.

**Additional Fields:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Field
     - Type
     - Default
     - Description
   * - ``is_evaluation``
     - ``bool``
     - ``False``
     - Enable evaluation mode
   * - ``run_id``
     - ``Optional[str]``
     - ``None``
     - Evaluation run identifier
   * - ``dataset_id``
     - ``Optional[str]``
     - ``None``
     - Dataset identifier for evaluation
   * - ``datapoint_id``
     - ``Optional[str]``
     - ``None``
     - Specific datapoint identifier

**Validation Rules:**

- All ID fields: Must be non-empty strings if provided

**Example:**

.. code-block:: python

   from honeyhive.config.models import EvaluationConfig
   
   eval_config = EvaluationConfig(
       is_evaluation=True,
       run_id="eval-run-123",
       dataset_id="dataset-456",
       datapoint_id="datapoint-789"
   )

APIClientConfig
---------------

Configuration for HoneyHive API client (future implementation), inherits from ``BaseHoneyHiveConfig``.

**Additional Fields:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Field
     - Type
     - Default
     - Description
   * - ``base_url``
     - ``Optional[str]``
     - ``None``
     - Base API URL for requests (env: ``HH_API_URL``)
   * - ``timeout``
     - ``Optional[float]``
     - ``None``
     - Request timeout in seconds (env: ``HH_TIMEOUT``)
   * - ``max_connections``
     - ``int``
     - ``10``
     - Maximum concurrent connections (env: ``HH_MAX_CONNECTIONS``)
   * - ``max_keepalive``
     - ``int``
     - ``20``
     - Maximum keepalive connections (env: ``HH_MAX_KEEPALIVE_CONNECTIONS``)
   * - ``rate_limit_calls``
     - ``int``
     - ``100``
     - Rate limit calls per window (env: ``HH_RATE_LIMIT_CALLS``)
   * - ``rate_limit_window``
     - ``float``
     - ``60.0``
     - Rate limit window in seconds (env: ``HH_RATE_LIMIT_WINDOW``)

**Validation Rules:**

- ``base_url``: Must be valid HTTP/HTTPS URL, trailing slash removed
- ``timeout``: Must be positive number if provided
- ``max_connections``, ``max_keepalive``: Must be positive integers
- ``rate_limit_calls``: Must be positive integer
- ``rate_limit_window``: Must be positive number

**Example:**

.. code-block:: python

   from honeyhive.config.models import APIClientConfig
   
   # Future usage
   api_config = APIClientConfig(
       api_key="hh_1234567890abcdef",
       base_url="https://api.honeyhive.ai",
       timeout=30.0,
       max_connections=10,
       rate_limit_calls=100,
       rate_limit_window=60.0
   )

Utility Functions
=================

merge_configs_with_params
-------------------------

Merges config objects with individual parameters for backwards compatibility.

**Signature:**

.. code-block:: python

   def merge_configs_with_params(
       config: Optional[TracerConfig] = None,
       session_config: Optional[SessionConfig] = None,
       evaluation_config: Optional[EvaluationConfig] = None,
       **individual_params: Any
   ) -> Tuple[TracerConfig, SessionConfig, EvaluationConfig]:

**Parameters:**

- ``config``: Core tracer configuration object
- ``session_config``: Session-specific configuration object  
- ``evaluation_config``: Evaluation-specific configuration object
- ``**individual_params``: Individual parameter overrides (take precedence)

**Returns:**

Tuple of ``(merged_tracer_config, merged_session_config, merged_evaluation_config)``

**Behavior:**

1. Starts with provided config objects or creates defaults
2. Overrides config object values with individual parameters
3. Individual parameters always take precedence over config object values
4. Returns fully merged configuration objects

**Example:**

.. code-block:: python

   from honeyhive.config.models import TracerConfig
   from honeyhive.config.utils import merge_configs_with_params
   
   # Base config
   config = TracerConfig(api_key="hh_123", verbose=False)
   
   # Merge with overrides
   merged = merge_configs_with_params(
       config=config,
       verbose=True,  # Overrides config.verbose=False
       session_name="special-session"  # Additional parameter
   )
   
   tracer_config, session_config, eval_config = merged
   print(tracer_config.verbose)  # True (overridden)
   print(tracer_config.api_key)  # "hh_123" (from config)

Environment Variable Integration
================================

All configuration models support automatic environment variable loading using Pydantic's ``Field(env=...)`` feature.

**Environment Variable Patterns:**

- **Prefix**: All HoneyHive environment variables use ``HH_`` prefix
- **Naming**: Field names are converted to uppercase with underscores
- **Precedence**: Individual parameters > config object values > environment variables

**Common Environment Variables:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Environment Variable
     - Description
   * - ``HH_API_KEY``
     - HoneyHive API key for authentication
   * - ``HH_PROJECT``
     - Default project name
   * - ``HH_SOURCE``
     - Source environment identifier
   * - ``HH_API_URL``
     - Custom HoneyHive server URL
   * - ``HH_VERBOSE``
     - Enable verbose logging (true/false)
   * - ``HH_TEST_MODE``
     - Enable test mode (true/false)
   * - ``HH_DISABLE_HTTP_TRACING``
     - Disable HTTP request tracing (true/false)
   * - ``HH_DISABLE_BATCH``
     - Disable batch processing (true/false)

**Example:**

.. code-block:: bash

   # Set environment variables
   export HH_API_KEY="hh_1234567890abcdef"
   export HH_PROJECT="my-llm-project"
   export HH_VERBOSE="true"

.. code-block:: python

   from honeyhive.config.models import TracerConfig
   
   # Automatically loads from environment variables
   config = TracerConfig()
   print(config.api_key)  # "hh_1234567890abcdef"
   print(config.project)  # "my-llm-project"
   print(config.verbose)  # True

Error Handling and Validation
=============================

All configuration models use Pydantic v2 validation with clear error messages.

**Validation Features:**

- **Type Safety**: Automatic type conversion and validation
- **Field Validation**: Custom validators for complex rules
- **Clear Errors**: Descriptive error messages with field context
- **Fail Fast**: Validation occurs at object creation time

**Common Validation Errors:**

API Key Validation
------------------

.. code-block:: python

   from honeyhive.config.models import TracerConfig
   from pydantic import ValidationError
   
   try:
       config = TracerConfig(api_key="")  # Empty string
   except ValidationError as e:
       print(e)
       # ValidationError: api_key must be a non-empty string

Project Name Validation
-----------------------

.. code-block:: python

   try:
       config = TracerConfig(project="my/project")  # Invalid characters
   except ValidationError as e:
       print(e)
       # ValidationError: project name contains invalid characters

URL Validation
--------------

.. code-block:: python

   try:
       config = TracerConfig(server_url="not-a-url")  # Invalid URL
   except ValidationError as e:
       print(e)
       # ValidationError: server_url must be a valid HTTP/HTTPS URL

UUID Validation
---------------

.. code-block:: python

   from honeyhive.config.models import SessionConfig
   
   try:
       config = SessionConfig(session_id="not-a-uuid")  # Invalid UUID
   except ValidationError as e:
       print(e)
       # ValidationError: session_id must be a valid UUID string

Backwards Compatibility Guarantees
==================================

The hybrid configuration approach provides **100% backwards compatibility** with the following guarantees:

**API Compatibility:**

1. **All existing constructors work unchanged**
2. **All existing parameter names are supported**
3. **All existing parameter types are accepted**
4. **All existing default values are preserved**
5. **All existing validation behavior is maintained**

**Behavioral Compatibility:**

1. **Parameter precedence is preserved** (individual params > config objects > environment vars)
2. **Error messages remain consistent** for existing validation failures
3. **Environment variable loading works as before**
4. **Initialization order and side effects are unchanged**

**Migration Path:**

1. **No forced migration** - existing code continues to work indefinitely
2. **Gradual adoption** - can mix old and new approaches in same codebase
3. **Incremental benefits** - adopt config objects where they provide value
4. **Zero breaking changes** - no version bumps required for compatibility

**Testing Verification:**

The backwards compatibility is verified through comprehensive test suites:

.. code-block:: python

   # All of these work and produce identical results:
   
   # Method 1: Original approach (unchanged)
   tracer1 = HoneyHiveTracer(api_key="hh_123", project="test", verbose=True)
   
   # Method 2: Config objects
   config = TracerConfig(api_key="hh_123", project="test", verbose=True)
   tracer2 = HoneyHiveTracer(config=config)
   
   # Method 3: Mixed approach
   tracer3 = HoneyHiveTracer(config=config, session_name="override")
   
   # All tracers have identical configuration and behavior
   assert tracer1.api_key == tracer2.api_key == tracer3.api_key
   assert tracer1.project == tracer2.project == tracer3.project
   assert tracer1.verbose == tracer2.verbose == tracer3.verbose

Benefits and Trade-offs
=======================

**Benefits:**

1. **Reduced Argument Count**: Fixes pylint R0913/R0917 issues
2. **Type Safety**: Pydantic validation with clear error messages
3. **Self-Documenting**: Field descriptions and examples in code
4. **Environment Integration**: Automatic loading from ``HH_*`` variables
5. **Maintainability**: Grouped related parameters, easier to extend
6. **IDE Support**: Better autocomplete and type hints
7. **Backwards Compatibility**: All existing code continues to work

**Trade-offs:**

1. **Additional Complexity**: More classes and imports for new users
2. **Learning Curve**: Developers need to understand config objects
3. **Import Overhead**: Slightly more imports for new approach
4. **Memory Usage**: Config objects use slightly more memory than individual parameters

**When to Use Each Approach:**

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Scenario
     - Recommended Approach
     - Rationale
   * - **Existing Code**
     - Keep individual parameters
     - No migration needed, works as-is
   * - **New Complex Initialization**
     - Use config objects
     - Better organization, type safety
   * - **Simple New Code**
     - Individual parameters OK
     - Less overhead for simple cases
   * - **Library/Framework Integration**
     - Config objects preferred
     - Better API design, extensibility
   * - **Environment-Heavy Deployments**
     - Config objects
     - Better environment variable support
   * - **Type-Critical Applications**
     - Config objects required
     - Pydantic validation essential

Future Extensions
=================

The hybrid configuration system is designed for extensibility:

**Planned Additions:**

1. **API Client Integration**: Full ``APIClientConfig`` implementation
2. **Evaluation Configs**: Enhanced evaluation and dataset configuration
3. **Integration Configs**: Provider-specific configuration objects
4. **Validation Plugins**: Custom validation rules for enterprise use
5. **Configuration Profiles**: Named configuration presets (dev, staging, prod)

**Extension Pattern:**

.. code-block:: python

   # Future: Custom domain configs
   from honeyhive.config.models.base import BaseHoneyHiveConfig
   
   class CustomIntegrationConfig(BaseHoneyHiveConfig):
       provider: str = Field(..., description="Integration provider name")
       custom_field: Optional[str] = None
       
       @field_validator('provider')
       @classmethod
       def validate_provider(cls, v: str) -> str:
           allowed = ['openai', 'anthropic', 'bedrock']
           if v not in allowed:
               raise ValueError(f'provider must be one of {allowed}')
           return v

**Backwards Compatibility Promise:**

All future extensions will maintain the hybrid approach and backwards compatibility guarantees. Existing code will continue to work regardless of new features added to the configuration system.

See Also
========

- :doc:`/reference/configuration/environment-vars` - Environment variable reference
- :doc:`/reference/api/tracer` - HoneyHiveTracer API reference  
- :doc:`/how-to/migration-compatibility/migration-guide` - General migration guidance
- :doc:`/explanation/architecture/overview` - SDK architecture overview
