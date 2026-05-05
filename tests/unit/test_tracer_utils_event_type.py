"""Unit tests for HoneyHive tracer utils event type functionality.

This module tests the event type detection utilities including pattern matching,
LLM attribute detection, and raw attribute processing.
"""

# pylint: disable=line-too-long,attribute-defined-outside-init,missing-class-docstring
# pylint: disable=too-few-public-methods,import-outside-toplevel
# Justification: Test module requires dynamic attributes and test classes may have few methods

from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer.utils.event_type import (
    _extract_base_attribute_name_dynamically,
    _identify_raw_attributes_dynamically,
    _is_raw_attribute_dynamically,
    _is_sensitive_attribute_dynamically,
    _process_raw_value_dynamically,
    _process_single_raw_attribute_dynamically,
    detect_event_type_from_patterns,
    extract_raw_attributes,
    get_llm_attributes,
    get_model_patterns,
)


class TestModelPatterns:
    """Test model pattern generation and detection."""

    def test_get_model_patterns_returns_list(self) -> None:
        """Test that get_model_patterns returns a list of strings."""
        patterns = get_model_patterns()

        assert isinstance(patterns, list)
        assert len(patterns) > 0
        assert all(isinstance(pattern, str) for pattern in patterns)

    def test_get_model_patterns_includes_provider_patterns(self) -> None:
        """Test that model patterns include major LLM provider patterns."""
        patterns = get_model_patterns()

        # Check for major provider patterns
        expected_providers = [
            "openai.chat.completions",
            "openai.completions",
            "anthropic.messages",
            "bedrock.invoke_model",
            "google.generativeai",
        ]

        for provider in expected_providers:
            assert provider in patterns

    def test_get_model_patterns_includes_operation_patterns(self) -> None:
        """Test that model patterns include generic operation patterns."""
        patterns = get_model_patterns()

        expected_operations = [
            "llm.",
            "model.",
            "chat",
            "completion",
            "generate",
            "inference",
        ]

        for operation in expected_operations:
            assert operation in patterns

    def test_get_model_patterns_includes_model_names(self) -> None:
        """Test that model patterns include popular model name patterns."""
        patterns = get_model_patterns()

        expected_models = ["gpt", "claude", "llama", "gemini", "mistral", "palm"]

        for model in expected_models:
            assert model in patterns

    def test_get_model_patterns_dynamic_extensibility(self) -> None:
        """Test that model patterns can be dynamically extended."""
        patterns = get_model_patterns()

        # Verify the function returns a comprehensive list
        assert (
            len(patterns) >= 15
        )  # Should have at least provider + operation + model patterns

        # Verify no duplicates
        assert len(patterns) == len(set(patterns))


class TestLLMAttributes:
    """Test LLM attribute generation and detection."""

    def test_get_llm_attributes_returns_list(self) -> None:
        """Test that get_llm_attributes returns a list of strings."""
        attributes = get_llm_attributes()

        assert isinstance(attributes, list)
        assert len(attributes) > 0
        assert all(isinstance(attr, str) for attr in attributes)

    def test_get_llm_attributes_includes_otel_conventions(self) -> None:
        """Test that LLM attributes include OpenTelemetry semantic conventions."""
        attributes = get_llm_attributes()

        expected_otel = [
            "llm.request.model",
            "llm.response.model",
            "llm.model.name",
            "gen_ai.request.model",
            "gen_ai.response.model",
        ]

        for attr in expected_otel:
            assert attr in attributes

    def test_get_llm_attributes_includes_provider_specific(self) -> None:
        """Test that LLM attributes include provider-specific attributes."""
        attributes = get_llm_attributes()

        expected_providers = [
            "openai.model",
            "anthropic.model",
            "bedrock.model_id",
            "google.model",
        ]

        for attr in expected_providers:
            assert attr in attributes

    def test_get_llm_attributes_includes_generic_attributes(self) -> None:
        """Test that LLM attributes include generic model attributes."""
        attributes = get_llm_attributes()

        expected_generic = ["model_name", "model_id", "model_type", "ai_model"]

        for attr in expected_generic:
            assert attr in attributes

    def test_get_llm_attributes_no_duplicates(self) -> None:
        """Test that LLM attributes list has no duplicates."""
        attributes = get_llm_attributes()

        assert len(attributes) == len(set(attributes))


class TestEventTypeDetection:
    """Test event type detection from patterns."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_patches = []

    def teardown_method(self) -> None:
        """Clean up after each test method."""
        # Stop all patches
        for patch_obj in self.mock_patches:
            patch_obj.stop()

    def test_detect_event_type_from_patterns_model_span_name(self) -> None:
        """Test event type detection from model-related span names."""
        test_cases = [
            ("openai.chat.completions.create", "model"),
            ("anthropic.messages.create", "model"),
            ("llm_call", "model"),
            ("gpt_request", "model"),
            ("chat_completion", "model"),
            ("model_inference", "model"),
        ]

        for span_name, expected_type in test_cases:
            result = detect_event_type_from_patterns(span_name, {})
            assert result == expected_type, f"Failed for span_name: {span_name}"

    def test_detect_event_type_from_patterns_model_attributes(self) -> None:
        """Test event type detection from model-related attributes."""
        test_cases = [
            ({"llm.request.model": "gpt-4"}, "model"),
            ({"gen_ai.request.model": "claude-3"}, "model"),
            ({"openai.model": "gpt-3.5-turbo"}, "model"),
            ({"model_name": "llama-2"}, "model"),
            ({"bedrock.model_id": "anthropic.claude-v2"}, "model"),
        ]

        for attributes, expected_type in test_cases:
            result = detect_event_type_from_patterns("generic_span", attributes)
            assert result == expected_type, f"Failed for attributes: {attributes}"

    def test_detect_event_type_from_patterns_tool_fallback(self) -> None:
        """Test event type detection falls back to tool for non-model operations."""
        test_cases = [
            ("data_processing", {}),
            ("api_call", {}),
            ("database_query", {}),
            ("file_operation", {"file_path": "/tmp/test.txt"}),
            ("generic_function", {"param1": "value1"}),
        ]

        for span_name, attributes in test_cases:
            result = detect_event_type_from_patterns(span_name, attributes)
            assert (
                result == "tool"
            ), f"Failed for span_name: {span_name}, attributes: {attributes}"

    def test_detect_event_type_from_patterns_case_insensitive(self) -> None:
        """Test event type detection is case insensitive."""
        test_cases = [
            ("GPT_CALL", "model"),
            ("OpenAI.Chat.Completions", "model"),
            ("LLM_REQUEST", "model"),
            ("Model_Inference", "model"),
        ]

        for span_name, expected_type in test_cases:
            result = detect_event_type_from_patterns(span_name, {})
            assert result == expected_type, f"Failed for span_name: {span_name}"

    def test_detect_event_type_from_patterns_combined_detection(self) -> None:
        """Test event type detection with both span name and attributes."""
        # Model detection should work with either span name or attributes
        result1 = detect_event_type_from_patterns(
            "generic_span", {"llm.request.model": "gpt-4"}
        )
        result2 = detect_event_type_from_patterns("llm_call", {"generic_attr": "value"})
        result3 = detect_event_type_from_patterns(
            "llm_call", {"llm.request.model": "gpt-4"}
        )

        assert result1 == "model"
        assert result2 == "model"
        assert result3 == "model"

    @pytest.mark.parametrize(
        "span_name,attributes,expected",
        [
            ("openai.chat.completions", {}, "model"),
            ("anthropic.messages", {}, "model"),
            ("bedrock.invoke_model", {}, "model"),
            ("google.generativeai", {}, "model"),
            ("data_processing", {}, "tool"),
            ("api_request", {}, "tool"),
            ("", {"llm.request.model": "gpt-4"}, "model"),
            ("", {"gen_ai.response.model": "claude"}, "model"),
            ("", {"openai.model": "gpt-3.5"}, "model"),
            ("", {"normal_attr": "value"}, "tool"),
        ],
    )
    def test_detect_event_type_parametrized(
        self, span_name: str, attributes: Dict[str, Any], expected: str
    ) -> None:
        """Test event type detection with parametrized inputs."""
        result = detect_event_type_from_patterns(span_name, attributes)
        assert result == expected


class TestRawAttributeExtraction:
    """Test raw attribute extraction functionality."""

    def test_extract_raw_attributes_simple_dict(self) -> None:
        """Test raw attribute extraction from simple dictionary."""
        attributes = {"key1": "value1", "key2": 42, "key3": True, "key4": 3.14}

        result = extract_raw_attributes(attributes)

        assert isinstance(result, dict)
        assert result["key1"] == "value1"
        assert result["key2"] == 42
        assert result["key3"] is True
        assert result["key4"] == 3.14

    def test_extract_raw_attributes_nested_dict(self) -> None:
        """Test raw attribute extraction from nested dictionary."""
        attributes = {
            "top_level": "value",
            "nested": {
                "inner_key": "inner_value",
                "deep_nested": {"deep_key": "deep_value"},
            },
        }

        result = extract_raw_attributes(attributes)

        # Should flatten nested structures
        assert "top_level" in result
        assert result["top_level"] == "value"

        # Nested attributes should be accessible
        nested_str = str(result)
        assert "inner_value" in nested_str
        assert "deep_value" in nested_str

    def test_extract_raw_attributes_with_lists(self) -> None:
        """Test raw attribute extraction with list values."""
        attributes = {
            "simple_list": ["item1", "item2", "item3"],
            "mixed_list": [1, "string", True, {"nested": "value"}],
            "empty_list": [],
        }

        result = extract_raw_attributes(attributes)

        assert "simple_list" in result
        assert "mixed_list" in result
        assert "empty_list" in result

    def test_extract_raw_attributes_filters_sensitive_data(self) -> None:
        """Test raw attribute extraction filters sensitive data."""
        attributes = {
            "api_key": "secret-api-key",
            "password": "secret-password",
            "token": "secret-token",
            "secret": "secret-value",
            "normal_attr": "normal-value",
            "user_id": "user123",
        }

        result = extract_raw_attributes(attributes)

        # Sensitive attributes should be filtered out
        result_str = str(result)
        assert "secret-api-key" not in result_str
        assert "secret-password" not in result_str
        assert "secret-token" not in result_str
        assert "secret-value" not in result_str

        # Normal attributes should be preserved
        assert "normal-value" in result_str
        assert "user123" in result_str

    def test_extract_raw_attributes_handles_none_values(self) -> None:
        """Test raw attribute extraction handles None values."""
        attributes = {
            "none_value": None,
            "normal_value": "test",
            "zero_value": 0,
            "false_value": False,
            "empty_string": "",
        }

        result = extract_raw_attributes(attributes)

        # Should handle all value types gracefully
        assert "none_value" in result
        assert "normal_value" in result
        assert "zero_value" in result
        assert "false_value" in result
        assert "empty_string" in result

    def test_extract_raw_attributes_handles_complex_objects(self) -> None:
        """Test raw attribute extraction handles complex objects."""

        class CustomObject:
            def __init__(self, value):
                self.value = value

            def __str__(self):
                return f"CustomObject({self.value})"

        attributes = {
            "custom_object": CustomObject("test"),
            "function": lambda x: x + 1,
            "normal_value": "test",
        }

        # Should not raise exceptions with complex objects
        result = extract_raw_attributes(attributes)

        assert isinstance(result, dict)
        assert "normal_value" in result

    def test_extract_raw_attributes_empty_input(self) -> None:
        """Test raw attribute extraction with empty input."""
        result = extract_raw_attributes({})

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_extract_raw_attributes_preserves_structure(self) -> None:
        """Test raw attribute extraction preserves important structure."""
        attributes = {
            "llm.request.model": "gpt-4",
            "llm.request.messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ],
            "llm.response.content": "Response text",
            "llm.usage.prompt_tokens": 10,
            "llm.usage.completion_tokens": 20,
        }

        result = extract_raw_attributes(attributes)

        # Important LLM attributes should be preserved
        assert "llm.request.model" in result
        assert result["llm.request.model"] == "gpt-4"
        assert "llm.usage.prompt_tokens" in result
        assert result["llm.usage.prompt_tokens"] == 10

    @pytest.mark.parametrize(
        "input_attrs,expected_keys",
        [
            ({"key1": "value1"}, ["key1"]),
            ({"key1": "value1", "key2": "value2"}, ["key1", "key2"]),
            ({}, []),
            ({"nested": {"inner": "value"}}, ["nested"]),
            ({"list_attr": [1, 2, 3]}, ["list_attr"]),
        ],
    )
    def test_extract_raw_attributes_parametrized(
        self, input_attrs: Dict[str, Any], expected_keys: List[str]
    ) -> None:
        """Test raw attribute extraction with parametrized inputs."""
        result = extract_raw_attributes(input_attrs)

        assert isinstance(result, dict)
        for key in expected_keys:
            assert key in result


class TestRawAttributeProcessingEdgeCases:
    """Test edge cases and internal functions for raw attribute processing."""

    def test_extract_raw_attributes_with_raw_suffix_attributes(self) -> None:
        """Test extraction with _raw suffix attributes that need special processing."""
        attributes = {
            "honeyhive_event_type_raw": "model",
            "custom_param_raw": "test_value",
            "normal_attr": "normal_value",
            "not_raw_attr": "another_value",
        }

        result = extract_raw_attributes(attributes)

        # Raw attributes should be processed and have suffix removed
        assert "honeyhive_event_type" in result
        assert result["honeyhive_event_type"] == "model"
        assert "custom_param" in result
        assert result["custom_param"] == "test_value"

        # Normal attributes should be preserved as-is
        assert "normal_attr" in result
        assert result["normal_attr"] == "normal_value"
        assert "not_raw_attr" in result
        assert result["not_raw_attr"] == "another_value"

    def test_extract_raw_attributes_with_tracer_instance_logging(self) -> None:
        """Test extraction with tracer instance for logging."""
        mock_tracer = Mock()
        attributes = {"test_key": "test_value", "honeyhive_param_raw": "raw_value"}

        result = extract_raw_attributes(attributes, tracer_instance=mock_tracer)

        assert isinstance(result, dict)
        assert "test_key" in result
        assert "honeyhive_param" in result

    def test_is_raw_attribute_dynamically(self) -> None:
        """Test raw attribute detection logic."""
        # Should detect raw attributes
        assert _is_raw_attribute_dynamically("honeyhive_event_type_raw") is True
        assert _is_raw_attribute_dynamically("custom_param_raw") is True
        assert _is_raw_attribute_dynamically("test_value_raw") is True

        # Should not detect non-raw attributes
        assert _is_raw_attribute_dynamically("normal_attr") is False
        assert _is_raw_attribute_dynamically("honeyhive_event_type") is False
        assert (
            _is_raw_attribute_dynamically("raw") is False
        )  # Just "raw" without underscore
        assert (
            _is_raw_attribute_dynamically("_raw") is True
        )  # "_raw" matches the pattern

    def test_is_sensitive_attribute_dynamically(self) -> None:
        """Test sensitive attribute detection logic."""
        # Should detect sensitive attributes
        sensitive_attrs = [
            "api_key",
            "password",
            "token",
            "secret",
            "auth",
            "credential",
            "private_key",
            "access_key",
            "session_key",
            "bearer",
        ]
        for attr in sensitive_attrs:
            assert _is_sensitive_attribute_dynamically(attr) is True
            assert (
                _is_sensitive_attribute_dynamically(attr.upper()) is True
            )  # Case insensitive

        # Should not flag LLM usage metrics with "token" (only when "usage" is also present)
        usage_attrs = ["llm.usage.tokens", "usage_tokens", "usage.token_count"]
        for attr in usage_attrs:
            assert _is_sensitive_attribute_dynamically(attr) is False

        # These should still be flagged as sensitive (no "usage" context)
        sensitive_token_attrs = ["token_count", "prompt_tokens", "completion_tokens"]
        for attr in sensitive_token_attrs:
            assert _is_sensitive_attribute_dynamically(attr) is True

        # Should not detect normal attributes
        normal_attrs = ["user_id", "model_name", "response_text", "timestamp"]
        for attr in normal_attrs:
            assert _is_sensitive_attribute_dynamically(attr) is False

    def test_identify_raw_attributes_dynamically_deprecated(self) -> None:
        """Test the deprecated batch processing function for raw attributes."""
        attributes = {
            "honeyhive_event_type_raw": "model",
            "custom_param_raw": "test_value",
            "normal_attr": "normal_value",
            "another_raw": "value",  # This should NOT match (no underscore before raw)
        }

        result = _identify_raw_attributes_dynamically(attributes)

        # Should only return raw attributes
        assert "honeyhive_event_type_raw" in result
        assert "custom_param_raw" in result
        assert "normal_attr" not in result
        assert (
            "another_raw" in result
        )  # This actually matches the pattern "_raw" at the end

    def test_process_single_raw_attribute_dynamically_success(self) -> None:
        """Test successful processing of a single raw attribute."""
        result = _process_single_raw_attribute_dynamically(
            "honeyhive_event_type_raw", "model"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "honeyhive_event_type" in result
        assert result["honeyhive_event_type"] == "model"

    def test_process_single_raw_attribute_dynamically_with_tracer(self) -> None:
        """Test raw attribute processing with tracer instance for logging."""
        mock_tracer = Mock()

        result = _process_single_raw_attribute_dynamically(
            "custom_param_raw", "test_value", tracer_instance=mock_tracer
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "custom_param" in result
        assert result["custom_param"] == "test_value"

    def test_process_single_raw_attribute_dynamically_invalid_name(self) -> None:
        """Test raw attribute processing with invalid attribute name."""
        mock_tracer = Mock()

        # Attribute name that doesn't end with _raw
        result = _process_single_raw_attribute_dynamically(
            "invalid_attr", "value", tracer_instance=mock_tracer
        )

        assert result is None

    def test_process_single_raw_attribute_dynamically_exception_handling(self) -> None:
        """Test exception handling in raw attribute processing."""
        mock_tracer = Mock()

        # Test with an attribute name that will cause issues in processing
        with patch(
            "honeyhive.tracer.utils.event_type._extract_base_attribute_name_dynamically",
            side_effect=Exception("Processing error"),
        ):
            result = _process_single_raw_attribute_dynamically(
                "test_raw", "value", tracer_instance=mock_tracer
            )

            assert result is None

    def test_extract_base_attribute_name_dynamically(self) -> None:
        """Test base attribute name extraction from raw attribute names."""
        # Should extract base names correctly
        assert (
            _extract_base_attribute_name_dynamically("honeyhive_event_type_raw")
            == "honeyhive_event_type"
        )
        assert (
            _extract_base_attribute_name_dynamically("custom_param_raw")
            == "custom_param"
        )
        assert (
            _extract_base_attribute_name_dynamically("test_RAW") == "test"
        )  # Case insensitive

        # Should return None for invalid names
        assert _extract_base_attribute_name_dynamically("no_raw_suffix") is None
        assert _extract_base_attribute_name_dynamically("raw") is None
        assert (
            _extract_base_attribute_name_dynamically("_raw") == ""
        )  # Returns empty string, not None

    def test_process_raw_value_dynamically_basic_types(self) -> None:
        """Test raw value processing with basic types."""
        # Should preserve basic types
        assert _process_raw_value_dynamically("string") == "string"
        assert _process_raw_value_dynamically(42) == 42
        assert _process_raw_value_dynamically(3.14) == 3.14
        assert _process_raw_value_dynamically(True) is True
        assert _process_raw_value_dynamically(False) is False
        assert _process_raw_value_dynamically([1, 2, 3]) == [1, 2, 3]
        assert _process_raw_value_dynamically({"key": "value"}) == {"key": "value"}

        # Should preserve None
        assert _process_raw_value_dynamically(None) is None

    def test_process_raw_value_dynamically_enum_conversion(self) -> None:
        """Test raw value processing with enum-like objects."""
        from enum import Enum

        class TestEnum(Enum):
            VALUE1 = "value1"
            VALUE2 = "value2"

        # Should convert enum to string
        result = _process_raw_value_dynamically(TestEnum.VALUE1)
        assert result == "value1"

    def test_process_raw_value_dynamically_complex_objects(self) -> None:
        """Test raw value processing with complex objects."""

        class CustomObject:
            def __init__(self, value):
                self.value = value

            def __str__(self):
                return f"CustomObject({self.value})"

        obj = CustomObject("test")
        result = _process_raw_value_dynamically(obj)

        # Should convert to string
        assert result == "CustomObject(test)"


class TestEventTypeDetectionEdgeCases:
    """Test edge cases in event type detection."""

    def test_detect_event_type_compound_patterns(self) -> None:
        """Test detection of compound AI/ML patterns in span names."""
        compound_patterns = [
            "ai_model_inference",
            "ml_prediction_service",
            "nlp_text_processing",
        ]

        for span_name in compound_patterns:
            result = detect_event_type_from_patterns(span_name, {})
            assert result == "model", f"Failed for compound pattern: {span_name}"

    def test_detect_event_type_empty_inputs(self) -> None:
        """Test event type detection with empty inputs."""
        # Empty span name and attributes should return default
        result = detect_event_type_from_patterns("", {})
        assert result == "tool"

        # None span name should be handled gracefully
        result = detect_event_type_from_patterns(None, {})
        assert result == "tool"

    def test_detect_event_type_with_tracer_logging(self) -> None:
        """Test event type detection with tracer instance for logging."""
        mock_tracer = Mock()

        # Should detect model type and log
        result = detect_event_type_from_patterns(
            "openai.chat.completions", {}, tracer_instance=mock_tracer
        )
        assert result == "model"

        # Should detect from attributes and log
        result = detect_event_type_from_patterns(
            "generic_span", {"llm.request.model": "gpt-4"}, tracer_instance=mock_tracer
        )
        assert result == "model"

    def test_detect_event_type_attribute_detection_edge_cases(self) -> None:
        """Test attribute-based detection edge cases."""
        # Empty attributes dict
        result = detect_event_type_from_patterns("generic_span", None)
        assert result == "tool"

        # Attributes with None values should still trigger detection
        result = detect_event_type_from_patterns(
            "generic_span", {"llm.request.model": None}
        )
        assert result == "model"
