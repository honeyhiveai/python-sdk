# Universal LLM Discovery Engine - DSL Specification v1.0

**Version**: 1.0  
**Date**: 2025-01-27  
**Status**: Formal Specification  
**Purpose**: Complete DSL specification before implementation

---

## 📋 **DSL Overview**

The Universal DSL consists of **four distinct specification types**, each with defined syntax, semantics, and validation rules:

1. **Structure Discovery DSL** - Defines how to analyze raw LLM provider responses
2. **Source Convention DSL** - Defines how to extract data from existing semantic conventions  
3. **Target Schema DSL** - Defines target schema structures (HoneyHive, etc.)
4. **Transform Rules DSL** - Defines transformation logic between source and target

## 🏗️ **DSL Type 1: Structure Discovery DSL**

### **Purpose**
Analyze raw JSON responses from LLM providers to identify structure patterns and extract field data.

### **File Naming Convention**
`structure_discovery_v{major}_{minor}.yaml`

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

# Optional sections
extraction_strategies:           # Optional section
  {strategy_name}:              # Strategy identifier
    conditions: object           # When to apply this strategy
    actions: [object]           # Steps to execute
    
validation_rules:               # Optional section
  required_patterns: [string]   # Patterns that must be present
  mutual_exclusions: [string]   # Patterns that cannot coexist
  
performance_hints:              # Optional section
  cache_keys: [string]          # Fields to use for caching
  optimization_flags: object    # Performance optimization settings
```

### **Validation Rules**

1. **Version Format**: Must follow semantic versioning (major.minor)
2. **Pattern IDs**: Must be sequential (pattern_001, pattern_002, etc.)
3. **Rule IDs**: Must be sequential within each semantic field type
4. **Confidence Values**: Must be between 0.0 and 1.0
5. **Path Expressions**: Must be valid JSONPath syntax with wildcard support
6. **References**: All pattern_match values must reference existing pattern IDs

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
      
  token_usage:
    rule_001:
      path_expression: "usage.prompt_tokens"
      pattern_match: "pattern_001"
      confidence: 0.98
      
    rule_002:
      path_expression: "usage.input_tokens"
      pattern_match: "pattern_002"
      confidence: 0.98

field_classification:
  message_content:
    path_indicators: ["message.content", "content.text", "parts.text"]
    content_validators:
      - type: "string"
        min_length: 1
        max_length: 100000
    context_clues: ["role", "assistant", "user"]
    confidence_modifiers:
      has_role_field: 0.1
      length_over_10: 0.05
      
  token_usage:
    path_indicators: ["usage", "tokens", "token_count"]
    content_validators:
      - type: "integer"
        min_value: 0
        max_value: 1000000
    context_clues: ["prompt_tokens", "completion_tokens"]
```

## 🏗️ **DSL Type 2: Source Convention DSL**

### **Purpose**
Define how to extract semantic data FROM existing observability framework conventions.

### **File Naming Convention**
`{convention_name}_source_v{major}_{minor}.yaml`

### **Schema Specification**

```yaml
# Required root structure
version: string                     # Semantic version
dsl_type: "source_convention"       # Fixed identifier
convention_name: string             # Convention identifier (openinference, traceloop, etc.)
description: string                 # Human-readable description

# Core specification sections
recognition_patterns:               # Required section
  primary_indicators: [object]      # Required: How to identify this convention
  confidence_scoring: object        # Required: Confidence calculation rules
  
extraction_rules:                   # Required section
  {semantic_category}:              # Semantic category (model_information, message_data, etc.)
    {field_name}:                   # Field identifier within category
      source_attribute: string      # Required: Source attribute name
      data_type: string            # Required: Expected data type
      semantic_type: string        # Required: Semantic classification
      extraction_rules: object     # Optional: Complex extraction logic
      structure_validation: object # Optional: Validation rules for complex types
      
# Optional sections
message_reconstruction:             # Optional: For conventions with flat message structure
  conversation_assembly: object     # Rules for rebuilding conversation structure
  
fallback_strategies:               # Optional: Handling missing/malformed data
  {strategy_name}: object          # Strategy definition
  
compatibility_notes:               # Optional: Version-specific notes
  deprecated_attributes: [string]   # Attributes being phased out
  new_attributes: [string]         # Recently added attributes
```

### **Validation Rules**

1. **Convention Name**: Must be lowercase, underscore-separated
2. **Semantic Categories**: Must use standard categories (model_information, message_data, usage_metrics, etc.)
3. **Data Types**: Must be from allowed set (string, integer, float, boolean, array, object)
4. **Semantic Types**: Must be from standard semantic type vocabulary
5. **Source Attributes**: Must be valid attribute names for the convention

### **Example Source Convention DSL**

```yaml
version: "0.1.15"
dsl_type: "source_convention"
convention_name: "openinference"
description: "Extract semantic data from OpenInference semantic conventions"

recognition_patterns:
  primary_indicators:
    - attribute_prefix: "llm."
      required_attributes: ["llm.model_name"]
      optional_attributes: ["llm.input_messages", "llm.output_messages"]
      
  confidence_scoring:
    high_confidence: 0.9
    medium_confidence: 0.7
    low_confidence: 0.5

extraction_rules:
  model_information:
    model_name:
      source_attribute: "llm.model_name"
      data_type: "string"
      semantic_type: "model_identifier"
      
    invocation_parameters:
      source_attribute: "llm.invocation_parameters"
      data_type: "object"
      semantic_type: "model_config"
      extraction_rules:
        temperature: "temperature"
        max_tokens: "max_tokens"
        
  message_data:
    input_messages:
      source_attribute: "llm.input_messages"
      data_type: "array"
      semantic_type: "input_messages"
      structure_validation:
        required_fields: ["role", "content"]
        optional_fields: ["name", "tool_calls"]

fallback_strategies:
  missing_total_tokens:
    action: "calculate"
    calculation: "llm.token_count_prompt + llm.token_count_completion"
```

## 🏗️ **DSL Type 3: Target Schema DSL**

### **Purpose**
Define target schema structures and mapping rules for output formats.

### **File Naming Convention**
`{schema_name}_target_v{major}_{minor}.yaml`

### **Schema Specification**

```yaml
# Required root structure
version: string                     # Semantic version
dsl_type: "target_schema"          # Fixed identifier
schema_name: string                # Schema identifier (honeyhive, openinference_output, etc.)
description: string                # Human-readable description

# Core specification sections
schema_structure:                  # Required section
  {section_name}:                 # Schema section (inputs, outputs, config, metadata, etc.)
    {field_name}:                 # Field within section
      data_type: string           # Required: Target data type
      required: boolean           # Required: Whether field is mandatory
      description: string         # Optional: Field description
      validation_rules: object    # Optional: Validation constraints
      default_value: any          # Optional: Default if not provided
      
mapping_rules:                    # Required section
  {section_name}:                 # Target section
    {field_name}:                 # Target field
      source_semantic_type: string # Required: Source semantic type to map from
      source_path: string         # Optional: Specific path in semantic data
      transform_function: string  # Optional: Transform to apply
      fallback_value: any         # Optional: Value if source missing
      
# Optional sections
validation_constraints:           # Optional: Cross-field validation
  {constraint_name}: object      # Constraint definition
  
output_formatting:               # Optional: Output format specifications
  serialization_format: string   # JSON, YAML, etc.
  field_ordering: [string]       # Preferred field order
  
compatibility_requirements:      # Optional: Compatibility specifications
  backward_compatible_versions: [string] # Versions this is compatible with
  breaking_changes: [string]     # Changes that break compatibility
```

### **Validation Rules**

1. **Schema Name**: Must be lowercase, underscore-separated
2. **Data Types**: Must be from standard type set
3. **Section Names**: Must follow schema naming conventions
4. **Source Semantic Types**: Must reference valid semantic types
5. **Transform Functions**: Must reference defined transform functions

### **Example Target Schema DSL**

```yaml
version: "1.0"
dsl_type: "target_schema"
schema_name: "honeyhive"
description: "HoneyHive unified schema for LLM observability data"

schema_structure:
  inputs:
    chat_history:
      data_type: "message_array"
      required: false
      description: "Conversation history with role and content"
      validation_rules:
        max_messages: 1000
        required_message_fields: ["role", "content"]
        
    system_prompt:
      data_type: "string"
      required: false
      description: "System-level instructions"
      validation_rules:
        max_length: 10000
        
  outputs:
    content:
      data_type: "string"
      required: true
      description: "Primary response content"
      
    tool_calls:
      data_type: "tool_call_array"
      required: false
      description: "Function/tool invocations"
      
  config:
    model:
      data_type: "string"
      required: true
      description: "Model identifier"
      
  metadata:
    usage:
      data_type: "usage_object"
      required: false
      description: "Token usage statistics"

mapping_rules:
  inputs:
    chat_history:
      source_semantic_type: "conversation_messages"
      transform_function: "normalize_message_array"
      
    system_prompt:
      source_semantic_type: "system_message"
      transform_function: "extract_text_content"
      
  outputs:
    content:
      source_semantic_type: "assistant_message"
      transform_function: "extract_text_content"
      fallback_value: ""
      
  config:
    model:
      source_semantic_type: "model_identifier"
      transform_function: "normalize_model_name"

validation_constraints:
  require_model_or_content:
    rule: "config.model OR outputs.content"
    error_message: "Either model or content must be present"
```

## 🏗️ **DSL Type 4: Transform Rules DSL**

### **Purpose**
Define transformation functions and logic for converting between data formats.

### **File Naming Convention**
`transform_rules_v{major}_{minor}.yaml`

### **Schema Specification**

```yaml
# Required root structure
version: string                     # Semantic version
dsl_type: "transform_rules"        # Fixed identifier
description: string                # Human-readable description

# Core specification sections
transform_functions:               # Required section
  {function_name}:                # Function identifier
    input_type: string            # Required: Expected input data type
    output_type: string           # Required: Produced output data type
    description: string           # Required: Function description
    implementation_type: string   # Required: native_python, lambda, custom
    implementation: string        # Required: Function implementation
    performance_class: string     # Required: O(1), O(log_n), O(n)
    validation_rules: object      # Optional: Input/output validation
    
data_type_conversions:            # Required section
  {source_type}_to_{target_type}: # Conversion identifier
    conversion_function: string   # Function to use for conversion
    validation_required: boolean  # Whether to validate before conversion
    error_handling: string       # How to handle conversion errors
    
# Optional sections
custom_transforms:                # Optional: Complex transformation logic
  {transform_name}: object       # Custom transform definition
  
performance_optimizations:        # Optional: Performance hints
  caching_strategies: object     # Caching configuration
  batch_processing: object       # Batch processing rules
```

### **Validation Rules**

1. **Function Names**: Must be lowercase, underscore-separated
2. **Performance Class**: Must be O(1), O(log n), or O(n) - O(n²) and higher forbidden
3. **Implementation Type**: Must be from allowed set
4. **Data Types**: Must be from standard type vocabulary
5. **Implementation**: Must be valid for the specified implementation type

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
          
          # Remove common prefixes
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
    
  normalize_message_array:
    input_type: "array"
    output_type: "message_array"
    description: "Normalize message arrays to standard format"
    implementation_type: "native_python"
    implementation: |
      def normalize_message_array(messages):
          if not isinstance(messages, list):
              return []
          
          normalized = []
          for msg in messages[:100]:  # Limit for O(1) behavior
              if isinstance(msg, dict):
                  normalized_msg = {
                      "role": msg.get("role", "unknown"),
                      "content": extract_text_content(msg.get("content", ""))
                  }
                  if "name" in msg:
                      normalized_msg["name"] = msg["name"]
                  normalized.append(normalized_msg)
          
          return normalized
    performance_class: "O(1)"

data_type_conversions:
  string_to_integer:
    conversion_function: "safe_int_conversion"
    validation_required: true
    error_handling: "return_zero"
    
  object_to_string:
    conversion_function: "json_serialize"
    validation_required: false
    error_handling: "return_str_representation"

custom_transforms:
  usage_metrics_aggregation:
    description: "Aggregate usage metrics from multiple sources"
    input_types: ["usage_object", "token_counts"]
    output_type: "normalized_usage"
    logic: "sum_token_counts_with_fallbacks"
```

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

### **Runtime Engine Requirements**
1. **Load compiled DSL configurations**
2. **Execute transforms with performance monitoring**
3. **Handle validation errors gracefully**
4. **Support hot-reloading of DSL configurations**
5. **Provide debugging and introspection capabilities**

---

**This DSL specification provides the complete foundation for implementing the Universal LLM Discovery Engine with formal syntax, semantics, and validation rules.**
