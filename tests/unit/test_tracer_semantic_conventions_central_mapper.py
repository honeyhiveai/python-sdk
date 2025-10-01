"""Unit tests for tracer.semantic_conventions.central_mapper module.

This module tests the CentralEventMapper class and get_central_mapper factory function,
which provide centralized semantic convention mapping for all extractors.

Test Coverage:
- CentralEventMapper class with 14 methods
- get_central_mapper factory function
- Convention detection logic (unique attributes vs patterns)
- Mapping pipeline with rule engine integration
- LLM event creation with Pydantic validation
- Exception handling and graceful degradation
- Statistics tracking across operations

Quality Targets:
- 100% pass rate
- 90%+ line coverage (483/537 lines)
- 10.0/10 Pylint score
- 0 MyPy errors
"""

# pylint: disable=too-many-lines,too-many-public-methods,unused-argument
# pylint: disable=redefined-outer-name,protected-access,line-too-long

from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch, PropertyMock

import pytest

from honeyhive.tracer.semantic_conventions.central_mapper import (
    CentralEventMapper,
    get_central_mapper,
)
from honeyhive.tracer.semantic_conventions.schema import EventType


class TestCentralEventMapper:
    """Test cases for CentralEventMapper class."""

    @pytest.fixture
    def mock_discovery(self) -> Mock:
        """Mock discovery instance with convention definitions."""
        mock_discovery = Mock()
        
        # Mock convention definition
        mock_definition = Mock()
        mock_definition.provider = "openinference"
        mock_definition.version = (0, 1, 31)
        mock_definition.version_string = "0.1.31"
        mock_definition.definition_data = {
            "detection_patterns": {
                "unique_attributes": ["gen_ai.system"],
                "required_attributes": ["llm.request.type"],
                "signature_attributes": ["gen_ai.request.model"],
                "attribute_patterns": ["gen_ai.*"]
            }
        }
        
        mock_discovery.definitions = {"openinference_v0_1_31": mock_definition}
        return mock_discovery

    @pytest.fixture
    def mock_rule_engine(self) -> Mock:
        """Mock rule engine for rule creation."""
        mock_engine = Mock()
        mock_engine.create_rules.return_value = [
            {"source": "gen_ai.request.model", "target": "config.model"},
            {"source": "llm.request.type", "target": "metadata.llm.request.type"}
        ]
        return mock_engine

    @pytest.fixture
    def mock_rule_applier(self) -> Mock:
        """Mock rule applier for attribute transformation."""
        mock_applier = Mock()
        mock_applier.apply_rules.return_value = {
            "inputs": {"chat_history": [{"role": "user", "content": "test"}]},
            "outputs": {"content": "response", "role": "assistant"},
            "config": {"model": "gpt-4", "provider": "openai"},
            "metadata": {"llm.request.type": "chat"}
        }
        return mock_applier

    @pytest.fixture
    def central_mapper(
        self, mock_discovery, mock_rule_engine, mock_rule_applier, request
    ) -> CentralEventMapper:
        """Create CentralEventMapper with all dependencies mocked.
        
        This fixture handles all the necessary patching so individual tests
        don't need to repeat the same patch decorators.
        """
        # Create persistent patches
        patcher_discovery = patch("honeyhive.tracer.semantic_conventions.central_mapper.get_discovery_instance", return_value=mock_discovery)
        patcher_rule_engine = patch("honeyhive.tracer.semantic_conventions.central_mapper.RuleEngine", return_value=mock_rule_engine)
        patcher_rule_applier = patch("honeyhive.tracer.semantic_conventions.central_mapper.RuleApplier", return_value=mock_rule_applier)
        patcher_safe_log = patch("honeyhive.tracer.semantic_conventions.central_mapper.safe_log")
        
        # Start all patches
        patcher_discovery.start()
        patcher_rule_engine.start()
        patcher_rule_applier.start()
        mock_safe_log = patcher_safe_log.start()
        
        # Register cleanup with pytest
        def cleanup():
            patcher_safe_log.stop()
            patcher_rule_applier.stop()
            patcher_rule_engine.stop()
            patcher_discovery.stop()
        
        request.addfinalizer(cleanup)
        
        # Create mapper
        mapper = CentralEventMapper()
        # Store the mock for test access
        mapper._mock_safe_log = mock_safe_log
        
        return mapper

    def test_init_creates_dependencies(self, mock_discovery, mock_rule_engine, mock_rule_applier):
        """Test __init__ creates all required dependencies."""
        with patch("honeyhive.tracer.semantic_conventions.central_mapper.get_discovery_instance", return_value=mock_discovery), \
             patch("honeyhive.tracer.semantic_conventions.central_mapper.RuleEngine", return_value=mock_rule_engine), \
             patch("honeyhive.tracer.semantic_conventions.central_mapper.RuleApplier", return_value=mock_rule_applier):
            
            mapper = CentralEventMapper()
            
            assert mapper.discovery == mock_discovery
            assert mapper.rule_engine == mock_rule_engine
            assert mapper.rule_applier == mock_rule_applier
            assert mapper.schema_stats == {
                "events_mapped": 0,
                "validation_errors": 0,
                "schema_types_used": {}
            }

    def test_map_attributes_to_schema_successful_mapping(self, central_mapper):
        """Test successful attribute mapping with detected convention."""
        attributes = {
            "gen_ai.system": "openai",
            "llm.request.type": "chat",
            "gen_ai.request.model": "gpt-4"
        }
        
        result = central_mapper.map_attributes_to_schema(attributes, "model")
        
        # Verify result structure
        assert "inputs" in result
        assert "outputs" in result
        assert "config" in result
        assert "metadata" in result
        
        # Verify statistics updated
        assert central_mapper.schema_stats["events_mapped"] == 1
        assert central_mapper.schema_stats["schema_types_used"]["model"] == 1
        
        # Verify logging calls (using stored mock)
        assert central_mapper._mock_safe_log.call_count >= 2  # Debug and info logs

    def test_map_attributes_to_schema_unknown_convention(self, central_mapper):
        """Test mapping with unknown convention returns empty structure."""
        # Mock discovery to return no definitions
        central_mapper.discovery.definitions = {}
        
        attributes = {"unknown.attribute": "value"}
        
        result = central_mapper.map_attributes_to_schema(attributes, "model")
        
        # Verify empty structure returned
        assert result == {"inputs": {}, "outputs": {}, "config": {}, "metadata": {}}
        
        # Verify no statistics updated for failed mapping
        assert central_mapper.schema_stats["events_mapped"] == 0

    def test_map_attributes_to_schema_no_definition_found(self, central_mapper):
        """Test mapping when convention detected but no definition found."""
        # Mock _detect_convention to return provider not in definitions
        with patch.object(central_mapper, "_detect_convention", return_value="unknown_provider"):
            attributes = {"test.attribute": "value"}
            
            result = central_mapper.map_attributes_to_schema(attributes, "model")
            
            # Verify empty structure returned
            assert result == {"inputs": {}, "outputs": {}, "config": {}, "metadata": {}}
            
            # Verify warning logged
            central_mapper._mock_safe_log.assert_any_call(
                None,
                "warning",
                "No definition found for detected convention: unknown_provider"
            )

    def test_map_attributes_to_schema_exception_handling(self, central_mapper):
        """Test exception handling in map_attributes_to_schema."""
        # Mock _detect_convention to raise exception
        with patch.object(central_mapper, "_detect_convention", side_effect=Exception("Test error")):
            attributes = {"test.attribute": "value"}
            
            result = central_mapper.map_attributes_to_schema(attributes, "model")
            
            # Verify empty structure returned
            assert result == {"inputs": {}, "outputs": {}, "config": {}, "metadata": {}}
            
            # Verify error logged and statistics updated
            central_mapper._mock_safe_log.assert_any_call(
                None,
                "error",
                "Semantic convention mapping failed for event_type model: Test error"
            )
            assert central_mapper.schema_stats["validation_errors"] == 1

    def test_detect_convention_compatibility_method(self, central_mapper):
        """Test detect_convention public method delegates to _detect_convention."""
        attributes = {"test.attribute": "value"}
        
        with patch.object(central_mapper, "_detect_convention", return_value="openinference") as mock_detect:
            result = central_mapper.detect_convention(attributes)
            
            assert result == "openinference"
            mock_detect.assert_called_once_with(attributes)

    def test_detect_convention_unique_attributes_match(self, central_mapper):
        """Test convention detection via unique attributes (first pass)."""
        attributes = {
            "gen_ai.system": "openai",  # Unique attribute for openinference
            "other.attribute": "value"
        }
        
        result = central_mapper._detect_convention(attributes)
        
        assert result == "openinference"
        
        # Verify debug log for unique attribute match
        central_mapper._mock_safe_log.assert_any_call(
            None,
            "debug",
            "🎯 Matched convention by unique attributes: openinference v0.1.31"
        )

    def test_detect_convention_pattern_match(self, central_mapper):
        """Test convention detection via general patterns (second pass)."""
        # Mock definition without unique attributes but with patterns
        mock_definition = Mock()
        mock_definition.provider = "traceloop"
        mock_definition.version = (0, 46, 2)
        mock_definition.version_string = "0.46.2"
        mock_definition.definition_data = {
            "detection_patterns": {
                "unique_attributes": [],  # No unique attributes
                "required_attributes": ["llm.request.type"],
                "signature_attributes": ["traceloop.span.kind"],
                "attribute_patterns": ["traceloop.*"]
            }
        }
        
        central_mapper.discovery.definitions = {
            "openinference_v0_1_31": central_mapper.discovery.definitions["openinference_v0_1_31"],
            "traceloop_v0_46_2": mock_definition
        }
        
        attributes = {
            "llm.request.type": "chat",
            "traceloop.span.kind": "llm",
            "traceloop.entity.name": "test"
        }
        
        # Mock _has_unique_attributes to return False for first pass
        with patch.object(central_mapper, "_has_unique_attributes", return_value=False), \
             patch.object(central_mapper, "_matches_definition", side_effect=lambda attrs, defn: defn.provider == "traceloop"):
            
            result = central_mapper._detect_convention(attributes)
            
            assert result == "traceloop"
            
            # Verify debug log for pattern match
            central_mapper._mock_safe_log.assert_any_call(
                None,
                "debug",
                "🔍 Matched convention by patterns: traceloop v0.46.2"
            )

    def test_detect_convention_no_match(self, central_mapper):
        """Test convention detection when no convention matches."""
        attributes = {"unknown.attribute": "value"}
        
        # Mock both passes to return False
        with patch.object(central_mapper, "_has_unique_attributes", return_value=False), \
             patch.object(central_mapper, "_matches_definition", return_value=False):
            
            result = central_mapper._detect_convention(attributes)
            
            assert result == "unknown"
            
            # Verify debug log for no match
            central_mapper._mock_safe_log.assert_any_call(
                None,
                "debug",
                "🔍 No convention matched for 1 attributes"
            )

    def test_detect_convention_exception_handling(self, central_mapper):
        """Test graceful degradation when _detect_convention encounters an exception."""
        attributes = {"test.attribute": "value"}
        
        # Mock _has_unique_attributes to raise an exception to trigger graceful degradation
        with patch.object(central_mapper, "_has_unique_attributes", side_effect=Exception("Test error")):
            result = central_mapper._detect_convention(attributes)
            
            # Verify graceful degradation: returns safe default
            assert result == "unknown"
            
            # Verify error logged for graceful degradation
            central_mapper._mock_safe_log.assert_any_call(None, "error", "Convention detection failed: Test error")

    def test_has_unique_attributes_found(self, central_mapper):
        """Test _has_unique_attributes when unique attribute is present."""
        attributes = {"gen_ai.system": "openai", "other.attr": "value"}
        definition = central_mapper.discovery.definitions["openinference_v0_1_31"]
        
        result = central_mapper._has_unique_attributes(attributes, definition)
        
        assert result is True
        
        # Verify debug log
        central_mapper._mock_safe_log.assert_any_call(
            None,
            "debug",
            "🎯 Found unique attribute 'gen_ai.system' for openinference"
        )

    def test_has_unique_attributes_not_found(self, central_mapper):
        """Test _has_unique_attributes when no unique attributes present."""
        attributes = {"other.attribute": "value"}
        definition = central_mapper.discovery.definitions["openinference_v0_1_31"]
        
        result = central_mapper._has_unique_attributes(attributes, definition)
        
        assert result is False

    def test_has_unique_attributes_no_definition_data(self, central_mapper):
        """Test _has_unique_attributes with no definition data."""
        attributes = {"test.attribute": "value"}
        
        mock_definition = Mock()
        mock_definition.definition_data = None
        
        result = central_mapper._has_unique_attributes(attributes, mock_definition)
        
        assert result is False

    def test_has_unique_attributes_no_unique_attrs(self, central_mapper):
        """Test _has_unique_attributes with no unique attributes in definition."""
        attributes = {"test.attribute": "value"}
        
        mock_definition = Mock()
        mock_definition.definition_data = {
            "detection_patterns": {
                "unique_attributes": []  # Empty list
            }
        }
        
        result = central_mapper._has_unique_attributes(attributes, mock_definition)
        
        assert result is False

    def test_has_unique_attributes_exception_handling(self, central_mapper):
        """Test graceful degradation when _has_unique_attributes encounters an exception."""
        attributes = {"test.attribute": "value"}
        
        mock_definition = Mock()
        mock_definition.provider = "test_provider"
        # Configure definition_data to raise exception when accessed
        type(mock_definition).definition_data = PropertyMock(side_effect=Exception("Test error"))
        
        result = central_mapper._has_unique_attributes(attributes, mock_definition)
        
        # Verify graceful degradation: returns safe default
        assert result is False
        
        # Verify warning logged for graceful degradation
        central_mapper._mock_safe_log.assert_any_call(
            None,
            "warning",
            "Error checking unique attributes for test_provider: Test error"
        )

    def test_matches_definition_all_criteria_met(self, central_mapper):
        """Test _matches_definition when all criteria are met."""
        attributes = {
            "llm.request.type": "chat",  # Required
            "gen_ai.request.model": "gpt-4",  # Signature
            "gen_ai.system": "openai"  # Pattern match
        }
        definition = central_mapper.discovery.definitions["openinference_v0_1_31"]
        
        result = central_mapper._matches_definition(attributes, definition)
        
        assert result is True

    def test_matches_definition_missing_required(self, central_mapper):
        """Test _matches_definition when required attributes missing."""
        attributes = {
            "gen_ai.request.model": "gpt-4",  # Signature present
            "gen_ai.system": "openai"  # Pattern match
            # Missing required: llm.request.type
        }
        definition = central_mapper.discovery.definitions["openinference_v0_1_31"]
        
        result = central_mapper._matches_definition(attributes, definition)
        
        assert result is False

    def test_matches_definition_missing_signature(self, central_mapper):
        """Test _matches_definition when signature attributes missing."""
        # Mock definition with signature attributes
        mock_definition = Mock()
        mock_definition.definition_data = {
            "detection_patterns": {
                "required_attributes": [],
                "signature_attributes": ["required.signature"],
                "attribute_patterns": []
            }
        }
        
        attributes = {"other.attribute": "value"}  # No signature attributes
        
        result = central_mapper._matches_definition(attributes, mock_definition)
        
        assert result is False

    def test_matches_definition_pattern_prefix_match(self, central_mapper):
        """Test _matches_definition with wildcard pattern matching."""
        mock_definition = Mock()
        mock_definition.definition_data = {
            "detection_patterns": {
                "required_attributes": [],
                "signature_attributes": [],
                "attribute_patterns": ["gen_ai.*"]  # Wildcard pattern
            }
        }
        
        attributes = {"gen_ai.request.model": "gpt-4"}  # Matches pattern
        
        result = central_mapper._matches_definition(attributes, mock_definition)
        
        assert result is True

    def test_matches_definition_pattern_exact_match(self, central_mapper):
        """Test _matches_definition with exact pattern matching."""
        mock_definition = Mock()
        mock_definition.definition_data = {
            "detection_patterns": {
                "required_attributes": [],
                "signature_attributes": [],
                "attribute_patterns": ["exact.match"]  # Exact pattern
            }
        }
        
        attributes = {"exact.match": "value"}  # Exact match
        
        result = central_mapper._matches_definition(attributes, mock_definition)
        
        assert result is True

    def test_matches_definition_no_pattern_match(self, central_mapper):
        """Test _matches_definition when no patterns match."""
        mock_definition = Mock()
        mock_definition.definition_data = {
            "detection_patterns": {
                "required_attributes": [],
                "signature_attributes": [],
                "attribute_patterns": ["specific.pattern"]
            }
        }
        
        attributes = {"other.attribute": "value"}  # No pattern match
        
        result = central_mapper._matches_definition(attributes, mock_definition)
        
        assert result is False

    def test_matches_definition_no_definition_data(self, central_mapper):
        """Test _matches_definition with no definition data."""
        mock_definition = Mock()
        mock_definition.definition_data = None
        
        attributes = {"test.attribute": "value"}
        
        result = central_mapper._matches_definition(attributes, mock_definition)
        
        assert result is False

    def test_matches_definition_exception_handling(self, central_mapper):
        """Test exception handling in _matches_definition."""
        mock_definition = Mock()
        mock_definition.provider = "test_provider"
        # Create definition_data that will cause an exception during pattern matching
        mock_definition.definition_data = {
            "detection_patterns": {
                "attribute_patterns": [123]  # Non-string pattern will cause AttributeError
            }
        }
        
        attributes = {"test.attribute": "value"}
        
        result = central_mapper._matches_definition(attributes, mock_definition)
        
        assert result is False
        
        # Verify warning logged
        central_mapper._mock_safe_log.assert_any_call(
            None,
            "warning",
            "Error matching definition test_provider: 'int' object has no attribute 'endswith'"
        )

    def test_get_definition_for_provider_found(self, central_mapper):
        """Test _get_definition_for_provider when provider is found."""
        result = central_mapper._get_definition_for_provider("openinference")
        
        assert result is not None
        assert result.provider == "openinference"
        
        # Verify debug log
        central_mapper._mock_safe_log.assert_any_call(
            None,
            "debug",
            "🔍 Found definition: openinference v0.1.31"
        )

    def test_get_definition_for_provider_not_found(self, central_mapper):
        """Test _get_definition_for_provider when provider not found."""
        result = central_mapper._get_definition_for_provider("unknown_provider")
        
        assert result is None

    def test_get_definition_for_provider_multiple_versions(self, central_mapper):
        """Test _get_definition_for_provider returns latest version."""
        # Add multiple versions of same provider
        mock_definition_old = Mock()
        mock_definition_old.provider = "openinference"
        mock_definition_old.version = (0, 1, 30)
        mock_definition_old.version_string = "0.1.30"
        
        mock_definition_new = Mock()
        mock_definition_new.provider = "openinference"
        mock_definition_new.version = (0, 1, 32)
        mock_definition_new.version_string = "0.1.32"
        
        central_mapper.discovery.definitions = {
            "openinference_v0_1_30": mock_definition_old,
            "openinference_v0_1_31": central_mapper.discovery.definitions["openinference_v0_1_31"],
            "openinference_v0_1_32": mock_definition_new
        }
        
        result = central_mapper._get_definition_for_provider("openinference")
        
        assert result == mock_definition_new  # Latest version
        assert result.version_string == "0.1.32"

    def test_get_definition_for_provider_exception_handling(self, central_mapper):
        """Test graceful degradation when _get_definition_for_provider encounters an exception."""
        # Configure discovery mock to raise exception when definitions is accessed
        type(central_mapper.discovery).definitions = PropertyMock(side_effect=Exception("Test error"))
        
        result = central_mapper._get_definition_for_provider("openinference")
        
        # Verify graceful degradation: returns safe default
        assert result is None
        
        # Verify error logged for graceful degradation
        central_mapper._mock_safe_log.assert_any_call(
            None,
            "error",
            "Error getting definition for openinference: Test error"
        )

    def test_create_base_event_default_values(self, central_mapper):
        """Test create_base_event with default values."""
        result = central_mapper.create_base_event("test_event", EventType.MODEL)
        
        assert result["event_name"] == "test_event"
        assert result["event_type"] == "model"
        assert result["source"] == "python-sdk"
        assert result["inputs"] == {}
        assert result["outputs"] == {}
        assert result["config"] == {}
        assert result["metadata"] == {}
        assert result["project_id"] is None
        assert result["event_id"] is None
        assert result["session_id"] is None
        assert result["parent_id"] is None
        assert result["children_ids"] == []
        assert result["error"] is None
        assert result["start_time"] is None
        assert result["end_time"] is None
        assert result["duration"] is None
        assert result["feedback"] == {}
        assert result["metrics"] == {}
        assert result["user_properties"] == {}

    def test_create_base_event_custom_source(self, central_mapper):
        """Test create_base_event with custom source."""
        result = central_mapper.create_base_event("test_event", EventType.CHAIN, "custom-source")
        
        assert result["event_name"] == "test_event"
        assert result["event_type"] == "chain"
        assert result["source"] == "custom-source"

    def test_map_llm_inputs_with_messages(self, central_mapper):
        """Test map_llm_inputs with messages."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        
        result = central_mapper.map_llm_inputs(messages=messages)
        
        assert "chat_history" in result
        assert len(result["chat_history"]) == 2
        assert result["chat_history"][0]["role"] == "user"
        assert result["chat_history"][0]["content"] == "Hello"
        assert result["chat_history"][1]["role"] == "assistant"
        assert result["chat_history"][1]["content"] == "Hi there"

    def test_map_llm_inputs_with_system_message(self, central_mapper):
        """Test map_llm_inputs with system message."""
        messages = [{"role": "user", "content": "Hello"}]
        system_message = "You are a helpful assistant"
        
        result = central_mapper.map_llm_inputs(
            messages=messages,
            system_message=system_message
        )
        
        assert len(result["chat_history"]) == 2
        assert result["chat_history"][0]["role"] == "system"
        assert result["chat_history"][0]["content"] == "You are a helpful assistant"
        assert result["chat_history"][1]["role"] == "user"
        assert result["chat_history"][1]["content"] == "Hello"

    def test_map_llm_inputs_with_prompts(self, central_mapper):
        """Test map_llm_inputs with prompts (alternative format)."""
        prompts = [
            {"role": "user", "content": "What is AI?"},
            "Simple string prompt"
        ]
        
        result = central_mapper.map_llm_inputs(prompts=prompts)
        
        assert len(result["chat_history"]) == 2
        assert result["chat_history"][0]["role"] == "user"
        assert result["chat_history"][0]["content"] == "What is AI?"
        assert result["chat_history"][1]["role"] == "user"
        assert result["chat_history"][1]["content"] == "Simple string prompt"

    def test_map_llm_inputs_with_functions(self, central_mapper):
        """Test map_llm_inputs with functions."""
        messages = [{"role": "user", "content": "Call a function"}]
        functions = [{"name": "get_weather", "description": "Get weather info"}]
        
        result = central_mapper.map_llm_inputs(messages=messages, functions=functions)
        
        assert "chat_history" in result
        assert "functions" in result
        assert result["functions"] == functions

    def test_map_llm_inputs_message_normalization(self, central_mapper):
        """Test map_llm_inputs normalizes message formats."""
        messages = [
            {"role": "user", "text": "Using text field"},  # text -> content
            {"role": "assistant", "content": "Normal content", "extra": "field"}
        ]
        
        result = central_mapper.map_llm_inputs(messages=messages)
        
        assert result["chat_history"][0]["content"] == "Using text field"
        assert result["chat_history"][1]["content"] == "Normal content"
        assert result["chat_history"][1]["extra"] == "field"  # Preserved

    def test_map_llm_inputs_empty_inputs(self, central_mapper):
        """Test map_llm_inputs with no inputs."""
        result = central_mapper.map_llm_inputs()
        
        assert result == {}

    def test_map_llm_outputs_basic(self, central_mapper):
        """Test map_llm_outputs with basic parameters."""
        result = central_mapper.map_llm_outputs(
            content="Hello there",
            role="assistant",
            finish_reason="stop"
        )
        
        assert result["content"] == "Hello there"
        assert result["role"] == "assistant"
        assert result["finish_reason"] == "stop"

    def test_map_llm_outputs_default_role(self, central_mapper):
        """Test map_llm_outputs sets default role for content."""
        result = central_mapper.map_llm_outputs(content="Response without role")
        
        assert result["content"] == "Response without role"
        assert result["role"] == "assistant"  # Default role

    def test_map_llm_outputs_from_messages(self, central_mapper):
        """Test map_llm_outputs extracts content from messages."""
        messages = [
            {"role": "user", "content": "Question"},
            {"role": "assistant", "content": "Answer from messages"}
        ]
        
        result = central_mapper.map_llm_outputs(messages=messages)
        
        assert result["content"] == "Answer from messages"
        assert result["role"] == "assistant"

    def test_map_llm_outputs_with_tool_calls(self, central_mapper):
        """Test map_llm_outputs with tool calls."""
        tool_calls = [
            {
                "id": "call_1",
                "name": "get_weather",
                "arguments": '{"location": "NYC"}'
            },
            {
                "id": "call_2",
                "function": {"name": "get_time", "arguments": "{}"}
            }
        ]
        
        result = central_mapper.map_llm_outputs(
            content="I'll help you with that",
            tool_calls=tool_calls
        )
        
        assert result["content"] == "I'll help you with that"
        assert result["tool_calls.0.id"] == "call_1"
        assert result["tool_calls.0.name"] == "get_weather"
        assert result["tool_calls.0.arguments"] == '{"location": "NYC"}'
        assert result["tool_calls.1.id"] == "call_2"
        assert result["tool_calls.1.name"] == "get_time"
        assert result["tool_calls.1.arguments"] == "{}"

    def test_map_llm_outputs_with_response_id(self, central_mapper):
        """Test map_llm_outputs with response ID."""
        result = central_mapper.map_llm_outputs(
            content="Response",
            response_id="resp_123"
        )
        
        assert result["content"] == "Response"
        assert result["id"] == "resp_123"

    def test_map_llm_config_basic(self, central_mapper):
        """Test map_llm_config with basic parameters."""
        result = central_mapper.map_llm_config(
            model="gpt-4",
            provider="openai",
            temperature=0.7,
            max_tokens=1000
        )
        
        assert result["model"] == "gpt-4"
        assert result["provider"] == "openai"
        assert result["temperature"] == 0.7
        assert result["max_completion_tokens"] == 1000
        assert result["headers"] == "None"  # Default
        assert result["is_streaming"] is False  # Default

    def test_map_llm_config_with_headers_and_streaming(self, central_mapper):
        """Test map_llm_config with headers and streaming."""
        result = central_mapper.map_llm_config(
            model="gpt-3.5-turbo",
            provider="openai",
            headers="Authorization: Bearer token",
            is_streaming=True
        )
        
        assert result["headers"] == "Authorization: Bearer token"
        assert result["is_streaming"] is True

    def test_map_llm_config_with_kwargs(self, central_mapper):
        """Test map_llm_config with additional kwargs."""
        result = central_mapper.map_llm_config(
            model="claude-3",
            provider="anthropic",
            top_p=0.9,
            frequency_penalty=0.1
        )
        
        assert result["model"] == "claude-3"
        assert result["provider"] == "anthropic"
        assert result["top_p"] == 0.9
        assert result["frequency_penalty"] == 0.1

    def test_map_llm_config_no_provider_defaults(self, central_mapper):
        """Test map_llm_config without provider doesn't set defaults."""
        result = central_mapper.map_llm_config(model="local-model")
        
        assert result["model"] == "local-model"
        assert "headers" not in result
        assert "is_streaming" not in result

    def test_map_llm_metadata_basic(self, central_mapper):
        """Test map_llm_metadata with basic parameters."""
        scope = {"name": "openai", "version": "1.0.0"}
        
        result = central_mapper.map_llm_metadata(
            scope=scope,
            request_type="chat",
            total_tokens=150,
            prompt_tokens=100,
            completion_tokens=50
        )
        
        assert result["scope"] == scope
        assert result["llm.request.type"] == "chat"
        assert result["total_tokens"] == 150
        assert result["prompt_tokens"] == 100
        assert result["completion_tokens"] == 50

    def test_map_llm_metadata_with_api_details(self, central_mapper):
        """Test map_llm_metadata with API details."""
        result = central_mapper.map_llm_metadata(
            api_base="https://api.openai.com/v1",
            response_model="gpt-4-0613",
            system_fingerprint="fp_123"
        )
        
        assert result["gen_ai.openai.api_base"] == "https://api.openai.com/v1"
        assert result["response_model"] == "gpt-4-0613"
        assert result["system_fingerprint"] == "fp_123"

    def test_map_llm_metadata_partial_tokens(self, central_mapper):
        """Test map_llm_metadata with partial token information."""
        result = central_mapper.map_llm_metadata(
            total_tokens=200,
            prompt_tokens=150
            # completion_tokens missing
        )
        
        assert result["total_tokens"] == 200
        assert result["prompt_tokens"] == 150
        assert "completion_tokens" not in result

    def test_map_llm_metadata_with_kwargs(self, central_mapper):
        """Test map_llm_metadata with additional kwargs."""
        result = central_mapper.map_llm_metadata(
            request_type="completion",
            custom_field="custom_value",
            another_field=42
        )
        
        assert result["llm.request.type"] == "completion"
        assert result["custom_field"] == "custom_value"
        assert result["another_field"] == 42

    def test_create_llm_event_successful(self, central_mapper):
        """Test create_llm_event successful creation."""
        with patch("honeyhive.tracer.semantic_conventions.central_mapper.HoneyHiveEventSchema") as mock_schema:
            mock_validated = Mock()
            mock_validated.model_dump.return_value = {"validated": "event"}
            mock_schema.return_value = mock_validated
            
            result = central_mapper.create_llm_event(
                event_name="test_llm",
                source="test-source",
                messages=[{"role": "user", "content": "Hello"}],
                content="Hi there",
                model="gpt-4",
                provider="openai"
            )
            
            assert result["validated"] == "event"
            assert central_mapper.schema_stats["events_mapped"] == 1
            assert central_mapper.schema_stats["schema_types_used"]["llm"] == 1

    def test_create_llm_event_validation_error(self, central_mapper):
        """Test create_llm_event with Pydantic validation error."""
        with patch("honeyhive.tracer.semantic_conventions.central_mapper.HoneyHiveEventSchema", side_effect=Exception("Validation failed")):
            result = central_mapper.create_llm_event(
                event_name="test_llm",
                source="test-source",
                content="Response"
            )
            
            # Should continue with unvalidated event
            assert result["event_name"] == "test_llm"
            assert result["event_type"] == "model"
            
            # Verify warning logged and stats updated
            central_mapper._mock_safe_log.assert_any_call(
                None,
                "warning",
                "Pydantic validation error: Validation failed"
            )
            assert central_mapper.schema_stats["validation_errors"] == 1

    def test_create_llm_event_exception_handling(self, central_mapper):
        """Test create_llm_event exception handling."""
        # Mock create_base_event to raise exception initially, then work
        with patch.object(central_mapper, "create_base_event", side_effect=[Exception("Test error"), {"minimal": "event"}]):
            result = central_mapper.create_llm_event(
                event_name="test_llm",
                source="test-source"
            )
            
            assert result["minimal"] == "event"
            
            # Verify error logged
            central_mapper._mock_safe_log.assert_any_call(
                None,
                "error",
                "Failed to create LLM event: Test error"
            )

    def test_get_mapping_stats(self, central_mapper):
        """Test get_mapping_stats returns copy of statistics."""
        # Modify stats
        central_mapper.schema_stats["events_mapped"] = 5
        central_mapper.schema_stats["validation_errors"] = 2
        central_mapper.schema_stats["schema_types_used"]["model"] = 3
        
        result = central_mapper.get_mapping_stats()
        
        assert result["events_mapped"] == 5
        assert result["validation_errors"] == 2
        assert result["schema_types_used"]["model"] == 3
        
        # Verify it's a copy (modifying result doesn't affect original)
        result["events_mapped"] = 10
        assert central_mapper.schema_stats["events_mapped"] == 5


class TestGetCentralMapper:
    """Test cases for get_central_mapper factory function."""

    @patch("honeyhive.tracer.semantic_conventions.central_mapper.safe_log")
    @patch("honeyhive.tracer.semantic_conventions.central_mapper.CentralEventMapper")
    def test_get_central_mapper_successful(self, mock_mapper_class, mock_safe_log):
        """Test successful central mapper creation."""
        mock_mapper = Mock()
        mock_mapper_class.return_value = mock_mapper
        mock_cache_manager = Mock()
        
        result = get_central_mapper(mock_cache_manager)
        
        assert result == mock_mapper
        mock_mapper_class.assert_called_once()
        
        # Verify debug log
        mock_safe_log.assert_called_once_with(
            None,
            "debug",
            f"🔍 CENTRAL MAPPER: Created instance for tracer {id(mock_cache_manager)}"
        )

    @patch("honeyhive.tracer.semantic_conventions.central_mapper.safe_log")
    @patch("honeyhive.tracer.semantic_conventions.central_mapper.CentralEventMapper")
    def test_get_central_mapper_no_cache_manager(self, mock_mapper_class, mock_safe_log):
        """Test central mapper creation without cache manager."""
        mock_mapper = Mock()
        mock_mapper_class.return_value = mock_mapper
        
        result = get_central_mapper(None)
        
        assert result == mock_mapper
        
        # Verify debug log with 'unknown'
        mock_safe_log.assert_called_once_with(
            None,
            "debug",
            "🔍 CENTRAL MAPPER: Created instance for tracer unknown"
        )

    @patch("honeyhive.tracer.semantic_conventions.central_mapper.safe_log")
    @patch("honeyhive.tracer.semantic_conventions.central_mapper.CentralEventMapper")
    def test_get_central_mapper_exception_handling(self, mock_mapper_class, mock_safe_log):
        """Test exception handling in get_central_mapper."""
        mock_mapper_class.side_effect = Exception("Creation failed")
        
        result = get_central_mapper(None)
        
        assert result is None
        
        # Verify error logged
        mock_safe_log.assert_called_with(
            None,
            "error",
            "Failed to create central mapper: Creation failed"
        )
