from honeyhive import dotdict
import pytest

def test_basic_dotdict_access():
    dd = dotdict({"a": {"b": 1}})
    assert dd.a.b == 1

def test_nested_dotdict():
    dd = dotdict({
        "level1": {
            "level2": {
                "level3": "value"
            }
        }
    })
    assert dd.level1.level2.level3 == "value"

def test_dotdict_with_list():
    dd = dotdict({
        "elements": [1, 2, 3],
        "nested": {"elements": [4, 5, 6]}
    })
    print('dotdict', dd.elements)
    assert dd.elements == [1, 2, 3]
    assert dd.nested.elements == [4, 5, 6]

def test_dotdict_modification():
    dd = dotdict({"x": 1})
    dd.x = 2
    dd.y = 3
    assert dd.x == 2
    assert dd.y == 3

def test_dotdict_dict_methods():
    dd = dotdict({"a": 1, "b": 2})
    assert dd.keys() == {"a", "b"}
    assert dict(dd) == {"a": 1, "b": 2}
    assert "a" in dd

def test_dotdict_error_handling():
    dd = dotdict({})
    with pytest.raises(AttributeError):
        _ = dd.nonexistent

def test_dotdict_from_none():
    dd = dotdict(None)
    assert dd == {}

def test_dotdict_empty():
    dd = dotdict({})
    assert len(dd) == 0
