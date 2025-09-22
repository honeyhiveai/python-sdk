# Pylint Test Rules

**🎯 Test-specific Pylint compliance for AI assistants**

## 🚨 **Critical Test Rules**

### **C0103: Invalid name (test methods)**

**Common test naming violations:**

```python
# ❌ VIOLATION - Invalid test method names
class TestProcessor:
    def testBasicProcessing(self):  # Should be snake_case
        pass
    
    def test_Process_Data(self):  # Mixed case
        pass
    
    def TestDataValidation(self):  # Missing test_ prefix
        pass

# ✅ CORRECT - Proper test naming
class TestProcessor:
    def test_basic_processing(self):
        """Test basic data processing functionality."""
        pass
    
    def test_process_data_with_config(self):
        """Test data processing with custom configuration."""
        pass
    
    def test_data_validation_with_invalid_input(self):
        """Test data validation handles invalid input correctly."""
        pass
```

### **W0621: Redefining name from outer scope (fixtures)**

```python
# ❌ VIOLATION - Fixture name shadows outer scope
items = ["global", "items"]

class TestProcessor:
    def test_processing(self, items):  # Shadows global 'items'
        pass

# ✅ CORRECT - Use descriptive fixture names
items = ["global", "items"]

class TestProcessor:
    def test_processing(self, test_items):
        """Test processing with test items."""
        pass
```

### **R0913: Too many arguments (test methods)**

```python
# ❌ VIOLATION - Too many test method arguments
def test_complex_scenario(
    self, mock_tracer, mock_exporter, mock_config, 
    mock_logger, mock_session, test_data
):
    pass

# ✅ CORRECT - Group related fixtures
@pytest.fixture
def mock_tracer_setup(mock_tracer, mock_exporter, mock_config):
    """Setup complete tracer with dependencies."""
    return TracerSetup(mock_tracer, mock_exporter, mock_config)

def test_complex_scenario(self, mock_tracer_setup, test_data):
    """Test complex scenario with grouped fixtures."""
    pass
```

## 📋 **Test Method Patterns**

### **Pattern 1: Simple Test Method**

```python
def test_process_single_item(self, mock_processor: Mock) -> None:
    """Test processing a single data item.
    
    Verifies that the processor correctly handles a single item
    and returns the expected result.
    """
    # Arrange
    test_item: DataItem = DataItem(id="test-123", value="test-data")
    expected_result: ProcessedItem = ProcessedItem(id="test-123", processed=True)
    
    with patch.object(mock_processor, 'process', return_value=expected_result):
        # Act
        result: ProcessedItem = function_under_test(mock_processor, test_item)
        
        # Assert
        assert result.id == "test-123"
        assert result.processed is True
```

### **Pattern 2: Exception Testing**

```python
def test_process_item_handles_invalid_input(self, mock_processor: Mock) -> None:
    """Test that processing handles invalid input gracefully.
    
    Verifies that appropriate exceptions are raised when
    invalid input is provided to the processor.
    """
    # Arrange
    invalid_item: DataItem = DataItem(id="", value=None)
    test_error = ValueError("Invalid item data")
    
    with patch.object(mock_processor, 'process', side_effect=test_error):
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid item data"):
            function_under_test(mock_processor, invalid_item)
```

### **Pattern 3: Parametrized Test**

```python
@pytest.mark.parametrize("input_value,expected_output", [
    ("test", "TEST"),
    ("hello", "HELLO"),
    ("", ""),
    ("123", "123"),
])
def test_string_transformation(
    self, 
    input_value: str, 
    expected_output: str,
    mock_transformer: Mock
) -> None:
    """Test string transformation with various inputs.
    
    Args:
        input_value: Input string to transform
        expected_output: Expected transformation result
        mock_transformer: Mock transformer object
    """
    # Arrange
    with patch.object(mock_transformer, 'transform', return_value=expected_output):
        # Act
        result: str = function_under_test(mock_transformer, input_value)
        
        # Assert
        assert result == expected_output
```

## 🚨 **Test Violations to Avoid**

### **🚨 MOST COMMON: W0613 Unused Mock Arguments**

**AI assistants frequently create mock parameters they never use**

```python
# ❌ VIOLATION - Mock parameter not used
@patch('honeyhive.utils.logger.safe_log')
def test_processor_initialization(self, mock_safe_log: Mock) -> None:
    """Test processor initialization."""
    processor = HoneyHiveSpanProcessor()
    assert processor.mode == "otlp"
    # mock_safe_log never used - Pylint W0613

# ✅ CORRECT - Either use the mock or remove it
@patch('honeyhive.utils.logger.safe_log')
def test_processor_initialization(self, mock_safe_log: Mock) -> None:
    """Test processor initialization with logging verification."""
    processor = HoneyHiveSpanProcessor()
    assert processor.mode == "otlp"
    mock_safe_log.assert_called()  # Now mock is used

# ✅ ALTERNATIVE - Use underscore prefix if mock needed for patching only
@patch('honeyhive.utils.logger.safe_log')
def test_processor_initialization(self, _mock_safe_log: Mock) -> None:
    """Test processor initialization (logging patched but not verified)."""
    processor = HoneyHiveSpanProcessor()
    assert processor.mode == "otlp"
    # Mock patches the method but we don't verify calls
```

### **🚨 COMMON: C1803 Explicit Empty Comparisons**

**AI assistants often use explicit comparisons instead of implicit booleanness**

```python
# ❌ VIOLATION - Explicit empty comparison
def test_empty_attributes(self) -> None:
    result = processor.get_attributes()
    assert result == {}  # Pylint C1803

# ✅ CORRECT - Use implicit booleanness
def test_empty_attributes(self) -> None:
    result = processor.get_attributes()
    assert not result  # Clean and Pythonic
```

### **🚨 COMMON: W0108 Unnecessary Lambda in Mocks**

```python
# ❌ VIOLATION - Unnecessary lambda wrapper
def test_baggage_side_effect(self) -> None:
    baggage_data = {"session_id": "test-123", "project": "test-proj"}
    mock_get_baggage.side_effect = lambda key, ctx: baggage_data.get(key)

# ✅ CORRECT - Direct method reference
def test_baggage_side_effect(self) -> None:
    baggage_data = {"session_id": "test-123", "project": "test-proj"}
    mock_get_baggage.side_effect = baggage_data.get
```

### **W0212: Access to a protected member**

```python
# ❌ VIOLATION - Accessing private members in tests
def test_internal_state(self, processor):
    processor._internal_cache = {}  # Accessing private member
    assert processor._process_count == 0

# ✅ CORRECT - Test through public interface
def test_cache_behavior(self, processor):
    """Test cache behavior through public methods."""
    processor.clear_cache()  # Public method
    result = processor.get_cache_stats()  # Public method
    assert result.size == 0
```

### **R0915: Too many statements (long test methods)**

```python
# ❌ VIOLATION - Test method too long
def test_massive_scenario(self):
    # 60+ statements testing everything
    setup_step_1()
    setup_step_2()
    # ... many more setup steps
    assert_result_1()
    assert_result_2()
    # ... many more assertions

# ✅ CORRECT - Break into focused test methods
def test_scenario_setup(self):
    """Test scenario setup phase."""
    result = setup_scenario()
    assert result.is_ready is True

def test_scenario_execution(self, setup_scenario):
    """Test scenario execution phase."""
    result = execute_scenario(setup_scenario)
    assert result.success is True

def test_scenario_cleanup(self, executed_scenario):
    """Test scenario cleanup phase."""
    cleanup_result = cleanup_scenario(executed_scenario)
    assert cleanup_result.cleaned is True
```

### **C0116: Missing function or method docstring**

```python
# ❌ VIOLATION - No docstring
def test_data_processing(self, mock_processor):
    result = mock_processor.process("test")
    assert result == "processed"

# ✅ CORRECT - Descriptive docstring
def test_data_processing(self, mock_processor: Mock) -> None:
    """Test that data processing returns expected result.
    
    Verifies that the processor correctly processes input data
    and returns the expected processed result.
    """
    # Arrange
    test_input: str = "test"
    expected_output: str = "processed"
    
    with patch.object(mock_processor, 'process', return_value=expected_output):
        # Act
        result: str = mock_processor.process(test_input)
        
        # Assert
        assert result == expected_output
```

## 📋 **Test Class Patterns**

### **Pattern 1: Simple Test Class**

```python
class TestDataProcessor:
    """Test suite for DataProcessor class."""
    
    def test_initialization(self) -> None:
        """Test DataProcessor initialization."""
        config = ProcessorConfig(batch_size=50)
        processor = DataProcessor(config)
        
        assert processor.config.batch_size == 50
        assert processor.is_ready is True
    
    def test_process_empty_batch(self, mock_processor: Mock) -> None:
        """Test processing empty batch returns empty result."""
        # Arrange
        empty_batch: List[DataItem] = []
        
        # Act
        result: List[ProcessedItem] = mock_processor.process_batch(empty_batch)
        
        # Assert
        assert result == []
        assert len(result) == 0
```

### **Pattern 2: Test Class with Setup/Teardown**

```python
class TestDatabaseConnection:
    """Test suite for DatabaseConnection class."""
    
    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.connection_string: str = "sqlite:///:memory:"
        self.test_config: ConnectionConfig = ConnectionConfig(
            host="localhost",
            port=5432,
            database="test_db"
        )
    
    def teardown_method(self) -> None:
        """Clean up after each test method."""
        # Cleanup code here
        pass
    
    def test_connection_establishment(self) -> None:
        """Test database connection can be established."""
        with DatabaseConnection(self.connection_string) as conn:
            assert conn.is_connected is True
    
    def test_connection_cleanup(self) -> None:
        """Test database connection is properly cleaned up."""
        conn = DatabaseConnection(self.connection_string)
        conn.connect()
        conn.disconnect()
        
        assert conn.is_connected is False
```

## 📋 **Test Checklist**

**Before generating ANY test method, verify:**

- [ ] **snake_case naming**: All test methods use snake_case
- [ ] **test_ prefix**: All test methods start with "test_"
- [ ] **Descriptive names**: Test names describe what is being tested
- [ ] **Proper docstring**: Explains what the test verifies
- [ ] **Type annotations**: All parameters and variables typed
- [ ] **≤50 statements**: Break long tests into smaller focused tests
- [ ] **No private access**: Test through public interfaces only
- [ ] **Clear AAA structure**: Arrange, Act, Assert sections
- [ ] **Unique fixture names**: Avoid shadowing outer scope variables

## ⚡ **Test Quick Fixes**

### **Fix Test Naming**
```python
# Change testSomething to test_something
# Change TestSomething to test_something (for methods)
```

### **Add Test Docstrings**
```python
def test_method(self) -> None:
    """Test that method does what it should do.
    
    Verifies specific behavior and expected outcomes.
    """
```

### **Break Long Tests**
```python
# Split one long test into multiple focused tests
# Each test should verify one specific behavior
```

---

**🎯 Remember**: Good tests are focused, well-named, and test one thing at a time.
