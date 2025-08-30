# Changelog

All notable changes to the HoneyHive Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Breaking Changes
- **Modernized Architecture**: `HoneyHiveTracer` now supports multiple independent instances
  - **`HoneyHiveTracer.init()` method maintained for backwards compatibility** - this is the preferred pattern
  - Direct constructor usage also available: `HoneyHiveTracer(api_key="key", project="project")`
  - Each initialization creates a new independent tracer instance

### Added
- **Multi-Instance Architecture**: Complete refactor to support multiple tracer instances
  - Create multiple independent tracers within the same runtime
  - Each tracer can have different API keys, projects, and sources
  - Independent lifecycle management for each tracer instance
  - Thread-safe operation with multiple tracers

- **Dynamic Session Naming**: Automatic session naming based on initialization file
  - Sessions automatically named after the file where tracer is initialized
  - Uses `inspect` module to detect calling file
  - Provides better organization and debugging capabilities

- **Smart TracerProvider Management**: Intelligent OpenTelemetry provider integration
  - Automatically detects existing TracerProvider instances
  - Integrates with existing providers or creates new ones as needed
  - Prevents conflicts with other OpenTelemetry implementations
  - `is_main_provider` flag for proper lifecycle management

- **Enhanced Decorator Support**: Improved `@trace` and `@atrace` decorators
  - Explicit tracer instance support: `@trace(tracer=my_tracer)`
  - Better multi-instance usage patterns
  - Maintains backward compatibility with global tracer usage
  - Improved error handling and performance
  - **`HoneyHiveTracer.init()` remains the preferred initialization method**

- **Comprehensive Testing**: Enhanced test coverage and new test patterns
  - Test coverage increased to 72.10% with new 70% threshold requirement
  - New multi-instance integration tests
  - Real API integration tests
  - TracerProvider integration tests
  - Enhanced unit tests for new architecture

- **Dependency Management**: Added `psutil` dependency
  - Enhanced memory usage monitoring in evaluation framework
  - Better performance monitoring capabilities

- **Evaluation Framework**: Comprehensive evaluation system for AI model assessment
  - Built-in evaluators: exact match, F1 score, length, semantic similarity
  - Custom evaluator framework for domain-specific evaluation
  - Threading support with `ThreadPoolExecutor` for parallel processing
  - Decorator pattern with `@evaluate_decorator` for seamless integration
  - API integration for storing evaluation results in HoneyHive
  - Batch processing capabilities for large datasets
  - Memory optimization and caching for repeated evaluations
  - Statistical significance testing and result comparison
  - Export formats: JSON, CSV, Excel
  - Integration with MLflow, Weights & Biases, and TensorBoard
  - Real-time evaluation monitoring and debugging tools

### Changed
- **Architecture**: Modern multi-instance architecture supporting multiple independent tracers
- **Initialization**: `HoneyHiveTracer.init()` remains the preferred method, direct constructor also available
- **Session Management**: Automatic file-based session naming
- **Provider Integration**: Smart OpenTelemetry provider detection and integration
- **Decorator Usage**: Recommended explicit tracer instance passing
- **Testing Standards**: Increased coverage requirement from 60% to 70%

### Deprecated
- **Global Tracer Usage**: `@trace` decorator without explicit tracer instance
  - Still functional but not recommended for new code
  - Use `@trace(tracer=instance)` for better multi-instance support

### Removed
- **Deprecation Warnings**: Replaced with direct error messages or guidance

### Technical Details
- **Coverage Threshold**: Increased to 70% with enforcement
- **Test Framework**: Enhanced pytest configuration with new markers
- **Quality Tools**: Black, isort, pylint, and mypy integration
- **Multi-Python Support**: Python 3.11, 3.12, and 3.13 testing

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
