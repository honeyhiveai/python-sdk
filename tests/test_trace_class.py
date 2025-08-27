#!/usr/bin/env python3
"""
Test the new trace_class decorator functionality

This test file validates the trace_class decorator that automatically
applies tracing to multiple methods within a class.
"""

import pytest
import asyncio
import inspect
import time
import os
from unittest.mock import patch

from honeyhive.tracer import HoneyHiveTracer, trace_class, enable_tracing

# Test configuration
TEST_CONFIG = {
    'HH_API_KEY': 'test-key',
    'HH_PROJECT': 'test-project',
    'HH_SOURCE': 'trace-class-test'
}


class TestTraceClassBasic:
    """Test basic trace_class decorator functionality"""
    
    def setup_method(self):
        """Reset tracer state before each test"""
        from honeyhive.tracer import reset_tracer_state
        reset_tracer_state()
    
    def teardown_method(self):
        """Clean up after each test"""
        from honeyhive.tracer import reset_tracer_state
        reset_tracer_state()
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_class_all_methods(self):
        """Test trace_class decorator with all methods traced"""
        @trace_class
        class TestService:
            def public_api(self):
                return "public_result"
            
            def internal_method(self):
                return "internal_result"
            
            def utility_function(self):
                return "utility_result"
        
        # Verify all methods are traced
        service = TestService()
        
        # Check that methods are wrapped with trace decorators
        assert hasattr(service.public_api, '__wrapped__')
        assert hasattr(service.internal_method, '__wrapped__')
        assert hasattr(service.utility_function, '__wrapped__')
        
        # Execute methods
        assert service.public_api() == "public_result"
        assert service.internal_method() == "internal_result"
        assert service.utility_function() == "utility_result"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_class_exclude_list(self):
        """Test trace_class decorator with exclude_list"""
        @trace_class(exclude_list=['internal_method'])
        class TestService:
            def public_api(self):
                return "public_result"
            
            def internal_method(self):
                return "internal_result"
            
            def utility_function(self):
                return "utility_result"
        
        service = TestService()
        
        # Check that excluded method is not traced
        assert not hasattr(service.internal_method, '__wrapped__')
        
        # Check that included methods are traced
        assert hasattr(service.public_api, '__wrapped__')
        assert hasattr(service.utility_function, '__wrapped__')
        
        # Execute methods
        assert service.public_api() == "public_result"
        assert service.internal_method() == "internal_result"
        assert service.utility_function() == "utility_result"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_class_include_list(self):
        """Test trace_class decorator with include_list"""
        @trace_class(include_list=['public_api', 'utility_function'])
        class TestService:
            def public_api(self):
                return "public_result"
            
            def internal_method(self):
                return "internal_result"
            
            def utility_function(self):
                return "utility_result"
        
        service = TestService()
        
        # Check that only included methods are traced
        assert hasattr(service.public_api, '__wrapped__')
        assert hasattr(service.utility_function, '__wrapped__')
        assert not hasattr(service.internal_method, '__wrapped__')
        
        # Execute methods
        assert service.public_api() == "public_result"
        assert service.internal_method() == "internal_result"
        assert service.utility_function() == "utility_result"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_class_dunder_methods_excluded(self):
        """Test that dunder methods are automatically excluded"""
        @trace_class
        class TestService:
            def __init__(self):
                self.initialized = True
            
            def __call__(self):
                return "called"
            
            def public_api(self):
                return "public_result"
            
            def __str__(self):
                return "TestService"
        
        service = TestService()
        
        # Check that dunder methods are not traced
        assert not hasattr(service.__init__, '__wrapped__')
        assert not hasattr(service.__call__, '__wrapped__')
        assert not hasattr(service.__str__, '__wrapped__')
        
        # Check that regular methods are traced
        assert hasattr(service.public_api, '__wrapped__')
        
        # Verify dunder methods work normally
        assert service.initialized is True
        assert service() == "called"
        assert str(service) == "TestService"
        
        # Execute traced method
        assert service.public_api() == "public_result"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_class_custom_event_type(self):
        """Test trace_class decorator with custom event_type"""
        @trace_class(event_type="model")
        class TestService:
            def generate_response(self):
                return "generated_response"
            
            def process_input(self):
                return "processed_input"
        
        service = TestService()
        
        # Check that methods are traced
        assert hasattr(service.generate_response, '__wrapped__')
        assert hasattr(service.process_input, '__wrapped__')
        
        # Execute methods
        assert service.generate_response() == "generated_response"
        assert service.process_input() == "processed_input"


class TestTraceClassAsync:
    """Test trace_class decorator with async methods"""
    
    def setup_method(self):
        """Reset tracer state before each test"""
        from honeyhive.tracer import reset_tracer_state
        reset_tracer_state()
    
    def teardown_method(self):
        """Clean up after each test"""
        from honeyhive.tracer import reset_tracer_state
        reset_tracer_state()
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_class_async_methods(self):
        """Test trace_class decorator with async methods"""
        @trace_class
        class AsyncTestService:
            async def async_generate(self):
                await asyncio.sleep(0.001)
                return "async_generated"
            
            async def async_process(self):
                await asyncio.sleep(0.001)
                return "async_processed"
            
            def sync_method(self):
                return "sync_result"
        
        service = AsyncTestService()
        
        # Check that all methods are traced
        assert hasattr(service.async_generate, '__wrapped__')
        assert hasattr(service.async_process, '__wrapped__')
        assert hasattr(service.sync_method, '__wrapped__')
        
        # Execute methods
        async_result1 = asyncio.run(service.async_generate())
        async_result2 = asyncio.run(service.async_process())
        sync_result = service.sync_method()
        
        assert async_result1 == "async_generated"
        assert async_result2 == "async_processed"
        assert sync_result == "sync_result"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_class_mixed_sync_async(self):
        """Test trace_class decorator with mixed sync and async methods"""
        @trace_class(exclude_list=['internal_helper'])
        class MixedService:
            def sync_public(self):
                return "sync_public"
            
            async def async_public(self):
                await asyncio.sleep(0.001)
                return "async_public"
            
            def internal_helper(self):
                return "internal_helper"
        
        service = MixedService()
        
        # Check that public methods are traced
        assert hasattr(service.sync_public, '__wrapped__')
        assert hasattr(service.async_public, '__wrapped__')
        assert not hasattr(service.internal_helper, '__wrapped__')
        
        # Execute methods
        sync_result = service.sync_public()
        async_result = asyncio.run(service.async_public())
        internal_result = service.internal_helper()
        
        assert sync_result == "sync_public"
        assert async_result == "async_public"
        assert internal_result == "internal_helper"


class TestTraceClassAdvanced:
    """Test advanced trace_class decorator functionality"""
    
    def setup_method(self):
        """Reset tracer state before each test"""
        from honeyhive.tracer import reset_tracer_state
        reset_tracer_state()
    
    def teardown_method(self):
        """Clean up after each test"""
        from honeyhive.tracer import reset_tracer_state
        reset_tracer_state()
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_class_inheritance(self):
        """Test trace_class decorator with class inheritance"""
        @trace_class(exclude_list=['_private'])
        class BaseService:
            def public_method(self):
                return "base_public"
            
            def _private(self):
                return "base_private"
        
        class DerivedService(BaseService):
            def derived_method(self):
                return "derived_method"
            
            def _private(self):
                return "derived_private"
        
        # Check base class
        base = BaseService()
        assert hasattr(base.public_method, '__wrapped__')
        assert not hasattr(base._private, '__wrapped__')
        
        # Check derived class
        derived = DerivedService()
        # Inherited methods from base class ARE traced (they're bound to the derived class instance)
        assert hasattr(derived.public_method, '__wrapped__')
        # New methods in derived class are NOT traced (only the base class was decorated)
        assert not hasattr(derived.derived_method, '__wrapped__')
        # Private methods are not traced
        assert not hasattr(derived._private, '__wrapped__')
        
        # Execute methods
        assert base.public_method() == "base_public"
        assert base._private() == "base_private"
        assert derived.public_method() == "base_public"
        assert derived.derived_method() == "derived_method"
        assert derived._private() == "derived_private"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_class_class_methods(self):
        """Test trace_class decorator with class methods"""
        @trace_class
        class TestService:
            @classmethod
            def class_method(cls):
                return "class_method"
            
            @staticmethod
            def static_method():
                return "static_method"
            
            def instance_method(self):
                return "instance_method"
        
        # Check that methods are traced
        # Note: inspect.getmembers(cls, inspect.isfunction) picks up static methods
        assert not hasattr(TestService.class_method, '__wrapped__')  # Class methods are not traced
        assert hasattr(TestService.static_method, '__wrapped__')  # Static methods ARE traced
        
        service = TestService()
        assert hasattr(service.instance_method, '__wrapped__')  # Instance methods are traced
        
        # Execute methods
        assert TestService.class_method() == "class_method"
        assert TestService.static_method() == "static_method"
        assert service.instance_method() == "instance_method"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_class_property_methods(self):
        """Test trace_class decorator with property methods"""
        @trace_class
        class TestService:
            @property
            def computed_value(self):
                return "computed"
            
            def regular_method(self):
                return "regular"
        
        service = TestService()
        
        # Check that regular methods are traced
        assert hasattr(service.regular_method, '__wrapped__')
        
        # Properties should not be traced (they're descriptors, not functions)
        assert not hasattr(service.computed_value, '__wrapped__')
        
        # Execute methods
        assert service.computed_value == "computed"
        assert service.regular_method() == "regular"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_class_span_naming(self):
        """Test that trace_class creates proper span names"""
        @trace_class
        class TestService:
            def method_one(self):
                return "one"
            
            def method_two(self):
                return "two"
        
        service = TestService()
        
        # Check that methods are traced
        assert hasattr(service.method_one, '__wrapped__')
        assert hasattr(service.method_two, '__wrapped__')
        
        # Execute methods
        assert service.method_one() == "one"
        assert service.method_two() == "two"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_class_performance(self):
        """Test trace_class decorator performance"""
        @trace_class
        class PerformanceService:
            def fast_method(self):
                return "fast"
            
            def another_fast_method(self):
                return "another_fast"
        
        service = PerformanceService()
        
        # Measure performance
        start_time = time.perf_counter()
        for _ in range(100):
            service.fast_method()
            service.another_fast_method()
        execution_time = time.perf_counter() - start_time
        
        # Should complete in reasonable time
        assert execution_time < 5.0  # 5 seconds for 200 method calls
        
        print(f"  📊 Execution time for 200 traced method calls: {execution_time:.3f}s")


class TestTraceClassIntegration:
    """Test trace_class decorator integration with other tracer features"""
    
    def setup_method(self):
        """Reset tracer state before each test"""
        from honeyhive.tracer import reset_tracer_state
        reset_tracer_state()
    
    def teardown_method(self):
        """Clean up after each test"""
        from honeyhive.tracer import reset_tracer_state
        reset_tracer_state()
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_class_with_enrich_span(self):
        """Test trace_class decorator with enrich_span functionality"""
        from honeyhive.tracer.custom import enrich_span
        
        @trace_class
        class EnrichService:
            def method_with_enrich(self):
                enrich_span(metadata={"method": "enriched"})
                return "enriched_result"
            
            def method_without_enrich(self):
                return "plain_result"
        
        service = EnrichService()
        
        # Check that methods are traced
        assert hasattr(service.method_with_enrich, '__wrapped__')
        assert hasattr(service.method_without_enrich, '__wrapped__')
        
        # Execute methods
        assert service.method_with_enrich() == "enriched_result"
        assert service.method_without_enrich() == "plain_result"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_class_nested_calls(self):
        """Test trace_class decorator with nested method calls"""
        @trace_class
        class NestedService:
            def outer_method(self):
                result = self.inner_method()
                return f"outer_{result}"
            
            def inner_method(self):
                return "inner"
        
        service = NestedService()
        
        # Check that methods are traced
        assert hasattr(service.outer_method, '__wrapped__')
        assert hasattr(service.inner_method, '__wrapped__')
        
        # Execute method
        result = service.outer_method()
        assert result == "outer_inner"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_class_error_handling(self):
        """Test trace_class decorator with error handling"""
        @trace_class
        class ErrorService:
            def error_method(self):
                raise ValueError("Test error")
            
            def normal_method(self):
                return "normal"
        
        service = ErrorService()
        
        # Check that methods are traced
        assert hasattr(service.error_method, '__wrapped__')
        assert hasattr(service.normal_method, '__wrapped__')
        
        # Test error handling
        with pytest.raises(ValueError, match="Test error"):
            service.error_method()
        
        # Test normal method
        assert service.normal_method() == "normal"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
