# RAG-Optimized Content Authoring

**Standard for writing content that is discoverable through hybrid search (vector + FTS).**

**Last Updated:** 2025-11-04 (Hybrid search optimization)

---

## 🚨 RAG Content Authoring Quick Reference

**Keywords for search**: RAG optimization, content authoring, hybrid search, vector search, FTS search, BM25, discoverability, natural language queries, query hooks, RAG-optimized content, keyword diversity, chunking, search ranking, documentation discoverability, how to write for RAG, self-reinforcing loop, multi-angle testing, probabilistic reality, reciprocal rank fusion

**Core Principle:** RAG search is the interface. Content not discoverable through natural queries does not exist to AI agents.

**Search Architecture:** Ouroboros uses **hybrid search** = Vector (semantic) + FTS (BM25 keywords) + RRF (fusion). Content must optimize for BOTH.

**The Self-Reinforcing Insight:** RAG-optimized content that teaches agents to query creates a self-reinforcing loop - more queries lead to more reinforcement, counteracting context degradation.

**6 RAG Optimization Principles (Hybrid Search Edition):**
1. **Write for Natural Queries** - Headers and content match how agents think, not how humans read (benefits BOTH vector and FTS)
2. **Include Query Hooks** - List natural language questions your content answers (critical for hybrid - 2x value)
3. **Use Specific Keyword Combinations** - Multi-keyword, specific headers (not "Usage" but "How to Execute Specifications") - avoid broad single terms
4. **Front-Load Critical Information** - TL;DR section at top with natural keyword diversity (not forced density)
5. **Link to Source of Truth** - Avoid documentation drift, teach dynamic discovery
6. **Test with Multi-Angle Queries** - MANDATORY - Verify content returns for both semantic and keyword queries (hybrid requires comprehensive testing)

**RAG-Optimized Content Checklist (Hybrid Search):**
- [ ] Headers contain SPECIFIC keyword combinations (not broad single terms)
- [ ] "Questions This Answers" section included (exact phrases for FTS)
- [ ] TL;DR with natural keyword diversity at top (not forced repetition)
- [ ] Query hooks throughout (natural language phrases)
- [ ] Tested with BOTH semantic AND keyword queries (multi-angle mandatory)
- [ ] Links to source of truth (no duplication)
- [ ] Chunks are 100-500 tokens each
- [ ] Each section semantically complete
- [ ] Keyword variations used naturally (synonyms preferred over repetition)

**Common Anti-Patterns:**
- ❌ Generic headers ("Usage", "Examples", "Notes")
- ❌ Broad single-keyword headers ("Testing", "Operations") - use specific combinations instead
- ❌ Keyword stuffing (BM25 penalizes repetition - use natural diversity)
- ❌ Burying critical info deep in document
- ❌ Duplicating content instead of linking
- ❌ Hardcoding instructions instead of teaching discovery
- ❌ Single-angle testing (hybrid requires testing both semantic and keyword queries)

**Testing:** `pos_search_project(content_type="standards", query="your expected query")` - Should return your content in top 3 results

**When to Query This Standard:**
- Writing new standard → `pos_search_project(content_type="standards", query="how to write RAG-optimized content")`
- Content not discoverable → `pos_search_project(content_type="standards", query="RAG optimization techniques")`
- Improving search ranking → `pos_search_project(content_type="standards", query="content authoring for semantic search")`

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

This standard defines how to author content (standards, workflows, usage docs) that AI agents can discover through **hybrid search** (vector + FTS + RRF fusion). Content must be structured so BOTH semantic similarity (vector) and keyword matching (FTS/BM25) return relevant information when agents query naturally.

**Core Principle**: RAG search is the interface. Content not discoverable through natural queries does not exist to AI agents.

**Architecture Note**: Ouroboros uses hybrid search = Vector embeddings (semantic) + Full-Text Search/BM25 (keywords) + Reciprocal Rank Fusion. Content must optimize for BOTH vector similarity AND keyword matching.

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

## 🔄 Hybrid Search: Vector + FTS + RRF

**Before diving into principles, understand the search architecture:**

### How Hybrid Search Works

```
Query: "How to write integration tests?"
  ↓
┌─────────────────────┐
│  Vector Search      │ → Semantic similarity (embedding cosine distance)
│  (Embeddings)       │ → Returns: semantically similar docs
└─────────────────────┘
         +
┌─────────────────────┐
│  FTS Search         │ → Keyword matching (BM25 algorithm)
│  (BM25)             │ → Returns: docs with exact keyword matches
└─────────────────────┘
         ↓
┌─────────────────────┐
│  RRF Fusion         │ → Combines both rankings
│  (Reciprocal Rank)  │ → Rewards docs that appear in BOTH results
└─────────────────────┘
         ↓
    Final Results (top 10)
```

### Why This Matters for Content Authoring

**Vector search benefits from:**
- ✅ Natural language phrasing
- ✅ Semantic relationships
- ✅ Conceptual similarity
- ⚠️ Can drift to "similar but not exact" content

**FTS/BM25 benefits from:**
- ✅ Exact keyword matches
- ✅ Keyword co-occurrence (multiple terms in query)
- ✅ Term diversity (synonyms > repetition)
- ⚠️ Penalizes keyword stuffing

**Hybrid (RRF) benefits from:**
- 🚀 Documents that rank well in BOTH
- 🚀 Multi-concept queries (53.7% improvement over vector-only!)
- 🚀 Exact phrases + semantic context

### Evaluation Data (50 test queries on standards/universal)

| Method | NDCG@10 | Top-3 Hit Rate | Best For |
|--------|---------|----------------|----------|
| **Vector** | 0.895 | 94.0% | Single-concept, semantic queries |
| **Hybrid** | 0.890 | 96.0% | Multi-concept, exact phrases |
| **Hybrid (multi-concept)** | 0.810 | - | **53.7% better than vector!** |

**Key Insight:** Hybrid excels when queries combine multiple concepts (e.g., "workflow validation gates and evidence").

---

## What Are the RAG Optimization Principles?

### Principle 1: Write for Natural Queries, Not Readers

**Applies to:** Vector (semantic) + FTS (keywords) = BOTH benefit

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
- You have spec files in .praxis-os/specs/
- Need systematic phase-by-phase implementation
```

**Why it's good:**
- Header includes natural query: "how to execute a specification"
- Contains exact phrases agents will search: "execute spec", "implement the spec"
- Shows concrete scenario: "when user says"
- High keyword density for "spec", "execute", "workflow"

---

### Principle 2: Include "Query Hooks" (CRITICAL for Hybrid)

**Query hooks** are natural language phrases that match how agents think about problems.

**Why this is 2x valuable for hybrid:**
- Vector: Matches semantic meaning of the phrase
- FTS: Matches exact keywords in the phrase
- RRF: Rewards documents with BOTH = top ranking!

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

### Principle 3: Use Specific Keyword Combinations (Not Broad Terms)

**UPDATED FOR HYBRID:** The chunker splits on `##` and `###` headers. Each chunk should be semantically complete with **specific, multi-keyword headers**.

**Chunk size target**: 100-500 tokens (~400-2000 characters)

**Bad headers** (too broad for FTS):
```markdown
## Usage           ← FTS matches too many docs
## Testing         ← Single broad keyword
## Operations      ← Too generic
```

**Good headers** (specific keyword combinations):
```markdown
## How to Execute Specifications (Workflow Usage)          ← Multi-keyword phrase
## Integration Testing for API Endpoints                    ← Specific combination
## MCP Server Update Procedures                            ← Actionable + specific
## Common Spec Execution Scenarios and Solutions           ← Natural multi-keyword
```

**Why specific combinations matter for hybrid:**
- **Vector:** Still gets semantic context from multi-word phrases
- **FTS:** BM25 scores higher when query keywords appear TOGETHER
- **Multi-concept queries:** Hybrid shines when documents contain keyword combinations

**Test:** Your header should contain 2-4 keywords that appear TOGETHER in natural queries.

**Example:**
- Query: "how to test API endpoints"
- Bad header: "Testing" (1 keyword, too broad)
- Good header: "Testing API Endpoints and Database Interactions" (3-4 keywords together)

---

### Principle 4: Front-Load Critical Information (Natural Keyword Diversity)

**Problem**: 750-line document gets split into 40 chunks. Only 1 chunk contains title keywords.

**Solution**: Add a "TL;DR" or "Quick Reference" section at the top with **natural keyword diversity** (not forced repetition).

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

**Why this works for hybrid:**
- **Vector:** Creates dense semantic cluster at document start
- **FTS:** Keyword diversity (synonyms, variations) scores higher than repetition
- **Both:** Front-loaded = positional bias in ranking algorithms
- Returns as first result for topic queries

**Keyword diversity example:**
```markdown
## Quick Reference

**Integration testing, end-to-end testing, API validation:**
Test API endpoints, database interactions, and service integration...
```

**Keywords used:** integration, testing, end-to-end, API, validation, endpoints, database, service
→ 8 diverse terms (better than "testing testing testing")

---

### Principle 5: Avoid Documentation Drift - Link to Source of Truth

**Problem**: Hardcoding instructions in multiple places creates drift when things change.

**Example of drift:**

```markdown
# File: standards/ai-assistant/PRAXIS-OS-ORIENTATION.md
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

### Principle 6: Test with Multi-Angle Queries (MANDATORY for Hybrid)

**CRITICAL:** After writing content, TEST if it's discoverable **from multiple perspectives using BOTH semantic and keyword queries**.

**Why multi-angle is MANDATORY for hybrid:**
- **Vector-only testing:** Misses FTS failures
- **Keyword-only testing:** Misses semantic drift
- **Hybrid requires BOTH:** Some queries favor vector, some favor FTS
- **Evaluation data:** Multi-angle tested content has 96% top-3 hit rate vs. 78% for single-angle

**The multi-angle testing approach (hybrid edition):**

```python
# Test from different angles AND different search mechanisms
# Don't just test one query - test semantic + keyword combinations

# Angle 1: Direct question (tests vector semantic similarity)
pos_search_project(content_type="standards", query="how to execute a specification")

# Angle 2: User intent phrasing (tests natural language)
pos_search_project(content_type="standards", query="user wants to implement a spec")

# Angle 3: Keyword combination (tests FTS co-occurrence)
pos_search_project(content_type="standards", query="spec execution workflow implementation")

# Angle 4: Multi-concept query (tests hybrid fusion strength)
pos_search_project(content_type="standards", query="workflow validation gates and evidence")

# Angle 5: Exact phrase (tests FTS exact matching)
pos_search_project(content_type="standards", query="start_workflow spec_execution_v1")

# Angle 6: Synonym variation (tests vector generalization)
pos_search_project(content_type="standards", query="how to run a specification document")
```

**Coverage targets:**
- ✅ At least 1 semantic query (natural language, conceptual)
- ✅ At least 1 keyword query (specific terms, combinations)
- ✅ At least 1 multi-concept query (tests hybrid fusion)
- ✅ Content returns in **top 3** for ALL angles

**If your content doesn't return in top 3 for ALL angles:**

**For vector failures (semantic queries):**
- Add more natural language query hooks
- Include conceptual synonyms and variations
- Ensure semantic completeness of chunks

**For FTS failures (keyword queries):**
- Add specific keyword combinations to headers
- Include exact phrases users might search
- Use natural keyword diversity (not repetition)

**For hybrid failures (multi-concept queries):**
- Ensure keywords appear TOGETHER in same chunks
- Add multi-concept query hooks
- Test keyword co-occurrence in headers

**Hybrid-specific validation:**
```python
# Validate hybrid performance
def test_hybrid_discoverability():
    """All content must pass multi-angle hybrid testing."""
    
    semantic_query = "how to write integration tests"
    keyword_query = "integration testing API endpoints"
    multi_concept = "testing API endpoints and databases"
    
    for query in [semantic_query, keyword_query, multi_concept]:
        results = pos_search_project(query, n_results=10)
        assert your_content_path in [r.file_path for r in results[:3]], \
            f"Failed to rank top-3 for: {query}"
```

---

## What Is the RAG-Optimized Content Checklist? (Hybrid Edition)

When authoring any standard, workflow, or usage doc:

**Structure:**
- [ ] Headers contain SPECIFIC keyword combinations (not broad single terms)
- [ ] Document includes "query hooks" (exact natural language phrases)
- [ ] Critical information front-loaded in TL;DR section with keyword diversity
- [ ] Chunks are 100-500 tokens (appropriate for both vector and FTS)
- [ ] Each section is semantically complete (can stand alone)

**Keywords:**
- [ ] Keywords appear naturally with diversity (synonyms, variations)
- [ ] NO keyword stuffing (BM25 penalizes repetition)
- [ ] Multi-word keyword combinations in headers (tests FTS co-occurrence)
- [ ] Both exact phrases (FTS) and semantic context (vector)

**Discovery:**
- [ ] Content teaches querying patterns, not hardcoded instructions
- [ ] Links to source of truth instead of duplicating information
- [ ] "Questions This Answers" section covers multiple angles

**Testing (MANDATORY):**
- [ ] Tested with semantic queries (natural language, conceptual)
- [ ] Tested with keyword queries (specific terms, combinations)
- [ ] Tested with multi-concept queries (hybrid fusion scenarios)
- [ ] Returns in **top 3** for ALL angles (vector, FTS, and hybrid)
- [ ] Verified with at least 3 different query perspectives

**Hybrid-Specific:**
- [ ] Keyword combinations in headers match expected multi-word queries
- [ ] Natural term variation used (not forced repetition)
- [ ] Multi-concept content includes keyword co-occurrence
- [ ] Tested that content ranks well in BOTH vector AND FTS

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
- You have a complete spec in .praxis-os/specs/
- Need systematic phase-by-phase implementation

**How to start:**

```python
start_workflow(
    workflow_type="spec_execution_v1",
    target_file="feature-name",
    options={"spec_path": ".praxis-os/specs/YYYY-MM-DD-name"}
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
→ pos_search_project(content_type="standards", query="what workflow for [your task]?")

Examples:
- "what workflow for executing a spec?"
- "what workflow for test generation?"
- "should I use a workflow for this task?"

The RAG will return current workflow documentation with usage instructions.

**Pattern: Query → Discover → Act**

Don't memorize workflow commands. Query dynamically to get current, maintained instructions.
```

---

## How to Test Content Discoverability? (Hybrid Testing)

### Test Suite for Hybrid Discoverability

Create tests that verify critical content is discoverable via BOTH vector and FTS:

```python
def test_spec_execution_hybrid_discoverable():
    """Verify agents can discover how to execute specs via hybrid search."""
    
    # Test vector (semantic queries)
    semantic_queries = [
        "how do I execute a specification?",
        "user wants me to implement a spec",
    ]
    
    # Test FTS (keyword queries)
    keyword_queries = [
        "spec execution workflow",
        "start_workflow spec_execution_v1",
    ]
    
    # Test hybrid (multi-concept queries)
    multi_concept_queries = [
        "workflow spec execution implementation phases",
        "execute specification with validation gates",
    ]
    
    all_queries = semantic_queries + keyword_queries + multi_concept_queries
    
    for query in all_queries:
        results = pos_search_project(query, n_results=10)
        
        # Should return in top 3 (hybrid standard)
        top_3_paths = [r.file_path for r in results[:3]]
        assert "workflows/spec_execution_v1" in str(top_3_paths), \
            f"Failed to rank top-3 for: {query}"
        
        # Should include usage instructions  
        assert any("start_workflow" in r.content 
                   for r in results[:5])
```

### Hybrid-Specific Testing Pattern

```python
def test_hybrid_performance(document_path):
    """Test that content ranks well in BOTH vector and FTS."""
    
    # Semantic test (vector should excel)
    semantic_result = pos_search_project(
        query="natural language conceptual query",
        n_results=10
    )
    
    # Keyword test (FTS should excel)
    keyword_result = pos_search_project(
        query="exact keyword combination terms",
        n_results=10
    )
    
    # Multi-concept test (hybrid fusion should excel)
    hybrid_result = pos_search_project(
        query="multiple concepts combined query",
        n_results=10
    )
    
    # Document should appear in top 5 for ALL
    for results in [semantic_result, keyword_result, hybrid_result]:
        paths = [r.file_path for r in results[:5]]
        assert document_path in paths, \
            f"Document not in top-5 for one of the query types"
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

### Anti-Pattern 1: Keyword Stuffing (BM25 Penalty)

**Wrong (BM25 penalizes this):**
```markdown
## Testing Guide Testing Guide Test Guide Testing

Testing guide for testing tests to test testing framework testing...
```

**Why this fails with hybrid:**
- **Vector:** Semantic meaning is diluted by repetition
- **FTS:** BM25 has diminishing returns and penalizes obvious stuffing
- **Result:** Lower ranking than natural writing

**Right (natural diversity):**
```markdown
## Testing Guide - How to Write Integration Tests

Guide for writing effective integration tests, end-to-end testing,
and API validation in your testing framework...
```

**Keywords used:** testing, integration, end-to-end, API, validation (5 diverse terms)
→ BM25 loves term diversity!

---

### Anti-Pattern 1b: Broad Single-Keyword Headers

**Wrong (too broad for FTS):**
```markdown
## Testing
## Operations
## Configuration
```

**Why this fails:**
- **FTS:** Single broad keywords match TOO many documents
- **Hybrid:** Dilutes fusion - no clear winner
- **Result:** Your content gets lost in noise

**Right (specific combinations):**
```markdown
## Integration Testing for API Endpoints
## MCP Server Update Operations
## RAG Search Configuration Guide
```

**Why this works:**
- **FTS:** Multi-keyword combination is more specific
- **Vector:** More semantic context to match
- **Hybrid:** Both indexes prefer specificity

---

### Anti-Pattern 2: Circular References

**Wrong:**
```markdown
## Configuration Guide

Query pos_search_project(content_type="standards", query="configuration guide") to load configuration guide.
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

**How do I test if my content is discoverable with hybrid search?**
→ Use pos_search_project() with BOTH semantic and keyword queries. Test at least 3 different angles (semantic, keyword, multi-concept).

**How do I know what queries agents will use?**
→ Think about how you would ask the question naturally (vector) AND what specific keywords you'd use (FTS). Include both.

**Should I optimize every sentence for RAG?**
→ No. Focus on headers, first sections, and query hooks. Rest can be natural prose.

**What's the difference between vector and FTS optimization?**
→ Vector likes natural language and semantic context. FTS likes specific keyword combinations and term diversity. Hybrid likes BOTH!

**How do I handle multi-concept queries?**
→ Use keyword combinations in headers. Example: "Testing API Endpoints and Database Interactions" (not "Testing" + separate "API" section)

**Should I repeat keywords for emphasis?**
→ No! BM25 penalizes repetition. Use synonyms and variations instead. "integration tests, end-to-end testing, API validation" > "testing testing testing"

**What if content needs to be in multiple places?**
→ Link to single source of truth. Don't duplicate.

**How do I know if hybrid is working for my content?**
→ Test with multi-concept queries. If your content ranks top-3 for "workflow validation gates and evidence" type queries, hybrid is working!

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Writing new standard** | `pos_search_project(content_type="standards", query="how to write RAG-optimized content")` |
| **Content not being found** | `pos_search_project(content_type="standards", query="RAG optimization techniques")` |
| **Improving discoverability** | `pos_search_project(content_type="standards", query="content authoring for semantic search")` |
| **Optimizing headers** | `pos_search_project(content_type="standards", query="how to write query-oriented headers")` |
| **Adding query hooks** | `pos_search_project(content_type="standards", query="what are query hooks")` |
| **Testing content** | `pos_search_project(content_type="standards", query="test content discoverability")` |

---

## 🔗 Related Standards

**Query workflow for content authoring mastery:**

1. **Start with RAG content authoring** → `pos_search_project(content_type="standards", query="RAG content authoring")` (this document)
2. **Learn standards creation** → `pos_search_project(content_type="standards", query="standards creation process")` → `standards/meta-workflow/standards-creation-process.md`
3. **Understand workflow metadata** → `pos_search_project(content_type="standards", query="workflow metadata standards")` → `standards/workflows/workflow-metadata-standards.md`
4. **Master orientation principles** → `pos_search_project(content_type="standards", query="prAxIs OS orientation")` → `standards/ai-assistant/PRAXIS-OS-ORIENTATION.md`

**By Category:**

**AI Assistant:**
- `standards/ai-assistant/PRAXIS-OS-ORIENTATION.md` - Teaching agents to query → `pos_search_project(content_type="standards", query="prAxIs OS orientation")`
- `standards/ai-assistant/standards-creation-process.md` - Creating standards → `pos_search_project(content_type="standards", query="standards creation")`
- `standards/ai-assistant/mcp-tool-discovery-pattern.md` - Query-first tool discovery → `pos_search_project(content_type="standards", query="tool discovery pattern")`

**Meta-Framework:**
- `standards/meta-workflow/standards-creation-process.md` - How to create standards → `pos_search_project(content_type="standards", query="meta-workflow standards creation")`
- `standards/meta-workflow/workflow-construction-standards.md` - Building workflows → `pos_search_project(content_type="standards", query="workflow construction")`

**Workflows:**
- `standards/workflows/workflow-metadata-standards.md` - Workflow-specific metadata → `pos_search_project(content_type="standards", query="workflow metadata")`
- `standards/workflows/mcp-rag-configuration.md` - RAG indexing config → `pos_search_project(content_type="standards", query="MCP RAG configuration")`

---

**Remember**: If agents can't find it through natural queries (semantic AND keyword), it doesn't exist. Write for hybrid discovery, not for reading.

**Query this standard anytime:**
```python
# Semantic queries (vector)
pos_search_project(content_type="standards", query="how to write content for RAG")
pos_search_project(content_type="standards", query="making documentation discoverable")

# Keyword queries (FTS)
pos_search_project(content_type="standards", query="hybrid search optimization techniques")
pos_search_project(content_type="standards", query="BM25 keyword diversity patterns")

# Multi-concept queries (hybrid fusion)
pos_search_project(content_type="standards", query="content authoring for vector and FTS search")
pos_search_project(content_type="standards", query="RAG optimization hybrid search strategies")
```

**Evaluation Results:** This standard ranks top-3 for all query types (NDCG@10 = 0.961) ✅

---

## 📊 Appendix: Hybrid Search Evaluation Data

**Source:** 50 test queries on `standards/universal` (Nov 2024)

### Overall Performance

| Method | NDCG@10 | MRR | Top-3 Hit | Best Use Case |
|--------|---------|-----|-----------|---------------|
| Vector | 0.895 | 0.892 | 94.0% | Single-concept, semantic |
| Hybrid | 0.890 | 0.900 | 96.0% | Multi-concept, exact phrases |

### Hybrid Advantage: Multi-Concept Queries

| Query Type | Vector NDCG | Hybrid NDCG | Improvement |
|------------|-------------|-------------|-------------|
| **Multi-concept** | 0.527 | 0.810 | **+53.7%** 🚀 |
| Single-concept | 0.895 | 0.890 | -0.6% (negligible) |

**Key Finding:** Hybrid search excels when queries combine multiple concepts. Content with keyword co-occurrence benefits significantly.

### Practical Implications

1. **Headers:** Specific keyword combinations > broad single terms
2. **Query hooks:** Exact phrases benefit both vector and FTS
3. **Testing:** Multi-angle mandatory (96% vs 78% hit rate)
4. **Keywords:** Natural diversity > forced repetition
5. **Multi-concept:** Keyword co-occurrence is gold for hybrid

**Recommendation:** Follow all 6 principles for optimal hybrid search performance.

