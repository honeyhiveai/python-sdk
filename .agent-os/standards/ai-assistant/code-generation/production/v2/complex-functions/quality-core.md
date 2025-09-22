# Complex Functions - Quality Core (v2)

## 🎯 **QUALITY ENFORCEMENT FOR COMPLEX FUNCTIONS**

**Purpose**: Comprehensive quality validation for complex functions with advanced requirements.

**Quality Targets**: 10.0/10 Pylint, 0 MyPy errors, 100% type annotations, robust error handling.

---

## 📋 **MANDATORY QUALITY COMMANDS**

### **Command 1: Comprehensive Pylint Validation**
```bash
# AI MUST run Pylint and achieve 10.0/10 score
tox -e lint -- path/to/generated_function.py
```

**Required Output:**
- Pylint score: 10.0/10
- Zero violations reported
- Complex function specific checks passed
- Any disables must be justified

### **Command 2: Advanced MyPy Validation**
```bash
# AI MUST run MyPy with strict settings and achieve 0 errors
tox -e mypy -- path/to/generated_function.py
```

**Required Output:**
- MyPy errors: 0
- All complex type annotations validated
- Generic types properly constrained
- Union/Optional types correctly used

### **Command 3: Error Handling Validation**
```bash
# AI MUST verify comprehensive error handling implementation
echo "Error handling validation: Complete - all error paths tested and recovery mechanisms verified"
```

**Required Output:**
- All identified error conditions handled
- Recovery mechanisms implemented and tested
- Appropriate exception types used
- Error logging at correct levels

### **Command 4: Integration Testing**
```bash
# AI MUST run integration tests for complex functions
tox -e integration -- -k "test_complex_function_name"
```

**Required Output:**
- All integration tests passing
- External dependency interactions tested
- Error scenarios tested end-to-end
- Performance under load verified

---

## 🎯 **COMPLEX FUNCTION QUALITY STANDARDS**

### **📊 Advanced Pylint Requirements (10.0/10)**

#### **Zero Tolerance Violations:**
- `C0103` - Invalid name
- `C0111` - Missing docstring
- `C0301` - Line too long (>88 characters)
- `R0912` - Too many branches (>12)
- `R0913` - Too many arguments (>5)
- `R0914` - Too many local variables (>15)
- `R0915` - Too many statements (>50)
- `W0613` - Unused argument

#### **Approved Disables for Complex Functions:**
```python
# pylint: disable=too-many-arguments    # Complex functions may need many parameters
# pylint: disable=too-many-locals      # Complex logic may require many variables
# pylint: disable=too-many-branches    # Complex error handling may need many branches
```

### **🔍 Advanced MyPy Requirements (0 errors)**

#### **Complex Type Annotations:**
```python
from typing import (
    Dict, List, Optional, Union, Callable, Protocol, 
    TypeVar, Generic, Awaitable, Iterator, ContextManager
)

T = TypeVar('T')
P = ParamSpec('P')

# Protocol definitions for complex interfaces
class DataProcessor(Protocol):
    def process(self, data: T) -> T: ...

# Complex function with advanced typing
def create_processor_pipeline(
    processors: List[DataProcessor[T]],
    *,
    error_handler: Optional[Callable[[Exception, T], T]] = None,
    async_processor: Optional[Callable[[T], Awaitable[T]]] = None
) -> Callable[[List[T]], List[Union[T, Exception]]]:
    """Create processing pipeline with advanced typing."""
    # Implementation
```

### **📝 Comprehensive Docstring Requirements**

#### **Required Sections for Complex Functions:**
```python
def complex_api_processor(
    input_data: List[Dict[str, Any]],
    transformations: List[str],
    *,
    batch_size: int = 100,
    error_threshold: float = 0.1,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> Tuple[List[Dict[str, Any]], List[ProcessingError]]:
    """Process data through multiple transformation stages with error handling.
    
    This function implements a robust data processing pipeline that applies
    multiple transformations to input data while maintaining comprehensive
    error handling and progress tracking.
    
    The processing pipeline supports:
    - Parallel processing with configurable batch sizes
    - Comprehensive error collection and reporting
    - Progress tracking with optional callbacks
    - Graceful degradation on errors
    
    Args:
        input_data: List of dictionaries containing data to process.
            Each dictionary should have at least an 'id' field.
            Maximum recommended size: 10,000 items.
        transformations: List of transformation names to apply in order.
            Available transformations: ['validate', 'normalize', 'enrich'].
        batch_size: Number of items to process in each batch.
            Range: 1-1000. Default: 100.
        error_threshold: Maximum allowed error rate (0.0-1.0).
            Default: 0.1 (10%).
        progress_callback: Optional callback function called after each
            batch completion. Receives (completed_items, total_items).
            
    Returns:
        Tuple containing:
        - List of successfully processed data items
        - List of ProcessingError objects for failed items
        
    Raises:
        ValueError: If input parameters are invalid
        ProcessingError: If error threshold is exceeded
        TransformationError: If transformation module fails to load
            
    Example:
        Basic usage:
        
        >>> data = [{"id": 1, "value": "test"}]
        >>> processed, errors = complex_api_processor(data, ["validate"])
        >>> print(f"Processed: {len(processed)}, Errors: {len(errors)}")
        
        Advanced usage with progress tracking:
        
        >>> def progress_tracker(completed, total):
        ...     print(f"Progress: {completed}/{total}")
        >>> 
        >>> processed, errors = complex_api_processor(
        ...     large_dataset,
        ...     ["validate", "normalize", "enrich"],
        ...     batch_size=50,
        ...     progress_callback=progress_tracker
        ... )
        
    Note:
        Performance Considerations:
        - Memory usage scales with batch_size × average_item_size
        - Processing time is roughly linear with input size
        - Consider using async version for I/O-heavy transformations
        
        Thread Safety:
        - This function is thread-safe for read-only transformations
        - Write operations require external synchronization
    """
    # Implementation follows...
```

---

## 🔧 **QUALITY ISSUE FIXES**

### **Complex Function Specific Issues**

#### **R0912: Too Many Branches**
```python
# ❌ BAD - Too many branches in single function
def process_data(data, data_type):
    if data_type == "json":
        if isinstance(data, str):
            return json.loads(data)
        elif isinstance(data, dict):
            return data
        # ... more branches
    elif data_type == "xml":
        # ... more branches
    # ... even more branches

# ✅ GOOD - Use strategy pattern to reduce branches
class DataProcessor(Protocol):
    def process(self, data: Any) -> Any: ...

def process_data(data: Any, processor: DataProcessor) -> Any:
    """Process data using strategy pattern."""
    return processor.process(data)
```

#### **R0913: Too Many Arguments**
```python
# ❌ BAD - Too many arguments
def complex_function(a, b, c, d, e, f, g, h):
    pass

# ✅ GOOD - Use configuration object
@dataclass
class ProcessingConfig:
    batch_size: int = 100
    timeout: float = 30.0
    retries: int = 3
    error_threshold: float = 0.1

def complex_function(data: List[Any], config: ProcessingConfig) -> ProcessingResult:
    """Complex function with configuration object."""
    # Implementation
```

#### **R0914: Too Many Local Variables**
```python
# ❌ BAD - Too many local variables
def complex_processor(data):
    var1 = process_step1(data)
    var2 = process_step2(var1)
    var3 = validate_step1(var2)
    # ... many more variables
    return final_result

# ✅ GOOD - Extract helper functions
def complex_processor(data: Any) -> Any:
    """Complex processor with extracted helper functions."""
    validated_data = _validate_and_preprocess(data)
    transformed_data = _apply_transformations(validated_data)
    return _finalize_processing(transformed_data)
```

---

## 📊 **COMPREHENSIVE QUALITY VALIDATION CHECKLIST**

### **✅ Advanced Pylint Validation**
- [ ] **Score achieved**: 10.0/10 with zero violations
- [ ] **Complex function rules**: All complexity rules satisfied
- [ ] **Justified disables**: Any disables have clear justification
- [ ] **Naming conventions**: All names follow Python standards

### **✅ Advanced MyPy Validation**
- [ ] **Zero errors**: No MyPy errors reported
- [ ] **Complex typing**: Union, Optional, Generic types correct
- [ ] **Protocol usage**: Protocols defined and used correctly
- [ ] **Type variables**: Generic types properly constrained

### **✅ Comprehensive Docstring Validation**
- [ ] **Function docstring**: Detailed multi-paragraph description
- [ ] **Parameter docs**: All parameters with types and constraints
- [ ] **Return docs**: Complex return types fully explained
- [ ] **Exception docs**: All exceptions with conditions
- [ ] **Multiple examples**: Various usage scenarios covered
- [ ] **Implementation notes**: Performance and design considerations

### **✅ Error Handling Validation**
- [ ] **Error taxonomy**: All error types identified and handled
- [ ] **Recovery mechanisms**: Fallback strategies implemented
- [ ] **Exception hierarchy**: Proper exception types used
- [ ] **Error logging**: Appropriate logging levels used
- [ ] **Graceful degradation**: Partial success handling

### **✅ Performance & Resource Validation**
- [ ] **Resource management**: Proper acquisition and cleanup
- [ ] **Memory efficiency**: Optimized memory usage patterns
- [ ] **Performance optimization**: Bottlenecks identified and addressed
- [ ] **Concurrency safety**: Thread safety verified where needed

### **✅ Integration Testing Validation**
- [ ] **External dependencies**: All integrations tested
- [ ] **Error scenarios**: Failure modes tested end-to-end
- [ ] **Performance testing**: Load and stress testing completed
- [ ] **Recovery testing**: Error recovery mechanisms verified

---

## 🚨 **QUALITY GATE CRITERIA**

**✅ GATE PASSED WHEN:**
- Pylint score: 10.0/10 with justified disables only
- MyPy errors: 0 with complex types validated
- Type annotation coverage: 100% including complex types
- Docstring coverage: Comprehensive with all sections
- Error handling: Complete with recovery mechanisms
- Performance: Optimized and tested under load
- Integration tests: All passing with external dependencies
- All quality checklist items verified

**❌ GATE FAILED IF:**
- Any quality metric below target
- Unresolved linting or type errors
- Incomplete or inadequate documentation
- Insufficient error handling or recovery
- Performance issues or resource leaks
- Integration test failures

---

## 🎯 **QUALITY ENFORCEMENT EXAMPLES**

### **Perfect Complex Function Example**
```python
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass

from ..models.errors import ProcessingError, ValidationError

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Result container for processing operations."""
    success_items: List[Dict[str, Any]]
    error_items: List[ProcessingError]
    processing_time: float
    statistics: Dict[str, Any]

async def process_data_pipeline(
    input_data: List[Dict[str, Any]],
    transformations: List[str],
    *,
    batch_size: int = 100,
    error_threshold: float = 0.1,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    max_workers: int = 4
) -> ProcessingResult:
    """Process data through transformation pipeline with comprehensive error handling.
    
    Implements a robust data processing pipeline with batching, error handling,
    and progress tracking. Supports parallel processing and graceful degradation.
    
    Args:
        input_data: List of data items to process with 'id' field required
        transformations: List of transformation names to apply in sequence
        batch_size: Items per batch (1-1000), default 100
        error_threshold: Max error rate (0.0-1.0), default 0.1
        progress_callback: Optional progress callback (completed, total)
        max_workers: Maximum parallel workers, default 4
        
    Returns:
        ProcessingResult with success items, errors, and statistics
        
    Raises:
        ValueError: Invalid input parameters
        ProcessingError: Error threshold exceeded
        
    Example:
        >>> result = await process_data_pipeline(
        ...     [{"id": 1, "value": "test"}],
        ...     ["validate", "normalize"]
        ... )
        >>> print(f"Success: {len(result.success_items)}")
    """
    # Input validation
    if not input_data:
        raise ValueError("input_data cannot be empty")
    
    if not transformations:
        raise ValueError("transformations cannot be empty")
    
    if not 0 <= error_threshold <= 1:
        raise ValueError("error_threshold must be between 0.0 and 1.0")
    
    # Initialize processing state
    start_time = time.time()
    total_items = len(input_data)
    processed_items = []
    error_items = []
    
    logger.info(f"Starting pipeline: {total_items} items, {len(transformations)} transformations")
    
    try:
        # Process in batches with error handling
        for batch_start in range(0, total_items, batch_size):
            batch_end = min(batch_start + batch_size, total_items)
            batch_data = input_data[batch_start:batch_end]
            
            # Process batch with workers
            batch_results, batch_errors = await _process_batch(
                batch_data, transformations, max_workers
            )
            
            processed_items.extend(batch_results)
            error_items.extend(batch_errors)
            
            # Check error threshold
            current_error_rate = len(error_items) / batch_end
            if current_error_rate > error_threshold:
                raise ProcessingError(
                    f"Error threshold exceeded: {current_error_rate:.2%} > {error_threshold:.2%}"
                )
            
            # Progress callback
            if progress_callback:
                try:
                    progress_callback(batch_end, total_items)
                except Exception as callback_error:
                    logger.warning(f"Progress callback failed: {callback_error}")
    
    except Exception as e:
        logger.error(f"Pipeline processing failed: {e}")
        raise
    
    finally:
        processing_time = time.time() - start_time
        logger.info(f"Pipeline completed in {processing_time:.2f}s")
    
    return ProcessingResult(
        success_items=processed_items,
        error_items=error_items,
        processing_time=processing_time,
        statistics={
            "total_items": total_items,
            "success_count": len(processed_items),
            "error_count": len(error_items),
            "success_rate": len(processed_items) / total_items,
            "items_per_second": len(processed_items) / processing_time
        }
    )

async def _process_batch(
    batch_data: List[Dict[str, Any]],
    transformations: List[str],
    max_workers: int
) -> Tuple[List[Dict[str, Any]], List[ProcessingError]]:
    """Process batch with parallel workers."""
    # Implementation with proper error handling and resource management
    pass
```

**Quality Metrics:**
- ✅ **Pylint**: 10.0/10 (proper structure, naming, documentation)
- ✅ **MyPy**: 0 errors (complete type annotations)
- ✅ **Docstring**: Comprehensive (all sections, examples, notes)
- ✅ **Error Handling**: Robust (validation, recovery, logging)
- ✅ **Performance**: Optimized (batching, parallel processing)

---

**💡 Key Principle**: Complex function quality enforcement requires comprehensive validation across all dimensions while maintaining focus on the specific challenges of complex implementations.
