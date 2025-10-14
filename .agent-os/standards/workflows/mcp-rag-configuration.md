# MCP RAG Configuration Standards

**Standards for configuring MCP RAG with workflow support**

---

## 🎯 Purpose

This document defines standards for configuring the MCP RAG system to properly index and serve workflow metadata, standards, and usage documentation to AI agents.

---

## 📂 Directory Structure

### Required Directories

The MCP RAG system indexes content from three primary directories:

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

## ⚙️ IndexBuilder Configuration

### Initialization Parameters

```python
from pathlib import Path
from scripts.build_rag_index import IndexBuilder

builder = IndexBuilder(
    index_path=Path(".agent-os/.cache/vector_index"),
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
| `index_path` | Yes | Where to store vector index | `.agent-os/.cache/vector_index` |
| `standards_path` | Yes | Technical standards directory | `universal/standards` |
| `usage_path` | No | Usage guides directory | `universal/usage` |
| `workflows_path` | **Yes** | Workflow metadata directory | `universal/workflows` |
| `embedding_provider` | No | Embedding model provider | `"local"` (free) |
| `embedding_model` | No | Specific model to use | Provider-specific default |

---

## 🔄 File Watcher Configuration

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

## 📊 Indexing Strategy

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

## 🔍 Search Optimization

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
await search_standards("What workflows are available?")
await search_standards("How do I generate tests for Python code?")
await search_standards("What phases does test generation have?")
await search_standards("What are the deliverables of Phase 2?")

# Should return relevant workflow metadata chunks
```

---

## 🚀 Server Configuration

### MCP Server Initialization

```python
def create_server(base_path: Optional[Path] = None) -> FastMCP:
    """Create MCP server with full workflow support."""
    
    base_path = base_path or Path(".agent-os")
    
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

## 🧪 Testing Configuration

### Verification Checklist

After configuring MCP RAG with workflows:

```python
# 1. Verify workflow directory is watched
✅ File watcher active on universal/workflows/
✅ Changes to metadata.json trigger rebuild

# 2. Verify workflows are indexed
✅ Query returns workflow metadata:
   await search_standards("test generation workflow")

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
    result = await search_standards(
        query="What workflows are available for testing?",
        n_results=5
    )
    assert len(result["results"]) > 0
    assert any("test_generation" in r["content"].lower() 
               for r in result["results"])
    
    # Test 2: Phase discovery
    result = await search_standards(
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

## ⚠️ Common Configuration Errors

### Error 1: Workflows Not Indexed

**Symptom:** `search_standards` doesn't return workflow information

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

## 📖 Migration Checklist

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

## 🎯 Performance Considerations

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

## 📚 Related Standards

- [Workflow System Overview](workflow-system-overview.md) - Complete workflow system guide
- [MCP Usage Guide](../../usage/mcp-usage-guide.md) - Using MCP tools
- [Workflow Metadata Guide](../../../mcp_server/WORKFLOW_METADATA_GUIDE.md) - Creating metadata

---

## 🔍 Querying This Document

```python
# Configuration questions
await search_standards("How do I configure MCP RAG for workflows?")

# Troubleshooting
await search_standards("Why aren't my workflows being indexed?")

# Setup guidance
await search_standards("What directories does RAG index?")
```

---

**Remember:** Proper MCP RAG configuration ensures workflows are discoverable, searchable, and automatically updated. All three directories (standards, usage, workflows) must be indexed and watched!
