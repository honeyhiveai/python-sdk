# Universal LLM Discovery Engine - Corrected File Structure Design

**Version**: 2.0  
**Date**: 2025-01-27  
**Status**: Design Phase - No Implementation Yet  

---

## 🎯 **Corrected Module Placement**

```
src/honeyhive/tracer/processing/
└── semantic_conventions/                    # Component of tracer.processing
    ├── __init__.py
    ├── universal_processor.py               # Main orchestrator
    ├── models.py                           # Pydantic v2 models
    │
    ├── config/                             # Centralized configuration
    │   ├── __init__.py
    │   ├── dsl/
    │   │   ├── structure_discovery.yaml    # How to analyze raw JSON
    │   │   ├── source_conventions/
    │   │   │   ├── openinference.yaml      # Extract FROM OpenInference
    │   │   │   ├── traceloop.yaml          # Extract FROM Traceloop
    │   │   │   └── openlit.yaml            # Extract FROM OpenLit
    │   │   ├── target_schemas/
    │   │   │   └── honeyhive.yaml          # Map TO HoneyHive schema
    │   │   └── transforms/
    │   │       └── transform_rules.yaml    # Transform functions
    │   └── loader.py                       # Centralized config loader
    │
    ├── engines/                            # Processing engines
    │   ├── __init__.py
    │   ├── structure_discovery.py          # Analyze raw LLM JSON responses
    │   ├── source_processor.py             # Extract from semantic conventions
    │   ├── target_mapper.py                # Map to target schemas
    │   └── transform_engine.py             # Execute transform functions
    │
    ├── dsl_compiler/                       # DSL compilation
    │   ├── __init__.py
    │   ├── compiler.py                     # Compile DSL to O(1) structures
    │   └── validator.py                    # Validate DSL syntax/semantics
    │
    └── integration/                        # Backward compatibility
        ├── __init__.py
        ├── compatibility_layer.py          # Backward compatibility
        └── migration_utilities.py          # Migration from current implementation
```

## 📋 **Key Design Corrections**

### **1. Module Placement**
- **Correct**: `src/honeyhive/tracer/processing/semantic_conventions/`
- **Not**: Top-level `src/honeyhive/tracer/semantic_conventions/`

### **2. Configuration Centralization**
- **All DSL files**: In `config/dsl/` with logical subdirectories
- **Single loader**: `config/loader.py` manages all DSL types
- **No scattered configs**: Engines import from centralized config

### **3. Clean File Names**
- **No version suffixes**: `universal_processor.py` not `universal_processor_v2_0.py`
- **Descriptive names**: `structure_discovery.py` not `generic_discovery_engine_v2_0.py`
- **Simple and clear**: Focus on functionality, not versioning

### **4. Logical Grouping**
- **Engines**: All processing logic
- **Config**: All configuration and DSL
- **Integration**: Compatibility and migration
- **DSL Compiler**: DSL parsing and compilation

## 🔧 **Usage Patterns**

### **Main Processor**
```python
# src/honeyhive/tracer/processing/semantic_conventions/universal_processor.py

from .config.loader import DSLConfigLoader
from .engines.structure_discovery import StructureDiscoveryEngine
from .engines.source_processor import SourceProcessor
from .engines.target_mapper import TargetMapper

class UniversalProcessor:
    """Main processor orchestrating all stages."""
    
    def __init__(self, cache_manager, tracer_instance=None):
        # Load all DSL configs from centralized location
        config_loader = DSLConfigLoader()
        self.dsl_configs = config_loader.load_all_configs()
        
        # Initialize engines with configs
        self.structure_engine = StructureDiscoveryEngine(
            self.dsl_configs["structure_discovery"],
            cache_manager
        )
        
        self.source_processors = {
            name: SourceProcessor(config, cache_manager)
            for name, config in self.dsl_configs["source_conventions"].items()
        }
        
        self.target_mapper = TargetMapper(
            self.dsl_configs["target_schema"],
            cache_manager
        )
```

### **Config Loader**
```python
# src/honeyhive/tracer/processing/semantic_conventions/config/loader.py

from pathlib import Path
import yaml
from ..dsl_compiler.compiler import DSLCompiler

class DSLConfigLoader:
    """Centralized loader for all DSL configurations."""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent / "dsl"
        self.compiler = DSLCompiler()
    
    def load_all_configs(self):
        """Load and compile all DSL configurations."""
        return {
            "structure_discovery": self._load_structure_discovery(),
            "source_conventions": self._load_source_conventions(),
            "target_schema": self._load_target_schema(),
            "transforms": self._load_transforms()
        }
    
    def _load_structure_discovery(self):
        """Load structure discovery DSL."""
        config_file = self.config_dir / "structure_discovery.yaml"
        with open(config_file) as f:
            raw_config = yaml.safe_load(f)
        return self.compiler.compile_structure_discovery(raw_config)
    
    def _load_source_conventions(self):
        """Load all source convention DSLs."""
        conventions_dir = self.config_dir / "source_conventions"
        compiled_conventions = {}
        
        for config_file in conventions_dir.glob("*.yaml"):
            convention_name = config_file.stem
            with open(config_file) as f:
                raw_config = yaml.safe_load(f)
            compiled_conventions[convention_name] = self.compiler.compile_source_convention(raw_config)
        
        return compiled_conventions
```

## 📁 **DSL Configuration Structure**

### **Structure Discovery DSL**
```yaml
# config/dsl/structure_discovery.yaml
version: "1.0"
dsl_type: "structure_discovery"
description: "Generic LLM provider response structure discovery"

structure_patterns:
  openai_pattern:
    signature_fields: ["choices", "usage.prompt_tokens", "model"]
    confidence_weight: 0.95
    
  anthropic_pattern:
    signature_fields: ["content", "usage.input_tokens", "stop_reason"]
    confidence_weight: 0.90

navigation_rules:
  message_content:
    openai_rule:
      path_expression: "choices.*.message.content"
      pattern_match: "openai_pattern"
      confidence: 0.95
```

### **Source Convention DSL**
```yaml
# config/dsl/source_conventions/openinference.yaml
version: "0.1.15"
dsl_type: "source_convention"
convention_name: "openinference"
description: "Extract semantic data from OpenInference conventions"

recognition_patterns:
  primary_indicators:
    - attribute_prefix: "llm."
      required_attributes: ["llm.model_name"]
      
extraction_rules:
  model_information:
    model_name:
      source_attribute: "llm.model_name"
      semantic_type: "model_identifier"
```

### **Target Schema DSL**
```yaml
# config/dsl/target_schemas/honeyhive.yaml
version: "1.0"
dsl_type: "target_schema"
schema_name: "honeyhive"
description: "HoneyHive unified schema mapping"

schema_sections:
  inputs:
    chat_history:
      source_semantic_type: "conversation_messages"
      data_type: "message_array"
      required: false
      
  outputs:
    content:
      source_semantic_type: "assistant_message"
      data_type: "string"
      required: true
```

## 🎯 **Integration with Existing Code**

### **Span Processor Integration**
```python
# src/honeyhive/tracer/processing/span_processor.py (existing file)

from .semantic_conventions.universal_processor import UniversalProcessor

class HoneyHiveSpanProcessor:
    """Existing span processor with integrated universal processor."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize universal processor
        self.universal_processor = UniversalProcessor(
            cache_manager=self.cache_manager,
            tracer_instance=getattr(self, 'tracer_instance', None)
        )
    
    def process_span_attributes(self, span_attributes):
        """Process span attributes using universal processor."""
        # Use universal processor for semantic convention processing
        result = self.universal_processor.process_llm_data(span_attributes)
        
        # Return in expected format
        return result.honeyhive_schema
```

## ✅ **Design Benefits**

### **1. Clean Architecture**
- No premature versioning in filenames
- Clear module hierarchy under `tracer.processing`
- Logical separation of concerns

### **2. Centralized Configuration**
- All DSL files in one location
- Easy to manage and version
- Single loader for all configs

### **3. Easy Integration**
- Fits naturally into existing `tracer.processing` module
- Minimal changes to existing span processor
- Backward compatibility maintained

### **4. Future-Proof**
- Easy to add new DSL types
- Simple to add new source conventions
- Straightforward to add new target schemas

---

**This corrected design provides clean architecture without premature versioning, proper module placement, and centralized configuration management.**
