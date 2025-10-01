# Quick Load Map - Context for Common Tasks

**🎯 Fast parallel file loading for common AI assistant tasks**

⚡ PURPOSE: Eliminate discovery overhead by providing direct file load commands
🎯 USAGE: Copy-paste the appropriate section's commands before starting task

---

## 🧪 **TASK: Generate Unit Tests**

### **Load in Parallel BEFORE Starting**
```
read_file(".agent-os/standards/best-practices.md")
read_file(".agent-os/standards/coding/python-standards.md")
read_file(".agent-os/standards/ai-assistant/code-generation/linters/pylint/test-rules.md")
read_file(".agent-os/standards/ai-assistant/code-generation/linters/pylint/pre-approved-test-disables.md")
read_file(".agent-os/standards/ai-assistant/code-generation/linters/mypy/type-annotations.md")
read_file(".agent-os/standards/ai-assistant/code-generation/tests/v3/FRAMEWORK-LAUNCHER.md")
read_file(".agent-os/standards/ai-assistant/code-generation/tests/v3/core/mocking-boundaries-reference.md")
read_file(".agent-os/standards/ai-assistant/code-generation/tests/v3/phases/7/common-failure-patterns.md")
read_file(".agent-os/standards/ai-assistant/tool-usage-patterns.md")
```

**Total Files**: 9 | **Read Time**: 30-60 seconds | **Prevents**: Pattern misalignment, unapproved disables, mocking errors, large file write failures

---

## 🏗️ **TASK: Generate Production Code**

### **Load in Parallel BEFORE Starting**
```
read_file(".agent-os/standards/best-practices.md")
read_file(".agent-os/standards/coding/python-standards.md")
read_file(".agent-os/standards/coding/type-safety.md")
read_file(".agent-os/standards/coding/graceful-degradation.md")
read_file(".agent-os/standards/ai-assistant/code-generation/production/README.md")
read_file(".agent-os/standards/ai-assistant/code-generation/linters/pylint/function-rules.md")
```

**Total Files**: 6 | **Read Time**: 30-45 seconds | **Prevents**: Type safety issues, missing error handling, quality violations

---

## 🔄 **TASK: Refactor Code**

### **Load in Parallel BEFORE Starting**
```
read_file(".agent-os/standards/coding/refactoring-protocols.md")
read_file(".agent-os/standards/development/code-quality.md")
read_file(".agent-os/standards/coding/graceful-degradation.md")
read_file(".agent-os/standards/coding/type-safety.md")
read_file(".agent-os/standards/best-practices.md")
```

**Total Files**: 5 | **Read Time**: 25-40 seconds | **Prevents**: Breaking changes, quality regression, safety violations

---

## 🌐 **TASK: Generate Integration Tests**

### **Load in Parallel BEFORE Starting**
```
read_file(".agent-os/standards/best-practices.md")
read_file(".agent-os/standards/testing/integration-testing-standards.md")
read_file(".agent-os/standards/ai-assistant/code-generation/tests/v3/FRAMEWORK-LAUNCHER.md")
read_file(".agent-os/standards/ai-assistant/code-generation/tests/v3/paths/integration-path.md")
read_file(".agent-os/standards/ai-assistant/code-generation/linters/pylint/test-rules.md")
```

**Total Files**: 5 | **Read Time**: 25-40 seconds | **Prevents**: Mock usage in integration tests, missing cleanup, API verification gaps

---

## 📝 **TASK: Update Documentation**

### **Load in Parallel BEFORE Starting**
```
read_file(".agent-os/standards/documentation/requirements.md")
read_file(".agent-os/standards/documentation/documentation-templates.md")
read_file(".agent-os/standards/best-practices.md")
```

**Total Files**: 3 | **Read Time**: 15-25 seconds | **Prevents**: EventType string literals, missing examples, broken links

---

## 🔒 **TASK: Git Operations**

### **Load in Parallel BEFORE Starting**
```
read_file(".agent-os/standards/ai-assistant/git-safety-rules.md")
read_file(".agent-os/standards/ai-assistant/commit-protocols.md")
read_file(".agent-os/standards/development/git-workflow.md")
```

**Total Files**: 3 | **Read Time**: 15-20 seconds | **Prevents**: --no-verify usage, unsafe operations, commit protocol violations

---

## 📋 **TASK: Create Specification**

### **Load in Parallel BEFORE Starting**
```
read_file(".agent-os/standards/development/specification-standards.md")
read_file(".agent-os/standards/best-practices.md")
```

**Total Files**: 2 | **Read Time**: 10-15 seconds | **Prevents**: Incomplete specs, missing required sections

---

## 🎯 **USAGE PATTERN**

### **Step 1: Identify Task Type**
```markdown
User request: "Generate unit tests for provider_processor.py"
→ Task Type: Generate Unit Tests
```

### **Step 2: Load Appropriate Context**
```markdown
Execute parallel read commands from "TASK: Generate Unit Tests" section above
```

### **Step 3: Proceed with Framework**
```markdown
Now execute framework with complete context foundation:
- Project conventions loaded ✅
- Linter standards memorized ✅
- Critical references reviewed ✅
→ Higher first-pass quality, fewer iterations
```

---

## 📊 **TIME INVESTMENT ANALYSIS**

```python
time_analysis = {
    "context_loading": {
        "phase_0_execution": "2-3 minutes (parallel file loading)",
        "comprehension": "Already done during loading",
        "total_upfront": "2-3 minutes"
    },
    "benefits": {
        "prevented_corrections": "3-5 user interventions avoided",
        "prevented_rework": "15-20 minutes saved",
        "higher_quality": "85-95% pattern alignment vs 60-70%",
        "net_benefit": "12-17 minutes faster + better results"
    },
    "conclusion": "Always worth the 2-3 minute investment"
}
```

---

## 🔗 **INTEGRATION POINTS**

### **Referenced From**:
- `.cursorrules` - Main entry point
- `SYSTEMATIC-DEVELOPMENT-CONTEXT.md` - Core methodology
- `compliance-checking.md` - Standards discovery

### **Enables**:
- Higher first-pass code quality
- Fewer user corrections needed
- Better pattern alignment with project
- Reduced total development time

---

🛑 VALIDATE-GATE: Quick Load Map Understanding
- [ ] Can identify task type from user request ✅/❌
- [ ] Know which context files to load for each task ✅/❌
- [ ] Understand benefit of upfront context loading ✅/❌

🎯 **Use this map at the start of every complex task to establish comprehensive context foundation**
