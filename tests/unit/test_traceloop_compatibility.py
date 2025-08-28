"""Test traceloop compatibility for association_properties."""

import pytest
from unittest.mock import Mock, patch
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.context import Context

from honeyhive.tracer.span_processor import HoneyHiveSpanProcessor


class TestTraceloopCompatibility:
    """Test that association_properties are converted to traceloop format."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = HoneyHiveSpanProcessor()
        
        # Create a proper mock span with set_attribute method
        self.mock_span = Mock()
        self.mock_span.set_attribute = Mock()
        
        self.mock_context = Mock(spec=Context)
        
        # Mock the baggage module
        self.baggage_patcher = patch('honeyhive.tracer.span_processor.baggage')
        self.mock_baggage = self.baggage_patcher.start()
        
        # Mock OpenTelemetry availability
        self.otel_patcher = patch('honeyhive.tracer.span_processor.OTEL_AVAILABLE', True)
        self.mock_otel = self.otel_patcher.start()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.baggage_patcher.stop()
        self.otel_patcher.stop()
    
    def test_association_properties_converted_to_traceloop_format(self):
        """Test that association_properties are converted to traceloop.association.properties.* format."""
        # Mock context with association_properties
        mock_context = Mock()
        # The context should have association_properties as a nested key
        mock_context.get.side_effect = lambda key: {
            'association_properties': {
                'user_id': 'legacy_user_123',
                'tenant_id': 'legacy_tenant_456',
                'environment': 'legacy_prod'
            }
        }.get(key)
        
        # Mock baggage to return values for required fields, but None for association_properties keys
        def mock_get_baggage(key, ctx):
            if key == 'session_id':
                return 'baggage_session_123'
            elif key == 'project':
                return 'baggage_project'
            elif key == 'source':
                return 'baggage_source'
            elif key == 'parent_id':
                return None
            else:
                # For association_properties keys, return None so they get set from association_properties
                return None
        
        self.mock_baggage.get_baggage.side_effect = mock_get_baggage
        
        # Debug: Print what we're setting up
        print(f"Mock context: {mock_context}")
        print(f"Mock context.get('association_properties'): {mock_context.get('association_properties')}")
        print(f"Mock baggage get_baggage side effect: {self.mock_baggage.get_baggage.side_effect}")
        
        # Call on_start with the mock context
        self.processor.on_start(self.mock_span, mock_context)
        
        # Debug: Print what happened
        print(f"Mock span set_attribute calls: {self.mock_span.set_attribute.call_args_list}")
        print(f"Mock baggage get_baggage calls: {self.mock_baggage.get_baggage.call_args_list}")
        
        # Verify that the span attributes were set with traceloop format
        # We expect 9 calls: 3 from baggage + 3 from association_properties + 3 traceloop equivalents
        actual_calls = self.mock_span.set_attribute.call_args_list
        assert len(actual_calls) == 9, f"Expected 9 calls, got {len(actual_calls)}"
        
        # Verify traceloop format attributes are present
        traceloop_attrs = [call[0] for call in actual_calls if call[0][0].startswith('traceloop.association.properties')]
        assert len(traceloop_attrs) == 6, f"Expected 6 traceloop attributes, got {len(traceloop_attrs)}"
        
        # Verify specific traceloop attributes
        traceloop_keys = [attr[0] for attr in traceloop_attrs]
        assert 'traceloop.association.properties.user_id' in traceloop_keys
        assert 'traceloop.association.properties.tenant_id' in traceloop_keys
        assert 'traceloop.association.properties.environment' in traceloop_keys
        assert 'traceloop.association.properties.session_id' in traceloop_keys
        assert 'traceloop.association.properties.project' in traceloop_keys
        assert 'traceloop.association.properties.source' in traceloop_keys
    
    def test_association_properties_skipped_if_already_in_baggage(self):
        """Test that association_properties are skipped if already set via baggage."""
        # Mock context with association_properties
        mock_context = Mock()
        # The context should have association_properties as a nested key
        mock_context.get.side_effect = lambda key: {
            'association_properties': {
                'session_id': 'legacy_session_123',
                'user_id': 'legacy_user_456'
            }
        }.get(key)
        
        # Mock baggage to return values for some keys (already set)
        def mock_get_baggage(key, ctx):
            if key == 'session_id':
                return 'baggage_session_123'
            elif key == 'project':
                return 'baggage_project'
            elif key == 'source':
                return 'baggage_source'
            elif key == 'parent_id':
                return None
            else:
                # For user_id, return None so it gets set from association_properties
                return None
        
        self.mock_baggage.get_baggage.side_effect = mock_get_baggage
        
        # Call on_start with the mock context
        self.processor.on_start(self.mock_span, mock_context)
        
        # Verify that session_id was not set from association_properties
        # (because it was already in baggage)
        actual_calls = self.mock_span.set_attribute.call_args_list
        
        # session_id should come from baggage, not association_properties
        baggage_session_calls = [call for call in actual_calls if call[0][0] == 'honeyhive.session_id']
        assert len(baggage_session_calls) == 1
        assert baggage_session_calls[0][0][1] == 'baggage_session_123'
        
        # traceloop.association.properties.session_id SHOULD be set (both formats always needed)
        traceloop_session_calls = [call for call in actual_calls if call[0][0] == 'traceloop.association.properties.session_id']
        assert len(traceloop_session_calls) == 1, "traceloop session_id should be set for backend compatibility"
        assert traceloop_session_calls[0][0][1] == 'baggage_session_123'
        
        # user_id should be set from association_properties (not in baggage)
        traceloop_user_calls = [call for call in actual_calls if call[0][0] == 'traceloop.association.properties.user_id']
        assert len(traceloop_user_calls) == 1
        assert traceloop_user_calls[0][0][1] == 'legacy_user_456'
    
    def test_association_properties_handles_none_values(self):
        """Test that association_properties handles None values gracefully."""
        # Mock context with association_properties containing None values
        mock_context = Mock()
        # The context should have association_properties as a nested key
        mock_context.get.side_effect = lambda key: {
            'association_properties': {
                'user_id': 'legacy_user_123',
                'project': None,
                'environment': 'legacy_prod',
                'empty_value': None
            }
        }.get(key)
        
        # Mock baggage to return values for required fields, but None for association_properties keys
        def mock_get_baggage(key, ctx):
            if key == 'session_id':
                return 'baggage_session_123'
            elif key == 'project':
                return 'baggage_project'
            elif key == 'source':
                return 'baggage_source'
            elif key == 'parent_id':
                return None
            else:
                # For association_properties keys, return None so they get set from association_properties
                return None
        
        self.mock_baggage.get_baggage.side_effect = mock_get_baggage
        
        # Call on_start with the mock context
        self.processor.on_start(self.mock_span, mock_context)
        
        # Verify that only non-None values were set
        actual_calls = self.mock_span.set_attribute.call_args_list
        
        # Check that traceloop attributes were set for non-None values
        traceloop_attrs = [call[0] for call in actual_calls if call[0][0].startswith('traceloop.association.properties')]
        
        # Should have 5 traceloop attributes: 2 from association_properties + 3 from baggage equivalents
        assert len(traceloop_attrs) == 5, f"Expected 5 traceloop attributes, got {len(traceloop_attrs)}"
        
        traceloop_keys = [attr[0] for attr in traceloop_attrs]
        assert 'traceloop.association.properties.user_id' in traceloop_keys
        assert 'traceloop.association.properties.environment' in traceloop_keys
        # project should be set from baggage (both formats always needed for backend compatibility)
        assert 'traceloop.association.properties.project' in traceloop_keys
        assert 'traceloop.association.properties.empty_value' not in traceloop_keys
    
    def test_association_properties_handles_missing_get_method(self):
        """Test that association_properties handles contexts without get method gracefully."""
        # Mock context without get method
        mock_context = Mock()
        del mock_context.get  # Remove get method
        
        # Mock baggage to return None for all keys
        self.mock_baggage.get_baggage.side_effect = lambda key, ctx: None
        
        # Call on_start with the mock context - should not raise an exception
        try:
            self.processor.on_start(self.mock_span, mock_context)
        except Exception as e:
            pytest.fail(f"on_start should handle missing get method gracefully, but raised: {e}")
        
        # Verify that no traceloop attributes were set
        actual_calls = self.mock_span.set_attribute.call_args_list
        traceloop_attrs = [call for call in actual_calls if call[0][0].startswith('traceloop.association.properties')]
        assert len(traceloop_attrs) == 0, "No traceloop attributes should be set when context has no get method"
    
    def test_association_properties_handles_exception_gracefully(self):
        """Test that association_properties handles exceptions gracefully."""
        # Mock context that raises an exception when get is called
        mock_context = Mock()
        mock_context.get.side_effect = Exception("Context error")
        
        # Mock baggage to return None for all keys
        self.mock_baggage.get_baggage.side_effect = lambda key, ctx: None
        
        # Call on_start with the mock context - should not raise an exception
        try:
            self.processor.on_start(self.mock_span, mock_context)
        except Exception as e:
            pytest.fail(f"on_start should handle context exceptions gracefully, but raised: {e}")
        
        # Verify that no traceloop attributes were set due to the exception
        actual_calls = self.mock_span.set_attribute.call_args_list
        traceloop_attrs = [call for call in actual_calls if call[0][0].startswith('traceloop.association.properties')]
        assert len(traceloop_attrs) == 0, "No traceloop attributes should be set when context.get raises an exception"
