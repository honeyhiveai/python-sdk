# Technical Specifications
# Agent OS MCP/RAG Evolution

**Document Version:** 1.0  
**Date:** October 3, 2025  
**Status:** Draft - Specification Phase  
**Owner:** AI-Assisted Development Platform Team

---

## 1. SYSTEM ARCHITECTURE

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ Cursor IDE (User Interface Layer)                              │
│ - AI Assistant (Claude Sonnet 4.5)                             │
│ - Editor Interface                                              │
│ - MCP Client (built into Cursor)                               │
└────────────────┬────────────────────────────────────────────────┘
                 │ MCP Protocol (stdio)
                 │ - Structured JSON messages
                 │ - Tool calls and responses
                 │
┌────────────────▼────────────────────────────────────────────────┐
│ MCP Server Layer (Python Process)                              │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ agent_os_rag.py (Main MCP Server)                       │   │
│ │ - Tool registration and routing                         │   │
│ │ - Request/response handling                             │   │
│ │ - Error handling and logging                            │   │
│ └───────┬─────────────────────────────────────────────────┘   │
│         │                                                       │
│ ┌───────▼────────────┐  ┌──────────────────┐  ┌────────────┐ │
│ │ Workflow Engine    │  │ RAG Engine       │  │ State Mgr  │ │
│ │ - Phase gating     │  │ - Vector search  │  │ - Workflow │ │
│ │ - Evidence check   │  │ - Chunking       │  │ - Artifacts│ │
│ │ - State tracking   │  │ - Fallback       │  │ - Progress │ │
│ └────────────────────┘  └──────────────────┘  └────────────┘ │
└────────────────┬────────────────────────────────────────────────┘
                 │ File I/O
┌────────────────▼────────────────────────────────────────────────┐
│ Data Layer (Local Filesystem)                                  │
│                                                                 │
│ .praxis-os/                                                      │
│ ├── standards/              (Source of truth, 198 .md files)   │
│ ├── .cache/                 (Gitignored, generated)            │
│ │   ├── vector_index/       (ChromaDB SQLite)                  │
│ │   └── state/              (Workflow state JSON)              │
│ └── mcp_servers/            (100% AI-authored code)            │
│     └── agent_os_rag.py     (This file)                        │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

**Cursor IDE:**
- Hosts AI assistant
- Launches MCP server on startup
- Routes MCP tool calls
- Displays results to user

**MCP Server (agent_os_rag.py):**
- Exposes MCP-compliant tools
- Routes requests to appropriate engines
- Manages workflow state
- Handles errors gracefully

**Workflow Engine:**
- Enforces phase sequence
- Validates checkpoints
- Tracks progress
- Manages artifacts

**RAG Engine:**
- Semantic search over Agent OS
- Document chunking
- Vector indexing
- Fallback to grep

**State Manager:**
- Persists workflow state
- Manages artifacts
- Handles resume/restart
- Cleans up old sessions

---

## 2. DATA MODELS

### 2.1 Workflow State Model

```python
class WorkflowState:
    """Represents current state of test generation workflow."""
    
    session_id: str              # Unique session identifier
    workflow_type: str           # "test_generation_v3", "production_code_v2"
    target_file: str             # File being worked on
    current_phase: int           # Current phase number (1-8)
    completed_phases: List[int]  # Phases completed
    phase_artifacts: Dict[int, PhaseArtifact]  # Outputs from each phase
    checkpoints: Dict[int, CheckpointStatus]   # Checkpoint pass/fail status
    created_at: datetime         # Session start time
    updated_at: datetime         # Last update time
    
    def to_dict(self) -> dict:
        """Serialize to JSON for persistence."""
        
    @classmethod
    def from_dict(cls, data: dict) -> "WorkflowState":
        """Deserialize from JSON."""
        
    def can_access_phase(self, phase: int) -> bool:
        """Check if phase is accessible given current state."""
        return phase == self.current_phase
    
    def complete_phase(self, phase: int, artifacts: PhaseArtifact) -> None:
        """Mark phase complete and advance."""
        self.completed_phases.append(phase)
        self.phase_artifacts[phase] = artifacts
        self.current_phase = phase + 1
        self.updated_at = datetime.now()
```

### 2.2 Phase Artifact Model

```python
class PhaseArtifact:
    """Artifacts produced by completing a phase."""
    
    phase_number: int            # Which phase produced this
    evidence: Dict[str, Any]     # Required evidence for checkpoint
    outputs: Dict[str, Any]      # Phase outputs (function lists, etc.)
    commands_executed: List[CommandExecution]  # Commands run
    timestamp: datetime          # When artifact created
    
    # Example for Phase 1 (Method Verification):
    # evidence = {
    #     "function_count": 21,
    #     "method_count": 15,
    #     "branch_count": 36,
    #     "ast_command_output": "grep -n 'def ' output..."
    # }
    # outputs = {
    #     "functions": ["compile", "parse", "validate", ...],
    #     "methods": ["_compile_provider", "_validate_syntax", ...],
    #     "internal_functions": ["_helper1", "_helper2"]
    # }
```

### 2.3 Document Chunk Model

```python
class DocumentChunk:
    """Represents a chunk of Agent OS documentation."""
    
    chunk_id: str                # MD5 hash of content
    file_path: str               # Source file path
    section_header: str          # Header this chunk belongs to
    content: str                 # The actual text content
    tokens: int                  # Token count
    metadata: ChunkMetadata      # Additional metadata
    embedding: Optional[List[float]]  # Vector embedding (1536 dims)
    
class ChunkMetadata:
    """Metadata for better retrieval."""
    
    framework_type: str          # "test_v3", "production_v2", etc.
    phase: Optional[int]         # If phase-specific
    category: str                # "requirement", "example", "reference"
    tags: List[str]              # ["mocking", "ast", "coverage", ...]
    is_critical: bool            # Contains MANDATORY/CRITICAL markers
    parent_headers: List[str]    # Breadcrumb of headers
```

### 2.4 Query Request/Response Models

```python
class SearchQuery:
    """Request for semantic search."""
    
    query: str                   # Natural language query
    n_results: int = 5          # Number of chunks to return
    filter_tags: Optional[List[str]] = None  # Filter by tags
    filter_phase: Optional[int] = None       # Filter by phase
    
class SearchResult:
    """Response from semantic search."""
    
    chunks: List[DocumentChunk]  # Retrieved chunks
    total_tokens: int            # Sum of chunk tokens
    retrieval_method: str        # "vector" or "grep" (fallback)
    relevance_scores: List[float]  # Similarity scores
    query_time_ms: float         # Query execution time
    
class WorkflowQuery:
    """Request for workflow-specific content."""
    
    session_id: str              # Workflow session
    action: str                  # "get_current_phase", "complete_phase", etc.
    evidence: Optional[Dict] = None  # Evidence for checkpoint
    
class WorkflowResponse:
    """Response from workflow engine."""
    
    phase_content: str           # Current phase content
    checkpoint_status: str       # "passed", "failed", "pending"
    missing_evidence: List[str]  # If checkpoint failed
    next_phase_unlocked: bool    # Whether advanced
    artifacts_available: Dict    # From previous phases
```

---

## 3. API SPECIFICATIONS

### 3.1 MCP Tool Definitions

#### Tool 1: search_standards

**Purpose:** Semantic search over Agent OS content

```python
@mcp_server.tool()
async def pos_search_project(action="search_standards", query=
    query: str,
    n_results: int = 5,
    filter_phase: Optional[int] = None,
    filter_tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Semantic search over Agent OS documentation.
    
    Args:
        query: Natural language question or topic
        n_results: Number of chunks to return (default 5)
        filter_phase: Optional phase number filter (1-8)
        filter_tags: Optional tags filter (e.g., ["mocking", "ast"])
    
    Returns:
        {
            "results": [
                {
                    "content": "chunk text...",
                    "file": ".praxis-os/standards/...",
                    "section": "header name",
                    "relevance_score": 0.95,
                    "tokens": 500
                }
            ],
            "total_tokens": 2500,
            "retrieval_method": "vector",  # or "grep"
            "query_time_ms": 45.2
        }
    
    Examples:
        # Get Phase 1 guidance
        pos_search_project(action="search_standards", query="Phase 1 method verification requirements", filter_phase=1)
        
        # Get mocking guidance
        pos_search_project(action="search_standards", query="how to determine mocking boundaries", filter_tags=["mocking"])
        
        # General query
        pos_search_project(action="search_standards", query="quality targets for test generation")
    """
```

#### Tool 2: start_workflow

**Purpose:** Initialize new workflow session

```python
@mcp_server.tool()
async def start_workflow(
    workflow_type: str,
    target_file: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Start new workflow session with phase gating.
    
    Args:
        workflow_type: "test_generation_v3" or "production_code_v2"
        target_file: File being worked on (e.g., "config/dsl/compiler.py")
        options: Optional workflow configuration
    
    Returns:
        {
            "session_id": "uuid-string",
            "workflow_type": "test_generation_v3",
            "total_phases": 8,
            "current_phase": 1,
            "phase_content": {
                "phase_number": 1,
                "phase_name": "Method Verification",
                "requirements": "...",
                "commands": [...],
                "checkpoint_criteria": {...}
            },
            "acknowledgment_required": "I acknowledge the critical importance..."
        }
    
    Example:
        start_workflow(
            workflow_type="test_generation_v3",
            target_file="src/honeyhive/tracer/core.py"
        )
    """
```

#### Tool 3: get_current_phase

**Purpose:** Retrieve current phase content for session

```python
@mcp_server.tool()
async def get_current_phase(
    session_id: str
) -> Dict[str, Any]:
    """
    Get current phase content and requirements.
    
    Args:
        session_id: Workflow session identifier
    
    Returns:
        {
            "session_id": "uuid",
            "current_phase": 2,
            "total_phases": 8,
            "phase_content": {
                "phase_number": 2,
                "phase_name": "Logging Analysis",
                "requirements": "...",
                "commands": [...],
                "checkpoint_criteria": {...}
            },
            "artifacts_from_previous_phases": {
                "phase_1": {
                    "function_count": 21,
                    "functions": ["compile", "parse", ...]
                }
            }
        }
    
    Example:
        get_current_phase(session_id="abc-123")
    """
```

#### Tool 4: complete_phase

**Purpose:** Submit evidence and attempt to complete phase

```python
@mcp_server.tool()
async def complete_phase(
    session_id: str,
    phase: int,
    evidence: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Submit evidence and attempt phase completion.
    
    Args:
        session_id: Workflow session identifier
        phase: Phase number being completed
        evidence: Evidence dictionary matching checkpoint criteria
    
    Returns:
        {
            "checkpoint_passed": True,
            "phase_completed": 1,
            "next_phase_unlocked": True,
            "next_phase_content": {
                "phase_number": 2,
                "phase_name": "Logging Analysis",
                ...
            }
        }
        
        OR if checkpoint fails:
        
        {
            "checkpoint_passed": False,
            "missing_evidence": [
                "function_count (required: int)",
                "ast_command_output (required: str)"
            ],
            "current_phase_content": {
                # Returns same phase content
            }
        }
    
    Example:
        complete_phase(
            session_id="abc-123",
            phase=1,
            evidence={
                "function_count": 21,
                "method_count": 15,
                "branch_count": 36,
                "ast_command_output": "grep output...",
                "functions_list": ["compile", "parse", ...]
            }
        )
    """
```

#### Tool 5: get_workflow_state

**Purpose:** Query current workflow state

```python
@mcp_server.tool()
async def get_workflow_state(
    session_id: str
) -> Dict[str, Any]:
    """
    Get complete workflow state for debugging/resume.
    
    Args:
        session_id: Workflow session identifier
    
    Returns:
        {
            "session_id": "uuid",
            "workflow_type": "test_generation_v3",
            "target_file": "config/dsl/compiler.py",
            "current_phase": 3,
            "completed_phases": [1, 2],
            "progress_percentage": 25,
            "phase_artifacts": {
                "1": {"function_count": 21, ...},
                "2": {"logger_calls": 15, ...}
            },
            "can_resume": True
        }
    """
```

---

## 4. CORE ALGORITHMS

### 4.1 Document Chunking Algorithm

**Objective:** Split Agent OS markdown into retrievable chunks

```python
class AgentOSChunker:
    """Intelligent chunking preserving semantic boundaries."""
    
    MAX_CHUNK_TOKENS = 500
    MIN_CHUNK_TOKENS = 100
    
    def chunk_document(self, filepath: str) -> List[DocumentChunk]:
        """
        Chunk markdown preserving headers and code blocks.
        
        Algorithm:
        1. Parse markdown into sections by ## headers
        2. For each section:
           a. If < MAX_TOKENS: Single chunk
           b. If > MAX_TOKENS:
              - Split on ### sub-headers first
              - If still > MAX_TOKENS, split on paragraphs
              - If still > MAX_TOKENS, split on sentences
        3. Preserve context by including parent headers
        4. Add metadata (framework, phase, tags)
        5. Generate chunk ID (MD5 hash)
        
        Example:
        Input: test-framework.md with 8 phases
        Output: ~40 chunks (5 per phase)
        - Phase 1 header + requirements (1 chunk)
        - Phase 1 commands (1 chunk)
        - Phase 1 examples (1 chunk)
        - Phase 1 checkpoint (1 chunk)
        - Phase 1 enforcement (1 chunk)
        """
        
        content = self._read_file(filepath)
        sections = self._parse_sections(content)
        chunks = []
        
        for section in sections:
            if self._token_count(section.content) <= self.MAX_CHUNK_TOKENS:
                chunks.append(self._create_chunk(section))
            else:
                sub_chunks = self._split_large_section(section)
                chunks.extend(sub_chunks)
        
        return chunks
    
    def _extract_metadata(self, chunk: DocumentChunk) -> ChunkMetadata:
        """
        Extract metadata for better retrieval.
        
        Extracts:
        - Framework type from file path
        - Phase number from headers
        - Category from section type
        - Tags from content keywords
        - Critical markers (MANDATORY, CRITICAL)
        """
```

### 4.2 Semantic Search Algorithm

**Objective:** Find most relevant chunks for query

```python
class RAGEngine:
    """Semantic search with fallback."""
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict] = None
    ) -> SearchResult:
        """
        Semantic search with graceful degradation.
        
        Algorithm:
        1. Generate query embedding (OpenAI or local)
        2. Query ChromaDB vector store
        3. If filters provided, apply post-filtering
        4. Rank by similarity score
        5. Return top N results
        6. If vector search fails, fall back to grep
        
        Example:
        Query: "Phase 1 method verification"
        Steps:
        1. Embed query → [0.23, 0.45, ..., 0.12] (1536 dims)
        2. Vector search → Top 10 similar chunks
        3. Filter by phase=1 → 5 chunks
        4. Rank by score → [0.95, 0.93, 0.89, 0.87, 0.85]
        5. Return top 5
        """
        
        try:
            # Primary: Vector search
            return self._vector_search(query, n_results, filters)
        except Exception as e:
            # Fallback: Grep search
            logger.warning(f"Vector search failed: {e}, falling back to grep")
            return self._grep_fallback(query, n_results)
    
    def _vector_search(self, query: str, n_results: int, filters: Dict) -> SearchResult:
        """ChromaDB vector search."""
        
    def _grep_fallback(self, query: str, n_results: int) -> SearchResult:
        """Grep-based fallback search."""
```

### 4.3 Phase Gating Algorithm

**Objective:** Enforce sequential phase execution

```python
class WorkflowEngine:
    """Phase gating and checkpoint validation."""
    
    def get_phase_content(
        self,
        session_id: str,
        requested_phase: int
    ) -> Dict[str, Any]:
        """
        Return phase content only if accessible.
        
        Algorithm:
        1. Load workflow state from session_id
        2. Check if requested_phase == current_phase
        3. If yes: Return phase content
        4. If no: Return error + current phase content
        5. Include artifacts from completed phases
        
        Example:
        State: {current_phase: 2, completed_phases: [1]}
        Request: phase=3
        Result: ERROR - "Complete Phase 2 first" + Phase 2 content
        
        Request: phase=2
        Result: SUCCESS + Phase 2 content + Phase 1 artifacts
        """
        
        state = self._load_state(session_id)
        
        if requested_phase != state.current_phase:
            return {
                "error": "Phase sequence violation",
                "message": f"Complete Phase {state.current_phase} first",
                "current_phase_content": self._get_content(state.current_phase),
                "artifacts": self._get_artifacts(state)
            }
        
        return {
            "phase_content": self._get_content(requested_phase),
            "artifacts": self._get_artifacts(state)
        }
    
    def validate_checkpoint(
        self,
        phase: int,
        evidence: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate evidence against checkpoint criteria.
        
        Algorithm:
        1. Load checkpoint requirements for phase
        2. Check each required field exists in evidence
        3. Validate field types match requirements
        4. Validate field values meet criteria (e.g., count > 0)
        5. Return (passed, missing_fields)
        
        Example Phase 1 Checkpoint:
        Required: {
            "function_count": int (> 0),
            "ast_command_output": str (non-empty),
            "functions_list": List[str] (length > 0)
        }
        
        Evidence: {
            "function_count": 21,
            "ast_command_output": "def compile()...",
            "functions_list": ["compile", "parse"]
        }
        
        Result: (True, [])
        """
```

---

## 5. FILE STRUCTURE

### 5.1 New Files Created (All AI-Authored)

```
.praxis-os/
├── mcp_servers/
│   ├── __init__.py                      # Empty
│   ├── agent_os_rag.py                  # Main MCP server (500 lines)
│   ├── workflow_engine.py               # Phase gating logic (300 lines)
│   ├── rag_engine.py                    # Semantic search (400 lines)
│   ├── state_manager.py                 # State persistence (200 lines)
│   ├── chunker.py                       # Document chunking (300 lines)
│   └── models.py                        # Data models (200 lines)
├── scripts/
│   ├── build_rag_index.py               # Index builder (200 lines)
│   ├── validate_rag.py                  # Validation script (150 lines)
│   └── benchmark_rag.py                 # Performance testing (150 lines)
└── .cache/                              # Gitignored
    ├── vector_index/                    # ChromaDB SQLite
    │   ├── chroma.sqlite3               # Vector DB
    │   ├── metadata.json                # Index metadata
    │   └── embeddings/                  # Binary embeddings
    └── state/                           # Workflow state
        └── sessions/                    # Session JSON files

.cursor/
└── mcp_servers.json                     # Cursor config (20 lines)

.gitignore
# Added lines:
.praxis-os/.cache/
.praxis-os/mcp_servers/__pycache__/
```

### 5.2 Modified Files

```
.praxis-os/mcp_servers/requirements.txt
# Added:
chromadb>=0.4.0
mcp>=1.0.0
openai>=1.0.0            # Optional
sentence-transformers>=2.0.0  # Optional
honeyhive>=0.1.0         # For dogfooding/observability

.gitignore
# Added:
.praxis-os/.cache/
```

---

## 6. CONFIGURATION

### 6.1 Cursor MCP Configuration

```json
// .cursor/mcp_servers.json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "python",
      "args": [
        ".praxis-os/mcp_servers/agent_os_rag.py"
      ],
      "env": {
        "AGENT_OS_INDEX_PATH": ".praxis-os/.cache/vector_index",
        "AGENT_OS_STATE_PATH": ".praxis-os/.cache/state",
        "AGENT_OS_STANDARDS_PATH": ".praxis-os/standards",
        "AGENT_OS_LOG_LEVEL": "INFO",
        "HH_API_KEY": "${HH_API_KEY}",
        "HONEYHIVE_PROJECT": "agent-os-mcp-rag",
        "HONEYHIVE_ENABLED": "true"
      }
    }
  }
}
```

### 6.2 MCP Server Configuration

```python
# .praxis-os/mcp_servers/agent_os_rag.py

CONFIG = {
    "index_path": os.getenv("AGENT_OS_INDEX_PATH", ".praxis-os/.cache/vector_index"),
    "state_path": os.getenv("AGENT_OS_STATE_PATH", ".praxis-os/.cache/state"),
    "standards_path": os.getenv("AGENT_OS_STANDARDS_PATH", ".praxis-os/standards"),
    "log_level": os.getenv("AGENT_OS_LOG_LEVEL", "INFO"),
    
    "chunking": {
        "max_tokens": 500,
        "min_tokens": 100,
        "overlap": 50  # Token overlap between chunks
    },
    
    "retrieval": {
        "default_n_results": 5,
        "max_n_results": 20,
        "relevance_threshold": 0.7
    },
    
    "performance": {
        "query_timeout_ms": 5000,
        "index_build_timeout_s": 120,
        "cache_ttl_s": 3600
    },
    
    "embeddings": {
        "provider": "openai",  # or "local"
        "model": "text-embedding-3-small",
        "dimensions": 1536
    },
    
    "observability": {
        "honeyhive_enabled": os.getenv("HONEYHIVE_ENABLED", "true") == "true",
        "honeyhive_project": os.getenv("HONEYHIVE_PROJECT", "agent-os-mcp-rag"),
        "trace_queries": True,
        "trace_workflows": True,
        "trace_checkpoints": True,
        "dogfooding_purpose": "Validate HoneyHive for AI agent observability"
    }
}
```

---

## 7. ERROR HANDLING

### 7.1 Error Categories

```python
class AgentOSError(Exception):
    """Base exception for Agent OS MCP system."""

class WorkflowError(AgentOSError):
    """Workflow-related errors (phase sequence, checkpoint)."""

class RetrievalError(AgentOSError):
    """RAG retrieval errors (vector search, index)."""

class StateError(AgentOSError):
    """State management errors (corruption, missing)."""

class ConfigError(AgentOSError):
    """Configuration errors (missing paths, invalid config)."""
```

### 7.2 Error Handling Strategy

```python
def handle_mcp_request(request: MCPRequest) -> MCPResponse:
    """Top-level error handling for all MCP requests."""
    
    try:
        # Route to appropriate handler
        result = route_request(request)
        return MCPResponse(success=True, data=result)
        
    except WorkflowError as e:
        # Workflow violations are expected (return helpful guidance)
        return MCPResponse(
            success=False,
            error_type="workflow_violation",
            message=str(e),
            recovery_hint="Complete current phase checkpoint first"
        )
    
    except RetrievalError as e:
        # RAG failures fall back to grep
        logger.warning(f"RAG failed: {e}, using fallback")
        result = fallback_grep_search(request.query)
        return MCPResponse(
            success=True,
            data=result,
            warning="Using fallback search (degraded mode)"
        )
    
    except Exception as e:
        # Unexpected errors never crash Cursor
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return MCPResponse(
            success=False,
            error_type="internal_error",
            message="Internal error occurred, check logs",
            recovery_hint="System remains functional, retry operation"
        )
```

---

## 8. PERFORMANCE SPECIFICATIONS

### 8.1 Target Performance Metrics

```python
PERFORMANCE_TARGETS = {
    "query_latency": {
        "p50": 30,   # milliseconds
        "p95": 100,  # milliseconds
        "p99": 200   # milliseconds
    },
    
    "index_build": {
        "initial_build": 60,     # seconds for 198 files
        "incremental_build": 30,  # seconds for changed files
        "background_rebuild": True  # Non-blocking
    },
    
    "memory": {
        "mcp_server_base": 50,   # MB
        "vector_index_loaded": 30,  # MB
        "per_session_state": 1,   # MB
        "total_max": 100          # MB
    },
    
    "disk": {
        "vector_index": 10,   # MB
        "state_files": 1,     # MB
        "logs": 10            # MB
    },
    
    "throughput": {
        "queries_per_second": 100,
        "concurrent_sessions": 5
    }
}
```

### 8.2 Optimization Strategies

**Query Optimization:**
- Cache recent query results (TTL: 1 hour)
- Pre-filter by phase/tags before vector search
- Limit vector search to top 20, then rank
- Use approximate nearest neighbor (default in ChromaDB)

**Index Optimization:**
- Build index on first run, persist to disk
- Incremental updates (only changed files)
- Background rebuilds (serve stale during rebuild)
- Compression for embedding storage

**Memory Optimization:**
- Lazy loading of index (only when needed)
- LRU cache for chunks (max 100 chunks)
- Periodic state cleanup (delete old sessions)
- Streaming responses (don't load all in memory)

---

## 9. SECURITY & PRIVACY

### 9.1 Security Considerations

**Local-Only Processing:**
- All data remains on local machine
- No external API calls (except optional embeddings during build)
- MCP server binds to localhost only
- No network listening

**Data Isolation:**
- Each workflow session isolated
- State files not shared between users
- No telemetry or usage tracking
- No logging of sensitive data

**Resource Limits:**
- Memory cap enforced (100MB)
- CPU throttling if exceeds 50%
- Disk space check before index build
- Timeout on long-running queries

### 9.2 Privacy Guarantees

```python
PRIVACY_GUARANTEES = {
    "no_external_calls": "Except optional OpenAI embeddings during setup",
    "no_data_collection": "Zero telemetry, analytics, or tracking",
    "local_processing": "All queries processed on local machine",
    "no_logging_of_content": "Only log errors, not user data",
    "state_cleanup": "Sessions deleted after 7 days of inactivity"
}
```

---

## 10. TESTING SPECIFICATIONS

### 10.1 Unit Test Coverage

**Target:** 90%+ line coverage, 85%+ branch coverage

```python
test_categories = {
    "workflow_engine": [
        "test_phase_gating_enforcement",
        "test_checkpoint_validation",
        "test_state_persistence",
        "test_artifact_management",
        "test_invalid_phase_access"
    ],
    
    "rag_engine": [
        "test_semantic_search_accuracy",
        "test_chunk_retrieval",
        "test_fallback_to_grep",
        "test_metadata_filtering",
        "test_relevance_scoring"
    ],
    
    "chunker": [
        "test_markdown_parsing",
        "test_section_splitting",
        "test_token_counting",
        "test_metadata_extraction",
        "test_chunk_id_generation"
    ],
    
    "state_manager": [
        "test_state_save_load",
        "test_session_cleanup",
        "test_corruption_recovery",
        "test_concurrent_access"
    ]
}
```

### 10.2 Integration Test Coverage

```python
integration_tests = {
    "end_to_end_workflow": [
        "test_complete_test_generation_flow",
        "test_phase_progression_with_evidence",
        "test_checkpoint_failure_handling",
        "test_session_resume_after_restart"
    ],
    
    "cursor_integration": [
        "test_mcp_server_startup",
        "test_tool_calls_from_cursor",
        "test_error_handling_in_cursor",
        "test_performance_under_load"
    ],
    
    "quality_preservation": [
        "test_same_outcomes_as_current_approach",
        "test_pylint_scores_maintained",
        "test_coverage_percentages_maintained"
    ]
}
```

---

## 11. DEPLOYMENT SPECIFICATIONS

### 11.1 Installation Process

```bash
# Step 1: Clone repository (unchanged)
git clone https://github.com/honeyhiveai/python-sdk.git
cd python-sdk

# Step 2: Install MCP dependencies (new)
pip install -r .praxis-os/mcp_servers/requirements.txt

# Step 3: Build initial index (automatic on first Cursor launch)
# - OR - 
python .praxis-os/scripts/build_rag_index.py

# Step 4: Launch Cursor (unchanged)
cursor .
# MCP server starts automatically
```

### 11.2 First-Run Experience

```python
first_run_flow = {
    "step_1": {
        "trigger": "Cursor launches, no index detected",
        "action": "Show notification: 'Building Agent OS index (one-time, ~60s)'",
        "progress": "Display progress bar"
    },
    
    "step_2": {
        "action": "Build vector index from .praxis-os/standards/",
        "duration": "45-60 seconds",
        "output": ".praxis-os/.cache/vector_index/"
    },
    
    "step_3": {
        "action": "MCP server ready",
        "notification": "Agent OS RAG ready - enhanced context efficiency enabled",
        "ready_for_queries": True
    }
}
```

### 11.3 Update/Maintenance

```bash
# When Agent OS content changes:
# Option 1: Automatic (default)
# - System detects content hash change
# - Rebuilds index in background
# - Continues serving queries during rebuild

# Option 2: Manual rebuild
python .praxis-os/scripts/build_rag_index.py --force

# Option 3: Clean rebuild
rm -rf .praxis-os/.cache/vector_index/
# Next Cursor launch rebuilds
```

---

**Document Status:** Complete - Ready for Review  
**Next Document:** tasks.md (Implementation Task Breakdown)  
**Total Lines:** 1,000+ (comprehensive technical specification)  
**AI Authorship:** 100%

