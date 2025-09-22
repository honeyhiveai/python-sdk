"""Unit tests for HoneyHive baggage dictionary utilities."""

# pylint: disable=too-many-public-methods,too-few-public-methods
# Justification: Comprehensive test coverage requires many test methods,
# and some test classes may have few methods for specific test scenarios.

from typing import Any
from unittest.mock import Mock, patch

import pytest

from honeyhive.utils.baggage_dict import BaggageDict


class TestBaggageDict:
    """Test BaggageDict functionality."""

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_init_empty(self, mock_context: Any, _mock_baggage: Any) -> None:
        """Test BaggageDict initialization with empty context."""
        mock_context.get_current.return_value = Mock()
        baggage = BaggageDict()
        assert baggage is not None
        assert baggage.context is not None

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_init_with_context(self, _mock_context: Any, _mock_baggage: Any) -> None:
        """Test BaggageDict initialization with custom context."""
        custom_context = Mock()
        baggage = BaggageDict(custom_context)
        assert baggage.context == custom_context

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_get_existing_key(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test getting existing baggage key."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_baggage.return_value = "test_value"

        baggage = BaggageDict()
        value = baggage.get("test_key")
        assert value == "test_value"
        mock_baggage.get_baggage.assert_called_once_with("test_key", baggage.context)

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_get_missing_key(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test getting missing baggage key."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_baggage.return_value = None

        baggage = BaggageDict()
        value = baggage.get("missing_key")
        assert value is None

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_get_with_default(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test getting baggage key with default value."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_baggage.return_value = None

        baggage = BaggageDict()
        value = baggage.get("missing_key", "default_value")
        assert value == "default_value"

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_set_key(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test setting baggage key."""
        mock_context.get_current.return_value = Mock()
        new_context = Mock()
        mock_baggage.set_baggage.return_value = new_context

        baggage = BaggageDict()
        result = baggage.set("test_key", "test_value")

        assert isinstance(result, BaggageDict)
        assert result.context == new_context
        mock_baggage.set_baggage.assert_called_once_with(
            "test_key", "test_value", baggage.context
        )

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_delete_key(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test deleting baggage key."""
        mock_context.get_current.return_value = Mock()
        new_context = Mock()
        mock_baggage.set_baggage.return_value = new_context

        baggage = BaggageDict()
        result = baggage.delete("test_key")

        assert isinstance(result, BaggageDict)
        assert result.context == new_context
        mock_baggage.set_baggage.assert_called_once_with(
            "test_key", None, baggage.context
        )

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_update_multiple_keys(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test updating multiple baggage keys."""
        mock_context.get_current.return_value = Mock()
        new_context = Mock()
        mock_baggage.set_baggage.return_value = new_context

        baggage = BaggageDict()
        result = baggage.update(key1="value1", key2="value2")

        assert isinstance(result, BaggageDict)
        assert result.context == new_context
        assert mock_baggage.set_baggage.call_count == 2

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_clear(self, mock_context: Any, _mock_baggage: Any) -> None:
        """Test clearing all baggage."""
        mock_context.get_current.return_value = Mock()

        baggage = BaggageDict()
        result = baggage.clear()

        assert isinstance(result, BaggageDict)
        assert result.context is not None

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_items(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test getting all baggage items."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_all.return_value = {"key1": "value1", "key2": "value2"}

        baggage = BaggageDict()
        items = baggage.items()

        assert items == {"key1": "value1", "key2": "value2"}

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_items_empty(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test getting items when baggage is empty."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_all.return_value = None

        baggage = BaggageDict()
        items = baggage.items()

        assert items == {}

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_items_exception_handling(
        self, mock_context: Any, mock_baggage: Any
    ) -> None:
        """Test items method with exception handling."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_all.side_effect = Exception("Test exception")

        baggage = BaggageDict()
        items = baggage.items()

        assert items == {}

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_keys(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test getting baggage keys."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_all.return_value = {"key1": "value1", "key2": "value2"}

        baggage = BaggageDict()
        keys = list(baggage.keys())

        assert set(keys) == {"key1", "key2"}

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_values(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test getting baggage values."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_all.return_value = {"key1": "value1", "key2": "value2"}

        baggage = BaggageDict()
        values = list(baggage.values())

        assert set(values) == {"value1", "value2"}

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_getitem_existing(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test getting item using bracket notation."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_baggage.return_value = "test_value"

        baggage = BaggageDict()
        value = baggage["test_key"]

        assert value == "test_value"

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_getitem_missing(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test getting missing item using bracket notation."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_baggage.return_value = None

        baggage = BaggageDict()
        with pytest.raises(KeyError):
            _ = baggage["missing_key"]

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_setitem(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test setting item using bracket notation."""
        mock_context.get_current.return_value = Mock()
        new_context = Mock()
        mock_baggage.set_baggage.return_value = new_context

        baggage = BaggageDict()
        baggage["test_key"] = "test_value"

        mock_baggage.set_baggage.assert_called_once_with(
            "test_key", "test_value", baggage.context
        )

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_delitem(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test deleting item using bracket notation."""
        mock_context.get_current.return_value = Mock()
        new_context = Mock()
        mock_baggage.set_baggage.return_value = new_context

        baggage = BaggageDict()
        del baggage["test_key"]

        mock_baggage.set_baggage.assert_called_once_with(
            "test_key", None, baggage.context
        )

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_contains_existing(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test checking if key exists."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_baggage.return_value = "test_value"

        baggage = BaggageDict()
        assert "test_key" in baggage

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_contains_missing(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test checking if missing key exists."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_baggage.return_value = None

        baggage = BaggageDict()
        assert "missing_key" not in baggage

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_len(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test getting baggage length."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_all.return_value = {"key1": "value1", "key2": "value2"}

        baggage = BaggageDict()
        length = len(baggage)

        assert length == 2

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_iter(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test iterating over baggage keys."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_all.return_value = {"key1": "value1", "key2": "value2"}

        baggage = BaggageDict()
        keys = list(baggage)

        assert set(keys) == {"key1", "key2"}

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_repr(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test string representation."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_all.return_value = {"key1": "value1"}

        baggage = BaggageDict()
        repr_str = repr(baggage)

        assert "BaggageDict" in repr_str
        assert "key1" in repr_str
        assert "value1" in repr_str

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_from_dict(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test creating BaggageDict from dictionary."""
        mock_context.get_current.return_value = Mock()
        new_context = Mock()
        mock_baggage.set_baggage.return_value = new_context

        data = {"key1": "value1", "key2": "value2"}
        baggage = BaggageDict.from_dict(data)

        assert isinstance(baggage, BaggageDict)
        assert mock_baggage.set_baggage.call_count == 2

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_from_dict_with_context(
        self, _mock_context: Any, mock_baggage: Any
    ) -> None:
        """Test creating BaggageDict from dictionary with custom context."""
        custom_context = Mock()
        new_context = Mock()
        mock_baggage.set_baggage.return_value = new_context

        data = {"key1": "value1"}
        baggage = BaggageDict.from_dict(data, custom_context)

        assert isinstance(baggage, BaggageDict)
        assert baggage.context == new_context

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_as_context(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test using BaggageDict as context manager."""
        mock_context.get_current.return_value = Mock()
        mock_context.attach.return_value = Mock()
        new_context = Mock()
        mock_baggage.set_baggage.return_value = new_context

        baggage = BaggageDict()
        baggage = baggage.set("test_key", "test_value")

        with baggage.as_context():
            # Context should be attached
            pass

        mock_context.attach.assert_called_once()
        mock_context.detach.assert_called_once()

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_as_context_exception(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test context manager with exception."""
        mock_context.get_current.return_value = Mock()
        mock_context.attach.return_value = Mock()
        new_context = Mock()
        mock_baggage.set_baggage.return_value = new_context

        baggage = BaggageDict()
        baggage = baggage.set("test_key", "test_value")

        with pytest.raises(ValueError):
            with baggage.as_context():
                raise ValueError("Test exception")

        mock_context.attach.assert_called_once()
        mock_context.detach.assert_called_once()

    # Note: OpenTelemetry is now a hard requirement, so no conditional import
    # tests needed

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_non_string_values(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test handling of non-string values."""
        mock_context.get_current.return_value = Mock()
        new_context = Mock()
        mock_baggage.set_baggage.return_value = new_context

        baggage = BaggageDict()
        result = baggage.set("number_key", 42)

        assert isinstance(result, BaggageDict)
        mock_baggage.set_baggage.assert_called_once_with(
            "number_key", "42", baggage.context
        )

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_boolean_values(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test handling of boolean values."""
        mock_context.get_current.return_value = Mock()
        new_context = Mock()
        mock_baggage.set_baggage.return_value = new_context

        baggage = BaggageDict()
        result = baggage.set("bool_key", True)

        assert isinstance(result, BaggageDict)
        mock_baggage.set_baggage.assert_called_once_with(
            "bool_key", "True", baggage.context
        )

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_none_values(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test handling of None values."""
        mock_context.get_current.return_value = Mock()
        new_context = Mock()
        mock_baggage.set_baggage.return_value = new_context

        baggage = BaggageDict()
        result = baggage.set("none_key", None)

        assert isinstance(result, BaggageDict)
        mock_baggage.set_baggage.assert_called_once_with(
            "none_key", "None", baggage.context
        )

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_complex_values(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test handling of complex values."""
        mock_context.get_current.return_value = Mock()
        new_context = Mock()
        mock_baggage.set_baggage.return_value = new_context

        complex_value = {"nested": "value", "list": [1, 2, 3]}
        baggage = BaggageDict()
        result = baggage.set("complex_key", complex_value)

        assert isinstance(result, BaggageDict)
        mock_baggage.set_baggage.assert_called_once_with(
            "complex_key", str(complex_value), baggage.context
        )

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_chained_operations(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test chaining multiple operations."""
        mock_context.get_current.return_value = Mock()
        new_context = Mock()
        mock_baggage.set_baggage.return_value = new_context

        baggage = BaggageDict()
        result = baggage.set("key1", "value1").set("key2", "value2").delete("key1")

        assert isinstance(result, BaggageDict)
        assert mock_baggage.set_baggage.call_count == 3

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_context_property(self, _mock_context: Any, _mock_baggage: Any) -> None:
        """Test context property."""
        custom_context = Mock()
        baggage = BaggageDict(custom_context)

        assert baggage.context == custom_context

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_empty_items_repr(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test string representation with empty baggage."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_all.return_value = {}

        baggage = BaggageDict()
        repr_str = repr(baggage)

        assert repr_str == "BaggageDict({})"

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_multiple_updates(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test multiple update operations."""
        mock_context.get_current.return_value = Mock()
        new_context = Mock()
        mock_baggage.set_baggage.return_value = new_context

        baggage = BaggageDict()
        result = baggage.update(a="1", b="2", c="3")

        assert isinstance(result, BaggageDict)
        assert mock_baggage.set_baggage.call_count == 3

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_get_with_none_value(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test getting a key that has None value."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_baggage.return_value = None

        baggage = BaggageDict()
        value = baggage.get("none_key", "default")

        assert value == "default"

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_get_with_empty_string(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test getting a key that has empty string value."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_baggage.return_value = ""

        baggage = BaggageDict()
        value = baggage.get("empty_key")

        assert value == ""

    @patch("honeyhive.utils.baggage_dict.baggage")
    @patch("honeyhive.utils.baggage_dict.context")
    def test_get_with_zero_value(self, mock_context: Any, mock_baggage: Any) -> None:
        """Test getting a key that has zero value."""
        mock_context.get_current.return_value = Mock()
        mock_baggage.get_baggage.return_value = "0"

        baggage = BaggageDict()
        value = baggage.get("zero_key")

        assert value == "0"


class TestBaggageDictImportHandling:
    """Test OpenTelemetry baggage import error handling using sys.modules
    manipulation."""

    # Note: Removed OTEL availability test since OpenTelemetry is now a hard
    # requirement

    # Note: Removed obsolete OTEL availability tests since OpenTelemetry is now
    # a hard requirement
