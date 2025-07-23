# Evaluation Harness Refactoring Analysis

## Current Architecture Issues

### src/honeyhive/evaluation/__init__.py (708 lines)
- **Monolithic Evaluation class**: Single class handling config, dataset management, execution, tracing, and results
- **Complex initialization**: 150+ line `__init__` method with multiple validation steps  
- **Method duplication**: Separate sync/async versions of similar methods (`_run_single_evaluator` vs `_arun_single_evaluator`)
- **Inconsistent error handling**: Mix of print statements, raised exceptions, and silent failures

### src/honeyhive/evaluation/evaluators.py (1168 lines)
- **Security risk**: Heavy use of `eval()` for dynamic code execution in aggregation
- **Complex metaclass**: `EvaluatorMeta` makes code hard to understand and debug
- **Massive code duplication**: ~50 line methods duplicated for sync/async versions
- **Overloaded settings**: `EvaluatorSettings` class has too many responsibilities

## Proposed Refactoring Structure

```
src/honeyhive/evaluation/
├── core/
│   ├── config.py         # EvaluationConfig, DatasetConfig
│   ├── dataset.py        # DatasetManager, DatasetValidator  
│   ├── runner.py         # EvaluationRunner
│   ├── tracing.py        # TracingManager
│   └── results.py        # ResultProcessor, ResultFormatter
├── evaluators/
│   ├── base.py           # BaseEvaluator, EvaluatorSettings
│   ├── decorators.py     # @evaluator, @aevaluator decorators
│   ├── engines.py        # TransformationEngine, AggregationEngine
│   └── expressions.py    # Safe expression evaluation (replaces eval())
└── exceptions.py         # Custom exception hierarchy
```

## Key Refactoring Opportunities

### 1. Extract Configuration Management
**Current**: Mixed in 680+ line Evaluation class
**Proposed**: Dedicated `EvaluationConfig` class with validation

### 2. Replace eval() with Safe Expression Parser
**Current**: `aggregate_score = eval(aggregation_expr, evaluator.all_evaluators, locals_dict)`
**Proposed**: AST-based safe expression evaluator

### 3. Unify Async/Sync Patterns  
**Current**: Duplicate method implementations
**Proposed**: Common core logic with async wrappers

### 4. Implement Exception Hierarchy
```python
class EvaluationException(Exception): pass
class ConfigurationError(EvaluationException): pass  
class DatasetError(EvaluationException): pass
class EvaluatorError(EvaluationException): pass
class TracingError(EvaluationException): pass
```

### 5. Add Comprehensive Type Hints
Many methods lack return type annotations and proper generic types

## Implementation Priority
1. **High**: Extract configuration classes (reduces complexity)
2. **High**: Replace eval() usage (security critical)  
3. **Medium**: Add exception hierarchy (improves debugging)
4. **Medium**: Comprehensive type hints (developer experience)
5. **Low**: Async optimization (performance)

## Benefits
- **Security**: Eliminates dangerous eval() usage
- **Maintainability**: Smaller, focused classes  
- **Testability**: Individual components can be unit tested
- **Type Safety**: Better IDE support and error catching
- **Extensibility**: Plugin-based evaluator architecture