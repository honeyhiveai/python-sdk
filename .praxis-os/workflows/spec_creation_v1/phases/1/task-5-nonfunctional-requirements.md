# Task 4: Specify Non-Functional Requirements

**Phase:** 1 (Requirements Gathering)  
**Purpose:** Define quality attributes (performance, security, usability, etc.)  
**Estimated Time:** 5 minutes

---

## 🎯 Objective

Document non-functional requirements (NFRs) that define HOW WELL the system must perform. NFRs specify quality attributes critical to user satisfaction and system success.

---

## Prerequisites

🛑 EXECUTE-NOW: Tasks 1-3 must be completed

⚠️ MUST-READ: Query MCP and reference template

```python
MCP: search_standards("non-functional requirements quality attributes")
```

See `core/srd-template.md` for complete NFR categories and examples.

---

## Steps

### Step 1: Add NFR Section

Append to srd.md:

```bash
cat >> .praxis-os/specs/{SPEC_DIR}/srd.md << 'EOF'

---

## 5. Non-Functional Requirements

NFRs define quality attributes and system constraints.

---

EOF
```

### Step 2: Define NFR Categories

Use the categories from `core/srd-template.md`:

**Performance:**
```markdown
### 5.1 Performance

**NFR-P1: Response Time**
- API endpoints: 95th percentile < 200ms
- Database queries: 99th percentile < 100ms
```

**Security:**
```markdown
### 5.2 Security

**NFR-S1: Authentication**
- All endpoints require authentication
- OAuth 2.0 + API key support
```

**Reliability:**
```markdown
### 5.3 Reliability

**NFR-R1: Availability**
- System uptime: 99.9%
- Planned maintenance: < 4 hours/month
```

**Scalability:**
```markdown
### 5.4 Scalability

**NFR-SC1: Horizontal Scaling**
- Support horizontal scaling (add instances)
- No shared state between instances
```

**Usability:**
```markdown
### 5.5 Usability

**NFR-U1: Accessibility**
- WCAG 2.1 Level AA compliance
- Screen reader compatible
```

**Maintainability:**
```markdown
### 5.6 Maintainability

**NFR-M1: Code Quality**
- Test coverage: minimum 80%
- Linting: zero errors
```

See `core/srd-template.md` for complete examples in each category.

### Step 3: Add Additional Categories as Needed

Consider:
- Portability (platform requirements)
- Compatibility (integration requirements)
- Localization (multi-language)
- Legal/Regulatory (compliance)

### Step 4: Reference Supporting Documentation

If Phase 0 completed:

```markdown
## 5.7 Supporting Documentation

NFRs informed by:
- **{DOCUMENT_NAME}**: {specific insight}
```

### Step 5: Validate NFRs

Check each is:
- **Measurable:** Has specific criteria
- **Testable:** Can be verified
- **Realistic:** Achievable
- **Relevant:** Necessary for success

📊 COUNT-AND-DOCUMENT: NFRs by category
- Performance: [number]
- Security: [number]
- Reliability: [number]
- Total: [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] NFR section added ✅/❌
- [ ] At least 3 NFR categories addressed ✅/❌
- [ ] All NFRs are measurable and testable ✅/❌
- [ ] NFRs are realistic and achievable ✅/❌

🚨 FRAMEWORK-VIOLATION: Vague quality attributes

NFRs must have specific, measurable criteria. See `core/srd-template.md` for examples.

---

## Next Task

🎯 NEXT-MANDATORY: [task-5-out-of-scope.md](task-5-out-of-scope.md)