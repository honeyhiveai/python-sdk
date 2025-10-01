# Instrumentor Version Strategy - Agent OS Compatibility Matrix Approach

**Date**: 2025-01-27  
**Analysis**: Long-term Operations Strategy  

---

## 🎯 **Key Insight: Agent OS Already Solves This**

After reviewing the Agent OS compatibility matrix specifications, **you're absolutely correct** - we should leverage the existing compatibility framework rather than building dynamic discovery.

## 📋 **Current Agent OS Approach**

### **Instrumentor Detection via Test Configuration**
```python
# tests/compatibility_matrix/run_compatibility_tests.py
self.test_configs = {
    "test_openinference_openai.py": {
        "provider": "OpenAI",
        "instrumentor": "openinference-instrumentation-openai",
        "category": "openinference",
        "required_env": ["OPENAI_API_KEY"],
    },
    "test_traceloop_anthropic.py": {
        "provider": "Anthropic (Traceloop)",
        "instrumentor": "opentelemetry-instrumentation-anthropic", 
        "category": "traceloop",
        "required_env": ["ANTHROPIC_API_KEY"],
    }
}
```

### **Version Detection via Package Inspection**
```python
# tests/compatibility_matrix/generate_version_matrix.py
def get_instrumentor_compatibility() -> Dict[str, Dict[str, str]]:
    """Get instrumentor compatibility information across Python versions."""
    
    # Import the test runner to get current configurations
    from run_compatibility_tests import CompatibilityTestRunner
    
    # Get all unique instrumentors from test configurations
    test_runner = CompatibilityTestRunner()
    instrumentors = set()
    
    for config in test_runner.test_configs.values():
        instrumentor = config.get("instrumentor")
        if instrumentor:
            instrumentors.add(instrumentor)
```

## 🎯 **Recommended Strategy: Leverage Agent OS Framework**

### **1. Use Compatibility Matrix as Source of Truth**
Instead of dynamic discovery, use the Agent OS compatibility matrix to determine:
- Which instrumentors are installed
- What versions they are
- What semantic conventions they use

### **2. Instrumentor → Semantic Convention Mapping**
```yaml
# config/dsl/instrumentor_mappings.yaml
instrumentor_semantic_conventions:
  # OpenInference instrumentors
  "openinference-instrumentation-openai":
    semantic_convention: "openinference"
    version_detection: "package_version"  # Use pip show
    supported_versions: ["0.1.15", "0.2.0"]
    
  "openinference-instrumentation-anthropic":
    semantic_convention: "openinference" 
    version_detection: "package_version"
    supported_versions: ["0.1.15", "0.2.0"]
    
  # Traceloop instrumentors
  "opentelemetry-instrumentation-openai":
    semantic_convention: "traceloop"
    version_detection: "package_version"
    supported_versions: ["0.46.2", "0.47.0"]
    
  "opentelemetry-instrumentation-anthropic":
    semantic_convention: "traceloop"
    version_detection: "package_version" 
    supported_versions: ["0.46.2", "0.47.0"]
```

### **3. Runtime Detection Algorithm**
```python
# engines/instrumentor_detector.py

class InstrumentorDetector:
    """Detect installed instrumentors and their semantic convention versions."""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.instrumentor_mappings = self._load_instrumentor_mappings()
        
    def detect_active_instrumentors(self) -> Dict[str, str]:
        """Detect which instrumentors are active and their versions."""
        
        # Use Agent OS compatibility matrix approach
        active_instrumentors = {}
        
        for instrumentor_name, config in self.instrumentor_mappings.items():
            if self._is_instrumentor_installed(instrumentor_name):
                version = self._get_instrumentor_version(instrumentor_name)
                semantic_convention = config["semantic_convention"]
                
                # Map to semantic convention version
                convention_version = self._map_to_convention_version(
                    instrumentor_name, version, semantic_convention
                )
                
                active_instrumentors[instrumentor_name] = {
                    "instrumentor_version": version,
                    "semantic_convention": semantic_convention,
                    "convention_version": convention_version
                }
        
        return active_instrumentors
    
    def _is_instrumentor_installed(self, package_name: str) -> bool:
        """Check if instrumentor package is installed."""
        try:
            import importlib.metadata
            importlib.metadata.version(package_name)
            return True
        except importlib.metadata.PackageNotFoundError:
            return False
    
    def _get_instrumentor_version(self, package_name: str) -> str:
        """Get installed version of instrumentor package."""
        import importlib.metadata
        return importlib.metadata.version(package_name)
    
    def _map_to_convention_version(self, instrumentor_name: str, 
                                   instrumentor_version: str, 
                                   semantic_convention: str) -> str:
        """Map instrumentor version to semantic convention version."""
        
        # Use version mapping rules from DSL
        mapping_rules = self.instrumentor_mappings[instrumentor_name]
        version_rules = mapping_rules.get("version_mapping", {})
        
        # Find best match for instrumentor version
        for version_range, convention_version in version_rules.items():
            if self._version_matches_range(instrumentor_version, version_range):
                return convention_version
        
        # Fallback to latest supported version
        supported_versions = mapping_rules["supported_versions"]
        return supported_versions[-1]  # Latest
```

### **4. Enhanced DSL with Version Mapping**
```yaml
# config/dsl/instrumentor_mappings.yaml
instrumentor_semantic_conventions:
  "openinference-instrumentation-openai":
    semantic_convention: "openinference"
    version_detection: "package_version"
    
    # Map instrumentor version ranges to semantic convention versions
    version_mapping:
      ">=1.0.0,<2.0.0": "0.1.15"  # OpenInference instrumentor v1.x → convention v0.1.15
      ">=2.0.0,<3.0.0": "0.2.0"   # OpenInference instrumentor v2.x → convention v0.2.0
    
    supported_versions: ["0.1.15", "0.2.0"]
    fallback_version: "0.1.15"
    
  "opentelemetry-instrumentation-openai":
    semantic_convention: "traceloop"
    version_detection: "package_version"
    
    version_mapping:
      ">=1.20.0,<1.25.0": "0.46.2"  # Traceloop instrumentor v1.20-1.24 → convention v0.46.2
      ">=1.25.0,<2.0.0": "0.47.0"   # Traceloop instrumentor v1.25+ → convention v0.47.0
    
    supported_versions: ["0.46.2", "0.47.0"]
    fallback_version: "0.46.2"
```

## ✅ **Benefits of Agent OS Approach**

### **1. Leverages Existing Infrastructure**
- Uses proven compatibility matrix framework
- Builds on existing instrumentor detection
- Integrates with current testing approach

### **2. No Dynamic Discovery Needed**
- Package versions are deterministic
- Instrumentor → convention mapping is stable
- Version detection via `pip show` is reliable

### **3. Long-term Maintainability**
- Agent OS specs already require version validation
- Compatibility matrix keeps mappings current
- Clear upgrade path when new versions release

### **4. Operational Excellence**
- Leverages existing CI/CD integration
- Uses proven testing patterns
- Fits into current development workflow

## 🔧 **Integration with Universal Engine**

### **Modified Architecture**
```python
# universal_processor.py

class UniversalProcessor:
    def __init__(self, cache_manager, tracer_instance=None):
        # Detect active instrumentors using Agent OS approach
        self.instrumentor_detector = InstrumentorDetector(cache_manager)
        self.active_instrumentors = self.instrumentor_detector.detect_active_instrumentors()
        
        # Load DSL configs based on detected instrumentors
        config_loader = DSLConfigLoader()
        self.dsl_configs = config_loader.load_configs_for_instrumentors(
            self.active_instrumentors
        )
        
        # Initialize engines with detected configurations
        self._initialize_engines()
    
    def process_llm_data(self, span_attributes):
        """Process LLM data using detected instrumentor configurations."""
        
        # Determine which instrumentor generated this data
        instrumentor_info = self._identify_source_instrumentor(span_attributes)
        
        if instrumentor_info:
            # Use specific DSL config for this instrumentor
            convention = instrumentor_info["semantic_convention"]
            version = instrumentor_info["convention_version"]
            
            processor = self.source_processors[f"{convention}_{version}"]
            return processor.process(span_attributes)
        
        # Fallback to structure discovery for unknown sources
        return self.structure_engine.process(span_attributes)
```

## 🎯 **Recommendation: Use Agent OS Framework**

**YES** - this is absolutely the right place to handle version detection. The Agent OS compatibility matrix framework already provides:

1. **Instrumentor Detection**: Via test configurations and package inspection
2. **Version Management**: Via compatibility matrix and version validation
3. **Mapping Infrastructure**: Via test runner configurations
4. **Long-term Maintenance**: Via required version validation specs

**Implementation Strategy**:
1. Extend Agent OS compatibility matrix to include semantic convention mappings
2. Use package version detection (not dynamic discovery) 
3. Map instrumentor versions to semantic convention versions via DSL
4. Integrate with existing testing and validation framework

This approach is **much more reliable** than dynamic discovery and leverages the existing, proven Agent OS infrastructure.
