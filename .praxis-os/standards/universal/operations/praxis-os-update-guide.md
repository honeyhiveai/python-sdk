# prAxIs OS Update Guide

**How to properly update prAxIs OS content in consuming projects**

**Keywords for search**: prAxIs OS update, how to update prAxIs OS, sync from universal, update procedures, content sync, MCP server upgrade, rsync commands, safe upgrade, prAxIs OS installation update

---

## 🚨 Quick Reference (TL;DR)

**Critical Rules:**
1. ✅ **ALWAYS sync from** `universal/` directory (source)
2. ❌ **NEVER sync from** `.praxis-os/` directory (build artifact)
3. ✅ **Use safe-upgrade** script for automated updates
4. ✅ **Sync to** `.praxis-os/` in your consuming project
5. ✅ **RAG index auto-rebuilds** on file changes (no manual action needed)

**Quick Update Command:**
```bash
# Sync from praxis-os/universal/ to your-project/.praxis-os/
rsync -av --delete /path/to/praxis-os/universal/ /path/to/your-project/.praxis-os/
```

**Recommended:** Use `praxis_os_upgrade_v1` workflow for safe, automated updates with validation and rollback.

---

## Questions This Answers

- "How do I update prAxIs OS in my project?"
- "Where do I sync prAxIs OS content from?"
- "Should I sync from .praxis-os or universal?"
- "How do I update standards and workflows?"
- "Does the RAG index rebuild automatically?"
- "How often should I update prAxIs OS?"
- "What's the safe way to update?"
- "How do I use the safe-upgrade script?"
- "What gets synced during an update?"
- "How do I update the MCP server?"

---

## 🚨 CRITICAL: Update Source Location

### ❌ WRONG - Do NOT Sync From

**NEVER sync from the `.praxis-os/` directory in the praxis-os repo:**

```bash
# ❌ WRONG - This is a build artifact, not source!
rsync -av /path/to/praxis-os/.praxis-os/ .praxis-os/
```

**Why this is wrong:**
- `.praxis-os/` is a **local build output directory**
- Contains processed/indexed files specific to the development environment
- May include test data, temporary files, or development-only content
- Not the canonical source of truth

### ✅ CORRECT - Sync From Universal

**ALWAYS sync from the `universal/` directory in the praxis-os repo:**

```bash
# ✅ CORRECT - Sync from source
rsync -av /path/to/praxis-os/universal/ .praxis-os/
```

**Why this is correct:**
- `universal/` contains the **canonical source content**
- Designed for distribution to consuming projects
- Versioned and maintained properly
- Clean, production-ready content

---

## 📂 Directory Structure Clarification

### In praxis-os Repo (Source)

```
praxis-os/
├── universal/              # ✅ SOURCE - Sync from here
│   ├── standards/          # Canonical standards content
│   ├── usage/              # Usage documentation  
│   └── workflows/          # Workflow definitions
│
├── .praxis-os/              # ❌ BUILD ARTIFACT - Do not sync
│   ├── standards/          # Processed/built content
│   ├── rag_index/          # Local vector database
│   └── .mcp_state/         # Local MCP state
│
└── mcp_server/             # MCP server source code
```

### In Your Consuming Project

```
your-project/
├── .praxis-os/              # ✅ Your local prAxIs OS installation
│   ├── standards/          # Synced from universal/standards/
│   ├── usage/              # Synced from universal/usage/
│   └── workflows/          # Synced from universal/workflows/
│
└── config.json             # Your project's custom paths (optional)
```

---

## 🔄 Update Process

### Step 1: Pull Latest from praxis-os

```bash
cd /path/to/praxis-os
git pull origin main
```

### Step 2: Sync to Your Project

**Option A: Safe Upgrade (Recommended)**

```bash
cd /path/to/your-project

# Use manifest-based safe upgrade tool (never deletes customer content)
python /path/to/praxis-os/scripts/safe-upgrade.py \
  --source /path/to/praxis-os \
  --target .praxis-os

# See interactive prompts for conflicts
# Creates automatic backup before changes
```

**Option B: Manual Sync (for advanced users)**

```bash
cd /path/to/your-project

# Sync standards (adds/updates only, never deletes)
rsync -av /path/to/praxis-os/universal/standards/ .praxis-os/standards/

# Sync usage docs
rsync -av /path/to/praxis-os/universal/usage/ .praxis-os/usage/

# Sync workflows (optional - only if you use them)
rsync -av /path/to/praxis-os/universal/workflows/ .praxis-os/workflows/
```

**Note:** Manual sync does NOT delete files. Old files remain. Use safe-upgrade.py for conflict detection.

### Step 3: RAG Index Auto-Updates

**No action needed!** The MCP server's file watcher automatically detects content changes and triggers incremental index updates.

```bash
# File watchers monitor:
# - .praxis-os/standards/
# - .praxis-os/usage/
# - .praxis-os/workflows/

# When you rsync new content, the watcher:
# 1. Detects file changes
# 2. Automatically rebuilds the RAG index
# 3. Updates are incremental (fast)

# You'll see in logs:
# "👀 File change detected, rebuilding RAG index..."
```

**Manual rebuild only needed if:**
- File watcher is disabled
- Running one-off index build
- Troubleshooting index issues

```bash
# Manual rebuild (rarely needed)
cd /path/to/your-project
python -m agent_os.scripts.build_rag_index
```

---

## 🎯 What to Sync

### Core Content (Always Sync)

✅ **Standards** - `universal/standards/` → `.praxis-os/standards/`
- Testing standards
- Production code standards
- Workflow standards
- Architecture patterns

✅ **Usage Documentation** - `universal/usage/` → `.praxis-os/usage/`
- MCP usage guide
- Configuration guides
- Best practices

### Optional Content

⚠️ **Workflows** - `universal/workflows/` → `.praxis-os/workflows/`
- Only sync if you use prAxIs OS workflows
- Test generation workflows
- Production code workflows
- Can customize or replace with your own

❌ **Do NOT Sync:**
- `.praxis-os/rag_index/` - This is your local vector database
- `.praxis-os/.mcp_state/` - This is your local MCP state
- `.praxis-os/scripts/` - Use the ones from mcp_server instead

---

## 🔧 Update Scripts

### Simple Update Script

Create `scripts/update-agent-os.sh` in your project:

```bash
#!/bin/bash
set -e

# Configuration
AGENT_OS_REPO="/path/to/praxis-os"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔄 Updating prAxIs OS content..."

# Use safe-upgrade tool (never deletes customer content)
echo "📦 Running safe upgrade..."
python "$AGENT_OS_REPO/scripts/safe-upgrade.py" \
  --source "$AGENT_OS_REPO" \
  --target "$PROJECT_ROOT/.praxis-os"

echo "✅ prAxIs OS content updated!"
echo "💡 File watcher will automatically rebuild RAG index"
echo "⏱️  Wait ~10-30 seconds for index update to complete"
```

Make it executable:
```bash
chmod +x scripts/update-agent-os.sh
```

Run it:
```bash
./scripts/update-agent-os.sh
```

### Advanced Update Script with Validation

```bash
#!/bin/bash
set -e

AGENT_OS_REPO="/path/to/praxis-os"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Validation: Check source exists
if [ ! -d "$AGENT_OS_REPO/universal" ]; then
    echo "❌ ERROR: Cannot find $AGENT_OS_REPO/universal/"
    echo "💡 Make sure AGENT_OS_REPO points to the praxis-os repository"
    exit 1
fi

# Validation: Warn if syncing from .praxis-os
if [[ "$AGENT_OS_REPO" == *".praxis-os"* ]]; then
    echo "❌ ERROR: Attempting to sync from .praxis-os directory!"
    echo "💡 You must sync from the 'universal/' directory, not '.praxis-os/'"
    echo "💡 Update AGENT_OS_REPO to point to the praxis-os repository root"
    exit 1
fi

# Backup existing content (optional)
BACKUP_DIR="$PROJECT_ROOT/.praxis-os.backup.$(date +%Y%m%d_%H%M%S)"
echo "💾 Creating backup at $BACKUP_DIR"
cp -r "$PROJECT_ROOT/.praxis-os" "$BACKUP_DIR"

# Use safe-upgrade tool (handles conflicts, never deletes customer content)
echo "🔄 Running safe upgrade from $AGENT_OS_REPO/universal/"

python "$AGENT_OS_REPO/scripts/safe-upgrade.py" \
    --source "$AGENT_OS_REPO" \
    --target "$PROJECT_ROOT/.praxis-os"

echo "✅ Update complete!"
echo "📁 Backup saved to: $BACKUP_DIR"
echo "💡 Delete backup after confirming everything works"
```

---

## 🔍 Version Tracking

### Check Current Version

The standards include version information:

```bash
# Check workflow metadata version
cat .praxis-os/workflows/test_generation_v3/metadata.json | grep version

# Check for version markers in standards
grep -r "Version:" .praxis-os/standards/ | head -5
```

### Track Updates in Your Project

Create `.praxis-os/VERSION.txt`:

```txt
prAxIs OS Content Version

Last Updated: 2025-10-06
Source Commit: abc123def
Updated By: josh
Notes: Updated to include v1.3.0 horizontal scaling features
```

Update this file each time you sync:

```bash
cat > .praxis-os/VERSION.txt << EOF
prAxIs OS Content Version

Last Updated: $(date +%Y-%m-%d)
Source Commit: $(cd /path/to/praxis-os && git rev-parse --short HEAD)
Updated By: $(whoami)
Notes: Regular update
EOF
```

---

## 🛡️ Manifest-Based Safe Upgrade (v1.3.0+)

**NEW in v1.3.0**: Automatic conflict detection and safe upgrades!

The manifest-based upgrade system uses checksums to detect conflicts between local customizations and upstream changes, making upgrades much safer.

### How It Works

1. **Manifest Generation**: Each release includes a `.universal-manifest.json` file with SHA-256 checksums of all skeleton files
2. **Conflict Detection**: The upgrade tool compares local files, upstream files, and the manifest to detect conflicts
3. **Smart Decisions**: Files are auto-updated safely or prompt for conflicts

### File States

- **NEW**: File exists in upstream but not locally → Prompts to add
- **UNCHANGED**: Both exist, no changes → Skipped silently
- **AUTO_UPDATE**: Local unchanged, upstream changed → Auto-updated safely
- **LOCAL_ONLY**: Local changed, upstream unchanged → Preserved automatically
- **CONFLICT**: Both changed → Interactive prompt

### Quick Start

#### Dry-Run (Preview Only)

```bash
cd /path/to/your-project
python /path/to/praxis-os/scripts/safe-upgrade.py \
  --source /path/to/praxis-os \
  --dry-run
```

**Output:**
```
📊 Analysis Summary:
   New files: 15
   Auto-update: 3
   Unchanged: 42
   Local-only changes: 2
   Conflicts: 0
   Errors: 0

➕ New files to add:
   + standards/ai-safety/new-standard.md
   ...
```

#### Live Upgrade

```bash
# Run without --dry-run to execute
python /path/to/praxis-os/scripts/safe-upgrade.py \
  --source /path/to/praxis-os \
  --target .praxis-os
```

**What happens:**
1. **Automatic backup** created (`.praxis-os.backup.20251007_120000`)
2. **New files** - Prompts to add each one
3. **Auto-updates** - Safely updates unchanged files automatically
4. **Conflicts** - Interactive prompts with diff viewer
5. **Summary report** with rollback instructions

### Interactive Prompts

#### New File Prompt

```
➕ New file: standards/testing/new-standard.md (12.3 KB)
   Add this file? [Y/n]: y
   ✅ Added
```

#### Conflict Prompt

```
⚠️  CONFLICT: usage/mcp-usage-guide.md
   Both local and universal versions have changed.

   Local:     15,234 bytes
   Universal: 15,891 bytes

   [K] Keep local (preserve your changes)
   [R] Replace with universal (lose local changes)
   [D] Show diff
   [S] Skip (decide later)

   Choice: d
```

### Rollback

If something goes wrong, rollback is simple:

```bash
# The tool shows these instructions after upgrade
rm -rf .praxis-os
mv .praxis-os.backup.20251007_120000 .praxis-os
```

### Advantages over rsync

| Feature | rsync | Manifest-Based |
|---------|-------|----------------|
| Conflict detection | ❌ None | ✅ Automatic |
| Preserves local changes | ⚠️ Manual --exclude | ✅ Automatic |
| Automatic backup | ❌ Manual | ✅ Automatic |
| Diff viewer | ❌ None | ✅ Built-in |
| Dry-run preview | ⚠️ Limited | ✅ Full analysis |
| Rollback | ❌ Manual backup | ✅ One command |

### Requirements

- **praxis-os v1.3.0+** (includes manifest)
- **Python 3.8+** (for upgrade script)
- **Manifest file**: `universal/.universal-manifest.json`

### Generate Manifest (Maintainers Only)

If you're maintaining a fork:

```bash
cd praxis-os
python scripts/generate-manifest.py --version 1.3.0
# Creates universal/.universal-manifest.json
```

---

## 🚨 Common Mistakes to Avoid

### ❌ Mistake 1: Syncing from .praxis-os

```bash
# WRONG - This syncs build artifacts
rsync -av praxis-os/.praxis-os/ .praxis-os/
```

**Fix:** Sync from `universal/` directory instead.

### ❌ Mistake 2: Overwriting Custom Workflows

If you have custom workflows, the safe-upgrade tool will detect and preserve them:

```bash
# Safe-upgrade automatically detects custom content
python /path/to/praxis-os/scripts/safe-upgrade.py \
  --source /path/to/praxis-os \
  --target .praxis-os

# You'll be prompted:
# ⚠️  CONFLICT: workflows/my_custom_workflow/
#   [K] Keep local (your custom workflow)
#   [R] Replace (not recommended)
#   [S] Skip
```

### ❌ Mistake 3: Syncing MCP Server State

```bash
# WRONG - Includes state files
rsync -av praxis-os/.praxis-os/ .praxis-os/
```

**Fix:** Always use source-controlled content from `universal/`, never `.praxis-os/`.

### ❌ Mistake 4: Not Rebuilding RAG Index

After updating content, always rebuild or restart MCP server to rebuild index.

---

## 📋 Update Checklist

Before updating:
- [ ] Pull latest from praxis-os repo
- [ ] Review changelog for breaking changes
- [ ] Backup current `.praxis-os/` directory (optional but recommended)

During update:
- [ ] Sync from `universal/standards/` (not `.praxis-os/standards/`)
- [ ] Sync from `universal/usage/`
- [ ] Sync from `universal/workflows/` (if applicable)
- [ ] Preserve custom workflows/configs (use --exclude)

After update:
- [ ] Wait for file watcher to rebuild index (~10-30 seconds)
- [ ] Test with a simple query: `pos_search_project(content_type="standards", query="test patterns")`
- [ ] Verify workflows still work (if used)
- [ ] Update `.praxis-os/VERSION.txt` (optional)
- [ ] Delete backup if everything works

Note: **No server restart needed** for content updates - file watcher handles it automatically!

---

## 🔧 config.json Considerations

If you use custom paths via `config.json`, make sure your update script syncs to those paths:

```json
{
  "rag_sources": {
    "standards_path": "custom/path/standards",
    "usage_path": "custom/path/usage",
    "workflows_path": "custom/path/workflows"
  }
}
```

Update script should respect these paths:

```bash
# Read config and use custom paths (if needed)
# Safe-upgrade tool handles standard paths automatically
python "$AGENT_OS_REPO/scripts/safe-upgrade.py" \
  --source "$AGENT_OS_REPO" \
  --target .praxis-os
```

---

## 📚 Related Documentation

- **Installation Guide**: How to set up prAxIs OS initially
- **MCP Usage Guide**: How to use MCP tools after updating
- **RAG Configuration**: How to configure custom RAG paths

---

## 🆘 Troubleshooting

### Issue: MCP Server Not Finding Updated Content

**Cause:** File watcher not running or index update failed

**Fix:**
```bash
# Check MCP server logs for file watcher status
# Should see: "👀 Watching .praxis-os/standards/ for AI edits..."

# If file watcher not running, restart MCP server
pkill -f "mcp.*agent-os-rag"
# Cursor will auto-restart server

# Or manually rebuild index (bypasses file watcher)
python -m agent_os.scripts.build_rag_index
```

### Issue: Lost Custom Files After Upgrade

**Cause:** Accidentally overwrote custom files during manual sync

**Fix:**
```bash
# Restore from backup (safe-upgrade creates these automatically)
rm -rf .praxis-os
mv .praxis-os.backup.20251006_120000 .praxis-os

# Next time, use safe-upgrade tool which detects conflicts
python /path/to/praxis-os/scripts/safe-upgrade.py \
    --source /path/to/praxis-os \
    --target .praxis-os
# Will prompt before overwriting any custom content
```

### Issue: Conflicting Versions

**Cause:** Partial update or mixed versions

**Fix:**
```bash
# Clean install using safe-upgrade tool
rm -rf .praxis-os/
mkdir -p .praxis-os/

python /path/to/praxis-os/scripts/safe-upgrade.py \
    --source /path/to/praxis-os \
    --target .praxis-os
```

---

## 🎓 Best Practices

1. **Always sync from `universal/`** - Never from `.praxis-os/`
2. **Use version tracking** - Maintain `.praxis-os/VERSION.txt`
3. **Test after updates** - Verify MCP tools work
4. **Automate updates** - Use update scripts to prevent mistakes
5. **Backup before updates** - Keep previous version for rollback
6. **Review changelogs** - Check for breaking changes
7. **Rebuild indexes** - Always rebuild RAG after content changes

---

## 🔐 Security Considerations

- **Source validation**: Verify you're syncing from the official praxis-os repo
- **Content inspection**: Review major updates before applying
- **Access control**: Restrict who can run update scripts
- **Audit trail**: Log all updates (use VERSION.txt)

---

## 📞 Need Help?

If you encounter issues:
1. Check this guide for common mistakes
2. Review the changelog in praxis-os repo
3. Verify you're syncing from `universal/` not `.praxis-os/`
4. Check file watchers are running (auto-rebuild)
5. Try a clean reinstall from `universal/`

---

## When to Query This Guide

This guide is most valuable when:

1. **Updating prAxIs OS**
   - Situation: Need to get latest standards and workflows
   - Query: `pos_search_project(content_type="standards", query="how to update prAxIs OS")`

2. **Unsure About Sync Source**
   - Situation: Don't know if I should sync from `.praxis-os` or `universal`
   - Query: `pos_search_project(content_type="standards", query="sync from universal or agent-os")`

3. **RAG Index Questions**
   - Situation: Wondering if I need to rebuild RAG index
   - Query: `pos_search_project(content_type="standards", query="RAG index auto rebuild")`

4. **MCP Server Updates**
   - Situation: Need to update MCP server code
   - Query: `pos_search_project(content_type="standards", query="update MCP server")`

5. **Update Frequency**
   - Situation: How often should I update?
   - Query: `pos_search_project(content_type="standards", query="prAxIs OS update frequency")`

### Query by Use Case

| Use Case | Example Query |
|----------|---------------|
| Update process | `pos_search_project(content_type="standards", query="how to update prAxIs OS")` |
| Sync source | `pos_search_project(content_type="standards", query="sync from universal")` |
| Safe upgrade | `pos_search_project(content_type="standards", query="safe upgrade prAxIs OS")` |
| RAG index | `pos_search_project(content_type="standards", query="RAG index rebuild")` |
| MCP server update | `pos_search_project(content_type="standards", query="update MCP server")` |

---

## Cross-References and Related Guides

**Update Standards:**
- `standards/installation/update-procedures.md` - Update procedures standard (discovery guide)
  → `pos_search_project(content_type="standards", query="prAxIs OS update standards")`

**Workflows:**
- `workflows/praxis_os_upgrade_v1/` - Automated safe upgrade workflow
  → `pos_search_project(content_type="standards", query="praxis os upgrade workflow")`

**Installation:**
- `usage/installation-guide.md` - Initial installation (if available)
  → `pos_search_project(content_type="standards", query="prAxIs OS installation")`

**Query workflow:**
1. **Before Update**: `pos_search_project(content_type="standards", query="how to update prAxIs OS")` → Learn process
2. **Execute**: Use `praxis_os_upgrade_v1` workflow for safe update
3. **Verify**: Check RAG index rebuilt automatically
4. **Troubleshoot**: `pos_search_project(content_type="standards", query="prAxIs OS update issues")` if needed

---

**Remember:** 
- ✅ Source: `universal/` directory
- ❌ Not: `.praxis-os/` directory

Always sync from the canonical source content, not build artifacts!
