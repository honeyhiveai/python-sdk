# MCP Tool Discovery Guide

**Keywords for search**: MCP tools, what tools available, list tools, tool discovery, MCP protocol introspection, tools/list, tool parameters, tool schemas, how to find tools, what tools can I use, MCP capabilities

---

## 🎯 TL;DR - MCP Tool Discovery Quick Reference

**Core Principle:** Don't maintain static tool catalogs. Use MCP protocol's built-in `tools/list` for dynamic discovery. No documentation drift.

**Discovery Pattern:**
1. Your agent framework (Cursor, Cline, Windsurf) automatically calls `tools/list` on MCP server connection
2. You get complete tool schemas: names, parameters, types, descriptions
3. Query `pos_search(content_type="standards", query="how to use [tool-name]")` for usage patterns and examples

**Why Dynamic Discovery:**
- ✅ Always current (no stale documentation)
- ✅ No maintenance burden (MCP protocol handles it)
- ✅ Single source of truth (tool implementations)
- ✅ Works across all MCP-compatible agents

**Quick Actions:**
- Need to know what tools exist? → Check your agent's MCP tool list (auto-populated)
- Need usage examples? → `pos_search(content_type="standards", query="how to use [tool-name]")`
- Need parameter details? → Tool schema from `tools/list` has complete type information

---

## 🎯 Purpose

This standard defines how to discover available MCP tools dynamically using the MCP protocol, avoiding static documentation that drifts from reality.

**Questions This Answers:**
- What MCP tools are available in prAxIs OS?
- How do I find out what parameters a tool takes?
- What's the difference between tools/list and pos_search?
- Why shouldn't I create a static tool catalog?
- How do I discover tool capabilities across different MCP servers?

---

## ⚠️ The Problem Without This Standard

**Without dynamic discovery pattern:**

```
❌ Static documentation:
- Tool added to MCP server
- Documentation not updated
- Agent searches for tool
- Finds old docs (missing new tool)
- Cannot use new capability

❌ Parameter confusion:
- Tool parameter changes
- Documentation stale
- Agent uses old signature
- Tool call fails
- Debugging confusion

❌ Cross-agent incompatibility:
- Different MCP servers
- Different tool sets
- Documentation for one server
- Agent assumes same tools everywhere
- Failures in different environments
```

**Result:** Documentation drift, failed tool calls, confusion about capabilities.

---

## 📋 The Standard: Dynamic MCP Tool Discovery

### MCP Protocol Built-In Discovery

The MCP protocol provides `tools/list` endpoint that returns complete tool information:

**What tools/list Returns:**
```json
{
  "tools": [
    {
      "name": "pos_search",
      "description": "Semantic search over prAxIs OS documentation...",
      "inputSchema": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "Natural language question or topic"
          },
          "n_results": {
            "type": "integer",
            "default": 5,
            "description": "Number of chunks to return"
          }
        },
        "required": ["query"]
      }
    },
    ...
  ]
}
```

**Contains:**
- ✅ Tool name
- ✅ Description
- ✅ Complete parameter schema (types, required/optional, defaults)
- ✅ Return value schema
- ✅ Always current (generated from tool implementations)

### How Your Agent Uses tools/list

**Automatic Discovery (Cursor, Cline, Windsurf):**

1. **On MCP connection:**
   ```
   Agent framework connects to MCP server
   → Automatically calls tools/list
   → Receives complete tool schemas
   → Populates autocomplete/suggestions
   ```

2. **During conversation:**
   ```
   You: "Search for authentication patterns"
   → Agent sees: pos_search tool available
   → Agent generates: pos_search(content_type="standards", query="authentication patterns")
   → Tool executes via MCP
   ```

3. **Parameter validation:**
   ```
   Agent has full schema from tools/list
   → Knows: query (required, string)
   → Knows: n_results (optional, integer, default 5)
   → Generates correct tool call
   ```

### Discovery Pattern: Two-Tier Approach

**Tier 1: Tool Schema (from tools/list)**
- What tools exist
- Parameter names and types
- Required vs optional
- Default values

**Tier 2: Usage Patterns (from pos_search)**
- When to use which tool
- Common usage examples
- Decision guidance
- Error handling patterns

**Example Discovery Flow:**

```
1. Agent knows tools exist (tools/list gave schemas)

2. Agent needs usage guidance:
   pos_search(content_type="standards", query="how to use pos_search")
   
3. RAG returns:
   - When to query (before implementing)
   - Common query patterns
   - Multi-angle querying
   - Example searches

4. Agent generates informed tool call:
   pos_search(content_type="standards", query="race conditions in async handlers")
```

---

## ✅ Checklist: Proper Tool Discovery

When you need to understand MCP tools:

- [ ] **Don't create static tool catalogs** - Use tools/list (dynamic)
- [ ] **Trust your agent framework** - It already called tools/list
- [ ] **Query for usage patterns** - `pos_search(content_type="standards", query="how to use [tool]")`
- [ ] **Check tool descriptions** - Parameter types in schema
- [ ] **Test tool calls incrementally** - Start with required params
- [ ] **Follow self-teaching pattern** - Tool descriptions teach querying

When writing MCP tool implementations:

- [ ] **Write clear descriptions** - Explain what tool does
- [ ] **Document parameters inline** - Schema descriptions
- [ ] **Include usage guidance** - Point to pos_search
- [ ] **Use type hints** - Enables proper schema generation
- [ ] **Keep schemas current** - Generated from code (automatic)

---

## 📖 Examples

### Example 1: Discovering Available Tools

**❌ Wrong Approach (Static Documentation):**
```
Human: "What MCP tools are available?"
Agent: Reads static-tool-catalog.md
Agent: "Here are the tools... (document from 3 months ago)"
Problem: Missing tools added last week
```

**✅ Right Approach (Dynamic Discovery):**
```
Human: "What MCP tools are available?"
Agent: "Let me check the current MCP server capabilities"
Agent: [Accesses tools/list from framework's MCP connection]
Agent: "Current tools: pos_search, start_workflow, invoke_specialist..."
Benefit: Always current, no drift
```

### Example 2: Understanding Tool Parameters

**❌ Wrong Approach:**
```
Agent: Needs to use pos_search
Agent: pos_search(query="patterns")
Error: Missing required parameter 'n_results'? No, it has default
Problem: Confused by outdated docs
```

**✅ Right Approach:**
```
Agent: Needs to use pos_search
Agent: [Checks tool schema from tools/list]
Agent: See: query (required), n_results (optional, default=5)
Agent: pos_search(query="patterns")  # Correct!
Success: Used schema, not documentation
```

### Example 3: Learning Usage Patterns

**✅ Best Approach (Two-Tier Discovery):**
```
Agent: Need to search standards
Agent: [tools/list provides schema] ← Tier 1: Structure
Agent: pos_search(content_type="standards", query="how to use pos_search") ← Tier 2: Guidance
Agent: RAG returns: "Query before implementing, use natural language..."
Agent: pos_search(content_type="standards", query="how to handle race conditions in async code")
Success: Schema + Usage patterns = Effective use
```

---

## 🚫 Anti-Patterns

### Anti-Pattern 1: Creating Static Tool Catalogs

**❌ Don't do this:**
```markdown
# MCP Tools Catalog

## pos_search
Parameters: query (string), n_results (int, default 5)
Description: Search over standards...

## start_workflow
Parameters: workflow_type (string), target_file (string)
Description: Start workflow...

[Every new tool requires updating this doc]
[Parameter changes require doc updates]
[Inevitable drift from reality]
```

**✅ Do this instead:**
```markdown
# MCP Tool Discovery Guide

Use tools/list (automatic in your agent framework).
Query pos_search(content_type="standards", query="how to use [tool]") for usage patterns.

Always current. No maintenance. No drift.
```

### Anti-Pattern 2: Memorizing Tool Signatures

**❌ Don't do this:**
```
Agent: [Tries to remember tool signatures from previous session]
Agent: pos_search(query, results)  # Wrong parameter name!
Error: 'results' not recognized (correct: 'n_results')
```

**✅ Do this instead:**
```
Agent: [Checks current schema from tools/list]
Agent: Parameters: query, n_results (from schema)
Agent: pos_search(query="patterns", n_results=5)
Success: Current schema, not memory
```

### Anti-Pattern 3: Not Querying for Usage

**❌ Don't do this:**
```
Agent: [Has schema, tries to use tool without context]
Agent: pos_search(content_type="standards", query="test")  # Too vague
Result: Poor results (generic query)
```

**✅ Do this instead:**
```
Agent: pos_search(content_type="standards", query="how to use pos_search")
Agent: [Learns: natural language, specific queries, multi-angle]
Agent: pos_search(content_type="standards", query="how to handle database race conditions")
Result: Excellent results (informed query)
```

---

## 🔗 Related Standards

**Query workflow for tool discovery:**

1. **Understanding tools/list** → This document
2. **Writing for RAG** → `pos_search(content_type="standards", query="RAG content authoring")`
3. **Tool usage patterns** → `pos_search(content_type="standards", query="how to use [tool-name]")`
4. **Self-teaching tools** → Tool descriptions include query guidance

**By Category:**

**MCP Protocol:**
- `usage/mcp-usage-guide.md` → `pos_search(content_type="standards", query="MCP usage guide")`
- `standards/development/mcp-tool-design-best-practices.md` → `pos_search(content_type="standards", query="MCP tool design")`

**Tool Usage:**
- Query dynamically: `pos_search(content_type="standards", query="how to use [tool-name]")`
- Examples in orientation: `pos_search(content_type="standards", query="prAxIs OS orientation")`

---

## 📞 Questions?

**How do I see what tools are available right now?**
→ Your agent framework already called `tools/list`. Check your MCP tool list (Cursor: autocomplete, Cline: tool panel).

**What if I need usage examples for a tool?**
→ Query: `pos_search(content_type="standards", query="how to use [tool-name]")` for patterns and examples.

**Why not maintain a tool catalog document?**
→ Documentation drift. tools/list is always current (generated from code). No maintenance needed.

**What's the difference between tool schema and usage patterns?**
→ Schema (tools/list): Structure (parameters, types). Usage patterns (pos_search): When/how to use effectively.

**Do I need to call tools/list manually?**
→ No. Your agent framework (Cursor, Cline, etc.) automatically calls it on MCP connection.

---

**Version:** 1.0.0  
**Last Updated:** 2025-10-12  
**Next Review:** Quarterly or when MCP protocol changes

