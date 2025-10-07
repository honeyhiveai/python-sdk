# Agent OS MCP Server - Changelog

All notable changes to the Agent OS MCP server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.4.0] - 2025-10-07

### Added
- **Modular Architecture**: Complete refactoring to modular structure
  - `models/` module: Data structures organized by domain (config, workflow, rag)
  - `config/` module: ConfigLoader and ConfigValidator for single source of truth
  - `monitoring/` module: Refactored file watcher with dependency injection
  - `server/` module: ServerFactory and modular tool registration
  - Sub-agent infrastructure ready for future expansion

### Changed
- **Configuration Management**: New ConfigLoader with graceful fallback
  - Validates all paths before server creation
  - Supports custom, partial, and invalid configs
  - Clear error messages for configuration issues
- **Dependency Injection**: All components created via ServerFactory
  - No hardcoded paths in any module
  - Easy to test with mocked dependencies
  - Clean separation of concerns
- **Tool Registration**: Modular tool organization
  - Tools grouped by domain (rag_tools, workflow_tools)
  - Tool count monitoring (warns at >20 tools)
  - Selective loading via `enabled_tool_groups` config
- **Entry Point**: __main__.py rewritten to use new architecture
  - Uses ConfigLoader, ConfigValidator, ServerFactory
  - Maintains backward compatibility with existing configs

### Removed
- `agent_os_rag.py` (984 lines): Replaced by modular architecture
- `models.py` (410 lines): Replaced by models/ module
- Old `_load_path_config()` function: Replaced by ConfigLoader
- Old `AgentOSFileWatcher`: Replaced by monitoring/watcher.py with DI

### Migration
- **No breaking changes**: All existing functionality preserved
- All 8 MCP tools work identically (1 RAG + 7 workflow)
- All 33 tests passing (28 unit + 5 integration)
- Existing config.json files work unchanged
- Import updates required for developers (see migration guide)

---

## [1.3.1] - 2025-10-06

### Fixed
- **Phase 0 Workflows Now Work Correctly**: Fixed hardcoded initial phase bug
  - **Bug**: Workflows starting at Phase 0 were incorrectly initialized to Phase 1
  - **Impact**: Phase 0 was completely skipped, breaking workflows like `test-generation-js-ts`
  - **Fix**: Dynamic phase detection in `state_manager.py` and `workflow_engine.py`
    - `StateManager.create_session()` now detects starting phase (0 or 1)
    - Checks if `phases/0/` directory exists in workflow structure
    - Defaults to Phase 1 for backwards compatibility
    - `WorkflowEngine.start_workflow()` uses `state.current_phase` instead of hardcoded 1
  - **Testing**: Added 7 new unit tests for Phase 0 detection and execution
  - **Backwards Compatible**: Workflows without Phase 0 still start at Phase 1

**Before (Broken):**
```python
start_workflow("test-generation-js-ts", "file.ts")
# Returns:
{
  "current_phase": 1,  # ❌ Should be 0
  "phase_content": {"phase_number": 1, ...}  # Skips Phase 0
}
```

**After (Fixed):**
```python
start_workflow("test-generation-js-ts", "file.ts")
# Returns:
{
  "current_phase": 0,  # ✅ Correct
  "phase_content": {"phase_number": 0, ...}  # Phase 0 content
}
```

---

## [1.3.0] - 2025-10-06

### Added
- **`get_task` MCP Tool (Horizontal Scaling)**: New tool for retrieving individual tasks
  - Signature: `get_task(session_id, phase, task_number)`
  - Returns complete task content with execution steps
  - Follows meta-framework principle: one task at a time
  - Ensures complete content via 50-chunk RAG retrieval
  - Sorted chunks maintain proper content order

- **Update Documentation (Critical)**: Comprehensive guides to prevent update mistakes
  
  **Content Updates (No Restart Required):**
  - **`universal/usage/agent-os-update-guide.md`**: Content update instructions
    - Correct source location (`universal/` not `.agent-os/`)
    - **File watcher auto-detects `.md`/`.json` changes** - no manual action needed
    - RAG index rebuilds automatically in ~10-30 seconds
    - **No server restart required** for content updates
    - Example update scripts with validation
    - Version tracking and rollback procedures
    - Troubleshooting common mistakes
  
  **Server Updates (Restart Required):**
  - **`universal/usage/mcp-server-update-guide.md`**: MCP server update instructions
    - **Server code updates (.py files) REQUIRE restart**
    - File watchers only monitor content files, not Python code
    - Package vs source installation updates
    - Dependency management
    - Breaking changes and migration guides
    - Production deployment strategies
  
  **Standards & Warnings:**
  - **`universal/standards/installation/update-procedures.md`**: Official update standards
    - Formal requirements distinguishing content vs server updates
    - Content updates: automatic via file watcher
    - Server updates: manual restart required
    - Validation and compliance checklists
    - Incident response procedures
  - **`CRITICAL_UPDATE_WARNING.md`**: High-visibility warning at repo root
    - Clear DO/DON'T comparison for content updates
    - Explains file watcher auto-detection
    - Emergency recovery steps
    - Quick reference for developers

### Changed
- **`get_current_phase` Now Returns Task Metadata Only**: Breaking change in response structure
  - `phase_content.tasks` now contains only: `task_number`, `task_name`, `task_file`
  - No longer includes full task `content` or `steps` (too much context)
  - Added message: "Use get_task(session_id, phase, task_number) to retrieve full task content"
  - General phase guidance still included in `content_chunks`

### Why This Change?

**Meta-Framework Alignment: Horizontal Scaling**

**Before (v1.2.3):** Returned all tasks at once
```typescript
get_current_phase() → {
  tasks: [
    { task_1: "...", content: "...", steps: [...] },  // 2KB
    { task_2: "...", content: "...", steps: [...] },  // 2KB
    { task_3: "...", content: "...", steps: [...] },  // 2KB
    ...
  ]  // 10KB total - attention overwhelm ❌
}
```

**After (v1.3.0):** Get task list, then retrieve one task at a time
```typescript
// Step 1: Get overview
get_current_phase() → {
  tasks: [
    { task_number: 1, task_name: "Console Detection", task_file: "..." },
    { task_number: 2, task_name: "Logger Analysis", task_file: "..." }
  ]  // Just metadata ~200 bytes ✅
}

// Step 2: Get first task
get_task(session_id, phase=1, task_number=1) → {
  content: "...",  // Complete task markdown
  steps: [...]      // Execution steps
}  // ~1-2KB focused context ✅

// Step 3: Execute, then get next task
get_task(session_id, phase=1, task_number=2) → { ... }
```

**Benefits:**
- ✅ Focused attention (one task at a time)
- ✅ Token efficient (only load what's needed now)
- ✅ Sequential execution enforced by API
- ✅ Honors horizontal scaling (small chunks ≤100 lines)
- ✅ Complete task content guaranteed

### Migration Guide

**Old pattern (v1.2.3):**
```python
phase = get_current_phase(session_id)
for task in phase['phase_content']['tasks']:
    # task already has full content and steps
    execute_steps(task['steps'])
```

**New pattern (v1.3.0):**
```python
phase = get_current_phase(session_id)
for task_meta in phase['phase_content']['tasks']:
    # Get full task content
    task = get_task(session_id, phase['current_phase'], task_meta['task_number'])
    # Now execute steps
    execute_steps(task['steps'])
```

---

## [1.2.3] - 2025-10-06

### Added
- **Structured Task Data in Phase Content**: MCP tools now return executable task data
  - `phase_content.tasks` array with structured task information
  - Each task includes task_name, task_number, task_file, content, and steps
  - Steps include command, description, type, and evidence_required
  - Extracts 🛑 EXECUTE-NOW commands from workflow files
  - Extracts 📊 COUNT-AND-DOCUMENT evidence markers
  - Supports 🔍 QUERY-AND-DECIDE decision points

### Changed
- **RAG-Based Task Retrieval**: Leverages existing workflow index (v1.2.1)
  - Dual RAG queries: general methodology + task-specific commands
  - Groups RAG chunks by task file
  - Extracts commands via regex patterns
  - No direct file reading required
  - Pure MCP interface for workflow execution

### Why This Enhancement?
**Before:** Agent had to read workflow task files directly from filesystem
```typescript
// Required file access
const task = await read_file('.agent-os/workflows/.../task-1-console.md');
// Manual parsing needed
const commands = parseMarkdown(task);
```

**After:** Agent gets structured tasks from MCP
```typescript
// Pure MCP, no file access
const session = await start_workflow(...);
const tasks = session.phase_content.tasks;
// Structured data ready to execute
for (const step of tasks[0].steps) {
  if (step.type === "execute_command") {
    await run_terminal_cmd(step.command);
  }
}
```

---

## [1.2.2] - 2025-10-06

### Fixed
- **Hardcoded Workflow Paths Bug**: MCP server now reads paths from `config.json`
  - Fixes workflow metadata not loading in consuming projects with custom structures
  - Eliminates need for symlink workaround
  - Backward compatible - falls back to defaults if no config

### Added
- **config.json Path Configuration**: Customize directory paths for standards, usage, workflows
  - `rag.standards_path` - Path to technical standards
  - `rag.usage_path` - Path to usage guides  
  - `rag.workflows_path` - Path to workflow metadata
  - Paths resolved relative to project root
  - Partial configuration supported (specify only what you need)

- **Integration Tests**: Comprehensive test suite for custom path configuration
  - Tests default paths (no config)
  - Tests custom paths from config.json
  - Tests partial configuration
  - Tests invalid config fallback
  - Tests workflow metadata loading from custom paths

### Changed
- **Path Resolution**: All paths now resolved through `_load_path_config()`
- **File Watcher**: Uses config paths for index rebuild

### Documentation
- **CONFIG_JSON_GUIDE.md**: Complete guide for configuring custom paths
  - Common directory structures
  - Path resolution examples
  - Verification steps
  - Migration guide from symlinks

### Why This Fix?
**Before:** Consuming projects had to use symlinks or match exact directory structure
```bash
# Required workaround
ln -s ../.agent-os-source/workflows .agent-os/universal/workflows
```

**After:** Configure paths in config.json
```json
{
  "rag": {
    "workflows_path": ".agent-os-source/workflows"
  }
}
```

---

## [1.2.1] - 2025-10-06

### Added
- **Workflows Directory RAG Indexing**: Workflow metadata now indexed for semantic discovery
  - Added `workflows_path` parameter to `IndexBuilder`
  - File watcher monitors `universal/workflows/` directory for changes
  - JSON files (metadata.json) now trigger index rebuilds
  - AI agents can discover workflows through semantic search

- **Comprehensive Workflow Standards Documentation**: Three indexed standards documents
  - `workflow-system-overview.md` - Complete workflow system guide (400+ lines)
  - `mcp-rag-configuration.md` - MCP RAG setup with workflows (400+ lines)
  - `workflow-metadata-standards.md` - Metadata creation standards (500+ lines)

### Changed
- **File Watcher Enhancement**: Now handles both `.md` and `.json` files
- **Directory Structure**: Updated paths to use `universal/` directory
  - `universal/standards/` - Technical standards (indexed)
  - `universal/workflows/` - Workflow metadata (indexed)
  - `universal/usage/` - Usage guides (indexed)

### Updated
- **MCP Usage Guide**: Added workflow discovery examples
- **IndexBuilder**: All calls now include workflows_path parameter
- **Server Initialization**: Passes workflows_path throughout system

### Why This Feature?
Before: AI agents couldn't discover workflows or understand MCP configuration
After: Complete workflow system discoverable through semantic search

**Discovery Flow:**
```python
# Discover workflows
result = await search_standards("What workflows are available for testing?")
# Returns: Workflow metadata and standards docs

# Learn configuration
result = await search_standards("How do I configure MCP RAG for workflows?")
# Returns: Complete configuration guide
```

---

## [1.2.0] - 2025-10-06

### Added
- **Workflow Overview in `start_workflow`**: Enhanced workflow initialization with comprehensive metadata
  - Returns complete workflow structure upfront (total phases, phase names, purposes)
  - Eliminates need for separate `get_workflow_state()` call to understand workflow
  - Includes estimated effort, key deliverables, and validation criteria for each phase
  - Backward compatible: works with or without metadata.json files
  - Auto-generates fallback metadata for existing workflows

### Why This Feature?
AI agents previously needed two API calls to understand workflow structure:
1. `start_workflow()` - Get session and Phase 1 content
2. `get_workflow_state()` - Learn total phases and structure

Now agents get complete overview immediately, enabling better planning and progress tracking.

### New Response Structure
```json
{
  "session_id": "uuid",
  "workflow_type": "test_generation_v3",
  "workflow_overview": {
    "total_phases": 8,
    "estimated_duration": "2-3 hours",
    "primary_outputs": ["test files", "coverage report"],
    "phases": [
      {
        "phase_number": 0,
        "phase_name": "Setup",
        "purpose": "Initialize test environment",
        "estimated_effort": "10 minutes",
        "key_deliverables": ["Test framework configured"],
        "validation_criteria": ["Test runner executes"]
      }
      // ... all phases
    ]
  },
  "current_phase": 1,
  "phase_content": {...}
}
```

### Metadata Files
- Created `universal/workflows/test_generation_v3/metadata.json`
- Created `universal/workflows/production_code_v2/metadata.json`
- See `WORKFLOW_METADATA_GUIDE.md` for creating metadata for new workflows

---

## [1.1.0] - 2025-10-06

### Added
- **`current_date` Tool**: New MCP tool to prevent AI date errors
  - Returns current date/time in ISO 8601 format (YYYY-MM-DD)
  - Provides multiple formatted outputs (spec directories, headers, readable)
  - Includes day of week, month, year, and unix timestamp
  - Solves systematic AI date error problem per Agent OS date policy
  - Example use: Create specifications with correct dates, proper directory naming

### Why This Feature?
AI assistants consistently make date errors:
- Using wrong dates (e.g., 2025-01-30 when current is 2025-10-06)
- Inconsistent date formats across documentation
- Hardcoded dates instead of getting current date

The `current_date` tool provides a single source of truth for the current date, ensuring all AI-generated content uses correct, consistently-formatted dates.

### Tool Documentation
```python
# Usage
result = await current_date()
# Returns:
{
  "iso_date": "2025-10-06",  # Primary format for all uses
  "iso_datetime": "2025-10-06T14:30:00.123456",
  "day_of_week": "Monday",
  "month": "October",
  "year": 2025,
  "unix_timestamp": 1728226200,
  "formatted": {
    "spec_directory": "2025-10-06-",  # For directory naming
    "header": "**Date**: 2025-10-06",  # For markdown headers
    "readable": "October 06, 2025"
  },
  "usage_note": "Use 'iso_date' (YYYY-MM-DD) for all specifications, directories, and headers per Agent OS date policy"
}
```

---

## [1.0.0] - 2025-10-05

### Added
- **Core MCP Server**: Main entry point with FastMCP integration
- **RAG Engine**: LanceDB vector search with 90%+ retrieval accuracy
- **Workflow Engine**: Phase-gated workflows with checkpoint validation
- **State Manager**: Workflow state persistence and resume capability
- **File Watcher**: Automatic index rebuild on content changes (hot reload)
- **5 MCP Tools**:
  - `search_standards` - Semantic search over standards
  - `start_workflow` - Initialize phase-gated workflow
  - `get_current_phase` - Retrieve current phase requirements
  - `complete_phase` - Submit evidence and advance
  - `get_workflow_state` - Query complete workflow state
- **Observability Hooks**: No-op by default, extensible for any platform
- **Local Embeddings**: Free, offline semantic search with sentence-transformers
- **Thread-Safe Hot Reload**: Concurrent query protection during index rebuilds
- **Documentation**: Complete README, observability integration guide

### Features
- 90% context reduction (50KB → 5KB via RAG)
- <100ms query latency
- Incremental index updates (fast hot reload)
- Project-agnostic (works with any codebase)
- No external dependencies for core functionality

### Architecture
- LanceDB for vector storage (deterministic, thread-safe)
- Sentence-transformers for embeddings (no API keys required)
- Watchdog for file system monitoring
- FastMCP for Cursor IDE integration

---

## Future Releases

### Planned for [1.1.0]
- [ ] Sub-agent: Design Validator (adversarial design review)
- [ ] Sub-agent: Concurrency Analyzer (thread safety analysis)
- [ ] Sub-agent: Architecture Critic (system design review)
- [ ] Sub-agent: Test Generator (systematic test creation)
- [ ] Enhanced RAG: Hybrid search (vector + keyword)
- [ ] Multi-language project support (Python + Go in same repo)

### Planned for [1.2.0]
- [ ] Workflow templates: API design validation
- [ ] Workflow templates: Security review
- [ ] Performance: Async RAG queries for batch operations
- [ ] Performance: Cached embeddings for frequently queried standards

---

## Updating

When a new version is released, users can update via:

```
"Update Agent OS to latest version"
```

Cursor agent will:
1. Pull latest from agent-os-enhanced repo
2. Update MCP server code
3. Preserve user customizations
4. Rebuild RAG index if needed

---

## Version Compatibility

| Agent OS Version | Python | LanceDB | Sentence-Transformers | MCP |
|------------------|--------|---------|----------------------|-----|
| 1.0.0            | ≥3.8   | ~=0.25.0 | ≥2.0.0               | ≥1.0.0 |

---

## Breaking Changes

None yet (initial release).

---

## Contributors

- 100% AI-authored via human orchestration (HoneyHive team)
- Built on Brian Casel's Builder Methods Agent OS foundation
- Inspired by HoneyHive's LLM Workflow Engineering methodology

---

**For detailed feature documentation, see README.md**
