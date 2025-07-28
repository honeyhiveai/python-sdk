import pytest
import asyncio
from unittest.mock import patch, MagicMock, Mock
from honeyhive.tracer.custom import (
    FunctionInstrumentor, 
    trace, 
    atrace, 
    enrich_span,
    instrumentor
)
from opentelemetry import trace as otel_trace
from opentelemetry.trace import Span


class TestFunctionInstrumentor:
    """Test suite for FunctionInstrumentor class"""

    def test_instrument(self):
        """Test FunctionInstrumentor._instrument method"""
        instrumentor = FunctionInstrumentor()
        instrumentor._instrument()
        
        assert hasattr(instrumentor, '_tracer')
        assert instrumentor._tracer is not None

    def test_uninstrument(self):
        """Test FunctionInstrumentor._uninstrument method"""
        instrumentor = FunctionInstrumentor()
        # Should not raise any exceptions
        instrumentor._uninstrument()

    def test_instrumentation_dependencies(self):
        """Test FunctionInstrumentor.instrumentation_dependencies method"""
        instrumentor = FunctionInstrumentor()
        deps = instrumentor.instrumentation_dependencies()
        assert deps == ()

    def test_set_span_attributes_dict(self):
        """Test _set_span_attributes with dictionary"""
        instrumentor = FunctionInstrumentor()
        mock_span = Mock()
        
        value = {'key1': 'value1', 'key2': {'nested': 'value2'}}
        instrumentor._set_span_attributes(mock_span, 'prefix', value)
        
        mock_span.set_attribute.assert_any_call('prefix.key1', 'value1')
        mock_span.set_attribute.assert_any_call('prefix.key2.nested', 'value2')

    def test_set_span_attributes_list(self):
        """Test _set_span_attributes with list"""
        instrumentor = FunctionInstrumentor()
        mock_span = Mock()
        
        value = ['item1', 'item2', {'nested': 'value'}]
        instrumentor._set_span_attributes(mock_span, 'prefix', value)
        
        mock_span.set_attribute.assert_any_call('prefix.0', 'item1')
        mock_span.set_attribute.assert_any_call('prefix.1', 'item2')
        mock_span.set_attribute.assert_any_call('prefix.2.nested', 'value')

    def test_set_span_attributes_primitives(self):
        """Test _set_span_attributes with primitive types"""
        instrumentor = FunctionInstrumentor()
        mock_span = Mock()
        
        # Test different primitive types
        instrumentor._set_span_attributes(mock_span, 'str_prefix', 'string_value')
        instrumentor._set_span_attributes(mock_span, 'int_prefix', 42)
        instrumentor._set_span_attributes(mock_span, 'bool_prefix', True)
        instrumentor._set_span_attributes(mock_span, 'float_prefix', 3.14)
        
        mock_span.set_attribute.assert_any_call('str_prefix', 'string_value')
        mock_span.set_attribute.assert_any_call('int_prefix', 42)
        mock_span.set_attribute.assert_any_call('bool_prefix', True)
        mock_span.set_attribute.assert_any_call('float_prefix', 3.14)

    def test_set_span_attributes_other_types(self):
        """Test _set_span_attributes with other types (converted to string)"""
        instrumentor = FunctionInstrumentor()
        mock_span = Mock()
        
        class CustomObject:
            def __str__(self):
                return "custom_object"
        
        instrumentor._set_span_attributes(mock_span, 'prefix', CustomObject())
        mock_span.set_attribute.assert_called_with('prefix', 'custom_object')

    def test_parse_and_match_success(self):
        """Test _parse_and_match with valid template and text"""
        instrumentor = FunctionInstrumentor()
        
        template = "Hello {{name}}, you are {{age}} years old"
        text = "Hello John, you are 25 years old"
        
        result = instrumentor._parse_and_match(template, text)
        
        assert result == {'name': 'John', 'age': '25'}

    def test_parse_and_match_failure(self):
        """Test _parse_and_match with mismatched template and text"""
        instrumentor = FunctionInstrumentor()
        
        template = "Hello {{name}}, you are {{age}} years old"
        text = "Hi John, you are 25"
        
        with pytest.raises(ValueError, match="does not match the template"):
            instrumentor._parse_and_match(template, text)

    def test_set_prompt_template(self):
        """Test _set_prompt_template method"""
        instrumentor = FunctionInstrumentor()
        mock_span = Mock()
        
        prompt_template = {
            "template": [
                {"role": "user", "content": "Hello {{name}}"}
            ],
            "prompt": [
                {"role": "user", "content": "Hello John"}
            ]
        }
        
        instrumentor._set_prompt_template(mock_span, prompt_template)
        
        # Verify that template and prompt are set
        mock_span.set_attribute.assert_any_call(
            'honeyhive_prompt_template.inputs.name', 'John'
        )

    def test_enrich_span_method(self):
        """Test _enrich_span method"""
        instrumentor = FunctionInstrumentor()
        mock_span = Mock()
        
        instrumentor._enrich_span(
            mock_span,
            config={'model': 'gpt-4'},
            metadata={'version': '1.0'},
            metrics={'latency': 100},
            feedback={'rating': 5},
            inputs={'query': 'test'},
            outputs={'response': 'result'},
            error='test error',
            tags={'environment': 'test', 'version': 'v1.0'}
        )
        
        # Verify all attributes are set
        mock_span.set_attribute.assert_any_call('honeyhive_config.model', 'gpt-4')
        mock_span.set_attribute.assert_any_call('honeyhive_metadata.version', '1.0')
        mock_span.set_attribute.assert_any_call('honeyhive_metrics.latency', 100)
        mock_span.set_attribute.assert_any_call('honeyhive_feedback.rating', 5)
        mock_span.set_attribute.assert_any_call('honeyhive_inputs.query', 'test')
        mock_span.set_attribute.assert_any_call('honeyhive_outputs.response', 'result')
        mock_span.set_attribute.assert_any_call('honeyhive_error', 'test error')
        mock_span.set_attribute.assert_any_call('honeyhive_tags.environment', 'test')
        mock_span.set_attribute.assert_any_call('honeyhive_tags.version', 'v1.0')


class TestTraceDecorator:
    """Test suite for trace decorator"""

    def test_trace_decorator_sync_function(self):
        """Test trace decorator on synchronous function"""
        @trace(event_type="tool", metadata={'test': 'value'})
        def test_function(x, y=10):
            return x + y
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            result = test_function(5, y=15)
            
            assert result == 20
            mock_tracer.start_as_current_span.assert_called_once_with('test_function')

    def test_trace_decorator_with_custom_event_name(self):
        """Test trace decorator with custom event name"""
        @trace(event_name="custom_name")
        def test_function():
            return "result"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            test_function()
            
            mock_tracer.start_as_current_span.assert_called_once_with('custom_name')

    def test_trace_decorator_exception_handling(self):
        """Test trace decorator exception handling"""
        @trace()
        def failing_function():
            raise ValueError("Test error")
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            with pytest.raises(ValueError, match="Test error"):
                failing_function()
            
            # Verify error was set on span
            mock_span.set_attribute.assert_any_call('honeyhive_error', 'Test error')

    def test_trace_decorator_async_function_error(self):
        """Test trace decorator raises error for async functions"""
        @trace()
        async def async_function():
            return "result"
        
        with pytest.raises(TypeError, match="please use @atrace for tracing async functions"):
            asyncio.run(async_function())

    def test_trace_decorator_prompt_template_parameter(self):
        """Test trace decorator with prompt_template parameter"""
        @trace()
        def test_function(prompt_template):
            return "result"
        
        prompt_template = {
            "template": [{"role": "user", "content": "Hello {{name}}"}],
            "prompt": [{"role": "user", "content": "Hello John"}]
        }
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            test_function(prompt_template)
            
            # Verify prompt template was processed
            mock_span.set_attribute.assert_any_call(
                'honeyhive_prompt_template.inputs.name', 'John'
            )

    def test_trace_decorator_invalid_event_type(self):
        """Test trace decorator with invalid event type"""
        @trace(event_type="invalid_type")
        def test_function():
            return "result"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            test_function()
            
            # Should not set event_type attribute for invalid type
            calls = [call for call in mock_span.set_attribute.call_args_list 
                    if 'honeyhive_event_type' in str(call)]
            assert len(calls) == 0


class TestAtraceDecorator:
    """Test suite for atrace decorator"""

    @pytest.mark.asyncio
    async def test_atrace_decorator_async_function(self):
        """Test atrace decorator on asynchronous function"""
        @atrace(event_type="chain", metadata={'async': 'true'})
        async def async_test_function(x, y=10):
            await asyncio.sleep(0.01)
            return x + y
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            result = await async_test_function(5, y=15)
            
            assert result == 20
            mock_tracer.start_as_current_span.assert_called_once_with('async_test_function')

    @pytest.mark.asyncio
    async def test_atrace_decorator_exception_handling(self):
        """Test atrace decorator exception handling"""
        @atrace()
        async def failing_async_function():
            await asyncio.sleep(0.01)
            raise ValueError("Async test error")
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            with pytest.raises(ValueError, match="Async test error"):
                await failing_async_function()
            
            # Verify error was set on span
            mock_span.set_attribute.assert_any_call('honeyhive_error', 'Async test error')

    @pytest.mark.asyncio
    async def test_atrace_decorator_with_custom_event_name(self):
        """Test atrace decorator with custom event name"""
        @atrace(event_name="custom_async_name")
        async def async_test_function():
            return "async result"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            result = await async_test_function()
            
            assert result == "async result"
            mock_tracer.start_as_current_span.assert_called_once_with('custom_async_name')


class TestEnrichSpanFunction:
    """Test suite for enrich_span function"""

    @patch('honeyhive.tracer.custom.otel_trace.get_current_span')
    def test_enrich_span_success(self, mock_get_current_span):
        """Test enrich_span with valid span"""
        mock_span = Mock()
        mock_get_current_span.return_value = mock_span
        
        with patch.object(instrumentor, '_enrich_span') as mock_enrich:
            enrich_span(
                config={'model': 'gpt-4'},
                metadata={'version': '1.0'},
                metrics={'latency': 100},
                feedback={'rating': 5},
                inputs={'query': 'test'},
                outputs={'response': 'result'},
                error='test error'
            )
            
            mock_enrich.assert_called_once_with(
                mock_span,
                {'model': 'gpt-4'},
                {'version': '1.0'},
                {'latency': 100},
                {'rating': 5},
                {'query': 'test'},
                {'response': 'result'},
                'test error'
            )

    @patch('honeyhive.tracer.custom.otel_trace.get_current_span')
    def test_enrich_span_no_current_span(self, mock_get_current_span):
        """Test enrich_span when no current span exists"""
        mock_get_current_span.return_value = None
        
        # Should not raise exception, just log warning
        enrich_span(metadata={'test': 'value'})

    @patch('honeyhive.tracer.custom.otel_trace.get_current_span')
    def test_enrich_span_partial_parameters(self, mock_get_current_span):
        """Test enrich_span with only some parameters"""
        mock_span = Mock()
        mock_get_current_span.return_value = mock_span
        
        with patch.object(instrumentor, '_enrich_span') as mock_enrich:
            enrich_span(metadata={'version': '1.0'}, error='test error')
            
            mock_enrich.assert_called_once_with(
                mock_span,
                None,  # config
                {'version': '1.0'},  # metadata
                None,  # metrics
                None,  # feedback
                None,  # inputs
                None,  # outputs
                'test error'  # error
            )


class TestDecoratorParameters:
    """Test suite for decorator parameter handling"""

    def test_trace_decorator_as_function_with_params(self):
        """Test trace decorator used as function with parameters"""
        decorator = trace(event_type="model", config={'param': 'value'})
        
        def test_function():
            return "result"
        
        decorated_function = decorator(test_function)
        
        assert decorated_function.event_type == "model"
        assert decorated_function.config == {'param': 'value'}

    def test_atrace_decorator_as_function_with_params(self):
        """Test atrace decorator used as function with parameters"""
        decorator = atrace(event_type="chain", metadata={'async': 'true'})
        
        async def async_test_function():
            return "async result"
        
        decorated_function = decorator(async_test_function)
        
        assert decorated_function.event_type == "chain"
        assert decorated_function.metadata == {'async': 'true'}

    def test_trace_decorator_method_binding(self):
        """Test trace decorator on class methods"""
        class TestClass:
            @trace()
            def test_method(self, value):
                return value * 2
        
        instance = TestClass()
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            result = instance.test_method(5)
            
            assert result == 10
            mock_tracer.start_as_current_span.assert_called_once_with('test_method')


class TestTaggingFunctionality:
    """Test suite for tagging functionality"""

    def test_trace_decorator_with_tags(self):
        """Test trace decorator with tags parameter"""
        @trace(tags={'component': 'llm', 'model': 'gpt4'})
        def test_function():
            return "result"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            test_function()
            
            # Verify tags are set on span
            mock_span.set_attribute.assert_any_call('honeyhive_tags.component', 'llm')
            mock_span.set_attribute.assert_any_call('honeyhive_tags.model', 'gpt4')

    @pytest.mark.asyncio
    async def test_atrace_decorator_with_tags(self):
        """Test atrace decorator with tags parameter"""
        @atrace(tags={'environment': 'production', 'async': 'true'})
        async def async_test_function():
            return "async result"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            result = await async_test_function()
            
            assert result == "async result"
            # Verify tags are set on span
            mock_span.set_attribute.assert_any_call('honeyhive_tags.environment', 'production')
            mock_span.set_attribute.assert_any_call('honeyhive_tags.async', 'true')

    def test_trace_decorator_with_mixed_parameters_and_tags(self):
        """Test trace decorator with tags along with other parameters"""
        @trace(
            event_type="model",
            config={'temperature': 0.7},
            metadata={'version': '1.0'},
            tags={'experiment': 'ab_test', 'user_type': 'premium'}
        )
        def test_function():
            return "result"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            test_function()
            
            # Verify all parameters are set including tags
            mock_span.set_attribute.assert_any_call('honeyhive_event_type', 'model')
            mock_span.set_attribute.assert_any_call('honeyhive_config.temperature', 0.7)
            mock_span.set_attribute.assert_any_call('honeyhive_metadata.version', '1.0')
            mock_span.set_attribute.assert_any_call('honeyhive_tags.experiment', 'ab_test')
            mock_span.set_attribute.assert_any_call('honeyhive_tags.user_type', 'premium')

    def test_trace_decorator_empty_tags(self):
        """Test trace decorator with empty tags dictionary"""
        @trace(tags={})
        def test_function():
            return "result"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            test_function()
            
            # Verify no tag attributes are set for empty tags
            tag_calls = [call for call in mock_span.set_attribute.call_args_list 
                        if 'honeyhive_tags' in str(call)]
            assert len(tag_calls) == 0

    def test_trace_decorator_none_tags(self):
        """Test trace decorator with None tags"""
        @trace(tags=None)
        def test_function():
            return "result"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            test_function()
            
            # Verify no tag attributes are set for None tags
            tag_calls = [call for call in mock_span.set_attribute.call_args_list 
                        if 'honeyhive_tags' in str(call)]
            assert len(tag_calls) == 0

    def test_enrich_span_with_tags(self):
        """Test enrich_span function with tags parameter"""
        with patch('honeyhive.tracer.custom.otel_trace.get_current_span') as mock_get_current_span:
            mock_span = Mock()
            mock_get_current_span.return_value = mock_span
            
            with patch.object(instrumentor, '_enrich_span') as mock_enrich:
                enrich_span(
                    metadata={'version': '1.0'},
                    tags={'service': 'api', 'region': 'us-east-1'}
                )
                
                mock_enrich.assert_called_once_with(
                    mock_span,
                    None,  # config
                    {'version': '1.0'},  # metadata
                    None,  # metrics
                    None,  # feedback
                    None,  # inputs
                    None,  # outputs
                    None,  # error
                    {'service': 'api', 'region': 'us-east-1'}  # tags
                )

    def test_enrich_span_only_tags(self):
        """Test enrich_span function with only tags parameter"""
        with patch('honeyhive.tracer.custom.otel_trace.get_current_span') as mock_get_current_span:
            mock_span = Mock()
            mock_get_current_span.return_value = mock_span
            
            with patch.object(instrumentor, '_enrich_span') as mock_enrich:
                enrich_span(tags={'deployment': 'staging', 'build': '123'})
                
                mock_enrich.assert_called_once_with(
                    mock_span,
                    None,  # config
                    None,  # metadata
                    None,  # metrics
                    None,  # feedback
                    None,  # inputs
                    None,  # outputs
                    None,  # error
                    {'deployment': 'staging', 'build': '123'}  # tags
                )

    def test_instrumentor_enrich_span_with_tags(self):
        """Test FunctionInstrumentor._enrich_span with tags"""
        instrumentor = FunctionInstrumentor()
        mock_span = Mock()
        
        instrumentor._enrich_span(
            mock_span,
            tags={'key1': 'value1', 'key2': 123, 'key3': True}
        )
        
        # Verify tags are set as span attributes
        mock_span.set_attribute.assert_any_call('honeyhive_tags.key1', 'value1')
        mock_span.set_attribute.assert_any_call('honeyhive_tags.key2', 123)
        mock_span.set_attribute.assert_any_call('honeyhive_tags.key3', True)

    def test_instrumentor_enrich_span_with_nested_tags(self):
        """Test FunctionInstrumentor._enrich_span with nested tags structure"""
        instrumentor = FunctionInstrumentor()
        mock_span = Mock()
        
        instrumentor._enrich_span(
            mock_span,
            tags={
                'service': {
                    'name': 'api',
                    'version': '2.0'
                },
                'environment': 'prod'
            }
        )
        
        # Verify nested tags are flattened correctly
        mock_span.set_attribute.assert_any_call('honeyhive_tags.service.name', 'api')
        mock_span.set_attribute.assert_any_call('honeyhive_tags.service.version', '2.0')
        mock_span.set_attribute.assert_any_call('honeyhive_tags.environment', 'prod')

    def test_trace_decorator_tags_with_different_types(self):
        """Test trace decorator tags with different value types"""
        @trace(tags={
            'string_tag': 'value',
            'int_tag': 42,
            'float_tag': 3.14,
            'bool_tag': True,
            'list_tag': ['item1', 'item2']
        })
        def test_function():
            return "result"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            test_function()
            
            # Verify different types are handled correctly
            mock_span.set_attribute.assert_any_call('honeyhive_tags.string_tag', 'value')
            mock_span.set_attribute.assert_any_call('honeyhive_tags.int_tag', 42)
            mock_span.set_attribute.assert_any_call('honeyhive_tags.float_tag', 3.14)
            mock_span.set_attribute.assert_any_call('honeyhive_tags.bool_tag', True)
            mock_span.set_attribute.assert_any_call('honeyhive_tags.list_tag.0', 'item1')
            mock_span.set_attribute.assert_any_call('honeyhive_tags.list_tag.1', 'item2')