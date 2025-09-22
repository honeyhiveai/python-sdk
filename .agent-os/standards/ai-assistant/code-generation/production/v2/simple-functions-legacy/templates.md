# Simple Function Templates

**🎯 Copy-paste ready templates for basic function generation**

## 🏗️ **Simple Function Template**

```python
def simple_function(param: str) -> bool:
    """Check if parameter meets criteria.
    
    :param param: Input string to validate
    :type param: str
    :return: True if valid, False otherwise
    :rtype: bool
    :raises ValueError: When param is empty or None
    
    **Example:**
    
    .. code-block:: python
    
        result = simple_function("test")
        if result:
            print("Valid input")
    """
    if not param:
        raise ValueError("Parameter cannot be empty")
    
    return len(param) > 0
```

## 🔧 **Simple Function with Optional Parameters**

```python
def function_with_optional(
    required_param: str,
    *,
    optional_param: Optional[int] = None,
    flag_param: bool = False
) -> Dict[str, Any]:
    """Function with optional parameters using keyword-only pattern.
    
    :param required_param: Required string parameter
    :type required_param: str
    :param optional_param: Optional integer parameter
    :type optional_param: Optional[int]
    :param flag_param: Boolean flag parameter
    :type flag_param: bool
    :return: Result dictionary
    :rtype: Dict[str, Any]
    """
    result: Dict[str, Any] = {"input": required_param}
    
    if optional_param is not None:
        result["optional"] = optional_param
    
    if flag_param:
        result["flag_enabled"] = True
    
    return result
```

## 📋 **Simple Function Checklist**

**When generating simple functions:**

- [ ] **Single responsibility**: Function does one thing well
- [ ] **Clear naming**: Function name describes what it does
- [ ] **Type annotations**: All parameters and return type annotated
- [ ] **Docstring**: Complete Sphinx-compatible documentation
- [ ] **Error handling**: Appropriate validation and exceptions
- [ ] **Example**: Working code example in docstring

---

**📝 Next**: [complex-function-templates.md](complex-function-templates.md) - Templates for complex functions
