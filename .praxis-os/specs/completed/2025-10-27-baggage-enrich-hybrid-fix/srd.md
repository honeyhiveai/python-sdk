# Software Requirements Document

**Project:** Baggage Context + Enrich Functions Hybrid API Fix  
**Date:** 2025-10-27  
**Priority:** Critical  
**Category:** Fix + Enhancement  
**Target Release:** v1.0.0 (2025-10-31)

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for fixing baggage context propagation in the evaluate() pattern and establishing a hybrid API approach for enrich functions that balances backward compatibility with clean API design for v1.0.

### 1.2 Scope
This feature will:
- Fix baggage context propagation to enable tracer discovery in evaluate() patterns
- Establish instance methods (`tracer.enrich_span()`, `tracer.enrich_session()`) as the PRIMARY API
- Maintain free functions (`enrich_span()`, `enrich_session()`) as LEGACY via automatic discovery
- Enable successful customer onboarding by Friday (2025-10-31)
- Provide clear migration path to v2.0

---

## 2. Business Goals

### Goal 1: Enable Successful Customer Onboarding by Friday

**Objective:** Ship v1.0.0 by Friday (2025-10-31) with working evaluate() pattern to support two customers currently onboarding onto the new tracer architecture.

**Success Metrics:**
- **evaluate() pattern functionality**: Broken (tracer discovery fails) → Working (tracer discovered via baggage)
- **Customer onboarding blockers**: 2 critical blockers → 0 blockers
- **Ship date**: At risk → On track for Friday deployment

**Business Impact:**
- Unblocks two customer onboarding processes currently stalled
- Prevents customer churn from failed onboarding experience
- Demonstrates v1.0 production-readiness for multi-instance architecture
- Revenue impact: Two customers can begin production usage

### Goal 2: Maintain 100% Backward Compatibility

**Objective:** Ensure zero breaking changes for existing v0.2.x users while establishing cleaner API for new users.

**Success Metrics:**
- **Breaking changes in v1.0**: Target 0 breaking changes
- **Legacy pattern support**: All v0.2.x patterns → Continue working in v1.0
- **User code changes required**: v0.2.x users require 0 code changes
- **Deprecation timeline**: No deprecation warnings in v1.0 → Warnings in v1.1+ → Removal in v2.0

**Business Impact:**
- Existing users can upgrade to v1.0 without code changes
- Reduces upgrade friction and support burden
- Maintains customer satisfaction during architectural transition
- Provides time for gradual migration (v1.0 → v1.9 → v2.0)

### Goal 3: Establish Clean API for Long-Term Maintenance

**Objective:** Document and promote instance methods as the primary API pattern, aligned with the multi-instance architecture, while maintaining backward compatibility.

**Success Metrics:**
- **API clarity**: Mixed patterns → Clear primary (instance) + legacy (free function)
- **New user API adoption**: Target 80%+ using instance methods in new code
- **Documentation quality**: Instance methods featured in 100% of new examples
- **API consistency**: Multi-instance architecture fully aligned with API patterns

**Business Impact:**
- Reduced confusion for new developers
- Cleaner, more maintainable codebase long-term
- Better IDE support and type safety
- Foundation for v2.0 clean API (instance methods only)

### Goal 4: Fix Architectural Incompatibility

**Objective:** Resolve the fundamental incompatibility between singleton-era free functions and the new multi-instance architecture by implementing selective baggage propagation.

**Success Metrics:**
- **Tracer discovery**: Fails in evaluate() → Works via baggage propagation
- **Evaluation context propagation**: Lost (run_id, dataset_id, datapoint_id) → Preserved
- **Thread safety**: Potential session ID conflicts → Verified thread-safe with selective propagation
- **Test coverage**: 0% for baggage propagation → 90%+ coverage

**Business Impact:**
- Architectural integrity restored
- No workarounds or hacks required
- Foundation for reliable multi-instance patterns
- Reduced technical debt from incomplete refactor

---

## 2.1 Supporting Documentation

The business goals above are informed by:
- **Design Document** (`.praxis-os/workspace/design/2025-10-27-baggage-enrich-hybrid-fix.md`): Complete 40-page design including technical analysis, architecture comparison, implementation phases
- **ENRICH_SPAN_ARCHITECTURE_ANALYSIS.md**: Original vs multi-instance architecture analysis, root cause of failures
- **ENRICH_SESSION_FIX_SUMMARY.md**: Documentation of enrich_session backward compatibility fix (already completed)
- **EVALUATION_BAGGAGE_ISSUE.md**: Critical bug analysis showing disabled context.attach() breaking evaluate() pattern
- **Customer Context**: Two customers onboarding, Friday v1.0 ship date deadline

---

## 3. Stakeholders

### Primary Stakeholders

**New Customers (2 currently onboarding)**
- Need: Working evaluate() pattern out of the box
- Impact: Blocked onboarding → Successful deployment
- Success Criteria: Can use evaluate() with enrich functions without errors

**Existing v0.2.x Users**
- Need: Zero code changes to upgrade to v1.0
- Impact: Smooth upgrade path without disruption
- Success Criteria: All existing code works unchanged in v1.0

**Development Team (Josh + AI Partnership)**
- Need: Ship v1.0 by Friday, clean API for maintenance
- Impact: On-time delivery, reduced technical debt
- Success Criteria: All tests passing, documentation complete, deployed by Friday

### Secondary Stakeholders

**Future v2.0 Users**
- Need: Clear migration path from v1.0 hybrid API
- Impact: Smooth transition to instance-only API
- Success Criteria: Comprehensive migration guide, deprecation warnings, timeline clarity

**Support Team**
- Need: Clear documentation, reduced confusion
- Impact: Fewer support tickets about API usage
- Success Criteria: Instance methods prominently featured in docs

---

## 4. User Stories

### US-1: New Customer Using evaluate()

**As a** new customer onboarding with the multi-instance tracer,  
**I want** to use `evaluate()` with `enrich_span()` in my user functions,  
**So that** I can add metadata to spans during evaluation runs.

**Acceptance Criteria:**
- evaluate() automatically creates and manages tracer instances per datapoint
- enrich_span() called inside user functions discovers the correct tracer via baggage
- Evaluation context (run_id, dataset_id, datapoint_id) propagates to all spans
- No explicit tracer parameter required in user function signatures

**Priority:** Critical (P0)

**Example:**
```python
from honeyhive import evaluate, trace, enrich_span

@trace(event_type="tool")
def my_evaluation_function(datapoint):
    result = process(datapoint)
    enrich_span(metadata={"result": result})  # Should work
    return {"output": result}

evaluate(
    function=my_evaluation_function,
    dataset=[{"inputs": {}}],
    api_key="...",
    project="..."
)
```

### US-2: New Customer Learning Instance Methods

**As a** new customer reading the documentation,  
**I want** to see instance methods (`tracer.enrich_span()`) as the primary recommended pattern,  
**So that** I learn the clean, explicit API from the start.

**Acceptance Criteria:**
- README.md features instance method examples prominently
- API reference documents instance methods first
- At least 5 integration examples show instance method pattern
- Migration guide explains instance method as "recommended"

**Priority:** High (P1)

**Example:**
```python
from honeyhive import HoneyHiveTracer, trace

tracer = HoneyHiveTracer(api_key="...", project="...")

@trace(event_type="tool")
def my_function():
    result = do_work()
    tracer.enrich_span(metadata={"status": "complete"})  # PRIMARY API
    return result
```

### US-3: Existing User Upgrading to v1.0

**As an** existing user with v0.2.x code,  
**I want** to upgrade to v1.0 without changing any of my code,  
**So that** I can get bug fixes and new features without disruption.

**Acceptance Criteria:**
- All v0.2.x free function patterns continue working
- No deprecation warnings in v1.0
- No breaking changes to API signatures
- Existing tests pass without modification

**Priority:** Critical (P0)

**Example (v0.2.x code works unchanged):**
```python
from honeyhive import enrich_span, enrich_session

@trace(event_type="tool")
def my_function():
    enrich_span(metadata={"key": "value"})  # Still works

enrich_session("session-id", metadata={...})  # Still works
```

### US-4: Developer Implementing the Fix

**As a** developer implementing this fix,  
**I want** clear phase-gated tasks with validation criteria,  
**So that** I can systematically deliver the fix by Friday with confidence.

**Acceptance Criteria:**
- 5-day implementation plan with daily deliverables
- Each phase has clear success criteria
- Comprehensive test plan (unit, integration, backward compat)
- Rollback plan if issues discovered

**Priority:** Critical (P0)

---

## 5. Functional Requirements

### FR-1: Selective Baggage Propagation

**Priority:** Critical  
**Description:** Re-enable `context.attach()` with selective key propagation to fix tracer discovery while avoiding session ID conflicts.

**Requirements:**
- `_apply_baggage_context()` must propagate evaluation context keys: `run_id`, `dataset_id`, `datapoint_id`, `honeyhive_tracer_id`, `project`, `source`
- `_apply_baggage_context()` must NOT propagate instance-specific keys: `session_id`, `session_name`
- Context must be attached using `context.attach(ctx)` (currently disabled)
- Implementation must be thread-safe (OpenTelemetry guarantees this)

**Acceptance Criteria:**
- `discover_tracer()` finds correct tracer via baggage in evaluate() pattern
- Evaluation context visible in all spans
- No session ID conflicts in multi-instance scenarios
- Thread isolation verified with concurrent tracers

**Testing:**
- Unit test: Selective key propagation
- Unit test: Thread isolation (baggage per thread)
- Integration test: evaluate() + enrich_span discovery

### FR-2: Instance Method API (Primary)

**Priority:** High  
**Description:** Document and promote instance methods as the primary API for span and session enrichment.

**Requirements:**
- `HoneyHiveTracer.enrich_span()` exists and works (already implemented)
- `HoneyHiveTracer.enrich_session()` exists and works (already fixed)
- Instance methods documented with comprehensive docstrings
- Instance methods featured in README and API reference
- Examples updated to show instance method pattern

**Acceptance Criteria:**
- Docstrings clearly state "This is the PRIMARY API"
- README shows instance method examples first
- 5-10 key examples updated to instance methods
- Migration guide recommends instance methods

**Testing:**
- Unit test: Instance method functionality
- Example test: All updated examples run successfully

### FR-3: Free Function API (Legacy)

**Priority:** High  
**Description:** Maintain free functions for backward compatibility with automatic tracer discovery.

**Requirements:**
- `enrich_span()` free function continues working
- `enrich_session()` free function continues working
- Discovery uses baggage context (priority 2 fallback)
- Graceful degradation if tracer not found
- No deprecation warnings in v1.0

**Acceptance Criteria:**
- All v0.2.x free function patterns work unchanged
- Discovery succeeds via baggage in evaluate()
- No breaking changes to function signatures
- Comprehensive backward compatibility tests

**Testing:**
- Unit test: Free function discovery
- Integration test: evaluate() + free function enrich
- Backward compat test: v0.2.x patterns

### FR-4: Documentation Updates

**Priority:** High  
**Description:** Update documentation to reflect hybrid API with clear recommendations.

**Requirements:**
- README.md updated with instance method examples
- API reference updated with instance methods first
- Migration guide created with v1.0 → v2.0 timeline
- 5-10 examples updated to instance methods
- Docstrings updated with PRIMARY/LEGACY indicators

**Acceptance Criteria:**
- New users see instance methods first in docs
- Migration guide complete with code examples
- Backward compat clearly documented
- Deprecation timeline visible

**Testing:**
- Documentation build succeeds
- All code examples in docs are tested
- Links and cross-references valid

### FR-5: Testing Coverage

**Priority:** Critical  
**Description:** Comprehensive testing to ensure fix works and no regressions introduced.

**Requirements:**
- Unit tests for baggage propagation (selective keys, thread isolation)
- Integration tests for evaluate() + enrich patterns
- Multi-instance safety tests (concurrent tracers)
- Backward compatibility tests (v0.2.x patterns)
- Manual testing with real API calls

**Acceptance Criteria:**
- Test coverage ≥ 90% for changed code
- All tests passing
- No regressions in existing functionality
- Multi-instance scenarios verified safe

**Testing:**
- See Testing Plan in Section 6

---

## 6. Non-Functional Requirements

### NFR-1: Backward Compatibility

**Priority:** Critical  
**Description:** Zero breaking changes for v0.2.x users

**Requirements:**
- All v0.2.x API patterns work unchanged
- No modifications required to existing user code
- No deprecation warnings in v1.0
- Performance unchanged or improved

**Acceptance Criteria:**
- Comprehensive backward compatibility test suite passing
- Manual verification with v0.2.x code samples
- No customer support tickets about breaking changes

**Validation:**
- Run v0.2.x examples with v1.0
- Verify all pass without modification

### NFR-2: Performance

**Priority:** High  
**Description:** No performance degradation from baggage propagation fix

**Requirements:**
- Baggage propagation overhead < 1ms per call
- Discovery overhead < 1ms per call
- No memory leaks from context management
- Thread-safe without performance penalty

**Acceptance Criteria:**
- Performance benchmarks show < 5% overhead
- Memory usage stable over long-running tests
- No performance regressions in evaluate() pattern

**Validation:**
- Performance benchmarks before/after
- Load test with 100+ datapoints
- Memory profiling

### NFR-3: Code Quality

**Priority:** High  
**Description:** Maintain high code quality standards

**Requirements:**
- Pylint score ≥ 9.5
- MyPy: 0 type errors
- All pre-commit hooks pass
- Comprehensive docstrings

**Acceptance Criteria:**
- Linter clean
- Type checker clean
- Pre-commit hooks pass
- Documentation complete

**Validation:**
- Run pylint, mypy, pre-commit
- Code review

### NFR-4: Testability

**Priority:** High  
**Description:** Code changes must be thoroughly testable

**Requirements:**
- Unit tests for all new logic
- Integration tests for evaluate() pattern
- Mock-free integration tests (Agent OS standard)
- Tests cover edge cases

**Acceptance Criteria:**
- Test coverage ≥ 90%
- Tests fast (< 1 minute total)
- Tests reliable (no flaky tests)
- Clear test naming

**Validation:**
- Coverage report
- CI/CD execution

### NFR-5: Documentation Quality

**Priority:** High  
**Description:** Documentation must be clear and comprehensive

**Requirements:**
- API reference complete and accurate
- Migration guide with code examples
- Examples tested and working
- Clear recommendations (PRIMARY vs LEGACY)

**Acceptance Criteria:**
- New users understand instance method pattern
- Existing users understand backward compat
- Migration path clear for v2.0
- No ambiguity in API recommendations

**Validation:**
- Documentation review
- Example testing
- User feedback (if available)

---

## 7. Out of Scope

The following are explicitly OUT OF SCOPE for v1.0:

### Excluded Features

1. **Deprecation Warnings**
   - No deprecation warnings for free functions in v1.0
   - Deferred to v1.1+
   - Rationale: Give users time to migrate without pressure

2. **Explicit Tracer Parameters in evaluate()**
   - Not passing tracer explicitly to user functions in v1.0
   - Deferred to v2.0 consideration
   - Rationale: Breaking change, not needed with baggage fix

3. **Context Variables (contextvars) Approach**
   - Not implementing contextvars-based discovery
   - Using baggage propagation instead
   - Rationale: OpenTelemetry-native solution preferred

4. **Free Function Removal**
   - Not removing free functions in v1.0
   - Deferred to v2.0
   - Rationale: Maintain backward compatibility

5. **All Examples Migration**
   - Not updating ALL examples in v1.0
   - Only updating 5-10 key examples
   - Deferred to v1.1+
   - Rationale: Time constraint for Friday ship

6. **Comprehensive Migration Guide**
   - Basic migration guide only in v1.0
   - Comprehensive guide in v1.1+
   - Rationale: Focus on implementation over documentation

### Future Enhancements (v2.0+)

1. **Deprecation Warnings** (v1.1-v1.9)
2. **Complete Example Migration** (v1.3)
3. **Free Function Removal** (v2.0)
4. **Explicit Tracer Passing** (v2.0 consideration)
5. **Advanced Discovery Patterns** (post-v2.0)

---

## 8. Constraints

### Technical Constraints

1. **OpenTelemetry Compatibility**
   - Must use OpenTelemetry baggage API correctly
   - Cannot break OpenTelemetry context propagation

2. **Thread Safety**
   - Must be thread-safe for ThreadPoolExecutor usage
   - Cannot introduce race conditions

3. **Python Version Support**
   - Must support Python 3.8+ (existing requirement)

### Business Constraints

1. **Friday Ship Date (2025-10-31)**
   - Deadline driven by customer onboarding
   - Cannot slip schedule

2. **Zero Breaking Changes**
   - Business requirement for v1.0
   - Cannot break existing user code

3. **Resource Constraints**
   - Single developer (Josh) + AI partnership
   - 5 days available (Mon-Fri)

### Quality Constraints

1. **Test Coverage**
   - Minimum 90% for changed code
   - All tests must pass

2. **Pre-commit Hooks**
   - All hooks must pass
   - Cannot skip or bypass

3. **Documentation**
   - Must be complete for v1.0 release
   - Cannot ship with incomplete docs

---

## 9. Assumptions

1. **Baggage Propagation is Thread-Safe**
   - Assumption: OpenTelemetry baggage is thread-local
   - Validation: OpenTelemetry documentation confirms this
   - Risk: Low

2. **Selective Keys Prevent Conflicts**
   - Assumption: Only propagating evaluation context keys prevents session ID conflicts
   - Validation: Design analysis, multi-instance testing
   - Risk: Medium (requires testing)

3. **Friday Ship is Achievable**
   - Assumption: 5-day phased implementation is sufficient
   - Validation: Detailed implementation plan
   - Risk: Medium (tight timeline)

4. **Customer Acceptance**
   - Assumption: New customers will adopt instance methods
   - Validation: Clear documentation, prominent examples
   - Risk: Low

5. **Backward Compatibility Sufficient**
   - Assumption: Existing users okay with hybrid API temporarily
   - Validation: No breaking changes, clear timeline to v2.0
   - Risk: Low

---

## 10. Dependencies

### External Dependencies

1. **OpenTelemetry SDK**
   - Required for baggage propagation
   - Version: Current (already in use)
   - Risk: None (already dependency)

2. **Python Standard Library**
   - threading, contextvars (if needed)
   - Version: 3.8+
   - Risk: None

### Internal Dependencies

1. **Tracer Registry System**
   - Required for discover_tracer() to work
   - Status: Already implemented
   - Risk: None

2. **Instance Methods**
   - enrich_span() and enrich_session() instance methods
   - Status: Already exist (enrich_session fixed)
   - Risk: None

3. **Test Infrastructure**
   - pytest, integration test framework
   - Status: Already in place
   - Risk: None

### Documentation Dependencies

1. **Sphinx Build System**
   - Required for API reference updates
   - Status: Already in use
   - Risk: None

2. **Example Infrastructure**
   - Integration examples with API keys
   - Status: Already exists
   - Risk: None

---

## 11. Success Metrics

### Release Metrics (v1.0 Ship)

1. **On-Time Delivery**
   - Target: Ship by Friday 2025-10-31
   - Measurement: Git tag + PyPI deployment date

2. **Zero Breaking Changes**
   - Target: 0 breaking changes
   - Measurement: Backward compatibility test suite passing

3. **Test Coverage**
   - Target: ≥ 90% for changed code
   - Measurement: Coverage report

4. **Quality Gates**
   - Target: All pre-commit hooks pass
   - Measurement: Pylint ≥ 9.5, MyPy 0 errors

### Post-Release Metrics (Week 1)

1. **Customer Onboarding Success**
   - Target: 2 customers successfully onboarded
   - Measurement: Customer feedback, production usage

2. **No Critical Bugs**
   - Target: 0 critical bugs reported
   - Measurement: GitHub issues, support tickets

3. **Adoption of Instance Methods**
   - Target: New customers use instance methods
   - Measurement: Code review of customer implementations

4. **User Satisfaction**
   - Target: Positive feedback from existing users
   - Measurement: GitHub feedback, support sentiment

### Long-Term Metrics (v1.x series)

1. **Migration Progress**
   - Target: 50%+ users migrate to instance methods by v1.9
   - Measurement: Usage telemetry (if available)

2. **Support Ticket Reduction**
   - Target: Fewer API confusion tickets
   - Measurement: Support ticket categorization

3. **Code Quality Maintenance**
   - Target: Maintain ≥ 9.5 Pylint, 0 MyPy errors
   - Measurement: CI/CD reports

---

## 12. Risks and Mitigation

### Risk 1: Baggage Propagation Causes New Issues

**Likelihood:** Low  
**Impact:** High  
**Mitigation:**
- Selective key propagation (only safe keys)
- Extensive multi-instance testing
- Thread isolation verification
- Rollback plan: Revert to contextvars approach

### Risk 2: Friday Deadline Too Aggressive

**Likelihood:** Low  
**Impact:** High  
**Mitigation:**
- Phased implementation (Mon-Thu implementation, Fri deploy)
- RC build deployed Wednesday for preview
- Customer validation Thursday
- Contingency: Ship v1.0-rc4 Friday, v1.0 final Monday

### Risk 3: Documentation Confusion

**Likelihood:** Medium  
**Impact:** Medium  
**Mitigation:**
- Clear "Primary API" badges in docs
- Migration guide prominent
- Examples updated with comments
- Contingency: Add prominent banner linking to migration guide

### Risk 4: Backward Compatibility Break Discovered

**Likelihood:** Very Low  
**Impact:** Critical  
**Mitigation:**
- Comprehensive backward compat tests
- No API removals in v1.0
- Pre-release testing with v0.2.x code
- Contingency: Hot-fix release v1.0.1 immediately

---

## 13. Approval

This SRD requires approval from:

- [ ] **Technical Lead (Josh)** - Requirements complete and accurate
- [ ] **AI Partner** - Technical feasibility validated
- [ ] **Stakeholders** - Business goals aligned

**Approval Date:** ___________

**Approved By:** ___________

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-27  
**Next Review:** Post-v1.0 release (2025-11-04)

