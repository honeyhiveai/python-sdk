# Critical Migration Issue: @atrace Decorator Behavior Change

**Date**: 2025-11-12  
**Context**: Customer migrating from original SDK to rc3 (0.1.0rc3)  
**Status**: 🔴 BREAKING CHANGE NOT DOCUMENTED

## Problem

Customer was using `@atrace` on synchronous functions in original SDK, code worked fine. Now testing rc3 and getting `TypeError: object str can't be used in 'await' expression`.

## Root Cause

In rc3, `@atrace` is **async-only** - it forces async wrapping. Using it on a sync function causes:
1. The decorator wraps the sync function as async
2. LangGraph calls the function expecting sync
3. Function returns a string (e.g., "approve" or "execute")
4. The async wrapper tries to await the string return value
5. **Crash**: `TypeError: object str can't be used in 'await' expression`

## What Changed in Refactor

### Original SDK (pre-refactor)
- `@atrace` behavior: **UNKNOWN - NEEDS INVESTIGATION**
- Likely either:
  - A) Worked on both sync and async (like current `@trace`)
  - B) Had better error handling for sync functions
  - C) Different implementation that didn't force async wrapping

### rc3 (post-refactor)
- `@atrace`: Async-only, forces async wrapping
- `@trace`: Unified, auto-detects sync/async (NEW)
- **Intent**: Deprecate `@atrace` in favor of unified `@trace`

## Documentation Gaps

### 1. Migration Guide Says "No Breaking Changes"
```
docs/how-to/migration-compatibility/migration-guide.rst:524
**No Breaking Changes in v0.1.0+**
This release maintains 100% backwards compatibility.
```

**PROBLEM**: This is **FALSE** if `@atrace` behavior changed!

### 2. Decorator Docs Say "both work identically"
```
docs/reference/api/decorators.rst:322
Alias for @trace specifically for async functions (both work identically).
```

**PROBLEM**: They do NOT work identically! 
- `@atrace` = async-only
- `@trace` = auto-detects sync/async

### 3. No Migration Warning for @atrace Users
The migration guide doesn't say:
- ⚠️ If you used `@atrace` on sync functions, replace with `@trace`
- ⚠️ `@atrace` is now async-only
- ⚠️ Use `@trace` for all new code (unified decorator)

## Impact

**SEVERITY**: 🔴 HIGH

**Affects**:
- Any customer using `@atrace` on sync functions
- LangGraph users (routing functions are often sync)
- Framework integrations with sync callbacks

**Result**:
- Code that worked in original SDK breaks in rc3
- Error is cryptic (TypeError about awaiting strings)
- No warning at decorator application time

## What We Need to Do

### 1. Immediate (Pre-1.0.0 Release)

**Update Migration Guide:**
```rst
Breaking Changes
================

.. warning::
   **@atrace Decorator Behavior Change**
   
   The ``@atrace`` decorator is now **async-only**. If you were using ``@atrace`` 
   on synchronous functions in the original SDK, you must switch to ``@trace``.
   
   **Before (Original SDK):**
   
   .. code-block:: python
   
      @atrace
      def sync_function(data):
          return process(data)
   
   **After (v0.1.0+):**
   
   .. code-block:: python
   
      @trace  # Use unified @trace decorator
      def sync_function(data):
          return process(data)
   
   The ``@trace`` decorator now auto-detects sync/async and works with both.
```

**Update Decorator Docs:**
```rst
@atrace Decorator
-----------------

.. deprecated:: 0.1.0
   Use ``@trace`` instead. The ``@trace`` decorator now auto-detects sync/async.

.. warning::
   **Async Functions Only**
   
   The ``@atrace`` decorator only works with async functions. For synchronous 
   functions, use ``@trace``.
```

### 2. Investigate Original SDK Behavior

**Action**: Check original SDK source to understand what changed
- How did `@atrace` work on sync functions in old SDK?
- Was this intentional or accidental compatibility?

### 3. Consider Runtime Warning

**Option**: Add warning when `@atrace` is used on sync function:
```python
@atrace
def sync_func():  # <-- Should log warning
    pass
```

Warning message:
```
⚠️ @atrace decorator used on synchronous function 'sync_func'. 
   @atrace is async-only. Use @trace for automatic sync/async detection.
   This may cause unexpected behavior.
```

### 4. Consider Graceful Degradation

**Option**: Make `@atrace` auto-detect like `@trace` and log deprecation warning:
```python
if not asyncio.iscoroutinefunction(func):
    logger.warning(
        f"@atrace used on sync function '{func.__name__}'. "
        "This is deprecated. Use @trace for sync functions."
    )
    # Fall back to sync behavior for backwards compatibility
```

## Customer Response

**Immediate Fix** (for this customer):
```python
# Change from:
@atrace
def should_approve(state: AgentState) -> Literal["approve", "execute"]:
    ...

# To:
@trace  # <-- Unified decorator, works on sync and async
def should_approve(state: AgentState) -> Literal["approve", "execute"]:
    ...
```

**Explanation**:
"The `@atrace` decorator in v0.1.0+ is async-only. Your `should_approve` function 
is synchronous, so you need to use the unified `@trace` decorator instead. The 
`@trace` decorator auto-detects whether your function is sync or async and handles 
both correctly."

## Open Questions

1. **Did original SDK `@atrace` work on sync functions?** 
   - Need to check old source code
   - If YES: This is a breaking change that needs documentation
   - If NO: Customer's code was already broken?

2. **How many customers are affected?**
   - Check if other customers use `@atrace` on sync functions
   - Search codebase examples for patterns

3. **Should we deprecate `@atrace` entirely?**
   - Since `@trace` now does everything
   - Keep `@atrace` as alias for backwards compat?
   - Or make it match `@trace` behavior?

## Decision Needed

**Option A**: Document as breaking change, require migration
- Pro: Clear separation of concerns
- Con: Breaks backwards compatibility claim

**Option B**: Make `@atrace` match `@trace` behavior
- Pro: True backwards compatibility
- Con: `@atrace` name becomes meaningless

**Option C**: Add runtime warning but allow sync usage
- Pro: Graceful migration path
- Con: Technical debt, confusing API

**Recommendation**: **Option A** + clear migration guide + runtime warning
- Document the breaking change honestly
- Provide clear migration path
- Add warning to help developers catch the issue
- Deprecate `@atrace` in favor of `@trace`

