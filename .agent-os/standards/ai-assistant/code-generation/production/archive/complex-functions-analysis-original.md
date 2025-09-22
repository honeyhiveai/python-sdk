# Complex Functions - Analysis Phase

## 🎯 **PHASE 2: REQUIREMENTS ANALYSIS FOR COMPLEX FUNCTIONS**

**Purpose**: Gather complete requirements for complex function generation.

**Complexity Level**: Complex (multiple responsibilities, error handling, external dependencies, state management)

---

## 📋 **MANDATORY ANALYSIS COMMANDS**

### **Command 1: Define Function Purpose & Responsibilities**
```bash
# AI MUST document all function responsibilities
echo "Function purpose: [PRIMARY PURPOSE]"
echo "Secondary responsibilities: [LIST OF SECONDARY RESPONSIBILITIES]"
```

**Required Output:**
- Primary purpose statement
- All secondary responsibilities identified
- Responsibility interaction analysis
- Complexity justification

### **Command 2: Determine Function Signature & Parameters**
```bash
# AI MUST define complex signature with all parameter types
echo "Function signature: def function_name(param1: Type1, param2: Type2, *, kwonly: Type3 = default) -> ReturnType:"
```

**Required Output:**
- Complete function name
- All positional parameters with types
- Keyword-only parameters identified
- Optional parameters with defaults
- Return type specification (may be Union/Optional)

### **Command 3: Map Dependencies & External Integrations**
```bash
# AI MUST list all dependencies and external systems
echo "Required imports: [STANDARD_LIBRARY, THIRD_PARTY, INTERNAL]"
echo "External systems: [APIs, DATABASES, FILES, SERVICES]"
```

**Required Output:**
- Standard library imports (3+ expected)
- Third-party dependencies
- Internal project imports
- External system integrations
- Dependency interaction mapping

### **Command 4: Plan Error Handling Strategy**
```bash
# AI MUST define comprehensive error handling
echo "Error handling strategy: [SPECIFIC ERROR TYPES AND RESPONSES]"
echo "Recovery mechanisms: [FALLBACK STRATEGIES]"
```

**Required Output:**
- All possible error conditions
- Exception hierarchy usage
- Error recovery strategies
- Logging requirements
- Graceful degradation plans

### **Command 5: Define State Management Requirements**
```bash
# AI MUST analyze state management needs
echo "State requirements: [STATE VARIABLES, PERSISTENCE, THREAD_SAFETY]"
```

**Required Output:**
- State variables identified
- State persistence needs
- Thread safety requirements
- State validation requirements

---

## 🔍 **COMPLEX FUNCTION ANALYSIS CHECKLIST**

### **✅ Function Purpose Analysis**
- [ ] **Primary purpose defined** - Main function responsibility clear
- [ ] **Secondary responsibilities mapped** - All additional responsibilities documented
- [ ] **Responsibility interactions analyzed** - How responsibilities interact
- [ ] **Complexity justified** - Why function requires complex approach

### **✅ Signature Analysis**
- [ ] **Function name chosen** - Descriptive of primary purpose
- [ ] **Parameter organization** - Logical grouping of parameters
- [ ] **Keyword-only parameters** - Complex parameters marked keyword-only
- [ ] **Default values strategic** - Sensible defaults for optional parameters
- [ ] **Return type complexity** - Union/Optional types used appropriately

### **✅ Dependency Analysis**
- [ ] **Import count justified** - 3+ imports with clear purpose
- [ ] **External systems mapped** - All external integrations identified
- [ ] **Dependency isolation** - Dependencies properly abstracted
- [ ] **Fallback strategies** - Plans for dependency failures

### **✅ Error Handling Analysis**
- [ ] **Error taxonomy complete** - All error types identified
- [ ] **Exception hierarchy** - Proper exception types chosen
- [ ] **Recovery strategies** - Fallback mechanisms defined
- [ ] **Logging strategy** - Appropriate logging levels planned

### **✅ State Management Analysis**
- [ ] **State variables identified** - All state requirements mapped
- [ ] **Persistence strategy** - State storage/retrieval planned
- [ ] **Thread safety assessed** - Concurrency requirements analyzed
- [ ] **State validation** - State integrity checks planned

---

## 📊 **ANALYSIS EXAMPLES**

### **Example 1: API Client with Retry Logic**
```python
# Function Purpose: Make HTTP requests with exponential backoff retry
# Secondary Responsibilities: 
#   - Request/response logging
#   - Authentication header management
#   - Response validation and parsing
#   - Circuit breaker pattern implementation
# Function Signature: 
def make_api_request(
    url: str,
    method: str = "GET",
    *,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 30.0,
    max_retries: int = 3,
    backoff_factor: float = 1.0
) -> Union[Dict[str, Any], List[Any], str]

# Required Imports: 
#   - requests, time, logging, json
#   - from typing import Optional, Dict, Any, Union, List
#   - from ..utils.auth import get_auth_headers
#   - from ..utils.logger import get_logger

# External Systems: HTTP APIs, Authentication service
# Error Handling Strategy:
#   - requests.RequestException -> retry with backoff
#   - requests.Timeout -> retry with increased timeout
#   - requests.HTTPError -> log and re-raise with context
#   - JSON decode errors -> return raw response
#   - Authentication errors -> refresh token and retry once
# Recovery Mechanisms:
#   - Exponential backoff for transient errors
#   - Circuit breaker after consecutive failures
#   - Fallback to cached response if available
# State Requirements:
#   - Request attempt counter
#   - Last successful response timestamp
#   - Circuit breaker state (open/closed/half-open)
```

### **Example 2: Data Processing Pipeline**
```python
# Function Purpose: Process data through multiple transformation stages
# Secondary Responsibilities:
#   - Input validation and sanitization
#   - Progress tracking and reporting
#   - Intermediate result caching
#   - Error aggregation and reporting
# Function Signature:
def process_data_pipeline(
    input_data: List[Dict[str, Any]],
    *,
    transformations: List[str],
    batch_size: int = 100,
    enable_caching: bool = True,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    error_threshold: float = 0.1
) -> Tuple[List[Dict[str, Any]], List[ProcessingError]]

# Required Imports:
#   - from typing import List, Dict, Any, Optional, Callable, Tuple
#   - from concurrent.futures import ThreadPoolExecutor
#   - import logging, json, hashlib
#   - from ..models.errors import ProcessingError
#   - from ..utils.cache import get_cache_client
#   - from ..transformations import get_transformer

# External Systems: Cache service, transformation modules
# Error Handling Strategy:
#   - Individual item errors -> collect and continue processing
#   - Transformation errors -> skip transformation, log warning
#   - Cache errors -> continue without caching
#   - Threshold exceeded -> abort processing, return partial results
# Recovery Mechanisms:
#   - Skip failed items and continue
#   - Fallback transformations for failed stages
#   - Partial result return on threshold breach
# State Requirements:
#   - Processing progress counter
#   - Error accumulator
#   - Cache hit/miss statistics
#   - Batch processing state
```

### **Example 3: Configuration Manager**
```python
# Function Purpose: Load and validate application configuration
# Secondary Responsibilities:
#   - Environment variable resolution
#   - Configuration file parsing
#   - Schema validation
#   - Hot reload support
# Function Signature:
def load_configuration(
    config_path: Optional[str] = None,
    *,
    environment: str = "production",
    enable_hot_reload: bool = False,
    validation_schema: Optional[Dict[str, Any]] = None,
    override_values: Optional[Dict[str, Any]] = None
) -> ConfigurationResult

# Required Imports:
#   - import os, json, yaml, logging
#   - from pathlib import Path
#   - from typing import Optional, Dict, Any
#   - from ..models.config import ConfigurationResult
#   - from ..utils.validation import validate_schema
#   - from ..utils.file_watcher import FileWatcher

# External Systems: File system, environment variables
# Error Handling Strategy:
#   - File not found -> use defaults with warning
#   - Parse errors -> abort with detailed error message
#   - Validation errors -> abort with field-specific errors
#   - Permission errors -> fallback to environment variables only
# Recovery Mechanisms:
#   - Default configuration fallback
#   - Environment variable override
#   - Partial configuration loading
# State Requirements:
#   - File modification timestamps
#   - Configuration cache
#   - Hot reload watcher state
#   - Validation result cache
```

---

## 🎯 **QUALITY REQUIREMENTS FOR COMPLEX FUNCTIONS**

### **📝 Documentation Requirements**
- **Docstring**: Comprehensive multi-line with detailed descriptions
- **Parameter Documentation**: All parameters with types, defaults, and constraints
- **Return Documentation**: Complex return types fully explained
- **Exception Documentation**: All possible exceptions with conditions
- **Examples**: Multiple usage examples covering different scenarios
- **Implementation Notes**: Algorithm explanations, performance considerations

### **🔧 Implementation Requirements**
- **Error Handling**: Comprehensive exception handling with recovery
- **Logging**: Structured logging at appropriate levels
- **Performance**: Optimized for expected load and data volumes
- **Resource Management**: Proper cleanup of resources (files, connections)
- **Thread Safety**: Concurrent access considerations
- **Input Validation**: Thorough parameter validation

### **📊 Testing Requirements**
- **Unit Tests**: 95%+ coverage with comprehensive test cases
- **Integration Tests**: External system interaction testing
- **Error Testing**: All error paths and recovery mechanisms
- **Performance Tests**: Load and stress testing
- **Mock Strategy**: Comprehensive mocking of external dependencies

---

## 🚨 **ANALYSIS GATE CRITERIA**

**✅ GATE PASSED WHEN:**
- All 5 mandatory commands executed with evidence
- Function confirmed as "complex" complexity level
- Complete requirements documented for all responsibilities
- All checklist items verified
- Quality requirements understood
- Error handling strategy comprehensive
- State management requirements clear

**❌ GATE FAILED IF:**
- Function has single responsibility (consider simple path)
- No external dependencies (consider simple path)
- Minimal error handling needed (consider simple path)
- No state management required (consider simple path)
- Requirements incomplete or unclear

---

**💡 Key Principle**: Complex functions require thorough analysis of all responsibilities, dependencies, and failure modes to ensure robust, maintainable implementation.
