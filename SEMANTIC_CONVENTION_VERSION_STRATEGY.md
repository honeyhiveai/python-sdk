# Semantic Convention Version Strategy

**Date**: 2025-01-27  
**Status**: Design Analysis  

## 🎯 **The Version Selection Problem**

### **Scenario: Multiple OpenInference Versions**
```
config/dsl/source_conventions/
├── openinference_v0_1_15.yaml    # Current stable
├── openinference_v0_2_0.yaml     # New release
└── openinference_v0_1_10.yaml    # Older version
```

**Question**: How does the system know which version to use for incoming OpenInference data?

## 📋 **Analysis: Version Detection Strategies**

### **Strategy 1: Auto-Detection Based on Data**
**Concept**: Analyze the incoming data to determine which version it matches

```yaml
# openinference_v0_1_15.yaml
recognition_patterns:
  version_indicators:
    - attribute_presence: ["llm.model_name", "llm.input_messages"]
    - attribute_absence: ["llm.conversation_id"]  # New in v0.2.0
    - version_confidence: 0.9
    
# openinference_v0_2_0.yaml  
recognition_patterns:
  version_indicators:
    - attribute_presence: ["llm.model_name", "llm.conversation_id"]  # New field
    - version_confidence: 0.95
```

**Pros**: Automatic, handles mixed versions
**Cons**: Complex, requires maintaining version differences

### **Strategy 2: Configuration Priority with Fallback**
**Concept**: Use newest version first, fallback to older if no match

```yaml
# config/loader.py configuration
source_convention_priority:
  openinference:
    - version: "0.2.0"
      file: "openinference_v0_2_0.yaml"
      priority: 1
    - version: "0.1.15" 
      file: "openinference_v0_1_15.yaml"
      priority: 2
    - version: "0.1.10"
      file: "openinference_v0_1_10.yaml"
      priority: 3
```

**Pros**: Simple, predictable
**Cons**: May miss version-specific optimizations

### **Strategy 3: Explicit Version Declaration**
**Concept**: Require version to be specified in the data or configuration

```python
# In span attributes
span_attributes = {
    "llm.model_name": "gpt-3.5-turbo",
    "llm.input_messages": [...],
    "_semantic_convention_version": "openinference/0.1.15"  # Explicit
}
```

**Pros**: Explicit, no guessing
**Cons**: Requires instrumentation changes

### **Strategy 4: Hybrid Approach (Recommended)**
**Concept**: Combine auto-detection with fallback priority

## 🎯 **Recommended: Hybrid Strategy**

### **Implementation Approach**

```yaml
# config/dsl/source_conventions/openinference_v0_2_0.yaml
version: "0.2.0"
dsl_type: "source_convention"
convention_name: "openinference"
description: "OpenInference v0.2.0 with conversation tracking"

recognition_patterns:
  version_detection:
    # Strong indicators this is v0.2.0
    definitive_indicators:
      - attribute_presence: ["llm.conversation_id"]  # New in v0.2.0
      - confidence_boost: 0.3
    
    # Weak indicators (could be this version)
    compatible_indicators:
      - attribute_presence: ["llm.model_name", "llm.input_messages"]
      - base_confidence: 0.7
    
    # Indicators this is NOT this version
    exclusion_indicators:
      - attribute_presence: ["llm.legacy_field"]  # Removed in v0.2.0
      - confidence_penalty: -0.5

  fallback_priority: 1  # Try this version first

# config/dsl/source_conventions/openinference_v0_1_15.yaml  
version: "0.1.15"
dsl_type: "source_convention"
convention_name: "openinference"
description: "OpenInference v0.1.15 stable release"

recognition_patterns:
  version_detection:
    compatible_indicators:
      - attribute_presence: ["llm.model_name", "llm.input_messages"]
      - base_confidence: 0.8
    
    exclusion_indicators:
      - attribute_presence: ["llm.conversation_id"]  # Not in v0.1.15
      - confidence_penalty: -0.9

  fallback_priority: 2  # Try after v0.2.0
```

### **Version Selection Algorithm**

```python
# engines/source_processor.py

class SourceProcessor:
    def detect_convention_version(self, attributes):
        """Detect which version of a convention to use."""
        
        # Step 1: Check for explicit version declaration
        explicit_version = attributes.get("_semantic_convention_version")
        if explicit_version:
            return self._load_explicit_version(explicit_version)
        
        # Step 2: Try auto-detection with all versions
        version_scores = {}
        
        for convention_name, versions in self.available_conventions.items():
            for version_config in sorted(versions, key=lambda x: x["fallback_priority"]):
                confidence = self._calculate_version_confidence(attributes, version_config)
                
                if confidence > 0.8:  # High confidence threshold
                    return version_config
                
                version_scores[version_config["version"]] = confidence
        
        # Step 3: Fallback to highest scoring version
        if version_scores:
            best_version = max(version_scores, key=version_scores.get)
            return self._get_version_config(best_version)
        
        # Step 4: Default to latest version
        return self._get_latest_version()
    
    def _calculate_version_confidence(self, attributes, version_config):
        """Calculate confidence that attributes match this version."""
        recognition = version_config["recognition_patterns"]["version_detection"]
        confidence = recognition.get("base_confidence", 0.5)
        
        # Check definitive indicators
        for indicator in recognition.get("definitive_indicators", []):
            if self._check_indicator(attributes, indicator):
                confidence += indicator.get("confidence_boost", 0.2)
        
        # Check exclusion indicators  
        for indicator in recognition.get("exclusion_indicators", []):
            if self._check_indicator(attributes, indicator):
                confidence += indicator.get("confidence_penalty", -0.5)
        
        return max(0.0, min(1.0, confidence))
```

## 📁 **File Naming Strategy**

### **Recommended Approach: Keep Version in Filename**
```
config/dsl/source_conventions/
├── openinference_v0_2_0.yaml      # Latest
├── openinference_v0_1_15.yaml     # Stable  
├── openinference_v0_1_10.yaml     # Legacy
├── traceloop_v0_46_2.yaml         # Current
├── traceloop_v0_45_0.yaml         # Previous
└── openlit_v0_1_0.yaml            # Current
```

### **Benefits of Versioned Filenames**
1. **Clear Version Management**: Easy to see what versions are supported
2. **Side-by-Side Comparison**: Can compare versions easily
3. **Gradual Migration**: Can deprecate old versions gradually
4. **Debugging**: Clear which version was used for processing
5. **Testing**: Can test against specific versions

### **Version Metadata in DSL**
```yaml
# Each DSL file includes version metadata
version: "0.1.15"
convention_name: "openinference"
supported_versions: ["0.1.15", "0.1.14", "0.1.13"]  # Backward compatibility
deprecated_after: "2025-12-31"  # Optional deprecation date
migration_notes: "Use llm.conversation_id in v0.2.0"  # Upgrade guidance
```

## 🔧 **Configuration Management**

### **Version Registry**
```yaml
# config/version_registry.yaml
semantic_conventions:
  openinference:
    latest: "0.2.0"
    stable: "0.1.15"
    supported: ["0.2.0", "0.1.15", "0.1.10"]
    deprecated: ["0.1.0", "0.0.9"]
    
  traceloop:
    latest: "0.46.2"
    stable: "0.46.2" 
    supported: ["0.46.2", "0.45.0"]
    
  openlit:
    latest: "0.1.0"
    stable: "0.1.0"
    supported: ["0.1.0"]

version_selection_strategy:
  default_mode: "auto_detect_with_fallback"
  fallback_to_latest: true
  confidence_threshold: 0.8
  enable_explicit_version: true
```

### **Loader Configuration**
```python
# config/loader.py
class DSLConfigLoader:
    def load_source_conventions(self):
        """Load source conventions with version management."""
        version_registry = self._load_version_registry()
        conventions = {}
        
        for convention_name, version_info in version_registry["semantic_conventions"].items():
            convention_versions = []
            
            for version in version_info["supported"]:
                filename = f"{convention_name}_v{version.replace('.', '_')}.yaml"
                config = self._load_convention_file(filename)
                config["fallback_priority"] = self._calculate_priority(version, version_info)
                convention_versions.append(config)
            
            conventions[convention_name] = convention_versions
        
        return conventions
```

## ✅ **Recommended Implementation**

### **1. Keep Version in Filenames**
- `openinference_v0_1_15.yaml`
- `traceloop_v0_46_2.yaml`
- Clear version identification

### **2. Use Hybrid Detection Strategy**
- Auto-detect based on data characteristics
- Fallback to priority order (latest first)
- Support explicit version declaration

### **3. Maintain Version Registry**
- Central registry of supported versions
- Clear deprecation timeline
- Migration guidance

### **4. Graceful Degradation**
- If specific version not found, try compatible versions
- Always have a fallback to latest stable
- Log version selection for debugging

This approach provides flexibility while maintaining clear version management and automatic detection capabilities.
