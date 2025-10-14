# Local Customizations to Preserve During Upgrade

**Date**: 2025-10-08
**Current Version**: v1.3.0 (from 2025-10-08)
**Target Version**: v1.4.0 (2025-10-07)

## Local Directories (DO NOT SYNC - Keep as-is)

### 1. `/specs/` - Project-Specific Specifications
- 20+ project-specific specification directories
- Each containing specs.md, srd.md, tasks.md, implementation.md, etc.
- Examples:
  - 2025-10-03-agent-os-mcp-rag-evolution/
  - 2025-10-04-honeyhive-sdk-docs-mcp/
  - 2025-10-07-honeyhive-sdk-docs-mcp-v2/
  - 2025-09-03-evaluation-to-experiment-alignment/ (27 files)
  - And many more...

### 2. `/product/` - Local Product Documentation
- audience.md
- decisions.md
- features.md
- overview.md
- roadmap.md

### 3. `/standards/ai-assistant/` - Custom Test Generation Frameworks
- 217 markdown files containing custom test generation standards
- Subdirectories:
  - code-generation/ (linters, production, tests, shared)
  - code-generation/tests/v3/ (129 files - extensive custom framework)
  - Custom patterns and quality gates
- Files:
  - AI-ASSISTED-DEVELOPMENT-PLATFORM-CASE-STUDY.md
  - DETERMINISTIC-LLM-OUTPUT-METHODOLOGY.md
  - LLM-WORKFLOW-ENGINEERING-METHODOLOGY.md
  - TEST_GENERATION_MANDATORY_FRAMEWORK.md
  - And many more custom standards...

### 4. `/workflows/` - May Have Local Customizations
- spec_creation_v1/
- spec_execution_v1/
- VERSION.txt (tracks local workflow version)

### 5. `/scripts/` - Local Validation Scripts
- Custom validation and test scripts

## Universal Content to Sync (FROM agent-os-enhanced/universal/)

### 1. `/standards/` (Base standards only, NOT ai-assistant)
From: `agent-os-enhanced/universal/standards/`
Sync directories:
- ai-safety/
- architecture/
- concurrency/
- database/
- documentation/
- failure-modes/
- installation/
- meta-framework/
- performance/
- security/
- testing/
- workflows/

### 2. `/usage/` (Usage guides)
From: `agent-os-enhanced/universal/usage/`
Files:
- agent-os-update-guide.md
- creating-specs.md
- mcp-server-update-guide.md
- mcp-usage-guide.md
- operating-model.md

### 3. `/mcp_server/` (Server code updates)
From: `agent-os-enhanced/.agent-os/mcp_server/`
Major changes in v1.4.0:
- Modular architecture refactor
- New models/, config/, monitoring/, server/ modules
- Updated __main__.py with ServerFactory

## Version Changes: v1.3.0 → v1.4.0

### Key Features Added:
1. **Modular Architecture**: Complete refactoring to modular structure
2. **Configuration Management**: New ConfigLoader with graceful fallback
3. **Dependency Injection**: ServerFactory pattern
4. **Tool Registration**: Modular tool organization

### Breaking Changes:
- None! Backward compatible with existing configs

### Migration Notes:
- All 8 MCP tools work identically
- Existing config.json files work unchanged
- Import updates required for developers (internal only)

## Safety Measures Taken:
1. ✅ Created backup at `.agent-os.backup`
2. ✅ Documented all local customizations
3. ✅ Using rsync with --exclude for selective sync
4. ✅ Will rebuild RAG index after sync (automatic via file watcher)
5. ✅ Will test with search_standards query
6. ✅ Will verify workflow functionality

## Rollback Procedure (if needed):
```bash
cd /Users/josh/src/github.com/honeyhiveai/python-sdk
rm -rf .agent-os
mv .agent-os.backup .agent-os
# Restart Cursor to reload MCP server
```

