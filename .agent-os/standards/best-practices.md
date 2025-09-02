# Development Best Practices - HoneyHive Python SDK

## Development Environment Setup

### Mandatory Code Quality Process

**⚠️ CRITICAL: Install Pre-commit Hooks**
```bash
# One-time setup (required for all developers)
./scripts/setup-dev.sh
```

**Automatic Quality Enforcement**:
- **Black formatting**: 88-character lines, applied on every commit
- **Import sorting**: isort with black profile
- **Static analysis**: pylint + mypy type checking  
- **YAML validation**: yamllint with 120-character lines
- **Tox verification**: Format and lint checks

**Before Every Commit**:
1. Pre-commit hooks run automatically (DO NOT bypass)
2. Manual verification: `tox -e format && tox -e lint`
3. **MANDATORY for AI Assistants**: Update documentation before committing
4. Emergency bypass only: `git commit --no-verify` (document why)

**Documentation Update Requirements**:
- **Code changes**: CHANGELOG.md must be updated
- **New features**: CHANGELOG.md + docs/FEATURE_LIST.rst + .agent-os/product/features.md
- **Workflow changes**: Update docs/TESTING.rst and .agent-os/standards/
- **Large changesets (>3 files)**: Comprehensive documentation review required
- **AI Assistant commits**: Automatic documentation compliance checking

### Required Tools
```bash
# Core development tools
pip install yamllint>=1.37.0  # YAML validation for workflows
brew install gh               # GitHub CLI for workflow investigation

# Verify installation
yamllint --version
gh --version
```

### Tool Usage Patterns
- **yamllint**: Validate GitHub Actions YAML syntax before commits
- **GitHub CLI**: Investigate workflow failures, view run logs, manage releases
- **Docker**: Required for Lambda testing and container validation

## Architecture Principles

### Multi-Instance Support
- Each tracer instance is independent
- No global singleton pattern
- Thread-safe initialization
- Support for multiple concurrent tracers
- Clear instance lifecycle management

### Separation of Concerns
```python
# Clear layer separation
src/honeyhive/
├── api/           # API client layer
├── tracer/        # OpenTelemetry integration
├── evaluation/    # Evaluation framework
├── models/        # Data models
└── utils/         # Shared utilities
```

### Dependency Injection
```python
# Pass dependencies explicitly
tracer = HoneyHiveTracer(
    api_key="key",
    project="project",
    instrumentors=[OpenAIInstrumentor()]  # Inject instrumentors
)

# Use factory methods for complex initialization
tracer = HoneyHiveTracer.init(
    api_key="key",
    server_url="https://custom.honeyhive.ai"
)
```

## SDK Design Patterns

### Graceful Degradation
```python
def create_session(self) -> Optional[str]:
    """Create session with graceful failure."""
    try:
        response = self.api.create_session()
        return response.session_id
    except Exception as e:
        if not self.test_mode:
            logger.warning(f"Session creation failed: {e}")
        # Continue without session - don't crash host app
        return None
```

### Decorator Pattern
```python
# Unified decorator for sync/async
@trace(event_type="llm_call")
def sync_function():
    pass

@trace(event_type="llm_call")
async def async_function():
    pass

# Class-level decoration
@trace_class
class MyService:
    def method(self):
        pass  # Automatically traced
```

### Context Management
```python
# Use context managers for resource management
with tracer.start_span("operation") as span:
    # Span automatically closed on exit
    result = perform_operation()
    span.set_attribute("result", result)

# Enrich span context manager
with enrich_span(event_type="enrichment"):
    # Enrichment applied to current span
    process_data()
```

## Error Handling Strategy

### Exception Hierarchy
```python
class HoneyHiveError(Exception):
    """Base exception for all HoneyHive errors."""

class ConfigurationError(HoneyHiveError):
    """Configuration-related errors."""

class APIError(HoneyHiveError):
    """API communication errors."""
    
class RateLimitError(APIError):
    """Rate limit exceeded."""
    
class AuthenticationError(APIError):
    """Authentication failed."""
```

### Retry Logic
```python
@retry(
    max_attempts=3,
    backoff_factor=2.0,
    exceptions=(httpx.TimeoutException, httpx.NetworkError)
)
async def make_api_call():
    """API call with exponential backoff retry."""
    return await client.post(url, json=data)
```

### Error Logging
```python
# Log at appropriate levels
logger.debug("Detailed trace information")
logger.info("Normal operation status")
logger.warning("Recoverable issues")
logger.error("Errors that need attention")
logger.critical("System failures")

# Include context in error messages
logger.error(
    "API call failed",
    extra={
        "url": url,
        "status_code": response.status_code,
        "project": self.project,
        "trace_id": span.get_span_context().trace_id
    }
)
```

## Performance Optimization

### Connection Pooling
```python
# Reuse HTTP connections
connection_pool = ConnectionPool(
    max_connections=config.max_connections,
    max_keepalive_connections=config.max_keepalive_connections,
    keepalive_expiry=config.keepalive_expiry
)

# Share client across requests
self._client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20
    )
)
```

### Batching Operations
```python
# Batch span exports
class BatchSpanProcessor:
    def __init__(self, max_batch_size=512, schedule_delay_millis=5000):
        self.batch = []
        self.max_batch_size = max_batch_size
        
    def on_end(self, span):
        self.batch.append(span)
        if len(self.batch) >= self.max_batch_size:
            self._export_batch()
```

### Async Best Practices
```python
# Use async for I/O operations
async def fetch_data(urls: List[str]):
    """Fetch data concurrently."""
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
    return responses

# Don't block the event loop
# Bad: time.sleep(1)
# Good: await asyncio.sleep(1)
```

## Testing Strategy

### Test Organization
```
tests/
├── unit/              # Fast, isolated tests
│   ├── test_api_client.py
│   ├── test_tracer_decorators.py
│   └── test_utils_config.py
├── integration/       # API integration tests
│   ├── test_openai_integration.py
│   └── test_langchain_integration.py
└── fixtures/         # Shared test fixtures
```

### Testing Best Practices
```python
# Always use tox for testing
# tox -e unit       # Unit tests
# tox -e integration # Integration tests
# tox -e py311     # Python 3.11 tests

# Mock external dependencies
@patch('honeyhive.api.client.httpx.AsyncClient')
def test_api_call(mock_client):
    """Test API call with mocked client."""
    mock_client.post.return_value = Mock(json={"success": True})

# Use fixtures for common setup
@pytest.fixture
def configured_tracer():
    """Provide configured tracer for tests."""
    return HoneyHiveTracer(
        api_key="test-key",
        test_mode=True
    )
```

### Test Coverage Requirements
- Minimum 90% code coverage
- Focus on business logic
- Test error paths
- Verify edge cases
- Include performance tests

## Security Practices

### API Key Management
```python
# Never log API keys
def __init__(self, api_key: str):
    self.api_key = api_key
    logger.info("Client initialized")  # Don't log the key!

# Validate API key format
if not api_key or not api_key.startswith("hh_"):
    raise ValueError("Invalid API key format")

# Support key rotation
def rotate_api_key(self, new_key: str):
    """Update API key without restart."""
    self.api_key = new_key
    self._reinitialize_client()
```

### Data Privacy
```python
# Redact sensitive data
def redact_pii(data: Dict[str, Any]) -> Dict[str, Any]:
    """Redact PII from data."""
    sensitive_keys = ["ssn", "email", "phone", "credit_card"]
    return {
        k: "***REDACTED***" if k in sensitive_keys else v
        for k, v in data.items()
    }

# Configurable data filtering
if config.redact_inputs:
    inputs = redact_pii(inputs)
```

## Configuration Management

### Environment Variable Patterns
```python
# Support multiple prefixes for compatibility
api_key = (
    os.getenv("HH_API_KEY") or
    os.getenv("HONEYHIVE_API_KEY") or
    os.getenv("API_KEY")
)

# Configuration precedence
# 1. Constructor parameters (highest)
# 2. HH_* environment variables
# 3. Standard environment variables
# 4. Default values (lowest)
```

### Configuration Validation
```python
class Config:
    def __init__(self):
        self.api_key = self._validate_api_key()
        self.timeout = self._validate_timeout()
        
    def _validate_timeout(self) -> float:
        """Validate and parse timeout value."""
        timeout = os.getenv("HH_TIMEOUT", "30.0")
        try:
            value = float(timeout)
            if value <= 0:
                raise ValueError("Timeout must be positive")
            return value
        except (ValueError, TypeError):
            logger.warning(f"Invalid timeout: {timeout}, using default")
            return 30.0
```

## Documentation Requirements

### Code Documentation
- Every module needs a docstring
- Every public function needs a docstring
- Complex logic requires inline comments
- Include usage examples in docstrings

### User Documentation
- Getting started guide
- Configuration reference
- Integration examples
- Troubleshooting guide
- API reference
- Migration guides

### Maintenance Documentation
- Architecture decisions
- Design patterns used
- Performance considerations
- Security implications
- Known limitations

## Release Process

### Version Management
```
# Semantic Versioning: MAJOR.MINOR.PATCH
0.1.0 - Initial beta release
0.1.1 - Bug fixes
0.2.0 - New features (backwards compatible)
1.0.0 - First stable release
2.0.0 - Breaking changes
```

### Release Checklist
- [ ] Update version in pyproject.toml
- [ ] Update CHANGELOG.md
- [ ] Run full test suite with tox
- [ ] Build documentation
- [ ] Create git tag
- [ ] Build and publish to PyPI
- [ ] Update GitHub release notes
- [ ] Notify users of breaking changes

### Backwards Compatibility
```python
# Deprecation warnings
def old_method(self):
    """Deprecated method."""
    warnings.warn(
        "old_method is deprecated, use new_method instead",
        DeprecationWarning,
        stacklevel=2
    )
    return self.new_method()

# Support multiple API versions
if api_version == "v1":
    return self._handle_v1_response(response)
else:
    return self._handle_v2_response(response)
```

## Development Workflow

### Code Review Process
1. Create feature branch
2. Implement changes
3. Write/update tests
4. Update documentation
5. Run tox locally
6. Create pull request
7. Address review feedback
8. Merge after approval

### Continuous Integration & CI/CD Best Practices

**Multi-Tier Testing Strategy** (see [CI/CD GitHub Actions Specification](../specs/2025-09-02-cicd-gha-best-practices/specs.md)):

- **Tier 1: Continuous Testing** - Fast feedback on every PR/push (5-10 minutes)
  - Run core tests on all Python versions (3.11, 3.12, 3.13)
  - Check code formatting with black and isort
  - Measure test coverage (minimum 70% requirement)
  - Validate YAML syntax with yamllint
  - Docker simulation testing for AWS Lambda compatibility

- **Tier 2: Daily Scheduled Testing** - Comprehensive validation (30-60 minutes)
  - Performance benchmarking with statistical significance
  - Real AWS Lambda environment testing
  - Security scans and dependency vulnerability checks
  - Build and deploy documentation
  - Performance regression detection

- **Tier 3: Release Candidate Testing** - Complete validation (45-90 minutes)
  - All tier 1 & 2 tests plus integration validation
  - Package building and distribution testing
  - Cross-platform testing (Ubuntu, Windows, macOS)
  - Quality gates for production deployment

**GitHub Actions Workflow Optimization**:

- **Smart Job Organization** - Reduce PR interface clutter through composite jobs
- **Conditional Execution** - Branch and commit message-based test triggering
- **Modern Action Versions** - Use latest stable actions (v4/v5)
- **Artifact Management** - Comprehensive test result preservation
- **Duplicate Prevention** - Optimize triggers to prevent redundant executions

### Developer Experience
- Clear error messages
- Helpful debug output
- Good IDE support
- Quick feedback loops
- Comprehensive examples
- Active community support

## Common Pitfalls to Avoid

### Anti-Patterns
- ❌ Global state
- ❌ Mutable default arguments
- ❌ Bare except clauses
- ❌ Hardcoded values
- ❌ Synchronous I/O in async code
- ❌ Memory leaks from circular references

### Best Practices
- ✅ Explicit is better than implicit
- ✅ Fail fast with clear errors
- ✅ Log liberally but carefully
- ✅ Test edge cases
- ✅ Document assumptions
- ✅ Keep it simple

## Performance Guidelines

### Profiling
```python
# Profile before optimizing
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# Code to profile
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Memory Management
- Use generators for large datasets
- Clear caches periodically
- Avoid circular references
- Use weak references where appropriate
- Monitor memory usage in tests

### Optimization Priorities
1. Correctness first
2. Readability second
3. Performance third
4. Measure before optimizing
5. Document optimizations

## AI Assistant Development Process Requirements

### 🤖 Mandatory AI Assistant Validation Process

**⚠️ CRITICAL**: AI assistants must follow strict validation protocols to prevent codebase drift and outdated reference errors.

#### Pre-Generation Validation (MANDATORY)

Before generating ANY code that integrates with the codebase:

1. **📋 Current API Validation**:
   ```bash
   # ALWAYS check current exports first
   read_file src/honeyhive/__init__.py
   grep -r "class.*:" src/honeyhive/api/
   ```

2. **🔍 Import Pattern Verification**:
   ```bash
   # Check current import patterns in examples
   grep -r "from honeyhive import" examples/
   grep -r "import honeyhive" tests/
   ```

3. **📚 Current Usage Pattern Analysis**:
   - Read at least 2-3 current example files
   - Check recent test files for current API usage
   - Verify class names and method signatures

#### Workflow/CI Generation Rules (MANDATORY)

**🚨 Never generate CI/CD workflows without codebase validation**:

1. **Current API Check**: Read `__init__.py` and `__all__` exports
2. **Test Pattern Review**: Check `tests/` for current import patterns  
3. **Example Validation**: Verify against `examples/` directory
4. **Documentation Cross-Check**: Ensure consistency with current docs

#### Case Study: HoneyHiveClient Failure (2025-09-02)

**❌ What Happened**: AI assistant generated workflow using `HoneyHiveClient` (deprecated Aug 28) instead of `HoneyHive` (current API)

**🔍 Root Cause**: Generated code from memory/assumptions instead of current codebase validation

**✅ Prevention**: Mandatory pre-generation codebase validation prevents this failure mode

#### AI Assistant Commit Requirements

**All AI assistant commits MUST**:
1. **Validate current API** before generating integration code
2. **Test generated code** against current codebase
3. **Update documentation** to reflect any changes
4. **Include validation evidence** in commit messages

**Example compliant commit message**:
```
feat: add release candidate workflow

VALIDATION EVIDENCE:
- Checked src/honeyhive/__init__.py exports: HoneyHive, HoneyHiveTracer
- Verified examples/basic_usage.py import patterns
- Tested against current API surface
- All imports validated against __all__ exports
```

#### Emergency Override Process

**Only in genuine emergencies**:
1. Document why validation was skipped
2. Add TODO for immediate post-emergency validation
3. Schedule validation within 24 hours
4. Update Agent OS with lessons learned

### 🔄 Continuous Validation Requirements

**For Long-Running Development Sessions**:
- Re-validate API every 50+ file changes
- Check for deprecation warnings before major code generation
- Refresh codebase understanding if session > 2 hours
- Always validate before final commits
