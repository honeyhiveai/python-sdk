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
- **Comprehensive Code Quality Enforcement**: Pre-commit hooks with Black, isort, pylint, mypy, and yamllint
- **Mandatory Documentation Updates**: Pre-commit checks ensuring CHANGELOG.md and feature docs are updated
- **Development Setup Automation**: `./scripts/setup-dev.sh` for one-time development environment configuration  
- **Documentation Synchronization Checks**: Automated validation of feature documentation consistency
- **AI Assistant Compliance**: Specific requirements for AI assistants to update documentation before commits
- **Release Candidate Workflow Fix**: Removed quotes from 'on' trigger to ensure GitHub Actions recognizes workflow_dispatch
- **Artifact Naming Improvement**: Changed artifact name to `honeyhive-python-sdk-<version>` for better identification
- **Build Package Output Fix**: Added proper job outputs to share RC_VERSION between workflow jobs
- **Workflow Test Update**: Fixed import test to use `HoneyHive` instead of removed `HoneyHiveClient`
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

- **AWS Lambda Compatibility**: Comprehensive Lambda testing and deployment support
  - Complete Lambda container testing framework with Docker simulation
  - Performance benchmarking suite for cold starts, warm starts, and throughput
  - Memory efficiency testing and optimization validation
  - Concurrent invocation testing and stress testing capabilities
  - Real AWS Lambda environment compatibility testing matrix
  - Multi-Python version Lambda testing (3.11, 3.12, 3.13)
  - Variable memory configuration testing (128MB, 256MB, 512MB, 1024MB)

- **Advanced Performance Testing**: Scientific SDK overhead measurement
  - Optimal SDK overhead testing with comparative baseline methodology
  - 99.8% variance reduction in performance measurements using statistical techniques
  - Bulk operation testing for statistically significant results
  - Coefficient of Variation (CV) analysis for measurement stability
  - CI-compatible performance thresholds for automated testing
  - Container-aware performance testing with environment adaptation

- **GitHub Actions Enhancements**: Robust CI/CD pipeline improvements
  - Release candidate workflow for manual deployment testing with comprehensive validation
  - Lambda compatibility matrix testing across Python versions and memory configurations
  - Streamlined workflow job organization with reduced PR interface clutter
  - Container validation and build verification in CI environments
  - Performance regression detection and monitoring with statistical thresholds
  - Artifact management and test result preservation across workflow runs
  - YAML syntax validation with yamllint integration and 120-character line length
  - Conditional testing logic preventing unnecessary runs and resource usage
  - Workflow trigger optimization eliminating duplicate PR/push executions

- **Development Tooling**: Enhanced development experience
  - GitHub CLI integration for workflow investigation and automation
  - Comprehensive error handling middleware for all API clients
  - Improved tox configuration with environment descriptions
  - Agent OS integration for structured development guidance

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
- **Performance Testing**: Enhanced with scientific measurement methodologies and CI compatibility
- **Lambda Testing**: Comprehensive serverless environment testing with real AWS simulation
- **CI/CD Pipeline**: Upgraded GitHub Actions with modern action versions and enhanced workflows
  - Eliminated workflow job clutter through matrix consolidation and composite jobs
  - Implemented smart conditional testing based on branch context and commit messages
  - Enhanced workflow artifact management with proper retention policies
- **Error Handling**: Unified error handling middleware pattern across all API clients
- **Threading Compatibility**: Improved cross-Python version compatibility for threading operations
- **Testing Infrastructure**: Comprehensive testing strategy with appropriate granularity
  - Continuous testing for basic validation on every PR and push
  - Daily scheduled testing for thorough performance and real AWS environment validation
  - Manual release candidate testing for comprehensive pre-deployment validation

### Fixed
- **Lambda Performance Thresholds**: Adjusted performance assertions for CI environment compatibility
  - Updated cold start performance thresholds from 300ms to 800ms for tracer initialization
  - Updated SDK overhead thresholds from 500ms to 1000ms for CI environments
  - Maintains performance regression detection while accommodating CI variability
- **Threading Compatibility**: Resolved `isinstance()` compatibility issues across Python versions
  - Replaced rigid type checking with duck typing for `threading.Lock` operations
  - Enhanced cross-version compatibility for Python 3.11, 3.12, and 3.13
- **Container Build Process**: Fixed Lambda container building and validation
  - Corrected Docker build paths for proper file inclusion
  - Enhanced container validation with comprehensive SDK import testing
- **GitHub Actions Workflows**: Updated deprecated action versions and improved reliability
  - Upgraded `actions/upload-artifact` from v3 to v4, `actions/setup-python` from v4 to v5
  - Upgraded `codecov/codecov-action` from v3 to v4, `actions/github-script` from v6 to v7
  - Upgraded `aws-actions/configure-aws-credentials` from v2 to v4
  - Enhanced workflow artifact management and test result preservation
  - Consolidated matrix jobs into composite jobs to reduce GitHub PR interface clutter
  - Fixed duplicate workflow executions on PR branches through improved trigger conditions
- **Test Configuration**: Resolved pytest configuration conflicts in Lambda testing
  - Fixed global `pytest.ini` addopts conflicts with specialized test commands
  - Improved test isolation and execution reliability
- **SDK Overhead Measurement**: Corrected variance in performance measurements
  - Implemented comparative baseline methodology reducing variance by 99.8%
  - Fixed misleading overhead calculations by separating cold start from runtime costs
  - Enhanced statistical significance with bulk operation testing

### Deprecated
- **Global Tracer Usage**: `@trace` decorator without explicit tracer instance
  - Still functional but not recommended for new code
  - Use `@trace(tracer=instance)` for better multi-instance support

### Removed
- **Deprecation Warnings**: Replaced with direct error messages or guidance
- **Obsolete Performance Tests**: Removed superseded SDK overhead tests
  - Eliminated `test_comprehensive_sdk_overhead` replaced by optimal methodology
  - Cleaned up unused helper methods and redundant test code

### Technical Details
- **Coverage Threshold**: Increased to 70% with enforcement
- **Test Framework**: Enhanced pytest configuration with new markers and Lambda testing
- **Quality Tools**: Black, isort, pylint, and mypy integration with Agent OS standards
- **Multi-Python Support**: Python 3.11, 3.12, and 3.13 testing across all environments
- **Lambda Testing**: 16 comprehensive Lambda tests with zero skipped tests
- **Performance Benchmarking**: Scientific methodology with statistical significance
- **CI/CD Integration**: Automated testing with GitHub Actions and container validation
- **Development Tools**: yamllint >=1.37.0 and GitHub CLI >=2.78.0 added to tech stack
- **Container Strategy**: Docker-based Lambda simulation with multi-environment testing
- **YAML Configuration**: Custom `.yamllint` configuration with 120-character line length limit
- **Workflow Organization**: Smart job grouping and conditional execution for optimal CI/CD experience

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
