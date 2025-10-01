# Implementation Plan - Testing Strategy

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
