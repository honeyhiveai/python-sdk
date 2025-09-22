# Test Generation Framework - Core

## 🚨 **MANDATORY FRAMEWORK ACKNOWLEDGMENT CONTRACT**

**🛑 AI ASSISTANTS: You MUST respond with this EXACT text before proceeding:**

```
I acknowledge the critical importance of this framework and commit to following it completely:

🎯 WHY THIS FRAMEWORK EXISTS:
• The codebase has extensive pre-commit hooks that catch quality violations
• When I generate low-quality code, it creates days of rework cycles for the team
• Surface-level analysis leads to missing conditional branches and exception paths
• Rushing through phases results in 83% coverage instead of 90%+ target
• Each shortcut I take multiplies into hours of debugging and fixing later

🔒 MY BINDING COMMITMENT:
✅ All 9 phases executed systematically with deep analysis (not surface-level)
✅ Progress table updated in chat window after each phase with evidence
✅ All mandatory commands executed with output copy-pasted (no "metrics collected" claims)
✅ All checkpoint gates passed with documented evidence (no assumptions)
✅ Conditional logic analysis for ALL safe_log calls and exception branches
✅ Specific missing branch identification in coverage planning (lines X-Y analysis)
✅ Metrics collection with JSON/summary output shown (actual command execution)
✅ MANDATORY file header with pre-approved pylint disables applied to ALL test files
✅ Quality targets achieved: 100% pass rate, 90%+ coverage, 10.0/10 Pylint, 0 MyPy errors
✅ **AUTOMATED VALIDATION**: Phase 8 quality gate script MUST return exit code 0
✅ **NO PREMATURE COMPLETION**: Cannot declare "framework complete" with failing tests
✅ Framework completion criteria met before marking complete

🚨 I UNDERSTAND THE CONSEQUENCES:
• Skipping deep conditional analysis = missing critical exception paths
• Rushing through phases = failing to achieve 90%+ coverage targets  
• Making assumptions = generating code that fails pre-commit hooks
• Surface-level work = creating rework cycles that waste team time
• Each framework violation directly causes the problems this framework prevents

I commit to systematic, thorough execution over speed, understanding that proper framework execution prevents far more time waste than it creates.
```

**🚨 CRITICAL**: Without this acknowledgment, you are NOT authorized to proceed with test generation.

---

## 📊 **MANDATORY PROGRESS TRACKING TABLE**

**🛑 CRITICAL: AI MUST update this table IN THE CHAT WINDOW after each phase**

| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 0: Pre-Generation Checklist | ❌ | None | 0/5 | Manual | ❌ |
| 0B: Pre-Generation Metrics | ❌ | **MUST SHOW JSON OUTPUT** | 0/1 | JSON Required | ❌ |
| 0C: Target Validation | ❌ | None | 0/5 | Manual | ❌ |
| 1: Method Verification | ❌ | None | 0/3 | Manual | ❌ |
| 2: Logging Analysis | ❌ | None | 0/3 | Manual | ❌ |
| 3: Dependency Analysis | ❌ | None | 0/4 | Manual | ❌ |
| 4: Usage Patterns | ❌ | None | 0/3 | Manual | ❌ |
| 5: Coverage Analysis | ❌ | None | 0/2 | Manual | ❌ |
| 6: Pre-Generation Validation | ❌ | None | 0/8 | Manual | ❌ |
| 7: Post-Generation Metrics | ❌ | **MUST SHOW JSON OUTPUT** | 0/1 | JSON Required | ❌ |
| 8: **MANDATORY QUALITY ENFORCEMENT** | ❌ | **MUST SHOW SCRIPT EXIT CODE 0** | **0/5** | **AUTOMATED** | ❌ |

**🚨 NEW REQUIREMENT**: Phase 8 requires `validate-test-quality.py` exit code 0 before completion.

**🛑 TABLE UPDATE REQUIREMENT: After completing EACH phase, AI MUST:**
1. **Copy the current table from previous response**
2. **Update the completed phase row with ✅ status and evidence**
3. **Show the updated table in the chat window**
4. **NEVER skip table updates between phases**

**📊 TABLE FORMATTING STANDARDS:**
- **Evidence column**: Maximum 30 characters, use brief summaries
- **Status column**: Only ✅ or ❌ symbols
- **Consistent alignment**: All pipes must align properly
- **No text overflow**: Long evidence goes in separate paragraph below table
- **Readable in chat**: Table must display properly in chat window

---

## 🎯 **QUALITY TARGETS (NON-NEGOTIABLE)**

### **Universal Targets (All Test Types)**
| Metric | Target | Enforcement |
|--------|--------|-------------|
| **Test Pass Rate** | 100% | ✅ All tests must pass |
| **Pylint Score** | **10.0/10** | ✅ Perfect score required |
| **MyPy Errors** | 0 | ✅ No type checking issues |
| **Black Formatting** | Clean | ✅ Proper code formatting |

### **Test Type Specific Targets**
| Test Type | Success Metric | Enforcement |
|-----------|---------------|-------------|
| **Unit Tests** | 90%+ Coverage | ✅ Comprehensive line coverage |
| **Integration Tests** | Functional Validation | ✅ End-to-end workflows work |

---

## 🚀 **PHASE FLOW OVERVIEW**

### **Phase Sequence**
```
Phase 0 Setup (Common) → Test Type Decision → Specialized Path

Unit Path:                    Integration Path:
├── Unit Analysis (1-6)      ├── Integration Analysis (1-6)
├── Unit Generation          ├── Integration Generation  
└── Unit Quality (7-8)       └── Integration Quality (7-8)
```

### **Critical Decision Points**
- **Phase 0C**: Unit vs Integration test type selection
- **Phase 6**: Pre-generation quality planning
- **Phase 8**: Quality enforcement until perfect scores

### **🛑 AUTOMATED QUALITY GATES**

**Each phase MUST pass automated validation before proceeding:**

#### **Phase 8 Quality Gate Script**
```bash
# MANDATORY: Execute before declaring Phase 8 complete
python .agent-os/scripts/validate-test-quality.py --test-file [GENERATED_FILE]
```

**Script Requirements:**
- **Exit Code 0**: All quality targets met, proceed allowed
- **Exit Code 1**: Quality targets failed, MUST fix before proceeding
- **Output**: JSON with exact metrics and blocking issues

#### **Quality Gate Enforcement Rules**
- **🚫 HARD STOP**: AI cannot proceed past Phase 8 without exit code 0
- **🚫 NO BYPASS**: No "framework complete" declarations with failing gates
- **🚫 NO ASSUMPTIONS**: Must show actual script execution and results

### **Mandatory Metrics Collection**
- **Phase 0B**: Pre-generation baseline metrics
- **Phase 7**: Post-generation quality metrics  
- **Phase 8**: Final perfect quality validation with automated gate

---

## 🧭 **NAVIGATION GUIDE**

### **Start Here (Required Reading Order)**
1. **This file** - Core framework rules and commitments
2. **[phase-checklist.md](phase-checklist.md)** - Step-by-step execution guide
3. **Choose your path based on test type:**
   - **[paths/unit-path.md](paths/unit-path.md)** - Unit test generation
   - **[paths/integration-path.md](paths/integration-path.md)** - Integration test generation

### **Reference Files (Use As Needed)**
- **[enforcement-responses.md](enforcement-responses.md)** - Violation detection and responses
- **[evidence-templates.md](evidence-templates.md)** - Required output formats

### **Legacy Files (Archived)**
- Original framework files moved to `../archive/` for reference
- Use new modular structure for all new test generation

---

## 🎯 **SUCCESS CRITERIA (ENHANCED)**

**Framework is complete when ALL of these are achieved:**
- All 9 phases marked ✅ in progress table
- All quality targets achieved and verified
- **Automated validation script returns exit code 0**
- **100% test pass rate confirmed by script**
- **10.0/10 Pylint score confirmed by script**
- **0 MyPy errors confirmed by script**
- **Black formatting confirmed by script**
- Final metrics show perfect scores
- Test generation successful without rework cycles

**🚨 CRITICAL**: Framework completion requires automated validation success, not just manual analysis.

**❌ INVALID COMPLETION CRITERIA:**
- "Issues identified and documented" 
- "Systematic fixes needed"
- "Framework demonstrates analysis capability"
- Any completion declaration with failing tests or quality scores

**🚨 Remember**: This framework exists because shortcuts create rework. Every checkpoint saves hours of debugging later.

---

## 🔄 **README DRIFT PREVENTION**

**🚨 MANDATORY DRIFT DETECTION**: [See complete enforcement policy](../../../../../README.md#-mandatory-drift-detection-script)

### **📋 Mandatory Update Propagation**
When making changes to this modular framework:

1. **📤 Propagate Upward**: Update references in higher-level READMEs
   - `../README.md` (Test Generation Hub)
   - `../../../README.md` (AI Assistant Standards)
   - `../../../../README.md` (Standards Overview)  
   - `../../../../../README.md` (Top-level Agent OS)

2. **🔗 Validate Links**: Ensure all internal references work
3. **🎯 Maintain Consistency**: Keep quality targets aligned across all levels
4. **📚 Update Navigation**: Adjust framework references throughout hierarchy

### **🛡️ Drift Prevention Protocol**
**Reference**: See complete drift prevention policy in `../../../../../README.md` (lines 279-312)

**🚨 MANDATORY DRIFT DETECTION SCRIPT:**
```bash
# REQUIRED: Run after ANY changes to this modular framework
cd ../../../../../.. && python .agent-os/scripts/validate-readme-hierarchy.py
```

**🛑 BLOCKING REQUIREMENT**: Script must pass (exit code 0) before changes are considered complete.

**🚨 Remember**: Changes to the modular framework must be reflected in the entire README hierarchy!
