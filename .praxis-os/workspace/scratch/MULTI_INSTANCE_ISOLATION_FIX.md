# Multi-Instance Context Isolation Fix

**Date:** October 29, 2025  
**Bug Introduced:** October 27, 2025 (commit `c15c3fd`)  
**Severity:** CRITICAL  
**Status:** ✅ FIXED

## Summary

Fixed a critical bug where `project` and `source` values leaked between tracer instances via global OpenTelemetry baggage context, causing incorrect attribution of spans to the wrong project/source.

## Root Cause

When implementing the fix for `evaluate() + enrich_span()` pattern (commit `c15c3fd`), `project` and `source` were added to `SAFE_PROPAGATION_KEYS`, which caused them to be propagated via `context.attach()` to the GLOBAL OpenTelemetry context.

This caused context leakage:
1. `tracer1` created with `source="multi_instance_test_1"` → sets global baggage
2. `tracer2` created with `source="multi_instance_test_2"` → **overwrites** global baggage
3. `tracer1.start_span()` reads from global baggage → gets `source="multi_instance_test_2"` ❌

## The Fix

### 1. Removed per-tracer values from global baggage

**File:** `src/honeyhive/tracer/processing/context.py`

```python
# BEFORE (BUGGY):
SAFE_PROPAGATION_KEYS = frozenset(
    {
        "run_id",
        "dataset_id",
        "datapoint_id",
        "honeyhive_tracer_id",
        "project",  # ❌ Per-tracer value in global context!
        "source",   # ❌ Per-tracer value in global context!
    }
)

# AFTER (FIXED):
SAFE_PROPAGATION_KEYS = frozenset(
    {
        "run_id",  # Shared across tracers in evaluate()
        "dataset_id",  # Shared across tracers in evaluate()
        "datapoint_id",  # Shared across tracers in evaluate()
        "honeyhive_tracer_id",  # Per-instance but safe for discovery
        # REMOVED: "project" - per-tracer value, from tracer instance
        # REMOVED: "source" - per-tracer value, from tracer instance
    }
)
```

### 2. Added fallback to tracer instance for project/source

**File:** `src/honeyhive/tracer/processing/span_processor.py`

```python
# BEFORE (BUGGY):
project = baggage.get_baggage("project", ctx)  # Only reads from baggage
if project:
    attributes["honeyhive.project"] = project

# AFTER (FIXED):
# Priority: tracer instance (multi-instance isolation), then baggage
project = None
if self.tracer_instance and hasattr(self.tracer_instance, "project_name"):
    project = self.tracer_instance.project_name  # ✅ From tracer instance!

if not project:
    project = baggage.get_baggage("project", ctx)  # Fallback to baggage

if project:
    attributes["honeyhive.project"] = project
```

Same pattern applied for `source`.

## Why This Works

**Per-tracer instance values** (`project`, `source`, `session_id`):
- Read from `tracer_instance` properties FIRST
- Fall back to baggage only if not found on instance
- Never propagated via global context

**Shared evaluation values** (`run_id`, `dataset_id`, `datapoint_id`):
- Propagated via global baggage (safe to share)
- Used by `evaluate()` to coordinate parallel tracer instances

**Tracer discovery** (`honeyhive_tracer_id`):
- Propagated via global baggage for decorator discovery
- Per-instance but safe because it's used for lookup, not attribution

## Test Results

### Before Fix
```
FAILED test_multi_instance_attribute_isolation
  AssertionError: assert 'multi_instance_test_2' == 'multi_instance_test_1'
```

### After Fix
```
✅ PASSED test_multi_instance_attribute_isolation
✅ PASSED test_evaluate_with_enrich_span_tracer_discovery
✅ PASSED test_evaluate_with_explicit_tracer_enrich
✅ PASSED test_evaluate_enrich_span_with_evaluation_context
✅ PASSED test_evaluate_enrich_span_error_handling
```

## Impact

### Fixed
- ✅ Multi-instance tracer isolation restored
- ✅ Correct project/source attribution per tracer
- ✅ `evaluate() + enrich_span()` still works (tracer discovery via `honeyhive_tracer_id`)

### No Regressions
- ✅ All `evaluate()` tests pass
- ✅ All `enrich_span()` tests pass
- ✅ Backend verification tests pass
- ✅ Multi-instance safety tests pass

## Key Insight

**The distinction between SHARED and PER-INSTANCE context is critical:**

| Context Type | Examples | Propagation | Source |
|--------------|----------|-------------|--------|
| **Shared** (evaluation context) | `run_id`, `dataset_id`, `datapoint_id` | ✅ Via global baggage | Shared across tracers |
| **Per-instance** (tracer identity) | `project`, `source`, `session_id` | ❌ NOT via global baggage | From tracer instance |
| **Discovery** (tracer lookup) | `honeyhive_tracer_id` | ✅ Via global baggage | Per-instance but safe |

## Related Commits

- **Introduced bug:** `c15c3fd` - "feat(tracer): implement instance method pattern for span/session enrichment (v1.0)" (Oct 27, 2025)
- **Fixed bug:** Current commit (Oct 29, 2025)

## Lessons Learned

1. **Global context is shared** - Any value in `context.attach()` affects ALL tracer instances
2. **Per-tracer values must NOT be in global context** - They will leak between instances
3. **Fallback pattern is essential** - Check tracer instance FIRST, then global context
4. **Backend verification tests catch this** - Integration tests with multiple tracers are critical

