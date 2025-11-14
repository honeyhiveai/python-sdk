# Knowledge Compounding Guide

**Keywords for search**: knowledge compounding, document learnings, write standard, create standard, project standards, capture patterns, reusable knowledge, system improvement, standards growth, pattern documentation, learning capture, how to document patterns, when to write standards, project-specific patterns

---

## 🎯 TL;DR - Knowledge Compounding Quick Reference

**Core Principle:** Systems improve through documented learnings. When you discover a pattern, document it for future agents.

**The Compounding Effect:**
```
Day 1: Universal standards only
Day 30: + 20 project-specific patterns (documented by agents)
Day 90: + 50 patterns, 5 custom workflows
Day 180: + 100 patterns, systematic reuse

Knowledge density increases → Quality compounds automatically
```

**Pattern: Search → Implement → Document**
1. Query before implementing: `pos_search_project(content_type="standards", query="how to [task]")`
2. Implement following patterns
3. Discover new project-specific pattern
4. Document learning: `create_standard("project/[domain]", "[pattern-name]", content)`
5. Future agents discover via RAG

**When to Document:**
- ✅ Discovered a pattern worth reusing
- ✅ Solved a project-specific problem
- ✅ Found an integration approach
- ✅ Created a domain convention
- ✅ Identified an optimization

**When NOT to Document:**
- ❌ One-time implementation details
- ❌ Already covered in universal standards
- ❌ Project README content
- ❌ Temporary workarounds

---

## Questions This Answers

- **When should I document a pattern as a standard?**
- **How do I use create_standard to capture learnings?**
- **What's the difference between project and universal standards?**
- **What is knowledge compounding and why does it matter?**
- **When should I create a new standard vs updating existing ones?**
- **What should I include in a project-specific standard?**
- **How do future agents discover my documented patterns?**
- **What are common anti-patterns to avoid when creating standards?**
- **How does the Search → Implement → Document pattern work?**
- **What's the difference between temporary notes and reusable standards?**

## 🎯 Purpose

This standard defines how to capture learnings as project-specific standards, enabling knowledge compounding where the system improves through accumulated documentation.

**Core Principle:**
- How does knowledge compounding improve agent output quality?
- What makes a good project-specific standard?

---

## ⚠️ The Problem Without Knowledge Compounding

**Without documentation pattern:**

```
❌ Agent 1 (Week 1):
- Implements authentication
- Discovers project uses custom JWT refresh pattern
- Completes task
- Learning lost

❌ Agent 2 (Week 3):
- Implements authorization
- Needs same JWT refresh pattern
- Cannot find prior work
- Reinvents pattern (slightly different)
- Inconsistency in codebase

❌ Agent 3 (Week 5):
- Debugging auth issues
- Two different JWT patterns in code
- Confusion about which is correct
- Time wasted on investigation
```

**With documentation pattern:**

```
✅ Agent 1 (Week 1):
- Implements authentication
- Discovers custom JWT refresh pattern
- Documents: create_standard("project/auth", "jwt-refresh-pattern", "...")
- Learning captured

✅ Agent 2 (Week 3):
- Needs JWT pattern
- Queries: pos_search_project(content_type="standards", query="JWT refresh pattern")
- RAG returns Agent 1's documentation
- Uses consistent pattern
- No reinvention

✅ Agent 3 (Week 5):
- Working on auth
- Queries standards
- Finds documented pattern
- Follows established convention
- Codebase consistency maintained
```

**Result Without:** Knowledge loss, inconsistency, reinvention, quality degradation  
**Result With:** Knowledge growth, consistency, reuse, quality improvement

---

## 📋 The Standard: Knowledge Compounding Pattern

### The Three-Step Pattern

**1. Query Before Implementing (Discovery)**
```
Before writing code:
pos_search_project(content_type="standards", query="how to [implement task in domain]")

Purpose: Learn from existing patterns
Benefit: Don't reinvent, follow conventions
```

**2. Implement Following Patterns (Execution)**
```
Implement using discovered patterns
Apply project conventions
Solve project-specific challenges

During: Notice what's project-specific vs universal
```

**3. Document New Patterns (Capture)**
```
After implementing, if you discovered something reusable:
create_standard(
    "project/[domain]",
    "[pattern-name]",
    "[markdown content]"
)

Purpose: Capture learning for future agents
Benefit: System improves through use
```

### Using create_standard Tool

**Tool Signature:**
```python
create_standard(
    category: str,      # "project/[domain]" or "universal/[category]"
    name: str,          # "pattern-name" (descriptive, kebab-case)
    content: str        # Markdown content (RAG-optimized)
)
```

**Category Conventions:**

**Project-specific patterns:**
- `project/auth` - Authentication patterns
- `project/database` - Database patterns
- `project/api` - API conventions
- `project/testing` - Test patterns
- `project/[domain]` - Domain-specific

**Universal patterns** (rare - most learnings are project-specific):
- `universal/[category]` - Only if applies to ALL projects

**Naming Conventions:**
- Use kebab-case: `jwt-refresh-pattern` not `JWTRefreshPattern`
- Be descriptive: `api-error-handling` not `errors`
- Include domain context: `database-migration-pattern` not `migrations`

### Content Structure for Project Standards

**RAG-optimized structure:**

```markdown
# [Pattern Name]

**Keywords for search**: [natural language phrases agents might query]

---

## 🎯 TL;DR - [Pattern Name] Quick Reference

[2-3 sentence summary]
[Key code snippet or approach]
[When to use this pattern]

---

## Context

[Why this pattern exists in this project]
[What problem it solves]
[When it was discovered/created]

---

## The Pattern

[Clear, actionable description]
[Code examples]
[Step-by-step if needed]

---

## Example Implementation

[Real example from the project]
[Show actual code]
[Explain key decisions]

---

## When to Use This Pattern

- ✅ Use when: [scenario 1]
- ✅ Use when: [scenario 2]
- ❌ Don't use when: [exception 1]
- ❌ Don't use when: [exception 2]

---

## Related Patterns

- Related standard 1: `pos_search_project(content_type="standards", query="[query]")`
- Related standard 2: `pos_search_project(content_type="standards", query="[query]")`
```

---

## ✅ Checklist: When to Document a Pattern

**Document as project standard when:**

- [ ] Pattern is project-specific (not covered in universal standards)
- [ ] Pattern will be reused (at least 2-3 more times)
- [ ] Pattern encodes project conventions or decisions
- [ ] Pattern solves a recurring problem
- [ ] Pattern represents a discovered optimization
- [ ] Pattern clarifies project-specific integration

**Don't document as standard when:**

- [ ] Already covered in universal standards (query first!)
- [ ] One-time implementation detail
- [ ] Better suited for project README
- [ ] Temporary workaround (not a pattern)
- [ ] Too implementation-specific (no reuse)

**Content quality checklist:**

- [ ] RAG-optimized (keywords, query hooks)
- [ ] Clear TL;DR at top
- [ ] Real code examples included
- [ ] When to use / not use guidance
- [ ] Related patterns linked via queries

---

## 📖 Examples

### Example 1: Documenting Auth Pattern

**Scenario:** Implementing authentication, discover project uses custom JWT refresh approach.

**✅ Good Documentation:**

```python
# After implementing auth successfully:

create_standard(
    category="project/auth",
    name="jwt-refresh-token-pattern",
    content="""
# JWT Refresh Token Pattern

**Keywords for search**: JWT refresh, token refresh, authentication refresh, session renewal, refresh token rotation

---

## 🎯 TL;DR

This project uses **refresh token rotation** with Redis for session management.

**Key approach:**
- Access tokens: 15min expiry
- Refresh tokens: 7 day expiry, single-use
- Storage: Redis with user:refresh:{token} keys
- On refresh: Issue new access + new refresh, revoke old refresh

---

## Context

Requirement: Long-lived sessions without compromising security.
Solution: Short access tokens + rotated refresh tokens.
Discovered: Week 1, authentication implementation.

---

## The Pattern

[Detailed implementation with code examples]
[Redis key structure]
[Refresh flow diagram]
[Error handling]

---

## Example Implementation

[Actual code from the project]

---

## When to Use This Pattern

- ✅ All authentication endpoints
- ✅ Session management
- ❌ Not for API keys (different pattern)
- ❌ Not for service-to-service (use different approach)
"""
)
```

**Why this is good:**
- ✅ RAG-optimized with keywords
- ✅ Clear TL;DR with key decisions
- ✅ Context explains why
- ✅ Real implementation details
- ✅ Guidance on when to use

### Example 2: Documenting Database Pattern

**Scenario:** Implementing database migrations, discover project-specific rollback strategy.

**✅ Good Documentation:**

```python
create_standard(
    category="project/database",
    name="migration-rollback-strategy",
    content="""
# Migration Rollback Strategy

**Keywords for search**: database migration, rollback, migration failures, database rollback, migration recovery, schema changes

---

## 🎯 TL;DR

This project uses **dual-direction migrations** with automatic rollback on failure.

**Key approach:**
- Every migration has up() and down()
- Migrations run in transaction (when possible)
- On failure: Automatic rollback via down()
- State tracking in migrations_history table

---

## Context

Requirement: Safe schema changes in production.
Challenge: Some DDL operations not transactional.
Solution: Explicit rollback procedures + state tracking.

---

## The Pattern

[Implementation details]
[Transaction handling]
[Non-transactional DDL approach]
[State tracking logic]

---

## Example Implementation

[Real migration examples from project]
[Rollback examples]
[Error handling examples]
"""
)
```

### Example 3: What NOT to Document

**❌ Don't document this:**

```python
# After implementing a specific feature:

create_standard(
    category="project/features",
    name="user-profile-endpoint",
    content="Implementation of /api/users/:id endpoint..."
)
```

**Why not:**
- ❌ Implementation detail, not a pattern
- ❌ No reuse (specific to one endpoint)
- ❌ Belongs in code comments or API docs
- ❌ Not a learnable pattern

**✅ Document this instead:**

```python
create_standard(
    category="project/api",
    name="rest-endpoint-pattern",
    content="""
# REST Endpoint Pattern

This project's convention for RESTful endpoints:
- Naming: /api/resources/:id
- Error responses: {error, message, remediation}
- Validation: Middleware approach
- Authentication: JWT header check

[Reusable across ALL endpoints]
"""
)
```

---

## 🚫 Anti-Patterns

### Anti-Pattern 1: Not Documenting Discoveries

**❌ Don't do this:**
```
Agent: [Solves complex integration problem]
Agent: [Finishes implementation]
Agent: "Done! Moving to next task"
Learning: Lost forever
Future agents: Reinvent the same solution
```

**✅ Do this instead:**
```
Agent: [Solves complex integration problem]
Agent: "This integration pattern is reusable"
Agent: create_standard("project/integrations", "api-retry-pattern", "...")
Learning: Captured and discoverable
Future agents: pos_search_project(content_type="standards", query="API retry") → Find and reuse
```

### Anti-Pattern 2: Documentation Dump

**❌ Don't do this:**
```python
create_standard(
    category="project/everything",
    name="all-our-patterns",
    content="""
    [50 pages of everything we do]
    [No structure]
    [Not RAG-optimized]
    [Not discoverable]
    """
)
```

**✅ Do this instead:**
```python
# Create focused, discoverable standards:

create_standard("project/auth", "jwt-pattern", "[JWT-specific content]")
create_standard("project/auth", "session-management", "[Session content]")
create_standard("project/api", "error-responses", "[Error content]")

# Each standard: focused, discoverable, reusable
```

### Anti-Pattern 3: Documenting Universal Patterns

**❌ Don't do this:**
```python
create_standard(
    category="project/concurrency",
    name="race-conditions",
    content="Race conditions happen when... [general CS concept]"
)
```

**Why not:**
- ❌ Already in universal standards
- ❌ Not project-specific
- ❌ Creates duplication

**✅ Do this instead:**
```python
# If project has SPECIFIC race condition pattern:

create_standard(
    category="project/concurrency",
    name="websocket-broadcast-locking",
    content="""
    This project's pattern for WebSocket broadcasts to avoid race conditions:
    - Use Redis pub/sub for coordination
    - Lock pattern: websocket:broadcast:{room_id}
    - [Project-specific implementation]
    """
)
```

---

## 📈 The Compounding Effect

**Knowledge growth over time:**

```
Week 1:
- Universal standards: 100 documents
- Project standards: 0 documents
- Query quality: Good (universal patterns)

Week 4:
- Universal standards: 100 documents
- Project standards: 15 documents (agents documented learnings)
- Query quality: Excellent (universal + project-specific)
- Consistency: High (agents follow documented patterns)

Week 12:
- Universal standards: 100 documents
- Project standards: 50 documents
- Query quality: Exceptional (deep project knowledge)
- Consistency: Very high (established conventions)
- Speed: Faster (less reinvention)
- Quality: 85-95% (vs 60-70% without compounding)

Week 24:
- Universal standards: 100 documents
- Project standards: 100+ documents
- Query quality: Expert-level (comprehensive knowledge base)
- New agents: Onboard faster (query to learn)
- Team knowledge: Captured and accessible
```

**System improves through use. This is knowledge compounding.**

---

## 🔗 Related Standards

**Query workflow for knowledge compounding:**

1. **Before implementing** → `pos_search_project(content_type="standards", query="how to [task]")`
2. **Learn pattern creation** → `pos_search_project(content_type="standards", query="how to create standards")`
3. **RAG optimization** → `pos_search_project(content_type="standards", query="RAG content authoring")`
4. **After implementing** → Use this guide to document

**By Category:**

**Standards Creation:**
- `standards/ai-assistant/standards-creation-process.md` → `pos_search_project(content_type="standards", query="standards creation process")`
- `standards/documentation/rag-content-authoring.md` → `pos_search_project(content_type="standards", query="RAG content authoring")`

**Tool Discovery:**
- `standards/ai-assistant/mcp-tool-discovery-pattern.md` → `pos_search_project(content_type="standards", query="tool discovery pattern")`

---

## 📞 Questions?

**How do I know if something should be documented?**
→ Ask: "Would future agents benefit from knowing this?" If yes, document it.

**What's the difference between project and universal standards?**
→ Universal: Applies to ALL projects. Project: Specific to THIS project's conventions and patterns.

**Should I document every implementation?**
→ No. Document patterns, not implementations. Patterns are reusable, implementations are one-time.

**What if I'm not sure if something is a pattern?**
→ If you'd want to reuse it 2-3 more times in this project, it's a pattern. Document it.

**Can I update existing project standards?**
→ Yes! If you discover improvements or refinements, update the standard. Knowledge evolves.

**How do I make sure my standard is discoverable?**
→ Follow RAG optimization: keywords, query hooks, TL;DR, natural language headers. See: `pos_search_project(content_type="standards", query="RAG content authoring")`

---

**Version:** 1.0.0  
**Last Updated:** 2025-10-12  
**Next Review:** Quarterly or when pattern emerges

