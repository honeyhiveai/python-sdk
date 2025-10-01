# Task 8.3: Extraction Testing

**🎯 Test data extraction for all verified instrumentors**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Task 8.2 complete (Detection tested) ✅/❌
- [ ] Detection tests passed for all verified instrumentors ✅/❌
- [ ] Test attributes from Phase 8.2 available ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Expand Test Attributes with Full Data**

🛑 EXECUTE-NOW: Add extraction fields to test data from Phase 8.2

For EACH verified instrumentor, add full extraction fields:

**Traceloop Full Test Data**:
```python
traceloop_full_attrs = {
    # Detection fields
    "gen_ai.system": "{provider_value}",
    "gen_ai.request.model": "{model}",
    
    # Extraction fields (from Phase 5 navigation rules)
    "gen_ai.prompt": "Test user message",
    "gen_ai.completion": "Test assistant response",
    "gen_ai.usage.prompt_tokens": 10,
    "gen_ai.usage.completion_tokens": 20,
    "gen_ai.request.temperature": 0.7,
    "gen_ai.request.max_tokens": 100,
    "gen_ai.response.finish_reasons": ["stop"],
    # Add all fields from navigation_rules.yaml
}
```

Repeat for OpenInference and OpenLit if verified

📊 COUNT-AND-DOCUMENT: Full test datasets: [X]

### **Step 2: Test Extraction for Each Instrumentor**

🛑 EXECUTE-NOW: Test complete extraction pipeline

```python
# scripts/test_{provider}_extraction.py
from src.honeyhive.tracer.processing.semantic_conventions.provider_processor import UniversalProviderProcessor

processor = UniversalProviderProcessor()

# Test Traceloop extraction (if verified)
traceloop_attrs = {...}  # From Step 1
result = processor.process_span_attributes(traceloop_attrs)

print(f"Detection: instrumentor={result['metadata']['instrumentor']}, provider={result['metadata']['provider']}")
print(f"Inputs: {result.get('inputs', {})}")
print(f"Outputs: {result.get('outputs', {})}")
print(f"Config: {result.get('config', {})}")

# Validate extraction
assert result['inputs'].get('messages') is not None, "Input messages not extracted"
assert result['outputs'].get('messages') is not None, "Output messages not extracted"
assert result['outputs'].get('model') == "{expected_model}", "Model mismatch"
assert result['config'].get('prompt_tokens') == 10, "Prompt tokens mismatch"
assert result['config'].get('completion_tokens') == 20, "Completion tokens mismatch"

# Test OpenInference, OpenLit if verified...

print("✅ All extraction tests passed!")
```

```bash
python scripts/test_{provider}_extraction.py
```

🛑 PASTE-OUTPUT: Extraction test results

📊 QUANTIFY-RESULTS: All extraction tests passed: YES/NO

### **Step 3: Validate 4-Section Schema**

🛑 EXECUTE-NOW: Verify all 4 sections populated

For each tested instrumentor, check:
- [ ] inputs section populated ✅/❌
- [ ] outputs section populated ✅/❌
- [ ] config section populated ✅/❌
- [ ] metadata section populated ✅/❌

📊 QUANTIFY-RESULTS: All 4 sections present: YES/NO

### **Step 4: Test Transform Execution**

🛑 EXECUTE-NOW: Verify transforms applied correctly

```python
# Check finish reason normalization
assert result['outputs']['finish_reason'] == "complete", "Finish reason not normalized"

# Check cost calculation (if pricing available)
cost = result['config'].get('cost')
assert cost is not None, "Cost not calculated"
assert cost > 0, "Cost should be positive"
print(f"Calculated cost: ${cost:.6f}")
```

🛑 PASTE-OUTPUT: Transform validation results

📊 QUANTIFY-RESULTS: Transforms executed correctly: YES/NO

### **Step 5: Test Extraction Performance**

🛑 EXECUTE-NOW: Test extraction speed

```python
import time

processor = UniversalProviderProcessor()
test_attrs = {...}  # Use one full test dataset

# Warm-up
for _ in range(10):
    processor.process_span_attributes(test_attrs)

# Time extraction
start = time.perf_counter()
for _ in range(1000):
    result = processor.process_span_attributes(test_attrs)
end = time.perf_counter()

avg_time_ms = (end - start) / 1000 * 1000
print(f"Average extraction time: {avg_time_ms:.4f} ms")
assert avg_time_ms < 5.0, f"Extraction too slow: {avg_time_ms:.4f} ms"
```

🛑 PASTE-OUTPUT: Performance results

📊 QUANTIFY-RESULTS: Extraction < 5ms: YES/NO

### **Step 6: Document Extraction Test Results**

🛑 EXECUTE-NOW: Update RESEARCH_SOURCES.md

```markdown
### **Extraction Testing**

**Test Coverage**: [X/3] instrumentors tested

**Extraction Results**:
- Traceloop: ✅ PASS / ❌ FAIL / ⚠️ N/A
  - Inputs: ✅ POPULATED
  - Outputs: ✅ POPULATED
  - Config: ✅ POPULATED (tokens + cost)
  - Metadata: ✅ POPULATED
- OpenInference: ✅ PASS / ❌ FAIL / ⚠️ N/A
  - [Same breakdown]
- OpenLit: ✅ PASS / ❌ FAIL / ⚠️ N/A
  - [Same breakdown]

**Transform Validation**:
- Finish reason normalization: ✅ WORKING
- Cost calculation: ✅ WORKING (${X.XX} for test)

**Performance**:
- Average extraction time: [X.XX] ms
- Performance target (< 5ms): ✅ MET

**Test Date**: 2025-09-30
**Status**: ✅ ALL TESTS PASSED / ⚠️ SOME FAILURES
```

📊 QUANTIFY-RESULTS: Extraction testing documented: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Extraction Testing Complete
- [ ] Full test data created for all verified instrumentors ✅/❌
- [ ] Extraction tests passed for all verified instrumentors ✅/❌
- [ ] All 4 sections populated correctly ✅/❌
- [ ] Transforms executed successfully ✅/❌
- [ ] Extraction performance < 5ms ✅/❌
- [ ] Results documented ✅/❌

🚨 FRAMEWORK-VIOLATION: If extraction fails or any section empty

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 8.3 → Extraction tested ([X/X] instrumentors passed)
🎯 NEXT-MANDATORY: [performance-validation.md](performance-validation.md)
