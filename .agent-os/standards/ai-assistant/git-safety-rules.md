# AI Assistant Git Safety Rules

**🚨 CRITICAL: Data Loss Prevention for AI Assistants**

This document defines strict safety rules that AI assistants MUST follow to prevent accidental data loss and maintain code integrity during development sessions.

## 🚫 STRICTLY FORBIDDEN Git Operations

**AI assistants are ABSOLUTELY FORBIDDEN from executing these commands without explicit user instruction:**

### Destructive File Operations
```bash
# ❌ NEVER USE - Can lose hours of uncommitted work
git checkout HEAD --                    # Reverts files to last commit
git checkout HEAD -- <file>            # Reverts specific file
git checkout -- <file>                 # Reverts file to HEAD
git restore <file>                      # Restores file from HEAD

# ❌ NEVER USE - Can lose commit history  
git reset --hard                        # Resets to HEAD, loses all changes
git reset --hard <commit>               # Resets to specific commit
git reset --mixed <commit>              # Resets index and HEAD

# ❌ NEVER USE - Can create confusing history
git revert <commit>                     # Creates revert commit
git revert HEAD                         # Reverts last commit

# ❌ NEVER USE - Can lose current work context
git checkout <commit>                   # Checks out old commit (detached HEAD)
git checkout <branch>                   # Switches branches (can lose work)
```

### Dangerous Branch Operations
```bash
# ❌ NEVER USE - Can lose branch history
git branch -D <branch>                  # Force deletes branch
git branch --delete --force <branch>    # Force deletes branch

# ❌ NEVER USE - Can overwrite remote history
git push --force                        # Force pushes (overwrites remote)
git push -f                            # Force push shorthand
git push --force-with-lease            # "Safer" force push (still dangerous)
```

### Repository State Changes
```bash
# ❌ NEVER USE - Can lose stashed work
git stash drop                         # Permanently deletes stash
git stash clear                        # Deletes all stashes

# ❌ NEVER USE - Can lose untracked files
git clean -fd                          # Removes untracked files and directories
git clean -fx                          # Removes ignored and untracked files
```

## ⚠️ RATIONALE: Why These Operations Are Dangerous

### Real-World Scenarios

**Data Loss Incident Example:**
```bash
# User has been working for 3 hours on uncommitted changes
# AI assistant runs: git checkout HEAD -- src/honeyhive/tracer/otel_tracer.py
# Result: 3 hours of work permanently lost
```

**Common AI Assistant Mistakes:**
1. **Attempting to "fix" merge conflicts** by reverting files
2. **"Cleaning up" by resetting to previous commits**
3. **"Undoing changes" without understanding current work state**
4. **Switching branches** without checking for uncommitted work

### Impact Assessment
- **Lost Development Time**: Hours or days of work can be lost instantly
- **Broken Development Flow**: Interrupts user's mental model and progress
- **Trust Erosion**: Users lose confidence in AI assistant capabilities
- **Project Delays**: Recovery time impacts delivery schedules

## ✅ SAFE ALTERNATIVES: What AI Assistants Should Do Instead

### File-Level Corrections
```bash
# ✅ SAFE: Use file editing tools instead of git revert
# Instead of: git checkout HEAD -- file.py
# Use: search_replace, write, or MultiEdit tools

# Example: Fix a broken import
search_replace file.py "from wrong import" "from correct import"
```

### Code Quality Fixes
```bash
# ✅ SAFE: Fix issues with targeted edits
# Instead of: git reset --hard (to "fix" linting errors)
# Use: Targeted fixes with proper tools

# Example: Fix formatting issues
run_terminal_cmd "black src/honeyhive/tracer/otel_tracer.py"
```

### Conflict Resolution
```bash
# ✅ SAFE: Resolve conflicts with file editing
# Instead of: git checkout HEAD -- conflicted_file.py
# Use: Read the file, understand conflicts, make targeted edits

read_file conflicted_file.py
# Analyze conflicts and make surgical fixes
search_replace conflicted_file.py "<<<<<<< HEAD" ""
```

### State Verification
```bash
# ✅ SAFE: Always check state before making changes
git status --porcelain              # Check for uncommitted changes
git branch --show-current          # Verify current branch
git log --oneline -5               # Check recent commits
```

## 🛡️ Safety Protocols

### Pre-Operation Checks

**MANDATORY: Execute before any git operations**

```bash
# 1. Check for uncommitted work
UNCOMMITTED=$(git status --porcelain)
if [ -n "$UNCOMMITTED" ]; then
    echo "⚠️  WARNING: Uncommitted changes detected"
    echo "$UNCOMMITTED"
    # STOP: Do not proceed with destructive operations
fi

# 2. Verify current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# 3. Check for untracked files
UNTRACKED=$(git ls-files --others --exclude-standard)
if [ -n "$UNTRACKED" ]; then
    echo "⚠️  WARNING: Untracked files present"
    echo "$UNTRACKED"
fi
```

### Safe Git Operations

**AI assistants MAY use these git operations:**

```bash
# ✅ SAFE: Read-only operations
git status                          # Check repository status
git log --oneline                   # View commit history
git branch                          # List branches
git diff                           # Show changes
git show <commit>                  # Show commit details

# ✅ SAFE: Non-destructive operations
git add <file>                     # Stage changes
git commit -m "message"            # Commit staged changes
git push                           # Push commits (no force)

# ✅ SAFE: Information gathering
git remote -v                      # Show remotes
git config --list                  # Show configuration
git ls-files                       # List tracked files
```

## 🚨 Emergency Recovery Procedures

### If Destructive Operation Was Executed

**Immediate steps if AI assistant accidentally runs forbidden command:**

1. **STOP ALL OPERATIONS** immediately
2. **Do NOT make any more git commands**
3. **Check git reflog** for recovery options:
   ```bash
   git reflog --all
   ```
4. **Inform user immediately** with:
   - Exact command that was executed
   - Current repository state
   - Available recovery options from reflog
5. **Wait for user instructions** before proceeding

### Recovery Commands (User-Only)

**These commands should only be suggested to users, never executed by AI:**

```bash
# Potential recovery options (USER DECIDES)
git reflog                         # Find lost commits
git cherry-pick <commit>           # Recover specific commits
git branch recovery <commit>       # Create branch from lost commit
```

## 📋 Compliance Checklist

**Before any git operation, AI assistants must verify:**

- [ ] **Operation is not on forbidden list**
- [ ] **No uncommitted changes will be lost**
- [ ] **Current branch is correct**
- [ ] **User has not explicitly forbidden the operation**
- [ ] **Operation serves a clear, necessary purpose**
- [ ] **Safe alternatives have been considered**

## 🔍 Monitoring and Enforcement

### Automated Enforcement

**Pre-commit hooks prevent dangerous operations:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: prevent-destructive-git
        name: Prevent destructive git operations
        entry: scripts/check-git-safety.sh
        language: script
        pass_filenames: false
```

### Audit Trail

**All git operations should be logged:**
```bash
# Log all git commands for audit
export PROMPT_COMMAND='history -a'
export HISTTIMEFORMAT="%Y-%m-%d %H:%M:%S "
```

## 🆘 Escalation Guidelines

### When to Escalate to User

**Immediately escalate when:**
- **Merge conflicts** require resolution
- **Branch switching** is needed
- **History rewriting** is requested
- **Force operations** are suggested by tools
- **Any uncertainty** about git operation safety

### Escalation Message Template

```
🚨 GIT SAFETY ESCALATION

I need to perform a git operation that could affect your work:
- Operation: [specific git command]
- Purpose: [why this is needed]
- Risk: [potential data loss or changes]
- Alternatives: [safer options if available]

Please confirm if you want me to proceed or suggest an alternative approach.
```

## 📚 Related Standards

- **[Quality Framework](quality-framework.md)** - Overall AI assistant quality requirements
- **[Commit Protocols](commit-protocols.md)** - Safe commit and review procedures
- **[Git Workflow](../development/git-workflow.md)** - Standard git practices for the project

---

**📝 Remember**: When in doubt, use file editing tools instead of git operations. It's always safer to make targeted changes than to use git's destructive capabilities.
