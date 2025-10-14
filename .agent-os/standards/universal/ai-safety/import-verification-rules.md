# Import Verification Rules - Universal AI Safety Pattern

**Timeless rule for AI assistants to verify imports before using them.**

---

## 🎯 TL;DR - Import Verification Quick Reference

**Keywords for search**: import verification, verify imports, hallucinated imports, import paths, check imports, AI import errors, module not found, import discovery, package structure

**Core Principle:** NEVER assume import paths. ALWAYS verify against existing codebase first.

**The Problem:**
- AI hallucinates import paths that "seem reasonable"
- Causes `ModuleNotFoundError` at runtime
- Wastes 30+ minutes debugging
- Creates user frustration

**MANDATORY 3-Step Verification:**
```bash
# Step 1: Check package __init__.py
read_file("src/package/__init__.py")  # See public API

# Step 2: Check example code
grep -r "from package import" examples/  # See actual usage

# Step 3: Check documentation
read_file("README.md")  # See documented patterns
```

**Forbidden Practice:**
```python
❌ from package.sdk.tracer import trace  # Assumed, not verified!
❌ from package.utils.helpers import format_data  # Hallucinated!
```

**Safe Workflow:**
```python
# 1. Verify first
read_file("src/honeyhive/__init__.py")
# Found: from honeyhive import trace

# 2. Use verified import
✅ from honeyhive import trace  # Confirmed exists
```

**Real Incident:**
- AI assumed: `from honeyhive.sdk.tracer import trace`
- Reality: `from honeyhive import trace`
- Result: 30 minutes debugging
- Prevention: 2 minutes to verify (15x faster)

**The 2-Minute Rule:**
- Spend 2 minutes verifying imports
- Saves 30+ minutes debugging
- 15x ROI on time investment

**Discovery Methods:**
1. Check `__init__.py` → Public API
2. Check examples → Actual usage patterns
3. Check tests → Real import statements
4. Check docs → Documented patterns
5. grep codebase → Find existing imports

**Enforcement:**
- Pre-commit validation checks all imports
- Linter flags unverified imports
- Code review catches assumed imports

---

## ❓ Questions This Answers

1. "How do I verify import paths?"
2. "What happens if I assume imports?"
3. "How to find correct import paths?"
4. "What is import verification?"
5. "Why do import errors happen?"
6. "How to prevent ModuleNotFoundError?"
7. "What are safe import practices?"
8. "How to discover package structure?"
9. "What is the 2-minute rule?"
10. "How to check if import exists?"

---

## What are Import Verification Rules?

Import verification rules require AI assistants to verify import paths exist in the codebase before using them, preventing hallucinated or assumed imports that cause runtime errors.

**Key principle:** NEVER assume import paths. ALWAYS verify against existing codebase first.

---

## What Import Practices Are Forbidden?

These practices MUST be avoided to prevent hallucinated imports and runtime errors.

### Never Assume Imports

```python
# ❌ BAD: Assuming import paths without verification
from package.sdk.tracer import trace  # Does this path exist?
from package.sdk.event_type import EventType  # Hallucinated?
from package.utils.helpers import format_data  # Guessed?
```

**Problem:** These paths seem "reasonable" but may not exist in the actual codebase.

---

## What Happens When Imports Aren't Verified? (Real Incident)

Real-world example demonstrating the cost of assumed imports.

### The MCP Server Import Error

**What AI Assumed:**
```python
from honeyhive.sdk.tracer import trace, enrich_span
from honeyhive.sdk.event_type import EventType
```

**Error:**
```
ModuleNotFoundError: No module named 'honeyhive.sdk'
```

**What Actually Existed:**
```python
from honeyhive import trace, enrich_span
from honeyhive.models import EventType
```

**Impact:**
- 30+ minutes debugging
- Multiple reload cycles
- User frustration
- Delayed delivery

**Prevention Time:**
- 2 minutes to check `__init__.py` and examples
- **15x faster than debugging**

---

## How to Verify Imports? (MANDATORY Process)

3-step verification process that MUST be followed before using any imports.

### MANDATORY: 3-Step Verification

**Before writing ANY code with imports:**

#### Step 1: Check Package __init__.py

```bash
# Read the package's __init__.py to see public API
read_file("src/package/__init__.py")
```

**Look for:**
- `__all__` list (defines public API)
- Direct imports that are re-exported
- Documented import patterns

**Example:**
```python
# src/honeyhive/__init__.py
from .tracer import trace, enrich_span
from .models import EventType

__all__ = ["trace", "enrich_span", "EventType"]
```

**Conclusion:** Import from top-level package:
```python
from honeyhive import trace, enrich_span
from honeyhive.models import EventType
```

---

#### Step 2: Search for Existing Usage

```bash
# Find how module is actually imported in codebase
grep -r "from package" examples/ --include="*.py" | head -20
grep -r "import package" src/ --include="*.py" | head -20
```

**Look for:**
- Consistent import patterns across multiple files
- Import patterns in examples directory (canonical usage)
- Import patterns in test files (working patterns)

---

#### Step 3: Test the Import

```bash
# Verify import actually works
python -c "from package import symbol; print('Success')"
```

**If import fails:**
- Do NOT use that import path
- Go back to Step 1 and find correct path

---

## What Is the Import Verification Checklist?

Complete checklist to validate imports before use.

**Before writing integration code:**

- [ ] Read package `__init__.py` to see exports
- [ ] Check examples directory for usage patterns
- [ ] Search codebase with `grep` for import patterns
- [ ] Test import in target environment
- [ ] Document where you found the correct pattern

---

## When Should Import Verification Be Applied?

Situations requiring import verification before use.

### Always Apply For:
- ✅ Third-party packages (external dependencies)
- ✅ Internal project modules (cross-module imports)
- ✅ Framework-specific imports (SDK integrations)
- ✅ Any import you haven't directly verified

### Skip For:
- ❌ Standard library (`import os`, `from typing import Dict`)
- ❌ Imports already verified in current session
- ❌ Imports you just wrote in the same file

---

## How to Discover Correct Import Paths?

Methods for finding actual import paths in the codebase.

### Method 1: Package __init__.py (Primary)

```bash
# Always start here - defines public API contract
read_file("src/[package]/__init__.py")
```

**Why:** The `__init__.py` is the source of truth for public API.

---

### Method 2: Examples Directory (Canonical Usage)

```bash
# Find working examples
list_dir("examples/")
read_file("examples/basic_usage.py")
```

**Why:** Examples show the intended usage patterns.

---

### Method 3: Grep for Patterns (Verification)

```bash
# Find all import statements for this package
grep -r "from [package] import" . --include="*.py"
```

**Why:** Shows how codebase consistently imports.

---

### Method 4: Documentation (If Available)

```bash
# Check official documentation
read_file("docs/api/quickstart.md")
```

**Why:** Official docs show recommended import patterns.

---

## What Is the Safe Import Workflow?

Complete workflow demonstrating proper import verification and usage.

### 1. Before Writing Code

```
User requests: "Create integration with Package X"

AI thinks:
1. Do I know Package X's import structure? NO
2. Must verify imports first
3. Read Package X's __init__.py
4. Check Package X examples
5. Test imports work
6. NOW write integration code
```

---

### 2. Document Source

```python
# Integration with Package X
# Import structure verified from:
# - src/package_x/__init__.py (lines 1-20)
# - examples/basic_usage.py (lines 5-10)
# - Tested: python -c "from package_x import Foo"

from package_x import Foo, Bar
```

---

## How Is Import Verification Enforced?

Enforcement mechanisms to prevent unverified imports.

### Pre-Code Generation Gate

**Before generating ANY integration code, AI MUST answer:**

1. ✅ Have I read the package `__init__.py`?
2. ✅ Have I checked the examples directory?
3. ✅ Have I verified imports with `grep`?
4. ✅ Can I cite the file where I found this pattern?

**If NO to any → STOP and verify first.**

---

### Escalation Template

```
🚨 IMPORT VERIFICATION REQUIRED

I need to import from [package] but have not verified the import paths.

Before proceeding, I will:
1. Read [package]/__init__.py
2. Check examples directory
3. Search codebase with grep
4. Test import in target environment

Estimated time: 2 minutes
Risk prevented: 30+ minutes of debugging ImportError

Proceeding with verification...
```

---

## What Import Anti-Patterns Should I Avoid?

Common mistakes that lead to import errors.

### Anti-Pattern 1: "Reasonable" Assumptions

```python
# ❌ BAD: Seems reasonable, but wrong
from myapp.utils.helpers import format_date
# Actual: from myapp.formatting import format_date
```

**Fix:** Verify, don't assume.

---

### Anti-Pattern 2: Copy-Paste from Similar Project

```python
# ❌ BAD: Copied from similar project, different structure
from other_project.api import Client
# This project uses: from this_project import Client
```

**Fix:** Verify for THIS project.

---

### Anti-Pattern 3: Guessing Based on File Structure

```python
# ❌ BAD: File exists at src/package/api/client.py
# Guessing: from package.api.client import Client
# Actual: from package import Client  # Re-exported in __init__.py
```

**Fix:** Check `__init__.py` for re-exports.

---

## How to Test Import Verification?

Testing strategies to validate import correctness.

### Automated Import Verification

```python
def verify_imports(import_statements):
    """
    Verify all import statements actually work.
    Run before committing code.
    """
    for statement in import_statements:
        try:
            exec(statement)
        except ImportError as e:
            raise ValueError(
                f"Import verification failed: {statement}\n"
                f"Error: {e}\n"
                f"Did you verify this import exists?"
            )
```

---

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Extract all import statements from staged files
imports=$(git diff --cached --name-only --diff-filter=ACM | \
          grep '\.py$' | \
          xargs grep -h "^from\|^import" | \
          sort -u)

# Test each import
echo "$imports" | while read line; do
    python -c "$line" 2>/dev/null || {
        echo "❌ Import verification failed: $line"
        exit 1
    }
done
```

---

## What Are Import Verification Best Practices?

Guidelines for reliable import usage.

### 1. Always Start with __init__.py

```
Package structure exploration:
1. Read src/package/__init__.py ← START HERE
2. Check examples/
3. Grep for patterns
4. Test imports
```

---

### 2. Prefer Top-Level Imports

```python
# ✅ GOOD: Top-level import (if available)
from package import Client

# ⚠️ OK: Submodule import (if necessary)
from package.api.client import Client

# ❌ BAD: Deep nesting (usually wrong)
from package.src.internal.impl.client import Client
```

**Principle:** Shallower imports are usually correct public API.

---

### 3. Document Import Source

```python
"""
Integration with External Package.

Import structure verified from:
- external_package/__init__.py (2025-01-15)
- examples/quickstart.py
- Tested with external_package==1.2.3
"""

from external_package import Client, Config
```

---

## What Is the 2-Minute Rule?

Cost-benefit analysis of import verification.

> **"Spend 2 minutes verifying imports before writing code,**  
> **or spend 30+ minutes debugging ImportError after."**

Import verification is not optional. It's a **CRITICAL** safety rule.

---

## Language-Specific Considerations

### Python
- Check `__init__.py` files
- Look for `__all__` lists
- Test with `python -c "import ..."`

### JavaScript/TypeScript
- Check `index.js` or `index.ts`
- Look for `export` statements
- Check `package.json` "exports" field

### Go
- Check package-level exports
- Only capitalized symbols are exported
- Test with `go run`

### Rust
- Check `lib.rs` or `mod.rs`
- Look for `pub use` statements
- Test with `cargo check`

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **New integration** | `search_standards("import verification")` |
| **Third-party package** | `search_standards("how to verify imports")` |
| **Module not found error** | `search_standards("how to find correct import paths")` |
| **SDK integration** | `search_standards("verify package imports")` |
| **Import errors** | `search_standards("import errors")` |
| **Package structure** | `search_standards("discover package structure")` |
| **Hallucinated imports** | `search_standards("AI import errors")` |
| **Before coding** | `search_standards("2 minute rule imports")` |

---

## 🔗 Related Standards

**Query workflow for import verification:**

1. **Start with verification** → `search_standards("import verification")` (this document)
2. **Learn production checklist** → `search_standards("production code checklist")` → `standards/ai-safety/production-code-checklist.md`
3. **Understand testing** → `search_standards("integration testing")` → `standards/testing/integration-testing.md`
4. **Learn code documentation** → `search_standards("code comments")` → `standards/documentation/code-comments.md`

**By Category:**

**AI Safety:**
- `standards/ai-safety/production-code-checklist.md` - Production requirements → `search_standards("production code checklist")`
- `standards/ai-safety/credential-file-protection.md` - File protection rules → `search_standards("credential file protection")`
- `standards/ai-safety/date-usage-policy.md` - Date handling → `search_standards("date usage policy")`
- `standards/ai-safety/git-safety-rules.md` - Git operations → `search_standards("git safety rules")`

**Testing:**
- `standards/testing/integration-testing.md` - Integration test patterns → `search_standards("integration testing")`
- `standards/testing/test-doubles.md` - Test isolation → `search_standards("test doubles")`

**Documentation:**
- `standards/documentation/code-comments.md` - Code documentation → `search_standards("code comments")`
- `standards/documentation/api-documentation.md` - API docs → `search_standards("API documentation")`

---

**Never assume import paths. Always verify. It takes 2 minutes to verify and prevents 30+ minutes of debugging. This is a critical safety rule for all AI-generated code.**
