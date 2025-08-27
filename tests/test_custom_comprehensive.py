#!/usr/bin/env python3
"""
Comprehensive tests for custom.py

These tests cover all the functionality in custom.py
to improve coverage from 28% to 40%+.
"""

import pytest
import inspect
import asyncio
import json
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeyhive.tracer.custom import (
    FunctionInstrumentor,
    trace,
    atrace,
    trace_class,
    enrich_span,
    disable_tracing,
    enable_tracing,
    _get_instrumentor,
    _create_traced_function,
    _apply_trace_class
)


class TestFunctionInstrumentor:
    """Test FunctionInstrumentor class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.instrumentor = FunctionInstrumentor()
    
    def test_initialization(self):
        """Test basic initialization"""
        assert hasattr(self.instrumentor, '_tracing_disabled')
        assert hasattr(self.instrumentor, 'trace')
        assert self.instrumentor._tracing_disabled is False
    
    def test_disable_tracing(self):
        """Test disabling tracing"""
        self.instrumentor.disable_tracing()
        assert self.instrumentor._tracing_disabled is True
    
    def test_enable_tracing(self):
        """Test enabling tracing"""
        self.instrumentor.disable_tracing()
        self.instrumentor.enable_tracing()
        assert self.instrumentor._tracing_disabled is False
    
    def test_instrumentation_dependencies(self):
        """Test instrumentation dependencies"""
        deps = self.instrumentor.instrumentation_dependencies()
        assert deps == ()
    
    def test_uninstrument(self):
        """Test uninstrument method"""
        # Should not raise any errors
        self.instrumentor._uninstrument()
    
    def test_set_span_attributes_dict(self):
        """Test setting span attributes with dictionary"""
        mock_span = Mock()
        
        test_dict = {"key1": "value1", "key2": "value2"}
        self.instrumentor._set_span_attributes(mock_span, "test_prefix", test_dict)
        
        # Should call set_attribute for each dict item
        assert mock_span.set_attribute.call_count == 2
        mock_span.set_attribute.assert_any_call("test_prefix.key1", "value1")
        mock_span.set_attribute.assert_any_call("test_prefix.key2", "value2")
    
    def test_set_span_attributes_list(self):
        """Test setting span attributes with list"""
        mock_span = Mock()
        
        test_list = ["item1", "item2"]
        self.instrumentor._set_span_attributes(mock_span, "test_prefix", test_list)
        
        # Should call set_attribute for each list item
        assert mock_span.set_attribute.call_count == 2
        mock_span.set_attribute.assert_any_call("test_prefix.0", "item1")
        mock_span.set_attribute.assert_any_call("test_prefix.1", "item2")
    
    def test_set_span_attributes_primitive_types(self):
        """Test setting span attributes with primitive types"""
        mock_span = Mock()
        
        # Test int
        self.instrumentor._set_span_attributes(mock_span, "test_int", 42)
        mock_span.set_attribute.assert_called_with("test_int", 42)
        
        # Test bool
        mock_span.reset_mock()
        self.instrumentor._set_span_attributes(mock_span, "test_bool", True)
        mock_span.set_attribute.assert_called_with("test_bool", True)
        
        # Test float
        mock_span.reset_mock()
        self.instrumentor._set_span_attributes(mock_span, "test_float", 3.14)
        mock_span.set_attribute.assert_called_with("test_float", 3.14)
        
        # Test string
        mock_span.reset_mock()
        self.instrumentor._set_span_attributes(mock_span, "test_string", "hello")
        mock_span.set_attribute.assert_called_with("test_string", "hello")
    
    def test_set_span_attributes_complex_type(self):
        """Test setting span attributes with complex types"""
        mock_span = Mock()
        
        # Test with a complex object that can be JSON serialized
        class ComplexObject:
            def __init__(self, value):
                self.value = value
        
        complex_obj = ComplexObject("test")
        
        with patch('json.dumps') as mock_json_dumps:
            mock_json_dumps.return_value = '{"value": "test"}'
            self.instrumentor._set_span_attributes(mock_span, "test_complex", complex_obj)
            
            mock_json_dumps.assert_called_once()
            mock_span.set_attribute.assert_called_with("test_complex", '{"value": "test"}')
    
    def test_set_span_attributes_json_fallback(self):
        """Test setting span attributes with JSON serialization fallback"""
        mock_span = Mock()
        
        # Test with an object that can't be JSON serialized
        class NonSerializableObject:
            def __str__(self):
                return "non_serializable"
        
        non_serializable = NonSerializableObject()
        
        with patch('json.dumps') as mock_json_dumps:
            mock_json_dumps.side_effect = TypeError("Can't serialize")
            self.instrumentor._set_span_attributes(mock_span, "test_fallback", non_serializable)
            
            mock_span.set_attribute.assert_called_with("test_fallback", "non_serializable")
    
    def test_parse_and_match_success(self):
        """Test successful template parsing and matching"""
        template = "Hello {{name}}, you are {{age}} years old"
        text = "Hello John, you are 30 years old"
        
        result = self.instrumentor._parse_and_match(template, text)
        
        assert result == {"name": "John", "age": "30"}
    
    def test_parse_and_match_failure(self):
        """Test template parsing failure"""
        template = "Hello {{name}}, you are {{age}} years old"
        text = "Hello John, you are 30"  # Missing "years old"
        
        with pytest.raises(ValueError, match="The text does not match the template"):
            self.instrumentor._parse_and_match(template, text)
    
    def test_set_prompt_template(self):
        """Test setting prompt template attributes"""
        mock_span = Mock()
        
        prompt_template = {
            "template": [{"content": "Hello {{name}}"}],
            "prompt": [{"content": "Hello John"}]
        }
        
        with patch.object(self.instrumentor, '_parse_and_match') as mock_parse:
            mock_parse.return_value = {"name": "John"}
            self.instrumentor._set_prompt_template(mock_span, prompt_template)
            
            # Should set various attributes
            assert mock_span.set_attribute.call_count >= 3
    
    def test_enrich_span(self):
        """Test span enrichment"""
        mock_span = Mock()
        
        config = {"model": "gpt-4"}
        metadata = {"user_id": "123"}
        metrics = {"accuracy": 0.95}
        feedback = {"rating": 5}
        inputs = {"prompt": "Hello"}
        outputs = {"response": "Hi there"}
        error = "Some error"
        
        with patch.object(self.instrumentor, '_set_span_attributes') as mock_set_attr:
            self.instrumentor._enrich_span(
                mock_span, config, metadata, metrics, feedback, inputs, outputs, error
            )
            
            # Should call _set_span_attributes for each parameter
            assert mock_set_attr.call_count == 7


class TestTraceDecorator:
    """Test trace decorator class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.instrumentor = FunctionInstrumentor()
        self.trace_decorator = self.instrumentor.trace
    
    def test_trace_decorator_initialization(self):
        """Test trace decorator initialization"""
        decorator = self.trace_decorator(
            event_type="model",
            config={"model": "gpt-4"},
            metadata={"user_id": "123"},
            event_name="test_function"
        )
        
        assert decorator.event_type == "model"
        assert decorator.config == {"model": "gpt-4"}
        assert decorator.metadata == {"user_id": "123"}
        assert decorator.event_name == "test_function"
    
    def test_trace_decorator_with_function(self):
        """Test trace decorator with function"""
        def test_func(x, y):
            return x + y
        
        decorator = self.trace_decorator(test_func)
        assert decorator.func == test_func
    
    def test_trace_decorator_callable(self):
        """Test trace decorator callable behavior"""
        def test_func(x, y):
            return x + y
        
        decorator = self.trace_decorator(test_func)
        result = decorator(5, 3)
        assert result == 8
    
    def test_trace_decorator_descriptor(self):
        """Test trace decorator descriptor protocol"""
        class TestClass:
            @self.trace_decorator
            def test_method(self, x):
                return x * 2
        
        obj = TestClass()
        result = obj.test_method(5)
        assert result == 10
    
    def test_setup_span(self):
        """Test span setup"""
        def test_func(name, age, prompt_template=None):
            return f"Hello {name}"
        
        decorator = self.trace_decorator(test_func)
        mock_span = Mock()
        
        with patch.object(self.instrumentor, '_set_prompt_template') as mock_set_prompt:
            decorator._setup_span(mock_span, ["John", 30], {})
            
            # Should set input parameters
            assert mock_span.set_attribute.call_count >= 2
    
    def test_handle_result(self):
        """Test result handling"""
        def test_func():
            return "test result"
        
        decorator = self.trace_decorator(test_func)
        mock_span = Mock()
        
        with patch.object(self.instrumentor, '_set_span_attributes') as mock_set_attr:
            result = decorator._handle_result(mock_span, "test result")
            
            assert result == "test result"
            mock_set_attr.assert_called_with(mock_span, "honeyhive_outputs.result", "test result")
    
    def test_handle_exception(self):
        """Test exception handling"""
        def test_func():
            return "test result"
        
        decorator = self.trace_decorator(test_func)
        mock_span = Mock()
        
        test_exception = Exception("Test error")
        
        with patch.object(self.instrumentor, '_set_span_attributes') as mock_set_attr:
            with pytest.raises(Exception, match="Test error"):
                decorator._handle_exception(mock_span, test_exception)
            
            mock_set_attr.assert_called_with(mock_span, "honeyhive_error", "Test error")


class TestATraceDecorator:
    """Test atrace decorator class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.instrumentor = FunctionInstrumentor()
        self.atrace_decorator = self.instrumentor.atrace
    
    def test_atrace_decorator_initialization(self):
        """Test atrace decorator initialization"""
        async def test_func():
            return "async result"
        
        decorator = self.atrace_decorator(test_func)
        assert decorator.func == test_func
    
    def test_atrace_decorator_callable(self):
        """Test atrace decorator callable behavior"""
        async def test_func(x, y):
            return x + y
        
        decorator = self.atrace_decorator(test_func)
        
        async def test_call():
            result = await decorator(5, 3)
            return result
        
        result = asyncio.run(test_call())
        assert result == 8


class TestTraceFunctions:
    """Test trace function decorators"""
    
    def test_trace_decorator_basic(self):
        """Test basic trace decorator"""
        @trace
        def test_func(x):
            return x * 2
        
        result = test_func(5)
        assert result == 10
    
    def test_trace_decorator_with_params(self):
        """Test trace decorator with parameters"""
        @trace(event_type="model", event_name="test_function")
        def test_func(x):
            return x * 2
        
        result = test_func(5)
        assert result == 10
    
    def test_trace_decorator_async(self):
        """Test trace decorator with async function"""
        @trace
        async def test_func(x):
            return x * 2
        
        async def test_call():
            return await test_func(5)
        
        result = asyncio.run(test_call())
        assert result == 10
    
    def test_atrace_decorator_basic(self):
        """Test basic atrace decorator"""
        @atrace
        async def test_func(x):
            return x * 2
        
        async def test_call():
            return await test_func(5)
        
        result = asyncio.run(test_call())
        assert result == 10
    
    def test_atrace_decorator_with_params(self):
        """Test atrace decorator with parameters"""
        @atrace(event_type="model", event_name="test_function")
        async def test_func(x):
            return x * 2
        
        async def test_call():
            return await test_func(5)
        
        result = asyncio.run(test_call())
        assert result == 10
    
    def test_atrace_decorator_sync_function_error(self):
        """Test atrace decorator with sync function (should raise error)"""
        # The error is raised during decoration, not during function call
        with pytest.raises(ValueError, match="@atrace decorator can only be used with async functions"):
            @atrace
            def test_func(x):
                return x * 2


class TestTraceClass:
    """Test trace_class decorator"""
    
    def test_trace_class_basic(self):
        """Test basic trace_class decorator"""
        @trace_class
        class TestClass:
            def method1(self):
                return "method1"
            
            def method2(self):
                return "method2"
        
        obj = TestClass()
        assert obj.method1() == "method1"
        assert obj.method2() == "method2"
    
    def test_trace_class_with_include_list(self):
        """Test trace_class with include list"""
        @trace_class(include_list=["method1"])
        class TestClass:
            def method1(self):
                return "method1"
            
            def method2(self):
                return "method2"
        
        obj = TestClass()
        assert obj.method1() == "method1"
        assert obj.method2() == "method2"  # Should not be traced
    
    def test_trace_class_with_exclude_list(self):
        """Test trace_class with exclude list"""
        @trace_class(exclude_list=["method2"])
        class TestClass:
            def method1(self):
                return "method1"
            
            def method2(self):
                return "method2"
        
        obj = TestClass()
        assert obj.method1() == "method1"
        assert obj.method2() == "method2"
    
    def test_trace_class_dunder_methods_excluded(self):
        """Test that dunder methods are excluded"""
        @trace_class
        class TestClass:
            def __init__(self):
                self.value = "init"
            
            def method1(self):
                return "method1"
            
            def __str__(self):
                return "str"
        
        obj = TestClass()
        assert obj.method1() == "method1"
        assert str(obj) == "str"


class TestEnrichSpan:
    """Test enrich_span function"""
    
    def test_enrich_span_with_current_span(self):
        """Test enrich_span with current span"""
        mock_span = Mock()
        
        with patch('honeyhive.tracer.custom.otel_trace.get_current_span', return_value=mock_span):
            with patch('honeyhive.tracer.custom._get_instrumentor') as mock_get_instr:
                mock_instrumentor = Mock()
                mock_get_instr.return_value = mock_instrumentor
                
                enrich_span(
                    config={"model": "gpt-4"},
                    metadata={"user_id": "123"}
                )
                
                mock_instrumentor._enrich_span.assert_called_once()
    
    def test_enrich_span_without_current_span(self):
        """Test enrich_span without current span"""
        with patch('honeyhive.tracer.custom.otel_trace.get_current_span', return_value=None):
            with patch('honeyhive.tracer.custom.logger') as mock_logger:
                enrich_span(config={"model": "gpt-4"})
                
                mock_logger.warning.assert_called_with("Please use enrich_span inside a traced function.")


class TestGlobalFunctions:
    """Test global functions"""
    
    def test_disable_tracing(self):
        """Test global disable_tracing function"""
        with patch('honeyhive.tracer.custom._get_instrumentor') as mock_get_instr:
            mock_instrumentor = Mock()
            mock_get_instr.return_value = mock_instrumentor
            
            disable_tracing()
            mock_instrumentor.disable_tracing.assert_called_once()
    
    def test_enable_tracing(self):
        """Test global enable_tracing function"""
        with patch('honeyhive.tracer.custom._get_instrumentor') as mock_get_instr:
            mock_instrumentor = Mock()
            mock_get_instr.return_value = mock_instrumentor
            
            enable_tracing()
            mock_instrumentor.enable_tracing.assert_called_once()
    
    def test_get_instrumentor(self):
        """Test _get_instrumentor function"""
        # Clear any existing instance
        import honeyhive.tracer.custom
        honeyhive.tracer.custom._instrumentor_instance = None
        
        with patch('honeyhive.tracer.custom.FunctionInstrumentor') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            result = _get_instrumentor()
            
            assert result == mock_instance
            mock_instance.instrument.assert_called_once()


class TestCreateTracedFunction:
    """Test _create_traced_function"""
    
    def test_create_traced_function_sync(self):
        """Test creating traced function for sync function"""
        def test_func(x):
            return x * 2
        
        with patch('honeyhive.tracer.custom._get_instrumentor') as mock_get_instr:
            mock_instrumentor = Mock()
            mock_instrumentor._tracing_disabled = False
            
            # Mock the trace method to return a proper trace instance
            mock_trace_instance = Mock()
            mock_trace_instance.sync_call.return_value = 10
            mock_instrumentor.trace.return_value = mock_trace_instance
            
            mock_get_instr.return_value = mock_instrumentor
            
            traced_func = _create_traced_function(test_func, event_type="tool")
            
            result = traced_func(5)
            assert result == 10
    
    def test_create_traced_function_async(self):
        """Test creating traced function for async function"""
        async def test_func(x):
            return x * 2
        
        with patch('honeyhive.tracer.custom._get_instrumentor') as mock_get_instr:
            mock_instrumentor = Mock()
            mock_instrumentor._tracing_disabled = False
            
            # Mock the trace method to return a proper trace instance
            mock_trace_instance = Mock()
            # Make the async_call method return an awaitable
            async def mock_async_call(*args, **kwargs):
                return 10
            mock_trace_instance.async_call = mock_async_call
            mock_instrumentor.trace.return_value = mock_trace_instance
            
            mock_get_instr.return_value = mock_instrumentor
            
            traced_func = _create_traced_function(test_func, event_type="tool")
            
            async def test_call():
                return await traced_func(5)
            
            result = asyncio.run(test_call())
            assert result == 10
    
    def test_create_traced_function_tracing_disabled(self):
        """Test creating traced function when tracing is disabled"""
        def test_func(x):
            return x * 2
        
        with patch('honeyhive.tracer.custom._get_instrumentor') as mock_get_instr:
            mock_instrumentor = Mock()
            mock_instrumentor._tracing_disabled = True
            mock_get_instr.return_value = mock_instrumentor
            
            traced_func = _create_traced_function(test_func, event_type="tool")
            
            result = traced_func(5)
            assert result == 10


class TestApplyTraceClass:
    """Test _apply_trace_class function"""
    
    def test_apply_trace_class_basic(self):
        """Test basic trace class application"""
        class TestClass:
            def method1(self):
                return "method1"
        
        with patch('honeyhive.tracer.custom.trace') as mock_trace:
            # Mock the trace decorator to return a callable
            mock_trace_decorator = Mock()
            mock_trace_decorator.return_value = "traced_method"
            mock_trace.return_value = mock_trace_decorator
            
            result = _apply_trace_class(TestClass, None, [], "tool", "internal")
            
            assert result == TestClass
            mock_trace.assert_called_once()
    
    def test_apply_trace_class_with_include_list(self):
        """Test trace class application with include list"""
        class TestClass:
            def method1(self):
                return "method1"
            
            def method2(self):
                return "method2"
        
        with patch('honeyhive.tracer.custom.trace') as mock_trace:
            # Mock the trace decorator to return a callable
            mock_trace_decorator = Mock()
            mock_trace_decorator.return_value = "traced_method"
            mock_trace.return_value = mock_trace_decorator
            
            result = _apply_trace_class(TestClass, ["method1"], [], "tool", "internal")
            
            assert result == TestClass
            # Should only trace method1
            assert mock_trace.call_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
