Feature List
============

Comprehensive list of features and capabilities provided by the HoneyHive Python SDK.

.. contents:: Table of Contents
   :local:
   :depth: 2

Core Features
-------------

OpenTelemetry Integration
~~~~~~~~~~~~~~~~~~~~~~~~~

* **Full OpenTelemetry Compliance** - Implements all OpenTelemetry standards
* **Span Management** - Create, manage, and export spans
* **Context Propagation** - Distributed tracing across service boundaries
* **Baggage Support** - Custom context propagation
* **OTLP Export** - Export traces to OpenTelemetry backends
* **Batch Processing** - Efficient span export with configurable batching

Session Management
~~~~~~~~~~~~~~~~~~

* **Automatic Session Creation** - Sessions created automatically on tracer initialization
* **Session Context** - Session information automatically included in spans
* **Custom Session Names** - Specify custom session identifiers
* **Session Persistence** - Session context maintained across operations
* **Multi-User Support** - Support for multiple concurrent sessions

Tracing Decorators
~~~~~~~~~~~~~~~~~~

* **@trace Decorator** - **Recommended**: Automatic tracing for both sync and async functions with dynamic detection
* **@atrace Decorator** - **Legacy**: Async-specific tracing decorator (use @trace for new code)
* **@trace_class Decorator** - Automatic tracing for all methods in a class
* **Automatic Detection** - Automatically detects function type (sync/async) for optimal tracing
* **Custom Attributes** - Add custom span attributes
* **Error Handling** - Automatic error recording and exception tracking
* **Performance Monitoring** - Built-in latency tracking

Evaluation Decorators
~~~~~~~~~~~~~~~~~~~~~

* **@evaluate Decorator** - Automatic evaluation of function outputs with evaluators
* **Built-in Evaluators** - Accuracy, F1-score, length, and custom evaluators
* **Batch Evaluation** - Evaluate multiple outputs simultaneously
* **Custom Metrics** - Define and use custom evaluation metrics
* **Result Storage** - Automatic storage of evaluation results

AI Operation Tracing
--------------------

* **OpenInference Integration** - Automatic AI operation instrumentation
* **Multi-Provider Support** - OpenAI, Anthropic, Google AI, and more
* **Zero Code Changes** - Automatic instrumentation without modifying existing code
* **Rich Metadata** - Detailed span attributes for AI operations
* **Token Tracking** - Automatic token usage monitoring
* **Latency Monitoring** - Performance tracking for AI operations

LLM Agent Observability
------------------------

* **Multi-Step Conversation Tracking** - Follow agent workflows across multiple LLM calls
* **Agent State Management** - Track context and state changes throughout conversations
* **Conversation Correlation** - Link related operations within agent workflows
* **Performance Analytics** - Monitor agent efficiency and response times
* **Cost Tracking** - Track token usage and costs across agent operations
* **Error Propagation** - Understand how errors affect agent workflows

Configuration Management
------------------------

* **Environment Variables** - Configuration via environment variables
* **Dynamic Configuration** - Runtime configuration updates
* **Test Mode** - Development and testing configurations
* **Multi-Environment Support** - Different configs for different environments
* **Secure Storage** - Secure handling of sensitive configuration

Performance Features
--------------------

* **Connection Pooling** - Efficient HTTP connection management
* **Batch Processing** - Configurable span batching for performance
* **Sampling** - Configurable tracing sampling
* **Conditional Tracing** - Enable/disable tracing based on conditions
* **Memory Optimization** - Efficient memory usage for long-running applications
* **Rate Limiting** - Built-in rate limiting for API calls

HTTP Instrumentation
--------------------

* **Automatic HTTP Tracing** - Trace HTTP requests automatically
* **Request/Response Attributes** - Capture HTTP method, URL, status codes
* **Header Tracking** - Monitor request and response headers
* **Error Tracking** - Automatic error recording for failed requests
* **Performance Metrics** - Response time and throughput monitoring
* **Configurable** - Enable/disable HTTP tracing as needed

Advanced Features
-----------------

Dependency Conflict Prevention
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Minimal Core Dependencies** - Only essential packages included
* **Optional Instrumentors** - Choose what gets instrumented
* **No Hard LLM Dependencies** - Avoid version conflicts with existing code
* **Flexible Integration** - Works with any LLM library versions
* **Conflict-Free Deployment** - Deploy without breaking existing workflows

Custom Instrumentors
~~~~~~~~~~~~~~~~~~~~

* **Base Instrumentor Class** - Create custom instrumentors
* **Conditional Instrumentation** - Instrument based on conditions
* **Custom Span Attributes** - Add custom attributes to spans
* **Span Filtering** - Filter spans based on custom criteria
* **Performance Hooks** - Custom performance monitoring hooks

Span Management
~~~~~~~~~~~~~~~

* **Manual Span Creation** - Create spans manually when needed
* **Span Attributes** - Add custom attributes to spans
* **Span Events** - Record events within spans
* **Span Links** - Link related spans together
* **Context Propagation** - Propagate context across threads and processes

Integration Features
--------------------

Framework Integration
~~~~~~~~~~~~~~~~~~~~~

* **Generic HTTP Support** - Works with any HTTP framework through OpenTelemetry
* **OpenTelemetry Standards** - Compatible with any OpenTelemetry-compliant framework

Cloud Integration
~~~~~~~~~~~~~~~~~

* **OpenTelemetry Export** - Export traces to any OpenTelemetry-compliant backend
* **Self-Hosted Support** - Deploy to your own infrastructure

Development Features
--------------------

Testing Support
~~~~~~~~~~~~~~~

* **Test Mode** - Special mode for testing and development
* **Mock Tracer** - Mock tracer for unit tests
* **Test Utilities** - Helper functions for testing
* **Integration Testing** - Support for integration tests
* **Performance Testing** - Tools for performance testing

Debugging Features
~~~~~~~~~~~~~~~~~~

* **Console Export** - Export traces to console for debugging
* **Debug Logging** - Comprehensive debug logging
* **Error Tracking** - Detailed error information and stack traces
* **Performance Profiling** - Performance profiling tools
* **Memory Profiling** - Memory usage monitoring

Monitoring and Observability
----------------------------

Metrics Collection
~~~~~~~~~~~~~~~~~~

* **Performance Metrics** - Automatic performance metrics collection through OpenTelemetry
* **Span Metrics** - Built-in span duration and count metrics

Logging Integration
~~~~~~~~~~~~~~~~~~~

* **Trace Correlation** - Correlate logs with traces using OpenTelemetry context
* **Debug Logging** - Comprehensive debug logging for troubleshooting

Security Features
-----------------

API Key Management
~~~~~~~~~~~~~~~~~~

* **Environment Variables** - Configuration via environment variables
* **Secure Handling** - Secure handling of API keys in memory

Data Privacy
~~~~~~~~~~~~

* **OpenTelemetry Standards** - Follows OpenTelemetry data handling standards
* **Configurable Export** - Control what data gets exported

Deployment Features
-------------------

Production Deployment
~~~~~~~~~~~~~~~~~~~~~

* **Production Configuration** - Production-ready configurations
* **Environment-Based Config** - Different configs for different environments

Self-Hosted Support
~~~~~~~~~~~~~~~~~~~

* **Custom Endpoints** - Support for custom API endpoints
* **On-Premises Deployment** - On-premises deployment support

Documentation Features
----------------------

* **Comprehensive Coverage** - Complete documentation of all implemented features
* **Accurate Representation** - No false claims, honest feature descriptions
* **Best Practices** - Clear guidance on decorator usage and patterns
* **LLM Agent Examples** - Real-world examples of multi-step workflows
* **Dependency Philosophy** - Clear explanation of minimal dependencies approach


