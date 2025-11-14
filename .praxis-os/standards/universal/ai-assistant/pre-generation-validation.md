# Pre-Generation Validation Protocols

**Universal standard for validating context before generating code or making changes**

---

## 🎯 TL;DR - Pre-Generation Validation Quick Reference

**Keywords for search**: pre-generation validation, validation checkpoints, pre-task validation, context validation, clean state, import verification, date validation, branch validation, validation before code generation

**Core Principle:** Validate context before each code generation to ensure current, accurate understanding of the codebase.

**Three Validation Checkpoints:**
1. **Pre-Task Validation** (once per user request) - Establish safe starting point, clean state PREFERRED
2. **Pre-Generation Validation** (before each file) - Verify current understanding, clean state NOT required
3. **Pre-Commit Validation** (once before commit) - Ensure quality and completeness

**Pre-Generation Validation Checklist (MANDATORY before each file):**
- [ ] Verify imports exist (never hallucinate imports)
- [ ] Check current date (use `current_date` tool, never hardcode)
- [ ] Verify working branch (use `git branch` if relevant)
- [ ] Confirm file locations (never assume paths)
- [ ] Review recent changes (check if file recently modified)

**Common Validation Mistakes:**
- ❌ Using outdated class/module names
- ❌ Hallucinating import paths
- ❌ Hardcoding dates
- ❌ Working on wrong branch
- ❌ Skipping per-file validation in multi-file tasks

**Validation Workflow:**
```
User Request → Pre-Task Validation (once, clean state preferred)
  → Generate File 1 → Pre-Generation Validation
  → Generate File 2 → Pre-Generation Validation
  → All Changes Complete → Pre-Commit Validation
```

**When to Query This Standard:**
- Before generating code → `pos_search_project(content_type="standards", query="pre-generation validation")`
- Import verification → `pos_search_project(content_type="standards", query="import verification")`
- Date handling → `pos_search_project(content_type="standards", query="date usage policy")`

---

## ❓ Questions This Answers

1. "What should I validate before generating code?"
2. "What are the three validation checkpoints?"
3. "When is clean state required vs optional?"
4. "How to verify import paths before using them?"
5. "How to handle dates in code generation?"
6. "What is pre-task vs pre-generation validation?"
7. "How to validate in multi-file tasks?"
8. "What are common validation mistakes?"
9. "When do I need to check working branch?"
10. "How to validate file locations?"

---

## 📋 Overview

### What is Pre-Generation Validation?

**Pre-generation validation** is the systematic process of ensuring AI has current, accurate understanding of the codebase before generating code or making changes.

### Why It Matters

Without pre-generation validation, AI may:
- ❌ Use outdated class/module names
- ❌ Use incorrect import paths
- ❌ Work on wrong branch
- ❌ Use hardcoded dates
- ❌ Base decisions on stale assumptions

With pre-generation validation, AI:
- ✅ Uses current code structure
- ✅ Follows correct import conventions
- ✅ Works on intended branch
- ✅ Uses current date
- ✅ Makes informed decisions

---

## What Are the Three Validation Checkpoints?

**CRITICAL**: There are THREE distinct validation moments, each with different requirements.

```
User Request → AI Work → Commit
     ↓           ↓         ↓
  Pre-Task   Pre-Gen   Pre-Commit
   (Once)   (Per File)  (Once)
```

### Checkpoint 1: Pre-Task Validation
- **When**: Once at the start of each user request
- **Purpose**: Establish safe, known starting point
- **Clean State**: ✅ PREFERRED (warn if not, proceed if user approves)

### Checkpoint 2: Pre-Generation Validation
- **When**: Before generating EACH file or code change
- **Purpose**: Ensure current understanding before each generation
- **Clean State**: ❌ NOT REQUIRED (would block multi-file generation!)

### Checkpoint 3: Pre-Commit Validation
- **When**: Once before committing all changes
- **Purpose**: Ensure quality and completeness
- **Clean State**: N/A (state will be dirty, about to commit)

---

## What Is Checkpoint 1: Pre-Task Validation?

**Run ONCE at the start of each user request.**

### Purpose

Establish a safe, known starting point for the task. Verify environment is correct, date is current, and starting state is understood.

### Validation Steps

```bash
# 1. Get current date (prevents hardcoded dates)
CURRENT_DATE=$(date +"%Y-%m-%d")
echo "Today is: $CURRENT_DATE"

# Store for use throughout task - don't re-run this for each file

# 2. Verify correct branch
git branch --show-current

# Expected: feature branch, not main/master (unless working on main)

# 3. Check starting state
git status --porcelain

# If clean: ✅ Good - safe starting point
# If not clean: ⚠️ Warn user, ask if they want to proceed
#   - May be unfinished work from previous task
#   - May be intentional (user wants to add to uncommitted work)
#   - User decides whether to proceed or clean up first

# 4. Verify development environment
[verify_dev_environment_active]
[verify_language_version]

# Examples by language:
# Python: which python && python --version
# JavaScript: which node && node --version
# Go: which go && go version
# Rust: which rustc && rustc --version

# 5. Review recent history (for awareness)
git log --oneline -5

# Purpose: Understand recent project activity
```

### Checklist

- [ ] **Current date**: Retrieved and stored in variable
- [ ] **Correct branch**: Verified and confirmed
- [ ] **Starting state**: Checked (warn if not clean, proceed if user approves)
- [ ] **Development environment**: Active and verified
- [ ] **Language/runtime version**: Confirmed
- [ ] **Recent history**: Reviewed last 5 commits
- [ ] **User intent**: Understand full scope of request

### Clean State Requirement

✅ **PREFERRED** but not strictly required

**If starting state is NOT clean**:
1. Warn user: "Current state has uncommitted changes: [list files]"
2. Ask: "Do you want to proceed or clean up first?"
3. If user approves: Proceed with task
4. If user wants cleanup: Wait for user to clean up

**Why not strictly required**: User may intentionally have uncommitted work they want to add to.

---

## What Is Checkpoint 2: Pre-Generation Validation?

**Run BEFORE generating EACH file or code change.**

### Purpose

Ensure current understanding of codebase before each generation. Be AWARE of project state without BLOCKING on it.

### CRITICAL: Multi-File Task Support

**This validation provides AWARENESS, not BLOCKING.**

Multi-file tasks require uncommitted changes after the first file. If we required clean state here, AI could only generate ONE file per task!

**Example Problem** (if we required clean state):
```bash
Task: "Create module with 3 files"

Generate file 1: ✅ State clean, proceed
# After file 1: State dirty (file 1 uncommitted)

Generate file 2: ❌ State not clean, BLOCKED! 
# Can't generate file 2!

Result: Only 1 file generated, task incomplete
```

**Correct Behavior**:
```bash
Task: "Create module with 3 files"

Generate file 1: ✅ State clean, proceed
# After file 1: State dirty - AWARE but not blocking

Generate file 2: ✅ State dirty (file 1), AWARE, proceed  
# After file 2: State dirty - AWARE but not blocking

Generate file 3: ✅ State dirty (files 1-2), AWARE, proceed

Result: All 3 files generated successfully
```

### Validation Steps

```bash
# 1. Use current date from pre-task variable
# $CURRENT_DATE already set in pre-task validation
# Don't re-run date command for each file

# 2. Verify current codebase understanding
read_file [entry_point_file]              # Check current API structure
[search] "[class_pattern]" [source_dir]   # Verify current class names
[search] "[import_pattern]" [examples_dir] # Check import conventions
[search] "[type_pattern]" [source_dir]    # Verify type usage patterns

# Examples by language:
# Python: 
#   read_file src/project/__init__.py
#   grep -r "^class " src/
#   grep -r "^from .* import" src/
#
# JavaScript:
#   read_file src/index.js
#   grep -r "^export class" src/
#   grep -r "^import.*from" src/
#
# Go:
#   read_file main.go
#   grep -r "^type.*struct" .
#   grep -r "^func" .

# 3. State awareness (NOT blocking!)
git status --porcelain

# Purpose: Know what's uncommitted, understand task progress
# NOT REQUIRED: Clean state (would block multi-file generation)
# 
# Interpretation:
# - If clean: First file in task
# - If dirty: Subsequent files in multi-file task (expected!)
# - Understand what's part of current task vs pre-existing

# 4. Verify still on correct branch
git branch --show-current

# Purpose: Prevent accidental branch switch during task
# This CAN block - if branch changed, something is wrong
```

### Checklist

- [ ] **API structure**: Current understanding verified
- [ ] **Class/module names**: Confirmed current names
- [ ] **Import patterns**: Verified correct conventions  
- [ ] **Type patterns**: Confirmed current usage
- [ ] **State awareness**: Know what's uncommitted (NOT blocking)
- [ ] **Correct branch**: Still on intended branch (this IS blocking)
- [ ] **Task context**: Understand what's already generated in this task

### Clean State Requirement

❌ **NOT REQUIRED** - Would block multi-file generation

**Key Principle**: Be AWARE of state, don't BLOCK on state

---

## What Is Checkpoint 3: Pre-Commit Validation?

**Run ONCE before committing all changes.**

### Purpose

Ensure all changes meet quality standards before committing. This is where we verify quality, not state cleanliness (state WILL be dirty at this point).

### Validation Steps

```bash
# 1. Verify committing from correct branch
git branch --show-current

# Should still be on the intended branch

# 2. Review what's being committed
git status --porcelain

# See all uncommitted changes that will be part of commit
# Expected: Multiple files if multi-file task

# 3. Run quality gates (ALL must pass)
[format_command]              # Code formatting
[lint_command]                # Static analysis
[type_check_command]          # Type checking
[unit_test_command]           # Unit tests
[integration_test_command]    # Integration tests (if applicable)

# Examples by language:
# Python:
#   tox -e format    # Black + isort
#   tox -e lint      # Pylint + mypy
#   tox -e unit      # pytest unit tests
#
# JavaScript:
#   npm run format   # Prettier
#   npm run lint     # ESLint
#   npm test         # Jest
#
# Go:
#   gofmt -l .
#   golint ./...
#   go test ./...
#
# Rust:
#   cargo fmt --check
#   cargo clippy
#   cargo test

# 4. Verify documentation (if applicable)
[doc_build_command]           # Documentation builds without warnings

# Examples:
# Python: cd docs && make html
# JavaScript: npm run docs
# Rust: cargo doc --no-deps
```

### Checklist

- [ ] **Correct branch**: Verified
- [ ] **Changes reviewed**: Appropriate scope
- [ ] **Formatting**: 100% compliant
- [ ] **Static analysis**: Meets project threshold
- [ ] **Type checking**: Zero errors (if project requires)
- [ ] **Unit tests**: 100% pass
- [ ] **Integration tests**: 100% pass (if applicable)
- [ ] **Documentation**: Builds successfully (if applicable)
- [ ] **User review**: Requested and received

### Clean State Requirement

N/A - State WILL be dirty (that's what we're committing)

---

## What Is Context-Specific Validation?

**Additional validation for specific contexts.**

### For Test Fixing Tasks

**Additional validation before fixing tests**:

```bash
# Understand production code before fixing tests

# 1. Read the production module being tested
read_file [production_module]

# 2. Search for method/class being tested
[search] "def method_name" [source_dir]
[search] "class ClassName" [source_dir]

# 3. Check method signatures
[search] -A10 "def method_name" [production_file]

# Purpose: Understand current implementation before fixing test
# Tests fail because they don't match production - need to know production
```

**Why This Matters**:

```python
# Test fails: ImportError: cannot import name 'OldClass'
# Without validation: AI guesses the import path, tries multiple times
# With validation: AI searches for class, finds it moved to new location, fixes import immediately
```

---

### For API Changes

**Additional validation before changing APIs**:

```bash
# Check current API consumers before making changes

# 1. Find all imports of the API
[search] "from module import" [examples_dir]
[search] "from module import" [test_dir]
[search] "import module" [source_dir]

# 2. Find all usages of the API
[search] "module\.function" [source_dir]
[search] "Class\(" [source_dir]

# Purpose: Understand impact of changes
# Helps identify breaking changes before making them
```

**Why This Matters**:

```python
# Changing function signature
# Without validation: AI changes function, breaks 10 call sites
# With validation: AI sees 10 call sites, updates them all in same commit
```

---

### For Configuration Changes

**Additional validation before changing configuration**:

```bash
# Check configuration usage patterns

# 1. Find how configuration is accessed
[search] "config\." [source_dir]
[search] "Config\(" [source_dir]

# 2. Find configuration creation
[search] "load_config" [source_dir]
[search] "create_config" [source_dir]

# Purpose: Ensure consistency in configuration usage
```

---

## Example: How Does Validation Work in Multi-File Tasks?

**Scenario**: User says "Create tracer module with implementation, config, and tests (3 files)"

### Pre-Task Validation (Once at Start)

```bash
# ============================================================
# PRE-TASK VALIDATION (Run ONCE at start of user request)
# ============================================================

CURRENT_DATE=$(date +"%Y-%m-%d")
echo "Today is: $CURRENT_DATE"
# Output: Today is: 2025-10-09

git branch --show-current
# Output: feature/new-tracer

git status --porcelain
# Output: (empty - clean)
# ✅ Clean starting point

which python && python --version
# Output: /path/to/venv/bin/python
#         Python 3.11.0
# ✅ Environment verified

git log --oneline -5
# Output: Recent commits for context
# ✅ Aware of recent changes

# PRE-TASK VALIDATION COMPLETE ✅
# Safe to proceed with task
```

---

### Generate File 1: src/tracer.py

```bash
# ============================================================
# PRE-GENERATION VALIDATION (Before file 1)
# ============================================================

# Use current date from pre-task (already set)
# $CURRENT_DATE = 2025-10-09

# Verify current codebase understanding
read_file src/__init__.py
# Check current API exports to understand structure
# ✅ Current understanding verified

grep -r "^class " src/
# Verify current class names and patterns
# ✅ Naming conventions understood

# State awareness (NOT blocking)
git status --porcelain
# Output: (empty - clean)
# ✅ AWARE: First file in task, state clean

# Verify still on correct branch
git branch --show-current
# Output: feature/new-tracer
# ✅ Still on correct branch

# PRE-GENERATION VALIDATION COMPLETE ✅
# Safe to generate file 1

# GENERATE: src/tracer.py
[AI writes src/tracer.py with Tracer class implementation]
```

---

### Generate File 2: src/tracer_config.py

```bash
# ============================================================
# PRE-GENERATION VALIDATION (Before file 2)
# ============================================================

# State awareness (NOT blocking)
git status --porcelain
# Output: ?? src/tracer.py
# ✅ AWARE: File 1 uncommitted (expected in multi-file task)
# ✅ NOT BLOCKING: Proceed with file 2
# 
# This is the CRITICAL FIX - we don't block on dirty state!

# Verify still on correct branch
git branch --show-current  
# Output: feature/new-tracer
# ✅ Still on correct branch

# Verify current patterns for config classes
grep -r "class.*Config" src/
# Check how other config classes are structured
# ✅ Pattern understood

# PRE-GENERATION VALIDATION COMPLETE ✅
# Safe to generate file 2

# GENERATE: src/tracer_config.py
[AI writes src/tracer_config.py with TracerConfig class]
```

---

### Generate File 3: tests/test_tracer.py

```bash
# ============================================================
# PRE-GENERATION VALIDATION (Before file 3)
# ============================================================

# State awareness (NOT blocking)
git status --porcelain
# Output: ?? src/tracer.py
#         ?? src/tracer_config.py
# ✅ AWARE: Files 1-2 uncommitted (expected in multi-file task)
# ✅ NOT BLOCKING: Proceed with file 3

# Read production code to test it correctly
read_file src/tracer.py
# Understand implementation to write appropriate tests
# ✅ Implementation understood

# Check existing test patterns
grep -r "^class Test" tests/
# Verify test naming conventions
# ✅ Test patterns understood

# PRE-GENERATION VALIDATION COMPLETE ✅
# Safe to generate file 3

# GENERATE: tests/test_tracer.py
[AI writes tests/test_tracer.py with comprehensive tests]
```

---

### Pre-Commit Validation (Once Before Committing All 3 Files)

```bash
# ============================================================
# PRE-COMMIT VALIDATION (Before committing all 3 files)
# ============================================================

# Verify still on correct branch
git branch --show-current
# Output: feature/new-tracer
# ✅ Correct branch

# Review what's being committed
git status --porcelain
# Output: ?? src/tracer.py
#         ?? src/tracer_config.py
#         ?? tests/test_tracer.py
# ✅ All 3 files ready to commit

# Run quality gates (ALL must pass)
tox -e format
# Output: ✅ All 3 files formatted correctly

tox -e lint
# Output: ✅ All 3 files pass linting (Pylint 10.0/10.0)

tox -e type
# Output: ✅ All 3 files pass type checking (MyPy 0 errors)

tox -e unit
# Output: ✅ All tests pass (100%)

# PRE-COMMIT VALIDATION COMPLETE ✅
# Safe to commit all 3 files

# Present to user for review
"Ready to commit 3 files:
 - src/tracer.py (implementation)
 - src/tracer_config.py (configuration)
 - tests/test_tracer.py (tests)

All quality gates passed. Commit?"

# User approves
git add src/tracer.py src/tracer_config.py tests/test_tracer.py
git commit -m "feat: add tracer module with configuration"

# TASK COMPLETE ✅
```

---

## What Are Common Validation Mistakes?

### Mistake 1: Requiring Clean State in Pre-Generation

**❌ WRONG**:
```bash
# Pre-generation validation (before each file)
git status --porcelain
if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: State must be clean"
    exit 1
fi
```

**Why It's Wrong**: Blocks multi-file generation after first file

**✅ CORRECT**:
```bash
# Pre-generation validation (before each file)
git status --porcelain
# Note uncommitted files, understand task context
# Continue regardless of state
```

---

### Mistake 2: Not Validating Current API Structure

**❌ WRONG**:
```python
# Assuming class name based on memory
from module import OldClassName  # May have been renamed!
```

**Why It's Wrong**: Uses outdated assumptions

**✅ CORRECT**:
```bash
# Validate current structure
grep -r "class.*ClassName" src/
# Find actual current class name, use that
```

---

### Mistake 3: Re-Running Date Command for Each File

**❌ WRONG**:
```bash
# Before each file:
CURRENT_DATE=$(date +"%Y-%m-%d")
```

**Why It's Wrong**: Wasteful, could cause inconsistency if crossing midnight

**✅ CORRECT**:
```bash
# Pre-task: Get date once
CURRENT_DATE=$(date +"%Y-%m-%d")

# Pre-generation: Use stored date
# Use $CURRENT_DATE variable
```

---

## How to Define Project-Specific Validation?

**Projects should define validation commands in `.praxis-os/standards/development/validation-commands.md`.**

### Example Validation Commands File

```markdown
# Project Name - Validation Commands

## Environment Validation

### Python Virtual Environment
```bash
which python
# Expected: /path/to/project/venv/bin/python

python --version
# Expected: Python 3.11+
```

## Codebase Understanding

### API Structure
```bash
read_file src/project/__init__.py
```

### Import Patterns
```bash
grep -r "^from project import" src/
```

## Quality Gates

### Format Check
```bash
tox -e format
# Must pass - zero tolerance
```

### Lint Check
```bash
tox -e lint
# Must pass - Pylint ≥8.0, MyPy 0 errors
```

### Test Execution
```bash
tox -e unit
# Must pass 100%
```
```

---

## How to Teach Validation to New AI Assistants?

### Key Principles

1. **Three checkpoints, three purposes** - Pre-task (safety), pre-generation (understanding), pre-commit (quality)
2. **Clean state at task start, not per-file** - Critical for multi-file tasks
3. **State awareness, not blocking** - Know what's uncommitted, don't block on it
4. **Current date once, use many times** - Don't re-run date command
5. **Validation is fast, rework is slow** - 30-90 seconds validation prevents hours of debugging

---

## ❓ FAQ

### Q: Why three validation checkpoints instead of one?

**A**: Each has a different purpose and timing. Pre-task establishes safety, pre-generation ensures understanding, pre-commit verifies quality.

### Q: Why not require clean state before each file?

**A**: It would block multi-file generation. After file 1, state is dirty, so file 2 would be blocked.

### Q: What if I'm not sure if state is clean because of current task or previous work?

**A**: Check git status early in task. If dirty at start, warn user. If becomes dirty during task, that's expected.

### Q: Should I validate before making each small change within a file?

**A**: No. Validate once before generating the file. Making multiple edits within same file doesn't need repeated validation.

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Before generating code** | `pos_search_project(content_type="standards", query="pre-generation validation")` |
| **Multi-file tasks** | `pos_search_project(content_type="standards", query="validation checkpoints")` |
| **Import verification** | `pos_search_project(content_type="standards", query="import verification rules")` |
| **Date handling** | `pos_search_project(content_type="standards", query="date usage policy")` |
| **Clean state questions** | `pos_search_project(content_type="standards", query="when is clean state required")` |
| **Validation mistakes** | `pos_search_project(content_type="standards", query="common validation mistakes")` |

---

## 🔗 Related Standards

**Query workflow for validation mastery:**

1. **Start with pre-generation validation** → `pos_search_project(content_type="standards", query="pre-generation validation")` (this document)
2. **Learn compliance protocol** → `pos_search_project(content_type="standards", query="compliance checking")` → `standards/ai-assistant/compliance-protocol.md`
3. **Understand commit protocol** → `pos_search_project(content_type="standards", query="commit protocol")` → `standards/ai-assistant/commit-protocol.md`
4. **Master import verification** → `pos_search_project(content_type="standards", query="import verification")` → `standards/ai-safety/import-verification-rules.md`

**By Category:**

**AI Safety:**
- `standards/ai-safety/import-verification-rules.md` - Verify imports before use → `pos_search_project(content_type="standards", query="import verification rules")`
- `standards/ai-safety/date-usage-policy.md` - Date handling → `pos_search_project(content_type="standards", query="date usage policy")`
- `standards/ai-safety/git-safety-rules.md` - Git safety → `pos_search_project(content_type="standards", query="git safety rules")`

**AI Assistant:**
- `standards/ai-assistant/compliance-protocol.md` - Check standards before code → `pos_search_project(content_type="standards", query="compliance checking")`
- `standards/ai-assistant/commit-protocol.md` - Review and commit → `pos_search_project(content_type="standards", query="commit protocol")`
- `standards/ai-assistant/analysis-methodology.md` - Comprehensive analysis → `pos_search_project(content_type="standards", query="analysis methodology")`

---

**This is a universal standard. It applies to all projects using prAxIs OS, regardless of programming language or technology stack.**

**For project-specific validation commands, see `.praxis-os/standards/development/validation-commands.md` in your project.**

