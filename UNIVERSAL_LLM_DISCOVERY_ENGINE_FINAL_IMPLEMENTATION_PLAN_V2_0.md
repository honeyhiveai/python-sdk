# Universal LLM Discovery Engine - Final Implementation Plan v2.0

**Version**: 2.0  
**Date**: 2025-01-27  
**Status**: Final Implementation Ready  
**Breaking Changes**: Complete architectural redesign with proper DSL separation

---

## 🎯 **Executive Summary**

The Universal LLM Discovery Engine v2.0 represents a complete architectural redesign based on lessons learned from the initial design. This version provides:

- **Proper Separation of Concerns**: Four distinct DSL types with single responsibility
- **Zero Provider Logic in Code**: All provider knowledge in DSL configurations
- **Formal DSL Specification**: Complete syntax and semantic definitions
- **Generic Processing**: Truly provider and convention agnostic code
- **O(1) Performance**: Hash-based operations throughout

## 🏗️ **Corrected Architecture Overview**

### **Two-Stage Processing Pipeline**

```
┌─────────────────────────────────────────────────────────────┐
│                    Stage 1: Multi-Source Input              │
│                                                             │
│  Raw LLM Response  │  Existing Semantic Conventions        │
│  (OpenAI/Anthropic)│  (OpenInference/Traceloop/OpenLit)    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                Stage 2: Generic Processing                 │
│                                                             │
│  Structure Discovery Engine  │  Source Convention Engine   │
│  (Raw JSON → Normalized)     │  (Conventions → Normalized) │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                Stage 3: Unified Mapping                    │
│                                                             │
│         Generic Mapping Engine → HoneyHive Schema          │
└─────────────────────────────────────────────────────────────┘
```

### **Four DSL Types with Single Responsibility**

1. **Structure Discovery DSL**: Analyze raw LLM provider JSON responses
2. **Source Convention DSL**: Extract data from existing semantic conventions
3. **Target Schema DSL**: Define HoneyHive schema structure and mapping rules
4. **Transform Rules DSL**: Define transformation functions and data conversions

## 📁 **Final File Structure**

```
src/honeyhive/tracer/semantic_conventions/
├── universal/
│   ├── __init__.py
│   ├── universal_processor_v2_0.py        # Main orchestrator
│   ├── models_v2_0.py                     # Pydantic v2 models
│   └── cache_integration_v2_0.py          # Multi-instance cache integration
│
├── structure_discovery/
│   ├── __init__.py
│   ├── generic_discovery_engine_v2_0.py   # Raw JSON structure analysis
│   ├── field_classifier_v2_0.py           # Generic field classification
│   ├── content_extractor_v2_0.py          # Generic content extraction
│   └── dsl/
│       └── structure_discovery_v2_0.yaml  # All structure patterns
│
├── source_conventions/
│   ├── __init__.py
│   ├── generic_source_processor_v2_0.py   # Extract from existing conventions
│   ├── convention_detector_v2_0.py        # Detect convention type
│   └── dsl/
│       ├── openinference_source_v0_1_15.yaml
│       ├── traceloop_source_v0_46_2.yaml
│       └── openlit_source_v0_1_0.yaml
│
├── target_mapping/
│   ├── __init__.py
│   ├── generic_mapping_engine_v2_0.py     # Map to target schemas
│   ├── schema_validator_v2_0.py           # Validate output schemas
│   └── dsl/
│       └── honeyhive_target_v2_0.yaml     # HoneyHive schema definition
│
├── transforms/
│   ├── __init__.py
│   ├── transform_engine_v2_0.py           # Execute transform functions
│   ├── performance_monitor_v2_0.py        # O(1) compliance monitoring
│   └── dsl/
│       └── transform_rules_v2_0.yaml      # All transform functions
│
├── dsl_compiler/
│   ├── __init__.py
│   ├── dsl_parser_v2_0.py                # Parse and validate DSL files
│   ├── dsl_compiler_v2_0.py              # Compile to O(1) structures
│   └── dsl_validator_v2_0.py             # Cross-DSL validation
│
├── integration/
│   ├── __init__.py
│   ├── compatibility_layer_v2_0.py        # Backward compatibility
│   ├── migration_utilities_v2_0.py        # Migration from v1.0
│   └── feature_flags_v2_0.py             # Gradual rollout support
│
└── legacy_backup/
    ├── transforms_backup_v1_0.py          # Original implementation backup
    ├── central_mapper_backup_v1_0.py      # Original central mapper
    └── migration_notes_v2_0.md            # Migration documentation
```

## 📋 **Core Components Specification**

### **Universal Processor v2.0**

```python
# src/honeyhive/tracer/semantic_conventions/universal/universal_processor_v2_0.py

"""
Universal LLM Discovery Engine v2.0 - Main Processor
Orchestrates all processing stages with zero provider-specific logic
"""

from typing import Any, Dict, Optional, Union
from .models_v2_0 import ProcessingResult, ProcessingContext
from ..structure_discovery.generic_discovery_engine_v2_0 import GenericDiscoveryEngine
from ..source_conventions.generic_source_processor_v2_0 import GenericSourceProcessor
from ..target_mapping.generic_mapping_engine_v2_0 import GenericMappingEngine

class UniversalProcessor:
    """Main processor orchestrating all stages - completely generic."""
    
    def __init__(self, dsl_configs: Dict[str, Any], cache_manager: Any, tracer_instance: Any = None):
        self.tracer_instance = tracer_instance
        self.cache = cache_manager.get_cache("universal_processor")
        
        # Initialize processing engines with DSL configurations
        self.structure_discovery = GenericDiscoveryEngine(
            dsl_configs["structure_discovery"], 
            cache_manager
        )
        
        self.source_processors = {
            name: GenericSourceProcessor(config, cache_manager)
            for name, config in dsl_configs["source_conventions"].items()
        }
        
        self.target_mapper = GenericMappingEngine(
            dsl_configs["target_schema"], 
            cache_manager
        )
        
        # Performance tracking
        self.processing_stats = {
            "total_processed": 0,
            "structure_discovery_calls": 0,
            "source_convention_calls": 0,
            "target_mapping_calls": 0,
            "cache_hits": 0
        }
    
    def process_llm_data(self, input_data: Union[Dict[str, Any], Any]) -> ProcessingResult:
        """
        Process LLM data from any source - completely generic processing.
        
        Args:
            input_data: Either raw LLM response JSON or span attributes with semantic conventions
            
        Returns:
            ProcessingResult with HoneyHive schema output
        """
        processing_context = ProcessingContext(
            tracer_instance_id=str(id(self.tracer_instance)) if self.tracer_instance else "default"
        )
        
        # Step 1: Determine input type and route to appropriate processor
        if self._is_raw_llm_response(input_data):
            # Route to structure discovery
            normalized_data = self.structure_discovery.discover_structure(input_data)
            processing_context.processing_path = "structure_discovery"
            self.processing_stats["structure_discovery_calls"] += 1
            
        else:
            # Route to source convention processing
            normalized_data = self._process_source_conventions(input_data)
            processing_context.processing_path = "source_conventions"
            self.processing_stats["source_convention_calls"] += 1
        
        # Step 2: Map to target schema (HoneyHive)
        target_result = self.target_mapper.map_to_schema(normalized_data)
        processing_context.target_mapping_confidence = target_result.confidence
        self.processing_stats["target_mapping_calls"] += 1
        
        # Step 3: Create final result
        self.processing_stats["total_processed"] += 1
        
        return ProcessingResult(
            honeyhive_schema=target_result.mapped_data,
            processing_context=processing_context,
            confidence=target_result.confidence,
            processing_stats=self.processing_stats.copy()
        )
    
    def _is_raw_llm_response(self, data: Any) -> bool:
        """Determine if input is raw LLM response vs semantic convention attributes."""
        if not isinstance(data, dict):
            return False
        
        # Check for semantic convention prefixes
        semantic_prefixes = ["llm.", "gen_ai.", "openlit."]
        has_semantic_attributes = any(
            key.startswith(prefix) for key in data.keys() for prefix in semantic_prefixes
        )
        
        # If has semantic attributes, it's from a convention
        # If no semantic attributes, assume it's raw LLM response
        return not has_semantic_attributes
    
    def _process_source_conventions(self, attributes: Dict[str, Any]) -> Any:
        """Process source convention attributes using appropriate processor."""
        # Try each source processor until one recognizes the convention
        for processor_name, processor in self.source_processors.items():
            result = processor.extract_semantic_data(attributes)
            if result and result.confidence > 0.5:
                return result.semantic_data
        
        # If no processor recognizes it, return empty normalized data
        return {}
```

### **DSL Compiler v2.0**

```python
# src/honeyhive/tracer/semantic_conventions/dsl_compiler/dsl_compiler_v2_0.py

"""
DSL Compiler v2.0 - Compiles all DSL types to O(1) runtime structures
"""

import yaml
from typing import Any, Dict, List
from pathlib import Path
from .dsl_validator_v2_0 import DSLValidator

class DSLCompiler:
    """Compile all DSL configurations into O(1) runtime structures."""
    
    def __init__(self, cache_manager: Any):
        self.cache = cache_manager.get_cache("dsl_compiler")
        self.validator = DSLValidator()
        
    def compile_all_dsls(self, dsl_directory: Path) -> Dict[str, Any]:
        """Compile all DSL files into runtime-ready configurations."""
        
        # Step 1: Load and validate all DSL files
        dsl_files = self._discover_dsl_files(dsl_directory)
        raw_dsls = self._load_dsl_files(dsl_files)
        
        # Step 2: Validate DSL syntax and semantics
        validation_result = self.validator.validate_all_dsls(raw_dsls)
        if not validation_result.is_valid:
            raise ValueError(f"DSL validation failed: {validation_result.errors}")
        
        # Step 3: Compile each DSL type
        compiled_dsls = {
            "structure_discovery": self._compile_structure_discovery(raw_dsls["structure_discovery"]),
            "source_conventions": self._compile_source_conventions(raw_dsls["source_conventions"]),
            "target_schema": self._compile_target_schema(raw_dsls["target_schema"]),
            "transform_rules": self._compile_transform_rules(raw_dsls["transform_rules"])
        }
        
        # Step 4: Create cross-reference maps for O(1) lookups
        compiled_dsls["cross_references"] = self._create_cross_reference_maps(compiled_dsls)
        
        return compiled_dsls
    
    def _compile_structure_discovery(self, dsl_config: Dict[str, Any]) -> Dict[str, Any]:
        """Compile structure discovery DSL into O(1) lookup structures."""
        compiled = {
            "version": dsl_config["version"],
            
            # Compile structure patterns into hash-based lookup
            "pattern_lookup": {
                pattern_id: {
                    "signature_fields": frozenset(pattern["signature_fields"]),
                    "optional_fields": frozenset(pattern.get("optional_fields", [])),
                    "confidence_weight": pattern["confidence_weight"]
                }
                for pattern_id, pattern in dsl_config["structure_patterns"].items()
            },
            
            # Compile navigation rules into path-based lookup
            "navigation_lookup": {},
            
            # Compile field classification into type-based lookup
            "classification_lookup": {}
        }
        
        # Build navigation lookup for O(1) path resolution
        for field_type, rules in dsl_config["navigation_rules"].items():
            compiled["navigation_lookup"][field_type] = {
                rule_id: {
                    "path_expression": rule["path_expression"],
                    "pattern_match": rule["pattern_match"],
                    "confidence": rule["confidence"]
                }
                for rule_id, rule in rules.items()
            }
        
        # Build classification lookup for O(1) field type determination
        for field_type, classification in dsl_config["field_classification"].items():
            compiled["classification_lookup"][field_type] = {
                "path_indicators": frozenset(classification["path_indicators"]),
                "content_validators": classification["content_validators"],
                "context_clues": frozenset(classification.get("context_clues", []))
            }
        
        return compiled
    
    def _compile_source_conventions(self, source_dsls: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Compile all source convention DSLs."""
        compiled_sources = {}
        
        for convention_name, dsl_config in source_dsls.items():
            compiled_sources[convention_name] = {
                "version": dsl_config["version"],
                "convention_name": dsl_config["convention_name"],
                
                # Compile recognition patterns for O(1) detection
                "recognition_patterns": self._compile_recognition_patterns(dsl_config["recognition_patterns"]),
                
                # Compile extraction rules for O(1) field extraction
                "extraction_rules": self._compile_extraction_rules(dsl_config["extraction_rules"]),
                
                # Compile fallback strategies
                "fallback_strategies": dsl_config.get("fallback_strategies", {})
            }
        
        return compiled_sources
    
    def _compile_target_schema(self, dsl_config: Dict[str, Any]) -> Dict[str, Any]:
        """Compile target schema DSL into O(1) mapping structures."""
        return {
            "version": dsl_config["version"],
            "schema_name": dsl_config["schema_name"],
            
            # Compile schema structure for O(1) validation
            "schema_structure": dsl_config["schema_structure"],
            
            # Compile mapping rules for O(1) field mapping
            "mapping_rules": dsl_config["mapping_rules"],
            
            # Compile validation constraints
            "validation_constraints": dsl_config.get("validation_constraints", {})
        }
    
    def _compile_transform_rules(self, dsl_config: Dict[str, Any]) -> Dict[str, Any]:
        """Compile transform rules DSL into executable functions."""
        compiled_functions = {}
        
        for function_name, function_config in dsl_config["transform_functions"].items():
            # Compile function implementation based on type
            if function_config["implementation_type"] == "native_python":
                # Execute the function definition to create callable
                exec(function_config["implementation"])
                func_name = function_config["implementation"].split("def ")[1].split("(")[0].strip()
                compiled_functions[function_name] = locals()[func_name]
            elif function_config["implementation_type"] == "lambda":
                compiled_functions[function_name] = eval(function_config["implementation"])
            
        return {
            "version": dsl_config["version"],
            "compiled_functions": compiled_functions,
            "data_type_conversions": dsl_config["data_type_conversions"]
        }
```

## 🚀 **Implementation Roadmap v2.0**

### **Phase 1: DSL Foundation (Week 1)**
- [ ] Implement DSL specification and validation framework
- [ ] Create DSL compiler with O(1) structure generation
- [ ] Build core Pydantic v2 models
- [ ] Implement generic processing base classes

### **Phase 2: Structure Discovery (Week 2)**
- [ ] Implement generic structure discovery engine
- [ ] Create structure discovery DSL configurations
- [ ] Build field classification and content extraction
- [ ] Add performance monitoring and validation

### **Phase 3: Source Convention Processing (Week 3)**
- [ ] Implement generic source convention processor
- [ ] Create source convention DSL configurations (OpenInference, Traceloop, OpenLit)
- [ ] Build convention detection and extraction logic
- [ ] Add fallback strategies and error handling

### **Phase 4: Target Mapping (Week 4)**
- [ ] Implement generic mapping engine
- [ ] Create HoneyHive target schema DSL
- [ ] Build transform engine with compiled functions
- [ ] Add schema validation and output formatting

### **Phase 5: Integration & Testing (Week 5)**
- [ ] Implement compatibility layer for backward compatibility
- [ ] Create comprehensive test suite with O(1) performance validation
- [ ] Build migration utilities from v1.0
- [ ] Add feature flags for gradual rollout

### **Phase 6: Deployment (Week 6)**
- [ ] Production deployment with monitoring
- [ ] Performance tuning and optimization
- [ ] Documentation and team training
- [ ] Legacy cleanup and archival

## ✅ **Success Criteria v2.0**

### **Technical Success**
- [ ] All operations provably O(1) with performance monitoring
- [ ] Zero provider-specific logic in processing code
- [ ] Complete DSL-driven configuration
- [ ] >99% mapping accuracy across all sources
- [ ] <10ms processing time per message

### **Architectural Success**
- [ ] Clean separation of concerns with single responsibility
- [ ] Formal DSL specification with validation
- [ ] Generic processing engines with no hardcoded logic
- [ ] Comprehensive error handling and fallback strategies

### **Operational Success**
- [ ] Seamless backward compatibility
- [ ] Gradual rollout with feature flags
- [ ] Comprehensive monitoring and alerting
- [ ] Zero-downtime deployment capability

---

**This v2.0 implementation plan represents a complete architectural redesign with proper separation of concerns, formal DSL specifications, and truly generic processing logic.**
