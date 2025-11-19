# Creating prAxIs OS Specifications

**Universal documentation for writing design specifications in any prAxIs OS project.**

**Keywords for search**: creating specs, how to write specifications, spec structure, design documents, software requirements document, SRD, specification templates, task breakdown, implementation planning

---

## 🚨 Quick Reference (TL;DR)

**5-File Spec Structure:**
1. **README.md** - Executive summary, status, quick overview (for stakeholders)
2. **srd.md** - Business requirements, goals, success metrics (Software Requirements Document)
3. **specs.md** - Technical specifications, architecture, design decisions
4. **tasks.md** - Implementation task breakdown with phases and dependencies
5. **implementation.md** - Detailed step-by-step implementation guidance

**All specs live in:** `.praxis-os/specs/YYYY-MM-DD-feature-name/`

**Quick Start:**
1. Create spec directory: `.praxis-os/specs/2025-10-11-my-feature/`
2. Copy 5 templates from this guide
3. Fill in README.md first (executive summary)
4. Then srd.md (business requirements)
5. Then specs.md (technical design)
6. Then tasks.md (break down into phases/tasks)
7. Finally implementation.md (detailed guidance)

**When to create a spec:**
- ✅ Feature affects multiple files/components
- ✅ Architectural decisions needed
- ✅ Need to track multi-phase work
- ✅ Collaboration with team/stakeholders
- ❌ Simple bug fixes (no spec needed)
- ❌ Single-file changes (no spec needed)

---

## Questions This Answers

- "How do I create a specification in prAxIs OS?"
- "What files should be in a spec directory?"
- "What's the difference between srd.md and specs.md?"
- "How do I structure tasks in tasks.md?"
- "What goes in README.md vs other files?"
- "When should I create a spec?"
- "How do I document requirements?"
- "How do I break down implementation tasks?"
- "What's a Software Requirements Document (SRD)?"
- "How do I document technical architecture?"
- "How do I track spec status?"
- "What templates should I use?"

---

## 🎯 What Is a Spec?

A **specification (spec)** is a design document that details a feature, enhancement, or architectural decision before implementation. Specs help:

- **Plan before coding** - Think through design challenges
- **Document decisions** - Record why choices were made
- **Enable collaboration** - Share context with team and AI
- **Track progress** - Break work into phases and tasks

---

## What is the Standard Spec Directory Structure?

All specs follow this standard structure (inspired by python-sdk prAxIs OS):

```
.praxis-os/specs/YYYY-MM-DD-feature-name/
├── README.md         # Executive summary, status, quick overview
├── srd.md           # Business requirements and goals (Software Requirements Document)
├── specs.md         # Technical specifications and design
├── tasks.md         # Implementation task breakdown
└── implementation.md # Detailed implementation guidance
```

### Optional Additional Files

```
├── testing-strategy.md   # Testing approach and requirements
├── case-study.md         # Real-world examples or case studies
├── VALIDATION.md         # Validation criteria and success metrics
└── [custom].md          # Any domain-specific documents
```

---

## What Templates Should I Use for Each File?

### How to Write README.md (File 1: Executive Summary)

```markdown
# [Feature Name] - Executive Summary

**Date:** YYYY-MM-DD  
**Status:** Design Phase | In Progress | Completed | Cancelled  
**Priority:** Critical | High | Medium | Low  
**Category:** [Category Name]

---

## 🎯 EXECUTIVE SUMMARY

### Strategic Vision
[1-2 paragraphs: What is this and why does it matter?]

### Core Innovation
[What makes this unique or important?]

### Business Impact

| Metric | Current State | After Implementation | Impact |
|--------|--------------|---------------------|---------|
| [Metric 1] | [Current] | [Future] | [Percentage] |
| [Metric 2] | [Current] | [Future] | [Percentage] |

---

## 📋 PROBLEM STATEMENT

[What problem are we solving?]

---

## 💡 SOLUTION OVERVIEW

[High-level solution approach]

---

## 📊 SUCCESS METRICS

- **Metric 1**: [Target]
- **Metric 2**: [Target]
- **Metric 3**: [Target]

---

## 📂 DETAILED DOCUMENTATION

- **[Business Requirements](srd.md)** - Goals, use cases, requirements
- **[Technical Specifications](specs.md)** - Architecture, design, APIs
- **[Implementation Plan](tasks.md)** - Phases, tasks, timeline
- **[Implementation Details](implementation.md)** - Code guidance, patterns
```

---

### How to Write srd.md (File 2: Software Requirements Document)

```markdown
# [Feature Name] - Software Requirements Document

**Business case, goals, and requirements.**

---

## 🎯 BUSINESS GOALS

### Primary Goals
1. [Goal 1]
2. [Goal 2]
3. [Goal 3]

### Success Criteria
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

---

## 👥 STAKEHOLDERS

### Primary Stakeholders
- **[Role]**: [Needs/Concerns]
- **[Role]**: [Needs/Concerns]

### Secondary Stakeholders
- **[Role]**: [Needs/Concerns]

---

## 📋 FUNCTIONAL REQUIREMENTS

### FR-1: [Requirement Name]
**Priority:** Must Have | Should Have | Nice to Have  
**Description:** [What the system must do]  
**Acceptance Criteria:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]

### FR-2: [Requirement Name]
...

---

## 🔒 NON-FUNCTIONAL REQUIREMENTS

### NFR-1: Performance
- [Performance requirement]

### NFR-2: Security
- [Security requirement]

### NFR-3: Scalability
- [Scalability requirement]

---

## ⚠️ CONSTRAINTS

### Technical Constraints
- [Constraint 1]
- [Constraint 2]

### Business Constraints
- [Constraint 1]
- [Constraint 2]

---

## 🎭 USER STORIES

### User Story 1
**As a** [user type]  
**I want** [capability]  
**So that** [benefit]

**Acceptance Criteria:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]

---

## 🚫 OUT OF SCOPE

[What is explicitly NOT included in this feature]
```

---

### How to Write specs.md (File 3: Technical Specifications)

```markdown
# [Feature Name] - Technical Specifications

**Architecture, design, and technical details.**

---

## 🏗️ ARCHITECTURE OVERVIEW

### System Diagram

```
[ASCII diagram or reference to diagram file]
```

### Components

#### Component 1: [Name]
**Purpose:** [What it does]  
**Responsibilities:**
- [Responsibility 1]
- [Responsibility 2]

#### Component 2: [Name]
...

---

## 📡 API SPECIFICATIONS

### API 1: [Name]

**Endpoint:** `[HTTP METHOD] /path/to/endpoint`  
**Purpose:** [What this API does]

**Request:**
```json
{
  "param1": "type",
  "param2": "type"
}
```

**Response:**
```json
{
  "result": "type",
  "status": "type"
}
```

**Error Handling:**
- `400`: [Error scenario]
- `404`: [Error scenario]
- `500`: [Error scenario]

---

## 💾 DATA MODELS

### Model 1: [Name]

```python
class ModelName:
    field1: Type  # Description
    field2: Type  # Description
```

**Validation Rules:**
- [Rule 1]
- [Rule 2]

---

## 🔄 WORKFLOW / PROCESS FLOW

### Workflow 1: [Name]

```
1. User/System triggers [event]
2. System performs [action]
3. System validates [condition]
4. If valid: [action A], else: [action B]
5. System returns [result]
```

---

## 🔐 SECURITY CONSIDERATIONS

### Authentication
- [How authentication works]

### Authorization
- [Who can access what]

### Data Protection
- [How data is protected]

---

## ⚡ PERFORMANCE CONSIDERATIONS

### Expected Load
- [Load characteristics]

### Performance Targets
- **Latency**: [Target]
- **Throughput**: [Target]
- **Scalability**: [Target]

### Optimization Strategies
- [Strategy 1]
- [Strategy 2]

---

## 🧪 TESTING STRATEGY

### Unit Testing
- [What will be unit tested]

### Integration Testing
- [What will be integration tested]

### End-to-End Testing
- [What will be E2E tested]

---

## 🔌 INTEGRATION POINTS

### Integration 1: [External System]
**Purpose:** [Why we integrate]  
**Method:** [How we integrate]  
**Error Handling:** [How failures are handled]

---

## 🚀 DEPLOYMENT STRATEGY

### Deployment Method
- [How this will be deployed]

### Rollout Plan
1. [Phase 1]
2. [Phase 2]
3. [Phase 3]

### Rollback Plan
- [How to rollback if issues occur]
```

---

### How to Write tasks.md (File 4: Implementation Task Breakdown)

```markdown
# [Feature Name] - Implementation Tasks

**Phased task breakdown for implementation.**

---

## 📊 IMPLEMENTATION PHASES

### Phase 1: Foundation (Week 1)

**Goal:** [What this phase achieves]

**Tasks:**
- [ ] **Task 1.1**: [Description]
  - **Estimated Time**: [Hours/Days]
  - **Dependencies**: [None | Task X.Y]
  - **Acceptance Criteria**:
    - [ ] [Criterion 1]
    - [ ] [Criterion 2]

- [ ] **Task 1.2**: [Description]
  - **Estimated Time**: [Hours/Days]
  - **Dependencies**: [Task 1.1]
  - **Acceptance Criteria**:
    - [ ] [Criterion 1]

**Phase Deliverables:**
- [Deliverable 1]
- [Deliverable 2]

**Validation Gate:**
- [ ] [Gate criterion 1]
- [ ] [Gate criterion 2]

---

### Phase 2: Core Implementation (Week 2)

[Same structure as Phase 1]

---

### Phase 3: Testing & Refinement (Week 3)

[Same structure as Phase 1]

---

### Phase 4: Documentation & Release (Week 4)

[Same structure as Phase 1]

---

## 🎯 MILESTONE TRACKING

| Milestone | Target Date | Status | Notes |
|-----------|------------|--------|-------|
| Phase 1 Complete | YYYY-MM-DD | ⏳ | |
| Phase 2 Complete | YYYY-MM-DD | ⏳ | |
| Phase 3 Complete | YYYY-MM-DD | ⏳ | |
| Phase 4 Complete | YYYY-MM-DD | ⏳ | |

---

## ⚠️ RISKS & MITIGATION

### Risk 1: [Risk Description]
**Likelihood:** High | Medium | Low  
**Impact:** High | Medium | Low  
**Mitigation Strategy:** [How to mitigate]

### Risk 2: [Risk Description]
...

---

## 📋 TASK DEPENDENCIES

```
Task 1.1 → Task 1.2 → Task 2.1
                  ↘ Task 2.2 → Task 3.1
```
```

---

### How to Write implementation.md (File 5: Detailed Implementation Guidance)

```markdown
# [Feature Name] - Implementation Details

**Detailed guidance for implementing this feature.**

---

## 🎯 IMPLEMENTATION OVERVIEW

This document provides detailed guidance for implementing [Feature Name]. Follow phases in order and complete validation gates before proceeding.

---

## 🔧 SETUP & PREREQUISITES

### Environment Setup
```bash
# Setup commands
[Command 1]
[Command 2]
```

### Dependencies
- **[Dependency 1]**: [Version] - [Purpose]
- **[Dependency 2]**: [Version] - [Purpose]

### Configuration
```json
{
  "config_key": "value",
  "description": "What this configures"
}
```

---

## 📂 FILE STRUCTURE

```
project/
├── component1/
│   ├── __init__.py
│   ├── core.py          # [Purpose]
│   └── utils.py         # [Purpose]
├── component2/
│   └── ...
└── tests/
    ├── test_component1.py
    └── test_component2.py
```

---

## 💻 IMPLEMENTATION PATTERNS

### Pattern 1: [Pattern Name]

**Use Case:** [When to use this pattern]

**Implementation:**
```python
# Code example showing the pattern
class ExamplePattern:
    def __init__(self):
        # Implementation details
        pass
    
    def method(self):
        # Pattern usage
        pass
```

**Best Practices:**
- [Best practice 1]
- [Best practice 2]

**Anti-Patterns to Avoid:**
- ❌ [Anti-pattern 1]
- ❌ [Anti-pattern 2]

---

### Pattern 2: [Pattern Name]

[Same structure as Pattern 1]

---

## 🧪 TESTING IMPLEMENTATION

### Unit Test Template

```python
import pytest
from component import ClassUnderTest

class TestClassName:
    def test_scenario_name(self):
        # Arrange
        sut = ClassUnderTest()
        
        # Act
        result = sut.method()
        
        # Assert
        assert result == expected_value
```

### Integration Test Template

```python
# Integration test example
@pytest.mark.integration
def test_integration_scenario():
    # Test real system interactions
    pass
```

---

## 🔍 CODE REVIEW CHECKLIST

**Before submitting for review, verify:**

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Code follows project style guide
- [ ] All public APIs have docstrings
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] Performance is acceptable
- [ ] Security considerations addressed
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated

---

## 📊 VALIDATION CRITERIA

### Functional Validation
- [ ] Feature works as specified
- [ ] All acceptance criteria met
- [ ] Edge cases handled

### Non-Functional Validation
- [ ] Performance meets targets
- [ ] Security requirements met
- [ ] Scalability verified

### Quality Validation
- [ ] Test coverage ≥ 90%
- [ ] No linter errors
- [ ] No type errors
- [ ] Documentation complete

---

## 🚀 DEPLOYMENT GUIDANCE

### Pre-Deployment Checklist
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Release notes prepared

### Deployment Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Post-Deployment Verification
- [ ] [Verification 1]
- [ ] [Verification 2]

### Rollback Procedure
1. [Rollback step 1]
2. [Rollback step 2]

---

## 🔧 TROUBLESHOOTING

### Issue 1: [Common Issue]
**Symptoms:** [What you'll see]  
**Cause:** [Why it happens]  
**Solution:** [How to fix]

### Issue 2: [Common Issue]
...

---

## 📚 ADDITIONAL RESOURCES

- [Resource 1]
- [Resource 2]
- [Resource 3]
```

---

## How to Validate Spec Completeness (Checklist)

When creating a new spec, ensure:

### Structure
- [ ] Directory named `YYYY-MM-DD-feature-name/`
- [ ] `README.md` with executive summary
- [ ] `srd.md` with business requirements
- [ ] `specs.md` with technical design
- [ ] `tasks.md` with implementation breakdown
- [ ] `implementation.md` with detailed guidance

### Content Quality
- [ ] Clear problem statement
- [ ] Specific success metrics
- [ ] Comprehensive requirements
- [ ] Detailed technical design
- [ ] Phased implementation plan
- [ ] Testing strategy included
- [ ] Security considerations addressed
- [ ] Performance targets defined

### Completeness
- [ ] All stakeholders identified
- [ ] All acceptance criteria defined
- [ ] All dependencies documented
- [ ] All risks identified with mitigation
- [ ] All integration points specified

---

## How to Review Specs?

### How to Self-Review Your Spec
1. Read spec end-to-end
2. Verify all sections are complete
3. Check for consistency across files
4. Validate technical feasibility

### How to Get Peer Review
1. Share spec with team/AI
2. Address feedback
3. Update documentation
4. Get approval

### How to Track Implementation Progress
1. Break into tasks
2. Assign ownership
3. Track progress
4. Update status regularly

---

## What are Spec Writing Best Practices?

### What TO DO:
✅ Write specs before coding  
✅ Use concrete examples  
✅ Define success metrics  
✅ Include diagrams/visuals  
✅ Document trade-offs  
✅ Update specs as design evolves  
✅ Link to related specs  
✅ Keep language clear and precise

### What NOT TO DO:
❌ Skip business requirements  
❌ Assume implementation details  
❌ Ignore non-functional requirements  
❌ Forget to update during implementation  
❌ Write specs that are too abstract  
❌ Neglect security/performance  
❌ Skip validation criteria

---

## When to Query This Guide

This guide is most valuable when:

1. **Starting a New Feature**
   - Situation: Need to document a new feature or architectural change
   - Query: `pos_search_project(content_type="standards", query="how to create specs")`

2. **Unsure About Spec Structure**
   - Situation: Don't know which file to put information in
   - Query: `pos_search_project(content_type="standards", query="spec structure README vs srd vs specs")`

3. **Creating Business Requirements**
   - Situation: Need template for Software Requirements Document
   - Query: `pos_search_project(content_type="standards", query="software requirements document template")`

4. **Breaking Down Implementation**
   - Situation: Need to create tasks.md with phases
   - Query: `pos_search_project(content_type="standards", query="how to break down implementation tasks")`

5. **Writing Technical Specs**
   - Situation: Need template for technical architecture
   - Query: `pos_search_project(content_type="standards", query="technical specification template")`

6. **Validating Spec Completeness**
   - Situation: Want to ensure all required sections are present
   - Query: `pos_search_project(content_type="standards", query="spec checklist requirements")`

### Query by Use Case

| Use Case | Example Query |
|----------|---------------|
| Starting new spec | `pos_search_project(content_type="standards", query="how to create specs")` |
| 5-file structure | `pos_search_project(content_type="standards", query="spec file structure")` |
| Business requirements | `pos_search_project(content_type="standards", query="SRD template")` |
| Technical design | `pos_search_project(content_type="standards", query="technical specification template")` |
| Task breakdown | `pos_search_project(content_type="standards", query="implementation task breakdown")` |
| Spec checklist | `pos_search_project(content_type="standards", query="spec completeness checklist")` |

---

## Cross-References and Related Guides

**Using Specs:**
- `workflows/spec_execution_v1/` - How to execute a spec systematically
  → `pos_search_project(content_type="standards", query="spec execution workflow")`

**AI Guidance:**
- `usage/ai-agent-quickstart.md` - How AI should implement specs
  → `pos_search_project(content_type="standards", query="AI agent quickstart")`

**Standards:**
- `standards/ai-safety/production-code-checklist.md` - Quality requirements for implementation
  → `pos_search_project(content_type="standards", query="production code checklist")`
- `standards/documentation/rag-content-authoring.md` - How to write discoverable documentation
  → `pos_search_project(content_type="standards", query="RAG content authoring")`

**Quality:**
- `standards/testing/test-pyramid.md` - Testing strategy for spec implementation
  → `pos_search_project(content_type="standards", query="test pyramid")`

**Query workflow:**
1. **Before**: `pos_search_project(content_type="standards", query="how to create specs")` → Learn structure and templates
2. **During**: Use templates from this guide to write each file
3. **Execute**: `pos_search_project(content_type="standards", query="spec execution workflow")` → Implement systematically
4. **Validate**: `pos_search_project(content_type="standards", query="production code checklist")` → Ensure quality

---

## 📞 Questions?

- **General spec questions**: See examples in `.praxis-os/specs/`
- **Template questions**: Refer to this document
- **Technical questions**: Consult team or AI assistant via MCP

---

**Remember:** Good specs save time, reduce bugs, and enable better AI assistance. Invest time upfront for better results downstream!
