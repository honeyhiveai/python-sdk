# Traceloop Migration Context - RC3 Semantic Convention Strategy

## 🔄 Critical Migration Context

### **Original Architecture:**
- **Old SDK**: Used Traceloop as the tracer implementation
- **Current Refactor**: Moving to native OpenTelemetry compliant configuration
- **RC3 Goal**: Support multiple semantic conventions including the old Traceloop patterns

## 🎯 Migration Implications for Semantic Convention Design

### **1. Traceloop Legacy Support**

Users migrating from the old SDK will have **existing Traceloop instrumentors** that generate `gen_ai.*` attributes:

```python
# Existing user setup (old SDK)
from traceloop.sdk import Traceloop
Traceloop.init()  # Generated gen_ai.* attributes

# New refactored SDK (RC3)
from honeyhive import HoneyHiveTracer
tracer = HoneyHiveTracer.init()  # Must handle gen_ai.* from existing instrumentors
```

### **2. BYOI Architecture Benefits**

The BYOI approach becomes even more critical for migration:

```python
# Users can keep existing Traceloop instrumentors
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.openai import OpenAIInstrumentor  # Traceloop

# New HoneyHive tracer with existing Traceloop instrumentor
tracer = HoneyHiveTracer.init(project="my-project")
openai_instrumentor = OpenAIInstrumentor()  # Still generates gen_ai.* attributes
openai_instrumentor.instrument(tracer_provider=tracer.provider)
```

### **3. Semantic Convention Priority Strategy**

Our priority order makes perfect sense for migration:

```python
CONVENTION_PRIORITY = [
    "honeyhive_native",  # New native HoneyHive attributes (highest)
    "traceloop",         # Existing gen_ai.* from old SDK (migration support)
    "openinference",     # Alternative instrumentor choice
    "openlit"            # Additional instrumentor support
]
```

## 🚀 Enhanced RC3 Strategy

### **Migration-Friendly Design**

```python
class TraceloopExtractor(BaseExtractor):
    """CRITICAL: Support existing Traceloop gen_ai.* patterns for migration"""
    
    def extract_config(self, attributes: dict) -> dict:
        """Extract Traceloop gen_ai.* config to HoneyHive schema"""
        config = {}
        
        # Traceloop model mapping
        if "gen_ai.request.model" in attributes:
            config["model"] = attributes["gen_ai.request.model"]
        
        # Traceloop provider mapping
        if "gen_ai.system" in attributes:
            config["provider"] = attributes["gen_ai.system"]
        
        # Traceloop temperature mapping
        if "gen_ai.request.temperature" in attributes:
            config["temperature"] = attributes["gen_ai.request.temperature"]
        
        return config
    
    def extract_inputs(self, attributes: dict) -> dict:
        """Extract Traceloop message format"""
        inputs = {}
        
        # Traceloop message pattern: gen_ai.request.messages.{index}.{field}
        messages = self._extract_traceloop_messages(attributes)
        if messages:
            inputs["chat_history"] = messages
        
        return inputs
    
    def extract_outputs(self, attributes: dict) -> dict:
        """Extract Traceloop response format"""
        outputs = {}
        
        # Traceloop response pattern
        if "gen_ai.response.model" in attributes:
            outputs["model"] = attributes["gen_ai.response.model"]
        
        # Extract response content
        response_content = self._extract_traceloop_response(attributes)
        if response_content:
            outputs["content"] = response_content
        
        return outputs
    
    def extract_metadata(self, attributes: dict) -> dict:
        """Extract Traceloop usage and metadata"""
        metadata = {}
        
        # Token usage (Traceloop pattern)
        if "gen_ai.usage.prompt_tokens" in attributes:
            metadata["usage"] = {
                "prompt_tokens": attributes["gen_ai.usage.prompt_tokens"],
                "completion_tokens": attributes.get("gen_ai.usage.completion_tokens", 0),
                "total_tokens": attributes.get("gen_ai.usage.total_tokens", 0)
            }
        
        return metadata
```

### **Migration Detection Logic**

```python
class SemanticConventionRegistry:
    def detect_primary_convention(self, attributes: dict) -> str:
        """Enhanced detection for migration scenarios"""
        
        # HoneyHive native (highest priority - new patterns)
        if any(key.startswith("honeyhive_") for key in attributes):
            return "honeyhive_native"
        
        # Traceloop (migration support - existing users)
        if any(key.startswith("gen_ai.") for key in attributes):
            if "gen_ai.usage.prompt_tokens" in attributes:
                return "traceloop"  # Classic Traceloop pattern
            elif "gen_ai.usage.input_tokens" in attributes:
                return "openlit"    # OpenLit variant
        
        # OpenInference (alternative choice)
        if any(key.startswith("llm.") for key in attributes):
            return "openinference"
        
        return "unknown"
```

## 🔄 Migration User Journey

### **Seamless Migration Path**

```python
# Step 1: User's existing setup (old SDK)
# from traceloop.sdk import Traceloop
# Traceloop.init()

# Step 2: Minimal migration (RC3)
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.openai import OpenAIInstrumentor  # Keep existing

tracer = HoneyHiveTracer.init(project="my-project")
instrumentor = OpenAIInstrumentor()  # Same Traceloop instrumentor
instrumentor.instrument(tracer_provider=tracer.provider)

# Result: Existing gen_ai.* attributes automatically converted to HoneyHive schema
```

### **Progressive Enhancement**

```python
# Step 3: Optional upgrade to OpenInference (later)
from openinference.instrumentation.openai import OpenAIInstrumentor  # New choice

# Step 4: Optional native HoneyHive patterns (advanced)
@trace(event_type=EventType.model)  # Native HoneyHive attributes
def my_function():
    pass
```

## 📋 Updated TODO Priorities for Migration

### **Critical Migration TODOs:**

1. **Enhanced Traceloop Support**: Comprehensive `gen_ai.*` attribute mapping
2. **Migration Documentation**: Clear upgrade path from old SDK
3. **Traceloop Message Parsing**: Handle `gen_ai.request.messages.{index}.{field}` pattern
4. **Usage Token Mapping**: Map Traceloop usage patterns to HoneyHive metadata
5. **Migration Testing**: Test with actual Traceloop instrumentor outputs

### **Migration-Specific Extractors:**

```python
# Priority order for migration support
self.extractors = {
    "honeyhive_native": HoneyHiveNativeExtractor(),     # New patterns
    "traceloop": TraceloopMigrationExtractor(),         # Migration support
    "openinference": OpenInferenceExtractor(),          # Alternative choice
    "openlit": OpenLitExtractor()                       # Additional support
}
```

## 💡 Key Migration Benefits

### **1. Zero Breaking Changes for Migration**
- Existing Traceloop instrumentors continue to work
- `gen_ai.*` attributes automatically converted
- No code changes required for basic migration

### **2. Progressive Enhancement**
- Users can migrate incrementally
- Keep existing instrumentors while adding new capabilities
- Gradual adoption of native HoneyHive patterns

### **3. Best of Both Worlds**
- **Migration support**: Handle existing Traceloop patterns
- **Future flexibility**: Support OpenInference, OpenLit, and native patterns
- **Performance**: Optimized processing for all convention types

## 🎯 RC3 Success Criteria (Migration-Focused)

1. **Seamless Traceloop Migration**: Existing `gen_ai.*` attributes work perfectly
2. **BYOI Flexibility**: Support multiple instrumentor choices
3. **Performance**: <100μs processing for all convention types
4. **Deep Research Prod Compatibility**: Generated events match expected format
5. **Migration Documentation**: Clear upgrade path and examples

This migration context makes our semantic convention architecture even more valuable - we're not just supporting multiple conventions, we're enabling a **seamless migration path** from the old Traceloop-based SDK to the new OpenTelemetry-compliant architecture!
