# Rollback Procedure

Complete guide for rolling back a failed prAxIs OS upgrade.

---

## When to Rollback

### Automatic Rollback Triggers

The workflow automatically rolls back if:

- Phase 2 fails (content upgrade errors)
- Phase 3 fails (dependency install or server restart fails)
- Phase 4 fails (validation fails)

### Manual Rollback Scenarios

You should manually rollback if:

- Upgrade completed but system is unstable
- Critical feature is broken after upgrade
- Need to revert to previous version for any reason

---

## Automatic Rollback

The workflow handles rollback automatically on failures.

### What Happens

1. Workflow detects phase failure
2. Loads backup path from Phase 1 artifacts
3. Stops MCP server
4. Restores all files from backup
5. Restores dependencies from requirements-snapshot.txt
6. Restarts server
7. Verifies health
8. Updates workflow state: status="rolled_back"

### Rollback Time

Target: **< 30 seconds**

---

## Manual Rollback

### Prerequisites

- Backup exists in `.praxis-os/.backups/`
- Know the backup timestamp or path
- Have file system write permissions

### Step-by-Step Procedure

#### 1. Stop MCP Server

```bash
pkill -f "python -m mcp_server"
```

Wait 2-3 seconds for graceful shutdown.

#### 2. Identify Backup

List available backups:

```bash
ls -la .praxis-os/.backups/
```

Choose the most recent backup (format: `YYYY-MM-DD-HHMMSS`).

#### 3. Verify Backup Integrity

```python
from mcp_server.backup_manager import BackupManager
from pathlib import Path

backup_mgr = BackupManager()
backup_path = Path(".praxis-os/.backups/2025-10-08-103045/")

if backup_mgr.verify_backup_integrity(backup_path):
    print("✅ Backup integrity verified")
else:
    print("❌ Backup integrity check failed!")
    # Try another backup
```

#### 4. Restore from Backup

```python
# Restore all files
backup_mgr.restore_from_backup(backup_path)
print("✅ Files restored from backup")
```

This restores:
- `mcp_server/` directory
- `config.json` file
- `standards/` directory
- `usage/` directory
- `workflows/` directory

#### 5. Restore Dependencies

```bash
# If requirements snapshot exists
pip install -r .praxis-os/.backups/2025-10-08-103045/requirements-snapshot.txt
```

#### 6. Restart Server

```bash
python -m mcp_server &
```

Wait 3-5 seconds for server to initialize.

#### 7. Verify Health

```python
from mcp_server.validation_module import ValidationModule

validator = ValidationModule()
health = validator.check_server_health()

if health["healthy"]:
    print("✅ Server is healthy")
else:
    print(f"❌ Server health check failed: {health['error']}")
```

#### 8. Update Workflow State (Optional)

If you were in the middle of an upgrade workflow:

```python
# Load workflow state
state = state_mgr.load_state(session_id)

# Update to rolled back status
state["metadata"]["status"] = "rolled_back"
state["metadata"]["rolled_back_at"] = datetime.now().isoformat()
state["metadata"]["rollback_reason"] = "Manual rollback by user"

# Save state
state_mgr.save_state(state)
```

---

## Verification Checklist

After rollback, verify:

- [ ] Server is running (`pgrep -f "python -m mcp_server"`)
- [ ] Server responds to health checks
- [ ] Tools are registered
- [ ] RAG search works
- [ ] Workflows can be started
- [ ] Browser tools work (if enabled)
- [ ] Version matches expected (check VERSION.txt)

---

## Troubleshooting Rollback

### Rollback Fails with Backup Integrity Error

**Problem:** Backup checksum verification fails

**Solution:**
1. Try previous backup (may be corrupted)
2. Check disk health
3. If multiple backups fail, restore manually:
   ```bash
   # Copy directories manually
   cp -r .praxis-os/.backups/TIMESTAMP/mcp_server .praxis-os/
   cp -r .praxis-os/.backups/TIMESTAMP/standards .praxis-os/
   # etc.
   ```

### Server Won't Start After Rollback

**Problem:** Server fails to start with restored code

**Solution:**
1. Check server logs for errors
2. Verify Python version compatibility
3. Reinstall dependencies:
   ```bash
   pip install -r .praxis-os/mcp_server/requirements.txt
   ```
4. Run post-install steps if needed:
   ```bash
   playwright install chromium
   ```

### Dependencies Conflict

**Problem:** pip install fails with dependency conflicts

**Solution:**
1. Create virtual environment
2. Install from requirements snapshot
3. OR: Install current requirements.txt (may lose exact versions)

---

## Data Preservation

### What is Preserved

During rollback, the following are **preserved**:

- User-created workflows (local only)
- User configuration (if not in backup)
- Custom modifications flagged as local-only
- Workflow session states

### What is Restored

The following are **restored** from backup:

- MCP server code
- Standards content
- Usage guides
- Workflows (from source)
- config.json

---

## Rollback Performance

### Typical Timing

| Step | Time |
|------|------|
| Stop server | 2s |
| Verify backup | 3s |
| Restore files | 10s |
| Restore dependencies | 10s |
| Restart server | 3s |
| Verify health | 2s |
| **Total** | **~30s** |

### Large Installations

For installations > 500 MB:
- Restore files: 20-30s
- Restore dependencies: 15-30s
- Total: 45-60s

---

## Prevention

To avoid needing rollback:

1. **Always use dry-run first**
   ```python
   options={"dry_run": true}
   ```

2. **Ensure git status is clean**
   ```bash
   git status --porcelain
   ```

3. **Verify sufficient disk space**
   ```bash
   df -h .praxis-os/
   ```

4. **Test in non-production first**
   - Test on development environment
   - Verify on staging before production

5. **Review conflict preview**
   - Check what files will change
   - Review conflicts before resolving

---

## Post-Rollback Actions

After successful rollback:

1. **Document the issue**
   - What failed?
   - At which phase?
   - Error messages?

2. **Keep the backup**
   - Don't delete the backup used for rollback
   - May need for comparison or re-rollback

3. **Investigate root cause**
   - Check upgrade logs
   - Review phase artifacts
   - Identify why upgrade failed

4. **Plan re-attempt**
   - Fix root cause
   - Ensure prerequisites met
   - Try upgrade again with fixes

---

## Emergency Contacts

If rollback fails and system is broken:

1. **Keep calm** - Backups exist
2. **Don't delete backups**
3. **Document exact error**
4. **Try manual restore**
5. **Contact support** with:
   - Session ID
   - Phase number when failed
   - Backup path used
   - Error messages
   - Server logs

---

**Remember:** Rollback is a safety feature. Use it without hesitation if needed. It's better to rollback and retry than to force a broken upgrade.

