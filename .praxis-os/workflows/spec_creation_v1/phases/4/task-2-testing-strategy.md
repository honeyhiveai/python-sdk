# Task 2: Define Testing Strategy

**Phase:** 4 (Implementation Guidance)  
**Purpose:** Specify testing approach and examples  
**Estimated Time:** 7 minutes

---

## 🎯 Objective

Define the testing strategy including unit tests, integration tests, mocking approach, and coverage targets. Provide concrete test examples.

---

## Prerequisites

🛑 EXECUTE-NOW: Task 1 must be completed

⚠️ MUST-READ: Query MCP and reference template

```python
MCP: search_standards("testing strategies integration testing")
```

See `core/implementation-template.md` for testing examples.

---

## Steps

### Step 1: Add Testing Section

Append to implementation.md:

```bash
cat >> .praxis-os/specs/{SPEC_DIR}/implementation.md << 'EOF'

---

## 4. Testing Strategy

EOF
```

### Step 2: Define Unit Testing Approach

Follow structure from `core/implementation-template.md`:

```markdown
### Unit Tests

**Coverage Target:** 80% minimum

**Pattern:**
```python
def test_feature():
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_value
```

**Test Organization:**
```
tests/
├── unit/
│   ├── test_services.py
│   ├── test_repositories.py
│   └── test_models.py
```
```

### Step 3: Define Integration Testing

```markdown
### Integration Tests

**Scope:** Component interactions, API endpoints, database

**Pattern:**
```python
def test_api_endpoint(client, db):
    response = client.post("/endpoint", json=payload)
    assert response.status_code == 200
    assert response.json()["data"] is not None
    
    # Verify database
    result = db.query("SELECT...")
    assert result is not None
```
```

### Step 4: Define Mocking Strategy

Document when to mock (external APIs, DB in unit tests, time, file I/O). See `core/implementation-template.md` for examples.

### Step 5: Add Test Examples

Reference relevant examples from `core/implementation-template.md` for your components.

### Step 6: Add Testing Checklist

```markdown
### Testing Checklist
- [ ] All tests passing, coverage > 80%
- [ ] Integration tests cover happy + error paths
- [ ] Performance tests for critical paths
```

📊 COUNT-AND-DOCUMENT: Test examples [number], coverage target [%]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] Testing strategy defined ✅/❌
- [ ] Unit test approach documented ✅/❌
- [ ] Integration test approach documented ✅/❌
- [ ] Mocking strategy specified ✅/❌
- [ ] Test examples provided ✅/❌
- [ ] Coverage targets specified ✅/❌

---

## Next Task

🎯 NEXT-MANDATORY: [task-3-deployment.md](task-3-deployment.md)
