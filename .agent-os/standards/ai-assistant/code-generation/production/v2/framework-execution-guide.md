# Production Code Framework - Execution Guide

## 🎯 **FRAMEWORK EXECUTION RULES**

**Purpose**: Systematic execution of production code generation with mandatory quality enforcement.

**Quality Targets**: 10.0/10 Pylint, 0 MyPy errors, 100% type annotations, comprehensive docstrings.

---

## 📋 **MANDATORY PROGRESS TRACKING**

**🚨 CRITICAL: AI MUST update this table IN THE CHAT WINDOW after each phase**

| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|------|
| 0: Pre-Generation Setup | ❌ | None | 0/3 | ❌ |
| 1: Complexity Assessment | ❌ | None | 0/2 | ❌ |
| 2: Requirements Analysis | ❌ | None | 0/4 | ❌ |
| 3: Template Selection | ❌ | None | 0/3 | ❌ |
| 4: Code Generation | ❌ | None | 0/2 | ❌ |
| 5: Quality Enforcement | ❌ | None | 0/5 | ❌ |

**ENFORCEMENT RULES:**
- ✅ **CORRECT**: Table shown in AI's chat responses
- ❌ **FORBIDDEN**: AI creating/modifying files with table
- ❌ **STOP**: If ANY cell shows ❌ or incomplete data

---

## 🚨 **ENFORCEMENT PATTERNS - PREVENTING AI SHORTCUTS**

### **⚠️ SKIP INDICATORS - IMMEDIATE STOP REQUIRED**

**If AI uses ANY of these phrases, immediately respond with "STOP - Complete Phase X checkpoint first":**

#### **Skip Indicators**
- "Let me start writing the code..."
- "I'll generate the function..."
- "Based on my understanding..."
- "The function should probably..."
- "I assume it needs..."
- "Let me create a simple..."

#### **Assumption Indicators**
- "I think..."
- "It should..."
- "Likely..."
- "Typically..."
- "Usually..."
- "The requirements seem to be..."

### **✅ REQUIRED EVIDENCE PATTERNS**

**AI MUST use these exact patterns to demonstrate proper analysis:**

#### **Requirements Analysis Evidence**
- ✅ "I analyzed the exact requirements and found:"
- ✅ "Function signature determined: `def func_name(param: Type) -> ReturnType:`"
- ✅ "Dependencies identified: [list of specific imports]"

#### **Template Selection Evidence**
- ✅ "Complexity level determined: [Simple/Complex/Class] based on [specific criteria]"
- ✅ "Template selected: [specific template name] from [file path]"
- ✅ "Template requirements verified: [list of requirements]"

#### **Quality Verification Evidence**
- ✅ "Pylint score achieved: 10.0/10"
- ✅ "MyPy errors: 0"
- ✅ "Type annotation coverage: 100%"

### **🛑 ENFORCEMENT RESPONSES**

#### **When AI Skips Steps:**
> "STOP - You're skipping the framework. Complete Phase X checkpoint gate first. Show me the exact analysis and evidence required."

#### **When AI Uses Assumptions:**
> "STOP - No assumptions allowed. Analyze the exact requirements and show concrete evidence."

#### **When AI Rushes to Code:**
> "STOP - Complete ALL phases first. Show me the completed progress tracking table."

---

## 🔒 **PHASE EXECUTION REQUIREMENTS**

### **Phase 0: Pre-Generation Setup**
**MANDATORY COMMANDS:**
1. Read pre-generation checklist
2. Verify environment setup
3. Confirm quality targets

**GATE CRITERIA:** All setup requirements verified

### **Phase 1: Complexity Assessment**
**MANDATORY COMMANDS:**
1. Analyze function/class requirements
2. Determine complexity level (Simple/Complex/Class)

**GATE CRITERIA:** Complexity level determined with justification

### **Phase 2: Requirements Analysis**
**MANDATORY COMMANDS:**
1. Define exact function signature
2. Identify all dependencies
3. Determine error handling requirements
4. Plan docstring structure

**GATE CRITERIA:** Complete requirements documented

### **Phase 3: Template Selection**
**MANDATORY COMMANDS:**
1. Select appropriate template
2. Verify template requirements
3. Plan customizations needed

**GATE CRITERIA:** Template selected and verified

### **Phase 4: Code Generation**
**MANDATORY COMMANDS:**
1. Generate code from template
2. Apply customizations

**GATE CRITERIA:** Code generated and customized

### **Phase 5: Quality Enforcement**
**MANDATORY COMMANDS:**
1. Run Pylint (target: 10.0/10)
2. Run MyPy (target: 0 errors)
3. Verify type annotations (target: 100%)
4. Verify docstring completeness
5. Run Black formatting

**GATE CRITERIA:** All quality targets achieved

---

## 🎯 **FRAMEWORK COMPLETION CRITERIA**

### **✅ FRAMEWORK SUCCESSFULLY COMPLETED WHEN:**

**Progress Tracking:**
- All 6 phases marked complete (✅) in progress table
- All commands executed with evidence documented
- All checkpoint gates passed

**Quality Validation:**
- 10.0/10 Pylint score achieved
- 0 MyPy errors achieved
- 100% type annotation coverage
- Complete docstring coverage
- Black formatting clean

**Documentation:**
- Progress table updated in chat window
- Evidence provided for each phase completion
- Final quality metrics demonstrate perfect scores

### **🎯 SUCCESS INDICATORS CHECKLIST**

**AI is ready to mark framework complete when they have provided:**

#### **Analysis Evidence (Phases 1-3)**
- [ ] **Complexity level determined** with specific justification
- [ ] **Complete requirements analysis** with function signature
- [ ] **All dependencies identified** with import statements
- [ ] **Template selected** with verification of requirements
- [ ] **Customization plan** documented

#### **Generation Evidence (Phases 4-5)**
- [ ] **Code generated** using selected template
- [ ] **Customizations applied** as planned
- [ ] **Quality targets achieved** with metrics shown

#### **Quality Achievement Evidence**
- [ ] **10.0/10 Pylint score** demonstrated
- [ ] **0 MyPy errors** achieved
- [ ] **100% type annotations** verified
- [ ] **Complete docstrings** verified
- [ ] **Black formatting** clean

#### **Framework Compliance Evidence**
- [ ] **Progress table** shown in chat (not files) with all ✅
- [ ] **No skip indicators** used in AI responses
- [ ] **Required evidence patterns** used throughout
- [ ] **All checkpoint gates** passed with documented evidence

---

**💡 Remember**: Production code quality is non-negotiable. Every checkpoint prevents hours of debugging and refactoring later.
