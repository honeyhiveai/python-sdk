# Implementation Plan - Detailed DSL Design

## 1. DSL Configuration System Architecture

### 1.1 YAML-Based DSL Structure

The DSL system uses YAML configurations that compile into O(1) hash-based lookup tables. Each DSL file contains specific configuration aspects:

```yaml
# src/honeyhive/tracer/semantic_conventions/dsl/configs/field_discovery.yaml

# Field Discovery DSL - O(1) Classification Rules
field_discovery:
  version: "1.0"
  
  # O(1) classification using frozensets
  classification_rules:
    role_identifiers:
      type: "frozenset"
      description: "O(1) role classification using membership testing"
      values:
        - "user"
        - "assistant" 
        - "system"
        - "function"
        - "tool"
        - "model"
        - "human"
        - "ai"
    
    completion_statuses:
      type: "frozenset"
      description: "O(1) completion status classification"
      values:
        - "stop"
        - "length"
        - "tool_calls"
        - "content_filter"
        - "function_call"
        - "end_turn"
        - "max_tokens"
        - "stop_sequence"
        - "STOP"
        - "LENGTH"
        - "CONTENT_FILTER"
    
    token_indicators:
      type: "frozenset"
      description: "O(1) token-related field identification"
      values:
        - "tokens"
        - "token_count"
        - "usage"
        - "prompt_tokens"
        - "completion_tokens"
        - "total_tokens"
        - "input_tokens"
        - "output_tokens"
        - "cache_hit_tokens"
        - "cache_creation_tokens"
    
    model_prefixes:
      type: "tuple"
      description: "O(1) model identification using startswith"
      values:
        - "gpt-"
        - "claude-"
        - "gemini-"
        - "llama-"
        - "mistral-"
        - "titan-"
        - "nova-"
        - "anthropic-"
        - "openai-"
        - "cohere-"
        - "ai21-"
        - "meta-"
    
    api_id_prefixes:
      type: "tuple"
      description: "O(1) API identifier recognition"
      values:
        - "chatcmpl-"
        - "msg_"
        - "call_"
        - "toolu_"
        - "req_"
        - "resp_"
        - "run_"
        - "thread_"
        - "asst_"
  
  # O(1) path-based classification using dict lookups
  path_indicators:
    type: "dict"
    description: "O(1) field classification based on path components"
    mappings:
      "choices": "MESSAGE_CONTENT"
      "message": "MESSAGE_CONTENT"
      "content": "MESSAGE_CONTENT"
      "role": "MESSAGE_ROLE"
      "tool_calls": "TOOL_CALLS"
      "function_call": "FUNCTION_CALL"
      "refusal": "REFUSAL"
      "audio": "AUDIO"
      "usage": "USAGE_METRICS"
      "model": "MODEL_IDENTIFIER"
      "finish_reason": "COMPLETION_STATUS"
      "stop_reason": "COMPLETION_STATUS"
      "system_fingerprint": "PROVIDER_METADATA"
      "created": "PROVIDER_METADATA"
      "id": "PROVIDER_METADATA"
      "object": "PROVIDER_METADATA"
      "safety": "SAFETY_INFO"
      "safetyRatings": "SAFETY_INFO"
      "safetySettings": "SAFETY_INFO"
  
  # O(1) content-based classification rules
  content_classification:
    string_length_thresholds:
      message_content_min: 10
      message_content_max: 10000
      identifier_max: 100
    
    numeric_classification:
      token_count_indicators:
        - "positive_integer"
        - "range_0_to_1000000"
      
      confidence_score_indicators:
        - "float_0_to_1"
        - "percentage_0_to_100"

# Provider Detection DSL
provider_detection:
  version: "1.0"
  
  # O(1) provider signatures using frozensets
  signatures:
    openai:
      type: "frozenset"
      description: "OpenAI API signature fields"
      required_fields:
        - "choices"
        - "usage.prompt_tokens"
        - "usage.completion_tokens"
        - "model"
        - "created"
      optional_fields:
        - "system_fingerprint"
        - "usage.total_tokens"
        - "id"
        - "object"
      confidence_weights:
        required_match: 0.8
        optional_match: 0.2
    
    anthropic:
      type: "frozenset"
      description: "Anthropic Claude API signature"
      required_fields:
        - "content"
        - "usage.input_tokens"
        - "usage.output_tokens"
        - "stop_reason"
        - "type"
        - "model"
      optional_fields:
        - "role"
        - "id"
      confidence_weights:
        required_match: 0.9
        optional_match: 0.1
    
    gemini:
      type: "frozenset"
      description: "Google Gemini API signature"
      required_fields:
        - "candidates"
        - "usageMetadata.promptTokenCount"
        - "usageMetadata.candidatesTokenCount"
      optional_fields:
        - "safetyRatings"
        - "modelVersion"
      confidence_weights:
        required_match: 0.85
        optional_match: 0.15
    
    aws_bedrock:
      type: "frozenset"
      description: "AWS Bedrock API signature"
      required_fields:
        - "results"
        - "inputTextTokenCount"
        - "outputText"
        - "completionReason"
      optional_fields:
        - "modelId"
        - "inferenceConfig"
      confidence_weights:
        required_match: 0.8
        optional_match: 0.2
    
    traceloop:
      type: "frozenset"
      description: "Traceloop instrumentation signature"
      required_fields:
        - "gen_ai.request.model"
        - "gen_ai.usage.prompt_tokens"
        - "gen_ai.system"
      optional_fields:
        - "gen_ai.completion"
        - "gen_ai.request.temperature"
      confidence_weights:
        required_match: 0.9
        optional_match: 0.1
    
    openinference:
      type: "frozenset"
      description: "OpenInference instrumentation signature"
      required_fields:
        - "llm.input_messages"
        - "llm.output_messages"
        - "llm.token_count_prompt"
      optional_fields:
        - "llm.model_name"
        - "llm.temperature"
      confidence_weights:
        required_match: 0.85
        optional_match: 0.15
  
  # Detection thresholds
  confidence_thresholds:
    high_confidence: 0.8
    medium_confidence: 0.6
    low_confidence: 0.4
    unknown_threshold: 0.3
  
  # Fallback handling
  unknown_provider_handling:
    generate_name_from_fields: true
    max_unique_indicators: 5
    default_confidence: 0.3
    preserve_signature: true
```

### 1.2 Mapping Rules DSL

```yaml
# src/honeyhive/tracer/semantic_conventions/dsl/configs/mapping_rules.yaml

# HoneyHive Schema Mapping Rules
mapping_rules:
  version: "1.0"
  
  # O(1) field type to HoneyHive section mapping
  default_mappings:
    MESSAGE_ROLE:
      target_section: "inputs"
      target_field: "chat_history"
      transform: "extract_role"
      confidence: 0.95
    
    MESSAGE_CONTENT:
      target_section: "outputs"
      target_field: "content"
      transform: "extract_content"
      confidence: 0.95
    
    TOOL_CALLS:
      target_section: "outputs"
      target_field: "tool_calls"
      transform: "normalize_tool_calls"
      confidence: 0.9
    
    FUNCTION_CALL:
      target_section: "outputs"
      target_field: "function_call"
      transform: "normalize_function_call"
      confidence: 0.9
    
    REFUSAL:
      target_section: "outputs"
      target_field: "refusal"
      transform: "direct"
      confidence: 1.0
    
    AUDIO:
      target_section: "outputs"
      target_field: "audio"
      transform: "preserve_audio_metadata"
      confidence: 0.9
    
    TOKEN_COUNT:
      target_section: "metadata"
      target_field: "usage"
      transform: "extract_token_count"
      confidence: 0.95
    
    MODEL_IDENTIFIER:
      target_section: "config"
      target_field: "model"
      transform: "normalize_model_name"
      confidence: 0.95
    
    COMPLETION_STATUS:
      target_section: "outputs"
      target_field: "finish_reason"
      transform: "normalize_finish_reason"
      confidence: 0.9
    
    USAGE_METRICS:
      target_section: "metadata"
      target_field: "usage"
      transform: "extract_usage_metrics"
      confidence: 0.95
    
    CONFIGURATION:
      target_section: "config"
      target_field: "parameters"
      transform: "extract_config"
      confidence: 0.8
    
    SAFETY_INFO:
      target_section: "metadata"
      target_field: "safety"
      transform: "normalize_safety_info"
      confidence: 0.9
    
    PROVIDER_METADATA:
      target_section: "metadata"
      target_field: "provider"
      transform: "preserve_metadata"
      confidence: 0.8
    
    UNKNOWN:
      target_section: "metadata"
      target_field: "unknown_fields"
      transform: "preserve_unknown"
      confidence: 0.5
  
  # Provider-specific overrides
  provider_overrides:
    openai:
      COMPLETION_STATUS:
        target_section: "outputs"
        target_field: "finish_reason"
        transform: "map_openai_finish_reason"
        confidence: 0.95
      
      TOOL_CALLS:
        target_section: "outputs"
        target_field: "tool_calls"
        transform: "preserve_openai_tool_calls"
        confidence: 0.95
      
      MESSAGE_CONTENT:
        target_section: "outputs"
        target_field: "content"
        transform: "extract_openai_message_content"
        confidence: 0.95
    
    anthropic:
      COMPLETION_STATUS:
        target_section: "outputs"
        target_field: "finish_reason"
        transform: "map_anthropic_stop_reason"
        confidence: 0.95
      
      MESSAGE_CONTENT:
        target_section: "outputs"
        target_field: "content_blocks"
        transform: "preserve_anthropic_content"
        confidence: 0.95
      
      TOOL_CALLS:
        target_section: "outputs"
        target_field: "tool_use"
        transform: "normalize_anthropic_tool_use"
        confidence: 0.9
    
    gemini:
      SAFETY_INFO:
        target_section: "metadata"
        target_field: "safety_ratings"
        transform: "normalize_gemini_safety"
        confidence: 0.9
      
      MESSAGE_CONTENT:
        target_section: "outputs"
        target_field: "content"
        transform: "extract_gemini_text_from_parts"
        confidence: 0.9
      
      USAGE_METRICS:
        target_section: "metadata"
        target_field: "usage"
        transform: "normalize_gemini_usage"
        confidence: 0.9
    
    aws_bedrock:
      MESSAGE_CONTENT:
        target_section: "outputs"
        target_field: "outputText"
        transform: "extract_bedrock_output_text"
        confidence: 0.9
      
      USAGE_METRICS:
        target_section: "metadata"
        target_field: "usage"
        transform: "normalize_bedrock_usage"
        confidence: 0.9
      
      COMPLETION_STATUS:
        target_section: "outputs"
        target_field: "finish_reason"
        transform: "map_bedrock_completion_reason"
        confidence: 0.9
  
  # Fallback strategies
  fallback_handling:
    preserve_unmapped: true
    unmapped_section: "metadata"
    unmapped_field: "unknown_fields"
    confidence_threshold: 0.5
    max_unmapped_fields: 50
```

### 1.3 Transform Functions DSL

```yaml
# src/honeyhive/tracer/semantic_conventions/dsl/configs/transforms.yaml

# Transform Functions Configuration
transforms:
  version: "1.0"
  
  # O(1) transform function definitions
  functions:
    direct:
      type: "passthrough"
      description: "Direct value passthrough with no transformation"
      implementation: "lambda value: value"
      performance: "O(1)"
    
    extract_role:
      type: "string_extraction"
      description: "Extract role from message structure"
      implementation: |
        def extract_role(value):
            if isinstance(value, dict) and "role" in value:
                return value["role"].lower() if isinstance(value["role"], str) else str(value["role"])
            elif isinstance(value, str):
                return value.lower()
            else:
                return "unknown"
      performance: "O(1)"
    
    extract_content:
      type: "content_extraction"
      description: "Extract content from various message formats"
      implementation: |
        def extract_content(value):
            if isinstance(value, dict):
                if "content" in value:
                    return value["content"]
                elif "text" in value:
                    return value["text"]
                elif "message" in value:
                    return value["message"]
            elif isinstance(value, str):
                return value
            elif isinstance(value, list) and len(value) > 0:
                # Handle content arrays (like Gemini parts)
                if isinstance(value[0], dict) and "text" in value[0]:
                    return value[0]["text"]
            return str(value) if value is not None else ""
      performance: "O(1)"
    
    normalize_tool_calls:
      type: "structure_normalization"
      description: "Normalize tool calls to standard format"
      implementation: |
        def normalize_tool_calls(value):
            if not isinstance(value, list):
                return []
            
            normalized = []
            for tool_call in value[:10]:  # Limit to 10 for O(1) behavior
                if isinstance(tool_call, dict):
                    normalized_call = {
                        "id": tool_call.get("id", ""),
                        "type": tool_call.get("type", "function"),
                        "function": {
                            "name": tool_call.get("function", {}).get("name", ""),
                            "arguments": tool_call.get("function", {}).get("arguments", "{}")
                        }
                    }
                    normalized.append(normalized_call)
            return normalized
      performance: "O(1) - limited to 10 items"
    
    normalize_function_call:
      type: "structure_normalization"
      description: "Normalize legacy function call format"
      implementation: |
        def normalize_function_call(value):
            if isinstance(value, dict):
                return {
                    "name": value.get("name", ""),
                    "arguments": value.get("arguments", "{}")
                }
            return None
      performance: "O(1)"
    
    preserve_audio_metadata:
      type: "metadata_preservation"
      description: "Preserve audio metadata while extracting key info"
      implementation: |
        def preserve_audio_metadata(value):
            if isinstance(value, dict):
                return {
                    "id": value.get("id"),
                    "expires_at": value.get("expires_at"),
                    "data": "[AUDIO_DATA]",  # Don't store actual audio data
                    "transcript": value.get("transcript", "")
                }
            return value
      performance: "O(1)"
    
    extract_token_count:
      type: "numeric_extraction"
      description: "Extract token count from usage information"
      implementation: |
        def extract_token_count(value):
            if isinstance(value, (int, float)):
                return int(value)
            elif isinstance(value, dict):
                # Try common token count field names
                for field in ["total_tokens", "prompt_tokens", "completion_tokens", "input_tokens", "output_tokens"]:
                    if field in value and isinstance(value[field], (int, float)):
                        return int(value[field])
                return sum(v for v in value.values() if isinstance(v, (int, float)))
            return 0
      performance: "O(1)"
    
    normalize_model_name:
      type: "string_normalization"
      description: "Normalize model names to standard format"
      implementation: |
        def normalize_model_name(value):
            if isinstance(value, str):
                # O(1) normalization using string operations
                model = value.lower().strip()
                
                # Remove common prefixes/suffixes
                if model.startswith(("openai/", "anthropic/", "google/")):
                    model = model.split("/", 1)[1]
                
                # Normalize version patterns
                if "-" in model and model.split("-")[-1].replace(".", "").isdigit():
                    # Keep version info
                    return model
                
                return model
            return str(value) if value else "unknown"
      performance: "O(1)"
    
    normalize_finish_reason:
      type: "enum_normalization"
      description: "Normalize finish reasons to standard values"
      implementation: |
        def normalize_finish_reason(value):
            if isinstance(value, str):
                reason = value.lower().strip()
                
                # O(1) mapping using dict lookup
                reason_map = {
                    "stop": "stop",
                    "length": "length",
                    "tool_calls": "tool_calls",
                    "function_call": "function_call",
                    "content_filter": "content_filter",
                    "end_turn": "stop",
                    "max_tokens": "length",
                    "stop_sequence": "stop"
                }
                
                return reason_map.get(reason, reason)
            return str(value) if value else "unknown"
      performance: "O(1)"
    
    extract_usage_metrics:
      type: "metrics_extraction"
      description: "Extract comprehensive usage metrics"
      implementation: |
        def extract_usage_metrics(value):
            if isinstance(value, dict):
                metrics = {}
                
                # O(1) field extraction using direct key access
                field_mappings = {
                    "prompt_tokens": ["prompt_tokens", "input_tokens", "inputTextTokenCount"],
                    "completion_tokens": ["completion_tokens", "output_tokens", "outputTextTokenCount", "candidatesTokenCount"],
                    "total_tokens": ["total_tokens", "totalTokenCount"]
                }
                
                for target_field, source_fields in field_mappings.items():
                    for source_field in source_fields:
                        if source_field in value and isinstance(value[source_field], (int, float)):
                            metrics[target_field] = int(value[source_field])
                            break
                
                # Calculate total if not present
                if "total_tokens" not in metrics and "prompt_tokens" in metrics and "completion_tokens" in metrics:
                    metrics["total_tokens"] = metrics["prompt_tokens"] + metrics["completion_tokens"]
                
                return metrics
            elif isinstance(value, (int, float)):
                return {"total_tokens": int(value)}
            
            return {}
      performance: "O(1)"
    
    preserve_metadata:
      type: "metadata_preservation"
      description: "Preserve provider-specific metadata"
      implementation: |
        def preserve_metadata(value):
            if isinstance(value, dict):
                # Preserve important metadata fields only
                preserved = {}
                important_fields = {"id", "created", "system_fingerprint", "model", "object", "version"}
                
                for field in important_fields:
                    if field in value:
                        preserved[field] = value[field]
                
                return preserved
            return value
      performance: "O(1)"
    
    preserve_unknown:
      type: "unknown_preservation"
      description: "Preserve unknown fields for debugging"
      implementation: |
        def preserve_unknown(value):
            # Limit size to prevent memory issues
            if isinstance(value, str) and len(value) > 1000:
                return value[:1000] + "...[truncated]"
            elif isinstance(value, (list, dict)) and len(str(value)) > 1000:
                return f"[{type(value).__name__} - size: {len(value)}]"
            return value
      performance: "O(1)"
  
  # Provider-specific transform overrides
  provider_transforms:
    openai:
      map_openai_finish_reason:
        implementation: |
          def map_openai_finish_reason(value):
              openai_reasons = {
                  "stop": "stop",
                  "length": "length", 
                  "tool_calls": "tool_calls",
                  "content_filter": "content_filter",
                  "function_call": "function_call"
              }
              return openai_reasons.get(str(value).lower(), str(value))
        performance: "O(1)"
      
      preserve_openai_tool_calls:
        implementation: |
          def preserve_openai_tool_calls(value):
              # Preserve OpenAI's exact tool call format
              if isinstance(value, list):
                  return [
                      {
                          "id": call.get("id"),
                          "type": call.get("type", "function"),
                          "function": call.get("function", {})
                      }
                      for call in value[:10]  # Limit for O(1)
                  ]
              return value
        performance: "O(1)"
    
    anthropic:
      map_anthropic_stop_reason:
        implementation: |
          def map_anthropic_stop_reason(value):
              anthropic_reasons = {
                  "end_turn": "stop",
                  "max_tokens": "length",
                  "stop_sequence": "stop",
                  "tool_use": "tool_calls"
              }
              return anthropic_reasons.get(str(value).lower(), str(value))
        performance: "O(1)"
      
      normalize_anthropic_tool_use:
        implementation: |
          def normalize_anthropic_tool_use(value):
              if isinstance(value, list):
                  normalized = []
                  for item in value[:10]:  # Limit for O(1)
                      if isinstance(item, dict) and item.get("type") == "tool_use":
                          normalized.append({
                              "id": item.get("id"),
                              "type": "function",
                              "function": {
                                  "name": item.get("name"),
                                  "arguments": json.dumps(item.get("input", {}))
                              }
                          })
                  return normalized
              return value
        performance: "O(1)"
    
    gemini:
      extract_gemini_text_from_parts:
        implementation: |
          def extract_gemini_text_from_parts(value):
              if isinstance(value, list):
                  # Extract text from parts array
                  text_parts = []
                  for part in value[:5]:  # Limit for O(1)
                      if isinstance(part, dict) and "text" in part:
                          text_parts.append(part["text"])
                  return " ".join(text_parts)
              elif isinstance(value, dict) and "parts" in value:
                  return extract_gemini_text_from_parts(value["parts"])
              return str(value) if value else ""
        performance: "O(1)"
      
      normalize_gemini_safety:
        implementation: |
          def normalize_gemini_safety(value):
              if isinstance(value, list):
                  safety_info = {}
                  for rating in value[:10]:  # Limit for O(1)
                      if isinstance(rating, dict):
                          category = rating.get("category", "unknown")
                          probability = rating.get("probability", "unknown")
                          safety_info[category] = probability
                  return safety_info
              return value
        performance: "O(1)"
  
  # Performance validation
  performance_requirements:
    max_execution_time_ns: 1000000  # 1ms max per transform
    max_memory_usage_mb: 10
    o1_compliance_required: true
    forbidden_operations:
      - "regex"
      - "iteration_over_unknown_size"
      - "recursive_calls"
      - "network_requests"
      - "file_operations"
```

## 2. DSL Compiler Implementation

### 2.1 YAML to O(1) Hash Table Compiler

```python
# src/honeyhive/tracer/semantic_conventions/dsl/compiler.py

import yaml
import hashlib
from typing import Any, Dict, FrozenSet, Tuple, Callable, Optional
from pathlib import Path
import importlib.util
import time

class O1DSLCompiler:
    """Compile YAML DSL configurations into O(1) hash-based lookup tables."""
    
    def __init__(self, cache_manager: Any, tracer_instance: Any = None):
        self.tracer_instance = tracer_instance
        self.cache = cache_manager.get_cache("dsl_compiler")
        
        # Compilation results
        self.compiled_field_discovery: Optional[Dict[str, Any]] = None
        self.compiled_provider_detection: Optional[Dict[str, Any]] = None
        self.compiled_mapping_rules: Optional[Dict[str, Any]] = None
        self.compiled_transforms: Optional[Dict[str, Callable]] = None
        
        # Performance tracking
        self.compilation_stats = {
            "total_compilations": 0,
            "cache_hits": 0,
            "compilation_time_ns": 0,
            "config_files_loaded": 0
        }
    
    def compile_all_configs_o1(self, config_dir: Path) -> Dict[str, Any]:
        """Compile all DSL configurations with O(1) access patterns."""
        start_time = time.perf_counter_ns()
        
        # O(1) cache lookup for compiled configs
        config_hash = self._create_config_hash_o1(config_dir)
        cache_key = f"compiled_configs:{config_hash}"
        
        cached_result = self.cache.get(cache_key)
        if cached_result:
            self.compilation_stats["cache_hits"] += 1
            return cached_result
        
        # Compile each configuration type
        compiled_configs = {
            "field_discovery": self._compile_field_discovery_o1(config_dir / "field_discovery.yaml"),
            "provider_detection": self._compile_provider_detection_o1(config_dir / "provider_detection.yaml"),
            "mapping_rules": self._compile_mapping_rules_o1(config_dir / "mapping_rules.yaml"),
            "transforms": self._compile_transforms_o1(config_dir / "transforms.yaml")
        }
        
        # Cache compiled result
        compilation_time = time.perf_counter_ns() - start_time
        compiled_configs["_compilation_metadata"] = {
            "compilation_time_ns": compilation_time,
            "config_hash": config_hash,
            "tracer_instance": str(id(self.tracer_instance)) if self.tracer_instance else "default"
        }
        
        self.cache.set(cache_key, compiled_configs, ttl=3600.0)
        self.compilation_stats["total_compilations"] += 1
        self.compilation_stats["compilation_time_ns"] += compilation_time
        
        return compiled_configs
    
    def _compile_field_discovery_o1(self, config_file: Path) -> Dict[str, Any]:
        """Compile field discovery config into O(1) lookup structures."""
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        field_discovery = config["field_discovery"]
        classification_rules = field_discovery["classification_rules"]
        
        # Compile into O(1) structures
        compiled = {
            # O(1) frozenset lookups
            "role_identifiers": frozenset(classification_rules["role_identifiers"]["values"]),
            "completion_statuses": frozenset(classification_rules["completion_statuses"]["values"]),
            "token_indicators": frozenset(classification_rules["token_indicators"]["values"]),
            
            # O(1) tuple for startswith operations
            "model_prefixes": tuple(classification_rules["model_prefixes"]["values"]),
            "api_id_prefixes": tuple(classification_rules["api_id_prefixes"]["values"]),
            
            # O(1) dict lookup for path indicators
            "path_indicators": {
                path: getattr(FieldType, field_type)
                for path, field_type in field_discovery["path_indicators"]["mappings"].items()
            },
            
            # Content classification thresholds
            "content_thresholds": field_discovery["content_classification"]
        }
        
        return compiled
    
    def _compile_provider_detection_o1(self, config_file: Path) -> Dict[str, Any]:
        """Compile provider detection config into O(1) signature matching."""
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        provider_detection = config["provider_detection"]
        signatures = provider_detection["signatures"]
        
        # Compile provider signatures into O(1) frozensets
        compiled_signatures = {}
        for provider_name, signature_config in signatures.items():
            required_fields = frozenset(signature_config["required_fields"])
            optional_fields = frozenset(signature_config.get("optional_fields", []))
            
            compiled_signatures[provider_name] = {
                "required_fields": required_fields,
                "optional_fields": optional_fields,
                "all_fields": required_fields | optional_fields,
                "confidence_weights": signature_config["confidence_weights"]
            }
        
        compiled = {
            "provider_signatures": compiled_signatures,
            "confidence_thresholds": provider_detection["confidence_thresholds"],
            "unknown_handling": provider_detection["unknown_provider_handling"]
        }
        
        return compiled
    
    def _compile_mapping_rules_o1(self, config_file: Path) -> Dict[str, Any]:
        """Compile mapping rules into O(1) lookup tables."""
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        mapping_rules = config["mapping_rules"]
        
        # Compile default mappings into O(1) dict lookups
        default_mappings = {}
        for field_type_str, mapping_config in mapping_rules["default_mappings"].items():
            field_type = getattr(FieldType, field_type_str)
            default_mappings[field_type] = (
                mapping_config["target_section"],
                mapping_config["target_field"],
                mapping_config["transform"]
            )
        
        # Compile provider overrides
        provider_overrides = {}
        for provider_name, overrides in mapping_rules["provider_overrides"].items():
            provider_mappings = {}
            for field_type_str, mapping_config in overrides.items():
                field_type = getattr(FieldType, field_type_str)
                provider_mappings[field_type] = (
                    mapping_config["target_section"],
                    mapping_config["target_field"],
                    mapping_config["transform"]
                )
            provider_overrides[provider_name] = provider_mappings
        
        compiled = {
            "default_mappings": default_mappings,
            "provider_overrides": provider_overrides,
            "fallback_handling": mapping_rules["fallback_handling"]
        }
        
        return compiled
    
    def _compile_transforms_o1(self, config_file: Path) -> Dict[str, Callable]:
        """Compile transform functions into O(1) callable lookup table."""
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        transforms_config = config["transforms"]
        functions = transforms_config["functions"]
        
        # Compile transform functions
        compiled_transforms = {}
        
        for function_name, function_config in functions.items():
            if function_config["type"] == "passthrough":
                compiled_transforms[function_name] = lambda x: x
            else:
                # Compile the function implementation
                implementation = function_config["implementation"]
                
                # Create function from string implementation
                if implementation.startswith("lambda"):
                    # Simple lambda function
                    compiled_transforms[function_name] = eval(implementation)
                else:
                    # Multi-line function definition
                    exec(implementation)
                    # Extract the function from local scope
                    func_name = implementation.split("def ")[1].split("(")[0].strip()
                    compiled_transforms[function_name] = locals()[func_name]
        
        # Add provider-specific transforms
        if "provider_transforms" in transforms_config:
            for provider_name, provider_funcs in transforms_config["provider_transforms"].items():
                for func_name, func_config in provider_funcs.items():
                    implementation = func_config["implementation"]
                    exec(implementation)
                    func_name_clean = implementation.split("def ")[1].split("(")[0].strip()
                    compiled_transforms[func_name] = locals()[func_name_clean]
        
        return compiled_transforms
    
    def _create_config_hash_o1(self, config_dir: Path) -> str:
        """Create O(1) hash of configuration directory for caching."""
        # O(1) hash using directory metadata
        config_files = ["field_discovery.yaml", "mapping_rules.yaml", "transforms.yaml"]
        
        hash_input = ""
        for config_file in config_files:
            file_path = config_dir / config_file
            if file_path.exists():
                stat = file_path.stat()
                hash_input += f"{config_file}:{stat.st_mtime}:{stat.st_size}:"
        
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]
    
    def validate_o1_compliance(self, compiled_configs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that compiled configurations maintain O(1) performance."""
        validation_results = {
            "is_o1_compliant": True,
            "warnings": [],
            "performance_metrics": {}
        }
        
        # Check data structure types for O(1) compliance
        field_discovery = compiled_configs["field_discovery"]
        
        # Validate frozenset usage
        for key, value in field_discovery.items():
            if key.endswith("_identifiers") or key.endswith("_statuses") or key.endswith("_indicators"):
                if not isinstance(value, frozenset):
                    validation_results["warnings"].append(f"Non-frozenset found: {key} should be frozenset for O(1) membership testing")
                    validation_results["is_o1_compliant"] = False
        
        # Validate tuple usage for startswith operations
        for key, value in field_discovery.items():
            if key.endswith("_prefixes"):
                if not isinstance(value, tuple):
                    validation_results["warnings"].append(f"Non-tuple found: {key} should be tuple for O(1) startswith operations")
                    validation_results["is_o1_compliant"] = False
        
        # Validate dict usage for lookups
        if "path_indicators" in field_discovery:
            if not isinstance(field_discovery["path_indicators"], dict):
                validation_results["warnings"].append("path_indicators should be dict for O(1) lookups")
                validation_results["is_o1_compliant"] = False
        
        return validation_results
```

## 3. DSL Integration with Existing Codebase

### 3.1 DSL Loader with Cache Integration

```python
# src/honeyhive/tracer/semantic_conventions/dsl/loader.py

from pathlib import Path
from typing import Any, Dict, Optional
import time
from .compiler import O1DSLCompiler
from .validator import DSLValidator

class DSLConfigLoader:
    """Load and manage DSL configurations with per-tracer-instance caching."""
    
    def __init__(self, cache_manager: Any, tracer_instance: Any = None):
        self.tracer_instance = tracer_instance
        self.cache = cache_manager.get_cache("dsl_loader")
        
        # Initialize components
        self.compiler = O1DSLCompiler(cache_manager, tracer_instance)
        self.validator = DSLValidator(cache_manager, tracer_instance)
        
        # Configuration state
        self.loaded_configs: Optional[Dict[str, Any]] = None
        self.config_version: Optional[str] = None
        
        # Performance tracking
        self.load_stats = {
            "total_loads": 0,
            "cache_hits": 0,
            "validation_time_ns": 0,
            "compilation_time_ns": 0
        }
    
    def load_bundled_configs_o1(self) -> Dict[str, Any]:
        """Load bundled DSL configurations with O(1) caching."""
        start_time = time.perf_counter_ns()
        
        # Get bundled config directory
        config_dir = Path(__file__).parent / "configs"
        
        # O(1) cache lookup
        cache_key = f"bundled_configs:{self.tracer_instance}"
        cached_configs = self.cache.get(cache_key)
        
        if cached_configs and self._is_config_current(cached_configs, config_dir):
            self.load_stats["cache_hits"] += 1
            self.loaded_configs = cached_configs
            return cached_configs
        
        # Load and validate configurations
        validation_start = time.perf_counter_ns()
        validation_result = self.validator.validate_all_configs(config_dir)
        validation_time = time.perf_counter_ns() - validation_start
        
        if not validation_result["is_valid"]:
            raise ValueError(f"DSL configuration validation failed: {validation_result['errors']}")
        
        # Compile configurations
        compilation_start = time.perf_counter_ns()
        compiled_configs = self.compiler.compile_all_configs_o1(config_dir)
        compilation_time = time.perf_counter_ns() - compilation_start
        
        # Add metadata
        compiled_configs["_loader_metadata"] = {
            "load_time_ns": time.perf_counter_ns() - start_time,
            "validation_time_ns": validation_time,
            "compilation_time_ns": compilation_time,
            "config_version": self._get_config_version(config_dir),
            "tracer_instance": str(id(self.tracer_instance)) if self.tracer_instance else "default"
        }
        
        # Cache compiled configurations
        self.cache.set(cache_key, compiled_configs, ttl=3600.0)
        
        # Update stats
        self.load_stats["total_loads"] += 1
        self.load_stats["validation_time_ns"] += validation_time
        self.load_stats["compilation_time_ns"] += compilation_time
        
        self.loaded_configs = compiled_configs
        return compiled_configs
    
    def get_field_discovery_config_o1(self) -> Dict[str, Any]:
        """Get field discovery configuration with O(1) access."""
        if not self.loaded_configs:
            self.load_bundled_configs_o1()
        
        return self.loaded_configs["field_discovery"]
    
    def get_provider_detection_config_o1(self) -> Dict[str, Any]:
        """Get provider detection configuration with O(1) access."""
        if not self.loaded_configs:
            self.load_bundled_configs_o1()
        
        return self.loaded_configs["provider_detection"]
    
    def get_mapping_rules_config_o1(self) -> Dict[str, Any]:
        """Get mapping rules configuration with O(1) access."""
        if not self.loaded_configs:
            self.load_bundled_configs_o1()
        
        return self.loaded_configs["mapping_rules"]
    
    def get_transform_functions_o1(self) -> Dict[str, Any]:
        """Get transform functions with O(1) access."""
        if not self.loaded_configs:
            self.load_bundled_configs_o1()
        
        return self.loaded_configs["transforms"]
    
    def _is_config_current(self, cached_configs: Dict[str, Any], config_dir: Path) -> bool:
        """Check if cached configuration is current using O(1) operations."""
        if "_loader_metadata" not in cached_configs:
            return False
        
        cached_version = cached_configs["_loader_metadata"].get("config_version")
        current_version = self._get_config_version(config_dir)
        
        return cached_version == current_version
    
    def _get_config_version(self, config_dir: Path) -> str:
        """Get configuration version using O(1) file metadata."""
        version_parts = []
        
        config_files = ["field_discovery.yaml", "mapping_rules.yaml", "transforms.yaml"]
        for config_file in config_files:
            file_path = config_dir / config_file
            if file_path.exists():
                stat = file_path.stat()
                version_parts.append(f"{stat.st_mtime}:{stat.st_size}")
        
        return ":".join(version_parts)
```

This comprehensive DSL design provides:

1. **O(1) Performance**: All lookups use frozensets, tuples, and dicts for constant-time operations
2. **Native Python Operations**: No regex, only startswith, in, len, and dict lookups
3. **Multi-Instance Support**: Integrates with existing cache manager per tracer instance
4. **Comprehensive Coverage**: Handles all discovered LLM provider patterns
5. **Extensibility**: Easy to add new providers and transforms via YAML
6. **Performance Validation**: Built-in O(1) compliance checking
7. **Caching**: Aggressive caching at every level for maximum performance

The DSL system compiles YAML configurations into optimized Python data structures that maintain O(1) performance characteristics while providing complete flexibility for handling any LLM provider's response format.
