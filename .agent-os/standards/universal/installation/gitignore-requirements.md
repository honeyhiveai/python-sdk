# Agent OS .gitignore Requirements

**Purpose**: Canonical list of required .gitignore entries for Agent OS installations

---

## 🎯 TL;DR - .gitignore Requirements Quick Reference

**Keywords for search**: gitignore requirements, Agent OS gitignore, what to ignore, .gitignore patterns, ephemeral content, do not commit, version control, .agent-os cache, vector index

**Core Principle:** Ignore ephemeral, machine-specific content. Commit everything else.

**MANDATORY .gitignore Entries:**
```gitignore
# Agent OS - Ephemeral content (do not commit)
.agent-os/.cache/          # ~1.3GB - Vector index
.agent-os/venv/            # ~100MB - Python virtual environment
.agent-os/mcp_server/__pycache__/  # ~5MB - Python bytecode
.agent-os/scripts/__pycache__/     # ~1MB - Python bytecode
.agent-os.backup.*         # ~1.3GB - Upgrade backups
.agent-os/.upgrade_lock    # <1KB - Upgrade lock file
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
✅ .agent-os/standards/    - Standards and fundamentals
✅ .agent-os/usage/        - Documentation
✅ .agent-os/workflows/    - Workflow definitions
✅ .agent-os/specs/        - Project specifications (CRITICAL!)
✅ .agent-os/mcp_server/   - MCP server code (if customized)
✅ .cursor/mcp.json        - Cursor MCP config
✅ .cursorrules            - AI behavioral triggers
```

**Verification:**
```bash
# Check what would be committed
git status --porcelain | grep ".agent-os/.cache"  # Should be empty
git status --porcelain | grep ".agent-os/venv"    # Should be empty

# If files appear, add to .gitignore and untrack
git rm --cached -r .agent-os/.cache/
```

**Installation Validation:**
- Run `git status` after Agent OS install
- Should NOT see `.agent-os/.cache/` or `.agent-os/venv/`
- If you do → .gitignore entries missing or incorrect

---

## ❓ Questions This Answers

1. "What should I add to .gitignore for Agent OS?"
2. "Why is my repo so large after Agent OS install?"
3. "What Agent OS files should be committed?"
4. "How to ignore .agent-os cache?"
5. "What are required gitignore entries?"
6. "Why ignore .agent-os/venv/?"
7. "Should I commit .agent-os/specs/?"
8. "How to verify gitignore is working?"
9. "What is the .agent-os/.cache/ directory?"
10. "How to fix accidentally committed cache?"

---

## Required Entries

All Agent OS installations MUST include these entries in the project's `.gitignore`:

```gitignore
# Agent OS - Ephemeral content (do not commit)
.agent-os/.cache/
.agent-os/venv/
.agent-os/mcp_server/__pycache__/
.agent-os/scripts/__pycache__/
.agent-os.backup.*
.agent-os/.upgrade_lock
```

---

## Why Is Each .gitignore Entry Required?

Understanding the purpose and impact of each pattern.

| Pattern | Size | Reason | Impact if Committed |
|---------|------|--------|---------------------|
| `.agent-os/.cache/` | ~1.3GB | Vector index, regenerated on each machine | Massive repo bloat, conflicts across machines |
| `.agent-os/venv/` | ~100MB | Python virtual environment | Platform-specific, breaks across OS/Python versions |
| `.agent-os/mcp_server/__pycache__/` | ~5MB | Python bytecode | Platform/Python version specific |
| `.agent-os/scripts/__pycache__/` | ~1MB | Python bytecode | Platform/Python version specific |
| `.agent-os.backup.*` | ~1.3GB | Upgrade backups (temporary) | Massive repo bloat, only needed locally for rollback |
| `.agent-os/.upgrade_lock` | <1KB | Upgrade lock file (temporary) | Meaningless outside upgrade process |

**Total potential bloat**: ~2.7GB of ephemeral files

---

## What Agent OS Files SHOULD Be Committed?

Content that should be tracked in version control for team collaboration.

Agent OS content that should be tracked in version control:

| Directory | Purpose | Commit? |
|-----------|---------|---------|
| `.agent-os/standards/` | Universal CS fundamentals + project standards | ✅ YES |
| `.agent-os/usage/` | Documentation + custom docs | ✅ YES |
| `.agent-os/workflows/` | Workflow definitions | ✅ YES |
| `.agent-os/specs/` | Project specifications | ✅ YES (critical!) |
| `.agent-os/mcp_server/` | MCP server code | ✅ YES (if customized) |
| `.cursor/mcp.json` | Cursor MCP configuration | ✅ YES |
| `.cursorrules` | AI assistant behavioral triggers | ✅ YES |

---

## What Is the Correct .gitignore Format?

Standard format for adding Agent OS entries to .gitignore.

The entries should be added as a single section:

```gitignore
# Agent OS - Ephemeral content (do not commit)
.agent-os/.cache/
.agent-os/venv/
.agent-os/mcp_server/__pycache__/
.agent-os/scripts/__pycache__/
.agent-os.backup.*
.agent-os/.upgrade_lock
```

**Rules**:
- Section header: `# Agent OS - Ephemeral content (do not commit)`
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
git check-ignore .agent-os/.cache/test         # Should exit 0
git check-ignore .agent-os.backup.20251008     # Should exit 0
git check-ignore .agent-os/.upgrade_lock       # Should exit 0

# Check if any ephemeral files are already committed
git ls-files .agent-os/.cache/ .agent-os/venv/ .agent-os.backup.*
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

**Previous Issue**: `.agent-os.backup.*` was not in original .gitignore, discovered during upgrade workflow testing when 665 backup files (117K insertions) were staged for commit.

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
standards_path = ".agent-os/standards/universal/installation/gitignore-requirements.md"
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
| **Agent OS installation** | `search_standards("gitignore requirements")` |
| **Large repo after install** | `search_standards("why is repo large after Agent OS")` |
| **What to commit** | `search_standards("what Agent OS files to commit")` |
| **Cache in git status** | `search_standards("ignore agent-os cache")` |
| **Setup .gitignore** | `search_standards("Agent OS gitignore")` |
| **Accidentally committed cache** | `search_standards("remove agent-os cache from git")` |
| **Writing workflows** | `search_standards("gitignore for workflows")` |

---

## 🔗 Related Standards

**Query workflow for .gitignore setup:**

1. **Start with requirements** → `search_standards("gitignore requirements")` (this document)
2. **Learn update procedures** → `search_standards("Agent OS update")` → `standards/installation/update-procedures.md`
3. **Understand git safety** → `search_standards("git safety rules")` → `standards/ai-safety/git-safety-rules.md`

**By Category:**

**Installation:**
- `standards/installation/update-procedures.md` - Update process → `search_standards("Agent OS update")`

**AI Safety:**
- `standards/ai-safety/git-safety-rules.md` - Git operations → `search_standards("git safety rules")`
- `standards/ai-safety/credential-file-protection.md` - File protection → `search_standards("credential file protection")`

**Workflows:**
- `workflows/agent_os_upgrade_v1/` - Automated upgrade → `search_standards("upgrade workflow")`

---

**Last Updated**: October 8, 2025  
**Canonical Source**: `universal/standards/installation/gitignore-requirements.md`

