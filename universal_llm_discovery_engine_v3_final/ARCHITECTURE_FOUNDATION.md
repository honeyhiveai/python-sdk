# Universal LLM Discovery Engine - Architecture Foundation

**Version**: 3.0 Final  
**Date**: 2025-01-27  
**Status**: Implementation Ready  
**Purpose**: Single source of truth for all architectural decisions

---

## 🎯 **Core Problem Statement**

Build a Universal LLM Discovery Engine that **neutrally supports any instrumentor/non-instrumentor integration** and maps span data to the HoneyHive schema/semantic convention for ingestion into the HoneyHive backend.

### **The Evolution of Requirements**

**Original Goal**: Support any instrumentor integration and map span data to HoneyHive schema

**Critical Discovery**: The `_normalize_message` function revealed that semantic convention handling alone is insufficient. We need **rich dynamic handling of LLM response data** embedded within span attributes to properly map complex, nested LLM provider responses.

### **What This System Provides**

1. **Universal Instrumentor Support**: Handle any instrumentor (OpenInference, Traceloop, OpenLit) or direct SDK usage
2. **HoneyHive Schema Mapping**: Convert all span data to HoneyHive's unified schema for backend ingestion
3. **Dynamic LLM Response Processing**: Handle complex, nested LLM provider response objects within semantic convention attributes
4. **Package-Based Detection**: Use Python package inspection for instrumentor detection
5. **O(1 Performance**: All operations constant time with hash-based lookups

## 🏗️ **Definitive Architecture**

### **Processing Pipeline (DSL-Driven)**

```
┌─────────────────────────────────────────────────────────────┐
│                 Stage 1: Instrumentor Detection            │
│                                                             │
│  Package Detection → Instrumentor Mapping DSL → Convention │
│                                                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Stage 2: Two-Level Data Processing            │
│                                                             │
│  Top Level: Source Convention DSL (semantic attributes)    │
│  Nested Level: Structure Discovery DSL (LLM responses)     │
│                                                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│               Stage 3: Universal Mapping                   │
│                                                             │
│  Target Schema DSL + Transform Rules DSL → HoneyHive       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **Five DSL Types (Definitive)**

1. **Instrumentor Mapping DSL**: Maps installed instrumentor packages to semantic convention versions using package detection
2. **Source Convention DSL**: Extracts data from semantic convention attributes at the top level of span data
3. **Structure Discovery DSL**: Dynamically analyzes raw LLM provider response objects nested within semantic attributes
4. **Target Schema DSL**: Defines HoneyHive schema structure and mapping rules
5. **Transform Rules DSL**: Defines transformation functions and data type conversions

## 📁 **Final File Structure**

```
src/honeyhive/tracer/processing/semantic_conventions/
├── __init__.py
├── universal_processor.py                    # Main orchestrator
├── models.py                                # Pydantic v2 models
│
├── config/                                  # Centralized configuration
│   ├── __init__.py
│   ├── dsl/
│   │   ├── instrumentor_mappings.yaml       # Agent OS integration
│   │   ├── structure_discovery.yaml         # LLM response analysis
│   │   ├── source_conventions/
│   │   │   ├── openinference_v0_1_15.yaml   # OpenInference extraction
│   │   │   ├── traceloop_v0_46_2.yaml       # Traceloop extraction
│   │   │   └── openlit_v0_1_0.yaml          # OpenLit extraction
│   │   ├── target_schemas/
│   │   │   └── honeyhive.yaml               # HoneyHive schema
│   │   └── transforms/
│   │       └── transform_rules.yaml         # Transform functions
│   └── loader.py                           # Centralized config loader
│
├── engines/                                # Processing engines
│   ├── __init__.py
│   ├── instrumentor_detector.py            # Agent OS integration
│   ├── source_processor.py                # Extract from semantic conventions
│   ├── structure_discovery.py             # Analyze LLM response objects
│   ├── target_mapper.py                   # Map to target schemas
│   └── transform_engine.py               # Execute transform functions
│
├── dsl_compiler/                          # DSL compilation
│   ├── __init__.py
│   ├── compiler.py                        # Compile DSL to O(1) structures
│   └── validator.py                       # Validate DSL syntax/semantics
│
└── integration/                           # Backward compatibility
    ├── __init__.py
    ├── compatibility_layer.py             # Backward compatibility
    └── migration_utilities.py             # Migration from current implementation
```

## 🔧 **Processing Flow Details**

### **Stage 1: Package-Based Instrumentor Detection**

```python
# Use Python package inspection to determine semantic convention
instrumentor_info = instrumentor_detector.detect_active_instrumentors()
# Result: {"openinference-instrumentation-openai": {"convention": "openinference", "version": "0.1.15"}}
```

### **Stage 2: Two-Level Data Processing**

```python
# Top Level: Extract semantic convention attributes
span_attributes = {
    "llm.model_name": "gpt-3.5-turbo",
    "llm.input_messages": [...],      # ← Structure Discovery analyzes this
    "llm.output_message": {...}       # ← Structure Discovery analyzes this
}

# Source Convention DSL extracts: llm.model_name → semantic_data.model
# Structure Discovery DSL analyzes: llm.input_messages content → semantic_data.messages
```

### **Stage 3: Universal Mapping**

```python
# Map all semantic data to HoneyHive schema
honeyhive_result = {
    "inputs": {"chat_history": extracted_messages},
    "outputs": {"content": extracted_content},
    "config": {"model": extracted_model},
    "metadata": {"usage": extracted_usage}
}
```

## ⚡ **Performance Requirements**

### **O(1) Operations Only**
- **Hash-based lookups**: All pattern matching uses frozenset/dict lookups
- **Native Python strings**: Only `startswith(tuple)`, `in frozenset`, `dict.get()`
- **No regex**: Explicitly forbidden for performance
- **Pre-compiled structures**: All DSL compiled to O(1) lookup tables

### **Memory Constraints**
- **<100MB per tracer instance**: Including all compiled DSL structures
- **Cache efficiency**: Use existing multi-instance cache architecture
- **Lazy loading**: Load DSL configurations on-demand

## 🎯 **Integration Points**

### **Python Package Detection**
```python
# Use standard Python package inspection
import importlib.metadata
import importlib.util

def detect_installed_instrumentors():
    """Detect installed instrumentor packages using Python package inspection."""
    instrumentors = {}
    
    # Check for common instrumentor packages
    instrumentor_packages = [
        "openinference-instrumentation-openai",
        "openinference-instrumentation-anthropic", 
        "opentelemetry-instrumentation-openai",
        "opentelemetry-instrumentation-anthropic"
    ]
    
    for package_name in instrumentor_packages:
        try:
            version = importlib.metadata.version(package_name)
            instrumentors[package_name] = version
        except importlib.metadata.PackageNotFoundError:
            continue
    
    return instrumentors
```

### **HoneyHive SDK Integration**
```python
# Integration with existing span processor
class HoneyHiveSpanProcessor:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.universal_processor = UniversalProcessor(
            cache_manager=self.cache_manager,
            tracer_instance=getattr(self, 'tracer_instance', None)
        )
    
    def process_span_attributes(self, span_attributes):
        result = self.universal_processor.process_llm_data(span_attributes)
        return result.honeyhive_schema
```

## ✅ **Success Criteria**

### **Technical Requirements**
- [ ] All operations provably O(1) with performance monitoring
- [ ] Zero provider-specific logic in processing code
- [ ] Complete package-based instrumentor detection
- [ ] >99% mapping accuracy across all sources
- [ ] <10ms processing time per message
- [ ] <100MB memory usage per tracer instance

### **Architectural Requirements**
- [ ] Clean separation of concerns with single responsibility
- [ ] Formal DSL specification with validation
- [ ] Generic processing engines with no hardcoded logic
- [ ] Comprehensive error handling and fallback strategies
- [ ] Full backward compatibility with existing SDK

### **Operational Requirements**
- [ ] Seamless integration with existing HoneyHive SDK
- [ ] Package-based instrumentor detection as primary method
- [ ] Comprehensive monitoring and alerting
- [ ] Zero-downtime deployment capability

---

**This Architecture Foundation document serves as the single source of truth for all implementation decisions. All other documents must align with these specifications.**
