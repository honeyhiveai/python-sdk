# Production Code - Complexity Assessment

## 🎯 **COMPLEXITY DECISION LOGIC**

**Purpose**: Determine the appropriate generation path based on code complexity and requirements.

**Decision Criteria**: Function purpose, dependencies, error handling, and architectural patterns.

---

## 🔀 **COMPLEXITY LEVELS**

### **📝 SIMPLE FUNCTIONS** 
**Characteristics:**
- Single, focused purpose
- Minimal external dependencies (0-2 imports)
- Basic parameter validation
- Simple return types (`str`, `bool`, `int`, `Optional[T]`)
- No complex error handling required

**Examples:**
- Utility functions (formatters, validators)
- Simple data transformations
- Basic string/number operations
- Configuration getters

**Template Path:** `simple-functions/`

---

### **🔧 COMPLEX FUNCTIONS**
**Characteristics:**
- Multiple responsibilities or complex logic
- Multiple external dependencies (3+ imports)
- Comprehensive error handling required
- Complex return types (`Dict`, `Tuple`, `Union`, custom types)
- Integration with external services/APIs
- Logging and monitoring integration

**Examples:**
- API request handlers
- Business logic processors
- Data pipeline functions
- Integration functions with HoneyHive tracer

**Template Path:** `complex-functions/`

---

### **🏗️ CLASS-BASED CODE**
**Characteristics:**
- Data modeling requirements
- State management needed
- Multiple related methods
- Configuration or service patterns
- Inheritance or composition patterns

**Examples:**
- Pydantic models
- Service classes
- Configuration classes
- Manager/Handler classes
- Custom exception classes

**Template Path:** `classes/`

---

## 🎯 **DECISION MATRIX**

| Criteria | Simple | Complex | Class |
|----------|--------|---------|-------|
| **Dependencies** | 0-2 imports | 3+ imports | Varies |
| **Error Handling** | Basic validation | Comprehensive | Varies |
| **Return Types** | Simple types | Complex types | Class instances |
| **External Integration** | None/minimal | Required | Varies |
| **State Management** | Stateless | Stateless | Stateful |
| **Responsibilities** | Single | Multiple | Multiple related |

---

## 🔍 **ASSESSMENT PROCESS**

### **Step 1: Analyze Requirements**
**Ask these questions:**
1. What is the primary purpose of this code?
2. How many external dependencies are needed?
3. What level of error handling is required?
4. What type of data does it work with?
5. Does it need to maintain state?

### **Step 2: Apply Decision Criteria**
**Use this logic:**

```python
def assess_complexity(requirements: Dict[str, Any]) -> str:
    """Assess code complexity level.
    
    Args:
        requirements: Dictionary of code requirements
        
    Returns:
        Complexity level: 'simple', 'complex', or 'class'
    """
    # Class-based indicators (highest priority)
    if (requirements.get('needs_state_management') or 
        requirements.get('data_modeling') or
        requirements.get('multiple_related_methods')):
        return 'class'
    
    # Complex function indicators
    if (requirements.get('dependencies', 0) >= 3 or
        requirements.get('comprehensive_error_handling') or
        requirements.get('external_integration') or
        requirements.get('complex_return_types')):
        return 'complex'
    
    # Default to simple
    return 'simple'
```

### **Step 3: Validate Decision**
**Verify your choice:**
- Does the selected path match the requirements?
- Are there any edge cases that change the complexity?
- Will the chosen template provide adequate structure?

---

## 📋 **ASSESSMENT EXAMPLES**

### **Example 1: String Validator**
```python
# Requirements:
# - Validate email format
# - Return boolean
# - No external dependencies
# - Basic validation only

# Assessment: SIMPLE
# Reasoning: Single purpose, no dependencies, simple return type
```

### **Example 2: API Event Creator**
```python
# Requirements:
# - Create HoneyHive events
# - Handle API errors
# - Integrate with tracer
# - Return complex response data
# - Logging integration

# Assessment: COMPLEX  
# Reasoning: Multiple dependencies, error handling, external integration
```

### **Example 3: Configuration Model**
```python
# Requirements:
# - Store configuration data
# - Validate configuration values
# - Provide default values
# - Support serialization

# Assessment: CLASS
# Reasoning: Data modeling, state management, multiple related methods
```

---

## 🎯 **QUALITY REQUIREMENTS BY COMPLEXITY**

### **📝 Simple Functions**
- **Pylint**: 10.0/10 (no exceptions)
- **MyPy**: 0 errors
- **Docstring**: Basic with parameters and return
- **Type Annotations**: 100% coverage
- **Testing**: Unit tests with 90%+ coverage

### **🔧 Complex Functions**
- **Pylint**: 10.0/10 (justified disables only)
- **MyPy**: 0 errors
- **Docstring**: Comprehensive with examples
- **Type Annotations**: 100% coverage
- **Error Handling**: Comprehensive with logging
- **Testing**: Unit + integration tests

### **🏗️ Class-Based Code**
- **Pylint**: 10.0/10 (justified disables only)
- **MyPy**: 0 errors
- **Docstring**: Class and method documentation
- **Type Annotations**: 100% coverage
- **Design Patterns**: Appropriate patterns used
- **Testing**: Comprehensive test coverage

---

**💡 Key Principle**: Accurate complexity assessment ensures the right template and quality standards are applied, preventing over-engineering simple code or under-engineering complex requirements.
