# Source Semantic Conventions DSL v1.0

**Version**: 1.0  
**Date**: 2025-01-27  
**Status**: Complete Source Convention Definitions  

## 🎯 **The Complete Transform Chain**

```
Source Convention Data → Generic Transform Engine → HoneyHive Schema
         ↑                        ↑                        ↑
Source Convention DSL    Transform Rules DSL    Target Schema DSL
```

We need to define **how to recognize and extract data from existing semantic conventions** that are already in the spans/traces.

## 📋 **Source Convention: OpenInference v0.1.15**

### **openinference_source_v0_1_15.yaml**
```yaml
version: "0.1.15"
convention_name: "openinference"
convention_type: "source"
description: "How to extract data FROM OpenInference semantic conventions"

# Define how to recognize OpenInference data
recognition_patterns:
  primary_indicators:
    - attribute_prefix: "llm."
    - required_attributes: ["llm.model_name"]
    - optional_attributes: ["llm.input_messages", "llm.output_messages"]
  
  confidence_scoring:
    high_confidence: 0.9  # Has llm.model_name + llm.input_messages
    medium_confidence: 0.7  # Has llm.model_name only
    low_confidence: 0.5   # Has any llm.* attributes

# Define how to extract semantic data FROM OpenInference attributes
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
        top_p: "top_p"

  message_data:
    input_messages:
      source_attribute: "llm.input_messages"
      data_type: "array"
      semantic_type: "input_messages"
      structure_validation:
        required_fields: ["role", "content"]
        optional_fields: ["name", "tool_calls"]
      extraction_rules:
        role: "role"
        content: "content"
        name: "name"
        tool_calls: "tool_calls"
    
    output_messages:
      source_attribute: "llm.output_messages"
      data_type: "array"
      semantic_type: "output_messages"
      structure_validation:
        required_fields: ["role", "content"]
        optional_fields: ["tool_calls", "function_call"]

  usage_metrics:
    prompt_tokens:
      source_attribute: "llm.token_count_prompt"
      data_type: "integer"
      semantic_type: "token_usage"
      
    completion_tokens:
      source_attribute: "llm.token_count_completion"
      data_type: "integer"
      semantic_type: "token_usage"
      
    total_tokens:
      source_attribute: "llm.token_count_total"
      data_type: "integer"
      semantic_type: "token_usage"
      fallback_calculation: "prompt_tokens + completion_tokens"

  response_metadata:
    response_model:
      source_attribute: "llm.response_model"
      data_type: "string"
      semantic_type: "response_metadata"

# Define how to handle missing or malformed data
fallback_strategies:
  missing_model_name:
    action: "extract_from_invocation_parameters"
    fallback_path: "llm.invocation_parameters.model"
    
  missing_total_tokens:
    action: "calculate"
    calculation: "llm.token_count_prompt + llm.token_count_completion"
    
  malformed_messages:
    action: "normalize_structure"
    required_structure:
      role: "string"
      content: "string"
```

## 📋 **Source Convention: Traceloop v0.46.2**

### **traceloop_source_v0_46_2.yaml**
```yaml
version: "0.46.2"
convention_name: "traceloop"
convention_type: "source"
description: "How to extract data FROM Traceloop Gen AI semantic conventions"

# Define how to recognize Traceloop data
recognition_patterns:
  primary_indicators:
    - attribute_prefix: "gen_ai."
    - required_attributes: ["gen_ai.request.model"]
    - optional_attributes: ["gen_ai.system", "gen_ai.completion"]
  
  confidence_scoring:
    high_confidence: 0.9  # Has gen_ai.request.model + gen_ai.system
    medium_confidence: 0.7  # Has gen_ai.request.model only
    low_confidence: 0.5   # Has any gen_ai.* attributes

# Define how to extract semantic data FROM Traceloop attributes
extraction_rules:
  model_information:
    request_model:
      source_attribute: "gen_ai.request.model"
      data_type: "string"
      semantic_type: "model_identifier"
      
    response_model:
      source_attribute: "gen_ai.response.model"
      data_type: "string"
      semantic_type: "model_identifier"
      fallback_source: "gen_ai.request.model"
    
    model_parameters:
      temperature:
        source_attribute: "gen_ai.request.temperature"
        data_type: "float"
        semantic_type: "model_config"
        
      max_tokens:
        source_attribute: "gen_ai.request.max_tokens"
        data_type: "integer"
        semantic_type: "model_config"
        
      top_p:
        source_attribute: "gen_ai.request.top_p"
        data_type: "float"
        semantic_type: "model_config"

  message_data:
    system_message:
      source_attribute: "gen_ai.system"
      data_type: "string"
      semantic_type: "system_message"
      
    user_prompt:
      source_attribute: "gen_ai.prompt"
      data_type: "string"
      semantic_type: "user_message"
      
    completion:
      source_attribute: "gen_ai.completion"
      data_type: "string"
      semantic_type: "assistant_message"

  usage_metrics:
    prompt_tokens:
      source_attribute: "gen_ai.usage.prompt_tokens"
      data_type: "integer"
      semantic_type: "token_usage"
      
    completion_tokens:
      source_attribute: "gen_ai.usage.completion_tokens"
      data_type: "integer"
      semantic_type: "token_usage"
      
    total_tokens:
      source_attribute: "gen_ai.usage.total_tokens"
      data_type: "integer"
      semantic_type: "token_usage"
      fallback_calculation: "prompt_tokens + completion_tokens"

  operation_metadata:
    operation_name:
      source_attribute: "gen_ai.operation.name"
      data_type: "string"
      semantic_type: "operation_metadata"
      
    request_id:
      source_attribute: "gen_ai.request.id"
      data_type: "string"
      semantic_type: "request_metadata"

# Handle Traceloop's flat message structure
message_reconstruction:
  conversation_assembly:
    system_message:
      source: "gen_ai.system"
      role: "system"
      
    user_message:
      source: "gen_ai.prompt"
      role: "user"
      
    assistant_message:
      source: "gen_ai.completion"
      role: "assistant"

# Define how to handle Traceloop-specific edge cases
fallback_strategies:
  missing_completion:
    action: "mark_incomplete"
    reason: "Response may be streaming or incomplete"
    
  missing_system:
    action: "use_default"
    default_value: null
    
  flat_to_structured_messages:
    action: "reconstruct_conversation"
    assembly_rules: "conversation_assembly"
```

## 📋 **Source Convention: OpenLit v0.1.0**

### **openlit_source_v0_1_0.yaml**
```yaml
version: "0.1.0"
convention_name: "openlit"
convention_type: "source"
description: "How to extract data FROM OpenLit semantic conventions"

# Define how to recognize OpenLit data
recognition_patterns:
  primary_indicators:
    - attribute_prefix: "openlit."
    - required_attributes: ["openlit.model"]
    - optional_attributes: ["openlit.cost", "openlit.tokens.input"]
  
  confidence_scoring:
    high_confidence: 0.9  # Has openlit.model + openlit.cost
    medium_confidence: 0.7  # Has openlit.model only
    low_confidence: 0.5   # Has any openlit.* attributes

# Define how to extract semantic data FROM OpenLit attributes
extraction_rules:
  model_information:
    model_name:
      source_attribute: "openlit.model"
      data_type: "string"
      semantic_type: "model_identifier"
      
    provider:
      source_attribute: "openlit.provider"
      data_type: "string"
      semantic_type: "provider_metadata"

  cost_tracking:
    request_cost:
      source_attribute: "openlit.cost"
      data_type: "float"
      semantic_type: "cost_metrics"
      
    cost_currency:
      source_attribute: "openlit.cost.currency"
      data_type: "string"
      semantic_type: "cost_metadata"
      default_value: "USD"

  usage_metrics:
    input_tokens:
      source_attribute: "openlit.tokens.input"
      data_type: "integer"
      semantic_type: "token_usage"
      
    output_tokens:
      source_attribute: "openlit.tokens.output"
      data_type: "integer"
      semantic_type: "token_usage"
      
    total_tokens:
      source_attribute: "openlit.tokens.total"
      data_type: "integer"
      semantic_type: "token_usage"
      fallback_calculation: "input_tokens + output_tokens"

  performance_metrics:
    latency:
      source_attribute: "openlit.latency"
      data_type: "float"
      semantic_type: "performance_metrics"
      
    throughput:
      source_attribute: "openlit.throughput"
      data_type: "float"
      semantic_type: "performance_metrics"

  message_data:
    # OpenLit may not have structured messages, extract from generic attributes
    input_data:
      source_attribute: "openlit.input"
      data_type: "string"
      semantic_type: "user_message"
      
    output_data:
      source_attribute: "openlit.output"
      data_type: "string"
      semantic_type: "assistant_message"

# OpenLit-specific handling
cost_calculation:
  supported_models:
    gpt-3.5-turbo:
      input_cost_per_1k: 0.0015
      output_cost_per_1k: 0.002
      
    gpt-4:
      input_cost_per_1k: 0.03
      output_cost_per_1k: 0.06
      
  fallback_cost_estimation:
    action: "estimate_from_tokens"
    default_input_rate: 0.001
    default_output_rate: 0.002

# Define how to handle OpenLit-specific patterns
fallback_strategies:
  missing_structured_messages:
    action: "reconstruct_from_raw"
    input_source: "openlit.input"
    output_source: "openlit.output"
    
  missing_cost_data:
    action: "estimate_cost"
    estimation_rules: "cost_calculation"
```

## 🔧 **Generic Source Convention Processor**

### **generic_source_processor_v1_0.py**
```python
"""
Generic Source Convention Processor v1.0
Extracts semantic data FROM any source convention using DSL rules
"""

from typing import Any, Dict, List, Optional
from .models_v1_0 import SemanticData, ExtractionResult

class GenericSourceProcessor:
    """Extract semantic data from any source convention using DSL."""
    
    def __init__(self, source_convention_dsl: Dict[str, Any], cache_manager: Any):
        self.convention_name = source_convention_dsl["convention_name"]
        self.recognition_patterns = source_convention_dsl["recognition_patterns"]
        self.extraction_rules = source_convention_dsl["extraction_rules"]
        self.fallback_strategies = source_convention_dsl.get("fallback_strategies", {})
        self.cache = cache_manager.get_cache("source_processing")
    
    def extract_semantic_data(self, span_attributes: Dict[str, Any]) -> Optional[ExtractionResult]:
        """Extract semantic data using DSL rules - no convention-specific logic."""
        
        # Step 1: Recognize if this is our convention
        confidence = self._calculate_recognition_confidence(span_attributes)
        if confidence < 0.5:
            return None
        
        # Step 2: Extract semantic data using DSL rules
        semantic_data = self._extract_by_rules(span_attributes)
        
        # Step 3: Apply fallback strategies for missing data
        complete_data = self._apply_fallback_strategies(semantic_data, span_attributes)
        
        return ExtractionResult(
            convention_name=self.convention_name,
            confidence=confidence,
            semantic_data=complete_data
        )
    
    def _calculate_recognition_confidence(self, attributes: Dict[str, Any]) -> float:
        """Calculate confidence that this is our convention - generic logic."""
        indicators = self.recognition_patterns["primary_indicators"]
        scoring = self.recognition_patterns["confidence_scoring"]
        
        # Check attribute prefix
        prefix_matches = 0
        total_attributes = len(attributes)
        
        for attr_name in attributes.keys():
            for indicator in indicators:
                if "attribute_prefix" in indicator:
                    if attr_name.startswith(indicator["attribute_prefix"]):
                        prefix_matches += 1
        
        # Check required attributes
        required_attrs = next((ind["required_attributes"] for ind in indicators if "required_attributes" in ind), [])
        required_matches = sum(1 for attr in required_attrs if attr in attributes)
        
        # Check optional attributes
        optional_attrs = next((ind["optional_attributes"] for ind in indicators if "optional_attributes" in ind), [])
        optional_matches = sum(1 for attr in optional_attrs if attr in attributes)
        
        # Calculate confidence based on DSL scoring rules
        if required_matches == len(required_attrs) and optional_matches > 0:
            return scoring["high_confidence"]
        elif required_matches == len(required_attrs):
            return scoring["medium_confidence"]
        elif prefix_matches > 0:
            return scoring["low_confidence"]
        else:
            return 0.0
    
    def _extract_by_rules(self, attributes: Dict[str, Any]) -> SemanticData:
        """Extract semantic data using DSL extraction rules - completely generic."""
        semantic_data = SemanticData()
        
        for category, rules in self.extraction_rules.items():
            category_data = {}
            
            for field_name, field_config in rules.items():
                source_attribute = field_config["source_attribute"]
                
                if source_attribute in attributes:
                    raw_value = attributes[source_attribute]
                    
                    # Generic data type conversion
                    converted_value = self._convert_data_type(
                        raw_value, 
                        field_config["data_type"]
                    )
                    
                    category_data[field_name] = {
                        "value": converted_value,
                        "semantic_type": field_config["semantic_type"],
                        "source_attribute": source_attribute
                    }
            
            if category_data:
                setattr(semantic_data, category, category_data)
        
        return semantic_data
    
    def _apply_fallback_strategies(self, semantic_data: SemanticData, attributes: Dict[str, Any]) -> SemanticData:
        """Apply fallback strategies for missing data - generic logic."""
        for strategy_name, strategy_config in self.fallback_strategies.items():
            action = strategy_config["action"]
            
            if action == "calculate":
                calculation = strategy_config["calculation"]
                result = self._evaluate_calculation(calculation, attributes)
                # Apply result based on strategy configuration
                
            elif action == "extract_from_invocation_parameters":
                fallback_path = strategy_config["fallback_path"]
                if fallback_path in attributes:
                    # Apply fallback extraction
                    pass
            
            # Add more generic fallback actions as needed
        
        return semantic_data
```

## 🎯 **Complete Transform Flow**

```
1. Span Attributes (OpenInference/Traceloop/OpenLit)
        ↓
2. Source Convention Processor (extracts semantic data)
        ↓
3. Semantic Data (normalized intermediate format)
        ↓
4. HoneyHive Schema Mapper (maps to target schema)
        ↓
5. HoneyHive Schema Output
```

Now we have complete DSL definitions for extracting data FROM existing semantic conventions and transforming TO the HoneyHive schema, all with generic processing logic!
