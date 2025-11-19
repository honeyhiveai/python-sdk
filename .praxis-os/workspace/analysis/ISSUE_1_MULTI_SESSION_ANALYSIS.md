# Issue 1: Multi-Session Support Analysis

**Question**: Should we keep `session_id` parameter in `tracer.enrich_session()` to support multiple sessions per tracer instance?

---

## Two Paths for `enrich_session()`

### Path 1: Free Function (Backwards Compatibility)
```python
# NOT bound to a tracer - session_id REQUIRED
from honeyhive import enrich_session

enrich_session(
    session_id="some-session-id",  # ← Required (no tracer context)
    metadata={"key": "value"},
    tracer=my_tracer  # ← Optional tracer to use
)
```
**Verdict**: This needs `session_id` parameter because it has no tracer instance context.

### Path 2: Instance Method (Recommended v1.0+)
```python
# Bound to tracer instance - session_id optional?
tracer = HoneyHiveTracer.init(api_key="...", project="...")

tracer.enrich_session(
    session_id="some-session-id",  # ← Question: Keep this?
    metadata={"key": "value"}
)
```
**Question**: Does the tracer support managing multiple sessions?

---

## Current Architecture: Single Session Per Tracer

### Evidence from Codebase

**1. Session ID is Set Once at Init** (`src/honeyhive/tracer/core/base.py:248-255`):
```python
# Session management attributes (both public and private for compatibility)
self.session_name = config.get("session_name")
self.session_id = config.get("session_id") or (
    config.get("session", {}).get("session_id")
    if isinstance(config.get("session"), dict)
    else None
)

self._session_name = self.session_name  # Private version for internal use
self._session_id = self.session_id  # Private version for internal use
```

**2. Session Created/Validated at Init** (`src/honeyhive/tracer/instrumentation/initialization.py:1010-1015`):
```python
# Handle session ID initialization
if tracer_instance.session_id:
    # Validate existing session ID
    _validate_session_id(tracer_instance)
else:
    # Create new session
    _create_new_session(tracer_instance)
```

**3. No Dynamic Session Switching Found**:
- ✅ `tracer.session_id = "..."` is assigned during init
- ✅ `tracer.session_id = "..."` is updated during validation/creation
- ❌ **No pattern found** for users changing `tracer.session_id` to switch sessions
- ❌ **No public API** like `tracer.switch_session(new_id)`

### Span-Level Session Override

**The decorator DOES support per-span session override** (`src/honeyhive/tracer/instrumentation/decorators.py:364-365`):
```python
if params.session_id is not None:
    enrich_kwargs["session_id"] = params.session_id
```

**Usage**:
```python
tracer = HoneyHiveTracer.init(api_key="...", project="...", session_id="default-session")

@trace(session_id="different-session")  # ← Override at SPAN level
def my_function():
    # This span goes to "different-session"
    pass
```

---

## Your Architectural Question

> "should we still keep it as an optional param to allow for flexibility in supporting multiple sessions in a single tracer instance?"

### Scenario: Multiple Sessions with One Tracer

**Use Case**:
```python
# Tracer has default session
tracer = HoneyHiveTracer.init(
    api_key="...",
    project="...",
    session_id="default-session-123"
)

# Create spans for different sessions
@trace(tracer=tracer, session_id="session-A")  # ← Spans go to session-A
def process_user_a():
    pass

@trace(tracer=tracer, session_id="session-B")  # ← Spans go to session-B
def process_user_b():
    pass

# But what about session enrichment?
tracer.enrich_session(
    session_id="session-A",  # ← Enrich session-A (not default)
    metadata={"user": "alice"}
)

tracer.enrich_session(
    session_id="session-B",  # ← Enrich session-B (not default)
    metadata={"user": "bob"}
)
```

### Current Support Level

**What Works**:
1. ✅ **Spans can target different sessions** via `@trace(session_id="...")`
2. ✅ **Session enrichment can target different sessions** via `tracer.enrich_session(session_id="...")`

**What's Unclear**:
1. ❓ **Is this the intended design?** One tracer managing multiple sessions?
2. ❓ **Or is it a vestigial pattern?** From when global functions needed explicit session_id?

---

## Three Design Options

### Option A: Remove `session_id` (Strict Single-Session Architecture)

**Philosophy**: Each tracer manages ONE session. For multiple sessions, create multiple tracers.

```python
# One tracer per session
tracer_a = HoneyHiveTracer.init(api_key="...", session_id="session-A")
tracer_b = HoneyHiveTracer.init(api_key="...", session_id="session-B")

# Enrich respective sessions
tracer_a.enrich_session(metadata={"user": "alice"})  # ← No session_id param
tracer_b.enrich_session(metadata={"user": "bob"})    # ← No session_id param
```

**Pros**:
- ✅ Cleaner API - one responsibility per tracer
- ✅ Less confusion about which session is "current"
- ✅ Matches multi-instance pattern philosophy

**Cons**:
- ❌ Breaking change for any code using explicit `session_id`
- ❌ Users must manage multiple tracer instances
- ❌ More memory overhead (though multi-instance pattern already does this)

### Option B: Keep `session_id` (Flexible Multi-Session Support)

**Philosophy**: One tracer can manage multiple sessions dynamically.

```python
# One tracer, multiple sessions
tracer = HoneyHiveTracer.init(api_key="...", session_id="default-session")

# Enrich different sessions explicitly
tracer.enrich_session(session_id="session-A", metadata={"user": "alice"})
tracer.enrich_session(session_id="session-B", metadata={"user": "bob"})
tracer.enrich_session(metadata={"default": "data"})  # ← Uses tracer's default session
```

**Pros**:
- ✅ Maintains backwards compatibility
- ✅ Flexibility for advanced use cases
- ✅ Matches span-level override pattern (`@trace(session_id="...")`)
- ✅ Single tracer can orchestrate multiple sessions

**Cons**:
- ❌ More complex mental model
- ❌ Potential confusion: "Which session am I enriching?"
- ❌ The tracer still has ONE default session (`self._session_id`)

### Option C: Deprecate, Then Remove (Gradual Migration)

**Philosophy**: Move to single-session per tracer, but give users time to migrate.

**v1.x**: Deprecation warning
```python
tracer.enrich_session(
    session_id="other-session",  # ← Warns: "session_id parameter deprecated"
    metadata={"key": "value"}
)
# Warning: session_id parameter in enrich_session() is deprecated.
# Use separate tracer instances for multiple sessions, or use enrich_event() directly.
```

**v2.0**: Parameter removed
```python
tracer.enrich_session(metadata={"key": "value"})  # ← session_id removed
```

**Pros**:
- ✅ Clear migration path
- ✅ Doesn't break existing code immediately
- ✅ Encourages better architecture (one tracer per session)

**Cons**:
- ❌ Deprecation period maintenance burden
- ❌ Still need to support parameter until v2.0

---

## Recommended Decision Framework

### Questions to Answer

1. **Is multi-session per tracer a supported pattern?**
   - Do you have customers using one tracer for multiple sessions?
   - Is this documented as a feature?
   - Are there internal use cases that rely on this?

2. **What's the tracer's responsibility?**
   - Is a tracer a "session manager" (manages many sessions)?
   - Or is a tracer a "session context" (IS a session)?

3. **How does this relate to multi-instance architecture?**
   - The multi-instance pattern already creates separate tracers
   - Is multi-session per tracer redundant with multi-instance?

### If Multi-Session is Intended:

**KEEP `session_id` parameter** (Option B)
- Document it clearly as a feature
- Add tests for multi-session enrichment
- Make it explicit that tracer can manage multiple sessions
- Consider adding `tracer.switch_session(id)` or `tracer.set_default_session(id)` for clarity

### If Single-Session is Intended:

**REMOVE `session_id` parameter** (Option A or C)
- Each tracer = one session
- For multiple sessions, create multiple tracers (already supported via multi-instance)
- Simpler mental model
- Aligns with multi-instance philosophy

---

## Current State Assessment

Based on code analysis:

**The architecture SEEMS to assume single-session per tracer**:
- Session ID set once at init
- No dynamic session switching API
- No clear documentation of multi-session pattern
- Private `_session_id` suggests it's internal state, not frequently changed

**But the parameter EXISTS for flexibility**:
- Marked as "backwards compatibility" in docs
- Allows override when needed
- Matches span-level override pattern

**My Interpretation**: 
The `session_id` parameter was kept for backwards compatibility with the old free function pattern (`enrich_session(session_id="...", tracer=tracer)`), but the recommended v1.0+ pattern is **one tracer per session**.

---

## Recommendation

**Option C (Deprecate, Then Remove)** with clarification:

1. **v1.x Behavior**:
   - Keep `session_id` parameter for backwards compat
   - Add note in docs: "For managing multiple sessions, create separate tracer instances (multi-instance pattern)"
   - Optionally add deprecation warning when `session_id != tracer._session_id`

2. **v2.0 Behavior**:
   - Remove `session_id` parameter from instance method
   - Keep it in free function (which is also deprecated, but for different reasons)
   - Document multi-instance as the way to manage multiple sessions

3. **If Multi-Session IS Needed**:
   - Add explicit API: `tracer.enrich_session_by_id(session_id, metadata={})`
   - Keep `tracer.enrich_session()` for default session
   - Clear separation of "enrich my session" vs "enrich some other session"

---

## What I Need From You

**Please clarify**:

1. **Is multi-session per tracer a supported use case?**
   - Have you seen customers do this?
   - Is it intended to work this way?

2. **What's the recommended pattern for multi-session scenarios?**
   - Create multiple tracers? (multi-instance)
   - Use one tracer with explicit session_ids?

3. **Decision**: Which option?
   - **Option A**: Remove now (breaking change)
   - **Option B**: Keep forever (feature)
   - **Option C**: Deprecate then remove (migration)
   - **Option D**: Keep but rename/clarify (e.g., `enrich_session_by_id()`)

Once you clarify the intended architecture, I can implement the appropriate solution.


