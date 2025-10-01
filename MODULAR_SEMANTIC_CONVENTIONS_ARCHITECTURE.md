# Modular Semantic Conventions Architecture

**Version**: 1.0  
**Date**: September 25, 2025  
**Status**: Implementation Plan  

## 📋 Overview

This document describes the new modular architecture for HoneyHive's semantic convention processing system. The architecture replaces the monolithic `config_mapper.py` (1,850+ lines) with a clean, maintainable, and extensible modular system centered around the `CentralEventMapper`.

## 🎯 Architecture Goals

### Primary Objectives
- **Single Source of Truth**: `CentralEventMapper` as the unified interface
- **Modular Design**: Focused modules with single responsibilities
- **Configuration-Driven**: Pure configuration-based mapping without hardcoded logic
- **Performance**: Fast string operations, no regex overhead
- **Extensibility**: Easy addition of new semantic conventions
- **Maintainability**: Clean separation of concerns for team development

### Design Principles
1. **Event-Type Agnostic**: Logic works for model, chain, tool, and session events
2. **Provider Agnostic**: Supports any OpenTelemetry instrumentor
3. **Pure Configuration**: All mapping rules come from definition files
4. **Fast Operations**: Native Python string operations over regex
5. **Backward Compatible**: No breaking changes to existing functionality

## 🏗️ Architecture Overview

```
src/honeyhive/tracer/semantic_conventions/
├── central_mapper.py              # 🎯 Primary Interface
├── mapping/                       # 📦 Modular Components
│   ├── __init__.py               # Module exports
│   ├── rule_engine.py            # Rule creation & coordination
│   ├── transforms.py             # Data transformation functions
│   ├── patterns.py               # Pattern matching utilities
│   └── rule_applier.py           # Rule application logic
├── definitions/                   # 📋 Convention Definitions
│   ├── openinference_v0_1_31.py
│   ├── traceloop_v0_46_2.py
│   └── ...
├── discovery.py                   # 🔍 Convention Discovery
├── schema.py                      # 📊 HoneyHive Event Schema
└── __init__.py                    # Public API
```

## 🎯 Core Components

### 1. CentralEventMapper (Primary Interface)

**File**: `central_mapper.py`  
**Role**: Single entry point for all semantic convention processing

```python
class CentralEventMapper:
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.discovery = get_discovery_instance()
    
    def map_attributes_to_schema(
        self, 
        attributes: Dict[str, Any], 
        event_type: str
    ) -> Dict[str, Any]:
        """Main mapping method - replaces ConfigDrivenMapper"""
        # 1. Detect convention using discovery system
        convention = self.discovery.detect_convention(attributes)
        
        # 2. Apply dynamic rules using rule engine
        mapped_data = self.rule_engine.apply_rules(
            attributes, convention, event_type
        )
        
        # 3. Validate and normalize against schema
        return self.validate_and_normalize(mapped_data, event_type)
```

**Key Methods**:
- `map_attributes_to_schema()`: Primary mapping interface
- `validate_and_normalize()`: Schema validation and cleanup
- `create_base_event()`: Event structure creation
- `set_processing_markers()`: Backend compatibility markers

### 2. Rule Engine (Core Logic)

**File**: `mapping/rule_engine.py`  
**Role**: Dynamic rule creation and coordination

```python
class RuleEngine:
    def create_rules(self, definition: ConventionDefinition) -> List[MappingRule]:
        """Creates mapping rules dynamically from definition files"""
        
    def apply_rules(
        self, 
        attributes: Dict[str, Any], 
        convention: str, 
        event_type: str
    ) -> Dict[str, Any]:
        """Applies rules to transform attributes to HoneyHive schema"""
```

**Key Components**:
- `MappingRule`: Dataclass defining source→target mappings
- `create_dynamic_rules()`: Reads definition files to create rules
- `apply_rules()`: Coordinates rule application process
- Integration with discovery system for convention detection

### 3. Transform Functions (Data Processing)

**File**: `mapping/transforms.py`  
**Role**: All data transformation logic

```python
class TransformRegistry:
    def apply_transform(self, transform: str, value: Any) -> Any:
        """Apply named transform function to value"""
        
    # Transform Functions:
    def parse_openinference_messages(self, value: str) -> List[Dict]:
    def parse_traceloop_prompts(self, attrs: Dict) -> List[Dict]:
    def extract_traceloop_completion_content(self, attrs: Dict) -> str:
    def direct(self, value: Any) -> Any:
    # ... more transforms
```

**Transform Categories**:
- **Parsing**: Convert string representations to structured data
- **Extraction**: Pull specific values from complex structures
- **Normalization**: Standardize formats across conventions
- **Direct**: Pass-through for simple mappings

### 4. Pattern Matching (Utilities)

**File**: `mapping/patterns.py`  
**Role**: Fast, efficient pattern matching

```python
class PatternMatcher:
    def find_matching_attributes(
        self, 
        attributes: Dict[str, Any], 
        pattern: str
    ) -> Dict[str, Any]:
        """Fast string-based wildcard matching"""
```

**Pattern Types**:
- **Exact Match**: `"gen_ai.system"` → exact attribute name
- **Suffix Wildcard**: `"gen_ai.prompt.*"` → `startswith()` matching
- **Infix Wildcard**: `"gen_ai.completion.*.role"` → `startswith() + endswith()`
- **Performance**: Native Python string operations (no regex)

### 5. Rule Application (Execution)

**File**: `mapping/rule_applier.py`  
**Role**: Execute mapping rules on data

```python
class RuleApplier:
    def apply_input_mapping(self, result: Dict, attrs: Dict, rule: MappingRule):
    def apply_output_mapping(self, result: Dict, attrs: Dict, rule: MappingRule):
    def apply_config_mapping(self, result: Dict, attrs: Dict, rule: MappingRule):
    def apply_metadata_mapping(self, result: Dict, attrs: Dict, rule: MappingRule):
```

**Rule Application Flow**:
1. **Pattern Matching**: Find attributes matching rule pattern
2. **Transform Application**: Apply configured transform function
3. **Target Assignment**: Set result in appropriate schema section
4. **Error Handling**: Graceful failure with logging

## 📋 HoneyHive Semantic Convention DSL

### Overview

The HoneyHive Semantic Convention DSL (Domain Specific Language) is a declarative configuration format that allows developers to define how OpenTelemetry attributes from different instrumentors should be mapped to the canonical HoneyHive event schema. This DSL eliminates the need for hardcoded mapping logic and enables pure configuration-driven semantic convention processing.

### DSL Core Structure

Every semantic convention is defined using a standardized dictionary structure:

```python
CONVENTION_DEFINITION = {
    "provider": str,           # Provider name (e.g., "traceloop", "openinference")
    "version": str,            # Version string (e.g., "0.46.2")
    "detection_patterns": {},  # How to detect this convention
    "input_mapping": {},       # How to map inputs
    "output_mapping": {},      # How to map outputs  
    "config_mapping": {},      # How to map configuration
    "metadata_mapping": {}     # How to map metadata (optional)
}
```

### Pattern Syntax Reference

| Pattern Type | Syntax | Example | Matches |
|--------------|--------|---------|---------|
| **Exact Match** | `"attribute_name"` | `"gen_ai.system"` | Exactly `gen_ai.system` |
| **Suffix Wildcard** | `"prefix.*"` | `"gen_ai.prompt.*"` | `gen_ai.prompt.0.role`, `gen_ai.prompt.1.content` |
| **Infix Wildcard** | `"prefix.*.suffix"` | `"gen_ai.completion.*.role"` | `gen_ai.completion.0.role`, `gen_ai.completion.1.role` |

**Performance**: All patterns use fast Python string operations - no regex overhead.

### Transform Functions Reference

| Transform | Purpose | Input Example | Output Example |
|-----------|---------|---------------|----------------|
| `"direct"` | Pass-through | `"gpt-4o"` | `"gpt-4o"` |
| `"parse_openinference_messages"` | Parse JSON messages | `"[{\"role\":\"user\"}]"` | `[{"role":"user"}]` |
| `"parse_traceloop_prompts"` | Flattened→structured | `{"gen_ai.prompt.0.role":"user"}` | `[{"role":"user"}]` |
| `"extract_traceloop_completion_content"` | Extract content | `{"gen_ai.completion.0.content":"Hi"}` | `"Hi"` |

### Complete DSL Example

```python
CONVENTION_DEFINITION = {
    "provider": "traceloop",
    "version": "0.46.2",
    
    "detection_patterns": {
        "required_attributes": ["gen_ai.system"],
        "signature_attributes": ["llm.request.type"],
        "attribute_patterns": ["gen_ai.*", "llm.*"]
    },
    
    "input_mapping": {
        "target_schema": "chat_history",
        "mappings": {
            "gen_ai.prompt.*": {
                "target": "chat_history",
                "transform": "parse_traceloop_prompts",
                "description": "Convert flattened prompts to chat history"
            }
        }
    },
    
    "output_mapping": {
        "target_schema": "content_finish_reason_role",
        "mappings": {
            "gen_ai.completion.*": {
                "target": "content",
                "transform": "extract_traceloop_completion_content"
            },
            "gen_ai.completion.*.role": {
                "target": "role",
                "transform": "extract_traceloop_completion_role"
            }
        }
    },
    
    "config_mapping": {
        "mappings": {
            "gen_ai.system": {
                "target": "provider",
                "transform": "direct"
            },
            "gen_ai.request.model": {
                "target": "model",
                "transform": "direct"
            }
        }
    }
}
```

### Creating Custom Transforms

Add new transform functions to `mapping/transforms.py`:

```python
def custom_transform_name(self, value: Any, attributes: Dict = None) -> Any:
    """
    Custom transform function.
    
    Args:
        value: Raw attribute value or matched attributes dict
        attributes: Full span attributes for context
        
    Returns:
        Transformed value in target format
    """
    # Implementation here
    return transformed_value
```

### DSL Best Practices

1. **Naming**: Use `{provider}_v{major}_{minor}_{patch}.py` format
2. **Patterns**: Use suffix wildcards (`prefix.*`) for performance
3. **Transforms**: Use `direct` for simple pass-through, custom for complex logic
4. **Documentation**: Include clear descriptions for all mappings
5. **Testing**: Validate with sample data before deployment

## Configuration-Driven Mapping

### Definition File Structure

Each semantic convention is defined in a structured configuration file:

```python
# Example: traceloop_v0_46_2.py
CONVENTION_DEFINITION = {
    "provider": "traceloop",
    "version": "0.46.2",
    "detection_patterns": {
        "required_attributes": ["gen_ai.system"],
        "signature_attributes": ["llm.request.type"],
        "attribute_patterns": ["gen_ai.*", "llm.*"]
    },
    "input_mapping": {
        "target_schema": "chat_history",
        "mappings": {
            "gen_ai.prompt.*": {
                "target": "chat_history",
                "transform": "parse_traceloop_prompts",
                "description": "Convert Traceloop prompts to chat history"
            }
        }
    },
    "output_mapping": {
        "target_schema": "content_finish_reason_role",
        "mappings": {
            "gen_ai.completion.*": {
                "target": "content",
                "transform": "extract_traceloop_completion_content"
            },
            "gen_ai.completion.*.role": {
                "target": "role",
                "transform": "extract_traceloop_completion_role"
            },
            "gen_ai.completion.*.finish_reason": {
                "target": "finish_reason",
                "transform": "extract_traceloop_completion_finish_reason"
            }
        }
    },
    "config_mapping": {
        "mappings": {
            "gen_ai.system": {
                "target": "provider",
                "transform": "direct"
            },
            "gen_ai.request.model": {
                "target": "model",
                "transform": "direct"
            }
        }
    }
}
```

### Dynamic Rule Creation

The rule engine reads these definition files and creates `MappingRule` objects:

```python
@dataclass
class MappingRule:
    source_pattern: str      # "gen_ai.prompt.*"
    target_field: str        # "inputs"
    target_path: str         # "inputs.chat_history"
    transform: str           # "parse_traceloop_prompts"
```

## 🔄 Processing Flow

### 1. Span Interception
```
OpenTelemetry Span Creation
    ↓
Provider-Level Interception
    ↓
Pre-End Processing Hook
    ↓
CentralEventMapper.map_attributes_to_schema()
```

### 2. Semantic Convention Processing
```
Raw Span Attributes
    ↓
Convention Detection (discovery.py)
    ↓
Rule Creation (rule_engine.py)
    ↓
Pattern Matching (patterns.py)
    ↓
Transform Application (transforms.py)
    ↓
Rule Application (rule_applier.py)
    ↓
Schema Validation (central_mapper.py)
    ↓
HoneyHive Event Schema
```

### 3. Output Format
```json
{
  "inputs": {
    "chat_history": [
      {"role": "user", "content": "What is 2+2?"}
    ]
  },
  "outputs": {
    "content": "4",
    "role": "assistant",
    "finish_reason": "stop"
  },
  "config": {
    "model": "gpt-4o",
    "provider": "openai",
    "temperature": 0.1
  },
  "metadata": {
    "total_tokens": 50,
    "prompt_tokens": 10,
    "completion_tokens": 40
  }
}
```

## 🚀 Performance Characteristics

### Optimization Strategies
1. **String Operations**: Native Python `startswith()` and `endswith()` over regex
2. **Caching**: Convention detection and rule creation results cached
3. **Lazy Loading**: Modules loaded only when needed
4. **Minimal Allocations**: Reuse data structures where possible

### Benchmark Targets
- **Processing Latency**: < 1ms per span for semantic convention mapping
- **Memory Overhead**: < 5MB additional memory usage
- **Throughput**: Support 1000+ spans/second processing
- **Startup Time**: < 100ms for module initialization

## 🔌 Integration Points

### Provider Interception Integration
```python
# provider_interception.py
def _semantic_convention_processor(self, span: Span) -> None:
    # Get span attributes
    span_attributes = dict(getattr(span, 'attributes', {}))
    
    # Use CentralEventMapper instead of ConfigDrivenMapper
    event_data = central_mapper.map_attributes_to_schema(
        span_attributes, 
        event_type="model"
    )
    
    # Apply processed attributes back to span with JSON serialization
    self._apply_processed_attributes(span, event_data)
    
    # Set processing markers for backend
    span.set_attribute("honeyhive_processed", "true")
    span.set_attribute("honeyhive_schema_version", "1.0")
```

### Backend Compatibility
The system maintains full compatibility with the HoneyHive backend:

1. **Processing Markers**: Spans marked with `honeyhive_processed="true"`
2. **JSON Serialization**: Complex objects serialized as JSON strings for OTLP
3. **Schema Version**: `honeyhive_schema_version="1.0"` for backend validation
4. **Event Type**: `honeyhive_event_type` set for proper categorization

## 📊 Schema Mapping Examples

### Traceloop → HoneyHive Schema
```python
# Input: Traceloop attributes
{
    "gen_ai.prompt.0.role": "user",
    "gen_ai.prompt.0.content": "What is 2+2?",
    "gen_ai.completion.0.content": "4",
    "gen_ai.completion.0.role": "assistant",
    "gen_ai.completion.0.finish_reason": "stop",
    "gen_ai.system": "openai",
    "gen_ai.request.model": "gpt-4o"
}

# Output: HoneyHive schema
{
    "inputs": {
        "chat_history": [{"role": "user", "content": "What is 2+2?"}]
    },
    "outputs": {
        "content": "4",
        "role": "assistant", 
        "finish_reason": "stop"
    },
    "config": {
        "provider": "openai",
        "model": "gpt-4o"
    }
}
```

### OpenInference → HoneyHive Schema
```python
# Input: OpenInference attributes
{
    "llm.input_messages": "[{\"role\": \"user\", \"content\": \"Hello\"}]",
    "llm.output_messages": "[{\"role\": \"assistant\", \"content\": \"Hi!\"}]",
    "llm.model_name": "gpt-4o",
    "llm.provider": "openai"
}

# Output: HoneyHive schema
{
    "inputs": {
        "chat_history": [{"role": "user", "content": "Hello"}]
    },
    "outputs": {
        "content": "Hi!",
        "role": "assistant"
    },
    "config": {
        "model": "gpt-4o",
        "provider": "openai"
    }
}
```

## 🔧 Extension Guide

### Adding New Semantic Conventions

1. **Create Definition File**:
   ```python
   # definitions/new_provider_v1_0_0.py
   CONVENTION_DEFINITION = {
       "provider": "new_provider",
       "version": "1.0.0",
       "detection_patterns": {...},
       "input_mapping": {...},
       "output_mapping": {...},
       "config_mapping": {...}
   }
   ```

2. **Add Transform Functions** (if needed):
   ```python
   # mapping/transforms.py
   def parse_new_provider_format(self, value: str) -> List[Dict]:
       """Custom parsing for new provider format"""
       # Implementation here
   ```

3. **Test Integration**:
   - Convention detection works
   - Rules are created correctly
   - Mapping produces correct schema
   - Performance is acceptable

### Custom Transform Functions

Transform functions follow a simple interface:
```python
def transform_function_name(self, value: Any, attributes: Dict[str, Any] = None) -> Any:
    """
    Transform input value to target format.
    
    Args:
        value: The input value to transform
        attributes: Full attribute dictionary for context (optional)
        
    Returns:
        Transformed value in target format
    """
```

## 🧪 Testing Strategy

### Unit Testing Structure
```
tests/unit/semantic_conventions/
├── test_central_mapper.py         # CentralEventMapper tests
├── mapping/
│   ├── test_rule_engine.py        # Rule creation tests
│   ├── test_transforms.py         # Transform function tests
│   ├── test_patterns.py           # Pattern matching tests
│   └── test_rule_applier.py       # Rule application tests
└── test_integration.py            # End-to-end tests
```

### Integration Testing
- **Provider Compatibility**: Test with OpenInference, Traceloop, OpenLit
- **Performance Benchmarks**: Validate latency and memory usage
- **Schema Validation**: Ensure output matches HoneyHive schema
- **Backend Compatibility**: Verify processing markers and JSON serialization

## 📈 Migration Benefits

### Before (Monolithic)
- **Single File**: 1,850+ lines in `config_mapper.py`
- **Hardcoded Logic**: Provider-specific methods with string patterns
- **Difficult Testing**: Monolithic structure hard to unit test
- **Poor Maintainability**: Changes require understanding entire file
- **Performance Issues**: Regex usage and complex logic paths

### After (Modular)
- **Focused Modules**: 4-5 files with single responsibilities
- **Configuration-Driven**: All logic comes from definition files
- **Easy Testing**: Each module can be tested independently
- **Team Development**: Multiple developers can work on different aspects
- **Better Performance**: Fast string operations and optimized paths

## 🔮 Future Enhancements

### Planned Improvements
1. **Caching Layer**: Cache rule creation and convention detection
2. **Async Processing**: Support for async span processing
3. **Metrics Collection**: Built-in performance and usage metrics
4. **Schema Evolution**: Support for schema versioning and migration
5. **Visual Mapping**: UI for creating and editing convention definitions

### Extensibility Points
- **Custom Transforms**: Plugin system for custom transform functions
- **Schema Validation**: Pluggable schema validators
- **Processing Hooks**: Pre/post processing extension points
- **Convention Discovery**: Custom convention detection strategies

## 📚 References

### Related Documentation
- [HoneyHive Event Schema](./schema.py) - Canonical event structure
- [Convention Discovery](./discovery.py) - Dynamic convention detection
- [Provider Interception](../processing/provider_interception.py) - Span processing integration
- [Performance Benchmarks](../../scripts/tracer-performance-benchmark.py) - Performance testing

### External Standards
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [OpenInference Specification](https://github.com/Arize-ai/openinference)
- [Traceloop Documentation](https://github.com/traceloop/openllmetry)

## 📖 DSL Developer Guide

### Step-by-Step: Adding a New Semantic Convention

#### Step 1: Create Definition File
```bash
# Create new definition file
touch src/honeyhive/tracer/semantic_conventions/definitions/my_provider_v1_0_0.py
```

#### Step 2: Define Basic Structure
```python
# my_provider_v1_0_0.py
CONVENTION_DEFINITION = {
    "provider": "my_provider",
    "version": "1.0.0",
    "detection_patterns": {
        "required_attributes": ["my_provider.system"],
        "signature_attributes": ["my_provider.request_id"],
        "attribute_patterns": ["my_provider.*"]
    }
}
```

#### Step 3: Map Inputs
```python
"input_mapping": {
    "target_schema": "chat_history",  # or "messages", "prompt", etc.
    "mappings": {
        "my_provider.input.messages": {
            "target": "chat_history",
            "transform": "parse_my_provider_messages",  # Custom transform
            "description": "Convert provider-specific message format"
        }
    }
}
```

#### Step 4: Map Outputs  
```python
"output_mapping": {
    "target_schema": "content_finish_reason_role",
    "mappings": {
        "my_provider.output.text": {
            "target": "content",
            "transform": "direct",
            "description": "Response text content"
        },
        "my_provider.output.role": {
            "target": "role", 
            "transform": "direct",
            "description": "Response role (assistant/user/system)"
        }
    }
}
```

#### Step 5: Map Configuration
```python
"config_mapping": {
    "mappings": {
        "my_provider.model": {
            "target": "model",
            "transform": "direct"
        },
        "my_provider.temperature": {
            "target": "temperature", 
            "transform": "direct"
        }
    }
}
```

#### Step 6: Create Custom Transform (if needed)
```python
# In mapping/transforms.py
def parse_my_provider_messages(self, value: str) -> List[Dict]:
    """Parse my provider's message format."""
    try:
        # Custom parsing logic here
        if isinstance(value, str):
            return json.loads(value)
        return value
    except (json.JSONDecodeError, TypeError):
        return []
```

#### Step 7: Test the Definition
```python
# Test script
def test_my_provider():
    sample_attrs = {
        "my_provider.system": "openai",
        "my_provider.input.messages": "[{\"role\":\"user\",\"content\":\"Hi\"}]",
        "my_provider.output.text": "Hello!",
        "my_provider.output.role": "assistant",
        "my_provider.model": "gpt-4o"
    }
    
    result = central_mapper.map_attributes_to_schema(sample_attrs, "model")
    
    # Validate expected structure
    assert result["inputs"]["chat_history"][0]["content"] == "Hi"
    assert result["outputs"]["content"] == "Hello!"
    assert result["config"]["model"] == "gpt-4o"
```

### DSL Pattern Matching Examples

#### Simple Exact Matching
```python
# Pattern: "gen_ai.system"
# Matches: Only "gen_ai.system"
# Use case: Single configuration values

"gen_ai.system": {
    "target": "provider",
    "transform": "direct"
}
```

#### Suffix Wildcard Matching
```python
# Pattern: "gen_ai.prompt.*"  
# Matches: "gen_ai.prompt.0.role", "gen_ai.prompt.0.content", "gen_ai.prompt.1.role"
# Use case: Arrays of structured data

"gen_ai.prompt.*": {
    "target": "chat_history",
    "transform": "parse_traceloop_prompts"
}
```

#### Infix Wildcard Matching
```python
# Pattern: "gen_ai.completion.*.content"
# Matches: "gen_ai.completion.0.content", "gen_ai.completion.1.content"
# Use case: Specific fields from arrays

"gen_ai.completion.*.content": {
    "target": "content", 
    "transform": "extract_traceloop_completion_content"
}
```

### Transform Function Patterns

#### JSON String Parsing
```python
def parse_json_array(self, value: str) -> List[Dict]:
    """Parse JSON string to structured array."""
    try:
        if isinstance(value, str):
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else [parsed]
        return value if isinstance(value, list) else [value]
    except (json.JSONDecodeError, TypeError):
        return []
```

#### Flattened Attribute Aggregation
```python
def aggregate_flattened_messages(self, attributes: Dict[str, Any]) -> List[Dict]:
    """Convert flattened attributes to message array."""
    messages = {}
    
    for key, value in attributes.items():
        # Parse key like "provider.messages.0.role"
        parts = key.split('.')
        if len(parts) >= 4 and parts[1] == 'messages':
            index = int(parts[2])
            field = parts[3]
            
            if index not in messages:
                messages[index] = {}
            messages[index][field] = value
    
    # Return sorted by index
    return [messages[i] for i in sorted(messages.keys())]
```

#### Value Extraction
```python
def extract_first_value(self, attributes: Dict[str, Any]) -> str:
    """Extract first matching value from attribute dict."""
    for key, value in attributes.items():
        if value is not None:
            return str(value)
    return ""
```

### DSL Validation Checklist

Before deploying a new semantic convention definition:

#### ✅ Structure Validation
- [ ] All required sections present (`provider`, `version`, `detection_patterns`)
- [ ] Detection patterns include required and signature attributes
- [ ] Mapping sections follow correct structure
- [ ] Transform functions exist and are properly named

#### ✅ Pattern Validation  
- [ ] Source patterns use valid wildcard syntax
- [ ] Patterns are specific enough to avoid conflicts
- [ ] Performance-optimized patterns (suffix wildcards preferred)

#### ✅ Transform Validation
- [ ] All referenced transform functions exist
- [ ] Transform functions handle edge cases gracefully
- [ ] Custom transforms include proper error handling
- [ ] Transform outputs match expected target schema

#### ✅ Integration Testing
- [ ] Convention detection works with sample data
- [ ] Mapping produces correct HoneyHive schema structure
- [ ] No conflicts with existing conventions
- [ ] Performance impact is acceptable

#### ✅ Documentation
- [ ] Clear descriptions for all mappings
- [ ] Examples of input/output formats
- [ ] Transform function documentation
- [ ] Integration instructions

### Common DSL Patterns

#### Chat-Style Conversations
```python
"input_mapping": {
    "target_schema": "chat_history",
    "mappings": {
        "provider.messages.*": {
            "target": "chat_history",
            "transform": "parse_provider_messages"
        }
    }
},
"output_mapping": {
    "target_schema": "content_finish_reason_role", 
    "mappings": {
        "provider.response.content": {"target": "content", "transform": "direct"},
        "provider.response.role": {"target": "role", "transform": "direct"},
        "provider.response.finish_reason": {"target": "finish_reason", "transform": "direct"}
    }
}
```

#### Single Prompt/Response
```python
"input_mapping": {
    "target_schema": "prompt",
    "mappings": {
        "provider.prompt": {
            "target": "prompt",
            "transform": "direct"
        }
    }
},
"output_mapping": {
    "target_schema": "content",
    "mappings": {
        "provider.completion": {
            "target": "content", 
            "transform": "direct"
        }
    }
}
```

#### Function/Tool Calls
```python
"input_mapping": {
    "target_schema": "function_call",
    "mappings": {
        "provider.function.name": {"target": "name", "transform": "direct"},
        "provider.function.arguments": {"target": "arguments", "transform": "parse_json"}
    }
},
"output_mapping": {
    "target_schema": "function_result",
    "mappings": {
        "provider.function.result": {"target": "result", "transform": "direct"}
    }
}
```

---

**Document Status**: Implementation Plan  
**Next Review**: After Phase 6 completion  
**Maintainer**: HoneyHive SDK Team  
**Last Updated**: September 25, 2025
