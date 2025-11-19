# Design Doc: Fix `enrich_span` Backwards Compatibility

**Status:** Investigation Complete - Ready for Implementation  
**Date:** 2025-10-19  
**Author:** Agent Investigation  

---

## Executive Summary

The `enrich_span` function in the current branch is not backwards compatible with the main branch interface. Users upgrading from main branch will experience breaking changes. This document details the investigation findings and proposes a fix that maintains full backwards compatibility while adding new functionality.

---

## Problem Statement

### User Impact

Users calling `enrich_span` with the original main branch interface receive errors or unexpected behavior:

```python
# Main branch code (should work but doesn't)
enrich_span(metadata={"user_id": "123", "feature": "chat"})
enrich_span(metrics={"score": 0.95}, feedback={"rating": 5})
```

**Current behavior:**
- Parameters are passed as `**kwargs` instead of being recognized as reserved namespaces
- Attributes are not namespaced correctly (missing `honeyhive_metadata.`, `honeyhive_metrics.`, etc.)
- The function signature is incompatible with existing user code

### Business Impact

- **Breaking change** for all users upgrading from main branch
- Documentation examples don't match implementation
- User code needs rewriting to work with new SDK version
- Loss of user trust in SDK stability

---

## Background: Main Branch Implementation

### Original Interface

The main branch `enrich_span` was a simple function with explicit reserved parameters:

```python
# Location: src/honeyhive/tracer/custom.py (main branch)
def enrich_span(
    config: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    event_id: Optional[str] = None
):
    """Enrich the current span with additional attributes."""
    span = otel_trace.get_current_span()
    if span is None:
        logger.warning("Please use enrich_span inside a traced function.")
    else:
        instrumentor._enrich_span(
            span, config, metadata, metrics, feedback, 
            inputs, outputs, error, event_id
        )
```

### Key Characteristics

1. **Reserved namespace parameters:** Each parameter maps to a specific attribute namespace
2. **Automatic span detection:** Uses `otel_trace.get_current_span()` - no tracer param needed
3. **Attribute namespacing:** Each reserved field is prefixed appropriately:
   - `metadata` → `honeyhive_metadata.*`
   - `metrics` → `honeyhive_metrics.*`
   - `feedback` → `honeyhive_feedback.*`
   - `inputs` → `honeyhive_inputs.*`
   - `outputs` → `honeyhive_outputs.*`
   - `config` → `honeyhive_config.*`
   - `error` → `honeyhive_error`
   - `event_id` → `honeyhive_event_id`

4. **Recursive attribute setting:** Uses `_set_span_attributes()` to handle nested dicts/lists:

```python
def _set_span_attributes(self, span, prefix, value):
    if isinstance(value, dict):
        for k, v in value.items():
            self._set_span_attributes(span, f"{prefix}.{k}", v)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            self._set_span_attributes(span, f"{prefix}.{i}", v)
    # ... handles primitives and JSON serialization
```

### Usage Examples from Main Branch

```python
# Example 1: Single namespace
enrich_span(metadata={"user_id": "123", "feature": "chat"})
# Result: honeyhive_metadata.user_id = "123"
#         honeyhive_metadata.feature = "chat"

# Example 2: Multiple namespaces
enrich_span(
    metadata={"session": "abc"},
    metrics={"latency_ms": 150},
    feedback={"rating": 5}
)
# Result: honeyhive_metadata.session = "abc"
#         honeyhive_metrics.latency_ms = 150
#         honeyhive_feedback.rating = 5

# Example 3: Nested structures
enrich_span(config={"model": "gpt-4", "params": {"temp": 0.7}})
# Result: honeyhive_config.model = "gpt-4"
#         honeyhive_config.params.temp = 0.7
```

---

## Current Implementation Analysis

### Architecture Overview

The current branch attempted to unify multiple invocation patterns through a class-based design:

```python
# Location: src/honeyhive/tracer/instrumentation/enrichment.py
class UnifiedEnrichSpan:
    def __call__(
        self,
        attributes: Optional[Dict[str, Any]] = None,
        tracer: Optional[Any] = None,
        **kwargs: Any,
    ) -> "UnifiedEnrichSpan":
        # Store arguments for later use
        self._attributes = attributes
        self._tracer = tracer
        self._kwargs = kwargs
        return self

# Global instance
enrich_span = UnifiedEnrichSpan()
```

### Core Logic Issues

The `enrich_span_core()` function doesn't implement namespace logic:

```python
def enrich_span_core(
    attributes: Optional[Dict[str, Any]] = None,
    tracer_instance: Optional[Any] = None,
    verbose: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    # Combine attributes and kwargs dynamically
    all_attributes = attributes.copy() if attributes else {}
    all_attributes.update(kwargs)
    
    # Apply attributes to the span
    for key, value in all_attributes.items():
        current_span.set_attribute(key, value)  # ❌ NO NAMESPACING
```

**Problems:**
1. ❌ Sets attributes directly without namespace prefixes
2. ❌ Doesn't use `_set_span_attributes()` for recursive handling
3. ❌ Doesn't recognize reserved parameter names
4. ❌ Doesn't handle nested dicts/lists properly

### Interface Incompatibilities

**Issue 1: Wrong parameter names**
```python
# Main branch (expected)
enrich_span(metadata={"key": "value"})

# Current implementation requires
enrich_span(attributes={"key": "value"})  # Different param name!
```

**Issue 2: Missing reserved parameters**
```python
# Main branch (expected)
enrich_span(
    metadata={...},
    metrics={...},
    feedback={...}
)

# Current implementation doesn't recognize these
# They just go into **kwargs and get lost
```

**Issue 3: Unnecessary tracer parameter**
```python
# Main branch (expected)
enrich_span(metadata={...})  # Auto-detects span

# Current implementation
enrich_span(attributes={...}, tracer=tracer)  # Requires tracer!
```

---

## Discovery: What Already Exists

### Good News: Core Components Available

The current codebase already has the necessary building blocks:

#### 1. `_set_span_attributes()` Helper

**Location:** `src/honeyhive/tracer/instrumentation/decorators.py` (lines 77-113)

```python
def _set_span_attributes(span: Any, prefix: str, value: Any) -> None:
    """Set span attributes with proper type handling and JSON serialization.
    
    Recursively sets span attributes for complex data structures.
    """
    if isinstance(value, dict):
        for k, v in value.items():
            _set_span_attributes(span, f"{prefix}.{k}", v)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            _set_span_attributes(span, f"{prefix}.{i}", v)
    elif isinstance(value, (bool, float, int, str)):
        span.set_attribute(prefix, value)
    else:
        # JSON serialize complex types
        span.set_attribute(prefix, json.dumps(value, default=str))
```

**Status:** ✅ Already implemented, identical logic to main branch

#### 2. Namespace Mapping Constants

**Location:** `src/honeyhive/tracer/instrumentation/decorators.py` (lines 128-135)

```python
COMPLEX_ATTRIBUTES = {
    "inputs": "honeyhive_inputs",
    "config": "honeyhive_config",
    "metadata": "honeyhive_metadata",
    "metrics": "honeyhive_metrics",
    "feedback": "honeyhive_feedback",
    "outputs": "honeyhive_outputs",
}

BASIC_ATTRIBUTES = {
    "event_type": "honeyhive_event_type",
    "event_name": "honeyhive_event_name",
    "event_id": "honeyhive_event_id",
    # ... more
}
```

**Status:** ✅ Already defined, can be reused

#### 3. OpenTelemetry Span Access

```python
from opentelemetry import trace

# Get current span (same as main branch)
current_span = trace.get_current_span()
```

**Status:** ✅ Already available, same as main branch

---

## Proposed Solution

### Design Goals

1. **Full backwards compatibility** - All main branch code works without changes
2. **Enhanced functionality** - Support new patterns (context manager, simple dict)
3. **Single core logic** - All invocation patterns flow through unified implementation
4. **Maintainability** - Clear, testable, well-documented code

### Solution Architecture

```
User calls enrich_span(...)
         ↓
UnifiedEnrichSpan.__call__()
  - Accept all reserved params explicitly
  - Accept arbitrary kwargs
  - Route to unified function
         ↓
enrich_span_unified()
  - Detect invocation pattern (context manager vs direct)
  - Route to appropriate handler
         ↓
enrich_span_core()
  - Get current span
  - Apply namespace logic
  - Use _set_span_attributes() for each namespace
  - Handle arbitrary kwargs → metadata namespace
         ↓
OpenTelemetry span attributes set correctly
```

### New Interface Signature

```python
class UnifiedEnrichSpan:
    def __call__(
        self,
        attributes: Optional[Dict[str, Any]] = None,  # New: simple dict support
        # Reserved namespaces (backwards compatible)
        metadata: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        feedback: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        event_id: Optional[str] = None,
        # Optional for advanced use
        tracer: Optional[Any] = None,
        # Arbitrary kwargs → metadata
        **kwargs: Any,
    ) -> "UnifiedEnrichSpan":
        """Unified enrich_span supporting multiple invocation patterns.
        
        Backwards compatible with main branch + new features.
        """
```

### Parameter Precedence and Merge Behavior

**When the same key appears in multiple places, use merge/override with this precedence:**

1. **Reserved parameters** (metadata, metrics, etc.) - Applied first
2. **`attributes` dict** - Applied second  
3. **`**kwargs`** - Applied last (wins conflicts)

**Rationale:**
- Explicit is better than implicit (reserved params have priority)
- Simple usage (kwargs) can override if needed for convenience
- No breaking changes for edge case usage patterns
- Predictable behavior: last parameter wins

**Example:**

```python
# All three set user_id - kwargs wins
enrich_span(
    metadata={"user_id": "from_metadata", "session": "abc"},
    attributes={"user_id": "from_attributes", "feature": "chat"},
    user_id="from_kwargs"  # This value wins
)

# Result:
# honeyhive_metadata.user_id = "from_kwargs" (kwargs won)
# honeyhive_metadata.session = "abc" (from metadata)
# honeyhive_metadata.feature = "chat" (from attributes)
```

**Implementation Order:**
1. Apply reserved namespace parameters first
2. Apply `attributes` dict (merges into metadata namespace)
3. Apply `**kwargs` (merges into metadata namespace, overwrites conflicts)

---

### Namespace Routing Logic

The core logic must route parameters to correct namespaces:

```python
def enrich_span_core(
    attributes: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    event_id: Optional[str] = None,
    tracer_instance: Optional[Any] = None,
    verbose: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Core enrichment logic with namespace support."""
    
    # Get current span
    current_span = trace.get_current_span()
    if not current_span or not hasattr(current_span, "set_attribute"):
        return {"success": False, "span": NoOpSpan(), "error": "No active span"}
    
    # Apply reserved namespaces
    if metadata:
        _set_span_attributes(current_span, "honeyhive_metadata", metadata)
    if metrics:
        _set_span_attributes(current_span, "honeyhive_metrics", metrics)
    if feedback:
        _set_span_attributes(current_span, "honeyhive_feedback", feedback)
    if inputs:
        _set_span_attributes(current_span, "honeyhive_inputs", inputs)
    if outputs:
        _set_span_attributes(current_span, "honeyhive_outputs", outputs)
    if config:
        _set_span_attributes(current_span, "honeyhive_config", config)
    
    # Handle simple attributes dict → metadata
    if attributes:
        _set_span_attributes(current_span, "honeyhive_metadata", attributes)
    
    # Handle arbitrary kwargs → metadata
    if kwargs:
        _set_span_attributes(current_span, "honeyhive_metadata", kwargs)
    
    # Handle error and event_id (non-namespaced)
    if error:
        current_span.set_attribute("honeyhive_error", error)
    if event_id:
        current_span.set_attribute("honeyhive_event_id", event_id)
    
    return {"success": True, "span": current_span, "attribute_count": ...}
```

---

## Production Code Standards

**🔒 MANDATORY:** All production code must meet these quality standards.

**Reference:** `.agent-os/standards/coding/python-standards.md`

### Code Quality Targets

- **Pylint Score:** 10.0/10 (perfect score)
- **MyPy Errors:** 0 (complete type safety)
- **Type Annotations:** 100% coverage
- **Docstrings:** 100% Sphinx-compatible

### Linter Priority Order

**Follow this order when addressing code quality:**

1. **Black** - Formatting first (auto-fixes most issues)
2. **isort** - Import sorting and organization
3. **MyPy** - Type safety (CRITICAL - catch type errors early!)
4. **Pylint** - Code quality and style (cosmetic issues last)

### Sphinx Docstring Format (MANDATORY)

**All public functions MUST use Sphinx-compatible docstrings:**

```python
def enrich_span_core(
    attributes: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    event_id: Optional[str] = None,
    tracer_instance: Optional[Any] = None,
    verbose: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Core enrichment logic with namespace support.
    
    This function implements the unified enrichment architecture that supports
    multiple invocation patterns while maintaining backwards compatibility with
    the main branch interface. It routes parameters to proper attribute
    namespaces and handles arbitrary kwargs.
    
    :param attributes: Simple dict that routes to metadata namespace
    :type attributes: Optional[Dict[str, Any]]
    :param metadata: Metadata namespace (honeyhive_metadata.*)
    :type metadata: Optional[Dict[str, Any]]
    :param metrics: Metrics namespace (honeyhive_metrics.*)
    :type metrics: Optional[Dict[str, Any]]
    :param feedback: Feedback namespace (honeyhive_feedback.*)
    :type feedback: Optional[Dict[str, Any]]
    :param inputs: Inputs namespace (honeyhive_inputs.*)
    :type inputs: Optional[Dict[str, Any]]
    :param outputs: Outputs namespace (honeyhive_outputs.*)
    :type outputs: Optional[Dict[str, Any]]
    :param config: Config namespace (honeyhive_config.*)
    :type config: Optional[Dict[str, Any]]
    :param error: Error string (honeyhive_error, non-namespaced)
    :type error: Optional[str]
    :param event_id: Event ID (honeyhive_event_id, non-namespaced)
    :type event_id: Optional[str]
    :param tracer_instance: Optional tracer instance for logging
    :type tracer_instance: Optional[Any]
    :param verbose: Whether to log debug information
    :type verbose: bool
    :param kwargs: Arbitrary kwargs that route to metadata namespace
    :type kwargs: Any
    :return: Enrichment result with success status and span reference
    :rtype: Dict[str, Any]
    :raises ValueError: If event_id is invalid UUID format
    
    **Example:**
    
    .. code-block:: python
    
        # Main branch backwards compatible usage
        result = enrich_span_core(
            metadata={"user_id": "123"},
            metrics={"score": 0.95}
        )
        
        # New simplified usage
        result = enrich_span_core(
            user_id="123",  # Routes to metadata
            feature="chat"  # Routes to metadata
        )
    
    **Note:**
    
    This function is thread-safe and uses OpenTelemetry's context
    propagation to access the current span automatically.
    """
```

### Type Annotations (100% Required)

**Every function, method, and variable MUST have type annotations:**

```python
from typing import Any, Dict, Optional

# Function signature - complete annotations
def process_attributes(
    span: Any,  # OpenTelemetry span
    prefix: str,
    value: Any
) -> None:
    """Process span attributes."""
    # Local variables - annotated
    processed_count: int = 0
    attribute_dict: Dict[str, Any] = {}
    
    # Implementation
```

### Import Organization (isort)

**Imports MUST be organized in this exact order:**

```python
"""Module docstring."""

# 1. Standard library imports
import os
import sys
from typing import Any, Dict, Optional

# 2. Third-party imports  
from opentelemetry import trace

# 3. Local imports
from ..utils.logger import safe_log
from .decorators import _set_span_attributes
```

**Import Rules:**
- Group imports: Standard library, third-party, local
- Alphabetical order within groups
- Blank line between groups
- No wildcard imports (`from module import *`)

### Error Handling Pattern (MANDATORY)

**All functions MUST handle errors gracefully:**

```python
def enrich_span_core(...) -> Dict[str, Any]:
    """Core enrichment logic."""
    try:
        # Get current span
        current_span = trace.get_current_span()
        
        if not current_span:
            safe_log(tracer_instance, "debug", "No active span")
            return {"success": False, "span": NoOpSpan(), "error": "No active span"}
        
        # Apply enrichment logic
        _set_span_attributes(current_span, "honeyhive_metadata", metadata)
        
        return {"success": True, "span": current_span}
        
    except SpecificError as e:
        # Handle known exceptions
        safe_log(tracer_instance, "warning", f"Known issue: {e}")
        raise  # Re-raise if caller should handle
        
    except Exception as e:
        # Catch all fallback - never crash host app
        safe_log(tracer_instance, "error", f"Unexpected error: {e}", exc_info=True)
        return {"success": False, "span": NoOpSpan(), "error": str(e)}
```

**Error Handling Rules:**
- Never crash the host application
- Catch specific exceptions first
- Always have a generic `Exception` fallback
- Use `safe_log()` utility, not print statements
- Return sensible defaults on errors
- Log with appropriate levels (debug/info/warning/error)

### Code Generation Checklist

**Before implementing, verify:**

- [ ] **Type Annotations:** 100% coverage on all functions, methods, variables
- [ ] **Docstrings:** Complete Sphinx format with `:param:`, `:return:`, `:raises:`
- [ ] **Error Handling:** Graceful degradation with specific exception handling
- [ ] **Import Organization:** Follows isort standards (3 groups, alphabetical)
- [ ] **Safe Logging:** Uses `safe_log()` utility for all logging
- [ ] **Code Examples:** Working examples in docstrings
- [ ] **Thread Safety:** Consider concurrent usage patterns
- [ ] **Input Validation:** Validate inputs with clear error messages

### Quality Validation Commands

```bash
# Format code
black src/honeyhive/tracer/instrumentation/enrichment.py

# Sort imports
isort src/honeyhive/tracer/instrumentation/enrichment.py

# Check type safety
mypy src/honeyhive/tracer/instrumentation/enrichment.py

# Check code quality
pylint src/honeyhive/tracer/instrumentation/enrichment.py

# Run all checks
black src/honeyhive/tracer/instrumentation/ && \
isort src/honeyhive/tracer/instrumentation/ && \
mypy src/honeyhive/tracer/instrumentation/ && \
pylint src/honeyhive/tracer/instrumentation/
```

---

## Implementation Plan

### Phase 1: Update Core Function

**File:** `src/honeyhive/tracer/instrumentation/enrichment.py`

**Changes to `enrich_span_core()`:**

1. Add all reserved parameters to signature
2. Import `_set_span_attributes` from decorators module
3. Implement namespace routing logic
4. Route arbitrary kwargs to metadata namespace
5. Remove direct `set_attribute()` calls, use `_set_span_attributes()` instead

### Phase 2: Update UnifiedEnrichSpan Class

**File:** `src/honeyhive/tracer/instrumentation/enrichment.py`

**Changes to `UnifiedEnrichSpan.__call__()`:**

1. Add all reserved parameters to signature
2. Store all parameters in instance variables
3. Pass all parameters through to `enrich_span_unified()`

**Changes to helper functions:**

1. Update `_enrich_span_context_manager()` - pass all params
2. Update `_enrich_span_direct_call()` - pass all params
3. Update `enrich_span_unified()` - accept all params

### Phase 3: Import and Export

**File:** `src/honeyhive/tracer/instrumentation/__init__.py`

Ensure `_set_span_attributes` is available:
```python
from .decorators import _set_span_attributes
```

**File:** `src/honeyhive/tracer/__init__.py`

Verify exports are correct (already done):
```python
from .instrumentation.enrichment import enrich_span
```

---

## Testing Strategy

**🔒 MANDATORY:** This project uses strict testing standards documented in:
- `tests/FIXTURE_STANDARDS.md` - Integration test fixture standards
- `.agent-os/standards/ai-assistant/code-generation/tests/v3/` - Test generation framework

### Testing Framework Requirements

**Before writing ANY tests, must follow:**
1. Skip-proof comprehensive analysis framework
2. Complete checkpoint gates with evidence
3. Unit vs Integration path separation (STRICT)
4. Standard fixtures for integration tests
5. Centralized validation helpers

### Quality Targets

- **Unit Tests:** 90%+ line coverage, 80%+ pass rate
- **Integration Tests:** Backend verification required via centralized helpers
- **V3 Framework:** 10.0/10 quality scores (Pylint + MyPy + coverage)

---

### Unit Tests

**Path:** Unit test path - Mock ALL external dependencies  
**File:** `tests/unit/test_tracer_instrumentation_enrichment.py`  
**Target:** 90%+ line coverage, complete isolation

**🔒 NAMING CONVENTION:**
```
tests/unit/test_[module_path]_[specific_file].py
```

**Examples from project:**
- `src/honeyhive/tracer/core/operations.py` → `test_tracer_core_operations.py`
- `src/honeyhive/utils/dotdict.py` → `test_utils_dotdict.py`
- `src/honeyhive/config/utils.py` → `test_config_utils.py`

**Our file:**
- `src/honeyhive/tracer/instrumentation/enrichment.py` → `test_tracer_instrumentation_enrichment.py` ✅

**Reference:** `.agent-os/standards/testing/unit-testing-standards.md`

**Testing Approach:**
- ✅ Mock `trace.get_current_span()` - no real OpenTelemetry
- ✅ Mock `_set_span_attributes()` or verify it's called correctly
- ✅ Test all parameter combinations
- ✅ Test namespace routing logic
- ✅ Test error conditions with proper mocking
- ✅ Use fixtures from `tests/unit/conftest.py`

**Test Method Naming Convention:**
```python
# Pattern: test_[function_name]_[scenario]_[condition]
def test_enrich_span_main_branch_metadata_interface() -> None:
def test_enrich_span_multiple_namespaces_success() -> None:
def test_enrich_span_error_no_active_span() -> None:
def test_enrich_span_edge_case_empty_dict() -> None:
```

**Test Class Organization:**
```python
class TestEnrichSpanCore:
    """Test enrich_span_core functionality."""
    # Group tests for core logic
    
class TestUnifiedEnrichSpan:
    """Test UnifiedEnrichSpan class functionality."""
    # Group tests for class behavior
    
class TestEnrichmentEdgeCases:
    """Test edge cases and error conditions."""
    # Group edge case tests
```

**Type Annotations (MANDATORY):**
```python
from typing import Any, Dict, Optional
from unittest.mock import Mock

def test_example(
    mock_get_current_span: Mock,  # Type annotate all parameters
    honeyhive_tracer: Mock
) -> None:  # Always annotate return type (None for tests)
    """Test example with complete type annotations."""
    # Annotate variables with complex types
    attributes: Dict[str, Any] = {"key": "value"}
    result: Optional[Dict[str, Any]] = None
    
    # Test implementation
```

**Test Cases Required:**

```python
# Test 1: Main branch metadata interface (backwards compat)
def test_main_branch_metadata_interface(mock_get_current_span):
    """Test main branch metadata parameter works."""
    # Mock span
    mock_span = Mock()
    mock_get_current_span.return_value = mock_span
    
    # Call with main branch interface
    enrich_span(metadata={"user_id": "123", "feature": "chat"})
    
    # Verify namespacing via _set_span_attributes
    # honeyhive_metadata.user_id = "123"
    # honeyhive_metadata.feature = "chat"

# Test 2: Multiple reserved namespaces
def test_main_branch_multiple_namespaces(mock_get_current_span):
    """Test multiple reserved namespaces work together."""
    mock_span = Mock()
    mock_get_current_span.return_value = mock_span
    
    enrich_span(
        metadata={"session": "abc"},
        metrics={"score": 0.95},
        feedback={"rating": 5}
    )
    
    # Verify each namespace is properly prefixed

# Test 3: Arbitrary kwargs → metadata
def test_arbitrary_kwargs_to_metadata(mock_get_current_span):
    """Test arbitrary kwargs route to metadata namespace."""
    mock_span = Mock()
    mock_get_current_span.return_value = mock_span
    
    enrich_span(user_id="123", feature="chat", score=0.95)
    
    # All should route to honeyhive_metadata.*

# Test 4: Nested dict namespacing
def test_nested_dict_namespacing(mock_get_current_span):
    """Test nested dicts are properly namespaced via _set_span_attributes."""
    mock_span = Mock()
    mock_get_current_span.return_value = mock_span
    
    enrich_span(config={"model": "gpt-4", "params": {"temp": 0.7}})
    
    # Verify recursive namespacing:
    # honeyhive_config.model = "gpt-4"
    # honeyhive_config.params.temp = 0.7

# Test 5: Simple dict → metadata
def test_simple_dict_to_metadata(mock_get_current_span):
    """Test simple dict routes to metadata namespace."""
    mock_span = Mock()
    mock_get_current_span.return_value = mock_span
    
    enrich_span({"user_id": "123", "feature": "chat"})
    
    # Should route to honeyhive_metadata.*

# Test 6: Error and event_id (non-namespaced)
def test_error_and_event_id_attributes(mock_get_current_span):
    """Test error and event_id are not namespaced."""
    mock_span = Mock()
    mock_get_current_span.return_value = mock_span
    
    enrich_span(error="test error", event_id="uuid-123")
    
    # Verify direct attribute setting:
    # honeyhive_error (no nesting)
    # honeyhive_event_id (no nesting)

# Test 7: All reserved params together
def test_all_reserved_parameters(mock_get_current_span):
    """Test all reserved parameters work together."""
    mock_span = Mock()
    mock_get_current_span.return_value = mock_span
    
    enrich_span(
        metadata={"a": 1},
        metrics={"b": 2},
        feedback={"c": 3},
        inputs={"d": 4},
        outputs={"e": 5},
        config={"f": 6},
        error="err",
        event_id="uuid"
    )
    
    # Verify all namespaces are applied correctly

# Test 8: Context manager pattern
def test_context_manager_pattern(mock_get_current_span):
    """Test context manager pattern works with namespacing."""
    mock_span = Mock()
    mock_get_current_span.return_value = mock_span
    
    with enrich_span(metadata={"key": "value"}) as span:
        assert span is not None
    
    # Verify attributes were set

# Test 9: No active span (error case)
def test_no_active_span(mock_get_current_span):
    """Test graceful handling when no span is active."""
    mock_get_current_span.return_value = None
    
    result = enrich_span(metadata={"key": "value"})
    
    # Should handle gracefully, not crash

# Test 10: Parameter precedence and merge behavior
def test_parameter_precedence_merge(mock_get_current_span):
    """Test parameter precedence when same key in multiple places."""
    mock_span = Mock()
    mock_get_current_span.return_value = mock_span
    
    # Test merge behavior: kwargs should win
    enrich_span(
        metadata={"user_id": "from_metadata", "session": "abc"},
        attributes={"user_id": "from_attributes", "feature": "chat"},
        user_id="from_kwargs"  # This should win
    )
    
    # Verify final values (kwargs wins, others preserved)
    # honeyhive_metadata.user_id = "from_kwargs"
    # honeyhive_metadata.session = "abc"
    # honeyhive_metadata.feature = "chat"

# Test 11: Edge cases
def test_edge_cases(mock_get_current_span):
    """Test edge cases: empty dicts, None values, etc."""
    mock_span = Mock()
    mock_get_current_span.return_value = mock_span
    
    # Empty metadata
    enrich_span(metadata={})
    
    # None values
    enrich_span(metadata=None, metrics=None)
    
    # Should handle gracefully
```

**Coverage Requirements:**
- All branches in `enrich_span_core()`
- All namespace routing paths
- Error handling paths
- Context manager entry/exit
- Direct call vs context manager patterns

---

### Integration Tests

**Path:** Integration test path - Use REAL dependencies  
**File:** `tests/integration/test_tracer_integration.py`  
**Target:** Backend verification via centralized helpers

**🚨 MANDATORY:** Use standard fixtures and validation helpers

**Testing Approach:**
- ✅ Use `integration_tracer` fixture (NOT manual tracer creation)
- ✅ Use `integration_client` fixture for API access
- ✅ Use `verify_tracer_span()` from `tests.utils.validation_helpers`
- ✅ Generate unique IDs via `tests.utils.unique_id.generate_test_id()`
- ✅ Verify attributes appear in backend
- ✅ Use fixtures from `tests/integration/conftest.py`

**Test Cases Required:**

```python
from tests.utils.validation_helpers import verify_tracer_span
from tests.utils.unique_id import generate_test_id

def test_enrich_span_backwards_compatible(
    integration_tracer, 
    integration_client, 
    real_project
):
    """Test enrich_span works with main branch interface end-to-end."""
    
    # Generate unique identifier for backend verification
    test_id, unique_id = generate_test_id("enrich_span_compat", "integration")
    
    # Create a traced operation
    with integration_tracer.start_span("test_enrichment") as span:
        # Use main branch interface
        enrich_span(
            metadata={"user_id": "123", "test_id": unique_id},
            metrics={"score": 0.95},
            feedback={"rating": 5}
        )
    
    # Flush to ensure data reaches backend
    integration_tracer.force_flush()
    
    # Use centralized validation helper
    verified_event = verify_tracer_span(
        tracer=integration_tracer,
        client=integration_client,
        project=real_project,
        span_name="test_enrichment",
        unique_identifier=unique_id,
        span_attributes={
            "honeyhive_metadata.user_id": "123",
            "honeyhive_metrics.score": 0.95,
            "honeyhive_feedback.rating": 5
        }
    )
    
    # Assert backend verification succeeded
    assert verified_event is not None
    assert verified_event.event_name == "test_enrichment"

def test_enrich_span_arbitrary_kwargs_integration(
    integration_tracer,
    integration_client,
    real_project
):
    """Test arbitrary kwargs work end-to-end."""
    
    test_id, unique_id = generate_test_id("enrich_kwargs", "integration")
    
    with integration_tracer.start_span("test_kwargs") as span:
        # New feature: arbitrary kwargs
        enrich_span(
            user_id="456",
            feature="chat",
            test_id=unique_id
        )
    
    integration_tracer.force_flush()
    
    verified_event = verify_tracer_span(
        tracer=integration_tracer,
        client=integration_client,
        project=real_project,
        span_name="test_kwargs",
        unique_identifier=unique_id,
        span_attributes={
            "honeyhive_metadata.user_id": "456",
            "honeyhive_metadata.feature": "chat"
        }
    )
    
    assert verified_event is not None

def test_enrich_span_nested_structures_integration(
    integration_tracer,
    integration_client,
    real_project
):
    """Test nested dicts/lists work end-to-end."""
    
    test_id, unique_id = generate_test_id("enrich_nested", "integration")
    
    with integration_tracer.start_span("test_nested") as span:
        enrich_span(
            config={"model": "gpt-4", "params": {"temp": 0.7}},
            metadata={"test_id": unique_id}
        )
    
    integration_tracer.force_flush()
    
    verified_event = verify_tracer_span(
        tracer=integration_tracer,
        client=integration_client,
        project=real_project,
        span_name="test_nested",
        unique_identifier=unique_id,
        span_attributes={
            "honeyhive_config.model": "gpt-4",
            "honeyhive_config.params.temp": 0.7
        }
    )
    
    assert verified_event is not None
```

**❌ DON'T DO THIS:**
```python
# WRONG: Manual tracer creation
def test_wrong_approach(real_api_key, real_project):
    tracer = HoneyHiveTracer(api_key=real_api_key, project=real_project)
    # Missing OTLP config, wrong pattern!

# WRONG: Manual validation
def test_wrong_validation(integration_tracer, integration_client):
    # ... create span ...
    events = integration_client.events.list_events(project=...)
    # Manual search instead of centralized helper!
```

---

### Backwards Compatibility Test

**File:** `tests/compatibility/test_backward_compatibility.py`

Update existing test (currently failing at line 111):

```python
def test_enrich_span_compatibility(self):
    """Test that enrich_span function works with all interfaces."""
    from honeyhive import enrich_span
    
    # Main branch interface - all reserved params
    enrich_span(metadata={"test": "value"})
    enrich_span(metrics={"score": 1.0})
    enrich_span(feedback={"rating": 5})
    enrich_span(inputs={"prompt": "test"})
    enrich_span(outputs={"response": "test"})
    enrich_span(config={"model": "gpt-4"})
    enrich_span(error="test error")
    enrich_span(event_id="test-uuid")
    
    # New features - arbitrary kwargs
    enrich_span(user_id="123", feature="chat")
    
    # New features - simple dict
    enrich_span({"user_id": "123"})
    
    # Combined - multiple namespaces
    enrich_span(
        metadata={"a": 1},
        metrics={"b": 2},
        user_id="123"  # arbitrary kwarg
    )
```

---

### Test Execution & Validation

**Run unit tests:**
```bash
pytest tests/unit/test_tracer_instrumentation_enrichment.py -v --cov=src/honeyhive/tracer/instrumentation/enrichment --cov-report=term-missing
```

**Coverage target:** 90%+ line coverage

**Run integration tests:**
```bash
pytest tests/integration/test_tracer_integration.py -k enrich_span -v
```

**Run backwards compatibility:**
```bash
pytest tests/compatibility/test_backward_compatibility.py::TestBackwardCompatibility::test_enrich_span_compatibility -v
```

**Run all enrichment tests:**
```bash
pytest -k "enrich_span" -v
```

---

## Backwards Compatibility Verification

### Compatibility Matrix

| Main Branch Usage | Current Status | After Fix |
|-------------------|----------------|-----------|
| `enrich_span(metadata={...})` | ❌ Broken | ✅ Works |
| `enrich_span(metrics={...})` | ❌ Broken | ✅ Works |
| `enrich_span(feedback={...})` | ❌ Broken | ✅ Works |
| `enrich_span(inputs={...})` | ❌ Broken | ✅ Works |
| `enrich_span(outputs={...})` | ❌ Broken | ✅ Works |
| `enrich_span(config={...})` | ❌ Broken | ✅ Works |
| `enrich_span(error="...")` | ❌ Broken | ✅ Works |
| `enrich_span(event_id="...")` | ❌ Broken | ✅ Works |
| Multiple namespaces | ❌ Broken | ✅ Works |
| Nested dicts/lists | ❌ Broken | ✅ Works |

### New Features (Bonus)

| New Feature | Status |
|-------------|--------|
| `enrich_span(user_id="123")` - arbitrary kwargs | ✅ Added |
| `enrich_span({"key": "value"})` - simple dict | ✅ Added |
| `with enrich_span(...) as span:` - context manager | ✅ Supported |

---

## Documentation Updates Needed

### Files to Update

1. **Tutorial:** `docs/tutorials/03-enable-span-enrichment.rst`
   - Verify examples work with fixed implementation
   - Add examples of new features (arbitrary kwargs)

2. **How-to Guide:** `docs/how-to/advanced-tracing/span-enrichment.rst`
   - Update pattern examples
   - Show both old and new interfaces

3. **Reference:** `docs/reference/api/decorators.rst`
   - Document complete signature
   - Show namespace routing behavior

### Example Documentation

```rst
Backwards Compatible Usage
---------------------------

The original interface is fully supported:

.. code-block:: python

   # Reserved namespaces (main branch compatible)
   enrich_span(
       metadata={"user_id": "123", "feature": "chat"},
       metrics={"latency_ms": 150, "tokens": 50},
       feedback={"rating": 5, "helpful": True}
   )

New Simplified Interface
------------------------

Arbitrary keywords route to metadata namespace:

.. code-block:: python

   # New: arbitrary kwargs → metadata
   enrich_span(user_id="123", feature="chat", score=0.95)
   # Equivalent to:
   # enrich_span(metadata={"user_id": "123", "feature": "chat", "score": 0.95})

Simple Dict Interface
---------------------

Pass a dict directly for metadata:

.. code-block:: python

   # New: simple dict → metadata
   enrich_span({"user_id": "123", "feature": "chat"})
```

---

## Success Criteria

### Must Have
- ✅ All main branch `enrich_span` calls work without modification
- ✅ Attributes are properly namespaced (`honeyhive_metadata.*`, etc.)
- ✅ Nested dicts/lists are recursively processed
- ✅ All backwards compatibility tests pass
- ✅ No breaking changes for existing users

### Should Have
- ✅ Arbitrary kwargs route to metadata namespace
- ✅ Simple dict support for convenience
- ✅ Context manager pattern works
- ✅ Documentation updated

### Nice to Have
- ✅ Performance is maintained or improved
- ✅ Code is more maintainable than before
- ✅ Clear error messages for misuse

---

## Risk Assessment

### Low Risk
- Using existing `_set_span_attributes()` helper (already tested)
- Adding parameters to function signature (backwards compatible)
- Namespace routing logic is straightforward

### Medium Risk
- Complex interaction between `attributes`, reserved params, and `**kwargs`
- Need careful testing of parameter precedence
- Context manager pattern must still work

### Mitigation
- Comprehensive unit tests for all parameter combinations
- Integration tests with real tracers
- Manual testing with documentation examples

---

## Timeline Estimate

- **Investigation:** ✅ Complete
- **Implementation:** 2-3 hours
  - Core logic: 1 hour
  - Class updates: 30 min
  - Testing: 1 hour
  - Documentation: 30 min
- **Testing & Validation:** 1 hour
- **Total:** 3-4 hours

---

## Appendix A: Code Snippets

### Current `enrich_span_core()` (Broken)

```python
def enrich_span_core(
    attributes: Optional[Dict[str, Any]] = None,
    tracer_instance: Optional[Any] = None,
    verbose: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    # Combine attributes and kwargs dynamically
    all_attributes = attributes.copy() if attributes else {}
    all_attributes.update(kwargs)
    
    # Apply attributes to the span
    for key, value in all_attributes.items():
        current_span.set_attribute(key, value)  # ❌ NO NAMESPACING
```

### Fixed `enrich_span_core()` (Proposed)

```python
def enrich_span_core(
    attributes: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    event_id: Optional[str] = None,
    tracer_instance: Optional[Any] = None,
    verbose: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Core enrichment logic with namespace support."""
    from .decorators import _set_span_attributes
    
    current_span = trace.get_current_span()
    if not current_span or not hasattr(current_span, "set_attribute"):
        return {"success": False, "span": NoOpSpan(), "error": "No active span"}
    
    attribute_count = 0
    
    # STEP 1: Apply reserved namespaces first (highest priority)
    if metadata:
        _set_span_attributes(current_span, "honeyhive_metadata", metadata)
        attribute_count += len(metadata)
    if metrics:
        _set_span_attributes(current_span, "honeyhive_metrics", metrics)
        attribute_count += len(metrics)
    if feedback:
        _set_span_attributes(current_span, "honeyhive_feedback", feedback)
        attribute_count += len(feedback)
    if inputs:
        _set_span_attributes(current_span, "honeyhive_inputs", inputs)
        attribute_count += len(inputs)
    if outputs:
        _set_span_attributes(current_span, "honeyhive_outputs", outputs)
        attribute_count += len(outputs)
    if config:
        _set_span_attributes(current_span, "honeyhive_config", config)
        attribute_count += len(config)
    
    # STEP 2: Apply simple attributes dict → metadata (overwrites conflicts)
    if attributes:
        _set_span_attributes(current_span, "honeyhive_metadata", attributes)
        attribute_count += len(attributes)
    
    # STEP 3: Apply arbitrary kwargs → metadata (lowest priority, wins conflicts)
    if kwargs:
        _set_span_attributes(current_span, "honeyhive_metadata", kwargs)
        attribute_count += len(kwargs)
    
    # Handle special non-namespaced attributes
    if error:
        current_span.set_attribute("honeyhive_error", error)
        attribute_count += 1
    if event_id:
        current_span.set_attribute("honeyhive_event_id", event_id)
        attribute_count += 1
    
    return {
        "success": True,
        "span": current_span,
        "attribute_count": attribute_count,
    }
```

---

## Appendix B: File Locations

### Files to Modify
- `src/honeyhive/tracer/instrumentation/enrichment.py` - Core implementation
- `tests/unit/test_tracer_instrumentation_enrichment.py` - Unit tests
- `tests/compatibility/test_backward_compatibility.py` - Update existing test
- `tests/integration/test_tracer_integration.py` - Integration tests

### Files to Reference (No Changes)
- `src/honeyhive/tracer/instrumentation/decorators.py` - Use `_set_span_attributes()`
- `src/honeyhive/tracer/processing/span_processor.py` - Reference namespace constants

### Files to Review
- `docs/tutorials/03-enable-span-enrichment.rst` - Verify examples
- `docs/how-to/advanced-tracing/span-enrichment.rst` - Verify patterns
- `examples/advanced_usage.py` - Verify example code

---

## Appendix C: Validation Commands

```bash
# Run unit tests
pytest tests/unit/test_tracer_instrumentation_enrichment.py -v

# Run backwards compatibility tests
pytest tests/compatibility/test_backward_compatibility.py::TestBackwardCompatibility::test_enrich_span_compatibility -v

# Run integration tests
pytest tests/integration/test_tracer_integration.py -k enrich_span -v

# Run all enrichment-related tests
pytest -k "enrich_span" -v

# Verify no regressions
pytest tests/ -v
```

---

## Questions for Review

1. Should `attributes` parameter take precedence over explicit `metadata` parameter if both are provided?
2. Should we validate/warn if users pass both `attributes` and `metadata`?
3. Should `error` support nested dicts or remain string-only like main branch?
4. Do we need to handle `event_id` UUID validation like main branch did?

---

**End of Design Document**

