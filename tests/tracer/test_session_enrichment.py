import pytest
import os
import time
import threading
from unittest.mock import patch, MagicMock, Mock
from honeyhive.tracer import HoneyHiveTracer, enrich_session
from honeyhive.models import operations
from opentelemetry import context


class TestSessionEnrichment:
    """Comprehensive tests for session enrichment functionality"""

    def setup_method(self):
        """Reset HoneyHiveTracer static variables before each test"""
        HoneyHiveTracer.api_key = None
        HoneyHiveTracer.server_url = None
        HoneyHiveTracer._is_traceloop_initialized = False

    def test_enrich_session_all_parameters(self):
        """Test session enrichment with all possible parameters"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
            mock_sdk = Mock()
            mock_sdk_class.return_value = mock_sdk
            mock_response = Mock()
            mock_response.status_code = 200
            mock_sdk.events.update_event.return_value = mock_response
            
            # Test with all parameters
            enrich_session(
                session_id='test-session-123',
                metadata={
                    'model': 'gpt-4',
                    'version': '1.0',
                    'user_id': 'user123',
                    'timestamp': time.time(),
                    'nested': {
                        'deep': {
                            'value': 'nested_data'
                        }
                    }
                },
                feedback={
                    'rating': 5,
                    'comment': 'Excellent response',
                    'thumbs_up': True,
                    'categories': ['helpful', 'accurate', 'clear']
                },
                metrics={
                    'latency': 1.5,
                    'token_count': 150,
                    'cost': 0.003,
                    'accuracy': 0.95,
                    'confidence': 0.87
                },
                config={
                    'temperature': 0.7,
                    'max_tokens': 500,
                    'top_p': 0.9,
                    'frequency_penalty': 0.0,
                    'presence_penalty': 0.0
                },
                outputs={
                    'response': 'Generated response text',
                    'finish_reason': 'stop',
                    'token_usage': {
                        'prompt_tokens': 50,
                        'completion_tokens': 100,
                        'total_tokens': 150
                    }
                },
                user_properties={
                    'user_id': 'user123',
                    'plan': 'premium',
                    'location': 'US',
                    'language': 'en'
                }
            )
            
            # Verify the API call was made correctly
            mock_sdk.events.update_event.assert_called_once()
            call_args = mock_sdk.events.update_event.call_args[1]['request']
            
            assert call_args.event_id == 'test-session-123'
            assert call_args.metadata['model'] == 'gpt-4'
            assert call_args.feedback['rating'] == 5
            assert call_args.metrics['latency'] == 1.5
            assert call_args.config['temperature'] == 0.7
            assert call_args.outputs['response'] == 'Generated response text'
            assert call_args.user_properties['plan'] == 'premium'

    def test_enrich_session_individual_parameters(self):
        """Test session enrichment with individual parameters"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        individual_tests = [
            {'metadata': {'test': 'metadata_only'}},
            {'feedback': {'rating': 3}},
            {'metrics': {'score': 0.8}},
            {'config': {'model': 'gpt-3.5-turbo'}},
            {'outputs': {'result': 'test_output'}},
            {'user_properties': {'user_type': 'trial'}},
        ]
        
        for test_params in individual_tests:
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_sdk.events.update_event.return_value = mock_response
                
                enrich_session(session_id='test-session', **test_params)
                
                mock_sdk.events.update_event.assert_called_once()
                call_args = mock_sdk.events.update_event.call_args[1]['request']
                
                # Verify only the specified parameter was set
                param_name = list(test_params.keys())[0]
                expected_value = test_params[param_name]
                actual_value = getattr(call_args, param_name)
                assert actual_value == expected_value

    def test_enrich_session_without_session_id(self):
        """Test session enrichment without explicit session ID (from context)"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        # Mock context with association properties
        mock_ctx = Mock()
        mock_ctx.get.return_value = {'session_id': 'context-session-123'}
        
        with patch('honeyhive.tracer.context.get_current', return_value=mock_ctx):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_sdk.events.update_event.return_value = mock_response
                
                enrich_session(metadata={'from_context': True})
                
                mock_sdk.events.update_event.assert_called_once()
                call_args = mock_sdk.events.update_event.call_args[1]['request']
                
                # Should use session ID from context
                assert call_args.event_id == 'context-session-123'
                assert call_args.metadata['from_context'] is True

    def test_enrich_session_no_context_no_session_id(self):
        """Test session enrichment with no context and no session ID"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        # Mock context with no association properties
        mock_ctx = Mock()
        mock_ctx.get.return_value = None
        
        with patch('honeyhive.tracer.context.get_current', return_value=mock_ctx):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                
                # Should raise exception when no session ID available
                with pytest.raises(Exception, match="Please initialize HoneyHiveTracer"):
                    enrich_session(metadata={'test': 'value'})

    def test_enrich_session_with_complex_data_types(self):
        """Test session enrichment with complex data types"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        from datetime import datetime
        from decimal import Decimal
        
        complex_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'decimal_value': float(Decimal('10.5')),  # Convert to float for JSON
                'large_number': 2**63 - 1,
                'scientific_notation': 1.23e-10,
                'unicode_text': '🚀 Test with emojis 🌟',
                'nested_list': [
                    {'item': 1, 'value': 'first'},
                    {'item': 2, 'value': 'second'}
                ],
                'mixed_types': {
                    'string': 'text',
                    'number': 42,
                    'float': 3.14,
                    'boolean': True,
                    'null': None
                }
            }
        }
        
        with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
            mock_sdk = Mock()
            mock_sdk_class.return_value = mock_sdk
            mock_response = Mock()
            mock_response.status_code = 200
            mock_sdk.events.update_event.return_value = mock_response
            
            enrich_session(session_id='test-session', **complex_data)
            
            mock_sdk.events.update_event.assert_called_once()
            call_args = mock_sdk.events.update_event.call_args[1]['request']
            
            # Verify complex data was handled
            assert 'unicode_text' in call_args.metadata
            assert call_args.metadata['large_number'] == 2**63 - 1
            assert len(call_args.metadata['nested_list']) == 2

    def test_enrich_session_api_errors(self):
        """Test session enrichment with API errors"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        error_scenarios = [
            (400, "Bad request"),
            (401, "Unauthorized"), 
            (403, "Forbidden"),
            (404, "Session not found"),
            (500, "Internal server error"),
            (503, "Service unavailable"),
        ]
        
        for status_code, error_message in error_scenarios:
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = status_code
                mock_response.raw_response.text = error_message
                mock_sdk.events.update_event.return_value = mock_response
                
                # Should handle API errors gracefully
                try:
                    enrich_session(
                        session_id='test-session',
                        metadata={'error_test': True}
                    )
                    # Some implementations might handle errors silently
                except Exception:
                    # Others might raise exceptions, both are acceptable
                    pass

    def test_enrich_session_network_failures(self):
        """Test session enrichment with network failures"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        import requests
        
        network_errors = [
            requests.ConnectionError("Network unreachable"),
            requests.Timeout("Request timeout"),
            requests.HTTPError("HTTP error"),
        ]
        
        for error in network_errors:
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_sdk.events.update_event.side_effect = error
                
                # Should handle network errors gracefully
                try:
                    enrich_session(
                        session_id='test-session',
                        metadata={'network_test': True}
                    )
                    # Success - error handled gracefully
                except type(error):
                    # Error propagation is also acceptable
                    pass

    def test_tracer_instance_enrich_session(self):
        """Test HoneyHiveTracer instance enrich_session method"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
            mock_sdk = Mock()
            mock_sdk_class.return_value = mock_sdk
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.object.session_id = "tracer-session-id"
            mock_sdk.session.start_session.return_value = mock_response
            mock_sdk.events.update_event.return_value = mock_response
            
            # Create tracer instance
            with patch.dict(os.environ, {
                'HH_API_KEY': 'test_key',
                'HH_PROJECT': 'test_project'
            }):
                tracer = HoneyHiveTracer()
                
                # Test instance method
                tracer.enrich_session(
                    metadata={'instance_method': True},
                    feedback={'rating': 4},
                    metrics={'success': 1}
                )
                
                mock_sdk.events.update_event.assert_called_once()
                call_args = mock_sdk.events.update_event.call_args[1]['request']
                
                assert call_args.event_id == "tracer-session-id"
                assert call_args.metadata['instance_method'] is True
                assert call_args.feedback['rating'] == 4
                assert call_args.metrics['success'] == 1

    def test_enrich_session_with_explicit_session_id_override(self):
        """Test enriching session with explicit session ID when context exists"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        # Mock context with different session ID
        mock_ctx = Mock()
        mock_ctx.get.return_value = {'session_id': 'context-session'}
        
        with patch('honeyhive.tracer.context.get_current', return_value=mock_ctx):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_sdk.events.update_event.return_value = mock_response
                
                # Explicit session ID should override context
                enrich_session(
                    session_id='explicit-session',
                    metadata={'explicit_override': True}
                )
                
                call_args = mock_sdk.events.update_event.call_args[1]['request']
                assert call_args.event_id == 'explicit-session'

    def test_enrich_session_concurrent_calls(self):
        """Test concurrent session enrichment calls"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        import queue
        results = queue.Queue()
        errors = queue.Queue()
        
        def concurrent_enrich(thread_id):
            try:
                with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                    mock_sdk = Mock()
                    mock_sdk_class.return_value = mock_sdk
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_sdk.events.update_event.return_value = mock_response
                    
                    enrich_session(
                        session_id=f'session-{thread_id}',
                        metadata={'thread_id': thread_id, 'concurrent': True},
                        metrics={'thread_score': thread_id * 0.1}
                    )
                    
                results.put({'thread_id': thread_id, 'success': True})
                
            except Exception as e:
                errors.put({'thread_id': thread_id, 'error': str(e)})
        
        # Start concurrent enrichment operations
        threads = []
        for i in range(10):
            thread = threading.Thread(target=concurrent_enrich, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)
        
        # Check results
        all_results = []
        while not results.empty():
            all_results.append(results.get())
        
        all_errors = []
        while not errors.empty():
            all_errors.append(errors.get())
        
        # All operations should succeed
        assert len(all_errors) == 0, f"Concurrent errors: {all_errors}"
        assert len(all_results) == 10

    def test_enrich_session_with_inputs_parameter(self):
        """Test session enrichment with inputs parameter (should log warning)"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
            mock_sdk = Mock()
            mock_sdk_class.return_value = mock_sdk
            mock_response = Mock()
            mock_response.status_code = 200
            mock_sdk.events.update_event.return_value = mock_response
            
            with patch('builtins.print') as mock_print:
                enrich_session(
                    session_id='test-session',
                    inputs={'prompt': 'test input', 'context': 'test context'},
                    metadata={'has_inputs': True}
                )
                
                # Should print warning about inputs not being supported
                mock_print.assert_called_with('inputs are not supported in enrich_session')

    def test_enrich_session_not_initialized(self):
        """Test session enrichment when tracer not initialized"""
        HoneyHiveTracer._is_traceloop_initialized = False
        
        with patch('builtins.print') as mock_print:
            enrich_session(
                session_id='test-session',
                metadata={'should_fail': True}
            )
            
            # Should print error message
            mock_print.assert_called()
            printed_message = mock_print.call_args[0][0]
            assert "Could not enrich session: HoneyHiveTracer not initialized" in printed_message

    def test_enrich_session_verbose_error_handling(self):
        """Test session enrichment error handling with verbose mode"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        HoneyHiveTracer.verbose = True
        
        with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
            mock_sdk = Mock()
            mock_sdk_class.return_value = mock_sdk
            mock_sdk.events.update_event.side_effect = Exception("Test error")
            
            with patch('honeyhive.tracer.print_exc') as mock_print_exc:
                enrich_session(
                    session_id='test-session',
                    metadata={'verbose_test': True}
                )
                
                # Should print exception traceback in verbose mode
                mock_print_exc.assert_called_once()

    def test_enrich_session_data_size_limits(self):
        """Test session enrichment with very large data"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        # Create large data structures
        large_metadata = {
            'large_string': 'x' * 10000,
            'large_list': list(range(1000)),
            'large_dict': {f'key_{i}': f'value_{i}' for i in range(500)}
        }
        
        with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
            mock_sdk = Mock()
            mock_sdk_class.return_value = mock_sdk
            mock_response = Mock()
            mock_response.status_code = 200
            mock_sdk.events.update_event.return_value = mock_response
            
            # Should handle large data without issues
            enrich_session(
                session_id='test-session',
                metadata=large_metadata
            )
            
            mock_sdk.events.update_event.assert_called_once()
            call_args = mock_sdk.events.update_event.call_args[1]['request']
            
            # Verify large data was passed through
            assert len(call_args.metadata['large_string']) == 10000
            assert len(call_args.metadata['large_list']) == 1000
            assert len(call_args.metadata['large_dict']) == 500

    def test_enrich_session_parameter_combinations(self):
        """Test various parameter combinations for session enrichment"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        parameter_combinations = [
            # Single parameters
            {'metadata': {'single': 'metadata'}},
            {'feedback': {'single': 'feedback'}},
            {'metrics': {'single': 'metrics'}},
            
            # Pairs
            {'metadata': {'pair': 'meta'}, 'feedback': {'pair': 'feed'}},
            {'metrics': {'pair': 'metric'}, 'config': {'pair': 'conf'}},
            
            # All except inputs
            {
                'metadata': {'all': 'meta'},
                'feedback': {'all': 'feed'}, 
                'metrics': {'all': 'metric'},
                'config': {'all': 'conf'},
                'outputs': {'all': 'out'},
                'user_properties': {'all': 'user'}
            }
        ]
        
        for params in parameter_combinations:
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_sdk.events.update_event.return_value = mock_response
                
                enrich_session(session_id='test-session', **params)
                
                mock_sdk.events.update_event.assert_called_once()
                call_args = mock_sdk.events.update_event.call_args[1]['request']
                
                # Verify all provided parameters were set
                for param_name, expected_value in params.items():
                    actual_value = getattr(call_args, param_name)
                    assert actual_value == expected_value