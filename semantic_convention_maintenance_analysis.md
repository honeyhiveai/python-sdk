# Semantic Convention Mapping: Maintenance Strategy Analysis

## Current Problem: Hardcoded Approach Leads to Technical Debt

### Issues with Static Mapping:
1. **Constant Code Changes**: Every new semantic convention requires code updates
2. **Version Fragmentation**: Different instrumentor versions use different attribute names
3. **Provider Variations**: Each LLM provider may have slight variations
4. **Breaking Changes**: Semantic convention updates break existing mappings
5. **Testing Overhead**: Each change requires comprehensive regression testing

## Recommended Approach: Configuration-Driven Dynamic Mapping

### 1. **Configuration-Based Mapping Rules**

Instead of hardcoded logic, use configuration files that define mapping rules:

```yaml
# semantic_mappings.yaml
semantic_conventions:
  openllmetry:
    version_ranges:
      - version: ">=0.30.0"
        mappings:
          config:
            provider: "gen_ai.system"
            model: "gen_ai.request.model"
            is_streaming: "gen_ai.request.streaming"
          inputs:
            chat_history:
              pattern: "gen_ai.request.messages.{index}.{field}"
              fields: ["role", "content"]
          outputs:
            finish_reason: "gen_ai.response.finish_reasons"
            content: "gen_ai.response.text"
          metadata:
            prompt_tokens: "gen_ai.usage.prompt_tokens"
            completion_tokens: "gen_ai.usage.completion_tokens"
            total_tokens: "gen_ai.usage.total_tokens"
      - version: ">=0.25.0,<0.30.0"
        mappings:
          # Legacy mappings for older versions
          
  openinference:
    version_ranges:
      - version: ">=1.0.0"
        mappings:
          config:
            provider: "llm.provider"
            model: "llm.model_name"
          inputs:
            chat_history:
              source: "llm.input_messages"
              format: "json_array"
          outputs:
            content: "output.value"
          metadata:
            prompt_tokens: "llm.token_count.prompt"
            completion_tokens: "llm.token_count.completion"
            
  openlit:
    version_ranges:
      - version: ">=1.0.0"
        mappings:
          config:
            provider: "gen_ai.system"
            model: "gen_ai.request.model"
          inputs:
            chat_history: "gen_ai.request.messages"
          outputs:
            content: "gen_ai.response.text"
          metadata:
            prompt_tokens: "gen_ai.usage.input_tokens"
            completion_tokens: "gen_ai.usage.output_tokens"

# Priority order for resolving conflicts
priority_order:
  - openllmetry
  - openinference  
  - openlit
  - honeyhive_legacy

# Fallback patterns for unknown attributes
fallback_patterns:
  - pattern: "gen_ai\\.request\\.messages\\.(\\d+)\\.(role|content)"
    target: "inputs.chat_history"
  - pattern: "gen_ai\\.usage\\.(.*_tokens)"
    target: "metadata"
  - pattern: "llm\\.(model_name|provider)"
    target: "config"
```

### 2. **Dynamic Mapping Engine**

```python
class SemanticConventionMapper:
    """Configuration-driven semantic convention mapper"""
    
    def __init__(self, config_path: str = "semantic_mappings.yaml"):
        self.config = self._load_config(config_path)
        self.pattern_cache = {}
        
    def map_attributes(self, attributes: dict) -> dict:
        """Dynamically map attributes using configuration rules"""
        
        # Detect which semantic conventions are present
        detected_conventions = self._detect_conventions(attributes)
        
        # Apply mappings in priority order
        mapped_data = {
            "config": {},
            "inputs": {},
            "outputs": {},
            "metadata": {}
        }
        
        for convention in self.config["priority_order"]:
            if convention in detected_conventions:
                convention_mappings = self._get_convention_mappings(
                    convention, detected_conventions[convention]["version"]
                )
                self._apply_mappings(attributes, convention_mappings, mapped_data)
        
        # Apply fallback patterns for unmapped attributes
        self._apply_fallback_patterns(attributes, mapped_data)
        
        return mapped_data
    
    def _detect_conventions(self, attributes: dict) -> dict:
        """Detect which semantic conventions are present and their versions"""
        conventions = {}
        
        # Check for OpenLLMetry attributes
        if any(key.startswith("gen_ai.") for key in attributes):
            scope = attributes.get("scope", {})
            if "opentelemetry.instrumentation" in str(scope):
                conventions["openllmetry"] = {
                    "version": self._extract_version(scope),
                    "confidence": 0.9
                }
        
        # Check for OpenInference attributes  
        if any(key.startswith("llm.") for key in attributes):
            conventions["openinference"] = {
                "version": "1.0.0",  # Default
                "confidence": 0.8
            }
            
        # Check for OpenLit attributes
        if any(key.startswith("gen_ai.usage.input_tokens") for key in attributes):
            conventions["openlit"] = {
                "version": "1.0.0",  # Default
                "confidence": 0.7
            }
            
        return conventions
    
    def _apply_mappings(self, attributes: dict, mappings: dict, target: dict):
        """Apply mapping rules to extract structured data"""
        
        for section, rules in mappings.items():
            if section not in target:
                target[section] = {}
                
            for target_field, source_pattern in rules.items():
                if isinstance(source_pattern, str):
                    # Simple field mapping
                    if source_pattern in attributes:
                        target[section][target_field] = attributes[source_pattern]
                        
                elif isinstance(source_pattern, dict):
                    # Complex mapping (e.g., chat_history extraction)
                    if source_pattern.get("pattern"):
                        extracted_data = self._extract_pattern_data(
                            attributes, source_pattern
                        )
                        if extracted_data:
                            target[section][target_field] = extracted_data
    
    def _extract_pattern_data(self, attributes: dict, pattern_config: dict) -> Any:
        """Extract data using pattern matching"""
        pattern = pattern_config["pattern"]
        
        if "chat_history" in pattern_config.get("target", ""):
            return self._extract_chat_messages(attributes, pattern_config)
        elif pattern_config.get("format") == "json_array":
            return self._extract_json_array(attributes, pattern_config)
        else:
            return self._extract_simple_pattern(attributes, pattern_config)
```

### 3. **Configuration Management**

```python
class ConfigurationManager:
    """Manages semantic convention configurations with hot-reloading"""
    
    def __init__(self):
        self.config_watchers = {}
        self.cached_configs = {}
        
    def get_config(self, config_name: str) -> dict:
        """Get configuration with caching and hot-reload support"""
        if config_name not in self.cached_configs:
            self.cached_configs[config_name] = self._load_config(config_name)
            self._setup_file_watcher(config_name)
        return self.cached_configs[config_name]
    
    def update_config(self, config_name: str, new_config: dict):
        """Update configuration at runtime"""
        self.cached_configs[config_name] = new_config
        # Notify all mappers using this config
        self._notify_config_change(config_name)
```

### 4. **Version-Aware Mapping**

```python
class VersionAwareMapper:
    """Handles version-specific semantic convention differences"""
    
    def get_mapping_for_version(self, convention: str, version: str) -> dict:
        """Get appropriate mapping based on semantic convention version"""
        
        version_ranges = self.config[convention]["version_ranges"]
        
        for version_range in version_ranges:
            if self._version_matches(version, version_range["version"]):
                return version_range["mappings"]
        
        # Fallback to latest version
        return version_ranges[0]["mappings"]
    
    def _version_matches(self, version: str, range_spec: str) -> bool:
        """Check if version matches range specification"""
        # Use semantic versioning logic
        from packaging import version as pkg_version
        
        # Parse range specifications like ">=0.30.0", ">=0.25.0,<0.30.0"
        # Implementation details...
```

## Maintenance Benefits of This Approach

### 1. **Zero Code Changes for New Conventions**
- Add new semantic conventions by updating YAML config
- No Python code changes required
- Hot-reload configurations without restarts

### 2. **Version Compatibility Management**
```yaml
# Handle breaking changes in semantic conventions
openllmetry:
  version_ranges:
    - version: ">=0.35.0"  # New version with breaking changes
      mappings:
        config:
          model: "gen_ai.request.model_name"  # Changed from "model"
    - version: ">=0.30.0,<0.35.0"  # Legacy support
      mappings:
        config:
          model: "gen_ai.request.model"  # Old attribute name
```

### 3. **Provider-Specific Overrides**
```yaml
# Handle provider-specific variations
provider_overrides:
  openai:
    additional_mappings:
      metadata:
        system_fingerprint: "gen_ai.openai.system_fingerprint"
  anthropic:
    additional_mappings:
      metadata:
        model_version: "gen_ai.anthropic.model_version"
```

### 4. **Fallback Pattern Matching**
```yaml
# Regex patterns for unknown attributes
fallback_patterns:
  - pattern: "gen_ai\\.request\\.messages\\.(\\d+)\\.(\\w+)"
    handler: "extract_message_field"
    target: "inputs.chat_history"
  - pattern: "gen_ai\\.usage\\.(\\w+_tokens)"
    handler: "extract_token_count"
    target: "metadata"
```

## Implementation Strategy

### Phase 1: Configuration Infrastructure
1. Create YAML configuration schema
2. Implement configuration loader with validation
3. Add hot-reload capability
4. Create version matching logic

### Phase 2: Dynamic Mapping Engine
1. Build pattern-based attribute extraction
2. Implement priority-based convention resolution
3. Add fallback pattern matching
4. Create structured data builders

### Phase 3: Migration and Testing
1. Create configuration for existing semantic conventions
2. Add comprehensive test suite with real data
3. Implement gradual rollout with feature flags
4. Monitor and tune mapping accuracy

## Long-Term Maintenance Model

### 1. **Community-Driven Configuration Updates**
- Configuration files in version control
- Pull request workflow for new semantic conventions
- Automated testing against real instrumentor data
- Community contributions for new providers

### 2. **Automated Convention Detection**
```python
# Future: ML-based convention detection
class ConventionDetector:
    def detect_unknown_convention(self, attributes: dict) -> dict:
        """Use ML to detect patterns in unknown semantic conventions"""
        # Analyze attribute patterns
        # Suggest mapping configurations
        # Auto-generate YAML configs
```

### 3. **Monitoring and Analytics**
```python
# Track mapping effectiveness
class MappingAnalytics:
    def track_unmapped_attributes(self, attributes: dict):
        """Track attributes that couldn't be mapped"""
        # Send to analytics for pattern analysis
        # Generate suggestions for new mappings
```

## Conclusion

**Recommended Approach: Configuration-Driven with Dynamic Fallbacks**

This approach provides:
- ✅ **Zero-code maintenance** for new semantic conventions
- ✅ **Version compatibility** management  
- ✅ **Hot-reload** capability for production updates
- ✅ **Pattern-based fallbacks** for unknown attributes
- ✅ **Community-driven** configuration updates
- ✅ **Future-proof** architecture

The initial investment in building this infrastructure pays off with virtually zero maintenance overhead for semantic convention changes, making it sustainable for long-term evolution of the LLM observability ecosystem.
