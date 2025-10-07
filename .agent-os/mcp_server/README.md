# Agent OS MCP Server

**Model Context Protocol server for Agent OS Enhanced with RAG, sub-agents, and workflow engine.**

## Components

### Core Server
- **`agent_os_rag.py`**: Main MCP server entry point
- **`rag_engine.py`**: LanceDB vector search with semantic retrieval
- **`workflow_engine.py`**: Phase-gated workflows with checkpoint validation
- **`state_manager.py`**: Workflow state persistence

### Sub-Agents (Specialized Tools)
- **`sub_agents/design_validator.py`**: Adversarial design review agent
- **`sub_agents/concurrency_analyzer.py`**: Thread safety analysis agent
- **`sub_agents/architecture_critic.py`**: System design review agent
- **`sub_agents/test_generator.py`**: Systematic test creation agent

## Installation

This MCP server is copied to `.agent-os/mcp_server/` in target projects during Agent OS installation.

## Dependencies

```txt
# MCP server dependencies
lancedb~=0.25.0          # Vector database
sentence-transformers>=2.0.0  # Local embeddings
mcp>=1.0.0               # Model Context Protocol
watchdog>=3.0.0          # File watching for hot reload
```

## Configuration

Configured in target project's `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "python",
      "args": ["${workspaceFolder}/.agent-os/mcp_server/agent_os_rag.py"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.agent-os"
      }
    }
  }
}
```

## Available Tools

### RAG Tools
- **`search_standards(query, n_results, filters)`**: Semantic search over standards
- **`start_workflow(workflow_type, target_file)`**: Initialize phase-gated workflow with complete overview
  - **NEW**: Returns `workflow_overview` with total phases, phase names, purposes, and deliverables
  - Eliminates need for separate `get_workflow_state()` call
  - See `WORKFLOW_METADATA_GUIDE.md` for details
- **`get_current_phase(session_id)`**: Get current phase requirements
- **`complete_phase(session_id, phase, evidence)`**: Submit evidence and advance
- **`get_workflow_state(session_id)`**: Query complete workflow state
- **`create_workflow(name, workflow_type, phases)`**: Generate new AI-assisted workflow frameworks
- **`current_date()`**: Get current date/time in ISO 8601 format (prevents AI date errors)

### Sub-Agent Tools
- **`validate_design(spec, target_domain)`**: Adversarial design review
- **`analyze_concurrency(code_snippet, language)`**: Thread safety analysis
- **`critique_architecture(design_doc)`**: System design review
- **`generate_tests(target_code, framework)`**: Systematic test generation

## Observability Integration (Optional)

The MCP server has no-op observability hooks by default. To add tracing:

**See `observability-integration.md` for detailed instructions on adding:**
- HoneyHive (AI-specific observability)
- OpenTelemetry (universal observability)
- Other platforms

User can request: "Add HoneyHive tracing" and you (Cursor agent) follow the guide.

## Version History

See `CHANGELOG.md` for version history and updates.

## Development

To modify the MCP server:
1. Make changes in `agent-os-enhanced/mcp_server/`
2. Test in a sample project
3. Update `CHANGELOG.md`
4. Tag release (semver)
5. Users update via: "Update Agent OS to latest version"

---

**Note:** The actual MCP server implementation files should be copied from the HoneyHive Python SDK's `.agent-os/mcp_server/` directory. This README serves as documentation for the structure.
