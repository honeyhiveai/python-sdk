"""Unit tests for DotDict utility class.

Comprehensive test suite for the DotDict class that provides dictionary access
with dot notation support. Tests all methods, edge cases, and error conditions.

Test Coverage:
- Initialization patterns (dict, kwargs, mixed)
- Attribute access (__getattr__, __setattr__, __delattr__)
- Item access (__getitem__, __setitem__ with dot notation)
- Dictionary methods (get, setdefault, update)
- Conversion methods (to_dict, copy, deepcopy)
- Nested dictionary handling and conversion
- Error conditions and edge cases

Following Agent OS testing standards with proper fixtures and isolation.
Generated using enhanced comprehensive analysis framework for 90%+ coverage.
"""

# pylint: disable=too-many-lines,line-too-long,redefined-outer-name,no-member
# Reason: Comprehensive testing file requires extensive test coverage for 90%+ target
# Line length disabled for test readability and comprehensive assertions
# Redefined outer name disabled for pytest fixture usage pattern
# No-member disabled for DotDict attribute access (false positives)

from typing import Any, Dict

import pytest

from honeyhive.utils.dotdict import DotDict


class TestDotDictInitialization:
    """Test cases for DotDict initialization patterns."""

    def test_init_empty(self) -> None:
        """Test DotDict initialization with no arguments."""
        dotdict = DotDict()

        assert len(dotdict) == 0
        assert isinstance(dotdict, dict)
        assert isinstance(dotdict, DotDict)

    def test_init_with_dict(self) -> None:
        """Test DotDict initialization with dictionary argument."""
        data: Dict[str, Any] = {"foo": "bar", "nested": {"key": "value"}}
        dotdict = DotDict(data)

        assert dotdict.foo == "bar"
        assert isinstance(dotdict.nested, DotDict)
        assert dotdict.nested.key == "value"

    def test_init_with_kwargs(self) -> None:
        """Test DotDict initialization with keyword arguments."""
        dotdict = DotDict(foo="bar", nested={"key": "value"})

        assert dotdict.foo == "bar"
        assert isinstance(dotdict.nested, DotDict)
        assert dotdict.nested.key == "value"

    def test_init_with_dict_and_kwargs(self) -> None:
        """Test DotDict initialization with both dict and kwargs."""
        data: Dict[str, Any] = {"a": 1, "b": 2}
        dotdict = DotDict(data, c=3, d=4)

        assert dotdict.a == 1
        assert dotdict.b == 2
        assert dotdict.c == 3
        assert dotdict.d == 4

    def test_init_nested_dict_conversion(self) -> None:
        """Test that nested dictionaries are converted to DotDict instances."""
        data: Dict[str, Any] = {"level1": {"level2": {"level3": "value"}}}
        dotdict = DotDict(data)

        assert isinstance(dotdict.level1, DotDict)
        assert isinstance(dotdict.level1.level2, DotDict)
        assert dotdict.level1.level2.level3 == "value"

    def test_init_mixed_nested_types(self) -> None:
        """Test initialization with mixed nested types."""
        data: Dict[str, Any] = {
            "string": "value",
            "number": 42,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "none": None,
        }
        dotdict = DotDict(data)

        assert dotdict.string == "value"
        assert dotdict.number == 42
        assert dotdict.list == [1, 2, 3]
        assert isinstance(dotdict.dict, DotDict)
        assert dotdict.dict.nested == "value"
        assert dotdict.none is None


class TestDotDictAttributeAccess:
    """Test cases for attribute-style access methods."""

    def test_getattr_success(self) -> None:
        """Test successful attribute access."""
        dotdict = DotDict({"foo": "bar"})

        assert dotdict.foo == "bar"

    def test_getattr_missing_key(self) -> None:
        """Test attribute access for missing key raises AttributeError."""
        dotdict = DotDict({"foo": "bar"})

        with pytest.raises(
            AttributeError, match="'DotDict' object has no attribute 'missing'"
        ):
            _ = dotdict.missing

    def test_getattr_nested_access(self) -> None:
        """Test attribute access for nested DotDict instances."""
        dotdict = DotDict({"nested": {"key": "value"}})

        assert isinstance(dotdict.nested, DotDict)
        assert dotdict.nested.key == "value"

    def test_setattr_new_key(self) -> None:
        """Test setting new attribute creates dictionary entry."""
        dotdict = DotDict()
        dotdict.new_key = "new_value"

        assert dotdict.new_key == "new_value"
        assert dotdict["new_key"] == "new_value"

    def test_setattr_existing_key(self) -> None:
        """Test setting existing attribute updates value."""
        dotdict = DotDict({"existing": "old_value"})
        dotdict.existing = "new_value"

        assert dotdict.existing == "new_value"
        assert dotdict["existing"] == "new_value"

    def test_setattr_dict_value_conversion(self) -> None:
        """Test setting attribute with dict value converts to DotDict."""
        dotdict = DotDict()
        dotdict.nested = {"key": "value"}

        assert isinstance(dotdict.nested, DotDict)
        assert dotdict.nested.key == "value"

    def test_setattr_nested_dict_conversion(self) -> None:
        """Test setting deeply nested dict converts all levels."""
        dotdict = DotDict()
        dotdict.deep = {"level1": {"level2": {"level3": "value"}}}

        assert isinstance(dotdict.deep, DotDict)
        assert isinstance(dotdict.deep.level1, DotDict)
        assert isinstance(dotdict.deep.level1.level2, DotDict)
        assert dotdict.deep.level1.level2.level3 == "value"

    def test_delattr_success(self) -> None:
        """Test successful attribute deletion."""
        dotdict = DotDict({"foo": "bar", "other": "value"})
        del dotdict.foo

        assert "foo" not in dotdict
        assert dotdict.other == "value"

    def test_delattr_missing_key(self) -> None:
        """Test deletion of missing attribute raises AttributeError."""
        dotdict = DotDict({"foo": "bar"})

        with pytest.raises(
            AttributeError, match="'DotDict' object has no attribute 'missing'"
        ):
            del dotdict.missing


class TestDotDictItemAccess:
    """Test cases for item-style access methods."""

    def test_getitem_simple(self) -> None:
        """Test simple item access."""
        dotdict = DotDict({"foo": "bar"})

        assert dotdict["foo"] == "bar"

    def test_getitem_missing_key(self) -> None:
        """Test item access for missing key raises KeyError."""
        dotdict = DotDict({"foo": "bar"})

        with pytest.raises(KeyError):
            _ = dotdict["missing"]

    def test_getitem_dot_notation(self) -> None:
        """Test item access with dot notation."""
        dotdict = DotDict({"nested": {"key": "value"}})

        assert dotdict["nested.key"] == "value"

    def test_getitem_deep_dot_notation(self) -> None:
        """Test deep dot notation access."""
        dotdict = DotDict({"level1": {"level2": {"level3": "value"}}})

        assert dotdict["level1.level2.level3"] == "value"

    def test_getitem_missing_dot_notation(self) -> None:
        """Test item access for missing dot notation key."""
        dotdict = DotDict({"nested": {"key": "value"}})

        with pytest.raises(KeyError):
            _ = dotdict["nested.missing"]

    def test_getitem_partial_missing_dot_notation(self) -> None:
        """Test dot notation with missing intermediate keys."""
        dotdict = DotDict({"nested": {"key": "value"}})

        with pytest.raises(KeyError):
            _ = dotdict["missing.key"]

    def test_setitem_simple(self) -> None:
        """Test simple item setting."""
        dotdict = DotDict()
        dotdict["foo"] = "bar"

        assert dotdict.foo == "bar"
        assert dotdict["foo"] == "bar"

    def test_setitem_dict_value_conversion(self) -> None:
        """Test setting item with dict value converts to DotDict."""
        dotdict = DotDict()
        dotdict["nested"] = {"key": "value"}

        assert isinstance(dotdict.nested, DotDict)
        assert dotdict.nested.key == "value"

    def test_setitem_dot_notation_creates_structure(self) -> None:
        """Test setting item with dot notation creates nested structure."""
        dotdict = DotDict()
        dotdict["nested.key"] = "value"

        assert isinstance(dotdict.nested, DotDict)
        assert dotdict.nested.key == "value"

    def test_setitem_deep_dot_notation(self) -> None:
        """Test setting item with deep dot notation."""
        dotdict = DotDict()
        dotdict["level1.level2.level3"] = "value"

        assert isinstance(dotdict.level1, DotDict)
        assert isinstance(dotdict.level1.level2, DotDict)
        assert dotdict.level1.level2.level3 == "value"

    def test_setitem_existing_dot_notation(self) -> None:
        """Test setting existing dot notation path updates value."""
        dotdict = DotDict({"nested": {"key": "old_value"}})
        dotdict["nested.key"] = "new_value"

        assert dotdict.nested.key == "new_value"

    def test_setitem_partial_existing_dot_notation(self) -> None:
        """Test setting dot notation with partially existing path."""
        dotdict = DotDict({"nested": {"existing": "value"}})
        dotdict["nested.new_key"] = "new_value"

        assert dotdict.nested.existing == "value"
        assert dotdict.nested.new_key == "new_value"


class TestDotDictDictionaryMethods:
    """Test cases for dictionary method implementations."""

    def test_get_with_existing_key(self) -> None:
        """Test get method with existing key."""
        dotdict = DotDict({"foo": "bar"})

        assert dotdict.get("foo") == "bar"

    def test_get_with_missing_key_no_default(self) -> None:
        """Test get method with missing key returns None."""
        dotdict = DotDict({"foo": "bar"})

        assert dotdict.get("missing") is None

    def test_get_with_missing_key_with_default(self) -> None:
        """Test get method with missing key returns default."""
        dotdict = DotDict({"foo": "bar"})

        assert dotdict.get("missing", "default") == "default"

    def test_get_with_dot_notation(self) -> None:
        """Test get method with dot notation."""
        dotdict = DotDict({"nested": {"key": "value"}})

        assert dotdict.get("nested.key") == "value"

    def test_get_with_missing_dot_notation(self) -> None:
        """Test get method with missing dot notation returns default."""
        dotdict = DotDict({"nested": {"key": "value"}})

        assert dotdict.get("nested.missing", "default") == "default"

    def test_get_with_partial_missing_dot_notation(self) -> None:
        """Test get method with missing intermediate dot notation."""
        dotdict = DotDict({"nested": {"key": "value"}})

        assert dotdict.get("missing.path", "default") == "default"

    def test_setdefault_new_key(self) -> None:
        """Test setdefault with new key sets and returns default."""
        dotdict = DotDict()
        result = dotdict.setdefault("new_key", "default_value")

        assert result == "default_value"
        assert dotdict.new_key == "default_value"

    def test_setdefault_existing_key(self) -> None:
        """Test setdefault with existing key returns existing value."""
        dotdict = DotDict({"existing": "value"})
        result = dotdict.setdefault("existing", "default_value")

        assert result == "value"
        assert dotdict.existing == "value"

    def test_setdefault_dot_notation_new(self) -> None:
        """Test setdefault with dot notation creates nested structure."""
        dotdict = DotDict()
        result = dotdict.setdefault("nested.key", "value")

        assert result == "value"
        assert isinstance(dotdict.nested, DotDict)
        assert dotdict.nested.key == "value"

    def test_setdefault_dot_notation_existing(self) -> None:
        """Test setdefault with existing dot notation path."""
        dotdict = DotDict({"nested": {"key": "existing_value"}})
        result = dotdict.setdefault("nested.key", "default_value")

        assert result == "existing_value"
        assert dotdict.nested.key == "existing_value"

    def test_setdefault_none_default(self) -> None:
        """Test setdefault with None as default value."""
        dotdict = DotDict()
        result = dotdict.setdefault("key", None)

        assert result is None
        assert dotdict.key is None

    def test_update_with_dict(self) -> None:
        """Test update method with dictionary."""
        dotdict = DotDict({"existing": "value"})
        dotdict.update({"new_key": "new_value", "existing": "updated"})

        assert dotdict.existing == "updated"
        assert dotdict.new_key == "new_value"

    def test_update_with_kwargs(self) -> None:
        """Test update method with keyword arguments."""
        dotdict = DotDict({"existing": "value"})
        dotdict.update(new_key="new_value", existing="updated")

        assert dotdict.existing == "updated"
        assert dotdict.new_key == "new_value"

    def test_update_with_dict_and_kwargs(self) -> None:
        """Test update method with both dict and kwargs."""
        dotdict = DotDict({"existing": "value"})
        dotdict.update({"dict_key": "dict_value"}, kwargs_key="kwargs_value")

        assert dotdict.existing == "value"
        assert dotdict.dict_key == "dict_value"
        assert dotdict.kwargs_key == "kwargs_value"

    def test_update_with_nested_dict(self) -> None:
        """Test update method with nested dictionary converts to DotDict."""
        dotdict = DotDict()
        dotdict.update({"nested": {"key": "value"}})

        assert isinstance(dotdict.nested, DotDict)
        assert dotdict.nested.key == "value"

    def test_update_none_other(self) -> None:
        """Test update method with None as other parameter."""
        dotdict = DotDict({"existing": "value"})
        dotdict.update(None, new_key="new_value")

        assert dotdict.existing == "value"
        assert dotdict.new_key == "new_value"


class TestDotDictConversionMethods:
    """Test cases for conversion and copying methods."""

    def test_to_dict_simple(self) -> None:
        """Test to_dict method with simple data."""
        data: Dict[str, Any] = {"foo": "bar", "number": 42}
        dotdict = DotDict(data)
        result = dotdict.to_dict()

        assert result == data
        assert isinstance(result, dict)
        assert not isinstance(result, DotDict)

    def test_to_dict_nested(self) -> None:
        """Test to_dict method with nested DotDict instances."""
        data: Dict[str, Any] = {"nested": {"key": "value", "deep": {"level": "data"}}}
        dotdict = DotDict(data)
        result = dotdict.to_dict()

        assert result == data
        assert isinstance(result["nested"], dict)
        assert not isinstance(result["nested"], DotDict)
        assert isinstance(result["nested"]["deep"], dict)
        assert not isinstance(result["nested"]["deep"], DotDict)

    def test_to_dict_mixed_types(self) -> None:
        """Test to_dict method preserves non-dict types."""
        data: Dict[str, Any] = {
            "string": "value",
            "number": 42,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "none": None,
        }
        dotdict = DotDict(data)
        result = dotdict.to_dict()

        assert result["string"] == "value"
        assert result["number"] == 42
        assert result["list"] == [1, 2, 3]
        assert isinstance(result["dict"], dict)
        assert not isinstance(result["dict"], DotDict)
        assert result["none"] is None

    def test_copy_shallow(self) -> None:
        """Test shallow copy method."""
        original = DotDict({"nested": {"key": "value"}})
        copied = original.copy()

        assert copied is not original
        assert isinstance(copied, DotDict)
        assert copied.nested.key == "value"
        # Nested objects are new DotDict instances due to initialization
        assert copied.nested is not original.nested

    def test_copy_independence(self) -> None:
        """Test that shallow copy creates independent top-level structure."""
        original = DotDict({"top": "value", "nested": {"key": "value"}})
        copied = original.copy()

        copied.top = "modified"
        copied.new_key = "new"

        assert original.top == "value"
        assert "new_key" not in original
        assert copied.top == "modified"
        assert copied.new_key == "new"

    def test_deepcopy_complete_independence(self) -> None:
        """Test deep copy method creates completely independent copy."""
        original = DotDict({"nested": {"key": "value"}})
        copied = original.deepcopy()

        assert copied is not original
        assert isinstance(copied, DotDict)
        assert copied.nested.key == "value"
        assert copied.nested is not original.nested

    def test_deepcopy_modification_independence(self) -> None:
        """Test that deep copy modifications don't affect original."""
        original = DotDict({"nested": {"key": "value", "list": [1, 2, 3]}})
        copied = original.deepcopy()

        copied.nested.key = "modified"
        copied.nested.list.append(4)

        assert original.nested.key == "value"
        assert original.nested.list == [1, 2, 3]
        assert copied.nested.key == "modified"
        assert copied.nested.list == [1, 2, 3, 4]


class TestDotDictInheritanceBehavior:
    """Test cases for dict inheritance behavior."""

    def test_dict_methods_available(self) -> None:
        """Test that standard dict methods are available."""
        dotdict = DotDict({"a": 1, "b": 2, "c": 3})

        assert len(dotdict) == 3
        assert "a" in dotdict
        assert "d" not in dotdict
        assert list(dotdict.keys()) == ["a", "b", "c"]
        assert list(dotdict.values()) == [1, 2, 3]
        assert list(dotdict.items()) == [("a", 1), ("b", 2), ("c", 3)]

    def test_dict_iteration(self) -> None:
        """Test that iteration works like standard dict."""
        dotdict = DotDict({"a": 1, "b": 2})
        keys = []

        for key in dotdict:
            keys.append(key)

        assert keys == ["a", "b"]

    def test_dict_bool_conversion(self) -> None:
        """Test boolean conversion behavior."""
        empty_dotdict = DotDict()
        filled_dotdict = DotDict({"key": "value"})

        assert not empty_dotdict
        assert bool(filled_dotdict)

    def test_dict_equality(self) -> None:
        """Test equality comparison with regular dicts."""
        dotdict = DotDict({"a": 1, "b": 2})
        regular_dict = {"a": 1, "b": 2}

        assert dotdict == regular_dict
        assert regular_dict == dotdict

    def test_dict_string_representation(self) -> None:
        """Test string representation includes DotDict type."""
        dotdict = DotDict({"a": 1})
        str_repr = str(dotdict)

        # Should contain the data, exact format may vary
        assert "a" in str_repr
        assert "1" in str_repr


class TestDotDictEdgeCases:
    """Test cases for edge cases and error conditions."""

    def test_empty_key_access(self) -> None:
        """Test behavior with empty string keys."""
        dotdict = DotDict()
        dotdict[""] = "empty_key_value"

        assert dotdict[""] == "empty_key_value"
        assert dotdict.get("") == "empty_key_value"

    def test_empty_dot_notation_raises_error(self) -> None:
        """Test that empty dot notation raises KeyError."""
        dotdict = DotDict({"key": "value"})

        with pytest.raises(KeyError):
            _ = dotdict[""]

    def test_dot_notation_with_empty_segments(self) -> None:
        """Test dot notation with empty segments raises appropriate errors."""
        dotdict = DotDict({"key": "value"})

        with pytest.raises(KeyError):
            _ = dotdict[".."]

        # This will raise TypeError because "value" is a string, not a dict
        with pytest.raises(TypeError):
            _ = dotdict["key..other"]

    def test_none_values(self) -> None:
        """Test handling of None values."""
        dotdict = DotDict()
        dotdict.none_value = None
        dotdict["none_key"] = None

        assert dotdict.none_value is None
        assert dotdict["none_key"] is None
        assert dotdict.get("none_value") is None

    def test_numeric_string_keys(self) -> None:
        """Test handling of numeric string keys."""
        dotdict = DotDict({"123": "numeric_key", "0": "zero"})

        assert dotdict["123"] == "numeric_key"
        assert dotdict["0"] == "zero"

    def test_special_character_keys(self) -> None:
        """Test handling of keys with special characters."""
        dotdict = DotDict(
            {"key-with-dashes": "value1", "key_with_underscores": "value2"}
        )

        assert dotdict["key-with-dashes"] == "value1"
        assert dotdict["key_with_underscores"] == "value2"

    def test_overwrite_dict_methods_as_attributes(self) -> None:
        """Test that dict method names can be used as keys."""
        dotdict = DotDict()
        dotdict["keys"] = "not_a_method"
        dotdict["items"] = "also_not_a_method"

        # Should be able to access as dictionary items
        assert dotdict["keys"] == "not_a_method"
        assert dotdict["items"] == "also_not_a_method"

        # Dict methods should still work
        assert "keys" in dotdict
        assert "items" in dotdict
        assert len(list(dotdict.keys())) == 2

    def test_complex_nested_operations(self) -> None:
        """Test complex nested operations and modifications."""
        dotdict = DotDict()

        # Create nested structure
        dotdict["a.b.c"] = "value1"
        dotdict["x.y.z"] = "value2"

        # Verify structure
        assert dotdict.a.b.c == "value1"
        assert dotdict.x.y.z == "value2"

        # Update nested values
        dotdict.a.b.c = "new_value1"
        dotdict["x.y.z"] = "new_value2"

        assert dotdict.a.b.c == "new_value1"
        assert dotdict.x.y.z == "new_value2"

        # Add to existing nested structure
        dotdict.a.b.d = "additional"
        dotdict["x.y.w"] = "more"

        assert dotdict.a.b.d == "additional"
        assert dotdict.x.y.w == "more"
        assert dotdict.a.b.c == "new_value1"  # Existing values preserved

    def test_attribute_error_message_format(self) -> None:
        """Test that AttributeError messages are properly formatted."""
        dotdict = DotDict({"existing": "value"})

        with pytest.raises(AttributeError) as exc_info:
            _ = dotdict.nonexistent

        error_message = str(exc_info.value)
        assert "'DotDict' object has no attribute 'nonexistent'" in error_message

    def test_key_error_propagation(self) -> None:
        """Test that KeyError is properly propagated for missing keys."""
        dotdict = DotDict({"nested": {"key": "value"}})

        # Simple missing key
        with pytest.raises(KeyError):
            _ = dotdict["missing"]

        # Missing in dot notation
        with pytest.raises(KeyError):
            _ = dotdict["nested.missing"]

        # Missing intermediate in dot notation
        with pytest.raises(KeyError):
            _ = dotdict["missing.key"]
