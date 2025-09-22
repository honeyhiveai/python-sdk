# Phase Navigation - Quick Checklist

## 🚀 **QUICK FRAMEWORK NAVIGATION**

🛑 VALIDATE-GATE: Phase Navigation Entry Requirements
- [ ] **MANDATORY FIRST**: Command language glossary read and acknowledged ✅/❌
- [ ] Framework core commitment contract acknowledged ✅/❌
- [ ] Phase execution order understood ✅/❌
- [ ] Navigation checklist commitment confirmed ✅/❌

⚠️ **MANDATORY FIRST STEP**: [core/command-language-glossary.md](core/command-language-glossary.md)
🚨 FRAMEWORK-VIOLATION: If proceeding without command glossary or skipping phases

**Entry Point**: [Framework Core](framework-core.md) - Read first for commitment contract  
**Success Metric**: 80%+ first-run pass rate (vs V2's 22% failure)  
**Path Selection**: Unit (mock external dependencies) or Integration (real APIs)  

---

## 🛑 **PHASE EXECUTION CHECKLIST EXECUTION**

⚠️ MUST-READ: All phases must be completed systematically in order

### **🎯 PHASE 0: SETUP & PATH SELECTION**
- [ ] **Environment Validation**: Verify workspace, git, Python
- [ ] **Pre-Generation Metrics**: Execute metrics collection script
- [ ] **Target Analysis**: Analyze production file (>50 lines)
- [ ] **PATH SELECTION**: Choose Unit or Integration path
- [ ] **Update Progress Table**: Mark Phase 0 complete with evidence

**Detailed Guidance**: [Phase 0 Setup](phases/phase-0-setup.md)

---

### **🔍 PHASE 1: METHOD VERIFICATION (CRITICAL)**
- [ ] **AST Function Analysis**: Extract all function signatures with parameters
- [ ] **Attribute Detection**: Find all `object.attribute` access patterns  
- [ ] **Function Call Analysis**: Identify all function calls with parameter counts
- [ ] **Mock Completeness Planning**: Document all required mock attributes
- [ ] **Update Progress Table**: Mark Phase 1 complete with evidence

**⚠️ CRITICAL**: This phase prevents 22% failures through deep analysis  
**Detailed Guidance**: [Phase 1 Method Verification](phases/phase-1-method-verification.md)

---

### **📝 PHASE 2: LOGGING ANALYSIS**
- [ ] **Logging Call Detection**: Find all safe_log and logger calls
- [ ] **Mock Strategy Planning**: Plan logging mock approach (unit) or real logging (integration)
- [ ] **Conditional Logging Analysis**: Identify logging branches and levels
- [ ] **Update Progress Table**: Mark Phase 2 complete with evidence

**Detailed Guidance**: [Phase 2 Logging Analysis](phases/phase-2-logging-analysis.md)

---

### **📦 PHASE 3: DEPENDENCY ANALYSIS**
- [ ] **Import Analysis**: Extract all external and internal dependencies
- [ ] **Mocking Strategy**: Plan unit (mock all) or integration (real APIs) approach
- [ ] **Configuration Dependencies**: Identify config and environment dependencies
- [ ] **Update Progress Table**: Mark Phase 3 complete with evidence

**Detailed Guidance**: [Phase 3 Dependency Analysis](phases/phase-3-dependency-analysis.md)

---

### **🔄 PHASE 4: USAGE PATTERNS**
- [ ] **Call Pattern Analysis**: Identify how functions are actually called
- [ ] **Parameter Usage**: Analyze parameter passing patterns
- [ ] **Return Value Usage**: Understand return value handling
- [ ] **Update Progress Table**: Mark Phase 4 complete with evidence

**Detailed Guidance**: [Phase 4 Usage Patterns](phases/phase-4-usage-patterns.md)

---

### **📊 PHASE 5: COVERAGE ANALYSIS**
- [ ] **Branch Analysis**: Identify all conditional branches for testing
- [ ] **Edge Case Planning**: Plan boundary and error condition tests
- [ ] **Coverage Target Setting**: Set path-specific coverage goals
- [ ] **Update Progress Table**: Mark Phase 5 complete with evidence

**Detailed Guidance**: [Phase 5 Coverage Analysis](phases/phase-5-coverage-analysis.md)

---

### **🔧 PHASE 6: PRE-GENERATION VALIDATION**
- [ ] **Import Path Validation**: Verify all imports work correctly
- [ ] **Function Signature Validation**: Confirm all signatures are correct
- [ ] **Mock Strategy Validation**: Verify mock completeness requirements
- [ ] **Path Strategy Confirmation**: Confirm unit vs integration approach
- [ ] **Update Progress Table**: Mark Phase 6 complete with evidence

**Detailed Guidance**: [Phase 6 Pre-Generation Validation](phases/phase-6-pre-generation.md)

---

### **⚡ TEST GENERATION**
- [ ] **Generate Test File**: Create comprehensive test file using analysis
- [ ] **Apply Path Strategy**: Use unit (mock external dependencies) or integration (real APIs)
- [ ] **Include All Requirements**: All attributes, signatures, dependencies from analysis

**Path-Specific Guidance**:
- **Unit Tests**: [Unit Path - Mock External Dependencies](paths/unit-path.md)
- **Integration Tests**: [Integration Path - Real APIs](paths/integration-path.md)

---

### **📊 PHASE 7: POST-GENERATION METRICS**
- [ ] **Metrics Collection**: Execute post-generation metrics script
- [ ] **Quality Assessment**: Initial quality check
- [ ] **Update Progress Table**: Mark Phase 7 complete with JSON evidence

**Detailed Guidance**: [Phase 7 Post-Generation Metrics](phases/phase-7-post-generation.md)

---

### **🚨 PHASE 8: AUTOMATED QUALITY ENFORCEMENT (MANDATORY)**
- [ ] **Execute Validation Script**: Run `validate-test-quality.py`
- [ ] **Achieve Exit Code 0**: All quality targets must be met
- [ ] **Fix Quality Issues**: Address any failing quality checks
- [ ] **Re-run Until Success**: Repeat until script returns exit code 0
- [ ] **Update Progress Table**: Mark Phase 8 complete with AUTOMATED validation

**⚠️ MANDATORY**: Framework is NOT complete until script returns exit code 0  
**Detailed Guidance**: [Phase 8 Quality Enforcement](phases/phase-8-quality-enforcement.md)

---

## 🛤️ **PATH-SPECIFIC QUICK REFERENCE**

### **🧪 UNIT TEST PATH**
**Strategy**: Mock everything, complete isolation
**Key Points**:
- Mock ALL external dependencies (requests, os, sys)
- Mock ALL internal modules (honeyhive.*)
- Mock ALL configuration and environment
- Complete mock object with all attributes from Phase 1
- 90%+ coverage target

**Quick Reference**: [Unit Path Guide](paths/unit-path.md)

### **🔗 INTEGRATION TEST PATH**
**Strategy**: Real APIs, end-to-end validation
**Key Points**:
- Use REAL HoneyHive APIs with test credentials
- Use REAL configuration with test environment
- Use REAL logging for output validation
- Implement proper resource cleanup
- 80%+ coverage target

**Quick Reference**: [Integration Path Guide](paths/integration-path.md)

---

## 📊 **PROGRESS TRACKING**

### **Mandatory Progress Table**
Update this table after each phase:

| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 0: Setup | ❌ | None | 0/5 | Manual | ❌ |
| 1: Method Verification | ❌ | None | 0/4 | Manual | ❌ |
| 2: Logging Analysis | ❌ | None | 0/3 | Manual | ❌ |
| 3: Dependency Analysis | ❌ | None | 0/4 | Manual | ❌ |
| 4: Usage Patterns | ❌ | None | 0/3 | Manual | ❌ |
| 5: Coverage Analysis | ❌ | None | 0/2 | Manual | ❌ |
| 6: Pre-Generation | ❌ | None | 0/8 | Manual | ❌ |
| 7: Post-Generation | ❌ | None | 0/1 | JSON Required | ❌ |
| 8: **Quality Enforcement** | ❌ | None | 0/5 | **EXIT CODE 0** | ❌ |

---

## 🚨 **CRITICAL SUCCESS FACTORS**

### **80%+ Pass Rate Requirements**
1. ✅ **Complete Phase 1**: Deep analysis catches all signatures and attributes
2. ✅ **Path Consistency**: Follow unit (mock) or integration (real) consistently
3. ✅ **Mock Completeness**: Include all attributes from Phase 1 analysis
4. ✅ **Automated Validation**: Phase 8 script achieves exit code 0
5. ✅ **No Shortcuts**: Complete all phases with evidence

### **22% Failure Prevention**
**V2 Failures That V3 Prevents**:
- ❌ Missing mock attributes → ✅ Phase 1 attribute detection
- ❌ Wrong function signatures → ✅ Phase 1 AST analysis
- ❌ Incomplete mocking → ✅ Path-specific strategies
- ❌ Framework shortcuts → ✅ Mandatory progress tracking

---

## 🎯 **QUICK START WORKFLOW**

1. **📖 Read Framework Core**: Understand commitment and architecture
2. **🛤️ Choose Path**: Unit (mock external dependencies) or Integration (real APIs)
3. **📋 Follow Checklist**: Complete each phase with evidence
4. **📊 Update Progress**: Mandatory table updates after each phase
5. **🚨 Validate Quality**: Phase 8 script must return exit code 0
6. **✅ Achieve Success**: 80%+ pass rate on generated tests

**Success Metric**: Framework execution achieves 80%+ first-run pass rate, matching archive performance and eliminating V2's catastrophic regression.
