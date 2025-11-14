# Evaluate + enrich_span Behavior Analysis

**Date:** October 28, 2025  
**Test Run ID:** `092e357a-9651-4e4a-8f42-c08bb58e6988`  
**Session IDs:** `bb26285e-8b5c-445a-a929-1ac422345e45`, `b357fc10-2196-488d-8dde-d3f00be0df4a`

---

## 🎯 Executive Summary

**Issue:** When using `evaluate()` with `@trace` decorated functions and `enrich_span()` calls:
- ✅ OTLP spans are created and exported successfully
- ✅ Sessions are created with evaluation metadata
- ✅ Outputs are enriched via the evaluate framework
- ❌ **Nested spans DO NOT appear in the backend**
- ❌ **Custom enrich_span metadata/metrics DO NOT appear in the backend**

---

## 📊 What We Tested

### Test Code (`nw_test.py`):
```python
@trace(event_name="evaluation_function", event_type="chain")
def evaluation_function(datapoint):
    inputs = datapoint.get("inputs", {})
    context = inputs.get("context", "")
    enrich_span(metrics={"input_length": len(context)})  # ← Custom metric
    return {
        "answer": invoke_summary_agent(**{"context": context})
    }

@trace(event_name="summary_agent", event_type="tool")
def invoke_summary_agent(**kwargs):
    enrich_span(metadata={"model": "test-model", "temperature": 0.7})  # ← Custom metadata
    return "The American Shorthair is..."
```

---

## 🔍 Backend Analysis

### What Made It to the Backend:

```json
{
  "event_name": "initialization",
  "event_type": "session",
  "metadata": {
    "run_id": "092e357a-9651-4e4a-8f42-c08bb58e6988",
    "dataset_id": "EXT-97a1a02335a1da5a",
    "datapoint_id": "EXT-400bd308f5ea115c",
    "num_events": 0,  // ← Should be 2 (evaluation_function + summary_agent)
    "num_model_events": 0,
    "has_feedback": false
  },
  "outputs": {
    "answer": "The American Shorthair is..."  // ← ✅ Enriched by evaluate()
  },
  "children": []  // ← ❌ Empty! Should contain 2 child events
}
```

### What's Missing:

1. **No nested events:**
   - `evaluation_function` span (chain)
   - `summary_agent` span (tool)

2. **No custom enrich_span data:**
   - ❌ `metadata.model` = "test-model"
   - ❌ `metadata.temperature` = 0.7
   - ❌ `metrics.input_length` = 619

---

## 🔬 Client-Side Analysis

### OTLP Export Logs Show SUCCESS:

```json
{
  "message": "SPAN PROCESSOR on_end - mode: otlp, span: evaluation_function",
  "attributes": {
    "honeyhive.session_id": "bb26285e-8b5c-445a-a929-1ac422345e45",
    "honeyhive_event_type": "chain",
    "honeyhive_event_name": "evaluation_function",
    "honeyhive_outputs.result.answer": "The American Shorthair is...",
    "honeyhive_duration_ms": 1212.49
  }
}
```

```json
{
  "message": "SPAN PROCESSOR on_end - mode: otlp, span: summary_agent",
  "attributes": {
    "honeyhive.session_id": "bb26285e-8b5c-445a-a929-1ac422345e45", 
    "honeyhive_event_type": "tool",
    "honeyhive_event_name": "summary_agent",
    "honeyhive_outputs": "The American Shorthair is...",
    "honeyhive_duration_ms": 508.28
  }
}
```

Both spans exported successfully: `"✅ Span exported via OTLP exporter (batched mode)"

`

---

## 🚨 **UPDATED: Root Cause Found**

### **Critical Discovery: CLIENT-SIDE BUG**

After testing with the ingestion service fixes, we discovered the issue is **CLIENT-SIDE**, not backend!

**The Problem:** `enrich_span(metadata={...}, metrics={...})` is **NOT attaching** the attributes to spans.

**Expected span attributes:**
```json
{
  "honeyhive_metadata.model": "test-model",
  "honeyhive_metadata.temperature": 0.7,
  "honeyhive_metrics.input_length": 619
}
```

**Actual span attributes:**
```json
{
  "honeyhive_metadata": "\"_Span(name=\\\"evaluation_function\\\", ...)\"",
  // ❌ NO nested metadata attributes
  // ❌ NO metrics attributes at all
}
```

The `_set_span_attributes()` function in `enrich_span_core()` is supposed to create namespaced attributes but something is failing. The backend ingestion service never receives the data because it's never sent!

---

## 🚨 Original Root Cause Analysis (Now Superseded)

### Execution Flow:

```
1. evaluate() creates tracer for datapoint
   ↓
2. Tracer creates session ("initialization" event)
   ↓
3. User function executes:
   - evaluation_function span created (@trace decorator)
   - enrich_span(metrics={...}) adds to span attributes
   - invoke_summary_agent span created (nested @trace)
   - enrich_span(metadata={...}) adds to span attributes
   ↓
4. force_flush_tracer() flushes all spans
   ↓
5. OTLP exporter sends spans to backend
   ↓
6. evaluate() enriches session with outputs via PUT /events
```

### The Problem:

**Spans are exported but NOT stored as nested events in the backend.**

The OTLP ingestion service receives the spans but is not:
1. Creating child event records from the spans
2. Linking them to the parent session via `parent_id` and `children_ids`
3. Parsing the `enrich_span` attributes into the event's metadata/metrics fields

---

## 💡 Why This Happens

### Two Separate Data Flows:

1. **Session Creation (Legacy API)**
   - `POST /session/start` creates the "initialization" session
   - This is done by `HoneyHiveTracer.__init__()` 
   - Creates an Event record in the database

2. **Span Export (OTLP Protocol)**
   - Spans are sent via OTLP HTTP endpoint
   - These go through the OTLP ingestion service
   - **BUT:** The ingestion service may not be creating Event records for nested spans

### The Disconnect:

The session Event exists in the database, but the OTLP spans are either:
- Not being converted to Event records, OR
- Being stored separately and not linked to the session Event

---

## 🛠️ Expected Behavior

### What SHOULD Happen:

```json
{
  "event_id": "bb26285e-8b5c-445a-a929-1ac422345e45",
  "event_name": "initialization",
  "event_type": "session",
  "num_events": 2,  // ← Should count child events
  "children_ids": [
    "evaluation_function_span_id",
    "summary_agent_span_id"
  ],
  "children": [
    {
      "event_id": "evaluation_function_span_id",
      "event_name": "evaluation_function",
      "event_type": "chain",
      "parent_id": "bb26285e-8b5c-445a-a929-1ac422345e45",
      "metrics": {
        "input_length": 619  // ← From enrich_span()
      }
    },
    {
      "event_id": "summary_agent_span_id",
      "event_name": "summary_agent",
      "event_type": "tool",
      "parent_id": "bb26285e-8b5c-445a-a929-1ac422345e45",
      "metadata": {
        "model": "test-model",  // ← From enrich_span()
        "temperature": 0.7
      }
    }
  ]
}
```

---

## 📋 Next Steps

### 1. Backend Investigation (Priority: High)

**Check OTLP Ingestion Service:**
- Is it receiving the spans? (Check logs)
- Is it creating Event records from spans?
- Is it linking spans to sessions via `parent_id`?
- Is it parsing `honeyhive_metadata.*` and `honeyhive_metrics.*` attributes?

**File:** `hive-kube/kubernetes/ingestion_service/app/services/otel_processing_service.js`

**Look for:**
```javascript
function parseTrace(trace) {
  // ...
  // Does this create Events for all spans?
  // Does this link child spans to parent session?
  // Does this parse honeyhive_metadata.* attributes?
}
```

### 2. Client-Side Verification (Priority: Medium)

**Verify span attributes are correct:**
```python
# Check what attributes are actually on the spans
# Look in OTLP export for:
# - honeyhive_metadata.model
# - honeyhive_metadata.temperature  
# - honeyhive_metrics.input_length
```

### 3. Integration Test (Priority: High)

**Create end-to-end test:**
1. Call `evaluate()` with `@trace` + `enrich_span()`
2. Wait for ingestion
3. Query backend for session
4. Assert: `num_events == 2`
5. Assert: `children_ids` contains both spans
6. Assert: Child events have custom metadata/metrics

---

## 🎓 Key Learnings

1. **OTLP export is working** - Spans are created and sent successfully
2. **Session creation is working** - Base session Event is created
3. **Output enrichment is working** - The evaluate framework adds outputs
4. **The gap is in OTLP ingestion** - Spans aren't becoming nested Events

This is likely a **backend OTLP ingestion issue**, not a client SDK issue.

---

## 📎 Artifacts

- Test script: `nw_test.py`
- Backend checker: `check_backend_data.py`
- Session IDs: 
  - `bb26285e-8b5c-445a-a929-1ac422345e45`
  - `b357fc10-2196-488d-8dde-d3f00be0df4a`
- Run ID: `092e357a-9651-4e4a-8f42-c08bb58e6988`

