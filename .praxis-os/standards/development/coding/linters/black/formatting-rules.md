# Black Formatting Rules

**🎯 Black code formatting requirements for consistent code style**

## 🚨 **Critical Black Rules**

### **Line Length: 88 Characters Maximum**

```python
# ❌ BLACK VIOLATION - Line too long (>88 characters)
def very_long_function_name_that_exceeds_the_line_limit(parameter_one, parameter_two, parameter_three, parameter_four):
    pass

# ✅ BLACK COMPLIANT - Properly formatted
def very_long_function_name_that_exceeds_the_line_limit(
    parameter_one: str,
    parameter_two: int,
    parameter_three: bool,
    parameter_four: Optional[Config]
) -> None:
    pass
```

### **String Quotes: Consistent Usage**

```python
# ❌ BLACK VIOLATION - Inconsistent quotes
message = 'Hello world'
error = "Something went wrong"
config = 'debug=true'

# ✅ BLACK COMPLIANT - Consistent double quotes
message = "Hello world"
error = "Something went wrong"
config = "debug=true"

# ✅ EXCEPTION - Use single quotes to avoid escaping
text_with_quotes = 'He said "Hello world" to me'
```

### **Trailing Commas: Required in Multi-line Structures**

```python
# ❌ BLACK VIOLATION - Missing trailing comma
items = [
    "first",
    "second",
    "third"  # Missing comma
]

# ✅ BLACK COMPLIANT - Trailing comma present
items = [
    "first",
    "second",
    "third",  # Trailing comma
]
```

## 📋 **Black Formatting Patterns**

### **Pattern 1: Function Definitions**

```python
# Short function - single line
def add(a: int, b: int) -> int:
    return a + b

# Long function - multi-line parameters
def process_data_with_comprehensive_configuration(
    input_data: List[DataItem],
    processing_config: ProcessingConfig,
    *,
    timeout: int = 30,
    retries: int = 3,
    verbose: bool = False,
    callback: Optional[Callable[[ProcessResult], None]] = None,
) -> ProcessResult:
    """Process data with comprehensive configuration options."""
    pass
```

### **Pattern 2: Function Calls**

```python
# Short call - single line
result = process_item(data, config)

# Long call - multi-line arguments
result = process_data_with_comprehensive_configuration(
    input_data=data_items,
    processing_config=config,
    timeout=60,
    retries=5,
    verbose=True,
    callback=handle_result,
)
```

### **Pattern 3: Collections**

```python
# Short list - single line
items = ["apple", "banana", "cherry"]

# Long list - multi-line with trailing comma
items = [
    "apple",
    "banana", 
    "cherry",
    "date",
    "elderberry",
]

# Dictionary - multi-line formatting
config = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "test_db",
    },
    "cache": {
        "enabled": True,
        "ttl": 3600,
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    },
}
```

### **Pattern 4: Class Definitions**

```python
# Simple class
class DataItem:
    """Simple data item."""
    
    def __init__(self, id: str, value: str) -> None:
        self.id = id
        self.value = value

# Complex class with long inheritance
class ComplexDataProcessorWithMultipleCapabilities(
    BaseProcessor,
    CacheableMixin,
    LoggableMixin,
    ConfigurableMixin,
):
    """Complex data processor with multiple capabilities."""
    
    def __init__(
        self,
        config: ProcessorConfig,
        *,
        cache_enabled: bool = True,
        log_level: str = "INFO",
        max_workers: int = 4,
    ) -> None:
        super().__init__(config)
        self.cache_enabled = cache_enabled
        self.log_level = log_level
        self.max_workers = max_workers
```

## 🚨 **Black Violations to Avoid**

### **Violation 1: Manual Line Breaking**

```python
# ❌ BLACK VIOLATION - Manual line breaking
result = some_function(param1, param2, \
                      param3, param4)

# ✅ BLACK COMPLIANT - Let Black handle formatting
result = some_function(param1, param2, param3, param4)
# Black will automatically format this if it's too long
```

### **Violation 2: Inconsistent Spacing**

```python
# ❌ BLACK VIOLATION - Inconsistent spacing
def function(a,b,c):
    result=a+b*c
    return result

# ✅ BLACK COMPLIANT - Consistent spacing
def function(a, b, c):
    result = a + b * c
    return result
```

### **Violation 3: Incorrect Bracket Formatting**

```python
# ❌ BLACK VIOLATION - Incorrect bracket formatting
items = [ "first", "second", "third" ]
config = { "key": "value", "number": 42 }

# ✅ BLACK COMPLIANT - Correct bracket formatting
items = ["first", "second", "third"]
config = {"key": "value", "number": 42}
```

## 📋 **Black Configuration**

### **Project Configuration (pyproject.toml)**

```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
```

### **Running Black**

```bash
# Format single file
black tests/unit/test_file.py

# Format entire directory
black src/

# Check formatting without making changes
black --check tests/unit/test_file.py

# Show diff of what would be changed
black --diff tests/unit/test_file.py
```

## 📋 **Black Integration Patterns**

### **Pattern 1: Pre-commit Integration**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11
```

### **Pattern 2: IDE Integration**

```json
// VS Code settings.json
{
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "editor.formatOnSave": true
}
```

### **Pattern 3: Tox Integration**

```ini
# tox.ini
[testenv:format]
deps = black
commands = black src/ tests/
```

## 📋 **Black Best Practices**

### **Practice 1: Let Black Handle Formatting**

```python
# Don't fight Black - write code naturally
def process_items(items, config, timeout=30, retries=3, verbose=False):
    # Black will format this properly
    pass

# Black output:
def process_items(
    items, config, *, timeout=30, retries=3, verbose=False
):
    pass
```

### **Practice 2: Use Black-Compatible Patterns**

```python
# Write code that Black formats nicely
data = {
    "users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ],
    "config": {
        "timeout": 30,
        "retries": 3,
    },
}
```

### **Practice 3: Combine with isort**

```bash
# Format imports first, then code
isort tests/unit/test_file.py
black tests/unit/test_file.py
```

## 📋 **Black Checklist**

**Before committing code, verify:**

- [ ] **Black formatting applied**: Run `black filename.py`
- [ ] **Line length ≤88**: No lines exceed 88 characters
- [ ] **Consistent quotes**: Prefer double quotes
- [ ] **Trailing commas**: Present in multi-line structures
- [ ] **Proper spacing**: Consistent spacing around operators
- [ ] **No manual line breaks**: Let Black handle line breaking
- [ ] **Clean brackets**: No extra spaces inside brackets

## ⚡ **Quick Black Fixes**

### **Auto-format File**
```bash
black tests/unit/test_file.py
```

### **Check Formatting**
```bash
black --check tests/unit/test_file.py
```

### **See What Would Change**
```bash
black --diff tests/unit/test_file.py
```

## 🎯 **Black Philosophy**

**Black's approach:**
- **Consistency over personal preference**
- **Minimal configuration options**
- **Automatic formatting decisions**
- **Focus on code content, not style**

**Benefits:**
- **No style debates**: Black decides formatting
- **Consistent codebase**: All code looks the same
- **Faster reviews**: No formatting discussions
- **Automatic compliance**: Run Black and you're compliant

---

**🎯 Remember**: Don't fight Black's formatting decisions. Trust the tool and focus on code logic.
