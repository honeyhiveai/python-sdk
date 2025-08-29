# HoneyHive Python SDK Feature List

A comprehensive overview of all **actually implemented** features available in the HoneyHive Python SDK.

## 🚀 **Core Features**

### **Tracing & Observability**
- **OpenTelemetry Integration**: Full OpenTelemetry compliance with OTLP export
- **Singleton Tracer Pattern**: `HoneyHiveTracer` with automatic singleton management
- **Dual Initialization Patterns**:
  - **`HoneyHiveTracer.init()`** - Official SDK pattern (recommended)
  - **Constructor-based initialization** - Enhanced pattern with additional options
- **Session Management**: Automatic session creation and management
- **Context Propagation**: Automatic context propagation across operations
- **Baggage Support**: Custom metadata propagation with experiment harness integration

### **Tracing Decorators**
- **`@trace`** - Primary decorator for synchronous functions (recommended)
  - Automatically handles function inputs, outputs, and metadata
  - Full attribute and metadata support
  - Experiment harness integration
- **`@atrace`** - Async decorator for asynchronous functions
- **`@trace_class`** - Automatic method tracing for entire classes
- **`enrich_span`** - Context manager for enriching existing spans

### **Manual Span Management**
- **`start_span()`** - Create custom spans with context manager
- **`enrich_span()`** - Add attributes to existing spans
- **`enrich_session()`** - Session-level enrichment with metadata, feedback, and metrics

### **Evaluation Framework** 🆕
- **Comprehensive Evaluation System**: Complete framework for LLM output evaluation
- **Built-in Evaluators**: Pre-implemented evaluation metrics
  - **ExactMatchEvaluator**: Perfect string matching
  - **F1ScoreEvaluator**: F1 score calculation for text similarity
  - **LengthEvaluator**: Text length analysis and scoring
  - **SemanticSimilarityEvaluator**: Meaning-based text comparison
- **Custom Evaluator Support**: Extensible framework for domain-specific evaluation
  - **BaseEvaluator**: Abstract base class for custom evaluators
  - **Flexible Interface**: Support for any callable evaluation function
  - **Type Safety**: Full type hints and validation
- **Threading & Parallel Processing**: High-performance evaluation capabilities
  - **ThreadPoolExecutor**: Parallel evaluation with configurable workers
  - **Context Propagation**: Maintains context across threads using `contextvars`
  - **Batch Processing**: Efficient evaluation of large datasets
  - **Configurable Workers**: Adjustable `max_workers` for different environments
- **Decorator Pattern**: Seamless integration with existing code
  - **`@evaluate_decorator`**: Main decorator for automatic evaluation
  - **`@evaluator`**: Tracing-integrated evaluation decorator
  - **`@aevaluator`**: Async evaluation decorator
- **Evaluation Pipeline**: Flexible evaluation orchestration
  - **`evaluate_with_evaluators`**: Core evaluation function with threading
  - **`evaluate_batch`**: Batch dataset evaluation
  - **Mixed Evaluator Types**: Support for strings, instances, and callables
- **API Integration**: Store evaluation results in HoneyHive
  - **`create_evaluation_run`**: Create and store evaluation runs
  - **Result Persistence**: Automatic storage of evaluation data
  - **Metadata Support**: Rich metadata for evaluation context
- **Performance Features**: Optimized for production use
  - **Score Normalization**: Automatic score scaling to 0.0-1.0 range
  - **Error Isolation**: Failed evaluators don't crash the process
  - **Resource Management**: Automatic cleanup of thread resources
  - **Scalability**: Designed for high-throughput evaluation workloads

### **API Client**
- **HTTP Client**: Async-capable HTTP client with connection pooling
- **Authentication**: API key-based authentication
- **Rate Limiting**: Built-in rate limiting with configurable limits
- **Error Handling**: Comprehensive error handling and logging
- **Session Management**: Create, manage, and track sessions
- **Event Logging**: Log events with rich metadata
- **Connection Pooling**: Efficient HTTP connection reuse with keep-alive

### **Configuration Management**
- **Environment Variables**: Support for `HH_*` environment variables
- **Dynamic Reloading**: Runtime configuration updates with `reload_config()`
- **Project Management**: Multi-project support
- **Source Tracking**: Environment and source identification
- **HTTP Client Configuration**: Configurable connection pooling, rate limiting, and proxy settings
- **Experiment Harness Integration**: Support for MLflow, Weights & Biases, Comet, and standard experiment variables

## **Experiment Harness Integration**

### **Automatic Detection**
- **MLflow**: Automatic detection of `MLFLOW_EXPERIMENT_ID` and `MLFLOW_EXPERIMENT_NAME`
- **Weights & Biases**: Automatic detection of `WANDB_RUN_ID` and `WANDB_PROJECT`
- **Comet**: Automatic detection of `COMET_EXPERIMENT_KEY` and `COMET_PROJECT_NAME`
- **Standard Variables**: Support for `EXPERIMENT_ID`, `EXPERIMENT_NAME`, `EXPERIMENT_VARIANT`, `EXPERIMENT_GROUP`
- **Metadata Parsing**: Support for JSON, key-value, and comma-separated metadata formats
- **Automatic Span Enrichment**: All spans automatically include experiment context

### **Span Attributes**
- **Experiment ID**: `honeyhive.experiment_id`
- **Experiment Name**: `honeyhive.experiment_name`
- **Experiment Variant**: `honeyhive.experiment_variant`
- **Experiment Group**: `honeyhive.experiment_group`
- **Experiment Metadata**: Individual attributes for each metadata key

## **Advanced Features**

### **Connection Management**
- **Connection Pooling**: Efficient HTTP connection reuse with configurable limits
- **Keep-Alive**: Connection keep-alive management with expiry settings
- **Timeout Handling**: Configurable timeouts and retries
- **Cleanup**: Automatic connection cleanup and resource management
- **Pool Configuration**: Configurable pool sizes and connection limits

### **Caching System**
- **In-Memory Cache**: Fast in-memory caching with TTL
- **LRU Eviction**: Least-recently-used cache eviction
- **Size Limits**: Configurable cache size limits
- **Function Caching**: `@cache` and `@acache` decorators for function results
- **Async Support**: Full async/await support for caching operations
- **Statistics**: Cache hit/miss statistics and performance metrics

### **Retry & Resilience**
- **Exponential Backoff**: Configurable exponential backoff strategies
- **Jitter Support**: Random jitter to prevent thundering herd
- **Multiple Strategies**: Exponential, linear, and constant backoff
- **Status Code Handling**: Configurable retry on specific HTTP status codes
- **Timeout Management**: Configurable timeouts for retry operations

### **Utilities**
- **Logging**: Structured logging with custom formatters (`HoneyHiveLogger`)
- **Data Structures**: `DotDict` for dot-notation access to dictionaries
- **Baggage Management**: `BaggageDict` for OpenTelemetry baggage operations
- **Validation**: Data validation and type checking with Pydantic models
- **Serialization**: JSON serialization and deserialization with error handling

## **Development & Testing**

### **Testing Support**
- **Tox Integration**: Multi-Python version testing (3.11, 3.12, 3.13)
- **Pytest Support**: Full pytest integration with fixtures and async support
- **Mock Support**: Comprehensive mocking and testing utilities with OpenTelemetry I/O error prevention
- **Integration Tests**: **REAL API integration testing** with 21 evaluation framework tests (no mocking)
- **Unit Tests**: Comprehensive unit test coverage (685 tests passing)
- **Test Coverage**: 70.89% coverage (exceeds 60% requirement)
- **Test Mode**: Built-in test mode for development and testing
- **Evaluation Testing**: Comprehensive testing of evaluation framework including threading
- **Test Isolation**: Clean environment setup with proper cleanup between tests
- **Real Credentials**: Integration tests use actual HoneyHive API credentials from `.env` file

### **Development Tools**
- **CLI Interface**: Command-line interface for common operations
- **Code Quality**: Black, isort, flake8, mypy integration
- **Documentation**: Comprehensive docstrings and examples
- **Type Hints**: Full type annotation support with mypy strict mode
- **Configuration Management**: CLI commands for viewing and managing configuration
- **Linting**: Perfect 10.00/10 pylint score with zero mypy errors

## **Performance & Reliability**

### **Performance Features**
- **Async Support**: Full async/await support throughout the codebase
- **Connection Reuse**: Efficient HTTP connection management
- **Batch Operations**: Support for batch API operations
- **Streaming**: Support for streaming responses
- **Lazy Initialization**: HTTP clients initialized only when needed
- **Parallel Evaluation**: Threading support for evaluation workloads
- **Batch Processing**: Efficient evaluation of large datasets

### **Reliability Features**
- **Error Recovery**: Automatic error recovery and retry
- **Rate Limiting**: Protection against API rate limit violations
- **Health Monitoring**: Built-in health check capabilities
- **Resource Management**: Automatic cleanup and resource management
- **Thread Safety**: Thread-safe evaluation framework
- **Error Isolation**: Failed evaluators don't affect others

## **Deployment & Operations**

### **Configuration**
- **Environment-Based**: Environment-specific configuration
- **Secrets Management**: Secure API key management via environment variables
- **Validation**: Configuration validation and error checking
- **Defaults**: Sensible defaults with override capability
- **Server URL Support**: Self-hosted deployment support with `server_url` parameter
- **Evaluation Configuration**: Configurable threading and batch processing

### **Monitoring**
- **OTLP Export**: OpenTelemetry Protocol (OTLP) export to HoneyHive backend
- **Span Processing**: Custom span processor for HoneyHive-specific attributes
- **Console Export**: Console export for debugging and development
- **Metrics Collection**: Built-in metrics collection via span attributes
- **Evaluation Metrics**: Comprehensive evaluation metrics and scoring

## **Security Features**

### **Authentication & Authorization**
- **API Key Security**: Secure API key handling via environment variables
- **Bearer Token**: Bearer token authentication for API requests
- **Rate Limiting**: Protection against abuse with configurable limits
- **Audit Logging**: Comprehensive audit trail via event logging

### **Data Protection**
- **HTTPS Only**: All API communication over HTTPS
- **SSL Verification**: Configurable SSL certificate verification
- **Proxy Support**: HTTP/HTTPS proxy support for enterprise environments
- **Access Control**: Project-based access control

## **Extensibility**

### **Integration Points**
- **OpenInference Support**: Automatic integration with OpenInference instrumentors
- **Custom Instrumentors**: Support for custom OpenTelemetry instrumentors
- **Middleware Support**: Custom middleware integration capabilities
- **Plugin Architecture**: Modular architecture for extensions
- **Custom Evaluators**: Extensible evaluation framework

### **Customization**
- **Custom Attributes**: Full support for custom span attributes
- **Custom Metadata**: Flexible metadata handling for all operations
- **Custom Metrics**: Support for custom performance metrics
- **Custom Feedback**: User feedback integration for evaluation
- **Custom Evaluation Logic**: Domain-specific evaluation algorithms

## **Documentation & Support**

### **Documentation**
- **API Reference**: Comprehensive API documentation
- **Examples**: Practical usage examples and tutorials
- **Best Practices**: Development and deployment best practices
- **Configuration Guide**: Detailed configuration documentation
- **Evaluation Guide**: Comprehensive evaluation framework documentation

### **Examples**
- **Basic Usage**: Simple tracing and API usage examples
- **Enhanced Tracing**: Advanced tracing features demonstration
- **Evaluation**: Model evaluation and metrics examples
- **Integration**: OpenInference and experiment harness integration
- **CLI Usage**: Command-line interface examples
- **Threading**: Parallel evaluation examples
- **Custom Evaluators**: Custom evaluation logic examples

## **Technical Specifications**

### **Requirements**
- **Python**: 3.11+ (with support for 3.11, 3.12, 3.13)
- **Dependencies**: OpenTelemetry, httpx, pydantic, click, pyyaml
- **Platform**: Cross-platform (Windows, macOS, Linux)

### **Performance**
- **Memory**: Efficient memory usage with connection pooling
- **CPU**: Minimal CPU overhead for tracing operations
- **Network**: Optimized network usage with keep-alive and connection reuse
- **Scalability**: Designed for high-throughput production environments
- **Evaluation**: Parallel processing for evaluation workloads

## **Notable Limitations**

### **Features Not Currently Implemented**
- **LLM Provider Integrations**: No direct OpenAI, Anthropic, or other LLM provider integrations
- **Framework Middleware**: No FastAPI, Flask, or Django middleware
- **LangChain/LlamaIndex**: No direct callback handlers for these frameworks
- **Webhook Support**: No webhook integration capabilities
- **Metrics Endpoint**: No metrics endpoint (meter_provider not configured)
- **Circuit Breaker**: No circuit breaker pattern implementation
- **Health Check Endpoints**: No built-in health check endpoints

### **Planned Features**
- **Enhanced LLM Integration**: Future support for direct LLM provider integration
- **Framework Middleware**: Planned middleware for popular web frameworks
- **Advanced Metrics**: Enhanced metrics collection and visualization
- **Real-time Monitoring**: Real-time monitoring and alerting capabilities

---

*This feature list reflects the actual implemented capabilities of the HoneyHive Python SDK as of version 0.1.0. Features are based on source code analysis and may differ from marketing materials or planned features.*
