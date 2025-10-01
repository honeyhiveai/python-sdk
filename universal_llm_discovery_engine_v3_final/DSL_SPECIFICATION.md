# Universal LLM Discovery Engine - DSL Specification

**Version**: 3.0 Final  
**Date**: 2025-01-27  
**Status**: Implementation Ready  
**Purpose**: Complete formal DSL specification for implementation

---

## 📋 **DSL Overview**

The Universal DSL consists of **five distinct specification types**, each with defined syntax, semantics, and validation rules. All DSL types are designed for O(1) compilation and runtime performance.

### **Five DSL Types (Aligned with Architecture Foundation)**

1. **Instrumentor Mapping DSL** - Maps installed instrumentors to semantic convention versions (using package detection)
2. **Source Convention DSL** - Extracts data from semantic convention attributes at the top level
3. **Structure Discovery DSL** - Dynamically analyzes raw LLM provider response objects nested within semantic attributes
4. **Target Schema DSL** - Defines HoneyHive schema structure and mapping rules
5. **Transform Rules DSL** - Defines transformation functions and data type conversions

## 🎯 **DSL Development Strategy**

The Universal LLM Discovery Engine uses **package-based instrumentor detection** for runtime operation. The **Agent OS Compatibility Matrix** serves as a development aid to help build accurate DSL configurations by providing version mapping data, but is not part of the production system.

## 🏗️ **DSL Type 1: Instrumentor Mapping DSL**

### **Purpose**
Maps installed instrumentor packages to their corresponding semantic convention versions using Python package detection. The version mappings in this DSL are built using data from the Agent OS compatibility matrix during development, but the runtime system uses standard Python package inspection.

### **File Location**
`config/dsl/instrumentor_mappings.yaml`

### **Schema Specification**

```yaml
# Required root structure
version: string                           # Semantic version (e.g., "1.0")
dsl_type: "instrumentor_mapping"          # Fixed identifier
description: string                       # Human-readable description

# Core specification sections
instrumentor_semantic_conventions:        # Required section
  "{package_name}":                      # Instrumentor package name
    semantic_convention: string           # Required: Convention name ("openinference", "traceloop", "openlit")
    version_detection: string             # Required: Detection method ("package_version")
    
    # Version mapping rules
    version_mapping:                      # Required: Map instrumentor versions to convention versions
      "{version_range}": string          # Version range → convention version
      
    supported_versions: [string]         # Required: List of supported convention versions
    fallback_version: string             # Required: Default version if detection fails
    
    # Optional metadata
    notes: string                        # Optional: Additional information
    deprecated_after: string             # Optional: ISO date when support ends

# Development metadata (not used at runtime)
development_metadata:                    # Optional: Development information
  built_from_compatibility_matrix: string # Source of version mapping data
  last_updated: string                   # ISO date of last update

# Performance optimization
performance_hints:                      # Required: Performance optimization
  cache_duration: integer               # How long to cache version detection results
  lazy_loading: boolean                 # Whether to detect versions on-demand
```

### **Example Instrumentor Mapping DSL**

```yaml
version: "1.0"
dsl_type: "instrumentor_mapping"
description: "Maps instrumentor packages to semantic convention versions via Agent OS compatibility matrix"

instrumentor_semantic_conventions:
  # OpenInference instrumentors
  "openinference-instrumentation-openai":
    semantic_convention: "openinference"
    version_detection: "package_version"
    
    version_mapping:
      ">=1.0.0,<2.0.0": "0.1.15"        # OpenInference instrumentor v1.x → convention v0.1.15
      ">=2.0.0,<3.0.0": "0.2.0"         # OpenInference instrumentor v2.x → convention v0.2.0
    
    supported_versions: ["0.1.15", "0.2.0"]
    fallback_version: "0.1.15"
    notes: "Primary OpenAI integration via OpenInference"
    
  "openinference-instrumentation-anthropic":
    semantic_convention: "openinference"
    version_detection: "package_version"
    
    version_mapping:
      ">=1.0.0,<2.0.0": "0.1.15"
      ">=2.0.0,<3.0.0": "0.2.0"
    
    supported_versions: ["0.1.15", "0.2.0"]
    fallback_version: "0.1.15"
    
  # Traceloop instrumentors
  "opentelemetry-instrumentation-openai":
    semantic_convention: "traceloop"
    version_detection: "package_version"
    
    version_mapping:
      ">=1.20.0,<1.25.0": "0.46.2"      # Traceloop instrumentor v1.20-1.24 → convention v0.46.2
      ">=1.25.0,<2.0.0": "0.47.0"       # Traceloop instrumentor v1.25+ → convention v0.47.0
    
    supported_versions: ["0.46.2", "0.47.0"]
    fallback_version: "0.46.2"
    notes: "Alternative OpenAI integration via Traceloop"

development_metadata:
  built_from_compatibility_matrix: "tests/compatibility_matrix/generate_version_matrix.py"
  last_updated: "2025-01-27"

performance_hints:
  cache_duration: 300  # 5 minutes
  lazy_loading: true
```

## 🏗️ **DSL Type 2: Source Convention DSL**

### **Purpose**
Define how to extract semantic data FROM existing observability framework conventions at the top level of span data.

### **File Location**
`config/dsl/source_conventions/{convention_name}_v{major}_{minor}.yaml`

### **Schema Specification**

```yaml
# Required root structure
version: string                    # Semantic version (e.g., "0.1.15")
dsl_type: "source_convention"      # Fixed identifier
convention_name: string            # Convention identifier (e.g., "openinference")
description: string                # Human-readable description

# Core specification sections
recognition_patterns:              # Required section
  primary_indicators:             # Strong indicators this convention is present
    - attribute_prefix: string     # Required: Attribute name prefix (e.g., "llm.")
      required_attributes: [string] # Required: Must-have attributes
      confidence_weight: float     # Required: 0.0-1.0
      
  version_detection:              # Optional: Version-specific detection
    definitive_indicators:        # Fields that definitively indicate version
      - attribute_presence: [string]
        confidence_boost: float
    exclusion_indicators:         # Fields that exclude this version
      - attribute_presence: [string]
        confidence_penalty: float

extraction_rules:                 # Required section
  {semantic_type}:               # Semantic type (model_info, conversation_messages, etc.)
    {field_name}:                # Field identifier
      source_attribute: string    # Required: Source attribute path
      semantic_type: string       # Required: Semantic classification
      data_type: string          # Required: Expected data type
      required: boolean          # Required: Whether field is mandatory
      fallback_attributes: [string] # Optional: Alternative source attributes
      validation_rules: object   # Optional: Validation constraints

# Performance optimization
performance_optimization:         # Required section
  hash_lookups:                  # Pre-compiled hash structures
    attribute_prefixes: frozenset # O(1) prefix matching
    required_attributes: frozenset # O(1) attribute checking
  native_operations:             # Native Python string operations only
    allowed_operations: [string] # startswith, in, get, len
    forbidden_operations: [string] # regex, complex parsing
```

### **Example Source Convention DSL**

```yaml
version: "0.1.15"
dsl_type: "source_convention"
convention_name: "openinference"
description: "Extract semantic data from OpenInference conventions"

recognition_patterns:
  primary_indicators:
    - attribute_prefix: "llm."
      required_attributes: ["llm.model_name"]
      confidence_weight: 0.9
      
  version_detection:
    definitive_indicators:
      - attribute_presence: ["llm.conversation_id"]  # New in v0.2.0
        confidence_boost: 0.3
    exclusion_indicators:
      - attribute_presence: ["llm.legacy_field"]     # Removed in v0.2.0
        confidence_penalty: -0.5

extraction_rules:
  model_information:
    model_name:
      source_attribute: "llm.model_name"
      semantic_type: "model_identifier"
      data_type: "string"
      required: true
      validation_rules:
        min_length: 1
        max_length: 200
    
    invocation_parameters:
      source_attribute: "llm.invocation_parameters"
      semantic_type: "model_config"
      data_type: "object"
      required: false
      fallback_attributes: ["llm.request.parameters"]

  conversation_messages:
    input_messages:
      source_attribute: "llm.input_messages"
      semantic_type: "input_messages"
      data_type: "array"
      required: false
      validation_rules:
        min_items: 0
        max_items: 1000
    
    output_messages:
      source_attribute: "llm.output_messages"
      semantic_type: "output_messages"
      data_type: "array"
      required: false

  usage_metrics:
    prompt_tokens:
      source_attribute: "llm.token_count_prompt"
      semantic_type: "token_usage"
      data_type: "integer"
      required: false
      validation_rules:
        min_value: 0
        max_value: 1000000
    
    completion_tokens:
      source_attribute: "llm.token_count_completion"
      semantic_type: "token_usage"
      data_type: "integer"
      required: false
      validation_rules:
        min_value: 0
        max_value: 1000000

performance_optimization:
  hash_lookups:
    attribute_prefixes: ["llm."]
    required_attributes: ["llm.model_name"]
  native_operations:
    allowed_operations: ["startswith", "in", "get", "len"]
    forbidden_operations: ["regex", "split", "replace"]
```

## 🏗️ **DSL Type 3: Structure Discovery DSL**

### **Purpose**
Dynamically analyze raw LLM provider response objects to understand their structure and extract meaningful data. This is a **separate, essential component** that handles the complexity of diverse LLM API response formats nested within semantic convention attributes.

### **File Location**
`config/dsl/structure_discovery.yaml`

### **Schema Specification**

```yaml
# Required root structure
version: string                    # Semantic version (e.g., "1.0")
dsl_type: "structure_discovery"    # Fixed identifier
description: string                # Human-readable description

# Core specification sections
structure_patterns:               # Required section
  pattern_{id}:                  # Pattern identifier (pattern_001, pattern_002, etc.)
    signature_fields: [string]    # Required: Array of field paths that identify this pattern
    optional_fields: [string]     # Optional: Array of field paths that may be present
    confidence_weight: float      # Required: 0.0-1.0, minimum confidence for pattern match
    pattern_name: string          # Optional: Human-readable name for debugging
    
navigation_rules:                # Required section
  {semantic_field_type}:         # Semantic field type (message_content, token_usage, etc.)
    rule_{id}:                   # Rule identifier (rule_001, rule_002, etc.)
      path_expression: string     # Required: JSONPath-like expression with wildcards
      pattern_match: string       # Required: References pattern_{id} from structure_patterns
      confidence: float           # Required: 0.0-1.0, confidence in this extraction rule
      fallback_paths: [string]    # Optional: Alternative paths if primary fails
      
field_classification:            # Required section
  {field_type}:                  # Field type identifier (message_content, token_usage, etc.)
    path_indicators: [string]     # Required: Path patterns that indicate this field type
    content_validators: [object]  # Required: Validation rules for field content
    context_clues: [string]       # Optional: Adjacent fields that provide context
    confidence_modifiers: object # Optional: Factors that adjust confidence scores

# Performance optimization
performance_optimization:         # Required section
  hash_based_matching:           # O(1) pattern matching
    signature_field_sets: frozenset # Pre-compiled signature field combinations
    path_expression_cache: dict  # Pre-compiled path expressions
  native_string_processing:      # Native Python operations only
    allowed_operations: [string] # startswith, in, get, len, isinstance
    forbidden_operations: [string] # regex, complex parsing, loops
```

### **Example Structure Discovery DSL**

```yaml
version: "1.0"
dsl_type: "structure_discovery"
description: "Generic LLM provider response structure discovery patterns"

structure_patterns:
  pattern_001:
    signature_fields: ["choices", "usage.prompt_tokens", "model"]
    optional_fields: ["id", "created", "system_fingerprint"]
    confidence_weight: 0.95
    pattern_name: "openai_chat_completion"
    
  pattern_002:
    signature_fields: ["content", "usage.input_tokens", "stop_reason"]
    optional_fields: ["id", "type", "role"]
    confidence_weight: 0.90
    pattern_name: "anthropic_message"
    
  pattern_003:
    signature_fields: ["candidates", "usageMetadata.promptTokenCount"]
    optional_fields: ["safetyRatings", "modelVersion"]
    confidence_weight: 0.85
    pattern_name: "gemini_response"

navigation_rules:
  message_content:
    rule_001:
      path_expression: "choices.*.message.content"
      pattern_match: "pattern_001"
      confidence: 0.95
      fallback_paths: ["choices.0.message.content"]
      
    rule_002:
      path_expression: "content.*.text"
      pattern_match: "pattern_002"
      confidence: 0.90
      fallback_paths: ["content.0.text"]
      
    rule_003:
      path_expression: "candidates.*.content.parts.*.text"
      pattern_match: "pattern_003"
      confidence: 0.85
      fallback_paths: ["candidates.0.content.parts.0.text"]

  token_usage:
    rule_001:
      path_expression: "usage.prompt_tokens"
      pattern_match: "pattern_001"
      confidence: 0.95
      
    rule_002:
      path_expression: "usage.input_tokens"
      pattern_match: "pattern_002"
      confidence: 0.90

field_classification:
  message_content:
    path_indicators: ["message.content", "content.text", "parts.text"]
    content_validators:
      - type: "string"
        min_length: 1
        max_length: 100000
    context_clues: ["role", "assistant", "user"]
    
  token_usage:
    path_indicators: ["usage", "tokens", "token_count"]
    content_validators:
      - type: "integer"
        min_value: 0
        max_value: 1000000
    context_clues: ["prompt_tokens", "completion_tokens"]

performance_optimization:
  hash_based_matching:
    signature_field_sets: [["choices", "usage.prompt_tokens", "model"], ["content", "usage.input_tokens", "stop_reason"]]
    path_expression_cache: {}
  native_string_processing:
    allowed_operations: ["startswith", "in", "get", "len", "isinstance"]
    forbidden_operations: ["regex", "split", "replace", "search"]
```

## 🏗️ **DSL Type 4: Target Schema DSL**

### **Purpose**
Define target schema structures and mapping rules for output formats (HoneyHive schema).

### **File Location**
`config/dsl/target_schemas/honeyhive.yaml`

### **Schema Specification**

```yaml
# Required root structure
version: string                    # Semantic version (e.g., "1.0")
dsl_type: "target_schema"          # Fixed identifier
schema_name: string                # Schema identifier (e.g., "honeyhive")
description: string                # Human-readable description

# Core specification sections
schema_structure:                  # Required section
  {section_name}:                 # Schema section (inputs, outputs, config, metadata)
    {field_name}:                 # Field identifier
      data_type: string           # Required: Expected data type
      required: boolean           # Required: Whether field is mandatory
      validation_rules: object    # Optional: Validation constraints
      description: string         # Optional: Field description

mapping_rules:                    # Required section
  {section_name}:                 # Schema section
    {field_name}:                 # Field identifier
      source_semantic_type: string # Required: Source semantic type to map from
      transformation: string      # Optional: Transform function to apply
      fallback_value: any         # Optional: Default value if source missing
      conditions: object          # Optional: Conditional mapping rules

# Performance optimization
performance_optimization:         # Required section
  schema_validation_cache: dict   # Pre-compiled validation rules
  mapping_lookup_tables: dict     # O(1) mapping lookups
```

### **Example Target Schema DSL**

```yaml
version: "1.0"
dsl_type: "target_schema"
schema_name: "honeyhive"
description: "HoneyHive unified schema mapping"

schema_structure:
  inputs:
    chat_history:
      data_type: "message_array"
      required: false
      validation_rules:
        max_items: 1000
        item_schema:
          role: "string"
          content: "string"
      description: "Conversation history messages"
      
    system_prompt:
      data_type: "string"
      required: false
      validation_rules:
        max_length: 10000
      description: "System prompt or instructions"

  outputs:
    content:
      data_type: "string"
      required: true
      validation_rules:
        min_length: 1
        max_length: 100000
      description: "Assistant response content"
      
    tool_calls:
      data_type: "tool_call_array"
      required: false
      validation_rules:
        max_items: 100
      description: "Tool/function calls made by assistant"
      
    finish_reason:
      data_type: "string"
      required: false
      validation_rules:
        allowed_values: ["stop", "length", "tool_calls", "content_filter"]
      description: "Reason for completion finish"

  config:
    model:
      data_type: "string"
      required: true
      validation_rules:
        min_length: 1
        max_length: 200
      description: "Model identifier"
      
    parameters:
      data_type: "object"
      required: false
      description: "Model parameters and settings"

  metadata:
    usage:
      data_type: "usage_object"
      required: false
      validation_rules:
        required_fields: ["prompt_tokens", "completion_tokens"]
      description: "Token usage metrics"
      
    processing_info:
      data_type: "processing_metrics"
      required: false
      description: "Processing performance metrics"

mapping_rules:
  inputs:
    chat_history:
      source_semantic_type: "input_messages"
      transformation: "normalize_message_array"
      fallback_value: []
      
    system_prompt:
      source_semantic_type: "system_message"
      transformation: "extract_text_content"
      fallback_value: null

  outputs:
    content:
      source_semantic_type: "assistant_message"
      transformation: "extract_text_content"
      conditions:
        required_if: "outputs_present"
      
    tool_calls:
      source_semantic_type: "tool_calls"
      transformation: "normalize_tool_calls"
      fallback_value: []

  config:
    model:
      source_semantic_type: "model_identifier"
      transformation: "normalize_model_name"
      conditions:
        required: true

  metadata:
    usage:
      source_semantic_type: "token_usage"
      transformation: "aggregate_usage_metrics"
      fallback_value: {}

performance_optimization:
  schema_validation_cache: {}
  mapping_lookup_tables: {}
```

## 🏗️ **DSL Type 5: Transform Rules DSL**

### **Purpose**
Define transformation functions and logic for converting between data formats with O(1) performance guarantees.

### **File Location**
`config/dsl/transforms/transform_rules.yaml`

### **Schema Specification**

```yaml
# Required root structure
version: string                    # Semantic version (e.g., "1.0")
dsl_type: "transform_rules"        # Fixed identifier
description: string                # Human-readable description

# Core specification sections
transform_functions:               # Required section
  {function_name}:                # Function identifier
    input_type: string            # Required: Expected input data type
    output_type: string           # Required: Expected output data type
    description: string           # Required: Function description
    implementation_type: string   # Required: "native_python" or "lambda"
    implementation: string        # Required: Function implementation
    performance_class: string     # Required: "O(1)", "O(log n)", etc.
    validation_rules: object      # Optional: Input/output validation

data_type_conversions:            # Required section
  {conversion_name}:              # Conversion identifier
    from_type: string             # Required: Source data type
    to_type: string               # Required: Target data type
    conversion_function: string   # Required: Function to use
    validation_required: boolean  # Required: Whether to validate conversion
    error_handling: string        # Required: Error handling strategy

# Performance guarantees
performance_guarantees:           # Required section
  max_execution_time_ms: integer  # Maximum execution time per function
  memory_limit_mb: integer        # Maximum memory usage per function
  forbidden_operations: [string] # Operations that violate O(1) requirement
```

### **Example Transform Rules DSL**

```yaml
version: "1.0"
dsl_type: "transform_rules"
description: "Transform functions for Universal LLM Discovery Engine"

transform_functions:
  normalize_model_name:
    input_type: "string"
    output_type: "string"
    description: "Normalize model names to standard format"
    implementation_type: "native_python"
    implementation: |
      def normalize_model_name(value):
          if not isinstance(value, str):
              return str(value).lower().strip()
          
          model = value.lower().strip()
          
          # Remove common prefixes using startswith (O(1))
          if model.startswith(("openai/", "anthropic/", "google/")):
              model = model.split("/", 1)[1]
          
          return model
    performance_class: "O(1)"
    validation_rules:
      max_input_length: 200
      
  extract_text_content:
    input_type: "any"
    output_type: "string"
    description: "Extract text content from various message formats"
    implementation_type: "native_python"
    implementation: |
      def extract_text_content(value):
          if isinstance(value, str):
              return value
          elif isinstance(value, dict):
              if "content" in value:
                  return str(value["content"])
              elif "text" in value:
                  return str(value["text"])
          elif isinstance(value, list) and len(value) > 0:
              if isinstance(value[0], dict) and "text" in value[0]:
                  return str(value[0]["text"])
          
          return str(value) if value is not None else ""
    performance_class: "O(1)"
    validation_rules:
      max_output_length: 100000
      
  aggregate_usage_metrics:
    input_type: "object"
    output_type: "usage_object"
    description: "Aggregate token usage from various sources"
    implementation_type: "native_python"
    implementation: |
      def aggregate_usage_metrics(usage_data):
          if not isinstance(usage_data, dict):
              return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
          
          prompt_tokens = usage_data.get("prompt_tokens", 0) or usage_data.get("input_tokens", 0)
          completion_tokens = usage_data.get("completion_tokens", 0) or usage_data.get("output_tokens", 0)
          total_tokens = usage_data.get("total_tokens", prompt_tokens + completion_tokens)
          
          return {
              "prompt_tokens": int(prompt_tokens) if prompt_tokens else 0,
              "completion_tokens": int(completion_tokens) if completion_tokens else 0,
              "total_tokens": int(total_tokens) if total_tokens else 0
          }
    performance_class: "O(1)"
    validation_rules:
      required_output_fields: ["prompt_tokens", "completion_tokens", "total_tokens"]

data_type_conversions:
  string_to_integer:
    from_type: "string"
    to_type: "integer"
    conversion_function: "int"
    validation_required: true
    error_handling: "return_zero"
    
  object_to_string:
    from_type: "object"
    to_type: "string"
    conversion_function: "json_serialize"
    validation_required: false
    error_handling: "return_str_representation"

performance_guarantees:
  max_execution_time_ms: 10
  memory_limit_mb: 10
  forbidden_operations: ["regex", "loops_over_unknown_size", "recursive_calls", "network_requests"]
```

## 🎯 **DSL Integration Strategy**

The five DSL types work together in a coordinated processing pipeline, with **package-based instrumentor detection** as the primary mechanism:

### **Processing Flow**

1. **Instrumentor Detection**: Use Python package inspection to detect installed instrumentors and map to semantic convention versions
2. **Source Convention Processing**: Extract top-level semantic data using detected convention version
3. **Structure Discovery**: Dynamically analyze raw LLM response objects embedded within the semantic data
4. **Target Schema Mapping**: Map extracted data to target schema (HoneyHive)
5. **Transform Rules**: Apply transformation logic between source and target formats

### **Two-Level Data Processing**

- **Top Level**: Semantic convention attributes (handled by Source Convention DSL)
- **Nested Level**: Raw LLM response objects within those attributes (handled by Structure Discovery DSL)

For example:
```
Span Attributes (Top Level - Source Convention):
├── llm.model_name: "gpt-3.5-turbo"
├── llm.input_messages: [...]  ← Structure Discovery analyzes this
└── llm.output_message: {...}  ← Structure Discovery analyzes this
```

### **Package-Based Detection Benefits**

- **Deterministic Version Detection**: No guessing based on data patterns
- **Standard Python Approach**: Uses built-in `importlib.metadata` for package inspection
- **Long-term Maintainability**: DSL configurations built from compatibility matrix data during development
- **Runtime Simplicity**: No external dependencies for instrumentor detection

## 📋 **DSL Validation Framework**

### **Schema Validation**
Each DSL file must pass:
1. **YAML Syntax Validation**: Valid YAML structure
2. **Schema Compliance**: Matches DSL type specification
3. **Reference Validation**: All references resolve correctly
4. **Performance Compliance**: No O(n²) or higher operations
5. **Semantic Validation**: Logical consistency checks

### **Cross-DSL Validation**
Multiple DSL files must pass:
1. **Reference Integrity**: Cross-file references are valid
2. **Type Compatibility**: Data types match between DSLs
3. **Semantic Consistency**: Semantic types are used consistently
4. **Version Compatibility**: Compatible version requirements

### **Runtime Validation**
During execution:
1. **Input Validation**: Data matches expected types and constraints
2. **Output Validation**: Results conform to specifications
3. **Performance Monitoring**: Operations stay within performance classes
4. **Error Handling**: Graceful handling of validation failures

## 🎯 **DSL Implementation Requirements**

### **DSL Compiler Requirements**
1. **Parse and validate all DSL types**
2. **Generate O(1) lookup structures**
3. **Compile transform functions to native Python**
4. **Create cross-reference maps**
5. **Generate validation code**
6. **Use compatibility matrix data for DSL configuration building**

### **Runtime Engine Requirements**
1. **Load compiled DSL configurations**
2. **Execute transforms with performance monitoring**
3. **Handle validation errors gracefully**
4. **Support configuration reloading**
5. **Provide debugging and introspection capabilities**
6. **Integrate with HoneyHive SDK caching architecture**

---

**This DSL Specification provides the complete formal specification for implementing all five DSL types with O(1) performance guarantees and Agent OS integration.**
