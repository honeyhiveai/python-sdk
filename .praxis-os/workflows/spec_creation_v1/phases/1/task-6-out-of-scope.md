# Task 5: Clarify Out-of-Scope Items

**Phase:** 1 (Requirements Gathering)  
**Purpose:** Explicitly state what will NOT be included  
**Estimated Time:** 5 minutes

---

## 🎯 Objective

Explicitly document what is out of scope. Defining boundaries prevents scope creep, manages expectations, and focuses effort on what matters most.

---

## Prerequisites

🛑 EXECUTE-NOW: Tasks 1-4 must be completed

⚠️ KEY INSIGHT: Out-of-scope is as important as in-scope

Prevents scope creep, manages expectations, provides clear boundaries.

---

## Steps

### Step 1: Add Out-of-Scope Section

Append to srd.md:

```bash
cat >> .praxis-os/specs/{SPEC_DIR}/srd.md << 'EOF'

---

## 6. Out of Scope

Explicitly defines what is NOT included. Items may be considered for future phases.

### Explicitly Excluded

---

EOF
```

### Step 2: Identify Out-of-Scope Items

Consider categories:
- Features not included (related but not required)
- User types not supported (edge case personas)
- Platforms not supported (OS, browsers, devices)
- Integrations not included (external systems)
- Quality levels beyond defined NFRs
- Compliance standards not required

### Step 3: Document Exclusions

Follow pattern from `core/srd-template.md`:

```markdown
#### Features

**Not Included in This Release:**
1. **{Feature Name}**
   - **Reason:** {Why excluded}
   - **Future Consideration:** {Potential for future}

#### User Types

**Not Supported:**
- **{User Type}**: {Reason}

#### Platforms

**Not Supported:**
- **{Platform}**: {Reason}

#### Integrations

**Not Included:**
- **{System}**: {Reason}
```

**Key:** Each exclusion needs clear rationale.

### Step 4: Add Future Roadmap

```markdown
## 6.1 Future Enhancements

**Potential Phase 2:**
- {Feature or capability}

**Potential Phase 3:**
- {Feature or capability}

**Explicitly Not Planned:**
- {Feature with reason}
```

### Step 5: Reference Supporting Documentation

If Phase 0 completed:

```markdown
## 6.2 Supporting Documentation

Out-of-scope items from:
- **{DOCUMENT_NAME}**: {boundary clarification}
```

### Step 6: Validate Boundaries

Check that:
- **Clear:** Each exclusion is specific
- **Justified:** Each has rationale
- **Complete:** All potential scope questions addressed
- **Aligned:** No contradictions with in-scope

📊 COUNT-AND-DOCUMENT: Out-of-scope items
- Features: [number]
- User types: [number]
- Platforms: [number]
- Total: [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] Out-of-scope section added ✅/❌
- [ ] At least 3 categories addressed ✅/❌
- [ ] Each exclusion has clear rationale ✅/❌
- [ ] Future enhancement path noted ✅/❌

---

## Phase 1 Completion

🎯 PHASE-COMPLETE: Requirements gathered

srd.md should contain:
- ✅ Business goals (minimum 1)
- ✅ User stories (minimum 1)
- ✅ Functional requirements (minimum 3)
- ✅ Non-functional requirements
- ✅ Out-of-scope clarification

Submit checkpoint evidence to advance to Phase 2.