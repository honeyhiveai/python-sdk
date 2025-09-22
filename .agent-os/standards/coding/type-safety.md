# Type Safety Standards - HoneyHive Python SDK

**🎯 MISSION: Maintain strict type safety to prevent runtime errors and improve code reliability**

This document defines comprehensive type safety standards for the HoneyHive Python SDK, with special focus on preventing the attribute access errors that occurred during the tracer refactor.

## 🚨 CRITICAL: The Refactor Lesson

**Case Study: Tracer Refactor Type Safety Failures (2025-09-15)**

During the tracer refactor, multiple attribute access errors slipped through despite having MyPy type checking:

```python
# ❌ What Happened: These errors were NOT caught by MyPy
def initialize_tracer(tracer_instance: Any) -> None:  # Any disables type checking!
    project = tracer_instance.project  # AttributeError at runtime
    source = tracer_instance.source    # AttributeError at runtime
    api_key = tracer_instance.api_key  # AttributeError at runtime
```

**Root Cause**: Using `Any` type annotations disabled MyPy's ability to catch attribute access errors.

**Prevention**: Proper forward references with `TYPE_CHECKING` blocks.

## ✅ Forward Reference Patterns (MANDATORY)

### Standard Forward Reference Pattern

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import HoneyHiveTracer

def initialize_tracer(tracer_instance: "HoneyHiveTracer") -> None:
    """Initialize tracer with proper type safety."""
    # MyPy now catches: tracer_instance.nonexistent_attribute
    project = tracer_instance.project_name  # ✅ Correct attribute access
    source = tracer_instance.source_environment  # ✅ Correct attribute access
```

### Multiple Forward References

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import HoneyHiveTracer
    from ..processing import SpanProcessor
    from ..integration import ProviderDetector

def complex_function(
    tracer: "HoneyHiveTracer",
    processor: "SpanProcessor", 
    detector: "ProviderDetector"
) -> None:
    """Function with multiple forward references."""
    pass
```

### Protocol-Based Forward References

```python
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ..core import HoneyHiveTracer

class TracerProtocol(Protocol):
    """Protocol defining tracer interface for type checking."""
    def project_name(self) -> str: ...
    def source_environment(self) -> str: ...
    def is_initialized(self) -> bool: ...

def process_tracer(tracer: TracerProtocol) -> None:
    """Process tracer using protocol for type safety."""
    # MyPy validates these attributes exist
    print(f"Project: {tracer.project_name}")
    print(f"Source: {tracer.source_environment}")
```

## ❌ Prohibited Patterns

### Never Use `Any` for Domain Objects

```python
# ❌ PROHIBITED: Disables all type checking
def process_tracer(tracer: Any) -> None:
    tracer.nonexistent_method()  # MyPy won't catch this error!

# ✅ REQUIRED: Use proper forward reference
def process_tracer(tracer: "HoneyHiveTracer") -> None:
    tracer.nonexistent_method()  # MyPy catches this error!
```

### Never Use Untyped Parameters in New Code

```python
# ❌ PROHIBITED: Missing type annotations
def legacy_function(data):  # No type hints
    return data.process()

# ✅ REQUIRED: Complete type annotations
def modern_function(data: Dict[str, Any]) -> ProcessedData:
    return ProcessedData(data)
```

### Never Ignore Type Errors Without Justification

```python
# ❌ PROHIBITED: Hiding type errors
result = unsafe_function()  # type: ignore

# ✅ REQUIRED: Justified type ignores with explanation
result = legacy_api_call()  # type: ignore[attr-defined]  # Legacy API, will be removed in v2.0
```

## 🔧 Circular Import Resolution Strategies

### Strategy 1: TYPE_CHECKING Blocks (Preferred)

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Import only for type checking, not at runtime
    from ..module_that_imports_us import CircularClass

def function(param: "CircularClass") -> None:
    """Function using forward reference to break circular import."""
    pass
```

### Strategy 2: Late Imports (When Necessary)

```python
def function() -> "CircularClass":
    """Function with late import to avoid circular dependency."""
    from ..module_that_imports_us import CircularClass  # Import inside function
    return CircularClass()
```

### Strategy 3: Protocol Interfaces (Complex Cases)

```python
from typing import Protocol

class CircularProtocol(Protocol):
    """Protocol to break circular dependency."""
    def method(self) -> str: ...
    def property_name(self) -> str: ...

def function(obj: CircularProtocol) -> None:
    """Function using protocol instead of concrete class."""
    result = obj.method()
    name = obj.property_name
```

## 🎯 MyPy Configuration Requirements

### Project-Level Configuration (pyproject.toml)

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true

# Per-module configuration
[[tool.mypy.overrides]]
module = "honeyhive.tracer.*"
strict = true
disallow_any_generics = true
```

### CI/CD Integration

```bash
# MANDATORY: MyPy must pass in all environments
python -m mypy src/honeyhive/tracer/ --strict
python -m mypy src/honeyhive/tracer/ --html-report mypy-reports/
python -m mypy src/honeyhive/tracer/ --any-exprs-report mypy-any/
```

### Coverage Tracking

```bash
# Monitor type coverage percentage
python -m mypy --html-report mypy-reports src/
# Target: >95% type coverage for new modules
```

## 🔄 Refactoring Type Safety Protocol

### Pre-Refactor Validation

```bash
# 1. Establish type safety baseline
python -m mypy src/module/ --show-error-codes > mypy-baseline.txt
python -m mypy --html-report mypy-before src/

# 2. Document current type coverage
python -m mypy --any-exprs-report mypy-any-before src/

# 3. Identify `Any` usage that needs fixing
grep -r ": Any" src/module/ > any-usage-before.txt
```

### During Refactor Requirements

**MANDATORY Rules:**
- ✅ **Never use `Any`** as temporary solution for type errors
- ✅ **Use forward references** with `TYPE_CHECKING` blocks immediately
- ✅ **Maintain or improve** type coverage percentage
- ✅ **Test type safety** after each logical change
- ✅ **Fix type errors** before moving to next component

**Prohibited Shortcuts:**
- ❌ **Never add `# type: ignore`** without specific justification
- ❌ **Never defer type fixes** to "later cleanup"
- ❌ **Never use `cast()`** to bypass type checking
- ❌ **Never remove type annotations** to "fix" errors

### Post-Refactor Validation

```bash
# Must pass with equal or better coverage
python -m mypy src/module/ --strict
python -m mypy --html-report mypy-after src/

# Compare coverage improvements
diff mypy-any-before/ mypy-any-after/
```

## 🤖 AI Assistant Type Safety Requirements

### Pre-Generation Type Validation

```bash
# MANDATORY: Check current type annotations before generating code
python -m mypy src/honeyhive/tracer/ --show-error-codes
grep -r ": Any" src/honeyhive/tracer/  # Should return minimal results
```

### Prohibited AI Assistant Patterns

- ❌ **Never use `Any`** for function parameters in new code
- ❌ **Never ignore type errors** with `# type: ignore` without justification
- ❌ **Never generate untyped code** in typed modules
- ❌ **Never use string imports** instead of proper forward references

### Required AI Assistant Actions

- ✅ **Always add `TYPE_CHECKING` blocks** for forward references
- ✅ **Always use quoted type hints** for forward references: `"ClassName"`
- ✅ **Always run MyPy** after generating typed code
- ✅ **Always fix type errors** before committing
- ✅ **Always validate attribute access** against actual class definitions

### AI Assistant Validation Checklist

```bash
# Before generating any code with type annotations:
1. read_file src/honeyhive/tracer/core/__init__.py  # Check actual exports
2. grep -r "class HoneyHiveTracer" src/  # Verify class definition
3. python -c "from honeyhive.tracer import HoneyHiveTracer; help(HoneyHiveTracer)" # Check methods
4. python -m mypy --show-error-codes src/  # Validate current state
```

## 📊 Type Coverage Requirements

### Coverage Targets

- **New modules**: 100% type coverage required
- **Refactored modules**: Must maintain or improve existing coverage
- **Legacy modules**: Minimum 80% type coverage for major changes
- **Critical paths**: 100% type coverage (API clients, decorators, core functionality)

### Measurement Tools

```bash
# Generate type coverage reports
python -m mypy --html-report mypy-reports src/
python -m mypy --any-exprs-report mypy-any src/

# Monitor `Any` usage (should decrease over time)
python -m mypy --any-exprs-report mypy-any src/ | grep -c "Any"
```

### Quality Gates

```bash
# CI/CD type safety gates
python -m mypy src/ --strict                    # Must pass
python -m mypy src/ --warn-unused-ignores       # No unused ignores
python -m mypy src/ --disallow-any-generics     # No generic Any usage
```

## 🔍 Complex Type Scenarios

### Generic Types with Constraints

```python
from typing import TypeVar, Generic, Protocol

T = TypeVar('T', bound='Traceable')

class Traceable(Protocol):
    """Protocol for objects that can be traced."""
    def get_trace_id(self) -> str: ...

class TracerManager(Generic[T]):
    """Generic tracer manager with type constraints."""
    
    def __init__(self, tracer_class: type[T]) -> None:
        self._tracer_class = tracer_class
    
    def create_tracer(self) -> T:
        return self._tracer_class()
```

### Union Types and Optional Handling

```python
from typing import Union, Optional

# Prefer Union over Any
def process_data(data: Union[str, bytes, None]) -> Optional[str]:
    """Process data with explicit type union."""
    if data is None:
        return None
    if isinstance(data, bytes):
        return data.decode('utf-8')
    return data

# Use Optional for nullable values
def get_session_id(tracer: "HoneyHiveTracer") -> Optional[str]:
    """Get session ID, may be None."""
    return getattr(tracer, '_session_id', None)
```

### Callback and Function Types

```python
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')

def with_tracing(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator with proper type preservation."""
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # Tracing logic here
        return func(*args, **kwargs)
    return wrapper
```

## 🛡️ Error Prevention Patterns

### Attribute Access Validation

```python
# ✅ SAFE: Check attribute existence before access
def safe_attribute_access(obj: "HoneyHiveTracer") -> Optional[str]:
    """Safely access tracer attributes."""
    if hasattr(obj, 'project_name'):
        return obj.project_name
    return None

# ✅ SAFE: Use getattr with default
def get_project_name(obj: "HoneyHiveTracer") -> str:
    """Get project name with fallback."""
    return getattr(obj, 'project_name', 'unknown')
```

### Type Guards for Runtime Validation

```python
from typing import TypeGuard

def is_initialized_tracer(obj: "HoneyHiveTracer") -> TypeGuard["InitializedTracer"]:
    """Type guard to check if tracer is initialized."""
    return hasattr(obj, '_initialized') and obj._initialized

def process_tracer(tracer: "HoneyHiveTracer") -> None:
    """Process tracer with type guard validation."""
    if is_initialized_tracer(tracer):
        # MyPy knows tracer is InitializedTracer here
        tracer.process_spans()  # This method only exists on initialized tracers
```

## 📋 Quality Checklist

### For New Code
- [ ] All functions have complete type annotations
- [ ] No usage of `Any` for domain objects
- [ ] Forward references use `TYPE_CHECKING` blocks
- [ ] MyPy passes with `--strict` mode
- [ ] All attribute access is validated against actual class definitions

### For Refactored Code
- [ ] Type coverage maintained or improved
- [ ] All `Any` usage replaced with proper types
- [ ] Circular imports resolved with proper patterns
- [ ] All attribute access errors fixed
- [ ] MyPy baseline improved from pre-refactor state

### For AI Assistant Generated Code
- [ ] Current codebase validated before generation
- [ ] Proper forward references used
- [ ] No hardcoded assumptions about class attributes
- [ ] Type annotations match actual implementation
- [ ] MyPy validation performed before commit

## 🔗 References

### Related Standards
- **[Python Standards](python-standards.md)** - General Python coding guidelines
- **[Refactoring Protocols](refactoring-protocols.md)** - Safe refactoring practices
- **[Code Quality](../development/code-quality.md)** - Quality gates and tool configuration

### External Resources
- **[MyPy Documentation](https://mypy.readthedocs.io/)** - Official MyPy documentation
- **[PEP 484](https://peps.python.org/pep-0484/)** - Type Hints specification
- **[PEP 563](https://peps.python.org/pep-0563/)** - Postponed Evaluation of Annotations

---

**📝 Next Steps**: Review [Refactoring Protocols](refactoring-protocols.md) for safe refactoring practices that maintain type safety.
