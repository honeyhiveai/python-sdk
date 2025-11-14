# Task 3: Specify APIs

**Phase:** 2 (Technical Design)  
**Purpose:** Define interfaces and contracts  
**Estimated Time:** 8 minutes

---

## 🎯 Objective

Define all APIs, interfaces, and contracts that components expose. Include HTTP APIs, internal interfaces, event schemas, and integration points.

---

## Prerequisites

🛑 EXECUTE-NOW: Tasks 1-2 must be completed

⚠️ MUST-READ: Query MCP and reference template

```python
MCP: search_standards("API design REST principles")
```

See `core/specs-template.md` for API patterns.

---

## Steps

### Step 1: Add API Section

Append to specs.md:

```bash
cat >> .praxis-os/specs/{SPEC_DIR}/specs.md << 'EOF'

---

## 3. API Design

---

EOF
```

### Step 2: Define HTTP/REST APIs

Follow endpoint pattern from `core/specs-template.md`:

```markdown
### 3.1 REST API Endpoints

#### GET /resources

**Purpose:** Retrieve resources

**Authentication:** Required

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | int | No | Page number |

**Response 200:**
```json
{
  "data": [],
  "meta": {}
}
```

**Error Responses:**
- 401: Unauthorized
- 404: Not found
```

### Step 3: Define Internal Interfaces

```markdown
### 3.2 Internal Interfaces

```python
class ServiceInterface:
    def create(self, data: DTO) -> Entity:
        """Create entity."""
        pass
```
```

### Step 4: Define DTOs

```markdown
### 3.3 Data Transfer Objects

```python
@dataclass
class ResourceDTO:
    name: str
    description: Optional[str]
```
```

### Step 5: Define Event Schemas (if applicable)

```markdown
### 3.4 Event Schemas

```json
{
  "event_type": "resource.created",
  "data": {}
}
```
```

### Step 6: Define Error Handling

```markdown
### 3.5 Error Handling

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable"
  }
}
```
```

📊 COUNT-AND-DOCUMENT: APIs defined
- REST endpoints: [number]
- Internal interfaces: [number]
- DTOs: [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] All public APIs documented ✅/❌
- [ ] Request/response formats defined ✅/❌
- [ ] Authentication specified ✅/❌
- [ ] Error handling documented ✅/❌

---

## Next Task

🎯 NEXT-MANDATORY: [task-4-data-models.md](task-4-data-models.md)