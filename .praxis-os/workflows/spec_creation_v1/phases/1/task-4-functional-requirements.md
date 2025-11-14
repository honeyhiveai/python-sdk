# Task 3: List Functional Requirements

**Phase:** 1 (Requirements Gathering)  
**Purpose:** Define specific capabilities the system must provide  
**Estimated Time:** 10 minutes

---

## 🎯 Objective

Document specific, testable functional requirements that define WHAT the system must do. Functional requirements translate user stories into concrete system capabilities.

---

## Prerequisites

🛑 EXECUTE-NOW: Tasks 1 & 2 must be completed

⚠️ MUST-READ: Query MCP and reference template

```python
MCP: search_standards("functional requirements standards")
```

See `core/srd-template.md` for FR format and examples.

---

## Steps

### Step 1: Add Functional Requirements Section

Append to srd.md using structure from `core/srd-template.md`:

```bash
cat >> .praxis-os/specs/{SPEC_DIR}/srd.md << 'EOF'

---

## 4. Functional Requirements

Functional requirements specify capabilities the system must provide.

---

EOF
```

### Step 2: Derive Requirements from User Stories

For each user story, identify specific system capabilities needed.

**Example from `core/srd-template.md`:**
- User Story: "export to CSV"
- → FR-001: CSV export functionality
- → FR-002: Preserve filters when exporting
- → FR-003: Handle special characters

### Step 3: Write Functional Requirements

Follow the FR pattern from `core/srd-template.md`:

```markdown
### FR-001: {Requirement Title}

**Description:** The system shall {specific capability}.

**Priority:** {Critical/High/Medium/Low}

**Related User Stories:** Story {number}

**Acceptance Criteria:**
- {Specific, testable criterion}
- {Specific, testable criterion}
```

**Key:** 
- Use "system shall" language
- Make criteria measurable
- See `core/srd-template.md` for good vs bad examples

### Step 4: Organize by Category

Group requirements by functional area:

```markdown
## 4.1 Requirements by Category

### Data Management
- FR-001, FR-005, FR-007

### User Interface
- FR-002, FR-003

### API / Integration
- FR-004, FR-008
```

### Step 5: Create Traceability Matrix

```markdown
## 4.2 Traceability Matrix

| Requirement | User Stories | Business Goals | Priority |
|-------------|--------------|----------------|----------|
| FR-001 | Story 1, 3 | Goal 1 | Critical |
| FR-002 | Story 2 | Goal 1 | High |
```

### Step 6: Reference Supporting Documentation

If Phase 0 completed:

```markdown
## 4.3 Supporting Documentation

Requirements informed by:
- **{DOCUMENT_NAME}**: {specific insight}
```

### Step 7: Validate Requirements

Check each requirement against criteria from `core/srd-template.md`:
- Specific, Testable, Unambiguous, Complete, Consistent, Feasible, Necessary

📊 COUNT-AND-DOCUMENT: Functional requirements
- Total: [number]
- Critical: [number]
- High: [number]
- Categories: [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] At least 3 functional requirements defined ✅/❌
- [ ] Each has FR-XXX identifier ✅/❌
- [ ] Each has clear description and acceptance criteria ✅/❌
- [ ] Requirements are specific and testable ✅/❌
- [ ] Traceability to user stories established ✅/❌

🚨 FRAMEWORK-VIOLATION: Vague requirements

See `core/srd-template.md` anti-patterns section. Every requirement MUST have specific, measurable criteria.

---

## Next Task

🎯 NEXT-MANDATORY: [task-4-nonfunctional-requirements.md](task-4-nonfunctional-requirements.md)