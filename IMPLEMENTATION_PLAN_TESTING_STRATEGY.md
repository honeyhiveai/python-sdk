# Implementation Plan - Comprehensive Testing Strategy

**Version**: 1.0  
**Date**: 2025-01-27  
**Status**: Implementation Ready  

## 1. Testing Strategy Overview

### 1.1 Testing Philosophy

The Universal LLM Discovery Engine requires comprehensive testing across multiple dimensions:

- **O(1) Performance Validation**: Every operation must maintain constant-time performance
- **Multi-Provider Compatibility**: Support for all major LLM providers
- **Backward Compatibility**: Seamless integration with existing HoneyHive SDK
- **Production Reliability**: 99.9% uptime with <0.1% error rate
- **Dynamic Adaptability**: Handle unknown providers and schema changes

### 1.2 Testing Pyramid Structure

```
                    /\
                   /  \
                  /E2E \     <- End-to-End Integration Tests
                 /______\
                /        \
               /Integration\ <- Integration Tests (Multi-Component)
              /__________\
             /            \
            /   Unit Tests  \ <- Unit Tests (Individual Components)
           /________________\
          /                  \
         /  Performance Tests  \ <- O(1) Performance & Load Tests
        /____________________\
```

## 2. Unit Testing Strategy

### 2.1 Core Component Unit Tests

```python
# tests/unit/test_universal_processor.py

import pytest
import time
from typing import Any, Dict, List
from unittest.mock import Mock, patch
from src.honeyhive.tracer.semantic_conventions.universal.processor import UniversalDSLProcessor
from src.honeyhive.tracer.semantic_conventions.universal.models import (
    O1FieldInfo, O1DiscoveredFields, O1ProviderInfo, FieldType, HoneyHiveSection
)

class TestUniversalDSLProcessor:
    """Comprehensive unit tests for Universal DSL Processor."""
    
    @pytest.fixture
    def mock_cache_manager(self):
        """Mock cache manager for testing."""
        cache_manager = Mock()
        cache_manager.get_cache.return_value = Mock()
        return cache_manager
    
    @pytest.fixture
    def processor(self, mock_cache_manager):
        """Create processor instance for testing."""
        return UniversalDSLProcessor(mock_cache_manager)
    
    def test_o1_field_discovery_performance(self, processor):
        """Test that field discovery maintains O(1) performance."""
        test_data = {
            "model": "gpt-3.5-turbo",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Hello, world!"
                }
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }
        
        # Measure performance across multiple runs
        execution_times = []
        for _ in range(100):
            start_time = time.perf_counter_ns()
            result = processor.discover_fields_o1(test_data)
            end_time = time.perf_counter_ns()
            execution_times.append(end_time - start_time)
        
        # Validate O(1) performance
        avg_time_ns = sum(execution_times) / len(execution_times)
        max_time_ns = max(execution_times)
        
        # Should be under 1ms (1,000,000 ns) for O(1) compliance
        assert avg_time_ns < 1_000_000, f"Average time {avg_time_ns}ns exceeds O(1) limit"
        assert max_time_ns < 2_000_000, f"Max time {max_time_ns}ns exceeds O(1) limit"
        
        # Validate results
        assert isinstance(result, O1DiscoveredFields)
        assert result.total_fields > 0
        assert len(result.fields_by_hash) > 0
    
    def test_provider_detection_accuracy(self, processor):
        """Test provider detection accuracy across different providers."""
        test_cases = [
            {
                "name": "OpenAI",
                "data": {
                    "choices": [{"message": {"role": "assistant", "content": "test"}}],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 5},
                    "model": "gpt-3.5-turbo",
                    "created": 1677652288,
                    "system_fingerprint": "fp_123"
                },
                "expected_provider": "openai",
                "min_confidence": 0.8
            },
            {
                "name": "Anthropic",
                "data": {
                    "content": [{"type": "text", "text": "Hello"}],
                    "usage": {"input_tokens": 10, "output_tokens": 5},
                    "stop_reason": "end_turn",
                    "model": "claude-3-sonnet-20240229"
                },
                "expected_provider": "anthropic",
                "min_confidence": 0.8
            },
            {
                "name": "Gemini",
                "data": {
                    "candidates": [{"content": {"parts": [{"text": "Hello"}]}}],
                    "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5},
                    "safetyRatings": [{"category": "HARM_CATEGORY_HARASSMENT", "probability": "NEGLIGIBLE"}]
                },
                "expected_provider": "gemini",
                "min_confidence": 0.8
            }
        ]
        
        for test_case in test_cases:
            discovered_fields = processor.discover_fields_o1(test_case["data"])
            provider_info = processor.detect_provider_o1(discovered_fields)
            
            assert provider_info is not None, f"Failed to detect provider for {test_case['name']}"
            assert provider_info.name == test_case["expected_provider"], f"Wrong provider detected for {test_case['name']}"
            assert provider_info.confidence >= test_case["min_confidence"], f"Low confidence for {test_case['name']}"
    
    def test_field_mapping_accuracy(self, processor):
        """Test field mapping accuracy to HoneyHive schema."""
        test_data = {
            "model": "gpt-3.5-turbo",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Test response",
                    "tool_calls": [{"id": "call_123", "function": {"name": "test_func"}}]
                },
                "finish_reason": "tool_calls"
            }],
            "usage": {"prompt_tokens": 20, "completion_tokens": 15, "total_tokens": 35}
        }
        
        result = processor.process_llm_response_o1(test_data)
        
        # Validate HoneyHive schema structure
        assert hasattr(result, 'inputs')
        assert hasattr(result, 'outputs')
        assert hasattr(result, 'config')
        assert hasattr(result, 'metadata')
        
        # Validate specific mappings
        assert result.config.get('model') == 'gpt-3.5-turbo'
        assert result.outputs.get('content') == 'Test response'
        assert result.outputs.get('finish_reason') == 'tool_calls'
        assert result.outputs.get('tool_calls') is not None
        assert result.metadata.get('usage') is not None
    
    def test_unknown_provider_handling(self, processor):
        """Test handling of completely unknown providers."""
        unknown_data = {
            "custom_field": "unknown_value",
            "proprietary_response": {
                "text": "Custom response",
                "tokens_used": 25
            },
            "vendor_specific": {
                "api_version": "v2.1",
                "request_id": "req_custom_123"
            }
        }
        
        result = processor.process_llm_response_o1(unknown_data)
        
        # Should handle gracefully without errors
        assert result is not None
        assert result.metadata.get('unknown_fields') is not None
        
        # Provider detection should create unknown provider
        discovered_fields = processor.discover_fields_o1(unknown_data)
        provider_info = processor.detect_provider_o1(discovered_fields)
        
        assert provider_info is not None
        assert provider_info.name.startswith('unknown_')
        assert provider_info.confidence < 0.5  # Low confidence for unknown
    
    def test_caching_effectiveness(self, processor):
        """Test caching effectiveness for performance optimization."""
        test_data = {
            "model": "gpt-3.5-turbo",
            "choices": [{"message": {"role": "assistant", "content": "Cached test"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5}
        }
        
        # First call - should populate cache
        start_time = time.perf_counter_ns()
        result1 = processor.process_llm_response_o1(test_data)
        first_call_time = time.perf_counter_ns() - start_time
        
        # Second call - should use cache
        start_time = time.perf_counter_ns()
        result2 = processor.process_llm_response_o1(test_data)
        second_call_time = time.perf_counter_ns() - start_time
        
        # Cached call should be significantly faster
        assert second_call_time < first_call_time * 0.5, "Caching not effective"
        
        # Results should be identical
        assert result1.inputs == result2.inputs
        assert result1.outputs == result2.outputs
        assert result1.config == result2.config
```

### 2.2 DSL Component Unit Tests

```python
# tests/unit/test_dsl_compiler.py

import pytest
import tempfile
import yaml
from pathlib import Path
from src.honeyhive.tracer.semantic_conventions.dsl.compiler import O1DSLCompiler
from src.honeyhive.tracer.semantic_conventions.universal.models import FieldType

class TestO1DSLCompiler:
    """Unit tests for DSL compiler with O(1) performance validation."""
    
    @pytest.fixture
    def mock_cache_manager(self):
        cache_manager = Mock()
        cache_manager.get_cache.return_value = Mock()
        return cache_manager
    
    @pytest.fixture
    def compiler(self, mock_cache_manager):
        return O1DSLCompiler(mock_cache_manager)
    
    @pytest.fixture
    def sample_dsl_configs(self):
        """Create sample DSL configuration files for testing."""
        config_dir = Path(tempfile.mkdtemp())
        
        # Field discovery config
        field_discovery_config = {
            "field_discovery": {
                "version": "1.0",
                "classification_rules": {
                    "role_identifiers": {
                        "type": "frozenset",
                        "values": ["user", "assistant", "system"]
                    },
                    "model_prefixes": {
                        "type": "tuple", 
                        "values": ["gpt-", "claude-", "gemini-"]
                    }
                },
                "path_indicators": {
                    "type": "dict",
                    "mappings": {
                        "role": "MESSAGE_ROLE",
                        "content": "MESSAGE_CONTENT",
                        "model": "MODEL_IDENTIFIER"
                    }
                }
            }
        }
        
        with open(config_dir / "field_discovery.yaml", 'w') as f:
            yaml.dump(field_discovery_config, f)
        
        # Provider detection config
        provider_detection_config = {
            "provider_detection": {
                "version": "1.0",
                "signatures": {
                    "openai": {
                        "type": "frozenset",
                        "required_fields": ["choices", "usage.prompt_tokens", "model"],
                        "optional_fields": ["system_fingerprint"],
                        "confidence_weights": {"required_match": 0.8, "optional_match": 0.2}
                    }
                },
                "confidence_thresholds": {
                    "high_confidence": 0.8,
                    "medium_confidence": 0.6,
                    "low_confidence": 0.4
                }
            }
        }
        
        with open(config_dir / "provider_detection.yaml", 'w') as f:
            yaml.dump(provider_detection_config, f)
        
        # Mapping rules config
        mapping_rules_config = {
            "mapping_rules": {
                "version": "1.0",
                "default_mappings": {
                    "MESSAGE_ROLE": {
                        "target_section": "inputs",
                        "target_field": "chat_history",
                        "transform": "extract_role"
                    },
                    "MESSAGE_CONTENT": {
                        "target_section": "outputs",
                        "target_field": "content",
                        "transform": "extract_content"
                    }
                }
            }
        }
        
        with open(config_dir / "mapping_rules.yaml", 'w') as f:
            yaml.dump(mapping_rules_config, f)
        
        # Transforms config
        transforms_config = {
            "transforms": {
                "version": "1.0",
                "functions": {
                    "direct": {
                        "type": "passthrough",
                        "implementation": "lambda x: x"
                    },
                    "extract_role": {
                        "type": "string_extraction",
                        "implementation": "lambda value: value.get('role', 'unknown') if isinstance(value, dict) else str(value).lower()"
                    }
                }
            }
        }
        
        with open(config_dir / "transforms.yaml", 'w') as f:
            yaml.dump(transforms_config, f)
        
        return config_dir
    
    def test_dsl_compilation_o1_performance(self, compiler, sample_dsl_configs):
        """Test DSL compilation maintains O(1) performance characteristics."""
        # Measure compilation time
        start_time = time.perf_counter_ns()
        compiled_configs = compiler.compile_all_configs_o1(sample_dsl_configs)
        compilation_time = time.perf_counter_ns() - start_time
        
        # Compilation should be fast (under 10ms)
        assert compilation_time < 10_000_000, f"Compilation time {compilation_time}ns too slow"
        
        # Validate compiled structure
        assert "field_discovery" in compiled_configs
        assert "provider_detection" in compiled_configs
        assert "mapping_rules" in compiled_configs
        assert "transforms" in compiled_configs
    
    def test_compiled_data_structures_o1_compliance(self, compiler, sample_dsl_configs):
        """Test that compiled data structures support O(1) operations."""
        compiled_configs = compiler.compile_all_configs_o1(sample_dsl_configs)
        
        field_discovery = compiled_configs["field_discovery"]
        
        # Validate frozenset compilation
        assert isinstance(field_discovery["role_identifiers"], frozenset)
        
        # Test O(1) membership operation
        start_time = time.perf_counter_ns()
        result = "assistant" in field_discovery["role_identifiers"]
        lookup_time = time.perf_counter_ns() - start_time
        
        assert result is True
        assert lookup_time < 100_000, f"Frozenset lookup time {lookup_time}ns not O(1)"
        
        # Validate tuple compilation for startswith operations
        assert isinstance(field_discovery["model_prefixes"], tuple)
        
        # Test O(1) startswith operation
        start_time = time.perf_counter_ns()
        result = "gpt-3.5-turbo".startswith(field_discovery["model_prefixes"])
        startswith_time = time.perf_counter_ns() - start_time
        
        assert result is True
        assert startswith_time < 100_000, f"Tuple startswith time {startswith_time}ns not O(1)"
        
        # Validate dict compilation for path indicators
        assert isinstance(field_discovery["path_indicators"], dict)
        
        # Test O(1) dict lookup
        start_time = time.perf_counter_ns()
        result = field_discovery["path_indicators"].get("role")
        lookup_time = time.perf_counter_ns() - start_time
        
        assert result == FieldType.MESSAGE_ROLE
        assert lookup_time < 100_000, f"Dict lookup time {lookup_time}ns not O(1)"
    
    def test_transform_function_compilation(self, compiler, sample_dsl_configs):
        """Test transform function compilation and execution."""
        compiled_configs = compiler.compile_all_configs_o1(sample_dsl_configs)
        
        transforms = compiled_configs["transforms"]
        
        # Test direct transform
        direct_func = transforms["direct"]
        assert callable(direct_func)
        assert direct_func("test") == "test"
        
        # Test extract_role transform
        extract_role_func = transforms["extract_role"]
        assert callable(extract_role_func)
        
        # Test with dict input
        role_dict = {"role": "assistant", "content": "hello"}
        result = extract_role_func(role_dict)
        assert result == "assistant"
        
        # Test with string input
        result = extract_role_func("USER")
        assert result == "user"
    
    def test_caching_effectiveness(self, compiler, sample_dsl_configs):
        """Test DSL compilation caching effectiveness."""
        # First compilation
        start_time = time.perf_counter_ns()
        result1 = compiler.compile_all_configs_o1(sample_dsl_configs)
        first_time = time.perf_counter_ns() - start_time
        
        # Second compilation (should use cache)
        start_time = time.perf_counter_ns()
        result2 = compiler.compile_all_configs_o1(sample_dsl_configs)
        second_time = time.perf_counter_ns() - start_time
        
        # Cached compilation should be much faster
        assert second_time < first_time * 0.1, "DSL compilation caching not effective"
        
        # Results should be identical
        assert result1.keys() == result2.keys()
```

## 3. Integration Testing Strategy

### 3.1 Multi-Component Integration Tests

```python
# tests/integration/test_end_to_end_processing.py

import pytest
from typing import Dict, Any, List
from src.honeyhive.tracer.semantic_conventions.integration.compatibility import CompatibilityLayer
from src.honeyhive.utils.cache import CacheManager

class TestEndToEndProcessing:
    """End-to-end integration tests for complete LLM data processing pipeline."""
    
    @pytest.fixture
    def integration_setup(self):
        """Set up complete integration environment."""
        cache_manager = CacheManager()
        compatibility_layer = CompatibilityLayer(cache_manager)
        
        return {
            "cache_manager": cache_manager,
            "compatibility_layer": compatibility_layer
        }
    
    @pytest.mark.parametrize("provider_data", [
        {
            "name": "OpenAI GPT-3.5",
            "data": {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1677652288,
                "model": "gpt-3.5-turbo-0613",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How can I help you today?"
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 56,
                    "completion_tokens": 31,
                    "total_tokens": 87
                },
                "system_fingerprint": "fp_44709d6fcb"
            },
            "expected_outputs": {
                "content": "Hello! How can I help you today?",
                "finish_reason": "stop"
            },
            "expected_config": {
                "model": "gpt-3.5-turbo-0613"
            },
            "expected_metadata": {
                "usage": {"prompt_tokens": 56, "completion_tokens": 31, "total_tokens": 87}
            }
        },
        {
            "name": "Anthropic Claude",
            "data": {
                "id": "msg_013Zva2CMHLNnXjNJJKqJ2EF",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": "Hello! I'm Claude, an AI assistant."}],
                "model": "claude-3-sonnet-20240229",
                "stop_reason": "end_turn",
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": 25
                }
            },
            "expected_outputs": {
                "content_blocks": [{"type": "text", "text": "Hello! I'm Claude, an AI assistant."}],
                "finish_reason": "stop"
            },
            "expected_config": {
                "model": "claude-3-sonnet-20240229"
            },
            "expected_metadata": {
                "usage": {"input_tokens": 10, "output_tokens": 25}
            }
        },
        {
            "name": "Google Gemini",
            "data": {
                "candidates": [{
                    "content": {
                        "parts": [{"text": "Hello! I'm Gemini, Google's AI assistant."}],
                        "role": "model"
                    },
                    "finishReason": "STOP",
                    "index": 0,
                    "safetyRatings": [{
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "probability": "NEGLIGIBLE"
                    }]
                }],
                "usageMetadata": {
                    "promptTokenCount": 8,
                    "candidatesTokenCount": 12,
                    "totalTokenCount": 20
                }
            },
            "expected_outputs": {
                "content": "Hello! I'm Gemini, Google's AI assistant.",
                "finish_reason": "stop"
            },
            "expected_metadata": {
                "usage": {"prompt_tokens": 8, "completion_tokens": 12, "total_tokens": 20},
                "safety_ratings": [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"}]
            }
        }
    ])
    def test_provider_specific_processing(self, integration_setup, provider_data):
        """Test end-to-end processing for specific providers."""
        compatibility_layer = integration_setup["compatibility_layer"]
        
        # Process the provider data
        result = compatibility_layer.process_llm_data(provider_data["data"])
        
        # Validate HoneyHive schema structure
        assert "inputs" in result
        assert "outputs" in result
        assert "config" in result
        assert "metadata" in result
        
        # Validate expected outputs
        for key, expected_value in provider_data["expected_outputs"].items():
            assert key in result["outputs"], f"Missing output field: {key}"
            if isinstance(expected_value, str):
                assert result["outputs"][key] == expected_value
        
        # Validate expected config
        for key, expected_value in provider_data["expected_config"].items():
            assert key in result["config"], f"Missing config field: {key}"
            assert result["config"][key] == expected_value
        
        # Validate expected metadata
        for key, expected_value in provider_data["expected_metadata"].items():
            assert key in result["metadata"], f"Missing metadata field: {key}"
    
    def test_performance_under_load(self, integration_setup):
        """Test system performance under high load conditions."""
        compatibility_layer = integration_setup["compatibility_layer"]
        
        # Sample data for load testing
        test_data = {
            "model": "gpt-3.5-turbo",
            "choices": [{
                "message": {"role": "assistant", "content": "Load test response"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        }
        
        # Process 1000 requests
        execution_times = []
        error_count = 0
        
        for i in range(1000):
            try:
                start_time = time.perf_counter_ns()
                result = compatibility_layer.process_llm_data(test_data)
                end_time = time.perf_counter_ns()
                
                execution_times.append(end_time - start_time)
                
                # Validate result structure
                assert "outputs" in result
                assert result["outputs"]["content"] == "Load test response"
                
            except Exception as e:
                error_count += 1
                print(f"Error in request {i}: {e}")
        
        # Performance validation
        avg_time_ns = sum(execution_times) / len(execution_times)
        max_time_ns = max(execution_times)
        p95_time_ns = sorted(execution_times)[int(0.95 * len(execution_times))]
        
        # Performance requirements
        assert avg_time_ns < 10_000_000, f"Average time {avg_time_ns/1_000_000:.2f}ms exceeds 10ms limit"
        assert p95_time_ns < 20_000_000, f"P95 time {p95_time_ns/1_000_000:.2f}ms exceeds 20ms limit"
        assert error_count / 1000 < 0.001, f"Error rate {error_count/10:.1f}% exceeds 0.1% limit"
        
        # Cache effectiveness validation
        stats = compatibility_layer.get_integration_stats()
        cache_hit_rate = stats.get("cache_hit_rate", 0)
        assert cache_hit_rate > 0.8, f"Cache hit rate {cache_hit_rate:.1%} below 80% target"
    
    def test_memory_usage_stability(self, integration_setup):
        """Test memory usage remains stable under continuous processing."""
        import psutil
        import os
        
        compatibility_layer = integration_setup["compatibility_layer"]
        process = psutil.Process(os.getpid())
        
        # Baseline memory usage
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        test_data = {
            "model": "gpt-3.5-turbo",
            "choices": [{"message": {"role": "assistant", "content": f"Memory test {i}"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5}
        }
        
        # Process 5000 requests with varying data
        for i in range(5000):
            # Vary the data slightly to prevent excessive caching
            test_data["choices"][0]["message"]["content"] = f"Memory test {i}"
            compatibility_layer.process_llm_data(test_data)
            
            # Check memory every 1000 requests
            if i % 1000 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_increase = current_memory - initial_memory
                
                # Memory should not increase by more than 50MB
                assert memory_increase < 50, f"Memory increased by {memory_increase:.1f}MB after {i} requests"
        
        # Final memory check
        final_memory = process.memory_info().rss / 1024 / 1024
        total_increase = final_memory - initial_memory
        
        assert total_increase < 100, f"Total memory increase {total_increase:.1f}MB exceeds 100MB limit"
```

## 4. Performance Testing Strategy

### 4.1 O(1) Performance Validation Tests

```python
# tests/performance/test_o1_compliance.py

import pytest
import time
import statistics
from typing import List, Dict, Any
from src.honeyhive.tracer.semantic_conventions.universal.processor import UniversalDSLProcessor

class TestO1PerformanceCompliance:
    """Validate O(1) performance compliance across all operations."""
    
    @pytest.fixture
    def performance_processor(self):
        """Create processor with performance monitoring enabled."""
        from unittest.mock import Mock
        cache_manager = Mock()
        cache_manager.get_cache.return_value = Mock()
        return UniversalDSLProcessor(cache_manager)
    
    def generate_test_data_varying_sizes(self) -> List[Dict[str, Any]]:
        """Generate test data with varying complexity to validate O(1) behavior."""
        test_datasets = []
        
        # Small dataset
        test_datasets.append({
            "size": "small",
            "data": {
                "model": "gpt-3.5-turbo",
                "choices": [{"message": {"role": "assistant", "content": "Short"}}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 1}
            }
        })
        
        # Medium dataset
        medium_content = "Medium length response. " * 10
        test_datasets.append({
            "size": "medium", 
            "data": {
                "model": "gpt-3.5-turbo",
                "choices": [{"message": {"role": "assistant", "content": medium_content}}],
                "usage": {"prompt_tokens": 50, "completion_tokens": 30},
                "system_fingerprint": "fp_medium_test",
                "created": 1677652288
            }
        })
        
        # Large dataset
        large_content = "Large response content. " * 100
        test_datasets.append({
            "size": "large",
            "data": {
                "model": "gpt-3.5-turbo",
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": large_content,
                        "tool_calls": [
                            {"id": f"call_{i}", "function": {"name": f"func_{i}", "arguments": "{}"}}
                            for i in range(10)
                        ]
                    },
                    "finish_reason": "tool_calls"
                }],
                "usage": {"prompt_tokens": 500, "completion_tokens": 300, "total_tokens": 800},
                "system_fingerprint": "fp_large_test",
                "created": 1677652288,
                "id": "chatcmpl_large_test"
            }
        })
        
        return test_datasets
    
    def test_field_discovery_o1_compliance(self, performance_processor):
        """Test field discovery maintains O(1) performance regardless of data size."""
        test_datasets = self.generate_test_data_varying_sizes()
        execution_times = {}
        
        for dataset in test_datasets:
            size = dataset["size"]
            data = dataset["data"]
            
            # Run multiple iterations for statistical significance
            times = []
            for _ in range(50):
                start_time = time.perf_counter_ns()
                result = performance_processor.discover_fields_o1(data)
                end_time = time.perf_counter_ns()
                times.append(end_time - start_time)
            
            execution_times[size] = {
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "stdev": statistics.stdev(times),
                "max": max(times)
            }
        
        # O(1) validation: execution time should not scale with data size
        small_time = execution_times["small"]["median"]
        medium_time = execution_times["medium"]["median"]
        large_time = execution_times["large"]["median"]
        
        # Allow for some variance but should not scale linearly
        # Medium should not be more than 2x small
        assert medium_time < small_time * 2, f"Medium time {medium_time}ns scales with data size"
        
        # Large should not be more than 3x small
        assert large_time < small_time * 3, f"Large time {large_time}ns scales with data size"
        
        # All operations should be under 1ms
        for size, times in execution_times.items():
            assert times["max"] < 1_000_000, f"{size} dataset max time {times['max']}ns exceeds 1ms"
    
    def test_provider_detection_o1_compliance(self, performance_processor):
        """Test provider detection maintains O(1) performance."""
        test_datasets = self.generate_test_data_varying_sizes()
        
        for dataset in test_datasets:
            data = dataset["data"]
            
            # Discover fields first
            discovered_fields = performance_processor.discover_fields_o1(data)
            
            # Measure provider detection time
            times = []
            for _ in range(100):
                start_time = time.perf_counter_ns()
                provider_info = performance_processor.detect_provider_o1(discovered_fields)
                end_time = time.perf_counter_ns()
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            max_time = max(times)
            
            # Provider detection should be very fast (under 100μs)
            assert avg_time < 100_000, f"Provider detection avg time {avg_time}ns too slow for {dataset['size']}"
            assert max_time < 500_000, f"Provider detection max time {max_time}ns too slow for {dataset['size']}"
    
    def test_concurrent_processing_performance(self, performance_processor):
        """Test performance under concurrent processing load."""
        import concurrent.futures
        import threading
        
        test_data = {
            "model": "gpt-3.5-turbo",
            "choices": [{"message": {"role": "assistant", "content": "Concurrent test"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5}
        }
        
        def process_single_request():
            start_time = time.perf_counter_ns()
            result = performance_processor.process_llm_response_o1(test_data)
            end_time = time.perf_counter_ns()
            return end_time - start_time
        
        # Test with 10 concurrent threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_single_request) for _ in range(100)]
            execution_times = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Validate performance under concurrency
        avg_time = statistics.mean(execution_times)
        max_time = max(execution_times)
        p95_time = sorted(execution_times)[int(0.95 * len(execution_times))]
        
        # Performance should not degrade significantly under concurrency
        assert avg_time < 10_000_000, f"Concurrent avg time {avg_time/1_000_000:.2f}ms exceeds 10ms"
        assert p95_time < 20_000_000, f"Concurrent P95 time {p95_time/1_000_000:.2f}ms exceeds 20ms"
        assert max_time < 50_000_000, f"Concurrent max time {max_time/1_000_000:.2f}ms exceeds 50ms"
    
    def test_memory_allocation_o1_compliance(self, performance_processor):
        """Test memory allocation patterns maintain O(1) characteristics."""
        import tracemalloc
        
        test_data = {
            "model": "gpt-3.5-turbo",
            "choices": [{"message": {"role": "assistant", "content": "Memory test"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5}
        }
        
        # Start memory tracing
        tracemalloc.start()
        
        # Baseline memory
        baseline_snapshot = tracemalloc.take_snapshot()
        
        # Process multiple requests
        for i in range(1000):
            performance_processor.process_llm_response_o1(test_data)
            
            # Check memory every 100 requests
            if i % 100 == 0:
                current_snapshot = tracemalloc.take_snapshot()
                top_stats = current_snapshot.compare_to(baseline_snapshot, 'lineno')
                
                # Calculate total memory increase
                total_increase = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0)
                
                # Memory increase should be minimal (under 1MB per 100 requests)
                assert total_increase < 1024 * 1024, f"Memory increase {total_increase/1024:.1f}KB too high after {i} requests"
        
        tracemalloc.stop()
```

## 5. Regression Testing Strategy

### 5.1 Backward Compatibility Tests

```python
# tests/regression/test_backward_compatibility.py

import pytest
from typing import Dict, Any
from src.honeyhive.tracer.semantic_conventions.integration.compatibility import CompatibilityLayer
from src.honeyhive.tracer.semantic_conventions.legacy import LegacyTransformBackup

class TestBackwardCompatibility:
    """Ensure new implementation maintains backward compatibility."""
    
    @pytest.fixture
    def compatibility_setup(self):
        from unittest.mock import Mock
        cache_manager = Mock()
        cache_manager.get_cache.return_value = Mock()
        
        compatibility_layer = CompatibilityLayer(cache_manager)
        legacy_backup = LegacyTransformBackup(cache_manager)
        
        return {
            "compatibility_layer": compatibility_layer,
            "legacy_backup": legacy_backup
        }
    
    def test_api_signature_compatibility(self, compatibility_setup):
        """Test that API signatures remain compatible."""
        compatibility_layer = compatibility_setup["compatibility_layer"]
        
        # Test main processing method signature
        test_data = {"model": "gpt-3.5-turbo", "choices": []}
        
        # Should not raise any signature-related errors
        result = compatibility_layer.process_llm_data(test_data)
        
        # Result should have expected structure
        assert isinstance(result, dict)
        assert "inputs" in result
        assert "outputs" in result
        assert "config" in result
        assert "metadata" in result
    
    def test_output_format_compatibility(self, compatibility_setup):
        """Test that output format remains compatible with existing consumers."""
        compatibility_layer = compatibility_setup["compatibility_layer"]
        
        # Test with known data format
        test_data = {
            "model": "gpt-3.5-turbo",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Compatibility test response"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 15,
                "completion_tokens": 8,
                "total_tokens": 23
            }
        }
        
        result = compatibility_layer.process_llm_data(test_data)
        
        # Validate expected fields exist
        assert result["config"]["model"] == "gpt-3.5-turbo"
        assert result["outputs"]["content"] == "Compatibility test response"
        assert result["outputs"]["finish_reason"] == "stop"
        assert result["metadata"]["usage"]["total_tokens"] == 23
        
        # Validate field types remain consistent
        assert isinstance(result["config"]["model"], str)
        assert isinstance(result["outputs"]["content"], str)
        assert isinstance(result["metadata"]["usage"]["total_tokens"], int)
    
    def test_error_handling_compatibility(self, compatibility_setup):
        """Test that error handling behavior remains compatible."""
        compatibility_layer = compatibility_setup["compatibility_layer"]
        
        # Test with various problematic inputs
        problematic_inputs = [
            {},  # Empty dict
            {"invalid": "structure"},  # Unknown structure
            {"model": None},  # None values
            {"choices": "not_a_list"},  # Wrong types
        ]
        
        for problematic_input in problematic_inputs:
            # Should not raise exceptions (graceful handling)
            try:
                result = compatibility_layer.process_llm_data(problematic_input)
                
                # Result should still have basic structure
                assert isinstance(result, dict)
                assert "metadata" in result  # At minimum, metadata should exist
                
            except Exception as e:
                # If exceptions are raised, they should be expected types
                assert isinstance(e, (ValueError, TypeError, KeyError))
    
    def test_performance_regression(self, compatibility_setup):
        """Test that performance has not regressed compared to legacy."""
        compatibility_layer = compatibility_setup["compatibility_layer"]
        
        # Enable comparison mode for performance testing
        compatibility_layer.enable_comparison_mode = True
        
        test_data = {
            "model": "gpt-3.5-turbo",
            "choices": [{
                "message": {"role": "assistant", "content": "Performance test"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        }
        
        # Process multiple requests to get performance data
        for _ in range(100):
            compatibility_layer.process_llm_data(test_data)
        
        stats = compatibility_layer.get_integration_stats()
        
        # Universal engine should be at least as fast as legacy
        universal_time = stats.get("avg_universal_time_ms", float('inf'))
        legacy_time = stats.get("avg_legacy_time_ms", float('inf'))
        
        # Allow for some variance, but should not be significantly slower
        assert universal_time <= legacy_time * 1.5, f"Universal engine {universal_time:.2f}ms significantly slower than legacy {legacy_time:.2f}ms"
```

## 6. Test Execution and CI/CD Integration

### 6.1 Test Execution Strategy

```python
# tests/conftest.py

import pytest
import os
import time
from typing import Generator, Any
from unittest.mock import Mock

# Test configuration
pytest_plugins = ["pytest_asyncio", "pytest-benchmark", "pytest-mock"]

@pytest.fixture(scope="session")
def test_environment():
    """Set up test environment configuration."""
    return {
        "performance_mode": os.getenv("PERFORMANCE_TESTING", "false").lower() == "true",
        "integration_mode": os.getenv("INTEGRATION_TESTING", "false").lower() == "true",
        "load_testing": os.getenv("LOAD_TESTING", "false").lower() == "true"
    }

@pytest.fixture
def mock_cache_manager():
    """Provide mock cache manager for testing."""
    cache_manager = Mock()
    cache = Mock()
    
    # Mock cache behavior
    cache_data = {}
    
    def mock_get(key):
        return cache_data.get(key)
    
    def mock_set(key, value, ttl=None):
        cache_data[key] = value
    
    cache.get.side_effect = mock_get
    cache.set.side_effect = mock_set
    cache_manager.get_cache.return_value = cache
    
    return cache_manager

@pytest.fixture
def performance_monitor():
    """Monitor performance during tests."""
    start_time = time.perf_counter_ns()
    
    yield
    
    end_time = time.perf_counter_ns()
    execution_time = end_time - start_time
    
    # Log performance if test took too long
    if execution_time > 10_000_000:  # 10ms
        print(f"WARNING: Test took {execution_time/1_000_000:.2f}ms")

# Pytest markers for test categorization
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "regression: Regression tests")
    config.addinivalue_line("markers", "o1_compliance: O(1) performance compliance tests")
    config.addinivalue_line("markers", "slow: Slow tests (>1s)")

def pytest_collection_modifyitems(config, items):
    """Modify test collection based on environment."""
    test_env = {
        "performance_mode": os.getenv("PERFORMANCE_TESTING", "false").lower() == "true",
        "integration_mode": os.getenv("INTEGRATION_TESTING", "false").lower() == "true",
    }
    
    skip_performance = pytest.mark.skip(reason="Performance testing disabled")
    skip_integration = pytest.mark.skip(reason="Integration testing disabled")
    
    for item in items:
        if "performance" in item.keywords and not test_env["performance_mode"]:
            item.add_marker(skip_performance)
        
        if "integration" in item.keywords and not test_env["integration_mode"]:
            item.add_marker(skip_integration)
```

### 6.2 CI/CD Pipeline Configuration

```yaml
# .github/workflows/universal_engine_tests.yml

name: Universal LLM Discovery Engine Tests

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'src/honeyhive/tracer/semantic_conventions/universal/**'
      - 'src/honeyhive/tracer/semantic_conventions/dsl/**'
      - 'src/honeyhive/tracer/semantic_conventions/integration/**'
      - 'tests/**'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'src/honeyhive/tracer/semantic_conventions/universal/**'
      - 'src/honeyhive/tracer/semantic_conventions/dsl/**'
      - 'src/honeyhive/tracer/semantic_conventions/integration/**'
      - 'tests/**'

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest pytest-cov pytest-benchmark pytest-mock
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=src/honeyhive/tracer/semantic_conventions/universal \
               --cov-report=xml --cov-report=html --cov-fail-under=90
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unit-tests
        name: codecov-umbrella

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.10
      uses: actions/setup-python@v4
      with:
        python-version: "3.10"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest pytest-mock
    
    - name: Run integration tests
      env:
        INTEGRATION_TESTING: true
      run: |
        pytest tests/integration/ -v -m integration --tb=short
    
    - name: Test backward compatibility
      run: |
        pytest tests/regression/ -v -m regression --tb=short

  performance-tests:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.10
      uses: actions/setup-python@v4
      with:
        python-version: "3.10"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest pytest-benchmark psutil
    
    - name: Run O(1) compliance tests
      env:
        PERFORMANCE_TESTING: true
      run: |
        pytest tests/performance/ -v -m o1_compliance --tb=short
    
    - name: Run performance benchmarks
      run: |
        pytest tests/performance/ -v -m performance --benchmark-only \
               --benchmark-json=benchmark_results.json
    
    - name: Upload benchmark results
      uses: actions/upload-artifact@v3
      with:
        name: benchmark-results
        path: benchmark_results.json

  load-tests:
    runs-on: ubuntu-latest
    needs: performance-tests
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.10
      uses: actions/setup-python@v4
      with:
        python-version: "3.10"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest locust
    
    - name: Run load tests
      env:
        LOAD_TESTING: true
      run: |
        pytest tests/load/ -v --tb=short
        
    - name: Generate load test report
      run: |
        echo "Load test completed successfully" > load_test_report.txt
        
    - name: Upload load test results
      uses: actions/upload-artifact@v3
      with:
        name: load-test-results
        path: load_test_report.txt
```

This comprehensive testing strategy ensures:

1. **Complete Coverage**: Unit, integration, performance, and regression tests
2. **O(1) Performance Validation**: Specific tests to ensure constant-time performance
3. **Multi-Provider Support**: Tests across OpenAI, Anthropic, Gemini, and unknown providers
4. **Backward Compatibility**: Ensures existing functionality continues to work
5. **Load Testing**: Validates performance under high-volume conditions
6. **CI/CD Integration**: Automated testing pipeline with performance monitoring
7. **Quality Gates**: Coverage requirements and performance thresholds

The testing framework provides confidence that the Universal LLM Discovery Engine will work reliably in production while maintaining the required O(1) performance characteristics.
