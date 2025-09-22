# V3 Framework Progress Table Template

**🎯 Mandatory Progress Tracking for All V3 Framework Executions**

*This table MUST be maintained in the chat window and updated after each phase completion. Use command language to enforce updates.*

---

## 🛑 **MAIN PROGRESS TABLE**

🛑 UPDATE-TABLE: Copy this table to chat window at framework start
🔄 UPDATE-STATUS: After each phase completion
📊 EVIDENCE-SUMMARY: Populate evidence column with quantified results
🔄 GATE-STATUS: Update gate column with ✅/❌ and validation proof

### **Template:**
```markdown
| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|------|
| 1: Method Verification | ⏸️ | Not started | 0/7 executed | ❌ |
| 2: Logging Analysis | ⏸️ | Not started | 0/6 executed | ❌ |
| 3: Dependency Analysis | ⏸️ | Not started | 0/7 executed | ❌ |
| 4: Usage Pattern Analysis | ⏸️ | Not started | 0/7 executed | ❌ |
| 5: Coverage Analysis | ⏸️ | Not started | 0/6 executed | ❌ |
| 6: Pre-Generation | ⏸️ | Not started | 0/7 executed | ❌ |
| 7: Test Generation | ⏸️ | Not started | 0/1 executed | ❌ |
| 8: Quality Validation | ⏸️ | Not started | 0/1 executed | ❌ |
```

---

## 🚨 **STATUS DEFINITIONS**

### **Status Column**
- **⏸️ Not Started**: Phase not yet begun
- **🔄 In Progress**: Phase currently executing
- **✅ Complete**: Phase finished with all evidence
- **❌ Failed**: Phase failed validation gates

### **Evidence Column Format**
```markdown
# Use quantified evidence only:
"20 functions, 189 attributes, 7 external deps"  # ✅ Good
"Analysis complete"                               # ❌ Bad
```

### **Commands Column Format**
```markdown
# Track actual command execution:
"5/7 executed"    # ✅ Shows progress
"All done"        # ❌ Vague
```

### **Gate Column Format**
```markdown
# Validation status with proof:
"✅ All criteria met with evidence"     # ✅ Good
"❌ Missing function count"             # ✅ Specific failure
"Passed"                               # ❌ Vague
```

---

## 🛑 **MANDATORY UPDATE COMMANDS**

### **Phase Start**
```markdown
🔄 UPDATE-STATUS: Phase [X] → 🔄 In Progress
🛑 UPDATE-TABLE: Show phase start in chat window
```

### **During Phase Execution**
```markdown
📊 COMMAND-OUTPUT-REQUIRED: [specific command]
🔄 UPDATE-STATUS: Commands [X/Y] executed
```

### **Phase Completion**
```markdown
📊 EVIDENCE-SUMMARY: [quantified results]
🔄 GATE-STATUS: Phase [X] → ✅/❌ with validation
🛑 UPDATE-TABLE: Complete evidence and gate status
```

### **Quality Gate Validation**
```markdown
🛑 VALIDATE-GATE: Phase [X] Complete
- [ ] All commands executed ✅/❌
- [ ] Evidence documented ✅/❌
- [ ] Quantified results provided ✅/❌
- [ ] Table updated ✅/❌
```

---

## 🎯 **CROSS-PHASE CONTINUITY**

### **Navigation Between Phases**
```markdown
🎯 CHECKPOINT-THEN: Proceed to Phase [X+1]
⚠️ MUST-COMPLETE: All Phase [X] requirements
🚨 FRAMEWORK-VIOLATION: If skipping evidence or table updates
```

### **Evidence Accumulation**
```markdown
🔄 EVIDENCE-SUMMARY: Consolidate all Phase [X] findings
📊 QUANTIFY-RESULTS: Specific counts and measurements
🛑 UPDATE-TABLE: Evidence column with consolidated results
```

---

## 🚨 **ENFORCEMENT MECHANISMS**

### **Table Update Enforcement**
```markdown
🛑 UPDATE-TABLE: [Required before any phase progression]
🚨 FRAMEWORK-VIOLATION: If table not visible in chat
⚠️ EVIDENCE-REQUIRED: Quantified results in evidence column
```

### **Progress Validation**
```markdown
🛑 VALIDATE-GATE: Progress Table Current
- [ ] All completed phases show ✅ ✅/❌
- [ ] Current phase shows 🔄 ✅/❌
- [ ] Evidence column populated ✅/❌
- [ ] Command counts accurate ✅/❌
```

### **Quality Gate Integration**
```markdown
🔄 GATE-STATUS: Automated validation results
📊 QUANTIFY-RESULTS: Pass rates, coverage, Pylint scores
🛑 UPDATE-TABLE: Final quality metrics in evidence
```

---

**🎯 This progress table template provides the structure for maintaining systematic evidence tracking across all V3 framework phases while using command language to enforce updates within file size constraints.**
