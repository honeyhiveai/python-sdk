# V3 Test Generation Framework - AI Launcher

**🚀 AI-Friendly Entry Point for V3 Test Generation Framework**

*This document provides the simplest possible interface for AI assistants to launch the complete V3 test generation process. Follow these steps systematically for deterministic, high-quality test generation.*

---

## 🎯 **QUICK START (AI ASSISTANTS)**

### **Step 0: MANDATORY - Read Command Glossary**
🛑 EXECUTE-NOW: Read and acknowledge command definitions
⚠️ MUST-READ: [core/command-language-glossary.md](core/command-language-glossary.md)
🛑 VALIDATE-GATE: Command Language Understanding
- [ ] All 🛑 commands understood as BLOCKING ✅/❌
- [ ] All ⚠️ commands understood as MANDATORY ✅/❌
- [ ] All 📊 commands understood as EVIDENCE-REQUIRED ✅/❌
- [ ] All 🚨 commands understood as VIOLATION-CONSEQUENCES ✅/❌
🚨 FRAMEWORK-VIOLATION: If proceeding without command glossary acknowledgment

### **Step 1: Acknowledge Framework Contract**
🛑 EXECUTE-NOW: State this exact acknowledgment:
```markdown
✅ I acknowledge the V3 Framework binding contract:
- I will follow ALL 8 phases systematically
- I will NOT skip steps or claim premature completion
- I will provide quantified evidence for each phase
- I will achieve 100% pass rate + 90%+ coverage + 10.0/10 Pylint + 0 MyPy errors
- I will use automated validation (validate-test-quality.py) for final verification
```
🚨 FRAMEWORK-VIOLATION: If proceeding without exact acknowledgment above

### **Step 2: Select Test Path**
```python
# Choose ONE path - cannot mix during execution
test_paths = {
    "unit": {
        "strategy": "Mock everything external - complete isolation",
        "coverage_target": "90%+ line/branch coverage", 
        "fixtures": "mock_tracer_base, mock_safe_log, disable_tracing_for_unit_tests",
        "validation": "No real API calls, all dependencies mocked"
    },
    "integration": {
        "strategy": "Real API usage - end-to-end validation",
        "coverage_target": "Functional flow coverage (not line %)",
        "fixtures": "honeyhive_tracer, honeyhive_client, verify_backend_event", 
        "validation": "Real backend verification with verify_backend_event"
    }
}

# MANDATORY: Declare your path selection
selected_path = "unit"  # or "integration"
```

### **Step 3: Initialize Progress Tracking**
🛑 UPDATE-TABLE: Copy progress table to chat window
⚠️ MUST-READ: [core/progress-table-template.md](core/progress-table-template.md)
🛑 PASTE-OUTPUT: Complete progress table in chat window

🚨 FRAMEWORK-VIOLATION: If you proceed past Phase 1 without showing the progress table in chat

**MANDATORY TABLE FORMAT** (paste this in your next response BEFORE starting Phase 1):
```markdown
| Phase | Status | Evidence | Commands |
|-------|--------|----------|----------|
| 0. Context Loading | ⏳ PENDING | | 0/8 |
| 1. Method Verification | ⏳ PENDING | | 0/4 |
| 2. Logging Analysis | ⏳ PENDING | | 0/4 |
| 3. Dependency Analysis | ⏳ PENDING | | 0/4 |
| 4. Usage Pattern Analysis | ⏳ PENDING | | 0/4 |
| 5. Coverage Analysis | ⏳ PENDING | | 0/4 |
| 6. Pre-Generation | ⏳ PENDING | | 0/8 |
| 6.5 Pre-Write Validation | ⏳ PENDING | | 0/6 |
| 7. Test Generation & Metrics | ⏳ PENDING | | 0/5 |
| 8. Quality Validation | ⏳ PENDING | | 0/4 |
```

**🎯 PASTE THIS TABLE IN YOUR RESPONSE BEFORE EXECUTING ANY PHASES**

### **Step 4: Execute Framework Phases**
🎯 NEXT-MANDATORY: [phases/1/shared-analysis.md](phases/1/shared-analysis.md)
⚠️ MUST-COMPLETE: All 8 phases with evidence
🛑 UPDATE-TABLE: After each phase completion

🔧 **Automated Execution** (Alternative):
```bash
cd /Users/josh/src/github.com/honeyhiveai/python-sdk
python scripts/generate-test-from-framework.py \
    --file src/honeyhive/tracer/instrumentation/initialization.py \
    --type unit
```
⚠️ EVIDENCE-REQUIRED: Manual validation even if automated script used

---

## 📋 **PHASE EXECUTION CHECKLIST**

### **Phase 1: Method Verification**
- [ ] **Read**: [phases/1/shared-analysis.md](phases/1/shared-analysis.md)
- [ ] **Execute**: AST analysis, attribute detection, import mapping
- [ ] **Evidence**: Quantified method/class/import counts
- [ ] **Validation**: All production code components catalogued

### **Phase 2: Logging Analysis** 
- [ ] **Read**: [phases/2/shared-analysis.md](phases/2/shared-analysis.md)
- [ ] **Execute**: Logging call detection, safe_log analysis, level classification
- [ ] **Evidence**: Quantified logging patterns and strategy
- [ ] **Validation**: All logging interactions understood

### **Phase 3: Dependency Analysis**
- [ ] **Read**: [phases/3/shared-analysis.md](phases/3/shared-analysis.md) 
- [ ] **Execute**: Dependency mapping, external/internal analysis, config dependencies
- [ ] **Evidence**: Complete dependency inventory with mocking strategy
- [ ] **Validation**: All dependencies categorized and strategy defined

### **Phase 4: Usage Pattern Analysis**
- [ ] **Read**: [phases/4/shared-analysis.md](phases/4/shared-analysis.md)
- [ ] **Execute**: Function calls, control flow, error handling, state management
- [ ] **Evidence**: Complete usage pattern inventory
- [ ] **Validation**: All code paths and interactions identified

### **Phase 5: Coverage Analysis**
- [ ] **Read**: [phases/5/shared-analysis.md](phases/5/shared-analysis.md)
- [ ] **Execute**: Line/branch/function coverage analysis and strategy
- [ ] **Evidence**: Coverage gaps identified with improvement plan
- [ ] **Validation**: Clear path to 90%+ coverage defined

### **Phase 6: Pre-Generation Validation**
- [ ] **Read**: [phases/6/shared-analysis.md](phases/6/shared-analysis.md)
- [ ] **Execute**: Template selection, fixture integration, Pylint disable discovery
- [ ] **Evidence**: Complete generation plan with all components ready
- [ ] **Validation**: All prerequisites satisfied for generation

### **Phase 6.5: Pre-Write Standards Validation** ⛔ **ABSOLUTELY BLOCKING - NOT OPTIONAL**
- [ ] **Read**: [phases/6/pre-write-validation.md](phases/6/pre-write-validation.md)
- [ ] **Execute**: Validate planned code against ALL loaded standards from Phase 0
- [ ] **Evidence**: 6/6 validations passed (imports, types, booleans, pylint, mocking, structure)
- [ ] **⛔ MANDATORY**: Post validation results in chat using exact template from phase doc
- [ ] **BLOCKING**: Cannot proceed to Phase 7 without posting 0 violations in chat

🚨 **FRAMEWORK-VIOLATION**: If file written without completing Phase 6.5 validation

⛔ **CRITICAL**: This phase was created because AI assistants repeatedly violated standards despite loading them in Phase 0. You MUST post validation results in chat. No exceptions. If you skip this phase, you will introduce standards violations that require rework.

### **Phase 7: Test Generation**
- [ ] **Read**: [phases/7/shared-analysis.md](phases/7/shared-analysis.md)
- [ ] **Execute**: Systematic test code generation using path-specific templates
- [ ] **Evidence**: Complete test file with comprehensive coverage
- [ ] **Validation**: Generated code follows all framework patterns

### **Phase 8: Quality Validation**
- [ ] **Read**: [phases/8/shared-analysis.md](phases/8/shared-analysis.md)
- [ ] **Execute**: Automated quality validation with validate-test-quality.py
- [ ] **Evidence**: 100% pass + 90%+ coverage + 10.0/10 Pylint + 0 MyPy
- [ ] **Validation**: Script exits with code 0 (success)

---

## 🚨 **CRITICAL SUCCESS REQUIREMENTS**

### **Mandatory Quality Gates**
```python
quality_requirements = {
    "test_pass_rate": "100% - All tests must pass",
    "coverage_unit": "90%+ line and branch coverage", 
    "coverage_integration": "Complete functional flow coverage",
    "pylint_score": "10.0/10 - Perfect static analysis",
    "mypy_errors": "0 - No type checking errors",
    "black_formatting": "100% compliant - No formatting issues"
}
```

### **Automated Validation Command**
```bash
# MANDATORY: Run this command for final validation
cd /Users/josh/src/github.com/honeyhiveai/python-sdk
python scripts/validate-test-quality.py tests/unit/test_tracer_instrumentation_initialization.py

# Must return exit code 0 for framework completion
echo "Exit code: $?"
```

### **Path Adherence Enforcement**
```python
# Unit Path - MUST mock external dependencies
unit_path_requirements = {
    "no_real_apis": "All external calls mocked (requests, opentelemetry, etc.)",
    "complete_isolation": "No dependencies on external services",
    "fixture_usage": "mock_tracer_base, mock_safe_log, disable_tracing_for_unit_tests",
    "coverage_focus": "90%+ line and branch coverage"
}

# Integration Path - MUST use real APIs  
integration_path_requirements = {
    "real_apis": "Actual API calls to backend services",
    "backend_verification": "verify_backend_event for all critical interactions",
    "fixture_usage": "honeyhive_tracer, honeyhive_client, verify_backend_event",
    "coverage_focus": "End-to-end functional validation"
}
```

---

## 🛡️ **AI GUARDRAILS**

### **Execution Discipline**
- **Sequential Only**: Cannot skip phases or jump ahead
- **Evidence Required**: Each phase must provide quantified results
- **No Shortcuts**: Must execute all analysis commands and document outputs
- **Path Lock**: Once path selected, cannot deviate to other strategy

### **Quality Enforcement**
- **Automated Validation**: validate-test-quality.py must return exit code 0
- **No Manual Override**: Cannot claim completion without automated verification
- **Complete Coverage**: All identified functions/methods must be tested
- **Framework Compliance**: Generated tests must follow established patterns

### **Common Failure Prevention**
```python
# Prevent these common AI failures
failure_prevention = {
    "surface_analysis": "Must execute ALL analysis commands, not summaries",
    "premature_completion": "Cannot claim done without validation script success", 
    "path_mixing": "Cannot use integration fixtures in unit tests or vice versa",
    "incomplete_mocking": "Unit tests must mock ALL external dependencies",
    "missing_evidence": "Each phase requires quantified, documented results"
}
```

---

## 📊 **SUCCESS METRICS**

### **Framework Execution Success**
```python
success_criteria = {
    "phase_completion": "All 8 phases completed with documented evidence",
    "quality_validation": "validate-test-quality.py exits with code 0",
    "test_execution": "pytest runs successfully with 100% pass rate",
    "coverage_achievement": "Coverage targets met for selected path",
    "static_analysis": "Pylint 10.0/10 and MyPy 0 errors achieved"
}
```

### **Expected Outcomes**
- **Unit Tests**: Complete isolation with comprehensive mocking and 90%+ coverage
- **Integration Tests**: Real API validation with backend verification
- **Quality Assurance**: Automated validation confirms all requirements met
- **Maintainability**: Generated tests follow established project patterns

---

## 🚀 **EXECUTION COMMANDS**

### **Quick Automated Execution**
```bash
# Full automated framework execution
cd /Users/josh/src/github.com/honeyhiveai/python-sdk

# For unit tests
python scripts/generate-test-from-framework.py \
    --production-file src/honeyhive/tracer/instrumentation/initialization.py \
    --test-path unit \
    --output-file tests/unit/test_tracer_instrumentation_initialization.py

# For integration tests  
python scripts/generate-test-from-framework.py \
    --production-file src/honeyhive/tracer/instrumentation/initialization.py \
    --test-path integration \
    --output-file tests/integration/test_tracer_instrumentation_initialization.py

# Validate results
python scripts/validate-test-quality.py [output-file]
```

### **Manual Phase-by-Phase Execution**
```bash
# If automation fails, execute phases manually
# Start with Phase 1 and proceed systematically
# Each phase builds on the previous phase's results
# Document all evidence and validate before proceeding
```

---

## 📚 **REFERENCE DOCUMENTATION**

### **Framework Architecture**
- **Complete API**: [v3-framework-api-specification.md](../v3-framework-api-specification.md)
- **AI Foundation**: [AI-SESSION-FOUNDATION.md](AI-SESSION-FOUNDATION.md)
- **Phase Details**: [phases/README.md](phases/README.md)

### **Templates and Patterns**
- **AI-Optimized Guide**: [ai-optimized/README.md](ai-optimized/README.md)
- **Code Templates**: [ai-optimized/templates/](ai-optimized/templates/)
- **Fixture Patterns**: [ai-optimized/templates/fixture-patterns.md](ai-optimized/templates/fixture-patterns.md)

### **Quality and Validation**
- **Enforcement**: [enforcement/README.md](enforcement/README.md)
- **Validation Scripts**: [../../scripts/](../../scripts/)
- **Quality Criteria**: [enforcement/quality-gates.md](enforcement/quality-gates.md)

---

**🎯 This launcher provides the simplest possible interface for AI assistants to execute the complete V3 framework systematically. Follow the checklist, provide evidence for each phase, and use automated validation to ensure deterministic, high-quality test generation.**
