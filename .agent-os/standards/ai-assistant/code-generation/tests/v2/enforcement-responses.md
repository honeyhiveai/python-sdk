# Violation Detection & Enforcement

## 🚨 **PHASE-SPECIFIC VIOLATION INDICATORS**

### **Phase 1 Violations:**
- "Method verification complete" (without table update)
- "Found X methods" (without showing updated progress table)
- "Moving to logging analysis" (without Phase 1 table evidence)

### **Phase 2 Violations:**
- "Logging analysis complete" (without table update)
- "Found logging calls" (without showing updated progress table)
- "Moving to dependency analysis" (without Phase 2 table evidence)

### **Phase 3 Violations:**
- "Dependencies analyzed" (without table update)
- "Mocking strategy complete" (without showing updated progress table)
- "Moving to usage patterns" (without Phase 3 table evidence)

### **Phase 4 Violations:**
- "Usage patterns found" (without table update)
- "Pattern analysis complete" (without showing updated progress table)
- "Moving to coverage analysis" (without Phase 4 table evidence)

### **Phase 5 Violations:**
- "Coverage planning complete" (without table update)
- "90% target set" (without showing updated progress table)
- "Moving to pre-generation linting" (without Phase 5 table evidence)

### **General Violation Indicators:**
- "Phase X complete" (without showing updated table)
- "Moving to next phase" (without table update)
- "Analysis finished" (without table evidence)
- "Proceeding to generation" (without complete table)
- Creating/modifying files with table instead of chat window
- Referencing "progress table in file" instead of chat window

---

## 🛑 **ENFORCEMENT RESPONSES**

### **Phase-Specific Enforcement Responses:**

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

### **Standard Enforcement Responses:**

**When AI Skips Steps:**
> "STOP - You're skipping the framework. Complete Phase X checkpoint gate first. Show me the exact command output and evidence required."

**When AI Uses Assumptions:**
> "STOP - No assumptions allowed. Run the mandatory commands and show exact evidence."

**When AI Paraphrases:**
> "STOP - Copy-paste the exact text with line numbers. No paraphrasing allowed."

**When AI Rushes to Code:**
> "STOP - Complete ALL phases first. Show me the completed progress tracking table."

**When AI Skips Metrics:**
> "STOP - Execute the metrics command and copy-paste the JSON output. No metrics = no progression."

**When AI Puts Table in Files:**
> "STOP - The progress table must be shown in the chat window, NOT in files. Copy-paste the current table here and update it with your progress."

**Framework Contract Violation:**
> "STOP - You violated the framework contract you committed to. You acknowledged that shortcuts create rework cycles and waste team time. Read the acknowledgment requirements and provide the exact text before proceeding."

---

## 🛑 **PHASE 8 SPECIFIC ENFORCEMENT**

### **Phase 8 Premature Completion Violations:**
- "Framework execution complete" (with failing tests)
- "Quality enforcement initiated" (without completion)
- "Systematic issues documented" (treating analysis as completion)
- "Framework complete" (without automated validation)
- "Issues identified and documented" (analysis instead of fixes)
- "Framework demonstrates analysis capability" (missing quality achievement)

### **Phase 8 Enforcement Response:**
> "STOP - You violated the Phase 8 quality gate. You cannot declare framework completion with failing tests. Execute the automated validation script and show exit code 0:
> 
> ```bash
> python .agent-os/scripts/validate-test-quality.py --test-file [YOUR_FILE]
> echo "Exit code: $?"
> ```
> 
> Continue fixing issues until the script returns exit code 0, then update the progress table with automated validation evidence."

### **Quality Gate Bypass Violations:**
- Declaring completion without script execution
- Showing script results but ignoring exit code 1
- Making excuses for failing quality targets
- Treating framework as "analysis only" instead of "quality achievement"
- Using phrases like "needs systematic fixes" as completion
- Marking Phase 8 complete without exit code 0

### **Quality Gate Bypass Response:**
> "STOP - The framework requires ACTUAL quality achievement, not just analysis. The automated validation script returned exit code 1, which means quality targets are not met. You must continue Phase 8 until the script returns exit code 0. No exceptions, no bypasses, no 'good enough' - the framework contract requires perfect quality scores."

### **Table Formatting Violations:**
- Malformed progress tables with overflowing text
- Missing pipe separators or inconsistent alignment
- Evidence column exceeding 30 characters
- Using text instead of ✅/❌ symbols in status column

### **Table Formatting Response:**
> "STOP - Your progress table is malformed and unreadable. Follow the table formatting standards:
> - Evidence column: Maximum 30 characters
> - Status column: Only ✅ or ❌ symbols
> - Consistent pipe alignment
> - Readable in chat window
> 
> Reformat the table properly before proceeding."
