API Reference
=============

.. note::
   **Information-oriented documentation**
   
   This reference provides comprehensive technical specifications for all HoneyHive SDK components. Use this section to look up exact API details, parameters, and return values.

.. note::
   **API Requirements**: The ``project`` parameter is required for ``HoneyHiveTracer.init()`` and ``HoneyHiveTracer()``. This parameter specifies which project in your HoneyHive workspace to send traces to.

**Quick Navigation:**

.. contents::
   :local:
   :depth: 2

Overview
--------

The HoneyHive Python SDK provides a comprehensive API for LLM observability and evaluation. This reference documents all available features, APIs, and configurations.

**Latest Updates** (November 2025):

- **Configurable Span Limits**: New ``TracerConfig`` options for span attribute/event/link limits (``max_attributes=1024``, ``max_events=1024``, ``max_links=128``, ``max_span_size=10MB``)
- **Core Attribute Preservation**: Automatic preservation of critical attributes (``session_id``, ``event_type``, ``event_name``, ``source``) with lazy activation for large spans
- **DatasetsAPI Filtering**: Enhanced ``list_datasets()`` with server-side filtering (``name`` and ``include_datapoints`` parameters) for efficient large-scale dataset management

Core Capabilities
~~~~~~~~~~~~~~~~~

**Tracing & Observability**:

- **Universal @trace Decorator**: Works with both sync and async functions with automatic detection
- **Multi-Instance Architecture**: Create multiple independent tracers within the same runtime  
- **Session Management**: Automatic session creation with dynamic naming based on initialization file
- **ProxyTracerProvider Compatibility**: Automatic detection and handling of OpenTelemetry's default provider states
- **Real API Testing**: Comprehensive testing framework with conditional mocking for production-grade validation
- **🆕 Instance Method Enrichment (v1.0)**: ``tracer.enrich_span()`` and ``tracer.enrich_session()`` instance methods are now the primary API with proper multi-instance support and tracer discovery via selective baggage propagation
- **Span Enrichment**: Multiple invocation patterns (reserved namespaces, simple dict, kwargs, context manager) with full backwards compatibility and namespace routing
- **HTTP Instrumentation**: Automatic HTTP request tracing with configurable enable/disable
- **Full Backwards Compatibility**: Complete parameter compatibility with main branch for seamless upgrades

**Evaluation Framework**:

- **@evaluate Decorator**: Automatic evaluation of function outputs with built-in and custom evaluators
- **Environment Variable Support**: Optional ``api_key`` and ``server_url`` parameters with automatic fallback to environment variables (``HONEYHIVE_API_KEY``/``HH_API_KEY`` and ``HONEYHIVE_SERVER_URL``/``HH_SERVER_URL``/``HH_API_URL``)
- **Batch Evaluation**: Evaluate multiple outputs simultaneously with threading support
- **Async Evaluations**: Full async support for evaluation workflows
- **Built-in Evaluators**: Accuracy, F1-score, length, quality score, and custom evaluators

**LLM Integration**:

- **BYOI Architecture**: Bring Your Own Instrumentor support for multiple providers (OpenInference, Traceloop, custom)
- **Auto-Instrumentor Support**: Zero-code integration with OpenAI, Anthropic, Google AI, and more
- **Multi-Provider Support**: Simultaneous tracing across multiple LLM providers  
- **Token Tracking**: Automatic token usage monitoring and cost tracking
- **Rich Metadata**: Detailed span attributes for AI operations
- **Framework Examples**: Integration examples for OpenAI Agents (SwarmAgent), AutoGen (AG2 multi-agent), DSPy (signatures and optimization), AWS Bedrock (Nova/Titan/Claude models), AWS Strands (TracerProvider pattern with Swarm collaboration and Graph workflows), Google ADK (async support), LangGraph (state workflows), Pydantic AI (type-safe agents), and more
- **🆕 Example Requirements**: Comprehensive ``requirements.txt`` for integration examples with organized dependencies by category (core, LLM providers, instrumentors, frameworks) and per-integration installation commands

**Performance & Reliability**:

- **Connection Pooling**: Efficient HTTP connection management with configurable limits
- **Rate Limiting**: Built-in rate limiting for API calls with exponential backoff
- **Graceful Degradation**: SDK never crashes host application, continues operation on failures
- **Batch Processing**: Configurable span batching for optimal performance
- **OTLP Performance Tuning**: Environment variables for batch size and flush interval optimization
- **OTLP JSON Format**: Support for HTTP/JSON export format via ``HH_OTLP_PROTOCOL=http/json``
- **Production Optimization**: ``HH_BATCH_SIZE`` and ``HH_FLUSH_INTERVAL`` for fine-tuned performance control

**Development & Quality**:

- **🆕 Span Capture Utilities**: Test case generation tools for capturing OpenTelemetry spans and converting them to unit tests
- **🆕 Raw Span Data Dumping**: Comprehensive debugging with `_dump_raw_span_data()` method that captures all OpenTelemetry span properties (context, attributes, events, links, resource info) as formatted JSON
- **🆕 Agent OS Enhanced MCP Server** (v0.1.0rc3): Modular architecture with workflow engine, phase gating, and file watcher for incremental RAG updates
- **🆕 Single Source of Truth Versioning** (v0.1.0rc3): Consolidated version management from 5 locations to 1 with late-import pattern
- **Compatibility Testing Infrastructure**: Automated backward compatibility validation and migration analysis
- **Zero Failing Tests Policy**: Comprehensive test quality enforcement framework with anti-skipping rules
- **Tox-Based Development**: Unified development environments for consistent formatting, linting, and testing
- **Pre-Commit Integration**: Automated quality gates using tox environments for consistency
- **Enhanced Quality Gates**: Comprehensive changelog and documentation validation for all significant changes
- **Documentation Quality Control**: Sphinx-based validation with warnings-as-errors enforcement
- **Navigation Validation Framework**: Comprehensive validation of documentation structure, toctrees, and cross-references
- **RST Hierarchy Validation**: Automated checking of reStructuredText section hierarchy consistency
- **Integration Testing Consolidation**: Two-tier testing strategy with clear unit vs integration boundaries
- **Post-Deploy Navigation Validation**: Automatic validation after every documentation deployment
- **Self-Updating Documentation Validation**: System automatically adapts as documentation grows
- **Git Branching Strategy**: Simplified workflow with main as single protected branch and feature-based development
- **CI/CD Optimization**: Smart workflow triggers (push on main only, PRs on all branches - eliminates duplicates)

**Configuration & Security**:

- **🆕 Hybrid Configuration System**: Modern Pydantic config objects with full backwards compatibility
- **Type-Safe Configuration**: IDE autocomplete and validation with graceful degradation
- **Environment Variables**: Comprehensive configuration via HH_* environment variables
- **Multi-Environment Support**: Different configurations for development, staging, production
- **API Key Management**: Secure handling with rotation support and validation
- **SSL/TLS Configuration**: Corporate environment SSL support with custom certificates

Main Components
~~~~~~~~~~~~~~~

- **HoneyHive Client**: Direct API access for data management and configuration
- **🆕 HoneyHiveTracer**: Modular distributed tracing engine with mixin-based architecture and OpenTelemetry compliance
- **🆕 Configuration Classes**: Type-safe Pydantic models (``TracerConfig``, ``BaseHoneyHiveConfig``, ``SessionConfig``)  
- **Decorators**: Simple observability with ``@trace``, ``@evaluate``, and ``@trace_class``
- **Evaluators**: Built-in and custom evaluation functions with async support
- **Instrumentors**: Auto-instrumentation for LLM providers (Bring Your Own Instrumentor)

Core API
--------

Client Classes
~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   api/client
   api/tracer
   api/tracer-architecture
   api/config-models

Decorators & Functions
~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   api/decorators

Configuration
~~~~~~~~~~~~~

**🆕 Hybrid Configuration System**: The SDK now supports both modern Pydantic config objects and traditional parameter passing with full backwards compatibility.

.. toctree::
   :maxdepth: 1

   configuration/hybrid-config-approach
   configuration/config-options
   configuration/environment-vars
   configuration/authentication

Data Models
~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   data-models/events
   data-models/spans
   data-models/evaluations

Experiments Module
~~~~~~~~~~~~~~~~~~

**Modern evaluation framework** with decorator-based evaluators and backend-powered aggregation.

.. note::
   **Session Enrichment**: The ``evaluate()`` function always enriches sessions with outputs, regardless of whether evaluators are provided. This ensures all execution results are persisted to the backend for later analysis.

.. toctree::
   :maxdepth: 1

   experiments/experiments
   experiments/core-functions
   experiments/evaluators
   experiments/results
   experiments/models
   experiments/utilities

Evaluation Framework (Deprecated)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::
   The ``evaluation`` module is deprecated. Use ``experiments`` module instead.
   See :doc:`evaluation/deprecation-notice` for migration details.

.. toctree::
   :maxdepth: 1

   evaluation/evaluators
   evaluation/deprecation-notice

Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   cli/index
   cli/commands
   cli/options

Feature Specifications
~~~~~~~~~~~~~~~~~~~~~~

Tracing Features
````````````````

**Decorator Support**:

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Feature
     - Status
     - Description
   * - ``@trace`` decorator
     - ✅ Stable
     - Universal decorator for sync/async functions with automatic detection
   * - ``@atrace`` decorator  
     - ⚠️ Legacy
     - Async-specific decorator (use ``@trace`` for new code)
   * - ``@trace_class`` decorator
     - ✅ Stable
     - Automatic tracing for all methods in a class
   * - Manual span creation
     - ✅ Stable
     - Context managers and direct span management

**Session Management**:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Capability
     - Implementation
   * - Automatic creation
     - Sessions created automatically on tracer initialization
   * - Dynamic naming
     - Session names default to initialization file name
   * - Custom naming
     - Support for explicit session identifiers
   * - Multi-session support
     - Multiple concurrent sessions per tracer instance
   * - Session enrichment
     - Backend persistence via ``enrich_session()`` with full backwards compatibility. Supports legacy ``session_id`` positional parameter and ``user_properties`` auto-conversion. See :doc:`/how-to/advanced-tracing/session-enrichment`

**Multi-Instance Architecture**:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Feature
     - Specification
   * - Independent instances
     - Multiple tracers with separate API keys, projects, sources
   * - Workflow isolation
     - Separate tracers for different workflows and environments
   * - Concurrent operation
     - Thread-safe operation with multiple active tracers
   * - Resource management
     - Independent lifecycle management for each tracer instance
   * - Provider strategy intelligence
     - Automatic detection and optimal integration with existing OpenTelemetry providers
   * - Span loss prevention
     - Main provider strategy prevents instrumentor spans from being lost in empty providers
   * - Coexistence capability
     - Independent provider strategy enables coexistence with functioning observability systems

Evaluation Features
```````````````````

**Evaluation Framework**:

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Feature
     - Type
     - Description
   * - ``@evaluate`` decorator
     - ✅ Stable
     - Automatic evaluation with custom evaluators
   * - ``@evaluator`` decorator
     - ✅ Stable
     - Create custom synchronous evaluators
   * - ``@aevaluator`` decorator
     - ✅ Stable
     - Create custom asynchronous evaluators
   * - ``evaluate_batch()``
     - ✅ Stable
     - Batch evaluation with threading support
   * - Built-in evaluators
     - ✅ Stable
     - Accuracy, F1-score, length, quality metrics

**Threading Support**:

- **Max Workers**: Configurable parallel execution (default: 10)
- **Async Compatible**: Works with both sync and async evaluation functions
- **Error Handling**: Individual evaluation failures don't stop batch processing
- **Result Aggregation**: Structured results with per-evaluator metrics

LLM Integration Features
````````````````````````

**LLM Provider Integration**:

HoneyHive supports automatic instrumentation for major LLM providers through the BYOI (Bring Your Own Instrumentor) architecture.

**Supported Providers**: OpenAI, Anthropic, Google AI, Google ADK, AWS Bedrock, Azure OpenAI, MCP

**Integration Options**:
- **OpenInference Instrumentors**: Lightweight, community-driven
- **Traceloop Instrumentors**: Enhanced metrics and production optimizations  
- **Custom Instrumentors**: Build your own using OpenTelemetry standards

.. note::
   **Complete Integration Details**
   
   - **Provider-Specific Guides**: :doc:`../how-to/index` - Step-by-step integration for each provider
   - **Compatibility Matrix**: :doc:`../explanation/index` - Full compatibility testing and Python version support
   - **Multi-Provider Setup**: :doc:`../how-to/integrations/multi-provider` - Use multiple providers simultaneously

**Integration Architecture**:

- **Bring Your Own Instrumentor (BYOI)**: Choose which providers to instrument
- **Zero Code Changes**: Automatic instrumentation without modifying existing code
- **Multi-Provider**: Simultaneous tracing across multiple LLM providers
- **Rich Metadata**: Detailed span attributes including tokens, costs, latency

Performance Features
````````````````````

**HTTP Configuration**:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Feature
     - Configuration
   * - Connection pooling
     - ``HH_MAX_CONNECTIONS`` (default: 100)
   * - Keep-alive
     - ``HH_KEEPALIVE_EXPIRY`` (default: 30s)
   * - Timeouts
     - ``HH_TIMEOUT`` (default: 30.0s)
   * - Rate limiting
     - ``HH_RATE_LIMIT_CALLS``, ``HH_RATE_LIMIT_WINDOW``
   * - Retry logic
     - ``HH_MAX_RETRIES`` with exponential backoff

**Optimization Features**:

- **Batch Processing**: Configurable span batching for export efficiency
- **Sampling**: Configurable tracing sampling for performance
- **Conditional Tracing**: Enable/disable based on conditions
- **Memory Optimization**: Efficient memory usage for long-running applications

Configuration Features
``````````````````````

**🆕 Hybrid Configuration System**:

The SDK supports three configuration approaches:

1. **Modern Pydantic Config Objects** (Recommended)
2. **Traditional Parameter Passing** (Backwards Compatible)  
3. **Mixed Approach** (Config objects + parameter overrides)

**Environment Variable Support**:

All configuration supports the ``HH_*`` prefix pattern:

- **Authentication**: ``HH_API_KEY``, ``HH_SOURCE``
- **Operational**: ``HH_TEST_MODE``, ``HH_DEBUG_MODE``, ``HH_DISABLE_TRACING``
- **Performance**: ``HH_TIMEOUT``, ``HH_MAX_CONNECTIONS``, ``HH_RATE_LIMIT_*``, ``HH_BATCH_SIZE``, ``HH_FLUSH_INTERVAL``
- **OTLP**: ``HH_OTLP_ENABLED``, ``HH_OTLP_ENDPOINT``, ``HH_OTLP_PROTOCOL``, ``HH_OTLP_HEADERS``
- **Security**: ``HH_SSL_*``, ``HH_PROXY_*``

**Configuration Hierarchy**:

1. **Individual Parameters** - Direct parameters to ``HoneyHiveTracer()``
2. **Config Object Values** - Values from ``TracerConfig`` objects
3. **Environment Variables** - ``HH_*`` environment variables
4. **Default Values** - Built-in SDK defaults

.. note::
   **API Key Special Case**: ``HH_API_KEY`` takes precedence over constructor ``api_key`` parameter for backwards compatibility. Other parameters follow standard precedence where constructor parameters can override environment variables.

.. note::
   **Runtime Configuration** (v0.1.0rc2+): Environment variables are now properly detected when set at runtime, enabling dynamic configuration without application restart.

.. note::
   **Complete Backwards Compatibility** (v0.1.0rc2+): All 16 original parameters from the main branch are now fully implemented, including ``server_url``, ``session_id``, ``disable_batch``, ``verbose``, evaluation parameters (``is_evaluation``, ``run_id``, ``dataset_id``, ``datapoint_id``), context propagation (``link_carrier``), session inputs, and git metadata collection. Features include evaluation baggage logic, batch processing control, and link/unlink/inject methods for context propagation.

Security Features
`````````````````

**API Key Management**:

- **Format Validation**: Validates ``hh_`` prefix format
- **Secure Storage**: Never logged or exposed in debug output
- **Rotation Support**: Runtime API key updates without restart
- **Environment-Specific**: Different keys for dev/staging/production

**SSL/TLS Support**:

- **Corporate Environments**: Custom CA certificate support
- **Proxy Configuration**: ``HTTPS_PROXY`` and ``HTTP_PROXY`` support
- **Certificate Validation**: Configurable SSL verification

Package Information
~~~~~~~~~~~~~~~~~~~

**Current Version**: |version|

**Python Compatibility**: 3.11+

**Core Dependencies**:
- opentelemetry-api >= 1.20.0
- opentelemetry-sdk >= 1.20.0
- httpx >= 0.24.0
- pydantic >= 2.0.0

**Installation**:

.. code-block:: bash

   pip install honeyhive

**Example Files**:

The SDK includes example files in the ``examples/`` directory:

- ``eval_example.py`` - Demonstrates the ``evaluate()`` function with dataset evaluation and span enrichment
- ``integrations/old_sdk.py`` - Legacy SDK example showing basic tracer initialization and OpenAI integration
- ``integrations/`` - Full integration examples for various LLM providers and frameworks

**See Also:**

- :doc:`../tutorials/index` - Learn by doing
- :doc:`../how-to/index` - Solve specific problems  
- :doc:`../explanation/index` - Understand concepts
