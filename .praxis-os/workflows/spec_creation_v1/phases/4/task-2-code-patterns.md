# Task 1: Document Code Patterns

**Phase:** 4 (Implementation Guidance)  
**Purpose:** Define coding patterns and anti-patterns  
**Estimated Time:** 8 minutes

---

## 🎯 Objective

Document recommended code patterns that developers should follow during implementation. Include concrete examples of good patterns and anti-patterns to avoid.

---

## Prerequisites

🛑 EXECUTE-NOW: Phase 3 must be completed

- Review specs.md for architecture and components
- Review tasks.md for implementation tasks

⚠️ MUST-READ: Query MCP and reference template

```python
MCP: search_standards("production code checklist code patterns")
```

See `core/implementation-template.md` for complete structure and pattern examples.

---

## Steps

### Step 1: Create implementation.md

Initialize from `core/implementation-template.md`:

```bash
cat > .praxis-os/specs/{SPEC_DIR}/implementation.md << 'EOF'
# Implementation Approach

**Project:** {FEATURE_NAME}  
**Date:** {CURRENT_DATE}

---

## 1. Implementation Philosophy

**Core Principles:**
1. {Principle - e.g., "Test-Driven Development"}
2. {Principle - e.g., "Incremental Delivery"}
3. {Principle - e.g., "Code Review Required"}

---

## 2. Implementation Order

[From tasks.md - reference phase sequence]

---

## 3. Code Patterns

EOF
```

### Step 2: Add Code Patterns

⚠️ MUST-READ: Use patterns from `core/implementation-template.md`

For each component in specs.md, add appropriate pattern:
- Repository Pattern (data access)
- Service Layer Pattern (business logic)
- API Controller Pattern (endpoints)
- Error Handling Pattern

Include both good examples and anti-patterns (what NOT to do).

### Step 3: Add Language-Specific Patterns

Based on tech stack from specs.md, add relevant patterns from template or standards.

### Step 4: Link to Components

Reference specific components from specs.md:
```markdown
### Pattern: {Pattern Name}
**Used in:** {Component names from specs.md section X}
**Example:** [See core/implementation-template.md]
```

📊 COUNT-AND-DOCUMENT: Patterns [number], anti-patterns [number], components mapped [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] implementation.md created ✅/❌
- [ ] Key patterns documented ✅/❌
- [ ] Code examples provided ✅/❌
- [ ] Anti-patterns identified ✅/❌
- [ ] Patterns linked to specs.md ✅/❌

🚨 FRAMEWORK-VIOLATION: Abstract patterns without examples

Every pattern must have concrete code examples. See `core/implementation-template.md` for pattern examples.

---

## Next Task

🎯 NEXT-MANDATORY: [task-2-testing-strategy.md](task-2-testing-strategy.md)

Continue to define testing strategy.
