# prAxIs OS .gitignore Requirements

**Purpose**: Canonical list of required .gitignore entries for prAxIs OS installations

---

## 🎯 TL;DR - .gitignore Requirements Quick Reference

**Keywords for search**: gitignore requirements, prAxIs OS gitignore, what to ignore, .gitignore patterns, ephemeral content, do not commit, version control, .praxis-os cache, vector index

**Core Principle:** Ignore ephemeral, machine-specific content. Commit everything else.

**MANDATORY .gitignore Entries:**
```gitignore
# prAxIs OS - Ephemeral content (do not commit)
.praxis-os/.cache/          # ~1.3GB - Vector index
.praxis-os/venv/            # ~100MB - Python virtual environment
.praxis-os/mcp_server/__pycache__/  # ~5MB - Python bytecode
.praxis-os/scripts/__pycache__/     # ~1MB - Python bytecode
.praxis-os.backup.*         # ~1.3GB - Upgrade backups
.praxis-os/.upgrade_lock    # <1KB - Upgrade lock file
.praxis-os/workspace/       # Temporary design docs, analysis, experiments
```

**Why These Are Required:**
- **Total bloat prevented**: ~2.7GB of ephemeral files
- `.cache/` - Regenerated on each machine (vector index)
- `venv/` - Platform-specific, breaks across OS/Python versions
- `__pycache__/` - Python version specific bytecode
- `.backup.*` - Temporary upgrade backups (local rollback only)
- `.upgrade_lock` - Meaningless outside upgrade process

**What TO Commit:**
```
✅ .praxis-os/standards/    - Standards and fundamentals
✅ .praxis-os/usage/        - Documentation
✅ .praxis-os/workflows/    - Workflow definitions
✅ .praxis-os/specs/        - Project specifications (CRITICAL!)
✅ .praxis-os/mcp_server/   - MCP server code (if customized)
✅ .cursor/mcp.json        - Cursor MCP config
✅ .cursorrules            - AI behavioral triggers
```

**Verification:**
```bash
# Check what would be committed
git status --porcelain | grep ".praxis-os/.cache"  # Should be empty
git status --porcelain | grep ".praxis-os/venv"    # Should be empty

# If files appear, add to .gitignore and untrack
git rm --cached -r .praxis-os/.cache/
```

**Installation Validation:**
- Run `git status` after prAxIs OS install
- Should NOT see `.praxis-os/.cache/` or `.praxis-os/venv/`
- If you do → .gitignore entries missing or incorrect

---

## ❓ Questions This Answers

1. "What should I add to .gitignore for prAxIs OS?"
2. "Why is my repo so large after prAxIs OS install?"
3. "What prAxIs OS files should be committed?"
4. "How to ignore .praxis-os cache?"
5. "What are required gitignore entries?"
6. "Why ignore .praxis-os/venv/?"
7. "Should I commit .praxis-os/specs/?"
8. "How to verify gitignore is working?"
9. "What is the .praxis-os/.cache/ directory?"
10. "How to fix accidentally committed cache?"

---

## Required Entries

All prAxIs OS installations MUST include these entries in the project's `.gitignore`:

```gitignore
# prAxIs OS - Ephemeral content (do not commit)
.praxis-os/.cache/
.praxis-os/venv/
.praxis-os/mcp_server/__pycache__/
.praxis-os/scripts/__pycache__/
.praxis-os.backup.*
.praxis-os/.upgrade_lock
```

---

## Why Is Each .gitignore Entry Required?

Understanding the purpose and impact of each pattern.

| Pattern | Size | Reason | Impact if Committed |
|---------|------|--------|---------------------|
| `.praxis-os/.cache/` | ~1.3GB | Vector index, regenerated on each machine | Massive repo bloat, conflicts across machines |
| `.praxis-os/venv/` | ~100MB | Python virtual environment | Platform-specific, breaks across OS/Python versions |
| `.praxis-os/mcp_server/__pycache__/` | ~5MB | Python bytecode | Platform/Python version specific |
| `.praxis-os/scripts/__pycache__/` | ~1MB | Python bytecode | Platform/Python version specific |
| `.praxis-os.backup.*` | ~1.3GB | Upgrade backups (temporary) | Massive repo bloat, only needed locally for rollback |
| `.praxis-os/.upgrade_lock` | <1KB | Upgrade lock file (temporary) | Meaningless outside upgrade process |
| `.praxis-os/workspace/` | Varies | Temporary design docs, analysis, experiments (Phase 1 artifacts) | Mixes ephemeral with permanent content, confuses specs with drafts |

**Total potential bloat**: ~2.7GB of ephemeral files

---

## What prAxIs OS Files SHOULD Be Committed?

Content that should be tracked in version control for team collaboration.

prAxIs OS content that should be tracked in version control:

| Directory | Purpose | Commit? |
|-----------|---------|---------|
| `.praxis-os/standards/` | Universal CS fundamentals + project standards | ✅ YES |
| `.praxis-os/usage/` | Documentation + custom docs | ✅ YES |
| `.praxis-os/workflows/` | Workflow definitions | ✅ YES |
| `.praxis-os/specs/` | Project specifications | ✅ YES (critical!) |
| `.praxis-os/mcp_server/` | MCP server code | ✅ YES (if customized) |
| `.cursor/mcp.json` | Cursor MCP configuration | ✅ YES |
| `.cursorrules` | AI assistant behavioral triggers | ✅ YES |

---

## What Is the Correct .gitignore Format?

Standard format for adding prAxIs OS entries to .gitignore.

The entries should be added as a single section:

```gitignore
# prAxIs OS - Ephemeral content (do not commit)
.praxis-os/.cache/
.praxis-os/venv/
.praxis-os/mcp_server/__pycache__/
.praxis-os/scripts/__pycache__/
.praxis-os.backup.*
.praxis-os/.upgrade_lock
```

**Rules**:
- Section header: `# prAxIs OS - Ephemeral content (do not commit)`
- One pattern per line
- Blank line before and after section (for readability)
- Append to existing `.gitignore` if present
- Create new `.gitignore` if missing

---

## How to Verify .gitignore Is Working?

Validation steps to ensure ephemeral files are properly ignored.

To verify entries are working:

```bash
# Check if patterns are ignored
git check-ignore .praxis-os/.cache/test         # Should exit 0
git check-ignore .praxis-os.backup.20251008     # Should exit 0
git check-ignore .praxis-os/.upgrade_lock       # Should exit 0

# Check if any ephemeral files are already committed
git ls-files .praxis-os/.cache/ .praxis-os/venv/ .praxis-os.backup.*
# Should return nothing
```

---

## Why Do These Requirements Exist? (Historical Context)

Understanding the reasoning behind .gitignore requirements.

**Added**: October 8, 2025  
**Rationale**: Users were committing 1.3GB+ vector indexes and upgrade backups, causing:
- GitHub rejecting pushes (file size limits)
- Repo clones taking 10+ minutes
- Merge conflicts on binary cache files
- Wasted CI/CD bandwidth

**Previous Issue**: `.praxis-os.backup.*` was not in original .gitignore, discovered during upgrade workflow testing when 665 backup files (117K insertions) were staged for commit.

---

## How Should Workflow Authors Handle .gitignore?

Guidance for workflow creators managing generated files.

### Installation Workflows

When writing installation guides, reference this file:

```python
# Read canonical requirements
with open(f"{AGENT_OS_SOURCE}/universal/standards/installation/gitignore-requirements.md") as f:
    content = f.read()
    # Extract code block with required entries
```

### Upgrade Workflows

When updating existing installations:

```python
# Read from standards, not hardcoded list
standards_path = ".praxis-os/standards/universal/installation/gitignore-requirements.md"
with open(standards_path) as f:
    content = f.read()
    # Extract and compare with target .gitignore
```

---

## How to Maintain .gitignore Requirements?

Guidelines for updating .gitignore entries over time.

To add a new required entry:

1. Add pattern to this file's "Required Entries" section
2. Update the table explaining why it's required
3. Installation and upgrade workflows will automatically pick it up

**Do NOT**:
- Hardcode lists in workflow task files
- Duplicate this list elsewhere
- Add entries without documenting the reason

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **prAxIs OS installation** | `pos_search_project(content_type="standards", query="gitignore requirements")` |
| **Large repo after install** | `pos_search_project(content_type="standards", query="why is repo large after prAxIs OS")` |
| **What to commit** | `pos_search_project(content_type="standards", query="what prAxIs OS files to commit")` |
| **Cache in git status** | `pos_search_project(content_type="standards", query="ignore agent-os cache")` |
| **Setup .gitignore** | `pos_search_project(content_type="standards", query="prAxIs OS gitignore")` |
| **Accidentally committed cache** | `pos_search_project(content_type="standards", query="remove agent-os cache from git")` |
| **Writing workflows** | `pos_search_project(content_type="standards", query="gitignore for workflows")` |

---

## 🔗 Related Standards

**Query workflow for .gitignore setup:**

1. **Start with requirements** → `pos_search_project(content_type="standards", query="gitignore requirements")` (this document)
2. **Learn update procedures** → `pos_search_project(content_type="standards", query="prAxIs OS update")` → `standards/installation/update-procedures.md`
3. **Understand git safety** → `pos_search_project(content_type="standards", query="git safety rules")` → `standards/ai-safety/git-safety-rules.md`

**By Category:**

**Installation:**
- `standards/installation/update-procedures.md` - Update process → `pos_search_project(content_type="standards", query="prAxIs OS update")`

**AI Safety:**
- `standards/ai-safety/git-safety-rules.md` - Git operations → `pos_search_project(content_type="standards", query="git safety rules")`
- `standards/ai-safety/credential-file-protection.md` - File protection → `pos_search_project(content_type="standards", query="credential file protection")`

**Workflows:**
- `workflows/praxis_os_upgrade_v1/` - Automated upgrade → `pos_search_project(content_type="standards", query="upgrade workflow")`

---

**Last Updated**: October 8, 2025  
**Canonical Source**: `universal/standards/installation/gitignore-requirements.md`
