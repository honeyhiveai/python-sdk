# Task 1: Define Business Goals

**Phase:** 1 (Requirements Gathering)  
**Purpose:** Articulate why this feature matters to the business  
**Estimated Time:** 5 minutes

---

## 🎯 Objective

Define clear business goals that this feature will achieve. Business goals provide strategic context for all technical decisions and help prioritize features when tradeoffs are necessary.

---

## Prerequisites

🛑 EXECUTE-NOW: Review Phase 0 insights (if available)

If Phase 0 was completed, review `supporting-docs/INDEX.md` for business-related insights.

⚠️ MUST-READ: Query MCP for guidance

```python
MCP: search_standards("creating specifications requirements")
```

⚠️ MUST-READ: Reference template

See `core/srd-template.md` for complete SRD structure and examples.

---

## Steps

### Step 1: Create srd.md with Business Goals Section

Use the template from `core/srd-template.md` to create srd.md:

```bash
cat > .praxis-os/specs/{SPEC_DIR}/srd.md << 'EOF'
# Software Requirements Document

**Project:** {FEATURE_NAME}  
**Date:** {CURRENT_DATE}  
**Priority:** {Critical/High/Medium/Low}  
**Category:** {Feature/Enhancement/Fix}

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for {brief_description}.

### 1.2 Scope
This feature will {brief_scope_statement}.

---

## 2. Business Goals

EOF
```

### Step 2: Write Business Goals

For each goal, answer: "What business outcome does this feature enable?"

Follow the pattern from `core/srd-template.md` section "Good Business Goal":
- Specific, measurable objective
- Success metrics with current → target state
- Clear business impact

Add to srd.md:

```markdown
### Goal 1: {Goal Title}

**Objective:** {Specific, measurable business outcome}

**Success Metrics:**
- {Metric 1}: {Current state} → {Target state}
- {Metric 2}: {Current state} → {Target state}

**Business Impact:**
- {Who benefits and how}
- {Expected value or cost savings}
```

### Step 3: Reference Supporting Documents (if Phase 0 completed)

```markdown
## 2.1 Supporting Documentation

The business goals above are informed by:
- **{DOCUMENT_NAME}**: {specific insight}

See `supporting-docs/INDEX.md` for complete analysis.
```

### Step 4: Validate Goals

Check each goal against criteria from `core/srd-template.md`:
- [ ] **Specific:** Clear what needs to be achieved
- [ ] **Measurable:** Has quantifiable success metrics
- [ ] **Business-Focused:** Explains business value
- [ ] **Actionable:** Can be addressed through requirements

📊 COUNT-AND-DOCUMENT: Business goals defined
- Total goals: [number]
- Goals with metrics: [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] srd.md created ✅/❌
- [ ] At least 1 business goal defined ✅/❌
- [ ] Each goal has clear objective ✅/❌
- [ ] Each goal has success metrics ✅/❌
- [ ] Business impact articulated ✅/❌
- [ ] Goals are specific and measurable ✅/❌

🚨 FRAMEWORK-VIOLATION: Generic business goals

Goals must have specific, measurable outcomes. See `core/srd-template.md` for good vs bad examples.

---

## Next Task

🎯 NEXT-MANDATORY: [task-2-user-stories.md](task-2-user-stories.md)

Continue to Task 2 to document user stories.