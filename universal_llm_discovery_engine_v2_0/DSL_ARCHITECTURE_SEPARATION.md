# DSL Architecture - Proper Separation of Responsibilities

**Version**: 1.0  
**Date**: 2025-01-27  
**Status**: Architecture Correction  

## 🎯 **The Two Distinct DSL Responsibilities**

### **1. LLM Response Structure Discovery DSL**
**Purpose**: Understand and parse diverse LLM provider response formats
**Input**: Raw JSON from any LLM provider (OpenAI, Anthropic, Gemini, etc.)
**Output**: Structured field classifications and extracted data

### **2. Semantic Convention Mapping DSL** 
**Purpose**: Convert between different observability framework conventions
**Input**: Structured data from discovery + source convention type
**Output**: Target convention format (OpenInference, Traceloop, OpenLit, HoneyHive)

## 🏗️ **Corrected DSL Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Raw LLM Provider Response                │
│  OpenAI JSON │ Anthropic JSON │ Gemini JSON │ Unknown JSON  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│            LLM Response Structure Discovery DSL             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │Structure Pattern│  │Field Classifier │  │Content Extract│ │
│  │   Recognition   │  │      DSL        │  │     DSL      │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Normalized Field Data                       │
│     {field_path, field_type, content, confidence}          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│             Semantic Convention Mapping DSL                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ OpenInference   │  │   Traceloop     │  │  HoneyHive   │ │
│  │   Mapping       │  │   Mapping       │  │   Mapping    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Target Convention Output                       │
│   OpenInference │ Traceloop │ OpenLit │ HoneyHive Schema   │
└─────────────────────────────────────────────────────────────┘
```

## 📋 **DSL Component Breakdown**

### **Component 1: LLM Response Structure Discovery DSL**

#### **1.1 Structure Pattern Recognition DSL**
```yaml
# llm_response_discovery/structure_patterns.yaml
structure_patterns:
  version: "1.0"
  
  # Detect provider response patterns
  provider_signatures:
    openai_pattern:
      required_paths: ["choices", "usage", "model"]
      optional_paths: ["id", "created", "system_fingerprint"]
      structure_type: "flat_choices_array"
      
    anthropic_pattern:
      required_paths: ["content", "usage", "model"]
      optional_paths: ["id", "type", "stop_reason"]
      structure_type: "content_array"
      
    gemini_pattern:
      required_paths: ["candidates", "usageMetadata"]
      optional_paths: ["safetyRatings", "modelVersion"]
      structure_type: "candidates_array"
  
  # Structure navigation rules
  navigation_rules:
    message_content_paths:
      - pattern: "choices.*.message.content"
        provider: "openai"
        confidence: 0.95
      - pattern: "content.*.text"
        provider: "anthropic" 
        confidence: 0.90
      - pattern: "candidates.*.content.parts.*.text"
        provider: "gemini"
        confidence: 0.85
```

#### **1.2 Field Classification DSL**
```yaml
# llm_response_discovery/field_classification.yaml
field_classification:
  version: "1.0"
  
  # Semantic field type classification
  field_types:
    message_content:
      indicators:
        path_patterns: ["message.content", "content.text", "parts.text"]
        content_patterns: ["string", "length > 0"]
        context_clues: ["role", "assistant", "user"]
      
    token_usage:
      indicators:
        path_patterns: ["usage", "tokens", "token_count"]
        content_patterns: ["integer", "range 0-1000000"]
        field_names: ["prompt_tokens", "completion_tokens", "input_tokens"]
      
    model_identifier:
      indicators:
        path_patterns: ["model", "model_name", "modelId"]
        content_patterns: ["string", "contains dash or underscore"]
        prefixes: ["gpt-", "claude-", "gemini-", "llama-"]
```

#### **1.3 Content Extraction DSL**
```yaml
# llm_response_discovery/content_extraction.yaml
content_extraction:
  version: "1.0"
  
  # Extraction rules for different content types
  extraction_rules:
    message_extraction:
      simple_text:
        source_path: "content"
        extraction_method: "direct"
        
      array_text:
        source_path: "content.*.text"
        extraction_method: "concatenate"
        separator: " "
        
      parts_array:
        source_path: "parts.*.text"
        extraction_method: "concatenate"
        separator: " "
    
    usage_extraction:
      openai_format:
        prompt_tokens: "usage.prompt_tokens"
        completion_tokens: "usage.completion_tokens"
        total_tokens: "usage.total_tokens"
        
      anthropic_format:
        prompt_tokens: "usage.input_tokens"
        completion_tokens: "usage.output_tokens"
        total_tokens: "calculated"
```

### **Component 2: Semantic Convention Mapping DSL**

#### **2.1 OpenInference Mapping DSL**
```yaml
# semantic_convention_mapping/openinference_mapping.yaml
openinference_mapping:
  version: "1.0"
  target_convention: "openinference"
  
  # Map normalized fields to OpenInference attributes
  field_mappings:
    message_content:
      input_messages:
        target_attribute: "llm.input_messages"
        format: "array_of_objects"
        structure:
          role: "extracted_role"
          content: "extracted_content"
      
      output_messages:
        target_attribute: "llm.output_messages"
        format: "array_of_objects"
        structure:
          role: "assistant"
          content: "extracted_content"
    
    token_usage:
      prompt_tokens:
        target_attribute: "llm.token_count_prompt"
        format: "integer"
        source: "normalized_usage.prompt_tokens"
        
      completion_tokens:
        target_attribute: "llm.token_count_completion"
        format: "integer"
        source: "normalized_usage.completion_tokens"
    
    model_info:
      model_name:
        target_attribute: "llm.model_name"
        format: "string"
        source: "normalized_model.name"
```

#### **2.2 Traceloop Mapping DSL**
```yaml
# semantic_convention_mapping/traceloop_mapping.yaml
traceloop_mapping:
  version: "1.0"
  target_convention: "traceloop"
  
  # Map normalized fields to Traceloop Gen AI attributes
  field_mappings:
    model_info:
      request_model:
        target_attribute: "gen_ai.request.model"
        format: "string"
        source: "normalized_model.name"
        
      response_model:
        target_attribute: "gen_ai.response.model"
        format: "string"
        source: "normalized_model.name"
    
    token_usage:
      prompt_tokens:
        target_attribute: "gen_ai.usage.prompt_tokens"
        format: "integer"
        source: "normalized_usage.prompt_tokens"
        
      completion_tokens:
        target_attribute: "gen_ai.usage.completion_tokens"
        format: "integer"
        source: "normalized_usage.completion_tokens"
    
    message_content:
      system_message:
        target_attribute: "gen_ai.system"
        format: "string"
        source: "normalized_messages.system"
        
      completion:
        target_attribute: "gen_ai.completion"
        format: "string"
        source: "normalized_messages.assistant"
```

#### **2.3 HoneyHive Schema Mapping DSL**
```yaml
# semantic_convention_mapping/honeyhive_mapping.yaml
honeyhive_mapping:
  version: "1.0"
  target_convention: "honeyhive"
  
  # Map normalized fields to HoneyHive four-section schema
  section_mappings:
    inputs:
      chat_history:
        source: "normalized_messages.conversation"
        format: "message_array"
        
      system_prompt:
        source: "normalized_messages.system"
        format: "string"
    
    outputs:
      content:
        source: "normalized_messages.assistant"
        format: "string"
        
      tool_calls:
        source: "normalized_tool_calls"
        format: "tool_call_array"
        
      finish_reason:
        source: "normalized_completion.finish_reason"
        format: "string"
    
    config:
      model:
        source: "normalized_model.name"
        format: "string"
        
      parameters:
        source: "normalized_config"
        format: "object"
    
    metadata:
      usage:
        source: "normalized_usage"
        format: "usage_object"
        
      provider:
        source: "detected_provider.name"
        format: "string"
        
      processing_metrics:
        source: "processing_context"
        format: "metrics_object"
```

## 🔧 **Implementation Architecture**

### **Processing Pipeline**
```python
# Step 1: LLM Response Structure Discovery
raw_response = get_llm_response()
discovery_engine = LLMResponseDiscoveryEngine(discovery_dsl_config)
normalized_data = discovery_engine.process(raw_response)

# Step 2: Semantic Convention Mapping  
mapping_engine = SemanticConventionMapper(mapping_dsl_config)
openinference_output = mapping_engine.map_to_openinference(normalized_data)
traceloop_output = mapping_engine.map_to_traceloop(normalized_data)
honeyhive_output = mapping_engine.map_to_honeyhive(normalized_data)
```

### **Clear Separation Benefits**
1. **Single Responsibility**: Each DSL component has one clear purpose
2. **Independent Evolution**: LLM discovery can evolve separately from convention mapping
3. **Reusable Components**: Convention mapping works with any normalized data
4. **Testable**: Each component can be tested independently
5. **Maintainable**: Changes to provider formats don't affect convention mapping

## 📋 **File Structure Correction**

```
src/honeyhive/tracer/semantic_conventions/
├── llm_response_discovery/           # LLM Response Structure Discovery
│   ├── __init__.py
│   ├── discovery_engine.py           # Main discovery processor
│   ├── structure_analyzer.py         # JSON structure analysis
│   ├── field_classifier.py           # Field type classification
│   ├── content_extractor.py          # Content extraction logic
│   └── dsl/
│       ├── structure_patterns.yaml   # Provider pattern recognition
│       ├── field_classification.yaml # Field type classification rules
│       └── content_extraction.yaml   # Content extraction rules
│
├── semantic_convention_mapping/      # Semantic Convention Mapping
│   ├── __init__.py
│   ├── mapping_engine.py             # Main mapping processor
│   ├── openinference_mapper.py       # OpenInference convention mapper
│   ├── traceloop_mapper.py           # Traceloop convention mapper
│   ├── honeyhive_mapper.py           # HoneyHive schema mapper
│   └── dsl/
│       ├── openinference_mapping.yaml
│       ├── traceloop_mapping.yaml
│       ├── honeyhive_mapping.yaml
│       └── openlit_mapping.yaml
│
└── universal/                        # Orchestration Layer
    ├── __init__.py
    ├── universal_processor.py        # Coordinates both engines
    └── models.py                     # Shared data models
```

This corrected architecture provides proper separation of concerns with single responsibility for each DSL component.
