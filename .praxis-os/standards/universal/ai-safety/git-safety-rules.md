# Git Safety Rules - Universal AI Safety Pattern

**Timeless rules for AI assistants to prevent data loss through git operations.**

---

## 🎯 TL;DR - Git Safety Rules Quick Reference

**Keywords for search**: git safety, git rules, AI git operations, git destructive commands, git data loss, never git reset, never git push force, safe git operations

**Core Principle:** AI assistants MUST NEVER run destructive git operations. Use file editing tools instead.

**STRICTLY FORBIDDEN Operations:**
```bash
❌ git checkout -- <file>         # Loses uncommitted work
❌ git reset --hard               # Destroys commits
❌ git push --force               # Overwrites remote
❌ git branch -D <branch>         # Deletes branches
❌ git stash drop                 # Loses stashed work
❌ git clean -fd                  # Removes untracked files
❌ git rebase -i                  # Rewrites history
❌ git commit --amend             # Changes commit history
```

**Why These Are Forbidden:**
- Cause PERMANENT data loss (no undo)
- Destroy hours of uncommitted work
- Overwrite remote history (confuses team)
- Create detached HEAD states (confusing)
- Delete branches permanently

**Safe Alternatives:**
- Instead of `git checkout --` → Use `search_replace()` or `write()` tools
- Instead of `git reset` → Tell user to manually review/reset
- Instead of `git push -f` → Tell user to resolve conflicts manually
- Instead of `git branch -D` → Tell user to delete manually if needed
- Read-only git operations are SAFE: `git status`, `git log`, `git diff`

**Safe Git Operations:**
```bash
✅ git status                     # Check repository state
✅ git log                        # View commit history
✅ git diff                       # View changes
✅ git branch                     # List branches (no flags)
✅ git show <commit>              # View commit details
```

**Real Incident:**
- AI ran `git checkout HEAD -- file.py`
- Lost 3 hours of uncommitted work
- User had to recreate from memory
- PERMANENT loss (no recovery)

**Enforcement:**
- Pre-commit hooks block destructive commands
- Code review flags git operations
- Validation fails on forbidden commands

---

## ❓ Questions This Answers

1. "Can AI run git commands?"
2. "What git operations are forbidden?"
3. "Why can't AI use git reset?"
4. "What happens if AI runs git push --force?"
5. "What are safe git operations?"
6. "How to revert file changes?"
7. "Can AI delete git branches?"
8. "What git commands cause data loss?"
9. "How to handle git conflicts?"
10. "What git operations are read-only safe?"

---

## What Are Git Safety Rules?

Git safety rules define operations that AI assistants must NEVER perform automatically, as they can cause permanent data loss or confusing repository states.

**Key principle:** AI assistants should use file editing tools, not destructive git operations.

---

## What Git Operations Are STRICTLY FORBIDDEN?

These operations MUST NEVER be performed by AI assistants due to permanent data loss risk.

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

## What Are Safe Alternatives to Destructive Git Operations?

When you need to modify files or repository state, use these safe alternatives.

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

## How Is Git Safety Enforced?

Multiple enforcement mechanisms prevent destructive git operations.

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

## What Git Operations Are Safe?

Read-only git operations that do not modify repository state are safe for AI use.

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

## What Happens When Git Safety Rules Are Violated? (Real Incident)

Real-world example demonstrating catastrophic consequences of destructive git operations.

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

## How to Validate Git Safety Compliance?

Checklist to verify compliance before any git operation.

**Before ANY git operation:**

- [ ] Is operation on forbidden list? (If YES → STOP)
- [ ] Will this operation lose uncommitted changes? (If YES → STOP)
- [ ] Is there a safer alternative (file editing)? (If YES → use it)
- [ ] Did user explicitly request this operation? (If NO → escalate)
- [ ] Have I checked `git status`? (If NO → check first)

---

## What to Do If Destructive Git Operation Is Requested? (Escalation)

Response protocol when user requests forbidden git operations.

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

## Why Do Git Safety Rules Exist?

Understanding the fundamental reasons for restricting AI git operations.

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

## How to Monitor Git Safety Compliance?

Methods for detecting and preventing destructive git operations.

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

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Git operations** | `pos_search_project(content_type="standards", query="git safety rules")` |
| **Revert changes** | `pos_search_project(content_type="standards", query="how to revert file changes")` |
| **Forbidden commands** | `pos_search_project(content_type="standards", query="forbidden git commands")` |
| **git reset** | `pos_search_project(content_type="standards", query="can AI use git reset")` |
| **git push force** | `pos_search_project(content_type="standards", query="git push force")` |
| **Safe git operations** | `pos_search_project(content_type="standards", query="safe git operations")` |
| **Data loss** | `pos_search_project(content_type="standards", query="git data loss")` |
| **Branch operations** | `pos_search_project(content_type="standards", query="AI delete git branch")` |

---

## 🔗 Related Standards

**Query workflow for git safety:**

1. **Start with git rules** → `pos_search_project(content_type="standards", query="git safety rules")` (this document)
2. **Learn production checklist** → `pos_search_project(content_type="standards", query="production code checklist")` → `standards/ai-safety/production-code-checklist.md`
3. **Learn credential protection** → `pos_search_project(content_type="standards", query="credential file protection")` → `standards/ai-safety/credential-file-protection.md`
4. **Understand security** → `pos_search_project(content_type="standards", query="security patterns")` → `standards/security/security-patterns.md`

**By Category:**

**AI Safety:**
- `standards/ai-safety/credential-file-protection.md` - File protection rules → `pos_search_project(content_type="standards", query="credential file protection")`
- `standards/ai-safety/production-code-checklist.md` - Production requirements → `pos_search_project(content_type="standards", query="production code checklist")`
- `standards/ai-safety/date-usage-policy.md` - Date handling → `pos_search_project(content_type="standards", query="date usage policy")`
- `standards/ai-safety/import-verification-rules.md` - Import safety → `pos_search_project(content_type="standards", query="import verification")`

**Installation:**
- `standards/installation/gitignore-requirements.md` - Gitignore patterns → `pos_search_project(content_type="standards", query="gitignore requirements")`

---

**Git operations are powerful but dangerous. AI assistants should use file editing tools by default. Only use git for safe, read-only, or explicitly requested operations. When in doubt, escalate to user.**
