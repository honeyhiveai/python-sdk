# RAG-Optimized Content Authoring

**Standard for writing content that is discoverable through semantic search.**

---

## 🚨 RAG Content Authoring Quick Reference

**Keywords for search**: RAG optimization, content authoring, semantic search, discoverability, natural language queries, query hooks, RAG-optimized content, keyword density, chunking, search ranking, documentation discoverability, how to write for RAG, self-reinforcing loop, multi-angle testing, probabilistic reality

**Core Principle:** RAG search is the interface. Content not discoverable through natural queries does not exist to AI agents.

**The Self-Reinforcing Insight:** RAG-optimized content that teaches agents to query creates a self-reinforcing loop - more queries lead to more reinforcement, counteracting context degradation.

**6 RAG Optimization Principles:**
1. **Write for Natural Queries** - Headers and content match how agents think, not how humans read
2. **Include Query Hooks** - List natural language questions your content answers
3. **Optimize Headers for Chunking** - Keyword-rich, specific headers (not "Usage" but "How to Execute Specifications")
4. **Front-Load Critical Information** - TL;DR section at top with high keyword density
5. **Link to Source of Truth** - Avoid documentation drift, teach dynamic discovery
6. **Test with Multi-Angle Queries** - Verify content returns from multiple perspectives (thorough, systematic approach)

**RAG-Optimized Content Checklist:**
- [ ] Headers contain searchable keywords
- [ ] "Questions This Answers" section included
- [ ] TL;DR with high keyword density at top
- [ ] Query hooks throughout (natural language phrases)
- [ ] Tested with natural queries (returns in top 3)
- [ ] Links to source of truth (no duplication)
- [ ] Chunks are 100-500 tokens each
- [ ] Each section semantically complete

**Common Anti-Patterns:**
- ❌ Generic headers ("Usage", "Examples", "Notes")
- ❌ Keyword stuffing
- ❌ Burying critical info deep in document
- ❌ Duplicating content instead of linking
- ❌ Hardcoding instructions instead of teaching discovery

**Testing:** `search_standards("your expected query")` - Should return your content in top 3 results

**When to Query This Standard:**
- Writing new standard → `search_standards("how to write RAG-optimized content")`
- Content not discoverable → `search_standards("RAG optimization techniques")`
- Improving search ranking → `search_standards("content authoring for semantic search")`

---

## ❓ Questions This Answers

1. "How to write content for RAG search?"
2. "How to make documentation discoverable?"
3. "What makes content RAG-optimized?"
4. "How to structure content for semantic search?"
5. "Why isn't my content being found by search?"
6. "What are query hooks?"
7. "How to optimize headers for chunking?"
8. "How to test if content is discoverable?"
9. "What are RAG content anti-patterns?"
10. "How to avoid documentation drift?"
11. "What is the self-reinforcing loop in RAG content?"
12. "Why test from multiple angles instead of single queries?"
13. "How does RAG content counteract context degradation?"
14. "What is multi-angle query testing?"

---

## 🎯 Purpose

This standard defines how to author content (standards, workflows, usage docs) that AI agents can discover through natural language RAG queries. Content must be structured so the chunking algorithm and ranking system return relevant information when agents query naturally.

**Core Principle**: RAG search is the interface. Content not discoverable through natural queries does not exist to AI agents.

---

## Why RAG Optimization Matters - The Fundamental Problem

**What happens when content isn't RAG-optimized:**

```
Agent queries: "how do I execute a specification?"
RAG returns: Irrelevant chunks, or nothing
Agent behavior: Guesses, hallucinates, or breaks patterns

Result: Agent never learns the correct approach
```

**What happens when content IS RAG-optimized:**

```
Agent queries: "how do I execute a specification?"
RAG returns: Workflow documentation with exact guidance
Agent behavior: Follows documented patterns

Result: Agent works correctly, system reinforces itself
```

### The Self-Reinforcing Loop

**RAG-optimized content creates a self-reinforcing behavior loop:**

```
1. Content teaches "query for guidance"
   ↓
2. Agent queries and finds helpful content
   ↓
3. Content reinforces "query liberally" message
   ↓
4. Agent queries more frequently
   ↓
5. More queries = more reinforcement = stronger behavior pattern

Result: Querying becomes the default behavior, counteracting probabilistic context degradation
```

**Why this matters:**
- Initial instructions fade as context grows (probabilistic reality)
- Each query retrieves the "query more" message
- Pattern becomes self-sustaining through repetition
- Works WITH AI's probabilistic nature, not against it

**Key insight**: Content that teaches agents to discover dynamically creates agents that query thoroughly and systematically - the foundation of quality work.

---

## What Are the RAG Optimization Principles?

### Principle 1: Write for Natural Queries, Not Readers

**Wrong mindset**: "I'm writing documentation for humans to read"

**Right mindset**: "I'm writing content that answers natural language questions"

**Example:**

**Bad** (not discoverable):
```markdown
## Workflow Usage

To use workflows, call the start function.
```

**Good** (discoverable):
```markdown
## How to Execute a Specification (Workflow Usage)

**When user says "execute spec" or "implement the spec":**

Use the spec_execution_v1 workflow:
```python
start_workflow("spec_execution_v1", target, options={"spec_path": "..."})
```

**Common scenarios:**
- User wants to implement a completed spec
- You have spec files in .agent-os/specs/
- Need systematic phase-by-phase implementation
```

**Why it's good:**
- Header includes natural query: "how to execute a specification"
- Contains exact phrases agents will search: "execute spec", "implement the spec"
- Shows concrete scenario: "when user says"
- High keyword density for "spec", "execute", "workflow"

---

### Principle 2: Include "Query Hooks"

**Query hooks** are natural language phrases that match how agents think about problems.

**Include these in every standard:**

```markdown
## Common Questions This Answers

- "How do I [task]?"
- "User wants me to [action]"
- "When should I use [feature]?"
- "What workflow for [scenario]?"
```

**Example:**

```markdown
## When to Use Workflows (Query Hooks)

**Questions this answers:**
- "Should I use a workflow for this task?"
- "User wants me to execute a spec - what do I do?"
- "How do I handle complex multi-phase work?"
- "What's the difference between workflows and ad-hoc coding?"

**Scenarios where you need workflows:**
- User says "execute this spec"
- Task has >3 phases or >5 days of work
- Need validation gates between phases
- Want state persistence and resumability
```

This chunk will now return for ANY of those natural queries!

---

### Principle 3: Optimize Headers for Chunking

The chunker splits on `##` and `###` headers. Each chunk should be semantically complete and keyword-rich.

**Chunk size target**: 100-500 tokens (~400-2000 characters)

**Bad headers** (not descriptive):
```markdown
## Usage
## Examples  
## Notes
```

**Good headers** (keyword-rich, specific):
```markdown
## How to Execute Specifications (Workflow Usage)
## Spec Execution Workflow Examples
## Common Spec Execution Scenarios and Solutions
```

**Why:**
- Headers become `section_header` metadata in chunks
- Headers appear in search results
- Headers should contain keywords agents will search for

---

### Principle 4: Front-Load Critical Information

**Problem**: 750-line document gets split into 40 chunks. Only 1 chunk contains title keywords.

**Solution**: Add a "TL;DR" or "Quick Reference" section at the top with high keyword density.

**Template:**

```markdown
# [Topic] - Complete Guide

## 🚨 [Topic] Quick Reference

**Critical information for [use case]:**

1. **[Key Point 1]** - [One sentence]
2. **[Key Point 2]** - [One sentence]  
3. **[Key Point 3]** - [One sentence]

**Keywords for search**: [topic], [synonym], [related term], [common query phrase]

**When to use**: [Common scenarios as natural language]

**Read complete guide below** for detailed patterns and examples.

---

[Rest of detailed content...]
```

**Why this works:**
- Creates one high-density chunk with all critical info
- Contains topic keywords multiple times (high relevance)
- Returns as first result for topic queries
- Includes explicit "search keywords" for ranking

---

### Principle 5: Avoid Documentation Drift - Link to Source of Truth

**Problem**: Hardcoding instructions in multiple places creates drift when things change.

**Example of drift:**

```markdown
# File: standards/ai-assistant/AGENT-OS-ORIENTATION.md
When user says "execute spec": start_workflow("spec_execution_v1", ...)

# File: usage/creating-specs.md  
To execute specs, use start_workflow("spec_execution_v1", ...)

# File: workflows/spec_execution_v1/README.md
[Actual current syntax that's different]

Result: Agent gets conflicting information!
```

**Solution: Single Source of Truth + Dynamic Discovery**

**In orientation file:**
```markdown
## How to Discover What to Do

When uncertain → Query for guidance:
- "how to execute a specification?"
- "user wants to implement spec"
- "what workflow for spec execution?"

The RAG will return current documentation from the workflow itself.

**Don't memorize commands. Query dynamically.**
```

**In workflow documentation:**
```markdown
## How to Use spec_execution_v1 Workflow

[Current, maintained instructions]
```

**Result**: Only ONE place to maintain, no drift possible.

---

### Principle 6: Test Discoverability with Multi-Angle Queries

After writing content, TEST if it's discoverable **from multiple perspectives**:

**The multi-angle testing approach:**

```python
# Test from different angles - thorough, systematic approach
# Don't just test one query - test how agents would think about this from different perspectives

# Angle 1: Direct question
search_standards("how to execute a specification")

# Angle 2: User intent phrasing
search_standards("user wants to implement a spec")

# Angle 3: Decision-making query
search_standards("when should I use workflows")

# Angle 4: Problem-solving query
search_standards("what workflow for spec execution")

# Angle 5: Tool discovery query
search_standards("what tools for implementing specs")
```

**Why multi-angle testing matters:**
- One query tests one keyword combination
- Real agents approach problems from different mental models
- Comprehensive discoverability = content ranks for multiple natural phrasings
- **Thorough, systematic testing = accuracy over speed**

**If your content doesn't return in top 3 for ALL angles**: 
- Add more natural language query hooks
- Increase keyword density in critical sections
- Front-load a TL;DR section
- Simplify headers to include keywords
- Add "Questions This Answers" section covering all angles

---

## What Is the RAG-Optimized Content Checklist?

When authoring any standard, workflow, or usage doc:

- [ ] Headers contain keywords agents will search for
- [ ] Document includes "query hooks" (natural language questions it answers)
- [ ] Critical information front-loaded in TL;DR section
- [ ] Keywords appear naturally throughout content (not keyword stuffing)
- [ ] Content teaches querying patterns, not hardcoded instructions
- [ ] Links to source of truth instead of duplicating information
- [ ] Tested with natural language queries (verified it returns)
- [ ] Chunks are 100-500 tokens (appropriate for semantic search)
- [ ] Each section is semantically complete (can stand alone)

---

## What Are RAG Optimization Examples?

### Example 1: Bad vs Good Workflow Documentation

**❌ Bad** (not discoverable):
```markdown
# spec_execution_v1

## Usage

Call the workflow with the spec path.

## Options

- spec_path: path to spec
```

**✅ Good** (discoverable):
```markdown
# Specification Execution Workflow (spec_execution_v1)

## How to Execute a Specification (When User Says "Implement Spec")

**Common scenarios:**
- User says "execute this spec" or "implement the spec"
- You have a complete spec in .agent-os/specs/
- Need systematic phase-by-phase implementation

**How to start:**

```python
start_workflow(
    workflow_type="spec_execution_v1",
    target_file="feature-name",
    options={"spec_path": ".agent-os/specs/YYYY-MM-DD-name"}
)
```

**What this workflow does:**
- Parses tasks from spec's tasks.md
- Executes phase-by-phase with validation gates
- Provides resumability if interrupted
- Enforces quality standards at each phase

**When NOT to use:**
- Small tasks (<30 minutes)
- Ad-hoc code changes
- Simple bug fixes

**Questions this answers:**
- "How do I execute a specification?"
- "User wants me to implement a spec - what do I do?"
- "What workflow for spec execution?"
```

---

### Example 2: Bad vs Good Orientation Content

**❌ Bad** (hardcoded, will drift):
```markdown
## Workflows

To execute specs, run:
start_workflow("spec_execution_v1", target, options={"spec_path": "..."})

For test generation, run:
start_workflow("test_generation_v3", target, options={...})
```

**✅ Good** (teaches discovery, no drift):
```markdown
## How to Discover What Workflow to Use

**You discover workflows dynamically through querying:**

When uncertain about what workflow to use:
→ search_standards("what workflow for [your task]?")

Examples:
- "what workflow for executing a spec?"
- "what workflow for test generation?"
- "should I use a workflow for this task?"

The RAG will return current workflow documentation with usage instructions.

**Pattern: Query → Discover → Act**

Don't memorize workflow commands. Query dynamically to get current, maintained instructions.
```

---

## How to Test Content Discoverability?

### Test Suite for Discoverability

Create tests that verify critical content is discoverable:

```python
def test_spec_execution_discoverable():
    """Verify agents can discover how to execute specs."""
    queries = [
        "how do I execute a specification?",
        "user wants me to implement a spec",
        "what workflow for spec execution?",
    ]
    
    for query in queries:
        results = search_standards(query, n_results=5)
        
        # Should return workflow documentation
        assert any("spec_execution_v1" in chunk.content 
                   for chunk in results.chunks)
        
        # Should include usage instructions  
        assert any("start_workflow" in chunk.content 
                   for chunk in results.chunks)
```

### Iteration Process

1. **Write content** using principles above
2. **Test queries** - Does it return for natural questions?
3. **Check ranking** - Is it in top 3 results?
4. **Refine** - Add query hooks, increase keyword density
5. **Retest** - Verify improvements
6. **Ship** - Content is now discoverable

---

## What Are RAG Content Anti-Patterns?

### Anti-Pattern 1: Keyword Stuffing

**Wrong:**
```markdown
## Testing Guide Testing Guide Test Guide Testing

Testing guide for testing tests to test testing framework testing...
```

**Right:**
Use keywords naturally in context, not repetitively.

```markdown
## Testing Guide - How to Write Tests

Guide for writing effective tests in your testing framework...
```

---

### Anti-Pattern 2: Circular References

**Wrong:**
```markdown
## Configuration Guide

Query search_standards("configuration guide") to load configuration guide.
```

**Right:**
```markdown
## Configuration Quick Reference

**Critical settings:**
- Database: connection_string, pool_size
- Cache: redis_url, ttl_seconds
- API: rate_limit, timeout

For complete guide, continue reading below.
```

---

### Anti-Pattern 3: Burying Critical Info

**Wrong:**
```markdown
# Complete Guide (750 lines)

## Background
[50 lines of history]

## Architecture  
[100 lines of design]

## Usage (finally!)
[Critical info at line 500]
```

**Right:**
```markdown
# Complete Guide

## Quick Reference (Critical Info)
[All critical info in first 50 lines]

## Detailed Background
[Additional context for those who need it]
```

---

## ❓ Frequently Asked Questions

**How do I test if my content is discoverable?**
→ Use search_standards() with natural queries you expect agents to use

**How do I know what queries agents will use?**
→ Think about how you would ask the question naturally. Include those phrases as query hooks.

**Should I optimize every sentence for RAG?**
→ No. Focus on headers, first sections, and query hooks. Rest can be natural prose.

**What if content needs to be in multiple places?**
→ Link to single source of truth. Don't duplicate.

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Writing new standard** | `search_standards("how to write RAG-optimized content")` |
| **Content not being found** | `search_standards("RAG optimization techniques")` |
| **Improving discoverability** | `search_standards("content authoring for semantic search")` |
| **Optimizing headers** | `search_standards("how to write query-oriented headers")` |
| **Adding query hooks** | `search_standards("what are query hooks")` |
| **Testing content** | `search_standards("test content discoverability")` |

---

## 🔗 Related Standards

**Query workflow for content authoring mastery:**

1. **Start with RAG content authoring** → `search_standards("RAG content authoring")` (this document)
2. **Learn standards creation** → `search_standards("standards creation process")` → `standards/meta-workflow/standards-creation-process.md`
3. **Understand workflow metadata** → `search_standards("workflow metadata standards")` → `standards/workflows/workflow-metadata-standards.md`
4. **Master orientation principles** → `search_standards("Agent OS orientation")` → `standards/ai-assistant/AGENT-OS-ORIENTATION.md`

**By Category:**

**AI Assistant:**
- `standards/ai-assistant/AGENT-OS-ORIENTATION.md` - Teaching agents to query → `search_standards("Agent OS orientation")`
- `standards/ai-assistant/standards-creation-process.md` - Creating standards → `search_standards("standards creation")`
- `standards/ai-assistant/MCP-TOOLS-GUIDE.md` - Dynamic discovery → `search_standards("MCP dynamic discovery")`

**Meta-Framework:**
- `standards/meta-workflow/standards-creation-process.md` - How to create standards → `search_standards("meta-workflow standards creation")`
- `standards/meta-workflow/workflow-construction-standards.md` - Building workflows → `search_standards("workflow construction")`

**Workflows:**
- `standards/workflows/workflow-metadata-standards.md` - Workflow-specific metadata → `search_standards("workflow metadata")`
- `standards/workflows/mcp-rag-configuration.md` - RAG indexing config → `search_standards("MCP RAG configuration")`

---

**Remember**: If agents can't find it through natural queries, it doesn't exist. Write for discovery, not for reading.

**Query this standard anytime:**
```python
search_standards("how to write content for RAG")
search_standards("content authoring for semantic search")
search_standards("making documentation discoverable")
```

