# Universal LLM Discovery Engine - Implementation Plan

**Version**: 3.0 Final  
**Date**: 2025-01-27  
**Status**: Implementation Ready  
**Purpose**: Complete implementation roadmap aligned with Architecture Foundation

---

## 🎯 **Implementation Overview**

This implementation plan provides a detailed roadmap for building the Universal LLM Discovery Engine that **neutrally supports any instrumentor/non-instrumentor integration** and maps span data to the HoneyHive schema for backend ingestion, with rich dynamic handling of nested LLM response data.

### **Key Implementation Principles**
1. **Agent OS First**: Primary detection via compatibility matrix
2. **O(1) Performance**: All operations constant time with hash-based lookups
3. **Zero Provider Logic**: All provider knowledge in DSL configurations
4. **Complete DSL-Driven**: All behavior defined in DSL, not code
5. **Backward Compatible**: Seamless integration with existing HoneyHive SDK

## 📁 **Final Implementation File Structure**

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

## 🚀 **Implementation Phases**

### **Phase 1: Foundation & DSL Infrastructure (Week 1)**

#### **Tasks**
- [ ] **1.1** Create Pydantic v2 models for all data structures
- [ ] **1.2** Implement DSL validator with schema validation
- [ ] **1.3** Implement DSL compiler with O(1) structure generation
- [ ] **1.4** Create centralized config loader
- [ ] **1.5** Set up performance monitoring framework

#### **Deliverables**
- `models.py` - Complete Pydantic v2 models
- `dsl_compiler/validator.py` - DSL validation framework
- `dsl_compiler/compiler.py` - DSL compilation to O(1) structures
- `config/loader.py` - Centralized configuration loading
- Performance monitoring utilities

#### **Success Criteria**
- [ ] All DSL files validate against schemas
- [ ] DSL compilation produces O(1) lookup structures
- [ ] Performance monitoring captures O(1) compliance
- [ ] Config loader handles all 5 DSL types

### **Phase 2: Agent OS Integration (Week 2)**

#### **Tasks**
- [ ] **2.1** Implement instrumentor detection using Agent OS compatibility matrix
- [ ] **2.2** Create instrumentor mapping DSL configurations
- [ ] **2.3** Integrate with existing `tests/compatibility_matrix/` infrastructure
- [ ] **2.4** Implement version detection and mapping logic
- [ ] **2.5** Add caching for instrumentor detection results

#### **Deliverables**
- `engines/instrumentor_detector.py` - Agent OS integration
- `config/dsl/instrumentor_mappings.yaml` - Instrumentor mappings
- Integration with compatibility matrix framework
- Caching layer for detection results

#### **Success Criteria**
- [ ] Instrumentor detection works with existing Agent OS infrastructure
- [ ] Version mapping is deterministic and cached
- [ ] Integration tests pass with real instrumentor packages
- [ ] Performance meets O(1) requirements

### **Phase 3: Source Convention Processing (Week 3)**

#### **Tasks**
- [ ] **3.1** Implement generic source convention processor
- [ ] **3.2** Create source convention DSL configurations for OpenInference, Traceloop, OpenLit
- [ ] **3.3** Implement convention detection and confidence scoring
- [ ] **3.4** Add fallback strategies for missing attributes
- [ ] **3.5** Integrate with Agent OS instrumentor detection

#### **Deliverables**
- `engines/source_processor.py` - Generic source convention processing
- Source convention DSL files for all supported conventions
- Convention detection with confidence scoring
- Fallback and error handling strategies

#### **Success Criteria**
- [ ] Processes all supported semantic conventions correctly
- [ ] Confidence scoring accurately identifies conventions
- [ ] Fallback strategies handle missing data gracefully
- [ ] Integration with instrumentor detection works seamlessly

### **Phase 4: Structure Discovery Engine (Week 4)**

#### **Tasks**
- [ ] **4.1** Implement generic structure discovery engine
- [ ] **4.2** Create structure discovery DSL configurations
- [ ] **4.3** Implement pattern matching with O(1) performance
- [ ] **4.4** Add field classification and content extraction
- [ ] **4.5** Integrate with source convention processing

#### **Deliverables**
- `engines/structure_discovery.py` - Generic structure discovery
- `config/dsl/structure_discovery.yaml` - Structure patterns
- O(1) pattern matching implementation
- Field classification and extraction logic

#### **Success Criteria**
- [ ] Handles diverse LLM response structures dynamically
- [ ] Pattern matching is provably O(1)
- [ ] Field classification accuracy >95%
- [ ] Integration with semantic convention data works correctly

### **Phase 5: Target Mapping & Transforms (Week 5)**

#### **Tasks**
- [ ] **5.1** Implement generic target mapping engine
- [ ] **5.2** Create HoneyHive target schema DSL
- [ ] **5.3** Implement transform engine with compiled functions
- [ ] **5.4** Add schema validation and output formatting
- [ ] **5.5** Integrate all processing stages

#### **Deliverables**
- `engines/target_mapper.py` - Generic target mapping
- `engines/transform_engine.py` - Transform function execution
- `config/dsl/target_schemas/honeyhive.yaml` - HoneyHive schema
- `config/dsl/transforms/transform_rules.yaml` - Transform functions

#### **Success Criteria**
- [ ] Maps all semantic data to HoneyHive schema correctly
- [ ] Transform functions execute with O(1) performance
- [ ] Schema validation catches all data quality issues
- [ ] End-to-end processing pipeline works correctly

### **Phase 6: Integration & Deployment (Week 6)**

#### **Tasks**
- [ ] **6.1** Implement main universal processor orchestrator
- [ ] **6.2** Create backward compatibility layer
- [ ] **6.3** Implement migration utilities from current system
- [ ] **6.4** Add comprehensive error handling and logging
- [ ] **6.5** Deploy with feature flags for gradual rollout

#### **Deliverables**
- `universal_processor.py` - Main orchestrator
- `integration/compatibility_layer.py` - Backward compatibility
- `integration/migration_utilities.py` - Migration tools
- Comprehensive error handling and logging
- Feature flag implementation

#### **Success Criteria**
- [ ] Universal processor orchestrates all stages correctly
- [ ] Backward compatibility maintains existing API contracts
- [ ] Migration from current system is seamless
- [ ] Error handling provides actionable feedback
- [ ] Feature flags enable safe gradual rollout

## 📋 **Core Component Specifications**

### **Universal Processor**

```python
# src/honeyhive/tracer/processing/semantic_conventions/universal_processor.py

"""
Universal LLM Discovery Engine - Main Processor
Orchestrates all processing stages with zero provider-specific logic
"""

from typing import Any, Dict, Optional, Union
from .models import ProcessingResult, ProcessingContext
from .engines.instrumentor_detector import InstrumentorDetector
from .engines.source_processor import SourceProcessor
from .engines.structure_discovery import StructureDiscoveryEngine
from .engines.target_mapper import TargetMapper
from .engines.transform_engine import TransformEngine
from .config.loader import DSLConfigLoader

class UniversalProcessor:
    """Main processor orchestrating all stages - completely generic."""
    
    def __init__(self, cache_manager: Any, tracer_instance: Any = None):
        self.tracer_instance = tracer_instance
        self.cache = cache_manager.get_cache("universal_processor")
        
        # Load all DSL configurations
        config_loader = DSLConfigLoader()
        self.dsl_configs = config_loader.load_all_configs()
        
        # Initialize processing engines
        self.instrumentor_detector = InstrumentorDetector(
            self.dsl_configs["instrumentor_mappings"], 
            cache_manager
        )
        
        self.source_processor = SourceProcessor(
            self.dsl_configs["source_conventions"], 
            cache_manager
        )
        
        self.structure_discovery = StructureDiscoveryEngine(
            self.dsl_configs["structure_discovery"], 
            cache_manager
        )
        
        self.target_mapper = TargetMapper(
            self.dsl_configs["target_schema"], 
            cache_manager
        )
        
        self.transform_engine = TransformEngine(
            self.dsl_configs["transform_rules"], 
            cache_manager
        )
        
        # Performance tracking
        self.processing_stats = {
            "total_processed": 0,
            "instrumentor_detection_calls": 0,
            "source_convention_calls": 0,
            "structure_discovery_calls": 0,
            "target_mapping_calls": 0,
            "cache_hits": 0
        }
    
    def process_llm_data(self, input_data: Union[Dict[str, Any], Any]) -> ProcessingResult:
        """
        Process LLM data using Agent OS-first approach.
        
        Args:
            input_data: Span attributes with semantic conventions and/or raw LLM responses
            
        Returns:
            ProcessingResult with HoneyHive schema output
        """
        processing_context = ProcessingContext(
            tracer_instance_id=str(id(self.tracer_instance)) if self.tracer_instance else "default"
        )
        
        # Stage 1: Agent OS Instrumentor Detection
        instrumentor_info = self.instrumentor_detector.detect_active_instrumentors()
        processing_context.detected_instrumentors = instrumentor_info
        self.processing_stats["instrumentor_detection_calls"] += 1
        
        # Stage 2: Two-Level Data Processing
        semantic_data = {}
        
        # Top Level: Source Convention Processing
        if instrumentor_info:
            convention_result = self.source_processor.extract_semantic_data(
                input_data, instrumentor_info
            )
            semantic_data.update(convention_result.semantic_data)
            processing_context.source_convention_confidence = convention_result.confidence
            self.processing_stats["source_convention_calls"] += 1
        
        # Nested Level: Structure Discovery for LLM Response Objects
        for field_name, field_value in semantic_data.items():
            if self._is_llm_response_object(field_value):
                discovery_result = self.structure_discovery.discover_structure(field_value)
                semantic_data[f"{field_name}_discovered"] = discovery_result.discovered_data
                processing_context.structure_discovery_confidence = discovery_result.confidence
                self.processing_stats["structure_discovery_calls"] += 1
        
        # Stage 3: Universal Mapping
        target_result = self.target_mapper.map_to_schema(semantic_data)
        processing_context.target_mapping_confidence = target_result.confidence
        self.processing_stats["target_mapping_calls"] += 1
        
        # Apply transforms
        final_result = self.transform_engine.apply_transforms(target_result.mapped_data)
        
        # Create final result
        self.processing_stats["total_processed"] += 1
        
        return ProcessingResult(
            honeyhive_schema=final_result,
            processing_context=processing_context,
            confidence=min(
                processing_context.source_convention_confidence or 1.0,
                processing_context.structure_discovery_confidence or 1.0,
                processing_context.target_mapping_confidence or 1.0
            ),
            processing_stats=self.processing_stats.copy()
        )
    
    def _is_llm_response_object(self, value: Any) -> bool:
        """Determine if value is a complex LLM response object needing structure discovery."""
        if not isinstance(value, (dict, list)):
            return False
        
        # Check for common LLM response patterns
        if isinstance(value, dict):
            llm_indicators = ["choices", "content", "candidates", "usage", "message"]
            return any(key in value for key in llm_indicators)
        
        if isinstance(value, list) and len(value) > 0:
            first_item = value[0]
            if isinstance(first_item, dict):
                message_indicators = ["role", "content", "text", "parts"]
                return any(key in first_item for key in message_indicators)
        
        return False
```

### **DSL Config Loader**

```python
# src/honeyhive/tracer/processing/semantic_conventions/config/loader.py

"""
Centralized DSL Configuration Loader
Loads and compiles all DSL configurations with caching
"""

import yaml
from pathlib import Path
from typing import Any, Dict
from ..dsl_compiler.compiler import DSLCompiler
from ..dsl_compiler.validator import DSLValidator

class DSLConfigLoader:
    """Centralized loader for all DSL configurations."""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent / "dsl"
        self.compiler = DSLCompiler()
        self.validator = DSLValidator()
        self._compiled_configs = None
    
    def load_all_configs(self) -> Dict[str, Any]:
        """Load and compile all DSL configurations."""
        if self._compiled_configs is not None:
            return self._compiled_configs
        
        # Load all DSL files
        raw_configs = {
            "instrumentor_mappings": self._load_yaml(self.config_dir / "instrumentor_mappings.yaml"),
            "structure_discovery": self._load_yaml(self.config_dir / "structure_discovery.yaml"),
            "source_conventions": self._load_source_conventions(),
            "target_schema": self._load_yaml(self.config_dir / "target_schemas" / "honeyhive.yaml"),
            "transform_rules": self._load_yaml(self.config_dir / "transforms" / "transform_rules.yaml")
        }
        
        # Validate all configurations
        validation_result = self.validator.validate_all_configs(raw_configs)
        if not validation_result.is_valid:
            raise ValueError(f"DSL validation failed: {validation_result.errors}")
        
        # Compile to O(1) structures
        self._compiled_configs = self.compiler.compile_all_configs(raw_configs)
        
        return self._compiled_configs
    
    def _load_source_conventions(self) -> Dict[str, Any]:
        """Load all source convention DSL files."""
        conventions_dir = self.config_dir / "source_conventions"
        conventions = {}
        
        for yaml_file in conventions_dir.glob("*.yaml"):
            convention_config = self._load_yaml(yaml_file)
            convention_name = convention_config["convention_name"]
            conventions[convention_name] = convention_config
        
        return conventions
    
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse YAML file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
```

## ⚡ **Performance Requirements & Validation**

### **O(1) Performance Guarantees**
- **Hash-based lookups**: All pattern matching uses `frozenset`/`dict` lookups
- **Native Python strings**: Only `startswith(tuple)`, `in frozenset`, `dict.get()`, `len()`
- **No regex**: Explicitly forbidden for performance
- **Pre-compiled structures**: All DSL compiled to O(1) lookup tables
- **Memory constraints**: <100MB per tracer instance

### **Performance Monitoring**
```python
# Performance monitoring built into each engine
class PerformanceMonitor:
    def __init__(self):
        self.operation_times = {}
        self.memory_usage = {}
    
    @contextmanager
    def monitor_operation(self, operation_name: str):
        start_time = time.perf_counter()
        start_memory = psutil.Process().memory_info().rss
        
        yield
        
        end_time = time.perf_counter()
        end_memory = psutil.Process().memory_info().rss
        
        self.operation_times[operation_name] = end_time - start_time
        self.memory_usage[operation_name] = end_memory - start_memory
        
        # Validate O(1) compliance
        if self.operation_times[operation_name] > 0.010:  # 10ms max
            logger.warning(f"Operation {operation_name} exceeded O(1) time limit")
```

## 🔧 **Integration with Existing HoneyHive SDK**

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

## ✅ **Success Criteria & Testing**

### **Technical Success Criteria**
- [ ] All operations provably O(1) with performance monitoring
- [ ] Zero provider-specific logic in processing code
- [ ] Complete Agent OS compatibility matrix integration
- [ ] >99% mapping accuracy across all sources
- [ ] <10ms processing time per message
- [ ] <100MB memory usage per tracer instance

### **Integration Testing**
- [ ] Agent OS compatibility matrix integration tests
- [ ] Multi-instrumentor environment testing
- [ ] Performance benchmarking with real data
- [ ] Backward compatibility validation
- [ ] Error handling and fallback testing

### **Deployment Strategy**
- [ ] Feature flags for gradual rollout
- [ ] A/B testing with current implementation
- [ ] Monitoring and alerting setup
- [ ] Rollback procedures
- [ ] Performance monitoring in production

## 📊 **Implementation Timeline**

| Phase | Duration | Key Deliverables | Success Gates |
|-------|----------|------------------|---------------|
| Phase 1 | Week 1 | DSL Infrastructure | DSL validation & compilation working |
| Phase 2 | Week 2 | Agent OS Integration | Instrumentor detection working |
| Phase 3 | Week 3 | Source Convention Processing | Convention extraction working |
| Phase 4 | Week 4 | Structure Discovery | LLM response analysis working |
| Phase 5 | Week 5 | Target Mapping & Transforms | End-to-end pipeline working |
| Phase 6 | Week 6 | Integration & Deployment | Production ready with monitoring |

---

**This Implementation Plan provides a complete, implementation-ready roadmap aligned with the Architecture Foundation and DSL Specification. All components are designed for O(1) performance with Agent OS integration as the primary approach.**
