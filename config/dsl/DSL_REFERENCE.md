# Universal LLM Discovery Engine v4.0 - DSL Reference Guide

**Version**: 4.0  
**Date**: 2025-09-30  
**Owner**: AI Assistant  
**Purpose**: Complete reference for provider DSL development and maintenance

---

## 📋 **Quick Reference**

Each provider requires **exactly 4 YAML files**:

```
config/dsl/providers/{provider_name}/
├── structure_patterns.yaml    # Provider signature detection (O(1) lookup)
├── navigation_rules.yaml       # Field extraction paths (how to get data)
├── field_mappings.yaml         # HoneyHive schema mapping (where data goes)
└── transforms.yaml             # Data transformation functions (data processing)
```

---

## 🎯 **File 1: Structure Patterns (Provider Detection)**

**Purpose**: Define unique field combinations that identify this provider's spans for O(1) detection.

### **Template Structure**

```yaml
version: "1.0"
provider: "{provider_name}"
dsl_type: "provider_structure_patterns"

patterns:
  # Pattern naming: {instrumentor}_{provider}
  # Examples: traceloop_openai, openinference_anthropic, openlit_gemini
  
  {instrumentor}_{provider}:
    required_fields:
      - "field.path.1"              # MUST be present for detection
      - "field.path.2"
      - "field.path.3"
    optional_fields:
      - "optional.field.1"          # MAY be present (boosts confidence)
      - "optional.field.2"
    confidence_weight: 0.95         # 0.0-1.0 (higher = more confident)
    description: "Human-readable pattern description"
    instrumentor_framework: "{instrumentor}"  # traceloop, openinference, openlit, etc.

validation:
  minimum_signature_fields: 2     # Min required fields for reliable detection
  maximum_patterns: 10            # Max patterns per provider
  confidence_threshold: 0.80      # Min confidence to accept pattern
```

### **Instrumentor-Specific Patterns**

**Traceloop** (uses `gen_ai.*` prefix):
```yaml
traceloop_openai:
  required_fields:
    - "gen_ai.system"              # Will be "openai"
    - "gen_ai.request.model"       # e.g., "gpt-4"
    - "gen_ai.usage.prompt_tokens"
  confidence_weight: 0.90
  instrumentor_framework: "traceloop"
```

**OpenInference** (uses `llm.*` prefix):
```yaml
openinference_openai:
  required_fields:
    - "llm.provider"               # Will be "openai"
    - "llm.model_name"             # e.g., "gpt-4"
    - "llm.input_messages"
  confidence_weight: 0.95
  instrumentor_framework: "openinference"
```

**OpenLit** (uses `openlit.*` prefix):
```yaml
openlit_openai:
  required_fields:
    - "openlit.provider"           # Will be "openai"
    - "openlit.model"              # e.g., "gpt-4"
    - "openlit.usage.prompt_tokens"
  confidence_weight: 0.95
  instrumentor_framework: "openlit"
```

### **Best Practices**
- ✅ Use 3-6 patterns per provider (covering main instrumentors)
- ✅ Include provider-specific fields that uniquely identify the provider
- ✅ Set confidence based on signature uniqueness (unique fields = higher confidence)
- ✅ Include value-based indicators (fields that contain provider name)
- ❌ Don't use generic fields shared across all providers
- ❌ Don't duplicate signatures between providers

---

## 🗺️ **File 2: Navigation Rules (Field Extraction)**

**Purpose**: Define how to extract data from detected provider attributes.

### **Template Structure**

```yaml
version: "1.0"
provider: "{provider_name}"
dsl_type: "provider_navigation_rules"

navigation_rules:
  # Rule naming: {instrumentor}_{field_name}
  # Examples: traceloop_model_name, openinference_input_messages
  
  {instrumentor}_{field_name}:
    source_field: "attribute.path.in.span"
    extraction_method: "direct_copy"        # See extraction methods below
    fallback_value: null                    # Value if field missing
    validation: "non_empty_string"          # Optional validation
    description: "What this rule extracts"
```

### **Extraction Methods**

| Method | Usage | Example |
|--------|-------|---------|
| `direct_copy` | Copy field value as-is | `attributes.get('llm.model_name')` |
| `array_flatten` | Flatten nested arrays | Combine message arrays |
| `object_merge` | Merge multiple objects | Combine usage metrics |
| `string_concat` | Join strings | Combine prompt parts |
| `numeric_sum` | Sum numbers | Total tokens |
| `first_non_null` | First non-null value | Fallback chain |

### **Validation Rules**

| Validator | Purpose | Use When |
|-----------|---------|----------|
| `non_empty_string` | Ensure string has content | Model names, prompts |
| `positive_number` | Ensure number > 0 | Token counts, costs |
| `array_of_objects` | Ensure array of dicts | Message arrays |
| `array_of_strings` | Ensure array of strings | Tool names |
| `valid_json` | Ensure parseable JSON | Raw responses |
| `non_null` | Ensure not None | Required fields |

### **Example: Complete Navigation Rules**

```yaml
navigation_rules:
  # TRACELOOP RULES (gen_ai.* prefix)
  traceloop_model_name:
    source_field: "gen_ai.request.model"
    extraction_method: "direct_copy"
    fallback_value: "unknown"
    validation: "non_empty_string"
    description: "Extract model from Traceloop"
    
  traceloop_prompt_tokens:
    source_field: "gen_ai.usage.prompt_tokens"
    extraction_method: "direct_copy"
    fallback_value: 0
    validation: "positive_number"
    description: "Extract prompt tokens from Traceloop"
  
  # OPENINFERENCE RULES (llm.* prefix)
  openinference_model_name:
    source_field: "llm.model_name"
    extraction_method: "direct_copy"
    fallback_value: "unknown"
    validation: "non_empty_string"
    description: "Extract model from OpenInference"
    
  openinference_input_messages:
    source_field: "llm.input_messages"
    extraction_method: "direct_copy"
    fallback_value: []
    validation: "array_of_objects"
    description: "Extract input messages from OpenInference"
  
  # OPENLIT RULES (openlit.* prefix)
  openlit_model_name:
    source_field: "openlit.model"
    extraction_method: "direct_copy"
    fallback_value: "unknown"
    validation: "non_empty_string"
    description: "Extract model from OpenLit"
```

### **Best Practices**
- ✅ Create rules for ALL 3 instrumentors (traceloop, openinference, openlit)
- ✅ Use descriptive rule names: `{instrumentor}_{what_it_extracts}`
- ✅ Always provide fallback values (never leave users with crashes)
- ✅ Match extraction method to data type (array for lists, direct for primitives)
- ❌ Don't hardcode instrumentor assumptions (use prefixed rule names)
- ❌ Don't leave fallback_value empty (always provide safe defaults)

---

## 🔗 **File 3: Field Mappings (HoneyHive Schema)**

**Purpose**: Map extracted data to HoneyHive's 4-section schema (inputs, outputs, config, metadata).

### **Template Structure**

```yaml
version: "1.0"
provider: "{provider_name}"
dsl_type: "provider_field_mappings"

field_mappings:
  # INPUTS: User inputs, chat history, prompts, context
  inputs:
    chat_history:
      source_rule: "input_messages"        # Base rule name (no instrumentor prefix!)
      required: false
      description: "User conversation history"
    
    prompt:
      source_rule: "user_prompt"
      required: false
      description: "User prompt text"
  
  # OUTPUTS: Model responses, completions, tool calls, results
  outputs:
    response:
      source_rule: "output_messages"
      required: false
      description: "Model response messages"
    
    completion:
      source_rule: "completion_text"
      required: false
      description: "Completion text content"
    
    finish_reason:
      source_rule: "finish_reason_normalized"
      required: false
      description: "Completion finish reason"
  
  # CONFIG: Model parameters, temperature, max tokens, system prompts
  config:
    model:
      source_rule: "model_name"            # Maps to navigation rule
      required: true
      description: "Model identifier"
    
    temperature:
      source_rule: "temperature"
      required: false
      description: "Model temperature setting"
    
    max_tokens:
      source_rule: "max_tokens"
      required: false
      description: "Maximum token limit"
  
  # METADATA: Usage metrics, timestamps, provider info, performance
  metadata:
    provider:
      source_rule: "static_{provider}"     # Static value
      required: true
      description: "Provider identifier"
    
    instrumentor:
      source_rule: "detect_instrumentor"   # Dynamic detection
      required: false
      description: "Instrumentor framework"
    
    prompt_tokens:
      source_rule: "prompt_tokens"
      required: false
      description: "Input token count"
    
    completion_tokens:
      source_rule: "completion_tokens"
      required: false
      description: "Output token count"
    
    cost:
      source_rule: "calculate_cost"        # Transform function
      required: false
      description: "Request cost in USD"
```

### **HoneyHive Schema Sections**

| Section | Purpose | Typical Fields |
|---------|---------|---------------|
| **inputs** | What the user provided | `chat_history`, `prompt`, `system_message`, `context`, `documents` |
| **outputs** | What the model returned | `response`, `completion`, `tool_calls`, `finish_reason`, `choices` |
| **config** | Model settings | `model`, `temperature`, `max_tokens`, `top_p`, `frequency_penalty` |
| **metadata** | System information | `provider`, `instrumentor`, `prompt_tokens`, `completion_tokens`, `cost`, `latency` |

### **Source Rule Types**

1. **Navigation Rules** (most common):
   ```yaml
   model:
     source_rule: "model_name"    # Maps to {instrumentor}_model_name in navigation_rules.yaml
   ```

2. **Transform Functions**:
   ```yaml
   cost:
     source_rule: "calculate_openai_cost"  # Defined in transforms.yaml
   ```

3. **Static Values**:
   ```yaml
   provider:
     source_rule: "static_openai"  # Returns "openai"
   ```

### **Two-Tier Routing Magic** ✨

**CRITICAL**: Use **base rule names** (without instrumentor prefix) in field_mappings!

The compiler generates instrumentor-aware routing code:

```yaml
# ❌ WRONG - Hardcodes instrumentor
config:
  model:
    source_rule: "openinference_model_name"  # Only works for OpenInference!

# ✅ CORRECT - Dynamic routing
config:
  model:
    source_rule: "model_name"  # Router tries: traceloop_model_name, openinference_model_name, openlit_model_name
```

Generated code:
```python
def extract_openai_data(attributes, instrumentor='unknown'):
    config = {}
    # Router automatically selects correct rule based on detected instrumentor
    config['model'] = (
        attributes.get('gen_ai.request.model', 'unknown') if instrumentor == 'traceloop' else
        attributes.get('llm.model_name', 'unknown') if instrumentor == 'openinference' else
        attributes.get('openlit.model', 'unknown') if instrumentor == 'openlit' else
        None
    )
```

### **Best Practices**
- ✅ Use **base rule names** (no instrumentor prefix) for automatic routing
- ✅ Mark `model` and `provider` as `required: true` (always needed)
- ✅ Provide descriptions for all fields (helps maintenance)
- ✅ Group logically (user data → inputs, model data → outputs, settings → config, metrics → metadata)
- ❌ Don't hardcode instrumentor-specific rules in field_mappings
- ❌ Don't skip descriptions (future you will thank you)

---

## ⚙️ **File 4: Transforms (Data Processing)**

**Purpose**: Define reusable transformation functions for data manipulation, cost calculation, and normalization.

### **Template Structure**

```yaml
version: "1.0"
provider: "{provider_name}"
dsl_type: "provider_transforms"

transforms:
  {transform_name}:
    function_type: "{type}"              # See function types below
    implementation: "{impl}"             # Python function name
    parameters:
      {param_name}: {param_value}        # Function-specific params
    description: "What this transform does"
```

### **Function Types**

#### **1. String Extraction**
Extract and process string data from complex structures.

```yaml
extract_user_prompt:
  function_type: "extract_message_content_by_role"
  implementation: "python_code_generated_at_build_time"
  parameters:
    role: "user"
    messages_field: "chat_history"
    separator: "\n\n"
  description: "Extract user messages and join with double newlines"
```

#### **2. Array Transformation**
Process arrays and lists.

```yaml
extract_tool_calls:
  function_type: "extract_field_values_from_messages"
  implementation: "python_code_generated_at_build_time"
  parameters:
    source_array_field: "response"
    extract_field: "tool_calls"
    flatten: true
  description: "Extract tool calls from response messages"
```

#### **3. Numeric Calculation**
Calculate costs, sums, averages.

```yaml
calculate_openai_cost:
  function_type: "calculate_openai_cost"
  implementation: "python_code_generated_at_build_time"
  parameters:
    model_field: "model"
    prompt_tokens_field: "prompt_tokens"
    completion_tokens_field: "completion_tokens"
    pricing_table:
      "gpt-4o": {input: 0.0025, output: 0.01}
      "gpt-4-turbo": {input: 0.01, output: 0.03}
      # ... current pricing as of 2025-09-30
  description: "Calculate request cost using current OpenAI pricing"
```

#### **4. Normalization**
Standardize values across providers.

```yaml
normalize_finish_reason:
  function_type: "normalize_finish_reason"
  implementation: "python_code_generated_at_build_time"
  parameters:
    source_field: "finish_reason"
    mapping:
      "stop": "complete"
      "length": "max_tokens"
      "tool_calls": "function_call"
      "content_filter": "filtered"
  description: "Normalize finish reason to standard values"
```

### **Common Transform Patterns**

```yaml
transforms:
  # Extract user prompt
  extract_user_prompt:
    function_type: "extract_message_content_by_role"
    parameters:
      role: "user"
      messages_field: "chat_history"
      separator: "\n\n"
  
  # Extract assistant completion
  extract_completion_text:
    function_type: "extract_message_content_by_role"
    parameters:
      role: "assistant"
      messages_field: "response"
      separator: "\n"
  
  # Extract system message
  extract_system_prompt:
    function_type: "extract_message_content_by_role"
    parameters:
      role: "system"
      messages_field: "chat_history"
      separator: ""
  
  # Normalize finish reason
  extract_finish_reason_normalized:
    function_type: "normalize_finish_reason"
    parameters:
      source_field: "finish_reason"
      mapping:
        "stop": "complete"
        "length": "max_tokens"
  
  # Calculate cost (provider-specific)
  calculate_{provider}_cost:
    function_type: "calculate_{provider}_cost"
    parameters:
      model_field: "model"
      prompt_tokens_field: "prompt_tokens"
      completion_tokens_field: "completion_tokens"
      pricing_table:
        "{model_1}": {input: 0.xxx, output: 0.xxx}
        "{model_2}": {input: 0.xxx, output: 0.xxx}
```

### **Pricing Tables**

**CRITICAL**: Always use **current pricing as of the date you're working**!

```yaml
# Example: OpenAI Pricing (2025-09-30)
pricing_table:
  "gpt-4o": {input: 0.0025, output: 0.01}
  "gpt-4o-mini": {input: 0.00015, output: 0.0006}
  "gpt-4-turbo": {input: 0.01, output: 0.03}
  "gpt-4": {input: 0.03, output: 0.06}
  "gpt-3.5-turbo": {input: 0.0005, output: 0.0015}
  # ... all current models
```

### **Best Practices**
- ✅ Keep pricing tables current (check official docs)
- ✅ Include ALL current models (including legacy for backward compatibility)
- ✅ Use descriptive transform names (`extract_user_prompt` not `get_prompt`)
- ✅ Document pricing source and date in provider's RESEARCH_SOURCES.md
- ❌ Don't hardcode old pricing (causes incorrect cost calculations)
- ❌ Don't skip model variants (users may use any model)

---

## 🚀 **Development Workflow**

### **Creating a New Provider**

1. **Generate Template** (30 seconds):
   ```bash
   cd /Users/josh/src/github.com/honeyhiveai/python-sdk
   python scripts/generate_provider_template.py {provider_name}
   ```

2. **Research Phase** (30-60 minutes):
   - Read official API documentation
   - Identify semantic convention patterns for each instrumentor
   - Research current models and pricing
   - Create `RESEARCH_SOURCES.md`

3. **Populate DSL Files** (1-2 hours):
   - **structure_patterns.yaml**: 3-6 patterns covering main instrumentors
   - **navigation_rules.yaml**: All extraction rules × 3 instrumentors
   - **field_mappings.yaml**: Complete HoneyHive schema mapping
   - **transforms.yaml**: Cost calculation + data transformations

4. **Compile & Validate** (1 minute):
   ```bash
   python -m config.dsl.compiler
   ```

5. **Test** (15-30 minutes):
   ```bash
   # Test detection
   python scripts/test_two_tier_extraction.py
   
   # Test performance
   python scripts/profile_universal_engine.py
   ```

### **Updating an Existing Provider**

1. **Check Research Sources**: Verify pricing and models are current
2. **Update Files**: Modify relevant YAML files
3. **Recompile**: `python -m config.dsl.compiler`
4. **Test**: Run extraction and performance tests
5. **Document**: Update RESEARCH_SOURCES.md with changes

---

## ✅ **Quality Checklist**

Before considering a provider "complete":

**Structure Patterns**:
- [ ] 3-6 patterns covering major instrumentors (Traceloop, OpenInference, OpenLit)
- [ ] Unique required_fields (not duplicated with other providers)
- [ ] Appropriate confidence_weight (0.85-0.95 for primary patterns)
- [ ] Clear descriptions

**Navigation Rules**:
- [ ] Rules for ALL 3 instrumentors (traceloop_*, openinference_*, openlit_*)
- [ ] Safe fallback values for all fields
- [ ] Appropriate validation rules
- [ ] Descriptive names and descriptions

**Field Mappings**:
- [ ] All 4 sections populated (inputs, outputs, config, metadata)
- [ ] `model` marked as required: true
- [ ] `provider` marked as required: true
- [ ] Base rule names (no instrumentor prefixes)
- [ ] Descriptions for all fields

**Transforms**:
- [ ] Cost calculation with current pricing (dated)
- [ ] Message extraction transforms (user, assistant, system)
- [ ] Finish reason normalization
- [ ] All required transforms referenced in field_mappings

**General**:
- [ ] Compiles without errors
- [ ] Passes bundle validation
- [ ] RESEARCH_SOURCES.md created and comprehensive
- [ ] Tested with real span data
- [ ] Performance meets targets (<0.1ms processing)

---

## 📚 **Reference Documentation**

- **v4.0 Design**: `/universal_llm_discovery_engine_v4_final/`
  - `ARCHITECTURE_FOUNDATION.md` - Architecture overview
  - `PROVIDER_SPECIFICATION.md` - Complete DSL specification
  - `IMPLEMENTATION_PLAN.md` - Build system details
  - `RESEARCH_REFERENCES.md` - Instrumentor patterns

- **Provider Examples**:
  - `config/dsl/providers/openai/` - Complete OpenAI implementation
  - `config/dsl/providers/anthropic/` - Complete Anthropic implementation
  - `config/dsl/providers/gemini/` - Complete Gemini implementation

- **Shared Configuration**:
  - `config/dsl/shared/core_schema.yaml` - HoneyHive schema definition
  - `config/dsl/shared/instrumentor_mappings.yaml` - Instrumentor patterns
  - `config/dsl/shared/validation_rules.yaml` - Common validation

- **Tools**:
  - `scripts/generate_provider_template.py` - Template generator
  - `config/dsl/compiler.py` - DSL compiler
  - `scripts/test_two_tier_extraction.py` - Extraction tester
  - `scripts/profile_universal_engine.py` - Performance profiler

---

## 🎯 **Quick Tips for AI Assistants**

As the owner of these files, keep these in mind:

1. **Always use base rule names** in field_mappings.yaml (no instrumentor prefix)
2. **Create rules for all 3 instrumentors** in navigation_rules.yaml
3. **Keep pricing current** - check official docs for latest pricing
4. **Test after every change** - compile and run extraction tests
5. **Document everything** - RESEARCH_SOURCES.md is your friend
6. **Follow the pattern** - look at openai/anthropic/gemini for reference
7. **Validate early** - catch issues at compile time, not runtime

**Common Mistakes to Avoid**:
- ❌ Hardcoding instrumentor-specific rules in field_mappings
- ❌ Forgetting to create rules for all instrumentors
- ❌ Using outdated pricing (always verify current pricing)
- ❌ Skipping RESEARCH_SOURCES.md (document your sources!)
- ❌ Not testing with real span data

---

**🚀 You're ready to create and maintain provider DSLs! Reference this guide anytime you need clarification.**
