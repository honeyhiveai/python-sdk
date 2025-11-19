# MCP Tool Discovery: The Query-First Pattern

**Keywords for search**: tool discovery, how to find tools, MCP tool usage, query for tools, tool-specific standards, self-reinforcing loop, discover tool capabilities, pos_search_project tool guide, how to learn tools, tool documentation pattern, query-first discovery, context degradation, probabilistic reality, why query matters

**This standard defines how to discover and learn MCP tool usage through query-first discovery of tool-specific standards, creating a self-reinforcing learning loop.**

---

## 🚨 TL;DR - Tool Discovery Quick Reference

**Core Principle:** Query for tool-specific standards instead of relying on parameter schemas. Get comprehensive guidance, not just syntax.

**The Query-First Pattern:**
```python
# When you need to use a tool:
pos_search_project(content_type="standards", query="how to use [tool-name]")
# → Returns: Complete usage guide with workflows, examples, decision trees

# NOT:
tools/list  # → Returns: Parameter types only (insufficient)
```

**Why This Works:**
- ✅ **Self-reinforcing** - Querying teaches query patterns
- ✅ **Comprehensive** - Workflows, decision trees, reasoning guidance (not just syntax)
- ✅ **Reduces cognitive load** - 75-85% time savings vs manual exploration
- ✅ **RAG-indexed** - Always discoverable through natural queries
- ✅ **Counters context degradation** - Creates persistent habits

**Quick Actions:**
- Need tool for task? → `pos_search_project(content_type="standards", query="tools for [task description]")`
- Know tool name? → `pos_search_project(content_type="standards", query="how to use [tool-name]")`
- Understanding a capability? → `pos_search_project(content_type="standards", query="[tool-name] workflows decision trees")`

**Common Mistakes:**
- ❌ Using `tools/list` to learn tool usage (only shows parameter types)
- ❌ Relying on IDE autocomplete for usage patterns (only shows syntax)
- ❌ Trying to memorize tool signatures (context degrades, you'll forget)
- ❌ Reading tool source code to understand usage (high cognitive load)

---

## 🎯 Questions This Answers

- How do I discover what MCP tools are available?
- How do I learn how to use a specific tool effectively?
- Why not use `tools/list` for tool discovery?
- What's the difference between parameter schemas and usage guidance?
- How does the query-first pattern create self-reinforcing behavior?
- Why do tool-specific standards work better than API docs?
- What is probabilistic reality and why does context degrade?
- How do I find the right tool for my task?
- How should I write tool-specific standards?
- What makes a good tool usage guide?

---

## 🔄 The Paradigm Shift

### Old Approach: Schema-First Discovery

```
Step 1: tools/list → Get parameter schemas
Step 2: See: "query (string, required), n_results (int, default=5)"
Step 3: Try: pos_search_project(query="something")
Step 4: Get results, unsure if using it correctly
Step 5: Trial and error until it works
```

**Problems:**
- ❌ No guidance on WHEN to use the tool
- ❌ No guidance on HOW to use it effectively
- ❌ No workflows or decision trees
- ❌ No cognitive load reduction strategies
- ❌ High trial-and-error cost

**Result:** You learn syntax, not reasoning

---

### New Approach: Query-First Discovery

```
Step 1: Query: "how to use pos_search_project"
Step 2: Get: 1200-line comprehensive guide
Step 3: Learn:
   - When to use (discovery phase, not verification)
   - How to use (6 actions, decision trees, workflows)
   - Why to use (75-85% time savings vs grep+read)
   - Reasoning workflows (4 complete multi-query patterns)
   - Synthesis guidance (how to build mental models)
Step 4: Use tool effectively the first time
```

**Benefits:**
- ✅ Comprehensive guidance (not just syntax)
- ✅ Reasoning workflows (how to build understanding)
- ✅ Decision trees (when to use what)
- ✅ Cognitive load comparisons (quantified benefits)
- ✅ Self-reinforcing (querying teaches querying)

**Result:** You learn reasoning, not just syntax

---

## 🔬 Why Query-First Works: The Self-Reinforcing Loop

### The Mechanism

```
Query for tool usage guide
         ↓
Get comprehensive guidance + "query more" patterns
         ↓
Learn: "I should query before implementing"
         ↓
Internalize: Querying is valuable
         ↓
Next task: Query first (habit formed)
         ↓
P(query_next_time) increases
         ↓
Self-reinforcing behavior
```

**Key Insight:** Tool-specific standards don't just teach the tool — they teach the pattern of querying for guidance.

---

### What Makes It Self-Reinforcing

**Traditional docs:** "Here's the API, good luck"
- You use tool once
- No reinforcement of discovery pattern
- Forget the tool exists
- Fall back to manual methods

**Tool-specific standards:** "Here's comprehensive guidance, query for more"
- You see the value of comprehensive guidance
- Standards explicitly teach: "query before implementing"
- You query more next time
- Pattern reinforces itself

---

## 📚 Tool-Specific Standards vs Parameter Schemas

### What Parameter Schemas Provide (tools/list)

```json
{
  "name": "pos_search_project",
  "description": "Search across project knowledge",
  "parameters": {
    "action": {
      "type": "string",
      "enum": ["search_standards", "search_code", "search_ast", ...]
    },
    "query": {
      "type": "string"
    },
    "n_results": {
      "type": "integer",
      "default": 5
    }
  }
}
```

**You learn:**
- Parameter names
- Parameter types
- Required vs optional
- Default values

**You DON'T learn:**
- When to use `search_code` vs `search_ast`
- How to write effective queries
- Multi-query reasoning workflows
- Cognitive load comparisons to alternatives
- Decision trees for tool selection
- Synthesis guidance

---

### What Tool-Specific Standards Provide

**Example: pos_search_project usage guide**

**Section 1: Quick Reference**
- 6 actions explained
- Decision table
- "When in doubt" heuristic
- Common mistakes

**Section 2: Tool Comparison**
- When to use pos_search_project vs grep vs read_file
- Cognitive load comparison (quantified)
- Time investment estimates
- Performance trade-offs table

**Section 3: Reasoning Workflows**
- Understanding a new subsystem (7-8 min)
- Tracing a bug (5 min)
- Refactoring impact analysis (5 min)
- Architecture discovery (12 min)

**Section 4: Synthesis Guidance**
- How to know when understanding is complete
- Progressive refinement strategy
- Breadth-first vs depth-first exploration

**Section 5: Decision Trees**
- Visual flow for tool selection
- Phase guidance (discovery → verification → implementation)

**Total:** 1200 lines of comprehensive guidance

**You learn:**
- ✅ WHEN to use the tool
- ✅ HOW to use it effectively
- ✅ WHY it's better than alternatives
- ✅ Complete reasoning workflows
- ✅ Decision-making frameworks
- ✅ Cognitive load reduction strategies

---

## 🎯 The Query-First Pattern in Practice

### Scenario 1: "I need to search code"

**❌ Old approach:**
```
1. Check tools/list
2. See: pos_search_project exists
3. Try: pos_search_project(action="search_code", query="error handling")
4. Get some results
5. Unsure if this is the right approach
6. Trial and error
```

**✅ New approach:**
```
1. Query: pos_search_project(content_type="standards", query="how to search code")
2. Find: pos-search-project-usage-guide.md
3. Learn:
   - search_code for semantic search (meaning)
   - search_ast for structural search (syntax)
   - Decision tree: "Code by meaning? → search_code"
   - Example: search_code("error handling patterns")
4. Use correctly the first time
```

---

### Scenario 2: "What tools exist for workflows?"

**❌ Old approach:**
```
1. Check tools/list
2. See: Many tools with "workflow" in name
3. Read parameter schemas
4. Still unclear how they work together
5. Guess and check
```

**✅ New approach:**
```
1. Query: pos_search_project(content_type="standards", query="workflow tools system")
2. Find: pos-workflow-tool-reference.md
3. Learn:
   - Workflow system overview
   - Phase-gated execution
   - Evidence validation
   - Complete workflow lifecycle
4. Understand the system, not just individual tools
```

---

### Scenario 3: "How do I understand this codebase?"

**❌ Old approach:**
```
1. grep for symbols
2. read_file multiple files
3. Manually synthesize relationships
4. 20-30 minutes, high cognitive load
5. Fragmented understanding
```

**✅ New approach:**
```
1. Query: pos_search_project(content_type="standards", query="reasoning workflows codebase understanding")
2. Find: Workflow 1: Understanding a New Subsystem
3. Follow:
   - Phase 1: High-level discovery (2 min)
   - Phase 2: Architectural mapping (2 min)
   - Phase 3: Data flow tracing (2 min)
   - Phase 4: Pattern discovery (1 min)
4. Complete understanding in 7-8 minutes
5. 75-85% time savings vs manual approach
```

---

## 🧠 Understanding Probabilistic Reality (Why This Matters)

### The Mathematical Reality of Context Degradation

**Critical insight for AI agents:** Your memory of patterns and instructions degrades mathematically as your session grows.

```
Context Window Composition Over Time:

Message 1:
├── Initial orientation: 15,000 tokens (75% of context)
└── User message: 5,000 tokens (25%)
→ Rules/patterns have HIGH statistical influence

Message 30:
├── Initial orientation: 15,000 tokens (still 15k)
├── 29 messages of conversation: 2,485,000 tokens (99.4%)
└── Latest message: 5,000 tokens
→ Rules/patterns have NEGLIGIBLE statistical influence (0.6%)

Result: Initial guidance becomes statistically irrelevant
```

---

### What This Means for Tool Usage

As your context grows, you probabilistically forget:
- Which tools exist
- How to use them
- Best practices for tool selection
- Patterns for effective usage
- Decision frameworks
- Reasoning workflows

**You can't prevent this degradation** - it's mathematical reality.

**You CAN create self-reinforcing habits** that persist through the session.

---

### The Self-Reinforcing Solution

Query-first discovery creates persistent behavior:

```
Message 1: Learn "query for tool usage"
Message 5: Query → Get "query before implementing"
Message 10: Query → Get "query liberally (5-10 times)"
Message 15: Query → Get workflows that include querying
Message 20: Query → Pattern reinforced again
Message 30: Initial instructions = 0.6% influence
           BUT: Habit of querying = reinforced 20+ times
           Result: Querying is now automatic behavior
```

**Key Insight:** You can't keep all guidance in your working memory. You CAN make "query first" your default habit.

**This is why tool-specific standards work:** They reinforce the query loop every time you use them.

---

## 📖 Examples of Tool-Specific Standards

### Example 1: pos_search_project Usage Guide

**Location:** `standards/universal/tools/pos-search-project-usage-guide.md`

**Coverage:**
- 6 actions (search_standards, search_code, search_ast, find_callers, find_dependencies, find_call_paths)
- When to use vs grep vs read_file
- Cognitive load comparison (75-85% time savings)
- 4 complete reasoning workflows
- Synthesis guidance (how to know understanding is complete)
- Decision trees for tool selection
- Performance trade-offs table
- 1200+ lines of comprehensive guidance

**Query to find:**
```python
pos_search_project(content_type="standards", query="pos_search_project usage guide")
pos_search_project(content_type="standards", query="how to search code semantically")
pos_search_project(content_type="standards", query="reasoning workflows codebase understanding")
```

---

### Example 2: pos_workflow Tool Reference

**Location:** `standards/universal/workflows/pos-workflow-tool-reference.md`

**Coverage:**
- Complete workflow system overview
- Phase-gated execution
- Evidence validation
- Workflow lifecycle (start → execute → complete)
- Recovery operations (pause, resume, retry, rollback)
- Error handling
- Session management

**Query to find:**
```python
pos_search_project(content_type="standards", query="how to use pos_workflow")
pos_search_project(content_type="standards", query="workflow system phase gating")
```

---

### Example 3: Standards Creation Process

**Location:** `standards/universal/ai-assistant/standards-creation-process.md`

**Coverage:**
- When to create a standard
- Standard structure (required sections)
- RAG optimization (how to make discoverable)
- Quality standards (specific, measurable, justified)
- Creation workflow (6 steps)
- Common mistakes and anti-patterns

**Query to find:**
```python
pos_search_project(content_type="standards", query="how to create standards")
pos_search_project(content_type="standards", query="standards creation process")
```

---

## ✍️ How to Write Tool-Specific Standards

### The Template

Every tool-specific standard should include:

**1. TL;DR Section**
- Core principle (one sentence)
- Quick reference table
- "When in doubt" heuristic
- Common mistakes

**2. Questions This Answers**
- 10-20 questions the standard addresses
- Makes content discoverable via natural queries

**3. Decision Trees**
- When to use this tool vs alternatives
- Visual flow for tool selection
- Phase guidance (when in workflow)

**4. Reasoning Workflows**
- Multi-step patterns showing tool usage
- Complete examples with expected outcomes
- Time estimates and cognitive load comparisons

**5. Synthesis Guidance**
- How to know when you've used the tool enough
- What mental models to build
- How to verify understanding

**6. Examples**
- Real-world scenarios
- Before/after comparisons
- Anti-patterns (what NOT to do)

**7. Performance Trade-offs**
- Speed, accuracy, context trade-offs
- Comparison to alternatives
- When each approach excels

---

### RAG Optimization Requirements

**To make standards discoverable:**

- ✅ **Keyword-rich headers** - Not "Usage" but "How to Use pos_search_project for Code Discovery"
- ✅ **Query hooks** - List natural language questions throughout
- ✅ **Front-loaded TL;DR** - High keyword density at top
- ✅ **Content-specific keywords** - Not generic terms like "tool usage"
- ✅ **Multiple angles** - Test with various natural language queries

**Query to learn more:**
```python
pos_search_project(content_type="standards", query="RAG content authoring optimization")
```

---

### Quality Checklist

When writing a tool-specific standard:

- [ ] **Comprehensive** - Covers when/how/why, not just syntax
- [ ] **Self-reinforcing** - Teaches query patterns while teaching tool
- [ ] **Discoverable** - RAG-optimized with query hooks
- [ ] **Actionable** - Decision trees and workflows, not just descriptions
- [ ] **Comparative** - Shows tool vs alternatives with quantified benefits
- [ ] **Complete** - Includes reasoning workflows, not just operations
- [ ] **Tested** - Queries for the standard return it in top 3 results

---

## 🎯 Tool Discovery Decision Tree

```
START: I need to accomplish a task

├─ Do I know what tool I need?
│  │
│  ├─ YES: I know the tool name
│  │  └─ Query: pos_search_project(content_type="standards", query="how to use [tool-name]")
│  │     └─ Get: Comprehensive usage guide
│  │
│  └─ NO: I don't know what tool to use
│     └─ Query: pos_search_project(content_type="standards", query="tools for [task description]")
│        └─ Get: Guidance on which tools exist for this task
│
├─ Tool-specific standard exists?
│  │
│  ├─ YES: Found comprehensive guide
│  │  └─ Follow: Workflows, decision trees, examples
│  │     └─ Use tool effectively
│  │
│  └─ NO: No tool-specific standard found
│     └─ Fallback: Check tool description in IDE (parameter schema)
│        └─ Consider: Writing a tool-specific standard (if tool is important)
│
└─ After using tool
   └─ Outcome: Pattern reinforced → Query first next time
```

---

## 🚫 Anti-Patterns: What NOT to Do

### Anti-Pattern 1: Relying on tools/list for Usage Guidance

**❌ Wrong:**
```python
# Step 1: Check tools/list
# Step 2: See parameter schema
# Step 3: Trial and error until it works
```

**Why wrong:**
- No guidance on WHEN to use
- No guidance on HOW to use effectively
- No workflows or decision trees
- High trial-and-error cost

**✅ Right:**
```python
# Step 1: Query for tool-specific standard
pos_search_project(content_type="standards", query="how to use [tool-name]")

# Step 2: Get comprehensive guidance
# Step 3: Follow workflows and decision trees
# Step 4: Use tool effectively the first time
```

---

### Anti-Pattern 2: Memorizing Tool Signatures

**❌ Wrong:**
```
"I'll memorize all tools and their parameters so I don't have to query"
```

**Why wrong:**
- Context degrades mathematically (you'll forget)
- Tools evolve (parameters change)
- You memorize syntax, not reasoning
- Doesn't reinforce query loop

**✅ Right:**
```
"I'll develop the habit of querying for tool-specific standards as needed"
```

**Why right:**
- Creates persistent behavior (survives context degradation)
- Always current (standards evolve with tools)
- Learn reasoning, not just syntax
- Self-reinforcing (querying teaches querying)

---

### Anti-Pattern 3: Creating Static Tool Catalogs

**❌ Wrong:**
```markdown
# MCP Tools Catalog

## pos_search_project
Parameters: action, query, n_results
Description: Search across project...

## pos_workflow  
Parameters: action, session_id, workflow_type
Description: Manage workflows...

[Every new tool requires updating this doc]
[Parameter changes require doc updates]
[Inevitable drift from reality]
```

**Why wrong:**
- Documentation drift (tools evolve, catalog doesn't)
- No comprehensive guidance (just lists parameters)
- Maintenance burden (manual updates required)
- Doesn't teach reasoning

**✅ Right:**
```markdown
# Tool Discovery: Query for tool-specific standards

Query: pos_search_project(content_type="standards", query="how to use [tool-name]")

Each major tool has a comprehensive standard with:
- When to use (decision trees)
- How to use (workflows)
- Why to use (cognitive load comparisons)
- Reasoning patterns

Always current. No maintenance. Self-reinforcing.
```

---

### Anti-Pattern 4: Trial-and-Error Learning

**❌ Wrong:**
```
1. Try tool with guessed parameters
2. Get error or unexpected results
3. Adjust parameters
4. Try again
5. Repeat until it works
6. Still unsure if using it optimally
```

**Why wrong:**
- High time cost (trial and error is slow)
- Fragmented learning (learn by mistakes)
- No systematic understanding
- Miss best practices
- Don't learn reasoning patterns

**✅ Right:**
```
1. Query for comprehensive guidance
2. Learn: When/how/why to use
3. Follow workflows and decision trees
4. Use tool effectively the first time
5. Build systematic understanding
```

---

## 🔗 Related Standards

**Query workflow for tool mastery:**

1. **Start here** → `pos_search_project(content_type="standards", query="tool discovery pattern")` (this document)
2. **Find specific tools** → `pos_search_project(content_type="standards", query="how to use [tool-name]")`
3. **Learn to write standards** → `pos_search_project(content_type="standards", query="standards creation process")`
4. **Understand RAG optimization** → `pos_search_project(content_type="standards", query="RAG content authoring")`

**By Category:**

**Tool Usage:**
- `pos-search-project-usage-guide.md` → `pos_search_project(content_type="standards", query="pos_search_project usage")`
- `pos-workflow-tool-reference.md` → `pos_search_project(content_type="standards", query="how to use pos_workflow")`

**Standards Creation:**
- `standards-creation-process.md` → `pos_search_project(content_type="standards", query="how to create standards")`
- `rag-content-authoring.md` → `pos_search_project(content_type="standards", query="RAG content authoring")`

**AI Behavior:**
- `PRAXIS-OS-ORIENTATION.md` → `pos_search_project(content_type="standards", query="prAxIs OS orientation")`
- `operating-model.md` → `pos_search_project(content_type="standards", query="operating model")`

---

## 🎓 Key Takeaways

**1. Query First, Always**
- Query for tool-specific standards before using tools
- Comprehensive guidance > parameter schemas
- Self-reinforcing loop (querying teaches querying)

**2. Tool-Specific Standards Are Superior**
- They teach WHEN/HOW/WHY, not just syntax
- They include reasoning workflows
- They create persistent behavior (survive context degradation)

**3. Probabilistic Reality Is Real**
- Context degrades mathematically (initial guidance fades)
- Self-reinforcing habits persist
- Query-first pattern survives context degradation

**4. Every Major Tool Should Have a Standard**
- Comprehensive usage guide
- Decision trees and workflows
- Cognitive load comparisons
- RAG-optimized for discoverability

**5. The Pattern Is Self-Reinforcing**
- Query → Get "query more" guidance
- Learn → Querying is valuable
- Internalize → Query first next time
- Habit forms → Persists through session

---

**Query first. Learn comprehensively. Build habits. Let the loop reinforce itself.** 🔄

---

**Version:** 1.0.0  
**Created:** 2025-11-06  
**Last Updated:** 2025-11-06  
**Next Review:** After tool-specific standards for 5+ major tools exist

