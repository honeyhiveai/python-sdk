# Task 2: Review for Consistency

**Phase:** 5 (Finalization)  
**Purpose:** Check cross-references and terminology  
**Estimated Time:** 5 minutes

---

## 🎯 Objective

Ensure consistency across all specification documents. Verify that component names, terminology, and cross-references are aligned throughout specs.md, srd.md, tasks.md, and implementation.md.

---

## Prerequisites

🛑 EXECUTE-NOW: Task 1 must be completed

- All documents must be complete

---

## Steps

### Step 1: Check Component Name Consistency

Verify component names are identical across documents:

```markdown
**Example Check:**
- specs.md calls it: "UserService"
- tasks.md references: "UserService" ✅
- implementation.md uses: "UserService" ✅

**Common Issues:**
- Different naming: UserService vs User_Service vs user-service
- Inconsistent capitalization: UserService vs userService
```

**Action:** Create component name list and verify usage in all docs.

### Step 2: Check Terminology Consistency

Verify technical terms are used consistently:

```markdown
**Example:**
- Don't mix "database" and "datastore"
- Don't mix "endpoint" and "route"
- Don't mix "authentication" and "auth" (pick one)

**Create terminology glossary:**
- API → Application Programming Interface
- Repository → Data access layer
- Service → Business logic layer
- Controller → API endpoint handler
```

### Step 3: Validate Cross-References

Check that references between documents are accurate:

```markdown
**specs.md → tasks.md:**
- specs.md defines "UserService" in Section 2.1
- tasks.md Task 2.1 should reference "Section 2.1 from specs.md"
- Verify reference is correct ✅/❌

**srd.md → specs.md:**
- srd.md Requirement FR-1: "User registration"
- specs.md should implement FR-1
- Verify all requirements addressed ✅/❌

**tasks.md → implementation.md:**
- tasks.md mentions testing approach
- implementation.md Section 4 should detail testing
- Verify consistency ✅/❌
```

### Step 4: Check Requirement Traceability

Every requirement in srd.md should trace to:
- A component in specs.md
- A task in tasks.md
- Code pattern in implementation.md

```markdown
**Traceability Matrix:**

| Requirement | specs.md | tasks.md | implementation.md |
|-------------|----------|----------|-------------------|
| FR-1        | Sec 2.1  | Task 2.1 | Pattern: Service  |
| FR-2        | Sec 2.2  | Task 2.2 | Pattern: API      |
```

### Step 5: Verify Data Model Consistency

Data models should be consistent:

```markdown
**Example:**
- specs.md defines User with: id, email, name
- implementation.md shows User class with same fields
- tasks.md references User model correctly

**Check:**
- [ ] Field names match
- [ ] Data types match
- [ ] Relationships documented consistently
```

### Step 6: Fix Inconsistencies

For each identified inconsistency:
1. Determine correct version
2. Update all documents
3. Re-verify consistency

📊 COUNT-AND-DOCUMENT: Consistency review
- Components checked: [number]
- Terminology inconsistencies: [number]
- Cross-reference issues: [number]
- All fixed: ✅/❌

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] Component names consistent ✅/❌
- [ ] Terminology consistent ✅/❌
- [ ] Cross-references validated ✅/❌
- [ ] Requirements traceable ✅/❌
- [ ] Data models aligned ✅/❌

🚨 FRAMEWORK-VIOLATION: Inconsistent specifications

Inconsistent terminology or naming will confuse implementation teams and cause errors.

---

## Next Task

🎯 NEXT-MANDATORY: [task-3-final-package.md](task-3-final-package.md)

Continue to generate final deliverable package.
