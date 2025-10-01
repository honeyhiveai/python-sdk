# HoneyHive Unified Schema Design: LLM-Neutral Observability

## Corrected Understanding

### HoneyHive's Role:
- ✅ **Primary observability platform** - not legacy
- ✅ **LLM-neutral provider** - supports all LLM providers and frameworks
- ✅ **Unified schema target** - normalize all semantic conventions into HoneyHive format
- ✅ **Multi-source ingestion** - OpenLLMetry, OpenInference, OpenLit, custom instrumentations

### Architecture Goal:
**All semantic conventions → HoneyHive unified schema**

```
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   OpenLLMetry   │───▶│                      │───▶│                     │
│  (gen_ai.*)     │    │                      │    │   HoneyHive         │
├─────────────────┤    │   Span Processor     │    │   Unified Schema    │
│  OpenInference  │───▶│   Dynamic Mapper     │───▶│                     │
│  (llm.*)        │    │                      │    │  • config           │
├─────────────────┤    │                      │    │  • inputs           │
│    OpenLit      │───▶│                      │    │  • outputs          │
│  (gen_ai.*)     │    │                      │    │  • metadata         │
├─────────────────┤    │                      │    │  • metrics          │
│   Custom/Other  │───▶│                      │    │  • feedback         │
│   Conventions   │    │                      │    │                     │
└─────────────────┘    └──────────────────────┘    └─────────────────────┘
```

## Unified Mapping Strategy

### 1. **HoneyHive Schema as Primary Target**

```python
# Target: HoneyHive unified event schema
HONEYHIVE_UNIFIED_SCHEMA = {
    "project_id": "string",
    "source": "string",
    "event_name": "string", 
    "event_type": "model|tool|chain|session",
    "event_id": "uuid",
    "session_id": "uuid",
    "parent_id": "uuid",
    "children_ids": ["uuid"],
    
    # Normalized configuration across all providers
    "config": {
        "provider": "OpenAI|Anthropic|Google|Cohere|...",
        "model": "gpt-4|claude-3|gemini-pro|...",
        "headers": "string",
        "is_streaming": "boolean",
        "temperature": "float",
        "max_tokens": "int",
        # ... other provider-agnostic config
    },
    
    # Structured inputs regardless of source format
    "inputs": {
        "chat_history": [
            {"role": "system|user|assistant", "content": "string"},
            {"role": "assistant", "content": "string", "tool_calls": [...]}
        ],
        "functions": [...],
        "prompt": "string",  # For non-chat models
        # ... other input types
    },
    
    # Structured outputs regardless of source format  
    "outputs": {
        "finish_reason": "stop|length|tool_calls|...",
        "role": "assistant",
        "content": "string",
        "tool_calls": [...],
        # ... other output types
    },
    
    # Rich metadata from instrumentation
    "metadata": {
        "instrumentation_scope": {"name": "string", "version": "string"},
        "llm_request_type": "chat|completion|embedding|...",
        "prompt_tokens": "int",
        "completion_tokens": "int", 
        "total_tokens": "int",
        "response_model": "string",
        "system_fingerprint": "string",
        "provider_specific": {...},  # Provider-specific metadata
        # ... other metadata
    },
    
    "start_time": "timestamp_ms",
    "end_time": "timestamp_ms", 
    "duration": "float_ms",
    "error": "string",
    "feedback": {},
    "metrics": {},
    "user_properties": {}
}
```

### 2. **Multi-Source Semantic Convention Mappers**

```python
class HoneyHiveUnifiedMapper:
    """Maps all semantic conventions to HoneyHive unified schema"""
    
    def __init__(self):
        self.mappers = {
            "openllmetry": OpenLLMetryMapper(),
            "openinference": OpenInferenceMapper(), 
            "openlit": OpenLitMapper(),
            "honeyhive_native": HoneyHiveNativeMapper(),
            "custom": CustomConventionMapper()
        }
        
        # Priority order for multi-convention scenarios
        self.priority_order = [
            "honeyhive_native",  # Highest priority - native HoneyHive attributes
            "openllmetry",       # Most common instrumentation
            "openinference",     # Arize/Phoenix ecosystem
            "openlit",           # OpenLit ecosystem
            "custom"             # Custom/unknown conventions
        ]
    
    def map_to_honeyhive_schema(self, attributes: dict) -> dict:
        """Convert any semantic convention to HoneyHive unified schema"""
        
        # Detect all present conventions
        detected_conventions = self._detect_all_conventions(attributes)
        
        # Initialize HoneyHive schema structure
        honeyhive_event = self._init_honeyhive_schema()
        
        # Apply mappers in priority order (later mappers can override earlier ones)
        for convention in self.priority_order:
            if convention in detected_conventions:
                mapper = self.mappers[convention]
                convention_data = mapper.extract_data(attributes)
                self._merge_into_honeyhive_schema(honeyhive_event, convention_data)
        
        return honeyhive_event
```

### 3. **Provider-Specific Mappers**

```python
class OpenLLMetryMapper:
    """Maps OpenLLMetry semantic conventions to HoneyHive schema"""
    
    def extract_data(self, attributes: dict) -> dict:
        return {
            "config": self._extract_config(attributes),
            "inputs": self._extract_inputs(attributes),
            "outputs": self._extract_outputs(attributes),
            "metadata": self._extract_metadata(attributes)
        }
    
    def _extract_config(self, attributes: dict) -> dict:
        """Extract provider-agnostic config from gen_ai.* attributes"""
        config = {}
        
        # Provider mapping
        if "gen_ai.system" in attributes:
            config["provider"] = attributes["gen_ai.system"]
        
        # Model mapping
        if "gen_ai.request.model" in attributes:
            config["model"] = attributes["gen_ai.request.model"]
        
        # Streaming flag
        if "gen_ai.request.streaming" in attributes:
            config["is_streaming"] = attributes["gen_ai.request.streaming"]
            
        # Temperature, max_tokens, etc.
        if "gen_ai.request.temperature" in attributes:
            config["temperature"] = attributes["gen_ai.request.temperature"]
            
        return config
    
    def _extract_inputs(self, attributes: dict) -> dict:
        """Extract structured inputs from gen_ai.request.messages.* pattern"""
        inputs = {}
        
        # Extract chat messages
        messages = self._extract_chat_messages(attributes)
        if messages:
            inputs["chat_history"] = messages
            
        # Extract functions/tools
        functions = self._extract_functions(attributes)
        if functions:
            inputs["functions"] = functions
            
        return inputs
    
    def _extract_chat_messages(self, attributes: dict) -> list:
        """Extract chat messages using native string operations"""
        messages = {}
        prefix = "gen_ai.request.messages."
        
        for key, value in attributes.items():
            if key.startswith(prefix):
                remainder = key[len(prefix):]
                dot_pos = remainder.find('.')
                
                if dot_pos != -1:
                    try:
                        index = int(remainder[:dot_pos])
                        field = remainder[dot_pos + 1:]
                        
                        if index not in messages:
                            messages[index] = {}
                            
                        # Handle nested tool_calls
                        if field.startswith("tool_calls."):
                            self._process_tool_call(messages[index], field, value)
                        else:
                            messages[index][field] = value
                            
                    except ValueError:
                        continue
        
        return [messages[i] for i in sorted(messages.keys())]

class OpenInferenceMapper:
    """Maps OpenInference semantic conventions to HoneyHive schema"""
    
    def extract_data(self, attributes: dict) -> dict:
        return {
            "config": {
                "provider": attributes.get("llm.provider"),
                "model": attributes.get("llm.model_name")
            },
            "inputs": self._extract_openinference_inputs(attributes),
            "outputs": self._extract_openinference_outputs(attributes),
            "metadata": {
                "prompt_tokens": attributes.get("llm.token_count.prompt"),
                "completion_tokens": attributes.get("llm.token_count.completion"),
                "total_tokens": attributes.get("llm.token_count.total")
            }
        }

class OpenLitMapper:
    """Maps OpenLit semantic conventions to HoneyHive schema"""
    
    def extract_data(self, attributes: dict) -> dict:
        return {
            "config": {
                "provider": attributes.get("gen_ai.system"),
                "model": attributes.get("gen_ai.request.model")
            },
            "metadata": {
                "prompt_tokens": attributes.get("gen_ai.usage.input_tokens"),
                "completion_tokens": attributes.get("gen_ai.usage.output_tokens")
            }
        }

class HoneyHiveNativeMapper:
    """Maps native HoneyHive attributes (highest priority)"""
    
    def extract_data(self, attributes: dict) -> dict:
        """Extract native honeyhive_* attributes"""
        data = {"config": {}, "inputs": {}, "outputs": {}, "metadata": {}}
        
        # Native HoneyHive attributes take precedence
        for key, value in attributes.items():
            if key.startswith("honeyhive_"):
                clean_key = key[10:]  # Remove "honeyhive_" prefix
                
                # Route to appropriate section
                if clean_key in ["provider", "model", "temperature", "max_tokens"]:
                    data["config"][clean_key] = value
                elif clean_key in ["inputs", "prompt", "messages"]:
                    data["inputs"][clean_key] = value
                elif clean_key in ["outputs", "response", "content"]:
                    data["outputs"][clean_key] = value
                else:
                    data["metadata"][clean_key] = value
        
        return data
```

### 4. **Convention Detection Strategy**

```python
def _detect_all_conventions(self, attributes: dict) -> set:
    """Detect all semantic conventions present in attributes"""
    conventions = set()
    
    # Check for OpenLLMetry
    if any(key.startswith("gen_ai.") for key in attributes):
        # Distinguish between OpenLLMetry and OpenLit
        if ("gen_ai.request.model" in attributes or 
            "gen_ai.usage.prompt_tokens" in attributes):
            conventions.add("openllmetry")
        elif ("gen_ai.usage.input_tokens" in attributes or
              "gen_ai.usage.output_tokens" in attributes):
            conventions.add("openlit")
    
    # Check for OpenInference
    if any(key.startswith("llm.") for key in attributes):
        conventions.add("openinference")
    
    # Check for native HoneyHive attributes
    if any(key.startswith("honeyhive_") for key in attributes):
        conventions.add("honeyhive_native")
    
    # Check for custom/unknown conventions
    known_prefixes = {"gen_ai.", "llm.", "honeyhive_", "traceloop."}
    if any(not any(key.startswith(prefix) for prefix in known_prefixes) 
           for key in attributes):
        conventions.add("custom")
    
    return conventions
```

### 5. **Intelligent Schema Merging**

```python
def _merge_into_honeyhive_schema(self, target: dict, source: dict):
    """Intelligently merge convention data into HoneyHive schema"""
    
    for section in ["config", "inputs", "outputs", "metadata"]:
        if section in source:
            for key, value in source[section].items():
                # Only set if not already present (priority order)
                if key not in target[section] and value is not None:
                    target[section][key] = value
                    
                # Special handling for arrays (merge instead of replace)
                elif key == "chat_history" and isinstance(value, list):
                    if key not in target[section]:
                        target[section][key] = value
                    else:
                        # Merge chat histories intelligently
                        target[section][key] = self._merge_chat_histories(
                            target[section][key], value
                        )
```

## Benefits of This Approach

### 1. **True LLM Neutrality**
- ✅ Supports **all major semantic conventions**
- ✅ **Provider-agnostic** unified schema
- ✅ **Future-proof** for new conventions
- ✅ **Extensible** for custom instrumentations

### 2. **Data Completeness**
- ✅ **Multi-source data fusion** - combine data from multiple conventions
- ✅ **Priority-based merging** - HoneyHive native > OpenLLMetry > others
- ✅ **Intelligent conflict resolution**
- ✅ **Rich metadata preservation**

### 3. **Performance Optimized**
- ✅ **Native string operations** only
- ✅ **Efficient convention detection**
- ✅ **Minimal allocations**
- ✅ **O(1) mapping lookups**

This positions HoneyHive as the **universal LLM observability platform** that can ingest and normalize data from any source into a unified, queryable schema.
