# Task 8.2: Detection Testing

**🎯 Test O(1) provider detection for all instrumentors**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Task 8.1 complete (Bundle compiled) ✅/❌
- [ ] compiled_bundle.pkl exists ✅/❌
- [ ] Extraction function callable ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Create Test Attributes for Each Verified Instrumentor**

🛑 EXECUTE-NOW: Create test data from Phase 2 verification

For EACH verified instrumentor, create test attributes:

**Traceloop Test Data** (if verified):
```python
traceloop_test_attrs = {
    "gen_ai.system": "{provider_specific_value}",  # From Phase 2
    "gen_ai.request.model": "{model_from_phase_3}",
    "gen_ai.usage.prompt_tokens": 100,
    # Add other required fields from Phase 4 pattern
}
```

**OpenInference Test Data** (if verified):
```python
openinference_test_attrs = {
    "llm.provider": "{provider_specific_value}",  # From Phase 2
    "llm.model_name": "{model_from_phase_3}",
    "llm.token_count.prompt": 100,
    # Add other required fields
}
```

**OpenLit Test Data** (if verified):
```python
openlit_test_attrs = {
    "openlit.provider": "{provider_specific_value}",  # From Phase 2
    "openlit.model": "{model_from_phase_3}",
    "openlit.usage.prompt_tokens": 100,
    # Add other required fields
}
```

📊 COUNT-AND-DOCUMENT: Test datasets created: [X] (one per verified instrumentor)

### **Step 2: Load Provider Processor**

🛑 EXECUTE-NOW: Initialize provider processor with compiled bundle

```bash
python -c "
from src.honeyhive.tracer.processing.semantic_conventions.provider_processor import UniversalProviderProcessor

processor = UniversalProviderProcessor()
print(f'Processor initialized: {processor is not None}')
print(f'Bundle loaded: {processor._bundle is not None}')
"
```

🛑 PASTE-OUTPUT: Processor initialization

📊 QUANTIFY-RESULTS: Processor initialized: YES/NO

### **Step 3: Test Detection for Each Instrumentor**

🛑 EXECUTE-NOW: Test detection with each test dataset

```python
# Create test script: scripts/test_{provider}_detection.py
from src.honeyhive.tracer.processing.semantic_conventions.provider_processor import UniversalProviderProcessor

processor = UniversalProviderProcessor()

# Test Traceloop (if verified)
traceloop_attrs = {...}  # From Step 1
instrumentor, provider = processor._detect_instrumentor_and_provider(traceloop_attrs)
print(f"Traceloop: instrumentor={instrumentor}, provider={provider}")
assert instrumentor == "traceloop", f"Expected 'traceloop', got '{instrumentor}'"
assert provider == "{expected_provider}", f"Expected '{expected_provider}', got '{provider}'"

# Test OpenInference (if verified)
# ...

# Test OpenLit (if verified)
# ...

print("✅ All detection tests passed!")
```

```bash
python scripts/test_{provider}_detection.py
```

🛑 PASTE-OUTPUT: Detection test results

📊 QUANTIFY-RESULTS: All detection tests passed: YES/NO

### **Step 4: Validate Detection Performance**

🛑 EXECUTE-NOW: Test detection speed (should be O(1))

```python
import time
from src.honeyhive.tracer.processing.semantic_conventions.provider_processor import UniversalProviderProcessor

processor = UniversalProviderProcessor()
test_attrs = {...}  # Use one test dataset

# Warm-up
for _ in range(10):
    processor._detect_instrumentor_and_provider(test_attrs)

# Time detection
start = time.perf_counter()
for _ in range(1000):
    instrumentor, provider = processor._detect_instrumentor_and_provider(test_attrs)
end = time.perf_counter()

avg_time_ms = (end - start) / 1000 * 1000
print(f"Average detection time: {avg_time_ms:.4f} ms")
assert avg_time_ms < 1.0, f"Detection too slow: {avg_time_ms:.4f} ms"
```

🛑 PASTE-OUTPUT: Performance results

📊 QUANTIFY-RESULTS: Detection < 1ms: YES/NO

### **Step 5: Document Detection Test Results**

🛑 EXECUTE-NOW: Update RESEARCH_SOURCES.md

```markdown
### **Detection Testing**

**Test Coverage**: [X/3] instrumentors tested

**Detection Results**:
- Traceloop: ✅ PASS / ❌ FAIL / ⚠️ N/A (not verified)
  - Detected instrumentor: traceloop
  - Detected provider: {provider}
- OpenInference: ✅ PASS / ❌ FAIL / ⚠️ N/A
  - Detected instrumentor: openinference
  - Detected provider: {provider}
- OpenLit: ✅ PASS / ❌ FAIL / ⚠️ N/A
  - Detected instrumentor: openlit
  - Detected provider: {provider}

**Performance**:
- Average detection time: [X.XX] ms
- O(1) performance: ✅ CONFIRMED (< 1ms)

**Test Date**: 2025-09-30
**Status**: ✅ ALL TESTS PASSED / ⚠️ SOME FAILURES
```

📊 QUANTIFY-RESULTS: Detection testing documented: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Detection Testing Complete
- [ ] Test data created for all verified instrumentors ✅/❌
- [ ] Provider processor initialized ✅/❌
- [ ] Detection tests passed for all verified instrumentors ✅/❌
- [ ] Detection performance < 1ms ✅/❌
- [ ] Results documented ✅/❌

🚨 FRAMEWORK-VIOLATION: If detection fails or performance > 1ms

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 8.2 → Detection tested ([X/X] instrumentors passed)
🎯 NEXT-MANDATORY: [extraction-testing.md](extraction-testing.md)
