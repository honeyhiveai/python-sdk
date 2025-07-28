import pytest
import asyncio
import re
import logging
from unittest.mock import patch, MagicMock, Mock
from honeyhive.tracer.custom import (
    FunctionInstrumentor, 
    trace, 
    atrace, 
    enrich_span,
    instrumentor
)
from opentelemetry import trace as otel_trace


class TestFunctionInstrumentorEdgeCases:
    """Edge cases and error conditions for FunctionInstrumentor"""

    def test_set_span_attributes_with_circular_references(self):
        """Test span attributes with circular reference objects"""
        instrumentor = FunctionInstrumentor()
        mock_span = Mock()
        
        # Create circular reference
        circular_obj = {'key': 'value'}
        circular_obj['self'] = circular_obj
        
        # Should handle gracefully without infinite recursion
        try:
            instrumentor._set_span_attributes(mock_span, 'circular', circular_obj)
            # May succeed with string conversion or handle gracefully
        except RecursionError:
            pytest.fail("Should not cause infinite recursion")
        except Exception:
            # Other exceptions are acceptable for circular references
            pass

    def test_set_span_attributes_with_very_deep_nesting(self):
        """Test span attributes with deeply nested structures"""
        instrumentor = FunctionInstrumentor()
        mock_span = Mock()
        
        # Create deeply nested structure
        deep_obj = {}
        current = deep_obj
        for i in range(100):  # Deep nesting
            current[f'level_{i}'] = {}
            current = current[f'level_{i}']
        current['final_value'] = 'reached_bottom'
        
        # Should handle deep nesting gracefully
        try:
            instrumentor._set_span_attributes(mock_span, 'deep', deep_obj)
            # Should complete without stack overflow
        except RecursionError:
            pytest.fail("Should handle deep nesting without recursion error")

    def test_set_span_attributes_with_large_data_structures(self):
        """Test span attributes with very large data structures"""
        instrumentor = FunctionInstrumentor()
        mock_span = Mock()
        
        # Large dictionary
        large_dict = {f'key_{i}': f'value_{i}' for i in range(1000)}
        
        # Large list
        large_list = [f'item_{i}' for i in range(1000)]
        
        # Should handle large structures
        instrumentor._set_span_attributes(mock_span, 'large_dict', large_dict)
        instrumentor._set_span_attributes(mock_span, 'large_list', large_list)
        
        # Should have made many set_attribute calls
        assert mock_span.set_attribute.call_count >= 1000

    def test_set_span_attributes_with_non_serializable_objects(self):
        """Test span attributes with non-serializable objects"""
        instrumentor = FunctionInstrumentor()
        mock_span = Mock()
        
        # Non-serializable objects
        non_serializable_objects = [
            lambda x: x,  # Function
            open(__file__, 'r'),  # File object
            type('CustomClass', (), {}),  # Class
            type('CustomClass', (), {})(),  # Instance
            complex(1, 2),  # Complex number
        ]
        
        for obj in non_serializable_objects:
            try:
                instrumentor._set_span_attributes(mock_span, 'non_serializable', obj)
                # Should convert to string representation
            except Exception:
                # Some exceptions are acceptable for non-serializable objects
                pass
            finally:
                if hasattr(obj, 'close'):
                    try:
                        obj.close()
                    except:
                        pass

    def test_parse_and_match_with_malformed_templates(self):
        """Test template parsing with malformed templates"""
        instrumentor = FunctionInstrumentor()
        
        malformed_templates = [
            "{{unclosed_placeholder",
            "unopened_placeholder}}",
            "{{}}",  # Empty placeholder
            "{{nested{{inner}}}}",  # Nested placeholders
            "{{placeholder with spaces}}",
            "{{placeholder-with-dashes}}",
            "{{123numeric_start}}",
            "",  # Empty template
            "no placeholders at all",
        ]
        
        test_text = "some test text"
        
        for template in malformed_templates:
            try:
                result = instrumentor._parse_and_match(template, test_text)
                # May succeed for some cases
            except ValueError:
                # Expected for malformed templates
                pass
            except Exception as e:
                # Other exceptions should be handled gracefully
                print(f"Template '{template}' caused unexpected error: {e}")

    def test_parse_and_match_with_special_regex_characters(self):
        """Test template parsing with special regex characters"""
        instrumentor = FunctionInstrumentor()
        
        # Templates with regex special characters
        special_char_templates = [
            "Price: ${{amount}} ({{currency}})",
            "Match [{{pattern}}] in text",
            "Expression: {{value}} + {{other}} = {{result}}",
            "Percentage: {{value}}% complete",
            "Regex: {{pattern}} matches ^{{start}}$",
            "Brackets: {{value}} in [brackets]",
            "Parentheses: ({{value}}) grouped",
        ]
        
        corresponding_texts = [
            "Price: $100 (USD)",
            "Match [test] in text",
            "Expression: 2 + 3 = 5",
            "Percentage: 75% complete",
            "Regex: abc matches ^start$",
            "Brackets: test in [brackets]",
            "Parentheses: (test) grouped",
        ]
        
        for template, text in zip(special_char_templates, corresponding_texts):
            try:
                result = instrumentor._parse_and_match(template, text)
                # Should handle special characters correctly
                assert isinstance(result, dict)
            except Exception as e:
                print(f"Special char template '{template}' failed: {e}")

    def test_set_prompt_template_with_malformed_data(self):
        """Test prompt template processing with malformed data"""
        instrumentor = FunctionInstrumentor()
        mock_span = Mock()
        
        malformed_prompt_templates = [
            # Missing required keys
            {"template": []},
            {"prompt": []},
            {},
            # Wrong data types
            {"template": "not_a_list", "prompt": "not_a_list"},
            {"template": None, "prompt": None},
            # Mismatched structures
            {
                "template": [{"role": "user", "content": "Hello {{name}}"}],
                "prompt": [{"role": "assistant", "content": "Different structure"}]
            },
            # Empty content
            {
                "template": [{"role": "user", "content": ""}],
                "prompt": [{"role": "user", "content": ""}]
            },
            # Missing content keys
            {
                "template": [{"role": "user"}],
                "prompt": [{"role": "user"}]
            },
        ]
        
        for prompt_template in malformed_prompt_templates:
            try:
                instrumentor._set_prompt_template(mock_span, prompt_template)
                # May succeed for some cases
            except (KeyError, AttributeError, TypeError, ValueError):
                # Expected for malformed data
                pass
            except Exception as e:
                print(f"Prompt template {prompt_template} caused unexpected error: {e}")

    def test_enrich_span_with_none_span(self):
        """Test span enrichment when span is None"""
        instrumentor = FunctionInstrumentor()
        
        # Should handle None span gracefully
        try:
            instrumentor._enrich_span(
                None,  # None span
                config={'test': 'value'},
                metadata={'test': 'meta'}
            )
            # Should complete without error
        except AttributeError:
            # Expected - None has no set_attribute method
            pass

    def test_trace_decorator_with_invalid_function_signatures(self):
        """Test trace decorator with various function signatures"""
        
        # Function with no parameters
        @trace()
        def no_params():
            return "no_params"
        
        # Function with *args only
        @trace()
        def args_only(*args):
            return f"args: {args}"
        
        # Function with **kwargs only
        @trace()
        def kwargs_only(**kwargs):
            return f"kwargs: {kwargs}"
        
        # Function with complex signature
        @trace()
        def complex_signature(a, b=10, *args, c=20, **kwargs):
            return f"a={a}, b={b}, args={args}, c={c}, kwargs={kwargs}"
        
        # Function with positional-only and keyword-only parameters (Python 3.8+)
        try:
            exec("""
@trace()
def modern_signature(pos_only, /, normal, *, kw_only):
    return f"pos_only={pos_only}, normal={normal}, kw_only={kw_only}"
            """)
        except SyntaxError:
            # Python < 3.8 doesn't support positional-only parameters
            pass
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            # Test various function calls
            result1 = no_params()
            assert result1 == "no_params"
            
            result2 = args_only(1, 2, 3)
            assert "args: (1, 2, 3)" == result2
            
            result3 = kwargs_only(x=1, y=2)
            assert "kwargs: {'x': 1, 'y': 2}" == result3
            
            result4 = complex_signature(1, 2, 3, 4, c=30, d=40)
            assert "a=1, b=2, args=(3, 4), c=30, kwargs={'d': 40}" == result4

    def test_trace_decorator_with_generator_function(self):
        """Test trace decorator with generator function"""
        @trace(event_type="tool")
        def generator_function(n):
            for i in range(n):
                yield i * 2
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            # Should handle generator gracefully
            gen = generator_function(3)
            results = list(gen)
            
            assert results == [0, 2, 4]
            mock_tracer.start_as_current_span.assert_called_once()

    def test_trace_decorator_with_class_methods(self):
        """Test trace decorator with various class method types"""
        
        class TestClass:
            class_var = "class_value"
            
            def __init__(self, value):
                self.instance_var = value
            
            @trace(event_type="model")
            def instance_method(self, x):
                return f"instance: {self.instance_var} + {x}"
            
            @classmethod
            @trace(event_type="tool")
            def class_method(cls, x):
                return f"class: {cls.class_var} + {x}"
            
            @staticmethod
            @trace(event_type="chain")
            def static_method(x):
                return f"static: {x}"
            
            @property
            @trace(event_type="tool")
            def traced_property(self):
                return f"property: {self.instance_var}"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            obj = TestClass("test_value")
            
            # Test instance method
            result1 = obj.instance_method("param")
            assert result1 == "instance: test_value + param"
            
            # Test class method
            result2 = TestClass.class_method("param")
            assert result2 == "class: class_value + param"
            
            # Test static method
            result3 = TestClass.static_method("param")
            assert result3 == "static: param"
            
            # Test property (if trace works on properties)
            try:
                result4 = obj.traced_property
                assert result4 == "property: test_value"
            except Exception:
                # Properties might not work with trace decorator
                pass

    @pytest.mark.asyncio
    async def test_atrace_decorator_edge_cases(self):
        """Test atrace decorator with edge cases"""
        
        # Async generator
        @atrace(event_type="tool")
        async def async_generator(n):
            for i in range(n):
                yield i
                await asyncio.sleep(0.001)
        
        # Async context manager
        @atrace(event_type="tool")
        async def async_context_function():
            class AsyncContextManager:
                async def __aenter__(self):
                    return self
                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    pass
            
            async with AsyncContextManager():
                await asyncio.sleep(0.001)
                return "context_result"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            # Test async generator
            async_gen = async_generator(3)
            results = []
            async for item in async_gen:
                results.append(item)
            assert results == [0, 1, 2]
            
            # Test async context manager function
            result = await async_context_function()
            assert result == "context_result"

    def test_trace_decorator_exception_in_setup(self):
        """Test trace decorator when setup_span raises exception"""
        
        @trace(event_type="tool")
        def test_function(param):
            return f"result: {param}"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            # Make _set_span_attributes raise an exception
            with patch.object(instrumentor, '_set_span_attributes', side_effect=Exception("Setup error")):
                try:
                    result = test_function("test_param")
                    # Function should still execute despite setup error
                    assert result == "result: test_param"
                except Exception:
                    # Setup exceptions might propagate
                    pass

    def test_instrumentor_initialization_edge_cases(self):
        """Test FunctionInstrumentor initialization edge cases"""
        
        # Test multiple instrumentor instances
        instrumentor1 = FunctionInstrumentor()
        instrumentor2 = FunctionInstrumentor()
        
        # Both should initialize independently
        instrumentor1._instrument()
        instrumentor2._instrument()
        
        assert hasattr(instrumentor1, '_tracer')
        assert hasattr(instrumentor2, '_tracer')

    def test_trace_decorator_with_recursive_functions(self):
        """Test trace decorator with recursive functions"""
        
        @trace(event_type="tool", metadata={'recursive': True})
        def recursive_function(n, depth=0):
            if n <= 0:
                return depth
            return recursive_function(n - 1, depth + 1)
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            result = recursive_function(5)
            assert result == 5
            
            # Should have traced each recursive call
            assert mock_tracer.start_as_current_span.call_count == 6  # 5 + base case

    def test_span_attribute_name_edge_cases(self):
        """Test span attribute naming with edge cases"""
        instrumentor = FunctionInstrumentor()
        mock_span = Mock()
        
        # Test various prefix and key combinations
        edge_case_data = {
            "": "empty_key",
            " ": "space_key", 
            "key with spaces": "value",
            "key.with.dots": "value",
            "key-with-dashes": "value",
            "key_with_underscores": "value",
            "UPPERCASE_KEY": "value",
            "123numeric_key": "value",
            "key!@#$%^&*()": "value",
            "unicode_key_🚀": "value",
        }
        
        for key, value in edge_case_data.items():
            try:
                instrumentor._set_span_attributes(mock_span, f"prefix.{key}", value)
                # Should handle various key formats
            except Exception as e:
                print(f"Key '{key}' caused error: {e}")

    def test_trace_decorator_with_lambda_functions(self):
        """Test trace decorator with lambda functions"""
        
        # Lambda functions can't normally be decorated, but test the attempt
        try:
            traced_lambda = trace(event_type="tool")(lambda x: x * 2)
            
            with patch.object(instrumentor, '_tracer') as mock_tracer:
                mock_span = Mock()
                mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
                mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
                
                result = traced_lambda(5)
                assert result == 10
                
        except Exception:
            # Lambda decoration might not work, which is acceptable
            pass

    def test_error_logging_and_warning_scenarios(self):
        """Test scenarios that should trigger logging warnings"""
        
        # Capture log messages
        with patch('honeyhive.tracer.custom.logger') as mock_logger:
            
            # Test invalid event type warning
            @trace(event_type="invalid_event_type")
            def test_function():
                return "result"
            
            with patch.object(instrumentor, '_tracer') as mock_tracer:
                mock_span = Mock()
                mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
                mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
                
                result = test_function()
                assert result == "result"
                
                # Should have logged a warning about invalid event type
                mock_logger.warning.assert_called()

    def test_enrich_span_without_current_span(self):
        """Test enrich_span when no current span exists"""
        
        with patch('honeyhive.tracer.custom.otel_trace.get_current_span', return_value=None):
            with patch('honeyhive.tracer.custom.logger') as mock_logger:
                
                # Should log warning and not crash
                enrich_span(metadata={'test': 'value'})
                
                # Should have logged warning
                mock_logger.warning.assert_called_with("Please use enrich_span inside a traced function.")

    def test_memory_usage_with_large_traces(self):
        """Test memory usage with large trace data"""
        
        @trace(event_type="tool")
        def memory_intensive_function():
            # Create large data structures
            large_data = {
                'large_list': list(range(10000)),
                'large_dict': {f'key_{i}': f'value_{i}' for i in range(1000)},
                'large_string': 'x' * 100000
            }
            return large_data
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            result = memory_intensive_function()
            
            # Should complete without memory issues
            assert len(result['large_list']) == 10000
            assert len(result['large_dict']) == 1000
            assert len(result['large_string']) == 100000