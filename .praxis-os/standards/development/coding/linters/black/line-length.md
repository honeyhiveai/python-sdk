# Black Line Length Management

**🎯 Managing line length within Black's 88-character limit**

## 🚨 **Critical Line Length Rules**

### **88 Characters Maximum**

```python
# ❌ VIOLATION - Line exceeds 88 characters
def very_long_function_name_with_many_parameters(param1, param2, param3, param4, param5, param6):
    pass

# ✅ CORRECT - Black will format to multiple lines
def very_long_function_name_with_many_parameters(
    param1, param2, param3, param4, param5, param6
):
    pass
```

### **Let Black Handle Line Breaking**

```python
# ❌ DON'T - Manual line breaking
result = some_very_long_function_name(parameter_one, parameter_two, \
                                     parameter_three, parameter_four)

# ✅ DO - Write naturally, let Black format
result = some_very_long_function_name(
    parameter_one, parameter_two, parameter_three, parameter_four
)
```

## 📋 **Line Length Patterns**

### **Pattern 1: Function Definitions**

```python
# Short function - stays on one line
def add(a: int, b: int) -> int:
    return a + b

# Medium function - Black breaks at parameters
def process_data(data: List[str], config: Config, timeout: int = 30) -> ProcessResult:
    pass

# Long function - Black breaks and aligns
def process_data_with_comprehensive_options(
    input_data: List[DataItem],
    processing_config: ProcessingConfig,
    *,
    timeout: int = 30,
    retries: int = 3,
    verbose: bool = False,
) -> ProcessResult:
    pass
```

### **Pattern 2: Function Calls**

```python
# Short call - single line
result = process(data)

# Medium call - Black may break
result = process_data_with_config(
    data_items, processing_config, timeout=60
)

# Long call - Black breaks and indents
result = process_data_with_comprehensive_options(
    input_data=large_dataset,
    processing_config=complex_config,
    timeout=120,
    retries=5,
    verbose=True,
)
```

### **Pattern 3: String Literals**

```python
# Short string - single line
message = "Processing completed successfully"

# Long string - use parentheses for concatenation
long_message = (
    "This is a very long message that exceeds the line length limit "
    "and needs to be broken into multiple parts for readability"
)

# Multi-line string - use triple quotes
sql_query = """
    SELECT users.id, users.name, profiles.email
    FROM users
    JOIN profiles ON users.id = profiles.user_id
    WHERE users.active = true
    ORDER BY users.created_at DESC
"""

# Format string - break at logical points
formatted_message = (
    f"Processing {len(items)} items with config {config.name} "
    f"(timeout: {config.timeout}s, retries: {config.retries})"
)
```

### **Pattern 4: Collections**

```python
# Short list - single line
items = ["apple", "banana", "cherry"]

# Medium list - Black decides formatting
items = [
    "apple", "banana", "cherry", "date", "elderberry"
]

# Long list - Black formats with trailing comma
long_list_of_configuration_options = [
    "enable_caching",
    "enable_logging", 
    "enable_metrics",
    "enable_tracing",
    "enable_debugging",
    "enable_profiling",
]

# Dictionary - Black formats consistently
configuration = {
    "database": {"host": "localhost", "port": 5432},
    "cache": {"enabled": True, "ttl": 3600},
    "logging": {"level": "INFO", "format": "%(message)s"},
}
```

## 🚨 **Line Length Strategies**

### **Strategy 1: Use Shorter Names**

```python
# ❌ LONG - Verbose names cause line length issues
def process_user_authentication_with_comprehensive_validation(
    user_authentication_credentials: UserAuthenticationCredentials,
    authentication_configuration: AuthenticationConfiguration,
) -> UserAuthenticationResult:
    pass

# ✅ SHORTER - Concise but clear names
def authenticate_user(
    credentials: AuthCredentials,
    config: AuthConfig,
) -> AuthResult:
    pass
```

### **Strategy 2: Extract Variables**

```python
# ❌ LONG - Complex expression on one line
result = complex_processing_function(
    data.get_items_with_filter(lambda x: x.status == "active" and x.priority > 5),
    config.get_processing_options_for_priority_items(),
)

# ✅ SHORTER - Extract to variables
active_priority_items = data.get_items_with_filter(
    lambda x: x.status == "active" and x.priority > 5
)
priority_options = config.get_processing_options_for_priority_items()
result = complex_processing_function(active_priority_items, priority_options)
```

### **Strategy 3: Use Keyword Arguments**

```python
# ❌ LONG - Many positional arguments
result = create_connection("localhost", 5432, "mydb", "user", "pass", 30, True, False)

# ✅ SHORTER - Keyword arguments with line breaks
result = create_connection(
    host="localhost",
    port=5432,
    database="mydb",
    username="user",
    password="pass",
    timeout=30,
    ssl_enabled=True,
    debug=False,
)
```

## 📋 **Black Line Breaking Rules**

### **Rule 1: Function Parameters**

```python
# Black breaks after opening parenthesis if too long
def function_with_many_parameters(
    param1: str,
    param2: int,
    param3: bool,
    *,
    optional_param: Optional[str] = None,
) -> ReturnType:
    pass
```

### **Rule 2: Function Arguments**

```python
# Black breaks function calls similarly
result = function_with_many_parameters(
    "string_value",
    42,
    True,
    optional_param="optional_value",
)
```

### **Rule 3: Collection Items**

```python
# Black adds trailing commas and breaks lines
items = [
    "first_item",
    "second_item", 
    "third_item",
]

# Black formats dictionaries consistently
config = {
    "key1": "value1",
    "key2": "value2",
    "key3": "value3",
}
```

## 📋 **Line Length Best Practices**

### **Practice 1: Write Naturally**

```python
# Don't pre-break lines - let Black decide
def process_items(items, config, timeout=30, retries=3):
    return [process_item(item, config) for item in items if item.is_valid()]

# Black will format appropriately:
def process_items(items, config, *, timeout=30, retries=3):
    return [
        process_item(item, config) 
        for item in items 
        if item.is_valid()
    ]
```

### **Practice 2: Use Parentheses for Long Expressions**

```python
# Long boolean expressions
if (
    user.is_authenticated
    and user.has_permission("read")
    and resource.is_accessible
    and not resource.is_locked
):
    process_request()

# Long arithmetic expressions
total_cost = (
    base_price
    + tax_amount
    + shipping_cost
    + handling_fee
    - discount_amount
)
```

### **Practice 3: Break at Logical Points**

```python
# Break at logical operators
condition = (
    item.status == "active"
    and item.priority > threshold
    and item.created_at > cutoff_date
)

# Break at method chains
result = (
    data_processor
    .filter_active_items()
    .sort_by_priority()
    .limit(max_items)
    .process()
)
```

## 📋 **Line Length Checklist**

**Before finalizing code:**

- [ ] **No lines exceed 88 characters**: Check with Black
- [ ] **Natural line breaks**: Let Black handle formatting
- [ ] **Logical breaking points**: Break at operators, commas
- [ ] **Consistent indentation**: Black handles this automatically
- [ ] **Trailing commas**: Black adds these in multi-line structures
- [ ] **No manual line continuations**: Avoid backslash continuations

## ⚡ **Quick Line Length Fixes**

### **Check Line Length**
```bash
# Black will show lines that are too long
black --check --diff filename.py
```

### **Auto-fix Line Length**
```bash
# Black automatically fixes line length
black filename.py
```

### **Manual Strategies**
- **Shorten variable names**: Use concise but clear names
- **Extract variables**: Break complex expressions
- **Use keyword arguments**: More readable than positional
- **Add parentheses**: Group related expressions

---

**🎯 Remember**: Trust Black to handle line length. Focus on writing clear, readable code and let Black format it consistently.
