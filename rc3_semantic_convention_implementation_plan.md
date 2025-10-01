# RC3 Semantic Convention Implementation Plan
## Revised Based on Atomic Span Understanding

## 🎯 Corrected Architecture Understanding

### **Key Insight: Spans Are Atomic**
- **One span = One primary semantic convention**
- **BYOI creates span diversity**, not span complexity
- **Parent/child spans** processed independently with different conventions
- **Conflict resolution** only needed for attribute overlap within same convention

### **Real-World Scenario:**
```python
@trace(event_type=EventType.model, event_name="chat_completion")  # Parent span: HoneyHive native
def my_chat_function(prompt: str):
    response = openai_client.chat.completions.create(...)  # Child span: OpenInference
    return response

# Result: Two separate spans processed independently
# Span 1: honeyhive_* attributes → HoneyHive schema
# Span 2: llm.* attributes → HoneyHive schema
```

## 🏗️ Simplified Architecture Design

### **Core Components (Streamlined)**

```python
# 1. Convention Detection (Simple)
class SemanticConventionRegistry:
    def detect_primary_convention(self, attributes: dict) -> str:
        """Detect single primary convention per span"""
        if any(key.startswith("honeyhive_") for key in attributes):
            return "honeyhive_native"  # Highest priority
        elif any(key.startswith("llm.") for key in attributes):
            return "openinference"
        elif any(key.startswith("gen_ai.") for key in attributes):
            if "gen_ai.usage.input_tokens" in attributes:
                return "openlit"
            else:
                return "traceloop"
        else:
            return "unknown"

# 2. Single Convention Extraction
class SemanticConventionMapper:
    def convert_to_honeyhive_schema(self, span_data: SpanData) -> dict:
        """Simple single-convention processing"""
        
        # Detect primary convention
        primary_convention = self.registry.detect_primary_convention(span_data.attributes)
        
        # Use appropriate extractor
        extractor = self.extractors[primary_convention]
        honeyhive_event = extractor.extract_to_honeyhive_schema(span_data)
        
        # Add session context from tracer instance
        self._add_session_context(honeyhive_event, span_data)
        
        return honeyhive_event
```

### **Extractor Architecture (Clean)**

```python
class BaseExtractor:
    """Simple base class for single-convention extraction"""
    
    def extract_to_honeyhive_schema(self, span_data: SpanData) -> dict:
        """Extract from single convention to HoneyHive schema"""
        
        honeyhive_event = self._initialize_honeyhive_event(span_data)
        
        honeyhive_event["config"] = self.extract_config(span_data.attributes)
        honeyhive_event["inputs"] = self.extract_inputs(span_data.attributes)
        honeyhive_event["outputs"] = self.extract_outputs(span_data.attributes)
        honeyhive_event["metadata"] = self.extract_metadata(span_data.attributes)
        
        return honeyhive_event
    
    @abstractmethod
    def extract_config(self, attributes: dict) -> dict:
        """Extract config section"""
        
    @abstractmethod
    def extract_inputs(self, attributes: dict) -> dict:
        """Extract inputs section"""
        
    @abstractmethod
    def extract_outputs(self, attributes: dict) -> dict:
        """Extract outputs section"""
        
    @abstractmethod
    def extract_metadata(self, attributes: dict) -> dict:
        """Extract metadata section"""
```

## 📋 Revised TODO List (Simplified)

### **Phase 1: Core Architecture (10 TODOs)**

1. **Create semantic_conventions module** - Basic structure
2. **Implement BaseExtractor** - Simple abstract class
3. **Create HoneyHiveNativeExtractor** - Handle existing honeyhive_* attributes (HIGHEST PRIORITY)
4. **Create OpenInferenceExtractor** - Extract llm.* to HoneyHive schema
5. **Create TraceloopExtractor** - Extract gen_ai.* to HoneyHive schema  
6. **Create OpenLitExtractor** - Extract gen_ai.usage.input_tokens pattern
7. **Implement SemanticConventionRegistry** - Simple primary convention detection
8. **Create SemanticConventionMapper** - Single convention processing
9. **Implement chat message extraction** - Parse message arrays efficiently
10. **Add session context integration** - Tracer instance session handling

### **Phase 2: Integration & Export (6 TODOs)**

11. **Create exporters module** - Clean exporter interface
12. **Implement HoneyHiveExporter** - Handle client/OTLP modes
13. **Create SpanContextManager** - Extract baggage/experiment logic
14. **Refactor span_processor.__init__** - Dependency injection
15. **Refactor span_processor.on_end** - Delegate to semantic mapper
16. **Implement span data extraction** - ReadableSpan to SpanData conversion

### **Phase 3: Performance & Validation (6 TODOs)**

17. **Add performance optimization** - Native string operations for hot path
18. **Implement event validation** - Schema validation before export
19. **Add error handling** - Graceful degradation throughout
20. **Create performance benchmarks** - Ensure <100μs processing time
21. **Implement backward compatibility** - Preserve existing functionality
22. **Add feature flags** - Enable/disable semantic convention processing

### **Phase 4: Testing & Quality (6 TODOs)**

23. **Create unit tests for extractors** - Test each convention type
24. **Create unit tests for mapper** - Test convention detection and processing
25. **Create integration tests** - Compare with Deep Research Prod samples
26. **Test multi-instance scenarios** - Validate tracer isolation
27. **Test BYOI patterns** - Mixed instrumentor scenarios
28. **Performance validation** - Benchmark against current implementation

### **Phase 5: Release Preparation (6 TODOs)**

29. **Create documentation** - Architecture and usage examples
30. **Validate against Deep Research Prod** - Exact format matching
31. **Implement fallback patterns** - Handle unknown conventions
32. **Add convention version detection** - Future-proofing
33. **Create RC3 integration tests** - Comprehensive release testing
34. **Final RC3 validation** - Complete system validation

## 🔥 Critical Implementation Details

### **1. HoneyHive Native Priority (Preserved Functionality)**

```python
class HoneyHiveNativeExtractor(BaseExtractor):
    """HIGHEST PRIORITY: Preserve all existing functionality"""
    
    def extract_config(self, attributes: dict) -> dict:
        config = {}
        
        # Handle complex honeyhive_config attribute
        if "honeyhive_config" in attributes:
            config.update(attributes["honeyhive_config"])
        
        # Handle individual config attributes
        for key, value in attributes.items():
            if key.startswith("honeyhive_") and "_config" not in key:
                if key.endswith(("_model", "_provider", "_temperature", "_max_tokens")):
                    clean_key = key.replace("honeyhive_", "")
                    config[clean_key] = value
        
        return config
    
    def extract_inputs(self, attributes: dict) -> dict:
        # Handle honeyhive_inputs (existing functionality)
        return attributes.get("honeyhive_inputs", {})
    
    def extract_outputs(self, attributes: dict) -> dict:
        # Handle honeyhive_outputs (existing functionality)  
        return attributes.get("honeyhive_outputs", {})
```

### **2. OpenInference Extraction (New)**

```python
class OpenInferenceExtractor(BaseExtractor):
    """Extract OpenInference llm.* attributes to HoneyHive schema"""
    
    def extract_config(self, attributes: dict) -> dict:
        config = {}
        
        # Map OpenInference to HoneyHive config
        if "llm.model_name" in attributes:
            config["model"] = attributes["llm.model_name"]
        if "llm.provider" in attributes:
            config["provider"] = attributes["llm.provider"]
        if "llm.temperature" in attributes:
            config["temperature"] = attributes["llm.temperature"]
        
        return config
    
    def extract_inputs(self, attributes: dict) -> dict:
        inputs = {}
        
        # Extract chat messages from llm.input_messages
        if "llm.input_messages" in attributes:
            inputs["chat_history"] = self._parse_openinference_messages(
                attributes["llm.input_messages"]
            )
        
        return inputs
```

### **3. Multi-Instance Session Context**

```python
class SemanticConventionMapper:
    def __init__(self, tracer_instance=None):
        self.tracer_instance = tracer_instance  # Critical for session isolation
        self.registry = SemanticConventionRegistry()
        self.extractors = {
            "honeyhive_native": HoneyHiveNativeExtractor(),
            "openinference": OpenInferenceExtractor(),
            "traceloop": TraceloopExtractor(),
            "openlit": OpenLitExtractor()
        }
    
    def _add_session_context(self, honeyhive_event: dict, span_data: SpanData):
        """Add session context with tracer instance priority"""
        
        # Session ID: tracer instance takes priority over baggage
        session_id = None
        if self.tracer_instance and hasattr(self.tracer_instance, "session_id"):
            session_id = self.tracer_instance.session_id
        
        if not session_id:
            session_id = baggage.get_baggage("session_id")
        
        if session_id:
            honeyhive_event["session_id"] = session_id
```

## 🎯 Success Criteria (Simplified)

1. **Zero Breaking Changes**: All existing @trace functionality preserved
2. **Single Convention Processing**: Clean detection and extraction per span
3. **Multi-Instance Safety**: Tracer isolation maintained
4. **Performance**: <100μs per span processing
5. **Deep Research Prod Compatibility**: Generated events match expected format
6. **BYOI Support**: Handle OpenInference, Traceloop, OpenLit instrumentors

## 💡 Key Benefits of Simplified Approach

1. **Cleaner Architecture**: Single convention per span = simpler logic
2. **Better Performance**: No complex merging or conflict resolution
3. **Easier Testing**: Test each convention type independently
4. **Maintainable**: Clear separation of concerns
5. **Future-Proof**: Easy to add new conventions as single extractors

This simplified approach aligns with the atomic nature of spans and provides a much cleaner path to RC3 while preserving all existing functionality.
