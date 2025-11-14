# prAxIs OS Feature Development Process

**The three-phase development process for building features in prAxIs OS: Conversational Design → Structured Spec → Structured Implementation.**

---

## 🚨 Quick Reference (TL;DR)

**User wants you to build something - what do you do?** When user says "build authentication" or "create payment system" or wants you to implement any feature, you follow three phases. Don't start coding immediately. Start with discussion, then create spec, then implement.

**Keywords for search**: build-something, user-wants-feature, start-coding-immediately, discussion-first, development-approach

**User says "build X" - where do you start? Three phases:**

**Phase 1: DISCUSS FIRST** (Don't start coding yet!)
- User says "build X" → You start with discussion (not coding, not workflows)
- Ask questions about what they want: "Do you need...?" "Should it...?"
- Explore approaches: "We could do A or B, here are trade-offs"
- Don't create spec yet - just discuss and understand
- Output: design-doc.md (captures what you discussed)

**Phase 2: CREATE SPEC** (User must trigger this)
- User says "create the spec" → Now you make formal spec
- Query: `pos_search_project(content_type="standards", query="how to create specification")` to find workflow
- Use workflow to create detailed spec
- User reviews spec before you do anything else
- Output: `.praxis-os/specs/YYYY-MM-DD-name/` (formal plan)

**Phase 3: BUILD IT** (User must approve first)
- User says "implement the spec" → Now you write code
- Query: `pos_search_project(content_type="standards", query="how to execute specification")` to find workflow
- Use workflow to implement systematically
- Build code + tests + docs
- Output: Production code (ready to ship)

**Critical - when user wants you to build something:**
- ❌ Don't start coding immediately when user says "build X"
- ❌ Don't skip straight to spec - discuss first
- ❌ Don't auto-advance - wait for user to say "go to next phase"
- ✅ Start with discussion to understand what they really want
- ✅ Query to discover workflows (don't assume you know which workflow to use)

---

## ❓ Questions This Answers

1. "User wants me to build something - what do I do?"
2. "User says 'build authentication' - where do I start?"
3. "Should I start coding immediately?"
4. "Do I start with a spec or start with discussion?"
5. "What's the development approach here?"
6. "Am I supposed to use a workflow or just talk?"
7. "When do I stop discussing and start building?"
8. "Can I skip the discussion and just code?"
9. "User gave me requirements - should I write code now?"
10. "What do I do first when user wants a feature?"
11. "How do I know when to create a spec?"
12. "Should I ask questions before coding?"
13. "Do I need approval before implementing?"
14. "User wants me to build X - what's my first action?"
15. "When should I be conversational vs structured?"
16. "How do I find the right workflow to use?"
17. "What if user says build something complex?"
18. "Should I discuss first or spec first?"
19. "Where do I start when building a feature?"
20. "What's the approach for going from idea to code?"

---

## 🎯 Purpose

Define the systematic three-phase development process that transforms user requirements into production-ready code through prAxIs OS. This process ensures quality through structured workflows while maintaining conversational flexibility in early design stages.

**Key Distinction:** The three phases use different modes (conversational vs workflow-driven) and have explicit transition points requiring human approval.

---

## Why This Matters - What Goes Wrong

**What happens when you start coding immediately:**

**Wrong approach (starting coding immediately):**
```
User: "Build authentication with JWT"
You: [Start coding immediately - no discussion]
30 minutes later...
User: "I meant OAuth, not JWT"
You: [Wasted 30 minutes, have to rewrite everything]
```

**Right approach (discuss first):**
```
User: "Build authentication with JWT"  
You: [Don't start coding - ask questions first]
You: "Do you need social auth? Refresh tokens? MFA?"
User: "Oh yes, Google OAuth and MFA"
You: [Now you understand what they really want]
You: [Create spec, get approval, then build it right the first time]
```

**What goes wrong when you don't follow this:**
- ❌ Start coding immediately → Build wrong thing, waste time
- ❌ Skip discussion → Misunderstand what user wants
- ❌ Skip spec → Miss requirements, have to redo work
- ❌ Don't know when to discuss vs when to use workflow → Wrong approach
- ❌ Auto-advance without approval → User loses control
- ❌ Assume you know the workflow → Use wrong or outdated workflow

---

## What Is the Three-Phase Development Process?

### Phase 1: Conversational Design Discussion

**When to use:** When user says "build authentication" or "create payment system" or "we need feature X" - this is your starting point for building any feature.

**Mode:** Conversational approach (NOT workflows) - have a design discussion to understand requirements before creating any spec.

**What to do when user says "build X":**

1. **Query for domain knowledge to inform design discussion:**
   ```python
   pos_search_project(content_type="standards", query="how to [domain] best practices")
   pos_search_project(content_type="standards", query="[technology] patterns")
   ```

2. **Ask clarifying questions in conversational design discussion:**
   - "Will this be for web, mobile, or both?"
   - "Do you have existing systems to integrate with?"
   - "What are the scale requirements?"
   - "Any compliance needs (GDPR, HIPAA)?"

3. **Propose approaches discovered from standards:**
   - "I found patterns for X using approach A or B"
   - "Approach A is simpler, Approach B scales better"
   - "What's your preference?"

4. **Document the design discussion:**
   - Create `.praxis-os/workspace/design/YYYY-MM-DD-feature-name.md` capturing the conversational exploration
   - Capture architecture decisions from discussion
   - Note trade-offs discussed
   - Include diagrams/examples

5. **Wait for user to trigger next phase:**
   - User says: "Create the spec" or
   - User says: "This design looks good, spec it"
   - **Do NOT auto-advance** - wait for explicit approval

**Critical:** Use conversational mode vs workflows in this phase. Design discussion needs flexibility that workflows don't provide.

**Output:** `design-doc.md` (informal design discussion capture)

**Duration:** 5-30 minutes typically

---

### Phase 2: Structured Spec Creation

**Trigger:** After design discussion, user says "Create the spec" OR "This design looks good, spec it"

**Mode:** Structured workflow-driven (NOT conversational anymore)

**How to move from design discussion to formal spec:**

1. **Query to discover how to create specification:**
   ```python
   pos_search_project(content_type="standards", query="how to create specification")
   ```
   
   **Critical:** Do NOT hardcode workflow names in your development process - always query to discover current workflows

2. **Use discovered workflow for building the spec:**
   - Follow workflow's systematic guidance
   - Phase-gated execution ensures quality
   - Complete checkpoints at each phase
   - Provide evidence requirements

3. **Create formal specification for building the feature:**
   - README.md (executive summary of what to build)
   - srd.md (business requirements)
   - specs.md (technical design for implementation)
   - tasks.md (breakdown of work from requirements to code)
   - implementation.md (detailed guidance for developers)

4. **Present spec for approval before implementation:**
   - User reviews specification files
   - User requests changes to requirements or design
   - You iterate based on feedback

5. **Wait for approval to advance to implementation:**
   - User says: "Approved" or "Implement the spec"
   - User may request team review first
   - **Do NOT start implementation without approval**

**This phase uses workflows vs conversational approach** - You need structure for systematic spec creation

**Output:** `.praxis-os/specs/YYYY-MM-DD-feature-name/` directory

**Duration:** 30 minutes - 2 hours typically

---

### Phase 3: Structured Implementation

**Trigger:** After spec approval, user says "Implement the spec" OR "Approved, build it"

**Mode:** Structured workflow-driven (systematic implementation from requirements to code)

**How to go from spec to production code:**

1. **Query to discover how to implement from spec:**
   ```python
   pos_search_project(content_type="standards", query="how to execute specification")
   ```
   
   **Critical:** Always query for implementation workflow in your development process - don't hardcode workflow names

2. **Use discovered workflow to build from requirements to code:**
   - Parse specification files (requirements, design, tasks)
   - Phase-gated implementation ensures systematic execution
   - Quality validation at each phase
   - Systematic test creation alongside code

3. **Implement feature systematically going from requirements to code:**
   - Phase 0: Review spec and setup structure
   - Phase 1: Core implementation of feature
   - Phase 2: Tests (unit, integration, e2e) 
   - Phase 3: Documentation for the feature
   - Phase 4: Quality validation (tests passing, linter clean)

4. **Present complete implementation of the feature:**
   - Production code implementing all requirements
   - Comprehensive tests validating behavior
   - Documentation explaining how to use the feature
   - All tests passing, linter clean

**This phase uses workflows for systematic building** - Structure ensures going from requirements to production code reliably

**Output:** Production code + tests + documentation (complete feature ready to ship)

**Duration:** 2-8 hours typically (depends on feature scope)

---

## What Are Phase Boundaries (CRITICAL)?

**You CANNOT:**
- ❌ Skip Phase 1 (design discussion) → Leads to misunderstanding requirements
- ❌ Skip Phase 2 (spec creation) → Leads to implementation errors and missed requirements
- ❌ Auto-advance phases without human trigger → Human approval required

**Each phase ends with explicit human trigger for next phase:**

```
Phase 1 ends when user says:
→ "Create the spec" or "This design looks good, spec it"

Phase 2 ends when user says:
→ "Implement the spec" or "Approved, build it"

Phase 3 ends when:
→ Implementation complete, tests passing, presented to user
```

**Why boundaries matter:**
- Design discussion ensures understanding before formalization
- Spec approval ensures agreement before implementation
- Implementation approval ensures quality before shipping

---

## What Are Phase Characteristics?

| Aspect | Phase 1: Design | Phase 2: Spec | Phase 3: Implementation |
|--------|-----------------|---------------|------------------------|
| **Mode** | Conversational | Workflow-driven | Workflow-driven |
| **Tools** | Query standards only | Workflow tools | Workflow tools |
| **Formality** | Informal exploration | Formal document | Production code |
| **Output** | design-doc.md | .praxis-os/specs/ | Code + tests + docs |
| **Duration** | Minutes | 30min - 2hrs | 2-8 hours |
| **Approval** | "Create spec" trigger | "Implement" trigger | Quality validation |
| **Flexibility** | High (exploratory) | Medium (structured) | Low (spec-driven) |

---

## What Is the Complete Development Checklist?

**Phase 1: Conversational Design**
- [ ] User initiated with "Build X" or similar
- [ ] Queried for domain patterns and best practices
- [ ] Asked clarifying questions about requirements
- [ ] Proposed approaches with trade-offs
- [ ] Created design-doc.md capturing conversation
- [ ] Waiting for "create spec" trigger (NOT auto-advancing)

**Phase 2: Structured Spec**
- [ ] User explicitly triggered with "create the spec"
- [ ] Queried: `pos_search_project(content_type="standards", query="how to create specification")`
- [ ] Discovered current spec creation workflow
- [ ] Executed workflow systematically
- [ ] Created all required spec files
- [ ] Presented for review
- [ ] Waiting for approval (NOT auto-implementing)

**Phase 3: Structured Implementation**
- [ ] User explicitly triggered with "implement the spec"
- [ ] Queried: `pos_search_project(content_type="standards", query="how to execute specification")`
- [ ] Discovered current implementation workflow
- [ ] Executed workflow systematically
- [ ] Implemented with tests and docs
- [ ] All tests passing
- [ ] Linter clean
- [ ] Presented complete work

---

## 📚 Examples

### Example 1: Authentication Feature (Complete Three-Phase Flow)

**Phase 1: Conversational Design (10 minutes)**

```
User: "Build authentication"

Agent: [Queries for patterns]
pos_search_project(content_type="standards", query="authentication patterns best practices")

Agent: "I found JWT and OAuth patterns. Questions:
       - Web only or mobile too?
       - Social auth needed?
       - Session duration requirements?"

User: "Web, Google OAuth, 24hr sessions"

Agent: [Creates design-doc.md with architecture]
"I've documented an OAuth 2.0 architecture with:
 - Google OAuth integration
 - 24hr access tokens
 - 7-day refresh tokens
 - Redis session storage
 
 design-doc.md is ready for review."

User: "Looks good"
```

**Phase 2: Spec Creation (45 minutes)**

```
User: "Create the spec"

Agent: [Discovery]
pos_search_project(content_type="standards", query="how to create specification")

Agent: [Finds current workflow, executes it]
"Starting spec creation workflow...
 Phase 0: Analyzing design doc
 Phase 1: Creating SRD (business requirements)
 Phase 2: Creating technical specs
 Phase 3: Breaking down tasks
 Phase 4: Writing implementation guidance
 
 Spec complete in .praxis-os/specs/2025-10-12-oauth-auth/"

User: [Reviews files]
"Add rate limiting to token endpoint"

Agent: [Updates specs.md and tasks.md]
"Updated. Spec now includes:
 - Rate limiting design (100 req/min per IP)
 - New task for implementing rate limiter"

User: "Approved"
```

**Phase 3: Implementation (6 hours)**

```
User: "Implement it"

Agent: [Discovery]
pos_search_project(content_type="standards", query="how to execute specification")

Agent: [Finds current workflow, executes it]
"Starting implementation workflow...
 Phase 0: Setting up structure
 Phase 1: Implementing OAuth flow
 Phase 2: Implementing rate limiting
 Phase 3: Writing tests (47 tests)
 Phase 4: Writing documentation
 Phase 5: Quality validation
 
 All tests passing ✓
 Linter clean ✓
 
 Implementation complete:
 - src/auth/oauth.py
 - src/auth/rate_limiter.py
 - tests/auth/ (47 tests)
 - docs/authentication.md"
```

---

### Example 2: Payment System (Showing Phase Boundaries)

**Phase 1: Design**

```
User: "Create payment processing"

Agent: [Conversational exploration]
- Asks about payment providers
- Discusses PCI compliance
- Explores architecture options
- Creates design-doc.md

User: [Reviews design]
"Change from Stripe to multiple providers"

Agent: [Updates design-doc.md]

User: "Perfect. Create the spec"  ← EXPLICIT PHASE TRANSITION
```

**Phase 2: Spec**

```
Agent: [Queries for spec workflow]
[Executes systematic spec creation]
[Creates comprehensive spec]

User: [Team reviews spec]
"Approved after team review"  ← EXPLICIT PHASE TRANSITION
```

**Phase 3: Implementation**

```
Agent: [Queries for implementation workflow]
[Systematic implementation with tests]
[Presents production-ready code]
```

---

## 🚫 Anti-Patterns

### Anti-Pattern 1: Skipping Design Phase

**Wrong:**
```
User: "Build authentication"
Agent: [Immediately creates spec or starts coding]
```

**Why it fails:**
- Misses requirements clarification
- No exploration of approaches
- User expectations not understood

**Right:**
```
User: "Build authentication"
Agent: [Asks clarifying questions]
Agent: [Explores design through conversation]
Agent: [Creates design-doc.md]
Agent: [Waits for "create spec" trigger]
```

---

### Anti-Pattern 2: Hardcoding Workflow Names

**Wrong:**
```python
if user_says_create_spec:
    start_workflow("spec_creation_v1", ...)
```

**Why it fails:**
- Breaks when v2 is released
- Can't discover better workflows
- Defeats discovery architecture

**Right:**
```python
# Discover current workflow
pos_search_project(content_type="standards", query="how to create specification")
# Returns current best practice (might be v2, v3, different workflow)
# Use whatever is discovered
```

---

### Anti-Pattern 3: Auto-Advancing Phases

**Wrong:**
```
Phase 1 complete → Agent auto-creates spec
Phase 2 complete → Agent auto-implements
```

**Why it fails:**
- No human approval gates
- User loses control
- Can't review before commitment

**Right:**
```
Phase 1 complete → Wait for "create spec" trigger
Phase 2 complete → Wait for "implement" trigger
```

---

### Anti-Pattern 4: Using Workflows in Phase 1

**Wrong:**
```
User: "Build authentication"
Agent: start_workflow("design_workflow", ...)
```

**Why it fails:**
- Design needs conversational flexibility
- Workflows are too rigid for exploration
- Premature structure

**Right:**
```
User: "Build authentication"  
Agent: [Pure conversation with queries for patterns]
```

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **User says "build X"** | `pos_search_project(content_type="standards", query="user wants me to build something what do I do")` |
| **Not sure where to start** | `pos_search_project(content_type="standards", query="user says build authentication where do I start")` |
| **Wondering if you should code now** | `pos_search_project(content_type="standards", query="should I start coding immediately")` |
| **Need to know the approach** | `pos_search_project(content_type="standards", query="what's the development approach")` |
| **Confused about discuss vs spec** | `pos_search_project(content_type="standards", query="do I start with spec or discussion")` |
| **Don't know when to use workflow** | `pos_search_project(content_type="standards", query="am I supposed to use workflow or talk")` |
| **User gave requirements** | `pos_search_project(content_type="standards", query="user gave requirements should I write code now")` |
| **Starting new feature** | `pos_search_project(content_type="standards", query="what do I do first when user wants feature")` |

---

## 🔗 Related Standards

**Query workflow for building features:**

1. **Start with development process** → `pos_search_project(content_type="standards", query="prAxIs OS development process")` (this document)
2. **Learn about spec creation** → `pos_search_project(content_type="standards", query="how to create specification")`
3. **Learn about spec execution** → `pos_search_project(content_type="standards", query="how to execute specification")`
4. **Understand operating model** → `pos_search_project(content_type="standards", query="prAxIs OS operating model human AI partnership")`

**By Phase:**

**Phase 1 (Design):**
- Query: `pos_search_project(content_type="standards", query="[domain] architecture patterns")`
- Query: `pos_search_project(content_type="standards", query="[technology] best practices")`

**Phase 2 (Spec):**
- Query: `pos_search_project(content_type="standards", query="how to create specification")`
- Query: `pos_search_project(content_type="standards", query="spec structure requirements")`

**Phase 3 (Implementation):**
- Query: `pos_search_project(content_type="standards", query="how to execute specification")`
- Query: `pos_search_project(content_type="standards", query="production code quality standards")`

---

**Remember**: Three distinct phases with explicit transitions. Query to discover workflows, don't hardcode. Human approval required between phases. This process ensures quality through systematic execution while maintaining conversational flexibility where needed.
