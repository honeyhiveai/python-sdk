# Change Impact Analysis - Documentation Updates

**CRITICAL: When you change ANY component, you MUST update ALL affected documentation.**

**Date**: 2025-10-09  
**Status**: Active  
**Scope**: prAxIs OS development and maintenance  
**Context**: AI agents must be thorough - this checklist ensures nothing is missed

---

## Questions This Answers

- **What documentation must I update when changing installation files?**
- **How do I identify all affected docs when modifying a workflow?**
- **What's the systematic process for analyzing change impact?**
- **Which files need updates when I add a new MCP tool?**
- **How do I verify all documentation updates are complete?**
- **What should I check before committing changes to standards?**
- **How do I update SYSTEM-SUMMARY.md after structural changes?**
- **What documentation ripple effects come from config changes?**
- **How do I ensure CHANGELOG.md captures all changes?**
- **What's the verification checklist for documentation completeness?**

## Quick Reference: Change Impact Analysis

**Core Principle:** Every change has documentation ripple effects → Map them → Update them → Verify them

**Common Change Types & Required Updates:**

1. **Installation Changes** → Update: `installation/README.md`, `SYSTEM-SUMMARY.md`, root `README.md`, `docs/content/installation.md`, `CHANGELOG.md`

2. **Workflow Changes** → Update: Task markdown, `metadata.json`, workflow README, standards docs, usage guides

3. **MCP Tool Changes** → Update: Tool docstrings, MCP tool list docs, usage examples, integration tests

4. **Standards Changes** → Update: Standard content, cross-references, related standards, usage examples

5. **Config Changes** → Update: Config schema, defaults documentation, migration guide, validation tests

**Verification Steps:**
1. Check line counts match documentation
2. Verify all referenced files exist
3. Test examples still work
4. Confirm CHANGELOG is updated
5. Review cross-references

**Time Investment:** 60 seconds prevents hours of confusion!

---

## 🎯 Core Principle

**"Every change has documentation ripple effects. Map them. Update them. Verify them."**

Missing one doc update creates confusion, wastes time, and undermines trust. This standard makes thoroughness systematic, not aspirational.

---

## 📊 Change Type → Documentation Impact Matrix

### 1. Installation Process Changes

**Trigger**: Modified any file in `installation/` directory

**Required Updates**:
- [ ] `installation/README.md` - Update file list, step count
- [ ] `installation/SYSTEM-SUMMARY.md` - Update architecture, file counts, line counts
- [ ] `README.md` (root) - Update installation guidance if entry point changed
- [ ] `docs/content/installation.md` - Update Docusaurus installation guide
- [ ] `mcp_server/CHANGELOG.md` - Document what changed and why

**Verification**:
```bash
# Check line counts are accurate
wc -l installation/*.md
# Verify all files referenced exist
grep -r "installation/" README.md docs/content/installation.md
```

**Example**:
- Added `04-gitignore.md` → Must renumber subsequent steps, update README, update SYSTEM-SUMMARY with new step, update docs/

---

### 2. Workflow Changes

**Trigger**: Modified any file in `universal/workflows/` or `.praxis-os/workflows/`

#### 2a. Added/Modified Workflow Task

**Required Updates**:
- [ ] `phases/N/phase.md` - Update task count, estimated time
- [ ] Workflow `README.md` - Update phase summary, total time
- [ ] `docs/content/workflows.md` - Update workflow catalog if new workflow
- [ ] `mcp_server/CHANGELOG.md` - Document change

**Verification**:
```bash
# Count tasks in phase
ls -1 universal/workflows/workflow_name/phases/N/task-*.md | wc -l
# Verify phase.md task count matches
grep "tasks" universal/workflows/workflow_name/phases/N/phase.md
```

#### 2b. Modified Workflow Metadata

**Required Updates**:
- [ ] Workflow `metadata.json` - Update version
- [ ] Workflow `README.md` - Update version, change summary
- [ ] `docs/content/workflows.md` - Update version reference
- [ ] `mcp_server/CHANGELOG.md` - Document change

---

### 3. MCP Tool Changes

**Trigger**: Added/modified tool in `mcp_server/server/tools/`

**Required Updates**:
- [ ] `docs/content/mcp-tools.md` - Add/update tool documentation with examples
- [ ] `universal/usage/mcp-usage-guide.md` - Add usage guidance if complex tool
- [ ] `mcp_server/CHANGELOG.md` - Document new/changed tool
- [ ] Tool count check - If adding tool, verify total count < 20 (performance threshold)

**Verification**:
```bash
# Count registered tools
grep -r "@server.tool()" mcp_server/server/tools/ | wc -l
# Verify docs match
grep "^### " docs/content/mcp-tools.md | wc -l
```

**Example**:
- Added `validate_workflow` tool → Must document in `mcp-tools.md` with parameters, returns, examples

---

### 4. Standards Changes

**Trigger**: Added/modified file in `universal/standards/`

**Required Updates**:
- [ ] `docs/content/standards.md` - Update standards catalog
- [ ] `.cursorrules` - Update if behavioral trigger needed
- [ ] Related workflow tasks - Update references if standard changed
- [ ] `mcp_server/CHANGELOG.md` - Document new/changed standard

**Verification**:
```bash
# List all standards
find universal/standards -name "*.md" -type f
# Verify docs reference exists
grep "standard-name" docs/content/standards.md
```

---

### 5. Configuration Changes

**Trigger**: Modified `config.json` schema, `models/config.py`, or default values

**Required Updates**:
- [ ] `docs/content/configuration.md` - Document new options (if file exists)
- [ ] `universal/usage/mcp-usage-guide.md` - Update configuration section
- [ ] `installation/` steps - Update if affects installation
- [ ] `mcp_server/CHANGELOG.md` - Document configuration change
- [ ] Inline docstrings - Update dataclass docstrings

**Verification**:
```bash
# Verify all config fields documented
python -c "from mcp_server.models.config import ServerConfig; import inspect; print(inspect.signature(ServerConfig))"
```

---

### 6. Dependency Changes

**Trigger**: Modified `mcp_server/requirements.txt`

**Required Updates**:
- [ ] `mcp_server/CHANGELOG.md` - Document why version changed
- [ ] `installation/05-venv-mcp.md` - Update if installation process affected
- [ ] `docs/content/installation.md` - Update requirements if user-facing
- [ ] Add comment in `requirements.txt` explaining version choice

**Verification**:
```bash
# Verify all deps have version justification
grep "~=" mcp_server/requirements.txt
# Each should have a comment above it
```

---

### 7. .gitignore Changes

**Trigger**: Modified `universal/standards/installation/gitignore-requirements.md`

**Required Updates**:
- [ ] `installation/04-gitignore.md` - Verify reads from canonical source
- [ ] `universal/workflows/praxis_os_upgrade_v1/phases/2/task-3-update-gitignore.md` - Verify reads from canonical source
- [ ] Root `.gitignore` - Update repo's own gitignore if needed
- [ ] `mcp_server/CHANGELOG.md` - Document what patterns changed

**Verification**:
```bash
# Verify both installation and upgrade reference the standard
grep "gitignore-requirements.md" installation/04-gitignore.md
grep "gitignore-requirements.md" universal/workflows/praxis_os_upgrade_v1/phases/2/task-3-update-gitignore.md
```

---

### 8. Architecture Changes

**Trigger**: Modified directory structure, file organization, or system design

**Required Updates**:
- [ ] `README.md` (root) - Update "Repository Structure"
- [ ] `docs/content/architecture.md` - Update architecture documentation
- [ ] `installation/00-START.md` - Update "Architecture Context"
- [ ] `installation/SYSTEM-SUMMARY.md` - Update "Directory Structure"
- [ ] `mcp_server/CHANGELOG.md` - Document architectural change

**Verification**:
```bash
# Generate actual directory tree
tree -L 2 -I '__pycache__|node_modules|venv|.cache'
# Compare with documented structure
```

---

### 9. Line Count Changes

**Trigger**: Modified any file that has its line count documented elsewhere

**Required Updates**:
- [ ] `README.md` - Update `.cursorrules` line count (if changed)
- [ ] `installation/README.md` - Update file line counts
- [ ] `installation/SYSTEM-SUMMARY.md` - Update file line counts
- [ ] Workflow `README.md` - Update task line counts if documented

**Verification**:
```bash
# Verify actual line count matches documented count
wc -l .cursorrules
grep "cursorrules" README.md
```

---

## 🔍 Pre-Change Checklist

Before making ANY change, ask:

1. **What am I changing?** (Code, workflow, installation, standards, docs)
2. **What type of change is it?** (See matrix above)
3. **What docs reference this?** (Search: `grep -r "component-name" docs/ README.md`)
4. **What depends on this?** (Other workflows, tools, installation steps)
5. **What examples use this?** (Code samples, quick starts)

---

## 🚨 High-Risk Changes (Extra Scrutiny)

### Changes to Installation Flow
- **Why risky**: Affects all new users, bootstrapping problem
- **Extra checks**: Test in clean environment, verify all cross-references

### Changes to Upgrade Workflow
- **Why risky**: Affects existing users, data integrity critical
- **Extra checks**: Test with actual `.praxis-os/` directory, verify rollback works

### Changes to MCP Tools
- **Why risky**: Breaking changes affect all AI agents using tools
- **Extra checks**: Backward compatibility, deprecation notices

### Changes to .cursorrules
- **Why risky**: Affects AI agent behavior globally
- **Extra checks**: Test with actual Cursor session, verify no regressions

---

## 🎯 The 10-Second Rule

Before ANY commit, spend 10 seconds asking:

1. **"Did I update the CHANGELOG?"**
2. **"Did I update docs/ if user-facing?"**
3. **"Did I update related workflows?"**
4. **"Did I verify line counts?"**
5. **"Did I check cross-references?"**

If any answer is "I'm not sure", **STOP and use this checklist.**

---

## 📚 Related Standards

- `documentation/pre-commit-checklist.md` - Systematic verification before commits
- `ai-safety/production-code-checklist.md` - Code quality requirements
- `documentation/readme-templates.md` - README structure

---

## 💡 Examples

### Example 1: Adding Installation Step

**Change**: Created `installation/04-gitignore.md`

**Impact Analysis**:
1. Installation process change → Type 1
2. Check matrix:
   - ✅ Updated `installation/README.md` (file list, step count)
   - ✅ Updated `installation/SYSTEM-SUMMARY.md` (7 steps, new file line count)
   - ✅ Updated `docs/content/installation.md` (mentioned in flow)
   - ✅ Updated `mcp_server/CHANGELOG.md`
   - ✅ Renumbered `04-venv-mcp.md` → `05-venv-mcp.md`
   - ✅ Updated `05-validate.md` → `06-validate.md`
   - ✅ Updated all "Next step" links

**Verification**:
```bash
ls -1 installation/*.md  # Verify numbering
grep "next step" installation/*.md  # Verify links
wc -l installation/*.md  # Verify SYSTEM-SUMMARY line counts
```

---

### Example 2: Adding MCP Tool

**Change**: Implemented `validate_workflow` tool

**Impact Analysis**:
1. MCP tool change → Type 3
2. Check matrix:
   - ✅ Updated `docs/content/mcp-tools.md` (added tool section with examples)
   - ✅ Updated `mcp_server/CHANGELOG.md`
   - ✅ Verified tool count < 20 (now at 12 tools)
   - ✅ Added docstring to tool function

**Verification**:
```bash
grep -A 20 "validate_workflow" docs/content/mcp-tools.md
grep "validate_workflow" mcp_server/CHANGELOG.md
```

---

### Example 3: Modifying Workflow Phase

**Change**: Added task to `praxis_os_upgrade_v1` Phase 2

**Impact Analysis**:
1. Workflow change → Type 2a
2. Check matrix:
   - ✅ Updated `phases/2/phase.md` (4 tasks now, time: 60s)
   - ✅ Updated workflow `README.md` (Phase 2: 4 tasks, updated total time)
   - ✅ Updated `mcp_server/CHANGELOG.md`
   - ✅ Renumbered subsequent tasks

**Verification**:
```bash
ls -1 universal/workflows/praxis_os_upgrade_v1/phases/2/task-*.md | wc -l  # Should be 4
grep "4 tasks" universal/workflows/praxis_os_upgrade_v1/phases/2/phase.md
grep "~3 minutes 35 seconds" universal/workflows/praxis_os_upgrade_v1/README.md
```

---

## 🚫 Anti-Patterns

### Anti-Pattern 1: "I'll Update Docs Later"
❌ Committing code without documentation updates
✅ Update all docs in the same commit

### Anti-Pattern 2: "It's Just a Small Change"
❌ Skipping impact analysis for "trivial" changes
✅ Every change gets impact analysis, no exceptions

### Anti-Pattern 3: "I Think I Got Everything"
❌ Guessing what needs updating
✅ Use the matrix systematically

### Anti-Pattern 4: "Docs Are Out of Sync"
❌ Treating docs as separate from code
✅ Docs are code, test them like code

---

**Remember: Incomplete documentation is worse than no documentation. It creates false confidence and wastes time. Use this checklist. Every time. No exceptions.**

