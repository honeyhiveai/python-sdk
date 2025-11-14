# prAxIs OS Update Standards (Discovery Guide)

**Guide for discovering and understanding prAxIs OS updates**

---

## Questions This Answers

- **How do I update prAxIs OS?**
- **When should I update prAxIs OS?**
- **What's the difference between content and server updates?**
- **How do I safely update without breaking custom content?**
- **What's the automated workflow for prAxIs OS upgrades?**
- **How do I get the latest standards and workflows?**
- **What validation happens during an update?**
- **How do I rollback if an update fails?**
- **What are the triggers for updating prAxIs OS?**
- **How long does a prAxIs OS update take?**

## 🚨 prAxIs OS Update Quick Reference (TL;DR)

**Keywords for search**: praxis os update, upgrade praxis os, how to update praxis os, praxis os installation update, update standards workflows, sync from universal, praxis os upgrade workflow, update procedure

**Critical: Use the automated workflow, not manual commands!**

```python
# ✅ CORRECT: Use the automated workflow
start_workflow(
    workflow_type="praxis_os_upgrade_v1",
    target_file="mcp_server",
    options={
        "source_path": "/path/to/praxis-os",
        "dry_run": false,
        "auto_restart": true
    }
)
```

**Why use the workflow:**
- ✅ Automatic validation (pre-flight checks prevent bad upgrades)
- ✅ Rollback capability (automatic rollback on any failure)
- ✅ Preserves custom content (never deletes user specs/standards)
- ✅ Handles server restart (survives MCP server restart)
- ✅ Complete validation (post-upgrade health checks)
- ✅ ~3.5 minutes fully guided

**For complete guide, continue reading below.**

---

## 🎯 Purpose

This standard helps AI agents **discover and understand** when and how to update prAxIs OS installations. It explains:

- **WHEN** to update (triggers, frequency, urgency)
- **WHY** the directory structure matters (universal/ namespace, custom protection)
- **HOW** to execute updates (via `praxis_os_upgrade_v1` workflow)
- **WHAT** to validate (directory structure, file counts, functionality)

**This is a discovery guide, not a command reference.** Use the `praxis_os_upgrade_v1` workflow for actual updates.

---

## 📦 Update Types

### Content Updates

Updating standards, workflows, and usage documentation:
- **Source**: `universal/` directory in praxis-os repository
- **Destination**: `.praxis-os/` directory in your project
- **Method**: Via `praxis_os_upgrade_v1` workflow
- **Time**: ~2 minutes
- **Requires**: File watcher auto-rebuilds RAG index (10-30 seconds)
- **No server restart needed** for content-only updates

### Server Updates

Updating the MCP server software:
- **Source**: `mcp_server/` directory or PyPI package
- **Method**: Via `praxis_os_upgrade_v1` workflow (handles pip install)
- **Time**: ~1.5 minutes
- **Requires**: MCP server restart (workflow handles this)

### Combined Updates

The `praxis_os_upgrade_v1` workflow handles **both types** in a single execution:
- Phase 0-2: Validate, backup, update content
- Phase 3: Update and restart MCP server (workflow survives restart)
- Phase 4-5: Validate and cleanup

---

## 📍 Directory Structure Standards

### Understanding the Universal Namespace

**STANDARD:** prAxIs OS content MUST be namespaced under `universal/` to preserve custom content.

**Source Repository Structure:**
```
praxis-os/
├── universal/                    ← CANONICAL SOURCE
│   ├── standards/
│   │   ├── ai-assistant/
│   │   ├── development/
│   │   ├── testing/
│   │   └── workflows/
│   ├── usage/
│   └── workflows/
│       ├── test_generation_v3/
│       ├── spec_execution_v1/
│       └── praxis_os_upgrade_v1/
│
└── .praxis-os/                    ← LOCAL BUILD (praxis-os only)
    ├── standards/
    ├── usage/
    ├── workflows/
    ├── rag_index/                ← Generated, never sync
    └── .mcp_state/               ← Generated, never sync
```

**Installed Project Structure:**
```
your-project/
└── .praxis-os/
    ├── standards/
    │   ├── universal/            ← prAxIs OS provided (synced with --delete)
    │   │   ├── ai-assistant/
    │   │   ├── development/
    │   │   ├── testing/
    │   │   └── workflows/
    │   └── development/          ← Project-specific (NEVER touched by sync)
    │       └── my-custom-standards.md
    │
    ├── usage/                    ← Mixed (prAxIs OS + custom, NO --delete)
    │   ├── mcp-usage-guide.md    ← prAxIs OS provided
    │   └── project-guide.md      ← Project-specific
    │
    ├── workflows/                ← prAxIs OS managed (synced with --delete)
    │   └── test_generation_v3/
    │
    ├── specs/                    ← Project-only (NEVER touched by sync)
    │   └── 2025-10-10-feature/
    │
    ├── rag_index/                ← Generated by MCP server
    └── .mcp_state/               ← Generated by MCP server
```

**Why This Structure:**

1. **Universal Namespace Isolation**: 
   - prAxIs OS content lives in `.praxis-os/standards/universal/`
   - Custom content lives in `.praxis-os/standards/development/`
   - Updates can safely use `--delete` on `universal/` without touching custom content

2. **Clear Ownership Boundaries**:
   - **System-Managed (can use --delete)**: `standards/universal/`, `workflows/`
   - **User-Writable (never --delete)**: `usage/`, `specs/`, `standards/development/`

3. **Safe Updates**:
   - Workflow knows exactly what to sync and what to protect
   - No need for complex `--exclude` patterns
   - Impossible to accidentally delete user content

---

## ⏰ When to Update

### Update Triggers

**MUST update immediately when:**
- 🔴 Security vulnerabilities disclosed
- 🔴 Breaking changes affect your project functionality
- 🔴 Bugs in current version block your work

**SHOULD update when:**
- 🟡 New workflow features you need are released
- 🟡 Significant performance improvements available
- 🟡 Your standards are >1 month old

**MAY update when:**
- 🟢 Minor documentation improvements
- 🟢 Monthly maintenance window
- 🟢 You're starting a new feature and want latest best practices

### Update Frequency Guidelines

- **Minimum**: Once per quarter
- **Recommended**: Monthly
- **Active Development**: Weekly (if using cutting-edge features)

### How to Check if Update Needed

```bash
# Check your current version
cat .praxis-os/VERSION.txt

# Check latest version in source repo
cd /path/to/praxis-os
git pull origin main
git log -1
```

If commit hashes differ, an update is available.

---

## 🚀 How to Execute Updates

### Use the Automated Workflow

**STANDARD:** All updates MUST use the `praxis_os_upgrade_v1` workflow.

```python
# Discover the workflow first
pos_search_project(content_type="standards", query="praxis os upgrade workflow")

# Start the workflow
start_workflow(
    workflow_type="praxis_os_upgrade_v1",
    target_file="mcp_server",
    options={
        "source_path": "/path/to/praxis-os",
        "dry_run": false,            # Set true to preview changes
        "auto_restart": true          # Auto-restart MCP server in Phase 3
    }
)

# The workflow will:
# Phase 0 (30s): Validate source, target, disk space, no concurrent upgrades
# Phase 1 (20s): Create backup, verify backup, acquire lock
# Phase 2 (60s): Dry-run, execute upgrade, update gitignore, verify checksums
# Phase 3 (60s): Copy server, install deps, restart server (workflow survives)
# Phase 4 (30s): Validate tools, smoke tests, generate report
# Phase 5 (15s): Release lock, archive backups, generate summary
```

### After Server Restart (Phase 3)

The workflow automatically resumes after the MCP server restart:

```python
# The workflow survives the restart via disk state
# Continue where you left off:
get_current_phase(session_id)  # Returns Phase 4 content

# Or check full state:
get_workflow_state(session_id)
```

---

## ✅ Post-Update Validation

### Directory Structure Check

Verify the structure matches the standard:

```bash
# Should exist - prAxIs OS universal content
test -d .praxis-os/standards/universal/ai-assistant/ && echo "✅ Universal standards present"

# Should exist if you have custom content
test -d .praxis-os/standards/development/ && echo "✅ Custom standards preserved"

# Should exist - user specs
test -d .praxis-os/specs/ && echo "✅ User specs preserved"

# Should NOT exist - old flat structure
test ! -d .praxis-os/standards/ai-assistant/ && echo "✅ No flat structure"
```

### Functional Validation

```python
# Test RAG search
pos_search_project(content_type="standards", query="testing standards")
# Should return results

# Test workflow discovery
pos_search_project(content_type="standards", query="test generation workflow")
# Should return test_generation_v3

# Test browser tool (if applicable)
pos_browser(action="navigate", url="https://example.com", session_id="test-123")
```

### File Count Validation

```bash
# Expected counts (approximate)
echo "Universal standards: $(find .praxis-os/standards/universal -type f -name '*.md' | wc -l)"
# Should be: 50-100 files

echo "Workflows: $(find .praxis-os/workflows -maxdepth 1 -type d | wc -l)"
# Should be: 3-10 workflows

echo "Usage docs: $(find .praxis-os/usage -type f -name '*.md' | wc -l)"
# Should be: 5-15 files
```

---

## 🚨 What NOT to Do

### ❌ FORBIDDEN: Manual rsync Commands

**DO NOT run manual rsync commands.** Use the workflow instead.

**Why manual commands are dangerous:**
```bash
# ❌ This looks safe but will destroy custom content:
rsync -av --delete /path/to/praxis-os/universal/standards/ .praxis-os/standards/

# What it does:
# 1. Deletes .praxis-os/standards/universal/ (OK)
# 2. Deletes .praxis-os/standards/development/ (YOUR CUSTOM CONTENT GONE!)
# 3. Copies universal/standards/* to .praxis-os/standards/ (wrong structure)
```

**The workflow handles this correctly:**
```bash
# ✅ Workflow does this (simplified):
rsync -av --delete universal/standards/ .praxis-os/standards/universal/
# Result: Only universal/ updated, custom content preserved
```

### ❌ FORBIDDEN: Syncing from .praxis-os/

```bash
# ❌ NEVER sync from the .praxis-os directory in praxis-os
rsync -av /path/to/praxis-os/.praxis-os/ .praxis-os/
```

**Why this is wrong:**
- `.praxis-os/` in praxis-os is a **build artifact directory**
- Contains processed files, RAG index, local state
- Not the canonical source of truth
- May include development-only or test data

**Always sync from `universal/`** (the workflow does this automatically).

### ❌ FORBIDDEN: Partial Updates

```bash
# ❌ Don't cherry-pick individual files
cp praxis-os/universal/standards/testing/test-pyramid.md .praxis-os/standards/universal/testing/
```

**Why this is wrong:**
- Creates version conflicts (some files new, some old)
- Breaks cross-references between standards
- RAG index may be inconsistent
- Hard to track what version you're on

**Always update atomically** (the workflow does this).

---

## 🔧 Troubleshooting

### Issue: Flat Structure Detected

**Symptom:**
```bash
ls .praxis-os/standards/
# Shows: ai-assistant/ development/ testing/
# Missing: universal/
```

**Cause:** Update was done with incorrect rsync command (pre-workflow era)

**Fix:**
```python
# Use the workflow with a fresh target
# The workflow will detect and fix the structure
start_workflow(
    workflow_type="praxis_os_upgrade_v1",
    target_file="mcp_server",
    options={"source_path": "/path/to/praxis-os"}
)
```

### Issue: Duplicate Files in Multiple Locations

**Symptom:**
```bash
# Same file exists in both places:
.praxis-os/standards/ai-assistant/rag-content-authoring.md
.praxis-os/standards/universal/ai-assistant/rag-content-authoring.md
```

**Cause:** Mix of old flat structure and new nested structure

**Fix:**
```bash
# 1. Backup your custom content
cp -r .praxis-os/standards/development/ /tmp/my-custom-standards/

# 2. Remove the flat structure
rm -rf .praxis-os/standards/ai-assistant/
rm -rf .praxis-os/standards/testing/
# Keep: .praxis-os/standards/universal/ and .praxis-os/standards/development/

# 3. Run the workflow to ensure consistency
start_workflow(workflow_type="praxis_os_upgrade_v1", ...)

# 4. Restore custom content if needed
cp -r /tmp/my-custom-standards/ .praxis-os/standards/development/
```

### Issue: Custom Content Deleted

**Symptom:** Your custom standards/workflows disappeared after update

**Cause:** Manual rsync with `--delete` on wrong directory

**Recovery:**
```bash
# 1. Restore from backup (workflow creates these)
ls -lt .praxis-os.backup.*
# Find most recent backup

# 2. Restore custom content
cp -r .praxis-os.backup.TIMESTAMP/standards/development/ .praxis-os/standards/

# 3. Use workflow for future updates to prevent this
```

**Prevention:** Always use the `praxis_os_upgrade_v1` workflow.

---

## 📊 Version Tracking

### VERSION.txt File

After updates, check `.praxis-os/VERSION.txt`:

```txt
prAxIs OS Content Version

Repository: https://github.com/honeyhiveai/praxis-os
Last Updated: 2025-10-10 18:30:00
Source Commit: abc123def
Updated By: praxis_os_upgrade_v1 workflow
Previous Version: v1.2.3
Current Version: v1.3.0
Notes: Updated for horizontal scaling features
```

The workflow maintains this automatically.

---

## 🔍 Discovery Queries

**To find this standard:**
```python
pos_search_project(content_type="standards", query="how to update praxis os")
pos_search_project(content_type="standards", query="praxis os upgrade procedure")
pos_search_project(content_type="standards", query="sync from universal directory")
```

**To find the workflow:**
```python
pos_search_project(content_type="standards", query="praxis os upgrade workflow")
pos_search_project(content_type="standards", query="automated upgrade with rollback")
```

**To understand directory structure:**
```python
pos_search_project(content_type="standards", query="praxis os directory structure universal namespace")
pos_search_project(content_type="standards", query="why nested standards structure")
```

---

## 📚 Related Standards

- [Workflow System Overview](../workflows/workflow-system-overview.md) - How workflows work
- [Workflow Metadata Standards](../workflows/workflow-metadata-standards.md) - Workflow discovery
- [Dogfooding Model](../development/dogfooding-model.md) - How praxis-os uses prAxIs OS

**Related Workflows:**
- `praxis_os_upgrade_v1` - Automated upgrade with validation and rollback
- `spec_execution_v1` - How to execute specifications after update

---

## ✅ Success Checklist

After reading this standard, you should understand:

- [ ] Why to use `praxis_os_upgrade_v1` workflow instead of manual commands
- [ ] When to trigger an update (security, bugs, features, maintenance)
- [ ] Why the universal/ namespace exists (custom content protection)
- [ ] What directory structure looks like after correct update
- [ ] How to validate the update was successful
- [ ] What to do if you detect the old flat structure
- [ ] Why manual rsync commands are dangerous

**Next Step:**
```python
# Start the upgrade workflow
start_workflow(
    workflow_type="praxis_os_upgrade_v1",
    target_file="mcp_server",
    options={"source_path": "/path/to/praxis-os"}
)
```

---

**This is a discovery standard, not an execution manual. Use the `praxis_os_upgrade_v1` workflow for actual updates.**
