# Test Method Templates

**🎯 Copy-paste ready templates for test method generation**

## 🧪 **Simple Unit Test Template**

```python
def test_simple_function_success(self) -> None:
    """Test successful execution of simple function.
    
    This test verifies the basic functionality works as expected
    with valid input parameters.
    """
    # Arrange
    test_input: str = "valid_input"
    expected_result: bool = True
    
    # Act
    result: bool = simple_function(test_input)
    
    # Assert
    assert result == expected_result
```

## 🔧 **Test with Mock Fixtures Template**

```python
def test_function_with_tracer(self, mock_tracer: Mock) -> None:
    """Test function that uses tracer dependency.
    
    :param mock_tracer: Mock tracer instance from fixture
    :type mock_tracer: Mock
    """
    # Arrange
    test_data: Dict[str, str] = {"key": "value"}
    expected_result: Dict[str, Any] = {"processed": test_data}
    
    # Configure mock
    mock_tracer.trace.return_value.__enter__.return_value.set_attribute = Mock()
    
    # Act
    result: Dict[str, Any] = process_with_tracer(test_data, mock_tracer)
    
    # Assert
    assert result == expected_result
    mock_tracer.trace.assert_called_once_with("processing")
```

## 🎭 **Test with Multiple Mock Decorators Template**

```python
@patch('honeyhive.utils.logger.safe_log')
@patch('honeyhive.tracer.processing.context.some_function')
def test_function_with_multiple_mocks(
    self,
    mock_function: Mock,
    mock_log: Mock,
    mock_tracer: Mock
) -> None:
    """Test function with multiple mocked dependencies.
    
    Note: @patch decorators inject mocks as positional arguments in reverse order.
    
    :param mock_function: Mock target function
    :type mock_function: Mock
    :param mock_log: Mock logging function
    :type mock_log: Mock
    :param mock_tracer: Mock tracer fixture
    :type mock_tracer: Mock
    """
    # Arrange
    test_input: str = "test_value"
    expected_output: str = "processed_value"
    mock_function.return_value = expected_output
    
    # Act
    result: str = target_function(test_input, mock_tracer)
    
    # Assert
    assert result == expected_output
    mock_function.assert_called_once_with(test_input)
    mock_log.assert_not_called()
```

## 📋 **Test Method Checklist**

**When generating test methods:**

- [ ] **Clear naming**: Test name describes what is being tested
- [ ] **Complete docstring**: Describes test purpose and parameters
- [ ] **Type annotations**: All parameters and variables typed
- [ ] **Arrange-Act-Assert**: Clear test structure
- [ ] **Mock configuration**: Proper mock setup and verification
- [ ] **Assertions**: Verify expected behavior and calls

---

**📝 Next**: [mock-patterns.md](mock-patterns.md) - Mock configuration patterns
