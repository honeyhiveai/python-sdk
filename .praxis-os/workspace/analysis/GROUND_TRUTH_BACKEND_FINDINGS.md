# Ground Truth Backend Analysis - CRITICAL BUG FOUND

**Date**: November 3, 2025  
**Status**: 🚨 **CRITICAL BUG IDENTIFIED** 🚨  
**Impact**: Ground truth data not being stored correctly, breaking metrics and UI

---

## Executive Summary

**FINDING**: The backend uses `ground_truth` (singular) **exclusively**, but the SDK is sending `ground_truths` (plural) when enriching sessions.

**IMPACT**:
- ❌ Ground truth data stored under wrong key (`feedback.ground_truths` instead of `feedback.ground_truth`)
- ❌ Metrics with `needs_ground_truth=true` fail to find ground truth data
- ❌ UI doesn't display ground truth (looks for `feedback.ground_truth`)
- ❌ LLM evaluators can't access ground truth via `{{feedback.ground_truth}}` template variable

---

## Backend Ground Truth Convention

### ✅ **Backend Standard: `ground_truth` (SINGULAR)**

All backend services use **singular** `ground_truth`:

#### 1. **Datapoint Storage** (API Models)
**Location**: OpenAPI spec → generated models

```typescript
// Datapoint schema
{
  inputs: Record<string, any>,
  ground_truth: Record<string, any>,  // ← SINGULAR
  history: Array<Record<string, any>>,
  metadata: Record<string, any>
}
```

#### 2. **Event Feedback Field**
**Location**: `ingestion_service/app/services/new_event_validation.js:81-86`

```javascript
if (eventMetadata.hasOwnProperty('ground_truth') && eventMetadata['ground_truth']) {
  if (!event.hasOwnProperty('feedback')) {
    event['feedback'] = {};
  }
  event['feedback']['ground_truth'] = eventMetadata['ground_truth'];  // ← SINGULAR
  delete event['metadata']['ground_truth'];
}
```

**Backend behavior**: Moves `metadata.ground_truth` → `feedback.ground_truth` (SINGULAR)

#### 3. **Metric Evaluation**
**Location**: `evaluation_service/app/services/metric_update_service.js:484`

```javascript
const needsGroundTruthButMissing = metric.needs_ground_truth && !event.feedback.ground_truth;
// ↑ Checks for SINGULAR ground_truth
```

**Location**: `evaluation_service/app/services/metric_update_service.js:550`

```javascript
const needsGroundTruthButMissing = metric.needs_ground_truth && !event.feedback.ground_truth;
```

**Behavior**: Metrics marked with `needs_ground_truth=true` check for `event.feedback.ground_truth` (SINGULAR)

#### 4. **LLM Evaluator Templates**
**Location**: `beekeeper_service/app/test-suites/integration/evaluation/evaluation.flaky.test.js:360`

```javascript
criteria: `Compare answer to ground truth: {{outputs.content}} vs {{feedback.ground_truth}}`
//                                                                     ↑ SINGULAR
```

**Location**: `beekeeper_service/app/test-suites/integration/evaluation/evaluation.flaky.test.js:438`

```javascript
criteria: `Compare the answer to the ground truth and rate accuracy from 1-5. 
           Question: {{inputs.prompt}} 
           Answer: {{outputs.content}} 
           Ground Truth: {{feedback.ground_truth}}  // ← SINGULAR
           Rating: [[rating]]`
```

**Behavior**: LLM evaluators reference `{{feedback.ground_truth}}` in prompt templates

#### 5. **Python Metric Templates**
**Location**: `frontend_service/public/metric_templates/python/semantic_similarity.py:30`

```python
ground_truth = event["feedback"]["ground_truth"]  # Access ground truth from feedback
# ↑ SINGULAR
```

**Location**: `frontend_service/public/metric_templates/python/rouge_l.py:29`

```python
ground_truth = event["feedback"]["ground_truth"]  # Reference text
```

**Location**: `frontend_service/public/metric_templates/python/bleu.py:29`

```python
reference = event["feedback"]["ground_truth"]  # Reference translation
```

**Behavior**: All Python metric templates access `event["feedback"]["ground_truth"]` (SINGULAR)

#### 6. **Frontend UI Display**
**Location**: `frontend_service/src/partials/evaluations/ReviewMode.tsx:290-294`

```typescript
{currentEvent?.feedback.ground_truth && (
  <div className="mt-2">
    <ReactMarkdown>{currentEvent.feedback.ground_truth}</ReactMarkdown>
  </div>
)}
```

**Location**: `frontend_service/src/partials/evaluations/FocusedReviewMode.tsx:367-371`

```typescript
{currentEvent?.feedback.ground_truth && (
  <div className="text-xs">
    <ReactMarkdown>{currentEvent.feedback.ground_truth}</ReactMarkdown>
  </div>
)}
```

**Behavior**: UI displays `feedback.ground_truth` (SINGULAR)

---

## SDK Bug: Sending Plural `ground_truths`

### ❌ **SDK Current Behavior: Sends `ground_truths` (PLURAL)**

**Location**: `src/honeyhive/experiments/core.py:449-450`

```python
# ❌ BUG: Sends PLURAL to backend that expects SINGULAR
if ground_truths is not None:
    update_data["feedback"] = {"ground_truths": ground_truths}  # ← WRONG!
```

**What happens**:
1. SDK sends `{"event_id": "session-123", "feedback": {"ground_truths": {...}}}`
2. Backend stores it under `feedback.ground_truths`
3. Metrics check `feedback.ground_truth` → **NOT FOUND** ❌
4. UI checks `feedback.ground_truth` → **NOT FOUND** ❌
5. LLM evaluators reference `{{feedback.ground_truth}}` → **EMPTY** ❌

---

## User-Facing SDK Pattern (Keep This!)

The SDK's **user-facing** pattern of using `ground_truths` (plural) is actually **good UX**:

```python
# User provides dataset with plural (makes sense - "what are the expected truths?")
dataset = [
    {"inputs": {"query": "Q1"}, "ground_truths": {"answer": "A1"}},
    {"inputs": {"query": "Q2"}, "ground_truths": {"answer": "A2"}},
]

# User-defined evaluators receive plural (consistent with dataset format)
def my_evaluator(outputs, inputs, ground_truths):
    expected = ground_truths.get("answer", "")
    actual = outputs.get("answer", "")
    return {"score": 1.0 if actual == expected else 0.0}
```

**Recommendation**: Keep the user-facing plural pattern, but **convert to singular when sending to backend**.

---

## The Fix

### Required Changes in SDK

**File**: `src/honeyhive/experiments/core.py:449-450`

```python
# ❌ BEFORE (BUG):
if ground_truths is not None:
    update_data["feedback"] = {"ground_truths": ground_truths}

# ✅ AFTER (FIX):
if ground_truths is not None:
    update_data["feedback"] = {"ground_truth": ground_truths}  # ← Convert to SINGULAR
    # Note: Variable name stays plural (user-facing), but key is singular (backend-facing)
```

**Rationale**:
- **User-facing SDK API**: Keep `ground_truths` (plural) for better DX
- **Backend communication**: Use `ground_truth` (singular) to match backend schema
- **Conversion layer**: SDK handles translation between user convention and backend convention

---

## Additional Finding: Built-In Evaluator Signature Mismatch

### Issue

Built-in evaluators use **different signature** than user-defined evaluators:

| Evaluator Type | Signature | Parameter Name | Notes |
|----------------|-----------|----------------|-------|
| **User-Defined** | `(outputs, inputs, ground_truths)` | Plural | Outputs first |
| **Built-In** | `(inputs, outputs, ground_truth)` | Singular | Inputs first |

**Example - Built-In Evaluator**:
```python
# src/honeyhive/evaluation/evaluators.py
class BaseEvaluator:
    def evaluate(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,  # ← SINGULAR
        **kwargs: Any,
    ) -> Dict[str, Any]:
```

**Example - User-Defined Evaluator**:
```python
# src/honeyhive/experiments/core.py
def run_single_evaluator(
    eval_func: Callable,
    datapoint_id: str,
    inputs: Dict[str, Any],
    outputs: Any,
    ground_truths: Optional[Any],  # ← PLURAL
) -> tuple[str, str, Any]:
    if ground_truths is not None:
        score = eval_func(outputs, inputs, ground_truths)  # ← (outputs, inputs, ground_truths)
```

**Impact**: 
- Creates confusion for users
- Different documentation patterns
- Can't easily swap between built-in and user-defined evaluators

**Recommendation**: 
- **Short term**: Document this difference clearly
- **Long term**: Consider unifying signatures in v2.0 (breaking change)
- **Most likely**: Align built-in evaluators to user-facing pattern: `(outputs, inputs, ground_truths)`

---

## Test Coverage Gap

The SDK's integration tests don't validate that ground truth data is correctly retrievable from the backend after enrichment.

**Missing test scenario**:
```python
def test_evaluate_ground_truth_stored_correctly():
    """Verify ground truth is accessible to metrics after evaluate()."""
    
    def my_function(datapoint):
        return {"answer": "test"}
    
    result = evaluate(
        function=my_function,
        dataset=[
            {"inputs": {"q": "test"}, "ground_truths": {"answer": "expected"}}
        ],
        evaluators=[],  # No evaluators for this test
        api_key=api_key,
        project="ground-truth-test"
    )
    
    # Fetch the session from backend
    session_id = result.session_id
    event = client.events.get_event(session_id)
    
    # ✅ Should be stored as feedback.ground_truth (singular)
    assert "ground_truth" in event.feedback
    assert event.feedback["ground_truth"] == {"answer": "expected"}
    
    # ❌ Should NOT be stored as ground_truths (plural)
    assert "ground_truths" not in event.feedback
```

---

## Action Items

### Priority 1: Fix Critical Bug (BLOCKER for metrics)
- [ ] Change `feedback: {"ground_truths": ...}` → `feedback: {"ground_truth": ...}` in `_enrich_session_with_results()`
- [ ] Keep user-facing `ground_truths` parameter name (internal SDK convention)
- [ ] Add comment explaining the conversion
- [ ] Update unit tests if they assert on the feedback key name

### Priority 2: Add Integration Test
- [ ] Add backend verification test for ground truth storage
- [ ] Verify `feedback.ground_truth` (singular) is accessible
- [ ] Verify metrics with `needs_ground_truth=true` can access it

### Priority 3: Document Signature Difference
- [ ] Add note to docs about built-in vs user-defined evaluator signatures
- [ ] Clarify when to use each pattern

### Priority 4: Consider Future Unification (v2.0)
- [ ] Align built-in evaluator signature to match user-defined pattern
- [ ] Create migration path for users
- [ ] Update all documentation

---

## Files Analyzed

### Backend Services
- `ingestion_service/app/services/new_event_validation.js` - Event preprocessing
- `evaluation_service/app/services/metric_update_service.js` - Metric execution
- `backend_service/app/routes/utils.js` - API utilities
- `frontend_service/public/metric_templates/python/*.py` - Metric templates
- `frontend_service/src/partials/evaluations/*.tsx` - UI components
- `beekeeper_service/app/test-suites/integration/evaluation/*.test.js` - Backend tests

### SDK Source
- `src/honeyhive/experiments/core.py` - evaluate() implementation
- `src/honeyhive/evaluation/evaluators.py` - Built-in evaluators
- `src/honeyhive/models/generated.py` - API models

---

**Next Step**: Fix the critical bug by changing the feedback key from plural to singular when sending to backend.

