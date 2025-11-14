# prAxIs OS Upgrade Workflow v1.0

AI-guided prAxIs OS upgrade with validation, rollback capability, and state persistence.

---

## Overview

The prAxIs OS Upgrade Workflow automates the process of upgrading prAxIs OS installations (content + MCP server) with:

- **Automatic validation** - Pre-flight checks prevent bad upgrades
- **Rollback capability** - Automatic rollback on any failure
- **State persistence** - Survives MCP server restarts
- **Comprehensive validation** - Post-upgrade health checks

**Total Time:** ~3 minutes 20 seconds

---

## Quick Start

### Starting the Upgrade

```python
# Via MCP tools
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

### After Server Restart (Phase 3)

```python
# Resume the workflow
get_workflow_state(session_id)
get_current_phase(session_id)
```

---

## Workflow Phases

### Phase 0: Pre-Flight Checks (30s)
- Validates source repository
- Checks git status is clean
- Verifies disk space
- Prevents concurrent upgrades

### Phase 1: Backup & Preparation (20s)
- Creates timestamped backup
- Generates checksum manifest
- Acquires upgrade lock

### Phase 2: Content Upgrade (45s)
- Runs safe-upgrade.py with conflict detection
- Updates standards, usage, workflows
- Updates version tracking

### Phase 3: MCP Server Upgrade (60s) ⚠️ **Critical Phase**
- Copies MCP server code
- Installs dependencies
- Runs post-install steps (playwright, etc.)
- **Restarts MCP server**
- Workflow resumes from disk state

### Phase 4: Post-Upgrade Validation (30s)
- Checks tool registration
- Runs smoke tests
- Validates RAG and browser tools

### Phase 5: Cleanup & Documentation (15s)
- Releases upgrade lock
- Archives old backups
- Generates reports

---

## Key Features

### ✅ Automatic Rollback

If any phase fails (2, 3, or 4), the workflow automatically rolls back to the backup created in Phase 1.

Target rollback time: < 30 seconds

### ✅ State Persistence

Workflow state is saved to disk after each phase, enabling the workflow to survive the MCP server restart in Phase 3.

### ✅ Safety First

- Pre-flight checks prevent bad upgrades
- Timestamped backups with checksum verification
- Never overwrites user config without prompting
- Concurrent upgrade prevention via lock file

### ✅ Comprehensive Validation

- Git status checks (source must be clean)
- Disk space checks (need 2x current size)
- Post-upgrade smoke tests
- Health checks after server restart

---

## Requirements

### Source Repository
- Must be praxis-os repository
- Git status must be clean (no uncommitted changes)
- Must have VERSION.txt file

### Target Installation
- Valid `.praxis-os/` directory structure
- Sufficient disk space (2x current size)
- No other upgrade workflows in progress

### System
- Python 3.8+
- pip for dependency installation
- Git for version control
- 500 MB+ free disk space

---

## Configuration Options

```python
options = {
    "source_path": "/path/to/praxis-os",  # Required
    "dry_run": false,           # Preview changes only
    "auto_restart": true,       # Auto-restart server in Phase 3
    "skip_tests": false,        # Skip validation tests
    "keep_backups": 3,          # Number of backups to keep
    "interactive_conflicts": true  # Prompt for conflict resolution
}
```

---

## Error Handling

### Common Failures

| Error | Phase | Action |
|-------|-------|--------|
| Dirty git status | 0 | Commit or stash changes |
| Insufficient disk space | 0 | Free up space |
| Backup creation failed | 1 | Check permissions |
| Content conflicts | 2 | Resolve conflicts or rollback |
| Dependency install failed | 3 | Auto-rollback |
| Server won't restart | 3 | Auto-rollback |
| Validation failed | 4 | Auto-rollback |

### Manual Rollback

If you need to manually rollback:

```python
from mcp_server.backup_manager import BackupManager
from pathlib import Path

backup_mgr = BackupManager()
backup_path = Path(".praxis-os/.backups/2025-10-08-103045/")
backup_mgr.restore_from_backup(backup_path)
```

---

## Components

The workflow uses the following MCP server components:

- **StateManager** - Workflow state persistence
- **BackupManager** - Backup creation and restoration
- **ValidationModule** - Pre-flight and post-upgrade validation
- **DependencyInstaller** - Python dependency management
- **ServerManager** - MCP server process management
- **ReportGenerator** - Upgrade reports and documentation

---

## Files Structure

```
universal/workflows/praxis_os_upgrade_v1/
├── metadata.json                    # Workflow metadata
├── README.md                        # This file
├── phases/
│   ├── 0-pre-flight-checks.md
│   ├── 1-backup-preparation.md
│   ├── 2-content-upgrade.md
│   ├── 3-mcp-server-upgrade.md
│   ├── 4-post-upgrade-validation.md
│   └── 5-cleanup-documentation.md
└── supporting-docs/
    ├── rollback-procedure.md
    ├── troubleshooting.md
    └── validation-criteria.md
```

---

## Success Metrics

An upgrade is successful if:

1. ✅ All 6 phases complete without errors
2. ✅ MCP server responds to requests
3. ✅ All expected tools registered
4. ✅ Smoke tests pass
5. ✅ No errors in server log
6. ✅ Version updated correctly
7. ✅ User customizations preserved

---

## Troubleshooting

### Upgrade stuck in Phase 3

The server restart in Phase 3 may take up to 30 seconds. If stuck longer:

1. Check server process: `pgrep -f "python -m mcp_server"`
2. Check server logs
3. Resume manually: `get_workflow_state(session_id)`

### Rollback failed

If automatic rollback fails:

1. Stop server: `pkill -f "python -m mcp_server"`
2. Manually restore from backup (see manual rollback above)
3. Restart server: `python -m mcp_server`

### Conflicts during upgrade

The workflow will detect conflicts and prompt for resolution. Options:

- **Keep local** - Preserve your changes
- **Use remote** - Accept upstream changes
- **Manual merge** - Resolve manually

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-09 | Initial implementation |

---

## Support

For issues or questions:

1. Check [troubleshooting.md](supporting-docs/troubleshooting.md)
2. Review upgrade logs in `.praxis-os/.cache/`
3. Check backup availability in `.praxis-os/.backups/`
4. Report issues with session ID and phase number

---

## License

Part of prAxIs OS - AI-powered development workflow system.

