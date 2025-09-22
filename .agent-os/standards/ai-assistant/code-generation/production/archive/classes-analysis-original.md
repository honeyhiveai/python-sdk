# Classes - Analysis Phase

## 🎯 **PHASE 2: REQUIREMENTS ANALYSIS FOR CLASSES**

**Purpose**: Gather complete requirements for class generation including data models, service classes, and configuration classes.

**Complexity Level**: Class-based (data modeling, state management, method organization, inheritance hierarchies)

---

## 📋 **MANDATORY ANALYSIS COMMANDS**

### **Command 1: Define Class Purpose & Type**
```bash
# AI MUST identify class type and primary purpose
echo "Class type: [DATA_MODEL|SERVICE_CLASS|CONFIGURATION|MANAGER|FACTORY|BUILDER]"
echo "Primary purpose: [DETAILED PURPOSE DESCRIPTION]"
```

**Required Output:**
- Specific class type identification
- Primary purpose and responsibility
- Use case scenarios
- Integration context within system

### **Command 2: Analyze Data Structure & Attributes**
```bash
# AI MUST define all class attributes and their types
echo "Class attributes: [ATTRIBUTE_NAME: TYPE, VALIDATION_RULES, DEFAULT_VALUE]"
echo "Computed properties: [PROPERTY_NAME: COMPUTATION_LOGIC]"
```

**Required Output:**
- All instance attributes with types
- Class attributes/constants
- Computed properties and their logic
- Attribute validation requirements
- Default values and initialization

### **Command 3: Define Method Interface & Behavior**
```bash
# AI MUST specify all methods and their signatures
echo "Public methods: [METHOD_NAME(params) -> return_type: PURPOSE]"
echo "Private methods: [_METHOD_NAME(params) -> return_type: PURPOSE]"
```

**Required Output:**
- All public method signatures
- Private/protected helper methods
- Static methods and class methods
- Method responsibilities and interactions
- Parameter validation requirements

### **Command 4: Map Inheritance & Composition Relationships**
```bash
# AI MUST define class relationships and dependencies
echo "Inheritance: [BASE_CLASS] -> [DERIVED_CLASS]"
echo "Composition: [COMPOSED_CLASS contains COMPONENT_CLASS]"
echo "Dependencies: [EXTERNAL_CLASSES, PROTOCOLS, INTERFACES]"
```

**Required Output:**
- Inheritance hierarchy design
- Composition relationships
- External dependencies
- Protocol/interface implementations
- Mixin usage patterns

### **Command 5: Plan Validation & Serialization Strategy**
```bash
# AI MUST define validation and serialization requirements
echo "Validation strategy: [FIELD_VALIDATION, CROSS_FIELD_VALIDATION, BUSINESS_RULES]"
echo "Serialization needs: [JSON, DICT, DATABASE, API_RESPONSE]"
```

**Required Output:**
- Field-level validation rules
- Cross-field validation logic
- Business rule validation
- Serialization/deserialization requirements
- Data transformation needs

---

## 🔍 **CLASS ANALYSIS CHECKLIST**

### **✅ Class Purpose Analysis**
- [ ] **Class type identified** - Specific class category determined
- [ ] **Primary purpose clear** - Main responsibility well-defined
- [ ] **Use cases documented** - All usage scenarios identified
- [ ] **System integration** - Role within larger system understood

### **✅ Data Structure Analysis**
- [ ] **Attributes cataloged** - All instance and class attributes identified
- [ ] **Type annotations** - Complete type information for all attributes
- [ ] **Validation rules** - Field validation requirements specified
- [ ] **Default values** - Initialization strategy defined
- [ ] **Computed properties** - Derived attributes identified

### **✅ Method Interface Analysis**
- [ ] **Public API defined** - All public methods with signatures
- [ ] **Private methods** - Helper methods identified
- [ ] **Method responsibilities** - Each method's purpose clear
- [ ] **Parameter validation** - Input validation requirements
- [ ] **Return types** - Output specifications complete

### **✅ Relationship Analysis**
- [ ] **Inheritance design** - Base class relationships defined
- [ ] **Composition structure** - Component relationships mapped
- [ ] **Dependency mapping** - External dependencies identified
- [ ] **Protocol compliance** - Interface implementations planned
- [ ] **Mixin integration** - Shared behavior patterns identified

### **✅ Validation & Serialization Analysis**
- [ ] **Field validation** - Individual field rules defined
- [ ] **Cross-field validation** - Inter-field dependencies identified
- [ ] **Business rules** - Domain-specific validation logic
- [ ] **Serialization formats** - Required output formats specified
- [ ] **Data transformation** - Conversion requirements mapped

---

## 📊 **ANALYSIS EXAMPLES**

### **Example 1: Pydantic Data Model**
```python
# Class Type: DATA_MODEL (Pydantic BaseModel)
# Primary Purpose: Represent API request/response data with validation
# Use Cases: API serialization, data validation, configuration parsing

# Class Attributes:
#   - id: Optional[str] = None (UUID validation)
#   - name: str (min_length=1, max_length=100)
#   - email: EmailStr (email format validation)
#   - age: int (ge=0, le=150)
#   - created_at: datetime = Field(default_factory=datetime.utcnow)
#   - tags: List[str] = Field(default_factory=list)
#   - metadata: Dict[str, Any] = Field(default_factory=dict)

# Computed Properties:
#   - display_name: str (formatted name with title case)
#   - is_adult: bool (age >= 18)
#   - age_group: str (child/teen/adult/senior based on age)

# Public Methods:
#   - to_dict() -> Dict[str, Any]: Convert to dictionary
#   - from_dict(data: Dict[str, Any]) -> 'UserModel': Create from dictionary
#   - validate_business_rules() -> None: Apply business validation
#   - update_metadata(key: str, value: Any) -> None: Update metadata

# Validation Strategy:
#   - Field validation: Pydantic validators for each field
#   - Cross-field validation: Email domain restrictions based on age
#   - Business rules: Name cannot contain email address

# Serialization Needs:
#   - JSON: For API responses
#   - Dict: For database storage
#   - API response: Exclude internal fields
```

### **Example 2: Service Class**
```python
# Class Type: SERVICE_CLASS
# Primary Purpose: Handle API communication with external service
# Use Cases: HTTP requests, authentication, response processing, error handling

# Class Attributes:
#   - base_url: str (API endpoint base URL)
#   - api_key: str (authentication key)
#   - timeout: float = 30.0 (request timeout)
#   - max_retries: int = 3 (retry attempts)
#   - session: Optional[httpx.AsyncClient] = None (HTTP session)
#   - circuit_breaker: CircuitBreaker (failure protection)

# Computed Properties:
#   - is_authenticated: bool (check if API key is valid)
#   - health_status: str (service health check result)
#   - request_count: int (total requests made)

# Public Methods:
#   - async authenticate() -> bool: Authenticate with service
#   - async get(endpoint: str, **kwargs) -> Dict[str, Any]: GET request
#   - async post(endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]: POST request
#   - async health_check() -> bool: Check service availability
#   - close() -> None: Cleanup resources

# Private Methods:
#   - _prepare_headers() -> Dict[str, str]: Prepare request headers
#   - _handle_response(response: httpx.Response) -> Dict[str, Any]: Process response
#   - _should_retry(exception: Exception) -> bool: Determine retry logic

# Inheritance: BaseAPIClient -> SpecificServiceClient
# Composition: Contains CircuitBreaker, RateLimiter, MetricsCollector
# Dependencies: httpx, logging, typing, custom error classes

# Validation Strategy:
#   - URL validation: Ensure valid base_url format
#   - API key validation: Check key format and permissions
#   - Parameter validation: Validate request parameters

# Serialization Needs:
#   - JSON: Request/response serialization
#   - Configuration: Service settings persistence
```

### **Example 3: Configuration Manager Class**
```python
# Class Type: CONFIGURATION (Singleton pattern)
# Primary Purpose: Manage application configuration with validation and hot reload
# Use Cases: Settings management, environment configuration, feature flags

# Class Attributes:
#   - _instance: Optional['ConfigManager'] = None (singleton instance)
#   - config_path: Path (configuration file path)
#   - environment: str = "production" (deployment environment)
#   - _config_data: Dict[str, Any] (loaded configuration)
#   - _file_watcher: Optional[FileWatcher] = None (hot reload support)
#   - _validation_schema: Dict[str, Any] (configuration schema)

# Computed Properties:
#   - database_url: str (constructed from config components)
#   - debug_mode: bool (derived from environment and debug flag)
#   - feature_flags: Dict[str, bool] (enabled features)
#   - api_settings: APISettings (typed configuration subset)

# Public Methods:
#   - get(key: str, default: Any = None) -> Any: Get configuration value
#   - set(key: str, value: Any) -> None: Set configuration value
#   - reload() -> None: Reload configuration from file
#   - validate() -> List[str]: Validate configuration
#   - enable_hot_reload() -> None: Enable file watching
#   - disable_hot_reload() -> None: Disable file watching

# Private Methods:
#   - _load_config() -> Dict[str, Any]: Load from file
#   - _merge_environment_vars() -> None: Override with env vars
#   - _validate_schema() -> List[str]: Schema validation
#   - _on_file_changed(path: Path) -> None: File change handler

# Inheritance: BaseConfig -> ConfigManager
# Composition: Contains FileWatcher, SchemaValidator
# Dependencies: pathlib, os, yaml, json, watchdog

# Validation Strategy:
#   - Schema validation: JSON schema for structure
#   - Type validation: Ensure correct data types
#   - Business rules: Environment-specific constraints
#   - Cross-field validation: Dependent configuration values

# Serialization Needs:
#   - YAML: Configuration file format
#   - JSON: API configuration export
#   - Environment variables: System integration
```

### **Example 4: Factory Class**
```python
# Class Type: FACTORY
# Primary Purpose: Create instances of related classes based on configuration
# Use Cases: Object creation, dependency injection, plugin system

# Class Attributes:
#   - _registry: Dict[str, Type] = {} (registered class types)
#   - _default_config: Dict[str, Any] (default configuration)
#   - _instances: Dict[str, Any] = {} (cached instances)

# Computed Properties:
#   - available_types: List[str] (registered type names)
#   - instance_count: int (number of cached instances)

# Public Methods:
#   - register(name: str, cls: Type, config: Dict[str, Any]) -> None: Register class
#   - create(name: str, **kwargs) -> Any: Create instance
#   - get_or_create(name: str, **kwargs) -> Any: Get cached or create new
#   - clear_cache() -> None: Clear instance cache

# Private Methods:
#   - _validate_registration(cls: Type) -> None: Validate class for registration
#   - _merge_config(base: Dict, override: Dict) -> Dict: Merge configurations
#   - _create_instance(cls: Type, config: Dict) -> Any: Instance creation logic

# Inheritance: BaseFactory -> SpecificFactory
# Dependencies: typing, abc, logging

# Validation Strategy:
#   - Class validation: Ensure registered classes meet interface
#   - Configuration validation: Validate creation parameters
#   - Instance validation: Verify created instances

# Serialization Needs:
#   - Configuration: Factory settings persistence
#   - Registry: Registered types metadata
```

---

## 🎯 **QUALITY REQUIREMENTS FOR CLASSES**

### **📝 Documentation Requirements**
- **Class Docstring**: Comprehensive description with purpose, usage, and examples
- **Attribute Documentation**: All attributes with types, validation, and defaults
- **Method Documentation**: Complete method documentation with parameters and returns
- **Usage Examples**: Multiple examples showing different use cases
- **Design Notes**: Architecture decisions, patterns used, and trade-offs

### **🔧 Implementation Requirements**
- **Type Safety**: 100% type annotation coverage for all attributes and methods
- **Validation**: Comprehensive input validation with clear error messages
- **Error Handling**: Robust exception handling with custom exception types
- **Resource Management**: Proper initialization and cleanup of resources
- **Thread Safety**: Concurrent access considerations where applicable
- **Performance**: Optimized for expected usage patterns

### **📊 Testing Requirements**
- **Unit Tests**: 95%+ coverage with comprehensive test cases
- **Integration Tests**: Class interaction testing with dependencies
- **Validation Testing**: All validation rules and error conditions
- **Serialization Testing**: All serialization/deserialization scenarios
- **Performance Testing**: Memory usage and execution time validation
- **Mock Strategy**: Comprehensive mocking of external dependencies

### **🏗️ Design Requirements**
- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed Principle**: Open for extension, closed for modification
- **Liskov Substitution**: Derived classes properly substitute base classes
- **Interface Segregation**: Focused interfaces without unnecessary methods
- **Dependency Inversion**: Depend on abstractions, not concretions

---

## 🚨 **ANALYSIS GATE CRITERIA**

**✅ GATE PASSED WHEN:**
- All 5 mandatory commands executed with evidence
- Class type and purpose clearly identified
- Complete attribute and method analysis
- Inheritance and composition relationships defined
- Validation and serialization strategy planned
- All checklist items verified
- Quality requirements understood
- Design principles considered

**❌ GATE FAILED IF:**
- Class purpose unclear or too broad (consider splitting)
- Insufficient attribute or method analysis
- Missing relationship analysis
- Validation strategy incomplete
- Serialization requirements unclear
- Design principles violated

---

**💡 Key Principle**: Class analysis requires comprehensive understanding of data structure, behavior, relationships, and integration patterns to ensure robust, maintainable object-oriented design.
