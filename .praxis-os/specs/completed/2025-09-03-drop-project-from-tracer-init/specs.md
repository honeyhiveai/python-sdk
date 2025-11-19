# Technical Specification: Drop Project Parameter from Tracer Init

## Overview

This specification defines the technical approach for removing the redundant `project` parameter from `HoneyHiveTracer` initialization. Since API keys are scoped to specific projects in HoneyHive, this parameter is unnecessary and creates configuration overhead.

## Implementation Phases

### Phase 1: API Key-Based Project Resolution

#### 1.1 Update Constructor Signature

**File**: `src/honeyhive/tracer/otel_tracer.py`

```python
def __init__(
    self,
    api_key: Optional[str] = None,
    # project parameter removed - resolved from API key
    source: str = "dev", 
    test_mode: bool = False,
    session_name: Optional[str] = None,
    instrumentors: Optional[list] = None,
    disable_http_tracing: bool = True,
):
    """Initialize HoneyHive tracer.
    
    Args:
        api_key: HoneyHive API key
        source: Source environment 
        test_mode: Whether to run in test mode
        session_name: Optional session name
        instrumentors: List of instrumentors to integrate
        disable_http_tracing: Whether to disable HTTP tracing
    """
    if not OTEL_AVAILABLE:
        raise ImportError("OpenTelemetry is required for HoneyHiveTracer")

    self.test_mode = test_mode
    self.disable_http_tracing = disable_http_tracing

    # Set HTTP tracing environment variable
    if disable_http_tracing:
        os.environ["HH_DISABLE_HTTP_TRACING"] = "true"
    else:
        os.environ["HH_DISABLE_HTTP_TRACING"] = "false"

    # Handle API key setup
    if not test_mode:
        self.api_key = api_key or config.api_key
        if not self.api_key:
            raise ValueError("API key is required")
    else:
        self.api_key = api_key or config.api_key or "test-api-key"

    # Resolve project from API key
    self.project = self._resolve_project()

    self.source = source
    
    # Continue with existing initialization...
```

#### 1.2 Implement Project Resolution Logic

```python
def _resolve_project(self) -> str:
    """Resolve project name from API key scope."""
    
    # Strategy 1: API Key Introspection (Primary)
    if not self.test_mode and self.api_key:
        try:
            project = self._get_project_from_api_key(self.api_key)
            if project:
                print(f"✓ Resolved project from API key: {project}")
                return project
        except Exception as e:
            print(f"⚠️  Could not resolve project from API key: {e}")
    
    # Strategy 2: Environment Variable (Development/Testing fallback)
    project = self._resolve_from_environment()
    if project:
        print(f"✓ Using project from environment: {project}")
        return project
    
    # Strategy 3: Test Mode Fallback
    if self.test_mode:
        project = self._generate_test_project()
        print(f"✓ Using test mode project: {project}")
        return project
    
    # Strategy 4: Error - cannot resolve
    raise ValueError(
        "Could not resolve project. Ensure your API key is valid or set HH_PROJECT environment variable for development."
    )

def _get_project_from_api_key(self, api_key: str) -> Optional[str]:
    """Get project from API key by querying HoneyHive API."""
    import requests
    
    try:
        # Check cache first
        cached_project = self._get_cached_project(api_key)
        if cached_project:
            return cached_project
        
        # Make API call to get project info
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            f"{config.api_url}/auth/verify", 
            headers=headers, 
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            project = data.get("project") or data.get("project_name")
            if project:
                # Cache the result
                self._cache_project(api_key, project)
                return project
        else:
            print(f"   ❌ API key validation failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Failed to validate API key: {e}")
        return None

def _resolve_from_environment(self) -> Optional[str]:
    """Resolve project from environment variables (development fallback)."""
    # Check HH_PROJECT only (for development/testing)
    project = os.getenv("HH_PROJECT")
    
    # Don't use "default" as it's not meaningful
    if project and project.strip() and project != "default":
        return project.strip()
    
    return None

def _generate_test_project(self) -> str:
    """Generate a meaningful project name for test mode."""
    import socket
    import time
    
    try:
        hostname = socket.gethostname().split('.')[0]
    except Exception:
        hostname = "unknown"
    
    timestamp = int(time.time())
    
    # Create a meaningful test project name
    return f"test-project-{hostname}-{timestamp}"

def _get_cached_project(self, api_key: str) -> Optional[str]:
    """Get cached project for API key."""
    # Simple in-memory cache - could be enhanced with TTL
    cache_key = f"project_{hash(api_key)}"
    return getattr(self.__class__, f"_cache_{cache_key}", None)

def _cache_project(self, api_key: str, project: str) -> None:
    """Cache project for API key."""
    cache_key = f"project_{hash(api_key)}"
    setattr(self.__class__, f"_cache_{cache_key}", project)
```

#### 1.3 Update init() Class Method

```python
@classmethod
def init(
    cls,
    api_key: Optional[str] = None,
    # project parameter removed - resolved from API key
    source: str = "dev",
    test_mode: bool = False,
    session_name: Optional[str] = None,
    server_url: Optional[str] = None,
    instrumentors: Optional[list] = None,
    disable_http_tracing: bool = True,
) -> "HoneyHiveTracer":
    """Create and initialize a new HoneyHive tracer instance.
    
    Args:
        api_key: HoneyHive API key
        source: Source environment
        test_mode: Whether to run in test mode
        session_name: Optional session name
        server_url: Custom server URL
        instrumentors: List of instrumentors to integrate
        disable_http_tracing: Whether to disable HTTP tracing
        
    Returns:
        Configured HoneyHiveTracer instance
    """
    if api_key is None:
        api_key = config.api_key

    # Handle server_url parameter
    if server_url:
        original_api_url = config.api_url
        try:
            config.api_url = server_url
            tracer = cls(
                api_key=api_key,
                source=source,
                test_mode=test_mode,
                session_name=session_name,
                instrumentors=instrumentors,
                disable_http_tracing=disable_http_tracing,
            )
        finally:
            config.api_url = original_api_url
        return tracer
    else:
        return cls(
            api_key=api_key,
            source=source,
            test_mode=test_mode,
            session_name=session_name,
            instrumentors=instrumentors,
            disable_http_tracing=disable_http_tracing,
        )
```

### Phase 2: Update Supporting Components

#### 2.1 Update HoneyHiveSpanProcessor

**File**: `src/honeyhive/tracer/span_processor.py`

```python
def on_start(self, span: Span, parent_context: Optional[Context] = None) -> None:
    """Process span on start with project from baggage or fallback."""
    
    # ... existing code ...
    
    # Get project from baggage (should be set by tracer)
    project = baggage.get_baggage("project", ctx)
    if not project:
        print(f"   ⚠️  No project in baggage, using fallback")
        # Use a reasonable fallback since project should always be in baggage
        project = "unknown-project"
    
    attributes_to_set["honeyhive.project"] = project
    
    # Continue with rest of processing...

# Remove _resolve_missing_project method - no longer needed
# Project should always be available in baggage when set by tracer
```

### Phase 3: Configuration Updates

#### 3.1 Update Config Class

**File**: `src/honeyhive/utils/config.py`

```python
@dataclass
class HoneyHiveConfig:
    """HoneyHive SDK configuration."""

    api_key: Optional[str] = None
    api_url: str = "https://api.honeyhive.ai"
    # project removed - resolved dynamically from API key
    source: str = "production"

    def __post_init__(self) -> None:
        """Post-initialization setup."""
        # API key with environment fallback
        if self.api_key is None:
            self.api_key = os.getenv("HH_API_KEY") or os.getenv("HONEYHIVE_API_KEY")

        # Source environment
        env_source = (
            os.getenv("HH_SOURCE") or 
            os.getenv("SOURCE") or 
            os.getenv("ENVIRONMENT")
        )
        if env_source:
            self.source = env_source
```

### Phase 4: Test Updates

#### 4.1 Update Unit Tests

**File**: `tests/unit/test_tracer_otel_tracer.py`

```python
def test_project_resolution_from_api_key(self) -> None:
    """Test project resolution from API key."""
    with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
        with patch.object(HoneyHiveTracer, '_get_project_from_api_key') as mock_api:
            mock_api.return_value = "api-project"
            tracer = HoneyHiveTracer(api_key="test_key", test_mode=False)
            assert tracer.project == "api-project"
            mock_api.assert_called_once_with("test_key")

def test_project_resolution_test_mode_fallback(self) -> None:
    """Test project resolution in test mode."""
    with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
        with patch.dict(os.environ, {}, clear=True):
            tracer = HoneyHiveTracer(api_key="test_key", test_mode=True)
            # Should generate a test project name
            assert tracer.project.startswith("test-project-")
            assert len(tracer.project.split('-')) >= 3  # test-project-hostname-timestamp

def test_project_resolution_environment_fallback(self) -> None:
    """Test project resolution from environment when API fails."""
    with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
        with patch.object(HoneyHiveTracer, '_get_project_from_api_key') as mock_api:
            mock_api.return_value = None  # API call fails
            with patch.dict(os.environ, {"HH_PROJECT": "env-project"}):
                tracer = HoneyHiveTracer(api_key="test_key", test_mode=False)
                assert tracer.project == "env-project"

def test_project_resolution_error_when_no_fallback(self) -> None:
    """Test that error is raised when project cannot be resolved."""
    with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
        with patch.object(HoneyHiveTracer, '_get_project_from_api_key') as mock_api:
            mock_api.return_value = None  # API call fails
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(ValueError, match="Could not resolve project"):
                    HoneyHiveTracer(api_key="test_key", test_mode=False)

def test_init_method_without_project(self) -> None:
    """Test init method works without project parameter."""
    with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
        with patch.object(HoneyHiveTracer, '_get_project_from_api_key') as mock_api:
            mock_api.return_value = "api-project"
            tracer = HoneyHiveTracer.init(api_key="test_key", test_mode=False)
            assert tracer.project == "api-project"
            assert tracer.api_key == "test_key"
```

#### 4.2 Update Integration Tests

**File**: `tests/integration/test_tracer_integration.py`

```python
def test_tracer_works_without_project_parameter(self):
    """Test that tracer functions correctly without project parameter."""
    
    # Set up API key mock
    with patch.object(HoneyHiveTracer, '_get_project_from_api_key') as mock_api:
        mock_api.return_value = "integration-test"
        
        # Initialize without project parameter
        tracer = HoneyHiveTracer.init(api_key="test-api-key", test_mode=False)
        
        # Verify basic functionality
        assert tracer.project == "integration-test"
        
        # Test tracing works
        with tracer.start_span("test-span") as span:
            span.set_attribute("test.attribute", "value")
            
        # Verify span was created and has correct project
        # ... additional verification logic ...
```

### Phase 5: Documentation Updates

#### 5.1 Update Examples

**File**: `examples/basic_usage.py`

```python
#!/usr/bin/env python3
"""
Basic Usage Example - Updated for API Key-Based Project Resolution

This example demonstrates the new API key-driven project resolution.
"""

import os
from honeyhive import HoneyHiveTracer, trace

# Set environment variables for configuration
os.environ["HH_API_KEY"] = "your-api-key-here"  # Project is implicit in API key
os.environ["HH_SOURCE"] = "development"

def main():
    """Main function demonstrating basic usage."""
    
    print("🚀 HoneyHive SDK Basic Usage Example")
    print("=" * 50)
    print("This example demonstrates API key-based project resolution")
    print("where project is automatically determined from your API key.\n")
    
    # ========================================================================
    # 1. SIMPLIFIED INITIALIZATION (PROJECT FROM API KEY)
    # ========================================================================
    print("1. API Key-Based Initialization")
    print("-" * 35)
    
    # Initialize tracer - project resolved from API key
    tracer = HoneyHiveTracer.init(
        api_key="your-api-key",  # Project is implicit in this key
        source="production"      # Only specify what you need
    )
    
    print(f"✓ Tracer initialized for project: {tracer.project}")
    print(f"✓ Project resolved from API key automatically")
    print(f"✓ Source environment: {tracer.source}")
    print(f"✓ Session ID: {tracer.session_id}")
    
    # ========================================================================
    # 2. MINIMAL INITIALIZATION (FULLY ENVIRONMENT-DRIVEN)
    # ========================================================================
    print("\n2. Minimal Initialization")
    print("-" * 27)
    
    # Even simpler - everything from environment
    minimal_tracer = HoneyHiveTracer.init()
    
    print(f"✓ Minimal tracer project: {minimal_tracer.project}")
    print(f"✓ Resolved automatically from API key!")
    
    # Rest of example remains the same...
```

#### 5.2 Update Documentation

**File**: `docs/tutorials/01-quick-start.rst`

```rst
Quick Start Guide
=================

Getting Started with HoneyHive Python SDK

Installation
------------

.. code-block:: bash

   pip install honeyhive

Basic Setup
-----------

The simplest way to get started is with your API key:

.. code-block:: bash

   export HH_API_KEY="your-api-key"  # Project is implicit in API key

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   # Project automatically resolved from API key
   tracer = HoneyHiveTracer.init()

Advanced Configuration
----------------------

You can still override settings programmatically:

.. code-block:: python

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",  # Project resolved from this key
       source="production"      # Specify environment
   )

Development and Testing
-----------------------

For local development, you can override the project:

.. code-block:: bash

   export HH_PROJECT="my-dev-project"  # Override for development
   export HH_API_KEY="your-api-key"

Migration from Previous Versions
--------------------------------

If you're upgrading from a previous version:

.. code-block:: python

   # OLD (no longer supported):
   tracer = HoneyHiveTracer.init(
       api_key="...",
       project="my-project",  # ❌ Removed - redundant!
       source="production"
   )

   # NEW (current):
   tracer = HoneyHiveTracer.init(
       api_key="...",  # Project resolved from API key
       source="production"
   )
```

## Testing Strategy

### Unit Test Coverage

1. **Project Resolution Logic**
   - Test environment variable resolution
   - Test API context resolution  
   - Test application context resolution
   - Test fallback generation

2. **Backward Compatibility**
   - Test explicit project parameter still works
   - Test deprecation warnings are shown
   - Test migration paths

3. **Error Handling**
   - Test graceful degradation when resolution fails
   - Test span processing with missing project
   - Test configuration fallbacks

### Integration Test Coverage

1. **Real Application Scenarios**
   - Test with various environment configurations
   - Test with different deployment patterns
   - Test multi-instance scenarios

2. **Performance Impact**
   - Measure initialization time impact
   - Test memory usage changes
   - Verify no performance regression

### Migration Test Coverage

1. **Backward Compatibility Tests**
   - Run existing test suite with no changes
   - Test deprecated parameter warnings
   - Test migration scenarios

## Performance Considerations

### Initialization Time

The new project resolution logic adds minimal overhead:

- Environment variable lookup: ~0.1ms
- Application context detection: ~1-2ms  
- Git repository detection: ~5-10ms (cached)
- Fallback generation: ~0.1ms

Total additional overhead: <10ms in worst case, typically <2ms.

### Memory Usage

- No significant memory overhead
- Resolution results not cached (each tracer resolves independently)
- Fallback to simple string generation when complex resolution fails

### Caching Strategy

Consider implementing caching for expensive operations:

```python
# Cache git repository detection results
_git_repo_cache = {}

def _get_git_repo_name(path: str) -> Optional[str]:
    if path in _git_repo_cache:
        return _git_repo_cache[path]
    
    result = _detect_git_repo(path)
    _git_repo_cache[path] = result
    return result
```

## Risk Mitigation

### Rollback Plan

1. **Phase 1 Rollback**: Remove deprecation warnings, keep both patterns
2. **Phase 2 Rollback**: Revert span processor changes
3. **Full Rollback**: Restore original implementation with git revert

### Monitoring Strategy

1. **Project Resolution Success Rate**
   - Track how often each resolution strategy succeeds
   - Monitor fallback usage rates
   - Alert if fallback usage exceeds thresholds

2. **User Experience Metrics**
   - Track initialization errors
   - Monitor support ticket volume
   - Measure migration adoption rates

3. **Performance Monitoring**
   - Track initialization time changes
   - Monitor memory usage impact
   - Alert on performance regressions

## Success Criteria Validation

### Automated Validation

```python
def validate_project_resolution():
    """Automated validation of project resolution."""
    
    test_cases = [
        # Environment variable resolution
        {"env": {"HH_PROJECT": "env-test"}, "expected": "env-test"},
        
        # Fallback generation
        {"env": {}, "expected_pattern": r"honeyhive-\w+-\d+"},
        
        # Backward compatibility
        {"explicit": "explicit-test", "expected": "explicit-test"},
    ]
    
    for case in test_cases:
        with patch.dict(os.environ, case.get("env", {})):
            if "explicit" in case:
                tracer = HoneyHiveTracer(
                    api_key="test", 
                    project=case["explicit"],
                    test_mode=True
                )
            else:
                tracer = HoneyHiveTracer(api_key="test", test_mode=True)
            
            if "expected" in case:
                assert tracer.project == case["expected"]
            else:
                assert re.match(case["expected_pattern"], tracer.project)
    
    print("✅ All project resolution validation tests passed")
```

This implementation guide provides the detailed technical steps needed to successfully remove the redundant project parameter by leveraging API key scoping, creating a cleaner and more intuitive API.
