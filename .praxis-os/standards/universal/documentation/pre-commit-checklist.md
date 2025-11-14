# Pre-Commit Checklist - prAxIs OS Development

**CRITICAL: Run this checklist before EVERY commit. No exceptions.**

**Date**: 2025-10-09  
**Status**: Active  
**Scope**: All prAxIs OS commits  
**Context**: Prevent incomplete work from entering the repository

---

## Questions This Answers

- **What must I check before every prAxIs OS commit?**
- **How do I verify all affected documentation is updated?**
- **What code quality checks should I run before committing?**
- **How do I ensure I haven't left debugging code in my commit?**
- **What's the systematic pre-commit workflow for prAxIs OS?**
- **How do I verify cross-references still work after changes?**
- **What should I check in git diff before committing?**
- **How do I ensure examples and tests match my code changes?**
- **What verification is needed for different change types?**
- **How long should the pre-commit checklist take?**

## Quick Reference: Pre-Commit Checklist

**Time Required:** 60 seconds (prevents hours of debugging)

**Core Principle:** A commit is a promise that everything works and is documented.

**Universal Checks (Every Commit):**
1. **Code Quality** (30s)
   - No `print()` statements (use logger)
   - No commented-out code
   - No `TODO` without issue link
   - No hardcoded secrets/paths
   - No unused imports

2. **Documentation Impact** (20s)
   - Affected docs updated?
   - Cross-references still valid?
   - Examples still work?
   - CHANGELOG updated?

3. **Git Hygiene** (10s)
   - Review git diff
   - Only changed files staged
   - No temp/debug files
   - Commit message clear

**Change-Specific Verification:**
- **Config changes** → Migration guide + validation tests
- **API changes** → Docstrings + integration tests
- **Workflow changes** → Task markdown + metadata.json

**Final Check:** "If someone reads ONLY the docs, will they understand this change?"

---

## 🎯 Core Principle

**"A commit is a promise that everything works and is documented. Keep your promises."**

This checklist is not bureaucracy - it's quality assurance. It takes 60 seconds and prevents hours of debugging.

---

## ✅ Universal Pre-Commit Checklist

### Phase 1: Code Quality (30 seconds)

```bash
# 1. Run linter (if applicable)
# For Python:
cd mcp_server && python -m flake8 . && cd ..

# 2. Check for obvious issues
# - No print() statements (use logger)
# - No commented-out code blocks
# - No TODO/FIXME without issue reference
# - No hardcoded paths or credentials

# 3. Verify imports
# - No unused imports
# - No circular dependencies
# - All imports at top of file
```

**Manual Checks**:
- [ ] No `print()` statements (use `logger` instead)
- [ ] No commented-out code
- [ ] No `TODO` without GitHub issue link
- [ ] No hardcoded secrets or credentials
- [ ] No absolute paths (use relative or config)

---

### Phase 2: Documentation Impact (20 seconds)

**Use the Impact Matrix**: `.praxis-os/standards/universal/documentation/change-impact-analysis.md`

Ask:
1. **What type of change is this?** (Installation, workflow, MCP tool, standards, etc.)
2. **Did I update ALL required docs?** (Check the matrix for your change type)
3. **Did I verify cross-references?** (Search for references to what you changed)

```bash
# Quick cross-reference check
grep -r "thing-i-changed" README.md docs/ universal/workflows/
```

**Mandatory Updates**:
- [ ] `mcp_server/CHANGELOG.md` - ALWAYS updated (with date: 2025-10-09)
- [ ] Related `docs/` files - If user-facing change
- [ ] Related workflow files - If workflow affected
- [ ] Line counts - If documented elsewhere

---

### Phase 3: Specific Verification (10 seconds)

#### If You Modified: Installation Files

```bash
# Verify file numbering is sequential
ls -1 installation/*.md

# Verify "next step" links are correct
grep -n "next step" installation/*.md

# Verify line counts in SYSTEM-SUMMARY
wc -l installation/*.md
grep "lines" installation/SYSTEM-SUMMARY.md
```

- [ ] File numbering sequential (00, 01, 02, ...)
- [ ] "Next step" links point to correct files
- [ ] Line counts in `SYSTEM-SUMMARY.md` accurate
- [ ] Updated `installation/README.md`

---

#### If You Modified: Workflow Files

```bash
# Verify task counts in phase.md
ls -1 universal/workflows/WORKFLOW/phases/N/task-*.md | wc -l
grep "tasks" universal/workflows/WORKFLOW/phases/N/phase.md

# Verify total time in README
grep "minutes" universal/workflows/WORKFLOW/README.md
```

- [ ] Task count in `phase.md` matches actual file count
- [ ] Task numbering sequential (task-1, task-2, ...)
- [ ] Estimated time updated in `phase.md`
- [ ] Total time updated in workflow `README.md`
- [ ] Workflow `README.md` phase summary updated

---

#### If You Modified: MCP Tools

```bash
# Count total registered tools
grep -r "@server.tool()" mcp_server/server/tools/ | wc -l

# Verify docs updated
grep "tool-name" docs/content/mcp-tools.md
```

- [ ] Tool count < 20 (performance threshold)
- [ ] Tool documented in `docs/content/mcp-tools.md` with:
  - [ ] Parameters (with types and descriptions)
  - [ ] Returns (with example JSON)
  - [ ] Usage example
  - [ ] Error handling
- [ ] Tool has Sphinx-style docstring
- [ ] `mcp_server/CHANGELOG.md` updated

---

#### If You Modified: Standards

```bash
# Verify standard is discoverable
find universal/standards -name "standard-name.md"

# Check if workflows reference it
grep -r "standard-name" universal/workflows/
```

- [ ] Standard in correct category directory
- [ ] Standard listed in `docs/content/standards.md`
- [ ] Related workflows updated if standard changed
- [ ] `.cursorrules` updated if behavioral trigger needed

---

#### If You Modified: .gitignore Requirements

```bash
# Verify both flows reference canonical source
grep "gitignore-requirements.md" installation/04-gitignore.md
grep "gitignore-requirements.md" universal/workflows/praxis_os_upgrade_v1/phases/2/task-3-update-gitignore.md
```

- [ ] `universal/standards/installation/gitignore-requirements.md` updated
- [ ] Installation step reads from canonical source
- [ ] Upgrade workflow task reads from canonical source
- [ ] Repository `.gitignore` updated if needed

---

#### If You Modified: Configuration

```bash
# Verify config schema is documented
python -c "from mcp_server.models.config import ServerConfig; help(ServerConfig)"
```

- [ ] `models/config.py` dataclass has docstrings
- [ ] Default values clearly documented
- [ ] Configuration docs updated (if exists)
- [ ] Installation steps updated if config affects setup

---

### Phase 4: Testing (varies)

**Code changes require tests** (see `production-code-checklist.md`):
- [ ] Unit tests for happy path
- [ ] Unit tests for failure modes
- [ ] Integration tests if touching external systems
- [ ] Concurrency tests if touching shared state

**Run tests**:
```bash
# Full test suite
pytest tests/

# Or specific test
pytest tests/unit/test_your_change.py -v
```

**Documentation changes require verification**:
- [ ] All links work (no 404s)
- [ ] All code examples are valid
- [ ] All line counts are accurate
- [ ] All cross-references are correct

---

### Phase 5: Git Hygiene (10 seconds)

```bash
# Review what you're committing
git diff --staged

# Verify no unintended changes
git status
```

**Check**:
- [ ] Only intended files staged
- [ ] No debug code committed
- [ ] No temporary files committed (.swp, .tmp, etc.)
- [ ] No large binaries committed (check `.gitignore`)
- [ ] No secrets in diff (API keys, passwords)

---

## 📝 Commit Message Format

**Required format**:
```
type(scope): brief description (50 chars max)

Detailed explanation of what changed and why (72 chars per line).

Documentation Updates:
- Updated: [list of docs updated]
- Verified: [what was verified]

Closes #123 (if applicable)
```

**Type**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code refactoring
- `test`: Adding/modifying tests
- `chore`: Maintenance (deps, config)

**Scope**:
- `installation`: Installation process
- `workflow`: Workflow changes
- `mcp`: MCP server/tools
- `standards`: Standards/docs
- `config`: Configuration

**Example**:
```
feat(installation): add gitignore management step

Added installation/04-gitignore.md to dynamically read and apply
.gitignore requirements from canonical source in standards. This
ensures ephemeral files (cache, backups, venv) are never committed.

Documentation Updates:
- Updated: installation/README.md, SYSTEM-SUMMARY.md, docs/content/installation.md
- Verified: Line counts, file numbering, cross-references
- Renumbered: 04-venv-mcp.md -> 05-venv-mcp.md, 05-validate.md -> 06-validate.md

Closes #42
```

---

## 🚨 Blockers (DO NOT COMMIT if any fail)

### Blocker 1: CHANGELOG Missing
❌ `mcp_server/CHANGELOG.md` not updated
✅ Every commit updates CHANGELOG with date and description

### Blocker 2: Broken References
❌ Links to files that don't exist
❌ References to line numbers that are wrong
✅ All references verified with `grep` or manual check

### Blocker 3: Incomplete Documentation
❌ New feature with no docs
❌ Modified process with no doc update
✅ All user-facing changes documented in `docs/`

### Blocker 4: Tests Failing
❌ `pytest` exits with errors
✅ All tests pass before commit

### Blocker 5: Out-of-Sync Line Counts
❌ Documented line count doesn't match actual
✅ Run `wc -l` and verify against docs

---

## ⚡ Quick Commit Checklist (60-Second Version)

```bash
# 1. Code quality (10s)
# - No print statements, commented code, hardcoded paths

# 2. Documentation impact (20s)
# - Check change-impact-analysis.md for required updates
# - Verify CHANGELOG.md updated with today's date (2025-10-09)

# 3. Specific verification (10s)
# - If installation: check numbering and line counts
# - If workflow: check task counts and times
# - If MCP tool: check tool count and docs
# - If standards: check discoverability

# 4. Testing (varies)
pytest tests/  # Or verify docs manually

# 5. Git hygiene (10s)
git diff --staged  # Review changes
git status  # Verify only intended files

# 6. Commit message
# - Format: type(scope): description
# - Include: Documentation Updates section
```

**The 10-Second Question**:
> "If another developer (or AI) pulls this commit, will they have everything they need to understand what changed and why?"

If **NO** → Don't commit yet.

---

## 🔄 Post-Commit Verification (Optional but Recommended)

After committing, verify:

```bash
# 1. Commit message is clear
git log -1

# 2. All docs still build (if Docusaurus)
cd docs && npm run build && cd ..

# 3. Tests still pass
pytest tests/

# 4. No untracked files that should be committed
git status
```

---

## 📚 Related Standards

- `documentation/change-impact-analysis.md` - What docs to update for each change type
- `ai-safety/production-code-checklist.md` - Code quality requirements
- `testing/test-pyramid.md` - Testing standards

---

## 💡 Tips for Efficiency

### Tip 1: Use Git Hooks
Create `.git/hooks/pre-commit` to automate checks:
```bash
#!/bin/bash
# Check if CHANGELOG updated
if ! git diff --cached --name-only | grep -q "CHANGELOG.md"; then
    echo "❌ CHANGELOG.md not updated!"
    exit 1
fi
```

### Tip 2: Create Aliases
```bash
alias pre-commit-check='pytest tests/ && wc -l installation/*.md'
```

### Tip 3: Use a Checklist Template
Keep a `PRE_COMMIT_TEMPLATE.md` in your workspace for quick reference.

---

## 🚫 Anti-Patterns

### Anti-Pattern 1: "It's Just a Quick Fix"
❌ Skipping checklist for "small" changes
✅ Every commit gets the checklist

### Anti-Pattern 2: "I'll Fix Docs in Next Commit"
❌ Committing code without docs
✅ Code and docs in same commit

### Anti-Pattern 3: "Tests Pass on My Machine"
❌ Not running full test suite
✅ Run `pytest tests/` before every commit

### Anti-Pattern 4: "Commit Message: 'Updates'"
❌ Vague commit messages
✅ Descriptive messages with "what" and "why"

---

## 🎯 The Contract

**When you commit, you promise:**
1. ✅ Code works (tests pass)
2. ✅ Documentation is complete and accurate
3. ✅ No breaking changes without warnings
4. ✅ CHANGELOG reflects what changed
5. ✅ Cross-references are valid
6. ✅ Future you (and others) can understand this commit

**Honor the contract. Use the checklist. Every time.**

---

**Remember: A commit is permanent. Rushing commits creates permanent technical debt. The 60 seconds you spend on this checklist saves hours of debugging and confusion later.**

