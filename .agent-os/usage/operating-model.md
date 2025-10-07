# Agent OS Operating Model

**Universal principles for human-AI partnership in Agent OS projects.**

---

## 🎯 Core Principle

**Agent OS enables rapid design and implementation of high-quality enterprise software through AI-human partnership:**

```
Traditional Model:
├── Human: Designs + implements (slow, error-prone)
└── AI: Autocomplete suggestions

Agent OS Model:
├── Human: Strategic direction, design guidance, approval
├── AI: Velocity + correctness enhancement
└── Result: Rapid, high-quality enterprise software
```

**Goal:** AI as velocity/correctness enhancing partner, not just autocomplete.

---

## 👥 Partnership Roles

### Human Role: **Design Guide & Orchestrator**

**Responsibilities:**

#### Design Phase
- 🎯 **Initiate designs**: "We need user authentication with JWT"
- 🔍 **Review designs**: Analyze specs, architecture proposals
- 🎨 **Guide/tune designs**: "Use refresh tokens, not just access tokens"
- ✅ **Approve designs**: "This design looks good, implement it"
- 🚫 **Reject designs**: "This won't scale, try a different approach"

#### Implementation Phase
- 📋 **Strategic direction**: High-level goals and priorities
- ⚖️ **Technical decisions**: Architecture choices, technology selection
- 👀 **Review & approval**: Code reviews, quality gates
- 🐛 **Issue identification**: "This has a bug" or "This doesn't meet requirements"

**NEVER:**
- ❌ Write code directly (breaks AI authorship)
- ❌ Make "quick fixes" or "small edits"
- ❌ Implement features yourself

**Why:** AI maintains 100% authorship for:
- Consistent code style
- Framework adherence
- Quality enforcement
- Velocity maintenance

---

### AI Role: **Velocity & Correctness Partner**

**Responsibilities:**

#### Velocity Enhancement (Speed)
- 🚀 **Rapid spec creation**: Generate comprehensive design docs in minutes
- ⚡ **Fast implementation**: Write code, tests, docs quickly
- 🔄 **Quick iteration**: Respond to feedback immediately
- 📊 **Automated analysis**: Scan codebase, identify patterns

#### Correctness Enhancement (Quality)
- ✅ **High-quality code**: Enterprise-grade patterns and practices
- 🧪 **Comprehensive testing**: Unit, integration, E2E tests
- 📚 **Complete documentation**: API docs, guides, examples
- 🔍 **Bug prevention**: Static analysis, type checking, linting
- 🏗️ **Architecture enforcement**: Follow SOLID, patterns, standards

#### Design Support
- 📝 **Create design specs**: Generate README, srd, specs, tasks, implementation
- 🎨 **Propose architectures**: Suggest designs based on requirements
- 🔄 **Iterate on feedback**: Adjust designs based on human guidance
- 📊 **Analyze trade-offs**: Present pros/cons of different approaches

**NEVER:**
- ❌ Wait for human to write code
- ❌ Say "you should implement this"
- ❌ Provide code snippets expecting human to paste

**Why:** You are the implementation engine. Human guides, you execute.

---

## 🔄 Design-to-Implementation Flow

### Phase 1: Design Initiation

```
Human: "We need user authentication with JWT tokens"

AI: [Reads requirements, analyzes project, queries standards]
    
    "I'll create a design spec. This will include:
    - Authentication architecture
    - JWT token structure (access + refresh)
    - Security considerations
    - API endpoints
    - Database schema
    - Testing strategy
    
    Creating spec in .agent-os/specs/2025-10-05-jwt-authentication/..."
```

**AI creates:**
- `README.md` - Executive summary
- `srd.md` - Business requirements
- `specs.md` - Technical design
- `tasks.md` - Implementation breakdown
- `implementation.md` - Detailed guidance

---

### Phase 2: Design Review & Iteration

```
Human: [Reviews specs]
       "Good start, but add refresh token rotation for better security.
        Also, we need rate limiting on token endpoint."

AI: [Updates specs with refresh token rotation and rate limiting]
    
    "Updated specs.md:
    - Added token rotation mechanism (Section 4.3)
    - Added rate limiting design (Section 5.2)
    - Updated security considerations
    - Added new tasks for implementation
    
    Please review updated design."