"""Unit tests for DotDict utility class."""

import copy
from typing import Any

import pytest

from honeyhive.utils.dotdict import DotDict


class TestDotDict:
    """Test cases for DotDict functionality."""

    def test_init_with_dict(self) -> None:
        """Test DotDict initialization with dictionary."""
        data = {"foo": "bar", "nested": {"key": "value"}}
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

    def test_init_with_multiple_args(self) -> None:
        """Test DotDict initialization with multiple arguments."""
        # DotDict doesn't support multiple dict arguments like regular dict
        # It only supports one dict argument plus kwargs
        dotdict = DotDict({"a": 1, "b": 2}, c=3)
        
        assert dotdict.a == 1
        assert dotdict.b == 2
        assert dotdict.c == 3

    def test_getattr_success(self) -> None:
        """Test successful attribute access."""
        dotdict = DotDict({"foo": "bar"})
        assert dotdict.foo == "bar"

    def test_getattr_missing(self) -> None:
        """Test attribute access for missing key."""
        dotdict = DotDict({"foo": "bar"})
        
        with pytest.raises(AttributeError, match="'DotDict' object has no attribute 'missing'"):
            _ = dotdict.missing

    def test_setattr_new_key(self) -> None:
        """Test setting new attribute."""
        dotdict = DotDict()
        dotdict.new_key = "new_value"
        
        assert dotdict.new_key == "new_value"
        assert dotdict["new_key"] == "new_value"

    def test_setattr_existing_key(self) -> None:
        """Test setting existing attribute."""
        dotdict = DotDict({"existing": "old_value"})
        dotdict.existing = "new_value"
        
        assert dotdict.existing == "new_value"

    def test_setattr_dict_value(self) -> None:
        """Test setting attribute with dict value."""
        dotdict = DotDict()
        dotdict.nested = {"key": "value"}
        
        assert isinstance(dotdict.nested, DotDict)
        assert dotdict.nested.key == "value"

    def test_delattr_success(self) -> None:
        """Test successful attribute deletion."""
        dotdict = DotDict({"foo": "bar"})
        del dotdict.foo
        
        assert "foo" not in dotdict

    def test_delattr_missing(self) -> None:
        """Test deletion of missing attribute."""
        dotdict = DotDict({"foo": "bar"})
        
        with pytest.raises(AttributeError, match="'DotDict' object has no attribute 'missing'"):
            del dotdict.missing

    def test_getitem_simple(self) -> None:
        """Test simple item access."""
        dotdict = DotDict({"foo": "bar"})
        assert dotdict["foo"] == "bar"

    def test_getitem_dot_notation(self) -> None:
        """Test item access with dot notation."""
        dotdict = DotDict({"nested": {"key": "value"}})
        assert dotdict["nested.key"] == "value"

    def test_getitem_deep_dot_notation(self) -> None:
        """Test deep dot notation access."""
        dotdict = DotDict({"level1": {"level2": {"level3": "value"}}})
        assert dotdict["level1.level2.level3"] == "value"

    def test_getitem_missing_key(self) -> None:
        """Test item access for missing key."""
        dotdict = DotDict({"foo": "bar"})
        
        with pytest.raises(KeyError):
            _ = dotdict["missing"]

    def test_getitem_missing_dot_notation(self) -> None:
        """Test item access for missing dot notation key."""
        dotdict = DotDict({"nested": {"key": "value"}})
        
        with pytest.raises(KeyError):
            _ = dotdict["nested.missing"]

    def test_setitem_simple(self) -> None:
        """Test simple item setting."""
        dotdict = DotDict()
        dotdict["foo"] = "bar"
        
        assert dotdict.foo == "bar"

    def test_setitem_dict_value(self) -> None:
        """Test setting item with dict value."""
        dotdict = DotDict()
        dotdict["nested"] = {"key": "value"}
        
        assert isinstance(dotdict.nested, DotDict)
        assert dotdict.nested.key == "value"

    def test_setitem_dot_notation(self) -> None:
        """Test setting item with dot notation."""
        dotdict = DotDict()
        dotdict["nested.key"] = "value"
        
        assert dotdict.nested.key == "value"

    def test_setitem_deep_dot_notation(self) -> None:
        """Test setting item with deep dot notation."""
        dotdict = DotDict()
        dotdict["level1.level2.level3"] = "value"
        
        assert dotdict.level1.level2.level3 == "value"

    def test_setitem_existing_dot_notation(self) -> None:
        """Test setting existing dot notation path."""
        dotdict = DotDict({"nested": {"key": "old_value"}})
        dotdict["nested.key"] = "new_value"
        
        assert dotdict.nested.key == "new_value"

    def test_get_with_default(self) -> None:
        """Test get method with default value."""
        dotdict = DotDict({"foo": "bar"})
        
        assert dotdict.get("foo") == "bar"
        assert dotdict.get("missing", "default") == "default"

    def test_get_with_dot_notation(self) -> None:
        """Test get method with dot notation."""
        dotdict = DotDict({"nested": {"key": "value"}})
        
        assert dotdict.get("nested.key") == "value"
        assert dotdict.get("nested.missing", "default") == "default"

    def test_get_with_missing_dot_notation(self) -> None:
        """Test get method with missing dot notation path."""
        dotdict = DotDict({"nested": {"key": "value"}})
        
        assert dotdict.get("missing.path", "default") == "default"

    def test_setdefault_new_key(self) -> None:
        """Test setdefault with new key."""
        dotdict = DotDict()
        result = dotdict.setdefault("new_key", "default_value")
        
        assert result == "default_value"
        assert dotdict.new_key == "default_value"

    def test_setdefault_existing_key(self) -> None:
        """Test setdefault with existing key."""
        dotdict = DotDict({"existing": "value"})
        result = dotdict.setdefault("existing", "default_value")
        
        assert result == "value"
        assert dotdict.existing == "value"

    def test_setdefault_dot_notation(self) -> None:
        """Test setdefault with dot notation."""
        dotdict = DotDict()
        result = dotdict.setdefault("nested.key", "value")
        
        assert result == "value"
        assert dotdict.nested.key == "value"

    def test_setdefault_existing_dot_notation(self) -> None:
        """Test setdefault with existing dot notation path."""
        dotdict = DotDict({"nested": {"key": "existing_value"}})
        result = dotdict.setdefault("nested.key", "default_value")
        
        assert result == "existing_value"
        assert dotdict.nested.key == "existing_value"

    def test_update_with_dict(self) -> None:
        """Test update method with dictionary."""
        dotdict = DotDict({"existing": "value"})
        dotdict.update({"new_key": "new_value"})
        
        assert dotdict.existing == "value"
        assert dotdict.new_key == "new_value"

    def test_update_with_kwargs(self) -> None:
        """Test update method with keyword arguments."""
        dotdict = DotDict({"existing": "value"})
        dotdict.update(new_key="new_value")
        
        assert dotdict.existing == "value"
        assert dotdict.new_key == "new_value"

    def test_update_with_dict_and_kwargs(self) -> None:
        """Test update method with both dict and kwargs."""
        dotdict = DotDict({"existing": "value"})
        dotdict.update({"dict_key": "dict_value"}, kwargs_key="kwargs_value")
        
        assert dotdict.existing == "value"
        assert dotdict.dict_key == "dict_value"
        assert dotdict.kwargs_key == "kwargs_value"

    def test_update_with_nested_dict(self) -> None:
        """Test update method with nested dictionary."""
        dotdict = DotDict()
        dotdict.update({"nested": {"key": "value"}})
        
        assert isinstance(dotdict.nested, DotDict)
        assert dotdict.nested.key == "value"

    def test_to_dict_simple(self) -> None:
        """Test to_dict method with simple data."""
        data = {"foo": "bar", "number": 42}
        dotdict = DotDict(data)
        result = dotdict.to_dict()
        
        assert result == data
        assert isinstance(result, dict)
        assert not isinstance(result, DotDict)

    def test_to_dict_nested(self) -> None:
        """Test to_dict method with nested data."""
        data = {"nested": {"key": "value", "deep": {"level": "data"}}}
        dotdict = DotDict(data)
        result = dotdict.to_dict()
        
        assert result == data
        assert isinstance(result["nested"], dict)
        assert not isinstance(result["nested"], DotDict)

    def test_copy_shallow(self) -> None:
        """Test shallow copy method."""
        original = DotDict({"nested": {"key": "value"}})
        copied = original.copy()
        
        assert copied is not original
        # The nested dict is converted to DotDict during initialization
        # so it's not the same object reference
        assert copied.nested is not original.nested
        assert copied.nested.key == "value"

    def test_deepcopy(self) -> None:
        """Test deep copy method."""
        original = DotDict({"nested": {"key": "value"}})
        copied = original.deepcopy()
        
        assert copied is not original
        assert copied.nested is not original.nested  # Deep copy
        assert copied.nested.key == "value"

    def test_inheritance_behavior(self) -> None:
        """Test that DotDict properly inherits from dict."""
        dotdict = DotDict({"a": 1, "b": 2})
        
        # Test dict methods
        assert len(dotdict) == 2
        assert "a" in dotdict
        assert list(dotdict.keys()) == ["a", "b"]
        assert list(dotdict.values()) == [1, 2]
        assert list(dotdict.items()) == [("a", 1), ("b", 2)]

    def test_nested_conversion(self) -> None:
        """Test that nested dictionaries are converted to DotDict."""
        data = {
            "level1": {
                "level2": {
                    "level3": "value"
                }
            }
        }
        dotdict = DotDict(data)
        
        assert isinstance(dotdict.level1, DotDict)
        assert isinstance(dotdict.level1.level2, DotDict)
        assert dotdict.level1.level2.level3 == "value"

    def test_complex_nested_operations(self) -> None:
        """Test complex nested operations."""
        dotdict = DotDict()
        
        # Set nested values
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
        
        # Delete nested values - use attribute deletion instead of item deletion
        del dotdict.a.b.c
        del dotdict.x.y.z
        
        with pytest.raises(AttributeError):
            _ = dotdict.a.b.c
        with pytest.raises(AttributeError):
            _ = dotdict.x.y.z

    def test_edge_cases(self) -> None:
        """Test edge cases and error conditions."""
        dotdict = DotDict()
        
        # Empty dot notation
        with pytest.raises(KeyError):
            _ = dotdict[""]
        
        # Dot notation with empty segments
        with pytest.raises(KeyError):
            _ = dotdict[".."]
        
        # Setting with empty key
        dotdict[""] = "empty_key_value"
        assert dotdict[""] == "empty_key_value"
        
        # Setting with None value
        dotdict.none_value = None
        assert dotdict.none_value is None
