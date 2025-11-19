# MCP RAG Configuration Standards

**Standards for configuring MCP RAG with workflow support**

---

## 🎯 TL;DR - MCP RAG Configuration Quick Reference

**Keywords for search**: MCP RAG configuration, RAG indexing, vector index, workflow metadata indexing, search_standards configuration, embedding configuration, file watcher, RAG performance

**Core Principle:** Configure MCP RAG to index standards (all AI-facing content) for AI agent discovery via `pos_search_project()`.

**One Directory Indexed:**
- **.praxis-os/standards/** - All AI-facing content (behavioral guidance, processes, examples)
  - `universal/ai-assistant/` - AI behavioral patterns and guides
  - `universal/workflows/` - Workflow standards and creation guides
  - `universal/operations/` - System operations and update guides
  - `project/` - Project-specific standards

**NOT Indexed:**
- **.praxis-os/workflows/** - Use `pos_workflow` tool for workflow discovery
  - Structured queries provide complete metadata
  - RAG search not appropriate for structured workflow data

**Key Configuration:**
```python
builder = IndexBuilder(
    index_path=Path(".praxis-os/.cache/vector_index"),
    standards_path=Path(".praxis-os/standards"),  # All AI-facing content
    embedding_provider="local",  # or "openai"
    embedding_model="all-MiniLM-L6-v2"  # Free, offline
)
```

**File Watcher (Hot Reload):**
- Watches .praxis-os/standards/ directory for changes
- Automatically rebuilds index on file modifications
- Typical rebuild: 2-5 seconds for single file
- Debounce: 5 seconds to batch rapid changes

**Indexing Strategy:**
- **Chunk size:** 500 tokens (overlap: 50 tokens)
- **Files:** Markdown (.md) and JSON (metadata.json)
- **Exclusions:** node_modules/, .git/, __pycache__/, build/

**Search Optimization:**
- Semantic search via vector similarity
- Returns top 5 results by default
- Includes file path, section headers, relevance score

**Performance Targets:**
- **Query time:** <100ms (95th percentile)
- **Index rebuild:** <10s for full corpus
- **Memory usage:** <500MB with index loaded

**Common Errors:**
- ❌ Querying for workflow metadata via `pos_search_project()` (use `pos_workflow` tool instead)
- ❌ Wrong embedding model (index incompatible with queries)
- ❌ Not restarting MCP server after config changes

---

## ❓ Questions This Answers

1. "How do I configure MCP RAG?"
2. "What directories should RAG index?"
3. "How do I enable workflow metadata indexing?"
4. "What embedding model should I use?"
5. "How does file watcher work?"
6. "How fast should RAG queries be?"
7. "How do I optimize RAG performance?"
8. "What files does RAG index?"
9. "How do I test RAG configuration?"
10. "What are common RAG configuration errors?"
11. "How do I enable hot reload for RAG?"

---

## 🎯 Purpose

This document defines standards for configuring the MCP RAG system to properly index and serve workflow metadata, standards, and usage documentation to AI agents.

---

## What Directory Structure Should RAG Index?

The MCP RAG system indexes content from three primary directories that contain discoverable content for AI agents.

### Required Directories

```
universal/
├── standards/          # Technical standards (MUST index)
│   ├── workflows/      # Workflow system standards
│   ├── testing/        # Testing standards
│   ├── architecture/   # Architecture patterns
│   └── ...
│
├── workflows/          # Workflow metadata (MUST index)
│   ├── test_generation_v3/
│   │   └── metadata.json
│   ├── production_code_v2/
│   │   └── metadata.json
│   └── ...
│
└── usage/             # Usage guides (MUST index)
    ├── mcp-usage-guide.md
    ├── operating-model.md
    └── ...
```

---

## How to Configure IndexBuilder?

IndexBuilder is the core component that creates and maintains the vector index for semantic search.

### Initialization Parameters

```python
from pathlib import Path
from scripts.build_rag_index import IndexBuilder

builder = IndexBuilder(
    index_path=Path(".praxis-os/.cache/vector_index"),
    standards_path=Path("universal/standards"),
    usage_path=Path("universal/usage"),          # Optional
    workflows_path=Path("universal/workflows"),  # NEW: Required for workflow discovery
    embedding_provider="local",  # or "openai"
    embedding_model="all-MiniLM-L6-v2"  # Free, offline
)
```

### Parameter Descriptions

| Parameter | Required | Purpose | Default |
|-----------|----------|---------|---------|
| `index_path` | Yes | Where to store vector index | `.praxis-os/.cache/vector_index` |
| `standards_path` | Yes | Technical standards directory | `universal/standards` |
| `usage_path` | No | Usage guides directory | `universal/usage` |
| `workflows_path` | **Yes** | Workflow metadata directory | `universal/workflows` |
| `embedding_provider` | No | Embedding model provider | `"local"` (free) |
| `embedding_model` | No | Specific model to use | Provider-specific default |

---

## How Does File Watcher Enable Hot Reload?

File Watcher monitors the universal/ directory and automatically rebuilds the index when files change, enabling instant discovery of new content.

### Required Watchers

The system MUST watch all three directories for changes:

```python
# Watch standards directory
observer_standards = Observer()
observer_standards.schedule(
    file_watcher,
    path=str(standards_path),
    recursive=True
)
observer_standards.start()

# Watch usage directory
observer_usage = Observer()
observer_usage.schedule(
    file_watcher,
    path=str(usage_path),
    recursive=True
)
observer_usage.start()

# Watch workflows directory (NEW - REQUIRED)
observer_workflows = Observer()
observer_workflows.schedule(
    file_watcher,
    path=str(workflows_path),
    recursive=True
)
observer_workflows.start()
```

### Why All Three Are Required

1. **Standards** - Core technical knowledge
2. **Usage** - How-to guides for AI agents
3. **Workflows** - Structured process definitions

Without workflows directory watching:
- ❌ New workflows not discoverable
- ❌ Metadata changes not indexed
- ❌ AI agents can't find workflow information

---

## What Indexing Strategy Should I Use?

The indexing strategy determines how content is broken into searchable chunks and stored in the vector database.

### File Types to Index

```python
INDEXABLE_EXTENSIONS = [
    ".md",      # Markdown documentation
    ".json"     # Workflow metadata (NEW)
]
```

### Special Handling for Workflow Metadata

Workflow `.json` files require **different chunking** than markdown:

```python
def chunk_workflow_metadata(metadata_path: Path) -> List[DocumentChunk]:
    """
    Chunk workflow metadata for semantic search.
    
    Strategy:
    1. Extract full metadata as one chunk (overview)
    2. Extract each phase as individual chunk (detailed)
    3. Add searchable text descriptions
    """
    with open(metadata_path) as f:
        metadata = json.load(f)
    
    chunks = []
    
    # Chunk 1: Full workflow overview
    overview_text = f"""
    Workflow: {metadata['workflow_type']}
    Description: {metadata['description']}
    Total Phases: {metadata['total_phases']}
    Duration: {metadata['estimated_duration']}
    Outputs: {', '.join(metadata['primary_outputs'])}
    """
    chunks.append(create_chunk(overview_text, metadata_path, "overview"))
    
    # Chunk 2-N: Individual phases
    for phase in metadata['phases']:
        phase_text = f"""
        Phase {phase['phase_number']}: {phase['phase_name']}
        Purpose: {phase['purpose']}
        Effort: {phase['estimated_effort']}
        Deliverables: {', '.join(phase['key_deliverables'])}
        Criteria: {', '.join(phase['validation_criteria'])}
        """
        chunks.append(create_chunk(phase_text, metadata_path, f"phase_{phase['phase_number']}"))
    
    return chunks
```

---

## How to Optimize Search Performance?

Search optimization ensures fast, relevant results for AI agent queries via `pos_search_project()`.

### Metadata for Better Search

Each indexed chunk should include:

```python
DocumentChunk(
    content=content,
    file_path=str(source_file),
    section_header=section_name,
    metadata={
        "type": "workflow" | "standard" | "usage",
        "workflow_type": "test_generation_v3",  # If workflow
        "phase_number": 0,  # If phase-specific
        "tags": ["testing", "python", "coverage"],
        "category": "workflows",
    }
)
```

### Query Examples

```python
# Discovery queries that SHOULD work:
await pos_search_project(content_type="standards", query="What workflows are available?")
await pos_search_project(content_type="standards", query="How do I generate tests for Python code?")
await pos_search_project(content_type="standards", query="What phases does test generation have?")
await pos_search_project(content_type="standards", query="What are the deliverables of Phase 2?")

# Should return relevant workflow metadata chunks
```

---

## How to Configure MCP Server for RAG?

MCP server configuration integrates the RAG engine with the Model Context Protocol for AI agent access.

### MCP Server Initialization

```python
def create_server(base_path: Optional[Path] = None) -> FastMCP:
    """Create MCP server with full workflow support."""
    
    base_path = base_path or Path(".praxis-os")
    
    # Define all paths
    standards_path = base_path / "universal" / "standards"
    usage_path = base_path / "universal" / "usage"
    workflows_path = base_path / "universal" / "workflows"  # NEW
    
    # Ensure index includes workflows
    _ensure_index_exists(
        index_path=base_path / ".cache" / "vector_index",
        standards_path=standards_path,
        usage_path=usage_path,
        workflows_path=workflows_path  # NEW - Required
    )
    
    # Initialize RAG engine
    rag_engine = RAGEngine(
        index_path=index_path,
        standards_path=standards_path.parent  # Parent to access all subdirs
    )
    
    # Initialize workflow engine with workflows path
    workflow_engine = WorkflowEngine(
        state_manager=state_manager,
        rag_engine=rag_engine,
        workflows_base_path=workflows_path  # NEW
    )
    
    return mcp
```

---

## How to Test RAG Configuration?

Testing ensures RAG is properly indexing content and returning relevant results for AI agent queries.

### Verification Checklist

After configuring MCP RAG with workflows:

```python
# 1. Verify workflow directory is watched
✅ File watcher active on universal/workflows/
✅ Changes to metadata.json trigger rebuild

# 2. Verify workflows are indexed
✅ Query returns workflow metadata:
   await pos_search_project(content_type="standards", query="test generation workflow")

# 3. Verify workflow loading works
✅ start_workflow returns workflow_overview
✅ Overview includes all phases
✅ Phase metadata is complete

# 4. Verify fallback works
✅ Workflows without metadata.json still work
✅ Fallback generates basic metadata

# 5. Verify hot reload works
✅ Edit metadata.json
✅ Wait 5 seconds (debounce)
✅ Query returns updated metadata
```

### Test Script

```python
import asyncio
from pathlib import Path

async def test_workflow_indexing():
    """Test that workflows are properly indexed."""
    
    # Test 1: Discovery
    result = await pos_search_project(
        query="What workflows are available for testing?",
        n_results=5
    )
    assert len(result["results"]) > 0
    assert any("test_generation" in r["content"].lower() 
               for r in result["results"])
    
    # Test 2: Phase discovery
    result = await pos_search_project(
        query="What phases does test_generation_v3 have?",
        n_results=5
    )
    assert len(result["results"]) > 0
    
    # Test 3: Start workflow includes overview
    session = await start_workflow(
        workflow_type="test_generation_v3",
        target_file="test.py"
    )
    assert "workflow_overview" in session
    assert session["workflow_overview"]["total_phases"] == 8
    
    print("✅ All workflow indexing tests passed")

if __name__ == "__main__":
    asyncio.run(test_workflow_indexing())
```

---

## What Common Configuration Errors Should I Avoid?

These common mistakes break RAG functionality or prevent content from being discoverable. Recognize and fix them.

### Error 1: Workflows Not Indexed

**Symptom:** `pos_search` doesn't return workflow information

**Cause:** `workflows_path` not passed to IndexBuilder

**Solution:**
```python
# BAD
builder = IndexBuilder(
    index_path=index_path,
    standards_path=standards_path,
    usage_path=usage_path
    # Missing workflows_path!
)

# GOOD
builder = IndexBuilder(
    index_path=index_path,
    standards_path=standards_path,
    usage_path=usage_path,
    workflows_path=workflows_path  # ✅ Added
)
```

### Error 2: Workflows Not Watched

**Symptom:** Metadata changes don't trigger index rebuild

**Cause:** File watcher not configured for workflows directory

**Solution:**
```python
# Add workflows directory watcher
observer_workflows = Observer()
observer_workflows.schedule(
    file_watcher,
    path=str(workflows_path),
    recursive=True
)
observer_workflows.start()
```

### Error 3: JSON Not Indexed

**Symptom:** Workflow metadata not searchable

**Cause:** `.json` files not included in indexable extensions

**Solution:**
```python
# Ensure .json files are indexed
if file_path.suffix in [".md", ".json"]:
    chunks = chunk_file(file_path)
    index_chunks(chunks)
```

---

## How to Migrate to Workflow-Enabled RAG?

Follow this checklist to upgrade existing RAG configuration to support workflow metadata indexing.

When upgrading existing repos to support workflow indexing:

- [ ] Add `workflows_path` parameter to `IndexBuilder.__init__`
- [ ] Update `IndexBuilder.source_paths` to include workflows
- [ ] Add `.json` to indexable file extensions
- [ ] Implement JSON chunking strategy
- [ ] Add workflows directory to file watcher
- [ ] Update `_ensure_index_exists` to pass workflows_path
- [ ] Update `create_server` to pass workflows_path
- [ ] Force rebuild index: `python scripts/build_rag_index.py --force`
- [ ] Test workflow discovery via search
- [ ] Verify `start_workflow` includes overview

---

## What Are RAG Performance Considerations?

Performance targets ensure RAG remains responsive and efficient for AI agent usage.

### Incremental Updates

Workflows should support **incremental indexing**:

```python
# When metadata.json changes:
# 1. Remove old chunks for that workflow
# 2. Generate new chunks
# 3. Add to index
# 4. Reload RAG engine

# This is faster than full rebuild (5s vs 60s)
```

### Caching Strategy

```python
# Workflow metadata should be cached in memory
class WorkflowEngine:
    def __init__(self):
        self._metadata_cache: Dict[str, WorkflowMetadata] = {}
    
    def load_workflow_metadata(self, workflow_type: str):
        # Check cache first
        if workflow_type in self._metadata_cache:
            return self._metadata_cache[workflow_type]
        
        # Load from file and cache
        metadata = self._load_from_file(workflow_type)
        self._metadata_cache[workflow_type] = metadata
        return metadata
```

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Configuring RAG** | `pos_search_project(content_type="standards", query="MCP RAG configuration")` |
| **Workflow indexing** | `pos_search_project(content_type="standards", query="workflow metadata indexing")` |
| **File watcher setup** | `pos_search_project(content_type="standards", query="file watcher RAG")` |
| **Vector index** | `pos_search_project(content_type="standards", query="configure vector index")` |
| **Embedding models** | `pos_search_project(content_type="standards", query="embedding configuration")` |
| **RAG performance** | `pos_search_project(content_type="standards", query="RAG performance")` |
| **Testing RAG** | `pos_search_project(content_type="standards", query="test RAG configuration")` |
| **Migration** | `pos_search_project(content_type="standards", query="migrate RAG configuration")` |

---

## 🔗 Related Standards

**Query workflow for complete RAG configuration:**

1. **Start with RAG config** → `pos_search_project(content_type="standards", query="MCP RAG configuration")` (this document)
2. **Understand workflow system** → `pos_search_project(content_type="standards", query="workflow system overview")` → `standards/workflows/workflow-system-overview.md`
3. **Learn workflow metadata** → `pos_search_project(content_type="standards", query="workflow metadata")` → `standards/workflows/workflow-metadata-standards.md`
4. **Use MCP tools** → `pos_search_project(content_type="standards", query="MCP usage guide")` → `usage/mcp-usage-guide.md`

**By Category:**

**Workflows:**
- `standards/workflows/workflow-system-overview.md` - Complete workflow system → `pos_search_project(content_type="standards", query="workflow system overview")`
- `standards/workflows/workflow-metadata-standards.md` - metadata.json structure → `pos_search_project(content_type="standards", query="workflow metadata")`
- `standards/workflows/workflow-construction-standards.md` - Building workflows → `pos_search_project(content_type="standards", query="workflow construction")`

**Usage:**
- `usage/mcp-usage-guide.md` - Using MCP tools → `pos_search_project(content_type="standards", query="MCP usage guide")`
- `usage/operating-model.md` - prAxIs OS operating model → `pos_search_project(content_type="standards", query="prAxIs OS operating model")`

**AI Assistant:**
- `standards/ai-assistant/rag-content-authoring.md` - Writing discoverable content → `pos_search_project(content_type="standards", query="RAG content authoring")`

---

**Remember:** Proper MCP RAG configuration ensures workflows are discoverable, searchable, and automatically updated. All three directories (standards, usage, workflows) must be indexed and watched!
