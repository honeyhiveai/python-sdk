# Agent OS Test Generation Framework v3 - Core Entry Point

## 🚨 **CRITICAL FRAMEWORK RESTORATION**

🛑 VALIDATE-GATE: Framework Core Entry Requirements
- [ ] **MANDATORY FIRST**: Command language glossary read and acknowledged ✅/❌
- [ ] V2 failure analysis understood (22% pass rate) ✅/❌
- [ ] V3 restoration mission acknowledged ✅/❌
- [ ] Binding commitment contract readiness confirmed ✅/❌

⚠️ **MANDATORY FIRST STEP**: Read [core/command-language-glossary.md](core/command-language-glossary.md)
🚨 FRAMEWORK-VIOLATION: If proceeding without command glossary acknowledgment

**Mission**: Restore 80%+ first-run pass rate by fixing V2's catastrophic regression  
**V2 Failure**: 22% pass rate due to lost archive capabilities  
**V3 Solution**: Hybrid architecture with archive depth + path-specific guidance  
**Success Metric**: 80%+ pass rate matching archive performance  

---

## 🛑 **BINDING COMMITMENT CONTRACT EXECUTION**

⚠️ MUST-READ: Framework commitment is binding and non-negotiable

**By using this framework, AI assistants commit to:**

1. **🔍 DEEP ANALYSIS EXECUTION**: Execute complete AST parsing, attribute detection, and signature extraction (not surface grep)
2. **🛤️ PATH-SPECIFIC ADHERENCE**: Follow unit (mock external dependencies) or integration (real APIs) path consistently
3. **📊 MANDATORY PROGRESS TRACKING**: Update progress table after each phase with evidence
4. **🚨 AUTOMATED VALIDATION**: Execute `validate-test-quality.py` with exit code 0 for Phase 8 completion
5. **🚫 NO FRAMEWORK SHORTCUTS**: Complete all phases systematically without bypassing analysis

**VIOLATION = FRAMEWORK FAILURE**: Shortcuts cause 22% pass rates. Complete execution achieves 80%+.

---

## 🏗️ **V3 HYBRID ARCHITECTURE**

### **📁 Framework Structure**
```
v3/
├── framework-core.md              # This file - entry point + contract
├── phase-navigation.md            # Quick checklist navigation
├── phases/                        # DETAILED phase guidance (archive depth)
│   ├── phase-1-method-verification.md    # AST parsing + attribute detection
│   ├── phase-2-logging-analysis.md       # Comprehensive logging strategy
│   ├── phase-3-dependency-analysis.md    # Complete mocking/API strategy
│   ├── phase-4-usage-patterns.md         # Deep call pattern analysis
│   ├── phase-5-coverage-analysis.md      # Branch + edge case planning
│   ├── phase-6-pre-generation.md         # Enhanced validation + readiness
│   ├── phase-7-post-generation.md        # Metrics collection
│   └── phase-8-quality-enforcement.md    # Automated validation gates
├── paths/                         # PATH-SPECIFIC guidance
│   ├── unit-path.md              # Unit: Mock everything, isolation focus
│   └── integration-path.md       # Integration: Real APIs, end-to-end focus
├── enforcement/                   # STRENGTHENED enforcement
│   ├── violation-detection.md    # Pattern recognition + responses
│   ├── quality-gates.md         # Automated gate validation
│   └── table-enforcement.md     # Mandatory progress tracking
└── archive-migration/            # Migration documentation
    ├── v2-gaps-analysis.md       # What v2 lost from archive
    └── restoration-checklist.md  # What was restored in v3
```

---

## 🚀 **FRAMEWORK EXECUTION FLOW**

### **🎯 PHASE 0: SETUP & PATH SELECTION**
1. **Environment Validation**: Verify workspace, git status, Python environment
2. **Target Analysis**: Analyze production file complexity and scope
3. **PATH SELECTION**: Choose Unit (mock external dependencies) or Integration (real APIs)
4. **Metrics Baseline**: Execute pre-generation metrics collection

### **🔍 PHASE 1: DEEP METHOD VERIFICATION**
**CRITICAL**: This phase prevents 22% failures through comprehensive analysis
- **AST Parsing**: Extract all function signatures with parameter counts
- **Attribute Detection**: Find all `object.attribute` access patterns
- **Signature Analysis**: Validate function call patterns and parameters
- **Mock Completeness**: Document all required mock attributes

**Path Integration**:
- **Unit Path**: Plan comprehensive mocking for all dependencies
- **Integration Path**: Plan real API usage with test credentials

### **📝 PHASES 2-6: COMPREHENSIVE ANALYSIS**
Each phase includes:
- **Archive-Depth Commands**: Restored from successful archive framework
- **Path-Specific Guidance**: Unit (mock) vs Integration (real) strategies
- **Mandatory Evidence**: Progress table updates with specific evidence
- **Quality Gates**: Validation checkpoints to prevent shortcuts

### **🚨 PHASE 8: AUTOMATED QUALITY ENFORCEMENT - ZERO TOLERANCE**
🚨 ZERO-TOLERANCE-ENFORCEMENT: ALL gates must pass - NO EXCEPTIONS
🚨 SUCCESS-CRITERIA-VIOLATION: Partial success = complete failure

**🚨 ABSOLUTE QUALITY REQUIREMENTS**:
- ✅ **100% test pass rate** (no failed tests allowed)
- ✅ **10.0/10 Pylint score** (exact requirement, not 9.15/10)
- ✅ **0 MyPy errors** (zero tolerance for type errors)
- ✅ **Black formatted** (consistent code style required)
- ✅ **80%+ coverage minimum** (90% target, 80% absolute minimum)

🚨 FRAMEWORK-VIOLATION: If declaring success with ANY quality gate failure
**MANDATORY**: Execute `validate-test-quality.py` with exit code 0

---

## 📊 **PROGRESS TRACKING TABLE**

**MANDATORY**: Update this table after each phase completion

| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 0: Pre-Generation Setup | ❌ | None | 0/5 | Manual | ❌ |
| 0B: Pre-Generation Metrics | ❌ | None | 0/1 | JSON Required | ❌ |
| 0C: Target Validation | ❌ | None | 0/5 | Manual | ❌ |
| 1: Method Verification | ❌ | None | 0/4 | Manual | ❌ |
| 2: Logging Analysis | ❌ | None | 0/3 | Manual | ❌ |
| 3: Dependency Analysis | ❌ | None | 0/4 | Manual | ❌ |
| 4: Usage Patterns | ❌ | None | 0/3 | Manual | ❌ |
| 5: Coverage Analysis | ❌ | None | 0/2 | Manual | ❌ |
| 6: Pre-Generation Validation | ❌ | None | 0/8 | Manual | ❌ |
| 7: Post-Generation Metrics | ❌ | None | 0/1 | JSON Required | ❌ |
| 8: **AUTOMATED QUALITY ENFORCEMENT** | ❌ | None | 0/5 | **SCRIPT EXIT CODE 0** | ❌ |

### **📋 TABLE FORMATTING STANDARDS**
- Use markdown table format with proper alignment
- Mark completed phases with ✅ status
- Include specific evidence (counts, findings, results)
- Update command completion counts (e.g., "3/4" for 3 of 4 commands executed)
- Mark validation type (Manual, JSON Required, AUTOMATED)
- Gate column shows ✅ only when phase fully complete

---

## 🛤️ **PATH-SPECIFIC EXECUTION**

### **🧪 UNIT TEST PATH**
**When to Choose**: Single module testing, dependency isolation required
**Strategy**: Mock everything - no real APIs, complete isolation
**Success Pattern**: 90%+ coverage through comprehensive mocking

**Key Requirements**:
- Mock ALL external dependencies (requests, os, sys, etc.)
- Mock ALL internal modules (honeyhive.*)
- Mock ALL configuration and environment access
- Complete mock object validation (all attributes from Phase 1)

**Reference**: [Unit Path Detailed Guidance](paths/unit-path.md)

### **🔗 INTEGRATION TEST PATH**
**When to Choose**: Multi-component testing, end-to-end validation required
**Strategy**: Real APIs - authentic system integration testing
**Success Pattern**: 80%+ coverage through real system validation

**Key Requirements**:
- Use REAL HoneyHive APIs with test credentials
- Use REAL configuration with test environment
- Use REAL logging for actual output validation
- Implement proper resource cleanup

**Reference**: [Integration Path Detailed Guidance](paths/integration-path.md)

---

## 🚨 **CRITICAL SUCCESS FACTORS**

### **🎯 80%+ Pass Rate Requirements**
1. **Complete Phase 1 Analysis**: AST parsing catches all signatures and attributes
2. **Path-Specific Execution**: Unit mocks external dependencies, Integration uses real APIs
3. **Mock Completeness**: All attributes identified in Phase 1 included in mocks
4. **Signature Accuracy**: Function calls match exact parameter counts from analysis
5. **Automated Validation**: Phase 8 script achieves exit code 0

### **💔 22% Failure Prevention**
**V2 Failures That V3 MUST Prevent**:
- Missing mock attributes (`config`, `is_main_provider`)
- Wrong function signatures (`get_tracer_logger` parameter count)
- Incomplete dependency mocking
- Framework shortcuts and bypasses

---

## 🛡️ **ENFORCEMENT MECHANISMS**

### **🚨 Automated Quality Gates**
- **Phase 8 Script**: `validate-test-quality.py` must return exit code 0
- **Progress Tracking**: Mandatory table updates prevent shortcuts
- **Violation Detection**: Specific patterns trigger enforcement responses

### **📋 Mandatory Evidence Requirements**
Each phase requires specific evidence:
- **Phase 1**: Function count, attribute list, signature analysis
- **Phase 2**: Logging call count, mock strategy documentation
- **Phase 3**: Dependency list, mocking plan, path-specific strategy
- **Phase 8**: Script output with all quality targets met

---

## 🔄 **FRAMEWORK NAVIGATION**

### **🚀 Quick Start**
1. **Read This File**: Understand commitment contract and architecture
2. **Choose Path**: Unit (mock external dependencies) or Integration (real APIs)
3. **Follow Navigation**: Use [phase-navigation.md](phase-navigation.md) for checklist
4. **Deep Dive**: Reference detailed phase files in `phases/` directory
5. **Path Guidance**: Follow path-specific strategies in `paths/` directory

### **📚 Detailed Guidance**
- **Phase Details**: Each phase has comprehensive guidance in `phases/`
- **Path Strategies**: Unit vs Integration strategies in `paths/`
- **Enforcement**: Violation detection and quality gates in `enforcement/`
- **Migration**: V2 gaps analysis and restoration docs in `archive-migration/`

---

## ✅ **SUCCESS CRITERIA**

**Framework execution is successful when:**
1. ✅ All 8 phases completed with evidence
2. ✅ Progress table shows all phases ✅
3. ✅ Path-specific strategy followed consistently
4. ✅ `validate-test-quality.py` returns exit code 0
5. ✅ Generated tests achieve 80%+ pass rate
6. ✅ No framework shortcuts or bypasses

**Framework failure indicators:**
- Phases marked complete without evidence
- Progress table not updated
- Mixed path strategies (unit + integration approaches)
- Phase 8 script failure (exit code ≠ 0)
- Generated tests with <80% pass rate

---

## 🎯 **FRAMEWORK COMMITMENT**

**This v3 framework restores the archive's proven 80%+ success rate through:**
- **Deep Analysis**: AST parsing and attribute detection
- **Path Clarity**: Clear unit (mock) vs integration (real) strategies  
- **Strong Enforcement**: Mandatory tables and automated validation
- **Comprehensive Guidance**: Detailed phase files with archive depth

**AI assistants using this framework commit to complete, systematic execution without shortcuts to achieve 80%+ first-run pass rates.**
