# V3 Framework Command Language Glossary

**🎯 Standardized Command Language for AI Control Within File Size Constraints**

*This glossary defines command-level language that creates binding obligations for AI execution. Each term has specific behavioral requirements that cannot be bypassed.*

🚨 **CRITICAL**: This glossary MUST be read before any V3 framework execution
🛑 **BINDING**: All commands create non-negotiable obligations
⚠️ **MANDATORY**: Reading this glossary is required by all entry points

---

## 🚨 **BLOCKING COMMANDS (Cannot Proceed)**

### **🛑 EXECUTE-NOW**
```markdown
🛑 EXECUTE-NOW: [command]
```
**Binding Requirement**: AI MUST execute the specified command immediately and paste output before any other action.
**Bypass Prevention**: No analysis, no summary, no interpretation - only direct execution and output documentation.

### **🛑 PASTE-OUTPUT**
```markdown
🛑 PASTE-OUTPUT: [description]
```
**Binding Requirement**: AI MUST paste the actual command output, not summarize or interpret.
**Bypass Prevention**: No "analysis complete" or "results show" - only raw output.

### **🛑 UPDATE-TABLE**
```markdown
🛑 UPDATE-TABLE: [table reference]
```
**Binding Requirement**: AI MUST update the specified progress table with quantified evidence before proceeding.
**Bypass Prevention**: Cannot claim completion without visible table update in chat.

### **🛑 VALIDATE-GATE**
```markdown
🛑 VALIDATE-GATE: [criteria]
```
**Binding Requirement**: AI MUST verify all specified criteria are met with documented proof.
**Bypass Prevention**: Cannot proceed until all checkboxes are ✅ with evidence.

---

## ⚠️ **WARNING COMMANDS (Strong Guidance)**

### **⚠️ MUST-READ**
```markdown
⚠️ MUST-READ: [file/section]
```
**Binding Requirement**: AI MUST read the specified content before proceeding with current task.
**Usage**: Navigation to critical files within size constraints.

### **⚠️ MUST-COMPLETE**
```markdown
⚠️ MUST-COMPLETE: [task list]
```
**Binding Requirement**: AI MUST complete all listed tasks with documented evidence.
**Usage**: Sequential task enforcement without repeating full instructions.

### **⚠️ EVIDENCE-REQUIRED**
```markdown
⚠️ EVIDENCE-REQUIRED: [specific evidence type]
```
**Binding Requirement**: AI MUST provide the specified type of evidence (quantified, command output, etc.).
**Usage**: Enforce evidence standards without repeating requirements.

---

## 🎯 **NAVIGATION COMMANDS (File Size Optimization)**

### **🎯 NEXT-MANDATORY**
```markdown
🎯 NEXT-MANDATORY: [file path]
```
**Binding Requirement**: AI MUST read and execute the specified file as the immediate next step.
**Usage**: Chain execution across small files without losing enforcement.

### **🎯 RETURN-WITH-EVIDENCE**
```markdown
🎯 RETURN-WITH-EVIDENCE: [evidence type]
```
**Binding Requirement**: AI MUST return to current context with specified evidence from external file.
**Usage**: Maintain progress tracking across file boundaries.

### **🎯 CHECKPOINT-THEN**
```markdown
🎯 CHECKPOINT-THEN: [next action]
```
**Binding Requirement**: AI MUST complete current checkpoint validation before specified next action.
**Usage**: Enforce validation gates in navigation flow.

---

## 📊 **EVIDENCE COMMANDS (Quality Enforcement)**

### **📊 COUNT-AND-DOCUMENT**
```markdown
📊 COUNT-AND-DOCUMENT: [what to count]
```
**Binding Requirement**: AI MUST provide exact numerical count with supporting evidence.
**Usage**: Prevent vague "analysis complete" claims.

### **📊 QUANTIFY-RESULTS**
```markdown
📊 QUANTIFY-RESULTS: [measurement type]
```
**Binding Requirement**: AI MUST provide specific numerical measurements, not qualitative assessments.
**Usage**: Enforce quantified evidence standards.

### **📊 COMMAND-OUTPUT-REQUIRED**
```markdown
📊 COMMAND-OUTPUT-REQUIRED: [command description]
```
**Binding Requirement**: AI MUST show actual terminal/script output, not interpretation.
**Usage**: Prevent command execution shortcuts.

---

## 🔄 **PROGRESS COMMANDS (Table Management)**

### **🔄 UPDATE-STATUS**
```markdown
🔄 UPDATE-STATUS: Phase [X] → [status]
```
**Binding Requirement**: AI MUST update progress table with specified phase status.
**Usage**: Maintain progress visibility across phases.

### **🔄 EVIDENCE-SUMMARY**
```markdown
🔄 EVIDENCE-SUMMARY: [evidence type]
```
**Binding Requirement**: AI MUST provide consolidated evidence summary for progress table.
**Usage**: Populate evidence column with quantified results.

### **🔄 GATE-STATUS**
```markdown
🔄 GATE-STATUS: [gate name] → ✅/❌
```
**Binding Requirement**: AI MUST update gate status with validation proof.
**Usage**: Track quality gate passage with evidence.

---

## 🚨 **VIOLATION DETECTION COMMANDS**

### **🚨 FRAMEWORK-VIOLATION**
```markdown
🚨 FRAMEWORK-VIOLATION: [violation type]
```
**Binding Requirement**: AI MUST acknowledge violation and return to proper framework execution.
**Usage**: Self-correction mechanism for framework deviations.

### **🚨 EVIDENCE-GAP**
```markdown
🚨 EVIDENCE-GAP: [missing evidence]
```
**Binding Requirement**: AI MUST provide missing evidence before proceeding.
**Usage**: Catch and correct evidence gaps in real-time.

### **🚨 QUALITY-FAILURE**
```markdown
🚨 QUALITY-FAILURE: [failure type]
```
**Binding Requirement**: AI MUST address quality failure with corrective action.
**Usage**: Enforce quality standards with immediate correction.

### **🚨 SUCCESS-CRITERIA-VIOLATION**
```markdown
🚨 SUCCESS-CRITERIA-VIOLATION: Partial success declared with quality failures
```
**Binding Requirement**: AI MUST NOT declare success with any quality gate failure.
**Usage**: Prevent rationalization of partial success as acceptable.

### **🚨 ZERO-TOLERANCE-ENFORCEMENT**
```markdown
🚨 ZERO-TOLERANCE-ENFORCEMENT: ALL gates must pass
```
**Binding Requirement**: AI MUST achieve 100% quality gate passage before success.
**Usage**: Enforce absolute quality standards with no exceptions.

---

## 💡 **USAGE PATTERNS FOR FILE SIZE CONSTRAINTS**

### **Pattern 1: Navigation with Enforcement**
```markdown
⚠️ MUST-READ: [phases/1/ast-analysis.md]
🛑 EXECUTE-NOW: Commands in that file
🛑 PASTE-OUTPUT: AST analysis results
🎯 RETURN-WITH-EVIDENCE: Function count and signatures
🛑 UPDATE-TABLE: Phase 1 status with evidence
```

### **Pattern 2: Cross-File Progress Tracking**
```markdown
🔄 UPDATE-STATUS: Phase 1 → In Progress
🎯 NEXT-MANDATORY: [phases/1/shared-analysis.md]
🎯 CHECKPOINT-THEN: Proceed to Phase 2
```

### **Pattern 3: Quality Gate Enforcement**
```markdown
🛑 VALIDATE-GATE: 
- [ ] Commands executed ✅/❌
- [ ] Output documented ✅/❌  
- [ ] Table updated ✅/❌
⚠️ EVIDENCE-REQUIRED: Quantified results only
```

---

## 🎯 **IMPLEMENTATION STRATEGY**

### **Small File Navigation**
Instead of repeating full instructions:
```markdown
# OLD (File Size Bloat):
## Phase 1 Requirements
- Execute AST analysis commands
- Document all function signatures  
- Update progress table with results
- Validate completion before Phase 2

# NEW (Command Language):
⚠️ MUST-READ: [ast-analysis.md]
🛑 EXECUTE-NOW: All commands in file
📊 QUANTIFY-RESULTS: Function count
🛑 UPDATE-TABLE: Phase 1 evidence
🎯 NEXT-MANDATORY: [phase-2/shared-analysis.md]
```

### **Progress Table Integration**
```markdown
# Reference table without repeating structure:
🛑 UPDATE-TABLE: Main progress (Phase X → status, evidence, gate)
🔄 EVIDENCE-SUMMARY: [specific evidence type]
🔄 GATE-STATUS: Phase X → ✅ with proof
```

### **Cross-Phase Enforcement**
```markdown
# Maintain enforcement across file boundaries:
🎯 CHECKPOINT-THEN: Next phase
⚠️ MUST-COMPLETE: All current phase tasks
🚨 FRAMEWORK-VIOLATION: If skipping evidence
```

---

## 🚨 **CRITICAL SUCCESS FACTORS**

1. **Consistent Usage**: All V3 files MUST use this glossary consistently
2. **Binding Language**: Commands create obligations, not suggestions
3. **Evidence Focus**: Every command ties to evidence requirements
4. **Size Efficiency**: Replaces verbose instructions with compact commands
5. **Cross-File Continuity**: Maintains enforcement across file boundaries

**This command language serves as "API calls" for AI behavior control within file size constraints.**
