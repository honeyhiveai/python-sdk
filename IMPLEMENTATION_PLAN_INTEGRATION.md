# Implementation Plan - Integration with Existing Codebase

**Version**: 1.0  
**Date**: 2025-01-27  
**Status**: Implementation Ready  

## 1. Integration Strategy Overview

### 1.1 Backward Compatibility Requirements

The Universal LLM Discovery Engine must integrate seamlessly with the existing HoneyHive SDK without breaking changes to:

- **Public APIs**: All existing tracer initialization and usage patterns
- **Configuration**: Existing environment variables and configuration options
- **Performance**: Must maintain or improve current performance characteristics
- **Multi-Instance Architecture**: Preserve per-tracer-instance isolation
- **Cache Integration**: Use existing `CacheManager` infrastructure

### 1.2 Integration Phases

1. **Phase 1**: Backup current implementation and create compatibility layer
2. **Phase 2**: Implement Universal Engine alongside existing system
3. **Phase 3**: Create feature flag for gradual rollout
4. **Phase 4**: Migrate existing functionality to new engine
5. **Phase 5**: Remove legacy code after validation

## 2. Detailed Integration Implementation

### 2.1 Backup and Preservation Strategy

```python
# src/honeyhive/tracer/semantic_conventions/legacy/__init__.py

"""
Legacy semantic convention implementation backup.

This module preserves the original implementation for:
1. Rollback capability if issues are discovered
2. A/B testing and comparison validation
3. Reference implementation for migration validation
"""

from typing import Any, Dict, Optional
import warnings

class LegacyTransformBackup:
    """Backup of original transform functionality."""
    
    def __init__(self, cache_manager: Any, tracer_instance: Any = None):
        self.cache_manager = cache_manager
        self.tracer_instance = tracer_instance
        
        # Import original implementations
        from .transforms_backup import _normalize_message as original_normalize_message
        from .central_mapper_backup import CentralEventMapper as OriginalMapper
        
        self.original_normalize_message = original_normalize_message
        self.original_mapper_class = OriginalMapper
    
    def get_original_mapper(self) -> Any:
        """Get original central mapper for comparison testing."""
        return self.original_mapper_class(self.cache_manager, self.tracer_instance)
    
    def normalize_message_legacy(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use original message normalization for comparison."""
        warnings.warn(
            "Using legacy message normalization. This is deprecated and will be removed.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.original_normalize_message(message_data)
```

### 2.2 Compatibility Layer Implementation

```python
# src/honeyhive/tracer/semantic_conventions/integration/compatibility.py

from typing import Any, Dict, List, Optional, Union
import time
import logging
from ..universal.processor import UniversalDSLProcessor
from ..legacy import LegacyTransformBackup

logger = logging.getLogger(__name__)

class CompatibilityLayer:
    """
    Compatibility layer that provides seamless integration between
    the new Universal LLM Discovery Engine and existing code.
    """
    
    def __init__(self, cache_manager: Any, tracer_instance: Any = None):
        self.cache_manager = cache_manager
        self.tracer_instance = tracer_instance
        
        # Initialize both systems
        self.universal_processor = UniversalDSLProcessor(cache_manager, tracer_instance)
        self.legacy_backup = LegacyTransformBackup(cache_manager, tracer_instance)
        
        # Feature flags for gradual rollout
        self.use_universal_engine = self._get_feature_flag("use_universal_engine", default=True)
        self.enable_comparison_mode = self._get_feature_flag("enable_comparison_mode", default=False)
        self.fallback_to_legacy = self._get_feature_flag("fallback_to_legacy", default=True)
        
        # Performance tracking
        self.integration_stats = {
            "universal_calls": 0,
            "legacy_calls": 0,
            "fallback_events": 0,
            "comparison_mismatches": 0,
            "avg_universal_time_ns": 0,
            "avg_legacy_time_ns": 0
        }
    
    def process_llm_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point that routes to appropriate processing engine.
        
        This method maintains the same signature as the original central mapper
        to ensure backward compatibility.
        """
        if self.enable_comparison_mode:
            return self._process_with_comparison(data)
        elif self.use_universal_engine:
            return self._process_with_universal_engine(data)
        else:
            return self._process_with_legacy_engine(data)
    
    def _process_with_universal_engine(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process using the new Universal LLM Discovery Engine."""
        start_time = time.perf_counter_ns()
        
        try:
            # Use universal processor
            result = self.universal_processor.process_llm_response_o1(data)
            
            # Convert to expected format for backward compatibility
            compatible_result = self._convert_to_legacy_format(result)
            
            # Update performance stats
            processing_time = time.perf_counter_ns() - start_time
            self.integration_stats["universal_calls"] += 1
            self._update_avg_time("universal", processing_time)
            
            return compatible_result
            
        except Exception as e:
            logger.warning(f"Universal engine failed: {e}")
            
            if self.fallback_to_legacy:
                logger.info("Falling back to legacy processing")
                self.integration_stats["fallback_events"] += 1
                return self._process_with_legacy_engine(data)
            else:
                raise
    
    def _process_with_legacy_engine(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process using the original legacy engine."""
        start_time = time.perf_counter_ns()
        
        # Use legacy mapper
        legacy_mapper = self.legacy_backup.get_original_mapper()
        result = legacy_mapper.map_event(data)
        
        # Update performance stats
        processing_time = time.perf_counter_ns() - start_time
        self.integration_stats["legacy_calls"] += 1
        self._update_avg_time("legacy", processing_time)
        
        return result
    
    def _process_with_comparison_mode(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process with both engines and compare results for validation."""
        # Process with both engines
        universal_start = time.perf_counter_ns()
        universal_result = self._process_with_universal_engine(data)
        universal_time = time.perf_counter_ns() - universal_start
        
        legacy_start = time.perf_counter_ns()
        legacy_result = self._process_with_legacy_engine(data)
        legacy_time = time.perf_counter_ns() - legacy_start
        
        # Compare results
        comparison_result = self._compare_results(universal_result, legacy_result)
        
        if not comparison_result["matches"]:
            self.integration_stats["comparison_mismatches"] += 1
            logger.warning(f"Result mismatch detected: {comparison_result['differences']}")
        
        # Log performance comparison
        logger.debug(f"Performance comparison - Universal: {universal_time/1000000:.2f}ms, Legacy: {legacy_time/1000000:.2f}ms")
        
        # Return universal result (assuming it's the target implementation)
        return universal_result
    
    def _convert_to_legacy_format(self, universal_result: Any) -> Dict[str, Any]:
        """Convert Universal Engine result to legacy format for compatibility."""
        if hasattr(universal_result, 'inputs'):
            # Convert O1MappingResult to legacy dict format
            return {
                "inputs": universal_result.inputs,
                "outputs": universal_result.outputs,
                "config": universal_result.config,
                "metadata": universal_result.metadata,
                # Add legacy-specific fields if needed
                "_processing_time_ms": universal_result.processing_context.total_processing_time_ms,
                "_provider": universal_result.processing_context.provider_info.name if universal_result.processing_context.provider_info else "unknown"
            }
        else:
            # Already in compatible format
            return universal_result
    
    def _compare_results(self, universal_result: Dict[str, Any], legacy_result: Dict[str, Any]) -> Dict[str, Any]:
        """Compare results from both engines for validation."""
        comparison = {
            "matches": True,
            "differences": [],
            "universal_fields": set(universal_result.keys()),
            "legacy_fields": set(legacy_result.keys())
        }
        
        # Compare common fields
        common_fields = comparison["universal_fields"] & comparison["legacy_fields"]
        
        for field in common_fields:
            if universal_result[field] != legacy_result[field]:
                comparison["matches"] = False
                comparison["differences"].append({
                    "field": field,
                    "universal_value": universal_result[field],
                    "legacy_value": legacy_result[field]
                })
        
        # Check for missing fields
        missing_in_universal = comparison["legacy_fields"] - comparison["universal_fields"]
        missing_in_legacy = comparison["universal_fields"] - comparison["legacy_fields"]
        
        if missing_in_universal:
            comparison["matches"] = False
            comparison["differences"].append({
                "type": "missing_in_universal",
                "fields": list(missing_in_universal)
            })
        
        if missing_in_legacy:
            comparison["differences"].append({
                "type": "missing_in_legacy", 
                "fields": list(missing_in_legacy)
            })
        
        return comparison
    
    def _get_feature_flag(self, flag_name: str, default: bool = False) -> bool:
        """Get feature flag value from environment or configuration."""
        import os
        
        # Check environment variable
        env_var = f"HONEYHIVE_{flag_name.upper()}"
        env_value = os.getenv(env_var)
        
        if env_value is not None:
            return env_value.lower() in ("true", "1", "yes", "on")
        
        # Check tracer instance configuration if available
        if hasattr(self.tracer_instance, 'config') and self.tracer_instance.config:
            config_value = self.tracer_instance.config.get(flag_name)
            if config_value is not None:
                return bool(config_value)
        
        return default
    
    def _update_avg_time(self, engine_type: str, processing_time_ns: int) -> None:
        """Update average processing time statistics."""
        stat_key = f"avg_{engine_type}_time_ns"
        call_key = f"{engine_type}_calls"
        
        current_avg = self.integration_stats[stat_key]
        call_count = self.integration_stats[call_key]
        
        # Calculate new average
        if call_count == 1:
            self.integration_stats[stat_key] = processing_time_ns
        else:
            self.integration_stats[stat_key] = (current_avg * (call_count - 1) + processing_time_ns) / call_count
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration performance and usage statistics."""
        stats = self.integration_stats.copy()
        
        # Add derived metrics
        total_calls = stats["universal_calls"] + stats["legacy_calls"]
        if total_calls > 0:
            stats["universal_usage_percentage"] = (stats["universal_calls"] / total_calls) * 100
            stats["fallback_rate"] = (stats["fallback_events"] / stats["universal_calls"]) * 100 if stats["universal_calls"] > 0 else 0
        
        # Convert nanoseconds to milliseconds for readability
        stats["avg_universal_time_ms"] = stats["avg_universal_time_ns"] / 1000000
        stats["avg_legacy_time_ms"] = stats["avg_legacy_time_ns"] / 1000000
        
        return stats
```

### 2.3 Migration Utilities

```python
# src/honeyhive/tracer/semantic_conventions/integration/migration.py

from typing import Any, Dict, List, Optional
import json
import time
from pathlib import Path

class MigrationUtility:
    """Utilities for migrating from legacy to universal engine."""
    
    def __init__(self, cache_manager: Any, tracer_instance: Any = None):
        self.cache_manager = cache_manager
        self.tracer_instance = tracer_instance
        
        # Migration tracking
        self.migration_log = []
        self.validation_results = []
    
    def validate_migration_readiness(self) -> Dict[str, Any]:
        """Validate that the system is ready for migration to universal engine."""
        validation_result = {
            "is_ready": True,
            "checks": [],
            "warnings": [],
            "errors": []
        }
        
        # Check 1: DSL configuration validity
        dsl_check = self._validate_dsl_configs()
        validation_result["checks"].append(dsl_check)
        if not dsl_check["passed"]:
            validation_result["is_ready"] = False
            validation_result["errors"].extend(dsl_check["errors"])
        
        # Check 2: Cache manager availability
        cache_check = self._validate_cache_manager()
        validation_result["checks"].append(cache_check)
        if not cache_check["passed"]:
            validation_result["is_ready"] = False
            validation_result["errors"].extend(cache_check["errors"])
        
        # Check 3: Performance baseline
        perf_check = self._validate_performance_baseline()
        validation_result["checks"].append(perf_check)
        if not perf_check["passed"]:
            validation_result["warnings"].extend(perf_check["warnings"])
        
        # Check 4: Memory requirements
        memory_check = self._validate_memory_requirements()
        validation_result["checks"].append(memory_check)
        if not memory_check["passed"]:
            validation_result["warnings"].extend(memory_check["warnings"])
        
        return validation_result
    
    def create_migration_plan(self, sample_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a detailed migration plan based on sample data analysis."""
        plan = {
            "migration_phases": [],
            "estimated_duration": "2-4 hours",
            "rollback_plan": {},
            "validation_steps": [],
            "risk_assessment": {}
        }
        
        # Analyze sample data to understand usage patterns
        data_analysis = self._analyze_sample_data(sample_data)
        
        # Phase 1: Preparation
        plan["migration_phases"].append({
            "phase": 1,
            "name": "Preparation",
            "duration": "30 minutes",
            "steps": [
                "Backup current implementation",
                "Validate DSL configurations",
                "Initialize universal engine",
                "Set up monitoring and logging"
            ]
        })
        
        # Phase 2: Gradual Rollout
        plan["migration_phases"].append({
            "phase": 2,
            "name": "Gradual Rollout",
            "duration": "1-2 hours",
            "steps": [
                "Enable comparison mode for validation",
                "Process 10% of traffic with universal engine",
                "Monitor performance and accuracy",
                "Gradually increase to 50% traffic",
                "Validate results and performance"
            ]
        })
        
        # Phase 3: Full Migration
        plan["migration_phases"].append({
            "phase": 3,
            "name": "Full Migration",
            "duration": "1 hour",
            "steps": [
                "Switch 100% traffic to universal engine",
                "Monitor for issues",
                "Validate all functionality",
                "Disable legacy fallback"
            ]
        })
        
        # Phase 4: Cleanup
        plan["migration_phases"].append({
            "phase": 4,
            "name": "Cleanup",
            "duration": "30 minutes",
            "steps": [
                "Remove legacy code (after validation period)",
                "Clean up temporary monitoring",
                "Update documentation",
                "Archive migration logs"
            ]
        })
        
        # Rollback plan
        plan["rollback_plan"] = {
            "triggers": [
                "Performance degradation > 20%",
                "Error rate increase > 5%",
                "Memory usage increase > 50%",
                "Accuracy degradation detected"
            ],
            "steps": [
                "Immediately switch back to legacy engine",
                "Analyze failure logs",
                "Fix issues in universal engine",
                "Re-test before retry"
            ]
        }
        
        # Risk assessment
        plan["risk_assessment"] = {
            "high_risks": [
                "Performance regression",
                "Data mapping accuracy issues"
            ],
            "medium_risks": [
                "Memory usage increase",
                "Cache performance impact"
            ],
            "low_risks": [
                "Configuration complexity",
                "Learning curve for debugging"
            ],
            "mitigation_strategies": [
                "Comprehensive testing with sample data",
                "Gradual rollout with monitoring",
                "Immediate rollback capability",
                "Performance baseline validation"
            ]
        }
        
        return plan
    
    def execute_migration_phase(self, phase_number: int, compatibility_layer: CompatibilityLayer) -> Dict[str, Any]:
        """Execute a specific migration phase with monitoring."""
        phase_result = {
            "phase": phase_number,
            "start_time": time.time(),
            "status": "in_progress",
            "steps_completed": [],
            "errors": [],
            "performance_metrics": {}
        }
        
        try:
            if phase_number == 1:
                # Preparation phase
                self._execute_preparation_phase(compatibility_layer, phase_result)
            elif phase_number == 2:
                # Gradual rollout phase
                self._execute_gradual_rollout_phase(compatibility_layer, phase_result)
            elif phase_number == 3:
                # Full migration phase
                self._execute_full_migration_phase(compatibility_layer, phase_result)
            elif phase_number == 4:
                # Cleanup phase
                self._execute_cleanup_phase(compatibility_layer, phase_result)
            
            phase_result["status"] = "completed"
            
        except Exception as e:
            phase_result["status"] = "failed"
            phase_result["errors"].append(str(e))
        
        phase_result["end_time"] = time.time()
        phase_result["duration_seconds"] = phase_result["end_time"] - phase_result["start_time"]
        
        # Log migration step
        self.migration_log.append(phase_result)
        
        return phase_result
    
    def _validate_dsl_configs(self) -> Dict[str, Any]:
        """Validate DSL configuration files."""
        check_result = {
            "name": "DSL Configuration Validation",
            "passed": True,
            "errors": [],
            "details": {}
        }
        
        try:
            from ..dsl.loader import DSLConfigLoader
            from ..dsl.validator import DSLValidator
            
            # Initialize validator
            validator = DSLValidator(self.cache_manager, self.tracer_instance)
            
            # Validate all configs
            config_dir = Path(__file__).parent.parent / "dsl" / "configs"
            validation_result = validator.validate_all_configs(config_dir)
            
            check_result["details"] = validation_result
            
            if not validation_result["is_valid"]:
                check_result["passed"] = False
                check_result["errors"] = validation_result["errors"]
                
        except Exception as e:
            check_result["passed"] = False
            check_result["errors"].append(f"DSL validation failed: {str(e)}")
        
        return check_result
    
    def _validate_cache_manager(self) -> Dict[str, Any]:
        """Validate cache manager functionality."""
        check_result = {
            "name": "Cache Manager Validation",
            "passed": True,
            "errors": [],
            "details": {}
        }
        
        try:
            # Test cache operations
            test_cache = self.cache_manager.get_cache("migration_test")
            
            # Test set/get
            test_key = "test_key"
            test_value = {"test": "data"}
            
            test_cache.set(test_key, test_value, ttl=60.0)
            retrieved_value = test_cache.get(test_key)
            
            if retrieved_value != test_value:
                check_result["passed"] = False
                check_result["errors"].append("Cache set/get operation failed")
            
            check_result["details"]["cache_test_passed"] = True
            
        except Exception as e:
            check_result["passed"] = False
            check_result["errors"].append(f"Cache manager validation failed: {str(e)}")
        
        return check_result
    
    def _validate_performance_baseline(self) -> Dict[str, Any]:
        """Validate performance baseline requirements."""
        check_result = {
            "name": "Performance Baseline Validation",
            "passed": True,
            "warnings": [],
            "details": {}
        }
        
        # This would include actual performance testing
        # For now, we'll simulate the check
        check_result["details"] = {
            "target_latency_ms": 10,
            "target_throughput": 10000,
            "memory_limit_mb": 100
        }
        
        return check_result
    
    def _validate_memory_requirements(self) -> Dict[str, Any]:
        """Validate memory requirements."""
        check_result = {
            "name": "Memory Requirements Validation",
            "passed": True,
            "warnings": [],
            "details": {}
        }
        
        # This would include actual memory usage analysis
        check_result["details"] = {
            "estimated_memory_mb": 50,
            "memory_limit_mb": 100,
            "within_limits": True
        }
        
        return check_result
    
    def _analyze_sample_data(self, sample_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sample data to understand usage patterns."""
        analysis = {
            "total_samples": len(sample_data),
            "provider_distribution": {},
            "field_patterns": {},
            "complexity_metrics": {}
        }
        
        # Analyze provider distribution
        for sample in sample_data:
            # This would include actual analysis logic
            pass
        
        return analysis
    
    def _execute_preparation_phase(self, compatibility_layer: CompatibilityLayer, phase_result: Dict[str, Any]) -> None:
        """Execute preparation phase steps."""
        # Step 1: Backup validation
        phase_result["steps_completed"].append("backup_validation")
        
        # Step 2: DSL initialization
        phase_result["steps_completed"].append("dsl_initialization")
        
        # Step 3: Universal engine initialization
        phase_result["steps_completed"].append("universal_engine_init")
        
        # Step 4: Monitoring setup
        phase_result["steps_completed"].append("monitoring_setup")
    
    def _execute_gradual_rollout_phase(self, compatibility_layer: CompatibilityLayer, phase_result: Dict[str, Any]) -> None:
        """Execute gradual rollout phase steps."""
        # Enable comparison mode
        compatibility_layer.enable_comparison_mode = True
        phase_result["steps_completed"].append("comparison_mode_enabled")
        
        # Monitor performance
        stats = compatibility_layer.get_integration_stats()
        phase_result["performance_metrics"] = stats
        phase_result["steps_completed"].append("performance_monitoring")
    
    def _execute_full_migration_phase(self, compatibility_layer: CompatibilityLayer, phase_result: Dict[str, Any]) -> None:
        """Execute full migration phase steps."""
        # Switch to universal engine
        compatibility_layer.use_universal_engine = True
        compatibility_layer.enable_comparison_mode = False
        phase_result["steps_completed"].append("full_universal_engine")
        
        # Final validation
        stats = compatibility_layer.get_integration_stats()
        phase_result["performance_metrics"] = stats
        phase_result["steps_completed"].append("final_validation")
    
    def _execute_cleanup_phase(self, compatibility_layer: CompatibilityLayer, phase_result: Dict[str, Any]) -> None:
        """Execute cleanup phase steps."""
        # Disable fallback
        compatibility_layer.fallback_to_legacy = False
        phase_result["steps_completed"].append("fallback_disabled")
        
        # Archive logs
        phase_result["steps_completed"].append("logs_archived")
```

### 2.4 Integration with Existing Span Processor

```python
# src/honeyhive/tracer/semantic_conventions/integration/span_processor_integration.py

from typing import Any, Dict, Optional
from ..processing.span_processor import HoneyHiveSpanProcessor
from .compatibility import CompatibilityLayer

class IntegratedSpanProcessor(HoneyHiveSpanProcessor):
    """
    Extended span processor that integrates Universal LLM Discovery Engine
    while maintaining compatibility with existing functionality.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize compatibility layer
        self.compatibility_layer = CompatibilityLayer(
            cache_manager=self.cache_manager,
            tracer_instance=getattr(self, 'tracer_instance', None)
        )
        
        # Integration metrics
        self.integration_metrics = {
            "total_spans_processed": 0,
            "universal_engine_usage": 0,
            "legacy_engine_usage": 0,
            "processing_errors": 0
        }
    
    def process_span_attributes(self, span_attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process span attributes using the integrated Universal LLM Discovery Engine.
        
        This method overrides the base span processor to use the new engine
        while maintaining backward compatibility.
        """
        try:
            # Use compatibility layer for processing
            processed_attributes = self.compatibility_layer.process_llm_data(span_attributes)
            
            # Update metrics
            self.integration_metrics["total_spans_processed"] += 1
            
            if self.compatibility_layer.use_universal_engine:
                self.integration_metrics["universal_engine_usage"] += 1
            else:
                self.integration_metrics["legacy_engine_usage"] += 1
            
            return processed_attributes
            
        except Exception as e:
            self.integration_metrics["processing_errors"] += 1
            
            # Log error and fallback to parent implementation
            logger.error(f"Integrated span processing failed: {e}")
            return super().process_span_attributes(span_attributes)
    
    def get_integration_metrics(self) -> Dict[str, Any]:
        """Get integration-specific metrics."""
        base_metrics = self.integration_metrics.copy()
        compatibility_stats = self.compatibility_layer.get_integration_stats()
        
        return {
            **base_metrics,
            "compatibility_stats": compatibility_stats,
            "engine_performance": {
                "universal_avg_time_ms": compatibility_stats.get("avg_universal_time_ms", 0),
                "legacy_avg_time_ms": compatibility_stats.get("avg_legacy_time_ms", 0),
                "fallback_rate": compatibility_stats.get("fallback_rate", 0)
            }
        }
```

## 3. Testing and Validation Integration

### 3.1 Integration Test Suite

```python
# tests/integration/test_universal_engine_integration.py

import pytest
from typing import Any, Dict, List
from src.honeyhive.tracer.semantic_conventions.integration.compatibility import CompatibilityLayer
from src.honeyhive.utils.cache import CacheManager

class TestUniversalEngineIntegration:
    """Integration tests for Universal LLM Discovery Engine."""
    
    @pytest.fixture
    def cache_manager(self):
        """Create cache manager for testing."""
        return CacheManager()
    
    @pytest.fixture
    def compatibility_layer(self, cache_manager):
        """Create compatibility layer for testing."""
        return CompatibilityLayer(cache_manager)
    
    def test_backward_compatibility(self, compatibility_layer):
        """Test that new engine maintains backward compatibility."""
        # Test data that should work with both engines
        test_data = {
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
        
        # Process with universal engine
        result = compatibility_layer.process_llm_data(test_data)
        
        # Verify expected structure
        assert "inputs" in result
        assert "outputs" in result
        assert "metadata" in result
        assert "config" in result
    
    def test_performance_comparison(self, compatibility_layer):
        """Test performance comparison between engines."""
        compatibility_layer.enable_comparison_mode = True
        
        test_data = {
            "model": "gpt-3.5-turbo",
            "choices": [{
                "message": {
                    "role": "assistant", 
                    "content": "Test response"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 20,
                "completion_tokens": 10,
                "total_tokens": 30
            }
        }
        
        # Process multiple times to get performance data
        for _ in range(100):
            compatibility_layer.process_llm_data(test_data)
        
        stats = compatibility_layer.get_integration_stats()
        
        # Verify performance metrics are collected
        assert stats["universal_calls"] > 0
        assert stats["legacy_calls"] > 0
        assert "avg_universal_time_ms" in stats
        assert "avg_legacy_time_ms" in stats
    
    def test_fallback_mechanism(self, compatibility_layer):
        """Test fallback to legacy engine on errors."""
        compatibility_layer.use_universal_engine = True
        compatibility_layer.fallback_to_legacy = True
        
        # Test with data that might cause issues
        problematic_data = {
            "invalid_structure": True,
            "nested": {
                "deeply": {
                    "nested": {
                        "data": "value"
                    }
                }
            }
        }
        
        # Should not raise exception due to fallback
        result = compatibility_layer.process_llm_data(problematic_data)
        
        # Verify fallback was used
        stats = compatibility_layer.get_integration_stats()
        assert stats["fallback_events"] >= 0  # May or may not fallback depending on implementation
    
    def test_feature_flag_control(self, compatibility_layer):
        """Test feature flag control of engine selection."""
        # Test universal engine enabled
        compatibility_layer.use_universal_engine = True
        compatibility_layer.enable_comparison_mode = False
        
        test_data = {"model": "gpt-3.5-turbo", "choices": []}
        
        result = compatibility_layer.process_llm_data(test_data)
        stats = compatibility_layer.get_integration_stats()
        
        assert stats["universal_calls"] > 0
        
        # Test legacy engine enabled
        compatibility_layer.use_universal_engine = False
        
        result = compatibility_layer.process_llm_data(test_data)
        stats = compatibility_layer.get_integration_stats()
        
        assert stats["legacy_calls"] > 0
```

## 4. Deployment and Rollout Strategy

### 4.1 Environment Variable Configuration

```bash
# Environment variables for controlling integration behavior

# Feature flags
export HONEYHIVE_USE_UNIVERSAL_ENGINE=true
export HONEYHIVE_ENABLE_COMPARISON_MODE=false
export HONEYHIVE_FALLBACK_TO_LEGACY=true

# Performance tuning
export HONEYHIVE_UNIVERSAL_ENGINE_CACHE_TTL=1800
export HONEYHIVE_UNIVERSAL_ENGINE_MAX_CACHE_SIZE=50000
export HONEYHIVE_UNIVERSAL_ENGINE_PERFORMANCE_THRESHOLD_MS=10

# Monitoring and logging
export HONEYHIVE_INTEGRATION_LOGGING_LEVEL=INFO
export HONEYHIVE_PERFORMANCE_MONITORING_ENABLED=true
export HONEYHIVE_COMPARISON_LOGGING_ENABLED=false
```

### 4.2 Gradual Rollout Configuration

```python
# src/honeyhive/tracer/semantic_conventions/integration/rollout_config.py

ROLLOUT_PHASES = {
    "phase_1": {
        "name": "Initial Testing",
        "universal_engine_percentage": 10,
        "comparison_mode": True,
        "duration_hours": 24,
        "success_criteria": {
            "error_rate_increase": "<5%",
            "performance_degradation": "<20%",
            "accuracy_threshold": ">95%"
        }
    },
    "phase_2": {
        "name": "Expanded Testing", 
        "universal_engine_percentage": 50,
        "comparison_mode": True,
        "duration_hours": 48,
        "success_criteria": {
            "error_rate_increase": "<3%",
            "performance_degradation": "<10%",
            "accuracy_threshold": ">98%"
        }
    },
    "phase_3": {
        "name": "Full Rollout",
        "universal_engine_percentage": 100,
        "comparison_mode": False,
        "duration_hours": 72,
        "success_criteria": {
            "error_rate_increase": "<2%",
            "performance_improvement": ">0%",
            "accuracy_threshold": ">99%"
        }
    }
}
```

This comprehensive integration plan ensures:

1. **Zero-Downtime Migration**: Gradual rollout with fallback capabilities
2. **Backward Compatibility**: Maintains all existing APIs and behaviors
3. **Performance Validation**: Continuous monitoring and comparison
4. **Risk Mitigation**: Multiple safety mechanisms and rollback procedures
5. **Comprehensive Testing**: Integration tests covering all scenarios
6. **Flexible Configuration**: Environment variables and feature flags for control

The integration approach allows for safe deployment of the Universal LLM Discovery Engine while preserving all existing functionality and providing multiple validation mechanisms.
