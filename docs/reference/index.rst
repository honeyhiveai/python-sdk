API Reference
=============

.. note::
   **Information-oriented documentation**
   
   This reference provides comprehensive technical specifications for all HoneyHive SDK components. Use this section to look up exact API details, parameters, and return values.

**Quick Navigation:**

.. contents::
   :local:
   :depth: 2

Overview
--------

The HoneyHive Python SDK provides a comprehensive API for LLM observability and evaluation. This reference documents all available features, APIs, and configurations.

Core Capabilities
~~~~~~~~~~~~~~~~~

**Tracing & Observability**:

- **Universal @trace Decorator**: Works with both sync and async functions with automatic detection
- **Multi-Instance Architecture**: Create multiple independent tracers within the same runtime  
- **Session Management**: Automatic session creation with dynamic naming based on initialization file
- **Span Enrichment**: Rich context manager pattern for automatic span enrichment with OpenTelemetry native integration
- **HTTP Instrumentation**: Automatic HTTP request tracing with configurable enable/disable

**Evaluation Framework**:

- **@evaluate Decorator**: Automatic evaluation of function outputs with built-in and custom evaluators
- **Batch Evaluation**: Evaluate multiple outputs simultaneously with threading support
- **Async Evaluations**: Full async support for evaluation workflows
- **Built-in Evaluators**: Accuracy, F1-score, length, quality score, and custom evaluators

**LLM Integration**:

- **BYOI Architecture**: Bring Your Own Instrumentor support for multiple providers (OpenInference, OpenLLMetry, custom)
- **Auto-Instrumentor Support**: Zero-code integration with OpenAI, Anthropic, Google AI, and more
- **Multi-Provider Support**: Simultaneous tracing across multiple LLM providers  
- **Token Tracking**: Automatic token usage monitoring and cost tracking
- **Rich Metadata**: Detailed span attributes for AI operations

**Performance & Reliability**:

- **Connection Pooling**: Efficient HTTP connection management with configurable limits
- **Rate Limiting**: Built-in rate limiting for API calls with exponential backoff
- **Graceful Degradation**: SDK never crashes host application, continues operation on failures
- **Batch Processing**: Configurable span batching for optimal performance

**Development & Quality**:

- **Zero Failing Tests Policy**: Comprehensive test quality enforcement framework with anti-skipping rules
- **Tox-Based Development**: Unified development environments for consistent formatting, linting, and testing
- **Pre-Commit Integration**: Automated quality gates using tox environments for consistency
- **Documentation Quality Control**: Sphinx-based validation with warnings-as-errors enforcement
- **Git Branching Strategy**: Simplified workflow with main as single protected branch and feature-based development
- **CI/CD Optimization**: Smart workflow triggers (push on main only, PRs on all branches - eliminates duplicates)

**Configuration & Security**:

- **Environment Variables**: Comprehensive configuration via HH_* environment variables
- **Multi-Environment Support**: Different configurations for development, staging, production
- **API Key Management**: Secure handling with rotation support and validation
- **SSL/TLS Configuration**: Corporate environment SSL support with custom certificates

Main Components
~~~~~~~~~~~~~~~

- **HoneyHive Client**: Direct API access for data management and configuration
- **HoneyHiveTracer**: Distributed tracing engine with OpenTelemetry compliance  
- **Decorators**: Simple observability with ``@trace``, ``@evaluate``, and ``@trace_class``
- **Evaluators**: Built-in and custom evaluation functions with async support
- **Instrumentors**: Auto-instrumentation for LLM providers (Bring Your Own Instrumentor)

Core API
--------

Client Classes
~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   api/client
   api/tracer

Decorators & Functions
~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   api/decorators

Configuration
~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   configuration/environment-vars
   configuration/config-options
   configuration/authentication

Data Models
~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   data-models/events
   data-models/spans
   data-models/evaluations

Evaluation Framework
~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   evaluation/evaluators

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
     - Backend persistence via ``enrich_session()``

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

**Auto-Instrumentor Support**:

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Provider
     - Status
     - Instrumentor Package
   * - OpenAI
     - ✅ Supported
     - ``openinference-instrumentation-openai`` (or OpenLLMetry equivalent)
   * - Anthropic
     - ✅ Supported
     - ``openinference-instrumentation-anthropic`` (or OpenLLMetry equivalent)
   * - Google AI
     - ✅ Supported
     - ``openinference-instrumentation-google-generativeai`` (or OpenLLMetry equivalent)
   * - AWS Bedrock
     - ✅ Supported
     - ``openinference-instrumentation-bedrock`` (or OpenLLMetry equivalent)
   * - Other Providers
     - 🔄 Expanding
     - Multiple instrumentor provider support (see compatibility matrix)
   * - Custom LLMs
     - ✅ Supported
     - Create custom instrumentors using OpenTelemetry standards

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

**Environment Variable Support**:

All configuration supports the ``HH_*`` prefix pattern:

- **Authentication**: ``HH_API_KEY``, ``HH_PROJECT``, ``HH_SOURCE``
- **Operational**: ``HH_TEST_MODE``, ``HH_DEBUG_MODE``, ``HH_DISABLE_TRACING``
- **Performance**: ``HH_TIMEOUT``, ``HH_MAX_CONNECTIONS``, ``HH_RATE_LIMIT_*``
- **Security**: ``HH_SSL_*``, ``HH_PROXY_*``

**Configuration Hierarchy**:

1. Constructor parameters (highest priority)
2. ``HH_*`` environment variables
3. Standard environment variables (``HTTP_*``, ``EXPERIMENT_*``)
4. Default values (lowest priority)

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

**See Also:**

- :doc:`../tutorials/index` - Learn by doing
- :doc:`../how-to/index` - Solve specific problems  
- :doc:`../explanation/index` - Understand concepts
