# Phase-by-Phase Checklist

## 🎯 **QUICK EXECUTION GUIDE**

**Use this checklist for systematic phase execution. Each phase MUST update progress table before proceeding.**

---

## 📋 **PHASE 0: PRE-GENERATION SETUP**

**🔍 Actions:**
- Validate Python environment active
- Check tox availability  
- Plan import organization strategy
- Set Black formatting approach
- Validate target file (reject `__init__.py`, `conftest.py`)

**📊 Table Update:** Mark Phase 0 complete with environment evidence
**🚪 Gate:** Cannot proceed without valid target and environment

---

## 📋 **PHASE 0B: PRE-GENERATION METRICS**

**🔍 Actions:**
- Execute: `python scripts/test-generation-metrics.py --production-file [FILE] --test-file [TARGET] --pre-generation --summary`
- Copy-paste JSON output in chat window
- Document baseline metrics file created

**📊 Table Update:** Mark Phase 0B complete with JSON evidence
**🚪 Gate:** Cannot proceed without metrics baseline

---

## 📋 **PHASE 0C: TARGET VALIDATION**

**🔍 Actions:**
- Verify target file has >50 lines business logic
- Determine test type: Unit (single module) vs Integration (multi-component)
- Validate file is appropriate for test generation
- Choose unit-path.md or integration-path.md

**📊 Table Update:** Mark Phase 0C complete with target validation evidence
**🚪 Gate:** Cannot proceed with invalid targets

---

## 📋 **PHASE 1: METHOD VERIFICATION**

**🔍 Actions:**
- Execute: `grep -n "^class\|^def\|^    def" [PRODUCTION_FILE]`
- Count total methods (public vs private)
- Identify all classes and their initialization
- Document method signatures and parameters

**📊 Table Update:** Mark Phase 1 complete with method count evidence
**🚪 Gate:** Must have complete method inventory

---

## 📋 **PHASE 2: LOGGING ANALYSIS**

**🔍 Actions:**
- Execute: `grep -n "log\." [PRODUCTION_FILE]`
- Execute: `grep -n "safe_log" [PRODUCTION_FILE]`
- Analyze all logging calls and levels
- Document conditional logging patterns

**📊 Table Update:** Mark Phase 2 complete with logging analysis evidence
**🚪 Gate:** Must understand all logging for test strategy

---

## 📋 **PHASE 3: DEPENDENCY ANALYSIS**

**🔍 Actions:**
- Execute: `grep -E "^import |^from " [PRODUCTION_FILE]`
- Identify external vs internal dependencies
- Plan mocking strategy (unit) or real API usage (integration)
- Document configuration dependencies

**📊 Table Update:** Mark Phase 3 complete with dependency analysis evidence
**🚪 Gate:** Must have complete dependency strategy

---

## 📋 **PHASE 4: USAGE PATTERNS**

**🔍 Actions:**
- Execute: `grep -r "from.*[MODULE_NAME]\|import.*[MODULE_NAME]" src/ --include="*.py"`
- Analyze how module is used in codebase
- Document common instantiation patterns
- Identify error handling scenarios

**📊 Table Update:** Mark Phase 4 complete with usage pattern evidence
**🚪 Gate:** Must understand real usage for comprehensive testing

---

## 📋 **PHASE 5: COVERAGE ANALYSIS**

**🔍 Actions:**
- Execute: `tox -e unit -- --cov=[MODULE_PATH] --cov-report=term-missing` (unit tests)
- OR plan functional validation scenarios (integration tests)
- Identify all conditional branches and error paths
- Set coverage target: 90%+ (unit) or functional validation (integration)

**📊 Table Update:** Mark Phase 5 complete with coverage planning evidence
**🚪 Gate:** Must have comprehensive coverage/validation plan

---

## 📋 **PHASE 6: PRE-GENERATION VALIDATION (ENHANCED)**

**🔍 Actions (MUST COMPLETE ALL):**
1. **Production File Quality Check:**
   - Execute: `tox -e lint -- [PRODUCTION_FILE]`
   - Execute: `black --check [PRODUCTION_FILE]`
   - Execute: `tox -e mypy -- [PRODUCTION_FILE]`

2. **Test Generation Readiness Validation:**
   - Verify import paths exist and are accessible
   - Check function signatures match expected patterns
   - Validate mock strategy against actual dependencies
   - Confirm test file naming convention compliance

3. **Quality Standards Preparation:**
   - Read linter documentation for test-specific requirements
   - Verify pytest fixture patterns are available
   - Check type annotation requirements for test methods
   - Validate mock library compatibility

4. **Template Syntax Validation:**
   - Verify test generation patterns are syntactically valid
   - Check that all required imports are available
   - Validate mock object creation patterns

**🚨 CRITICAL ENHANCEMENT:** This phase now validates test generation readiness, not just production file quality

**📊 Table Update:** Mark Phase 6 complete with comprehensive validation evidence
**🚪 Gate:** Must have complete quality plan and validated generation readiness before proceeding

---

## 📋 **PHASE 7: POST-GENERATION METRICS**

**🔍 Actions:**
- Execute: `python scripts/test-generation-metrics.py --production-file [FILE] --test-file [GENERATED] --post-generation --summary`
- Copy-paste JSON output in chat window
- Verify test pass rate, coverage, Pylint, MyPy scores

**📊 Table Update:** Mark Phase 7 complete with post-generation metrics
**🚪 Gate:** Must show actual quality metrics

---

## 📋 **PHASE 8: MANDATORY QUALITY ENFORCEMENT**

**🔍 Actions (MUST COMPLETE ALL):**
1. **Fix ALL failing tests** - 100% pass rate required (no exceptions)
2. **Fix ALL Pylint issues** - 10.0/10 score required (no exceptions)  
3. **Fix ALL MyPy errors** - 0 errors required (no exceptions)
4. **Achieve coverage target** - 90%+ unit, functional validation integration
5. **Execute automated validation** - `python .agent-os/scripts/validate-test-quality.py --test-file [FILE]`

**🚨 AUTOMATED GATE REQUIREMENT:**
```bash
# MANDATORY: Must show exit code 0 before completion
python .agent-os/scripts/validate-test-quality.py --test-file [GENERATED_FILE]
echo "Exit code: $?"  # Must be 0
```

**📊 Table Update:** Mark Phase 8 complete ONLY with automated validation exit code 0
**🚪 Gate:** **HARD STOP** - Cannot complete until script returns exit code 0
**🚫 Enforcement:** AI assistants CANNOT bypass this gate or declare completion with failing validation

**❌ PROHIBITED ACTIONS:**
- Declaring "framework complete" with failing tests
- Marking Phase 8 complete without automated validation
- Using phrases like "needs fixes" or "systematic issues identified" as completion
- Treating analysis as completion instead of continuing to fix

---

## ✅ **COMPLETION CRITERIA**

**Framework successfully completed when:**
- All 9 phases marked ✅ in progress table
- All quality targets achieved and verified
- Final metrics show perfect scores
- No rework cycles required

**🚨 Critical Reminder:** Update progress table in chat window after EVERY phase. Skipping table updates violates the framework contract.
