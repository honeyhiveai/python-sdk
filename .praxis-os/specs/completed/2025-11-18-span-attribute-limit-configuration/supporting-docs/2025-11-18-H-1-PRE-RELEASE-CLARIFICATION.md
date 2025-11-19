# H-1 Clarification: Pre-Release Context

**Date:** 2025-11-18  
**Status:** ✅ RESOLVED - Not Applicable  
**Issue Type:** Conceptual Misunderstanding

---

## User Clarification

> "backwards compatibility, this is confusion on your part, we are in final prerelease validation / fixes, this is setting up what will be the base behavior at release, tests, etc, would need to be updated for this work, as well as any code path which is already a violation as there should be no static defined values in the codebase"

---

## Original Concern (H-1)

**Pessimistic Review Identified:**
- H-1: Backwards Compatibility Claims Are Wrong
- Concern: Changing default from 128 → 1024 breaks backward compatibility
- Proposed: Deprecation warnings, migration guide, etc.

**Why This Was Wrong:**
I was treating this as a change to an EXISTING released SDK, when in reality:
- v1.0.0 has NOT been released yet
- This is PRE-RELEASE validation and fixes
- We're establishing what WILL BE the base behavior
- There's nothing to be "backward compatible" with

---

## Corrected Understanding

### Context: Pre-Release Validation

**What this work is:**
1. ✅ Final pre-release validation and fixes
2. ✅ Establishing the BASE behavior for v1.0.0 first release
3. ✅ Setting defaults that will ship with v1.0.0
4. ✅ Updating tests to match new defaults
5. ✅ Removing any hardcoded/static limit values

**What this work is NOT:**
1. ❌ Changing existing production behavior
2. ❌ Breaking existing customer deployments
3. ❌ Requiring migration from old SDK
4. ❌ Needing deprecation warnings

### Implementation Requirements

**Phase 1 Must Include:**

1. **Update All Tests**
   - Update test assertions to expect new defaults:
     - `max_attributes=1024` (not 128)
     - `max_span_size=10485760` (10MB)
     - `max_events=1024` (not 128)
     - `max_links=128`
   - No tests should hardcode limits
   - All tests should get limits from config

2. **Remove Static Defined Values**
   - ❌ No hardcoded `128` anywhere
   - ❌ No hardcoded `1024` anywhere
   - ❌ No static limit definitions
   - ✅ All limits from `TracerConfig`
   - ✅ All limits configurable (constructor or env vars)

3. **Verify No Code Path Violations**
   - Search codebase for hardcoded limit values
   - Ensure all limit references go through config
   - No magic numbers for span limits

**Example Violations to Fix:**

```python
# ❌ BAD - Hardcoded limit
if len(span.attributes) > 128:
    logger.warning("Too many attributes")

# ✅ GOOD - From config
max_attrs = getattr(self.tracer_instance, '_max_attributes', 1024)
if len(span.attributes) > max_attrs:
    logger.warning(f"Too many attributes (limit: {max_attrs})")
```

```python
# ❌ BAD - Static default
DEFAULT_MAX_ATTRIBUTES = 128

# ✅ GOOD - From TracerConfig
# (defined in src/honeyhive/config/models/tracer.py)
max_attributes: int = Field(default=1024, ...)
```

---

## Post-v1.0.0 Behavior

**After first release, standard rules apply:**

### Future Limit Changes Would Require:

1. **Major Version Bump (v2.0.0)** - If breaking
   - Example: Changing default from 1024 → 512 (reducing)
   - Example: Removing a configuration option

2. **Minor Version Bump (v1.1.0)** - If additive
   - Example: Adding new `max_span_count` limit
   - Example: Adding new configuration options

3. **Patch Version Bump (v1.0.1)** - If bug fix
   - Example: Fixing calculation error in size limit

### Deprecation Strategy:

**If we need to change defaults post-v1.0.0:**
1. Add deprecation warning in v1.x
2. Document migration path
3. Give users 2-3 releases to adapt
4. Change default in v2.0.0

**Example:**
```python
# v1.5.0 - Deprecation warning
if max_attributes == 1024:  # Old default
    logger.warning(
        "DeprecationWarning: max_attributes default will change from 1024 to 512 in v2.0.0. "
        "Explicitly set max_attributes=1024 to keep current behavior."
    )

# v2.0.0 - New default
max_attributes: int = Field(default=512, ...)
```

---

## Action Items for Phase 1

### Week 1: Configuration + Test Updates

- [ ] Implement `max_attributes`, `max_span_size`, `max_events`, `max_links` in `TracerConfig`
- [ ] Update ALL unit tests to expect new defaults
- [ ] Update ALL integration tests to expect new defaults
- [ ] Search codebase for hardcoded `128` or `1024` values
- [ ] Verify all limit references go through config

### Verification Checklist

**Before Phase 1 completion:**

```bash
# Search for potential hardcoded limits
grep -rn "128\|1024" src/ tests/ --include="*.py" | grep -v "# MB\|MB\|1024 \* 1024"

# Should find ZERO hardcoded limit comparisons
# Should only find:
# - Comments explaining limits
# - Size calculations (e.g., 10 * 1024 * 1024 for 10MB)
# - Config field definitions
```

**What should exist:**
- ✅ Config definitions in `TracerConfig`
- ✅ Config reading in initialization
- ✅ Config propagation to components
- ✅ Test configs with explicit values

**What should NOT exist:**
- ❌ Hardcoded limit checks (`if count > 128`)
- ❌ Static limit constants (`MAX_ATTRS = 128`)
- ❌ Magic numbers in comparisons
- ❌ Limit values outside config

---

## Lessons Learned

### 1. Context is Critical

**Mistake:** Assumed this was a change to existing SDK  
**Reality:** This IS the first release

**Impact:** Wasted effort on backwards compatibility concerns that don't apply

---

### 2. Pre-Release vs Post-Release

**Pre-Release (Now):**
- Establish base behavior
- Set initial defaults
- Update tests to match
- No compatibility concerns

**Post-Release (Future):**
- Maintain compatibility
- Deprecation warnings
- Migration guides
- Semantic versioning

---

### 3. "Static Defined Values" Requirement

**User's explicit requirement:**
> "any code path which is already a violation as there should be no static defined values in the codebase"

**Interpretation:**
- All limits must be configurable
- No magic numbers for limits
- Everything goes through `TracerConfig`
- Dynamic, not static

**Why this matters:**
- Flexibility for edge cases
- Testability (can inject test values)
- Maintainability (single source of truth)
- User control (can tune for their workload)

---

## Updated H-1 Status

**Original:** 🟠 HIGH - Backwards compatibility concerns  
**Updated:** ✅ N/A - Pre-release, establishing base behavior

**Resolution:**
- Not applicable for v1.0.0 (no prior release)
- Tests will be updated as part of Phase 1
- Hardcoded limits will be removed
- Base behavior established at first release

**Remaining Work:**
- Verify no static defined values in codebase
- Update all tests to new defaults
- Ensure all limits come from config

---

## Related Documents

- **Pessimistic Review:** `.praxis-os/workspace/review/2025-11-18-span-limits-pessimistic-review.md` (H-1 section)
- **C-5 Resolution:** Rollback also N/A for same reason (pre-release)
- **Phase 1 Tasks:** All critical issues resolved, ready for implementation

---

## Conclusion

✅ **H-1 RESOLVED** - Not applicable

**Key Insight:** This is not a "change" to existing behavior - this IS the initial behavior for v1.0.0.

**Action Required:**
1. Update all tests (Phase 1)
2. Remove hardcoded limits (Phase 1)
3. Verify all limits from config (Phase 1)

**No backwards compatibility concerns for v1.0.0 release.**

