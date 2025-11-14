# Workflow Discovery and Execution Patterns

**Keywords for search**: workflow discovery, pos_workflow, how to use workflows, workflow lifecycle, workflow patterns, start workflow, complete phase, workflow session, phase gates, workflow execution, resume workflow, workflow errors, workflow recovery, get task, tools/list, workflow pitfalls, workflow troubleshooting

**Core Principle:** Workflows are discovered through `tools/list` and executed through behavioral patterns. Learn the lifecycle, not the parameters. Real work produces valid evidence naturally.

---

## 🎯 TL;DR - Workflow Discovery Quick Reference

**Discovery Pattern:**
1. Check `tools/list` → See pos_workflow with current actions/parameters
2. Query standards → Understand lifecycle patterns (this doc)
3. Start simple → Begin with basic actions, build understanding
4. Learn from errors → Error messages guide remediation

**Lifecycle Pattern:**
```
start → list_sessions (get session_id) → get_task → [do work] → complete_phase → repeat
```

**Golden Rules:**
- ✅ Check `tools/list` for current parameters (source of truth)
- ✅ Do real work first, then submit natural evidence
- ✅ Query standards when stuck, don't assume tool is broken
- ❌ Don't guess parameters from memory
- ❌ Don't skip `complete_phase` (validation gates exist for quality)
- ❌ Don't look for validation schemas (intentionally hidden)

---

## 🎯 Purpose

Define behavioral patterns for discovering and executing workflows with pos_workflow. This standard teaches HOW to work with workflows through discovery patterns, not WHAT parameters exist (use `tools/list` for that).

**Key Distinction:** This is about patterns and lifecycle, not documentation. Parameters come from `tools/list` (dynamic, always current). This doc captures observed behavioral patterns that help AI agents work effectively with workflows.

---

## ❌ The Problem

**Without workflow discovery patterns:**
- AI agents guess parameters instead of checking `tools/list` (drift, errors)
- AI agents assume tool is broken on first error instead of querying for help
- AI agents skip `complete_phase` and manually advance (bypassing quality gates)
- AI agents look for validation schemas (breaking adversarial design)
- AI agents try to game evidence submission (fails validation, wastes time)
- AI agents start new sessions instead of resuming existing ones (context loss)

**Result:** Failed workflows, quality bypasses, frustrated agents, repeated mistakes.

---

## ❓ Questions This Answers

1. "How do I discover workflow capabilities?"
2. "What's the workflow execution lifecycle?"
3. "How do I start a workflow?"
4. "How do I find my session ID?"
5. "How do I resume an existing workflow?"
6. "What evidence do I submit for phase gates?"
7. "How do I know what to submit for validation?"
8. "Why did my phase validation fail?"
9. "How do I recover from workflow errors?"
10. "Should I start a new session or resume existing?"
11. "Why can't I find validation requirements?"
12. "How do I move to the next phase?"
13. "What are common workflow mistakes?"
14. "Where do I find current pos_workflow parameters?"

---

## ✅ The Standard: Workflow Discovery Patterns

### Pattern 1: Discovery Before Use

**Always discover capabilities before invoking:**

1. **Check `tools/list` first** - Source of truth for current actions and parameters
2. **Query this standard** - Understand lifecycle patterns and pitfalls
3. **Start with basic actions** - list_workflows, list_sessions (safe, read-only)
4. **Build understanding incrementally** - Don't jump to complex actions

**Why:** Parameters change, documentation drifts, but `tools/list` is always current. Discovery prevents errors.

---

### Pattern 2: Workflow Execution Lifecycle

**Standard workflow progression:**

```
Phase 0: Discovery
  ↓
Action: start (or resume existing session via list_sessions)
  ↓
Save session_id (you'll need it for every subsequent call)
  ↓
Action: get_task (understand what to do)
  ↓
[Do the actual work - implement, test, validate]
  ↓
Action: complete_phase (submit evidence from real work)
  ↓
If validation passes: Advance to next phase
If validation fails: Read errors, fix, retry
  ↓
Repeat for each phase until workflow_complete: true
```

**Critical:** Each phase requires `complete_phase` with evidence. Don't skip this - it's the quality gate.

---

### Pattern 3: Session Management

**Resume vs Start:**

```python
# ALWAYS check for existing sessions first
list_sessions(status="active")  # or "paused"

# If session exists and you want to continue:
→ Use existing session_id
→ Check get_state to see current phase
→ Continue from where you left off

# If no session exists or starting new work:
→ start() to create new session
→ Save the returned session_id
```

**Why:** Starting new sessions when one exists loses context and creates orphaned sessions.

---

### Pattern 4: Evidence Submission (Adversarial Design)

**The intentional friction model:**

✅ **Do this:**
- Complete the actual work first
- Describe what you did naturally
- Submit evidence from real work (file paths, test output, metrics)
- Trust that real work produces valid evidence

❌ **Don't do this:**
- Try to find validation schemas (they're hidden by design)
- Fake evidence to match imagined structure (will fail validation)
- Submit boolean flags without proof artifacts (gaming, will fail)
- Look for shortcuts (doing work is easier than gaming)

**Why validation schemas are hidden:** This is adversarial design. The friction forces you to do real work. Real work naturally produces valid evidence. Gaming is harder than compliance. This friction GUARANTEES quality.

**If validation fails:**
- Read the error message carefully (provides remediation)
- Fix what the error identifies
- Resubmit naturally
- Don't try to reverse-engineer schemas from errors

---

### Pattern 5: Error Recovery

**When workflows fail:**

```
Error occurs
  ↓
Action: get_errors (understand what failed)
  ↓
Read error message (contains remediation guidance)
  ↓
Query standards if unclear (don't assume tool is broken)
  ↓
Fix the actual problem
  ↓
Action: retry_phase (try again with fixes)
  OR
Action: rollback (if need to go back further)
```

**Attribution heuristic:**
- Tool returned error message → Tool is working, I did something wrong
- Error has remediation steps → Follow them
- Unclear error → Query standards for patterns
- Tool actually broken → Very rare, query first

**Why:** Most "broken tool" assumptions are misunderstandings. Query before concluding failure.

---

## ✅ Workflow Discovery Checklist

Before starting workflow execution:
- [ ] Checked `tools/list` for current pos_workflow actions
- [ ] Queried this standard for lifecycle patterns
- [ ] Understand discovery-first approach (not guessing)

During workflow execution:
- [ ] Used list_sessions to check for existing sessions before starting new
- [ ] Saved session_id from start() for all subsequent calls
- [ ] Used get_task to understand work before doing it
- [ ] Did actual work before submitting evidence
- [ ] Used complete_phase (not manual phase advancement)
- [ ] Submitted natural evidence from real work (not guessing structure)

When errors occur:
- [ ] Used get_errors to understand failure
- [ ] Queried standards before assuming tool is broken
- [ ] Followed error remediation guidance
- [ ] Used retry_phase or rollback as appropriate

---

## 🎯 Examples: Workflow Patterns in Action

### Example 1: Starting New Workflow

```
Scenario: User says "execute the query gamification spec"

✅ Good:
1. Check tools/list → See pos_workflow parameters
2. Query: "how to start workflow"
3. list_workflows() → Find spec_execution_v1
4. start(workflow_type="spec_execution_v1", 
        target_file="query-gamification", 
        options={"spec_path": "..."})
5. Save session_id from response

❌ Bad:
1. Guess parameters from memory
2. start() with wrong workflow_type
3. Get error, assume tool is broken
4. Try to work around instead of querying
```

---

### Example 2: Evidence Submission

```
Scenario: Completed Phase 1 implementation tasks

✅ Good:
1. Actually implement the modules
2. Actually write tests and run them
3. Actually verify code quality
4. Submit natural evidence:
   {
     "files_created": ["query_classifier.py", "query_tracker.py"],
     "test_output": "tests/unit/test_query_classifier.py PASSED",
     "tests_passing": 15,
     "linting_clean": true
   }
5. Real work → validation passes naturally

❌ Bad:
1. Try to find gate-definition.yaml
2. Read validation schema
3. Craft evidence to match schema
4. Submit without doing work
5. Gaming attempt → validation fails → wasted time
```

---

### Example 3: Error Recovery

```
Scenario: complete_phase() returns validation failure

✅ Good:
1. get_errors(session_id)
2. Read error: "Missing required field: test_output"
3. Realize I didn't include test output path
4. Add evidence: {"test_output": ".test-results/output.txt"}
5. retry_phase()

❌ Bad:
1. Get error
2. Assume pos_workflow is broken
3. Try to manually advance phase
4. Skip validation entirely
5. Quality gate bypassed → technical debt
```

---

### Example 4: Session Resumption

```
Scenario: Conversation interrupted, continuing work

✅ Good:
1. list_sessions(status="active")
2. See existing session for query-gamification
3. get_state(session_id) → Currently on Phase 2
4. Continue with Phase 2 tasks
5. Context preserved, work continues

❌ Bad:
1. Forget to check for existing sessions
2. start() new workflow
3. Create duplicate session
4. Lose all Phase 1 progress
5. Orphaned session remains
```

---

## ❌ Anti-Patterns: Common Workflow Mistakes

### Anti-Pattern 1: Parameter Guessing

**Wrong:**
```python
# Guessing from memory or documentation
pos_workflow(action="start", workflow="spec_execution")  # Wrong param name
```

**Right:**
```python
# Check tools/list first
# See that it's workflow_type, not workflow
pos_workflow(action="start", workflow_type="spec_execution_v1")
```

**Why it's wrong:** Parameters change. Documentation drifts. Memory is unreliable. `tools/list` is source of truth.

---

### Anti-Pattern 2: Assuming Tool Breakage

**Wrong:**
```
Get error → "pos_workflow must be broken" → Try workarounds
```

**Right:**
```
Get error → Query "workflow troubleshooting" → Understand mistake → Fix it
```

**Why it's wrong:** Most errors are usage mistakes, not bugs. Query before assuming failure. Tool returning errors means it's working (error handling is working).

---

### Anti-Pattern 3: Skipping complete_phase

**Wrong:**
```python
# Manually advancing to next phase
# Reading workflow state files directly
# Trying to bypass validation
```

**Right:**
```python
# Use the designed workflow
complete_phase(session_id, phase=1, evidence={...})
# Let validation run
# Trust the process
```

**Why it's wrong:** Phase gates enforce quality. Skipping them creates technical debt. The friction is intentional and valuable.

---

### Anti-Pattern 4: Schema Hunting

**Wrong:**
```python
# Looking for gate-definition.yaml
# Trying to read validation schemas
# Crafting evidence to match schema structure
```

**Right:**
```python
# Do the actual work
# Describe what you did naturally
# Submit evidence from real work
# Trust that real work produces valid evidence
```

**Why it's wrong:** Schemas are hidden by adversarial design. This friction forces real work. Real work produces valid evidence naturally. Gaming is harder than compliance. This protects quality.

---

### Anti-Pattern 5: Session Duplication

**Wrong:**
```python
# Not checking for existing sessions
start()  # Creates new session
# Loses all previous progress
```

**Right:**
```python
list_sessions(status="active")
# See existing session
# Resume it instead of starting new
```

**Why it's wrong:** Duplicates effort, loses context, creates orphaned sessions.

---

## 🔗 When to Query This Standard

Query this standard when you need workflow patterns:

| Scenario | Example Query |
|----------|--------------|
| Starting workflows | "how to start workflow" |
| Understanding lifecycle | "workflow execution lifecycle" |
| Session management | "resume workflow session" |
| Evidence submission | "workflow evidence validation" |
| Error recovery | "workflow troubleshooting" |
| Common mistakes | "workflow pitfalls" |
| Discovery patterns | "how to discover workflow capabilities" |

**Remember:** This standard teaches patterns. Use `tools/list` for current parameters.

---

## 🎓 The Meta-Lesson: Discovery Over Documentation

**This standard itself demonstrates the philosophy:**
- ✅ Teaches patterns (lifecycle, recovery, pitfalls)
- ✅ Points to source of truth (`tools/list` for parameters)
- ✅ Explains WHY (adversarial design, friction as feature)
- ❌ Doesn't duplicate `tools/list` (would drift)
- ❌ Doesn't hardcode parameters (would become stale)
- ❌ Doesn't expose schemas (would break quality gates)

**The lesson:** Learn how to fish (discovery patterns), don't memorize fish (hardcoded docs). Discovery scales, documentation drifts.

---

## 🔗 Related Standards

- **[Agent Decision Protocol](./agent-decision-protocol.md)** - Query: "decision protocol error attribution"
- **[prAxIs OS Orientation](./PRAXIS-OS-ORIENTATION.md)** - Query: "orientation bootstrap queries"
- **[RAG Content Authoring](./rag-content-authoring.md)** - Query: "RAG optimization query hooks"
- **[Adversarial Design](../../explanation/adversarial-design.md)** - Query: "adversarial design information asymmetry"

---

## 📊 Validation

This standard is discoverable from multiple query angles:

**Tested queries that return this standard:**
- "how to use workflows"
- "workflow lifecycle patterns"
- "pos_workflow discovery"
- "workflow evidence submission"
- "workflow error recovery"
- "workflow troubleshooting"
- "resume workflow session"
- "workflow common mistakes"

**RAG optimization checklist:**
- ✅ TL;DR with high keyword density
- ✅ "Questions This Answers" section (14 questions)
- ✅ Query-oriented headers ("How to X" not "Usage")
- ✅ Keywords line for explicit search terms
- ✅ Multiple query angles tested
- ✅ Links to source of truth (tools/list)
- ✅ Cross-references with query patterns
- ✅ Chunks are semantically complete

---

**Last Updated:** 2025-10-24 (Based on dogfooding session observations)
**Version:** 1.0 (Initial pattern extraction from real usage)

