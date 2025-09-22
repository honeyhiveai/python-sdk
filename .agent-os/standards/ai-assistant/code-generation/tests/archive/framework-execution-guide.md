# Framework Execution Guide

## 🎯 **FRAMEWORK OVERVIEW**

**Purpose**: Understand how to execute the 9-phase test generation framework with mandatory quality enforcement.

**Next Step**: After reading this, proceed to **[Phase 0 Setup](phase-0-setup.md)**

---

## 🚨 **MANDATORY PROGRESS TRACKING TABLE**

**CRITICAL: AI MUST update this table IN THE CHAT WINDOW after each phase**

| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|------|
| 0: Pre-Generation Checklist | ❌ | None | 0/5 | ❌ |
| 0B: Pre-Generation Metrics | ❌ | **MUST SHOW JSON OUTPUT** | 0/1 | ❌ |
| 0C: Target Validation | ❌ | None | 0/5 | ❌ |
| 1: Method Verification | ❌ | None | 0/3 | ❌ |
| 2: Logging Analysis | ❌ | None | 0/3 | ❌ |
| 3: Dependency Analysis | ❌ | None | 0/4 | ❌ |
| 4: Usage Patterns | ❌ | None | 0/3 | ❌ |
| 5: Coverage Analysis | ❌ | None | 0/2 | ❌ |
| 6: Pre-Generation Linting | ❌ | None | 0/4 | ❌ |
| 7: Post-Generation Metrics | ❌ | **MUST SHOW JSON OUTPUT** | 0/1 | ❌ |
| 8: **MANDATORY QUALITY ENFORCEMENT** | ❌ | **MUST SHOW FINAL JSON** | **0/5** | ❌ |

---

## 🔒 **CHECKPOINT GATE RULES**

### **🚨 MANDATORY ENFORCEMENT**

**RULE 1: Sequential Execution**
- Cannot skip phases or proceed without completing current phase
- Each phase must show evidence of completion in progress table
- All commands must be executed and results documented

**RULE 2: Quality Gates**
- Phase 0C: Cannot proceed with invalid test targets
- Phase 6: Cannot generate tests without reading linter documentation
- Phase 8: Cannot complete until ALL quality targets met

**RULE 3: Progress Tracking**
- Must update progress table in chat after each phase
- Must show evidence of commands executed
- Must document gate status (✅ passed or ❌ blocked)

---

## 📊 **METRICS COLLECTION REQUIREMENTS**

### **🚨 MANDATORY METRICS PHASES - CANNOT BE SKIPPED**

**🛑 CRITICAL: AI MUST execute these commands and show output in chat window**

**Phase 0B: Pre-Generation Metrics (BLOCKING)**
```bash
python scripts/test-generation-metrics.py --production-file [PRODUCTION_FILE] --test-file [TARGET_TEST_FILE] --pre-generation --summary
```
**REQUIRED OUTPUT**: AI must copy-paste the formatted summary report showing baseline metrics.

**Phase 7: Post-Generation Metrics (BLOCKING)**
```bash
python scripts/test-generation-metrics.py --production-file [PRODUCTION_FILE] --test-file [GENERATED_TEST_FILE] --post-generation --summary
```
**REQUIRED OUTPUT**: AI must copy-paste the formatted summary report showing test results, coverage, Pylint score, and MyPy errors.

**Phase 8: Final Metrics (BLOCKING - After Quality Fixes)**
```bash
python scripts/test-generation-metrics.py --production-file [PRODUCTION_FILE] --test-file [FINAL_TEST_FILE] --post-generation --summary
```
**REQUIRED OUTPUT**: AI must copy-paste the formatted summary report showing final perfect quality scores with all targets met (✅).

**🚨 ENFORCEMENT**: If AI says "metrics collected" without showing actual command output, respond with:
> "STOP - Show me the actual metrics summary report. Copy-paste the formatted output in the chat window."

### **Metrics Storage**
- All metrics saved as JSON files with timestamps
- Used for framework effectiveness analysis
- Required for framework completion validation

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

## 🚀 **EXECUTION WORKFLOW**

### **Phase Flow Overview**
```
Phase 0 Setup (Common) → Test Type Decision → Specialized Path

Unit Path:                    Integration Path:
├── Unit Analysis (1-6)      ├── Integration Analysis (1-6)
├── Unit Generation          ├── Integration Generation  
└── Unit Quality (7-8)       └── Integration Quality (7-8)
```

### **File Reading Order**
1. **This file** - Framework rules and tracking
2. **[Phase 0 Setup](phase-0-setup.md)** - Common setup + test type decision
3. **Choose specialized path based on test type decision**

---

## 🚨 **ENFORCEMENT PATTERNS - PREVENTING AI SHORTCUTS**

### **⚠️ SKIP INDICATORS - IMMEDIATE STOP REQUIRED**

**If AI uses ANY of these phrases, immediately respond with "STOP - Complete Phase X checkpoint first":**

#### **Skip Indicators**
- "Let me start writing the tests..."
- "I'll generate the test file..."
- "Based on my understanding..."
- "I can see that the code..."
- "The method probably..."
- "I assume it returns..."
- "Metrics collected" (without showing actual command output)
- "I'll collect the metrics" (without executing commands)
- "Baseline metrics gathered" (without JSON output)

#### **Table Skipping Indicators (IMMEDIATE STOP)**
- "Phase X complete" (without showing updated table)
- "Moving to next phase" (without table update)
- "Analysis finished" (without table evidence)
- "Proceeding to generation" (without complete table)
- Creating/modifying files with table instead of chat window
- Referencing "progress table in file" instead of chat window

#### **Phase-Specific Violation Indicators (CRITICAL)**
**Phase 1 Violations:**
- "Method verification complete" (without table update)
- "Found X methods" (without showing updated progress table)
- "Moving to logging analysis" (without Phase 1 table evidence)

**Phase 2 Violations:**
- "Logging analysis complete" (without table update)
- "Found logging calls" (without showing updated progress table)
- "Moving to dependency analysis" (without Phase 2 table evidence)

**Phase 3 Violations:**
- "Dependencies analyzed" (without table update)
- "Mocking strategy complete" (without showing updated progress table)
- "Moving to usage patterns" (without Phase 3 table evidence)

**Phase 4 Violations:**
- "Usage patterns found" (without table update)
- "Pattern analysis complete" (without showing updated progress table)
- "Moving to coverage analysis" (without Phase 4 table evidence)

**Phase 5 Violations:**
- "Coverage planning complete" (without table update)
- "90% target set" (without showing updated progress table)
- "Moving to pre-generation linting" (without Phase 5 table evidence)

#### **Assumption Indicators**
- "I think..."
- "It should..."
- "Likely..."
- "Typically..."
- "Usually..."
- "The message is similar to..."

### **✅ REQUIRED EVIDENCE PATTERNS**

**AI MUST use these exact patterns to demonstrate proper analysis:**

#### **Method Verification Evidence**
- ✅ "I ran `grep -n 'def ' file.py` and found exactly X methods:"
- ✅ "Line 123 shows: `def method_name(self, param1: str) -> bool:`"
- ✅ "Total method count verified: X methods"

#### **Logging Analysis Evidence**
- ✅ "Exact message found: `safe_log(self, 'debug', 'exact text here')`"
- ✅ "Line 456: contains exactly this text:"
- ✅ "I copied the exact output from grep:"

#### **Dependency Analysis Evidence**
- ✅ "I read the actual implementation in file.py and found:"
- ✅ "The function returns exactly: `bool` (verified from source)"
- ✅ "Analyzed X external dependencies:"

### **🛑 ENFORCEMENT RESPONSES**

#### **When AI Skips Steps:**
> "STOP - You're skipping the framework. Complete Phase X checkpoint gate first. Show me the exact command output and evidence required."

#### **When AI Uses Assumptions:**
> "STOP - No assumptions allowed. Run the mandatory commands and show exact evidence."

#### **When AI Paraphrases:**
> "STOP - Copy-paste the exact text with line numbers. No paraphrasing allowed."

#### **When AI Rushes to Code:**
> "STOP - Complete ALL phases first. Show me the completed progress tracking table."

#### **When AI Skips Metrics:**
> "STOP - Execute the metrics command and copy-paste the JSON output. No metrics = no progression."

#### **When AI Skips Table Updates:**
> "STOP - You completed Phase X but didn't update the progress table. Show me the updated table in the chat window with Phase X marked as ✅ and evidence documented before proceeding."

#### **Phase-Specific Enforcement Responses:**
**Phase 1 Violation Response:**
> "STOP - You completed Phase 1 (Method Verification) but didn't update the progress table. Show me the updated table in the chat window with Phase 1 marked as ✅ and method count evidence documented before proceeding to Phase 2."

**Phase 2 Violation Response:**
> "STOP - You completed Phase 2 (Logging Analysis) but didn't update the progress table. Show me the updated table in the chat window with Phase 2 marked as ✅ and logging evidence documented before proceeding to Phase 3."

**Phase 3 Violation Response:**
> "STOP - You completed Phase 3 (Dependency Analysis) but didn't update the progress table. Show me the updated table in the chat window with Phase 3 marked as ✅ and dependency evidence documented before proceeding to Phase 4."

**Phase 4 Violation Response:**
> "STOP - You completed Phase 4 (Usage Patterns) but didn't update the progress table. Show me the updated table in the chat window with Phase 4 marked as ✅ and pattern evidence documented before proceeding to Phase 5."

**Phase 5 Violation Response:**
> "STOP - You completed Phase 5 (Coverage Analysis) but didn't update the progress table. Show me the updated table in the chat window with Phase 5 marked as ✅ and coverage evidence documented before proceeding to Phase 6."

#### **When AI Puts Table in Files:**
> "STOP - The progress table must be shown in the chat window, NOT in files. Copy-paste the current table here and update it with your progress."

### **📊 PROGRESS VALIDATION ENFORCEMENT**

**🚨 CRITICAL: AI must show this completed table IN CHAT WINDOW after EVERY PHASE (NOT in files):**

**🛑 TABLE UPDATE REQUIREMENT: After completing EACH phase, AI MUST:**
1. **Copy the current table from previous response**
2. **Update the completed phase row with ✅ status and evidence**
3. **Show the updated table in the chat window**
4. **NEVER skip table updates between phases**

**🚨 CRITICAL: AI must show this completed table IN CHAT WINDOW before proceeding (NOT in files):**

| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|------|
| 0: Pre-Generation Checklist | ✅ | Environment + imports planned | 5/5 | ✅ |
| 0B: Pre-Generation Metrics | ✅ | Baseline metrics collected | 1/1 | ✅ |
| 0C: Target Validation | ✅ | Valid target confirmed | 3/3 | ✅ |
| 1: Method Verification | ✅ | X methods, Y imports | 3/3 | ✅ |
| 2: Logging Analysis | ✅ | X messages, Y returns | 3/3 | ✅ |
| 3: Dependency Analysis | ✅ | X deps analyzed | 4/4 | ✅ |
| 4: Usage Patterns | ✅ | X patterns found | 3/3 | ✅ |
| 5: Coverage Analysis | ✅ | X methods, Y branches | 2/2 | ✅ |
| 6: Pre-Generation Linting | ✅ | Linter docs read | 4/4 | ✅ |
| 7: Post-Generation Metrics | ✅ | Quality metrics collected | 1/1 | ✅ |
| 8: Quality Enforcement | ✅ | All targets met | 5/5 | ✅ |

**ENFORCEMENT RULES:**
- ✅ **CORRECT**: Table shown in AI's chat responses
- ❌ **FORBIDDEN**: AI creating/modifying files with table
- ❌ **STOP**: If ANY cell shows ❌ or incomplete data

### **📋 STANDARDIZED EVIDENCE FORMAT**

**🚨 CRITICAL: Evidence column must contain specific, measurable results:**

| Phase | Evidence Format Example |
|-------|------------------------|
| **0: Pre-Generation Checklist** | `Environment active, 5 imports planned, Black strategy set` |
| **0B: Pre-Generation Metrics** | `Baseline JSON created: test_generation_metrics_[timestamp].json` |
| **0C: Target Validation** | `Valid target: [filename], 127 lines code, 3 classes found` |
| **1: Method Verification** | `Found 8 methods, 12 imports, 3 classes verified` |
| **2: Logging Analysis** | `Found 15 safe_log calls, 8 conditional branches analyzed` |
| **3: Dependency Analysis** | `Analyzed 6 external deps, 4 internal imports mapped` |
| **4: Usage Patterns** | `Found 12 usage patterns: error handling in 5 locations, validation in 3 methods, API calls use retry logic` |
| **5: Coverage Analysis** | `Target: 90%+ coverage, 23 methods, 45 branches planned` |
| **6: Pre-Generation Linting** | `Read 4 linter docs, pylint disables planned` |
| **7: Post-Generation Metrics** | `Tests pass: 100%, Coverage: 92%, Pylint: 10.0/10` |
| **8: Quality Enforcement** | `All targets met: Pass ✅, Coverage ✅, Pylint ✅, MyPy ✅` |

**🛑 INVALID EVIDENCE EXAMPLES:**
- ❌ "Analysis complete" (too vague)
- ❌ "Methods found" (no specific count)
- ❌ "Dependencies analyzed" (no details)
- ❌ "Quality good" (no metrics)

### **🎯 ENHANCED EVIDENCE FORMAT REQUIREMENTS**

**🚨 MANDATORY: Each phase must provide detailed, specific evidence that demonstrates thorough analysis:**

#### **Phase 1: Method Verification - Enhanced Evidence**
```
✅ REQUIRED FORMAT: "Found X methods, Y imports, Z classes verified"
✅ ENHANCED FORMAT: "Found 8 methods (5 public, 3 private), 12 imports (3 external, 9 internal), 3 classes verified with __init__ methods"
```

#### **Phase 2: Logging Analysis - Enhanced Evidence**
```
✅ REQUIRED FORMAT: "Found X safe_log calls, Y conditional branches analyzed"
✅ ENHANCED FORMAT: "Found 15 safe_log calls (8 debug, 4 info, 3 error), 8 conditional branches analyzed in error paths"
```

#### **Phase 3: Dependency Analysis - Enhanced Evidence**
```
✅ REQUIRED FORMAT: "Analyzed X external deps, Y internal imports mapped"
✅ ENHANCED FORMAT: "Analyzed 6 external deps (requests, json, os), 4 internal imports mapped (tracer.core, utils.logger)"
```

#### **Phase 4: Usage Patterns - Enhanced Evidence**
```
✅ REQUIRED FORMAT: "Found X usage patterns, Y error scenarios identified"
✅ ENHANCED FORMAT: "Found 12 usage patterns: error handling in 5 locations, validation in 3 methods, API calls use retry logic, file operations have error paths"
```

#### **Phase 5: Coverage Analysis - Enhanced Evidence**
```
✅ REQUIRED FORMAT: "Target: 90%+ coverage, X methods, Y branches planned"
✅ ENHANCED FORMAT: "Target: 90%+ coverage, 23 methods (18 public, 5 private), 45 branches planned (15 error paths, 12 validation branches, 18 business logic)"
```

**🎯 WHY ENHANCED EVIDENCE MATTERS:**
- **Prevents AI Hallucination**: Forces actual code examination vs. assumptions
- **Builds User Confidence**: Demonstrates thorough, systematic analysis
- **Improves Test Quality**: Better analysis foundation leads to better tests
- **Creates Accountability**: Makes it impossible to skip detailed analysis steps

**📋 EVIDENCE FORMAT GUIDELINES:**
- **REQUIRED FORMAT**: Minimum acceptable evidence (counts + basic categorization)
- **ENHANCED FORMAT**: Preferred detailed evidence (specific breakdowns + context)
- **RECOMMENDATION**: Always aim for enhanced format when analysis reveals meaningful patterns
- **ENFORCEMENT**: Required format is minimum; enhanced format builds confidence and prevents shortcuts

### **📋 TEMPLATE TABLE UPDATES BY PHASE**

**🚨 CRITICAL: Copy these exact table updates after completing each phase:**

**After Phase 0 (Pre-Generation Checklist):**
```
| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|------|
| 0: Pre-Generation Checklist | ✅ | Environment active, 5 imports planned, Black strategy set | 5/5 | ✅ |
| 0B: Pre-Generation Metrics | ❌ | None | 0/1 | ❌ |
| 0C: Target Validation | ❌ | None | 0/5 | ❌ |
| 1: Method Verification | ❌ | None | 0/3 | ❌ |
| 2: Logging Analysis | ❌ | None | 0/3 | ❌ |
| 3: Dependency Analysis | ❌ | None | 0/4 | ❌ |
| 4: Usage Patterns | ❌ | None | 0/3 | ❌ |
| 5: Coverage Analysis | ❌ | None | 0/2 | ❌ |
| 6: Pre-Generation Linting | ❌ | None | 0/4 | ❌ |
| 7: Post-Generation Metrics | ❌ | None | 0/1 | ❌ |
| 8: Quality Enforcement | ❌ | None | 0/5 | ❌ |
```

**After Phase 1 (Method Verification) - Enhanced Evidence Example:**
```
| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|------|
| 0: Pre-Generation Checklist | ✅ | Environment active, 5 imports planned, Black strategy set | 5/5 | ✅ |
| 0B: Pre-Generation Metrics | ✅ | Baseline JSON created: test_generation_metrics_[timestamp].json | 1/1 | ✅ |
| 0C: Target Validation | ✅ | Valid target: [filename], 127 lines code, 3 classes found | 5/5 | ✅ |
| 1: Method Verification | ✅ | Found 8 methods (5 public, 3 private), 12 imports (3 external, 9 internal), 3 classes verified with __init__ methods | 3/3 | ✅ |
| 2: Logging Analysis | ❌ | None | 0/3 | ❌ |
| 3: Dependency Analysis | ❌ | None | 0/4 | ❌ |
| 4: Usage Patterns | ❌ | None | 0/3 | ❌ |
| 5: Coverage Analysis | ❌ | None | 0/2 | ❌ |
| 6: Pre-Generation Linting | ❌ | None | 0/4 | ❌ |
| 7: Post-Generation Metrics | ❌ | None | 0/1 | ❌ |
| 8: Quality Enforcement | ❌ | None | 0/5 | ❌ |
```

**🚨 ENFORCEMENT**: AI MUST show similar progressive table updates after EVERY phase completion.

---

## 🔒 **FRAMEWORK COMPLETION CRITERIA**

### **✅ FRAMEWORK SUCCESSFULLY COMPLETED WHEN:**

**Progress Tracking:**
- All 9 phases marked complete (✅) in progress table
- All commands executed with evidence documented
- All checkpoint gates passed
- **🚨 MANDATORY**: Progress table shown in chat window after EVERY phase completion

**🛑 CHECKPOINT ENFORCEMENT:**
- **Phase 0 Gate**: Cannot proceed without environment validation + metrics collection
- **Phase 1-6 Gates**: Cannot proceed without updating table with specific evidence
- **Phase 7 Gate**: Cannot proceed without post-generation metrics in chat window
- **Phase 8 Gate**: Cannot complete until final metrics show perfect quality scores

**Quality Validation:**
- All quality targets achieved (100% pass, perfect Pylint, 0 MyPy errors)
- Test type specific targets met (coverage or functional validation)
- Black formatting clean

**Metrics Collection:**
- Pre-generation metrics collected (Phase 0B)
- Post-generation metrics collected (Phase 7)
- Final metrics collected after quality fixes (Phase 8)

**Documentation:**
- Progress table updated in chat window
- Evidence provided for each phase completion
- Final metrics demonstrate perfect quality scores

### **🎯 SUCCESS INDICATORS CHECKLIST**

**AI is ready to mark framework complete when they have provided:**

#### **Analysis Evidence (Phases 1-6)**
- [ ] **Exact method count** with line numbers from grep output
- [ ] **All logging messages** copy-pasted exactly (no paraphrasing)
- [ ] **All dependencies analyzed** with actual behavior documented
- [ ] **All usage patterns** documented with evidence from codebase
- [ ] **Coverage target calculated** with exact method/branch counts
- [ ] **All linter documentation** read and referenced

#### **Command Execution Evidence**
- [ ] **All mandatory commands executed** with output shown in chat
- [ ] **Pre-generation metrics JSON** copy-pasted in chat window
- [ ] **Post-generation metrics JSON** copy-pasted in chat window  
- [ ] **Final metrics JSON** copy-pasted in chat window after quality fixes
- [ ] **All three metrics files** created with timestamps

#### **Quality Achievement Evidence**
- [ ] **100% test pass rate** demonstrated
- [ ] **10.0/10 Pylint score** achieved  
- [ ] **0 MyPy errors** achieved
- [ ] **Black formatting** clean
- [ ] **Unit Test Quality**: [Unit Test Quality Standards](unit-test-quality.md#mandatory-unit-test-quality-targets) - 90%+ coverage achieved
- [ ] **Integration Test Quality**: [Integration Test Quality Standards](integration-test-quality.md#mandatory-integration-test-quality-targets) - Functional validation achieved

#### **Framework Compliance Evidence**
- [ ] **Progress table** shown in chat (not files) with all ✅
- [ ] **No skip indicators** used in AI responses
- [ ] **Required evidence patterns** used throughout
- [ ] **All checkpoint gates** passed with documented evidence

**💡 Remember**: The framework exists because AI assistants consistently skip these steps. Every checkpoint saves hours of debugging failed tests later.

---

## 🚨 **ENFORCEMENT MECHANISMS**

### **Soft Enforcement (Documentation)**
- Progress tracking table with mandatory updates
- Checkpoint gates with clear pass/fail criteria
- Quality targets with specific metrics

### **Hard Enforcement (Commands)**
- Mandatory metrics collection commands
- Required linter documentation reading
- Quality fix commands that must pass

### **Framework Integrity**
- Cannot mark complete without meeting ALL criteria
- Must demonstrate evidence of each phase completion
- Final metrics must show perfect quality scores

### **🚨 TABLE CONSISTENCY VIOLATION DETECTION**

**🛑 AUTOMATIC VIOLATION TRIGGERS - IMMEDIATE ENFORCEMENT REQUIRED:**

#### **Missing Table Updates (CRITICAL VIOLATIONS)**
- AI completes phase analysis but doesn't show updated table
- AI says "Phase X complete" without table evidence
- AI moves to next phase without updating previous phase status
- AI references table "in file" instead of showing in chat

#### **Incomplete Table Evidence (BLOCKING VIOLATIONS)**
- Evidence column shows vague descriptions ("analysis done")
- Commands column not updated with actual counts (0/3 → 3/3)
- Status remains ❌ despite claiming phase completion
- Gate column not updated to ✅ after successful completion

#### **Table Location Violations (IMMEDIATE STOP)**
- AI creates/modifies files containing progress table
- AI says "see table in [filename]" instead of chat window
- AI references external table location
- AI asks user to check file for progress instead of showing in chat

#### **Sequential Violations (FRAMEWORK BYPASS)**
- AI skips phases and updates multiple table rows at once
- AI shows completed table without demonstrating phase work
- AI jumps to code generation without complete table
- AI claims "all phases done" without progressive table updates

**🛑 ENFORCEMENT PROTOCOL:**
1. **Detect violation** using patterns above
2. **STOP immediately** with specific violation message
3. **Require correction** before allowing any progression
4. **Verify compliance** with proper table update in chat window

---

**🎯 Next Step**: Proceed to **[Phase 0 Setup](phase-0-setup.md)** to begin framework execution.
