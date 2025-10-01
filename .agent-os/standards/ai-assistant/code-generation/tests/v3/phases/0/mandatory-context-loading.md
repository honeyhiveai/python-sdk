# Phase 0: Mandatory Context Loading

**🎯 Load project-wide standards BEFORE starting analysis**

🛑 VALIDATE-GATE: Phase 0 Entry Requirements
- [ ] Framework contract acknowledged ✅/❌
- [ ] Test path selected (unit/integration) ✅/❌
- [ ] Ready to load comprehensive project context ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding to Phase 1 without loading all mandatory context

---

## 🚨 **WHY PHASE 0 EXISTS**

### **The Problem Without It**:
```python
without_context_loading = {
    "generates_code": "Using only test-specific framework knowledge",
    "misses_patterns": "Project conventions like native strings over regex",
    "user_corrections": "Why are we using regex? Why this pattern?",
    "iterations_needed": "Multiple rounds to align with project standards",
    "total_time": "Longer due to rework cycles"
}
```

### **The Solution With Phase 0**:
```python
with_context_loading = {
    "generates_code": "Using full project + framework knowledge",
    "follows_patterns": "Project conventions from the start",
    "user_corrections": "Minimal - aligned with standards",
    "iterations_needed": "Fewer - first-pass quality higher",
    "total_time": "Faster overall - less rework"
}
```

---

## 📋 **MANDATORY CONTEXT FILES**

### **TASK 0.1: Load Project-Wide Standards**
🛑 EXECUTE-NOW: Load these in parallel (3 files)
```
read_file(".agent-os/standards/best-practices.md")
read_file(".agent-os/standards/coding/python-standards.md")
read_file(".agent-os/standards/development/code-quality.md")
```

**What You'll Learn**:
- ✅ Native Python strings preferred over regex (best-practices.md lines 119-247)
- ✅ Type annotation requirements for all code
- ✅ Graceful degradation patterns
- ✅ Project-wide coding conventions

📊 COUNT-AND-DOCUMENT: Project-wide standards loaded: [3/3]

---

### **TASK 0.2: Load Test-Specific Linter Standards**
🛑 EXECUTE-NOW: Load these in parallel (3 files)
```
read_file(".agent-os/standards/ai-assistant/code-generation/linters/pylint/test-rules.md")
read_file(".agent-os/standards/ai-assistant/code-generation/linters/pylint/pre-approved-test-disables.md")
read_file(".agent-os/standards/ai-assistant/code-generation/linters/mypy/type-annotations.md")
```

**What You'll Learn**:
- ✅ Pre-approved Pylint disables (standard header)
- ✅ Never-approved disables (must fix instead)
- ✅ MyPy type annotation patterns for tests
- ✅ Common test violation prevention

📊 COUNT-AND-DOCUMENT: Linter standards loaded: [3/3]

---

### **TASK 0.3: Load Critical Testing References**
🛑 EXECUTE-NOW: Load these in parallel (2 files)
```
read_file(".agent-os/standards/ai-assistant/code-generation/tests/v3/core/mocking-boundaries-reference.md")
read_file(".agent-os/standards/ai-assistant/code-generation/tests/v3/phases/7/common-failure-patterns.md")
```

**What You'll Learn**:
- ✅ Internal vs external mocking boundaries (prevents 70% coverage issues)
- ✅ Common failure patterns (prevents 60-70% of post-generation failures)
- ✅ Coverage implications of mocking choices
- ✅ Predictable error patterns and fixes

📊 COUNT-AND-DOCUMENT: Testing references loaded: [2/2]

---

## 📊 **EVIDENCE COLLECTION**

### **Context Loading Verification**
🛑 PASTE-OUTPUT: Confirm all files loaded successfully

**Required Evidence**:
```markdown
✅ Phase 0 Context Loading Complete:

**Project-Wide Standards** (3/3):
- best-practices.md: Loaded ✅ (Native strings over regex, lines 119-247)
- python-standards.md: Loaded ✅ (Python-specific conventions)
- code-quality.md: Loaded ✅ (Quality requirements)

**Linter Standards** (3/3):
- test-rules.md: Loaded ✅ (Common test violations)
- pre-approved-test-disables.md: Loaded ✅ (Canonical approved list)
- type-annotations.md: Loaded ✅ (MyPy patterns)

**Testing References** (2/2):
- mocking-boundaries-reference.md: Loaded ✅ (Internal vs external)
- common-failure-patterns.md: Loaded ✅ (Predictable failures)

**Total Context Files**: 8/8 loaded successfully
```

🛑 UPDATE-TABLE: Phase 0 → Context foundation established with 8/8 files

---

## 🎯 **CONTEXT FOUNDATION BENEFITS**

### **First-Pass Code Quality Impact**:
```python
quality_improvement = {
    "without_phase_0": {
        "pattern_alignment": "60-70% (missing project conventions)",
        "user_corrections": "5-7 corrections needed",
        "iterations": "Multiple rounds to align patterns",
        "example_issues": ["Why regex?", "Use approved disables", "Don't mock internal"]
    },
    "with_phase_0": {
        "pattern_alignment": "85-95% (comprehensive standards loaded)",
        "user_corrections": "1-2 corrections needed",
        "iterations": "Minimal rework required",
        "example_benefits": ["Native strings from start", "Correct disables", "Proper mocking"]
    }
}
```

### **Time Investment Analysis**:
- **Phase 0 execution time**: 2-3 minutes (parallel file loading)
- **Rework time saved**: 15-20 minutes (fewer iterations)
- **Net benefit**: 12-17 minutes faster overall + higher quality

---

## 🚨 **VALIDATION GATE: PHASE 0 COMPLETE**

🛑 VALIDATE-GATE: Context Foundation Established
- [ ] All 8 mandatory context files loaded ✅/❌
- [ ] Project conventions understood (native strings, etc.) ✅/❌
- [ ] Linter standards reviewed (approved disables, etc.) ✅/❌
- [ ] Mocking boundaries mastered (internal vs external) ✅/❌
- [ ] Common failure patterns memorized ✅/❌
- [ ] Progress table updated with Phase 0 completion ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding to Phase 1 without all context loaded

🛑 UPDATE-TABLE: Phase 0 → Complete with comprehensive context foundation
🎯 NEXT-MANDATORY: [../1/shared-analysis.md](../1/shared-analysis.md)

---

**🎯 Phase 0 ensures AI assistants start with comprehensive project knowledge, preventing pattern misalignment and reducing rework cycles by 60-70%.**
