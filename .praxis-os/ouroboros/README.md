# Ouroboros: prAxIs OS MCP Server v2

**"The snake consuming itself to be reborn"**

**Date Started:** 2025-11-03  
**Status:** 🟢 Active Development  
**Purpose:** Clean-slate rebuild of MCP server with proper architecture

---

## Why Ouroboros?

The original MCP server grew from 5k → 30k LOC without architectural refactoring. It accumulated:
- Dual orchestrators (RAGEngine + IndexManager)
- Scattered subsystems (RAG across 4 directories)
- Tight coupling (components reaching into each other)
- External scripts (FileWatcher spawning build_rag_index.py)
- 1,870 LOC single files violating SRP

Refactoring in place would take 2-3 weeks with high risk. Building clean from scratch with the knowledge we gained takes 3-5 days.

**Ouroboros is that clean rebuild.**

---

## Core Principles

### 1. Tool-Centric Architecture
- MCP server exists to expose tools
- Tool Registry is the interface layer
- Auto-discovery: Drop tool in `tools/`, it's registered
- Config-optional: Can disable domains, defaults to all enabled

### 2. Domain Abstraction
- Small tool count (5-10 tools)
- Each tool = rich domain with `action` parameter
- Reasoning-friendly (domain selection, not tool memorization)
- Example: `pos_search(action="search"|"find_callers"|"find_dependencies")`

### 3. Behavioral Engineering
- Parameter complexity creates need for guidance
- Standards provide guidance (RAG-indexed)
- Prepends reinforce querying loop (in every result)
- **The system trains AI agents to query before acting**

### 4. Clear Module Boundaries
- No stream crossing between subsystems
- Tools → Middleware → Subsystems (one-way flow)
- Subsystems NEVER import from each other
- Shared utilities in `utils/` only

### 5. Container Encapsulation
- StandardsIndex owns ALL its sub-indexes (vector, FTS, scalar)
- CodeIndex owns ALL its sub-indexes (vector, AST, graph)
- External callers NEVER touch sub-indexes directly
- `_sync_all_indexes()` is the ONLY place synchronization happens

---

## Architecture

```
ouroboros/
│
├── __main__.py                  Entry point
│
├── registry/                    THE INTERFACE LAYER
│   ├── tool_registry.py         Auto-discover & register tools
│   ├── config_loader.py         Load configuration
│   └── validator.py             Validate tools & config
│
├── tools/                       ENTRY POINTS (Auto-discovered)
│   ├── pos_search.py            Search domain
│   ├── pos_workflow.py          Workflow domain
│   ├── pos_browser.py           Browser domain
│   ├── pos_filesystem.py        File operations domain
│   └── pos_info.py              Server metadata domain
│
├── middleware/                  CROSS-CUTTING CONCERNS
│   ├── prepend_generator.py    Query gamification
│   ├── query_tracker.py        Metrics & logging
│   ├── query_classifier.py     Query routing hints
│   └── session_manager.py      Session ID management
│
├── subsystems/                  HIDDEN IMPLEMENTATION
│   │
│   ├── rag/                    Search & Indexing Subsystem
│   │   ├── index_manager.py        Orchestrator
│   │   ├── standards_index.py      Container (vector+FTS+scalar)
│   │   ├── code_index.py           Container (vector+AST+graph)
│   │   ├── base_index.py           Base class
│   │   ├── file_watcher.py         Change detection
│   │   └── chunker.py              Content processing
│   │
│   ├── workflow/               Workflow Subsystem
│   │   ├── engine.py               Execution engine
│   │   ├── state_manager.py        State persistence
│   │   ├── validator.py            Validation logic
│   │   ├── parsers.py              Task doc parsing
│   │   └── checkpoint_loader.py    Gates/checkpoints
│   │
│   └── browser/                Browser Subsystem
│       ├── manager.py              Session management
│       └── actions.py              Browser operations
│
├── utils/                       SHARED UTILITIES
│   ├── config.py               Unified config loading
│   ├── logging.py              Logging setup
│   └── metrics.py              Metrics infrastructure
│
└── tests/                      TEST SUITE
    ├── integration/            Integration tests
    └── unit/                   Unit tests
```

---

## Development Plan

### Phase 1: Foundation (Day 1) ✅ IN PROGRESS
- [x] Create directory structure
- [ ] Tool registry with auto-discovery
- [ ] Basic tool loading & registration
- [ ] Config system (load index_config.yaml)
- [ ] Logging infrastructure

### Phase 2: RAG Subsystem (Day 2)
- [ ] Port StandardsIndex (the good parts)
- [ ] Implement _sync_all_indexes() pattern
- [ ] Port file watcher (in-process, no external scripts)
- [ ] Implement pos_search tool
- [ ] Test: Search works, incremental updates work

### Phase 3: Middleware (Day 2-3)
- [ ] Port prepend_generator
- [ ] Port query_tracker
- [ ] Port query_classifier
- [ ] Test: Prepends appear in results, queries tracked

### Phase 4: Workflow Subsystem (Day 3)
- [ ] Port workflow engine
- [ ] Port state manager
- [ ] Port parsers
- [ ] Implement pos_workflow tool
- [ ] Test: Workflow execution works

### Phase 5: Browser Subsystem (Day 4)
- [ ] Port browser manager
- [ ] Split browser actions from monolith
- [ ] Implement pos_browser tool
- [ ] Test: Browser automation works

### Phase 6: Integration & Testing (Day 5)
- [ ] Integration tests
- [ ] Performance testing
- [ ] Documentation
- [ ] Switch from old server to Ouroboros

---

## Key Differences from Old Server

### Old Server
- ❌ Dual orchestrators (RAGEngine + IndexManager)
- ❌ FileWatcher spawns external scripts
- ❌ RAG code across 4 directories
- ❌ No _sync_all_indexes() pattern
- ❌ browser_tools.py = 1,870 LOC monolith
- ❌ Workflow scattered across 6 directories
- ❌ No clear module boundaries

### Ouroboros
- ✅ Single orchestrator (IndexManager only)
- ✅ FileWatcher calls IndexManager in-process
- ✅ All RAG code in subsystems/rag/
- ✅ _sync_all_indexes() enforced in all containers
- ✅ Browser actions properly split
- ✅ All workflow code in subsystems/workflow/
- ✅ Clear boundaries, no stream crossing

---

## Porting Strategy

**What to port:**
- ✅ StandardsIndex container logic (vector+FTS+scalar)
- ✅ ASTIndex parsing & symbol extraction
- ✅ CodeIndex semantic search
- ✅ Workflow engine & state management
- ✅ Browser manager & Playwright integration
- ✅ Prepend generator & query tracking
- ✅ Parsers & chunking logic

**What to rewrite:**
- ✅ Tool registry (new auto-discovery)
- ✅ File watcher integration (in-process)
- ✅ Config loading (unified schema)
- ✅ Module structure (clean boundaries)

**What to skip:**
- ❌ RAGEngine (replaced by IndexManager)
- ❌ build_rag_index.py (external script)
- ❌ Duplicate handlers/validators
- ❌ Root-level chaos files

---

## Success Criteria

### Must Haves
1. ✅ All tools auto-discovered from tools/ directory
2. ✅ RAG search works (standards + code)
3. ✅ Incremental updates work (file watcher)
4. ✅ All sub-indexes sync atomically (_sync_all_indexes)
5. ✅ Workflow execution works
6. ✅ Browser automation works
7. ✅ Prepends appear in all search results
8. ✅ No external script spawning
9. ✅ Clear subsystem boundaries
10. ✅ Passes all integration tests

### Nice to Haves
1. Performance equivalent or better than old server
2. Comprehensive test coverage
3. Migration guide from old server
4. Documentation of architectural decisions

---

## Timeline

**Estimated:** 3-5 days of focused development
**Started:** 2025-11-03
**Target Completion:** 2025-11-08
**Actual Completion:** TBD

---

## Notes

This is not just a refactor. This is applying everything we learned:
- From the corruption bugs (need _sync_all_indexes)
- From the lost work (dev vs distribution)
- From the architectural audit (30k LOC analysis)
- From understanding the behavioral engineering principles

**Ouroboros rises from the ashes of the old server, wiser and cleaner.**

---

**Status:** 🐍 The snake begins to consume itself...

