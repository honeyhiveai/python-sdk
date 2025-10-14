# Agent OS Update Procedures Standard

**Standards for updating Agent OS content in consuming projects**

---

## 🎯 Purpose

This document establishes standards for safely and correctly updating Agent OS in consuming projects. This includes:
- **Content updates**: Standards, workflows, and documentation
- **Server updates**: MCP server software and dependencies

Following these standards prevents common mistakes that can corrupt local installations.

---

## 📦 Update Types

### Content Updates

Updating standards, workflows, and usage documentation stored in `.agent-os/`:
- Source: `universal/` directory
- Destination: `.agent-os/` directory
- Method: rsync
- Requires: RAG index rebuild

### Server Updates

Updating the MCP server software itself:
- Source: `mcp_server/` directory or PyPI package
- Method: pip install
- Requires: Server restart

**Both types may be needed** when updating to a new version.

---

## 📍 Source Standards

### Content Source Location

**STANDARD:** All Agent OS content MUST be synced from the `universal/` directory in the agent-os-enhanced repository.

```
agent-os-enhanced/
└── universal/          ← SYNC FROM HERE
    ├── standards/
    ├── usage/
    └── workflows/
```

### Prohibited Source Locations

**PROHIBITED:** Syncing from the `.agent-os/` directory is FORBIDDEN.

```
agent-os-enhanced/
└── .agent-os/          ← NEVER SYNC FROM HERE
    ├── standards/
    ├── rag_index/
    └── .mcp_state/
```

**Rationale:**
- `.agent-os/` is a build artifact directory
- Contains processed files and local state
- Not version-controlled source content
- May include development-only or test data

### Server Source Location

**STANDARD:** MCP server software MUST be obtained from:
- **Recommended**: PyPI package (`pip install agent-os-mcp`)
- **Development**: Source repository (`mcp_server/` directory)
- **Prohibited**: Copying from another project's installation

```
agent-os-enhanced/
├── mcp_server/              ← Server source code
│   ├── agent_os_rag.py
│   ├── workflow_engine.py
│   ├── requirements.txt     ← Server dependencies
│   └── ...
└── universal/               ← Content source
```

---

## 🔄 Update Frequency Standard

### Regular Updates

**STANDARD:** Projects SHOULD update Agent OS content:
- **Minimum**: Once per quarter
- **Recommended**: Monthly or when new features are needed
- **Critical**: Immediately for security fixes

### Update Triggers

Projects MUST update when:
- Security vulnerabilities are disclosed
- Breaking changes affect project functionality
- New workflow features are required
- Bugs in current version impact operations

---

## 📋 Update Process Standard

### Pre-Update Requirements

Before updating, projects MUST:

1. **Verify Source Repository**
   ```bash
   cd /path/to/agent-os-enhanced
   git remote -v
   # Verify origin points to official repository
   ```

2. **Pull Latest Changes**
   ```bash
   git pull origin main
   git log -1  # Note commit hash for tracking
   ```

3. **Create Backup** (Recommended)
   ```bash
   cp -r .agent-os/ .agent-os.backup.$(date +%Y%m%d)
   ```

### Update Execution Standard

**STANDARD:** Updates MUST use rsync with these parameters:

```bash
# Standards (required)
rsync -av --delete \
    /path/to/agent-os-enhanced/universal/standards/ \
    .agent-os/standards/

# Usage docs (required)
rsync -av --delete \
    /path/to/agent-os-enhanced/universal/usage/ \
    .agent-os/usage/

# Workflows (optional)
rsync -av --delete \
    /path/to/agent-os-enhanced/universal/workflows/ \
    .agent-os/workflows/
```

**Required Flags:**
- `-a`: Archive mode (preserves permissions, timestamps)
- `-v`: Verbose (logs operations)
- `--delete`: Removes obsolete files

### Post-Update Requirements

After updating content, projects MUST:

1. **Wait for Auto-Index Update**
   - File watcher detects changes automatically
   - Index rebuilds incrementally (10-30 seconds)
   - **No server restart needed** for content updates
   - Monitor logs: "👀 File change detected, rebuilding RAG index..."

2. **Verify Update**
   ```bash
   # Wait for index rebuild to complete, then test
   # (Usually 10-30 seconds after rsync completes)
   
   mcp_agent-os-rag_search_standards(
       query="testing standards",
       n_results=3
   )
   ```

3. **Update Version Tracking**
   ```bash
   echo "Updated: $(date +%Y-%m-%d)" >> .agent-os/VERSION.txt
   echo "Commit: $(cd /path/to/agent-os-enhanced && git rev-parse --short HEAD)" >> .agent-os/VERSION.txt
   ```

**Note:** Manual index rebuild only needed if file watcher is disabled or troubleshooting.

### MCP Server Update Requirements

After updating MCP server software, projects MUST:

1. **Restart MCP Server**
   ```bash
   # Stop current server
   pkill -f "mcp.*agent-os-rag"
   
   # Restart via Cursor IDE or process manager
   ```

2. **Verify Server Version**
   ```bash
   pip show agent-os-mcp  # Check installed version
   ```

3. **Test New Features**
   - Verify new tools appear in Cursor
   - Test that existing workflows still work
   - Check for breaking changes

4. **Track Server Version**
   ```bash
   cat > .agent-os/SERVER_VERSION.txt << EOF
   Server Version: $(pip show agent-os-mcp | grep Version | awk '{print $2}')
   Updated: $(date +"%Y-%m-%d")
   EOF
   ```

---

## 🚨 Prohibited Actions

### FORBIDDEN Operations

The following actions are PROHIBITED:

1. **Syncing from .agent-os directory**
   ```bash
   # ❌ FORBIDDEN
   rsync -av agent-os-enhanced/.agent-os/ .agent-os/
   ```

2. **Manual file copying without rsync**
   ```bash
   # ❌ FORBIDDEN - Doesn't preserve structure
   cp -r agent-os-enhanced/universal/* .agent-os/
   ```

3. **Partial updates without tracking**
   ```bash
   # ❌ FORBIDDEN - Leads to version conflicts
   rsync -av agent-os-enhanced/universal/standards/testing/ .agent-os/standards/testing/
   # (missing other standards)
   ```

4. **Syncing state directories**
   ```bash
   # ❌ FORBIDDEN - Corrupts local state
   rsync -av agent-os-enhanced/.agent-os/rag_index/ .agent-os/rag_index/
   rsync -av agent-os-enhanced/.agent-os/.mcp_state/ .agent-os/.mcp_state/
   ```

---

## 🔒 Protection Standards

### Custom Content Protection

**STANDARD:** Projects with custom workflows/standards MUST use exclusions:

```bash
rsync -av --delete \
    --exclude="workflows/custom_workflow/" \
    --exclude="standards/custom_standards/" \
    /path/to/agent-os-enhanced/universal/ \
    .agent-os/
```

### State File Protection

**STANDARD:** Update scripts MUST always exclude:
- `rag_index/` - Local vector database
- `.mcp_state/` - MCP server state
- `scripts/` - Use from mcp_server instead
- `*.log` - Local log files

### Rollback Capability

**STANDARD:** Production systems MUST maintain rollback capability:

```bash
# Before update
BACKUP_DIR=".agent-os.backup.$(date +%Y%m%d_%H%M%S)"
cp -r .agent-os/ "$BACKUP_DIR"

# Keep last 3 backups
ls -dt .agent-os.backup.* | tail -n +4 | xargs rm -rf
```

---

## 📊 Version Tracking Standard

### Version File Requirement

**STANDARD:** Projects MUST maintain `.agent-os/VERSION.txt`:

```txt
Agent OS Content Version

Repository: https://github.com/honeyhiveai/agent-os-enhanced
Last Updated: 2025-10-06 14:30:00
Source Commit: abc123def456
Updated By: deployment-script
Previous Version: v1.2.3
Current Version: v1.3.0
Notes: Updated for horizontal scaling features
```

### Update Log Requirement

**STANDARD:** Projects SHOULD maintain `.agent-os/UPDATE_LOG.txt`:

```txt
2025-10-06 14:30:00 | abc123def | Updated to v1.3.0 (horizontal scaling)
2025-09-15 10:15:00 | def456abc | Updated to v1.2.2 (config.json paths)
2025-09-01 16:45:00 | 123abc456 | Updated to v1.2.0 (workflow metadata)
```

---

## 🔍 Validation Standard

### Pre-Update Validation

**STANDARD:** Update scripts MUST validate source before syncing:

```bash
# Validate source exists
if [ ! -d "$SOURCE/universal/standards" ]; then
    echo "ERROR: Invalid source directory"
    exit 1
fi

# Validate not syncing from .agent-os
if [[ "$SOURCE" == *".agent-os"* ]]; then
    echo "ERROR: Cannot sync from .agent-os directory"
    exit 1
fi

# Validate git repository
if [ ! -d "$SOURCE/.git" ]; then
    echo "WARNING: Source is not a git repository"
fi
```

### Post-Update Validation

**STANDARD:** Updates MUST be validated after completion:

```bash
# Check essential directories exist
test -d .agent-os/standards/ || { echo "ERROR: standards missing"; exit 1; }
test -d .agent-os/usage/ || { echo "ERROR: usage missing"; exit 1; }

# Check MCP can query
mcp_query_result=$(mcp_agent-os-rag_search_standards \
    --query "testing standards" \
    --n_results 1)

if [ -z "$mcp_query_result" ]; then
    echo "ERROR: MCP query failed"
    exit 1
fi

echo "✅ Update validated successfully"
```

---

## 🎓 Training Standard

### Required Knowledge

Teams MUST understand:
1. Difference between `universal/` (source) and `.agent-os/` (build artifact)
2. Why syncing from `.agent-os/` is forbidden
3. How to verify source repository authenticity
4. Rollback procedures for failed updates

### Documentation Requirement

**STANDARD:** Projects MUST document their update process:

```markdown
# Our Agent OS Update Process

## Schedule
- Monthly automated updates (1st of month)
- Emergency updates as needed

## Responsible Team
- Primary: DevOps team
- Backup: Platform team

## Process
1. Run ./scripts/update-agent-os.sh
2. Verify with test query
3. Update VERSION.txt
4. Monitor for 24 hours

## Rollback
1. Stop MCP server
2. Restore from .agent-os.backup.*
3. Restart MCP server
```

---

## 🔧 Automation Standard

### Update Script Requirements

**STANDARD:** Automated update scripts MUST:

1. **Validate source location**
2. **Create backups**
3. **Use correct rsync flags**
4. **Rebuild RAG index**
5. **Log all operations**
6. **Validate success**
7. **Send notifications on failure**

### Example Standard-Compliant Script

```bash
#!/bin/bash
set -euo pipefail

# Configuration
AGENT_OS_REPO="${AGENT_OS_REPO:-/opt/agent-os-enhanced}"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_FILE="$PROJECT_ROOT/.agent-os/UPDATE_LOG.txt"

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Validation
validate_source() {
    if [ ! -d "$AGENT_OS_REPO/universal" ]; then
        log "ERROR: Invalid source - universal/ not found"
        exit 1
    fi
    
    if [[ "$AGENT_OS_REPO" == *".agent-os"* ]]; then
        log "ERROR: Source contains .agent-os - forbidden"
        exit 1
    fi
}

# Backup
create_backup() {
    local backup_dir=".agent-os.backup.$(date +%Y%m%d_%H%M%S)"
    log "Creating backup: $backup_dir"
    cp -r "$PROJECT_ROOT/.agent-os" "$PROJECT_ROOT/$backup_dir"
}

# Update
perform_update() {
    log "Syncing from $AGENT_OS_REPO/universal/"
    
    rsync -av --delete \
        --exclude="rag_index/" \
        --exclude=".mcp_state/" \
        "$AGENT_OS_REPO/universal/standards/" "$PROJECT_ROOT/.agent-os/standards/"
    
    rsync -av --delete \
        "$AGENT_OS_REPO/universal/usage/" "$PROJECT_ROOT/.agent-os/usage/"
    
    rsync -av --delete \
        "$AGENT_OS_REPO/universal/workflows/" "$PROJECT_ROOT/.agent-os/workflows/"
}

# Main
main() {
    log "Starting Agent OS update"
    validate_source
    create_backup
    perform_update
    log "Update complete - commit: $(cd "$AGENT_OS_REPO" && git rev-parse --short HEAD)"
}

main
```

---

## 📈 Monitoring Standard

### Update Metrics

**STANDARD:** Projects SHOULD track:
- Update frequency
- Update duration
- Failure rate
- Rollback count

### Alert Conditions

**STANDARD:** Projects MUST alert on:
- Update failures
- RAG index rebuild failures
- Post-update validation failures
- MCP server restart failures

---

## 🆘 Incident Response Standard

### Update Failure Response

When an update fails:

1. **DO NOT proceed with partial update**
2. **Restore from backup immediately**
3. **Document failure cause**
4. **Review validation checks**
5. **Test fix in non-production first**

### Corruption Recovery

If content is corrupted:

```bash
# 1. Stop MCP server
pkill -f "mcp.*agent-os-rag" || true

# 2. Remove corrupted content
rm -rf .agent-os/

# 3. Clean reinstall from source
mkdir -p .agent-os/
rsync -av /path/to/agent-os-enhanced/universal/ .agent-os/

# 4. Rebuild RAG index
python -m agent_os.scripts.build_rag_index

# 5. Restart MCP server
# (restart via your process manager)
```

---

## ✅ Compliance Checklist

Before marking an update as complete, verify:

- [ ] Synced from `universal/` directory (not `.agent-os/`)
- [ ] Used rsync with `-av --delete` flags
- [ ] Excluded state directories (rag_index, .mcp_state)
- [ ] Protected custom workflows/standards
- [ ] Created backup before update
- [ ] Rebuilt RAG index after update
- [ ] Validated with test query
- [ ] Updated VERSION.txt
- [ ] Logged update in UPDATE_LOG.txt
- [ ] Tested workflow execution (if applicable)

---

**This is a standard document. All consuming projects MUST follow these procedures when updating Agent OS content.**
