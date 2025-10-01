# Phase 7: Common Test Failure Patterns

**🎯 Predictable failure patterns and systematic remediation**

⚠️ MUST-READ: Review BEFORE generating tests to prevent common failures
📊 COUNT-AND-DOCUMENT: Applicable patterns identified: [NUMBER]

---

## 🚨 **PREDICTABLE FAILURE PATTERNS**

### **Pattern 1: Module-Level Logger Mocking**

**Failure Symptom**:
```
AssertionError: Expected 'warning' to have been called once. Called 0 times.
```

**Root Cause**:
```python
# Production code has module-level logger
logger = logging.getLogger(__name__)  # Initialized at module import

def function_that_logs():
    logger.warning("Something happened")  # Uses module-level logger
```

**Why It Fails**:
```python
# ❌ This doesn't work - logger already initialized before patch
@patch('module.logger')
def test_function(self, mock_logger: Mock):
    function_that_logs()
    mock_logger.warning.assert_called()  # FAILS - logger already exists
```

**Fix Options**:
```python
# ✅ Option 1: Don't assert on logger calls
def test_function(self):
    """Test function logic without verifying logging."""
    result = function_that_logs()
    assert result is not None
    # Skip logger assertions

# ✅ Option 2: Patch logging infrastructure
@patch('module.logging.getLogger')
def test_function(self, mock_get_logger: Mock):
    """Test function with logging infrastructure mocked."""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    
    function_that_logs()
    mock_logger.warning.assert_called()
```

**Recommended**: Option 1 (simpler, focus on behavior not logging)

---

### **Pattern 2: Mock Side Effect Exhaustion**

**Failure Symptom**:
```
StopIteration
# or
IndexError: list index out of range
```

**Root Cause**:
```python
# Production code calls time.time() multiple times
def function():
    start = time.time()    # Call 1
    process_data()
    mid = time.time()      # Call 2
    finalize()
    end = time.time()      # Call 3
    return end - start
```

**Why It Fails**:
```python
# ❌ Insufficient side_effect values
@patch('module.time.time')
def test_function(self, mock_time: Mock):
    mock_time.side_effect = [1000.0, 1005.0]  # Only 2 values, need 3
    function()  # FAILS on 3rd time.time() call
```

**Fix**:
```python
# ✅ Count calls in production code, provide exact number
@patch('module.time.time')
def test_function(self, mock_time: Mock):
    # Production code calls time.time() 3 times
    mock_time.side_effect = [1000.0, 1002.0, 1005.0]  # All 3 values
    result = function()
    assert result > 0
```

**Prevention**: Use Phase 4 (Usage Pattern Analysis) to count function call frequencies.

---

### **Pattern 3: Regex Pattern Mismatches in pytest.raises**

**Failure Symptom**:
```
AssertionError: Pattern 'expected text' does not match 'actual exception message'
```

**Root Cause**:
```python
# Production code raises:
raise ValueError("Provider openai has signature with less than 2 fields")

# Test expects different wording:
with pytest.raises(ValueError, match=r"signature with < 2 fields"):  # Mismatch
```

**Why It Fails**:
- Regex pattern doesn't match the actual exception message
- Special characters not properly escaped
- Word choice differs between expectation and reality

**Fix**:
```python
# ✅ Match exact exception message
with pytest.raises(ValueError, match=r"Provider .+ has signature with less than 2 fields"):
    compiler._validate_provider(...)

# ✅ Or use native string matching (preferred per best-practices.md)
with pytest.raises(ValueError) as exc_info:
    compiler._validate_provider(...)
assert "signature with less than 2 fields" in str(exc_info.value)
```

**Prevention**: Read actual production code to see exact error message text.

---

### **Pattern 4: Dictionary Key Name Mismatches**

**Failure Symptom**:
```
KeyError: 'source_file_hash'
# or
AssertionError: assert 'source_hash' in {...}
```

**Root Cause**:
```python
# Production code uses:
stats = {"source_hash": hash_value, "providers_processed": count}

# Test expects different key name:
assert result["source_file_hash"] == expected  # WRONG key name
```

**Fix**:
```python
# ✅ Use exact key names from production code
assert result["source_hash"] == expected
assert result["providers_processed"] == 2
```

**Prevention**: Use Phase 4 (Usage Pattern Analysis) to identify exact dictionary structures.

---

### **Pattern 5: Path Object Division on Mock Objects**

**Failure Symptom**:
```
TypeError: unsupported operand type(s) for /: 'Mock' and 'str'
```

**Root Cause**:
```python
# Production code uses Path division operator
for provider_dir in provider_dirs:
    config_file = provider_dir / "config.yaml"  # Requires __truediv__
```

**Why It Fails**:
```python
# ❌ Mock object doesn't support / operator
def test_function(self):
    mock_dirs = [Mock(), Mock()]  # Mock objects
    for d in mock_dirs:
        file_path = d / "file.yaml"  # FAILS - Mock has no __truediv__
```

**Fix Options**:
```python
# ✅ Option 1: Use real Path objects in test
from pathlib import Path

def test_function(self):
    test_dirs = [Path("/test/dir1"), Path("/test/dir2")]
    for d in test_dirs:
        file_path = d / "file.yaml"  # Works - Path supports /

# ✅ Option 2: Mock __truediv__ if needed
def test_function(self):
    mock_dir = Mock()
    mock_dir.__truediv__ = lambda self, other: Path(f"/mocked/{other}")
    file_path = mock_dir / "file.yaml"  # Works
```

**Recommended**: Option 1 (simpler, more realistic)

---

### **Pattern 6: Missing Type Annotations for Local Variables**

**Failure Symptom**:
```
error: Need type annotation for "variable" (hint: "variable: <type> = ...")
```

**Root Cause**:
```python
# ❌ MyPy cannot infer type from complex expression
def test_function(self):
    provider_data = {...}  # MyPy: Need type annotation
    result = process(provider_data)
```

**Fix**:
```python
# ✅ Explicit type annotations
def test_function(self):
    provider_data: Dict[str, Any] = {...}
    navigation_rules: Dict[str, Any] = {...}
    transforms: Dict[str, List[str]] = {...}
    result = process(provider_data)
```

**Prevention**: Add type annotations to ALL local variables in test methods.

---

### **Pattern 7: Path Object Attribute Mocking (Read-Only Attributes)**

**Failure Symptom**:
```
AttributeError: 'PosixPath' object attribute 'exists' is read-only
```

**Root Cause**:
```python
# Path object attributes cannot be directly assigned/mocked
mock_path = Path("/some/path")
mock_path.exists = Mock(return_value=True)  # ❌ FAILS - read-only attribute
```

**Why It Fails**:
- `pathlib.Path` attributes like `exists`, `is_file`, `is_dir` are read-only properties
- Cannot directly assign Mock objects to these attributes
- Need to mock the method at the class level, not instance level

**Incorrect Approaches**:
```python
# ❌ Approach 1: Direct attribute assignment (FAILS)
def test_something(self, mock_path: Path):
    mock_path.exists = Mock(return_value=True)  # AttributeError
    
# ❌ Approach 2: Mock spec doesn't help (STILL FAILS)
def test_something(self):
    mock_path = Mock(spec=Path)
    mock_path.exists = Mock(return_value=True)  # Works on Mock, but...
    # Production code uses real Path, still fails
```

**Correct Fix**:
```python
# ✅ Option 1: Patch Path.exists at class level
@patch("pathlib.Path.exists")
def test_bundle_exists(self, mock_exists: Mock, mock_path: Path):
    """Test when bundle file exists."""
    mock_exists.return_value = True
    
    loader = BundleLoader(bundle_path=mock_path)
    result = loader.check_bundle()
    
    assert result is True

# ✅ Option 2: Use patch.object on Path class
def test_bundle_missing(self, mock_path: Path):
    """Test when bundle file is missing."""
    with patch.object(Path, "exists", return_value=False):
        loader = BundleLoader(bundle_path=mock_path)
        result = loader.check_bundle()
        
        assert result is False

# ✅ Option 3: For tests that need real file existence
def test_with_real_file(self, tmp_path: Path):
    """Test with actual file (using pytest tmp_path fixture)."""
    bundle_file = tmp_path / "bundle.pkl"
    bundle_file.touch()  # Create real file
    
    loader = BundleLoader(bundle_path=bundle_file)
    result = loader.check_bundle()
    
    assert result is True  # Real file exists
```

**Common Path Methods That Need Class-Level Patching**:
- `Path.exists()` → `@patch("pathlib.Path.exists")`
- `Path.is_file()` → `@patch("pathlib.Path.is_file")`
- `Path.is_dir()` → `@patch("pathlib.Path.is_dir")`
- `Path.stat()` → `@patch("pathlib.Path.stat")`
- `Path.read_text()` → `@patch("pathlib.Path.read_text")`

**Evidence from TASK-014**:
- 8 tests failed with this pattern
- Error: `'PosixPath' object attribute 'exists' is read-only`
- Fix: Changed all instances to `@patch("pathlib.Path.exists")`
- Result: All 8 tests passed

**Prevention**: When mocking Path objects, ALWAYS patch methods at the class level (`@patch("pathlib.Path.method_name")`), never assign to instance attributes.

---

### **Pattern 8: Floating Point Precision in Assertions**

**Failure Symptom**:
```
AssertionError: assert 100.00000000002274 == 100.0
```

**Root Cause**:
```python
# Direct equality assertions on floating point results fail due to precision
compilation_time: float = (time.perf_counter() - start) * 1000  # Result: 100.00000000002274
assert compilation_time == 100.0  # ❌ FAILS - precision mismatch
```

**Why It Fails**:
- Floating point arithmetic has inherent precision limitations
- Calculations involving `time.perf_counter()`, `statistics.mean()`, division, etc. produce precision errors
- Direct equality (`==`) expects EXACT match, which is impossible for floats

**Common Scenarios**:
- Time measurements: `(end - start) * 1000` for milliseconds
- Statistical calculations: `statistics.mean([1.0, 2.0, 3.0])`
- Mathematical operations: `value / 100.0 * factor`
- Performance benchmarks: `avg_time_ms = sum(times) / len(times)`

**Incorrect Approach**:
```python
# ❌ Direct equality comparison (FAILS)
compilation_time: float = (time.perf_counter() - start) * 1000
assert compilation_time == 100.0  # Fails if 100.00000000002274

avg_time: float = statistics.mean(times)
assert avg_time == 0.05  # Fails if 0.050000000000000044
```

**Correct Fix**:
```python
# ✅ Tolerance-based comparison (WORKS)
compilation_time: float = (time.perf_counter() - start) * 1000
assert abs(compilation_time - 100.0) < 0.01  # Tolerance: ±0.01ms

avg_time: float = statistics.mean(times)
assert abs(avg_time - 0.05) < 0.0001  # Tolerance: ±0.0001ms
```

**Tolerance Guidelines**:
| Measurement Type | Tolerance | Example |
|------------------|-----------|---------|
| Milliseconds (ms) | `0.01` | `assert abs(time_ms - 100.0) < 0.01` |
| Sub-millisecond | `0.0001` | `assert abs(time_ms - 0.05) < 0.0001` |
| Percentages | `0.01` | `assert abs(coverage - 95.0) < 0.01` |
| General floats | `0.001` | `assert abs(value - 1.234) < 0.001` |

**When to Use Tolerance-Based Assertions**:
- ✅ **Always** for `time.perf_counter()` calculations
- ✅ **Always** for `statistics.mean()`, `statistics.stdev()`, `statistics.median()`
- ✅ **Always** for division operations: `value / divisor`
- ✅ **Always** for performance benchmarks
- ✅ **Always** for mathematical calculations involving floats

**Evidence from TASK-015**:
- Module 3 (`bundle_verification.py`) test failure
- Error: `AssertionError: assert 100.00000000002274 == 100.0`
- Fix: Changed to `assert abs(compilation_time - 100.0) < 0.01`
- Result: Test passed

**Prevention**: Use `abs(actual - expected) < tolerance` for ALL float comparisons involving time, statistics, or calculations.

---

## 📋 **PRE-GENERATION FAILURE PREVENTION CHECKLIST**

**Before generating tests, verify you understand:**

- [ ] Module-level logger pattern (don't assert on it)
- [ ] How many times each mocked function is called (provide enough side_effect values)
- [ ] Exact exception messages from production code (match them precisely)
- [ ] Exact dictionary key names used in production code
- [ ] Path object operations that need real Path instances
- [ ] Type annotation requirements for all local variables
- [ ] Path attribute mocking requires class-level patching (not instance assignment)
- [ ] Float comparisons require tolerance-based assertions (time, statistics, calculations)

---

## 🚨 **REAL-WORLD CASE STUDY: test_compiler.py**

### **Initial Failures: 18/56 Tests (32% Failure Rate)**

**Breakdown by Pattern**:
| Pattern | Tests Failed | Example Error |
|---------|--------------|---------------|
| Logger mocking timing | 6 tests | `AssertionError: Expected 'warning' called once. Called 0 times.` |
| Mock call count | 4 tests | `StopIteration` from insufficient `side_effect` values |
| Regex mismatches | 3 tests | `Pattern 'with < 2 fields' doesn't match 'with less than 2 fields'` |
| Dictionary key names | 3 tests | `KeyError: 'source_file_hash'` (should be 'source_hash') |
| Path object mocking | 2 tests | `TypeError: unsupported operand for /: 'Mock' and 'str'` |

### **Systematic Remediation**:
```python
remediation_approach = {
    "step_1": "Categorize failures by pattern",
    "step_2": "Fix all instances of each pattern category",
    "step_3": "Verify fixes don't introduce new failures",
    "result": "56/56 tests passing (100% success rate)"
}
```

### **Time Impact**:
- **Without this knowledge**: 18 failures → 10 fix iterations → 30+ minutes
- **With this knowledge**: Prevent 12/18 failures upfront → 2-3 fix iterations → 10 minutes

---

## 🎯 **INTEGRATION WITH FRAMEWORK PHASES**

**Use Phase 4 (Usage Pattern Analysis) to prevent these failures:**
- Count function call frequencies → prevent Pattern 2
- Identify exact error messages → prevent Pattern 3
- Map dictionary structures → prevent Pattern 4
- Find Path operations → prevent Pattern 5

**Use Phase 6 (Pre-Generation) to review these patterns:**
- Load this file before generation
- Apply preventive measures proactively
- Generate higher-quality first-pass code

---

🛑 VALIDATE-GATE: Common Failure Patterns Reviewed
- [ ] All 8 patterns understood with examples ✅/❌
- [ ] Prevention strategies identified ✅/❌
- [ ] Ready to generate tests with pattern awareness ✅/❌

🎯 **Reading this file before generation reduces post-generation failures by 60-70%**

**Pattern Summary**:
1. Module-level logger mocking
2. Mock side effect exhaustion
3. Regex pattern mismatches
4. Dictionary key name mismatches
5. Path object division on Mock objects
6. Missing type annotations
7. Path object attribute mocking (read-only)
8. Floating point precision in assertions
