# Universal LLM Discovery Engine - DSL Architecture v1.0

**Version**: 1.0  
**Date**: 2025-01-27  
**Status**: Corrected Architecture  
**Breaking Change**: Complete separation of concerns with generic processing

---

## 🎯 **Core Principle: Zero Provider Logic in Code**

All provider-specific knowledge lives in DSL configuration files. The processing code is completely generic and driven by DSL rules.

## 🏗️ **Two-Stage Generic Processing Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Stage 1: Structure Discovery             │
│                                                             │
│  Raw JSON Input → Generic Discovery Engine → Normalized Data│
│                          ↑                                  │
│                   Structure DSL v1.0                       │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                 Stage 2: Convention Mapping                │
│                                                             │
│ Normalized Data → Generic Mapping Engine → Target Schema   │
│                          ↑                                 │
│                   Mapping DSL v1.0                        │
└─────────────────────────────────────────────────────────────┘
```

## 📁 **File Structure with Proper Versioning**

```
src/honeyhive/tracer/semantic_conventions/
├── structure_discovery/
│   ├── __init__.py
│   ├── generic_discovery_engine_v1_0.py      # Zero provider logic
│   ├── field_classifier_v1_0.py              # Generic field classification
│   ├── content_extractor_v1_0.py             # Generic content extraction
│   └── dsl/
│       ├── structure_discovery_v1_0.yaml     # All structure patterns
│       ├── field_classification_v1_0.yaml    # All field type rules
│       └── content_extraction_v1_0.yaml      # All extraction rules
│
├── convention_mapping/
│   ├── __init__.py
│   ├── generic_mapping_engine_v1_0.py        # Zero convention logic
│   ├── schema_transformer_v1_0.py            # Generic transformations
│   └── dsl/
│       ├── openinference_v0_1_15.yaml        # OpenInference convention
│       ├── traceloop_v0_46_2.yaml            # Traceloop convention
│       ├── openlit_v0_1_0.yaml               # OpenLit convention
│       └── honeyhive_v1_0.yaml               # HoneyHive schema
│
└── universal/
    ├── __init__.py
    ├── universal_processor_v1_0.py           # Orchestrates both stages
    ├── models_v1_0.py                        # Pydantic v2 models
    └── cache_integration_v1_0.py             # Cache management
```

## 📋 **Stage 1: Structure Discovery DSL v1.0**

### **structure_discovery_v1_0.yaml**
```yaml
version: "1.0"
description: "Generic structure discovery patterns - no provider names in processing code"

# Pattern definitions - referenced by hash, not provider name
structure_patterns:
  pattern_001:
    signature_fields: ["choices", "usage.prompt_tokens", "model"]
    optional_fields: ["id", "created", "system_fingerprint"]
    confidence_weight: 0.95
    
  pattern_002:
    signature_fields: ["content", "usage.input_tokens", "stop_reason"]
    optional_fields: ["id", "type", "role"]
    confidence_weight: 0.90
    
  pattern_003:
    signature_fields: ["candidates", "usageMetadata.promptTokenCount"]
    optional_fields: ["safetyRatings", "modelVersion"]
    confidence_weight: 0.85

# Navigation rules - generic path expressions
navigation_rules:
  message_content:
    rule_001:
      path_expression: "choices.*.message.content"
      pattern_match: "pattern_001"
      confidence: 0.95
      
    rule_002:
      path_expression: "content.*.text"
      pattern_match: "pattern_002"
      confidence: 0.90
      
    rule_003:
      path_expression: "candidates.*.content.parts.*.text"
      pattern_match: "pattern_003"
      confidence: 0.85

  token_usage:
    rule_001:
      prompt_tokens_path: "usage.prompt_tokens"
      completion_tokens_path: "usage.completion_tokens"
      pattern_match: "pattern_001"
      
    rule_002:
      prompt_tokens_path: "usage.input_tokens"
      completion_tokens_path: "usage.output_tokens"
      pattern_match: "pattern_002"
```

### **field_classification_v1_0.yaml**
```yaml
version: "1.0"
description: "Generic field type classification rules"

classification_rules:
  message_content:
    path_indicators:
      - "message.content"
      - "content.text"
      - "parts.text"
    content_validators:
      - type: "string"
      - min_length: 1
      - max_length: 100000
    context_clues:
      - adjacent_fields: ["role", "assistant", "user"]
    
  token_usage:
    path_indicators:
      - "usage"
      - "tokens"
      - "token_count"
    content_validators:
      - type: "integer"
      - min_value: 0
      - max_value: 1000000
    field_name_patterns:
      - "prompt_tokens"
      - "completion_tokens"
      - "input_tokens"
      - "output_tokens"
    
  model_identifier:
    path_indicators:
      - "model"
      - "model_name"
      - "modelId"
    content_validators:
      - type: "string"
      - contains_pattern: ["dash", "underscore", "colon"]
    prefix_patterns:
      - "gpt-"
      - "claude-"
      - "gemini-"
      - "llama-"
```

## 📋 **Stage 2: Convention Mapping DSL v1.0**

### **openinference_v0_1_15.yaml**
```yaml
version: "0.1.15"
convention_name: "openinference"
description: "OpenInference semantic convention mapping"

field_mappings:
  message_content:
    input_messages:
      target_attribute: "llm.input_messages"
      data_type: "array"
      structure:
        role: 
          source: "normalized_field.role"
          type: "string"
        content:
          source: "normalized_field.content"
          type: "string"
    
    output_messages:
      target_attribute: "llm.output_messages"
      data_type: "array"
      structure:
        role:
          value: "assistant"
          type: "string"
        content:
          source: "normalized_field.content"
          type: "string"

  token_usage:
    prompt_tokens:
      target_attribute: "llm.token_count_prompt"
      source: "normalized_usage.prompt_tokens"
      data_type: "integer"
      
    completion_tokens:
      target_attribute: "llm.token_count_completion"
      source: "normalized_usage.completion_tokens"
      data_type: "integer"

  model_info:
    model_name:
      target_attribute: "llm.model_name"
      source: "normalized_model.name"
      data_type: "string"
```

### **honeyhive_v1_0.yaml**
```yaml
version: "1.0"
convention_name: "honeyhive"
description: "HoneyHive unified schema mapping"

schema_sections:
  inputs:
    chat_history:
      source: "normalized_messages.conversation"
      data_type: "message_array"
      required: false
      
    system_prompt:
      source: "normalized_messages.system"
      data_type: "string"
      required: false

  outputs:
    content:
      source: "normalized_messages.assistant_content"
      data_type: "string"
      required: true
      
    tool_calls:
      source: "normalized_tool_calls.array"
      data_type: "tool_call_array"
      required: false
      
    finish_reason:
      source: "normalized_completion.finish_reason"
      data_type: "string"
      required: false

  config:
    model:
      source: "normalized_model.name"
      data_type: "string"
      required: true
      
    parameters:
      source: "normalized_config.parameters"
      data_type: "object"
      required: false

  metadata:
    usage:
      source: "normalized_usage"
      data_type: "usage_object"
      required: false
      
    processing_info:
      source: "processing_context.metrics"
      data_type: "metrics_object"
      required: false
```

## 🔧 **Generic Processing Implementation**

### **generic_discovery_engine_v1_0.py**
```python
"""
Generic Structure Discovery Engine v1.0
Zero provider-specific logic - all behavior from DSL
"""

from typing import Any, Dict, Optional
from .models_v1_0 import NormalizedFieldData, DiscoveryResult

class GenericDiscoveryEngine:
    """Completely generic discovery engine driven by DSL configuration."""
    
    def __init__(self, dsl_config: Dict[str, Any], cache_manager: Any):
        self.structure_patterns = dsl_config["structure_patterns"]
        self.navigation_rules = dsl_config["navigation_rules"]
        self.classification_rules = dsl_config["classification_rules"]
        self.cache = cache_manager.get_cache("structure_discovery")
    
    def discover_structure(self, raw_data: Dict[str, Any]) -> DiscoveryResult:
        """Generic structure discovery using DSL patterns."""
        # Step 1: Pattern matching (generic)
        matched_pattern = self._match_structure_pattern(raw_data)
        
        # Step 2: Field extraction (generic)
        extracted_fields = self._extract_fields_by_rules(raw_data, matched_pattern)
        
        # Step 3: Field classification (generic)
        classified_fields = self._classify_fields(extracted_fields)
        
        return DiscoveryResult(
            matched_pattern=matched_pattern,
            classified_fields=classified_fields,
            confidence=self._calculate_confidence(matched_pattern, classified_fields)
        )
    
    def _match_structure_pattern(self, data: Dict[str, Any]) -> Optional[str]:
        """Match structure pattern using DSL rules - no provider logic."""
        for pattern_id, pattern_config in self.structure_patterns.items():
            signature_fields = pattern_config["signature_fields"]
            
            # Generic field presence check
            matches = sum(1 for field in signature_fields if self._has_field_path(data, field))
            confidence = matches / len(signature_fields)
            
            if confidence >= pattern_config["confidence_weight"]:
                return pattern_id
        
        return None
    
    def _extract_fields_by_rules(self, data: Dict[str, Any], pattern_id: str) -> Dict[str, Any]:
        """Extract fields using navigation rules - completely generic."""
        extracted = {}
        
        for field_type, rules in self.navigation_rules.items():
            for rule_id, rule_config in rules.items():
                if rule_config["pattern_match"] == pattern_id:
                    path_expression = rule_config["path_expression"]
                    extracted_value = self._extract_by_path_expression(data, path_expression)
                    
                    if extracted_value:
                        extracted[field_type] = {
                            "value": extracted_value,
                            "rule_id": rule_id,
                            "confidence": rule_config["confidence"]
                        }
                        break
        
        return extracted
    
    def _extract_by_path_expression(self, data: Dict[str, Any], path_expression: str) -> Any:
        """Generic path expression evaluation."""
        # Handle wildcard paths like "choices.*.message.content"
        path_parts = path_expression.split(".")
        current = data
        
        for part in path_parts:
            if part == "*":
                # Handle array wildcard
                if isinstance(current, list) and len(current) > 0:
                    current = current[0]  # Take first element
                else:
                    return None
            else:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
        
        return current
    
    def _has_field_path(self, data: Dict[str, Any], field_path: str) -> bool:
        """Generic field path existence check."""
        return self._extract_by_path_expression(data, field_path) is not None
```

### **generic_mapping_engine_v1_0.py**
```python
"""
Generic Convention Mapping Engine v1.0
Zero convention-specific logic - all behavior from DSL
"""

from typing import Any, Dict
from .models_v1_0 import NormalizedFieldData, MappingResult

class GenericMappingEngine:
    """Completely generic mapping engine driven by DSL configuration."""
    
    def __init__(self, convention_dsl_config: Dict[str, Any], cache_manager: Any):
        self.convention_name = convention_dsl_config["convention_name"]
        self.field_mappings = convention_dsl_config.get("field_mappings", {})
        self.schema_sections = convention_dsl_config.get("schema_sections", {})
        self.cache = cache_manager.get_cache("convention_mapping")
    
    def map_to_convention(self, normalized_data: NormalizedFieldData) -> MappingResult:
        """Generic mapping using DSL rules - no convention logic."""
        if self.schema_sections:
            # HoneyHive-style section mapping
            return self._map_to_sections(normalized_data)
        else:
            # Flat attribute mapping (OpenInference, Traceloop, etc.)
            return self._map_to_attributes(normalized_data)
    
    def _map_to_sections(self, normalized_data: NormalizedFieldData) -> MappingResult:
        """Generic section-based mapping."""
        result = {}
        
        for section_name, section_config in self.schema_sections.items():
            result[section_name] = {}
            
            for field_name, field_config in section_config.items():
                source_path = field_config["source"]
                data_type = field_config["data_type"]
                
                # Generic source data extraction
                source_value = self._extract_from_normalized_data(normalized_data, source_path)
                
                if source_value is not None:
                    # Generic type conversion
                    converted_value = self._convert_data_type(source_value, data_type)
                    result[section_name][field_name] = converted_value
        
        return MappingResult(
            convention_name=self.convention_name,
            mapped_data=result,
            mapping_confidence=self._calculate_mapping_confidence(result)
        )
    
    def _map_to_attributes(self, normalized_data: NormalizedFieldData) -> MappingResult:
        """Generic attribute-based mapping."""
        result = {}
        
        for field_category, mappings in self.field_mappings.items():
            for mapping_name, mapping_config in mappings.items():
                target_attribute = mapping_config["target_attribute"]
                source_path = mapping_config.get("source")
                
                if source_path:
                    source_value = self._extract_from_normalized_data(normalized_data, source_path)
                    if source_value is not None:
                        data_type = mapping_config["data_type"]
                        converted_value = self._convert_data_type(source_value, data_type)
                        result[target_attribute] = converted_value
        
        return MappingResult(
            convention_name=self.convention_name,
            mapped_data=result,
            mapping_confidence=self._calculate_mapping_confidence(result)
        )
```

## ✅ **Key Improvements**

1. **Zero Provider Logic**: No "if provider == 'openai'" anywhere in code
2. **Proper Versioning**: All files have version numbers
3. **Generic Processing**: All logic driven by DSL configuration
4. **Single Responsibility**: Clear separation between discovery and mapping
5. **Maintainable**: Easy to reason about with clear file structure

The processing code is now completely generic and all provider/convention knowledge lives in versioned DSL files.
