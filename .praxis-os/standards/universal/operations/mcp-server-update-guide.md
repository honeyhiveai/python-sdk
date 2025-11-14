# MCP Server Update Guide

**How to update the prAxIs OS MCP server software in consuming projects**

**Keywords for search**: MCP server update, update MCP server, upgrade MCP server, server software update, MCP Python code update, server restart, dependency update

---

## 🚨 Quick Reference (TL;DR)

**Two types of updates:**

1. **Content Updates** (standards/workflows) → Use `praxis_os_upgrade_v1` workflow
   - No server restart needed
   - RAG index rebuilds automatically

2. **MCP Server Updates** (Python code) → Covered in this guide
   - ⚠️ **Requires server restart**
   - May have breaking changes
   - Use `praxis_os_upgrade_v1` workflow (recommended) or manual method

**Recommended: Use the workflow for both types**

---

## Questions This Answers

- "How do I update the MCP server software?"
- "Do I need to restart the MCP server?"
- "What's the difference between content and server updates?"
- "How do I update MCP server dependencies?"
- "When should I update the MCP server?"
- "How do I test MCP server updates?"
- "What if the server update breaks something?"
- "How do I roll back an MCP server update?"

---

## 📋 Two Types of Updates

### 1. Content Updates (Covered in standards/installation/update-procedures.md)

Updating standards, workflows, and documentation:
```bash
rsync -av praxis-os/universal/ .praxis-os/
```

**Requirements:**
- ✅ File watcher auto-detects changes
- ✅ RAG index rebuilds automatically (~10-30 seconds)
- ✅ **No server restart needed**

### 2. Server Updates (THIS GUIDE)

Updating the MCP server software itself:
```bash
# Copy updated Python code from source
cp -r /path/to/praxis-os/mcp_server .praxis-os/

# Update dependencies
.praxis-os/venv/bin/pip install -r .praxis-os/mcp_server/requirements.txt --upgrade
```

**Requirements:**
- ⚠️ **Server restart required** (`pkill -f "mcp.*agent-os-rag"`)
- ⚠️ May have breaking API changes
- ⚠️ Test thoroughly before deploying

---

## 🔍 What is the MCP Server?

The **MCP server** is the Python application that:
- Provides MCP tools to Cursor IDE
- Runs RAG semantic search
- Manages workflow state
- Enforces phase gating

**Location in source repo:**
```
praxis-os/
└── mcp_server/              ← The server software
    ├── praxis_os_rag.py      ← Main server
    ├── workflow_engine.py   ← Workflow logic
    ├── rag_engine.py        ← RAG search
    ├── requirements.txt     ← Dependencies
    └── ...
```

---

## 🔄 When to Update the MCP Server

### Update Triggers

Update the MCP server when:
- ✅ New MCP tools are added (e.g., `get_task` in v1.3.0)
- ✅ Bug fixes in server code
- ✅ Security vulnerabilities in dependencies
- ✅ Performance improvements
- ✅ Breaking changes that affect your workflows

### Check Current Version

```bash
# If installed as package
pip show agent-os-mcp

# If running from source
cd /path/to/praxis-os/mcp_server
git log -1 --oneline
```

---

## 📦 Installation Method

prAxIs OS uses a **copy-based installation** where `mcp_server/` from the source repository is copied to your project's `.praxis-os/mcp_server/` directory.

**Architecture:**
```
praxis-os/              Your Project/
├── mcp_server/        ──────►  └── .praxis-os/
    └── ...                         └── mcp_server/  (copied)
```

**Why copy instead of pip/symlink?**
- ✅ No external package dependencies
- ✅ Explicit version control
- ✅ Works offline
- ✅ Simple, predictable installation

### Getting Latest MCP Server Code

```bash
cd /path/to/praxis-os

# Pull latest changes from repository
git pull origin main

# Note the commit hash for tracking
git log -1 --oneline
```

---

## 🔄 Update Process

### Step 1: Check Compatibility

**Before updating, check for breaking changes:**

```bash
# Read the changelog in the source repo
cat /path/to/praxis-os/mcp_server/CHANGELOG.md

# Look for "Breaking Changes" or "Changed" sections
# Example: v1.3.0 changed get_current_phase response structure
```

### Step 2: Backup Current Installation (Recommended)

```bash
# From your project root
cd /path/to/your-project

# Backup current MCP server
cp -r .praxis-os/mcp_server .praxis-os/mcp_server.backup

# Record current version
echo "Backup created: $(date)" >> .praxis-os/UPDATE_LOG.txt
```

### Step 3: Copy Updated MCP Server

```bash
# Copy from source to your project
cp -r /path/to/praxis-os/mcp_server .praxis-os/

# Verify copy completed
ls -la .praxis-os/mcp_server/
```

### Step 4: Update Dependencies

```bash
# Update Python dependencies in the isolated venv
.praxis-os/venv/bin/pip install -r .praxis-os/mcp_server/requirements.txt --upgrade

# Verify no errors
echo $?  # Should output: 0
```

### Step 5: Restart MCP Server

**Critical:** The MCP server **MUST be restarted** for server code changes to take effect.

```bash
# Find and stop the running server
pkill -f "mcp.*agent-os-rag" || pkill -f "uvx.*mcp"

# Restart via Cursor IDE
# 1. Cursor > Settings > MCP Servers
# 2. Find "agent-os-rag"
# 3. Click "Restart"

# Or restart Cursor completely
```

**Why restart is required for server updates:**
- Python code is loaded at server startup
- Changes to `.py` files require process restart
- File watchers only monitor **content files**, not server code

**Note:** Content updates (`.md` files) do **NOT** require restart - file watchers handle those automatically.

### Step 6: Verify Update

**Check server starts without errors:**
```bash
# Check Cursor MCP logs
# Cursor → Settings → MCP Servers → agent-os-rag → View Logs

# Should see:
# ✅ MCP server started successfully
# ✅ RAG engine initialized
# ✅ Workflow engine loaded
# ✅ Tools registered: X tools
```

**Test with a simple query:**
```python
# In Cursor chat
mcp_agent-os-rag_search_standards(
    query="testing standards",
    n_results=1
)

# Should return results without errors
```

**Verify new features (if applicable):**
- Check for new tools in Cursor's MCP tool list
- Test that existing workflows still work
- Confirm no breaking changes affect your project

---

## 🔧 Dependency Updates

### Updating Python Dependencies

**Always use the isolated venv:**

```bash
# From your project root
cd /path/to/your-project

# Check for outdated packages in prAxIs OS venv
.praxis-os/venv/bin/pip list --outdated

# Update all from requirements.txt
.praxis-os/venv/bin/pip install -r .praxis-os/mcp_server/requirements.txt --upgrade

# Restart MCP server after updates
pkill -f "mcp.*agent-os-rag"
```

### Security Updates

```bash
# Check for security vulnerabilities
.praxis-os/venv/bin/pip-audit

# Or use safety
.praxis-os/venv/bin/pip install safety
.praxis-os/venv/bin/safety check

# Update vulnerable packages immediately
.praxis-os/venv/bin/pip install --upgrade <package-name>

# Restart MCP server
pkill -f "mcp.*agent-os-rag"
```

---

## ⚠️ Breaking Changes

### v1.3.0 Breaking Changes

**`get_current_phase` Response Changed:**

**Before (v1.2.3):**
```json
{
  "phase_content": {
    "tasks": [
      {
        "task_number": 1,
        "content": "...",  // Full content included
        "steps": [...]
      }
    ]
  }
}
```

**After (v1.3.0):**
```json
{
  "phase_content": {
    "tasks": [
      {
        "task_number": 1,
        "task_name": "...",
        "task_file": "..."
        // No content - use get_task tool
      }
    ]
  }
}
```

**Migration Required:**
```python
# Old code (v1.2.3)
phase = get_current_phase(session_id)
for task in phase['phase_content']['tasks']:
    execute(task['steps'])  # Direct access

# New code (v1.3.0)
phase = get_current_phase(session_id)
for task_meta in phase['phase_content']['tasks']:
    task = get_task(session_id, phase['current_phase'], task_meta['task_number'])
    execute(task['steps'])  # Must fetch task first
```

---

## 🎯 Version-Specific Considerations

### v1.3.0 → Latest

- New `get_task` tool available
- `get_current_phase` returns task metadata only
- Update any code that assumes tasks have full content

### v1.2.x → v1.3.0

- **Breaking:** Update workflow execution code to use `get_task`
- **New:** Horizontal scaling enforced (one task at a time)
- **Benefit:** Token-efficient task execution

### v1.1.x → v1.2.x

- Workflow metadata support added
- RAG indexes workflows directory
- File watcher for workflow changes

---

## 🔍 Verification Checklist

After updating, verify:

- [ ] Server restarts successfully
- [ ] No import errors in logs
- [ ] Can query standards: `pos_search_project(content_type="standards", query="test")`
- [ ] Can start workflows: `start_workflow(...)`
- [ ] New tools appear (if applicable)
- [ ] Existing workflows still work
- [ ] RAG index rebuilds successfully

---

## 🆘 Troubleshooting

### Issue: Server Won't Start After Update

**Symptoms:** MCP server fails to start, Cursor shows connection error

**Causes:**
- Incompatible dependency versions
- Python version mismatch
- Corrupted installation
- Copy incomplete

**Fix:**
```bash
# 1. Check Python version (requires 3.9+)
.praxis-os/venv/bin/python --version

# 2. Verify copy completed
ls -la .praxis-os/mcp_server/
# Should see __init__.py, praxis_os_rag.py, etc.

# 3. Reinstall dependencies in isolated venv
.praxis-os/venv/bin/pip install -r .praxis-os/mcp_server/requirements.txt --force-reinstall

# 4. Check for import errors
.praxis-os/venv/bin/python -c "from mcp_server import workflow_engine; print('OK')"

# 5. Restart MCP server
pkill -f "mcp.*agent-os-rag"
```

### Issue: Import Errors After Update

**Symptoms:** `ModuleNotFoundError` or `ImportError`

**Fix:**
```bash
# 1. Verify mcp_server was copied completely
diff -r /path/to/praxis-os/mcp_server .praxis-os/mcp_server
# Should show no differences (or only version changes)

# 2. Reinstall dependencies
.praxis-os/venv/bin/pip install -r .praxis-os/mcp_server/requirements.txt --force-reinstall

# 3. Check specific package
.praxis-os/venv/bin/pip install --force-reinstall lancedb

# 4. Restart server
pkill -f "mcp.*agent-os-rag"
```

### Issue: New Tools Not Appearing

**Symptoms:** Updated server but new tools don't appear

**Fix:**
```bash
# 1. Verify you copied the new version
ls -la .praxis-os/mcp_server/
grep -r "new_tool_name" .praxis-os/mcp_server/

# 2. Hard restart Cursor
# Quit Cursor completely, then reopen

# 3. Check MCP server logs
# Cursor > Settings > MCP Servers > agent-os-rag > View Logs
# Look for tool registration messages

# 4. Verify PYTHONPATH in .cursor/mcp.json
cat .cursor/mcp.json | grep PYTHONPATH
# Should be: "${workspaceFolder}/.praxis-os"
```

### Issue: Changes Not Taking Effect

**Symptoms:** Made updates but server behaves the same

**Causes:**
- Old code still in `.praxis-os/mcp_server/`
- Server not restarted
- Wrong code copied

**Fix:**
```bash
# 1. Verify what was copied
diff -r /path/to/praxis-os/mcp_server .praxis-os/mcp_server

# 2. Force re-copy
rm -rf .praxis-os/mcp_server
cp -r /path/to/praxis-os/mcp_server .praxis-os/

# 3. Restart server (CRITICAL)
pkill -f "mcp.*agent-os-rag"

# 4. Verify in logs
# Cursor > Settings > MCP Servers > agent-os-rag > View Logs
# Should show server restarted with new code
```

---

## 🔐 Production Deployment

### Staged Rollout

```bash
# 1. Development environment
cd /path/to/praxis-os
git pull origin main
cp -r mcp_server /path/to/dev-project/.praxis-os/
# Test thoroughly
# Restart MCP server: pkill -f "mcp.*agent-os-rag"

# 2. Staging environment
cd /path/to/praxis-os
git checkout v1.3.0  # Pin to specific version
cp -r mcp_server /path/to/staging-project/.praxis-os/
# Run integration tests
# Restart MCP server

# 3. Production environment (same version as staging)
git checkout v1.3.0
cp -r mcp_server /path/to/production-project/.praxis-os/
# Monitor for issues
# Restart MCP server
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy MCP server from source
COPY mcp_server/ /app/.praxis-os/mcp_server/

# Install dependencies
COPY mcp_server/requirements.txt /app/
RUN python -m venv /app/.praxis-os/venv && \
    /app/.praxis-os/venv/bin/pip install -r requirements.txt

# Copy content (standards, workflows, usage)
COPY .praxis-os/standards/ /app/.praxis-os/standards/
COPY .praxis-os/usage/ /app/.praxis-os/usage/
COPY .praxis-os/workflows/ /app/.praxis-os/workflows/

# Set Python path
ENV PYTHONPATH=/app/.praxis-os

# Run server
CMD ["/app/.praxis-os/venv/bin/python", "-m", "mcp_server"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: mcp-server
        image: your-registry/agent-os-mcp:v1.3.0  # Built from Dockerfile above
        env:
        - name: PYTHONPATH
          value: "/app/.praxis-os"
        - name: AGENT_OS_BASE_PATH
          value: "/app/.praxis-os"
```

---

## 📊 Version Tracking

### Track Server Version

Create `.praxis-os/SERVER_VERSION.txt`:

```txt
MCP Server Version Tracking

Server Version: 1.3.0
Installation Method: pip package
Python Version: 3.11.5
Last Updated: 2025-10-06
Updated By: deployment-script

Dependencies:
- lancedb==0.5.0
- sentence-transformers==2.2.2
- fastmcp==0.2.0

Notes: Updated for horizontal scaling support
```

### Automated Version Tracking

```bash
#!/bin/bash
cat > .praxis-os/SERVER_VERSION.txt << EOF
MCP Server Version Tracking

Server Version: $(pip show agent-os-mcp | grep Version | awk '{print $2}')
Installation Method: pip package
Python Version: $(python --version | awk '{print $2}')
Last Updated: $(date +"%Y-%m-%d %H:%M:%S")
Updated By: $(whoami)

Dependencies:
$(pip freeze | grep -E "lancedb|sentence-transformers|fastmcp")

Notes: Automated update
EOF
```

---

## 🔄 Combined Update (Content + Server)

### Update Script for Both

```bash
#!/bin/bash
set -e

AGENT_OS_REPO="/path/to/praxis-os"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔄 Updating prAxIs OS (Content + Server)..."

# 1. Pull latest source
cd "$AGENT_OS_REPO"
git pull origin main
COMMIT=$(git rev-parse --short HEAD)

# 2. Update MCP server (copy-based)
echo "📦 Updating MCP server..."
rm -rf "$PROJECT_ROOT/.praxis-os/mcp_server"
cp -r "$AGENT_OS_REPO/mcp_server" "$PROJECT_ROOT/.praxis-os/"

# 3. Update dependencies in isolated venv
echo "📦 Updating dependencies..."
"$PROJECT_ROOT/.praxis-os/venv/bin/pip" install -r "$PROJECT_ROOT/.praxis-os/mcp_server/requirements.txt" --upgrade

# 4. Update content (file watcher will auto-rebuild index)
echo "📦 Updating content (safe-upgrade protects custom content)..."
python "$AGENT_OS_REPO/scripts/safe-upgrade.py" \
  --source "$AGENT_OS_REPO" \
  --target "$PROJECT_ROOT/.praxis-os"

# 5. Restart server
echo "🔄 Restarting MCP server..."
pkill -f "mcp.*agent-os-rag" || true
# Server will auto-restart via Cursor

# 6. Track versions
cat > "$PROJECT_ROOT/.praxis-os/UPDATE_LOG.txt" << EOF
Last Update: $(date +"%Y-%m-%d %H:%M:%S")
Source Commit: $COMMIT
MCP Server: Copied from $AGENT_OS_REPO
Content: Synced from universal/
EOF

echo "✅ Update complete!"
echo "💡 Verify by testing: pos_search_project('test')"
echo "📋 Check logs: Cursor > Settings > MCP Servers > agent-os-rag > View Logs"
```

---

## When to Query This Guide

This guide is most valuable when:

1. **Updating MCP Server Software**
   - Situation: Need to update Python server code
   - Query: `pos_search_project(content_type="standards", query="how to update MCP server")`

2. **Server Restart Questions**
   - Situation: Unsure if restart needed after update
   - Query: `pos_search_project(content_type="standards", query="MCP server restart required")`

3. **Dependency Updates**
   - Situation: Need to update server dependencies
   - Query: `pos_search_project(content_type="standards", query="update MCP server dependencies")`

4. **Breaking Changes**
   - Situation: Checking for breaking changes in update
   - Query: `pos_search_project(content_type="standards", query="MCP server breaking changes")`

5. **Rollback Scenarios**
   - Situation: Need to roll back failed server update
   - Query: `pos_search_project(content_type="standards", query="rollback MCP server update")`

### Query by Use Case

| Use Case | Example Query |
|----------|---------------|
| Server update | `pos_search_project(content_type="standards", query="update MCP server")` |
| Restart required | `pos_search_project(content_type="standards", query="MCP server restart")` |
| Dependencies | `pos_search_project(content_type="standards", query="MCP server dependencies")` |
| Testing updates | `pos_search_project(content_type="standards", query="test MCP server update")` |
| Rollback | `pos_search_project(content_type="standards", query="rollback MCP server")` |

---

## Cross-References and Related Guides

**Update Standards:**
- `standards/installation/update-procedures.md` - Content update procedures
  → `pos_search_project(content_type="standards", query="prAxIs OS update standards")`

**Workflows:**
- `workflows/praxis_os_upgrade_v1/` - Automated upgrade workflow (handles both content and server)
  → `pos_search_project(content_type="standards", query="praxis os upgrade workflow")`

**MCP Documentation:**
- `usage/mcp-usage-guide.md` - How to use MCP tools
  → `pos_search_project(content_type="standards", query="MCP tools guide")`
- `mcp_server/CHANGELOG.md` - Server version history

**Query workflow:**
1. **Before Update**: `pos_search_project(content_type="standards", query="how to update MCP server")` → Learn process
2. **Check Changes**: Read CHANGELOG.md for breaking changes
3. **Execute**: Use `praxis_os_upgrade_v1` workflow (recommended) or manual method
4. **Validate**: Test MCP tools after restart
5. **Troubleshoot**: `pos_search_project(content_type="standards", query="MCP server update issues")` if needed

---

## 🎓 Best Practices

1. **Test before deploying** - Update dev/staging first
2. **Read changelogs** - Check for breaking changes
3. **Backup before updating** - Keep rollback option
4. **Restart server** - Always restart after updating
5. **Verify tools** - Test that new features work
6. **Track versions** - Maintain SERVER_VERSION.txt
7. **Monitor logs** - Watch for errors after update

---

## 🔗 Quick Reference

```bash
# Get latest source
cd /path/to/praxis-os && git pull origin main

# Copy to your project
cp -r /path/to/praxis-os/mcp_server /path/to/your-project/.praxis-os/

# Update dependencies
/path/to/your-project/.praxis-os/venv/bin/pip install -r /path/to/your-project/.praxis-os/mcp_server/requirements.txt --upgrade

# Restart server
pkill -f "mcp.*agent-os-rag"  # Cursor will auto-restart

# Verify
pos_search_project(content_type="standards", query="test")  # Should work without errors
```

---

**Remember:**
- **Content updates**: Copy from `universal/` → `.praxis-os/`
- **Server updates**: Copy from `mcp_server/` → `.praxis-os/mcp_server/`
- **Always restart** server after code changes: `pkill -f "mcp.*agent-os-rag"`
- **Verify in logs** after restart (Cursor → Settings → MCP Servers → View Logs)
- **Test thoroughly** before production deployment
