#!/usr/bin/env python3
"""
Script to generate comprehensive implementation plan files.
This avoids the "Model failed to call the tool with correct arguments" error
by generating the content programmatically.
"""

def create_o1_algorithms_plan():
    content = """# Implementation Plan - O(1) Algorithms

## Core O(1) Algorithm Implementations

### 1. O(1) Provider Detection Algorithm

```python
class O1ProviderDetector:
    def __init__(self, cache_manager):
        self.cache = cache_manager.get_cache("provider_detection")
        
        # Pre-computed provider signature hashes for O(1) lookup
        self.provider_signatures = {
            "openai_hash": "openai",
            "anthropic_hash": "anthropic", 
            "gemini_hash": "gemini",
            "traceloop_hash": "traceloop"
        }
        
        # O(1) field presence indicators
        self.provider_indicators = {
            "openai": frozenset({"choices", "usage.prompt_tokens", "system_fingerprint"}),
            "anthropic": frozenset({"content", "usage.input_tokens", "stop_reason"}),
            "gemini": frozenset({"candidates", "usageMetadata", "safetyRatings"}),
            "traceloop": frozenset({"gen_ai.request.model", "gen_ai.usage.prompt_tokens"})
        }
    
    def detect_provider_o1(self, field_paths: frozenset) -> tuple[str, float]:
        # O(1) signature hash creation
        signature_hash = self._create_signature_hash_o1(field_paths)
        
        # O(1) cache lookup
        cached_result = self.cache.get(f"provider:{signature_hash}")
        if cached_result:
            return cached_result
        
        # O(1) provider matching using set intersection
        best_provider = None
        best_score = 0.0
        
        for provider, indicators in self.provider_indicators.items():
            # O(1) set intersection
            matches = len(indicators & field_paths)
            if matches > 0:
                score = matches / len(indicators)
                if score > best_score:
                    best_score = score
                    best_provider = provider
        
        result = (best_provider or "unknown", best_score)
        self.cache.set(f"provider:{signature_hash}", result)
        return result
```

### 2. O(1) Field Mapping Algorithm

```python
class O1MappingEngine:
    def __init__(self, cache_manager):
        self.cache = cache_manager.get_cache("field_mapping")
        
        # Pre-computed mapping rules for O(1) lookup
        self.field_mappings = {
            "role_hash": ("inputs", "chat_history", "extract_role"),
            "content_hash": ("inputs", "chat_history", "extract_content"),
            "tokens_hash": ("metadata", "usage", "direct"),
            "model_hash": ("config", "model", "direct")
        }
    
    def apply_mapping_o1(self, field_info: O1FieldInfo) -> tuple[str, str, str]:
        # O(1) hash-based mapping lookup
        mapping = self.field_mappings.get(field_info.content_hash)
        if mapping:
            return mapping
        
        # O(1) fallback mapping based on field type
        return self._get_fallback_mapping_o1(field_info.field_type)
```

### 3. O(1) Transform Engine

```python
class O1TransformEngine:
    def __init__(self):
        # Pre-computed transform functions for O(1 lookup
        self.transforms = {
            "direct": lambda x: x,
            "extract_role": self._extract_role_o1,
            "extract_content": self._extract_content_o1,
            "normalize_tokens": self._normalize_tokens_o1
        }
    
    def apply_transform_o1(self, value: Any, transform_name: str) -> Any:
        # O(1) transform function lookup
        transform_func = self.transforms.get(transform_name, self.transforms["direct"])
        return transform_func(value)
    
    def _extract_role_o1(self, value: Any) -> str:
        # O(1) role extraction using native Python operations
        if isinstance(value, str):
            return value.lower() if value.lower() in self.role_identifiers else "user"
        elif isinstance(value, dict):
            return value.get("role", "user")
        return "user"
```
"""
    
    with open("IMPLEMENTATION_PLAN_O1_ALGORITHMS.md", "w") as f:
        f.write(content)

def create_integration_plan():
    content = """# Implementation Plan - Integration

## Integration with Existing Codebase

### 1. CentralEventMapper Integration

```python
# Update src/honeyhive/tracer/semantic_conventions/central_mapper.py

class CentralEventMapper:
    def __init__(self) -> None:
        # Keep existing initialization
        self.discovery = get_discovery_instance()
        self.rule_engine = RuleEngine()
        self.rule_applier = RuleApplier()
        
        # Add universal processor (created per-instance)
        self.universal_processor = None
        
        self.schema_stats: Dict[str, Any] = {
            "events_mapped": 0,
            "validation_errors": 0,
            "schema_types_used": {},
        }

    def _get_universal_processor(self, tracer_instance: Any = None) -> UniversalDSLProcessor:
        if not self.universal_processor:
            from .universal.processor import UniversalDSLProcessor
            self.universal_processor = UniversalDSLProcessor(tracer_instance)
        return self.universal_processor

    def map_attributes_to_schema(
        self, attributes: Dict[str, Any], event_type: str = "model"
    ) -> Dict[str, Any]:
        try:
            # Try O(1) universal processor first
            universal_processor = self._get_universal_processor()
            result = universal_processor.process_attributes_o1(attributes)
            
            if result and any(result.get(section) for section in ["inputs", "outputs", "config", "metadata"]):
                self.schema_stats["events_mapped"] += 1
                return result
                
        except Exception as e:
            safe_log(None, "warning", f"Universal processor failed, falling back: {e}")
        
        # Fallback to existing logic
        return self._legacy_map_attributes_to_schema(attributes, event_type)
```

### 2. Backup Current Implementation

```bash
# Create backup directory
mkdir -p src/honeyhive/tracer/semantic_conventions/legacy

# Backup current files
cp src/honeyhive/tracer/semantic_conventions/mapping/transforms.py \\
   src/honeyhive/tracer/semantic_conventions/legacy/transforms_backup.py

cp src/honeyhive/tracer/semantic_conventions/central_mapper.py \\
   src/honeyhive/tracer/semantic_conventions/legacy/central_mapper_backup.py
```

### 3. Span Processor Integration

The span processor already uses the CentralEventMapper, so integration is automatic:

```python
# In src/honeyhive/tracer/processing/span_processor.py
# No changes needed - it already uses CentralEventMapper.map_attributes_to_schema()
```
"""
    
    with open("IMPLEMENTATION_PLAN_INTEGRATION.md", "w") as f:
        f.write(content)

def create_testing_plan():
    content = """# Implementation Plan - Testing Strategy

## Comprehensive Testing Approach

### 1. O(1) Performance Tests

```python
import time
import pytest
from src.honeyhive.tracer.semantic_conventions.universal.processor import UniversalDSLProcessor

class TestO1Performance:
    def test_field_discovery_is_o1(self):
        processor = UniversalDSLProcessor()
        
        # Test with increasing data sizes
        sizes = [10, 100, 1000, 10000]
        times = []
        
        for size in sizes:
            test_data = self._generate_test_data(size)
            
            start_time = time.perf_counter()
            result = processor.discover_fields_o1(test_data)
            end_time = time.perf_counter()
            
            times.append(end_time - start_time)
        
        # Verify O(1) behavior - times should be roughly constant
        # Allow for some variance but should not scale linearly
        assert times[-1] / times[0] < 2.0, "Field discovery is not O(1)"
    
    def test_provider_detection_is_o1(self):
        processor = UniversalDSLProcessor()
        
        # Test with different provider response sizes
        for size in [10, 100, 1000]:
            test_data = self._generate_provider_data(size)
            
            start_time = time.perf_counter()
            provider_info = processor.detect_provider_o1(test_data)
            end_time = time.perf_counter()
            
            # Should complete in <1ms regardless of size
            assert (end_time - start_time) < 0.001
```

### 2. Accuracy Tests

```python
class TestMappingAccuracy:
    def test_openai_response_mapping(self):
        processor = UniversalDSLProcessor()
        
        openai_response = {
            "choices": [{"message": {"role": "assistant", "content": "Hello"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5}
        }
        
        result = processor.process_attributes_o1(openai_response)
        
        assert result["outputs"]["role"] == "assistant"
        assert result["outputs"]["content"] == "Hello"
        assert result["metadata"]["prompt_tokens"] == 10
        assert result["metadata"]["completion_tokens"] == 5
```

### 3. Backward Compatibility Tests

```python
class TestBackwardCompatibility:
    def test_existing_api_compatibility(self):
        # Test that existing CentralEventMapper API still works
        mapper = CentralEventMapper()
        
        test_attributes = {"gen_ai.request.model": "gpt-3.5-turbo"}
        result = mapper.map_attributes_to_schema(test_attributes)
        
        # Should return same structure as before
        assert "inputs" in result
        assert "outputs" in result
        assert "config" in result
        assert "metadata" in result
```
"""
    
    with open("IMPLEMENTATION_PLAN_TESTING.md", "w") as f:
        f.write(content)

if __name__ == "__main__":
    print("Generating implementation plan files...")
    create_o1_algorithms_plan()
    create_integration_plan()
    create_testing_plan()
    print("Implementation plan files created successfully!")
