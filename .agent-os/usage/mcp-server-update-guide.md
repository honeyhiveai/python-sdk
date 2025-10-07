# MCP Server Update Guide

**How to update the Agent OS MCP server software in consuming projects**

---

## 📋 Two Types of Updates

### 1. Content Updates (Covered in agent-os-update-guide.md)

Updating standards, workflows, and documentation:
```bash
rsync -av agent-os-enhanced/universal/ .agent-os/
```

**Requirements:**
- ✅ File watcher auto-detects changes
- ✅ RAG index rebuilds automatically (~10-30 seconds)
- ✅ **No server restart needed**

### 2. Server Updates (THIS GUIDE)

Updating the MCP server software itself:
```bash
# Update Python code and dependencies
pip install --upgrade agent-os-mcp
```

**Requirements:**
- ⚠️ **Server restart required**
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
agent-os-enhanced/
└── mcp_server/              ← The server software
    ├── agent_os_rag.py      ← Main server
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
cd /path/to/agent-os-enhanced/mcp_server
git log -1 --oneline
```

---

## 📦 Installation Methods

### Method 1: Package Installation (Recommended for Consumers)

If you installed the MCP server as a Python package:

```bash
# Update to latest version
pip install --upgrade agent-os-mcp

# Or specific version
pip install agent-os-mcp==1.3.0

# Verify installation
pip show agent-os-mcp
```

### Method 2: Source Installation (For Development)

If you're running directly from the agent-os-enhanced repo:

```bash
cd /path/to/agent-os-enhanced

# Pull latest changes
git pull origin main

# Update dependencies
pip install -r mcp_server/requirements.txt --upgrade

# Verify
python -c "from mcp_server import workflow_engine; print('OK')"
```

### Method 3: Editable Installation (For Contributors)

If you're developing against the MCP server:

```bash
cd /path/to/agent-os-enhanced

# Pull latest changes
git pull origin main

# Reinstall in editable mode
pip install -e ./mcp_server

# Verify
pip show agent-os-mcp
```

---

## 🔄 Update Process

### Step 1: Check Compatibility

**Before updating, check for breaking changes:**

```bash
# Read the changelog
cat /path/to/agent-os-enhanced/mcp_server/CHANGELOG.md

# Look for "Breaking Changes" or "Changed" sections
# Example: v1.3.0 changed get_current_phase response structure
```

### Step 2: Backup Current Setup (Recommended)

```bash
# Backup virtual environment
cp -r venv/ venv.backup/

# Or just record current versions
pip freeze > requirements.backup.txt
```

### Step 3: Update the Server

**For Package Installation:**
```bash
pip install --upgrade agent-os-mcp
```

**For Source Installation:**
```bash
cd /path/to/agent-os-enhanced
git pull origin main
pip install -r mcp_server/requirements.txt --upgrade
```

### Step 4: Restart MCP Server

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

### Step 5: Verify Update

```bash
# Test with a simple query
mcp_agent-os-rag_search_standards(
    query="testing standards",
    n_results=1
)

# Check for new tools (e.g., get_task in v1.3.0)
# They should appear in Cursor's MCP tool list
```

---

## 🔧 Dependency Updates

### Updating Python Dependencies

```bash
# Check for outdated packages
pip list --outdated

# Update specific packages
pip install --upgrade lancedb sentence-transformers

# Or update all from requirements.txt
pip install -r mcp_server/requirements.txt --upgrade
```

### Security Updates

```bash
# Check for security vulnerabilities
pip-audit  # Or use safety: pip install safety && safety check

# Update vulnerable packages immediately
pip install --upgrade <package-name>
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
- [ ] Can query standards: `search_standards("test")`
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

**Fix:**
```bash
# 1. Check Python version (requires 3.9+)
python --version

# 2. Reinstall in clean environment
python -m venv venv.new
source venv.new/bin/activate
pip install agent-os-mcp

# 3. Verify installation
python -c "from mcp_server import agent_os_rag; print('OK')"
```

### Issue: Import Errors After Update

**Symptoms:** `ModuleNotFoundError` or `ImportError`

**Fix:**
```bash
# Reinstall dependencies
pip install -r mcp_server/requirements.txt --force-reinstall

# Or specific package
pip install --force-reinstall lancedb
```

### Issue: New Tools Not Appearing

**Symptoms:** Updated to v1.3.0 but `get_task` tool not available

**Fix:**
```bash
# 1. Verify server version
pip show agent-os-mcp  # Should show 1.3.0+

# 2. Hard restart Cursor
# Quit Cursor completely, then reopen

# 3. Check MCP server logs
# Cursor > Settings > MCP Servers > agent-os-rag > View Logs

# 4. Reinstall if needed
pip install --force-reinstall agent-os-mcp==1.3.0
```

### Issue: Breaking Changes After Update

**Symptoms:** Existing workflows fail after update

**Fix:**
```bash
# 1. Rollback to previous version
pip install agent-os-mcp==1.2.3  # Or restore from backup

# 2. Review migration guide in CHANGELOG
cat mcp_server/CHANGELOG.md

# 3. Update your code to match new API
# (See Breaking Changes section above)

# 4. Test with updated code
# 5. Re-update server when ready
```

---

## 🔐 Production Deployment

### Staged Rollout

```bash
# 1. Development environment
pip install --upgrade agent-os-mcp
# Test thoroughly

# 2. Staging environment
pip install agent-os-mcp==1.3.0
# Run integration tests

# 3. Production environment
pip install agent-os-mcp==1.3.0
# Monitor for issues
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

# Install MCP server
RUN pip install agent-os-mcp==1.3.0

# Copy content
COPY .agent-os/ /app/.agent-os/

# Run server
CMD ["python", "-m", "mcp_server.agent_os_rag"]
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
        image: agent-os-mcp:1.3.0
        env:
        - name: AGENT_OS_BASE_PATH
          value: "/app/.agent-os"
```

---

## 📊 Version Tracking

### Track Server Version

Create `.agent-os/SERVER_VERSION.txt`:

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
cat > .agent-os/SERVER_VERSION.txt << EOF
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

AGENT_OS_REPO="/path/to/agent-os-enhanced"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔄 Updating Agent OS (Content + Server)..."

# 1. Pull latest source
cd "$AGENT_OS_REPO"
git pull origin main
COMMIT=$(git rev-parse --short HEAD)

# 2. Update server software
echo "📦 Updating MCP server..."
pip install -r mcp_server/requirements.txt --upgrade

# 3. Update content
echo "📦 Updating content..."
rsync -av --delete "$AGENT_OS_REPO/universal/standards/" "$PROJECT_ROOT/.agent-os/standards/"
rsync -av --delete "$AGENT_OS_REPO/universal/usage/" "$PROJECT_ROOT/.agent-os/usage/"
rsync -av --delete "$AGENT_OS_REPO/universal/workflows/" "$PROJECT_ROOT/.agent-os/workflows/"

# 4. Restart server
echo "🔄 Restarting MCP server..."
pkill -f "mcp.*agent-os-rag" || true
# Server will auto-restart via Cursor

# 5. Track versions
cat > "$PROJECT_ROOT/.agent-os/SERVER_VERSION.txt" << EOF
Server Version: $(pip show agent-os-mcp 2>/dev/null | grep Version | awk '{print $2}' || echo "source")
Content Commit: $COMMIT
Updated: $(date +"%Y-%m-%d %H:%M:%S")
EOF

echo "✅ Update complete!"
echo "💡 Verify by testing: search_standards('test')"
```

---

## 📚 Related Documentation

- **Content Updates**: `agent-os-update-guide.md`
- **Installation**: Agent OS installation guide
- **MCP Configuration**: Cursor MCP server setup
- **CHANGELOG**: `mcp_server/CHANGELOG.md`

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
# Check current version
pip show agent-os-mcp

# Update server
pip install --upgrade agent-os-mcp

# Update from source
cd agent-os-enhanced && git pull && pip install -r mcp_server/requirements.txt --upgrade

# Restart server
pkill -f "mcp.*agent-os-rag" && # Cursor will auto-restart

# Verify
search_standards("test")
```

---

**Remember:**
- **Content updates**: Sync from `universal/` → `.agent-os/`
- **Server updates**: `pip install --upgrade agent-os-mcp`
- **Always restart** server after updates
- **Test thoroughly** before production deployment
