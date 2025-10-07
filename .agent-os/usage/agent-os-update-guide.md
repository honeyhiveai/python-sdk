# Agent OS Update Guide

**How to properly update Agent OS content in consuming projects**

---

## 🚨 CRITICAL: Update Source Location

### ❌ WRONG - Do NOT Sync From

**NEVER sync from the `.agent-os/` directory in the agent-os-enhanced repo:**

```bash
# ❌ WRONG - This is a build artifact, not source!
rsync -av /path/to/agent-os-enhanced/.agent-os/ .agent-os/
```

**Why this is wrong:**
- `.agent-os/` is a **local build output directory**
- Contains processed/indexed files specific to the development environment
- May include test data, temporary files, or development-only content
- Not the canonical source of truth

### ✅ CORRECT - Sync From Universal

**ALWAYS sync from the `universal/` directory in the agent-os-enhanced repo:**

```bash
# ✅ CORRECT - Sync from source
rsync -av /path/to/agent-os-enhanced/universal/ .agent-os/
```

**Why this is correct:**
- `universal/` contains the **canonical source content**
- Designed for distribution to consuming projects
- Versioned and maintained properly
- Clean, production-ready content

---

## 📂 Directory Structure Clarification

### In agent-os-enhanced Repo (Source)

```
agent-os-enhanced/
├── universal/              # ✅ SOURCE - Sync from here
│   ├── standards/          # Canonical standards content
│   ├── usage/              # Usage documentation  
│   └── workflows/          # Workflow definitions
│
├── .agent-os/              # ❌ BUILD ARTIFACT - Do not sync
│   ├── standards/          # Processed/built content
│   ├── rag_index/          # Local vector database
│   └── .mcp_state/         # Local MCP state
│
└── mcp_server/             # MCP server source code
```

### In Your Consuming Project

```
your-project/
├── .agent-os/              # ✅ Your local Agent OS installation
│   ├── standards/          # Synced from universal/standards/
│   ├── usage/              # Synced from universal/usage/
│   └── workflows/          # Synced from universal/workflows/
│
└── config.json             # Your project's custom paths (optional)
```

---

## 🔄 Update Process

### Step 1: Pull Latest from agent-os-enhanced

```bash
cd /path/to/agent-os-enhanced
git pull origin main
```

### Step 2: Sync to Your Project

```bash
cd /path/to/your-project

# Sync standards
rsync -av --delete /path/to/agent-os-enhanced/universal/standards/ .agent-os/standards/

# Sync usage docs
rsync -av --delete /path/to/agent-os-enhanced/universal/usage/ .agent-os/usage/

# Sync workflows (optional - only if you use them)
rsync -av --delete /path/to/agent-os-enhanced/universal/workflows/ .agent-os/workflows/
```

**Note:** The `--delete` flag removes files in destination that don't exist in source. Use with caution if you have custom local files.

### Step 3: RAG Index Auto-Updates

**No action needed!** The MCP server's file watcher automatically detects content changes and triggers incremental index updates.

```bash
# File watchers monitor:
# - .agent-os/standards/
# - .agent-os/usage/
# - .agent-os/workflows/

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

✅ **Standards** - `universal/standards/` → `.agent-os/standards/`
- Testing standards
- Production code standards
- Workflow standards
- Architecture patterns

✅ **Usage Documentation** - `universal/usage/` → `.agent-os/usage/`
- MCP usage guide
- Configuration guides
- Best practices

### Optional Content

⚠️ **Workflows** - `universal/workflows/` → `.agent-os/workflows/`
- Only sync if you use Agent OS workflows
- Test generation workflows
- Production code workflows
- Can customize or replace with your own

❌ **Do NOT Sync:**
- `.agent-os/rag_index/` - This is your local vector database
- `.agent-os/.mcp_state/` - This is your local MCP state
- `.agent-os/scripts/` - Use the ones from mcp_server instead

---

## 🔧 Update Scripts

### Simple Update Script

Create `scripts/update-agent-os.sh` in your project:

```bash
#!/bin/bash
set -e

# Configuration
AGENT_OS_REPO="/path/to/agent-os-enhanced"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔄 Updating Agent OS content..."

# Sync from universal (source) directory
echo "📦 Syncing standards..."
rsync -av --delete "$AGENT_OS_REPO/universal/standards/" "$PROJECT_ROOT/.agent-os/standards/"

echo "📦 Syncing usage docs..."
rsync -av --delete "$AGENT_OS_REPO/universal/usage/" "$PROJECT_ROOT/.agent-os/usage/"

echo "📦 Syncing workflows..."
rsync -av --delete "$AGENT_OS_REPO/universal/workflows/" "$PROJECT_ROOT/.agent-os/workflows/"

echo "✅ Agent OS content updated!"
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

AGENT_OS_REPO="/path/to/agent-os-enhanced"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Validation: Check source exists
if [ ! -d "$AGENT_OS_REPO/universal" ]; then
    echo "❌ ERROR: Cannot find $AGENT_OS_REPO/universal/"
    echo "💡 Make sure AGENT_OS_REPO points to the agent-os-enhanced repository"
    exit 1
fi

# Validation: Warn if syncing from .agent-os
if [[ "$AGENT_OS_REPO" == *".agent-os"* ]]; then
    echo "❌ ERROR: Attempting to sync from .agent-os directory!"
    echo "💡 You must sync from the 'universal/' directory, not '.agent-os/'"
    echo "💡 Update AGENT_OS_REPO to point to the agent-os-enhanced repository root"
    exit 1
fi

# Backup existing content (optional)
BACKUP_DIR="$PROJECT_ROOT/.agent-os.backup.$(date +%Y%m%d_%H%M%S)"
echo "💾 Creating backup at $BACKUP_DIR"
cp -r "$PROJECT_ROOT/.agent-os" "$BACKUP_DIR"

# Sync content
echo "🔄 Syncing from $AGENT_OS_REPO/universal/"

rsync -av --delete \
    --exclude="rag_index/" \
    --exclude=".mcp_state/" \
    --exclude="scripts/" \
    "$AGENT_OS_REPO/universal/standards/" "$PROJECT_ROOT/.agent-os/standards/"

rsync -av --delete \
    "$AGENT_OS_REPO/universal/usage/" "$PROJECT_ROOT/.agent-os/usage/"

rsync -av --delete \
    "$AGENT_OS_REPO/universal/workflows/" "$PROJECT_ROOT/.agent-os/workflows/"

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
cat .agent-os/workflows/test_generation_v3/metadata.json | grep version

# Check for version markers in standards
grep -r "Version:" .agent-os/standards/ | head -5
```

### Track Updates in Your Project

Create `.agent-os/VERSION.txt`:

```txt
Agent OS Content Version

Last Updated: 2025-10-06
Source Commit: abc123def
Updated By: josh
Notes: Updated to include v1.3.0 horizontal scaling features
```

Update this file each time you sync:

```bash
cat > .agent-os/VERSION.txt << EOF
Agent OS Content Version

Last Updated: $(date +%Y-%m-%d)
Source Commit: $(cd /path/to/agent-os-enhanced && git rev-parse --short HEAD)
Updated By: $(whoami)
Notes: Regular update
EOF
```

---

## 🚨 Common Mistakes to Avoid

### ❌ Mistake 1: Syncing from .agent-os

```bash
# WRONG - This syncs build artifacts
rsync -av agent-os-enhanced/.agent-os/ .agent-os/
```

**Fix:** Sync from `universal/` directory instead.

### ❌ Mistake 2: Overwriting Custom Workflows

If you have custom workflows, protect them:

```bash
# Use --exclude to protect custom workflows
rsync -av --delete \
    --exclude="my_custom_workflow/" \
    agent-os-enhanced/universal/workflows/ .agent-os/workflows/
```

### ❌ Mistake 3: Syncing MCP Server State

```bash
# WRONG - Includes state files
rsync -av agent-os-enhanced/.agent-os/ .agent-os/
```

**Fix:** Always use source-controlled content from `universal/`, never `.agent-os/`.

### ❌ Mistake 4: Not Rebuilding RAG Index

After updating content, always rebuild or restart MCP server to rebuild index.

---

## 📋 Update Checklist

Before updating:
- [ ] Pull latest from agent-os-enhanced repo
- [ ] Review changelog for breaking changes
- [ ] Backup current `.agent-os/` directory (optional but recommended)

During update:
- [ ] Sync from `universal/standards/` (not `.agent-os/standards/`)
- [ ] Sync from `universal/usage/`
- [ ] Sync from `universal/workflows/` (if applicable)
- [ ] Preserve custom workflows/configs (use --exclude)

After update:
- [ ] Wait for file watcher to rebuild index (~10-30 seconds)
- [ ] Test with a simple query: `search_standards("test patterns")`
- [ ] Verify workflows still work (if used)
- [ ] Update `.agent-os/VERSION.txt` (optional)
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
# Read config and use custom paths
STANDARDS_PATH=$(jq -r '.rag_sources.standards_path // ".agent-os/standards"' config.json)
rsync -av --delete "$AGENT_OS_REPO/universal/standards/" "$STANDARDS_PATH/"
```

---

## 📚 Related Documentation

- **Installation Guide**: How to set up Agent OS initially
- **MCP Usage Guide**: How to use MCP tools after updating
- **RAG Configuration**: How to configure custom RAG paths

---

## 🆘 Troubleshooting

### Issue: MCP Server Not Finding Updated Content

**Cause:** File watcher not running or index update failed

**Fix:**
```bash
# Check MCP server logs for file watcher status
# Should see: "👀 Watching .agent-os/standards/ for AI edits..."

# If file watcher not running, restart MCP server
pkill -f "mcp.*agent-os-rag"
# Cursor will auto-restart server

# Or manually rebuild index (bypasses file watcher)
python -m agent_os.scripts.build_rag_index
```

### Issue: Sync Deleted Custom Files

**Cause:** Used `--delete` flag without excluding custom files

**Fix:**
```bash
# Restore from backup
cp -r .agent-os.backup.20251006_120000/* .agent-os/

# Re-sync with exclusions
rsync -av --delete \
    --exclude="my_custom_workflow/" \
    --exclude="my_custom_standards/" \
    agent-os-enhanced/universal/ .agent-os/
```

### Issue: Conflicting Versions

**Cause:** Partial update or mixed versions

**Fix:**
```bash
# Clean install from source
rm -rf .agent-os/
mkdir -p .agent-os/
rsync -av agent-os-enhanced/universal/ .agent-os/
```

---

## 🎓 Best Practices

1. **Always sync from `universal/`** - Never from `.agent-os/`
2. **Use version tracking** - Maintain `.agent-os/VERSION.txt`
3. **Test after updates** - Verify MCP tools work
4. **Automate updates** - Use update scripts to prevent mistakes
5. **Backup before updates** - Keep previous version for rollback
6. **Review changelogs** - Check for breaking changes
7. **Rebuild indexes** - Always rebuild RAG after content changes

---

## 🔐 Security Considerations

- **Source validation**: Verify you're syncing from the official agent-os-enhanced repo
- **Content inspection**: Review major updates before applying
- **Access control**: Restrict who can run update scripts
- **Audit trail**: Log all updates (use VERSION.txt)

---

## 📞 Need Help?

If you encounter issues:
1. Check this guide for common mistakes
2. Review the changelog in agent-os-enhanced repo
3. Verify you're syncing from `universal/` not `.agent-os/`
4. Check file watchers are running (auto-rebuild)
5. Try a clean reinstall from `universal/`

---

**Remember:** 
- ✅ Source: `universal/` directory
- ❌ Not: `.agent-os/` directory

Always sync from the canonical source content, not build artifacts!
