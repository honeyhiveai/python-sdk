# Agent OS V3 Testing Framework Integration

**Date**: October 2, 2025  
**Priority**: CRITICAL  
**Status**: Integrated into tasks.md  

---

## 🎯 Overview

This document confirms the integration of the **Agent OS V3 Testing Framework** into the experiments module implementation plan.

**V3 Framework Location**: `.praxis-os/standards/ai-assistant/code-generation/tests/`

---

## 🚨 CRITICAL: V3 Framework Requirements

### Mandatory Acknowledgment Contract

Before ANY test generation begins, the AI assistant MUST provide this EXACT acknowledgment:

```
I acknowledge the critical importance of this framework and commit to following it completely:

🎯 WHY THIS FRAMEWORK EXISTS:
• The codebase has extensive pre-commit hooks that catch quality violations
• When I generate low-quality code, it creates days of rework cycles for the team
• Surface-level analysis leads to missing conditional branches and exception paths
• Rushing through phases results in 83% coverage instead of 90%+ target
• Each shortcut I take multiplies into hours of debugging and fixing later

🔒 MY BINDING COMMITMENT:
✅ All 8 phases executed systematically with deep analysis (not surface-level)
✅ Progress table updated in chat window after each phase with evidence
✅ All mandatory commands executed with output copy-pasted (no "metrics collected" claims)
✅ All checkpoint gates passed with documented evidence (no assumptions)
✅ Conditional logic analysis for ALL branches and exception paths
✅ Specific missing branch identification in coverage planning (lines X-Y analysis)
✅ Metrics collection with JSON/summary output shown (actual command execution)
✅ MANDATORY file header with pre-approved pylint disables applied to ALL test files
✅ Quality targets achieved: 100% pass rate, 90%+ coverage, 10.0/10 Pylint, 0 MyPy errors
✅ Framework completion criteria met before marking complete

🚨 I UNDERSTAND THE CONSEQUENCES:
• Skipping deep conditional analysis = missing critical exception paths
• Rushing through phases = failing to achieve 90%+ coverage targets  
• Making assumptions = generating code that fails pre-commit hooks
• Surface-level work = creating rework cycles that waste team time
• Each framework violation directly causes the problems this framework prevents

I commit to systematic, thorough execution over speed, understanding that proper framework execution prevents far more time waste than it creates.
```

**🚨 WITHOUT THIS ACKNOWLEDGMENT, TEST GENERATION IS NOT AUTHORIZED.**

---

## 📋 V3 Framework 8-Phase System

### Phase 0: Pre-Generation Setup
- Environment validation
- Metrics collection (baseline)
- Target validation

### Phases 1-6: Comprehensive Analysis
- **Phase 1**: Method verification
- **Phase 2**: Logging analysis
- **Phase 3**: Dependency mapping
- **Phase 4**: Usage patterns
- **Phase 5**: Coverage planning
- **Phase 6**: Linting validation

### Phases 7-8: Quality Assurance
- **Phase 7**: Metrics collection
- **Phase 8**: Quality enforcement (loop until perfect)

**CRITICAL**: Progress table MUST be updated after EACH phase with evidence.

---

## 🎯 Quality Targets (MANDATORY)

| Test Type | Pass Rate | Coverage | Pylint | MyPy | Mock Strategy |
|-----------|-----------|----------|--------|------|---------------|
| **Unit Tests** | 100% | 90%+ | 10.0/10 | 0 errors | Required (all external deps) |
| **Integration Tests** | 100% | 80%+ | 10.0/10 | 0 errors | Forbidden (real APIs only) |
| **Backward Compat** | 100% | 90%+ | 10.0/10 | 0 errors | Required (mock experiments) |

**Quality Enforcement Loop**: Tests MUST iterate until ALL targets met.

---

## 📁 Test Files with V3 Framework

### TASK-014: Unit Tests (V3 Framework)
**Test Files**:
1. `tests/unit/experiments/test_models.py`
   - **Path**: V3 Unit Path
   - **Mocks**: All external dependencies
   - **Targets**: 100% pass, 90%+ coverage, 10.0/10 Pylint

2. `tests/unit/experiments/test_utils.py`
   - **Path**: V3 Unit Path
   - **Mocks**: hashlib, json
   - **Targets**: 100% pass, 90%+ coverage, 10.0/10 Pylint

3. `tests/unit/experiments/test_results.py`
   - **Path**: V3 Unit Path
   - **Mocks**: HoneyHive client, API responses
   - **Targets**: 100% pass, 90%+ coverage, 10.0/10 Pylint

4. `tests/unit/experiments/test_core.py`
   - **Path**: V3 Unit Path
   - **Mocks**: Tracer, API client, ThreadPoolExecutor
   - **Targets**: 100% pass, 90%+ coverage, 10.0/10 Pylint

5. `tests/unit/experiments/test_evaluators.py`
   - **Path**: V3 Unit Path
   - **Mocks**: Tracer, evaluator functions
   - **Targets**: 100% pass, 90%+ coverage, 10.0/10 Pylint

### TASK-015: Integration Tests (V3 Framework)
**Test Files**:
1. `tests/integration/test_experiment_workflow.py`
   - **Path**: V3 Integration Path
   - **Mocks**: FORBIDDEN (real APIs only)
   - **Targets**: 100% pass, 80%+ coverage, 10.0/10 Pylint

2. `tests/integration/test_external_datasets.py`
   - **Path**: V3 Integration Path
   - **Mocks**: FORBIDDEN (real APIs only)
   - **Targets**: 100% pass, 80%+ coverage, 10.0/10 Pylint

3. `tests/integration/test_backend_results.py`
   - **Path**: V3 Integration Path
   - **Mocks**: FORBIDDEN (real APIs only)
   - **Targets**: 100% pass, 80%+ coverage, 10.0/10 Pylint

4. `tests/integration/test_evaluator_integration.py`
   - **Path**: V3 Integration Path
   - **Mocks**: FORBIDDEN (real APIs only)
   - **Targets**: 100% pass, 80%+ coverage, 10.0/10 Pylint

### TASK-016: Backward Compatibility Tests (V3 Framework)
**Test Files**:
1. `tests/unit/evaluation/test_backward_compatibility.py`
   - **Path**: V3 Unit Path
   - **Mocks**: experiments module imports
   - **Targets**: 100% pass, 90%+ coverage, 10.0/10 Pylint

---

## 🔗 Framework References

### Primary Entry Points
- **V3 Framework Hub**: `.praxis-os/standards/ai-assistant/code-generation/tests/README.md`
- **V3 Framework Launcher**: `.praxis-os/standards/ai-assistant/code-generation/tests/v3/FRAMEWORK-LAUNCHER.md`
- **V3 API Specification**: `.praxis-os/standards/ai-assistant/code-generation/tests/v3/v3-framework-api-specification.md`

### Path-Specific Guides
- **V3 Unit Path**: `.praxis-os/standards/ai-assistant/code-generation/tests/v3/paths/unit-path.md`
- **V3 Integration Path**: `.praxis-os/standards/ai-assistant/code-generation/tests/v3/paths/integration-path.md`
- **Path Selection Guide**: `.praxis-os/standards/ai-assistant/code-generation/tests/v3/paths/README.md`

### Templates
- **Unit Test Template**: `.praxis-os/standards/ai-assistant/code-generation/tests/v3/ai-optimized/templates/unit-test-template.md`
- **Integration Template**: `.praxis-os/standards/ai-assistant/code-generation/tests/v3/ai-optimized/templates/integration-template.md`

### Quality Standards
- **V3 Enforcement**: `.praxis-os/standards/ai-assistant/code-generation/tests/v3/enforcement/README.md`
- **Quality Gates**: `.praxis-os/standards/ai-assistant/code-generation/tests/v3/enforcement/quality-gates.md`

---

## ✅ Integration Checklist

- [x] V3 framework requirements added to TASK-014 (Unit Tests)
- [x] V3 framework requirements added to TASK-015 (Integration Tests)
- [x] V3 framework requirements added to TASK-016 (Backward Compat Tests)
- [x] V3 framework references added to TASK-CP-01 (Standards Compliance)
- [x] Quality targets table added (unit vs integration)
- [x] Acknowledgment contract requirement documented
- [x] 8-phase system documented
- [x] Progress table requirement documented
- [x] Evidence-based execution requirement documented
- [x] Mock strategy enforcement documented (unit: required, integration: forbidden)

---

## 🚨 Critical Requirements Summary

### Before Starting ANY Test
1. ✅ Provide V3 framework acknowledgment contract (verbatim)
2. ✅ Initialize progress table
3. ✅ Reference V3 framework documentation

### During Test Generation
1. ✅ Execute all 8 phases systematically
2. ✅ Update progress table after EACH phase
3. ✅ Show command outputs (evidence-based)
4. ✅ Follow path-specific requirements (unit vs integration)
5. ✅ Apply proper mock strategy (unit: all mocks, integration: no mocks)

### Before Completing Task
1. ✅ Run quality enforcement loop
2. ✅ Achieve ALL quality targets (100% pass, 90%+/80%+ coverage, 10.0/10 Pylint, 0 MyPy)
3. ✅ Document evidence of quality achievement
4. ✅ Validate framework completion criteria met

---

## 📊 Success Metrics

**V3 Framework Success Rate**: 80%+ (proven)

**Quality Targets** (all must be met):
- ✅ 100% test pass rate
- ✅ 90%+ coverage (unit) / 80%+ coverage (integration)
- ✅ 10.0/10 Pylint score
- ✅ 0 MyPy errors
- ✅ Pre-commit hooks pass

**Failure Prevention**:
- ❌ NO test generation without acknowledgment contract
- ❌ NO phase completion without evidence
- ❌ NO framework completion without quality targets
- ❌ NO assumptions or "I'll follow the framework" shortcuts

---

## 🎯 Benefits of V3 Framework

1. **Prevents Rework**: Upfront quality prevents pre-commit hook failures
2. **Deterministic Quality**: 80%+ success rate (vs 22% without framework)
3. **Comprehensive Coverage**: Systematic analysis ensures no missed branches
4. **Automated Validation**: Quality gates prevent low-quality completion
5. **Evidence-Based**: No assumptions, all claims backed by command outputs

---

**Status**: ✅ INTEGRATED  
**Tasks Updated**: TASK-014, TASK-015, TASK-016, TASK-CP-01  
**Framework Version**: V3 (Production-Ready)  
**Success Rate**: 80%+


