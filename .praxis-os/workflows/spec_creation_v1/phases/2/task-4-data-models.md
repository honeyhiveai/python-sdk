# Task 4: Model Data

**Phase:** 2 (Technical Design)  
**Purpose:** Define data structures and schemas  
**Estimated Time:** 7 minutes

---

## 🎯 Objective

Define all data models including domain entities, database schemas, and relationships.

---

## Prerequisites

🛑 EXECUTE-NOW: Tasks 1-3 must be completed

⚠️ MUST-READ: Reference template

See `core/specs-template.md` for data model patterns.

---

## Steps

### Step 1: Add Data Models Section

Append to specs.md:

```bash
cat >> .praxis-os/specs/{SPEC_DIR}/specs.md << 'EOF'

---

## 4. Data Models

---

EOF
```

### Step 2: Define Domain Models

Follow pattern from `core/specs-template.md`:

```markdown
### 4.1 Domain Models

```python
@dataclass
class Resource:
    id: UUID
    name: str
    status: Status
    created_at: datetime
    
    def is_active(self) -> bool:
        """Check if active."""
        return self.status == Status.ACTIVE
```

**Business Rules:**
- {Rule 1}
- {Rule 2}
```

### Step 3: Define Database Schema

```markdown
### 4.2 Database Schema

**Table: resources**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Identifier |
| name | VARCHAR(255) | NOT NULL | Name |

**Indexes:**
- idx_resources_owner ON (owner_id)
```

### Step 4: Define Relationships

Use ERD from `core/architecture-diagrams.md`:

```markdown
### 4.3 Relationships

[Insert ERD diagram]

**Rules:**
- User : Resource = 1:N
- Cascade delete configured
```

### Step 5: Define Validation

```markdown
### 4.4 Validation

**Resource:**
- `name`: 1-255 characters
- `status`: Valid enum value
```

📊 COUNT-AND-DOCUMENT: Data models
- Domain models: [number]
- Tables: [number]
- Relationships: [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] Domain models defined ✅/❌
- [ ] Database schema specified ✅/❌
- [ ] Relationships documented ✅/❌
- [ ] Validation rules defined ✅/❌

---

## Next Task

🎯 NEXT-MANDATORY: [task-5-security.md](task-5-security.md)