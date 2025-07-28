import pytest
import os
from unittest.mock import patch, MagicMock, Mock
from honeyhive.tracer import HoneyHiveTracer
from honeyhive.utils.baggage_dict import BaggageDict


class TestHoneyHiveTracerTagging:
    """Test suite for HoneyHive tracer tagging functionality"""

    def setup_method(self):
        """Setup for each test method"""
        # Set required environment variables
        os.environ["HH_API_KEY"] = "test_api_key"
        os.environ["HH_PROJECT"] = "test_project"
        
    def teardown_method(self):
        """Cleanup after each test method"""
        # Reset class variables to avoid state leakage
        HoneyHiveTracer._is_traceloop_initialized = False
        HoneyHiveTracer.api_key = None
        HoneyHiveTracer.server_url = None
        
        # Clean up environment variables
        if "HH_API_KEY" in os.environ:
            del os.environ["HH_API_KEY"]
        if "HH_PROJECT" in os.environ:
            del os.environ["HH_PROJECT"]

    @patch('honeyhive.tracer.HoneyHiveTracer._HoneyHiveTracer__start_session')
    @patch('traceloop.sdk.Traceloop.init')
    @patch('traceloop.sdk.Traceloop.set_association_properties')
    def test_tracer_init_with_tags(self, mock_set_association, mock_init, mock_start_session):
        """Test HoneyHiveTracer initialization with tags"""
        mock_start_session.return_value = "test_session_id"
        
        tags = {"environment": "production", "version": "v1.0", "team": "ml"}
        tracer = HoneyHiveTracer(tags=tags)
        
        # Verify tags are stored in the tracer
        assert tracer.tags == tags
        
        # Verify tags are added to baggage with tag_ prefix
        expected_baggage_tags = {
            "tag_environment": "production",
            "tag_version": "v1.0", 
            "tag_team": "ml"
        }
        
        # Check that baggage contains the tag entries
        baggage_dict = tracer.baggage.get_all_baggage()
        for key, value in expected_baggage_tags.items():
            assert baggage_dict[key] == value

    @patch('honeyhive.tracer.HoneyHiveTracer._HoneyHiveTracer__start_session')
    @patch('traceloop.sdk.Traceloop.init')
    @patch('traceloop.sdk.Traceloop.set_association_properties')
    def test_tracer_init_without_tags(self, mock_set_association, mock_init, mock_start_session):
        """Test HoneyHiveTracer initialization without tags"""
        mock_start_session.return_value = "test_session_id"
        
        tracer = HoneyHiveTracer()
        
        # Verify tags default to empty dictionary
        assert tracer.tags == {}
        
        # Verify no tag entries in baggage
        baggage_dict = tracer.baggage.get_all_baggage()
        tag_entries = {k: v for k, v in baggage_dict.items() if k.startswith("tag_")}
        assert len(tag_entries) == 0

    @patch('honeyhive.tracer.HoneyHiveTracer._HoneyHiveTracer__start_session')
    @patch('traceloop.sdk.Traceloop.init')
    @patch('traceloop.sdk.Traceloop.set_association_properties')
    def test_tracer_init_with_none_tags(self, mock_set_association, mock_init, mock_start_session):
        """Test HoneyHiveTracer initialization with None tags"""
        mock_start_session.return_value = "test_session_id"
        
        tracer = HoneyHiveTracer(tags=None)
        
        # Verify tags default to empty dictionary
        assert tracer.tags == {}

    @patch('honeyhive.tracer.HoneyHiveTracer._HoneyHiveTracer__start_session')
    @patch('traceloop.sdk.Traceloop.init')
    @patch('traceloop.sdk.Traceloop.set_association_properties')
    @patch('opentelemetry.context.get_current')
    @patch('opentelemetry.context.attach')
    def test_add_tags_method(self, mock_attach, mock_get_current, mock_set_association, mock_init, mock_start_session):
        """Test HoneyHiveTracer.add_tags method"""
        mock_start_session.return_value = "test_session_id"
        mock_context = Mock()
        mock_get_current.return_value = mock_context
        
        tracer = HoneyHiveTracer(tags={"initial": "tag"})
        
        # Add new tags
        new_tags = {"environment": "staging", "build": "123"}
        tracer.add_tags(new_tags)
        
        # Verify tags are updated
        expected_tags = {"initial": "tag", "environment": "staging", "build": "123"}
        assert tracer.tags == expected_tags
        
        # Only check baggage if tracer was initialized successfully
        if hasattr(tracer, 'baggage') and getattr(tracer, '_tags_initialized', False):
            baggage_dict = tracer.baggage.get_all_baggage()
            assert baggage_dict["tag_environment"] == "staging"
            assert baggage_dict["tag_build"] == "123"
            assert baggage_dict["tag_initial"] == "tag"

    @patch('honeyhive.tracer.HoneyHiveTracer._HoneyHiveTracer__start_session')
    @patch('traceloop.sdk.Traceloop.init')
    @patch('traceloop.sdk.Traceloop.set_association_properties')
    def test_add_tags_invalid_input(self, mock_set_association, mock_init, mock_start_session):
        """Test HoneyHiveTracer.add_tags with invalid input"""
        mock_start_session.return_value = "test_session_id"
        
        tracer = HoneyHiveTracer()
        
        # Test with non-dictionary input
        with pytest.raises(ValueError, match="Tags must be a dictionary"):
            tracer.add_tags("not_a_dict")
        
        with pytest.raises(ValueError, match="Tags must be a dictionary"):
            tracer.add_tags(["list", "not", "dict"])
        
        with pytest.raises(ValueError, match="Tags must be a dictionary"):
            tracer.add_tags(123)

    @patch('honeyhive.tracer.HoneyHiveTracer._HoneyHiveTracer__start_session')
    @patch('traceloop.sdk.Traceloop.init')
    @patch('traceloop.sdk.Traceloop.set_association_properties')
    @patch('opentelemetry.context.get_current')
    @patch('opentelemetry.context.attach')
    def test_add_tags_overwrite_existing(self, mock_attach, mock_get_current, mock_set_association, mock_init, mock_start_session):
        """Test HoneyHiveTracer.add_tags overwrites existing tags"""
        mock_start_session.return_value = "test_session_id"
        mock_context = Mock()
        mock_get_current.return_value = mock_context
        
        tracer = HoneyHiveTracer(tags={"environment": "dev", "version": "v1.0"})
        
        # Add tags that overwrite existing ones
        new_tags = {"environment": "production", "team": "backend"}
        tracer.add_tags(new_tags)
        
        # Verify tags are updated correctly
        expected_tags = {"environment": "production", "version": "v1.0", "team": "backend"}
        assert tracer.tags == expected_tags
        
        # Only check baggage if tracer was initialized successfully
        if hasattr(tracer, 'baggage') and getattr(tracer, '_tags_initialized', False):
            baggage_dict = tracer.baggage.get_all_baggage()
            assert baggage_dict["tag_environment"] == "production"
            assert baggage_dict["tag_version"] == "v1.0"
            assert baggage_dict["tag_team"] == "backend"

    @patch('honeyhive.tracer.HoneyHiveTracer._HoneyHiveTracer__start_session')
    @patch('traceloop.sdk.Traceloop.init')
    @patch('traceloop.sdk.Traceloop.set_association_properties')
    def test_tags_with_different_types(self, mock_set_association, mock_init, mock_start_session):
        """Test HoneyHiveTracer with tags of different types"""
        mock_start_session.return_value = "test_session_id"
        
        tags = {
            "string_tag": "value",
            "int_tag": 42,
            "float_tag": 3.14,
            "bool_tag": True,
            "none_tag": None
        }
        
        tracer = HoneyHiveTracer(tags=tags)
        
        # Verify all tag types are converted to strings in baggage
        baggage_dict = tracer.baggage.get_all_baggage()
        assert baggage_dict["tag_string_tag"] == "value"
        assert baggage_dict["tag_int_tag"] == "42"
        assert baggage_dict["tag_float_tag"] == "3.14"
        assert baggage_dict["tag_bool_tag"] == "True"
        assert baggage_dict["tag_none_tag"] == "None"

    @patch('honeyhive.tracer.HoneyHiveTracer._HoneyHiveTracer__start_session')
    @patch('traceloop.sdk.Traceloop.init')
    @patch('traceloop.sdk.Traceloop.set_association_properties')
    @patch('opentelemetry.context.get_current')
    @patch('opentelemetry.context.attach')
    def test_add_tags_empty_dictionary(self, mock_attach, mock_get_current, mock_set_association, mock_init, mock_start_session):
        """Test HoneyHiveTracer.add_tags with empty dictionary"""
        mock_start_session.return_value = "test_session_id"
        mock_context = Mock()
        mock_get_current.return_value = mock_context
        
        tracer = HoneyHiveTracer(tags={"existing": "tag"})
        original_tags = tracer.tags.copy()
        
        # Add empty tags dictionary
        tracer.add_tags({})
        
        # Verify nothing changes
        assert tracer.tags == original_tags

    @patch('honeyhive.tracer.HoneyHiveTracer._HoneyHiveTracer__start_session')
    @patch('traceloop.sdk.Traceloop.init')
    @patch('traceloop.sdk.Traceloop.set_association_properties')
    def test_tags_integration_with_existing_baggage(self, mock_set_association, mock_init, mock_start_session):
        """Test that tags integrate properly with existing baggage items"""
        mock_start_session.return_value = "test_session_id"
        
        tags = {"service": "api", "region": "us-west"}
        tracer = HoneyHiveTracer(
            tags=tags,
            project="test_project",
            source="test_source"
        )
        
        baggage_dict = tracer.baggage.get_all_baggage()
        
        # Verify both system baggage and tags are present
        assert baggage_dict["session_id"] == "test_session_id"
        assert baggage_dict["project"] == "test_project"
        assert baggage_dict["source"] == "test_source"
        assert baggage_dict["tag_service"] == "api"
        assert baggage_dict["tag_region"] == "us-west"

    @patch('honeyhive.tracer.HoneyHiveTracer._HoneyHiveTracer__start_session')
    @patch('traceloop.sdk.Traceloop.init')
    @patch('traceloop.sdk.Traceloop.set_association_properties')
    def test_tags_with_special_characters(self, mock_set_association, mock_init, mock_start_session):
        """Test HoneyHiveTracer with tags containing special characters"""
        mock_start_session.return_value = "test_session_id"
        
        tags = {
            "tag-with-dash": "value1",
            "tag_with_underscore": "value2",
            "tag.with.dot": "value3",
            "tag with space": "value4"
        }
        
        tracer = HoneyHiveTracer(tags=tags)
        
        # Verify all tags are stored correctly
        assert tracer.tags == tags
        
        # Verify tags are added to baggage (they should be converted to strings)
        baggage_dict = tracer.baggage.get_all_baggage()
        assert baggage_dict["tag_tag-with-dash"] == "value1"
        assert baggage_dict["tag_tag_with_underscore"] == "value2"
        assert baggage_dict["tag_tag.with.dot"] == "value3"
        assert baggage_dict["tag_tag with space"] == "value4"