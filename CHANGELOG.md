# Changelog

All notable changes to the HoneyHive Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of HoneyHive Python SDK
- OpenTelemetry integration with custom span processor and exporter
- Session management with start and retrieve operations
- Event creation and batch operations
- **NEW**: Dynamic trace decorator (`@dynamic_trace`) for unified sync/async function tracing
- Tracing decorators for sync and async functions (`@trace`, `@atrace`)
- HTTP instrumentation for automatic request tracing
- Evaluation tools with built-in metrics
- CLI interface for common operations
- Comprehensive configuration management
- Retry logic with multiple backoff strategies
- Baggage support for context propagation
- Type hints and validation with Pydantic
- Async/await support throughout the SDK
- Context managers for resource management
- Dot notation dictionary utilities
- Comprehensive test suite with tox support
- **NEW**: `HoneyHiveTracer.init()` method for official SDK compatibility
  - Matches docs.honeyhive.ai initialization pattern exactly
  - Supports self-hosted deployments with `server_url` parameter
  - Full backwards compatibility with existing code
  - Environment variable integration
  - Automatic singleton management
  - **NEW**: `disable_http_tracing` parameter (defaults to True for performance)

### Features
- **API Client**: Full-featured HTTP client with retry support
- **Tracing**: OpenTelemetry-based tracing with automatic span creation and unified decorators
- **Sessions**: Track and manage LLM sessions with rich metadata
- **Events**: Create and manage events with batch support
- **Evaluation**: Built-in evaluation metrics and scoring functions
- **CLI**: Command-line interface for SDK operations
- **Configuration**: Environment-based configuration with validation
- **Utilities**: Helper utilities for common operations

### Technical Details
- Python 3.11+ support
- OpenTelemetry 1.21.0+ integration
- Pydantic 2.10.0+ for data validation
- httpx for HTTP client operations
- wrapt for decorator support
- Comprehensive type hints
- Multi-Python version testing with tox
- Code coverage and linting support

## [0.1.0] - 2024-01-XX

### Added
- Initial release
- Core SDK functionality
- OpenTelemetry integration
- Session and event management
- Tracing decorators
- Evaluation tools
- CLI interface
- Comprehensive documentation
- Test suite

### Features
- Complete API client implementation
- OpenTelemetry tracer with custom span processor
- Session and event API operations
- Sync and async decorators for tracing
- HTTP instrumentation
- Evaluation framework
- Command-line interface
- Configuration management
- Retry logic and error handling
- Type safety with Pydantic models

### Documentation
- Comprehensive README with examples
- API reference documentation
- Usage examples and tutorials
- Development setup instructions
- Contributing guidelines

### Testing
- Unit tests for all components
- Integration test framework
- Multi-Python version testing
- Code coverage reporting
- Linting and formatting checks
