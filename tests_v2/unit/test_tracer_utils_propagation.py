"""Unit tests for HoneyHive tracer utils propagation functionality.

This module tests the context propagation utilities including carrier sanitization,
header extraction, and dynamic key matching using standard fixtures and comprehensive
edge case coverage following Agent OS testing standards.
"""

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer.utils.propagation import (
    _case_insensitive_lookup_dynamically,
    _create_default_getter_dynamically,
    _extract_header_value_dynamically,
    _fuzzy_key_lookup_dynamically,
    _generate_key_variations_dynamically,
    _get_carrier_value_dynamically,
    _get_custom_propagation_headers_dynamically,
    _get_propagation_headers_dynamically,
    _log_sanitization_results_dynamically,
    _sanitize_carrier_headers_dynamically,
    sanitize_carrier,
)


class TestSanitizeCarrier:
    """Test main carrier sanitization functionality."""

    def test_sanitize_carrier_with_valid_headers(self, honeyhive_tracer: Any) -> None:
        """Test carrier sanitization with valid OpenTelemetry headers."""
        carrier = {
            "baggage": "session_id=test123,user_id=456",
            "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
            "tracestate": "rojo=00f067aa0ba902b7,congo=t61rcWkgMzE",
            "custom-header": "should-be-ignored",
        }

        result = sanitize_carrier(carrier, tracer_instance=honeyhive_tracer)

        assert isinstance(result, dict)
        assert "baggage" in result
        assert "traceparent" in result
        assert "tracestate" in result
        assert "custom-header" not in result
        assert result["baggage"] == "session_id=test123,user_id=456"

    def test_sanitize_carrier_with_empty_carrier(self, honeyhive_tracer: Any) -> None:
        """Test carrier sanitization with empty carrier."""
        carrier: Dict[str, Any] = {}

        result = sanitize_carrier(carrier, tracer_instance=honeyhive_tracer)

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_sanitize_carrier_with_none_carrier(self, honeyhive_tracer: Any) -> None:
        """Test carrier sanitization with None carrier."""
        with patch("honeyhive.tracer.utils.propagation.safe_log") as mock_log:
            result = sanitize_carrier(
                None, tracer_instance=honeyhive_tracer  # type: ignore[arg-type]
            )

        assert not result
        mock_log.assert_called()

    def test_sanitize_carrier_with_case_insensitive_headers(
        self, honeyhive_tracer: Any
    ) -> None:
        """Test carrier sanitization with case-insensitive header matching."""
        carrier = {
            "BAGGAGE": "session_id=test123",
            "TraceParent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
            "TRACESTATE": "rojo=00f067aa0ba902b7",
        }

        result = sanitize_carrier(carrier, tracer_instance=honeyhive_tracer)

        assert len(result) == 3
        assert "baggage" in result or "BAGGAGE" in result
        assert "traceparent" in result or "TraceParent" in result
        assert "tracestate" in result or "TRACESTATE" in result

    def test_sanitize_carrier_with_custom_getter(self, honeyhive_tracer: Any) -> None:
        """Test carrier sanitization with custom getter."""
        carrier = {"baggage": "test=value"}

        # Create a mock getter
        mock_getter = Mock()
        mock_getter.get.return_value = "test=value"

        result = sanitize_carrier(
            carrier, getter=mock_getter, tracer_instance=honeyhive_tracer
        )

        assert isinstance(result, dict)
        mock_getter.get.assert_called()

    @patch("honeyhive.tracer.utils.propagation.safe_log")
    def test_sanitize_carrier_exception_handling(
        self, mock_log: Any, honeyhive_tracer: Any
    ) -> None:
        """Test carrier sanitization exception handling."""
        # Create a carrier that will cause an exception in processing
        carrier = {"baggage": "test=value"}

        with patch(
            "honeyhive.tracer.utils.propagation._sanitize_carrier_headers_dynamically",
            side_effect=Exception("Test error"),
        ):
            result = sanitize_carrier(carrier, tracer_instance=honeyhive_tracer)

        assert not result
        mock_log.assert_called_with(
            honeyhive_tracer,
            "warning",
            "Failed to sanitize carrier",
            honeyhive_data={
                "error": "Test error",
                "carrier_keys": ["baggage"],
            },
        )


class TestCreateDefaultGetterDynamically:
    """Test default getter creation functionality."""

    def test_create_default_getter_returns_getter_instance(self) -> None:
        """Test that default getter creation returns a valid getter."""
        getter = _create_default_getter_dynamically()

        assert hasattr(getter, "get")
        assert hasattr(getter, "keys")
        assert callable(getter.get)
        assert callable(getter.keys)

    def test_default_getter_get_method(self) -> None:
        """Test default getter get method functionality."""
        getter = _create_default_getter_dynamically()
        carrier = {"test-key": "test-value", "UPPER": "upper-value"}

        # Test exact match
        result = getter.get(carrier, "test-key")
        assert result == "test-value"

        # Test case-insensitive match
        result = getter.get(carrier, "upper")
        assert result == "upper-value"

    def test_default_getter_keys_method(self) -> None:
        """Test default getter keys method functionality."""
        getter = _create_default_getter_dynamically()
        carrier = {"key1": "value1", "key2": "value2"}

        result = getter.keys(carrier)

        assert isinstance(result, list)
        assert set(result) == {"key1", "key2"}

    def test_default_getter_keys_with_empty_carrier(self) -> None:
        """Test default getter keys method with empty carrier."""
        getter = _create_default_getter_dynamically()

        result = getter.keys({})
        assert not result

        result = getter.keys(None)
        assert not result


class TestGetCarrierValueDynamically:
    """Test dynamic carrier value retrieval functionality."""

    def test_get_carrier_value_exact_match(self) -> None:
        """Test carrier value retrieval with exact key match."""
        carrier = {"baggage": "session_id=123", "traceparent": "trace-value"}

        result = _get_carrier_value_dynamically(carrier, "baggage")

        assert result == "session_id=123"

    def test_get_carrier_value_case_insensitive(self) -> None:
        """Test carrier value retrieval with case-insensitive matching."""
        carrier = {"BAGGAGE": "session_id=123", "TraceParent": "trace-value"}

        result = _get_carrier_value_dynamically(carrier, "baggage")
        assert result == "session_id=123"

        result = _get_carrier_value_dynamically(carrier, "traceparent")
        assert result == "trace-value"

    def test_get_carrier_value_fuzzy_matching(self) -> None:
        """Test carrier value retrieval with fuzzy key matching."""
        carrier = {"trace_parent": "trace-value", "trace-state": "state-value"}

        # Should find trace_parent when looking for traceparent (underscore to hyphen)
        result = _get_carrier_value_dynamically(carrier, "trace-parent")
        assert result == "trace-value"

        # Should find trace-state when looking for tracestate (hyphen to underscore)
        result = _get_carrier_value_dynamically(carrier, "trace_state")
        assert result == "state-value"

    def test_get_carrier_value_with_empty_inputs(self) -> None:
        """Test carrier value retrieval with empty inputs."""
        result = _get_carrier_value_dynamically({}, "key")
        assert result is None

        result = _get_carrier_value_dynamically(None, "key")  # type: ignore
        assert result is None

        result = _get_carrier_value_dynamically({"key": "value"}, "")
        assert result is None

        result = _get_carrier_value_dynamically({"key": "value"}, None)  # type: ignore
        assert result is None

    def test_get_carrier_value_key_not_found(self) -> None:
        """Test carrier value retrieval when key is not found."""
        carrier = {"existing-key": "value"}

        result = _get_carrier_value_dynamically(carrier, "non-existent-key")

        assert result is None

    def test_get_carrier_value_exception_handling(self) -> None:
        """Test carrier value retrieval with exception in strategies."""
        carrier = {"key": "value"}

        # Mock one strategy to raise an exception
        with patch(
            "honeyhive.tracer.utils.propagation._case_insensitive_lookup_dynamically",
            side_effect=Exception("Test error"),
        ):
            # Should still work with other strategies
            result = _get_carrier_value_dynamically(carrier, "key")
            assert result == "value"


class TestCaseInsensitiveLookupDynamically:
    """Test case-insensitive lookup functionality."""

    def test_case_insensitive_lookup_exact_match(self) -> None:
        """Test case-insensitive lookup with exact match."""
        carrier = {"baggage": "value", "traceparent": "trace"}

        result = _case_insensitive_lookup_dynamically(carrier, "baggage")

        assert result == "value"

    def test_case_insensitive_lookup_different_cases(self) -> None:
        """Test case-insensitive lookup with different cases."""
        carrier = {"BAGGAGE": "upper-value", "TraceParent": "mixed-case"}

        result = _case_insensitive_lookup_dynamically(carrier, "baggage")
        assert result == "upper-value"

        result = _case_insensitive_lookup_dynamically(carrier, "TRACEPARENT")
        assert result == "mixed-case"

        result = _case_insensitive_lookup_dynamically(carrier, "traceparent")
        assert result == "mixed-case"

    def test_case_insensitive_lookup_not_found(self) -> None:
        """Test case-insensitive lookup when key is not found."""
        carrier = {"existing": "value"}

        result = _case_insensitive_lookup_dynamically(carrier, "non-existent")

        assert result is None

    def test_case_insensitive_lookup_empty_carrier(self) -> None:
        """Test case-insensitive lookup with empty carrier."""
        result = _case_insensitive_lookup_dynamically({}, "key")

        assert result is None


class TestFuzzyKeyLookupDynamically:
    """Test fuzzy key lookup functionality."""

    def test_fuzzy_key_lookup_hyphen_underscore(self) -> None:
        """Test fuzzy lookup with hyphen/underscore variations."""
        carrier = {"trace-parent": "hyphen-value", "trace_state": "underscore-value"}

        result = _fuzzy_key_lookup_dynamically(carrier, "trace_parent")
        assert result == "hyphen-value"

        result = _fuzzy_key_lookup_dynamically(carrier, "trace-state")
        assert result == "underscore-value"

    def test_fuzzy_key_lookup_case_variations(self) -> None:
        """Test fuzzy lookup with case variations."""
        carrier = {"BAGGAGE": "upper", "Traceparent": "title", "tracestate": "lower"}

        result = _fuzzy_key_lookup_dynamically(carrier, "baggage")
        assert result == "upper"

        result = _fuzzy_key_lookup_dynamically(carrier, "traceparent")
        assert result == "title"

    def test_fuzzy_key_lookup_not_found(self) -> None:
        """Test fuzzy lookup when no variations match."""
        carrier = {"existing": "value"}

        result = _fuzzy_key_lookup_dynamically(carrier, "completely-different")

        assert result is None

    def test_fuzzy_key_lookup_empty_carrier(self) -> None:
        """Test fuzzy lookup with empty carrier."""
        result = _fuzzy_key_lookup_dynamically({}, "key")

        assert result is None


class TestGenerateKeyVariationsDynamically:
    """Test key variation generation functionality."""

    def test_generate_key_variations_basic(self) -> None:
        """Test key variation generation with basic input."""
        variations = _generate_key_variations_dynamically("traceparent")

        # Check that all expected variations are present
        # (order may vary due to deduplication)
        assert "traceparent" in variations  # Original/lowercase
        assert "TRACEPARENT" in variations  # Uppercase
        assert "Traceparent" in variations  # Title case
        # For "traceparent" (no underscore), underscore to hyphen creates "trace-parent"
        # But hyphen to underscore doesn't change it, so no "trace-parent" expected

        # The actual variations for "traceparent" should be:
        # ["traceparent", "TRACEPARENT", "Traceparent"] (duplicates removed)
        assert len(variations) == 3

    def test_generate_key_variations_with_hyphens(self) -> None:
        """Test key variation generation with hyphenated input."""
        variations = _generate_key_variations_dynamically("trace-parent")

        assert "trace-parent" in variations
        assert "TRACE-PARENT" in variations
        assert "Trace-Parent" in variations
        assert "trace_parent" in variations

    def test_generate_key_variations_with_underscores(self) -> None:
        """Test key variation generation with underscored input."""
        variations = _generate_key_variations_dynamically("trace_state")

        assert "trace_state" in variations
        assert "TRACE_STATE" in variations
        assert "Trace_State" in variations
        assert "trace-state" in variations

    def test_generate_key_variations_empty_string(self) -> None:
        """Test key variation generation with empty string."""
        variations = _generate_key_variations_dynamically("")

        assert not variations

    def test_generate_key_variations_deduplication(self) -> None:
        """Test that key variations are deduplicated."""
        variations = _generate_key_variations_dynamically("test")

        # "test" and "test".lower() are the same, should only appear once
        assert variations.count("test") == 1


class TestSanitizeCarrierHeadersDynamically:
    """Test carrier header sanitization functionality."""

    def test_sanitize_carrier_headers_with_standard_headers(self) -> None:
        """Test header sanitization with standard OpenTelemetry headers."""
        carrier = {
            "baggage": "session_id=123",
            "traceparent": "00-trace-span-01",
            "tracestate": "vendor=state",
            "custom": "ignored",
        }

        mock_getter = Mock()
        mock_getter.get.side_effect = lambda c, k: c.get(k.lower())

        with patch("honeyhive.tracer.utils.propagation.safe_log"):
            result = _sanitize_carrier_headers_dynamically(carrier, mock_getter)

        assert "baggage" in result
        assert "traceparent" in result
        assert "tracestate" in result
        assert "custom" not in result

    def test_sanitize_carrier_headers_empty_carrier(self) -> None:
        """Test header sanitization with empty carrier."""
        mock_getter = Mock()
        mock_getter.get.return_value = None

        result = _sanitize_carrier_headers_dynamically({}, mock_getter)

        assert not result

    @patch("honeyhive.tracer.utils.propagation.safe_log")
    def test_sanitize_carrier_headers_logs_found_headers(self, mock_log: Any) -> None:
        """Test that header sanitization logs found headers."""
        carrier = {"baggage": "test=value"}
        mock_getter = Mock()
        mock_getter.get.side_effect = lambda c, k: c.get(k)

        _sanitize_carrier_headers_dynamically(carrier, mock_getter)

        # Should log debug message for found header
        mock_log.assert_called()
        args, _ = mock_log.call_args
        assert args[1] == "debug"
        assert args[2] == "Found propagation header"


class TestGetPropagationHeadersDynamically:
    """Test propagation header list generation."""

    def test_get_propagation_headers_includes_standard_headers(self) -> None:
        """Test that standard OpenTelemetry headers are included."""
        headers = _get_propagation_headers_dynamically()

        assert "baggage" in headers
        assert "traceparent" in headers
        assert "tracestate" in headers

    def test_get_propagation_headers_includes_custom_headers(self) -> None:
        """Test that custom headers are included when available."""
        with patch(
            "honeyhive.tracer.utils.propagation."
            "_get_custom_propagation_headers_dynamically",
            return_value=["custom-header"],
        ):
            headers = _get_propagation_headers_dynamically()

        assert "baggage" in headers
        assert "traceparent" in headers
        assert "tracestate" in headers
        assert "custom-header" in headers


class TestGetCustomPropagationHeadersDynamically:  # pylint: disable=too-few-public-methods
    """Test custom propagation header retrieval."""

    def test_get_custom_propagation_headers_returns_empty_list(self) -> None:
        """Test that custom headers returns empty list by default."""
        headers = _get_custom_propagation_headers_dynamically()

        assert not headers
        assert isinstance(headers, list)


class TestExtractHeaderValueDynamically:
    """Test header value extraction functionality."""

    def test_extract_header_value_exact_case(self) -> None:
        """Test header extraction with exact case match."""
        carrier = {"baggage": "test=value"}
        mock_getter = Mock()
        mock_getter.get.side_effect = lambda c, k: c.get(k)

        with patch("honeyhive.tracer.utils.propagation.safe_log"):
            result = _extract_header_value_dynamically(carrier, "baggage", mock_getter)

        assert result == "test=value"

    def test_extract_header_value_case_variations(self) -> None:
        """Test header extraction with case variations."""
        carrier = {"BAGGAGE": "test=value"}
        mock_getter = Mock()
        mock_getter.get.side_effect = lambda c, k: c.get(k)

        with patch("honeyhive.tracer.utils.propagation.safe_log"):
            result = _extract_header_value_dynamically(carrier, "baggage", mock_getter)

        assert result == "test=value"

    def test_extract_header_value_not_found(self) -> None:
        """Test header extraction when header is not found."""
        carrier = {"other": "value"}
        mock_getter = Mock()
        mock_getter.get.return_value = None

        result = _extract_header_value_dynamically(carrier, "baggage", mock_getter)

        assert result is None

    @patch("honeyhive.tracer.utils.propagation.safe_log")
    def test_extract_header_value_logs_found_variation(self, mock_log: Any) -> None:
        """Test that header extraction logs found case variations."""
        carrier = {"BAGGAGE": "test=value"}
        mock_getter = Mock()
        mock_getter.get.side_effect = lambda c, k: c.get(k)

        _extract_header_value_dynamically(carrier, "baggage", mock_getter)

        # Should log debug message for found variation
        mock_log.assert_called()
        args, _ = mock_log.call_args
        assert args[1] == "debug"
        assert args[2] == "Found header with case variation"

    def test_extract_header_value_exception_handling(self) -> None:
        """Test header extraction with getter exceptions."""
        carrier = {"baggage": "test=value"}
        mock_getter = Mock()
        mock_getter.get.side_effect = [
            Exception("First error"),
            Exception("Second error"),
            Exception("Third error"),
            "test=value",
        ]

        with patch("honeyhive.tracer.utils.propagation.safe_log"):
            result = _extract_header_value_dynamically(carrier, "baggage", mock_getter)

        assert result == "test=value"


class TestLogSanitizationResultsDynamically:
    """Test sanitization results logging functionality."""

    @patch("honeyhive.tracer.utils.propagation.safe_log")
    def test_log_sanitization_results_with_data(
        self, mock_log: Any, honeyhive_tracer: Any
    ) -> None:
        """Test sanitization results logging with actual data."""
        original_carrier = {"BAGGAGE": "test=value", "custom": "ignored"}
        sanitized_carrier = {"baggage": "test=value"}

        _log_sanitization_results_dynamically(
            original_carrier, sanitized_carrier, honeyhive_tracer
        )

        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "Carrier sanitization completed",
            honeyhive_data={
                "original_keys": ["BAGGAGE", "custom"],
                "sanitized_keys": ["baggage"],
                "found_baggage": True,
                "found_traceparent": False,
                "found_tracestate": False,
            },
        )

    @patch("honeyhive.tracer.utils.propagation.safe_log")
    def test_log_sanitization_results_empty_carriers(
        self, mock_log: Any, honeyhive_tracer: Any
    ) -> None:
        """Test sanitization results logging with empty carriers."""
        _log_sanitization_results_dynamically({}, {}, honeyhive_tracer)

        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "Carrier sanitization completed",
            honeyhive_data={
                "original_keys": [],
                "sanitized_keys": [],
                "found_baggage": False,
                "found_traceparent": False,
                "found_tracestate": False,
            },
        )

    @patch("honeyhive.tracer.utils.propagation.safe_log")
    def test_log_sanitization_results_none_carriers(
        self, mock_log: Any, honeyhive_tracer: Any  # pylint: disable=unused-argument
    ) -> None:
        """Test sanitization results logging with None carriers."""
        # The function handles None carriers by checking "if original_carrier else []"
        # but the "in" operator on None will raise TypeError,
        # so this should raise
        with pytest.raises(TypeError):
            _log_sanitization_results_dynamically(
                None, None, honeyhive_tracer  # type: ignore[arg-type]
            )

    @patch("honeyhive.tracer.utils.propagation.safe_log")
    def test_log_sanitization_results_all_headers_found(
        self, mock_log: Any, honeyhive_tracer: Any
    ) -> None:
        """Test sanitization results logging when all standard headers are found."""
        original_carrier = {
            "BAGGAGE": "test",
            "TRACEPARENT": "trace",
            "TRACESTATE": "state",
        }
        sanitized_carrier = {
            "baggage": "test",
            "traceparent": "trace",
            "tracestate": "state",
        }

        _log_sanitization_results_dynamically(
            original_carrier, sanitized_carrier, honeyhive_tracer
        )

        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "Carrier sanitization completed",
            honeyhive_data={
                "original_keys": ["BAGGAGE", "TRACEPARENT", "TRACESTATE"],
                "sanitized_keys": ["baggage", "traceparent", "tracestate"],
                "found_baggage": True,
                "found_traceparent": True,
                "found_tracestate": True,
            },
        )
