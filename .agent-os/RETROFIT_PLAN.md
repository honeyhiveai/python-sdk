# Agent OS Retrofit Plan
**Date**: 2025-10-14  
**Source**: agent-os-enhanced (commit e505669)  
**Target**: python-sdk/.agent-os (current v1.4.0)

---

## 🎯 Objective
Pull latest agent-os-enhanced work back into python-sdk/.agent-os, replacing prototype changes with upstream refinements.

## 📊 What Will Be Overwritten

### MCP Server Files (Replace All)
```
.agent-os/mcp_server/
├── core/parsers.py (466 lines changed)
├── core/session.py (80 lines changed)
├── models/config.py (2 lines changed)
├── models/workflow.py (41 lines changed)
├── requirements.txt (9 lines changed)
├── server/factory.py (34 lines changed)
├── server/tools/__init__.py (14 lines changed)
└── workflow_engine.py (75 lines changed)
```

**Action**: Complete replacement from agent-os-enhanced/mcp_server/

### Usage Documentation (Replace All)
```
.agent-os/usage/
├── agent-os-update-guide.md (238 lines changed)
├── mcp-server-update-guide.md (324 lines changed)
└── mcp-usage-guide.md (59 lines changed)
```

**Action**: Complete replacement from agent-os-enhanced/universal/usage/

### New Files to Add

#### New MCP Server Modules
```
+ backup_manager.py - Backup management
+ dependency_installer.py - Auto-install dependencies  
+ port_manager.py - Port conflict resolution
+ project_info.py - Project metadata extraction
+ report_generator.py - Upgrade reports
+ server_manager.py - Server lifecycle
+ transport_manager.py - Dual transport (stdio + HTTP)
+ validation_module.py - Pre-flight validation
+ workflow_validator.py - Workflow compliance
+ core/metrics.py - Performance metrics
+ models/upgrade_models.py - Upgrade data models
+ sub_agents/discovery.py - Sub-agent discovery
+ sub_agents/mcp_client_example.py - Example client
```

#### New Workflows
```
+ workflows/agent_os_upgrade_v1/ - Systematic upgrade workflow
+ workflows/standards_creation_v1/ - Standards creation workflow
+ workflows/workflow_creation_v1/ - Workflow creation workflow
```

#### New Standards
```
+ standards/meta-workflow/ - Workflow creation patterns
+ universal/usage/ai-agent-quickstart.md - Bootstrap guide
```

#### Updated Standards
```
~ standards/ai-assistant/ - Streamlined from 217 to 13 focused files
  (Will preserve local 217 files, add new upstream files)
```

## 🛡️ What Will Be Preserved

### Local-Only Content (NEVER Touched)
```
✅ .agent-os/specs/ - 20+ project-specific specifications
✅ .agent-os/standards/ai-assistant/ - 217 custom test generation files
✅ .agent-os/product/ - Product documentation
✅ .agent-os/scripts/ - Validation scripts
✅ .agent-os/workflows/test_generation_v3/ - Custom workflow
✅ .agent-os/config.json - Local configuration
✅ .agent-os/UPGRADE_*.md - Upgrade documentation
✅ .agent-os/VERSION.txt - Version tracking
✅ .agent-os/venv/ - Python virtual environment
```

## 📋 Execution Steps

### Phase 0: Pre-Flight
1. ✅ Create backup: `.agent-os.backup.retrofit.20251014`
2. ✅ Document current state
3. ✅ Validate source repository
4. ✅ Check disk space

### Phase 1: Remove Prototype Changes
1. Remove modified mcp_server files (will be replaced)
2. Remove modified usage files (will be replaced)

### Phase 2: Sync MCP Server
1. Copy entire `agent-os-enhanced/mcp_server/` → `.agent-os/mcp_server/`
2. Preserve `.agent-os/mcp_server/mcp_server/` (local only)

### Phase 3: Sync Usage Documentation
1. Copy `agent-os-enhanced/universal/usage/` → `.agent-os/usage/`

### Phase 4: Sync Standards
1. Copy `agent-os-enhanced/universal/standards/` → `.agent-os/standards/`
   - Use --ignore-existing to preserve local ai-assistant/ files
   - Add new meta-workflow/ directory

### Phase 5: Sync Workflows
1. Copy new workflows:
   - agent_os_upgrade_v1/
   - standards_creation_v1/
   - workflow_creation_v1/
2. Update existing workflows:
   - spec_creation_v1/
   - spec_execution_v1/

### Phase 6: Post-Retrofit
1. Update VERSION.txt with new commit
2. Update requirements if needed
3. Restart MCP server to reload
4. Validate with test queries
5. Update UPGRADE_COMPLETE.md

## 🔄 Rollback Procedure

If anything goes wrong:
```bash
cd /Users/josh/src/github.com/honeyhiveai/python-sdk
rm -rf .agent-os
mv .agent-os.backup.retrofit.20251014 .agent-os
# Restart Cursor
```

## 📊 Estimated Impact

- **Files Replaced**: ~50 (mcp_server + usage)
- **Files Added**: ~100 (new modules, workflows, standards)
- **Files Preserved**: ~250 (specs, custom standards, product, scripts)
- **Total Changes**: ~150 files affected
- **Time Estimate**: 5-10 minutes
- **Risk Level**: LOW (full backup + clear rollback)

## ✅ Success Criteria

1. MCP server starts without errors
2. All 8+ MCP tools respond to queries
3. Workflow commands work (start_workflow, get_current_phase, etc.)
4. Local customizations still present
5. No import errors or missing dependencies

---

**Ready to Execute**: Awaiting approval to proceed with Phase 0 (backup).

