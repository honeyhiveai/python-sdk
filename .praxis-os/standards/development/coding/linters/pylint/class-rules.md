# Pylint Class Rules

**🎯 Class-specific Pylint compliance for AI assistants**

## 🚨 **Critical Class Rules**

### **R0902: Too many instance attributes (>7)**

**Common class-related Pylint violation:**

```python
# ❌ VIOLATION - Too many instance attributes
class DataProcessor:
    def __init__(self):
        self.input_data = None
        self.output_data = None
        self.config = None
        self.logger = None
        self.cache = None
        self.metrics = None
        self.status = None
        self.error_handler = None  # 8th attribute - violation

# ✅ CORRECT - Group related attributes
class DataProcessor:
    def __init__(self, config: ProcessorConfig):
        self.config: ProcessorConfig = config
        self.state: ProcessorState = ProcessorState()
        self.services: ProcessorServices = ProcessorServices(config)
        self.metrics: ProcessorMetrics = ProcessorMetrics()
```

### **R0903: Too few public methods (<2)**

```python
# ❌ VIOLATION - Only one public method
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

# ✅ CORRECT - Either add methods or use function
class Calculator:
    """Calculator with multiple operations."""
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
    
    def subtract(self, a: int, b: int) -> int:
        """Subtract two numbers."""
        return a - b

# ✅ ALTERNATIVE - Use function instead of single-method class
def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

### **R0904: Too many public methods (>20)**

```python
# ❌ VIOLATION - Too many methods in one class
class MassiveService:
    def method1(self): pass
    def method2(self): pass
    # ... 25+ methods

# ✅ CORRECT - Split into focused classes
class UserService:
    """Handle user-related operations."""
    
    def create_user(self, user_data: UserData) -> User:
        """Create a new user."""
        pass
    
    def update_user(self, user_id: str, updates: UserUpdates) -> User:
        """Update existing user."""
        pass

class AuthService:
    """Handle authentication operations."""
    
    def authenticate(self, credentials: Credentials) -> AuthResult:
        """Authenticate user credentials."""
        pass
    
    def refresh_token(self, token: str) -> AuthResult:
        """Refresh authentication token."""
        pass
```

## 📋 **Class Design Patterns**

### **Pattern 1: Simple Data Class**

```python
class ProcessorConfig:
    """Configuration for data processor."""
    
    def __init__(
        self,
        *,
        batch_size: int = 100,
        timeout: int = 30,
        retries: int = 3,
        debug: bool = False
    ) -> None:
        """Initialize processor configuration.
        
        Args:
            batch_size: Number of items to process in each batch
            timeout: Processing timeout in seconds
            retries: Number of retry attempts
            debug: Enable debug logging
        """
        self.batch_size: int = batch_size
        self.timeout: int = timeout
        self.retries: int = retries
        self.debug: bool = debug
    
    def validate(self) -> None:
        """Validate configuration values.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.retries < 0:
            raise ValueError("retries must be non-negative")
```

### **Pattern 2: Service Class**

```python
class DataProcessor:
    """Process data with configurable options."""
    
    def __init__(self, config: ProcessorConfig) -> None:
        """Initialize data processor.
        
        Args:
            config: Processor configuration
        """
        self.config: ProcessorConfig = config
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._cache: Dict[str, Any] = {}
        self._metrics: ProcessorMetrics = ProcessorMetrics()
    
    def process_batch(self, items: List[DataItem]) -> List[ProcessedItem]:
        """Process a batch of data items.
        
        Args:
            items: Items to process
            
        Returns:
            List of processed items
            
        Raises:
            ProcessingError: If batch processing fails
        """
        if not items:
            return []
        
        try:
            results: List[ProcessedItem] = []
            for item in items:
                processed = self._process_single_item(item)
                results.append(processed)
            
            self._metrics.record_batch_processed(len(results))
            return results
        
        except Exception as e:
            self._logger.error(f"Batch processing failed: {e}")
            raise ProcessingError(f"Failed to process batch: {e}") from e
    
    def get_metrics(self) -> ProcessorMetrics:
        """Get processing metrics.
        
        Returns:
            Current processor metrics
        """
        return self._metrics
    
    def clear_cache(self) -> None:
        """Clear internal cache."""
        self._cache.clear()
        self._logger.debug("Cache cleared")
    
    def _process_single_item(self, item: DataItem) -> ProcessedItem:
        """Process a single data item.
        
        Args:
            item: Item to process
            
        Returns:
            Processed item
        """
        # Implementation details
        pass
```

### **Pattern 3: Context Manager Class**

```python
class DatabaseConnection:
    """Database connection with automatic cleanup."""
    
    def __init__(self, connection_string: str) -> None:
        """Initialize database connection.
        
        Args:
            connection_string: Database connection string
        """
        self.connection_string: str = connection_string
        self._connection: Optional[Connection] = None
        self._logger: logging.Logger = logging.getLogger(__name__)
    
    def __enter__(self) -> 'DatabaseConnection':
        """Enter context manager."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager."""
        self.disconnect()
    
    def connect(self) -> None:
        """Establish database connection."""
        try:
            self._connection = create_connection(self.connection_string)
            self._logger.info("Database connection established")
        except Exception as e:
            self._logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            self._logger.info("Database connection closed")
    
    def execute_query(self, query: str) -> QueryResult:
        """Execute database query.
        
        Args:
            query: SQL query to execute
            
        Returns:
            Query results
            
        Raises:
            ConnectionError: If not connected to database
        """
        if not self._connection:
            raise ConnectionError("Not connected to database")
        
        return self._connection.execute(query)
```

## 🚨 **Class Violations to Avoid**

### **C0103: Invalid class name**

```python
# ❌ VIOLATION - Invalid naming
class dataProcessor:  # Should be PascalCase
    pass

class data_processor:  # Should be PascalCase
    pass

# ✅ CORRECT - PascalCase naming
class DataProcessor:
    pass
```

### **W0613: Unused argument in method**

```python
# ❌ VIOLATION - Unused parameter
class Processor:
    def process(self, data, unused_param):
        return data.transform()

# ✅ CORRECT - Remove unused parameter
class Processor:
    def process(self, data):
        return data.transform()
```

### **R0201: Method could be a function**

```python
# ❌ VIOLATION - Method doesn't use self
class Utilities:
    def format_string(self, text):
        return text.upper()

# ✅ CORRECT - Make it a function or use self
def format_string(text: str) -> str:
    """Format string to uppercase."""
    return text.upper()

# ✅ ALTERNATIVE - Use instance state
class Formatter:
    def __init__(self, case_style: str):
        self.case_style = case_style
    
    def format_string(self, text: str) -> str:
        """Format string according to case style."""
        if self.case_style == 'upper':
            return text.upper()
        elif self.case_style == 'lower':
            return text.lower()
        return text
```

## 📋 **Class Checklist**

**Before generating ANY class, verify:**

- [ ] **≤7 instance attributes**: Group related attributes into objects
- [ ] **≥2 public methods**: Or use function instead of single-method class
- [ ] **≤20 public methods**: Split large classes into focused ones
- [ ] **PascalCase naming**: Class names use PascalCase convention
- [ ] **Proper docstring**: Class purpose and usage documented
- [ ] **All methods use self**: Or make them functions/static methods
- [ ] **Single responsibility**: Class has one clear purpose
- [ ] **Proper initialization**: `__init__` method with type annotations

---

**🎯 Remember**: Well-designed classes are focused, cohesive, and have clear responsibilities.
