#!/usr/bin/env python3
"""
Test the new async-conditional trace decorator behavior

This test file specifically validates the new unified @trace decorator
that automatically handles both sync and async functions.
"""

import pytest
import asyncio
import inspect
import time
from unittest.mock import patch
import os

from honeyhive.tracer import HoneyHiveTracer, trace, atrace, enable_tracing

# Test configuration
TEST_CONFIG = {
    'HH_API_KEY': 'test-key',
    'HH_PROJECT': 'test-project',
    'HH_SOURCE': 'async-conditional-test'
}


class TestAsyncConditionalBehavior:
    """Test the new async-conditional trace decorator behavior"""
    
    def setup_method(self):
        """Reset tracer state before each test"""
        from honeyhive.tracer import reset_tracer_state
        reset_tracer_state()
    
    def teardown_method(self):
        """Clean up after each test"""
        from honeyhive.tracer import reset_tracer_state
        reset_tracer_state()
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_decorator_sync_function(self):
        """Test @trace decorator with synchronous functions"""
        @trace
        def sync_function():
            return "sync_result"
        
        # Verify function type detection
        assert not inspect.iscoroutinefunction(sync_function)
        
        # Execute function
        result = sync_function()
        assert result == "sync_result"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_decorator_async_function(self):
        """Test @trace decorator with asynchronous functions"""
        @trace
        async def async_function():
            await asyncio.sleep(0.001)
            return "async_result"
        
        # Verify function type detection
        assert inspect.iscoroutinefunction(async_function)
        
        # Execute function
        result = asyncio.run(async_function())
        assert result == "async_result"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_decorator_with_parameters(self):
        """Test @trace decorator with parameters for both sync and async"""
        @trace(event_type="tool", event_name="sync_tool")
        def sync_tool():
            return "sync_tool_result"
        
        @trace(event_type="model", event_name="async_model")
        async def async_model():
            await asyncio.sleep(0.001)
            return "async_model_result"
        
        # Verify function types
        assert not inspect.iscoroutinefunction(sync_tool)
        assert inspect.iscoroutinefunction(async_model)
        
        # Execute functions
        sync_result = sync_tool()
        async_result = asyncio.run(async_model())
        
        assert sync_result == "sync_tool_result"
        assert async_result == "async_model_result"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_decorator_chaining(self):
        """Test @trace decorator chaining with both sync and async"""
        @trace(event_name="outer")
        @trace(event_name="inner")
        def chained_sync():
            return "chained_sync"
        
        @trace(event_name="outer")
        @trace(event_name="inner")
        async def chained_async():
            await asyncio.sleep(0.001)
            return "chained_async"
        
        # Verify function types
        assert not inspect.iscoroutinefunction(chained_sync)
        assert inspect.iscoroutinefunction(chained_async)
        
        # Execute functions
        sync_result = chained_sync()
        async_result = asyncio.run(chained_async())
        
        assert sync_result == "chained_sync"
        assert async_result == "chained_async"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_decorator_class_methods(self):
        """Test @trace decorator with class methods (both sync and async)"""
        class TestClass:
            @trace
            def sync_method(self):
                return "sync_method"
            
            @trace
            async def async_method(self):
                await asyncio.sleep(0.001)
                return "async_method"
            
            @classmethod
            @trace
            def sync_class_method(cls):
                return "sync_class_method"
            
            @classmethod
            @trace
            async def async_class_method(cls):
                await asyncio.sleep(0.001)
                return "async_class_method"
        
        obj = TestClass()
        
        # Verify function types
        assert not inspect.iscoroutinefunction(obj.sync_method)
        assert inspect.iscoroutinefunction(obj.async_method)
        assert not inspect.iscoroutinefunction(TestClass.sync_class_method)
        assert inspect.iscoroutinefunction(TestClass.async_class_method)
        
        # Execute methods
        sync_result = obj.sync_method()
        async_result = asyncio.run(obj.async_method())
        sync_class_result = TestClass.sync_class_method()
        async_class_result = asyncio.run(TestClass.async_class_method())
        
        assert sync_result == "sync_method"
        assert async_result == "async_method"
        assert sync_class_result == "sync_class_method"
        assert async_class_result == "async_class_method"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_decorator_error_handling(self):
        """Test @trace decorator error handling for both sync and async"""
        @trace
        def sync_error_function():
            raise ValueError("sync error")
        
        @trace
        async def async_error_function():
            await asyncio.sleep(0.001)
            raise ValueError("async error")
        
        # Test sync error
        with pytest.raises(ValueError, match="sync error"):
            sync_error_function()
        
        # Test async error
        with pytest.raises(ValueError, match="async error"):
            asyncio.run(async_error_function())
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_atrace_decorator_legacy_support(self):
        """Test @atrace decorator legacy support (should still work)"""
        @atrace
        async def legacy_async_function():
            await asyncio.sleep(0.001)
            return "legacy_result"
        
        # Verify function type
        assert inspect.iscoroutinefunction(legacy_async_function)
        
        # Execute function
        result = asyncio.run(legacy_async_function())
        assert result == "legacy_result"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_atrace_decorator_sync_function_error(self):
        """Test that @atrace decorator raises error for sync functions"""
        with pytest.raises(ValueError, match="@atrace decorator can only be used with async functions"):
            @atrace
            def sync_function():
                return "this should fail"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_atrace_decorator_with_parameters(self):
        """Test @atrace decorator with parameters (legacy support)"""
        @atrace(event_type="chain", event_name="legacy_chain")
        async def legacy_chain_function():
            await asyncio.sleep(0.001)
            return "legacy_chain_result"
        
        # Verify function type
        assert inspect.iscoroutinefunction(legacy_chain_function)
        
        # Execute function
        result = asyncio.run(legacy_chain_function())
        assert result == "legacy_chain_result"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_mixed_decorator_usage(self):
        """Test mixed usage of @trace and @atrace decorators"""
        @trace(event_type="tool")
        def sync_tool():
            return "sync_tool"
        
        @atrace(event_type="model")
        async def async_model():
            await asyncio.sleep(0.001)
            return "async_model"
        
        @trace(event_type="chain")
        async def async_chain():
            await asyncio.sleep(0.001)
            return "async_chain"
        
        # Verify function types
        assert not inspect.iscoroutinefunction(sync_tool)
        assert inspect.iscoroutinefunction(async_model)
        assert inspect.iscoroutinefunction(async_chain)
        
        # Execute functions
        sync_result = sync_tool()
        async_model_result = asyncio.run(async_model())
        async_chain_result = asyncio.run(async_chain())
        
        assert sync_result == "sync_tool"
        assert async_model_result == "async_model"
        assert async_chain_result == "async_chain"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_decorator_performance_comparison(self):
        """Test performance comparison between sync and async decorators"""
        @trace
        def fast_sync_function():
            return "fast_sync"
        
        @trace
        async def fast_async_function():
            return "fast_async"
        
        # Measure sync performance
        start_time = time.perf_counter()
        for _ in range(1000):
            fast_sync_function()
        sync_time = time.perf_counter() - start_time
        
        # Measure async performance
        start_time = time.perf_counter()
        for _ in range(1000):
            asyncio.run(fast_async_function())
        async_time = time.perf_counter() - start_time
        
        # Both should be fast
        assert sync_time < 10.0  # Should complete in under 10 seconds (includes tracer init)
        assert async_time < 15.0  # Should complete in under 15 seconds (includes tracer init)
        
        # Both should complete in reasonable time
        print(f"  📊 Sync time: {sync_time:.3f}s")
        print(f"  📊 Async time: {async_time:.3f}s")
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_decorator_function_signature_preservation(self):
        """Test that decorators preserve function signatures"""
        @trace
        def function_with_args(a, b, c=10, *, d=20):
            return a + b + c + d
        
        @trace
        async def async_function_with_args(a, b, c=10, *, d=20):
            await asyncio.sleep(0.001)
            return a + b + c + d
        
        # Check signatures
        sync_sig = inspect.signature(function_with_args)
        async_sig = inspect.signature(async_function_with_args)
        
        # Both should have the same parameters
        assert list(sync_sig.parameters.keys()) == ['a', 'b', 'c', 'd']
        assert list(async_sig.parameters.keys()) == ['a', 'b', 'c', 'd']
        
        # Test function calls
        sync_result = function_with_args(1, 2, 3, d=4)
        async_result = asyncio.run(async_function_with_args(1, 2, 3, d=4))
        
        assert sync_result == 10  # 1 + 2 + 3 + 4
        assert async_result == 10  # 1 + 2 + 3 + 4


class TestAsyncConditionalIntegration:
    """Test integration of async-conditional behavior with other tracer features"""
    
    def setup_method(self):
        """Reset tracer state before each test"""
        from honeyhive.tracer import reset_tracer_state
        reset_tracer_state()
    
    def teardown_method(self):
        """Clean up after each test"""
        from honeyhive.tracer import reset_tracer_state
        reset_tracer_state()
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_decorator_with_enrich_span(self):
        """Test @trace decorator with enrich_span functionality"""
        from honeyhive.tracer.custom import enrich_span
        
        @trace(event_type="tool")
        def sync_tool_with_enrich():
            enrich_span(metadata={"tool_type": "calculator"})
            return "enriched_sync_result"
        
        @trace(event_type="model")
        async def async_model_with_enrich():
            enrich_span(metadata={"model_type": "gpt-4"})
            await asyncio.sleep(0.001)
            return "enriched_async_result"
        
        # Execute functions
        sync_result = sync_tool_with_enrich()
        async_result = asyncio.run(async_model_with_enrich())
        
        assert sync_result == "enriched_sync_result"
        assert async_result == "enriched_async_result"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_decorator_with_enrich_session(self):
        """Test @trace decorator with enrich_session functionality"""
        from honeyhive.tracer import enrich_session
        
        @trace(event_type="chain")
        def sync_chain_with_session():
            enrich_session(metadata={"chain_type": "qa"})
            return "session_enriched_sync"
        
        @trace(event_type="chain")
        async def async_chain_with_session():
            enrich_session(metadata={"chain_type": "qa"})
            await asyncio.sleep(0.001)
            return "session_enriched_async"
        
        # Execute functions
        sync_result = sync_chain_with_session()
        async_result = asyncio.run(async_chain_with_session())
        
        assert sync_result == "session_enriched_sync"
        assert async_result == "session_enriched_async"
    
    @patch.dict(os.environ, TEST_CONFIG, clear=True)
    def test_trace_decorator_nested_calls(self):
        """Test @trace decorator with nested function calls"""
        @trace(event_type="tool")
        def inner_sync_tool():
            return "inner_sync"
        
        @trace(event_type="model")
        async def inner_async_model():
            await asyncio.sleep(0.001)
            return "inner_async"
        
        @trace(event_type="chain")
        def outer_sync_chain():
            sync_result = inner_sync_tool()
            return f"outer_sync_{sync_result}"
        
        @trace(event_type="chain")
        async def outer_async_chain():
            async_result = await inner_async_model()
            return f"outer_async_{async_result}"
        
        # Execute functions
        sync_result = outer_sync_chain()
        async_result = asyncio.run(outer_async_chain())
        
        assert sync_result == "outer_sync_inner_sync"
        assert async_result == "outer_async_inner_async"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
