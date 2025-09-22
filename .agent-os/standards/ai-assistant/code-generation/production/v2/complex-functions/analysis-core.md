# Complex Functions - Analysis Core (v2)

## 🎯 **ANALYSIS PHASE FOR COMPLEX FUNCTIONS**

**Purpose**: Focused requirements analysis for complex functions with multiple responsibilities.

**Complexity Level**: Complex (error handling, external dependencies, state management)

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

### **Command 2: Determine Function Signature**
```bash
# AI MUST define complex signature with all parameter types
echo "Function signature: def function_name(param1: Type1, *, kwonly: Type3 = default) -> ReturnType:"
```

**Required Output:**
- Complete function name
- All positional parameters with types
- Keyword-only parameters identified
- Optional parameters with defaults
- Return type specification (Union/Optional)

### **Command 3: Map Dependencies & External Systems**
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

---

## 🔍 **ANALYSIS CHECKLIST**

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
```

---

## 🎯 **QUALITY REQUIREMENTS**

### **📝 Documentation Requirements**
- **Docstring**: Comprehensive multi-line with detailed descriptions
- **Parameter Documentation**: All parameters with types, defaults, and constraints
- **Return Documentation**: Complex return types fully explained
- **Exception Documentation**: All possible exceptions with conditions
- **Examples**: Multiple usage examples covering different scenarios

### **🔧 Implementation Requirements**
- **Error Handling**: Comprehensive exception handling with recovery
- **Logging**: Structured logging at appropriate levels
- **Performance**: Optimized for expected load and data volumes
- **Resource Management**: Proper cleanup of resources
- **Thread Safety**: Concurrent access considerations
- **Input Validation**: Thorough parameter validation

---

## 🚨 **ANALYSIS GATE CRITERIA**

**✅ GATE PASSED WHEN:**
- All 4 mandatory commands executed with evidence
- Function confirmed as "complex" complexity level
- Complete requirements documented for all responsibilities
- All checklist items verified
- Quality requirements understood
- Error handling strategy comprehensive

**❌ GATE FAILED IF:**
- Function has single responsibility (consider simple path)
- No external dependencies (consider simple path)
- Minimal error handling needed (consider simple path)
- Requirements incomplete or unclear

---

**💡 Key Principle**: Complex function analysis requires thorough examination of all responsibilities, dependencies, and failure modes to ensure robust implementation.
