# Import Verification Rules

**🚨 CRITICAL: Verify Before Import**

**Status:** MANDATORY  
**Priority:** CRITICAL  
**Enforcement:** Pre-Code Generation

---

## 🎯 Core Principle

**NEVER assume import paths. ALWAYS verify against existing codebase first.**

AI assistants frequently hallucinate or assume import paths that don't exist, leading to `ImportError` failures that could have been prevented with simple verification.

---

## 🚫 Forbidden Practices

### **Never Do This**

```python
# ❌ BAD: Assuming import paths without verification
from honeyhive.sdk.tracer import trace  # Does this exist?
from honeyhive.sdk.event_type import EventType  # Hallucinated path
```

**Problem:** These paths were assumed based on "reasonable" naming conventions but don't actually exist in the codebase.

---

## ✅ Required Verification Process

### **MANDATORY: 3-Step Import Verification**

**Before writing ANY code that imports from the project, you MUST:**

#### **Step 1: Check the Main Package Export**

```bash
# Read the package __init__.py to see what's exported
read_file("src/honeyhive/__init__.py")
```

**Look for:**
- Public API exports (`__all__` list)
- Direct imports that are re-exported
- Documented import patterns

#### **Step 2: Search for Existing Usage**

```bash
# Find how the module is actually imported in the codebase
grep -r "from honeyhive" examples/ --include="*.py" | head -20
grep -r "from honeyhive" src/ --include="*.py" | head -20
```

**Look for:**
- Consistent import patterns across multiple files
- Import statements in examples directory (canonical usage)
- Import statements in test files (working patterns)

#### **Step 3: Verify Imports Work**

```bash
# Test the import path actually works
./python-sdk/bin/python -c "from honeyhive import trace, enrich_span; print('Success')"
```

---

## 📋 Import Verification Checklist

**Complete this checklist BEFORE writing integration code:**

- [ ] **Read `__init__.py`**: Verified what the package exports
- [ ] **Check examples**: Found actual usage in examples directory
- [ ] **Search codebase**: Confirmed import pattern with `grep`
- [ ] **Test import**: Validated import works in target Python environment
- [ ] **Document source**: Note where you found the correct pattern

---

## 🎯 When to Apply

**This rule applies when integrating with:**

- ✅ Third-party packages (external dependencies)
- ✅ Internal project modules (cross-module imports)
- ✅ Framework-specific imports (SDK integrations)
- ✅ Any import you haven't directly verified

**This rule does NOT apply to:**

- ❌ Standard library imports (`import os`, `from typing import Dict`)
- ❌ Imports you've already verified in the current session

---

## 🔍 Discovery Methods

### **Method 1: Package __init__.py (Primary)**

```bash
# Always start here
read_file("src/[package]/__init__.py")
```

**Why:** The `__init__.py` defines the public API contract.

### **Method 2: Examples Directory (Canonical Usage)**

```bash
# Find working examples
codebase_search(
  query="example usage of [module] imports",
  target_directories=["examples"]
)
```

**Why:** Examples show the intended usage patterns.

### **Method 3: Grep for Patterns (Verification)**

```bash
# Find all import statements
grep -r "from [package] import" . --include="*.py"
```

**Why:** Shows how the codebase consistently imports.

### **Method 4: Read Recent Code (Context)**

```bash
# Check recently written integration code
read_file("[recent_integration_file].py")
```

**Why:** Recent code likely uses current import patterns.

---

## 📊 Real-World Case Study

### **The MCP Server Import Error (October 2025)**

**What Happened:**
```python
# AI Assistant wrote:
from honeyhive.sdk.tracer import trace, enrich_span
from honeyhive.sdk.event_type import EventType

# Error: ModuleNotFoundError: No module named 'honeyhive.sdk'
```

**Root Cause:** AI assumed import paths without verification.

**What Should Have Been Done:**

1. **Read `src/honeyhive/__init__.py`** → Would have seen:
   ```python
   from .tracer import trace, enrich_span
   from .models import EventType
   ```

2. **Check examples** → Would have found:
   ```python
   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   ```

3. **Correct imports:**
   ```python
   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   ```

**Time Wasted:** 30+ minutes of debugging, multiple reloads, user frustration

**Time if Verified First:** 2 minutes to check `__init__.py` and examples

---

## 🚨 Enforcement Protocol

### **Pre-Code Generation Gate**

**Before generating ANY integration code, the AI assistant MUST answer:**

1. ✅ Have you read the package `__init__.py`?
2. ✅ Have you checked the examples directory?
3. ✅ Have you verified the import with `grep`?
4. ✅ Can you cite the file where you found this pattern?

**If NO to any question → STOP and verify first.**

### **Escalation Template**

When you're about to write import statements without verification:

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
```

---

## 📚 Related Standards

- **[Validation Protocols](validation-protocols.md)** - Comprehensive validation requirements
- **[Pre-Generation Checklist](code-generation/pre-generation-checklist.md)** - Full pre-generation validation
- **[Quality Framework](quality-framework.md)** - Overall quality gates

---

## 🎓 Key Takeaway

**The 2-Minute Rule:**

> *"Spend 2 minutes verifying imports before writing code, or spend 30+ minutes debugging ImportError after."*

Import verification is not optional. It's a **CRITICAL** safety rule that prevents easily avoidable failures.

---

**🔐 REMEMBER**: 
- **NEVER** assume import paths
- **ALWAYS** check `__init__.py` first
- **ALWAYS** search examples directory
- **ALWAYS** verify with grep before using
- Prevention is 15x faster than debugging

