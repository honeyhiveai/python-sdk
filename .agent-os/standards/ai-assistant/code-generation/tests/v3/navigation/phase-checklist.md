# Phase Execution Checklist

**🎯 AI Checklist for Systematic Framework Execution**

🛑 VALIDATE-GATE: Phase Checklist Entry Requirements
- [ ] Framework execution commitment confirmed ✅/❌
- [ ] Systematic phase order understood ✅/❌
- [ ] Checklist completion requirement acknowledged ✅/❌

🚨 FRAMEWORK-VIOLATION: If skipping phases or executing out of order

## 🛑 **PHASE EXECUTION ORDER EXECUTION**

⚠️ MUST-READ: All phases must be completed in order - no skipping allowed

### **Phase 0: Framework Preparation**
- [ ] Read binding contract: [../core/binding-contract.md](../core/binding-contract.md)
- [ ] Select test path: Unit or Integration
- [ ] Initialize progress tracking table
- [ ] Acknowledge framework commitment

### **Phase 1: Method Verification** 
- [ ] Execute: [../phases/1/ast-parsing.md](../phases/1/ast-parsing.md)
- [ ] Complete: Method signature extraction
- [ ] Complete: Attribute detection analysis
- [ ] Update: Progress table with findings

### **Phase 2: Logging Analysis**
- [ ] Execute: [../phases/2/logging-strategy.md](../phases/2/logging-strategy.md)  
- [ ] Complete: safe_log usage identification
- [ ] Complete: Logging verification patterns
- [ ] Update: Progress table with strategy

### **Phase 3: Dependency Analysis**
- [ ] Execute: [../phases/3/dependency-mapping.md](../phases/3/dependency-mapping.md)
- [ ] Complete: Mock vs real API strategy
- [ ] Complete: Fixture requirement identification
- [ ] Update: Progress table with dependencies

### **Phase 4: Usage Patterns**
- [ ] Execute: [../phases/4/pattern-analysis.md](../phases/4/pattern-analysis.md)
- [ ] Complete: Call pattern identification
- [ ] Complete: Edge case discovery
- [ ] Update: Progress table with patterns

### **Phase 5: Coverage Analysis**
- [ ] Execute: [../phases/5/coverage-planning.md](../phases/5/coverage-planning.md)
- [ ] Complete: Branch coverage planning
- [ ] Complete: Test scenario identification
- [ ] Update: Progress table with coverage

### **Phase 6: Pre-Generation**
- [ ] Execute: [../phases/6/validation.md](../phases/6/validation.md)
- [ ] Complete: Template selection
- [ ] Complete: Fixture integration
- [ ] Update: Progress table with readiness

### **Phase 7: Post-Generation**
- [ ] Execute: [../phases/7/metrics.md](../phases/7/metrics.md)
- [ ] Complete: Test file generation
- [ ] Complete: Initial quality check
- [ ] Update: Progress table with results

### **Phase 8: Quality Enforcement**
- [ ] Execute: [../phases/8/validation.md](../phases/8/validation.md)
- [ ] Complete: Automated quality validation
- [ ] Complete: validate-test-quality.py execution
- [ ] Update: Final progress table

## 🚨 **CRITICAL CHECKPOINTS**

### **Before Phase 1**
- ✅ Framework contract acknowledged
- ✅ Test path selected (unit/integration)
- ✅ Progress table initialized

### **Before Phase 6**
- ✅ All analysis phases completed
- ✅ Progress table shows evidence
- ✅ Path-specific strategy confirmed

### **Before Phase 8**
- ✅ Test file generated
- ✅ Templates used correctly
- ✅ Fixtures integrated properly

### **Framework Completion**
- ✅ validate-test-quality.py exit code 0
- ✅ All quality targets achieved
- ✅ Progress table complete with evidence

---

**🎯 Check off each item systematically. Never skip phases or checkpoints.**
