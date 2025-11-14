# Pylint Function Rules

**🎯 Function-specific Pylint compliance for AI assistants**

## 🚨 **Critical Function Rules**

### **R0917: Too many positional arguments (>5)**

**Most common function-related Pylint violation:**

```python
# ❌ VIOLATION - 6 positional arguments
def process_data(data, config, options, timeout, retries, verbose):
    pass

# ✅ CORRECT - Use keyword-only arguments after 5th
def process_data(data, config, options, timeout, *, retries=3, verbose=False):
    pass

# ✅ BETTER - Use keyword-only after 3rd for readability
def process_data(data, config, *, options=None, timeout=30, retries=3, verbose=False):
    pass
```

### **R0913: Too many arguments (>5 total)**

```python
# ❌ VIOLATION - Too many total arguments
def configure_system(host, port, username, password, timeout, retries, ssl, debug):
    pass

# ✅ CORRECT - Group related parameters
def configure_system(connection_config: ConnectionConfig, *, timeout=30, debug=False):
    pass
```

### **R0915: Too many statements (>50)**

```python
# ❌ VIOLATION - Function too long
def massive_function():
    # 60+ statements here
    statement1()
    statement2()
    # ... many more statements
    statement60()

# ✅ CORRECT - Break into smaller functions
def process_data():
    """Main processing function."""
    data = _prepare_data()
    results = _transform_data(data)
    _save_results(results)

def _prepare_data():
    """Prepare data for processing."""
    # Focused preparation logic
    pass

def _transform_data(data):
    """Transform prepared data."""
    # Focused transformation logic
    pass
```

## 📋 **Function Design Patterns**

### **Pattern 1: Simple Function**

```python
def process_item(item: Item, *, config: Optional[Config] = None) -> ProcessedItem:
    """Process a single item with optional configuration.
    
    Args:
        item: The item to process
        config: Optional processing configuration
        
    Returns:
        The processed item
        
    Raises:
        ProcessingError: If item cannot be processed
    """
    if config is None:
        config = Config()
    
    try:
        result: ProcessedItem = transform_item(item, config)
        return result
    except Exception as e:
        raise ProcessingError(f"Failed to process item: {e}") from e
```

### **Pattern 2: Complex Function with Keyword-Only Args**

```python
def create_connection(
    host: str,
    port: int,
    *,
    username: Optional[str] = None,
    password: Optional[str] = None,
    timeout: int = 30,
    ssl_enabled: bool = True,
    retries: int = 3,
    debug: bool = False
) -> Connection:
    """Create a network connection with comprehensive options.
    
    Args:
        host: Target host address
        port: Target port number
        username: Optional authentication username
        password: Optional authentication password
        timeout: Connection timeout in seconds
        ssl_enabled: Whether to use SSL/TLS
        retries: Number of retry attempts
        debug: Enable debug logging
        
    Returns:
        Configured connection object
    """
    config = ConnectionConfig(
        host=host,
        port=port,
        username=username,
        password=password,
        timeout=timeout,
        ssl_enabled=ssl_enabled,
        retries=retries,
        debug=debug
    )
    
    return Connection(config)
```

### **Pattern 3: Function with Error Handling**

```python
def safe_file_operation(
    filepath: str,
    operation: str,
    *,
    backup: bool = True,
    timeout: Optional[int] = None
) -> OperationResult:
    """Safely perform file operation with error handling.
    
    Args:
        filepath: Path to target file
        operation: Operation to perform ('read', 'write', 'delete')
        backup: Whether to create backup before operation
        timeout: Optional operation timeout
        
    Returns:
        Result of the operation
        
    Raises:
        FileOperationError: If operation fails
        TimeoutError: If operation times out
    """
    if not os.path.exists(filepath):
        raise FileOperationError(f"File not found: {filepath}")
    
    if backup and operation in ('write', 'delete'):
        _create_backup(filepath)
    
    try:
        if timeout:
            result = _execute_with_timeout(operation, filepath, timeout)
        else:
            result = _execute_operation(operation, filepath)
        
        return OperationResult(success=True, result=result)
    
    except TimeoutError:
        raise
    except Exception as e:
        return OperationResult(
            success=False,
            error=f"Operation failed: {e}"
        )
```

## 🚨 **Function Violations to Avoid**

### **R0912: Too many branches (>12)**

```python
# ❌ VIOLATION - Too many if/elif branches
def process_status(status):
    if status == 'pending':
        return handle_pending()
    elif status == 'processing':
        return handle_processing()
    elif status == 'completed':
        return handle_completed()
    # ... 10+ more elif branches

# ✅ CORRECT - Use dictionary mapping or strategy pattern
STATUS_HANDLERS = {
    'pending': handle_pending,
    'processing': handle_processing,
    'completed': handle_completed,
    # ... more handlers
}

def process_status(status: str) -> ProcessResult:
    """Process status using handler mapping."""
    handler = STATUS_HANDLERS.get(status)
    if handler is None:
        raise ValueError(f"Unknown status: {status}")
    
    return handler()
```

### **R0911: Too many return statements (>6)**

```python
# ❌ VIOLATION - Too many return points
def validate_data(data):
    if not data:
        return False
    if not data.get('id'):
        return False
    if not data.get('name'):
        return False
    # ... 8+ more return statements

# ✅ CORRECT - Single return point with validation logic
def validate_data(data: Dict[str, Any]) -> bool:
    """Validate data dictionary."""
    required_fields = ['id', 'name', 'email', 'status']
    
    if not data:
        return False
    
    missing_fields = [field for field in required_fields if not data.get(field)]
    return len(missing_fields) == 0
```

## 📋 **Function Checklist**

**Before generating ANY function, verify:**

- [ ] **≤5 positional arguments**: Use `*,` for keyword-only after 5th
- [ ] **≤50 statements**: Break large functions into smaller ones
- [ ] **≤12 branches**: Use mapping or strategy pattern for complex branching
- [ ] **≤6 return statements**: Prefer single return point when possible
- [ ] **Proper docstring**: Include Args, Returns, Raises sections
- [ ] **Type annotations**: All parameters and return value typed
- [ ] **Error handling**: Appropriate exception handling
- [ ] **Single responsibility**: Function does one thing well

---

**🎯 Remember**: Well-designed functions are short, focused, and have clear interfaces.
