# Tasks.md Template

Template for creating tasks.md during Phase 3 (Task Breakdown).

---

## Complete tasks.md Structure

```markdown
# Implementation Tasks

**Project:** {FEATURE_NAME}  
**Date:** {CURRENT_DATE}  
**Status:** Draft - Pending Approval

---

## Time Estimates

### Human Implementation (Traditional)
- **Phase 1:** {hours} ({description})
- **Phase 2:** {hours} ({description})
- **Total:** {hours} ({days})

### AI Agent + Human Orchestration (prAxIs OS)
- **Phase 1:** {wall clock hours}h wall, {human minutes} min active ({leverage}x)
- **Phase 2:** {wall clock hours}h wall, {human minutes} min active ({leverage}x)
- **Total:** {wall clock hours}h wall, {human hours}h active ({leverage}x leverage)

---

## Phase 1: {Phase Name}

**Objective:** {What this phase accomplishes}

**Estimated Duration:** {hours}

### Phase 1 Tasks

- [ ] **Task 1.1**: {Task name}
  - **Human Baseline:** {hours} ({S/M/L})
  - **prAxIs OS:** {wall hours}h wall, {active min} min active ({leverage}x)
  
  - {Action item}
  - {Action item}
  - Verify {verification}
  
  **Acceptance Criteria:**
  - [ ] {Criterion 1}
  - [ ] {Criterion 2}

- [ ] **Task 1.2**: {Task name}
  - **Human Baseline:** {hours} ({S/M/L})
  - **prAxIs OS:** {wall hours}h wall, {active min} min active ({leverage}x)
  
  - {Action item}
  
  **Acceptance Criteria:**
  - [ ] {Criterion}

---

## Phase 2: {Phase Name}

[Repeat structure]

---

## Dependencies

### Phase 1 → Phase 2
{Describe dependency}

---

## Risk Mitigation

### Risk: {Risk description}
**Mitigation:** {How to mitigate}

---

## Testing Strategy

### Unit Tests
- {What to test}

### Integration Tests
- {What to test}

---

## Acceptance Criteria Summary

### Phase 1
- [ ] {High-level criterion}

### Phase 2
- [ ] {High-level criterion}
```

---

## Task Format Guidelines

### Good Task Format

```markdown
- [ ] **Task 1.1**: Create database schema
  - **Human Baseline:** 4 hours (M)
  - **prAxIs OS:** 4h wall clock, 12 min active (20x leverage)
  
  - Define tables for users, resources, tags
  - Add indexes for foreign keys and frequently queried columns
  - Create migration file with up/down migrations
  - Verify schema matches data models from specs.md
  
  **Acceptance Criteria:**
  - [ ] All tables created with correct columns and types
  - [ ] Foreign key constraints defined
  - [ ] Indexes created for performance
  - [ ] Migration runs successfully (up and down)
  - [ ] Schema documentation updated
```

**Why Good:**
- Dual time estimates (human baseline vs Agent OS)
- Shows leverage multiplier (20x)
- Clear wall clock vs active time distinction
- Specific action items
- Clear verification step
- Measurable acceptance criteria
- Traceable to specs.md

### Poor Task Format

```markdown
- [ ] **Task 1.1**: Setup database
  - Create database
  
  **Acceptance Criteria:**
  - [ ] Database works
```

**Why Bad:**
- Vague action items
- No verification
- Unmeasurable criteria
- Not actionable

---

## Acceptance Criteria Guidelines

### INVEST Criteria

**I**ndependent: Can be completed independently  
**N**egotiable: Details can be refined  
**V**aluable: Delivers clear value  
**E**stimable: Can be sized and estimated  
**S**mall: Fits in reasonable timeframe  
**T**estable: Has clear success criteria

### Good Acceptance Criteria

```markdown
**Acceptance Criteria:**
- [ ] All unit tests passing (>80% coverage)
- [ ] API endpoint responds within 200ms (p95)
- [ ] Error handling covers 5 identified edge cases
- [ ] Documentation includes 3 code examples
- [ ] Linter reports zero errors
```

**Why Good:** Specific, measurable, testable

### Poor Acceptance Criteria

```markdown
**Acceptance Criteria:**
- [ ] Code is done
- [ ] Tests exist
- [ ] Works well
```

**Why Bad:** Vague, not measurable

---

## Dependency Mapping

### Linear Dependencies

```
Phase 1 → Phase 2 → Phase 3
  ↓         ↓         ↓
Task 1.1  Task 2.1  Task 3.1
Task 1.2  Task 2.2  Task 3.2
```

### Parallel with Sync Points

```
Phase 1
├── Task 1.1 (parallel)
├── Task 1.2 (parallel)
└── Task 1.3 (depends on 1.1 + 1.2)
```

### Task-Level Dependencies

```markdown
- [ ] **Task 2.3**: Implement API endpoints
  - **Depends on:** Task 2.1 (data models), Task 2.2 (business logic)
```

---

## Time Estimation Guidelines

### Dual Estimation: Human vs AI Agent

prAxIs OS requires **two time estimates** to show the leverage multiplier (20-40x typical).

**For complete dual estimation guidance, query these standards:**

1. **Core Formula & Calculation:**
   ```
   search_standards("H W A L variables wall clock duration human active time")
   ```
   Returns: Complete 4-step calculation (H → W → A → L) with examples

2. **Task Type Multipliers:**
   ```
   search_standards("table boilerplate setup straightforward logic complex algorithm")
   ```
   Returns: Complete table with AI multipliers (0.8x-1.5x) and orchestration % (3-10%)

3. **What Counts as Active Time:**
   ```
   search_standards("reading task specification giving direction reviewing output")
   ```
   Returns: Detailed breakdown of what to include/exclude in orchestration time

4. **Task Format:**
   ```
   search_standards("task format example Human Baseline Agent OS")
   ```
   Returns: Template format with leverage multiplier shown

5. **Parallel Multiplier Effect:**
   ```
   search_standards("parallel multiplier effect")
   ```
   Returns: How parallel work creates 100-400x effective leverage

6. **Calibration Guidance:**
   ```
   search_standards("start conservative 1.2x multiplier 8-10% orchestration")
   ```
   Returns: Conservative starting point, refinement over 5-10 tasks

---

### Quick Formula (One-Liner)

```
H (baseline) → W = H × M (wall clock) → A = W × O (active time) → L = H ÷ A (leverage)

Typical: H=4h, M=1.0, W=4h, O=0.05, A=12min → L=20x
```

---

### Task Format Example

```markdown
- [ ] **Task 1.1**: Create database schema
  - **Human Baseline:** 4 hours (M)
  - **prAxIs OS:** 4h wall clock, 12 min active (20x leverage)
  
  - Define tables for users, resources, tags
  - Add indexes for foreign keys
  - Create migration file
  - Verify schema matches specs.md
  
  **Acceptance Criteria:**
  - [ ] All tables created with correct types
  - [ ] Foreign key constraints defined
  - [ ] Indexes created for performance
  - [ ] Migration runs successfully
```

---

### T-Shirt Sizing (Human Baseline)

- **Small (S):** 1-2 hours
- **Medium (M):** 2-4 hours
- **Large (L):** 4-8 hours
- **Extra Large (XL):** 8-16 hours (consider breaking down)

---

## Validation Gate Checklist

For each phase, include:

```markdown
## Phase {N} Validation Gate

Before advancing to Phase {N+1}:
- [ ] All tasks in Phase {N} completed ✅/❌
- [ ] All acceptance criteria met ✅/❌
- [ ] All tests passing ✅/❌
- [ ] No linting errors ✅/❌
- [ ] Code reviewed ✅/❌
- [ ] Documentation updated ✅/❌
```

---

## Common Patterns

### Setup Phase (Usually Phase 1)

- Directory structure
- Configuration files
- Database setup
- Dependency installation

### Implementation Phase (Middle phases)

- Core functionality
- Business logic
- Data access
- API endpoints

### Testing Phase (Late phase)

- Unit tests
- Integration tests
- Performance tests
- Documentation

### Deployment Phase (Final phase)

- Deployment scripts
- Monitoring setup
- Documentation finalization
- Announcement/handoff

