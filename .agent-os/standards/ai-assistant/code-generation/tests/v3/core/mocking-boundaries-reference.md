# Mocking Boundaries - Critical Internal vs External Distinction

**🎯 CRITICAL: Understand this BEFORE generating any unit tests**

🛑 VALIDATE-GATE: Mocking Boundaries Understanding
- [ ] Internal vs External classification comprehended ✅/❌
- [ ] Coverage implications understood ✅/❌
- [ ] Concrete examples reviewed ✅/❌

🚨 FRAMEWORK-VIOLATION: If mocking internal methods of class under test

---

## 🎯 **THE FUNDAMENTAL RULE**

### **Mock What the Code DEPENDS ON (External)**
### **Execute What the Code CONTAINS (Internal)**

```python
# Simple mental model
class CodeUnderTest:
    def public_method(self):
        # THIS is internal - execute it (achieves coverage)
        result = self._internal_helper()
        
        # THIS is external - mock it (isolates test)
        data = external_library.fetch_data()
        
        return result
```

---

## 🚨 **CRITICAL CLASSIFICATIONS**

### **✅ EXTERNAL - Always Mock for Unit Tests**

**1. Third-Party Libraries**
```python
# Always mock these
@patch('requests.post')
@patch('os.getenv')
@patch('sys.exit')
@patch('time.time')
@patch('json.dumps')
@patch('yaml.safe_load')
```

**2. Cross-Module Project Dependencies**
```python
# Mock imports from OTHER project modules
@patch('honeyhive.utils.logger.safe_log')  # Different module
@patch('honeyhive.config.loader.load_config')  # Different module
@patch('config.dsl.validator.validate_schema')  # Different module
```

**3. I/O Operations**
```python
# Mock file system and network operations
@patch('pathlib.Path.exists')
@patch('pathlib.Path.read_text')
@patch('builtins.open')
```

**4. Global State & Singletons**
```python
# Mock environment and global objects
@patch('os.environ.get')
@patch('logging.getLogger')
```

---

### **❌ INTERNAL - NEVER Mock for Unit Tests**

**1. Methods of the Class Under Test**
```python
# Testing ProviderCompiler class
class TestProviderCompiler:
    
    # ❌ WRONG - Mocking internal method
    @patch.object(ProviderCompiler, '_generate_extraction_function')
    def test_compile_extraction_functions(self, mock_generate):
        compiler = ProviderCompiler()
        compiler._compile_extraction_functions(...)
        # Result: 0% coverage of _generate_extraction_function
    
    # ✅ CORRECT - Execute internal method
    def test_compile_extraction_functions(self):
        compiler = ProviderCompiler()
        # Let _generate_extraction_function execute naturally
        result = compiler._compile_extraction_functions(...)
        # Result: Full coverage of internal logic
```

**2. Private Functions in the Same File**
```python
# Testing module.py which has _helper_function()

# ❌ WRONG - Mocking same-file helper
@patch('module._helper_function')
def test_main_function(mock_helper):
    main_function()  # _helper_function is mocked

# ✅ CORRECT - Let helper execute
def test_main_function():
    result = main_function()  # _helper_function executes normally
    assert result is not None
```

**3. Instance Attributes**
```python
# ❌ WRONG - Don't mock instance state
mock_compiler.providers = Mock()  # Mocking the data itself

# ✅ CORRECT - Set real data
mock_compiler.providers = {"openai": {...}}  # Real dict for testing
```

---

## 📋 **CONCRETE DECISION TREE**

```
Should I mock this?
├── Is it in a different Python package? (e.g., requests, yaml)
│   └── YES → ✅ MOCK IT (external dependency)
├── Is it from a different project module? (e.g., honeyhive.utils when testing honeyhive.tracer)
│   └── YES → ✅ MOCK IT (cross-module dependency)
├── Is it an I/O operation? (file, network, database)
│   └── YES → ✅ MOCK IT (external I/O)
├── Is it a method of the class I'm testing?
│   └── YES → ❌ DON'T MOCK (internal method - needs coverage)
├── Is it a function in the same file?
│   └── YES → ❌ DON'T MOCK (internal function - needs coverage)
└── Is it instance data/attributes?
    └── YES → ❌ DON'T MOCK (use real data structures)
```

---

## 🎯 **REAL-WORLD EXAMPLE: test_compiler.py**

### **File Being Tested**: `config/dsl/compiler.py`

**Contains**:
```python
class ProviderCompiler:
    def compile_all_providers(self):
        self._load_all_providers()           # INTERNAL - don't mock
        self._validate_all_providers()       # INTERNAL - don't mock
        signatures = self._compile_signature_indices()  # INTERNAL - don't mock
        functions = self._compile_extraction_functions()  # INTERNAL - don't mock
        
    def _compile_extraction_functions(self):
        for provider in self.providers:
            code = self._generate_extraction_function(provider)  # INTERNAL - don't mock
            
    def _generate_extraction_function(self, provider):
        yaml.safe_load(...)  # EXTERNAL - mock this
        Path(...).exists()   # EXTERNAL - mock this
```

### **Correct Mocking Strategy**:

```python
# ✅ EXTERNAL - Mock these
@patch('config.dsl.compiler.yaml.safe_load')
@patch('config.dsl.compiler.Path')
@patch('config.dsl.compiler.json.dumps')
@patch('config.dsl.compiler.logging')
def test_compile_extraction_functions(
    mock_logging, mock_json, mock_path, mock_yaml
):
    # Set up compiler with real data
    compiler = ProviderCompiler(...)
    compiler.providers = {"openai": {...}}  # Real dict, not Mock
    
    # Let ALL internal methods execute naturally
    result = compiler._compile_extraction_functions(...)
    
    # This exercises:
    # - _compile_extraction_functions() ✅ coverage
    # - _generate_extraction_function() ✅ coverage
    # - _generate_field_extraction_code() ✅ coverage
    
# ❌ INTERNAL - NEVER mock these
# @patch.object(compiler, '_generate_extraction_function')  ← NO!
# @patch.object(compiler, '_compile_validation_rules')      ← NO!
```

---

## 🚨 **WHY THIS IS CRITICAL**

### **Impact on Coverage**:
```python
coverage_analysis = {
    "mocking_internal_methods": {
        "coverage_achieved": "0-30% (methods are mocked, not executed)",
        "framework_target": "90%+ required",
        "result": "IMPOSSIBLE to achieve target"
    },
    "mocking_only_external": {
        "coverage_achieved": "90-95% (all internal code executes)",
        "framework_target": "90%+ required",
        "result": "Target easily achievable"
    }
}
```

### **Impact on Test Value**:
```python
test_quality = {
    "mocking_internal": "Tests that mocks work, not that code works",
    "mocking_external": "Tests that code works with controlled dependencies"
}
```

---

## 📊 **SELF-VALIDATION CHECKLIST**

**Before generating test for ANY method, ask yourself:**

- [ ] Am I mocking a method that belongs to the class I'm testing? → ❌ DON'T
- [ ] Am I mocking a function defined in the file I'm testing? → ❌ DON'T
- [ ] Am I mocking something from a different module/package? → ✅ DO
- [ ] Am I mocking I/O operations? → ✅ DO
- [ ] Will my mocking strategy allow the production code to execute? → ✅ MUST

---

## 🎯 **COVERAGE VALIDATION**

**After generating tests, verify:**
```bash
# Check that internal methods have coverage
coverage report --show-missing

# Look for internal methods with 0% coverage
# Example warning signs:
# _generate_extraction_function  0%   ← WRONG (internal method not executed)
# _compile_validation_rules      0%   ← WRONG (internal method not executed)
```

**If internal methods show 0% coverage → You mocked them incorrectly**

---

🛑 UPDATE-TABLE: Mocking boundaries reference reviewed and understood
🎯 NEXT-MANDATORY: Apply correct mocking strategy in test generation
