# Task 2: Define Components

**Phase:** 2 (Technical Design)  
**Purpose:** Break system into logical components  
**Estimated Time:** 8 minutes

---

## 🎯 Objective

Define individual components from architecture. Specify responsibilities, interfaces, dependencies, and internal structure for each.

---

## Prerequisites

🛑 EXECUTE-NOW: Task 1 must be completed

⚠️ MUST-READ: Reference template

See `core/specs-template.md` for component definition patterns.

---

## Steps

### Step 1: Add Components Section

Append to specs.md:

```bash
cat >> .praxis-os/specs/{SPEC_DIR}/specs.md << 'EOF'

---

## 2. Component Design

---

EOF
```

### Step 2: Document Each Component

Follow pattern from `core/specs-template.md` section "Component Definition Pattern":

```markdown
### 2.1 Component: {Name}

**Purpose:** {One-sentence description}

**Responsibilities:**
- {Responsibility 1}
- {Responsibility 2}

**Requirements Satisfied:**
- FR-{XXX}: {How}

**Public Interface:**
```python
class ComponentName:
    def method_1(self, param: Type) -> ReturnType:
        """Handle operation."""
        pass
```

**Dependencies:**
- Requires: {Component/service}
- Provides: {What others depend on}

**Error Handling:**
- {Condition} → {Handling}
```

### Step 3: Define Component Interactions

Show how components communicate (use diagrams from `core/architecture-diagrams.md`):

```markdown
## 2.X Component Interactions

**Interaction Diagram:**
[Use component interaction diagram from core/architecture-diagrams.md]

| From | To | Method | Purpose |
|------|----|----|---------|
| A | B | `process()` | {Purpose} |
```

### Step 4: Define Module Structure

```markdown
## 2.Y Module Organization

**Directory Structure:**
```
project/
├── api/
├── services/
├── models/
└── repositories/
```

**Dependency Rules:**
- No circular imports
- Use dependency injection
```

📊 COUNT-AND-DOCUMENT: Components defined
- Total: [number]
- Interfaces: [number]
- Dependencies mapped: [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] All architecture components documented ✅/❌
- [ ] Clear responsibilities for each ✅/❌
- [ ] Public interfaces defined ✅/❌
- [ ] Dependencies mapped ✅/❌
- [ ] Module structure defined ✅/❌

---

## Next Task

🎯 NEXT-MANDATORY: [task-3-apis.md](task-3-apis.md)