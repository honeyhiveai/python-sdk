# Task 2: Document User Stories

**Phase:** 1 (Requirements Gathering)  
**Purpose:** Capture user needs and desired outcomes  
**Estimated Time:** 5 minutes

---

## 🎯 Objective

Document user stories that describe who needs this feature, what they want to accomplish, and why it matters. User stories keep requirements focused on actual user needs rather than technical solutions.

---

## Prerequisites

🛑 EXECUTE-NOW: Task 1 must be completed

⚠️ MUST-READ: Reference template

See `core/srd-template.md` for user story format and examples.

---

## Steps

### Step 1: Add User Stories Section

Append to srd.md:

```bash
cat >> .praxis-os/specs/{SPEC_DIR}/srd.md << 'EOF'

---

## 3. User Stories

User stories describe the feature from the user's perspective.

### Story Format

**As a** {user type}  
**I want to** {capability}  
**So that** {benefit}

---

EOF
```

### Step 2: Identify User Personas

Identify who will use this feature:
- End users (developers, analysts, customers, etc.)
- System administrators
- API consumers
- Other systems or services

📊 COUNT-AND-DOCUMENT: Personas identified
- Total personas: [number]
- Primary persona: [name/description]

### Step 3: Write User Stories

Follow the pattern from `core/srd-template.md` section "Good User Story":

```markdown
### Story 1: {Short Title}

**As a** {specific user type}  
**I want to** {specific capability}  
**So that** {specific benefit}

**Acceptance Criteria:**
- Given {context}
- When {action}
- Then {expected outcome}

**Priority:** {Critical/High/Medium/Low}
```

See `core/srd-template.md` for good vs bad examples.

### Step 4: Prioritize Stories

Rank by:
- Business goal alignment (from Task 1)
- User impact (how many users, how often)
- Dependencies (must-haves vs nice-to-haves)

Add priority summary:

```markdown
## 3.1 Story Priority Summary

**Critical (Must-Have):**
- Story {number}: {title}

**High Priority:**
- Story {number}: {title}
```

### Step 5: Reference Supporting Documentation

If Phase 0 completed:

```markdown
## 3.2 Supporting Documentation

User needs from supporting documents:
- **{DOCUMENT_NAME}**: {user need}

See `supporting-docs/INDEX.md` for details.
```

### Step 6: Validate Stories

Check INVEST criteria (see `core/srd-template.md`):
- Independent, Negotiable, Valuable, Estimable, Small, Testable

📊 COUNT-AND-DOCUMENT: User stories
- Total: [number]
- Critical: [number]
- High: [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] At least 1 user story documented ✅/❌
- [ ] Follows "As a...I want...So that" format ✅/❌
- [ ] Each story has acceptance criteria ✅/❌
- [ ] Stories are prioritized ✅/❌
- [ ] Focus on user needs (not technical solutions) ✅/❌

🚨 FRAMEWORK-VIOLATION: Solution-focused stories

Stories must describe WHAT users need and WHY, not HOW. See `core/srd-template.md` anti-patterns section.

---

## Next Task

🎯 NEXT-MANDATORY: [task-3-functional-requirements.md](task-3-functional-requirements.md)