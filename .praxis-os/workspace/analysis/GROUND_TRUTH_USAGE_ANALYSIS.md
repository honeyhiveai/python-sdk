# Ground Truth Usage Analysis: SDK Singular vs Plural

**Date**: November 3, 2025  
**Status**: Analysis Complete - Ready for Backend Review

---

## Executive Summary

The SDK uses **both** `ground_truth` (singular) and `ground_truths` (plural) in different contexts:

- **API Models** → `ground_truth` (singular) ✅
- **User-Facing Evaluator Signatures** → `ground_truths` (plural) ✅
- **Dataset Format** → `ground_truths` (plural) ✅
- **Session Feedback Field** → `ground_truths` (plural) ✅

**Key Finding**: The SDK converts from the API's singular `ground_truth` to the user-facing plural `ground_truths` when presenting data to users and in evaluator function signatures.

---

## Detailed Usage Breakdown

### 1. API Models (Singular: `ground_truth`)

**File**: `src/honeyhive/models/generated.py`

The API models use `ground_truth` (singular):

```python
# Datapoint Model
class Datapoint(BaseModel):
    ground_truth: Optional[Dict[str, Any]] = None  # Line 525

# CreateDatapointRequest Model
class CreateDatapointRequest(BaseModel):
    ground_truth: Optional[Dict[str, Any]] = Field(
        None, description="Expected output JSON object for the datapoint"
    )  # Lines 552-554

# UpdateDatapointRequest Model
class UpdateDatapointRequest(BaseModel):
    ground_truth: Optional[Dict[str, Any]] = Field(
        None, description="Expected output JSON object for the datapoint"
    )  # Lines 574-576
```

**Usage**: When calling the HoneyHive API for datapoints, the SDK uses `ground_truth` (singular).

**Example** (`src/honeyhive/api/datapoints.py`):
```python
# Creating a datapoint
client.datapoints.create_datapoint(
    CreateDatapointRequest(
        project=project,
        inputs=inputs,
        ground_truth=ground_truth,  # ← Singular
        # ...
    )
)
```

---

### 2. Dataset Format Conversion (Plural: `ground_truths`)

**File**: `src/honeyhive/experiments/core.py:740-749`

When fetching datapoints from the API, the SDK converts to plural for the dataset format:

```python
for dp_id in ds_response.datapoints:
    try:
        dp = client.datapoints.get_datapoint(dp_id)
        dataset_list.append(
            {
                "inputs": dp.inputs or {},
                "ground_truths": dp.ground_truth,  # ← API singular → SDK plural
                "id": dp.field_id or dp_id,
            }
        )
```

**User-Facing Dataset Format**:
```python
dataset = [
    {"inputs": {"query": "Q1"}, "ground_truths": {"answer": "A1"}},  # ← Plural
    {"inputs": {"query": "Q2"}, "ground_truths": {"answer": "A2"}},  # ← Plural
]
```

---

### 3. Evaluator Function Signatures (MIXED: Both Singular and Plural!)

#### 3a. User-Defined Evaluators (Plural: `ground_truths`)

**File**: `src/honeyhive/experiments/core.py:510-559`

User-defined evaluator functions receive `ground_truths` (plural) as the third parameter:

```python
def run_single_evaluator(
    eval_func: Callable,
    datapoint_id: str,
    inputs: Dict[str, Any],
    outputs: Any,
    ground_truths: Optional[Any],  # ← Plural parameter
) -> tuple[str, str, Any]:
    # Standard signature: evaluator(outputs, inputs, ground_truths)
    if ground_truths is not None:
        score = eval_func(outputs, inputs, ground_truths)  # ← Plural
    else:
        score = eval_func(outputs, inputs)
```

**User-Facing Evaluator Signature**:
```python
def my_evaluator(outputs, inputs, ground_truths):  # ← Plural
    """
    Args:
        outputs: Function outputs to evaluate
        inputs: Original inputs from datapoint
        ground_truths: Expected outputs from datapoint  # ← Plural
    """
    expected = ground_truths.get("answer", "")
    actual = outputs.get("answer", "")
    return {"score": 1.0 if actual == expected else 0.0}
```

#### 3b. Built-In Evaluators (Singular: `ground_truth`)

**File**: `src/honeyhive/evaluation/evaluators.py`

Built-in evaluator classes (like `ExactMatchEvaluator`, `F1ScoreEvaluator`) use `ground_truth` (singular):

```python
class BaseEvaluator:
    def evaluate(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,  # ← Singular
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Evaluate the given inputs and outputs."""
        raise NotImplementedError("Subclasses must implement evaluate method")
    
    def __call__(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,  # ← Singular
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make the evaluator callable."""
        return self.evaluate(inputs, outputs, ground_truth, **kwargs)
```

**⚠️ INCONSISTENCY DETECTED**: Built-in evaluators expect `ground_truth` (singular), but user-defined evaluators receive `ground_truths` (plural). These are called through different code paths:
- Built-in evaluators: Called via `BaseEvaluator.__call__()` with `(inputs, outputs, ground_truth)`
- User-defined evaluators: Called directly with `(outputs, inputs, ground_truths)`

**Note**: The parameter order is also different!
- Built-in: `(inputs, outputs, ground_truth)`
- User-defined: `(outputs, inputs, ground_truths)`

---

### 4. Session Feedback Storage (Plural: `ground_truths`)

**File**: `src/honeyhive/experiments/core.py:431-457`

When enriching sessions, `ground_truths` (plural) is stored in the `feedback` field:

```python
def _enrich_session_with_results(
    session_id: str,
    *,
    datapoint_id: Optional[str],
    outputs: Any,
    ground_truths: Any,  # ← Plural parameter
    evaluator_metrics: Dict[str, Dict[str, Any]],
    client: Any,
    verbose: bool,
) -> None:
    """Enrich a session with outputs, ground_truths, and evaluator metrics."""
    update_data = {}
    
    if outputs is not None:
        update_data["outputs"] = outputs
    
    # Store ground_truths in feedback field
    if ground_truths is not None:
        update_data["feedback"] = {"ground_truths": ground_truths}  # ← Plural
    
    if datapoint_id and datapoint_id in evaluator_metrics:
        update_data["metrics"] = evaluator_metrics[datapoint_id]
    
    if update_data:
        update_request = UpdateEventRequest(event_id=session_id, **update_data)
        client.events.update_event(update_request)  # ← Sends to API
```

---

### 5. Documentation Pattern (Plural: `ground_truths`)

All user-facing documentation uses `ground_truths` (plural):

**Tutorial Example** (`docs/tutorials/05-run-first-experiment.rst`):
```python
dataset = [
    {
        "inputs": {"question": "What is the capital of France?"},
        "ground_truths": {"answer": "Paris"}  # ← Plural
    },
    {
        "inputs": {"question": "What is 2 + 2?"},
        "ground_truths": {"answer": "4"}  # ← Plural
    }
]

def accuracy_evaluator(outputs, inputs, ground_truths):  # ← Plural
    expected = ground_truths.get("answer", "").lower().strip()
    actual = outputs.get("answer", "").lower().strip()
    return {"score": 1.0 if actual == expected else 0.0}
```

---

## Issue Context: `needs_ground_truth` Field

The original issue mentioned removing the "Ground Truth Enabled" toggle for evaluators:

> Remove the "Ground Truth Enabled" toggle for evaluators, and let schemas be flexible

**Current State**:
```python
# src/honeyhive/models/generated.py

class Metric(BaseModel):
    needs_ground_truth: Optional[bool] = Field(  # Line 360
        None, 
        description="Indicates if the metric requires ground truth to compute"
    )

class MetricEdit(BaseModel):
    needs_ground_truth: Optional[bool] = Field(  # Line 436
        None,
        description="Indicates if the metric requires ground truth to compute"
    )
```

**Usage**: This field is in the `Metric` and `MetricEdit` models (generated from OpenAPI spec), indicating whether an evaluator requires ground truth data.

---

## SDK Naming Convention Summary

| Context | Field Name | Location | Purpose | Notes |
|---------|-----------|----------|---------|-------|
| **API Request/Response** | `ground_truth` (singular) | `generated.py` models | HoneyHive API contract | Generated from OpenAPI spec |
| **Dataset Format** | `ground_truths` (plural) | User-facing dataset lists | User-provided test data | Converted from API's singular |
| **User-Defined Evaluators** | `ground_truths` (plural) | Evaluator function params | 3rd param: `(outputs, inputs, ground_truths)` | User-facing pattern |
| **Built-In Evaluators** | `ground_truth` (singular) | `BaseEvaluator.evaluate()` | 3rd param: `(inputs, outputs, ground_truth)` | ⚠️ Different param order! |
| **Session Feedback** | `ground_truths` (plural) | `feedback` field in events | Stored with session results | Sent to backend API |
| **Documentation** | `ground_truths` (plural) | All user-facing docs | Consistent user pattern | Tutorials, guides, examples |

---

## Questions for Backend Review

1. **API Consistency**: Does the backend API expect `ground_truth` (singular) everywhere?
   - Datapoints API: Uses `ground_truth` (singular) ✅
   - Events API: When we send `feedback: {"ground_truths": ...}`, does the backend handle the plural correctly? ⚠️
   
2. **Session Feedback Field**: When enriching sessions via `EventsAPI.update_event()`, we send:
   ```json
   {
     "event_id": "session-123",
     "feedback": {"ground_truths": {...}}
   }
   ```
   Does the backend expect `ground_truths` (plural) or `ground_truth` (singular) in the feedback field?

3. **Evaluator Parameter Inconsistency**: We have two different evaluator signatures:
   - User-defined: `(outputs, inputs, ground_truths)` - plural, outputs first
   - Built-in: `(inputs, outputs, ground_truth)` - singular, inputs first
   
   Should these be unified? Which pattern should be the standard?

4. **needs_ground_truth Field**: Is this field still used in the backend? 
   - Currently in `Metric` and `MetricEdit` models
   - Should it be removed or made more flexible per issue #4?
   - How does the backend use this field for evaluator execution?

5. **Dataset Storage**: When datasets are stored in the backend, do they use `ground_truth` or `ground_truths`?

---

## Recommendations

### Option 1: Keep Current Pattern (Recommended)
- **API**: Use `ground_truth` (singular) - matches generated models
- **SDK User-Facing**: Use `ground_truths` (plural) - better developer experience
- **Conversion Layer**: SDK handles conversion between API and user formats

**Pros**:
- Matches current implementation
- Better DX (plural makes sense for "what are the expected outputs?")
- No breaking changes

**Cons**:
- Requires conversion logic

### Option 2: Standardize on Singular
- Change all user-facing `ground_truths` to `ground_truth`
- Update documentation, examples, and evaluator signatures

**Pros**:
- Consistent with API models
- No conversion needed

**Cons**:
- **BREAKING CHANGE** for all users
- Would require migration guide
- Less intuitive (singular for a dict of multiple expected outputs)

---

## Next Steps

1. ✅ **SDK Analysis Complete**
2. ⏳ **Backend Review**: User will review backend services for consistency
3. ⏳ **Decision**: Confirm naming convention strategy
4. ⏳ **Implementation**: Apply any necessary fixes

---

## Files Analyzed

### Source Code
- `src/honeyhive/models/generated.py` - API models (singular)
- `src/honeyhive/experiments/core.py` - Dataset conversion, evaluator execution (plural)
- `src/honeyhive/api/datapoints.py` - API calls (singular)
- `src/honeyhive/evaluation/evaluators.py` - Built-in evaluators (singular in params)

### Documentation
- `docs/tutorials/05-run-first-experiment.rst` - Tutorial examples (plural)
- `docs/how-to/evaluation/creating-evaluators.rst` - Evaluator guide (plural)
- `docs/reference/experiments/evaluators.rst` - API reference (singular in some, plural in others)
- `docs/reference/experiments/core-functions.rst` - Core function docs (plural)

---

**Analysis prepared for**: Backend consistency review  
**Status**: Ready for cross-service validation

