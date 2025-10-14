# Git Safety Rules - Universal AI Safety Pattern

**Timeless rules for AI assistants to prevent data loss through git operations.**

## What Are Git Safety Rules?

Git safety rules define operations that AI assistants must NEVER perform automatically, as they can cause permanent data loss or confusing repository states.

**Key principle:** AI assistants should use file editing tools, not destructive git operations.

---

## 🚫 STRICTLY FORBIDDEN Operations

### Category 1: File Reversion (Destroys Uncommitted Work)

```bash
# ❌ NEVER - Loses all uncommitted changes
git checkout HEAD -- <file>
git checkout -- <file>
git restore <file>

# Example scenario:
# User worked 3 hours on file.py (uncommitted)
# AI runs: git checkout HEAD -- file.py
# Result: 3 hours of work PERMANENTLY LOST
```

---

### Category 2: History Rewriting (Destroys Commits)

```bash
# ❌ NEVER - Resets to previous state, loses commits
git reset --hard
git reset --hard <commit>
git reset --mixed <commit>

# ❌ NEVER - Creates confusing history
git revert <commit>
```

---

### Category 3: Force Operations (Overwrites Remote)

```bash
# ❌ NEVER - Overwrites remote history
git push --force
git push -f
git push --force-with-lease  # Still dangerous
```

---

### Category 4: Branch Operations (Loses Branches)

```bash
# ❌ NEVER - Permanently deletes branches
git branch -D <branch>
git branch --delete --force <branch>

# ❌ NEVER - Switches context, can lose work
git checkout <branch>
git checkout <commit>  # Detached HEAD state
```

---

### Category 5: Stash/Clean Operations (Loses Files)

```bash
# ❌ NEVER - Permanently deletes stashed work
git stash drop
git stash clear

# ❌ NEVER - Removes untracked files forever
git clean -fd
git clean -fx
```

---

## ✅ Safe Alternatives

### Instead of Reverting Files → Use File Editing

```bash
# ❌ WRONG
git checkout HEAD -- broken_file.py

# ✅ CORRECT
# Use search_replace, write, or other file editing tools
search_replace("broken_file.py", "wrong_code", "correct_code")
```

---

### Instead of Resetting → Use Targeted Fixes

```bash
# ❌ WRONG
git reset --hard  # "Fix" linting errors by reverting everything

# ✅ CORRECT
# Fix the actual issue
run_terminal_cmd("black src/")
run_terminal_cmd("isort src/")
```

---

### Instead of Resolving Conflicts with Checkout → Edit Files

```bash
# ❌ WRONG
git checkout HEAD -- conflicted_file.py  # Loses one side of conflict

# ✅ CORRECT
# Read file, understand conflict, make surgical edit
read_file("conflicted_file.py")
# Manually resolve conflicts with targeted edits
```

---

## 🛡️ Safety Protocol

### Pre-Operation Checks (MANDATORY)

**Before ANY git operation, AI must check:**

```bash
# 1. Check for uncommitted work
git status --porcelain

# If output is non-empty → STOP
# Do NOT proceed with destructive operations
```

```bash
# 2. Verify current branch
git branch --show-current

# Ensure you understand what branch you're on
```

```bash
# 3. Check for untracked files  
git ls-files --others --exclude-standard

# Warn if untracked files exist
```

---

## ✅ Safe Git Operations

**AI assistants MAY use these read-only/additive operations:**

```bash
# ✅ SAFE: Information gathering
git status
git log --oneline
git branch
git diff
git show <commit>
git remote -v

# ✅ SAFE: Adding work (not destructive)
git add <file>
git commit -m "message"
git push  # (without --force)
```

---

## 🚨 Real-World Incident

### The 3-Hour Loss

**What Happened:**
```bash
# User spent 3 hours implementing complex feature
# Changes were uncommitted (user's workflow)
# AI assistant tried to "fix" a linting error
# AI ran: git checkout HEAD -- src/feature.py
# Result: 3 hours of work PERMANENTLY LOST
```

**Correct Approach:**
```bash
# AI should have used linter to fix the issue
run_terminal_cmd("black src/feature.py")
# This fixes linting WITHOUT destroying user's work
```

---

## 📋 Compliance Checklist

**Before ANY git operation:**

- [ ] Is operation on forbidden list? (If YES → STOP)
- [ ] Will this operation lose uncommitted changes? (If YES → STOP)
- [ ] Is there a safer alternative (file editing)? (If YES → use it)
- [ ] Did user explicitly request this operation? (If NO → escalate)
- [ ] Have I checked `git status`? (If NO → check first)

---

## 🆘 Escalation Protocol

### When to Escalate to User

**Immediately escalate when:**
- Merge conflicts need resolution
- Branch switching is needed
- History rewriting is suggested
- Force operations are needed
- Any uncertainty about safety

### Escalation Template

```
🚨 GIT SAFETY ESCALATION

I need to perform a git operation that could affect your work:

Operation: [specific git command]
Purpose: [why this is needed]
Risk: [potential data loss]
Alternatives: [safer options if available]

Please confirm if you want me to proceed or suggest an alternative.
```

---

## 🚫 Why These Rules Exist

### 1. AI Has No Time Pressure

```
Human developer: "I'll just git reset --hard, it's faster"
                (Tired, deadline pressure, mistakes happen)

AI assistant: [Has microseconds to think]
             [Never gets tired]
             [Should ALWAYS use safer alternative]
```

**AI has no excuse for shortcuts.**

---

### 2. File Editing is Always Safer

```
git checkout HEAD -- file.py     → DESTROYS uncommitted work
search_replace(file.py, ...)     → ONLY changes what you specify
```

**Principle:** Surgical edits > nuclear git operations

---

### 3. Recovery is Harder Than Prevention

```
Time to verify: 5 seconds (git status)
Time to edit file: 10 seconds (search_replace)
Time to recover lost work: HOURS or IMPOSSIBLE
```

---

## 🔍 Monitoring

### Audit All Git Operations

```bash
# Log all git commands for review
export PROMPT_COMMAND='history -a'
export HISTTIMEFORMAT="%Y-%m-%d %H:%M:%S "
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Block dangerous operations
if [[ "$1" == "reset" && "$2" == "--hard" ]]; then
    echo "❌ BLOCKED: git reset --hard is forbidden"
    exit 1
fi
```

---

## 📚 Related Patterns

- **Graceful Degradation:** When git operation fails, use file editing instead
- **Least Privilege:** AI should use minimal permissions (file editing, not git)
- **Reversibility:** File edits are reversible (undo), git operations often aren't

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.agent-os/standards/ai-workflows/git-safety-enforcement.md` (Language-specific enforcement)
- See `.agent-os/standards/ai-workflows/file-editing-patterns.md` (Safe alternatives)
- Etc.

---

**Git operations are powerful but dangerous. AI assistants should use file editing tools by default. Only use git for safe, read-only, or explicitly requested operations. When in doubt, escalate to user.**
