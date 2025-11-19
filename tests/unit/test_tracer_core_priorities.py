"""Unit tests for honeyhive.tracer.core.priorities module.

This module provides comprehensive unit tests for the core attribute priority
system, ensuring critical attributes are correctly classified and prioritized
for eviction protection.
"""

# pylint: disable=duplicate-code
# Justification: Test constants intentionally duplicate source constants from
# priorities.py to verify correct values. This is standard test practice - tests
# must independently define expected values to validate implementation.

import pytest

from honeyhive.tracer.core.priorities import (
    CORE_ATTRIBUTES,
    CRITICAL_ATTRIBUTES,
    HIGH_PRIORITY_ATTRIBUTES,
    HONEYHIVE_NAMESPACE,
    NORMAL_PRIORITY_ATTRIBUTES,
    AttributePriority,
    get_attribute_priority,
    get_attributes_by_priority,
    get_core_attributes,
    get_critical_attributes,
    is_core_attribute,
    is_critical_attribute,
)


class TestAttributePriority:
    """Test suite for AttributePriority enum."""

    def test_priority_values(self) -> None:
        """Test AttributePriority enum has correct integer values."""
        assert AttributePriority.CRITICAL == 0
        assert AttributePriority.HIGH == 1
        assert AttributePriority.NORMAL == 2
        assert AttributePriority.LOW == 3

    def test_priority_ordering(self) -> None:
        """Test AttributePriority values are correctly ordered."""
        assert AttributePriority.CRITICAL < AttributePriority.HIGH
        assert AttributePriority.HIGH < AttributePriority.NORMAL
        assert AttributePriority.NORMAL < AttributePriority.LOW


class TestCoreAttributeSets:
    """Test suite for core attribute set definitions."""

    def test_critical_attributes_defined(self) -> None:
        """Test CRITICAL_ATTRIBUTES set contains expected attributes."""
        expected_critical = {
            f"{HONEYHIVE_NAMESPACE}session_id",
            f"{HONEYHIVE_NAMESPACE}event_type",
            f"{HONEYHIVE_NAMESPACE}event_name",
            f"{HONEYHIVE_NAMESPACE}source",
            f"{HONEYHIVE_NAMESPACE}duration",
        }
        assert CRITICAL_ATTRIBUTES == expected_critical

    def test_high_priority_attributes_defined(self) -> None:
        """Test HIGH_PRIORITY_ATTRIBUTES set contains expected attributes."""
        expected_high = {
            f"{HONEYHIVE_NAMESPACE}event_id",
            f"{HONEYHIVE_NAMESPACE}outputs",
        }
        assert HIGH_PRIORITY_ATTRIBUTES == expected_high

    def test_normal_priority_attributes_defined(self) -> None:
        """Test NORMAL_PRIORITY_ATTRIBUTES set contains expected attributes."""
        expected_normal = {
            f"{HONEYHIVE_NAMESPACE}project_id",
            f"{HONEYHIVE_NAMESPACE}tenant",
            f"{HONEYHIVE_NAMESPACE}start_time",
            f"{HONEYHIVE_NAMESPACE}end_time",
            f"{HONEYHIVE_NAMESPACE}inputs",
            f"{HONEYHIVE_NAMESPACE}metadata",
        }
        assert NORMAL_PRIORITY_ATTRIBUTES == expected_normal

    def test_core_attributes_union(self) -> None:
        """Test CORE_ATTRIBUTES is union of all priority levels."""
        expected_union = (
            CRITICAL_ATTRIBUTES | HIGH_PRIORITY_ATTRIBUTES | NORMAL_PRIORITY_ATTRIBUTES
        )
        assert CORE_ATTRIBUTES == expected_union

    def test_no_attribute_overlap(self) -> None:
        """Test attribute sets don't overlap between priority levels."""
        assert CRITICAL_ATTRIBUTES.isdisjoint(HIGH_PRIORITY_ATTRIBUTES)
        assert CRITICAL_ATTRIBUTES.isdisjoint(NORMAL_PRIORITY_ATTRIBUTES)
        assert HIGH_PRIORITY_ATTRIBUTES.isdisjoint(NORMAL_PRIORITY_ATTRIBUTES)

    def test_all_attributes_use_honeyhive_namespace(self) -> None:
        """Test all core attributes use honeyhive namespace."""
        for attr in CORE_ATTRIBUTES:
            assert attr.startswith(HONEYHIVE_NAMESPACE)


class TestGetAttributePriority:
    """Test suite for get_attribute_priority function."""

    def test_critical_attributes_return_priority_zero(self) -> None:
        """Test critical attributes return CRITICAL priority."""
        for attr in CRITICAL_ATTRIBUTES:
            priority = get_attribute_priority(attr)
            assert priority == AttributePriority.CRITICAL
            assert priority == 0

    def test_high_priority_attributes_return_priority_one(self) -> None:
        """Test high-priority attributes return HIGH priority."""
        for attr in HIGH_PRIORITY_ATTRIBUTES:
            priority = get_attribute_priority(attr)
            assert priority == AttributePriority.HIGH
            assert priority == 1

    def test_normal_priority_attributes_return_priority_two(self) -> None:
        """Test normal-priority attributes return NORMAL priority."""
        for attr in NORMAL_PRIORITY_ATTRIBUTES:
            priority = get_attribute_priority(attr)
            assert priority == AttributePriority.NORMAL
            assert priority == 2

    def test_unknown_attributes_return_low_priority(self) -> None:
        """Test unknown attributes return LOW priority."""
        unknown_attrs = [
            "custom.field",
            "openinference.span.kind",
            "llm.request_id",
            "honeyhive.custom_field",  # honeyhive namespace but not core
            "random_attribute",
        ]
        for attr in unknown_attrs:
            priority = get_attribute_priority(attr)
            assert priority == AttributePriority.LOW
            assert priority == 3

    def test_empty_string_returns_low_priority(self) -> None:
        """Test empty string returns LOW priority."""
        priority = get_attribute_priority("")
        assert priority == AttributePriority.LOW

    def test_case_sensitive_matching(self) -> None:
        """Test attribute matching is case-sensitive."""
        # Correct case
        correct = get_attribute_priority("honeyhive.session_id")
        assert correct == AttributePriority.CRITICAL

        # Wrong case
        wrong_case = get_attribute_priority("honeyhive.SESSION_ID")
        assert wrong_case == AttributePriority.LOW

        wrong_case2 = get_attribute_priority("HONEYHIVE.session_id")
        assert wrong_case2 == AttributePriority.LOW


class TestIsCriticalAttribute:
    """Test suite for is_critical_attribute function."""

    def test_critical_attributes_return_true(self) -> None:
        """Test critical attributes return True."""
        for attr in CRITICAL_ATTRIBUTES:
            assert is_critical_attribute(attr) is True

    def test_non_critical_core_attributes_return_false(self) -> None:
        """Test non-critical core attributes return False."""
        for attr in HIGH_PRIORITY_ATTRIBUTES | NORMAL_PRIORITY_ATTRIBUTES:
            assert is_critical_attribute(attr) is False

    def test_unknown_attributes_return_false(self) -> None:
        """Test unknown attributes return False."""
        assert is_critical_attribute("custom.field") is False
        assert is_critical_attribute("honeyhive.custom") is False
        assert is_critical_attribute("") is False


class TestIsCoreAttribute:
    """Test suite for is_core_attribute function."""

    def test_all_core_attributes_return_true(self) -> None:
        """Test all defined core attributes return True."""
        for attr in CORE_ATTRIBUTES:
            assert is_core_attribute(attr) is True

    def test_critical_attributes_return_true(self) -> None:
        """Test critical attributes are recognized as core."""
        for attr in CRITICAL_ATTRIBUTES:
            assert is_core_attribute(attr) is True

    def test_high_priority_attributes_return_true(self) -> None:
        """Test high-priority attributes are recognized as core."""
        for attr in HIGH_PRIORITY_ATTRIBUTES:
            assert is_core_attribute(attr) is True

    def test_normal_priority_attributes_return_true(self) -> None:
        """Test normal-priority attributes are recognized as core."""
        for attr in NORMAL_PRIORITY_ATTRIBUTES:
            assert is_core_attribute(attr) is True

    def test_unknown_attributes_return_false(self) -> None:
        """Test unknown attributes return False."""
        unknown_attrs = [
            "custom.field",
            "openinference.span.kind",
            "honeyhive.unknown_field",
            "",
        ]
        for attr in unknown_attrs:
            assert is_core_attribute(attr) is False


class TestGetCriticalAttributes:
    """Test suite for get_critical_attributes function."""

    def test_returns_critical_attributes_set(self) -> None:
        """Test function returns correct critical attributes."""
        result = get_critical_attributes()
        assert result == CRITICAL_ATTRIBUTES

    def test_returns_copy_not_reference(self) -> None:
        """Test function returns a copy, not reference to original set."""
        result = get_critical_attributes()
        result.add("test.attribute")

        # Original should be unchanged
        assert "test.attribute" not in CRITICAL_ATTRIBUTES

    def test_returned_set_is_mutable(self) -> None:
        """Test returned set can be modified without affecting module."""
        result = get_critical_attributes()
        original_size = len(result)
        result.clear()

        assert len(result) == 0
        assert len(get_critical_attributes()) == original_size


class TestGetCoreAttributes:
    """Test suite for get_core_attributes function."""

    def test_returns_core_attributes_set(self) -> None:
        """Test function returns correct core attributes."""
        result = get_core_attributes()
        assert result == CORE_ATTRIBUTES

    def test_returns_copy_not_reference(self) -> None:
        """Test function returns a copy, not reference to original set."""
        result = get_core_attributes()
        result.add("test.attribute")

        # Original should be unchanged
        assert "test.attribute" not in CORE_ATTRIBUTES

    def test_includes_all_priority_levels(self) -> None:
        """Test returned set includes critical, high, and normal priorities."""
        result = get_core_attributes()

        for attr in CRITICAL_ATTRIBUTES:
            assert attr in result

        for attr in HIGH_PRIORITY_ATTRIBUTES:
            assert attr in result

        for attr in NORMAL_PRIORITY_ATTRIBUTES:
            assert attr in result


class TestGetAttributesByPriority:
    """Test suite for get_attributes_by_priority function."""

    def test_critical_priority_returns_critical_attributes(self) -> None:
        """Test filtering by CRITICAL priority returns correct attributes."""
        result = get_attributes_by_priority(AttributePriority.CRITICAL)
        assert result == CRITICAL_ATTRIBUTES

    def test_high_priority_returns_high_attributes(self) -> None:
        """Test filtering by HIGH priority returns correct attributes."""
        result = get_attributes_by_priority(AttributePriority.HIGH)
        assert result == HIGH_PRIORITY_ATTRIBUTES

    def test_normal_priority_returns_normal_attributes(self) -> None:
        """Test filtering by NORMAL priority returns correct attributes."""
        result = get_attributes_by_priority(AttributePriority.NORMAL)
        assert result == NORMAL_PRIORITY_ATTRIBUTES

    def test_low_priority_returns_empty_set(self) -> None:
        """Test filtering by LOW priority returns empty set."""
        result = get_attributes_by_priority(AttributePriority.LOW)
        assert result == set()

    def test_invalid_priority_type_raises_error(self) -> None:
        """Test passing invalid priority type raises ValueError."""
        with pytest.raises(ValueError, match="priority must be AttributePriority"):
            get_attributes_by_priority(0)  # type: ignore[arg-type]

        with pytest.raises(ValueError, match="priority must be AttributePriority"):
            get_attributes_by_priority("CRITICAL")  # type: ignore[arg-type]

        with pytest.raises(ValueError, match="priority must be AttributePriority"):
            get_attributes_by_priority(None)  # type: ignore[arg-type]


class TestPrioritySystemIntegration:
    """Integration tests for priority system behavior."""

    def test_all_core_attributes_have_priority(self) -> None:
        """Test every core attribute has a defined priority."""
        for attr in CORE_ATTRIBUTES:
            priority = get_attribute_priority(attr)
            assert priority in {
                AttributePriority.CRITICAL,
                AttributePriority.HIGH,
                AttributePriority.NORMAL,
            }

    def test_priority_distribution(self) -> None:
        """Test priority distribution matches expected counts."""
        critical_count = len(CRITICAL_ATTRIBUTES)
        high_count = len(HIGH_PRIORITY_ATTRIBUTES)
        normal_count = len(NORMAL_PRIORITY_ATTRIBUTES)

        assert (
            critical_count == 5
        )  # session_id, event_type, event_name, source, duration
        assert high_count == 2  # event_id, outputs
        assert normal_count == 6  # project_id, tenant, start/end_time, inputs, metadata

    def test_critical_attribute_priorities_lowest(self) -> None:
        """Test critical attributes have lowest priority value (highest protection)."""
        for critical_attr in CRITICAL_ATTRIBUTES:
            critical_priority = get_attribute_priority(critical_attr)

            for other_attr in HIGH_PRIORITY_ATTRIBUTES | NORMAL_PRIORITY_ATTRIBUTES:
                other_priority = get_attribute_priority(other_attr)
                assert critical_priority < other_priority

    def test_attribute_priority_sorting(self) -> None:
        """Test attributes can be sorted by priority for eviction order."""
        all_attrs = list(CORE_ATTRIBUTES) + ["custom.field1", "custom.field2"]

        # Sort by priority (critical first, low last)
        sorted_attrs = sorted(all_attrs, key=get_attribute_priority)

        # First attributes should be critical
        for i in range(len(CRITICAL_ATTRIBUTES)):
            assert get_attribute_priority(sorted_attrs[i]) == AttributePriority.CRITICAL

        # Last attributes should be custom (LOW priority)
        assert get_attribute_priority(sorted_attrs[-1]) == AttributePriority.LOW
        assert get_attribute_priority(sorted_attrs[-2]) == AttributePriority.LOW


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    def test_namespace_prefix_handling(self) -> None:
        """Test handling of attributes with and without namespace."""
        # With namespace - core attribute
        with_namespace = f"{HONEYHIVE_NAMESPACE}session_id"
        assert is_critical_attribute(with_namespace) is True

        # Without namespace - not core
        without_namespace = "session_id"
        assert is_critical_attribute(without_namespace) is False
        assert get_attribute_priority(without_namespace) == AttributePriority.LOW

    def test_partial_namespace_match(self) -> None:
        """Test partial namespace matches are not recognized as core."""
        partial_matches = [
            "honeyhiv.session_id",  # Missing 'e'
            "honeyhive_session_id",  # Underscore instead of dot
            "honeyhivesession_id",  # No separator
        ]
        for attr in partial_matches:
            assert is_core_attribute(attr) is False
            assert get_attribute_priority(attr) == AttributePriority.LOW

    def test_empty_and_whitespace_attributes(self) -> None:
        """Test handling of empty and whitespace-only attributes."""
        test_attrs = ["", " ", "  ", "\t", "\n"]
        for attr in test_attrs:
            assert is_core_attribute(attr) is False
            assert get_attribute_priority(attr) == AttributePriority.LOW
