# Design Document Structure Standard

**Design documents are strategic planning artifacts for human decision-making, distinct from specifications (AI execution) and implementation plans (code-level details).**

---

## 🚨 Quick Reference

**Keywords for search**: design doc, design document, architecture design, planning document, technical design, design doc vs spec, what to include in design, design document structure, design document template, strategic planning

**When to Use**: Before creating a spec, when exploring options, when human decisions needed on architecture/approach

**Core Principle**: Design docs answer WHAT/HOW/WHY. Specs answer WHEN/WHO and break into executable tasks.

**Key Distinction**:
- **Design Doc**: 5-20 pages, options analysis, strategic decisions, human approval
- **Spec**: 100+ pages, task breakdown, execution details, AI execution via `spec_execution_v1`

**Don't Include**: Timeline estimates (days/weeks), detailed task breakdowns (that's tasks.md), sprint planning (not relevant to AI)

---

## 🔍 What Questions Does This Answer?

- When should I write a design doc vs. going straight to a spec?
- What should I include in a design doc?
- How much detail is appropriate?
- What should I leave out of a design doc?
- How does a design doc fit into the prAxIs OS workflow?
- What's the difference between a design doc and a spec?
- How do design docs support AI agent development?

---

## 📖 Purpose

Design documents bridge strategic thinking and systematic execution. They:

1. **Capture Options**: Explore multiple approaches before committing
2. **Facilitate Human Review**: Enable strategic decisions with full context
3. **Document Trade-offs**: Record why decisions were made
4. **Identify Risks**: Surface issues before implementation starts
5. **Enable Approval**: Get buy-in before expensive spec creation
6. **Provide Input**: Inform `spec_creation_v1` workflow with design decisions

**Design docs are for thinking. Specs are for doing.**

---

## 📐 Standard Structure

### Must Have Sections

#### 1. Problem Statement
**What are we solving and why?**

- Current pain points
- Impact if not solved
- Scope boundaries (what's included/excluded)
- Success looks like...

#### 2. Goals & Non-Goals
**Explicit scope boundaries**

**Goals (In Scope):**
- Specific, measurable outcomes
- Success criteria
- Key capabilities to deliver

**Non-Goals (Out of Scope):**
- What we're explicitly NOT doing
- Future work (v2, v3)
- Related but separate concerns

#### 3. Current State Analysis
**What exists today?**

- Current architecture/implementation
- What works well (keep this)
- What's broken (fix this)
- What's missing (add this)
- Metrics/data supporting need

#### 4. Proposed Design
**What will it look like?**

This is the **core** of the design doc. Include:

- **Architecture**: Components, interactions, data flow
- **Data Models**: Key structures, relationships
- **Interfaces**: APIs, contracts, integration points
- **Behaviors**: How it works, key algorithms
- **Examples**: Concrete scenarios showing design in action

**Focus on WHAT and HOW, not WHEN or WHO.**

#### 5. Options Considered
**What alternatives did we explore?**

For each option:
- **Option X: [Name]**
- **Pros**: Benefits, strengths
- **Cons**: Drawbacks, concerns
- **Trade-offs**: What you gain vs. lose

**Recommendation**: State which option and why.

#### 6. Risks & Mitigations
**What could go wrong?**

For each risk:
- **Risk**: Description
- **Probability**: High/Medium/Low
- **Impact**: Critical/High/Medium/Low
- **Mitigation**: How to reduce probability/impact
- **Contingency**: What to do if it happens

#### 7. Open Questions
**What decisions need human input?**

- List questions requiring strategic decisions
- Provide context for each
- Suggest options (if any)
- Identify decision-maker
- Set deadline (if time-sensitive)

### Should Have Sections

#### 8. Success Criteria
**How do we know it worked?**

- Quantitative metrics (numbers, percentages)
- Qualitative outcomes (behaviors, experiences)
- Acceptance criteria (testable conditions)

#### 9. File Change Summary
**What code/files affected?**

- Files to create
- Files to modify
- Files to delete
- Dependencies impacted

#### 10. Testing Approach
**How to validate?**

- Unit test strategy
- Integration test strategy
- Validation methods
- Acceptance testing

### Optional Sections

- **Background/Context**: If needed for reviewers
- **Prior Art**: Existing solutions, inspiration
- **References**: Links to related docs
- **Appendices**: Detailed data, research, diagrams

---

## ❌ What NOT to Include

### Timeline Estimates
**Don't**: "Phase 1 (3 days), Phase 2 (5 days), Week 1-2, Sprint 1"
**Why**: AI agents don't work in sprints. Time emerges from task granularity in spec.
**Instead**: Focus on what needs to happen, let spec process determine timing.

### Detailed Task Breakdowns
**Don't**: "Task 1.1: Do X, Task 1.2: Do Y, Task 1.3: Do Z"
**Why**: That's what `tasks.md` is for in spec_creation_v1.
**Instead**: Describe work at epic/component level, leave task breakdown to spec.

### Sprint Planning / Resource Allocation
**Don't**: "Alice works on backend, Bob on frontend, needs 2 engineers"
**Why**: prAxIs OS uses AI agents, not human resource planning.
**Instead**: Describe work scope, AI execution handles the "who."

### Implementation Code Samples
**Don't**: Full code implementations, detailed algorithms
**Why**: That's implementation phase, not design phase.
**Instead**: Pseudocode, interface signatures, data structure examples (conceptual).

### Story Points / Velocity Metrics
**Don't**: "8 story points, team velocity 25 points/sprint"
**Why**: Not relevant to AI agent development model.
**Instead**: Complexity indicators if needed (simple/medium/complex).

---

## 🔄 Design Doc vs. Spec

| Aspect | Design Doc | Spec |
|--------|-----------|------|
| **Purpose** | Strategic planning, options analysis | AI execution, systematic implementation |
| **Audience** | Humans making decisions | AI agents doing work |
| **Length** | 5-20 pages (focused) | 100+ pages (comprehensive) |
| **Focus** | WHAT/HOW/WHY (architecture, trade-offs) | Tasks, dependencies, validation gates |
| **Structure** | Flexible narrative | Fixed format (README, SRD, specs, implementation, tasks) |
| **Timing** | Before committing to approach | After design approved |
| **Detail Level** | High-level architecture, options | File-level changes, test cases |
| **Outcome** | Human approval to proceed | Working code via `spec_execution_v1` |
| **Creation** | Manual (human thinking) | Via `spec_creation_v1` workflow |
| **Execution** | N/A (planning artifact) | Via `spec_execution_v1` workflow |
| **Updates** | Rare (frozen after approval) | Frequent (living document during execution) |

---

## 🔁 Workflow Integration

### Where Design Docs Fit

```
1. Problem Identified
2. Initial Analysis
3. Design Doc Created ← (strategic thinking)
4. Human Reviews Design
5. Design Approved/Iterated
6. spec_creation_v1 Started (using design as input)
7. Spec Created (README, SRD, specs, implementation, tasks)
8. spec_execution_v1 Started
9. Implementation Completed
```

### When to Write a Design Doc

**Write a design doc when:**
- ✅ Multiple approaches possible (need to compare)
- ✅ Significant architectural changes
- ✅ High risk or uncertainty
- ✅ Human strategic decisions needed
- ✅ Cross-team coordination required
- ✅ Need to get buy-in before expensive work

**Skip design doc when:**
- ❌ Approach is obvious
- ❌ Incremental change to existing system
- ❌ Low risk, well-understood problem
- ❌ Time-sensitive (spike then decide)

### How to Use Design Docs with prAxIs OS

**Step 1: Create Design Doc**
```
Write document manually (human strategic thinking)
Focus on options, trade-offs, architecture
Get human review and approval
```

**Step 2: Create Spec from Design**
```
pos_workflow(
  action="start",
  workflow_type="spec_creation_v1",
  target_file=".praxis-os/specs/review/YYYY-MM-DD-feature-name"
)

Use design doc as input during spec creation
Design doc informs SRD, specs, implementation guidance
```

**Step 3: Execute Spec**
```
pos_workflow(
  action="start",
  workflow_type="spec_execution_v1",
  target_file=".praxis-os/specs/review/YYYY-MM-DD-feature-name",
  options={"spec_path": ".praxis-os/specs/review/YYYY-MM-DD-feature-name"}
)

Spec's tasks.md drives execution
AI agent completes tasks systematically
```

---

## 📝 Example Design Doc Outline

```markdown
# Feature X Design Document

## Problem Statement
[What are we solving? Current pain points? Impact?]

## Goals & Non-Goals
Goals:
- [Specific outcomes]

Non-Goals:
- [Out of scope]

## Current State
[What exists? What works? What's broken?]

## Proposed Design

### Architecture
[Components, interactions, data flow]

### Data Models
[Key structures]

### API/Interfaces
[Integration points]

### Key Behaviors
[How it works]

### Example Scenarios
[Concrete usage examples]

## Options Considered

### Option A: [Name]
Pros: [Benefits]
Cons: [Drawbacks]

### Option B: [Name]
Pros: [Benefits]
Cons: [Drawbacks]

**Recommendation**: Option A because [rationale]

## Risks & Mitigations
- Risk: [Description] | Probability: Medium | Impact: High
  - Mitigation: [How to reduce]
  - Contingency: [If it happens]

## Open Questions
1. [Question needing human decision]
2. [Question needing clarification]

## Success Criteria
- [Measurable outcome 1]
- [Measurable outcome 2]

## File Changes
- Create: [files]
- Modify: [files]
- Delete: [files]

## Testing Approach
- Unit: [Strategy]
- Integration: [Strategy]
- Validation: [Methods]
```

---

## ✅ Design Doc Checklist

Before finalizing your design doc:

- [ ] Problem statement is clear and specific
- [ ] Goals explicitly state what success looks like
- [ ] Non-goals prevent scope creep
- [ ] Current state analysis shows what exists today
- [ ] Proposed design describes WHAT and HOW (not WHEN)
- [ ] At least 2 options considered (shows thinking)
- [ ] Trade-offs explained for each option
- [ ] Recommendation stated with rationale
- [ ] Risks identified with mitigations
- [ ] Open questions listed for human decisions
- [ ] Success criteria are measurable
- [ ] NO timeline estimates (days/weeks)
- [ ] NO detailed task breakdowns (leave for spec)
- [ ] NO sprint planning or resource allocation
- [ ] Examples illustrate design concretely
- [ ] File changes summarized (high-level)
- [ ] Testing approach outlined

---

## 🚫 Common Anti-Patterns

### Anti-Pattern 1: Design Doc as Project Plan
**Problem**: Including sprint timelines, task assignments, velocity estimates
**Why Bad**: AI agents don't work in sprints, spec handles execution details
**Fix**: Focus on WHAT/HOW/WHY, remove WHEN/WHO

### Anti-Pattern 2: Too Much Detail
**Problem**: File-by-file code samples, line-by-line changes
**Why Bad**: That's implementation phase, not design phase
**Fix**: Show architecture and interfaces, leave implementation to spec execution

### Anti-Pattern 3: Single Option
**Problem**: Only describing one approach, no alternatives
**Why Bad**: Doesn't show options were considered
**Fix**: Include at least 2 options with pros/cons, state why you chose one

### Anti-Pattern 4: No Trade-offs
**Problem**: Only listing pros, ignoring cons
**Why Bad**: Every design has trade-offs, pretending otherwise reduces trust
**Fix**: Honestly state trade-offs, show you've thought through implications

### Anti-Pattern 5: Vague Goals
**Problem**: "Make it better," "improve performance"
**Why Bad**: Can't validate success, scope creep inevitable
**Fix**: Specific, measurable goals ("reduce latency by 50%," "support 10K req/s")

### Anti-Pattern 6: No Risks
**Problem**: Not identifying what could go wrong
**Why Bad**: Surprises during implementation, no mitigation plan
**Fix**: List risks with probability/impact, plan mitigations

### Anti-Pattern 7: Open Questions Without Context
**Problem**: "How should we handle X?" with no background
**Why Bad**: Reviewers can't make informed decisions
**Fix**: Provide context, options, recommendation for each question

---

## 📚 Related Standards

**See also:**
- `search_standards("rag content authoring")` - How to write for discoverability
- `search_standards("specification structure")` - How specs differ from design docs
- `search_standards("workflow creation")` - When to use workflows vs. tools
- `search_standards("documentation completeness")` - Quality standards for all docs
- `search_standards("knowledge compounding")` - How to capture learnings

---

## 💡 Real-World Example

**Good Design Doc**: `.praxis-os/workspace/design/2025-10-23-session-state-redesign.md`
- Clear problem statement (session state incomplete)
- Multiple options explored (where to store timing data)
- Trade-offs explained (calculation vs. storage)
- Risks identified (migration corruption)
- No timeline estimates (focuses on what/how)

**Spec Created from Design**: `.praxis-os/specs/review/2025-10-23-workflow-system-v1-completion/`
- Generated via `spec_creation_v1` workflow
- Design doc informed SRD and specs.md
- tasks.md broke work into phases with dependencies
- spec_execution_v1 will execute systematically

---

## 🎯 Key Takeaways

1. **Design docs are for thinking, specs are for doing**
2. **Focus on WHAT/HOW/WHY, not WHEN/WHO**
3. **Show options and trade-offs (prove you thought it through)**
4. **Identify risks early (mitigation is easier in design phase)**
5. **Get human approval before expensive spec work**
6. **Use design doc as input to `spec_creation_v1`**
7. **Keep it 5-20 pages (if longer, split into multiple docs)**
8. **Let spec process determine timing and task breakdown**

---

**Version**: 1.0.0  
**Created**: 2025-10-23  
**Last Updated**: 2025-10-23  
**Next Review**: After first 5 design docs created using this standard

